#!/usr/bin/env python3
"""Check basic graph algorithm traces for disciplinary contradictions."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re

from scripts._qa_common import ROOT, strip_frontmatter


TARGETS = [
    ROOT / "03_progressions" / "supports" / "terminale" / "T07",
    ROOT / "03_progressions" / "supports" / "terminale" / "T08",
    ROOT / "03_progressions" / "fiches_cours" / "terminale" / "T07",
    ROOT / "03_progressions" / "fiches_cours" / "terminale" / "T08",
]


@dataclass
class GraphTraceResult:
    errors: list[str] = field(default_factory=list)
    files_checked: int = 0


def parse_undirected_edges(text: str) -> dict[str, set[str]]:
    graph: dict[str, set[str]] = {}
    for a, b in re.findall(r"\b([A-Z])\s*-\s*([A-Z])\b", text):
        graph.setdefault(a, set()).add(b)
        graph.setdefault(b, set()).add(a)
    return graph


def bfs_order(graph: dict[str, set[str]], start: str) -> list[str]:
    seen = {start}
    queue = [start]
    order: list[str] = []
    while queue:
        node = queue.pop(0)
        order.append(node)
        for neighbor in sorted(graph.get(node, set())):
            if neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return order


def dfs_order(graph: dict[str, set[str]], start: str) -> list[str]:
    seen: set[str] = set()
    order: list[str] = []

    def visit(node: str) -> None:
        seen.add(node)
        order.append(node)
        for neighbor in sorted(graph.get(node, set())):
            if neighbor not in seen:
                visit(neighbor)

    visit(start)
    return order


def predecessor_map_from_bfs(graph: dict[str, set[str]], start: str) -> dict[str, str]:
    pred: dict[str, str] = {}
    seen = {start}
    queue = [start]
    while queue:
        node = queue.pop(0)
        for neighbor in sorted(graph.get(node, set())):
            if neighbor not in seen:
                seen.add(neighbor)
                pred[neighbor] = node
                queue.append(neighbor)
    return pred


def reconstruct_path(predecessors: dict[str, str], start: str, target: str) -> list[str]:
    path = [target]
    current = target
    while current != start:
        if current not in predecessors:
            return []
        current = predecessors[current]
        path.append(current)
    return list(reversed(path))


def parse_predecessors(text: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for child, parent in re.findall(r"\b([A-Z])\s*<-\s*([A-Z])\b", text):
        result[child] = parent
    for child, parent in re.findall(r"pr[ée]d[ée]cesseur\s+de\s+([A-Z])\s*[:=]\s*([A-Z])", text, flags=re.I):
        result[child] = parent
    return result


def graph_block_errors(text: str) -> list[str]:
    errors: list[str] = []
    text = strip_frontmatter(text)
    graph = parse_undirected_edges(text)
    checked_text = re.sub(r"BFS\s+confondu\s+avec\s+DFS", "", text, flags=re.I)
    checked_text = re.sub(r"^#.*DFS.*$", "", checked_text, flags=re.I | re.M)
    checked_text = re.sub(r"`[^`]*`", "", checked_text)
    lowered = checked_text.lower()
    if "bfs" in lowered and "file" not in lowered:
        errors.append("BFS mentionné sans file")
    if "dfs" in lowered and not re.search(r"pile|récurs|recurs|profondeur|avant retour", lowered):
        errors.append("DFS mentionné sans pile ni récursion")
    if re.search(r"graphe\s+non\s+orient", lowered):
        edges = set(re.findall(r"\b([A-Z])\s*-\s*([A-Z])\b", text))
        for a, b in edges:
            matrix_hint = f"{b},{a}"
            if "matrice" in lowered and matrix_hint in text and (b, a) not in edges:
                errors.append(f"graphe non orienté non symétrique pour {a}-{b}")
    if re.search(r"A\s*-\s*B", text) and re.search(r"B\s*-\s*C", text):
        if re.search(r"chemin\s+reconstruit\s+A\s*->\s*C(?!\s*->|\s*via)", text, re.I):
            errors.append("chemin A -> C reconstruit sans passer par B dans le graphe A-B, B-C")
    predecessors = parse_predecessors(text)
    if graph and predecessors:
        start_match = re.search(r"(?:départ|depart|depuis|source)\s*[:=]?\s*([A-Z])", text, re.I)
        start = start_match.group(1) if start_match else sorted(graph)[0]
        expected_pred = predecessor_map_from_bfs(graph, start)
        for child, parent in predecessors.items():
            if child in expected_pred and expected_pred[child] != parent:
                errors.append(f"prédécesseur incohérent pour {child}: attendu {expected_pred[child]}, trouvé {parent}")
    if graph and "bfs" in lowered:
        order_match = re.search(r"ordre\s+(?:bfs|de découverte|decouverte)\s*[:=]\s*([A-Z](?:\s*[,>]\s*[A-Z])*)", text, re.I)
        if order_match:
            announced = re.findall(r"[A-Z]", order_match.group(1))
            start = announced[0] if announced else sorted(graph)[0]
            expected = bfs_order(graph, start)
            if announced != expected[: len(announced)]:
                errors.append(f"ordre BFS incohérent: annoncé {announced}, attendu {expected}")
    if graph and re.search(r"chemin\s+reconstruit", text, re.I):
        path_match = re.search(r"chemin\s+reconstruit\s*[:=]?\s*([A-Z](?:\s*->\s*[A-Z])*)", text, re.I)
        if path_match:
            path = re.findall(r"[A-Z]", path_match.group(1))
            for a, b in zip(path, path[1:]):
                if b not in graph.get(a, set()):
                    errors.append(f"chemin reconstruit invalide: arête absente {a}-{b}")
    if re.search(r"cycle\s+(?:présent|existe|déclaré)", lowered):
        if not re.search(r"\b[A-Z]\s*-\s*[A-Z].*\b[A-Z]\s*-\s*[A-Z].*\b[A-Z]\s*-\s*[A-Z]", text, re.S):
            errors.append("cycle déclaré sans arêtes suffisantes pour le vérifier")
    return errors


def graph_block_is_consistent(text: str) -> bool:
    return not graph_block_errors(text)


def candidate_files(root: Path = ROOT) -> list[Path]:
    files: list[Path] = []
    for base in TARGETS:
        if base.exists():
            files.extend(sorted(base.glob("*.md")))
    return files


def analyze_graph_algorithm_trace_consistency(root: Path = ROOT) -> GraphTraceResult:
    result = GraphTraceResult()
    for path in candidate_files(root):
        result.files_checked += 1
        text = path.read_text(encoding="utf-8", errors="replace")
        for error in graph_block_errors(text):
            result.errors.append(f"{path.relative_to(root).as_posix()}: {error}")
    return result


def main() -> int:
    result = analyze_graph_algorithm_trace_consistency()
    if result.errors:
        print("check_graph_algorithm_trace_consistency: KO")
        for error in result.errors[:160]:
            print(f"- {error}")
        return 1
    print(f"check_graph_algorithm_trace_consistency: PASS ({result.files_checked} fichiers)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
