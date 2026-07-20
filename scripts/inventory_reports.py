"""Conservative Markdown-claim extraction for the collection inventory."""

from __future__ import annotations

import re
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any, Callable, Mapping


REPORT_SOURCE_CANDIDATES: tuple[str, ...] = (
    "ETAT_COLLECTION.md",
    "Mathematiques/manuel-maths/DIRECTIVES_EN_COURS.md",
    "Mathematiques/manuel-maths/ETAT_COLLECTION.md",
    "Mathematiques/manuel-maths/MISSION_LOG.md",
    "Mathematiques/manuel-maths/RAPPORT_FINAL_1SPE.md",
    "NSI/DIRECTIVES_EN_COURS.md",
    "NSI/MISSION_LOG.md",
)
HISTORICAL_ROOT_REPORT = "audit/historique/ETAT_COLLECTION_AVANT_P0.md"
GENERATED_REPORT_MARKERS: tuple[str, ...] = (
    "AUTO-GENERE PAR inventory_collection.py",
    "AUTO-GÉNÉRÉ PAR inventory_collection.py",
    "GENERE AUTOMATIQUEMENT PAR inventory_collection.py",
    "GÉNÉRÉ AUTOMATIQUEMENT PAR inventory_collection.py",
)

ClaimResolver = Callable[
    [Mapping[str, Any], str, str], tuple[int | bool | None, str | None, str | None]
]


def report_source_paths(
    repository: Path | str, tracked_files: tuple[str, ...]
) -> tuple[str, ...]:
    """Select hand-written evidence and prevent generated-output recursion."""

    root = Path(repository)
    tracked = frozenset(tracked_files)
    candidates = list(REPORT_SOURCE_CANDIDATES)
    if HISTORICAL_ROOT_REPORT in tracked:
        candidates.remove("ETAT_COLLECTION.md")
        candidates.append(HISTORICAL_ROOT_REPORT)
    return tuple(
        path
        for path in sorted(set(candidates), key=str.casefold)
        if path in tracked and not _is_generated_report(root / path)
    )


def reconcile_reports(
    repository: Path | str,
    inventory: Mapping[str, Any],
    report_paths: tuple[str, ...],
    *,
    resolve_claim: ClaimResolver,
) -> dict[str, Any]:
    """Extract only supported claims and preserve every unresolved one."""

    root = Path(repository)
    claims: list[dict[str, Any]] = []
    for path in report_paths:
        try:
            lines = (root / path).read_text(encoding="utf-8").splitlines()
        except (OSError, UnicodeError) as exc:
            claims.append(
                _claim(
                    path=path,
                    line=0,
                    scope=f"report:{path}",
                    metric="lecture_rapport",
                    declared=True,
                    calculated=None,
                    evidence=None,
                    raw="",
                    reason=f"rapport illisible: {type(exc).__name__}",
                )
            )
            continue
        claims.extend(_extract_markdown_claims(path, lines, inventory, resolve_claim))
    claims.sort(
        key=lambda item: (
            item["path"],
            item["line"],
            item["scope"],
            item["metric"],
            str(item["declared"]),
        )
    )
    unresolved = [claim for claim in claims if claim["etat"] == "ouvert"]
    states = Counter(claim["etat"] for claim in claims)
    return {
        "claims": claims,
        "claims_non_resolues": unresolved,
        "sources": list(report_paths),
        "summary": {
            "confirme": states["confirme"],
            "contredit": states["contredit"],
            "ouvert": states["ouvert"],
        },
    }


