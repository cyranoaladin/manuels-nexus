#!/usr/bin/env python3
"""Ferme les 166 QCM restés en `HUMAN_REVIEW_REQUIRED`, et le prouve.

Ce producteur ne décide de rien : il EXÉCUTE les dérivations mécaniques
déclarées dans `qcm_reviews.py`, VÉRIFIE les revues conceptuelles, et
rapproche le résultat de la clé du QCM.

L'INDÉPENDANCE EST STRUCTURELLE, pas promise. Une dérivation mécanique reçoit
le dictionnaire des options et rien d'autre : ni la clé, ni les diagnostics,
ni le champ `correcte`. Elle calcule une valeur, cherche l'option qui la
décrit, et renvoie une lettre. Le rapprochement avec la clé se fait ici,
après. Une divergence est un DÉFAUT publié, jamais une valeur ajustée.

Une revue conceptuelle, elle, doit nommer : le raisonnement, l'objet de cours
qui l'établit — et ce fichier doit exister —, la capacité du programme, et une
réfutation par distracteur. Le producteur refuse une revue qui laisserait un
distracteur sans réfutation, ou qui en réfuterait un qui n'existe pas.

Aucun rapprochement par mots-clés : une réfutation absente est absente, et
aucune ressemblance de vocabulaire ne la remplace.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import traceback
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import evidence_freshness as freshness  # noqa: E402
import qcm_reviews as declarations  # noqa: E402

EVIDENCE = ROOT / "audit/QCM_INDEPENDENT_EVIDENCE_V2.json"
OUTPUT_JSON = ROOT / "audit/QCM_REVIEW_CLOSURE.json"
OUTPUT_MD = ROOT / "audit/QCM_REVIEW_CLOSURE.md"

PROVEN = "MECHANICALLY_PROVEN"
REVIEWED = "CONCEPTUALLY_REVIEWED"
OPEN = "REVIEW_OPEN"
DISAGREEMENT = "KEY_DISAGREEMENT"
BROKEN = "DERIVATION_FAILED"


def _questions(root: Path) -> list[dict[str, Any]]:
    evidence = json.loads((root / EVIDENCE.relative_to(ROOT)).read_text("utf-8"))
    ouvertes = [
        q for q in evidence["questions"]
        if q["evidence_status"] == "HUMAN_REVIEW_REQUIRED"
    ]
    corpus: dict[str, Any] = {}
    enrichies = []
    for question in ouvertes:
        chemin = question["source_path"]
        if chemin not in corpus:
            corpus[chemin] = json.loads((root / chemin).read_text("utf-8"))
        brute = next(
            x for x in corpus[chemin]["questions"]
            if x["id"] == question["question_id"]
        )
        enrichies.append({
            "chapter": question["chapter"],
            "question_id": question["question_id"],
            "capacity": brute.get("capacite"),
            "source_path": chemin,
            "enonce": brute["enonce"],
            "options": dict(brute["options"]),
            "cle": brute["correcte"],
            "diagnostics": brute.get("diagnostics") or {},
        })
    return enrichies


def _evaluer_mecanique(question, famille, derivation) -> dict[str, Any]:
    # La dérivation ne reçoit QUE les options : une copie, pour qu'elle ne
    # puisse pas non plus muter la question.
    options = dict(question["options"])
    try:
        lettre = derivation(options)
    except Exception as erreur:  # noqa: BLE001 - on publie l'échec
        return {
            "state": BROKEN,
            "family": famille,
            "computed": None,
            "detail": f"{type(erreur).__name__}: {erreur}",
            "traceback": traceback.format_exc(limit=3),
        }
    if lettre not in question["options"]:
        return {
            "state": BROKEN,
            "family": famille,
            "computed": lettre,
            "detail": "la dérivation a renvoyé une lettre hors des options",
        }
    if lettre != question["cle"]:
        return {
            "state": DISAGREEMENT,
            "family": famille,
            "computed": lettre,
            "detail": (
                f"la dérivation conclut {lettre}, la clé dit "
                f"{question['cle']}"
            ),
        }
    return {"state": PROVEN, "family": famille, "computed": lettre}


def _evaluer_conceptuelle(question, revue, root: Path) -> dict[str, Any]:
    cours = str(revue["source_cours"])
    if not (root / cours).is_file():
        return {
            "state": BROKEN,
            "computed": revue["reponse"],
            "detail": f"objet de cours absent du dépôt : {cours}",
        }
    distracteurs = set(question["options"]) - {question["cle"]}
    refutes = set(revue["refutations"])
    if refutes != distracteurs:
        manquants = sorted(distracteurs - refutes)
        surnumeraires = sorted(refutes - distracteurs)
        return {
            "state": BROKEN,
            "computed": revue["reponse"],
            "detail": (
                f"réfutations incomplètes — manquantes {manquants}, "
                f"hors options {surnumeraires}"
            ),
        }
    courtes = sorted(
        lettre for lettre, texte in revue["refutations"].items()
        if len(str(texte).strip()) < 40
    )
    if courtes:
        return {
            "state": BROKEN,
            "computed": revue["reponse"],
            "detail": f"réfutations trop brèves pour établir quoi que ce soit : {courtes}",
        }
    if revue["reponse"] != question["cle"]:
        return {
            "state": DISAGREEMENT,
            "computed": revue["reponse"],
            "detail": (
                f"la revue conclut {revue['reponse']}, la clé dit "
                f"{question['cle']}"
            ),
        }
    return {
        "state": REVIEWED,
        "computed": revue["reponse"],
        "source_cours": cours,
        "source_programme": revue["source_programme"],
    }


def build(root: Path = ROOT) -> dict[str, Any]:
    resultats = []
    for question in _questions(root):
        cle = (question["chapter"], question["question_id"])
        mecanique = declarations.MECHANICAL_DERIVATIONS.get(cle)
        conceptuelle = declarations.CONCEPTUAL_REVIEWS.get(cle)
        if mecanique is not None:
            famille, derivation = mecanique
            verdict = _evaluer_mecanique(question, famille, derivation)
            regime = declarations.MECHANICAL
        elif conceptuelle is not None:
            verdict = _evaluer_conceptuelle(question, conceptuelle, root)
            regime = declarations.CONCEPTUAL
        else:
            verdict = {
                "state": OPEN,
                "computed": None,
                "detail": "aucune dérivation ni revue déclarée",
            }
            regime = None
        resultats.append({
            "chapter": question["chapter"],
            "question_id": question["question_id"],
            "capacity": question["capacity"],
            "source_path": question["source_path"],
            "regime": regime,
            "key": question["cle"],
            **verdict,
        })

    etats = {etat: 0 for etat in (PROVEN, REVIEWED, OPEN, DISAGREEMENT, BROKEN)}
    for ligne in resultats:
        etats[ligne["state"]] += 1
    familles = {famille: 0 for famille in declarations.FAMILIES}
    for ligne in resultats:
        if ligne["state"] == PROVEN:
            familles[ligne["family"]] += 1

    total = len(resultats)
    summary = {
        "QCM_HUMAN_REVIEW_POPULATION": total,
        "QCM_MECHANICAL_PROVEN": etats[PROVEN],
        "QCM_MECHANICAL_BY_FAMILY": familles,
        "QCM_CONCEPTUAL_REVIEWED": etats[REVIEWED],
        "QCM_REVIEW_OPEN": etats[OPEN],
        "QCM_KEY_DISAGREEMENTS": etats[DISAGREEMENT],
        "QCM_DERIVATION_FAILURES": etats[BROKEN],
        "QCM_REVIEW_CLOSED": etats[PROVEN] + etats[REVIEWED],
    }
    if sum(etats.values()) != total:
        raise ValueError("items perdus dans la clôture QCM")

    payload = {
        "artifact_type": "qcm_review_closure",
        "schema_version": 1,
        "generated_by": "scripts/build_qcm_review_closure.py",
        "declaration_table": "scripts/qcm_reviews.py",
        "approves_nothing": True,
        "independence_contract": (
            "Une dérivation mécanique ne reçoit que les options, jamais la clé "
            "ni les diagnostics. Le rapprochement avec la clé est fait par ce "
            "producteur, après."
        ),
        "summary": summary,
        "questions": resultats,
    }
    payload["closure_digest"] = "sha256:" + hashlib.sha256(
        json.dumps(
            [
                [r["chapter"], r["question_id"], r["state"], r.get("computed")]
                for r in resultats
            ],
            ensure_ascii=False, sort_keys=True, separators=(",", ":"),
        ).encode("utf-8")
    ).hexdigest()
    payload["freshness"] = freshness.stamp(
        ["audit/QCM_INDEPENDENT_EVIDENCE_V2.json", "scripts/qcm_reviews.py"],
        root=root,
    )
    return payload


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lignes = [
        "# Clôture des QCM restés en revue humaine",
        "",
        f"- Population : `{s['QCM_HUMAN_REVIEW_POPULATION']}`",
        f"- `QCM_MECHANICAL_PROVEN` : `{s['QCM_MECHANICAL_PROVEN']}` "
        f"({s['QCM_MECHANICAL_BY_FAMILY']})",
        f"- `QCM_CONCEPTUAL_REVIEWED` : `{s['QCM_CONCEPTUAL_REVIEWED']}`",
        f"- `QCM_REVIEW_OPEN` : `{s['QCM_REVIEW_OPEN']}`",
        f"- `QCM_KEY_DISAGREEMENTS` : `{s['QCM_KEY_DISAGREEMENTS']}`",
        f"- `QCM_DERIVATION_FAILURES` : `{s['QCM_DERIVATION_FAILURES']}`",
        "",
    ]
    ennuis = [
        r for r in payload["questions"]
        if r["state"] in (DISAGREEMENT, BROKEN)
    ]
    if ennuis:
        lignes += ["## Divergences et échecs", ""]
        for r in ennuis:
            lignes.append(
                f"- `{r['chapter']}/{r['question_id']}` — `{r['state']}` : "
                f"{r.get('detail', '')}"
            )
        lignes.append("")
    return "\n".join(lignes)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not OUTPUT_JSON.is_file():
            print("QCM_REVIEW_CLOSURE check: MISSING")
            return 1
        if OUTPUT_JSON.read_text(encoding="utf-8") != rendered:
            print("QCM_REVIEW_CLOSURE check: STALE")
            return 1
        print("QCM_REVIEW_CLOSURE check: OK")
        return 0
    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
