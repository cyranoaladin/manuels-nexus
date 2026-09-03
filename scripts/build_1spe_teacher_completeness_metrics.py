#!/usr/bin/env python3
"""Gate « completude professeur » du manuel 1SPE, en metriques nommees.

Un rapport de release ne doit contenir aucun triplet non nomme. Chaque
metrique de cet artefact porte donc METRIC_NAME, EXPECTED et OBSERVED, et
son EXPECTED est DERIVE des sources, jamais ecrit :

* corriges : tout objet publie d'un type que le corpus declare corrigeable
  (un type est corrigeable des lors qu'un objet de ce type declare
  `corrige_tex`, ou qu'un objet de correction le designe en retour) doit
  avoir une correction publiee cote professeur seulement ;
* cles QCM : chaque question qui declare sa reponse dans le JSON canonique du
  QCM doit voir cette meme reponse dans la zone gardee professeur du TeX ;
* baremes : tout objet publie dont la META declare un total de points doit
  voir, dans sa correction, le porteur de bareme de la charte — macro
  resolue dans les gabarits, pas nommee ici.

Le sens inverse est prouve dans le meme artefact : la variante eleve ne doit
porter ni objet de correction, ni porteur de bareme, ni cle de QCM.

Les PDF candidats ne sont qu'une verification SECONDAIRE, liee par sha256 :
ils sont reconstruits ailleurs, la verite est dans les sources.

Metrique bloquante : TEACHER_MISSING_REQUIRED_CONTENT.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Iterable

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import (  # noqa: E402
    MATH,
    ROOT,
    object_meta,
    published_sources,
    path_digest,
    relative,
    sha256_of,
)

MANUAL = "1SPE"
JSON_TARGET = ROOT / "audit/1SPE_TEACHER_COMPLETENESS_METRICS.json"
MD_TARGET = ROOT / "audit/1SPE_TEACHER_COMPLETENESS_METRICS.md"
CHARTER_ROOT = ROOT / "gabarits"
PDF_DIR = MATH / "build" / "MANUEL_1SPE"

#: Champ META par lequel un objet declare sa propre correction.
FORWARD_LINK = "corrige_tex"
#: Suffixe des champs META par lesquels une correction designe son objet.
BACK_LINK_SUFFIXES = ("_id", "_ref")
#: Un total de points se declare par un champ META numerique dont le nom parle
#: de bareme ou de points. C'est une regle sur la forme des metadonnees, pas
#: une liste d'objets.
GRADED_FIELD = re.compile(r"bar[eè]me|point", re.IGNORECASE)
BAREME_WORD = re.compile(r"bar[eè]me", re.IGNORECASE)
#: Diagnostic uniquement : une repartition de points redigee en prose ne vaut
#: pas le porteur de bareme de la charte, mais dire laquelle des deux manque
#: rend la dette actionnable.
PROSE_MARK = re.compile(r"\b\d+(?:[.,]\d+)?\s*(?:pts?|points?)\b", re.IGNORECASE)

_NEWCOMMAND = re.compile(r"\\newcommand\{\\([A-Za-z]+)\}(?:\[[^\]]*\])*\{")
_TEACHER_CONDITIONAL = "\\ifnxVersionProfesseur"
_ANY_CONDITIONAL = re.compile(r"\\if[a-zA-Z@]*")
_ENDIF = "\\fi"
_SECTION_TITLE = re.compile(r"\\section\*\{([^}]*)\}")
_QCM_KEY_ROW = re.compile(
    r"^\s*(Q\d+)\s*&[^&\\]*&\s*\\textbf\{([A-Za-z0-9]+)\}", re.MULTILINE
)


# ---------------------------------------------------------------------------
# Vocabulaire derive de la charte
# ---------------------------------------------------------------------------
def _macro_bodies(text: str) -> Iterable[tuple[str, str]]:
    for match in _NEWCOMMAND.finditer(text):
        start = match.end() - 1
        depth = 0
        index = start
        while index < len(text):
            char = text[index]
            if char == "\\" and index + 1 < len(text):
                index += 2
                continue
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    break
            index += 1
        yield match.group(1), text[start + 1 : index]


def bareme_carrier_macros(charter_root: Path = CHARTER_ROOT) -> frozenset[str]:
    """Macros de la charte qui composent un bareme."""

    carriers: set[str] = set()
    for path in sorted(charter_root.rglob("*")):
        if path.suffix not in {".cls", ".sty"}:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for name, body in _macro_bodies(text):
            if BAREME_WORD.search(body):
                carriers.add(name)
    if not carriers:
        raise RuntimeError("la charte ne declare aucun porteur de bareme")
    return frozenset(carriers)


# ---------------------------------------------------------------------------
# Lecture de la surface publiee
# ---------------------------------------------------------------------------
class Surface:
    """Published objects of one manual, indexed by the assembler's own view."""

    def __init__(self, manual: str = MANUAL) -> None:
        self.manual = manual
        self.teacher = published_sources(manual, "professeur")
        self.student = published_sources(manual, "eleve")
        self.text = {
            path: path.read_text(encoding="utf-8")
            for path in dict.fromkeys(self.teacher + self.student)
        }
        self.meta = {path: object_meta(text) for path, text in self.text.items()}
        self.student_set = set(self.student)

    def identifier(self, path: Path) -> str | None:
        value = self.meta[path].get("id")
        return value if isinstance(value, str) else None

    def object_type(self, path: Path) -> str | None:
        value = self.meta[path].get("type_objet")
        return value if isinstance(value, str) else None

    def by_identifier(self) -> dict[str, Path]:
        index: dict[str, Path] = {}
        for path in self.teacher:
            identifier = self.identifier(path)
            if identifier:
                index[identifier] = path
        return index

    # -- corrections ------------------------------------------------------
    def back_links(self, path: Path) -> list[str]:
        return [
            value
            for key, value in self.meta[path].items()
            if key.endswith(BACK_LINK_SUFFIXES)
            and isinstance(value, str)
            and value
            and key != "id"
        ]

    def correctable_types(self) -> frozenset[str]:
        """Types the corpus itself declares as requiring a correction."""

        identifiers = self.by_identifier()
        types: set[str] = set()
        for path in self.teacher:
            if self.meta[path].get(FORWARD_LINK):
                declared = self.object_type(path)
                if declared:
                    types.add(declared)
        for path in self.teacher:
            if not self.is_correction(path):
                continue
            for target in self.back_links(path):
                referenced = identifiers.get(target)
                if referenced is not None:
                    declared = self.object_type(referenced)
                    if declared:
                        types.add(declared)
        return frozenset(types)

    def is_correction(self, path: Path) -> bool:
        """A correction is a teacher-only object that points back at another."""

        if path in self.student_set:
            return False
        return bool(self.back_links(path))

    def corrections(self) -> dict[Path, Path | None]:
        """Map every teacher object to its correction, forward link first.

        L'index est reconstruit a chaque appel : la surface reste mutable, et
        un gate ne doit jamais raisonner sur un index perime.
        """

        resolved = {path.resolve(): path for path in self.teacher}
        by_target: dict[str, Path] = {}
        for path in self.teacher:
            if not self.is_correction(path):
                continue
            for target in self.back_links(path):
                by_target.setdefault(target, path)
        index: dict[Path, Path | None] = {}
        for path in self.teacher:
            declared = self.meta[path].get(FORWARD_LINK)
            found: Path | None = None
            if isinstance(declared, str) and declared:
                found = resolved.get((MATH / declared).resolve())
            if found is None:
                identifier = self.identifier(path)
                if identifier:
                    candidate = by_target.get(identifier)
                    found = None if candidate is path else candidate
            index[path] = found
        return index

    def correction_of(self, path: Path) -> Path | None:
        return self.corrections().get(path)

    # -- variantes --------------------------------------------------------
    def student_visible(self, path: Path) -> str:
        return strip_teacher_zones(self.text[path])


