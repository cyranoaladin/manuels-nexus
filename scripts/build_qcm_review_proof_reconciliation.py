#!/usr/bin/env python3
"""Reconcilie la preuve de revue independante des QCM avec le corpus courant.

La preuve historique lie chaque ligne au sha256 du FICHIER ENTIER. Une
modification d'une seule question perime donc toutes les lignes du fichier :
la campagne C6/C7 de VARALEA, qui a ajoute six questions, a ainsi invalide les
quinze lignes historiques du chapitre alors que quatorze d'entre elles ne
changeaient que d'accents et de position de cle.

Ce producteur ne rebinde rien et n'approuve rien. Il etablit, par identifiant
exact et non par simple denombrement :

* les questions dont l'identite SEMANTIQUE est inchangee, dont la preuve
  historique peut etre reportee (CARRIED_FORWARD_UNCHANGED) ;
* les questions dont la preuve doit etre refaite (REPROOF_REQUIRED), avec la
  classification exacte de leur delta ;
* les lacunes de COUVERTURE de la preuve historique, c'est-a-dire les champs
  que la preuve n'a jamais captures et que le verificateur courant ne compare
  pas non plus.

Contrat d'identite semantique. Le condense porte sur ce que la preuve atteste
reellement : capacite, enonce, ENSEMBLE des options, VALEUR de la bonne
reponse, et modele d'erreur attache a chaque option par sa valeur.

Il est insensible aux accents, la campagne diacritiques etant une correction
editoriale mandatee qui ne change aucune mathematique. Il est insensible aussi
a la POSITION des options : le reequilibrage des cles deplace la bonne reponse
d'une lettre a l'autre sans toucher a l'enonce, aux options, a la valeur
correcte ni aux diagnostics. Indexer par la lettre faisait perdre la preuve de
245 questions pour un reordonnancement purement editorial.

Il reste sensible a toute option ajoutee, retiree ou modifiee, a tout
changement de la VALEUR correcte et a tout modele d'erreur.

Le champ `renvoi` est exclu du condense : les partitions historiques ne l'ont
pas capture de facon homogene, certaines lignes portant `remediation_reference:
null` alors que le fichier qu'elles lient porte bien un renvoi. L'ecart est
signale comme lacune de couverture, jamais absorbe en silence.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "audit" / "qcm_review_evidence"
QCM_ROOT = ROOT / "Mathematiques" / "manuel-maths" / "chapitres"
#: Les QCM NSI existent depuis la campagne de redaction : les laisser hors du
#: corpus ferait declarer NO_QCM a des chapitres qui en portent un, et leurs
#: questions echapperaient au routage de preuve. Elles y entrent donc, comme
#: toute question jamais prouvee -- ce qui augmente la dette, sans la reduire.
QCM_ROOTS = (QCM_ROOT, ROOT / "NSI" / "chapitres")
JSON_TARGET = ROOT / "audit" / "QCM_REVIEW_PROOF_RECONCILIATION.json"
MD_TARGET = ROOT / "audit" / "QCM_REVIEW_PROOF_RECONCILIATION.md"

#: Les partitions historiques, avec leur cardinal attendu.
PARTITIONS = (
    ("1SPE", EVIDENCE / "1SPE_162.json", 162),
    ("TSPE", EVIDENCE / "TSPE_96.json", 96),
    ("TCOMPL_TEXPERTES", EVIDENCE / "TCOMPL_TEXPERTES_73.json", 73),
)

#: Chapitre dont la campagne C6/C7 impose une nouvelle preuve integrale : les
#: six questions ajoutees changent le perimetre du chapitre, et une preuve
#: partielle laisserait un QCM publie dont une partie n'a jamais ete resolue
#: independamment.
FULL_REPROOF_CHAPTERS = ("1SPE-VARIABLES-ALEATOIRES",)


class ReconciliationError(RuntimeError):
    """Leve quand les entrees ne permettent pas une reconciliation exacte."""


def _normalise(value: Any) -> str:
    """Texte comparable : accents retires, espaces normalises."""

    decomposed = unicodedata.normalize("NFD", str(value))
    stripped = "".join(
        char for char in decomposed if unicodedata.category(char) != "Mn"
    )
    return re.sub(r"\s+", " ", stripped).strip()


def _declared_answer(row: dict[str, Any]) -> str:
    answer = row.get("declared_answer") or row.get("declared_answer_current_source")
    if not isinstance(answer, str):
        raise ReconciliationError(
            f"reponse declaree absente: {row.get('chapter')}/{row.get('question_id')}"
        )
    return answer


def _proof_error_models(row: dict[str, Any]) -> dict[str, str]:
    """Les modeles d'erreur, quelle que soit la forme de la partition."""

    details = row.get("diagnostic_details")
    if isinstance(details, dict):
        return {
            letter: _normalise(entry.get("explanation"))
            for letter, entry in details.items()
        }
    listed = row.get("diagnostics")
    if isinstance(listed, list):
        return {
            entry["option"]: _normalise(entry.get("error_model")) for entry in listed
        }
    return {}


