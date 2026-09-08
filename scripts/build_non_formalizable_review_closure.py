#!/usr/bin/env python3
"""Current scientific review of mathematical objects without a formal oracle.

The current review index owns the population and source-bound evidence. Legacy
path-only declarations, QCM status copies and formula-containment classifications
are retained at the takeover snapshot but cannot certify current content. The
legacy inspection helpers below remain available for forensic comparison only.
A closed scientific review is VALIDATED_BY_EVIDENCE, never human approval.
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


def build(root: Path = ROOT, *, inventory=None) -> dict[str, Any]:
    """The current index is authoritative; old heuristics remain historical."""
    import build_current_review_index as current_review
    index = current_review.build_fresh(root, inventory)
    historical = current_review.historical_payload(root, "audit/NON_FORMALIZABLE_REVIEW_CLOSURE.json")
    legacy = {row["path"]: row for row in json.loads(historical or b'{"objects":[]}')["objects"]}
    lignes = []
    for row in index["objects"]:
        if row["mathematics_classification"] != "MATHEMATICAL_NON_FORMALIZABLE":
            continue
        science = row["reviews"]["SCIENTIFIC_REVIEW"]
        validated = science["state"] == "VALIDATED_BY_EVIDENCE"
        old = legacy.get(row["path"], {})
        ligne = {
            "manual": row["manual"], "chapter": row["chapter"],
            "object_id": row["object_id"], "type_objet": row["object_type"],
            "path": row["path"], "source_sha256": row["source_sha256"],
            "semantic_digest": row["semantic_digest"], "dependency_digest": row["dependency_digest"],
            "state": "SEMANTICALLY_REVIEWED" if validated else "PENDING",
            "evidence": (current_review.REVIEW_LEDGER + "#" + science["review_id"]) if validated else None,
            "detail": science.get("rationale") if validated else "sans preuve scientifique liée au contenu et aux dépendances courants",
            "legacy_classification": {
                "state": old.get("state", "NOT_IN_HISTORICAL_POPULATION"),
                "evidence": old.get("evidence"),
                "historical_commit": current_review.TAKEOVER_HEAD,
                "current_credit": False,
                "reason": "No source/dependency-bound independent review; substring containment is not a proof of reasoning.",
            },
        }
        if validated:
            ligne["review"] = science
        lignes.append(ligne)
    par_etat: dict[str, int] = {}
    par_type: dict[str, dict[str, int]] = {}
    for ligne in lignes:
        etat = ligne["state"]
        par_etat[etat] = par_etat.get(etat, 0) + 1
        seau = par_type.setdefault(str(ligne["type_objet"]), {})
        seau[etat] = seau.get(etat, 0) + 1
    resume = {
        "MATHEMATICAL_NON_FORMALIZABLE_TOTAL": len(lignes),
        "MATHEMATICAL_NON_FORMALIZABLE_REVIEW_PENDING": par_etat.get("PENDING", 0),
        "COVERED_BY_QCM_PROOF_CHAIN": 0, "COVERED_BY_QCM_EVIDENCE": 0,
        "SEMANTICALLY_REVIEWED": par_etat.get("SEMANTICALLY_REVIEWED", 0),
        "REVIEW_INHERITED_BY_IDENTICAL_CONTENT": 0,
        "TRULY_NOT_REQUIRING_MATHEMATICAL_REVIEW": 0,
        "OTHER": 0, "NON_FORMALIZABLE_POPULATION_UNRECONCILED": len(lignes) - sum(par_etat.values()),
        "REVIEWED": par_etat.get("SEMANTICALLY_REVIEWED", 0),
        "DEFECTS_FOUND": None, "FINDING_ASSESSMENT": "NOT_COMPUTED_BY_THIS_PRODUCER",
        "STATES_SUM_EQUALS_TOTAL": sum(par_etat.values()) == len(lignes),
        "APPROVES_NOTHING": True,
    }
    current_review.assert_current(root, index)
    return {
        "artifact_type": "non_formalizable_review_closure", "schema_version": 2,
        "generated_by": "scripts/build_non_formalizable_review_closure.py",
        "authority_note": "Une unité fermée est VALIDATED_BY_EVIDENCE. Aucune approbation humaine n'est produite.",
        "current_review_index": current_review.binding(index),
        "historical_classification_source": {
            "path": "audit/NON_FORMALIZABLE_REVIEW_CLOSURE.json",
            "historical_commit": current_review.TAKEOVER_HEAD,
            "sha256": current_review.sha256(historical) if historical else None,
        },
        "summary": resume, "by_type": {cle: par_type[cle] for cle in sorted(par_type)},
        "defects": None, "objects": lignes,
        "freshness": freshness.stamp(index["input_digests"], root=root),
    }


def render_md(payload: dict[str, Any]) -> str:
    resume = payload["summary"]
    lignes = [
        "# Revue mathématique des objets non formalisables",
        "",
        "Ces objets ne portent pas d'oracle formel. Ce registre suit leur",
        "revue scientifique ; il ne décide pas si un oracle peut être ajouté.",
        "",
        f"- Population : `{resume['MATHEMATICAL_NON_FORMALIZABLE_TOTAL']}`",
        f"- `MATHEMATICAL_NON_FORMALIZABLE_REVIEW_PENDING` : "
        f"`{resume['MATHEMATICAL_NON_FORMALIZABLE_REVIEW_PENDING']}`",
        f"- Couverts par la chaîne QCM : `{resume['COVERED_BY_QCM_PROOF_CHAIN']}`",
        f"- Revus : `{resume['REVIEWED']}`",
        "- Défauts trouvés en revue : Non évalué par ce registre.",
        "",
        "| Type | Revus | Chaîne QCM | En attente |",
        "|---|---|---|---|",
    ]
    for type_objet, etats in payload["by_type"].items():
        lignes.append(
            f"| {type_objet} | {etats.get('SEMANTICALLY_REVIEWED', 0)} | "
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