def strip_teacher_zones(text: str) -> str:
    """Remove every `\\ifnxVersionProfesseur ... \\fi` region."""

    out: list[str] = []
    index = 0
    while index < len(text):
        start = text.find(_TEACHER_CONDITIONAL, index)
        if start == -1:
            out.append(text[index:])
            break
        out.append(text[index:start])
        depth = 1
        cursor = start + len(_TEACHER_CONDITIONAL)
        while cursor < len(text) and depth:
            if text.startswith(_ENDIF, cursor) and not text[
                cursor + len(_ENDIF) : cursor + len(_ENDIF) + 1
            ].isalpha():
                depth -= 1
                cursor += len(_ENDIF)
                continue
            conditional = _ANY_CONDITIONAL.match(text, cursor)
            if conditional is not None and conditional.group(0) != _ENDIF:
                depth += 1
                cursor = conditional.end()
                continue
            cursor += 1
        index = cursor
    return "".join(out)


def uncommented(text: str) -> str:
    return "\n".join(
        line for line in text.split("\n") if not line.lstrip().startswith("%")
    )


# ---------------------------------------------------------------------------
# Metriques
# ---------------------------------------------------------------------------
def correction_metric(surface: Surface) -> dict[str, Any]:
    types = surface.correctable_types()
    expected: list[Path] = [
        path for path in surface.teacher if surface.object_type(path) in types
    ]
    index = surface.corrections()
    rows: list[dict[str, Any]] = []
    observed = 0
    for path in expected:
        correction = index.get(path)
        leaked = correction is not None and correction in surface.student_set
        if correction is not None and not leaked:
            observed += 1
        else:
            rows.append(
                {
                    "object_id": surface.identifier(path),
                    "object_type": surface.object_type(path),
                    "source_path": relative(path),
                    "correction_path": (
                        relative(correction) if correction is not None else None
                    ),
                    "gap": "CORRECTION_LEAKS_TO_STUDENT" if leaked else "NO_CORRECTION",
                }
            )
    return {
        "METRIC_NAME": "TEACHER_CORRECTION_PER_CORRECTABLE_OBJECT",
        "EXPECTED": len(expected),
        "OBSERVED": observed,
        "EXPECTED_DERIVATION": (
            "objets publies dont le type est declare corrigeable par le corpus "
            f"({', '.join(sorted(types))})"
        ),
        "gaps": rows,
    }