def _extract_markdown_claims(
    path: str,
    lines: list[str],
    inventory: Mapping[str, Any],
    resolve_claim: ClaimResolver,
) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    current_manual = _manual_from_report_path(path)
    base_scope = f"manual:{current_manual}" if current_manual else f"report:{path}"
    continuation_scope: str | None = None
    continuation_lines = 0
    table_headers: list[str] | None = None
    for index, raw in enumerate(lines, start=1):
        stripped = raw.strip()
        heading_manual = _manual_from_heading(stripped, path)
        if heading_manual is not None:
            current_manual = heading_manual
            base_scope = f"manual:{current_manual}"
        explicit_scope = _scope_from_line(stripped, inventory, current_manual)
        if explicit_scope is not None:
            continuation_scope = explicit_scope
            continuation_lines = 2
        elif not stripped or (
            continuation_scope is not None
            and not raw[:1].isspace()
            and stripped.startswith(("-", "#", "|", ">"))
        ):
            continuation_scope = None
            continuation_lines = 0

        heading_match = re.search(r"(?i)^#{2,6}\s+chapitres\s*\((\d+)\)\s*$", stripped)
        if heading_match and current_manual:
            claims.append(
                _resolved_claim(
                    inventory,
                    path=path,
                    line=index,
                    scope=f"manual:{current_manual}",
                    metric="chapitres",
                    declared=int(heading_match.group(1)),
                    raw=raw,
                    resolve_claim=resolve_claim,
                )
            )

        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [_clean_markdown(cell) for cell in stripped.strip("|").split("|")]
            normalized_cells = [_normalize_text(cell) for cell in cells]
            if _is_table_separator(cells):
                continue
            if any(cell in {"chapitre", "variante"} for cell in normalized_cells):
                table_headers = normalized_cells
                continue
            if table_headers is not None and len(cells) == len(table_headers):
                claims.extend(
                    _claims_from_table_row(
                        inventory,
                        path,
                        index,
                        raw,
                        table_headers,
                        cells,
                        current_manual,
                        resolve_claim,
                    )
                )
        elif table_headers is not None and stripped:
            table_headers = None

        line_scope = explicit_scope or continuation_scope or base_scope
        claims.extend(
            _inline_numeric_claims(
                inventory,
                path=path,
                line=index,
                scope=line_scope,
                raw=raw,
                resolve_claim=resolve_claim,
            )
        )
        if _is_completeness_assertion(stripped, line_scope):
            claims.append(
                _resolved_claim(
                    inventory,
                    path=path,
                    line=index,
                    scope=line_scope,
                    metric="completude",
                    declared=True,
                    raw=raw,
                    resolve_claim=resolve_claim,
                )
            )
        if explicit_scope is None and continuation_scope is not None:
            continuation_lines -= 1
            if continuation_lines <= 0:
                continuation_scope = None
    return claims


def _claims_from_table_row(
    inventory: Mapping[str, Any],
    path: str,
    line: int,
    raw: str,
    headers: list[str],
    cells: list[str],
    current_manual: str | None,
    resolve_claim: ClaimResolver,
) -> list[dict[str, Any]]:
    claims: list[dict[str, Any]] = []
    row = dict(zip(headers, cells, strict=True))
    label = row.get("chapitre")
    variant = row.get("variante")
    if label is not None:
        if _normalize_text(label) == "total":
            scope = f"manual:{current_manual}" if current_manual else f"report:{path}"
        else:
            chapter = _chapter_from_label(label, inventory, current_manual)
            scope = f"chapter:{chapter}" if chapter else f"unresolved:{label}"
    elif variant is not None:
        scope = (
            f"variant:{current_manual}:{_normalize_text(variant).replace(' ', '_')}"
            if current_manual
            else f"unresolved:{variant}"
        )
    else:
        return claims
    for header, metric in (
        ("exercices", "exercices_principaux"),
        ("corriges", "corriges"),
        ("pages", "pages_compilees"),
        ("pages chap", "pages_compilees"),
        ("verify ok", "verify_assertions"),
    ):
        value = _parse_markdown_integer(row.get(header))
        if value is not None:
            claims.append(
                _resolved_claim(
                    inventory,
                    path=path,
                    line=line,
                    scope=scope,
                    metric=metric,
                    declared=value,
                    raw=raw,
                    resolve_claim=resolve_claim,
                )
            )
    return claims


INLINE_COUNT_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"(?<![\w/])(\d+)\s*(?:ex|exercices?)\b", "exercices_principaux"),
    (r"(?<![\w/])(\d+)\s*corrig(?:e|é)s\b", "corriges"),
    (r"(?<![\w/])(\d+)\s*(?:cdp|coups?\s+de\s+pouce)\b", "coups_de_pouce"),
    (r"(?<![\w/])(\d+)\s*(?:eval|evaluations?|évaluations?)\b", "evaluations"),
    (r"(?<![\w/])(\d+)\s*td\b", "td"),
    (r"(?<![\w/])(\d+)\s*projets?\b", "projets"),
    (r"(?<![\w/])(\d+)\s*chapitres?\b", "chapitres"),
    (r"(?<![\w/])(\d+)\s*(?:tests?|pass)\b", "tests_passes"),
    (r"(?<![\w/])(\d+)\s*(?:p\.|pages?)\b", "pages_compilees"),
    (r"(?<![\w/])(\d+)\s*qcm\b", "qcm_items_declares"),
    (
        r"(?<![\w/])(\d+)\s*(?:rem|remediations?|remédiations?)\b",
        "remediations_items_declares",
    ),
)


