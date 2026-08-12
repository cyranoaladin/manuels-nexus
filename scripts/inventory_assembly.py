"""Pure selection and validation helpers for declared assemblers."""

from __future__ import annotations

import ast
import fnmatch
import json
import os
import stat
from collections import Counter, defaultdict
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping

try:
    from scripts import inventory_graph
except ModuleNotFoundError:  # direct execution through inventory_collection.py
    import inventory_graph


class AssemblyAnalysisError(RuntimeError):
    """Raised when an assembler cannot be inspected safely."""


class _ManifestConfinementError(ValueError):
    """Raised when a manifest path cannot be opened without following links."""


_AUDITED_SELECTION_CONSTANTS = frozenset(
    {
        "BOOK_MANIFESTS",
        "CHAPITRES",
        "ELEVE_ALLOWED_TYPES",
        "ELEVE_EXCLUDES",
        "ELEVE_VARIANTS",
        "ORDER",
        "VARIANT_ORDERS",
        "VARIANTS",
        "VARIANTES",
    }
)
_MUTATING_METHODS = frozenset(
    {
        "add",
        "append",
        "clear",
        "difference_update",
        "discard",
        "extend",
        "insert",
        "intersection_update",
        "pop",
        "popitem",
        "remove",
        "reverse",
        "setdefault",
        "sort",
        "symmetric_difference_update",
        "update",
    }
)
_NESTED_MUTABLE_ACCESSORS = frozenset({"get", "items", "values"})
_DYNAMIC_NAMESPACE_BUILTINS = frozenset(
    {"eval", "exec", "globals", "locals", "vars"}
)
_MODULE_REFLECTIVE_NAMESPACE_SYMBOLS = frozenset(
    {
        "__builtins__",
        "__import__",
        "builtins",
        "delattr",
        "getattr",
        "import_module",
        "setattr",
        *_DYNAMIC_NAMESPACE_BUILTINS,
    }
)
_NESTED_REFLECTIVE_NAMESPACE_NAMES = frozenset(
    {"__builtins__", "__import__", "import_module"}
)
_NESTED_REFLECTIVE_NAMESPACE_ATTRIBUTES = frozenset(
    {"import_module", *_DYNAMIC_NAMESPACE_BUILTINS}
)