def qcm_key_metric(surface: Surface) -> dict[str, Any]:
    expected = 0
    observed = 0
    rows: list[dict[str, Any]] = []
    for path in surface.teacher:
        canonical = sorted(path.parent.glob(f"{path.stem}.json"))
        if not canonical:
            continue
        payload = json.loads(canonical[0].read_text(encoding="utf-8"))
        questions = payload.get("questions")
        if not isinstance(questions, list):
            continue
        declared = {
            question["id"]: question["correcte"]
            for question in questions
            if isinstance(question, dict)
            and isinstance(question.get("id"), str)
            and isinstance(question.get("correcte"), str)
        }
        if not declared:
            continue
        guarded = _teacher_zone(surface.text[path])
        found = dict(_QCM_KEY_ROW.findall(guarded))
        for question_id, answer in sorted(declared.items()):
            expected += 1
            if found.get(question_id) == answer:
                observed += 1
            else:
                rows.append(
                    {
                        "source_path": relative(path),
                        "canonical_source": relative(canonical[0]),
                        "question": question_id,
                        "declared_answer": answer,
                        "teacher_zone_answer": found.get(question_id),
                        "gap": "KEY_MISSING_OR_DIVERGENT",
                    }
                )
    return {
        "METRIC_NAME": "TEACHER_QCM_ANSWER_KEY_PER_DECLARED_QUESTION",
        "EXPECTED": expected,
        "OBSERVED": observed,
        "EXPECTED_DERIVATION": (
            "questions declarant leur reponse dans le JSON canonique du QCM "
            "publie"
        ),
        "gaps": rows,
    }


