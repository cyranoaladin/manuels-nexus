"""Aucun gate de release ne peut imposer un nombre d'exercices par chapitre.

Le quota `>=50 ex/chapitre` a cree l'incitation exacte qui a produit le
remplissage : neuf cents copies d'exercices d'analyse dispersees dans quinze
chapitres, chacune satisfaisant un compteur et aucune un eleve. Le Release
Owner l'a supersede le 2026-09-07.

Ce garde est statique : il lit le depot, pas une mesure. Un seuil numerique
reintroduit dans un producteur ou un test bloquant le ferait echouer, quelle
que soit la valeur du corpus a ce moment-la.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "audit/FIFTY_EXERCISES_POLICY_ORIGIN.json"

#: Un COMPTE d'exercices de chapitre confronte a un ENTIER LITTERAL. Ce n'est
#: pas « le mot exercice pres d'un nombre » : comparer deux compteurs entre
#: eux (`correction_count >= exercise_count`) est une coherence, pas un
#: quota, et compter les questions d'un enonce non plus.
COMPTEUR = (
    r"(?:target_exercises|plafond_exercices|min_exercises|max_exercises"
    r"|exercise_count|exercices_count|nb_exercices|nombre_exercices"
    r"|exercises_per_chapter|exercices_par_chapitre)"
)
QUOTA = re.compile(
    rf"{COMPTEUR}\s*(?:[<>]=?|==)\s*\d+"
    rf"|\d+\s*(?:[<>]=?|==)\s*{COMPTEUR}"
    rf"|{COMPTEUR}\s*=\s*\d+",
    re.I,
)

#: Les fichiers qui PARLENT du quota pour dire qu'il est supersede n'en sont
#: pas des applications. On les nomme, plutot que d'assouplir la regle.
DOCUMENTATION = {
    "scripts/build_fifty_exercises_policy_origin.py",
    "tests/test_no_fixed_exercise_quota.py",
    "tests/test_contaminated_approval_and_policy.py",
}

#: Un tableau de bord qui declare lui-meme n'etre pas autoritaire pour la
#: release peut garder un seuil indicatif. La declaration doit etre dans le
#: fichier, lisible, et pas dans une liste d'exceptions tenue ailleurs.
NON_AUTORITAIRE = re.compile(r"non autoritaire pour la release", re.I)


def _sources() -> list[Path]:
    chemins: list[Path] = []
    for dossier in ("scripts", "tests"):
        chemins.extend(sorted((ROOT / dossier).rglob("*.py")))
    chemins.extend(sorted((ROOT / "Mathematiques/manuel-maths/scripts").rglob("*.py")))
    return chemins


def test_no_release_gate_enforces_a_fixed_exercise_count() -> None:
    coupables = []
    for chemin in _sources():
        relatif = str(chemin.relative_to(ROOT))
        if relatif in DOCUMENTATION:
            continue
        texte = chemin.read_text(encoding="utf-8", errors="replace")
        if NON_AUTORITAIRE.search(texte):
            continue
        for numero, ligne in enumerate(texte.splitlines(), 1):
            if ligne.lstrip().startswith("#"):
                continue
            if QUOTA.search(ligne):
                coupables.append(f"{relatif}:{numero}: {ligne.strip()}")
    assert not coupables, (
        "un seuil fixe d'exercices est reapparu dans un gate ; il faut une "
        "nouvelle decision humaine explicite pour cela :\n" + "\n".join(coupables)
    )


def test_the_policy_artifact_declares_the_supersession() -> None:
    payload = json.loads(POLICY.read_text(encoding="utf-8"))
    supersession = payload["supersession"]
    assert payload["summary"]["FIFTY_EXERCISES_RELEASE_REQUIREMENT"] == (
        "SUPERSEDED_EDITORIAL_VOLUME_TARGET"
    )
    assert payload["summary"]["FIXED_EXERCISE_COUNT_RELEASE_GATES"] == 0
    assert supersession["SUPERSEDED_BY_RELEASE_OWNER"] == "abenrhouma"
    assert supersession["SUPERSESSION_DATE"] == "2026-09-07"
    assert len(supersession["SUPERSESSION_REASON"]) >= 4
    assert supersession["HISTORICAL_PROMPT_PRESERVED"] is True


def test_the_historical_directive_is_not_erased() -> None:
    """On n'efface pas une directive : on dit ce qu'elle est devenue."""

    prompt = (ROOT / "PROMPT_MISSION_COLLECTION.md").read_text(encoding="utf-8")
    assert "≥50 ex/chapitre" in prompt
    payload = json.loads(POLICY.read_text(encoding="utf-8"))
    assert payload["summary"]["HISTORICAL_REQUIREMENT_EXISTED"] is True


def test_fewer_exercises_without_coverage_loss_does_not_fail_the_release() -> None:
    """Le critere porte sur la couverture, pas sur le volume.

    Quinze chapitres ont perdu entre 80 et 90 % de leurs exercices pendant la
    decontamination. Aucune capacite officielle n'est restee sans exercice, et
    la matrice de richesse est COMPLETE : la baisse de volume ne fait echouer
    aucun axe.
    """

    richesse = json.loads(
        (ROOT / "audit/CHAPTER_RICHNESS_MATRIX.json").read_text(encoding="utf-8")
    )
    assert richesse["machine_status"] == "COMPLETE"
    insuffisantes = [
        (chapitre, code)
        for chapitre, contenu in richesse["chapters"].items()
        for code, ligne in contenu["capacities"].items()
        if ligne.get("missing_function")
    ]
    assert insuffisantes == []


def test_a_full_chapter_with_a_real_gap_still_fails() -> None:
    """L'inverse doit tenir : cinquante exercices ne rachetent pas un manque.

    On force une capacite sans aucune pratique ciblee dans un chapitre par
    ailleurs fourni ; la regle de richesse doit la declarer insuffisante.
    """

    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location(
        "richesse_quota", ROOT / "scripts/build_chapter_richness_matrix.py"
    )
    module = importlib.util.module_from_spec(spec)
    sys.modules["richesse_quota"] = module
    spec.loader.exec_module(module)

    import json
    import tempfile

    with tempfile.TemporaryDirectory() as dossier:
        racine = Path(dossier) / "chapitres"
        chapitre = racine / "TCOMPL-PLEIN"
        (chapitre / "exercices").mkdir(parents=True)
        (chapitre / "contrat.yaml").write_text(
            "chapitre: TCOMPL-PLEIN\ncapacites:\n"
            "  - { code: C1, ref_capacite: TCOMPL-PLEIN-C1,"
            " libelle_eleve: \"Je sais appliquer une methode.\" }\n"
            "  - { code: C2, ref_capacite: TCOMPL-PLEIN-C2,"
            " libelle_eleve: \"Je sais conclure.\" }\n",
            encoding="utf-8",
        )
        # Cinquante exercices, tous sur C1 : le chapitre est « plein » et C2
        # n'a rien. Le volume ne rachete pas le manque.
        for n in range(1, 51):
            meta = {
                "id": f"TCOMPL-PLEIN-EX-{n:03d}", "chapitre": "TCOMPL-PLEIN",
                "type_objet": "exercice", "capacites_codes": ["C1"],
                "parcours": 1 + n % 3, "duree_min": 10,
            }
            (chapitre / "exercices" / f"TCOMPL-PLEIN-EX-{n:03d}.tex").write_text(
                "% META: " + json.dumps(meta, ensure_ascii=False) + "\n"
                "\\begin{exercice}{TCOMPL-PLEIN-EX-" + f"{n:03d}" + "}{1}{10}\n"
                f"Appliquer la methode au cas numero {n}.\n\\end{{exercice}}\n",
                encoding="utf-8",
            )
        matrice = module.build_matrix("TCOMPL-PLEIN", chapter_root=racine)

    lignes = matrice["capacities"]
    assert lignes["C1"]["opportunities"]["targeted_practice"] == 50
    assert lignes["C2"]["status"] == "INSUFFICIENT", lignes["C2"]
    assert "NO_TARGETED_PRACTICE" in lignes["C2"]["missing_function"]
    assert matrice["machine_status"] != "COMPLETE"
