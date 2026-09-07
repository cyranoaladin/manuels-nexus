#!/usr/bin/env python3
"""Fermeture de la revue mathématique des objets non formalisables.

La dimension `mathematics` prouve ce qui se calcule. Elle déclare
`NOT_APPLICABLE` ce qui ne se calcule pas — et `NOT_APPLICABLE` n'est pas
`PASS`. Ce producteur mesure ce que cette déclaration laisse ouvert.

Trois façons, et trois seulement, de fermer un objet :

`COVERED_BY_QCM_PROOF_CHAIN`
    l'objet est un QCM, et CHACUNE de ses questions est établie par la chaîne
    de preuve QCM — dérivation exécutée, revue conceptuelle écrite, preuve
    reportée à l'identique sémantique, ou recalcul machine. Une seule question
    sans état ferme la porte : on ne duplique pas une revue qui existe, mais
    on ne l'invente pas non plus.

`REVIEWED`
    une revue mathématique écrite le déclare, avec ses quatre dimensions.

`PENDING`
    tout le reste. C'est ce que la dimension doit refuser.

Le producteur n'approuve rien : une unité fermée est `VALIDATED_BY_EVIDENCE`.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import build_dimension_mathematics as maths  # noqa: E402
import evidence_freshness as freshness  # noqa: E402
import non_formalizable_reviews as declarations  # noqa: E402

INVENTORY = ROOT / "audit/INVENTAIRE_COLLECTION.json"
CLOSURE = ROOT / "audit/QCM_REVIEW_CLOSURE.json"
EVIDENCE = ROOT / "audit/QCM_INDEPENDENT_EVIDENCE_V2.json"
OUTPUT_JSON = ROOT / "audit/NON_FORMALIZABLE_REVIEW_CLOSURE.json"
OUTPUT_MD = ROOT / "audit/NON_FORMALIZABLE_REVIEW_CLOSURE.md"

VERIFY_BLOCK = re.compile(r"^% BEGIN-VERIFY\s*$(.*?)^% END-VERIFY\s*$", re.S | re.M)

#: États de la chaîne QCM qui valent preuve scientifique pour une question.
QCM_PROVEN_STATES = frozenset({"MECHANICALLY_PROVEN", "CONCEPTUALLY_REVIEWED"})
QCM_EVIDENCE_STATES = frozenset({"CARRIED_FORWARD_IDENTICAL", "MACHINE_RECALCULATED"})


def _population() -> list[dict[str, Any]]:
    """Les objets mathématiques qu'aucun oracle ne peut trancher.

    La classification est celle de la dimension elle-même, appelée ici plutôt
    que recopiée : deux définitions de la même population finiraient par
    diverger, et c'est la dimension qui fait autorité.
    """
    inventaire = json.loads(INVENTORY.read_text(encoding="utf-8"))
    objets: list[dict[str, Any]] = []
    for manuel, contenu in sorted(inventaire.get("manuals", {}).items()):
        for chapitre, valeur in sorted(contenu.get("chapters", {}).items()):
            for objet in valeur.get("objects", []):
                chemin = ROOT / str(objet.get("path", ""))
                if not chemin.is_file():
                    continue
                texte = chemin.read_text(encoding="utf-8", errors="replace")
                if VERIFY_BLOCK.search(texte):
                    continue
                premiere = texte.split("\n", 1)[0]
                meta = (
                    json.loads(premiere[len("% META:"):])
                    if premiere.startswith("% META:") else {}
                )
                corps = "\n".join(texte.splitlines()[1:])
                if maths.classify_not_applicable(
                    manuel, meta.get("type_objet"), corps
                ) != "MATHEMATICAL_NON_FORMALIZABLE":
                    continue
                objets.append({
                    "manual": manuel,
                    "chapter": chapitre,
                    "object_id": objet.get("id"),
                    "type_objet": meta.get("type_objet"),
                    "path": str(objet["path"]),
                })
    objets.sort(key=lambda o: o["path"])
    return objets


def _qcm_question_states() -> dict[str, dict[str, str]]:
    """Pour chaque source QCM, l'état de preuve de chacune de ses questions."""
    etats: dict[str, dict[str, str]] = {}
    evidence = json.loads(EVIDENCE.read_text(encoding="utf-8"))
    for ligne in evidence.get("questions") or []:
        source = str(ligne.get("source_path"))
        etats.setdefault(source, {})[str(ligne.get("question_id"))] = str(
            ligne.get("evidence_status")
        )
    closure = json.loads(CLOSURE.read_text(encoding="utf-8"))
    for ligne in closure.get("questions") or []:
        source = str(ligne.get("source_path"))
        etats.setdefault(source, {})[str(ligne.get("question_id"))] = str(
            ligne.get("state")
        )
    return etats


def _qcm_sources_for(chemin: Path) -> list[Path]:
    """Les sources JSON qui engendrent ce `.tex` de QCM."""
    return sorted(chemin.parent.glob("*-QCM.json")) + sorted(
        chemin.parent.glob("*-QCM-DIAG.json")
    )


