#!/usr/bin/env python3
"""Ce que devenaient les treize « manquants » et les quarante-cinq « partiels ».

Un compteur qui passe de treize a zero ne prouve rien par lui-meme : il peut
signaler un manuel complete, un outillage repare, ou une mesure assouplie. Ce
producteur repond attendu par attendu, en confrontant l'etat fige AVANT la
contre-expertise a la matrice courante.

Trois verdicts pour les manquants :

- FALSE_MISSING_TOOLING : le manuel le traitait ; c'est la mesure qui ne le
  voyait pas ;
- MISSING_FROM_ASSEMBLY : le contenu existait, mais aucun manuel assemble ne
  le portait ;
- TRUE_CONTENT_GAP : le contenu manquait reellement, et il a fallu l'ecrire.

Deux pour les partiels :

- FALSE_PARTIAL_TOOLING : l'entrainement existait sous une forme que le
  controle n'acceptait pas ;
- TRUE_PARTIAL_PEDAGOGICAL : l'entrainement manquait vraiment.

Aucun chiffre de ce rapport n'est saisi a la main : tout se deduit de
`audit/baselines/COVERAGE_BEFORE_COUNTER_EXPERTISE.json` et de la matrice
courante.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / "audit" / "baselines" / "COVERAGE_BEFORE_COUNTER_EXPERTISE.json"
COVERAGE = ROOT / "audit" / "OFFICIAL_TO_MANUAL_COVERAGE.json"
OUT = ROOT / "audit" / "PROGRAMME_COUNTER_EXPERTISE_REPORT.json"
OUT_MD = ROOT / "audit" / "PROGRAMME_COUNTER_EXPERTISE_REPORT.md"

#: Ce que la seule comparaison des artefacts ne peut pas savoir : qu'un
#: contenu a ete ECRIT, qu'une page existante n'etait pas assemblee, ou qu'un
#: entrainement manquait vraiment. Chaque entree nomme le fichier qui la
#: prouve ; un chemin qui n'existe plus fait echouer la generation.
DISPOSITIONS: tuple[dict[str, Any], ...] = (
    {
        "manual": "TCOMPL",
        "wording_prefix": "Statistique descriptive : caractéristiques de dispersion",
        "verdict": "TRUE_CONTENT_GAP",
        "cause": "aucun cours du manuel n'exposait mediane, quartiles, deciles ni rapport interdecile",
        "modification": "cours redige : dispersion, quartiles, deciles, rapport interdecile, exemple travaille sur vingt revenus",
        "content_created": (
            "Mathematiques/manuel-maths/chapitres/TCOMPL-INEGALITES/cours/10_C0_dispersion.tex",
        ),
    },
    {
        "manual": "TSPE",
        "wording_prefix": "Développement de u",
        "verdict": "TRUE_CONTENT_GAP",
        "cause": "le chapitre traitait le produit scalaire sans developper la norme d'une somme ni enoncer les formules de polarisation",
        "modification": "cours redige : developpement de la norme d'une somme et d'une difference, les deux formules de polarisation et leurs demonstrations",
        "content_created": (
            "Mathematiques/manuel-maths/chapitres/TSPE-GEOMETRIE-ESPACE/cours/12_C7_produit_scalaire.tex",
        ),
    },
    {
        "manual": "TCOMPL",
        "wording_prefix": "reconnaître ce qu’est une proposition mathématique",
        "verdict": "MISSING_FROM_ASSEMBLY",
        "cause": "la page transversale de logique existait, mais l'assembleur ne la portait dans aucun manuel de terminale complementaire",
        "modification": "ANNEXES_TRANSVERSALES etendu : une source logique canonique, plusieurs assemblages",
        "content_created": (),
    },
    {
        "manual": "TCOMPL",
        "wording_prefix": "lire et écrire des propositions contenant les connecteurs",
        "verdict": "MISSING_FROM_ASSEMBLY",
        "cause": "meme cause : page transversale existante, absente de l'assemblage TCOMPL",
        "modification": "ANNEXES_TRANSVERSALES etendu",
        "content_created": (),
    },
    {
        "manual": "TCOMPL",
        "wording_prefix": "formuler une implication, une équivalence logique",
        "verdict": "MISSING_FROM_ASSEMBLY",
        "cause": "meme cause : page transversale existante, absente de l'assemblage TCOMPL",
        "modification": "ANNEXES_TRANSVERSALES etendu",
        "content_created": (),
    },
    {
        "manual": "TCOMPL",
        "wording_prefix": "lire et écrire des propositions contenant une quantification",
        "verdict": "MISSING_FROM_ASSEMBLY",
        "cause": "meme cause : page transversale existante, absente de l'assemblage TCOMPL",
        "modification": "ANNEXES_TRANSVERSALES etendu",
        "content_created": (),
    },
    {
        "manual": "1SPE",
        "wording_prefix": "Calcul de cos",
        "verdict": "TRUE_CONTENT_GAP",
        "cause": (
            "le libelle officiel a perdu ses fractions a l'extraction "
            "(« Calcul de cos , sin , cos , sin . 4 4 3 3 ») : aucune "
            "recherche n'etait possible. La lecture du chapitre a montre que "
            "les valeurs remarquables etaient donnees sans etre demontrees"
        ),
        "modification": (
            "demonstration complete redigee : cosinus et sinus de pi/4, pi/3 "
            "et pi/6, avec hypotheses et chaine logique, plus bloc VERIFY etendu"
        ),
        "content_created": (
            "Mathematiques/manuel-maths/chapitres/1SPE-TRIGONOMETRIE/cours/"
            "11_C2_cosinus_sinus.tex",
        ),
    },
    {
        "manual": "1SPE",
        "wording_prefix": "Calculer un taux d’évolution réciproque",
        "verdict": "TRUE_PARTIAL_PEDAGOGICAL",
        "cause": "automatisme travaille dans un seul chapitre, ce que le programme exclut",
        "modification": "reinvestissement ecrit dans un autre chapitre, avec son corrige",
        "content_created": (
            "Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/exercices/1SPE-EXPO-EX-051.tex",
            "Mathematiques/manuel-maths/chapitres/1SPE-EXPONENTIELLE/corriges/1SPE-EXPO-CO-051.tex",
        ),
    },
    {
        "manual": "1SPE",
        "wording_prefix": "Calculer le taux d’évolution équivalent",
        "verdict": "TRUE_PARTIAL_PEDAGOGICAL",
        "cause": "automatisme travaille dans un seul chapitre, ce que le programme exclut",
        "modification": "reinvestissement ecrit dans un autre chapitre, avec son corrige",
        "content_created": (
            "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/exercices/1SPE-SUITES-EX-052.tex",
            "Mathematiques/manuel-maths/chapitres/1SPE-SUITES/corriges/1SPE-SUITES-CO-052.tex",
        ),
    },
    {
        "manual": "1SPE",
        "wording_prefix": "Calculer et interpréter des indicateurs statistiques",
        "verdict": "TRUE_PARTIAL_PEDAGOGICAL",
        "cause": "automatisme travaille dans un seul chapitre, ce que le programme exclut",
        "modification": "reinvestissement ecrit dans un autre chapitre, avec son corrige",
        "content_created": (
            "Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/exercices/1SPE-VARALEA-EX-055.tex",
            "Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/corriges/1SPE-VARALEA-CO-055.tex",
        ),
    },
)

#: Ce qu'un changement de nature de preuve dit de la cause. La correspondance
#: n'est pas une supposition : chaque nature nomme le defaut d'outillage qui a
#: ete repare pour l'obtenir.
CAUSES_PAR_PREUVE = {
    "OFFICIAL_ROW_EVIDENCE": (
        "la ligne du tableau officiel n'etait pas conservee : le contenu et "
        "les capacites qui le realisent etaient mesures separement"
    ),
    "CONTENT_MATCH_MANUAL_WIDE": (
        "la recherche etait bornee a une portee de theme, et s'arretait avant "
        "le reste du manuel -- une page transversale ou un autre chapitre"
    ),
    "CONTENT_MATCH": (
        "l'attendu n'etait rattache a aucun atome, et le rapprochement par "
        "contenu ne concluait pas"
    ),
    "DECLARED_CAPACITY": (
        "l'attendu n'avait aucun parent etabli : la disposition a tranche le "
        "rattachement"
    ),
    "ALGORITHMIC_WORK_IN_THE_SAME_PART": (
        "le programme nomme un exemple d'algorithme sans l'imposer ; le "
        "travail algorithmique de la partie le sert"
    ),
}


def _disposition(ligne: dict[str, Any]) -> dict[str, Any] | None:
    for entree in DISPOSITIONS:
        if entree["manual"] == ligne["manual"] and ligne[
            "official_wording"
        ].startswith(entree["wording_prefix"]):
            return entree
    return None


def _verdict_derive(
    avant: dict[str, Any], apres: dict[str, Any]
) -> tuple[str, str, str]:
    """Verdict, cause et modification, sans aucune saisie manuelle."""
    faux = {
        "MISSING": "FALSE_MISSING_TOOLING",
        "PARTIAL": "FALSE_PARTIAL_TOOLING",
        "UNDECIDABLE_BY_CONTENT_MATCH": "FALSE_MISSING_TOOLING",
    }[avant["coverage_status"]]
    if not apres["mandatory"]:
        return (
            faux,
            "NORMATIVITY_MISCLASSIFIED : le BO nomme un exemple d'algorithme, "
            "il ne l'impose pas ; l'atomisation en avait fait une obligation",
            "normativite corrigee ; l'attendu ne compte plus au denominateur "
            "des obligations",
        )
    if apres["evidence_kind"] == "CONTRADICTORY_REVIEW":
        revue = apres["contradictory_review"]
        return (
            faux,
            revue.get("cause")
            or "verdict rendu a la lecture de l'objet, et non au rapprochement de mots",
            "revue contradictoire declaree ; verdict rendu a la lecture de "
            f"l'objet : {revue.get('verdict', '?')}",
        )
    cause = CAUSES_PAR_PREUVE.get(
        apres["evidence_kind"], f"nature de preuve {apres['evidence_kind']}"
    )
    return faux, cause, f"preuve etablie par {apres['evidence_kind']}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    base = json.loads(BASELINE.read_text(encoding="utf-8"))
    courante = json.loads(COVERAGE.read_text(encoding="utf-8"))
    par_id = {r["official_id"]: r for r in courante["rows"]}

    lignes: list[dict[str, Any]] = []
    ecrits: list[dict[str, Any]] = []
    for avant in base["rows"]:
        apres = par_id.get(avant["official_id"])
        if apres is None:
            print(
                f"ATTENDU DISPARU : {avant['official_id']}\n"
                "Un attendu de la ligne de base doit rester dans la matrice : "
                "sa disparition serait un changement de perimetre, pas une "
                "couverture.",
                file=sys.stderr,
            )
            return 2
        disposition = _disposition(avant)
        if disposition is not None:
            verdict = disposition["verdict"]
            cause = disposition["cause"]
            modification = disposition["modification"]
            crees = list(disposition["content_created"])
            for chemin in crees:
                if not (ROOT / chemin).exists():
                    print(f"CONTENU DECLARE INTROUVABLE : {chemin}", file=sys.stderr)
                    return 2
        else:
            verdict, cause, modification = _verdict_derive(avant, apres)
            crees = []
        ligne = {
            "official_id": avant["official_id"],
            "manual": avant["manual"],
            "official_wording": avant["official_wording"],
            "official_normativity_before": avant["official_normativity"],
            "mandatory_now": apres["mandatory"],
            "ancien_verdict": avant["coverage_status"],
            "ancien_motif": avant["coverage_reason"],
            "verdict_apres_contre_expertise": verdict,
            "cause": cause,
            "existing_evidence_if_any": sorted(
                oid
                for role in apres["objects_by_role"]
                for oid in apres["objects_by_role"][role]
            )[:6],
            "evidence_kind_now": apres["evidence_kind"],
            "coverage_status_now": apres["coverage_status"],
            "modification_effectuee": modification,
            "content_created": "YES" if crees else "NO",
            "content_paths": crees,
        }
        lignes.append(ligne)
        for chemin in crees:
            ecrits.append({
                "path": chemin,
                "official_id": avant["official_id"],
                "manual": avant["manual"],
                "official_wording": avant["official_wording"],
                "verdict": verdict,
            })

    anciens_manquants = [x for x in lignes if x["ancien_verdict"] == "MISSING"]
    anciens_partiels = [x for x in lignes if x["ancien_verdict"] == "PARTIAL"]
    anciens_indecidables = [
        x for x in lignes
        if x["ancien_verdict"] == "UNDECIDABLE_BY_CONTENT_MATCH"
    ]
    compte_indecidables = Counter(
        x["verdict_apres_contre_expertise"] for x in anciens_indecidables
    )
    compte_manquants = Counter(
        x["verdict_apres_contre_expertise"] for x in anciens_manquants
    )
    compte_partiels = Counter(
        x["verdict_apres_contre_expertise"] for x in anciens_partiels
    )

    charge = {
        "artifact_type": "programme_counter_expertise_report",
        "schema_version": 1,
        "generated_by": "scripts/build_counter_expertise_report.py",
        "question": (
            "Chacun des treize « manquants » et des quarante-cinq « partiels » "
            "a-t-il ete refute, assemble, ou reellement comble ?"
        ),
        "baseline_commit": base["source_commit"],
        "summary": {
            "MISSING_BEFORE": base["MISSING_BEFORE"],
            "PARTIAL_BEFORE": base["PARTIAL_BEFORE"],
            "UNDECIDABLE_BEFORE": base["UNDECIDABLE_BEFORE"],
            "FALSE_MISSING_TOOLING": compte_manquants.get("FALSE_MISSING_TOOLING", 0),
            "MISSING_FROM_ASSEMBLY": compte_manquants.get("MISSING_FROM_ASSEMBLY", 0),
            "TRUE_CONTENT_GAP": compte_manquants.get("TRUE_CONTENT_GAP", 0),
            "FALSE_PARTIAL_TOOLING": compte_partiels.get("FALSE_PARTIAL_TOOLING", 0),
            "TRUE_PARTIAL_PEDAGOGICAL": compte_partiels.get(
                "TRUE_PARTIAL_PEDAGOGICAL", 0
            ),
            "UNDECIDABLE_FALSE_MISSING_TOOLING": compte_indecidables.get(
                "FALSE_MISSING_TOOLING", 0
            ),
            "UNDECIDABLE_TRUE_CONTENT_GAP": compte_indecidables.get(
                "TRUE_CONTENT_GAP", 0
            ),
            "OFFICIAL_REQUIRED_MISSING_NOW": courante["summary"][
                "OFFICIAL_REQUIRED_MISSING"
            ],
            "OFFICIAL_REQUIRED_PARTIAL_NOW": courante["summary"][
                "OFFICIAL_REQUIRED_PARTIAL"
            ],
            "CONTENT_CREATED_BECAUSE_PROGRAMME_REALLY_MISSING": len(ecrits),
        },
        "former_missing": anciens_manquants,
        "former_partial": anciens_partiels,
        "former_undecidable": anciens_indecidables,
        "CONTENT_CREATED_BECAUSE_PROGRAMME_REALLY_MISSING": ecrits,
        # Ecrit aussi, mais pour une autre raison, et le dire est la moitie du
        # travail : le BO NOMME ces deux simulations sans les imposer. Les
        # ranger avec les manques du programme aurait fait passer un
        # enrichissement pour une obligation comblee.
        "EDITORIAL_QUALITY_ENRICHMENT": [
            {
                "path": chemin,
                "standard": "NEXUS_ALGORITHMIC_QUALITY_STANDARD",
                "official_basis": "Exemple d'algorithme cite par le programme, non impose",
            }
            for chemin in (
                "Mathematiques/manuel-maths/chapitres/TSPE-PROBABILITES/cours/"
                "17_ALG_planche_de_galton.tex",
                "Mathematiques/manuel-maths/chapitres/TSPE-PROBABILITES/cours/"
                "18_ALG_marche_aleatoire.tex",
            )
        ],
    }
    for enrichissement in charge_enrichissements(charge):
        if not (ROOT / enrichissement).exists():
            print(f"ENRICHISSEMENT INTROUVABLE : {enrichissement}", file=sys.stderr)
            return 2
    texte = json.dumps(charge, ensure_ascii=False, indent=2) + "\n"
    markdown = _markdown(charge)
    if args.check:
        for chemin, attendu in ((OUT, texte), (OUT_MD, markdown)):
            if not chemin.exists() or chemin.read_text(encoding="utf-8") != attendu:
                print(f"DIVERGENT : {chemin.relative_to(ROOT)}")
                return 1
        print("Rapport de contre-expertise conforme au generateur.")
        return 0
    OUT.write_text(texte, encoding="utf-8")
    OUT_MD.write_text(markdown, encoding="utf-8")
    for cle, valeur in charge["summary"].items():
        print(f"{cle} = {valeur}")
    return 0


def _cellule(valeur: str) -> str:
    return valeur.replace("|", "/").replace("\n", " ")


def _markdown(charge: dict[str, Any]) -> str:
    resume = charge["summary"]
    lignes = [
        "# Contre-expertise des attendus non couverts",
        "",
        "Artefact derive : `audit/PROGRAMME_COUNTER_EXPERTISE_REPORT.json`.",
        "Aucun chiffre de cette page n'est saisi a la main ; tous viennent du",
        "generateur `scripts/build_counter_expertise_report.py`, qui compare",
        f"la ligne de base `{charge['baseline_commit'][:9]}` a la matrice courante.",
        "",
        "## Synthese",
        "",
        "| Compteur | Valeur |",
        "| --- | --- |",
    ]
    lignes += [f"| {cle} | {valeur} |" for cle, valeur in resume.items()]
    for titre, cle in (
        ("Les anciens « manquants »", "former_missing"),
        ("Les anciens « partiels »", "former_partial"),
        ("Les anciens « indecidables »", "former_undecidable"),
    ):
        lignes += [
            "",
            f"## {titre}",
            "",
            "| Manuel | Attendu officiel | Ancien verdict | Verdict apres "
            "contre-expertise | Cause | Preuve existante | Modification | "
            "Contenu ecrit |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        for x in charge[cle]:
            preuves = ", ".join(x["existing_evidence_if_any"]) or "—"
            lignes.append(
                f"| {x['manual']} | {_cellule(x['official_wording'][:90])} | "
                f"{x['ancien_verdict']} | {x['verdict_apres_contre_expertise']} | "
                f"{_cellule(x['cause'][:150])} | {_cellule(preuves)} | "
                f"{_cellule(x['modification_effectuee'][:120])} | "
                f"{x['content_created']} |"
            )
    lignes += [
        "",
        "## CONTENT_CREATED_BECAUSE_PROGRAMME_REALLY_MISSING",
        "",
        "Ce qui a ete ECRIT, et rien d'autre : les reparations d'outillage n'y",
        "figurent pas.",
        "",
        "| Fichier | Manuel | Attendu | Verdict |",
        "| --- | --- | --- | --- |",
    ]
    for x in charge["CONTENT_CREATED_BECAUSE_PROGRAMME_REALLY_MISSING"]:
        lignes.append(
            f"| `{x['path']}` | {x['manual']} | "
            f"{_cellule(x['official_wording'][:70])} | {x['verdict']} |"
        )
    lignes += [
        "",
        "## EDITORIAL_QUALITY_ENRICHMENT",
        "",
        "Ecrit aussi, mais pour une autre raison : le programme NOMME ces",
        "exemples d'algorithme sans les imposer. Ils ne comblent aucun manque",
        "obligatoire et ne comptent a aucun denominateur.",
        "",
        "| Fichier | Fondement | Norme |",
        "| --- | --- | --- |",
    ]
    for x in charge["EDITORIAL_QUALITY_ENRICHMENT"]:
        lignes.append(
            f"| `{x['path']}` | {_cellule(x['official_basis'])} | {x['standard']} |"
        )
    return "\n".join(lignes) + "\n"


def charge_enrichissements(charge: dict[str, Any]) -> list[str]:
    return [x["path"] for x in charge["EDITORIAL_QUALITY_ENRICHMENT"]]


if __name__ == "__main__":
    sys.exit(main())