def _proof_renvois(row: dict[str, Any]) -> dict[str, Any]:
    details = row.get("diagnostic_details")
    if isinstance(details, dict):
        return {
            letter: entry.get("remediation_reference")
            for letter, entry in details.items()
        }
    listed = row.get("diagnostics")
    if isinstance(listed, list):
        return {
            entry["option"]: entry.get("remediation_reference") for entry in listed
        }
    return {}


def _source_error_models(question: dict[str, Any]) -> dict[str, str]:
    return {
        letter: _normalise(entry.get("erreur"))
        for letter, entry in (question.get("diagnostics") or {}).items()
    }


def _source_renvois(question: dict[str, Any]) -> dict[str, Any]:
    return {
        letter: entry.get("renvoi")
        for letter, entry in (question.get("diagnostics") or {}).items()
    }


def _by_value(
    options: dict[str, str], attached: dict[str, Any]
) -> dict[str, Any]:
    """Ce qui est attache a une option, indexe par sa VALEUR et non sa lettre."""

    return {
        _normalise(value): attached.get(letter)
        for letter, value in options.items()
        if attached.get(letter) is not None
    }


def _semantic_fields_from_proof(row: dict[str, Any]) -> dict[str, Any]:
    options = {letter: _normalise(value) for letter, value in row["options"].items()}
    key = _declared_answer(row)
    return {
        "capacity": _normalise(row["capacity"]),
        "statement": _normalise(row["statement"]),
        "option_values": sorted(options.values()),
        "correct_value": options[key],
        "error_models_by_value": _by_value(row["options"], _proof_error_models(row)),
    }


def _semantic_fields_from_source(question: dict[str, Any]) -> dict[str, Any]:
    options = {
        letter: _normalise(value) for letter, value in question["options"].items()
    }
    key = question["correcte"]
    return {
        "capacity": _normalise(question["capacite"]),
        "statement": _normalise(question["enonce"]),
        "option_values": sorted(options.values()),
        "correct_value": options[key],
        "error_models_by_value": _by_value(
            question["options"], _source_error_models(question)
        ),
    }