def _canonicalize_literal(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {
            key: _canonicalize_literal(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(value, (set, frozenset)):
        return sorted(_canonicalize_literal(item) for item in value)
    if isinstance(value, (list, tuple)):
        return [_canonicalize_literal(item) for item in value]
    return value


def _target_root_names(*targets: ast.AST) -> set[str]:
    names: set[str] = set()
    pending = list(targets)
    while pending:
        target = pending.pop()
        if isinstance(target, ast.Name):
            names.add(target.id)
        elif isinstance(target, (ast.List, ast.Tuple)):
            pending.extend(target.elts)
        elif isinstance(target, (ast.Attribute, ast.Starred, ast.Subscript)):
            pending.append(target.value)
    return names


def _binding_target_names(*targets: ast.AST) -> set[str]:
    names: set[str] = set()
    pending = list(targets)
    while pending:
        target = pending.pop()
        if isinstance(target, ast.Name):
            names.add(target.id)
        elif isinstance(target, (ast.List, ast.Tuple)):
            pending.extend(target.elts)
        elif isinstance(target, ast.Starred):
            pending.append(target.value)
    return names


def _mutation_target_names(*targets: ast.AST) -> set[str]:
    names: set[str] = set()
    pending = list(targets)
    while pending:
        target = pending.pop()
        if isinstance(target, (ast.Attribute, ast.Subscript)):
            names.update(_target_root_names(target.value))
        elif isinstance(target, (ast.List, ast.Tuple)):
            pending.extend(target.elts)
        elif isinstance(target, ast.Starred):
            pending.append(target.value)
    return names


def _import_bound_names(node: ast.Import | ast.ImportFrom) -> set[str]:
    names: set[str] = set()
    for alias in node.names:
        if alias.name == "*":
            continue
        names.add(alias.asname or alias.name.split(".", maxsplit=1)[0])
    return names


class _ScopeBindingCollector(ast.NodeVisitor):
    def __init__(self) -> None:
        self.globals: set[str] = set()
        self.locals: set[str] = set()
        self.nonlocals: set[str] = set()

    def visit_Global(self, node: ast.Global) -> None:
        self.globals.update(node.names)

    def visit_Nonlocal(self, node: ast.Nonlocal) -> None:
        self.nonlocals.update(node.names)

    def visit_Assign(self, node: ast.Assign) -> None:
        self.locals.update(_binding_target_names(*node.targets))
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self.locals.update(_binding_target_names(node.target))
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self.locals.update(_binding_target_names(node.target))
        self.generic_visit(node)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        self.locals.update(_binding_target_names(node.target))
        self.generic_visit(node)

    def visit_Delete(self, node: ast.Delete) -> None:
        self.locals.update(_binding_target_names(*node.targets))
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self.locals.update(_binding_target_names(node.target))
        self.generic_visit(node)

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self.visit_For(node)

    def visit_With(self, node: ast.With) -> None:
        self.locals.update(
            _binding_target_names(
                *(
                    item.optional_vars
                    for item in node.items
                    if item.optional_vars is not None
                )
            )
        )
        self.generic_visit(node)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        self.visit_With(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.name is not None:
            self.locals.add(node.name)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:
        self.locals.update(_import_bound_names(node))

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        self.locals.update(_import_bound_names(node))

    def visit_MatchAs(self, node: ast.MatchAs) -> None:
        if node.name is not None:
            self.locals.add(node.name)
        self.generic_visit(node)

    def visit_MatchStar(self, node: ast.MatchStar) -> None:
        if node.name is not None:
            self.locals.add(node.name)

    def visit_MatchMapping(self, node: ast.MatchMapping) -> None:
        if node.rest is not None:
            self.locals.add(node.rest)
        self.generic_visit(node)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self.locals.add(node.name)
        for decorator in node.decorator_list:
            self.visit(decorator)
        for default in (*node.args.defaults, *node.args.kw_defaults):
            if default is not None:
                self.visit(default)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self.visit_FunctionDef(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        for default in (*node.args.defaults, *node.args.kw_defaults):
            if default is not None:
                self.visit(default)

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self.locals.add(node.name)
        for decorator in node.decorator_list:
            self.visit(decorator)
        for base in node.bases:
            self.visit(base)
        for keyword in node.keywords:
            self.visit(keyword.value)


def _argument_names(arguments: ast.arguments) -> set[str]:
    names = {
        argument.arg
        for argument in (
            *arguments.posonlyargs,
            *arguments.args,
            *arguments.kwonlyargs,
        )
    }
    if arguments.vararg is not None:
        names.add(arguments.vararg.arg)
    if arguments.kwarg is not None:
        names.add(arguments.kwarg.arg)
    return names


@dataclass(frozen=True)
class _LexicalScope:
    kind: str
    locals: frozenset[str]
    globals: frozenset[str]
    nonlocals: frozenset[str]


def _lexical_scope(
    kind: str,
    body: list[ast.stmt],
    *,
    arguments: ast.arguments | None = None,
) -> _LexicalScope:
    collector = _ScopeBindingCollector()
    for statement in body:
        collector.visit(statement)
    local_names = set(collector.locals)
    if arguments is not None:
        local_names.update(_argument_names(arguments))
    local_names.difference_update(collector.globals | collector.nonlocals)
    return _LexicalScope(
        kind=kind,
        locals=frozenset(local_names),
        globals=frozenset(collector.globals),
        nonlocals=frozenset(collector.nonlocals),
    )


_MODULE_SCOPE = _LexicalScope(
    kind="module",
    locals=frozenset(),
    globals=frozenset(),
    nonlocals=frozenset(),
)


def _guaranteed_class_statement_bindings(statement: ast.stmt) -> set[str]:
    if isinstance(statement, ast.Assign):
        return _binding_target_names(*statement.targets)
    if isinstance(statement, ast.AnnAssign) and statement.value is not None:
        return _binding_target_names(statement.target)
    if isinstance(statement, ast.AugAssign):
        return _binding_target_names(statement.target)
    if isinstance(statement, (ast.With, ast.AsyncWith)):
        return _binding_target_names(
            *(
                item.optional_vars
                for item in statement.items
                if item.optional_vars is not None
            )
        )
    if isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return {statement.name}
    if isinstance(statement, (ast.Import, ast.ImportFrom)):
        return _import_bound_names(statement)
    return set()


class _AuditedMutationVisitor(ast.NodeVisitor):
    def __init__(
        self,
        supported_top_level_node_ids: set[int],
        module_bound_names: frozenset[str],
    ) -> None:
        self.ambiguous: set[str] = set()
        self.declared: set[str] = set()
        self._scopes: list[_LexicalScope] = [_MODULE_SCOPE]
        self._class_runtime_bindings: list[set[str] | None] = [None]
        self._mutable_aliases: list[dict[str, set[str]]] = [{}]
        self._supported_top_level_node_ids = supported_top_level_node_ids
        self._module_bound_names = module_bound_names
        self._sys_module_aliases: set[str] = set()

    def _mark_reflective_namespace(self) -> None:
        self.ambiguous.update(_AUDITED_SELECTION_CONSTANTS)

    def _binding_module_names(self, names: set[str]) -> set[str]:
        audited = names & _AUDITED_SELECTION_CONSTANTS
        scope = self._scopes[-1]
        if scope.kind == "module":
            return audited
        return audited & scope.globals

    def _name_resolves_to_module(self, name: str) -> bool:
        scope = self._scopes[-1]
        if scope.kind == "module":
            return True
        if scope.kind == "class":
            if name in scope.globals:
                return True
            class_bindings = self._class_runtime_bindings[-1]
            if class_bindings is not None and name in class_bindings:
                return False
        else:
            if name in scope.globals:
                return True
            if name in scope.locals or name in scope.nonlocals:
                return False
        for enclosing in reversed(self._scopes[:-1]):
            if enclosing.kind not in {"comprehension", "function"}:
                continue
            if name in enclosing.locals or name in enclosing.nonlocals:
                return False
        return True

    def _mutation_module_names(self, names: set[str]) -> set[str]:
        module_names = {
            name
            for name in names & _AUDITED_SELECTION_CONSTANTS
            if self._name_resolves_to_module(name)
        }
        for name in names:
            module_names.update(self._alias_module_names(name))
        return module_names

    def _alias_module_names(self, name: str) -> set[str]:
        current_scope = self._scopes[-1]
        if current_scope.kind != "module" and name in current_scope.globals:
            return set(self._mutable_aliases[0].get(name, set()))
        for index in range(len(self._scopes) - 1, -1, -1):
            scope = self._scopes[index]
            if scope.kind == "class":
                if index == len(self._scopes) - 1:
                    class_bindings = self._class_runtime_bindings[index]
                    if class_bindings is not None and name in class_bindings:
                        return set(self._mutable_aliases[index].get(name, set()))
                continue
            aliases = self._mutable_aliases[index]
            if name in aliases:
                return set(aliases[name])
            if scope.kind in {"comprehension", "function"} and name in scope.locals:
                return set()
        return set()

    def _alias_binding_index(self, name: str) -> int:
        current_index = len(self._scopes) - 1
        current_scope = self._scopes[current_index]
        if current_scope.kind == "module":
            return 0
        if name in current_scope.globals:
            return 0
        if name in current_scope.nonlocals:
            for index in range(current_index - 1, 0, -1):
                scope = self._scopes[index]
                if scope.kind == "function" and name in scope.locals:
                    return index
        return current_index

    @staticmethod
    def _copy_alias_state(
        state: list[dict[str, set[str]]],
    ) -> list[dict[str, set[str]]]:
        return [
            {name: set(module_names) for name, module_names in aliases.items()}
            for aliases in state
        ]

    def _alias_state(self) -> list[dict[str, set[str]]]:
        return self._copy_alias_state(self._mutable_aliases)

    def _merge_alias_states(
        self,
        *states: list[dict[str, set[str]]],
    ) -> list[dict[str, set[str]]]:
        merged = [{} for _scope in self._scopes]
        for state in states:
            for index, aliases in enumerate(state):
                for name, module_names in aliases.items():
                    merged[index].setdefault(name, set()).update(module_names)
        return merged

    def _visit_statements_from_alias_state(
        self,
        statements: list[ast.stmt],
        state: list[dict[str, set[str]]],
    ) -> list[dict[str, set[str]]]:
        self._mutable_aliases = self._copy_alias_state(state)
        for statement in statements:
            self.visit(statement)
        return self._alias_state()

    def _visit_statement_prefix_alias_states(
        self,
        statements: list[ast.stmt],
        state: list[dict[str, set[str]]],
    ) -> list[list[dict[str, set[str]]]]:
        self._mutable_aliases = self._copy_alias_state(state)
        states = [self._alias_state()]
        for statement in statements:
            self.visit(statement)
            states.append(self._alias_state())
        return states

    def _value_module_names(self, value: ast.AST | None) -> set[str]:
        if not isinstance(value, ast.Name) or not isinstance(value.ctx, ast.Load):
            return set()
        alias_names = self._alias_module_names(value.id)
        if alias_names:
            return alias_names
        if value.id in _AUDITED_SELECTION_CONSTANTS and self._name_resolves_to_module(
            value.id
        ):
            return {value.id}
        return set()

    def _indexed_module_names(self, value: ast.AST | None) -> set[str]:
        if not isinstance(value, ast.Subscript):
            return set()
        container = value.value
        if (
            isinstance(container, ast.Name)
            and container.id in _AUDITED_SELECTION_CONSTANTS
            and self._name_resolves_to_module(container.id)
        ):
            return {container.id}
        return set()

    def _accessor_module_names(self, value: ast.AST | None) -> set[str]:
        if not isinstance(value, ast.Call) or not isinstance(value.func, ast.Attribute):
            return set()
        if value.func.attr not in _NESTED_MUTABLE_ACCESSORS:
            return set()
        return self._value_module_names(value.func.value)

    def _derived_alias_names(self, value: ast.AST | None) -> set[str]:
        indexed_names = self._indexed_module_names(value)
        if indexed_names:
            return indexed_names
        accessor_names = self._accessor_module_names(value)
        if accessor_names:
            return accessor_names
        if isinstance(value, ast.Name) and isinstance(value.ctx, ast.Load):
            return self._alias_module_names(value.id)
        return set()

    def _iterated_alias_names(self, value: ast.AST | None) -> set[str]:
        derived_names = self._indexed_module_names(value) | self._accessor_module_names(
            value
        )
        if derived_names:
            return derived_names
        if isinstance(value, (ast.List, ast.Set, ast.Tuple)):
            return set().union(
                *(
                    self._derived_alias_names(item) | self._iterated_alias_names(item)
                    for item in value.elts
                )
            )
        return set()

    def _assignment_alias_names(self, value: ast.AST | None) -> set[str]:
        return self._derived_alias_names(value)

    def _mutation_expression_module_names(self, value: ast.AST | None) -> set[str]:
        module_names = self._derived_alias_names(value)
        if module_names:
            return module_names
        if isinstance(value, (ast.Attribute, ast.Subscript)):
            return self._mutation_expression_module_names(value.value)
        return set()

    def _clear_aliases(self, names: set[str]) -> None:
        for name in names:
            self._mutable_aliases[self._alias_binding_index(name)].pop(name, None)

    def _bind_aliases(self, names: set[str], module_names: set[str]) -> None:
        scope = self._scopes[-1]
        local_binding = (
            scope.kind in {"comprehension", "function"}
            and names <= set(scope.locals)
            and not names & (set(scope.globals) | set(scope.nonlocals))
        )
        if local_binding:
            aliases = self._mutable_aliases[-1]
            for name in names:
                aliases[name] = set(module_names)
            return
        if names and names <= set(scope.nonlocals):
            # Calls are not executed by the static analyzer. Introducing an
            # audited alias through nonlocal is therefore unsafe regardless of
            # whether a later call can be proven.
            self._record_module_names(module_names)
            for name in names:
                self._mutable_aliases[self._alias_binding_index(name)][name] = set(
                    module_names
                )
            return
        self._record_module_names(module_names)

    def _record_iteration_aliases(
        self,
        target: ast.AST,
        iterable: ast.AST,
    ) -> set[str]:
        bound_names = _binding_target_names(target)
        self._record_binding(bound_names)
        self._clear_aliases(bound_names)
        alias_names = self._iterated_alias_names(iterable)
        if alias_names:
            self._bind_aliases(bound_names, alias_names)
        return bound_names

    def _record_assignment_value(
        self,
        targets: tuple[ast.AST, ...],
        value: ast.AST | None,
    ) -> None:
        bound_names = _binding_target_names(*targets)
        alias_names = self._assignment_alias_names(value)
        simple_targets = bool(targets) and all(
            isinstance(target, ast.Name) for target in targets
        )
        self._clear_aliases(bound_names)
        if alias_names and simple_targets:
            self._bind_aliases(bound_names, alias_names)
            return
        self._record_escape(value)

    def _record_module_names(self, module_names: set[str]) -> None:
        self.declared.update(module_names)
        self.ambiguous.update(module_names)

    def _record_binding(self, names: set[str], *, supported: bool = False) -> None:
        module_names = self._binding_module_names(names)
        self.declared.update(module_names)
        if not supported:
            self.ambiguous.update(module_names)

    def _record_mutation(self, names: set[str]) -> None:
        self._record_module_names(self._mutation_module_names(names))

    def _escaping_module_names(self, value: ast.AST | None) -> set[str]:
        if value is None:
            return set()
        if isinstance(value, ast.Name):
            alias_names = self._alias_module_names(value.id)
            if alias_names:
                return alias_names
            if (
                isinstance(value.ctx, ast.Load)
                and value.id in _AUDITED_SELECTION_CONSTANTS
                and self._name_resolves_to_module(value.id)
            ):
                return {value.id}
            return set()
        if isinstance(value, ast.Starred):
            return self._escaping_module_names(value.value)
        if isinstance(value, (ast.List, ast.Set, ast.Tuple)):
            return set().union(
                *(self._escaping_module_names(item) for item in value.elts)
            )
        if isinstance(value, ast.Dict):
            return set().union(
                *(
                    self._escaping_module_names(item)
                    for item in (*value.keys, *value.values)
                )
            )
        if isinstance(value, ast.IfExp):
            return self._escaping_module_names(
                value.body
            ) | self._escaping_module_names(value.orelse)
        if isinstance(value, ast.BoolOp):
            return set().union(
                *(self._escaping_module_names(item) for item in value.values)
            )
        if isinstance(value, ast.NamedExpr):
            return self._escaping_module_names(value.value)
        if isinstance(value, ast.Await):
            return self._escaping_module_names(value.value)
        if isinstance(value, ast.Subscript):
            return self._indexed_module_names(value)
        if isinstance(value, ast.Call):
            return self._accessor_module_names(value)
        return set()

    def _record_escape(self, value: ast.AST | None) -> None:
        self.ambiguous.update(self._escaping_module_names(value))

    def visit_Assign(self, node: ast.Assign) -> None:
        self._record_binding(
            _binding_target_names(*node.targets),
            supported=id(node) in self._supported_top_level_node_ids,
        )
        self._record_mutation(_mutation_target_names(*node.targets))
        self._record_module_names(
            set().union(
                *(self._mutation_expression_module_names(target) for target in node.targets)
            )
        )
        self._record_assignment_value(tuple(node.targets), node.value)
        self.generic_visit(node)

    def visit_AnnAssign(self, node: ast.AnnAssign) -> None:
        self._record_binding(
            _binding_target_names(node.target),
            supported=id(node) in self._supported_top_level_node_ids,
        )
        self._record_mutation(_mutation_target_names(node.target))
        self._record_module_names(
            self._mutation_expression_module_names(node.target)
        )
        self._record_assignment_value((node.target,), node.value)
        self.generic_visit(node)

    def visit_AugAssign(self, node: ast.AugAssign) -> None:
        self._record_mutation(_target_root_names(node.target))
        self._record_module_names(
            self._mutation_expression_module_names(node.target)
        )
        self._record_binding(_binding_target_names(node.target))
        self.generic_visit(node)

    def visit_NamedExpr(self, node: ast.NamedExpr) -> None:
        self._record_binding(_binding_target_names(node.target))
        self._record_escape(node.value)
        self.generic_visit(node)

    def visit_Delete(self, node: ast.Delete) -> None:
        self._record_binding(_binding_target_names(*node.targets))
        self._record_mutation(_mutation_target_names(*node.targets))
        self._record_module_names(
            set().union(
                *(self._mutation_expression_module_names(target) for target in node.targets)
            )
        )
        deleted_names = _binding_target_names(*node.targets)
        self._clear_aliases(deleted_names)
        class_bindings = self._class_runtime_bindings[-1]
        if class_bindings is not None:
            class_bindings.difference_update(deleted_names)
        self.generic_visit(node)

    def visit_Name(self, node: ast.Name) -> None:
        if (
            isinstance(node.ctx, ast.Load)
            and (
                node.id in _DYNAMIC_NAMESPACE_BUILTINS
                or node.id in _NESTED_REFLECTIVE_NAMESPACE_NAMES
                or (
                    len(self._scopes) == 1
                    and node.id in _MODULE_REFLECTIVE_NAMESPACE_SYMBOLS
                )
            )
        ):
            self._mark_reflective_namespace()

    def visit_Attribute(self, node: ast.Attribute) -> None:
        if (
            node.attr in _NESTED_REFLECTIVE_NAMESPACE_ATTRIBUTES
            or (
                node.attr == "modules"
                and isinstance(node.value, ast.Name)
                and node.value.id in self._sys_module_aliases
            )
            or (
                node.attr == "__dict__"
                and isinstance(node.value, ast.Name)
                and node.value.id in self._sys_module_aliases
            )
            or (
                len(self._scopes) == 1
                and node.attr in _MODULE_REFLECTIVE_NAMESPACE_SYMBOLS
            )
        ):
            self._mark_reflective_namespace()
        self.generic_visit(node)

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute) and node.func.attr in _MUTATING_METHODS:
            self._record_mutation(_target_root_names(node.func.value))
            self._record_module_names(
                self._mutation_expression_module_names(node.func.value)
            )
        immutable_book_manifest_key_copy = (
            isinstance(node.func, ast.Name)
            and node.func.id == "tuple"
            and len(self._scopes) == 1
            and "tuple" not in self._module_bound_names
            and len(node.args) == 1
            and not node.keywords
            and isinstance(node.args[0], ast.Name)
            and node.args[0].id == "BOOK_MANIFESTS"
        )
        for argument in node.args:
            if not immutable_book_manifest_key_copy:
                self._record_escape(argument)
        for keyword in node.keywords:
            self._record_escape(keyword.value)
        self.generic_visit(node)

    def visit_Return(self, node: ast.Return) -> None:
        self._record_escape(node.value)
        self.generic_visit(node)

    def visit_Yield(self, node: ast.Yield) -> None:
        self._record_escape(node.value)
        self.generic_visit(node)

    def visit_YieldFrom(self, node: ast.YieldFrom) -> None:
        self._record_escape(node.value)
        self.generic_visit(node)

    def visit_For(self, node: ast.For) -> None:
        self.visit(node.iter)
        entry_state = self._alias_state()
        bound_names = self._record_iteration_aliases(node.target, node.iter)
        class_bindings = self._class_runtime_bindings[-1]
        previous_bindings = set(class_bindings) if class_bindings is not None else None
        if class_bindings is not None:
            class_bindings.update(bound_names - set(self._scopes[-1].globals))
        for statement in node.body:
            self.visit(statement)
        body_state = self._alias_state()
        if class_bindings is not None and previous_bindings is not None:
            class_bindings.clear()
            class_bindings.update(previous_bindings)
        loop_state = self._merge_alias_states(entry_state, body_state)
        else_state = self._visit_statements_from_alias_state(node.orelse, loop_state)
        self._mutable_aliases = self._merge_alias_states(
            entry_state,
            body_state,
            else_state,
        )

    def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
        self.visit_For(node)

    def visit_While(self, node: ast.While) -> None:
        self.visit(node.test)
        entry_state = self._alias_state()
        body_state = self._visit_statements_from_alias_state(node.body, entry_state)
        loop_state = self._merge_alias_states(entry_state, body_state)
        else_state = self._visit_statements_from_alias_state(node.orelse, loop_state)
        self._mutable_aliases = self._merge_alias_states(
            entry_state,
            body_state,
            else_state,
        )

    def visit_If(self, node: ast.If) -> None:
        self.visit(node.test)
        entry_state = self._alias_state()
        body_state = self._visit_statements_from_alias_state(node.body, entry_state)
        else_state = self._visit_statements_from_alias_state(node.orelse, entry_state)
        self._mutable_aliases = self._merge_alias_states(body_state, else_state)

    def visit_Try(self, node: ast.Try) -> None:
        entry_state = self._alias_state()
        body_states = self._visit_statement_prefix_alias_states(node.body, entry_state)
        body_state = body_states[-1]
        normal_state = self._visit_statements_from_alias_state(node.orelse, body_state)
        exit_states = [normal_state]
        handler_entry_state = self._merge_alias_states(*body_states)
        for handler in node.handlers:
            self._mutable_aliases = self._copy_alias_state(handler_entry_state)
            self.visit(handler)
            exit_states.append(self._alias_state())
        merged_state = self._merge_alias_states(*exit_states)
        self._mutable_aliases = self._visit_statements_from_alias_state(
            node.finalbody,
            merged_state,
        )

    def visit_TryStar(self, node: ast.TryStar) -> None:
        self.visit_Try(node)

    def visit_With(self, node: ast.With) -> None:
        class_bindings = self._class_runtime_bindings[-1]
        previous_bindings = set(class_bindings) if class_bindings is not None else None
        for item in node.items:
            self.visit(item.context_expr)
            if item.optional_vars is None:
                continue
            bound_names = _binding_target_names(item.optional_vars)
            self._record_binding(bound_names)
            if class_bindings is not None:
                class_bindings.update(bound_names - set(self._scopes[-1].globals))
        for statement in node.body:
            self.visit(statement)
        if class_bindings is not None and previous_bindings is not None:
            class_bindings.clear()
            class_bindings.update(previous_bindings)

    def visit_AsyncWith(self, node: ast.AsyncWith) -> None:
        self.visit_With(node)

    def visit_ExceptHandler(self, node: ast.ExceptHandler) -> None:
        if node.type is not None:
            self.visit(node.type)
        class_bindings = self._class_runtime_bindings[-1]
        previous_bindings = set(class_bindings) if class_bindings is not None else None
        if node.name is not None:
            self._record_binding({node.name})
            if class_bindings is not None:
                class_bindings.add(node.name)
        for statement in node.body:
            self.visit(statement)
        if class_bindings is not None and previous_bindings is not None:
            class_bindings.clear()
            class_bindings.update(previous_bindings)

    def visit_Import(self, node: ast.Import) -> None:
        for alias in node.names:
            if alias.name == "sys":
                self._sys_module_aliases.add(alias.asname or "sys")
            if alias.name == "builtins":
                self._mark_reflective_namespace()
        self._record_binding(_import_bound_names(node))

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:
        for alias in node.names:
            if alias.name == "sys":
                self._sys_module_aliases.add(alias.asname or "sys")
        imports_reflective_symbol = any(
            alias.name in _MODULE_REFLECTIVE_NAMESPACE_SYMBOLS
            for alias in node.names
        )
        if (
            node.module == "builtins"
            or (
                node.module == "sys"
                and any(alias.name == "modules" for alias in node.names)
            )
            or (
                node.module == "importlib"
                and any(alias.name == "import_module" for alias in node.names)
            )
            or (len(self._scopes) == 1 and imports_reflective_symbol)
        ):
            self._mark_reflective_namespace()
        if any(alias.name == "*" for alias in node.names):
            # A star import may overwrite any audited global. It only invalidates
            # assemblers that independently opt into the closed contract.
            self.ambiguous.update(_AUDITED_SELECTION_CONSTANTS)
        self._record_binding(_import_bound_names(node))

    def visit_MatchAs(self, node: ast.MatchAs) -> None:
        if node.name is not None:
            self._record_binding({node.name})
        self.generic_visit(node)

    def visit_MatchStar(self, node: ast.MatchStar) -> None:
        if node.name is not None:
            self._record_binding({node.name})

    def visit_MatchMapping(self, node: ast.MatchMapping) -> None:
        if node.rest is not None:
            self._record_binding({node.rest})
        self.generic_visit(node)

    def _visit_function(
        self,
        node: ast.FunctionDef | ast.AsyncFunctionDef,
    ) -> None:
        enclosing_alias_state = self._alias_state()
        self._record_binding({node.name})
        for decorator in node.decorator_list:
            self.visit(decorator)
        for default in (*node.args.defaults, *node.args.kw_defaults):
            if default is not None:
                self._record_escape(default)
                self.visit(default)
        arguments = (
            *node.args.posonlyargs,
            *node.args.args,
            *node.args.kwonlyargs,
        )
        if node.args.vararg is not None:
            arguments += (node.args.vararg,)
        if node.args.kwarg is not None:
            arguments += (node.args.kwarg,)
        annotations = [
            argument.annotation
            for argument in arguments
            if argument.annotation is not None
        ]
        if node.returns is not None:
            annotations.append(node.returns)
        for annotation in annotations:
            self._record_escape(annotation)
            self.visit(annotation)
        self._scopes.append(
            _lexical_scope("function", node.body, arguments=node.args)
        )
        self._class_runtime_bindings.append(None)
        self._mutable_aliases.append({})
        for statement in node.body:
            self.visit(statement)
        self._mutable_aliases.pop()
        self._class_runtime_bindings.pop()
        self._scopes.pop()
        self._mutable_aliases = enclosing_alias_state

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def visit_Lambda(self, node: ast.Lambda) -> None:
        enclosing_alias_state = self._alias_state()
        for default in (*node.args.defaults, *node.args.kw_defaults):
            if default is not None:
                self._record_escape(default)
                self.visit(default)
        lambda_collector = _ScopeBindingCollector()
        lambda_collector.visit(node.body)
        lambda_locals = _argument_names(node.args) | lambda_collector.locals
        self._scopes.append(
            _LexicalScope(
                kind="function",
                locals=frozenset(lambda_locals),
                globals=frozenset(),
                nonlocals=frozenset(),
            )
        )
        self._class_runtime_bindings.append(None)
        self._mutable_aliases.append({})
        self._record_escape(node.body)
        self.visit(node.body)
        self._mutable_aliases.pop()
        self._class_runtime_bindings.pop()
        self._scopes.pop()
        self._mutable_aliases = enclosing_alias_state

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._record_binding({node.name})
        for decorator in node.decorator_list:
            self.visit(decorator)
        for base in node.bases:
            self.visit(base)
        for keyword in node.keywords:
            self.visit(keyword.value)
        self._scopes.append(_lexical_scope("class", node.body))
        self._class_runtime_bindings.append(set())
        self._mutable_aliases.append({})
        for statement in node.body:
            self.visit(statement)
            class_bindings = self._class_runtime_bindings[-1]
            if class_bindings is not None:
                class_bindings.update(
                    _guaranteed_class_statement_bindings(statement)
                    - set(self._scopes[-1].globals)
                )
        self._mutable_aliases.pop()
        self._class_runtime_bindings.pop()
        self._scopes.pop()

    def _visit_comprehension(
        self,
        generators: list[ast.comprehension],
        outputs: tuple[ast.expr, ...],
    ) -> None:
        if not generators:
            return
        self.visit(generators[0].iter)
        local_names = set().union(
            *(_binding_target_names(generator.target) for generator in generators)
        )
        self._scopes.append(
            _LexicalScope(
                kind="comprehension",
                locals=frozenset(local_names),
                globals=frozenset(),
                nonlocals=frozenset(),
            )
        )
        self._class_runtime_bindings.append(None)
        self._mutable_aliases.append({})
        for index, generator in enumerate(generators):
            if index:
                self.visit(generator.iter)
            self._record_iteration_aliases(generator.target, generator.iter)
            for condition in generator.ifs:
                self.visit(condition)
        for output in outputs:
            self._record_escape(output)
            self.visit(output)
        self._mutable_aliases.pop()
        self._class_runtime_bindings.pop()
        self._scopes.pop()

    def visit_ListComp(self, node: ast.ListComp) -> None:
        self._visit_comprehension(node.generators, (node.elt,))

    def visit_SetComp(self, node: ast.SetComp) -> None:
        self._visit_comprehension(node.generators, (node.elt,))

    def visit_DictComp(self, node: ast.DictComp) -> None:
        self._visit_comprehension(node.generators, (node.key, node.value))

    def visit_GeneratorExp(self, node: ast.GeneratorExp) -> None:
        self._visit_comprehension(node.generators, (node.elt,))


def _ast_latex_inputs(tree: ast.AST) -> list[tuple[str, str]]:
    inputs: set[tuple[str, str]] = set()
    for node in ast.walk(tree):
        text: str | None = None
        if isinstance(node, ast.JoinedStr):
            text = "".join(
                part.value
                for part in node.values
                if isinstance(part, ast.Constant) and isinstance(part.value, str)
            )
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            text = node.value
        if text:
            inputs.update(inventory_graph.latex_inputs(text))
    return sorted(inputs)


def analyze_assembler(path: Path | str) -> dict[str, Any]:
    """Read assembler declarations and generated LaTeX without importing code."""

    source = Path(path)
    try:
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=source.name)
    except SyntaxError as exc:
        detail = exc.msg + (f" (ligne {exc.lineno})" if exc.lineno else "")
        raise AssemblyAnalysisError(f"assembleur Python invalide: {detail}") from exc
    except (OSError, UnicodeError) as exc:
        raise AssemblyAnalysisError(
            f"assembleur Python illisible: {type(exc).__name__}"
        ) from exc

    constants: dict[str, Any] = {}
    accepted_names = _AUDITED_SELECTION_CONSTANTS
    supported_top_level_node_ids = {
        id(node)
        for node in tree.body
        if (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
        )
        or (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.value is not None
        )
    }
    module_scope = _lexical_scope("module", tree.body)
    mutation_visitor = _AuditedMutationVisitor(
        supported_top_level_node_ids,
        module_scope.locals,
    )
    mutation_visitor.visit(tree)

    declared_constants = set(mutation_visitor.declared)
    ambiguous_constants = set(mutation_visitor.ambiguous)
    unresolved_constants: set[str] = set()
    for node in tree.body:
        name: str | None = None
        value_node: ast.AST | None = None
        if isinstance(node, ast.Assign) and len(node.targets) == 1:
            target = node.targets[0]
            if isinstance(target, ast.Name):
                name = target.id
                value_node = node.value
        elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
            name = node.target.id
            value_node = node.value
        if name not in accepted_names or value_node is None:
            continue
        declared_constants.add(name)
        try:
            constants[name] = _canonicalize_literal(ast.literal_eval(value_node))
        except (ValueError, TypeError):
            constants.pop(name, None)
            unresolved_constants.add(name)
            continue
        unresolved_constants.discard(name)

    variants: set[str] = set()
    for name in ("VARIANTS", "VARIANTES"):
        value = constants.get(name, [])
        if isinstance(value, list):
            variants.update(item for item in value if isinstance(item, str))
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Attribute) or node.func.attr != "add_argument":
            continue
        option_names: list[str] = []
        for argument in node.args:
            try:
                literal = ast.literal_eval(argument)
            except (ValueError, TypeError):
                continue
            if isinstance(literal, str):
                option_names.append(literal)
        if "--variant" not in option_names:
            continue
        choices = next(
            (keyword.value for keyword in node.keywords if keyword.arg == "choices"),
            None,
        )
        if choices is None:
            continue
        if isinstance(choices, ast.Name) and choices.id in constants:
            literal_choices = constants[choices.id]
        else:
            try:
                literal_choices = ast.literal_eval(choices)
            except (ValueError, TypeError):
                continue
        if isinstance(literal_choices, (list, tuple, set, frozenset)):
            variants.update(item for item in literal_choices if isinstance(item, str))

    return {
        "ambiguous_constants": sorted(ambiguous_constants),
        "constants": dict(sorted(constants.items())),
        "declared_constants": sorted(declared_constants),
        "latex_inputs": _ast_latex_inputs(tree),
        "unresolved_constants": sorted(unresolved_constants),
        "variants": sorted(variants),
    }


def valid_order(value: Any) -> list[list[str]]:
    if not isinstance(value, list):
        return []
    return [
        [item[0], item[1]]
        for item in value
        if isinstance(item, list)
        and len(item) == 2
        and all(isinstance(part, str) for part in item)
    ]


def _is_valid_variant_order(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and len(valid_order(value)) == len(value)
        and all(part.strip() for rule in value for part in rule)
    )


def _is_valid_book_manifests(value: Any) -> bool:
    return (
        isinstance(value, Mapping)
        and bool(value)
        and all(
            isinstance(manual, str)
            and bool(manual.strip())
            and isinstance(manifest, str)
            and bool(manifest.strip())
            for manual, manifest in value.items()
        )
    )


def validate_analysis(
    path: str,
    analysis: Mapping[str, Any],
) -> list[tuple[str, str]]:
    errors: list[tuple[str, str]] = []
    order = analysis["constants"].get("ORDER")
    if (
        not isinstance(order, list)
        or not order
        or len(valid_order(order)) != len(order)
    ):
        errors.append(("ORDER", "ORDER absent ou invalide"))
    variants = analysis.get("variants")
    if not isinstance(variants, list) or not variants:
        errors.append(("variants", "aucune variante litterale resolue"))
    if path.endswith("/scripts/assemble_manuel.py"):
        constants = analysis["constants"]
        declared_constants = set(analysis.get("declared_constants", constants))
        ambiguous_constants = set(analysis.get("ambiguous_constants", []))
        unresolved_constants = set(analysis.get("unresolved_constants", []))
        unsafe_constants = ambiguous_constants | unresolved_constants
        chapters = constants.get("CHAPITRES")
        valid_chapters = (
            isinstance(chapters, list)
            and bool(chapters)
            and all(
                isinstance(chapter, str) and bool(chapter.strip())
                for chapter in chapters
            )
        )
        book_manifests = constants.get("BOOK_MANIFESTS")
        valid_book_manifests = _is_valid_book_manifests(book_manifests)
        if not valid_chapters and not valid_book_manifests:
            if "BOOK_MANIFESTS" in declared_constants:
                errors.append(
                    (
                        "BOOK_MANIFESTS",
                        "BOOK_MANIFESTS doit etre un mapping litteral ferme non vide",
                    )
                )
            else:
                errors.append(("CHAPITRES", "CHAPITRES absent ou invalide"))
        if "BOOK_MANIFESTS" in unsafe_constants and (
            "BOOK_MANIFESTS" in constants
            or "BOOK_MANIFESTS" in unresolved_constants
        ):
            errors.append(
                (
                    "BOOK_MANIFESTS",
                    "declaration ou mutation BOOK_MANIFESTS hors affectation "
                    "litterale top-level interdite",
                )
            )
        if isinstance(variants, list) and "eleve" in variants:
            student_types = analysis["constants"].get("ELEVE_ALLOWED_TYPES")
            if (
                not isinstance(student_types, list)
                or not student_types
                or not all(isinstance(value, str) and value for value in student_types)
            ):
                errors.append(
                    (
                        "ELEVE_ALLOWED_TYPES",
                        "filtre metadata eleve absent ou invalide",
                    )
                )
        closed_contract = bool(
            declared_constants & {"ELEVE_VARIANTS", "VARIANT_ORDERS"}
        )
        if closed_contract:
            declared_variants = constants.get("VARIANTS")
            variant_orders = constants.get("VARIANT_ORDERS")
            valid_declared_variants = (
                isinstance(declared_variants, list)
                and bool(declared_variants)
                and all(
                    isinstance(value, str) and bool(value.strip())
                    for value in declared_variants
                )
                and len(set(declared_variants)) == len(declared_variants)
                and sorted(declared_variants) == variants
            )
            valid_variant_orders = (
                valid_declared_variants
                and isinstance(variant_orders, Mapping)
                and all(isinstance(key, str) for key in variant_orders)
                and set(variant_orders) == set(declared_variants)
                and all(
                    _is_valid_variant_order(rules)
                    for rules in variant_orders.values()
                )
            )
            if "VARIANT_ORDERS" in unsafe_constants:
                errors.append(
                    (
                        "VARIANT_ORDERS",
                        "declaration ou mutation VARIANT_ORDERS hors affectation "
                        "litterale top-level interdite",
                    )
                )
            elif not valid_variant_orders:
                errors.append(
                    (
                        "VARIANT_ORDERS",
                        "VARIANT_ORDERS doit couvrir exactement VARIANTS avec "
                        "des regles [repertoire, glob] non vides",
                    )
                )
            student_variants = constants.get("ELEVE_VARIANTS")
            valid_student_variants = (
                isinstance(student_variants, list)
                and bool(student_variants)
                and all(
                    isinstance(value, str) and bool(value.strip())
                    for value in student_variants
                )
                and len(set(student_variants)) == len(student_variants)
                and "eleve" in student_variants
                and valid_declared_variants
                and set(student_variants) <= set(declared_variants)
            )
            if "ELEVE_VARIANTS" in unsafe_constants:
                errors.append(
                    (
                        "ELEVE_VARIANTS",
                        "declaration ou mutation ELEVE_VARIANTS hors affectation "
                        "litterale top-level interdite",
                    )
                )
            elif not valid_student_variants:
                errors.append(
                    (
                        "ELEVE_VARIANTS",
                        "ELEVE_VARIANTS doit etre un sous-ensemble non vide de "
                        "VARIANTS contenant eleve",
                    )
                )
            existing_error_fields = {field for field, _reason in errors}
            ignored_runtime_constants = (
                {"CHAPITRES"} if valid_book_manifests else set()
            )
            for name in sorted(
                unsafe_constants
                - {
                    "ELEVE_VARIANTS",
                    "VARIANT_ORDERS",
                    *ignored_runtime_constants,
                }
            ):
                if name in existing_error_fields:
                    continue
                errors.append(
                    (
                        name,
                        f"declaration ou mutation {name} hors affectation "
                        "litterale top-level interdite",
                    )
                )
    return errors


def select_items(
    objects: list[dict[str, Any]],
    order: Any,
    variant: str,
    *,
    exclusions: Any,
    allowed_source_types: Any = None,
    variant_orders: Any = None,
) -> tuple[list[dict[str, Any]], Counter[str]]:
    if variant_orders is not None:
        rules = (
            valid_order(variant_orders.get(variant, []))
            if isinstance(variant_orders, Mapping)
            else []
        )
    elif variant == "methodes":
        rules: list[list[str]] = [["methodes", "*"]]
    elif variant == "remediation":
        rules = [["remediation", "*"]]
    elif variant == "amenagee":
        rules = [["amenagee", "*"]]
    else:
        rules = valid_order(order)
    excluded_directories = (
        {item for item in exclusions if isinstance(item, str)}
        if isinstance(exclusions, list)
        else set()
    )
    allowed_types = (
        {item for item in allowed_source_types if isinstance(item, str)}
        if isinstance(allowed_source_types, list)
        else None
    )
    selected_candidates: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    for directory, pattern in rules:
        if directory in excluded_directories:
            continue
        filename_pattern = pattern + ".tex"
        matches = sorted(
            (
                item
                for item in objects
                if PurePosixPath(item["path"]).parent.name == directory
                and (
                    allowed_types is None
                    or item.get("source_type") in allowed_types
                )
                and fnmatch.fnmatchcase(
                    PurePosixPath(item["path"]).name, filename_pattern
                )
            ),
            key=lambda item: item["path"],
        )
        if directory == "exercices":
            matches = [
                item for item in matches if not item["path"].endswith("-CDP.tex")
            ] + [item for item in matches if item["path"].endswith("-CDP.tex")]
        selected_candidates.extend(matches)
        counts.update(item["path"] for item in matches)
    seen: set[str] = set()
    selected: list[dict[str, Any]] = []
    for item in selected_candidates:
        if item["path"] in seen:
            continue
        seen.add(item["path"])
        selected.append(item)
    duplicates = Counter({path: count for path, count in counts.items() if count > 1})
    return selected, duplicates


def _anomaly(source: str, target: str, field: str, reason: str) -> dict[str, str]:
    return {
        "champ": field,
        "cible": target,
        "raison": reason,
        "source": source,
    }


def _all_objects(inventory: Mapping[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        (
            item
            for manual in inventory["manuals"].values()
            for chapter in manual["chapters"].values()
            for item in chapter["objects"]
        ),
        key=lambda item: item["path"],
    )


def _append_assembly(
    inventory: dict[str, Any],
    *,
    assembly_id: str,
    assembler_path: str,
    manual: str,
    scope: str,
    variant: str,
    chapters: list[str],
    eligible_objects: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    duplicates: Counter[str],
) -> None:
    selected_paths = [item["path"] for item in selected]
    selected_set = set(selected_paths)
    excluded_types = sorted(
        {
            item["source_type"]
            for item in eligible_objects
            if item["path"] not in selected_set
        }
    )
    inventory["assemblies"].append(
        {
            "assembler": assembler_path,
            "assembly_id": assembly_id,
            "chapters": list(chapters),
            "excluded_source_types": excluded_types,
            "included_files": list(selected_paths),
            "included_objects": list(selected_paths),
            "manual": manual,
            "scope": scope,
            "variant": variant,
        }
    )
    for path, count in sorted(duplicates.items()):
        inventory["anomalies"]["duplicate_assembly_objects"].append(
            _anomaly(
                assembler_path,
                path,
                assembly_id,
                f"{count} regles de glob selectionnent le meme objet; "
                "l'assembleur le deduplique",
            )
        )


def _build_chapter_assemblies(
    inventory: dict[str, Any],
    assembler_path: str,
    analysis: dict[str, Any],
    manual: str,
    chapter: str,
    objects: list[dict[str, Any]],
    *,
    assembly_project_name: Callable[[str], str],
) -> None:
    for variant in analysis["variants"]:
        assembly_id = f"{assembly_project_name(manual)}:chapter:{chapter}:{variant}"
        selected, duplicates = select_items(
            objects,
            analysis["constants"].get("ORDER", []),
            variant,
            exclusions=(),
        )
        _append_assembly(
            inventory,
            assembly_id=assembly_id,
            assembler_path=assembler_path,
            manual=manual,
            scope="chapter",
            variant=variant,
            chapters=[chapter],
            eligible_objects=objects,
            selected=selected,
            duplicates=duplicates,
        )


def _build_manual_assemblies(
    inventory: dict[str, Any],
    assembler_path: str,
    analysis: dict[str, Any],
    manual: str,
    chapters: list[str],
    objects_by_chapter: Mapping[str, list[dict[str, Any]]],
    *,
    assembly_project_name: Callable[[str], str],
) -> None:
    constants = analysis["constants"]
    student_excludes = constants.get("ELEVE_EXCLUDES", [])
    student_allowed_types = constants.get("ELEVE_ALLOWED_TYPES")
    variant_orders = constants.get("VARIANT_ORDERS")
    declared_student_variants = constants.get("ELEVE_VARIANTS")
    student_variants = (
        {
            value
            for value in declared_student_variants
            if isinstance(value, str)
        }
        if isinstance(declared_student_variants, list)
        else {"eleve"}
    )
    for variant in analysis["variants"]:
        selected: list[dict[str, Any]] = []
        duplicate_counts: Counter[str] = Counter()
        inclusion_counts: Counter[str] = Counter()
        eligible: list[dict[str, Any]] = []
        is_student_variant = variant in student_variants
        exclusions = student_excludes if is_student_variant else []
        for chapter in chapters:
            chapter_objects = objects_by_chapter.get(chapter, [])
            eligible.extend(chapter_objects)
            chapter_selected, chapter_duplicates = select_items(
                chapter_objects,
                constants.get("ORDER", []),
                variant,
                exclusions=exclusions,
                allowed_source_types=(
                    student_allowed_types if is_student_variant else None
                ),
                variant_orders=variant_orders,
            )
            selected.extend(chapter_selected)
            inclusion_counts.update(item["path"] for item in chapter_selected)
            duplicate_counts.update(chapter_duplicates)
        assembly_id = f"{assembly_project_name(manual)}:manual:{manual}:{variant}"
        _append_assembly(
            inventory,
            assembly_id=assembly_id,
            assembler_path=assembler_path,
            manual=manual,
            scope="manual",
            variant=variant,
            chapters=chapters,
            eligible_objects=eligible,
            selected=selected,
            duplicates=duplicate_counts,
        )
        for selected_path, count in sorted(inclusion_counts.items()):
            if count > 1:
                inventory["anomalies"]["duplicate_assembly_objects"].append(
                    _anomaly(
                        assembler_path,
                        selected_path,
                        assembly_id,
                        f"objet inclus {count} fois car CHAPITRES contient un "
                        "chapitre duplique",
                    )
                )


def _add_dynamic_dependencies(
    inventory: dict[str, Any],
    root: Path,
    tracked: frozenset[str],
    *,
    project_for_manual: Callable[[str], str],
    resolve_latex_target: Callable[[str, str, frozenset[str]], str],
) -> None:
    analyses: dict[str, dict[str, Any]] = {}
    for assembly in inventory["assemblies"]:
        if assembly["scope"] not in {"chapter", "manual"}:
            continue
        dependencies: list[str] = []
        project = project_for_manual(assembly["manual"])
        for chapter in assembly["chapters"]:
            dependencies.append(f"{project}/chapitres/{chapter}/contrat.yaml")
        if assembly["scope"] == "chapter":
            dependencies.append(f"{project}/gabarits/chapitre_master.tex")
        else:
            assembler_path = assembly["assembler"]
            if assembler_path not in analyses:
                try:
                    analyses[assembler_path] = analyze_assembler(root / assembler_path)
                except AssemblyAnalysisError:
                    analyses[assembler_path] = {"latex_inputs": []}
            for _command, raw_target in analyses[assembler_path].get(
                "latex_inputs", []
            ):
                dependencies.append(
                    resolve_latex_target(assembler_path, raw_target, tracked)
                )
        for dependency in dict.fromkeys(dependencies):
            if dependency in tracked and (root / dependency).is_file():
                if dependency not in assembly["included_files"]:
                    assembly["included_files"].append(dependency)
                continue
            inventory["anomalies"]["broken_assembly_references"].append(
                _anomaly(
                    assembly["assembler"],
                    dependency,
                    assembly["assembly_id"],
                    "dependance dynamique d'assemblage absente",
                )
            )


def _read_confined_manifest(root: Path, relative_path: PurePosixPath) -> str:
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    nonblock = getattr(os, "O_NONBLOCK", 0)
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | nofollow
    with ExitStack() as fd_stack:
        try:
            directory_fd = os.open(
                root,
                os.O_RDONLY | getattr(os, "O_DIRECTORY", 0),
            )
        except OSError as exc:
            raise _ManifestConfinementError(
                "racine du depot inaccessible pour le confinement du manifeste"
            ) from exc
        fd_stack.callback(os.close, directory_fd)

        for component in relative_path.parts[:-1]:
            try:
                metadata = os.stat(
                    component,
                    dir_fd=directory_fd,
                    follow_symlinks=False,
                )
            except OSError as exc:
                raise _ManifestConfinementError(
                    "composant parent du manifeste absent ou inaccessible"
                ) from exc
            if stat.S_ISLNK(metadata.st_mode):
                raise _ManifestConfinementError(
                    "composant parent symbolique interdit pour le manifeste"
                )
            if not stat.S_ISDIR(metadata.st_mode):
                raise _ManifestConfinementError(
                    "composant parent non repertoire interdit pour le manifeste"
                )
            try:
                next_fd = os.open(component, directory_flags, dir_fd=directory_fd)
            except OSError as exc:
                raise _ManifestConfinementError(
                    "ouverture confinee d'un parent du manifeste impossible"
                ) from exc
            fd_stack.callback(os.close, next_fd)
            try:
                opened_metadata = os.fstat(next_fd)
            except OSError as exc:
                raise _ManifestConfinementError(
                    "verification confinee d'un parent du manifeste impossible"
                ) from exc
            if (metadata.st_dev, metadata.st_ino) != (
                opened_metadata.st_dev,
                opened_metadata.st_ino,
            ) or not stat.S_ISDIR(opened_metadata.st_mode):
                raise _ManifestConfinementError(
                    "composant parent du manifeste modifie pendant le controle"
                )
            directory_fd = next_fd

        filename = relative_path.parts[-1]
        try:
            metadata = os.stat(
                filename,
                dir_fd=directory_fd,
                follow_symlinks=False,
            )
        except OSError as exc:
            raise _ManifestConfinementError(
                "fichier manifeste absent ou inaccessible"
            ) from exc
        if stat.S_ISLNK(metadata.st_mode):
            raise _ManifestConfinementError("fichier manifeste symbolique interdit")
        if not stat.S_ISREG(metadata.st_mode):
            raise _ManifestConfinementError("fichier manifeste non regulier")
        try:
            manifest_fd = os.open(
                filename,
                os.O_RDONLY | nonblock | nofollow,
                dir_fd=directory_fd,
            )
        except OSError as exc:
            raise _ManifestConfinementError(
                "ouverture confinee du fichier manifeste impossible"
            ) from exc
        manifest_fd_owned = [True]

        def close_owned_manifest_fd() -> None:
            if manifest_fd_owned[0]:
                os.close(manifest_fd)

        fd_stack.callback(close_owned_manifest_fd)
        try:
            opened_metadata = os.fstat(manifest_fd)
        except OSError as exc:
            raise _ManifestConfinementError(
                "verification confinee du fichier manifeste impossible"
            ) from exc
        if (metadata.st_dev, metadata.st_ino) != (
            opened_metadata.st_dev,
            opened_metadata.st_ino,
        ) or not stat.S_ISREG(opened_metadata.st_mode):
            raise _ManifestConfinementError(
                "fichier manifeste modifie pendant le controle"
            )
        stream = os.fdopen(manifest_fd, encoding="utf-8")
        manifest_fd_owned[0] = False
        with stream:
            return stream.read()


def _manifest_backed_chapters(
    root: Path,
    tracked: frozenset[str],
    assembler_path: str,
    analysis: Mapping[str, Any],
    *,
    supported_manuals: set[str],
    manual_for_chapter: Callable[[str], str | None],
) -> tuple[dict[str, list[str]] | None, list[tuple[str, str]]]:
    book_manifests = analysis["constants"].get("BOOK_MANIFESTS")
    if not isinstance(book_manifests, Mapping):
        return None, []

    project_path = PurePosixPath(assembler_path).parent.parent
    chapters_by_manual: dict[str, list[str]] = {}
    errors: list[tuple[str, str]] = []
    for manual, raw_manifest_path in book_manifests.items():
        field = f"BOOK_MANIFESTS[{manual!r}]"
        if manual not in supported_manuals:
            errors.append((field, f"manuel non pris en charge: {manual}"))
            continue
        if not isinstance(raw_manifest_path, str):
            errors.append((field, "chemin de manifeste invalide"))
            continue
        manifest_path = PurePosixPath(raw_manifest_path)
        if manifest_path.is_absolute():
            errors.append((field, "chemin de manifeste absolu interdit"))
            continue
        if ".." in manifest_path.parts:
            errors.append((field, "chemin de manifeste contenant .. interdit"))
            continue
        canonical_manifest_path = f"manifests/books/{manual}.json"
        if raw_manifest_path != canonical_manifest_path:
            errors.append(
                (
                    field,
                    "chemin de manifeste non canonique; "
                    f"attendu {canonical_manifest_path}",
                )
            )
            continue

        repository_manifest = (project_path / manifest_path).as_posix()
        if repository_manifest not in tracked:
            errors.append(
                (field, f"fichier manifeste non suivi par Git: {repository_manifest}")
            )
            continue
        try:
            manifest_text = _read_confined_manifest(
                root,
                PurePosixPath(repository_manifest),
            )
        except _ManifestConfinementError as exc:
            errors.append((field, str(exc)))
            continue
        except UnicodeError:
            errors.append((field, "fichier manifeste illisible"))
            continue
        try:
            manifest = json.loads(manifest_text)
        except json.JSONDecodeError:
            errors.append((field, f"JSON de manifeste invalide: {repository_manifest}"))
            continue
        if not isinstance(manifest, Mapping):
            errors.append((field, f"JSON de manifeste invalide: {repository_manifest}"))
            continue
        if manifest.get("book_id") != manual:
            errors.append(
                (
                    field,
                    f"book_id du manifeste different de la cle {manual}: "
                    f"{manifest.get('book_id')!r}",
                )
            )
            continue

        raw_chapters = manifest.get("chapters")
        if not isinstance(raw_chapters, list) or not raw_chapters:
            errors.append((field, "liste chapters du manifeste absente ou vide"))
            continue
        chapter_ids: list[str] = []
        seen_chapters: set[str] = set()
        manifest_error_count = len(errors)
        for index, chapter in enumerate(raw_chapters):
            chapter_id = chapter.get("id") if isinstance(chapter, Mapping) else None
            chapter_field = f"{field}.chapters[{index}].id"
            if (
                not isinstance(chapter_id, str)
                or not chapter_id.strip()
                or chapter_id != chapter_id.strip()
            ):
                errors.append((chapter_field, "id de chapitre invalide"))
                continue
            if chapter_id in seen_chapters:
                errors.append((chapter_field, f"id de chapitre duplique: {chapter_id}"))
                continue
            if manual_for_chapter(chapter_id) != manual:
                errors.append(
                    (
                        chapter_field,
                        f"id de chapitre invalide pour le manuel {manual}: {chapter_id}",
                    )
                )
                continue
            seen_chapters.add(chapter_id)
            chapter_ids.append(chapter_id)
        if len(errors) == manifest_error_count:
            chapters_by_manual[manual] = chapter_ids

    if errors:
        return {}, errors

    static_chapters = analysis["constants"].get("CHAPITRES")
    if isinstance(static_chapters, list) and static_chapters:
        static_manuals: list[str] = []
        for chapter in static_chapters:
            manual = manual_for_chapter(chapter)
            if manual not in static_manuals:
                static_manuals.append(manual or "")
        runtime_order = [
            chapter
            for manual in static_manuals
            for chapter in chapters_by_manual.get(manual, [])
        ]
        if static_chapters != runtime_order:
            errors.append(
                (
                    "CHAPITRES",
                    "ordre statique CHAPITRES divergent de l'ordre runtime "
                    "des manifests",
                )
            )
            return {}, errors

    return chapters_by_manual, []


def add_declared_assemblies(
    inventory: dict[str, Any],
    root: Path,
    tracked: frozenset[str],
    *,
    source_roles: Mapping[str, str],
    assembler_source_roles: frozenset[str],
    assembler_path_allowlist: frozenset[str],
    manual_ids: tuple[str, ...],
    manual_for_chapter: Callable[[str], str | None],
    supported_manuals: Callable[[str], tuple[str, ...]],
    project_for_manual: Callable[[str], str],
    assembly_project_name: Callable[[str], str],
    chapter_directory: Callable[[str, str], str],
    resolve_latex_target: Callable[[str, str, frozenset[str]], str],
) -> None:
    """Discover assemblers, build variants and compute actual manual coverage."""

    anomalies = inventory["anomalies"]
    objects = _all_objects(inventory)
    objects_by_chapter: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in objects:
        objects_by_chapter[item["path_chapter"]].append(item)
    for chapter_objects in objects_by_chapter.values():
        chapter_objects.sort(key=lambda item: item["path"])

    assembler_paths = sorted(
        path
        for path in tracked
        if path in assembler_path_allowlist
        and source_roles[path] in assembler_source_roles
    )
    analyses: dict[str, dict[str, Any]] = {}
    for path in assembler_paths:
        try:
            analysis = analyze_assembler(root / path)
        except AssemblyAnalysisError as exc:
            anomalies["assembler_invalid"].append(_anomaly(path, path, "AST", str(exc)))
            continue
        validation_errors = validate_analysis(path, analysis)
        if validation_errors:
            anomalies["assembler_invalid"].extend(
                _anomaly(path, path, field, reason)
                for field, reason in validation_errors
            )
            continue
        analyses[path] = analysis

    manual_engine_manuals: set[str] = set()
    chapter_engine_manuals: set[str] = set()
    for path, analysis in sorted(analyses.items()):
        if path.endswith("/scripts/assemble_manuel.py"):
            supported = set(supported_manuals(path))
            manifest_chapters, manifest_errors = _manifest_backed_chapters(
                root,
                tracked,
                path,
                analysis,
                supported_manuals=supported,
                manual_for_chapter=manual_for_chapter,
            )
            if manifest_errors:
                anomalies["assembler_invalid"].extend(
                    _anomaly(path, path, field, reason)
                    for field, reason in manifest_errors
                )
                continue
            if manifest_chapters is None:
                chapters = analysis["constants"].get("CHAPITRES", [])
                if not isinstance(chapters, list):
                    continue
                chapters = [item for item in chapters if isinstance(item, str)]
            else:
                chapters = [
                    chapter
                    for manual in manifest_chapters
                    for chapter in manifest_chapters[manual]
                ]
            grouped: dict[str, list[str]] = defaultdict(list)
            declared_manuals: set[str] = set()
            for index, chapter in enumerate(chapters):
                manual = manual_for_chapter(chapter)
                if manual is None:
                    anomalies["broken_assembly_references"].append(
                        _anomaly(
                            path,
                            chapter,
                            f"CHAPITRES[{index}]",
                            "prefixe de chapitre inconnu dans CHAPITRES",
                        )
                    )
                    continue
                if manual not in supported:
                    anomalies["broken_assembly_references"].append(
                        _anomaly(
                            path,
                            chapter,
                            f"CHAPITRES[{index}]",
                            "chapitre hors du perimetre des manuels pris en "
                            "charge par cet assembleur",
                        )
                    )
                    continue
                declared_manuals.add(manual)
                if chapter not in inventory["manuals"][manual]["chapters"]:
                    anomalies["broken_assembly_references"].append(
                        _anomaly(
                            path,
                            chapter,
                            f"CHAPITRES[{index}]",
                            "chapitre declare par l'assembleur absent des sources suivies",
                        )
                    )
                    continue
                grouped[manual].append(chapter)
            manual_engine_manuals.update(declared_manuals)
            for manual, manual_chapters in sorted(grouped.items()):
                _build_manual_assemblies(
                    inventory,
                    path,
                    analysis,
                    manual,
                    manual_chapters,
                    objects_by_chapter,
                    assembly_project_name=assembly_project_name,
                )
        else:
            supported = supported_manuals(path)
            chapter_engine_manuals.update(supported)
            for manual in supported:
                for chapter in sorted(inventory["manuals"][manual]["chapters"]):
                    _build_chapter_assemblies(
                        inventory,
                        path,
                        analysis,
                        manual,
                        chapter,
                        objects_by_chapter.get(chapter, []),
                        assembly_project_name=assembly_project_name,
                    )

    _add_dynamic_dependencies(
        inventory,
        root,
        tracked,
        project_for_manual=project_for_manual,
        resolve_latex_target=resolve_latex_target,
    )
    manual_covered_chapters: dict[str, set[str]] = defaultdict(set)
    for assembly in inventory["assemblies"]:
        if assembly["scope"] == "manual" and assembly["manual"] in manual_ids:
            manual_covered_chapters[assembly["manual"]].update(assembly["chapters"])

    for manual in sorted(manual_ids):
        project = project_for_manual(manual)
        if manual not in chapter_engine_manuals:
            anomalies["missing_assemblers"].append(
                _anomaly(
                    f"{project}/scripts/assemble.py",
                    manual,
                    "chapitre",
                    "aucun assembleur de chapitre suivi",
                )
            )
        if manual not in manual_engine_manuals:
            anomalies["missing_assemblers"].append(
                _anomaly(
                    f"{project}/scripts/assemble_manuel.py",
                    manual,
                    "manuel",
                    "aucun assembleur de manuel suivi",
                )
            )
        for chapter in sorted(inventory["manuals"][manual]["chapters"]):
            if chapter not in manual_covered_chapters[manual]:
                chapter_model = inventory["manuals"][manual]["chapters"][chapter]
                anomalies["chapters_not_in_manual"].append(
                    _anomaly(
                        chapter_model["contract_path"]
                        or chapter_directory(manual, chapter),
                        chapter,
                        "CHAPITRES",
                        "chapitre absent de tout assemblage de manuel",
                    )
                )


def add_unassembled_objects(inventory: dict[str, Any]) -> None:
    assembled = {
        path
        for assembly in inventory["assemblies"]
        for path in assembly["included_objects"]
    }
    for item in _all_objects(inventory):
        if item["path"] not in assembled:
            inventory["anomalies"]["unassembled_objects"].append(
                _anomaly(
                    item["path"],
                    item["path"],
                    "assemblages_declares",
                    "objet META exclu de tous les assemblages declares",
                )
            )
