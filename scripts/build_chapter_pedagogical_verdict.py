#!/usr/bin/env python3
"""Revue pedagogique adversariale, chapitre par chapitre.

Le nombre d'exercices ne dit rien. Ce producteur mesure ce que le critere
qualitatif exige : le programme est-il enseigne, l'entrainement est-il varie,
la difficulte progresse-t-elle, les corriges suivent-ils, la maitrise est-elle
evaluable, la remediation existe-t-elle la ou elle est pertinente.

CHAQUE VERDICT EST DERIVE, JAMAIS AFFIRME. Les quatre couvertures viennent des
`competences` et des `parcours` que chaque exercice DECLARE dans son META,
croisees avec les capacites du contrat :

`DIRECT_APPLICATION_COVERAGE`  une capacite dispose d'un exercice de parcours 1
                               ou d'un exercice de competence « calculer » ;
`VARIATION_COVERAGE`           elle dispose d'au moins une SITUATION DE
                               TRANSFERT au sens de la taxonomie des fonctions
                               pedagogiques -- pas d'un simple second exercice ;
`REASONING_COVERAGE`           elle dispose d'un exercice « raisonner » ;
`SYNTHESIS_COVERAGE`           le chapitre propose au moins un exercice de
                               parcours 3, ou une evaluation qui croise
                               plusieurs capacites.

Un chapitre dont une capacite substantielle n'a que de l'application directe
n'est pas ADEQUATE : il entraine a reproduire, pas a transferer.

LA DIVERSITE SE LIT DANS LES ENONCES, PAS DANS LES COMPTEURS. Chaque capacite
recoit une analyse individuelle (`per_capacity`) qui nomme les fonctions
pedagogiques reellement presentes et conclut `DIVERSITY_SUFFICIENT` ou
`REAL_DIVERSITY_GAP`. Aucune regle du type « une capacite -> deux nouveaux
exercices » n'existe ici : une capacite deja pourvue d'une application et
d'une situation de transfert est suffisante, quel que soit son effectif, et
une capacite pourvue de dix applications directes ne l'est pas.

UN CHAPITRE EVALUE PAR PROJET N'EST PAS UN CHAPITRE SANS QUALITE. Lorsque le
contrat porte `assessment_mode: PROJECT_ASSESSMENT`, les axes qui presupposent
une banque d'exercices sont declares `NOT_APPLICABLE_PROJECT_ASSESSMENT` et
remplaces par les axes que ce mode exige reellement : un cahier des charges,
une grille criteriee, une version amenagee, un controle des connaissances.
L'exemption change ce qu'on mesure ; elle n'abaisse pas l'exigence.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path
from typing import Any

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from exercise_function_taxonomy import (  # noqa: E402
    DIRECT,
    REASONING as F_REASONING,
    SYNTHESIS as F_SYNTHESIS,
    TRANSFER_FUNCTIONS,
    diversity_verdict,
    functions_of,
)

ROOT = Path(__file__).resolve().parents[1]
CORPORA = ("Mathematiques/manuel-maths/chapitres", "NSI/chapitres")
JSON_TARGET = ROOT / "audit/CHAPTER_PEDAGOGICAL_VERDICT.json"
MD_TARGET = ROOT / "audit/CHAPTER_PEDAGOGICAL_VERDICT.md"
GENERATED_BY = "scripts/build_chapter_pedagogical_verdict.py"

STRONG, ADEQUATE, WEAK, UNUSABLE = "STRONG", "ADEQUATE", "WEAK", "UNUSABLE"
VERDICTS = (STRONG, ADEQUATE, WEAK, UNUSABLE)
NOT_APPLICABLE = "NOT_APPLICABLE_PROJECT_ASSESSMENT"


def _meta(path: Path) -> dict[str, Any]:
    texte = path.read_text(encoding="utf-8", errors="replace")
    if not texte.startswith("% META:"):
        return {}
    try:
        return json.loads(texte.split("\n", 1)[0][len("% META: "):])
    except json.JSONDecodeError:
        return {}


def _objects(directory: Path) -> list[dict[str, Any]]:
    """Le META ET le corps : la diversite se lit dans ce que l'enonce demande."""

    if not directory.is_dir():
        return []
    objets = []
    for chemin in sorted(directory.glob("*.tex")):
        texte = chemin.read_text(encoding="utf-8", errors="replace")
        corps = texte.split("\n", 1)[1] if texte.startswith("% META:") else texte
        objets.append(
            dict(
                _meta(chemin),
                _path=str(chemin.relative_to(ROOT)),
                _body=corps,
            )
        )
    return objets


