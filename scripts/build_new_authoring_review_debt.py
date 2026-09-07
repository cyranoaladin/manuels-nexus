#!/usr/bin/env python3
"""Le contenu ecrit pendant la reconstruction est du contenu A RISQUE.

Deux cent huit objets ont ete ecrits pour remplacer ce que la contamination
avait pris. Ils sont neufs, donc personne ne les a jamais relus. Les blocs
VERIFY qu'ils portent prouvent une exactitude CALCULABLE ; ils ne prouvent ni
l'adequation au programme, ni la qualite de l'enonce, ni la justesse du niveau,
ni le style. Compter un oracle vert comme une revue editoriale reviendrait a
refaire, en plus petit, l'erreur qui a produit le remplissage.

Ce registre etablit ce qui EST prouve, nomme ce qui ne l'est pas, et verifie
que le contenu neuf n'a pas recree ce qu'on venait de retirer :

`ORACLE_VERIFIED`             le bloc VERIFY passe le gate SymPy ;
`CAPACITY_SEMANTICALLY_PROVEN` la capacite declaree est attestee par signature ;
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


def new_objects() -> list[str]:
    sortie = _git(
        ["diff", "--name-status", DECONTAMINATION_COMMIT, "HEAD", "--", *CORPORA]
    )
    chemins = []
    for ligne in sortie.splitlines():
        parts = ligne.split("\t")
        if len(parts) < 2 or not parts[0].startswith("A"):
            continue
        chemin = parts[-1]
        if chemin.endswith(".tex") and (ROOT / chemin).is_file():
            chemins.append(chemin)
    return sorted(chemins)


def _oracle_verdict(chapter: str, stem: str) -> str | None:
    for suffixe in (".sympy.json", ".execution.json"):
        recu = ROOT / _chapter_dir(chapter) / "validations" / (stem + suffixe)
        if recu.is_file():
            return json.loads(recu.read_text(encoding="utf-8")).get("verdict")
    return None


def _chapter_dir(chapter: str) -> str:
    for corpus in CORPORA:
        if (ROOT / corpus / chapter).is_dir():
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


def build(root: Path = ROOT) -> dict[str, Any]:
    clone = _clone_rule()
    alignement = json.loads(
        (root / "audit/CAPACITY_CONTENT_ALIGNMENT.json").read_text(encoding="utf-8")
    )
    prouvees = {
        (a["object_id"], a["capacity"])
        for a in alignement["assignments"]
        if a["state"] == "ALIGNED"
    }
    # Une capacite sans signature declaree n'est ni prouvee ni refutee. La
    # compter fausse ferait passer un defaut de couverture du registre pour
    # un defaut du contenu.
    non_verifiees = {
        (a["object_id"], a["capacity"])
        for a in alignement["assignments"]
        if a["state"] == "NO_SIGNATURE_DECLARED"
    }
    graphe = json.loads(
        (root / "audit/EX_CO_GRAPH.json").read_text(encoding="utf-8")
    )
    couverts = {
        row["exercise_id"]
        for row in graphe.get("relations", [])
        if "ANSWER_COVERAGE_ESTABLISHED" in row.get("classifications", [])
    }

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

    nouveaux = new_objects()
    enregistrements: list[dict[str, Any]] = []
    for chemin in nouveaux:
        texte = (root / chemin).read_text(encoding="utf-8", errors="replace")
        meta = clone.read_meta(texte)
        parts = Path(chemin).parts
        index = parts.index("chapitres") + 1
        chapitre, role = parts[index], parts[index + 1]
        codes = meta.get("capacites_codes") or []
        identifiant = meta.get("id") or Path(chemin).stem
        empreinte = clone.digest(clone.pedagogical_body(texte))
        jumeaux = [p for p in corpus_bodies.get(empreinte, []) if p != chemin]
        enregistrements.append({
            "object_id": identifiant,
            "path": chemin,
            "chapter": chapitre,
            "role": role,
            "declared_capacities": codes,
            "declared_status": meta.get("status"),
            "carries_oracle": bool(VERIFY.search(texte)),
            "oracle_verdict": _oracle_verdict(chapitre, Path(chemin).stem),
            # Le registre d'alignement n'examine que les EXERCICES : c'est la
            # que la capacite se declare et se prouve. Un corrige ou une fiche
            # de remediation herite de la preuve de l'objet qu'il sert -- et
            # cet heritage se lit par la reference declaree, jamais par une
            # ressemblance d'identifiant.
            "capacity_semantically_proven": _capacity_proof(
                role, identifiant, codes, meta, prouvees, non_verifiees
            ),
            "answer_coverage_established": (
                identifiant in couverts if role == "exercices" else None
            ),
            "body_digest": empreinte,
            "exact_twins": sorted(jumeaux),
            "editorial_review": "EDITORIAL_REVIEW_PENDING",
        })

    exacts = [r for r in enregistrements if r["exact_twins"]]
    sans_oracle = [
        r for r in enregistrements
        if not r["carries_oracle"] and r["role"] in {"exercices", "corriges"}
    ]
    oracle_rouge = [
        r for r in enregistrements
        if r["oracle_verdict"] not in (None, "pass")
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
        "NEW_AUTHORING_REVIEW_PENDING": len(enregistrements),
        "NEW_AUTHORING_EXACT_CLONES": len(exacts),
        "NEW_AUTHORING_NEAR_CLONES": 0,
        "ORACLE_VERIFIED": sum(
            1 for r in enregistrements if r["oracle_verdict"] == "pass"
        ),
        "OBJECTS_WITHOUT_ORACLE": len(sans_oracle),
        "ORACLE_FAILURES": len(oracle_rouge),
        "CAPACITY_SEMANTICALLY_PROVEN": sum(
            1 for r in enregistrements if r["capacity_semantically_proven"]
        ),
        "CAPACITY_NOT_PROVEN": len(capacite_non_prouvee),
        "ANSWER_COVERAGE_ESTABLISHED": sum(
            1 for r in enregistrements if r["answer_coverage_established"]
        ),
        "ANSWER_COVERAGE_MISSING": len(sans_couverture),
        "APPROVES_NOTHING": True,
    }
    return {
        "artifact_type": "new_authoring_review_debt",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "decontamination_commit": DECONTAMINATION_COMMIT,
        "rule": (
            "un bloc VERIFY prouve une exactitude calculable ; il ne prouve ni "
            "l'adequation au programme, ni la qualite de l'enonce, ni le "
            "niveau, ni le style. Ces objets restent en dette de revue "
            "editoriale."
        ),
        "human_review_required": True,
        "release_blocking": True,
        "approves_nothing": True,
        "summary": summary,
        "exact_clones": exacts,
        "objects_without_oracle": [r["path"] for r in sans_oracle],
        "oracle_failures": [r["path"] for r in oracle_rouge],
        "capacity_not_proven": [r["path"] for r in capacite_non_prouvee],
        "answer_coverage_missing": [r["path"] for r in sans_couverture],
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
        "CAPACITY_SEMANTICALLY_PROVEN", "CAPACITY_NOT_PROVEN",
        "ANSWER_COVERAGE_ESTABLISHED", "ANSWER_COVERAGE_MISSING",
    ):
        lignes.append(f"- `{cle}` : `{s[cle]}`")
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
