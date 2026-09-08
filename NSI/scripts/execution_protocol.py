"""Observable NSI assertions and literal published-code dependencies.

This protocol certifies executed assertions/traces, not historical claims or
complete program correctness. An AST match binds a published listing to a
loaded program; it does not prove that a function body or each branch ran.
Network isolation comes from the existing Nexus
review sandbox; no less confined fallback is used.
"""
from __future__ import annotations

import ast
import hashlib
import json
from pathlib import Path
import re
import uuid

PROTOCOL = 'NSI_EXECUTED_CLAIMS_V1'
VERIFY = re.compile(r"% BEGIN-VERIFY\n(.*?)% END-VERIFY", re.S)
TRACE = re.compile(r"% BEGIN-TRACE\n(.*?)% EXPECTED\n(.*?)% END-TRACE", re.S)
PYENV = re.compile(r"\\begin\{python\}(.*?)\\end\{python\}", re.S)
SOURCE_REFERENCE = re.compile(r'^% PYTHON-SOURCE:[ \t]*([^\s]+)[ \t]*$', re.M)
CHECKED_ASSERTIONS = r'''
import ast, json
program = PROGRAM_LITERAL
counts = {"assertions_executed": 0, "failed_assertions": 0}
class Watch(ast.NodeTransformer):
    def visit_Assert(self, node):
        self.generic_visit(node)
        def call(name):
            return ast.Expr(value=ast.Call(func=ast.Name(id=name, ctx=ast.Load()), args=[], keywords=[]))
        return ast.copy_location(ast.Try(body=[call("__nexus_start__"), node],
            handlers=[ast.ExceptHandler(type=ast.Name(id="__nexus_exception__", ctx=ast.Load()),
                name=None, body=[call("__nexus_fail__"), ast.Raise()])], orelse=[], finalbody=[]), node)
def start():
    counts["assertions_executed"] += 1
def fail():
    counts["failed_assertions"] += 1
tree = Watch().visit(ast.parse(program))
ast.fix_missing_locations(tree)
namespace = {"__name__": "__main__", "__nexus_start__": start, "__nexus_fail__": fail, "__nexus_exception__": BaseException}
exec(compile(tree, "<nsi-verify>", "exec"), namespace)
if not counts["assertions_executed"] or counts["failed_assertions"]:
    raise RuntimeError("no exercised assertion or absorbed assertion failure")
print(COMPLETION_MARKER + json.dumps(counts))
'''


def digest(data: bytes) -> str:
    return 'sha256:' + hashlib.sha256(data).hexdigest()


def checked_assertions(program, runner, timeout=30):
    marker = 'NEXUS_COMPLETED_' + uuid.uuid4().hex + ':'
    wrapped = CHECKED_ASSERTIONS.replace('COMPLETION_MARKER', repr(marker)).replace('PROGRAM_LITERAL', repr(program))
    rc, stdout, stderr = runner(wrapped, timeout=timeout)
    lines = stdout.splitlines()
    if rc or not lines or not lines[-1].startswith(marker):
        return {'pass': False, 'assertions_executed': None,
                'detail': (stderr or stdout or 'execution ended before completion')[-1200:]}
    try:
        counts = json.loads(lines[-1][len(marker):])
    except (ValueError, TypeError):
        return {'pass': False, 'assertions_executed': None, 'detail': 'invalid checked completion'}
    ok = counts.get('assertions_executed', 0) > 0 and counts.get('failed_assertions') == 0
    return {'pass': ok, **counts, 'detail': '' if ok else 'incomplete assertions'}


def completed_trace(program, runner, timeout=30):
    marker = 'NEXUS_COMPLETED_' + uuid.uuid4().hex
    wrapped = ('import sys\n' + f'exec(compile({program!r}, "<nsi-trace>", "exec"), '
               '{"__name__": "__main__"})\n' + f'sys.stdout.write({marker!r})\n')
    rc, out, err = runner(wrapped, timeout=timeout)
    completed = rc == 0 and out.endswith(marker)
    return completed, out[:-len(marker)] if completed else out, err


def ast_statements(program):
    return [ast.dump(node, include_attributes=False) for node in ast.parse(program).body]


def linked_to_executed_program(listing, programs):
    try:
        required = ast_statements(listing)
        candidates = [ast_statements(program) for program in programs]
    except SyntaxError:
        return False
    return bool(required) and any(
        required == candidate[start:start + len(required)]
        for candidate in candidates for start in range(len(candidate) - len(required) + 1))