def _analyse_capacite(code: str, objets: list[dict[str, Any]]) -> dict[str, Any]:
    """Ce dont cette capacite dispose reellement pour entrainer au transfert.

    La sortie nomme les fonctions presentes et le manque. Elle ne prescrit
    aucun effectif : le mandat refuse explicitement toute regle implicite
    « une capacite -> deux nouveaux exercices ».
    """

    fonctions = [functions_of(o.get("_body") or "", o) for o in objets]
    verdict = diversity_verdict(fonctions)
    natures = collections.Counter(f for liste in fonctions for f in liste)
    parcours = sorted({o.get("parcours") for o in objets if o.get("parcours")})
    variation = sum(1 for liste in fonctions if set(liste) & TRANSFER_FUNCTIONS)
    raisonnement = sum(1 for liste in fonctions if F_REASONING in liste)
    synthese = sum(1 for liste in fonctions if F_SYNTHESIS in liste)

    if not objets:
        raison = "aucun exercice ne porte cette capacite : rien n'entraine a rien"
    elif verdict["verdict"] == "DIVERSITY_SUFFICIENT":
        raison = (
            "l'eleve dispose d'une application directe et de "
            + ", ".join(verdict["transfer_functions"]).lower()
            + " : le transfert est travaille, ajouter des exercices n'ajouterait"
            " pas de diversite"
        )
    elif DIRECT not in natures:
        raison = (
            "aucun exercice n'installe le geste de base ; l'eleve rencontre la"
            " capacite d'emblee en situation"
        )
    else:
        raison = (
            f"les {len(objets)} exercices repetent l'application directe ; aucun"
            " ne change de contexte, de strategie ni de registre, donc l'eleve"
            " apprend une procedure et non une competence"
        )

    return {
        "CAPACITY_ID": code,
        "CURRENT_EXERCISES": len(objets),
        "EXERCISE_NATURES": dict(sorted(natures.items())),
        "CURRENT_VARIATION": variation,
        "CURRENT_REASONING": raisonnement,
        "CURRENT_SYNTHESIS": synthese,
        "DIFFICULTY_SPREAD": parcours,
        "DIVERSITY_VERDICT": verdict["verdict"],
        "REAL_DIVERSITY_GAP": verdict["verdict"] == "REAL_DIVERSITY_GAP",
        "MISSING_FUNCTIONS": verdict["missing"],
        "RATIONALE": raison,
        "OBJECTS": [o.get("id") for o in objets if o.get("id")],
    }


def _has_files(directory: Path) -> bool:
    return directory.is_dir() and any(directory.iterdir())


def _project_assessed(contrat: dict[str, Any]) -> bool:
    return contrat.get("assessment_mode") == "PROJECT_ASSESSMENT"


def _chapter_root(chapter: str) -> Path | None:
    for corpus in CORPORA:
        candidat = ROOT / corpus / chapter
        if (candidat / "contrat.yaml").is_file():
            return candidat
    return None


