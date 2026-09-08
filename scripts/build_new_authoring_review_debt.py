#!/usr/bin/env python3
"""Le contenu ecrit pendant la reconstruction est du contenu A RISQUE.

La population est derivee du corpus courant et de son historique de retrait.
Les nouveaux objets restent en attente jusqu'a une revue liee a leurs sources. Les blocs
VERIFY qu'ils portent prouvent une exactitude CALCULABLE ; ils ne prouvent ni
l'adequation au programme, ni la qualite de l'enonce, ni la justesse du niveau,
ni le style. Compter un oracle vert comme une revue editoriale reviendrait a
refaire, en plus petit, l'erreur qui a produit le remplissage.

Ce registre etablit ce qui EST prouve, nomme ce qui ne l'est pas, et verifie
que le contenu neuf n'a pas recree ce qu'on venait de retirer :

`ORACLE_VERIFIED`             le bloc VERIFY passe le gate SymPy ;
`CAPACITY_SEMANTICALLY_PROVEN` la capacite declaree est attestee par une revue actuelle ;
`ANSWER_COVERAGE_ESTABLISHED`  le corrige repond a chaque question ;
`EDITORIAL_REVIEW_PENDING`     personne n'a relu l'enonce, le niveau, le style.

ET LES CONTROLES D'ORIGINALITE. Un exercice neuf identique a un autre, ou a un
objet d'un autre chapitre, serait le defaut d'origine reintroduit par la main
qui le reparait.
"""

from __future__ import annotations

import argparse
import collections
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
JSON_TARGET = ROOT / "audit/NEW_AUTHORING_REVIEW_DEBT.json"
MD_TARGET = ROOT / "audit/NEW_AUTHORING_REVIEW_DEBT.md"
GENERATED_BY = "scripts/build_new_authoring_review_debt.py"

#: Le commit qui a retire les objets contamines. Tout objet pedagogique
#: apparu depuis, et toujours present, est du contenu de reconstruction.
DECONTAMINATION_COMMIT = "30c029dd"

CORPORA = ("Mathematiques/manuel-maths/chapitres", "NSI/chapitres")
VERIFY = re.compile(r"% BEGIN-VERIFY\n(.*?)% END-VERIFY", re.S)

_LEDGER = None


def _clone_rule():
    global _LEDGER
    if _LEDGER is None:
        spec = importlib.util.spec_from_file_location(
            "nard_clone", ROOT / "scripts/build_p0_content_clone_ledger.py"
        )
        module = importlib.util.module_from_spec(spec)
        sys.modules["nard_clone"] = module
        spec.loader.exec_module(module)
        _LEDGER = module
    return _LEDGER


def _git(args: list[str]) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=False
    ).stdout


def new_objects(root: Path = ROOT) -> list[str]:
    from build_current_review_index import _new_paths
    return sorted(_new_paths(root))


def _oracle_verdict(chapter: str, stem: str, root: Path = ROOT) -> str | None:
    from scientific_receipt_binding import bind, usable
    directory = root / _chapter_dir(chapter, root)
    for suffixe in (".sympy.json", ".execution.json"):
        recu = directory / "validations" / (stem + suffixe)
        if recu.is_file():
            record = json.loads(recu.read_text(encoding="utf-8"))
            binding = bind(record, directory, root)
            if binding["state"] != "CURRENT_BOUND":
                return "stale"
            if not usable(binding):
                return "untrusted_method"
            return record.get("verdict")
    return None


def _chapter_dir(chapter: str, root: Path = ROOT) -> str:
    for corpus in CORPORA:
        if (root / corpus / chapter).is_dir():
            return f"{corpus}/{chapter}"
    return ""


def _capacity_proof(role, identifiant, codes, meta, prouvees, non_verifiees):
    """La capacite de cet objet est-elle attestee ?

    Un exercice porte sa propre preuve. Un corrige herite de celle de son
    exercice, nomme par `exercice_ref`. Une fiche de remediation ne declare
    pas une capacite servie mais une difficulte traitee : elle n'entre pas
    dans ce compte, et le dire vaut mieux que de la compter fausse.
    """

    if not codes:
        return None
    cible = identifiant if role == "exercices" else meta.get("exercice_ref")
    if not cible:
        return None
    if any((cible, code) in non_verifiees for code in codes):
        return None
    return all((cible, code) in prouvees for code in codes)