def build() -> dict[str, Any]:
    population = _population()
    etats_qcm = _qcm_question_states()
    lignes: list[dict[str, Any]] = []

    for objet in population:
        chemin = ROOT / objet["path"]
        revue = declarations.REVIEWS.get(objet["path"])
        etat, preuve, detail = "PENDING", None, None

        if objet["type_objet"] in ("qcm", "qcm_diagnostics"):
            sources = _qcm_sources_for(chemin)
            questions: dict[str, str] = {}
            for source in sources:
                questions.update(etats_qcm.get(str(source.relative_to(ROOT)), {}))
            if not questions:
                detail = "aucune question routée pour cette source"
            else:
                ouvertes = sorted(
                    identifiant for identifiant, valeur in questions.items()
                    if valeur not in QCM_PROVEN_STATES | QCM_EVIDENCE_STATES
                )
                if ouvertes:
                    detail = f"questions sans preuve : {ouvertes[:5]}"
                else:
                    etat = "COVERED_BY_QCM_PROOF_CHAIN"
                    preuve = "audit/QCM_REVIEW_CLOSURE.json"
                    detail = f"{len(questions)} questions, toutes établies"

        if etat == "PENDING" and revue is not None:
            etat = "REVIEWED"
            preuve = "scripts/non_formalizable_reviews.py"

        ligne = dict(objet, state=etat, evidence=preuve, detail=detail)
        if revue is not None:
            ligne["review"] = revue
        lignes.append(ligne)

    par_etat: dict[str, int] = {}
    for ligne in lignes:
        par_etat[ligne["state"]] = par_etat.get(ligne["state"], 0) + 1
    par_type: dict[str, dict[str, int]] = {}
    for ligne in lignes:
        seau = par_type.setdefault(str(ligne["type_objet"]), {})
        seau[ligne["state"]] = seau.get(ligne["state"], 0) + 1

    defauts = [
        {"path": ligne["path"], "defect": ligne["review"]["defect"]}
        for ligne in lignes
        if ligne.get("review") and ligne["review"].get("defect")
    ]

    resume = {
        "MATHEMATICAL_NON_FORMALIZABLE_TOTAL": len(lignes),
        "MATHEMATICAL_NON_FORMALIZABLE_REVIEW_PENDING": par_etat.get("PENDING", 0),
        "COVERED_BY_QCM_PROOF_CHAIN": par_etat.get("COVERED_BY_QCM_PROOF_CHAIN", 0),
        "REVIEWED": par_etat.get("REVIEWED", 0),
        "DEFECTS_FOUND": len(defauts),
        "STATES_SUM_EQUALS_TOTAL": sum(par_etat.values()) == len(lignes),
        "APPROVES_NOTHING": True,
    }
    payload = {
        "artifact_type": "non_formalizable_review_closure",
        "schema_version": 1,
        "generated_by": "scripts/build_non_formalizable_review_closure.py",
        "authority_note": (
            "Une unité fermée est VALIDATED_BY_EVIDENCE, jamais `approved` : "
            "le sign-off humain porte sur le corpus gelé."
        ),
        "summary": resume,
        "by_type": {cle: par_type[cle] for cle in sorted(par_type)},
        "defects": defauts,
        "objects": lignes,
    }
    payload["freshness"] = freshness.stamp(
        ["audit/INVENTAIRE_COLLECTION.json", "audit/QCM_REVIEW_CLOSURE.json",
         "audit/QCM_INDEPENDENT_EVIDENCE_V2.json",
         "scripts/non_formalizable_reviews.py"],
        root=ROOT,
    )
    return payload


def render_md(payload: dict[str, Any]) -> str:
    resume = payload["summary"]
    lignes = [
        "# Revue mathématique des objets non formalisables",
        "",
        "Un oracle prouve ce qui se calcule. Ces objets n'en portent pas et ne",
        "peuvent pas en porter : leur exactitude se démontre autrement.",
        "",
        f"- Population : `{resume['MATHEMATICAL_NON_FORMALIZABLE_TOTAL']}`",
        f"- `MATHEMATICAL_NON_FORMALIZABLE_REVIEW_PENDING` : "
        f"`{resume['MATHEMATICAL_NON_FORMALIZABLE_REVIEW_PENDING']}`",
        f"- Couverts par la chaîne QCM : `{resume['COVERED_BY_QCM_PROOF_CHAIN']}`",
        f"- Revus : `{resume['REVIEWED']}`",
        f"- Défauts trouvés en revue : `{resume['DEFECTS_FOUND']}`",
        "",
        "| Type | Revus | Chaîne QCM | En attente |",
        "|---|---|---|---|",
    ]
    for type_objet, etats in payload["by_type"].items():
        lignes.append(
            f"| {type_objet} | {etats.get('REVIEWED', 0)} | "
            f"{etats.get('COVERED_BY_QCM_PROOF_CHAIN', 0)} | "
            f"{etats.get('PENDING', 0)} |"
        )
    lignes.append("")
    return "\n".join(lignes)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    payload = build()
    rendu = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if arguments.check:
        if OUTPUT_JSON.is_file() and OUTPUT_JSON.read_text(encoding="utf-8") == rendu:
            print("NON_FORMALIZABLE_REVIEW_CLOSURE check: OK")
            return 0
        print("NON_FORMALIZABLE_REVIEW_CLOSURE check: STALE")
        return 1
    OUTPUT_JSON.write_text(rendu, encoding="utf-8")
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