def audit(chapter: str) -> dict[str, Any]:
    racine = _chapter_root(chapter)
    if racine is None:
        raise ValueError(f"chapitre inconnu : {chapter}")
    contrat = yaml.safe_load((racine / "contrat.yaml").read_text(encoding="utf-8")) or {}
    capacites = [c["code"] for c in contrat.get("capacites", [])]

    exercices = _objects(racine / "exercices")
    corriges = _objects(racine / "corriges")
    evaluations = _objects(racine / "evaluations")
    remediations = _objects(racine / "remediation")
    methodes = _objects(racine / "methodes")
    cours = _objects(racine / "cours") + _objects(racine / "projet")

    par_capacite: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for objet in exercices:
        for code in objet.get("capacites_codes") or []:
            par_capacite[code].append(objet)

    # Neuf chapitres NSI laissent la majorite de leurs exercices sans capacite
    # declaree -- huit n'en declarent aucune, un seul sur cinquante-cinq. Les
    # exercices existent et sont riches ; c'est le rattachement qui manque.
    # Conclure « diversite insuffisante » serait un faux positif : le defaut
    # est editorial, pas pedagogique, et il porte son propre nom. On evalue
    # alors la diversite sur le vivier entier du chapitre, et on signale
    # separement le rattachement manquant. Le seuil est la majorite : tant
    # qu'une majorite d'exercices est rattachee, la lecture par capacite reste
    # evidente et c'est elle qui fait foi.
    rattaches = [o for o in exercices if o.get("capacites_codes")]
    non_rattaches = len(exercices) - len(rattaches)
    rattachement_absent = bool(exercices) and non_rattaches > len(rattaches)
    if rattachement_absent:
        globale = _analyse_capacite("*", exercices)
        globale["CAPACITY_ID"] = "CHAPTER_POOL"
        globale["RATIONALE"] = (
            "aucun exercice ne declare de capacite : la diversite est mesuree"
            " sur le vivier entier du chapitre, et le rattachement manquant"
            " est reporte comme defaut editorial distinct -- "
            + globale["RATIONALE"]
        )
        per_capacity = [globale]
    else:
        per_capacity = [
            _analyse_capacite(code, par_capacite.get(code, [])) for code in capacites
        ]
    lacunes = [a["CAPACITY_ID"] for a in per_capacity if a["REAL_DIVERSITY_GAP"]]

    directe = [
        code for code in capacites
        if any(
            o.get("parcours") == 1 or "calculer" in (o.get("competences") or [])
            for o in par_capacite.get(code, [])
        )
    ]
    variation = (
        capacites if rattachement_absent and not lacunes else
        [] if rattachement_absent else
        [a["CAPACITY_ID"] for a in per_capacity if not a["REAL_DIVERSITY_GAP"]]
    )
    raisonnement = [
        code for code in capacites
        if any("raisonner" in (o.get("competences") or []) for o in par_capacite.get(code, []))
    ]
    synthese = (
        any(o.get("parcours") == 3 for o in exercices)
        or any(len(o.get("capacites_codes") or []) >= 2 for o in evaluations + exercices)
    )
    parcours = sorted({o.get("parcours") for o in exercices if o.get("parcours")})
    fonctions_chapitre = sorted(
        {f for a in per_capacity for f in a["EXERCISE_NATURES"]}
    )

    couverture = {
        "DIRECT_APPLICATION_COVERAGE": f"{len(directe)}/{len(capacites)}",
        "VARIATION_COVERAGE": f"{len(variation)}/{len(capacites)}",
        "REASONING_COVERAGE": f"{len(raisonnement)}/{len(capacites)}",
        "SYNTHESIS_COVERAGE": "OUI" if synthese else "NON",
        "DIFFICULTY_PROGRESSION": parcours,
        "ASSESSMENT_COVERAGE": len(evaluations),
        "EXERCISE_FUNCTIONS_PRESENT": fonctions_chapitre,
        "CAPACITIES_WITH_REAL_DIVERSITY_GAP": lacunes,
        "CAPACITY_ASSIGNMENT_MISSING": rattachement_absent,
        "EXERCISES_WITHOUT_CAPACITY": non_rattaches,
    }

    axes = {
        "CAPACITY_ASSIGNMENT": WEAK if rattachement_absent else STRONG,
        "COURSE_COMPLETENESS": STRONG if len(cours) >= len(capacites) else (
            ADEQUATE if cours else WEAK
        ),
        "EXERCISE_DIVERSITY": (
            UNUSABLE if not exercices else
            WEAK if lacunes else
            STRONG if len(fonctions_chapitre) >= 4 else ADEQUATE
        ),
        "DIFFICULTY_PROGRESSION": (
            STRONG if len(parcours) >= 3 else
            ADEQUATE if len(parcours) == 2 else WEAK
        ),
        "CORRECTION_QUALITY": (
            STRONG if len(corriges) >= len(exercices) and exercices else
            ADEQUATE if corriges else WEAK
        ),
        "ASSESSMENT_QUALITY": (
            STRONG if len(evaluations) >= 2 else
            ADEQUATE if evaluations or contrat.get("assessment_mode") else WEAK
        ),
        "REMEDIATION": (
            STRONG if len(remediations) >= 3 else
            ADEQUATE if remediations else WEAK
        ),
    }

    # Un chapitre evalue par projet n'a pas de banque d'exercices, et ce n'est
    # pas un defaut : c'est la decision du 2026-09-06 inscrite au contrat. Les
    # quatre axes qui presupposent cette banque sont donc hors-sujet, et on les
    # remplace par ce que le mode PROJET exige vraiment. Neutraliser sans
    # remplacer serait une exemption ; remplacer, c'est mesurer autre chose.
    if _project_assessed(contrat) and not exercices:
        for axe in ("EXERCISE_DIVERSITY", "DIFFICULTY_PROGRESSION",
                    "CORRECTION_QUALITY", "REMEDIATION"):
            axes[axe] = NOT_APPLICABLE
        axes["PROJECT_BRIEF"] = STRONG if cours else UNUSABLE
        axes["PROJECT_CRITERIA_GRID"] = (
            STRONG if _has_files(racine / "validations") else WEAK
        )
        axes["PROJECT_KNOWLEDGE_CHECK"] = (
            STRONG if _has_files(racine / "qcm") else WEAK
        )
        axes["PROJECT_ADAPTED_VERSION"] = (
            STRONG if _has_files(racine / "amenagee") else WEAK
        )

    ordre = {STRONG: 3, ADEQUATE: 2, WEAK: 1, UNUSABLE: 0}
    applicables = [v for v in axes.values() if v != NOT_APPLICABLE]
    pire = min(applicables, key=lambda v: ordre[v])
    return {
        "CHAPTER_ID": chapter,
        "ASSESSMENT_MODE": contrat.get("assessment_mode") or "WRITTEN_ASSESSMENT",
        "OFFICIAL_CAPACITIES": capacites,
        "counts": {
            "cours": len(cours), "methodes": len(methodes),
            "exercices": len(exercices), "corriges": len(corriges),
            "evaluations": len(evaluations), "remediations": len(remediations),
        },
        "coverage": couverture,
        "uncovered": {
            "direct_application": [c for c in capacites if c not in directe],
            "variation": [c for c in capacites if c not in variation],
            "reasoning": [c for c in capacites if c not in raisonnement],
        },
        "per_capacity": per_capacity,
        **axes,
        "PEDAGOGICAL_VERDICT": pire,
    }


