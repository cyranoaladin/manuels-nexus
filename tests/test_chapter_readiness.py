from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys

import yaml

from scripts.capacity_identity import CapacityIdentityResolver

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "chapter_readiness.py"
SPEC = importlib.util.spec_from_file_location("chapter_readiness", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
chapter_readiness = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = chapter_readiness
SPEC.loader.exec_module(chapter_readiness)

SUITES = (
    ROOT
    / "Mathematiques"
    / "manuel-maths"
    / "chapitres"
    / "1SPE-SUITES"
)
BUILD_MANIFEST = ROOT / "audit" / "BUILD_MANIFEST.json"


def test_qcm_meta_is_counted_without_promoting_generated_status(
    tmp_path: Path,
) -> None:
    chapter = tmp_path / "1SPE-TEST-QCM"
    qcm = chapter / "qcm"
    qcm.mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(
        yaml.safe_dump(
            {
                "chapitre": "1SPE-TEST-QCM",
                "statut": "draft",
                "capacites": [{"code": "C1", "ref_capacite": "REF-C1"}],
            }
        ),
        encoding="utf-8",
    )
    (qcm / "1SPE-TEST-QCM-QCM.tex").write_text(
        "% META: "
        + json.dumps(
            {
                "id": "1SPE-TEST-QCM-QCM",
                "chapitre": "1SPE-TEST-QCM",
                "type_objet": "qcm",
                "status": "generated",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    (qcm / "1SPE-TEST-QCM-QCM.json").write_text(
        json.dumps({"chapitre": "1SPE-TEST-QCM", "questions": []}) + "\n",
        encoding="utf-8",
    )

    result = chapter_readiness.analyser(chapter, {}, {})

    assert result.objects_total == 1
    assert result.objects_generated == 1
    assert result.objects_reviewed == 0


def test_qcm_official_reference_credits_owner_and_reports_missing_neighbour(
    tmp_path: Path,
) -> None:
    chapter = tmp_path / "TSPE-PROBABILITES"
    qcm = chapter / "qcm"
    qcm.mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(
        yaml.safe_dump(
            {
                "chapitre": "TSPE-PROBABILITES",
                "statut": "needs_review",
                "capacites": [
                    {"code": "C1", "ref_capacite": "TSPE-PROBA-C1"},
                    {"code": "C10", "ref_capacite": "TSPE-CONCLGN-C1"},
                ],
            }
        ),
        encoding="utf-8",
    )
    (qcm / "TSPE-PROBABILITES-QCM.json").write_text(
        json.dumps(
            {
                "chapitre": "TSPE-PROBABILITES",
                "questions": [
                    {
                        "id": "Q1",
                        "capacite": "TSPE-CONCLGN-C1",
                        "correcte": "A",
                        "options": {"A": "a", "B": "b"},
                        "diagnostics": {"B": {"erreur": "e", "renvoi": "C10"}},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    resolver = CapacityIdentityResolver.from_corpora((tmp_path,))

    result = chapter_readiness.analyser(chapter, {}, {}, resolver=resolver)

    assert result.qcm_capacities_assessed == ["C10"]
    assert result.qcm_capacities_missing == ["C1"]
    assert result.qcm_status == "capacites_manquantes:C1"


def test_real_1spe_suites_keeps_all_objects_generated_and_release_blocking(
) -> None:
    result = chapter_readiness.analyser(
        SUITES,
        {"1SPE": "2026"},
        {},
    )

    assert result.objects_total == 161
    assert result.objects_generated == 161
    assert result.objects_reviewed == 0
    assert result.contract_status == "draft"
    assert result.authority == "NON_AUTHORITATIVE_LEGACY_DASHBOARD"
    assert "161/161 objets encore au statut generated" in result.blocking_findings
    assert result.release_ready is False


def test_present_pdfs_without_observed_manifest_builds_are_not_ready() -> None:
    manifest = json.loads(BUILD_MANIFEST.read_text(encoding="utf-8"))
    assert manifest["builds"] == []
    assert (
        ROOT
        / "Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.pdf"
    ).is_file()
    assert (
        ROOT
        / "Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_professeur.pdf"
    ).is_file()

    result = next(
        chapter
        for chapter in chapter_readiness.collecter()
        if chapter.chapter_id == "1SPE-SUITES"
    )

    assert result.student_build is False
    assert result.teacher_build is False


def test_canonical_observed_build_variants_enable_only_exact_variant() -> None:
    student = chapter_readiness.analyser(
        SUITES,
        {"1SPE": "2026"},
        {"1SPE": {"eleve"}},
    )
    teacher = chapter_readiness.analyser(
        SUITES,
        {"1SPE": "2026"},
        {"1SPE": {"professeur"}},
    )

    assert student.student_build is True
    assert student.teacher_build is False
    assert teacher.student_build is False
    assert teacher.teacher_build is True


def test_official_reference_credits_only_its_resolved_local_capacity(
    tmp_path: Path,
) -> None:
    chapter = tmp_path / "TSPE-PROBABILITES"
    exercises = chapter / "exercices"
    exercises.mkdir(parents=True)
    (chapter / "contrat.yaml").write_text(
        yaml.safe_dump(
            {
                "statut": "needs_review",
                "capacites": [
                    {"code": "C1", "ref_capacite": "TSPE-PROBA-C1"},
                    {"code": "C10", "ref_capacite": "TSPE-CONCLGN-C1"},
                ],
            }
        ),
        encoding="utf-8",
    )
    (exercises / "EX.tex").write_text(
        "% META: "
        + json.dumps(
            {
                "id": "EX",
                "chapitre": "TSPE-PROBABILITES",
                "type_objet": "exercice",
                "capacites": ["TSPE-CONCLGN-C1"],
                "parcours": 1,
                "status": "needs_review",
            }
        )
        + "\n",
        encoding="utf-8",
    )
    resolver = CapacityIdentityResolver.from_corpora((tmp_path,))

    result = chapter_readiness.analyser(chapter, {}, {}, resolver=resolver)

    assert result.capability_min_exercises["C1"] == 0
    assert result.capability_min_exercises["C10"] == 1
    assert "TSPE-CONCLGN-C1" not in result.capability_min_exercises


def _chapitre_minimal(racine: Path, nom: str) -> Path:
    """Un chapitre reduit au strict necessaire pour etre analyse."""

    chapitre = racine / nom
    chapitre.mkdir(parents=True)
    (chapitre / "contrat.yaml").write_text(
        yaml.safe_dump(
            {
                "chapitre": nom,
                "statut": "draft",
                "capacites": [{"code": "C1", "ref_capacite": "REF-C1"}],
            }
        ),
        encoding="utf-8",
    )
    return chapitre


def _recu(dossier: Path, nom: str, charge: dict) -> None:
    dossier.mkdir(parents=True, exist_ok=True)
    (dossier / nom).write_text(json.dumps(charge) + "\n", encoding="utf-8")


def test_scientific_review_ne_compte_que_les_recus_qui_lient_leur_source(
    tmp_path: Path,
) -> None:
    """Un `pass` non lie n'est pas une preuve scientifique.

    Le recu SymPy nomme la source qu'il atteste et porte son condensat : il
    meurt avec elle. Les recus de similarite et les rapports adversariaux ne
    nomment rien -- ils survivraient a une reecriture complete du contenu.
    Les additionner dans un meme `pass` publie un total qui ressemble a une
    preuve sans en etre une.
    """

    chapitre = _chapitre_minimal(tmp_path, "1SPE-TEST-RECUS")
    validations = chapitre / "validations"
    _recu(
        validations,
        "objet.sympy.json",
        {
            "objet_id": "objet",
            "gate": "sympy",
            "verdict": "pass",
            "source_path": "chapitres/1SPE-TEST-RECUS/cours/objet.tex",
            "source_sha256": "sha256:" + "0" * 64,
        },
    )
    _recu(
        validations,
        "objet.similarity.json",
        {"objet_id": "objet", "gate": "similarity", "verdict": "pass"},
    )
    _recu(
        validations,
        "objet.adversarial.json",
        {"objet_id": "objet", "verdict": "pass", "mode": "auto-validation autonome"},
    )

    resultat = chapter_readiness.analyser(chapitre, {}, {})

    assert resultat.scientific_review == {"pass": 1}, (
        "seul le recu SymPy, qui lie sa source, vaut preuve scientifique"
    )
    assert resultat.unbound_receipts == {
        "adversarial": {"pass": 1},
        "similarity": {"pass": 1},
    }, "les recus non lies doivent etre nommes, jamais fondus dans le total"


def test_un_echec_non_lie_reste_visible_et_ne_disparait_pas(
    tmp_path: Path,
) -> None:
    """Ecarter un recu de la preuve ne doit pas le rendre muet.

    Si l'on cessait simplement de lire les recus non lies, un `fail` de
    similarite disparaitrait du tableau de bord : on aurait echange un total
    trompeur contre un silence, ce qui est pire.
    """

    chapitre = _chapitre_minimal(tmp_path, "1SPE-TEST-ECHEC")
    _recu(
        chapitre / "validations",
        "objet.similarity.json",
        {"objet_id": "objet", "gate": "similarity", "verdict": "fail"},
    )

    resultat = chapter_readiness.analyser(chapitre, {}, {})

    assert resultat.scientific_review == {}
    assert resultat.unbound_receipts == {"similarity": {"fail": 1}}
    assert resultat.blocking_findings, "un echec, meme non lie, reste bloquant"


def test_le_total_publie_de_1spe_suites_est_celui_de_ses_recus_lies() -> None:
    """Le chapitre reel : 262 `pass` annonces pour 122 preuves liees."""

    resultat = chapter_readiness.analyser(
        SUITES, chapter_readiness._versions_programme(), chapter_readiness._builds_observes()
    )
    lies = sum(resultat.scientific_review.values())
    non_lies = sum(
        sum(verdicts.values()) for verdicts in resultat.unbound_receipts.values()
    )

    assert resultat.scientific_review.get("pass") == 122
    assert resultat.scientific_review.get("manual_review") == 31
    assert lies == 153
    assert non_lies > 0, "le chapitre porte bien des recus non lies"
