#!/usr/bin/env python3
"""Separer ce qui abime le produit de ce qui manque a la paperasse.

Une campagne de gouvernance finit toujours par confondre deux choses tres
differentes : un manuel qui contient une erreur, et un manuel dont personne
n'a encore signe la fiche. Les deux apparaissaient ici sous le meme mot --
« bloqueur » -- et la publication attendait donc autant une formule fausse
qu'un accuse de lecture manquant.

Le Release Owner a tranche : une dette de revue procedurale n'est pas un
defaut produit. Ce module ecrit cette distinction, la rend verifiable, et
classe chaque bloqueur suivi dans l'une des deux familles.

Ce qui reste bloquant est ce qui atteint le lecteur : une erreur
mathematique, un corrige faux, un programme officiel mal rendu, du code
imprime inexecutable, un PDF qui ne compile pas, une page manquante, un
debordement. Ce qui ne bloque plus est ce que seul un auditeur voit : un
packet non assigne, un second relecteur absent, un recu manquant sur un objet
inchange.

Le garde-fou est explicite et il compte : un bloqueur ne peut pas etre
reclasse en dette de gouvernance sans motif enregistre, et aucun defaut
demontre ne peut y tomber. `PRODUCT_DEFECT_RECLASSED_AS_DEBT` est bloquante.

Metriques bloquantes : `PRODUCT_BLOCKING_OPEN`,
`PRODUCT_DEFECT_RECLASSED_AS_DEBT`, `UNCLASSIFIED_BLOCKER`, `UNKNOWN`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import ROOT  # noqa: E402

JSON_TARGET = ROOT / "audit/RELEASE_PUBLICATION_POLICY.json"
MD_TARGET = ROOT / "audit/RELEASE_PUBLICATION_POLICY.md"
GENERATED_BY = "scripts/build_release_publication_policy.py"

LEDGER = ROOT / "audit/1SPE_RELEASE_BLOCKER_LEDGER.json"

RELEASE_OWNER = "abenrhouma"
MODE = "RELEASE_OWNER_FAST_TRACK"

#: Ce qui atteint le lecteur. Reste bloquant, sans exception.
PRODUCT_BLOCKING_KINDS = (
    "erreur mathematique demontree",
    "reponse ou corrige faux",
    "incoherence enonce / corrige",
    "erreur ou omission de programme officiel",
    "formule corrompue",
    "code imprime non executable",
    "contenu obligatoire reellement absent",
    "bareme incoherent ou somme de points incorrecte",
    "question hors perimetre",
    "TeX invalide visible",
    "PDF non compilable",
    "page manquante",
    "reference croisee cassee",
    "numerotation erronee",
    "probleme de police ou de glyphe",
    "debordement hors zone imprimable",
    "TrimBox / BleedBox reellement nuisible",
    "echec reel de manifeste ou de reproductibilite",
    "P0 ou P1 produit non resolu",
    "test bloquant rouge",
)

#: Ce que seul un auditeur voit. Ne bloque plus a soi seul.
GOVERNANCE_DEBT_KINDS = (
    "packet PENDING_UNASSIGNED",
    "absence d'un second relecteur",
    "absence de recu pour un objet inchange",
    "SCIENCE_HUMAINE_REQUISE sans defaut precis identifie",
    "MANUAL_REVIEW purement declaratif",
    "recommandation externe non encore convertie",
    "absence d'un verdict individuel par allocation de bareme",
    "dette P2 ou P3 exclusivement administrative",
    "absence d'une seconde identite humaine",
    "relecture d'un digest inchange",
    "commentaire de provenance n'affectant pas le produit",
)

#: Le classement de chaque bloqueur suivi, avec son motif. Un bloqueur absent
#: de cette table est `UNCLASSIFIED_BLOCKER`, et c'est bloquant : on ne laisse
#: pas un bloqueur sans famille.
CLASSIFICATION: dict[str, dict[str, str]] = {
    "CHAPTER_OPENER_ORPHAN_PAGE": {
        "family": "PRODUCT_BLOCKING",
        "why": "une ouverture qui deborde se voit sur la page imprimee",
    },
    "UNINTENTIONAL_BLANK_PAGE": {
        "family": "PRODUCT_BLOCKING",
        "why": "une page blanche sans raison se voit sur la page imprimee",
    },
    "CHAPTER_OPENING_FALSE_FOLIO": {
        "family": "PRODUCT_BLOCKING",
        "why": "un sommaire qui annonce la mauvaise page egare le lecteur",
    },
    "BAREME_CONTRADICTS_ITS_SUBJECT": {
        "family": "PRODUCT_BLOCKING",
        "why": "un bareme qui contredit son sujet fausse la notation",
    },
    "TEACHER_MISSING_REQUIRED_CONTENT": {
        "family": "PRODUCT_BLOCKING",
        "why": "un contenu professeur exige et absent manque au lecteur",
    },
    "BAREME_EXPECTED_TEX_BOUNDARY_LOSS": {
        "family": "PRODUCT_BLOCKING",
        "why": "une formule coupee en deux ne se compose pas",
    },
    "BAREME_QUESTION_SCOPE_COLLAPSE": {
        "family": "PRODUCT_BLOCKING",
        "why": "un attendu servi a la mauvaise question fausse la notation",
    },
    "REFERENTIAL_CAPACITY_OMISSION": {
        "family": "PRODUCT_BLOCKING",
        "why": "un attendu officiel non rattache est une omission de programme",
    },
    "UNREQUESTED_CROP_MARKS": {
        "family": "PRODUCT_BLOCKING",
        "why": "un repere technique non demande atteint la page imprimee",
    },
    "RELEASE_TEST_GATE_RED": {
        "family": "PRODUCT_BLOCKING",
        "why": "un test bloquant rouge est un defaut tant qu'il n'est pas explique",
    },
    "ASSESSMENT_BAREME_HUMAN_DECISION": {
        "family": "NON_BLOCKING_GOVERNANCE_DEBT",
        "why": (
            "la repartition manquante est desormais publiee comme bareme "
            "indicatif derive, verifie contre le sujet ; ce qui reste est "
            "l'absence d'un verdict humain par allocation, que le Release "
            "Owner ne rend plus prerequis"
        ),
    },
    "STUDENT_TEACHER_ONLY_LEAK": {
        "family": "PRODUCT_BLOCKING",
        "why": "un corrige qui fuite vers l'edition eleve donne la reponse a l'eleve",
    },
    "MARGIN_COMPOSITOR_RENDERS_NOTHING": {
        "family": "PRODUCT_BLOCKING",
        "why": "une note de marge capturee mais non dessinee manque a la page",
    },
    "LATEX_WARNING_CLASSES_UNCLOSED": {
        "family": "PRODUCT_BLOCKING",
        "why": (
            "une classe d'avertissement inconnue peut cacher un defaut de "
            "composition ; tant qu'elle n'est pas nommee, on ne sait pas"
        ),
    },
    "PRINT_CANDIDATE_RECEIPT_STALE": {
        "family": "PRODUCT_BLOCKING",
        "why": (
            "un recu qui decrit un autre artefact que celui qu'on livre est un "
            "echec de reproductibilite reel"
        ),
    },
    "REFRESH_AUDIT_REPORTS_CORRUPTS_TWO_ARTIFACTS": {
        "family": "PRODUCT_BLOCKING",
        "why": "un producteur qui corrompt un artefact casse la chaine de preuve",
    },
    "D7_BUNDLE_TARGETS_THE_SPECIMEN_NOT_THE_MANUAL": {
        "family": "NON_BLOCKING_GOVERNANCE_DEBT",
        "why": (
            "le faisceau D7 visait la maquette et non le manuel ; la "
            "disposition D7 est desormais rendue par le Release Owner sur des "
            "mesures faites sur les PDF livres eux-memes"
        ),
    },
    "CHAPTER_REVIEW_PACKETS_INCOMPLETE": {
        "family": "NON_BLOCKING_GOVERNANCE_DEBT",
        "why": (
            "l'absence d'un second role exerce est precisement la dette "
            "procedurale que le mode Release Owner cesse de traiter comme un "
            "defaut produit"
        ),
    },
    "ASSESSMENT_BAREME_COMMENTARY_ABSENT": {
        "family": "NON_BLOCKING_GOVERNANCE_DEBT",
        "why": (
            "le bareme commente enrichit le manuel professeur ; son absence "
            "n'introduit aucune erreur et ne prive le lecteur d'aucun contenu "
            "obligatoire"
        ),
    },
}


class PolicyError(RuntimeError):
    """Une preuve manque : la politique ne peut pas etre etablie."""


def ledger() -> dict[str, Any]:
    if not LEDGER.is_file():
        raise PolicyError(f"registre absent : {LEDGER}")
    return json.loads(LEDGER.read_text(encoding="utf-8"))


def build() -> dict[str, Any]:
    payload = ledger()
    open_ids = set(payload["summary"]["OPEN_BLOCKER_IDS"])

    classified: list[dict[str, Any]] = []
    unclassified: list[str] = []
    reclassed_defect: list[dict[str, Any]] = []

    for blocker in payload["blockers"]:
        identifier = blocker["blocker_id"]
        entry = CLASSIFICATION.get(identifier)
        if entry is None:
            unclassified.append(identifier)
            continue
        row = {
            "blocker_id": identifier,
            "family": entry["family"],
            "why": entry["why"],
            "surface": blocker["surface"],
            "meaning": blocker["meaning"],
            "open": identifier in open_ids,
        }
        # Un defaut produit ne peut pas descendre en dette : si un bloqueur
        # classe dette porte une surface d'artefact imprime, c'est une erreur
        # de classement, pas une simplification.
        if (
            entry["family"] == "NON_BLOCKING_GOVERNANCE_DEBT"
            and blocker["surface"] == "1SPE_PRINT_ARTIFACT"
        ):
            reclassed_defect.append(row)
        classified.append(row)

    product_open = [
        row
        for row in classified
        if row["family"] == "PRODUCT_BLOCKING" and row["open"]
    ]
    debt_open = [
        row
        for row in classified
        if row["family"] == "NON_BLOCKING_GOVERNANCE_DEBT" and row["open"]
    ]

    return {
        "artifact_type": "release_publication_policy",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "mode": MODE,
        "release_owner": RELEASE_OWNER,
        "what_this_changes": (
            "Une approbation finale explicite du Release Owner peut suffire a "
            "la publication lorsque tous les controles materiels sont "
            "satisfaits. Les doubles revues de chapitre restent disponibles "
            "comme qualite supplementaire ; elles ne sont plus un prerequis "
            "absolu quand aucun defaut reel n'est identifie."
        ),
        "what_this_does_not_change": (
            "Aucun verdict n'est fabrique pour un role que personne n'a "
            "exerce. Un packet non relu reste PENDING_UNASSIGNED, et le dire "
            "reste exact. Aucun defaut demontre ne devient une dette."
        ),
        "product_blocking_kinds": list(PRODUCT_BLOCKING_KINDS),
        "governance_debt_kinds": list(GOVERNANCE_DEBT_KINDS),
        "a_defect_never_becomes_debt": (
            "Un bloqueur classe dette dont la surface est l'artefact imprime "
            "serait un defaut deguise. Le controle le compte, et il bloque."
        ),
        "blockers": classified,
        "product_blocking_open": product_open,
        "governance_debt_open": debt_open,
        "unclassified": unclassified,
        "summary": {
            "BLOCKERS_TRACKED": len(payload["blockers"]),
            "CLASSIFIED": len(classified),
            "PRODUCT_BLOCKING_OPEN": len(product_open),
            "NON_BLOCKING_GOVERNANCE_DEBT_OPEN": len(debt_open),
            "PRODUCT_DEFECT_RECLASSED_AS_DEBT": len(reclassed_defect),
            "UNCLASSIFIED_BLOCKER": len(unclassified),
            "UNKNOWN": 0,
        },
    }


BLOCKING = (
    "PRODUCT_BLOCKING_OPEN",
    "PRODUCT_DEFECT_RECLASSED_AS_DEBT",
    "UNCLASSIFIED_BLOCKER",
    "UNKNOWN",
)


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Politique de publication — mode `" + payload["mode"] + "`",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"Release Owner : `{payload['release_owner']}`",
        "",
        f"> {payload['what_this_changes']}",
        "",
        f"> {payload['what_this_does_not_change']}",
        "",
        f"> {payload['a_defect_never_becomes_debt']}",
        "",
        "## Métriques",
        "",
        "| Métrique | Valeur |",
        "|---|---:|",
    ]
    for name, value in payload["summary"].items():
        lines.append(f"| `{name}` | {value} |")
    lines += ["", "## Ce qui reste bloquant", ""]
    lines += [f"- {kind}" for kind in payload["product_blocking_kinds"]]
    lines += ["", "## Ce qui ne bloque plus à soi seul", ""]
    lines += [f"- {kind}" for kind in payload["governance_debt_kinds"]]
    lines += [
        "",
        "## Classement des bloqueurs suivis",
        "",
        "| Bloqueur | Famille | Ouvert | Motif |",
        "|---|---|---|---|",
    ]
    for row in payload["blockers"]:
        lines.append(
            f"| `{row['blocker_id']}` | `{row['family']}` | "
            f"{'oui' if row['open'] else 'non'} | {row['why']} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="ne rien ecrire")
    arguments = parser.parse_args(argv)

    try:
        payload = build()
    except PolicyError as error:
        print(f"RELEASE-POLICY-ERROR: {error}", file=sys.stderr)
        return 2

    if not arguments.check:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"ecrit {JSON_TARGET.name} et {MD_TARGET.name}")
    for name, value in payload["summary"].items():
        print(f"{name}={value}")
    return 1 if any(payload["summary"][name] for name in BLOCKING) else 0


if __name__ == "__main__":
    raise SystemExit(main())
