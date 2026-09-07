#!/usr/bin/env python3
"""Juge l'applicabilité pédagogique réelle de chaque couple (capacité, rôle).

`TRUE_PEDAGOGICAL_COVERAGE` compte 441 cellules sans contenu VALIDE au sens de
sa règle de crédit : un objet ne crédite une capacité que s'il la déclare
exactement. Lire ce nombre comme « 441 objets à écrire » serait faux, et le
Release Owner l'a refusé explicitement.

Une cellule vide a cinq causes possibles, et une seule appelle de l'écriture.

`SATISFIED_BY_EXISTING_CONTENT`  un objet de ce rôle traite déjà cette
                                 capacité dans ce chapitre.
`SATISFIED_TRANSVERSALLY`        le rôle est présent dans le chapitre et sa
                                 règle admet qu'un objet couvre plusieurs
                                 capacités — un cours enseigne plusieurs
                                 capacités, un exercice en travaille
                                 plusieurs, une remédiation transversale en
                                 traite plusieurs.
`BAD_MAPPING`                    le contenu existe mais il est crédité à un
                                 autre rôle : c'est la cartographie qui est
                                 fausse, pas le corpus.
`ROLE_NOT_APPLICABLE`            le rôle n'est pas dû pour cette capacité :
                                 pas de corrigé sans objet source, pas de QCM
                                 par capacité hors politique canonique, pas de
                                 fiche méthode pour répéter une définition.
`REAL_PEDAGOGICAL_GAP`           il manque réellement quelque chose.

LES RÈGLES SONT CELLES DE LA DÉCISION HUMAINE, PAS LES MIENNES. Chaque verdict
cite la règle qui le fonde et les objets qu'il a constatés. Le verdict par
défaut est `REAL_PEDAGOGICAL_GAP` : une cellule qu'aucune règle ne couvre
reste une lacune, jamais une exemption par omission.
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import evidence_freshness as freshness  # noqa: E402

COVERAGE = ROOT / "audit/TRUE_PEDAGOGICAL_COVERAGE.json"
INVENTORY = ROOT / "audit/INVENTAIRE_COLLECTION.json"
OUTPUT_JSON = ROOT / "audit/PEDAGOGICAL_ROLE_APPLICABILITY_AUDIT.json"
OUTPUT_MD = ROOT / "audit/PEDAGOGICAL_ROLE_APPLICABILITY_AUDIT.md"

SATISFIED = "SATISFIED_BY_EXISTING_CONTENT"
TRANSVERSAL = "SATISFIED_TRANSVERSALLY"
BAD_MAPPING = "BAD_MAPPING"
NOT_APPLICABLE = "ROLE_NOT_APPLICABLE"
REAL_GAP = "REAL_PEDAGOGICAL_GAP"

VERDICTS = (SATISFIED, TRANSVERSAL, BAD_MAPPING, NOT_APPLICABLE, REAL_GAP)

#: Rôles dont la décision humaine admet explicitement qu'un objet couvre
#: plusieurs capacités. Le rôle doit être PRÉSENT dans le chapitre : la
#: transversalité couvre une déclaration incomplète, jamais une absence.
TRANSVERSAL_ROLES = {
    "cours": (
        "COURSE — plusieurs capacités peuvent être enseignées dans un même "
        "objet de cours ; un fichier distinct par capacité n'est pas requis."
    ),
    "exercices": (
        "EXERCISE — un même exercice peut travailler plusieurs capacités."
    ),
    "evaluations": (
        "ASSESSMENT — l'évaluation peut être écrite, pratique, projet, QCM ou "
        "synthèse selon le contrat pédagogique ; pas nécessairement un objet "
        "séparé par capacité."
    ),
    "remediation": (
        "REMEDIATION — une remédiation transversale peut couvrir plusieurs "
        "capacités."
    ),
}

#: Une capacite qu'AUCUN objet du chapitre ne declare, tous roles confondus.
#: La transversalite couvre une declaration incomplete — un cours qui enseigne
#: la capacite sans la nommer dans son META. Elle ne peut pas couvrir une
#: capacite dont le chapitre ne porte aucune trace : il n'y a alors aucun objet
#: a designer, et le verdict « transversal » ne renverrait a rien de
#: verifiable.
#:
#: Le depot en compte trois, toutes dans TCOMPL, et je les ai lues avant de
#: poser la regle :
#:
#:   TCOMPL-ECHANTILLONNAGE::C7  loi uniforme sur {1..n} et son esperance. Le
#:       seul « uniforme » du chapitre est le tirage `random` sur [0,1] servant
#:       a simuler une epreuve de Bernoulli : la loi n'est jamais definie.
#:   TCOMPL-MODELES-EVOLUTION::C6  limites de suites, operations sur les
#:       limites, passage a la limite dans les inegalites, theoreme des
#:       gendarmes. Le cours n'enonce que la limite d'une suite geometrique.
#:   TCOMPL-TEMPS-ATTENTE::C7  loi uniforme sur [0,1] puis [a,b], densite,
#:       fonction de repartition, esperance et variance. Le chapitre traite la
#:       loi geometrique et la loi exponentielle ; « uniforme » n'apparait que
#:       dans le contrat.
#:
#: La regle se retire d'elle-meme : des qu'un objet declare la capacite, la
#: cellule n'est plus orpheline et les regles ordinaires reprennent.
ORPHAN_RULE = (
    "Aucun objet du chapitre ne déclare cette capacité, tous rôles confondus : "
    "la transversalité couvre une déclaration incomplète, pas une absence de "
    "contenu. La capacité est au contrat et n'est enseignée nulle part."
)

QCM_POLICY = (
    "QCM — non obligatoire par capacité hors politique canonique explicite. "
    "La politique déposée (audit/QCM_POLICY_ORIGIN.md) fixe "
    "PEDAGOGICALLY_REQUIRED_QCM_GAPS = 0 et atteste une couverture "
    "d'auto-évaluation de 52/52 chapitres : le QCM diagnostique le chapitre, "
    "il n'atomise pas ses capacités."
)

CORRECTION_RULE = (
    "CORRECTION — exigée seulement lorsqu'il existe un exercice ou une "
    "évaluation nécessitant une correction. Pas de corrigé artificiel sans "
    "objet source."
)

#: Chapitres dont le mode d'evaluation est le projet annuel. La decision
#: humaine du 2026-09-06 fixe `ASSESSMENT_MODE = PROJECT_ASSESSMENT` : le
#: chapitre porte le projet et sa grille criteriee, pas un cours, des
#: exercices, des evaluations ou une remediation separes.
PROJECT_ASSESSED = {
    ("TNSI", "TNSI-PROJET"): (
        "ASSESSMENT_MODE = PROJECT_ASSESSMENT (décision humaine du "
        "2026-09-06). Le chapitre porte le projet annuel `TNSI-PROJET-ANNUEL` "
        "et sa grille critériée, qui déclarent C1 et C2. Un cours, des "
        "exercices, des évaluations ou une remédiation séparés y seraient sans "
        "objet : ce n'est pas ainsi que ce chapitre enseigne ni évalue."
    ),
}
PROJECT_ROLES = frozenset(
    {"cours", "exercices", "evaluations", "remediation", "corriges", "methodes"}
)

#: `BAD_MAPPING` n'est assigne par aucune regle, et le compteur reste a zero.
#: Ce n'est pas un oubli : je n'ai trouve, dans les donnees disponibles, aucun
#: critere qui etablisse mecaniquement qu'un contenu existe et se trouve
#: credite au mauvais role. Une premiere tentative comparait le type d'objet
#: aux roles mesures ; elle a produit 64 verdicts en confondant deux choses —
#: les types canoniques sont au singulier quand les roles sont au pluriel, si
#: bien que `exercice` paraissait non mesure, et surtout un exercice qui
#: declare une capacite ne rend pas la fiche methode de cette capacite « mal
#: cartographiee ». Inventer le critere aurait rempli une categorie que la
#: preuve ne soutient pas.
METHOD_RULE = (
    "METHOD — nécessaire seulement lorsqu'il existe une démarche réutilisable "
    "qui mérite d'être formalisée. Pas de fiche méthode pour répéter une "
    "définition."
)


def _index(coverage: dict[str, Any]) -> dict[str, Any]:
    """Ce que le chapitre contient réellement, par rôle et par capacité."""
    role_objects: dict[tuple, set[str]] = collections.defaultdict(set)
    capacity_roles: dict[tuple, set[str]] = collections.defaultdict(set)
    for row in coverage["rows"]:
        cle = (row["manual"], row["chapter"])
        if row.get("valid_objects", 0) > 0:
            role_objects[(cle[0], cle[1], row["role"])].update(
                row.get("valid_object_ids") or []
            )
            capacity_roles[(cle[0], cle[1], row["capacity"])].add(row["role"])
    return {"role_objects": role_objects, "capacity_roles": capacity_roles}


def _remediation_verdict(unit: dict[str, Any]) -> tuple[str, str] | None:
    """Verdict d'applicabilite deja rendu pour la remediation d'un chapitre."""
    try:
        from build_auxiliary_rubric_applicability import (  # noqa: PLC0415
            COVERED_ELSEWHERE, NOT_REQUIRED, VERDICTS as RUBRIC_VERDICTS,
        )
    except ImportError:
        return None
    declare = RUBRIC_VERDICTS.get((unit["chapter"], "remediation"))
    if declare is None:
        return None
    if declare["verdict"] == NOT_REQUIRED:
        return NOT_APPLICABLE, declare["evidence"]
    if declare["verdict"] == COVERED_ELSEWHERE:
        return TRANSVERSAL, declare["evidence"]
    return None


def _method_verdict(
    unit: dict[str, Any],
) -> tuple[str, str, str | None] | None:
    """Verdict éditorial déjà rendu pour les fiches méthode.

    L'audit `METHOD_SHEET_REQUIREMENT_AUDIT` a jugé une par une les capacités
    des vingt-cinq chapitres qui portent une exigence de méthode — d'abord les
    53 de 1NSI, puis les 118 des seize chapitres que ce triage avait laissés
    sans verdict. Le refaire ici en dupliquerait la décision ; on la lit.
    """
    try:
        from method_sheet_decisions import (  # noqa: PLC0415
            CAPACITY_VERDICTS, DECLARATIVE, PROCEDURAL_COVERED,
        )
    except ImportError:
        return None
    decision = CAPACITY_VERDICTS.get(unit["chapter"], {}).get(unit["capacity"])
    if decision is None:
        return None
    verdict, raison, couvrant = decision
    if verdict == DECLARATIVE:
        return NOT_APPLICABLE, f"{METHOD_RULE} Verdict déposé : {raison}", None
    if verdict == PROCEDURAL_COVERED:
        # L'objet qui couvre est un cours, une fiche existante ou un
        # répertoire : il n'est pas de ce rôle-ci, mais il doit être NOMMÉ,
        # sans quoi le verdict ne renvoie à rien de vérifiable.
        return SATISFIED, f"{METHOD_RULE} Verdict déposé : {raison}", couvrant
    return None


def classify(unit: dict[str, Any], index: dict[str, Any]) -> dict[str, Any]:
    manual, chapter = unit["manual"], unit["chapter"]
    capacity, role = unit["capacity"], unit["role"]
    role_objects = sorted(index["role_objects"].get((manual, chapter, role), ()))
    autres_roles = sorted(
        index["capacity_roles"].get((manual, chapter, capacity), ())
    )

    verdict, rationale, source = REAL_GAP, None, None

    if unit.get("valid_objects", 0) > 0:
        verdict = SATISFIED
        rationale = "Un objet de ce rôle déclare exactement cette capacité."
        source = "TRUE_PEDAGOGICAL_COVERAGE.rows"
    elif (manual, chapter) in PROJECT_ASSESSED and role in PROJECT_ROLES:
        verdict, rationale = NOT_APPLICABLE, PROJECT_ASSESSED[(manual, chapter)]
        source = "audit/TNSI_PROJET_ASSESSMENT_MODE.json"
    elif role in TRANSVERSAL_ROLES and not autres_roles:
        rationale = f"{TRANSVERSAL_ROLES[role]} {ORPHAN_RULE}"
        source = "ORPHAN_CAPACITY"
    elif role == "remediation" and _remediation_verdict(unit) is not None:
        verdict, rationale = _remediation_verdict(unit)
        source = "audit/AUXILIARY_RUBRIC_APPLICABILITY.json"
        if verdict == TRANSVERSAL and not role_objects:
            # La couverture vient d'un AUTRE rôle — les diagnostics du QCM du
            # chapitre. Nommer ces objets-là, sans quoi le verdict
            # « transversal » ne désignerait rien de vérifiable.
            role_objects = sorted(
                index["role_objects"].get((manual, chapter, "qcm"), ())
            )
    elif role == "qcm":
        if role_objects:
            verdict, rationale = NOT_APPLICABLE, QCM_POLICY
            source = "audit/QCM_POLICY_ORIGIN.md"
        else:
            rationale = (
                "Le chapitre ne porte aucun QCM : la couverture "
                "d'auto-évaluation qu'invoque la politique n'est pas acquise."
            )
    elif role == "corriges":
        besoin = {"exercices", "evaluations"} & set(autres_roles)
        if not besoin:
            verdict, rationale = NOT_APPLICABLE, CORRECTION_RULE
            source = "décision humaine §5 CORRECTION"
        elif role_objects:
            verdict, rationale = TRANSVERSAL, (
                f"{CORRECTION_RULE} Le chapitre porte des corrigés ; la "
                "correction de cette capacité peut y figurer sans que l'objet "
                "la déclare."
            )
            source = "décision humaine §5 CORRECTION"
        else:
            rationale = (
                f"{CORRECTION_RULE} Un objet source existe pour cette "
                f"capacité ({', '.join(besoin)}) mais le chapitre ne porte "
                "aucun corrigé."
            )
    elif role == "methodes":
        depose = _method_verdict(unit)
        if depose is not None:
            verdict, rationale, couvrant = depose
            source = "audit/METHOD_SHEET_REQUIREMENT_AUDIT.json"
            if couvrant:
                role_objects = [couvrant]
        else:
            rationale = (
                f"{METHOD_RULE} Aucun verdict éditorial n'a été rendu pour "
                "cette capacité : elle reste une lacune tant que l'absence "
                "n'est pas justifiée."
            )
    elif role in TRANSVERSAL_ROLES:
        if role_objects:
            verdict, rationale = TRANSVERSAL, (
                f"{TRANSVERSAL_ROLES[role]} Le chapitre porte "
                f"{len(role_objects)} objet(s) de ce rôle."
            )
            source = f"décision humaine §5 {role.upper()}"
        else:
            rationale = (
                f"{TRANSVERSAL_ROLES[role]} Le chapitre n'en porte aucun : "
                "la transversalité ne peut pas couvrir une absence."
            )
    else:
        rationale = f"Rôle {role} sans règle d'applicabilité déposée."

    return {
        "MANUAL": manual,
        "CHAPTER": chapter,
        "CAPACITY": capacity,
        "ROLE": role,
        "CURRENT_OBJECTS": sorted(unit.get("valid_object_ids") or []),
        "TRANSVERSAL_OBJECTS": role_objects,
        "REQUIREMENT_SOURCE": source or "TRUE_PEDAGOGICAL_COVERAGE",
        "APPLICABILITY_VERDICT": verdict,
        "RATIONALE": rationale,
        "capacity_covered_by_roles": autres_roles,
        "canonical_capacity_uid": unit["canonical_capacity_uid"],
    }


def build(root: Path = ROOT) -> dict[str, Any]:
    coverage = json.loads(COVERAGE.read_text(encoding="utf-8"))
    index = _index(coverage)
    units = [
        classify(unit, index) for unit in coverage["authoring_backlog"]
    ]

    counts = collections.Counter(u["APPLICABILITY_VERDICT"] for u in units)
    inconnus = set(counts) - set(VERDICTS)
    if inconnus:
        raise ValueError(f"verdicts hors nomenclature: {sorted(inconnus)}")

    total = len(units)
    somme = sum(counts.values())
    if somme != total:
        raise ValueError(f"items perdus: {somme} != {total}")

    summary = {
        "PEDAGOGICAL_ROLE_UNITS_TOTAL": total,
        SATISFIED: counts.get(SATISFIED, 0),
        TRANSVERSAL: counts.get(TRANSVERSAL, 0),
        BAD_MAPPING: counts.get(BAD_MAPPING, 0),
        NOT_APPLICABLE: counts.get(NOT_APPLICABLE, 0),
        REAL_GAP: counts.get(REAL_GAP, 0),
        "CATEGORIES_SUM": somme,
        "NO_ITEM_LOST": somme == total,
    }
    payload = {
        "artifact_type": "pedagogical_role_applicability_audit",
        "schema_version": 1,
        "generated_by": "scripts/build_pedagogical_role_applicability.py",
        "approves_nothing": True,
        "verdict_nomenclature": list(VERDICTS),
        "default_verdict": REAL_GAP,
        "rules": {
            "TRANSVERSAL_ROLES": TRANSVERSAL_ROLES,
            "QCM": QCM_POLICY,
            "CORRECTION": CORRECTION_RULE,
            "METHOD": METHOD_RULE,
        },
        "summary": summary,
        "units": units,
    }
    payload["freshness"] = freshness.stamp(
        ["audit/TRUE_PEDAGOGICAL_COVERAGE.json", "audit/QCM_POLICY_ORIGIN.md",
         "audit/METHOD_SHEET_REQUIREMENT_AUDIT.json"],
        root=root,
    )
    return payload


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lines = [
        "# Applicabilité pédagogique des rôles — triage des unités",
        "",
        f"- `PEDAGOGICAL_ROLE_UNITS_TOTAL` : **{s['PEDAGOGICAL_ROLE_UNITS_TOTAL']}**",
        f"- `SATISFIED_BY_EXISTING_CONTENT` : `{s[SATISFIED]}`",
        f"- `SATISFIED_TRANSVERSALLY` : `{s[TRANSVERSAL]}`",
        f"- `BAD_MAPPING` : `{s[BAD_MAPPING]}`",
        f"- `ROLE_NOT_APPLICABLE` : `{s[NOT_APPLICABLE]}`",
        f"- `REAL_PEDAGOGICAL_GAP` : **{s[REAL_GAP]}**",
        "",
        f"Somme des catégories : `{s['CATEGORIES_SUM']}` — aucun item perdu : "
        f"`{s['NO_ITEM_LOST']}`.",
        "",
        "## Lacunes réelles, par manuel et par rôle",
        "",
        "| Manuel | Rôle | Lacunes |",
        "|---|---|---|",
    ]
    gaps = collections.Counter(
        (u["MANUAL"], u["ROLE"]) for u in payload["units"]
        if u["APPLICABILITY_VERDICT"] == REAL_GAP
    )
    for (manual, role), n in sorted(gaps.items()):
        lines.append(f"| {manual} | {role} | {n} |")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    rendered = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    if args.check:
        if not OUTPUT_JSON.is_file() or \
                OUTPUT_JSON.read_text(encoding="utf-8") != rendered:
            print("PEDAGOGICAL_ROLE_APPLICABILITY_AUDIT check: STALE")
            return 1
        print("PEDAGOGICAL_ROLE_APPLICABILITY_AUDIT check: OK")
        return 0
    OUTPUT_JSON.write_text(rendered, encoding="utf-8")
    OUTPUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
