"""Les vues de lecture humaine : deterministes, completes, et sans autorite.

Une vue derivee qui porterait un verdict, ou qui nommerait un relecteur, ferait
signer une decision hors du packet canonique. Ces tests verrouillent les trois
proprietes qui rendent la vue sure : elle se regenere a l'identique, elle couvre
les dix chapitres pour les deux roles, et elle ne decide rien.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _load_producer():
    spec = importlib.util.spec_from_file_location(
        "build_human_review_reading_views",
        ROOT / "scripts" / "build_human_review_reading_views.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


PRODUCER = _load_producer()

VERDICTS = ("APPROVED", "CHANGES_REQUESTED", "REJECTED")


@pytest.fixture(scope="module")
def rendered() -> dict[Path, str]:
    return PRODUCER.render_all()


def test_two_runs_produce_identical_files() -> None:
    """Deux executions rendent exactement les memes octets."""

    first = PRODUCER.render_all()
    second = PRODUCER.render_all()
    assert sorted(first) == sorted(second)
    for path, content in first.items():
        assert second[path] == content, path.as_posix()


def test_every_chapter_and_role_has_a_view(rendered: dict[Path, str]) -> None:
    chapters = PRODUCER.chapter_ids()
    assert len(chapters) == 10, chapters
    expected = {
        PRODUCER.REVIEWS / chapter / f"view-{letter}-{role}.md"
        for chapter in chapters
        for role, letter in PRODUCER.ROLES.items()
    }
    assert expected <= set(rendered)
    assert len(expected) == 20
    assert PRODUCER.COMMON_DOCUMENT in rendered
    assert len(rendered) == 21


def test_views_on_disk_match_the_producer(rendered: dict[Path, str]) -> None:
    """Les vues commitees sont celles que le producteur rend aujourd'hui."""

    assert PRODUCER.main(["--check"]) == 0


def _views(rendered: dict[Path, str]) -> dict[Path, str]:
    return {
        path: content
        for path, content in rendered.items()
        if path != PRODUCER.COMMON_DOCUMENT
    }


def test_no_view_carries_a_verdict(rendered: dict[Path, str]) -> None:
    """Les seuls verdicts cites sont le rappel des verdicts autorises."""

    for path, content in _views(rendered).items():
        carrying = [
            line
            for line in content.splitlines()
            if any(verdict in line for verdict in VERDICTS)
        ]
        assert len(carrying) == 1, (path.as_posix(), carrying)
        line = carrying[0]
        assert line.startswith("- Verdicts autorises"), (path.as_posix(), line)
        assert "jamais dans cette vue" in line, (path.as_posix(), line)
        for verdict in VERDICTS:
            assert f"`{verdict}`" in line


def test_no_view_names_a_reviewer(rendered: dict[Path, str]) -> None:
    """Aucune identite, aucun identifiant de relecteur, aucune signature."""

    forbidden = (
        "reviewer_id",
        "reviewer_name",
        "reviewer_identity",
        "assigned_reviewer",
        "signataire",
        "signe par",
        "signe le",
        "attestation",
    )
    email = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
    for path, content in rendered.items():
        lowered = content.lower()
        for token in forbidden:
            assert token not in lowered, (path.as_posix(), token)
        assert not email.search(content), path.as_posix()
        assert "PENDING_UNASSIGNED" in content or path == PRODUCER.COMMON_DOCUMENT


def test_each_view_carries_the_three_mandatory_mentions(
    rendered: dict[Path, str],
) -> None:
    for path, content in _views(rendered).items():
        assert PRODUCER.MENTION_BASELINE in content, path.as_posix()
        assert PRODUCER.MENTION_DERIVED in content, path.as_posix()
        assert PRODUCER.MENTION_DECISION_UNIT in content, path.as_posix()
        assert "CONTENT_APPROVAL_BINDS_TO = SEMANTIC_DIGEST" in content
        assert "porte D7" in content


def test_each_view_binds_to_its_own_semantic_digest(
    rendered: dict[Path, str],
) -> None:
    for chapter in PRODUCER.chapter_ids():
        state = json.loads(
            (PRODUCER.REVIEWS / chapter / "REVIEW_STATE.json").read_text(
                encoding="utf-8"
            )
        )
        for role, letter in PRODUCER.ROLES.items():
            path = PRODUCER.REVIEWS / chapter / f"view-{letter}-{role}.md"
            content = rendered[path]
            assert state["semantic_review_digest"] in content, path.as_posix()
            assert state["object_set_digest"] in content, path.as_posix()


