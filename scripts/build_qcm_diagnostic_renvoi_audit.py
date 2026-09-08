#!/usr/bin/env python3
"""Chaque renvoi de diagnostic QCM désigne-t-il un endroit qui existe ?

Un diagnostic de distracteur dit deux choses : quelle erreur l'élève a
probablement commise, et OÙ retrouver la notion. Le second champ, `renvoi`,
n'a jamais été vérifié : la preuve historique ne le capturait pas, et le
vérificateur courant ne le compare pas. 41 questions sont restées en attente
pour cette raison.

Ce producteur vérifie les 1470 renvois du dépôt, pas seulement les 41.

QUATRE FORMES DE CIBLE, RÉSOLUES CHACUNE À SA SOURCE.

  `C<n>`      une capacité — elle doit figurer au contrat du chapitre ;
  `M<n>`      une fiche méthode — le marqueur doit être porté par un objet du
              chapitre, soit dans son META `methodes`, soit dans le label de
              son environnement `fichemethode` ;
  `R<n>`      une remédiation — le marqueur doit être le suffixe de l'identité
              d'un objet de remédiation du chapitre ;
  `RE-C<n>`   une remédiation désignée par la capacité qu'elle reprend ;
  `Cours …`   le chapitre doit porter des objets de cours.

Un renvoi peut en désigner plusieurs, séparés par `;`. Chaque cible est
résolue séparément : `M3 ; R3` exige que les deux existent.

CE QUE CE PRODUCTEUR NE FAIT PAS. Il ne juge pas de la PERTINENCE d'un renvoi
par ressemblance de vocabulaire. Un renvoi qui pointe vers une capacité autre
que celle de la question n'est pas une erreur en soi — c'est même souvent
l'intention : le distracteur confond une notion enseignée ailleurs, et le
renvoi doit y conduire. Ces cas-là sont donc JUGÉS UN PAR UN et déposés dans
`CROSS_CAPACITY_JUSTIFICATIONS` ; un renvoi croisé sans justification déposée
fait échouer la construction.
"""

from __future__ import annotations

import argparse
import collections
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import evidence_freshness as freshness  # noqa: E402

OUTPUT_JSON = ROOT / "audit/QCM_DIAGNOSTIC_RENVOI_AUDIT.json"
OUTPUT_MD = ROOT / "audit/QCM_DIAGNOSTIC_RENVOI_AUDIT.md"

CHAPTER_ROOTS = ("Mathematiques/manuel-maths/chapitres", "NSI/chapitres")

CAPACITE = re.compile(r"^C\d+$")
METHODE = re.compile(r"^M\d+$")
REMEDIATION = re.compile(r"^R\d+$")
REMEDIATION_CAPACITE = re.compile(r"^RE-(C\d+)$")

#: Renvois qui pointent vers une capacité AUTRE que celle de la question.
#: Chacun est jugé : le distracteur porte une confusion dont la notion est
#: enseignée ailleurs, et le renvoi doit conduire là où elle l'est.
CROSS_CAPACITY_JUSTIFICATIONS: dict[tuple[str, str, str], str] = {
    ("TNSI-HISTOIRE-INFORMATIQUE", "Q4", "B"): (
        "La question évalue en C2 l'ajout d'un service logiciel sur une "
        "infrastructure existante. Le distracteur invente un réseau physique "
        "indépendant : C1 distingue Internet et le Web, puis C2 précise "
        "l'utilisation des ressources matérielles par les logiciels."
    ),
    ("TNSI-HISTOIRE-INFORMATIQUE", "Q4", "C"): (
        "La question porte sur le rôle logiciel du Web en C2. Le distracteur "
        "en fait une condition d'apparition d'ARPANET : les repères 1969 et "
        "1989 en C1 réfutent cette causalité, avant de revenir aux couches "
        "logicielles étudiées en C2."
    ),
    ("TSPE-LIMITES-FONCTIONS", "Q5", "C"): (
        "La question calcule une limite (C1), mais le distracteur ignore la "
        "croissance comparée, qui est l'objet de C3. Renvoyer à C1 laisserait "
        "l'élève devant le même blocage."
    ),
    ("TSPE-LIMITES-FONCTIONS", "Q9", "C"): (
        "La question porte sur l'interprétation d'une asymptote (C2) ; le "
        "distracteur se trompe sur les limites de l'exponentielle, enseignées "
        "en C1. C'est là qu'il faut retourner."
    ),
    ("TSPE-SUITES-LIMITES", "Q7", "B"): (
        "La question porte sur le théorème de la limite monotone (C4) ; le "
        "distracteur confond convergence et croissance, notions définies en C1."
    ),
    ("TSPE-GEOMETRIE-ESPACE", "Q8", "C"): (
        "La question porte sur les bases (C4) ; le distracteur invoque "
        "l'orthogonalité, qui relève du produit scalaire (C7). La confusion "
        "porte sur C7, pas sur C4."
    ),
    ("TSPE-GEOMETRIE-ESPACE", "Q12", "B"): (
        "La question calcule un angle (C9) ; le distracteur se trompe dans le "
        "produit scalaire lui-même (C7), qui est l'outil du calcul."
    ),
    ("TSPE-GEOMETRIE-ESPACE", "Q16", "C"): (
        "La question demande de DÉMONTRER l'équation cartésienne (C16) ; le "
        "distracteur confond le vecteur normal avec les coordonnées du point, "
        "confusion qui se traite en C13, où l'équation est établie."
    ),
    ("1SPE-EXPONENTIELLE", "Q15", "B"): (
        "Renvoi composé : C3 pour le signe de l'exponentielle, C5 pour la "
        "décroissance modélisée. Le distracteur mêle les deux, et le renvoi "
        "les nomme toutes les deux."
    ),
    ("1SPE-VARIABLES-ALEATOIRES", "Q16", "D"): (
        "La question porte sur la simulation d'une variable (C6) ; le "
        "distracteur confond la taille d'un échantillon avec le NOMBRE "
        "d'échantillons, notion de C7."
    ),
    ("TSPE-PRIMITIVES-EQDIFF", "Q2", "B"): (
        "La question porte sur la démonstration (C4) ; le distracteur se "
        "trompe sur l'ensemble des primitives, décrit en C1."
    ),
    ("TSPE-PRIMITIVES-EQDIFF", "Q2", "C"): (
        "Même question, même confusion sur l'ensemble des primitives : le "
        "renvoi conduit en C1, où cet ensemble est caractérisé."
    ),
    ("TSPE-PRIMITIVES-EQDIFF", "Q2", "D"): (
        "Même question, troisième distracteur : il se trompe encore sur la "
        "forme de l'ensemble des primitives, caractérisé en C1. Le renvoi y "
        "conduit, et non vers la démonstration qui fait l'objet de la question."
    ),
}