def _inline_numeric_claims(
    inventory: Mapping[str, Any],
    *,
    path: str,
    line: int,
    scope: str,
    raw: str,
    resolve_claim: ClaimResolver,
) -> list[dict[str, Any]]:
    normalized = _normalize_text(raw)
    contextual_threshold = "par chapitre" in normalized or "par case" in normalized
    remediation_exercises = bool(re.search(r"\b(?:ex|exercices?)\s+remedi", normalized))
    incremental_exercises = bool(
        re.search(r"\b(?:ex|exercices?)\s+supplement", normalized)
    )
    claims: list[dict[str, Any]] = []
    for pattern, metric in INLINE_COUNT_PATTERNS:
        for match in re.finditer(pattern, raw, flags=re.IGNORECASE):
            effective_metric = metric
            effective_scope = scope
            if metric == "exercices_principaux" and contextual_threshold:
                effective_metric = "seuil_exercices_declares"
                effective_scope = "directive:collection"
            elif metric == "exercices_principaux" and remediation_exercises:
                effective_metric = "exercices_remediation_declares"
            elif metric == "exercices_principaux" and incremental_exercises:
                effective_metric = "exercices_increment_declares"
            claims.append(
                _resolved_claim(
                    inventory,
                    path=path,
                    line=line,
                    scope=effective_scope,
                    metric=effective_metric,
                    declared=int(match.group(1)),
                    raw=raw,
                    resolve_claim=resolve_claim,
                )
            )
    return claims


def _resolved_claim(
    inventory: Mapping[str, Any],
    *,
    path: str,
    line: int,
    scope: str,
    metric: str,
    declared: int | bool,
    raw: str,
    resolve_claim: ClaimResolver,
) -> dict[str, Any]:
    calculated, evidence, reason = resolve_claim(inventory, scope, metric)
    return _claim(
        path=path,
        line=line,
        scope=scope,
        metric=metric,
        declared=declared,
        calculated=calculated,
        evidence=evidence,
        raw=raw,
        reason=reason,
    )


def _claim(
    *,
    path: str,
    line: int,
    scope: str,
    metric: str,
    declared: int | bool,
    calculated: int | bool | None,
    evidence: str | None,
    raw: str,
    reason: str | None,
) -> dict[str, Any]:
    state = (
        "ouvert"
        if calculated is None
        else "confirme"
        if calculated == declared
        else "contredit"
    )
    result = {
        "calculated": calculated,
        "declared": declared,
        "evidence": evidence,
        "etat": state,
        "line": line,
        "metric": metric,
        "path": path,
        "raw": raw,
        "scope": scope,
    }
    if reason is not None:
        result["reason"] = reason
    return result


def _is_generated_report(path: Path) -> bool:
    try:
        prefix = path.read_text(encoding="utf-8")[:4096]
    except (OSError, UnicodeError):
        return False
    normalized = unicodedata.normalize("NFC", prefix).upper()
    return any(marker.upper() in normalized for marker in GENERATED_REPORT_MARKERS)


def _manual_from_report_path(path: str) -> str | None:
    normalized = path.upper()
    if "1SPE" in normalized or normalized.endswith("RAPPORT_FINAL_1SPE.MD"):
        return "1SPE"
    if "TSPE" in normalized:
        return "TSPE_2026_2027"
    return None


def _manual_from_heading(line: str, path: str) -> str | None:
    normalized = _normalize_text(line)
    if (
        "1spe" in normalized
        or "mathematiques premiere" in normalized
        or ("premiere specialite" in normalized and path.startswith("Mathematiques/"))
    ):
        return "1SPE"
    if (
        "tspe" in normalized
        or "mathematiques terminale" in normalized
        or ("terminale specialite" in normalized and path.startswith("Mathematiques/"))
    ):
        return "TSPE_2026_2027"
    if "1nsi" in normalized or (
        "nsi premiere" in normalized and path.startswith("NSI/")
    ):
        return "1NSI"
    if "tnsi" in normalized or (
        "nsi terminale" in normalized and path.startswith("NSI/")
    ):
        return "TNSI"
    return None


