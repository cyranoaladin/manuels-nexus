#!/usr/bin/env python3
"""Valide, ou réfute, chaque identité DÉCLARÉE exacte du corpus.

« Identité déclarée exacte » n'est pas une preuve. Elle dit seulement qu'un
`% META` nomme une capacité, et que ce nom résout exactement dans le contrat
du chapitre. Mille neuf cent cinquante cellules reposent là-dessus, et rien
n'a jamais été recalculé depuis le CORPS des objets qui les créditent.

Ce producteur recalcule. Pour chaque objet créditant une cellule, il construit
un CONDENSÉ SÉMANTIQUE à partir de six composantes lues dans le texte lui-même :

    énoncé          la prose, commentaires retirés, espaces normalisés ;
    nombres         les littéraux numériques, dans l'ordre ;
    formules        les passages en mode mathématique, dans l'ordre ;
    code            les listings et les blocs de vérification ;
    figures         les inclusions graphiques et environnements de figure ;
    sous-questions  l'ordre des `\\item` des énumérations.

Trois verdicts, et trois seulement :

`PROVEN_EXACT_SEMANTIC_IDENTITY`
    la déclaration résout exactement, et rien ne la contredit : aucun autre
    objet du même chapitre ne crédite une capacité DIFFÉRENTE avec un corps
    sémantiquement identique.

`SEMANTIC_DELTA`
    deux objets créditent la même cellule avec des corps qui ne diffèrent que
    par leurs nombres. Ce sont des variantes : chacune garde sa propre revue
    de delta, aucune preuve n'est héritée.

`INVALID_IDENTITY_DECLARATION`
    la machine DÉMONTRE une contradiction : un même corps sémantique crédite
    deux capacités distinctes du même chapitre — la signature du P0 fondateur —
    ou la capacité déclarée est absente du contrat.

CE QUE CE PRODUCTEUR NE FAIT PAS. Il ne certifie pas qu'un corps est
pédagogiquement ADAPTÉ à la capacité qu'il déclare : c'est un jugement humain,
et il reste dû. `PROVEN_EXACT_SEMANTIC_IDENTITY` établit que la DÉCLARATION
est saine, pas que le contenu est bon. Une cellule validée est
`VALIDATED_BY_EVIDENCE` ; elle n'est jamais `approved`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(ROOT / "scripts"))

import yaml  # noqa: E402

import evidence_freshness as freshness  # noqa: E402

COVERAGE = ROOT / "audit/TRUE_PEDAGOGICAL_COVERAGE.json"
OUTPUT_JSON = ROOT / "audit/DECLARED_IDENTITY_VALIDATION.json"
OUTPUT_MD = ROOT / "audit/DECLARED_IDENTITY_VALIDATION.md"

DECLARED_STATE = "DECLARED_EXACT_IDENTITY_NOT_SEMANTICALLY_VALIDATED"

PROVEN = "PROVEN_EXACT_SEMANTIC_IDENTITY"
DELTA = "SEMANTIC_DELTA"
INVALID = "INVALID_IDENTITY_DECLARATION"

MATH = re.compile(
    r"\$\$.*?\$\$|\$[^$]+\$|\\\[.*?\\\]|\\begin\{(?:align|equation|gather)\*?\}"
    r".*?\\end\{(?:align|equation|gather)\*?\}",
    re.S,
)
CODE = re.compile(
    r"\\begin\{(?:python|sql|console|lstlisting)\}.*?\\end\{(?:python|sql|console|lstlisting)\}"
    r"|% BEGIN-VERIFY\n.*?% END-VERIFY",
    re.S,
)
FIGURE = re.compile(
    r"\\includegraphics(?:\[[^\]]*\])?\{[^}]*\}"
    r"|\\begin\{(?:tikzpicture|figure)\}.*?\\end\{(?:tikzpicture|figure)\}",
    re.S,
)
ITEM = re.compile(r"\\item\b")
NUMBER = re.compile(r"-?\d+(?:[.,]\d+)?")
COMMENT = re.compile(r"^%.*$", re.M)
SPACE = re.compile(r"\s+")


def _digest(values: Any) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(values, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def semantic_components(texte: str) -> dict[str, Any]:
    """Les six composantes sémantiques, lues dans le texte lui-même."""
    sans_meta = "\n".join(
        ligne for ligne in texte.splitlines() if not ligne.startswith("% META:")
    )
    code = CODE.findall(sans_meta)
    reste = CODE.sub(" ", sans_meta)
    figures = FIGURE.findall(reste)
    reste = FIGURE.sub(" ", reste)
    formules = MATH.findall(reste)
    prose = MATH.sub(" ", reste)
    prose = COMMENT.sub(" ", prose)
    sous_questions = len(ITEM.findall(sans_meta))
    return {
        "statement": SPACE.sub(" ", prose).strip(),
        "numbers": NUMBER.findall(sans_meta),
        "formulas": [SPACE.sub(" ", f).strip() for f in formules],
        "code": [SPACE.sub(" ", c).strip() for c in code],
        "figures": [SPACE.sub(" ", f).strip() for f in figures],
        "subquestions": sous_questions,
    }


def semantic_digest(texte: str) -> str:
    return _digest(semantic_components(texte))


def numeric_skeleton_digest(texte: str) -> str:
    """Le condensé une fois les nombres abstraits : deux variantes le partagent."""
    composantes = semantic_components(texte)
    composantes["numbers"] = ["#"] * len(composantes["numbers"])
    composantes["statement"] = NUMBER.sub("#", composantes["statement"])
    composantes["formulas"] = [NUMBER.sub("#", f) for f in composantes["formulas"]]
    composantes["code"] = [NUMBER.sub("#", c) for c in composantes["code"]]
    return _digest(composantes)


def build(coverage: dict[str, Any] | None = None) -> dict[str, Any]:
    coverage = coverage or json.loads(COVERAGE.read_text(encoding="utf-8"))
    cellules = [
        ligne for ligne in coverage["rows"] if ligne["state"] == DECLARED_STATE
    ]

    # Condensés calculés une fois par objet : un même corps crédite souvent
    # plusieurs cellules, et le relire à chaque fois ne dirait rien de plus.
    condenses: dict[str, dict[str, str] | None] = {}

    def condense(relatif: str) -> dict[str, str] | None:
        """Le condensé d'un objet, ou d'UNE question de QCM.

        Une cellule QCM est adressée par question : `…-QCM.json#Q3`. Traiter
        cette adresse comme un fichier la déclarerait absente du disque, et
        réfuterait en masse des déclarations parfaitement saines.
        """
        if relatif in condenses:
            return condenses[relatif]
        fichier, _, question = relatif.partition("#")
        chemin = ROOT / fichier
        if not chemin.is_file():
            condenses[relatif] = None
            return None
        if question:
            document = json.loads(chemin.read_text(encoding="utf-8"))
            trouvee = next(
                (q for q in document.get("questions") or []
                 if str(q.get("id")) == question),
                None,
            )
            if trouvee is None:
                condenses[relatif] = None
                return None
            texte = json.dumps(
                {cle: trouvee.get(cle) for cle in ("enonce", "options", "correcte")},
                ensure_ascii=False, sort_keys=True,
            )
        else:
            texte = chemin.read_text(encoding="utf-8", errors="replace")
        condenses[relatif] = {
            "semantic": semantic_digest(texte),
            "skeleton": numeric_skeleton_digest(texte),
        }
        return condenses[relatif]

    # DEUX OBJETS DISTINCTS dont les corps sont sémantiquement identiques mais
    # qui créditent des capacités différentes du même chapitre : c'est la
    # signature du P0 fondateur, et l'une des deux déclarations est fausse.
    #
    # Un même objet qui déclare plusieurs capacités n'est PAS cela : une
    # évaluation qui porte sur trois capacités les sert réellement toutes les
    # trois, et sa déclaration le dit. Indexer par corps sans distinguer les
    # objets réfutait mille cent vingt-neuf cellules parfaitement saines — le
    # détecteur mentait, et le compte le disait.
    def identite(relatif: str) -> str:
        """L'identité de l'objet, lue dans SON `% META`, jamais devinée.

        La couverture publie `valid_object_ids` et `valid_object_paths` triés
        SÉPARÉMENT : les apparier par position croise les identités dès que les
        deux ordres diffèrent, et attribue alors un corps au mauvais objet.
        L'identité se lit donc dans le fichier lui-même.
        """
        fichier, _, question = relatif.partition("#")
        if question:
            return relatif
        chemin = ROOT / fichier
        if not chemin.is_file():
            return relatif
        premiere = chemin.read_text(encoding="utf-8", errors="replace").split("\n", 1)[0]
        if premiere.startswith("% META:"):
            try:
                return str(json.loads(premiere[len("% META:"):]).get("id") or relatif)
            except ValueError:
                return relatif
        return relatif

    capacites_par_corps: dict[tuple[str, str], dict[str, set[str]]] = {}
    for cellule in cellules:
        for relatif in cellule["valid_object_paths"]:
            empreinte = condense(relatif)
            if empreinte is None:
                continue
            seau = capacites_par_corps.setdefault(
                (cellule["chapter"], empreinte["semantic"]), {}
            )
            seau.setdefault(identite(relatif), set()).add(cellule["capacity"])

    # Le contrat de chapitre fait autorité sur les capacités qui existent.
    # Les déduire des lignes de couverture rendrait le contrôle vide : une
    # capacité serait « au contrat » du seul fait d'apparaître dans la ligne
    # qu'on est en train de juger.
    contrats: dict[str, set[str] | None] = {}

    def contrat(chapitre: str) -> set[str] | None:
        if chapitre in contrats:
            return contrats[chapitre]
        trouve: set[str] | None = None
        for racine in (
            ROOT / "Mathematiques/manuel-maths/chapitres",
            ROOT / "NSI/chapitres",
        ):
            chemin = racine / chapitre / "contrat.yaml"
            if chemin.is_file():
                document = yaml.safe_load(chemin.read_text(encoding="utf-8")) or {}
                trouve = {
                    str(entree["code"])
                    for entree in document.get("capacites") or []
                    if entree.get("code")
                }
                break
        contrats[chapitre] = trouve
        return trouve

    lignes: list[dict[str, Any]] = []
    for cellule in cellules:
        chapitre = cellule["chapter"]
        capacite = cellule["capacity"]
        motifs: list[str] = []
        empreintes: list[str] = []
        squelettes: list[str] = []
        absents: list[str] = []

        for relatif in cellule["valid_object_paths"]:
            empreinte = condense(relatif)
            if empreinte is None:
                absents.append(relatif)
                continue
            identifiant = identite(relatif)
            empreintes.append(empreinte["semantic"])
            squelettes.append(empreinte["skeleton"])
            par_objet = capacites_par_corps.get((chapitre, empreinte["semantic"]), {})
            autres = {
                autre: capacites
                for autre, capacites in par_objet.items()
                if autre != identifiant and capacite not in capacites
            }
            if autres:
                motifs.append(
                    "corps sémantique identique à celui de "
                    f"{sorted(autres)}, crédité à d'autres capacités "
                    f"{sorted(set().union(*autres.values()))} du même chapitre"
                )

        codes = contrat(chapitre)
        if codes is not None and capacite not in codes:
            motifs.append("capacité absente du contrat de chapitre")
        if absents:
            motifs.append(f"objet créditant absent du disque : {absents[:2]}")

        if motifs:
            verdict = INVALID
        elif len(empreintes) > 1 and len(set(empreintes)) > 1 and len(
            set(squelettes)
        ) == 1:
            verdict = DELTA
        else:
            verdict = PROVEN

        lignes.append({
            "canonical_capacity_uid": cellule["canonical_capacity_uid"],
            "manual": cellule["manual"],
            "chapter": chapitre,
            "capacity": capacite,
            "role": cellule["role"],
            "crediting_objects": cellule["valid_object_ids"],
            "crediting_paths": cellule["valid_object_paths"],
            "semantic_digests": empreintes,
            "numeric_skeleton_digests": squelettes,
            "VERDICT": verdict,
            "contradictions": sorted(set(motifs)),
        })

    lignes.sort(key=lambda ligne: (ligne["canonical_capacity_uid"], ligne["role"]))
    par_verdict: dict[str, int] = {}
    for ligne in lignes:
        par_verdict[ligne["VERDICT"]] = par_verdict.get(ligne["VERDICT"], 0) + 1

    resume = {
        "DECLARED_IDENTITY_CELLS": len(lignes),
        "PROVEN_EXACT_SEMANTIC_IDENTITIES": par_verdict.get(PROVEN, 0),
        "SEMANTIC_DELTA_VARIANTS": par_verdict.get(DELTA, 0),
        "INVALID_IDENTITY_DECLARATIONS": par_verdict.get(INVALID, 0),
        "DECLARED_IDENTITY_UNVALIDATED": len(lignes) - sum(par_verdict.values()),
        "VERDICTS_SUM_EQUALS_TOTAL": sum(par_verdict.values()) == len(lignes),
        "PEDAGOGICAL_ADEQUACY_STILL_HUMAN": True,
        "APPROVES_NOTHING": True,
    }
    return {
        "artifact_type": "declared_identity_validation",
        "schema_version": 1,
        "generated_by": "scripts/build_declared_identity_validation.py",
        "authority_note": (
            "Établit que la DÉCLARATION est saine, jamais que le contenu est "
            "pédagogiquement adapté : ce jugement reste humain et reste dû. "
            "Une cellule validée est VALIDATED_BY_EVIDENCE, jamais `approved`."
        ),
        "semantic_components": [
            "statement", "numbers", "formulas", "code", "figures", "subquestions",
        ],
        "summary": resume,
        "invalid_declarations": [
            ligne for ligne in lignes if ligne["VERDICT"] == INVALID
        ],
        "cells": lignes,
        "freshness": freshness.stamp(
            ["audit/TRUE_PEDAGOGICAL_COVERAGE.json"], root=ROOT
        ),
    }


def render_md(payload: dict[str, Any]) -> str:
    resume = payload["summary"]
    lignes = [
        "# Validation des identités déclarées",
        "",
        "« Identité déclarée exacte » n'est pas une preuve : un `% META` qui",
        "résout exactement dit seulement qu'un nom est bien formé. Le condensé",
        "sémantique est ici recalculé depuis le corps des objets.",
        "",
        f"- Cellules examinées : `{resume['DECLARED_IDENTITY_CELLS']}`",
        f"- `PROVEN_EXACT_SEMANTIC_IDENTITY` : "
        f"`{resume['PROVEN_EXACT_SEMANTIC_IDENTITIES']}`",
        f"- `SEMANTIC_DELTA` : `{resume['SEMANTIC_DELTA_VARIANTS']}`",
        f"- `INVALID_IDENTITY_DECLARATION` : "
        f"`{resume['INVALID_IDENTITY_DECLARATIONS']}`",
        f"- `DECLARED_IDENTITY_UNVALIDATED` : "
        f"`{resume['DECLARED_IDENTITY_UNVALIDATED']}`",
        "",
        "L'adéquation pédagogique du corps à la capacité reste un jugement",
        "humain, et reste due.",
        "",
    ]
    if payload["invalid_declarations"]:
        lignes += ["## Déclarations réfutées", ""]
        for ligne in payload["invalid_declarations"]:
            lignes.append(
                f"- `{ligne['canonical_capacity_uid']}::{ligne['role']}` — "
                f"{'; '.join(ligne['contradictions'])}"
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
            print("DECLARED_IDENTITY_VALIDATION check: OK")
            return 0
        print("DECLARED_IDENTITY_VALIDATION check: STALE")
        return 1
    OUTPUT_JSON.write_text(rendu, encoding="utf-8")
    OUTPUT_MD.write_text(render_md(payload), encoding="utf-8")
    print(json.dumps(payload["summary"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