def test_each_view_carries_its_role_checklist(rendered: dict[Path, str]) -> None:
    for chapter in PRODUCER.chapter_ids():
        for role, letter in PRODUCER.ROLES.items():
            content = rendered[
                PRODUCER.REVIEWS / chapter / f"view-{letter}-{role}.md"
            ]
            for item in PRODUCER.CHECKLISTS[role]:
                assert item in content, (chapter, role, item)


def test_each_view_carries_capabilities_assembly_and_pdf(
    rendered: dict[Path, str],
) -> None:
    for chapter in PRODUCER.chapter_ids():
        contract_capacities = [
            capacity["libelle_eleve"]
            for capacity in PRODUCER.yaml.safe_load(
                (PRODUCER.CHAPTERS_DIR / chapter / "contrat.yaml").read_text(
                    encoding="utf-8"
                )
            )["capacites"]
        ]
        for role, letter in PRODUCER.ROLES.items():
            content = rendered[
                PRODUCER.REVIEWS / chapter / f"view-{letter}-{role}.md"
            ]
            for libelle in contract_capacities:
                assert libelle in content, (chapter, role, libelle)
            assert "Structure reelle et ordre d'assemblage courant" in content
            assert "collect_chapter" in content
            assert "MANUELS_PDF_PUBLICATION/01_Maths_1re_Spe_Eleve.pdf" in content


def test_assembly_gap_is_measured_against_repository_relative_paths(
    rendered: dict[Path, str],
) -> None:
    """Un chemin absolu compare a un chemin relatif declarerait tout absent."""

    sources = PRODUCER.load_sources()
    gaps = {
        chapter: PRODUCER.chapter_facts(chapter, sources)["not_assembled"]
        for chapter in PRODUCER.chapter_ids()
    }
    assert gaps["1SPE-VARIABLES-ALEATOIRES"] == [
        "Mathematiques/manuel-maths/chapitres/1SPE-VARIABLES-ALEATOIRES/cours/"
        f"experimentations/{name}"
        for name in (
            "02_frequences_lettres.tex",
            "03_simuler_variable.tex",
            "04_fonction_moyenne.tex",
            "05_distance_moyenne_esperance.tex",
            "06_proportion_2sigma.tex",
        )
    ]
    for chapter, missing in gaps.items():
        if chapter == "1SPE-VARIABLES-ALEATOIRES":
            continue
        assert missing == [], (chapter, missing)
        for letter, role in (("A", PRODUCER.ROLE_A), ("B", PRODUCER.ROLE_B)):
            content = rendered[
                PRODUCER.REVIEWS / chapter / f"view-{letter}-{role}.md"
            ]
            assert "absents de la sequence assemblee" not in content


def test_mathematics_view_groups_human_science_by_family(
    rendered: dict[Path, str],
) -> None:
    """Les objets de science humaine requise sont groupes, jamais deverses."""

    ledger = json.loads(PRODUCER.DISPOSITION_LEDGER.read_text(encoding="utf-8"))
    for chapter in PRODUCER.chapter_ids():
        expected = [
            entry
            for entry in ledger["objects"]
            if entry["chapter"] == chapter
            and entry["disposition"] == PRODUCER.HUMAN_SCIENCE
        ]
        content = rendered[
            PRODUCER.REVIEWS / chapter / f"view-A-{PRODUCER.ROLE_A}.md"
        ]
        assert "Points d'attention scientifiques, par famille" in content
        assert f"{len(expected)} objets" in content
        families = [line for line in content.splitlines() if line.startswith("### Famille")]
        assert families, chapter
        # chaque famille declare un type d'objet : jamais une liste JSON brute.
        assert "```json" not in content


def test_pedagogy_view_consolidates_cells_by_capacity(
    rendered: dict[Path, str],
) -> None:
    ledger = json.loads(PRODUCER.SEMANTIC_LEDGER.read_text(encoding="utf-8"))
    for chapter in PRODUCER.chapter_ids():
        codes = sorted(
            {
                record["official_capacity"]["local_code"]
                for record in ledger["records"]
                if record["chapter"] == chapter
            }
        )
        content = rendered[
            PRODUCER.REVIEWS / chapter / f"view-B-{PRODUCER.ROLE_B}.md"
        ]
        for code in codes:
            assert f"### Capacite `{code}`" in content, (chapter, code)
        assert "Progression de difficulte declaree" in content
        assert "gestes de raisonnement declares" in content
        assert "Routage de cette capacite vers l'humain" in content
        assert PRODUCER.ROUTING_DOCTRINE in content
        # la doctrine est dite une fois, pas recopiee sous chaque capacite.
        assert content.count(PRODUCER.ROUTING_DOCTRINE) == 1