def build(root: Path = ROOT, *, inventory=None) -> dict[str, Any]:
    import build_current_review_index as current_review
    index = current_review.build_fresh(root, inventory)
    current_by_path = {row["path"]: row for row in index["objects"]}
    clone = _clone_rule()
    # Old aggregate signatures and question counts do not certify current
    # semantics. Programme and correction reviews bind the actual sources
    # and dependencies through the single current index.

    # Corps normalises de TOUT le corpus, pour le controle d'originalite.
    corpus_bodies: dict[str, list[str]] = collections.defaultdict(list)
    for corpus in CORPORA:
        racine = root / corpus
        if not racine.is_dir():
            continue
        for chemin in sorted(racine.rglob("*.tex")):
            texte = chemin.read_text(encoding="utf-8", errors="replace")
            corps = clone.pedagogical_body(texte)
            if clone.payload_only(corps):
                corpus_bodies[clone.digest(corps)].append(
                    str(chemin.relative_to(root))
                )

    nouveaux = sorted(row["path"] for row in index["objects"] if row["new_authoring"])
    enregistrements: list[dict[str, Any]] = []
    for chemin in nouveaux:
        texte = (root / chemin).read_text(encoding="utf-8", errors="replace")
        meta = clone.read_meta(texte)
        parts = Path(chemin).parts
        chapter_index = parts.index("chapitres") + 1
        chapitre, role = parts[chapter_index], parts[chapter_index + 1]
        codes = meta.get("capacites_codes") or []
        identifiant = meta.get("id") or Path(chemin).stem
        empreinte = clone.digest(clone.pedagogical_body(texte))
        reviews = current_by_path[chemin]["reviews"]
        jumeaux = [p for p in corpus_bodies.get(empreinte, []) if p != chemin]
        enregistrements.append({
            "object_id": identifiant,
            "path": chemin,
            "chapter": chapitre,
            "role": role,
            "declared_capacities": codes,
            "declared_status": meta.get("status"),
            "carries_oracle": bool(VERIFY.search(texte)),
            "oracle_verdict": _oracle_verdict(chapitre, Path(chemin).stem, root),
            "capacity_semantically_proven": (
                reviews["PROGRAMME_REVIEW"]["state"] == "VALIDATED_BY_EVIDENCE"
                if codes else None
            ),
            "answer_coverage_established": (
                reviews.get("CORRECTION_ALIGNMENT_REVIEW", {}).get("state") == "VALIDATED_BY_EVIDENCE"
                if "CORRECTION_ALIGNMENT_REVIEW" in current_by_path[chemin]["required_review_dimensions"] else None
            ),
            "body_digest": empreinte,
            "exact_twins": sorted(jumeaux),
            "source_sha256": current_by_path[chemin]["source_sha256"],
            "semantic_digest": current_by_path[chemin]["semantic_digest"],
            "dependency_digest": current_by_path[chemin]["dependency_digest"],
            "review_state": current_by_path[chemin]["review_state"],
            "required_review_dimensions": current_by_path[chemin]["required_review_dimensions"],
            "reviews": current_by_path[chemin]["reviews"],
            "editorial_review": (
                "VALIDATED_BY_EVIDENCE" if current_by_path[chemin]["reviews"]["EDITORIAL_REVIEW"]["state"]
                == "VALIDATED_BY_EVIDENCE" else "EDITORIAL_REVIEW_PENDING"
            ),
        })

    exacts = [r for r in enregistrements if r["exact_twins"]]
    sans_oracle = [
        r for r in enregistrements
        if not r["carries_oracle"] and r["role"] in {"exercices", "corriges"}
    ]
    oracle_rouge = [
        r for r in enregistrements
        if r["oracle_verdict"] == "fail"
    ]
    capacite_non_prouvee = [
        r for r in enregistrements if r["capacity_semantically_proven"] is False
    ]
    sans_couverture = [
        r for r in enregistrements if r["answer_coverage_established"] is False
    ]

    summary = {
        "NEW_AUTHORING_OBJECTS": len(enregistrements),
        "NEW_AUTHORING_BY_ROLE": dict(sorted(
            collections.Counter(r["role"] for r in enregistrements).items()
        )),
        "NEW_AUTHORING_BY_CHAPTER": dict(sorted(
            collections.Counter(r["chapter"] for r in enregistrements).items()
        )),
        "NEW_AUTHORING_REVIEW_PENDING": sum(row["review_state"] == "PENDING" for row in enregistrements),
        "NEW_AUTHORING_EXACT_CLONES": len(exacts),
        "NEW_AUTHORING_NEAR_CLONES": None,
        "NEAR_CLONE_REVIEW_STATUS": "NOT_COMPUTED_BY_THIS_PRODUCER",
        "ORACLE_VERIFIED": sum(
            1 for r in enregistrements if r["oracle_verdict"] == "pass"
        ),
        "OBJECTS_WITHOUT_ORACLE": len(sans_oracle),
        "ORACLE_FAILURES": len(oracle_rouge),
        "STALE_OR_UNTRUSTED_ORACLE_EVIDENCE": sum(
            r["oracle_verdict"] in {"stale", "untrusted_method"} for r in enregistrements
        ),
        "MISSING_ORACLE_RECEIPTS": sum(r["carries_oracle"] and r["oracle_verdict"] is None for r in enregistrements),
        "CAPACITY_SEMANTICALLY_PROVEN": sum(
            1 for r in enregistrements if r["capacity_semantically_proven"]
        ),
        "CAPACITY_NOT_PROVEN": len(capacite_non_prouvee),
        "CAPACITY_REVIEW_PENDING": len(capacite_non_prouvee),
        "ANSWER_COVERAGE_ESTABLISHED": sum(
            1 for r in enregistrements if r["answer_coverage_established"]
        ),
        "ANSWER_COVERAGE_MISSING": None,
        "ANSWER_COVERAGE_REVIEW_PENDING": len(sans_couverture),
        "FINDING_ASSESSMENT": "NOT_COMPUTED_BY_THIS_PRODUCER",
        "APPROVES_NOTHING": True,
    }
    current_review.assert_current(root, index)
    return {
        "artifact_type": "new_authoring_review_debt",
        "current_review_index": current_review.binding(index),
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "decontamination_commit": DECONTAMINATION_COMMIT,
        "rule": (
            "un bloc VERIFY prouve une exactitude calculable ; il ne prouve ni "
            "l'adequation au programme, ni la qualite de l'enonce, ni le "
            "niveau, ni le style. Seules les revues independantes liees aux "
            "sources et dependances courantes ferment la dette determinable ; "
            "l'approbation humaine reste distincte."
        ),
        "human_review_required": True,
        "release_blocking": True,
        "approves_nothing": True,
        "summary": summary,
        "exact_clones": exacts,
        "objects_without_oracle": [r["path"] for r in sans_oracle],
        "oracle_failures": [r["path"] for r in oracle_rouge],
        "capacity_not_proven": [r["path"] for r in capacite_non_prouvee],
        "answer_coverage_review_pending": [r["path"] for r in sans_couverture],
        "entries": enregistrements,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    s = payload["summary"]
    lignes = [
        "# Dette de revue du contenu neuf",
        "",
        payload["rule"].capitalize() + ".",
        "",
    ]
    for cle in (
        "NEW_AUTHORING_OBJECTS", "NEW_AUTHORING_REVIEW_PENDING",
        "NEW_AUTHORING_EXACT_CLONES", "NEW_AUTHORING_NEAR_CLONES",
        "ORACLE_VERIFIED", "OBJECTS_WITHOUT_ORACLE", "ORACLE_FAILURES",
        "STALE_OR_UNTRUSTED_ORACLE_EVIDENCE", "MISSING_ORACLE_RECEIPTS",
        "CAPACITY_SEMANTICALLY_PROVEN", "CAPACITY_NOT_PROVEN",
        "ANSWER_COVERAGE_ESTABLISHED", "ANSWER_COVERAGE_REVIEW_PENDING",
    ):
        value = s[cle] if s[cle] is not None else "NON_EVALUE_PAR_CE_REGISTRE"
        lignes.append(f"- `{cle}` : `{value}`")
    lignes += ["", "## Par chapitre", ""]
    for chapitre, nombre in payload["summary"]["NEW_AUTHORING_BY_CHAPTER"].items():
        lignes.append(f"- {chapitre} : {nombre}")
    lignes.append("")
    return "\n".join(lignes)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    payload = build(ROOT)
    rendus = {
        JSON_TARGET: json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        MD_TARGET: render_markdown(payload),
    }
    if args.check:
        ecarts = [
            str(p.relative_to(ROOT))
            for p, c in rendus.items()
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