def build(chapters: list[str]) -> dict[str, Any]:
    lignes = [audit(chapter) for chapter in chapters]
    verdicts = collections.Counter(row["PEDAGOGICAL_VERDICT"] for row in lignes)
    return {
        "artifact_type": "chapter_pedagogical_verdict",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "rule": (
            "chaque verdict est derive des competences et parcours DECLARES "
            "par les exercices, croises avec les capacites du contrat ; aucun "
            "verdict n'est affirme"
        ),
        "approves_nothing": True,
        "summary": {
            "CHAPTERS_AUDITED": len(lignes),
            "VERDICTS": dict(sorted(verdicts.items())),
            "WEAK_OR_UNUSABLE": verdicts.get(WEAK, 0) + verdicts.get(UNUSABLE, 0),
        },
        "chapters": lignes,
    }


TCOMPL = [
    "TCOMPL-CALCULS-AIRES", "TCOMPL-CORRELATION-CAUSALITE",
    "TCOMPL-ECHANTILLONNAGE", "TCOMPL-INEGALITES",
    "TCOMPL-INFERENCE-BAYESIENNE", "TCOMPL-LOGARITHME-HISTORIQUE",
    "TCOMPL-MODELES-EVOLUTION", "TCOMPL-MODELES-FONCTION",
    "TCOMPL-TEMPS-ATTENTE",
]
TEXPERTES = [
    "TEXP-ARITHMETIQUE", "TEXP-COMPLEXES-ALGEBRE-GEOMETRIE",
    "TEXP-COMPLEXES-TRIGO-POLYNOMES", "TEXP-GRAPHES", "TEXP-MATRICES-MARKOV",
]


def render_markdown(payload: dict[str, Any]) -> str:
    lignes = [
        "# Verdict pedagogique par chapitre", "",
        payload["rule"].capitalize() + ".", "",
        "| chapitre | cours | ex | co | eval | rem | diversite | progression | verdict |",
        "| --- | ---: | ---: | ---: | ---: | ---: | --- | --- | --- |",
    ]
    for row in payload["chapters"]:
        c = row["counts"]
        lignes.append(
            f"| {row['CHAPTER_ID']} | {c['cours']} | {c['exercices']} | "
            f"{c['corriges']} | {c['evaluations']} | {c['remediations']} | "
            f"{row['EXERCISE_DIVERSITY']} | {row['DIFFICULTY_PROGRESSION']} | "
            f"**{row['PEDAGOGICAL_VERDICT']}** |"
        )
    lignes.append("")
    return "\n".join(lignes)


def all_chapters() -> list[str]:
    """TOUS les chapitres du corpus, pas seulement ceux qu'on a reconstruits.

    Restreindre la revue aux quatorze chapitres touches laisserait
    trente-huit chapitres NON AUDITES -- et « non audite » n'est pas
    « adequat ». Le gate exige un verdict pour chacun.
    """

    chapitres: list[str] = []
    for corpus in CORPORA:
        racine = ROOT / corpus
        if not racine.is_dir():
            continue
        chapitres.extend(
            sorted(
                d.name for d in racine.iterdir() if (d / "contrat.yaml").is_file()
            )
        )
    return sorted(chapitres)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build(all_chapters())
    rendus = {
        JSON_TARGET: json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        MD_TARGET: render_markdown(payload),
    }
    if args.check:
        ecarts = [
            str(p.relative_to(ROOT)) for p, c in rendus.items()
            if not p.is_file() or p.read_text(encoding="utf-8") != c
        ]
        for e in ecarts:
            print(f"diff: {e}")
        return 1 if ecarts else 0
    for chemin, contenu in rendus.items():
        chemin.write_text(contenu, encoding="utf-8")
        print(f"wrote {chemin.relative_to(ROOT)}")
    print(json.dumps(payload["summary"], ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