def test_capacity_without_official_wording_is_named_as_such(
    rendered: dict[Path, str],
) -> None:
    """Une capacite sans libelle BO se voit, elle ne se remplit pas toute seule."""

    for chapter in PRODUCER.chapter_ids():
        referential = json.loads(
            (
                PRODUCER.REFERENTIEL
                / f"capacites_{chapter.replace('-', '_')}.json"
            ).read_text(encoding="utf-8")
        )
        declared = {item["id"] for item in referential["capacites"]}
        contract = PRODUCER.yaml.safe_load(
            (PRODUCER.CHAPTERS_DIR / chapter / "contrat.yaml").read_text(
                encoding="utf-8"
            )
        )
        missing = [
            item["code"]
            for item in contract["capacites"]
            if item["ref_capacite"] not in declared
        ]
        content = rendered[
            PRODUCER.REVIEWS / chapter / f"view-B-{PRODUCER.ROLE_B}.md"
        ]
        if missing:
            assert PRODUCER.NO_BO_WORDING in content, chapter
        else:
            assert PRODUCER.NO_BO_WORDING not in content, chapter
    varalea = rendered[
        PRODUCER.REVIEWS
        / "1SPE-VARIABLES-ALEATOIRES"
        / f"view-B-{PRODUCER.ROLE_B}.md"
    ]
    assert varalea.count(PRODUCER.NO_BO_WORDING) == 4


def test_human_routed_qcm_question_is_visible_in_its_chapter(
    rendered: dict[Path, str],
) -> None:
    """La seule question 1SPE routee vers l'humain ne se perd pas dans la masse."""

    evidence = json.loads(PRODUCER.QCM_EVIDENCE.read_text(encoding="utf-8"))
    routed = [
        question
        for question in evidence["questions"]
        if question["chapter"].startswith("1SPE-") and question["human_review_required"]
    ]
    assert [(q["chapter"], q["question_id"]) for q in routed] == [
        ("1SPE-VARIABLES-ALEATOIRES", "Q16")
    ]
    source = json.loads(
        (PRODUCER.ROOT / routed[0]["source_path"]).read_text(encoding="utf-8")
    )
    question = next(item for item in source["questions"] if item["id"] == "Q16")
    for role, letter in PRODUCER.ROLES.items():
        content = rendered[
            PRODUCER.REVIEWS
            / "1SPE-VARIABLES-ALEATOIRES"
            / f"view-{letter}-{role}.md"
        ]
        assert "`Q16`" in content
        assert question["enonce"] in content
        for option in question["options"].values():
            assert option in content
        assert routed[0]["reason"] in content
    for chapter in PRODUCER.chapter_ids():
        if chapter == "1SPE-VARIABLES-ALEATOIRES":
            continue
        content = rendered[
            PRODUCER.REVIEWS / chapter / f"view-A-{PRODUCER.ROLE_A}.md"
        ]
        assert "Aucune question de ce chapitre n'est routee" in content


def test_declared_answer_keys_never_leak_into_a_view(
    rendered: dict[Path, str],
) -> None:
    """L'expert etablit la reponse : la cle declaree ne voyage pas avec l'enonce."""

    for path, content in rendered.items():
        assert '"correcte"' not in content, path.as_posix()
        assert "cle declaree" not in content or "n'est pas reproduite" in content


def test_common_document_has_template_and_instructions(
    rendered: dict[Path, str],
) -> None:
    content = rendered[PRODUCER.COMMON_DOCUMENT]
    assert "Modele d'assignation" in content
    assert "Instructions de revue" in content
    assert "assigne_a: null" in content
    assert "10 chapitres x 2 roles = 20 verdicts" in content
    for chapter in PRODUCER.chapter_ids():
        assert f"`{chapter}`" in content


def test_compact_ids_folds_consecutive_numbering() -> None:
    assert PRODUCER.compact_ids(["X-001", "X-002", "X-003"]) == "`X-001..003`"
    assert PRODUCER.compact_ids(["X-001", "X-003"]) == "`X-001`, `X-003`"
    assert (
        PRODUCER.compact_ids(["X-031-CDP", "X-032-CDP"]) == "`X-031..032-CDP`"
    )
    assert PRODUCER.compact_ids(["Q2", "Q10", "Q1"]) == "`Q1..2`, `Q10`"
    assert PRODUCER.compact_ids(["SANS-NUMERO"]) == "`SANS-NUMERO`"