def _meta(chemin: Path) -> dict[str, Any]:
    premiere = chemin.read_text(encoding="utf-8", errors="replace").split("\n", 1)[0]
    if not premiere.startswith("% META:"):
        return {}
    try:
        return json.loads(premiere[7:])
    except json.JSONDecodeError:
        return {}


def method_markers(chapitre: Path) -> set[str]:
    """Marqueurs `M<n>` que le chapitre porte réellement.

    Deux sources, parce que le dépôt en utilise deux : le champ META
    `methodes` des chapitres NSI, et le label de `\\begin{fichemethode}{M1}`
    des chapitres de mathématiques, dont le META ne porte pas ce champ.
    """
    marqueurs: set[str] = set()
    dossier = chapitre / "methodes"
    if not dossier.is_dir():
        return marqueurs
    for fichier in dossier.glob("*.tex"):
        texte = fichier.read_text(encoding="utf-8", errors="replace")
        marqueurs |= {str(m) for m in (_meta(fichier).get("methodes") or [])}
        marqueurs |= {
            label.strip()
            for label in re.findall(r"\\begin\{fichemethode\}\{([^}]*)\}", texte)
        }
    return marqueurs


def remediation_markers(chapitre: Path) -> set[str]:
    """Marqueurs `R<n>` que le chapitre porte, lus sur l'identité des objets."""
    marqueurs: set[str] = set()
    dossier = chapitre / "remediation"
    if not dossier.is_dir():
        return marqueurs
    for fichier in dossier.glob("*.tex"):
        meta = _meta(fichier)
        identite = str(meta.get("id") or fichier.stem)
        marqueurs.add(identite.rsplit("-", 1)[-1])
        marqueurs |= {str(r) for r in (meta.get("remediations") or [])}
    return marqueurs


def _cibles(renvoi: str) -> list[str]:
    return [morceau.strip() for morceau in renvoi.split(";") if morceau.strip()]