def _teacher_zone(text: str) -> str:
    """Concatenation of every teacher-only conditional region of `text`."""

    zones: list[str] = []
    index = 0
    while True:
        start = text.find(_TEACHER_CONDITIONAL, index)
        if start == -1:
            return "\n".join(zones)
        depth = 1
        cursor = start + len(_TEACHER_CONDITIONAL)
        while cursor < len(text) and depth:
            if text.startswith(_ENDIF, cursor) and not text[
                cursor + len(_ENDIF) : cursor + len(_ENDIF) + 1
            ].isalpha():
                depth -= 1
                cursor += len(_ENDIF)
                continue
            conditional = _ANY_CONDITIONAL.match(text, cursor)
            if conditional is not None and conditional.group(0) != _ENDIF:
                depth += 1
                cursor = conditional.end()
                continue
            cursor += 1
        zones.append(text[start:cursor])
        index = cursor


def graded_objects(surface: Surface) -> list[Path]:
    graded: list[Path] = []
    for path in surface.teacher:
        for key, value in surface.meta[path].items():
            if (
                isinstance(value, (int, float))
                and not isinstance(value, bool)
                and GRADED_FIELD.search(key)
            ):
                graded.append(path)
                break
    return graded


def bareme_metric(surface: Surface, carriers: frozenset[str]) -> dict[str, Any]:
    expected = graded_objects(surface)
    index = surface.corrections()
    rows: list[dict[str, Any]] = []
    observed = 0
    for path in expected:
        correction = index.get(path)
        text = surface.text[correction] if correction is not None else ""
        carried = any(f"\\{name}" in text for name in carriers)
        if carried:
            observed += 1
        else:
            rows.append(
                {
                    "object_id": surface.identifier(path),
                    "source_path": relative(path),
                    "correction_path": (
                        relative(correction) if correction is not None else None
                    ),
                    "gap": "NO_CHARTER_BAREME_CARRIER_IN_CORRECTION",
                    "prose_mark_allocation": bool(
                        correction is not None
                        and PROSE_MARK.search(uncommented(surface.text[correction]))
                    ),
                }
            )
    return {
        "METRIC_NAME": "TEACHER_BAREME_PER_GRADED_OBJECT",
        "EXPECTED": len(expected),
        "OBSERVED": observed,
        "EXPECTED_DERIVATION": (
            "objets publies dont la META declare un total de points numerique"
        ),
        "OBSERVED_CARRIER": sorted(f"\\{name}" for name in carriers),
        "gaps": rows,
    }


def student_leak_metrics(
    surface: Surface, carriers: frozenset[str]
) -> list[dict[str, Any]]:
    corrections = [
        relative(path) for path in surface.student if surface.is_correction(path)
    ]
    baremes: list[dict[str, Any]] = []
    keys: list[dict[str, Any]] = []
    for path in surface.student:
        visible = uncommented(surface.student_visible(path))
        for name in sorted(carriers):
            if f"\\{name}" in visible:
                baremes.append({"source_path": relative(path), "carrier": f"\\{name}"})
        for question_id, answer in _QCM_KEY_ROW.findall(visible):
            keys.append(
                {
                    "source_path": relative(path),
                    "question": question_id,
                    "answer": answer,
                }
            )
    return [
        {
            "METRIC_NAME": "STUDENT_VARIANT_CORRECTION_OBJECTS",
            "EXPECTED": 0,
            "OBSERVED": len(corrections),
            "EXPECTED_DERIVATION": (
                "la variante eleve ne publie aucun objet de correction"
            ),
            "gaps": [{"source_path": path} for path in corrections],
        },
        {
            "METRIC_NAME": "STUDENT_VARIANT_BAREME_CARRIERS",
            "EXPECTED": 0,
            "OBSERVED": len(baremes),
            "EXPECTED_DERIVATION": (
                "aucun porteur de bareme de la charte hors zone gardee "
                "professeur dans la variante eleve"
            ),
            "gaps": baremes,
        },
        {
            "METRIC_NAME": "STUDENT_VARIANT_QCM_ANSWER_KEYS",
            "EXPECTED": 0,
            "OBSERVED": len(keys),
            "EXPECTED_DERIVATION": (
                "aucune ligne de cle de correction hors zone gardee professeur "
                "dans la variante eleve"
            ),
            "gaps": keys,
        },
    ]