def source_dependencies(tex: Path, text: str, root: Path):
    chapter = next((parent for parent in tex.parents if parent.parent.name == 'chapitres'), tex.parent)
    manifest, checks, programs = {}, [], {}
    if len(re.findall(r'^%\s*PYTHON-SOURCE\b', text, re.M)) != len(SOURCE_REFERENCE.findall(text)):
        checks.append({'type': 'printed_source_alignment', 'pass': False,
                       'reason': 'MALFORMED_PYTHON_SOURCE', 'detail': 'malformed Python source reference'})
    for relative in SOURCE_REFERENCE.findall(text):
        candidates = {(base / relative).resolve() for base in (chapter, tex.parent, root)}
        candidates = {p for p in candidates if p.is_relative_to(root.resolve()) and p.is_file()}
        if len(candidates) != 1:
            checks.append({'type': 'printed_source_alignment', 'pass': False,
                           'detail': f'missing, outside or ambiguous Python source: {relative}'})
            continue
        path = candidates.pop()
        data = path.read_bytes()
        key = path.relative_to(root.resolve()).as_posix()
        manifest[key] = digest(data)
        try:
            programs[key] = ast_statements(data.decode())
        except (UnicodeError, SyntaxError):
            checks.append({'type': 'printed_source_alignment', 'pass': False,
                           'source': key, 'detail': 'Python source cannot be parsed'})
    for index, listing in enumerate(PYENV.findall(text)):
        try:
            required = ast_statements(listing)
            matches = [path for path, statements in programs.items() if required and statements == required]
        except SyntaxError:
            matches = []
        checks.append({'type': 'printed_source_alignment', 'index': index, 'pass': bool(matches),
                       'matching_sources': matches,
                       'reason': None if matches else 'MISSING_PUBLISHED_SOURCE',
                       'detail': '' if matches else 'published listing has no identical explicitly referenced Python source'})
    return manifest, checks


def implementation_manifest(repository: Path):
    names = ('NSI/scripts/verify_python.py', 'NSI/scripts/execution_protocol.py',
             'NSI/scripts/common.py', 'scripts/review_1nsi_content.py')
    return {name: digest((repository / name).read_bytes()) for name in names}


def complete_marker_sets(text):
    return (text.count('% BEGIN-VERIFY') == text.count('% END-VERIFY') == len(VERIFY.findall(text))
            and text.count('% BEGIN-TRACE') == text.count('% END-TRACE') == len(TRACE.findall(text))
            and text.count(r'\begin{python}') == text.count(r'\end{python}') == len(PYENV.findall(text)))


def current_evidence(receipt, source, manual_root, repository):
    """Validate method/dependency binding without executing the source."""
    if receipt.get('verification_protocol') != PROTOCOL:
        return 'UNTRUSTED_NSI_VERIFICATION_METHOD'
    try:
        implementation = implementation_manifest(repository)
        if receipt.get('implementation_digests') != implementation:
            return 'STALE_NSI_IMPLEMENTATION_DIGESTS'
        if receipt.get('verifier_sha256') != implementation['NSI/scripts/verify_python.py']:
            return 'STALE_VERIFIER_DIGEST'
        text = source.read_text()
        dependencies, alignment = source_dependencies(source, text, manual_root)
    except (OSError, UnicodeError):
        return 'UNTRUSTED_NSI_INPUT_UNAVAILABLE'
    if receipt.get('dependency_digests') != dependencies:
        return 'STALE_NSI_DEPENDENCY_DIGESTS'
    if receipt.get('certifies_documentary_claims') is not False or receipt.get('certifies_complete_program_correctness') is not False:
        return 'UNSUPPORTED_NSI_CERTIFICATION_SCOPE'
    if receipt.get('verdict') == 'pass':
        checks = receipt.get('details', {}).get('checks')
        if (not isinstance(checks, list) or not all(isinstance(c, dict) for c in checks)
                or not complete_marker_sets(text) or any(c.get('pass') is False for c in checks + alignment)):
            return 'UNTRUSTED_NSI_EXECUTION_OBSERVATIONS'
        source_checks = [c for c in checks if c.get('type') == 'python_source_execution']
        if (sorted(c.get('source', '') for c in source_checks) != sorted(dependencies)
                or any(c.get('state') != 'LINKED_TO_EXECUTED_PROGRAM' for c in source_checks)):
            return 'UNTRUSTED_NSI_UNEXECUTED_DEPENDENCY'
        for kind, pattern in [('verify', VERIFY), ('trace', TRACE), ('listing_execution', PYENV)]:
            rows = [c for c in checks if c.get('type') == kind]
            if [c.get('index') for c in rows] != list(range(len(pattern.findall(text)))):
                return 'UNTRUSTED_NSI_EXECUTION_OBSERVATIONS'
            if kind == 'listing_execution':
                if any(c.get('state') != 'LINKED_TO_EXECUTED_PROGRAM' for c in rows):
                    return 'UNTRUSTED_NSI_UNEXECUTED_LISTING'
            elif any(c.get('pass') is not True for c in rows):
                return 'UNTRUSTED_NSI_EXECUTION_OBSERVATIONS'
            if kind == 'verify' and any(type(c.get('assertions_executed')) is not int or c['assertions_executed'] < 1
                                       or c.get('failed_assertions') != 0 for c in rows):
                return 'UNTRUSTED_NSI_EXECUTION_OBSERVATIONS'
        if not VERIFY.search(text) and not TRACE.search(text):
            return 'UNTRUSTED_NSI_EXECUTION_OBSERVATIONS'
    return 'CURRENT_TRUSTED'