def _scope_from_line(
    line: str, inventory: Mapping[str, Any], current_manual: str | None
) -> str | None:
    explicit_ids = re.findall(r"\b(?:1SPE|TSPE|1NSI|TNSI)-[A-Z0-9-]+\b", line)
    known = [
        chapter
        for chapter in explicit_ids
        if _manual_containing_chapter(inventory, chapter) is not None
    ]
    if len(set(known)) == 1:
        return f"chapter:{known[0]}"
    if len(set(known)) > 1:
        return "unresolved:portee_chapitres_ambigue"
    candidates: list[str] = []
    normalized_line = _normalize_text(line)
    manuals = [current_manual] if current_manual else list(inventory["manuals"])
    for manual_id in manuals:
        if manual_id is None:
            continue
        for chapter_id, chapter in inventory["manuals"][manual_id]["chapters"].items():
            if any(
                alias and alias in normalized_line
                for alias in _chapter_aliases(chapter_id, chapter)
            ):
                candidates.append(chapter_id)
    unique = sorted(set(candidates))
    if len(unique) == 1:
        return f"chapter:{unique[0]}"
    if len(unique) > 1:
        return "unresolved:portee_chapitres_ambigue"
    return None


def _chapter_from_label(
    label: str, inventory: Mapping[str, Any], current_manual: str | None
) -> str | None:
    label_tokens = set(_stemmed_tokens(label))
    if not label_tokens:
        return None
    manuals = [current_manual] if current_manual else list(inventory["manuals"])
    matches: list[str] = []
    for manual_id in manuals:
        if manual_id is None:
            continue
        for chapter_id, chapter in inventory["manuals"][manual_id]["chapters"].items():
            for alias in _chapter_aliases(chapter_id, chapter):
                alias_tokens = set(_stemmed_tokens(alias))
                if label_tokens <= alias_tokens or alias_tokens <= label_tokens:
                    matches.append(chapter_id)
                    break
    unique = sorted(set(matches))
    return unique[0] if len(unique) == 1 else None


def _manual_containing_chapter(
    inventory: Mapping[str, Any], chapter_id: str
) -> str | None:
    matches = [
        manual_id
        for manual_id, manual in inventory["manuals"].items()
        if chapter_id in manual["chapters"]
    ]
    return matches[0] if len(matches) == 1 else None


def _chapter_aliases(chapter_id: str, chapter: Mapping[str, Any]) -> tuple[str, ...]:
    prefix = chapter_id.split("-", 1)[0]
    suffix = chapter_id.removeprefix(prefix + "-").replace("-", " ")
    contract = chapter.get("contract")
    title = contract.get("titre") if isinstance(contract, Mapping) else None
    aliases = [suffix]
    if isinstance(title, str):
        aliases.append(title)
    return tuple(_normalize_text(alias) for alias in aliases)


def _stemmed_tokens(value: str) -> tuple[str, ...]:
    tokens: list[str] = []
    for token in _normalize_text(value).split():
        if len(token) > 5 and token.endswith("es"):
            token = token[:-2]
        elif len(token) > 4 and token.endswith(("e", "s")):
            token = token[:-1]
        tokens.append(token)
    return tuple(tokens)


def _normalize_text(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value)
    ascii_letters = "".join(
        char for char in decomposed if not unicodedata.combining(char)
    )
    return " ".join(re.findall(r"[a-z0-9]+", ascii_letters.lower()))


def _clean_markdown(value: str) -> str:
    return value.strip().replace("**", "").replace("__", "").strip()


def _parse_markdown_integer(value: str | None) -> int | None:
    if value is None:
        return None
    match = re.fullmatch(r"\s*~?\s*(\d+)\s*", _clean_markdown(value))
    return int(match.group(1)) if match else None


def _is_table_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def _is_completeness_assertion(line: str, scope: str) -> bool:
    normalized = _normalize_text(line)
    if not (scope.startswith("manual:") or scope.startswith("chapter:")):
        return False
    return bool(
        re.search(r"\bmanuel\s+(?:[a-z0-9]+\s+){0,2}complet\b", normalized)
        or re.search(r"\bpilote\b.*\bcomplet\b", normalized)
    )
