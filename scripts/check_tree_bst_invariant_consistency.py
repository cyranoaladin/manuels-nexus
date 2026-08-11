#!/usr/bin/env python3
"""Check tree and BST examples against core invariants."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT


TARGETS = [
    ROOT / "03_progressions" / "supports" / "terminale" / "T05",
    ROOT / "03_progressions" / "supports" / "terminale" / "T06",
    ROOT / "03_progressions" / "fiches_cours" / "terminale" / "T05",
    ROOT / "03_progressions" / "fiches_cours" / "terminale" / "T06",
]


@dataclass
class TreeTraceResult:
    errors: list[str] = field(default_factory=list)
    files_checked: int = 0


@dataclass
class BstNode:
    value: int
    left: "BstNode | None" = None
    right: "BstNode | None" = None


def insert_bst(node: BstNode | None, value: int, *, allow_duplicates: bool = False) -> BstNode:
    if node is None:
        return BstNode(value)
    if value == node.value and not allow_duplicates:
        return node
    if value < node.value:
        node.left = insert_bst(node.left, value, allow_duplicates=allow_duplicates)
    else:
        node.right = insert_bst(node.right, value, allow_duplicates=allow_duplicates)
    return node


def build_bst(values: list[int], *, allow_duplicates: bool = False) -> BstNode | None:
    root: BstNode | None = None
    for value in values:
        root = insert_bst(root, value, allow_duplicates=allow_duplicates)
    return root


def inorder(node: BstNode | None) -> list[int]:
    if node is None:
        return []
    return [*inorder(node.left), node.value, *inorder(node.right)]


def search_bst(node: BstNode | None, value: int) -> bool:
    while node is not None:
        if value == node.value:
            return True
        node = node.left if value < node.value else node.right
    return False


def insertion_values(text: str) -> list[int]:
    match = re.search(r"insertion\s*[:：]\s*([0-9,\s>\-]+)", text, re.I)
    if not match:
        return []
    return [int(value) for value in re.findall(r"\d+", match.group(1))]


def numbers_after(label: str, text: str) -> list[int]:
    match = re.search(rf"{label}\s*[:：]\s*([0-9,\s>\-]+)", text, re.I)
    if not match:
        return []
    return [int(value) for value in re.findall(r"\d+", match.group(1))]


def tree_block_errors(text: str) -> list[str]:
    errors: list[str] = []
    lowered = text.lower()
    if "abr" in lowered or "arbre binaire de recherche" in lowered:
        infix = numbers_after(r"parcours\s+infixe", text)
        if infix and infix != sorted(infix):
            errors.append(f"parcours infixe non trié pour un ABR: {infix}")
        values = insertion_values(text)
        if values and infix:
            expected = inorder(build_bst(values))
            if infix != expected:
                errors.append(f"parcours infixe annoncé {infix} différent de l'ABR reconstruit {expected}")
        rlr_match = re.search(r"racine\s+(\d+).*gauche\s+(\d+).*droite\s+(\d+)", text, re.I | re.S)
        if rlr_match:
            root, left, right = map(int, rlr_match.groups())
            if not (left < root < right):
                errors.append("invariant ABR gauche < racine < droite contredit")
        if "doublon" in lowered and not re.search(r"refus|compteur|droite|gauche|convention", lowered):
            errors.append("cas doublon mentionné sans convention explicite")
    if "arbre vide" in lowered and not re.search(r"none|vide|erreur|renvoie|cas de base", lowered):
        errors.append("cas arbre vide mentionné sans comportement")
    return errors


def tree_block_is_consistent(text: str) -> bool:
    return not tree_block_errors(text)


def candidate_files(root: Path = ROOT) -> list[Path]:
    files: list[Path] = []
    for base in TARGETS:
        if base.exists():
            files.extend(sorted(base.glob("*.md")))
    return files


def analyze_tree_bst_invariant_consistency(root: Path = ROOT) -> TreeTraceResult:
    result = TreeTraceResult()
    for path in candidate_files(root):
        result.files_checked += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        for error in tree_block_errors(text):
            result.errors.append(f"{path.relative_to(root).as_posix()}: {error}")
    return result


def main() -> int:
    result = analyze_tree_bst_invariant_consistency()
    if result.errors:
        print("check_tree_bst_invariant_consistency: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print(f"check_tree_bst_invariant_consistency: PASS ({result.files_checked} fichiers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