def semantic_question_digest(fields: dict[str, Any]) -> str:
    """Condense content-addressed d'une question, independant du fichier.

    Independant AUSSI de la position des options. Une permutation ne change ni
    l'enonce, ni l'ensemble des options, ni la VALEUR de la bonne reponse, ni
    le diagnostic attache a chaque option : elle ne change que la lettre qui
    les designe. Indexer par la lettre ferait perdre la preuve de 245
    questions pour un simple reordonnancement editorial.
    """

    payload = json.dumps(fields, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


def current_question_digest(question: dict[str, Any]) -> str:
    """Bind the exact current payload, including letters, order and accents.

    Historical semantic identity deliberately tolerates editorial changes and
    omits references not captured then. A stored current letter or full review
    cannot inherit those tolerances. Ordered options remain explicit even when
    the enclosing JSON object is serialized with sorted keys.
    """
    fields = dict(question)
    fields["options"] = list(question["options"].items())
    return semantic_question_digest(fields)


def proof_row_options(row: dict[str, Any]) -> dict[str, str]:
    return dict(row["options"])


def _classify_delta(
    proof_fields: dict[str, Any], source_fields: dict[str, Any],
    proof_row: dict[str, Any], question: dict[str, Any],
) -> list[str]:
    """Classification exacte du delta, selon les classes de la gouvernance."""

    classes: list[str] = []

    if proof_fields["capacity"] != source_fields["capacity"]:
        classes.append("CAPACITY_CHANGE")

    if proof_row["statement"] != question["enonce"]:
        if proof_fields["statement"] == source_fields["statement"]:
            classes.append("ACCENT_ONLY")
        else:
            classes.append("STATEMENT_SEMANTIC_CHANGE")

    if proof_fields["option_values"] != source_fields["option_values"]:
        classes.append("DISTRACTOR_SEMANTIC_CHANGE")
    elif proof_row_options(proof_row) != question["options"]:
        classes.append("OPTION_REORDER_ONLY")

    if proof_fields["correct_value"] != source_fields["correct_value"]:
        classes.append("KEY_VALUE_CHANGED")
    elif _declared_answer(proof_row) != question["correcte"]:
        classes.append("KEY_POSITION_CHANGED_BUT_VALUE_SAME")

    if proof_fields["error_models_by_value"] != source_fields["error_models_by_value"]:
        classes.append("DIAGNOSTIC_TEXT_CHANGE")

    return classes or ["OTHER"]


def _load_proof(root: Path | None = None) -> dict[tuple[str, str], dict[str, Any]]:
    proof: dict[tuple[str, str], dict[str, Any]] = {}
    for name, path, expected in PARTITIONS:
        if root is not None:
            path = root / path.relative_to(ROOT)
        if not path.is_file():
            raise ReconciliationError(f"partition absente: {path}")
        rows = json.loads(path.read_text(encoding="utf-8"))["questions"]
        if len(rows) != expected:
            raise ReconciliationError(
                f"{name}: {len(rows)} lignes, {expected} attendues"
            )
        for row in rows:
            key = (row["chapter"], row["question_id"])
            if key in proof:
                raise ReconciliationError(f"ligne de preuve dupliquee: {key}")
            proof[key] = row
    return proof


def _qcm_sources(root: Path | None = None) -> tuple[Path, ...]:
    """Inventory every QCM source, including documents with no questions."""
    roots = QCM_ROOTS if root is None else tuple(root / path.relative_to(ROOT) for path in QCM_ROOTS)
    return tuple(
        path for racine in roots for path in sorted(racine.glob("*/qcm/*-QCM.json"))
    )


def _load_corpus(root: Path | None = None) -> dict[tuple[str, str], tuple[dict[str, Any], str]]:
    corpus: dict[tuple[str, str], tuple[dict[str, Any], str]] = {}
    actual_root = root or ROOT
    for path in _qcm_sources(root):
        document = json.loads(path.read_text(encoding="utf-8"))
        relative = path.relative_to(actual_root).as_posix()
        for question in document["questions"]:
            key = (document["chapitre"], question["id"])
            if key in corpus:
                raise ReconciliationError(f"question dupliquee dans le corpus: {key}")
            corpus[key] = (question, relative)
    return corpus


def build_reconciliation(root: Path | None = None) -> dict[str, Any]:
    proof = _load_proof(root)
    corpus = _load_corpus(root)

    orphan_proof_rows = sorted(f"{c}/{q}" for c, q in set(proof) - set(corpus))

    historical_not_current = [
        {
            "chapter": chapter, "question_id": question_id,
            "source_path": proof[(chapter, question_id)]["source_path"],
            "proof_semantic_digest": semantic_question_digest(
                _semantic_fields_from_proof(proof[(chapter, question_id)])
            ),
            "state": "HISTORICAL_NOT_CURRENT",
            "current_scientific_credit": False,
            "reason": "QUESTION_ABSENT_FROM_CURRENT_CORPUS",
        }
        for chapter, question_id in sorted(set(proof) - set(corpus))
    ]

    carried: list[dict[str, Any]] = []
    reproof: list[dict[str, Any]] = []
    coverage_gaps: list[dict[str, Any]] = []

    for key in sorted(corpus):
        chapter, question_id = key
        question, source_path = corpus[key]
        source_fields = _semantic_fields_from_source(question)
        digest = semantic_question_digest(source_fields)
        row = proof.get(key)

        if row is None:
            reproof.append(
                {
                    "chapter": chapter,
                    "question_id": question_id,
                    "source_path": source_path,
                    "current_semantic_digest": digest,
                    "reason": "NEW_QUESTION_NEVER_PROVEN",
                    "delta_classes": [],
                }
            )
            continue

        proof_fields = _semantic_fields_from_proof(row)
        proof_digest = semantic_question_digest(proof_fields)
        identical = proof_digest == digest

        # Indexe par VALEUR d'option : apres un reequilibrage des cles, la
        # lettre a change sans que le renvoi ait bouge. Comparer par lettre
        # ferait apparaitre une lacune la ou il n'y en a pas.
        proof_renvois = _by_value(row["options"], _proof_renvois(row))
        source_renvois = _by_value(question["options"], _source_renvois(question))
        uncaptured = sorted(
            option_value
            for option_value, value in source_renvois.items()
            if value is not None and proof_renvois.get(option_value) is None
        )
        if uncaptured:
            coverage_gaps.append(
                {
                    "chapter": chapter,
                    "question_id": question_id,
                    "field": "diagnostics.renvoi",
                    "options": uncaptured,
                    "note": (
                        "la source porte un renvoi que la preuve historique n'a "
                        "jamais capture ; le verificateur courant ne compare pas "
                        "ce champ"
                    ),
                }
            )

        forced = chapter in FULL_REPROOF_CHAPTERS
        if identical and not forced:
            carried.append(
                {
                    "chapter": chapter,
                    "question_id": question_id,
                    "source_path": source_path,
                    "semantic_digest": digest,
                    "status": "CARRIED_FORWARD_UNCHANGED",
                }
            )
            continue

        reproof.append(
            {
                "chapter": chapter,
                "question_id": question_id,
                "source_path": source_path,
                "current_semantic_digest": digest,
                "proof_semantic_digest": proof_digest,
                "reason": (
                    "CHAPTER_SCOPE_CHANGED_FULL_REPROOF"
                    if identical and forced
                    else "SEMANTIC_CHANGE"
                ),
                "delta_classes": (
                    []
                    if identical
                    else _classify_delta(proof_fields, source_fields, row, question)
                ),
            }
        )

    aggregate = hashlib.sha256()
    for entry in sorted(
        carried + reproof, key=lambda item: (item["chapter"], item["question_id"])
    ):
        aggregate.update(f"{entry['chapter']}/{entry['question_id']}".encode("utf-8"))
        aggregate.update(b"\0")
        aggregate.update(
            (entry.get("semantic_digest") or entry["current_semantic_digest"]).encode(
                "utf-8"
            )
        )
        aggregate.update(b"\0")

    counts = {
        "OLD_PROOF_QUESTION_COUNT": len(proof),
        "CURRENT_QCM_QUESTION_COUNT": len(corpus),
        "CARRIED_FORWARD_UNCHANGED": len(carried),
        "REPROOF_REQUIRED": len(reproof),
        "PROOF_ROWS_WITHOUT_CURRENT_QUESTION": len(orphan_proof_rows),
        "HISTORICAL_QUESTIONS_STILL_CURRENT": len(set(proof) & set(corpus)),
        "HISTORICAL_QUESTIONS_NOT_CURRENT": len(historical_not_current),
    }
    if counts["CARRIED_FORWARD_UNCHANGED"] + counts["REPROOF_REQUIRED"] != len(corpus):
        raise ReconciliationError("la partition ne couvre pas le corpus courant")

    return {
        "artifact_type": "qcm_review_proof_reconciliation",
        "schema_version": 1,
        "generated_by": "scripts/build_qcm_review_proof_reconciliation.py",
        "approves_nothing": True,
        "rebinds_nothing": True,
        "historical_proof_status": "HISTORICAL",
        "semantic_digest_contract": {
            "fields": [
                "capacity",
                "statement",
                "option_values",
                "correct_value",
                "diagnostics.erreur indexes par valeur d'option",
            ],
            "position_independent": True,
            "position_rationale": (
                "une permutation d'options ne change aucune des choses que la "
                "revue atteste ; elle change la lettre, pas la mathematique"
            ),
            "accent_insensitive": True,
            "accent_rationale": (
                "la campagne diacritiques est une correction editoriale mandatee "
                "qui ne change aucune mathematique"
            ),
            "excluded": ["diagnostics.renvoi"],
            "excluded_rationale": (
                "les partitions historiques ne capturent pas ce champ de facon "
                "homogene ; l'ecart est signale en lacune de couverture"
            ),
            "never_use_whole_file_sha_as_per_question_identity": True,
        },
        "counts": counts,
        "equation": (
            f"{len(corpus)} = {len(carried)} + {len(reproof)}"
        ),
        "aggregate_current_set_digest": "sha256:" + aggregate.hexdigest(),
        "proof_rows_without_current_question": orphan_proof_rows,
        "historical_not_current": historical_not_current,
        "carried_forward": carried,
        "reproof_required": reproof,
        "proof_field_coverage_gaps": coverage_gaps,
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def render_md(payload: dict[str, Any]) -> str:
    counts = payload["counts"]
    lines = [
        "<!-- generated by build_qcm_review_proof_reconciliation.py -->",
        "",
        "# Reconciliation de la preuve de revue independante des QCM",
        "",
        "Cet artefact n'approuve rien et ne rebinde rien.",
        "",
        f"- Lignes de preuve historique : {counts['OLD_PROOF_QUESTION_COUNT']}",
        f"- Questions du corpus courant : {counts['CURRENT_QCM_QUESTION_COUNT']}",
        f"- Preuve reportable a l'identique : {counts['CARRIED_FORWARD_UNCHANGED']}",
        f"- Preuve a refaire : {counts['REPROOF_REQUIRED']}",
        f"- Equation : {payload['equation']}",
        f"- Condense d'ensemble courant : `{payload['aggregate_current_set_digest']}`",
        "",
        "## Questions dont la preuve doit etre refaite",
        "",
        "| chapitre | question | motif | classes de delta |",
        "|---|---|---|---|",
    ]
    for entry in payload["reproof_required"]:
        classes = ", ".join(entry["delta_classes"]) or "—"
        lines.append(
            f"| {entry['chapter']} | {entry['question_id']} | {entry['reason']} | {classes} |"
        )
    lines += [
        "",
        "## Lacunes de couverture de la preuve historique",
        "",
        f"{len(payload['proof_field_coverage_gaps'])} question(s) dont la source porte "
        "un renvoi que la preuve n'a jamais capture.",
        "",
        "| chapitre | question | champ | options |",
        "|---|---|---|---|",
    ]
    for gap in payload["proof_field_coverage_gaps"]:
        lines.append(
            f"| {gap['chapter']} | {gap['question_id']} | {gap['field']} | "
            f"{', '.join(gap['options'])} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check", action="store_true", help="echoue si les artefacts sont perimes"
    )
    args = parser.parse_args(argv)

    payload = build_reconciliation()
    rendered_json = render_json(payload)
    rendered_md = render_md(payload)

    if args.check:
        stale = [
            str(target.relative_to(ROOT))
            for target, rendered in (
                (JSON_TARGET, rendered_json),
                (MD_TARGET, rendered_md),
            )
            if not target.is_file()
            or target.read_text(encoding="utf-8") != rendered
        ]
        if stale:
            print("STALE: " + ", ".join(stale))
            return 1
        print(
            "PASS reconciliation preuve QCM: "
            f"{payload['equation']} | lacunes de couverture "
            f"{len(payload['proof_field_coverage_gaps'])}"
        )
        return 0

    JSON_TARGET.write_text(rendered_json, encoding="utf-8")
    MD_TARGET.write_text(rendered_md, encoding="utf-8")
    print(f"wrote {JSON_TARGET.name} / {MD_TARGET.name}: {payload['equation']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