# ---------------------------------------------------------------------------
# Verification secondaire sur les PDF candidats
# ---------------------------------------------------------------------------
def teacher_only_headings(surface: Surface) -> list[str]:
    """Section titles that only a teacher-guarded zone declares."""

    headings: set[str] = set()
    for path in surface.teacher:
        zone = _teacher_zone(surface.text[path])
        for match in _SECTION_TITLE.finditer(zone):
            title = re.sub(r"\\[A-Za-z]+\s*", "", match.group(1)).strip()
            if title:
                headings.add(title)
    return sorted(headings)


def pdf_secondary_evidence(
    surface: Surface, carriers: frozenset[str]
) -> dict[str, Any]:
    """Read the candidate PDFs, if present, as SECONDARY evidence only."""

    headings = teacher_only_headings(surface)
    base = {
        "evidence_role": "SECONDARY_NON_AUTHORITATIVE",
        "note": (
            "les PDF candidats sont reconstruits par un autre chantier ; ils "
            "sont lus ici a titre de verification secondaire et lies par "
            "sha256, jamais comme preuve de release"
        ),
        "bareme_word_regex": BAREME_WORD.pattern,
        "teacher_only_headings_searched": headings,
    }
    try:
        import fitz  # noqa: PLC0415
    except ImportError:
        return {**base, "status": "PYMUPDF_UNAVAILABLE", "documents": []}
    documents: list[dict[str, Any]] = []
    for path in sorted(PDF_DIR.glob("*.pdf")):
        with fitz.open(path) as document:
            text = "\n".join(page.get_text() for page in document)
            pages = document.page_count
        documents.append(
            {
                "path": relative(path),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "pages": pages,
                "bareme_word_occurrences": len(BAREME_WORD.findall(text)),
                "teacher_only_heading_occurrences": sum(
                    text.count(heading) for heading in headings
                ),
            }
        )
    return {**base, "status": "READ" if documents else "NO_CANDIDATE_PDF",
            "documents": documents}


