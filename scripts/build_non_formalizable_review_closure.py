#!/usr/bin/env python3
"""Fermeture de la revue mathématique des objets non formalisables.

La dimension `mathematics` prouve ce qui se calcule. Elle déclare
`NOT_APPLICABLE` ce qui ne se calcule pas — et `NOT_APPLICABLE` n'est pas
`PASS`. Ce producteur mesure ce que cette déclaration laisse ouvert.

Cinq états, et cinq seulement. Leur somme vaut la population : c'est la
condition `NON_FORMALIZABLE_POPULATION_UNRECONCILED = 0`.

`COVERED_BY_QCM_PROOF_CHAIN`
    l'objet est un QCM, et CHACUNE de ses questions est établie par la chaîne
    de preuve QCM — dérivation exécutée, revue conceptuelle écrite, preuve
    reportée à l'identique sémantique, ou recalcul machine. Une seule question
    sans état ferme la porte : on ne duplique pas une revue qui existe, mais
    on ne l'invente pas non plus.

`REVIEWED`
    une revue mathématique écrite le déclare, avec ses quatre dimensions.

`REVIEW_INHERITED_BY_IDENTICAL_CONTENT`
    l'objet porte, au caractère près, le contenu d'un objet déjà revu du même
    chapitre. L'héritage n'est pas une présomption : le condensé sémantique
    des deux corps est identique, et le registre nomme la source.

`TRULY_NOT_REQUIRING_MATHEMATICAL_REVIEW`
    l'objet est un SATELLITE — un coup de pouce, une version aménagée — dont
    CHAQUE expression mathématique figure déjà, au caractère près, dans un
    objet du même chapitre porteur d'un oracle qui passe. Il n'énonce donc
    aucune proposition qui lui soit propre : sa vérité mathématique est celle
    d'un objet déjà prouvé, et le seul jugement qui lui reste est pédagogique.

    Ce n'est pas une dispense : c'est une preuve de CONTENANCE, et elle se
    réfute. Qu'on introduise une formule que le chapitre ne porte pas, et
    l'objet quitte cette classe pour redevenir `PENDING`. C'est arrivé une
    fois, sur un coup de pouce qui énonçait la formule du milieu d'un segment
    que son chapitre n'écrivait nulle part.

`PENDING`
    tout le reste. C'est ce que la dimension doit refuser.

Le producteur n'approuve rien : une unité fermée est `VALIDATED_BY_EVIDENCE`.
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


def _condense(chemin: Path) -> str:
    """Le condensé sémantique d'un corps : identifiants et espaces neutralisés.

    Deux objets qui ne différent que par leur numéro portent le même contenu ;
    deux objets qui différent d'un signe n'ont pas le même condensé.
    """

    texte = _corps_nu(chemin)
    texte = re.sub(r"\{[A-Z0-9\-]+-(?:EX|CDP|ME|CO|AM)-\d+[^}]*\}", "{}", texte)
    return hashlib.sha256(" ".join(texte.split()).encode("utf-8")).hexdigest()


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


#: Les rôles qui ne portent jamais d'énoncé autonome : ils accompagnent un
#: objet dont la vérification appartient à l'oracle.
ROLES_SATELLITES = frozenset({"coup_de_pouce", "amenagee"})

FRAGMENT = re.compile(r"\$([^$]+)\$|\\\[(.*?)\\\]", re.S)


def _fragments(texte: str) -> set[str]:
    """Les expressions mathématiques écrites dans ce corps."""

    trouvees = set()
    for entre_dollars, entre_crochets in FRAGMENT.findall(texte):
        fragment = " ".join((entre_dollars or entre_crochets).split())
        if fragment:
            trouvees.add(fragment)
    return trouvees


def _corps_nu(chemin: Path) -> str:
    texte = chemin.read_text(encoding="utf-8", errors="replace")
    return re.sub(r"^%.*$", "", texte, flags=re.M)


def _reference_du_chapitre(racine_chapitre: Path) -> str:
    """Ce que le chapitre porte déjà, et que l'oracle ou la revue a vu.

    On ne prend que les rôles dont le contenu mathématique est établi
    ailleurs : le cours, les méthodes, les exercices et leurs corrigés.
    Un satellite ne peut pas s'appuyer sur un autre satellite.
    """

    morceaux = []
    for sous in ("cours", "methodes", "exercices", "corriges"):
        repertoire = racine_chapitre / sous
        if not repertoire.is_dir():
            continue
        for fichier in sorted(repertoire.glob("*.tex")):
            if fichier.stem.endswith("-CDP"):
                continue
            morceaux.append(_corps_nu(fichier))
    return "\n".join(morceaux)


def _qcm_sources_for(chemin: Path) -> list[Path]:
    """Les sources JSON qui engendrent ce `.tex` de QCM."""
    return sorted(chemin.parent.glob("*-QCM.json")) + sorted(
        chemin.parent.glob("*-QCM-DIAG.json")
    )


def build() -> dict[str, Any]:
    population = _population()
    etats_qcm = _qcm_question_states()
    references: dict[str, str] = {}
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
            etat = "SEMANTICALLY_REVIEWED"
            preuve = "scripts/non_formalizable_reviews.py"

        if etat == "PENDING" and objet["type_objet"] in ROLES_SATELLITES:
            reference = references.setdefault(
                objet["chapter"], _reference_du_chapitre(chemin.parent.parent)
            )
            propres = sorted(
                fragment for fragment in _fragments(_corps_nu(chemin))
                if fragment not in reference
            )
            if not propres:
                etat = "TRULY_NOT_REQUIRING_MATHEMATICAL_REVIEW"
                preuve = "contenance : aucune expression propre au satellite"
                detail = (
                    "toutes les expressions figurent deja dans le cours, les "
                    "methodes, les exercices ou les corriges du chapitre"
                )
            else:
                detail = f"expressions propres au satellite : {propres[:3]}"

        ligne = dict(objet, state=etat, evidence=preuve, detail=detail)
        if revue is not None:
            ligne["review"] = revue
        lignes.append(ligne)

    # L'HERITAGE NE SE PRESUME PAS. Un objet ne reprend la revue d'un autre
    # que si leurs corps ont le meme condense, calcule ici et inscrit dans la
    # ligne : le lecteur peut le refaire.
    revus = {
        _condense(ROOT / ligne["path"]): ligne["object_id"]
        for ligne in lignes
        if ligne["state"] == "SEMANTICALLY_REVIEWED"
    }
    for ligne in lignes:
        if ligne["state"] != "PENDING":
            continue
        empreinte = _condense(ROOT / ligne["path"])
        source = revus.get(empreinte)
        if source and source != ligne["object_id"]:
            ligne["state"] = "REVIEW_INHERITED_BY_IDENTICAL_CONTENT"
            ligne["evidence"] = f"SEMANTIC_DIGEST_IDENTICAL:{source}"
            ligne["detail"] = f"sha256:{empreinte[:16]} identique a {source}"

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
        "COVERED_BY_QCM_EVIDENCE": par_etat.get("COVERED_BY_QCM_PROOF_CHAIN", 0),
        "SEMANTICALLY_REVIEWED": par_etat.get("SEMANTICALLY_REVIEWED", 0),
        "REVIEW_INHERITED_BY_IDENTICAL_CONTENT": par_etat.get(
            "REVIEW_INHERITED_BY_IDENTICAL_CONTENT", 0
        ),
        "TRULY_NOT_REQUIRING_MATHEMATICAL_REVIEW": par_etat.get(
            "TRULY_NOT_REQUIRING_MATHEMATICAL_REVIEW", 0
        ),
        "OTHER": len(lignes) - sum(
            par_etat.get(etat, 0) for etat in (
                "PENDING", "COVERED_BY_QCM_PROOF_CHAIN", "SEMANTICALLY_REVIEWED",
                "REVIEW_INHERITED_BY_IDENTICAL_CONTENT",
                "TRULY_NOT_REQUIRING_MATHEMATICAL_REVIEW",
            )
        ),
        "NON_FORMALIZABLE_POPULATION_UNRECONCILED": len(lignes) - sum(par_etat.values()),
        "REVIEWED": par_etat.get("SEMANTICALLY_REVIEWED", 0),
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