def build(root: Path = ROOT) -> dict[str, Any]:
    lignes = []
    inputs: list[str] = []
    for racine in CHAPTER_ROOTS:
        for qcm in sorted((root / racine).glob("*/qcm/*-QCM.json")):
            chapitre = qcm.parent.parent
            contrat_path = chapitre / "contrat.yaml"
            contrat = (
                yaml.safe_load(contrat_path.read_text(encoding="utf-8")) or {}
                if contrat_path.is_file() else {}
            )
            codes = {
                str(c["code"]) for c in (contrat.get("capacites") or [])
                if isinstance(c, dict) and c.get("code")
            }
            methodes = method_markers(chapitre)
            remediations = remediation_markers(chapitre)
            porte_cours = (chapitre / "cours").is_dir() and any(
                (chapitre / "cours").glob("*.tex")
            )
            inputs.append(qcm.relative_to(root).as_posix())

            payload = json.loads(qcm.read_text(encoding="utf-8"))
            for question in payload.get("questions", []):
                capacite = question.get("capacite")
                for lettre, diagnostic in (question.get("diagnostics") or {}).items():
                    renvoi = str((diagnostic or {}).get("renvoi") or "").strip()
                    etat, detail, croise = "RESOLVED", None, False
                    if not renvoi:
                        etat, detail = "MISSING_RENVOI", "aucun renvoi déclaré"
                    for cible in _cibles(renvoi):
                        tete = cible.split(",")[0].strip()
                        if CAPACITE.match(tete):
                            if tete not in codes:
                                etat = "BROKEN"
                                detail = f"capacité {tete} absente du contrat"
                            elif capacite and tete != capacite:
                                croise = True
                        elif METHODE.match(tete):
                            if tete not in methodes:
                                etat = "BROKEN"
                                detail = f"fiche méthode {tete} absente du chapitre"
                        elif REMEDIATION.match(tete):
                            if tete not in remediations:
                                etat = "BROKEN"
                                detail = f"remédiation {tete} absente du chapitre"
                        elif REMEDIATION_CAPACITE.match(tete):
                            code = REMEDIATION_CAPACITE.match(tete).group(1)
                            if code not in codes:
                                etat = "BROKEN"
                                detail = f"capacité {code} absente du contrat"
                        elif tete.lower().startswith("cours"):
                            if not porte_cours:
                                etat = "BROKEN"
                                detail = "le chapitre ne porte aucun cours"
                        else:
                            etat = "UNKNOWN_FORM"
                            detail = f"forme de renvoi non reconnue : {tete!r}"
                    justification = None
                    if croise and etat == "RESOLVED":
                        cle = (chapitre.name, str(question.get("id")), str(lettre))
                        justification = CROSS_CAPACITY_JUSTIFICATIONS.get(cle)
                        if justification is None:
                            raise ValueError(
                                f"renvoi croisé non jugé : {cle} -> {renvoi!r}"
                            )
                    lignes.append({
                        "chapter": chapitre.name,
                        "question_id": question.get("id"),
                        "option": lettre,
                        "question_capacity": capacite,
                        "renvoi": renvoi,
                        "state": etat,
                        "cross_capacity": croise,
                        "justification": justification,
                        "detail": detail,
                    })

    etats = collections.Counter(ligne["state"] for ligne in lignes)
    croises = [ligne for ligne in lignes if ligne["cross_capacity"]]
    summary = {
        "QCM_DIAGNOSTIC_RENVOI_POPULATION": len(lignes),
        "QCM_DIAGNOSTIC_RENVOI_RESOLVED": etats["RESOLVED"],
        "BROKEN_REMEDIATION_REFERENCES": etats["BROKEN"],
        "QCM_DIAGNOSTIC_MISMATCH": etats["BROKEN"] + etats["UNKNOWN_FORM"]
        + etats["MISSING_RENVOI"],
        "QCM_DIAGNOSTIC_RENVOI_UNKNOWN_FORM": etats["UNKNOWN_FORM"],
        "QCM_DIAGNOSTIC_RENVOI_MISSING": etats["MISSING_RENVOI"],
        "CROSS_CAPACITY_RENVOI_JUSTIFIED": len(croises),
    }
    payload = {
        "artifact_type": "qcm_diagnostic_renvoi_audit",
        "schema_version": 1,
        "generated_by": "scripts/build_qcm_diagnostic_renvoi_audit.py",
        "approves_nothing": True,
        "resolution_rule": (
            "Une cible est résolue quand l'objet qu'elle nomme EXISTE dans le "
            "chapitre. Aucun rapprochement par ressemblance de vocabulaire."
        ),
        "summary": summary,
        "cross_capacity": croises,
        "defects": [
            ligne for ligne in lignes if ligne["state"] != "RESOLVED"
        ],
        "renvois": lignes,
    }
    payload["freshness"] = freshness.stamp(sorted(inputs), root=root)
    return payload


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lignes = [
        "# Renvois des diagnostics QCM : chaque cible existe-t-elle ?",
        "",
        f"- Population : `{s['QCM_DIAGNOSTIC_RENVOI_POPULATION']}` renvois",
        f"- `BROKEN_REMEDIATION_REFERENCES` : `{s['BROKEN_REMEDIATION_REFERENCES']}`",
        f"- `QCM_DIAGNOSTIC_MISMATCH` : `{s['QCM_DIAGNOSTIC_MISMATCH']}`",
        f"- `CROSS_CAPACITY_RENVOI_JUSTIFIED` : "
        f"`{s['CROSS_CAPACITY_RENVOI_JUSTIFIED']}`",
        "",
        "## Renvois croisés, jugés un par un",
        "",
    ]
    for ligne in payload["cross_capacity"]:
        lignes.append(
            f"- `{ligne['chapter']}/{ligne['question_id']}` option "
            f"`{ligne['option']}` — capacité `{ligne['question_capacity']}`, "
            f"renvoi `{ligne['renvoi']}` : {ligne['justification']}"
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
            print("QCM_DIAGNOSTIC_RENVOI_AUDIT check: MISSING")
            return 1
        if OUTPUT_JSON.read_text(encoding="utf-8") != rendered:
            print("QCM_DIAGNOSTIC_RENVOI_AUDIT check: STALE")
            return 1
        print("QCM_DIAGNOSTIC_RENVOI_AUDIT check: OK")
        return 0
    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