# ---------------------------------------------------------------------------
# Assemblage
# ---------------------------------------------------------------------------
def build_payload() -> dict[str, Any]:
    surface = Surface(MANUAL)
    carriers = bareme_carrier_macros()
    teacher_metrics = [
        correction_metric(surface),
        qcm_key_metric(surface),
        bareme_metric(surface, carriers),
    ]
    leak_metrics = student_leak_metrics(surface, carriers)
    for metric in teacher_metrics + leak_metrics:
        metric["GAP"] = metric["EXPECTED"] - metric["OBSERVED"]
        metric["STATUS"] = "PASS" if metric["GAP"] == 0 else "FAIL"
    missing = sum(max(metric["GAP"], 0) for metric in teacher_metrics)
    leaks = sum(metric["OBSERVED"] for metric in leak_metrics)
    graded = graded_objects(surface)
    index = surface.corrections()
    cited: set[Path] = set()
    for path in graded:
        cited.add(path)
        correction = index.get(path)
        if correction is not None:
            cited.add(correction)
    for path in surface.teacher:
        canonical = sorted(path.parent.glob(f"{path.stem}.json"))
        if canonical:
            cited.add(path)
            cited.update(canonical)
    return {
        "schema_version": 1,
        "artifact_name": "1SPE_TEACHER_COMPLETENESS_METRICS",
        "generated_by": "scripts/build_1spe_teacher_completeness_metrics.py",
        "manual": MANUAL,
        "scope": (
            "completude de la variante professeur et etancheite de la variante "
            "eleve, etablies sur les sources publiees par l'assembleur"
        ),
        "published_object_counts": {
            "teacher": len(surface.teacher),
            "student": len(surface.student),
        },
        "published_surface_path_digest": path_digest(
            set(surface.teacher) | set(surface.student)
        ),
        "metric_evidence_digest": sha256_of(cited),
        "summary": {
            "TEACHER_MISSING_REQUIRED_CONTENT": missing,
            "STUDENT_TEACHER_ONLY_LEAKS": leaks,
            "GATE": "PASS" if missing == 0 and leaks == 0 else "FAIL",
        },
        "metrics": teacher_metrics + leak_metrics,
        "pdf_secondary_evidence": pdf_secondary_evidence(surface, carriers),
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def render_markdown(payload: dict[str, Any]) -> str:
    summary = payload["summary"]
    lines = [
        "# Gate — completude professeur du manuel 1SPE",
        "",
        f"Genere par `{payload['generated_by']}`.",
        "",
        "| METRIC_NAME | EXPECTED | OBSERVED | GAP | STATUS |",
        "| --- | --- | --- | --- | --- |",
    ]
    for metric in payload["metrics"]:
        lines.append(
            f"| {metric['METRIC_NAME']} | {metric['EXPECTED']} | "
            f"{metric['OBSERVED']} | {metric['GAP']} | {metric['STATUS']} |"
        )
    lines.extend(
        [
            "",
            "| METRIC_NAME | VALEUR |",
            "| --- | --- |",
            "| TEACHER_MISSING_REQUIRED_CONTENT | "
            f"{summary['TEACHER_MISSING_REQUIRED_CONTENT']} |",
            f"| STUDENT_TEACHER_ONLY_LEAKS | {summary['STUDENT_TEACHER_ONLY_LEAKS']} |",
            f"| GATE | {summary['GATE']} |",
            "",
            "## Derivation de chaque EXPECTED",
            "",
        ]
    )
    for metric in payload["metrics"]:
        lines.append(
            f"- `{metric['METRIC_NAME']}` : {metric['EXPECTED_DERIVATION']}"
        )
    lines.extend(["", "## Ecarts", ""])
    any_gap = False
    for metric in payload["metrics"]:
        if not metric["gaps"]:
            continue
        any_gap = True
        lines.extend([f"### {metric['METRIC_NAME']}", ""])
        for gap in metric["gaps"]:
            detail = gap.get("object_id") or gap.get("question") or gap.get(
                "source_path"
            )
            lines.append(f"- `{detail}` — {gap.get('gap', 'LEAK')}")
        lines.append("")
    if not any_gap:
        lines.extend(["Aucun ecart.", ""])
    evidence = payload["pdf_secondary_evidence"]
    lines.extend(
        [
            "## Verification secondaire sur les PDF candidats",
            "",
            f"Role de preuve : `{evidence['evidence_role']}` "
            f"(statut `{evidence['status']}`).",
            "",
        ]
    )
    if evidence["documents"]:
        lines.extend(
            [
                "| PDF | sha256 | pages | occurrences « bareme » | "
                "titres reserves professeur |",
                "| --- | --- | --- | --- | --- |",
            ]
        )
        for document in evidence["documents"]:
            lines.append(
                f"| `{document['path']}` | `{document['sha256']}` | "
                f"{document['pages']} | {document['bareme_word_occurrences']} | "
                f"{document['teacher_only_heading_occurrences']} |"
            )
        lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build_payload()
    expected = {JSON_TARGET: render_json(payload), MD_TARGET: render_markdown(payload)}
    if args.check:
        stale = [
            path
            for path, content in expected.items()
            if not path.exists() or path.read_text(encoding="utf-8") != content
        ]
        for path in stale:
            print(f"STALE_OR_MISSING: {relative(path)}")
        if stale:
            return 1
        summary = payload["summary"]
        print(
            "TEACHER_MISSING_REQUIRED_CONTENT="
            f"{summary['TEACHER_MISSING_REQUIRED_CONTENT']} "
            f"STUDENT_TEACHER_ONLY_LEAKS={summary['STUDENT_TEACHER_ONLY_LEAKS']}"
        )
        return 0 if summary["GATE"] == "PASS" else 1
    for path, content in expected.items():
        path.write_text(content, encoding="utf-8")
        print(f"wrote {relative(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
