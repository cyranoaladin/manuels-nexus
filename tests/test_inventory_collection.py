from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "inventory_collection.py"


def _load_inventory_module():
    assert SCRIPT.is_file(), "scripts/inventory_collection.py doit etre cree"
    spec = importlib.util.spec_from_file_location("inventory_collection", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture()
def inventory_module():
    return _load_inventory_module()


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def _init_repository(root: Path) -> None:
    subprocess.run(["git", "init", "-q", str(root)], check=True)


def _track(root: Path, *relative_paths: str) -> None:
    subprocess.run(
        ["git", "-C", str(root), "add", "--", *relative_paths],
        check=True,
    )


def _contract(chapter: str, level: str, capacities: int = 2) -> str:
    rows = "\n".join(
        f'  - {{ code: C{index}, ref_capacite: {chapter}-C{index}, libelle_eleve: "Capacite {index}" }}'
        for index in range(1, capacities + 1)
    )
    return (
        f"chapitre: {chapter}\n"
        f"niveau: {level}\n"
        f"titre: Chapitre de test\n"
        "statut: approved\n"
        "capacites:\n"
        f"{rows}\n"
    )


def _meta(**overrides: object) -> str:
    data: dict[str, object] = {
        "id": "1SPE-TEST-COURS-C1",
        "chapitre": "1SPE-TEST",
        "type_objet": "cours",
        "status": "generated",
    }
    data.update(overrides)
    return (
        "% META: "
        + json.dumps(data, ensure_ascii=False, sort_keys=True)
        + "\nContenu\n"
    )


def _chapter_path(manual: str, chapter: str) -> str:
    if manual in {"1SPE", "TSPE"}:
        return f"Mathematiques/manuel-maths/chapitres/{chapter}"
    return f"NSI/chapitres/{chapter}"


def test_git_tracked_files_excludes_untracked_sources(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    tracked = f"{base}/cours/section.tex"
    untracked = f"{base}/cours/brouillon.tex"
    _write(tmp_path / tracked, _meta())
    _write(tmp_path / untracked, _meta(id="1SPE-TEST-BROUILLON"))
    _track(tmp_path, tracked)

    assert inventory_module.git_tracked_files(tmp_path) == (tracked,)


def test_load_contract_reads_yaml_without_losing_capacity_order(
    tmp_path: Path, inventory_module
) -> None:
    contract_path = tmp_path / "contrat.yaml"
    _write(contract_path, _contract("1SPE-TEST", "1SPE", capacities=2))

    contract = inventory_module.load_contract(contract_path)

    assert contract["chapitre"] == "1SPE-TEST"
    assert [capacity["code"] for capacity in contract["capacites"]] == ["C1", "C2"]


def test_read_meta_validates_required_fields(tmp_path: Path, inventory_module) -> None:
    valid_path = tmp_path / "valid.tex"
    missing_id_path = tmp_path / "missing-id.tex"
    invalid_json_path = tmp_path / "invalid-json.tex"
    _write(valid_path, _meta())
    _write(
        missing_id_path,
        '% META: {"chapitre": "1SPE-TEST", "type_objet": "cours", "status": "generated"}\n',
    )
    _write(invalid_json_path, "% META: pas-du-json\n")

    assert inventory_module.read_meta(valid_path)["id"] == "1SPE-TEST-COURS-C1"
    with pytest.raises(inventory_module.MetadataError, match="id"):
        inventory_module.read_meta(missing_id_path)
    with pytest.raises(inventory_module.MetadataError, match="JSON"):
        inventory_module.read_meta(invalid_json_path)


def test_non_string_subtype_is_reported_as_invalid_metadata_without_crashing(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    contract = f"{base}/contrat.yaml"
    invalid = f"{base}/cours/invalid-subtype.tex"
    _write(tmp_path / contract, _contract("1SPE-TEST", "1SPE", capacities=1))
    _write(tmp_path / invalid, _meta(sous_type=["diagnostic"]))
    _track(tmp_path, contract, invalid)

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["anomalies"]["metadata_invalid"] == [
        {"path": invalid, "reason": "champ META sous_type invalide: texte attendu"}
    ]
    assert inventory["manuals"]["1SPE"]["chapters"]["1SPE-TEST"]["objects"] == []


@pytest.mark.parametrize(
    ("source_type", "source_subtype", "expected"),
    [
        ("cours", None, "sections_cours"),
        ("cours", "diagnostic", "diagnostics"),
        ("cours", "td_contextualise", "td"),
        ("cours", "td_fil_rouge", "td"),
        ("cours", "ouverture", None),
        ("methode", None, "methodes"),
        ("exercice", None, "exercices_principaux"),
        ("corrige", None, "corriges"),
        ("corrige_evaluation", None, "corriges"),
        ("evaluation_corrige", None, "corriges"),
        ("coup_de_pouce", None, "coups_de_pouce"),
        ("qcm", None, "qcm"),
        ("qcm_diagnostics", None, "diagnostics"),
        ("remediation", None, "remediations"),
        ("td", None, "td"),
        ("evaluation", None, "evaluations"),
        ("projet", None, "projets"),
        ("amenagee", None, None),
    ],
)
def test_canonical_category_preserves_required_taxonomy(
    source_type: str,
    source_subtype: str | None,
    expected: str | None,
    inventory_module,
) -> None:
    assert inventory_module.canonical_category(source_type, source_subtype) == expected


def test_subtype_priority_changes_counts_but_preserves_source_taxonomy(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    sources = {
        f"{base}/contrat.yaml": _contract("1SPE-TEST", "1SPE", capacities=1),
        f"{base}/cours/diagnostic.tex": _meta(
            id="1SPE-TEST-DIAG", sous_type="diagnostic"
        ),
        f"{base}/cours/ouverture.tex": _meta(
            id="1SPE-TEST-OPEN", sous_type="ouverture"
        ),
        f"{base}/cours/td-context.tex": _meta(
            id="1SPE-TEST-TD-CONTEXT", sous_type="td_contextualise"
        ),
        f"{base}/cours/td-fil.tex": _meta(
            id="1SPE-TEST-TD-FIL", sous_type="td_fil_rouge"
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    chapter = inventory_module.build_inventory(tmp_path)["manuals"]["1SPE"]["chapters"][
        "1SPE-TEST"
    ]

    assert chapter["counts"]["sections_cours"] == 0
    assert chapter["counts"]["diagnostics"] == 1
    assert chapter["counts"]["td"] == 2
    assert chapter["source_taxonomy"] == {"cours": 4}
    assert chapter["source_subtypes"] == {
        "diagnostic": 1,
        "ouverture": 1,
        "td_contextualise": 1,
        "td_fil_rouge": 1,
    }


def test_build_inventory_aggregates_objects_and_keeps_four_manuals(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    math_base = _chapter_path("1SPE", "1SPE-TEST")
    nsi_base = _chapter_path("1NSI", "1NSI-TEST")
    sources = {
        f"{math_base}/contrat.yaml": _contract("1SPE-TEST", "1SPE", capacities=2),
        f"{math_base}/cours/c1.tex": _meta(),
        f"{math_base}/methodes/m1.tex": _meta(id="1SPE-TEST-M1", type_objet="methode"),
        f"{math_base}/exercices/e1.tex": _meta(
            id="1SPE-TEST-EX-001", type_objet="exercice"
        ),
        f"{math_base}/corriges/co1.tex": _meta(
            id="1SPE-TEST-CO-001", type_objet="corrige"
        ),
        f"{math_base}/exercices/e1-cdp.tex": _meta(
            id="1SPE-TEST-EX-001-CDP", type_objet="coup_de_pouce"
        ),
        f"{math_base}/qcm/qcm.tex": _meta(id="1SPE-TEST-QCM", type_objet="qcm"),
        f"{math_base}/qcm/diag.tex": _meta(
            id="1SPE-TEST-QCM-DIAG", type_objet="qcm_diagnostics"
        ),
        f"{math_base}/remediation/r1.tex": _meta(
            id="1SPE-TEST-REM-001", type_objet="remediation"
        ),
        f"{math_base}/td/td.tex": _meta(id="1SPE-TEST-TD", type_objet="td"),
        f"{math_base}/evaluations/eval.tex": _meta(
            id="1SPE-TEST-EVAL", type_objet="evaluation"
        ),
        f"{math_base}/projets/projet.tex": _meta(
            id="1SPE-TEST-PROJET", type_objet="projet"
        ),
        f"{math_base}/evaluations/corrige.tex": _meta(
            id="1SPE-TEST-EVAL-CO", type_objet="corrige_evaluation"
        ),
        f"{nsi_base}/contrat.yaml": _contract("1NSI-TEST", "1NSI", capacities=1),
        f"{nsi_base}/cours/c1.tex": _meta(
            id="1NSI-TEST-COURS-C1",
            chapitre="1NSI-TEST",
            type_objet="cours",
            status="approved",
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)

    assert list(inventory["manuals"]) == ["1NSI", "1SPE", "TNSI", "TSPE_2026_2027"]
    chapter = inventory["manuals"]["1SPE"]["chapters"]["1SPE-TEST"]
    assert chapter["counts"] == {
        "capacites": 2,
        "sections_cours": 1,
        "methodes": 1,
        "exercices_principaux": 1,
        "corriges": 2,
        "coups_de_pouce": 1,
        "qcm": 1,
        "diagnostics": 1,
        "remediations": 1,
        "td": 1,
        "evaluations": 1,
        "projets": 1,
    }
    assert chapter["source_taxonomy"] == {
        "corrige": 1,
        "corrige_evaluation": 1,
        "coup_de_pouce": 1,
        "cours": 1,
        "evaluation": 1,
        "exercice": 1,
        "methode": 1,
        "projet": 1,
        "qcm": 1,
        "qcm_diagnostics": 1,
        "remediation": 1,
        "td": 1,
    }
    assert chapter["statuses"] == {"generated": 12}
    assert inventory["manuals"]["1SPE"]["totals"] == chapter["counts"]
    assert inventory["manuals"]["1NSI"]["totals"]["capacites"] == 1
    assert inventory["manuals"]["TNSI"]["chapters"] == {}
    assert inventory["manuals"]["TSPE_2026_2027"]["chapters"] == {}


def test_build_inventory_reports_metadata_ids_and_blocking_statuses(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1NSI", "1NSI-TEST")
    sources = {
        f"{base}/contrat.yaml": _contract("1NSI-TEST", "1NSI", capacities=1).replace(
            "statut: approved", "statut: draft"
        ),
        f"{base}/cours/valid.tex": _meta(
            id="DUPLICATE-ID", chapitre="1NSI-TEST", status="needs_review"
        ),
        f"{base}/methodes/duplicate.tex": _meta(
            id="DUPLICATE-ID",
            chapitre="1NSI-TEST",
            type_objet="methode",
            status="generated",
        ),
        f"{base}/cours/no-meta.tex": "Contenu sans en-tete META\n",
        f"{base}/cours/invalid.tex": "% META: {json invalide}\n",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    anomalies = inventory["anomalies"]

    assert anomalies["metadata_missing"] == [
        {"path": f"{base}/cours/no-meta.tex", "reason": "en-tete % META absent"}
    ]
    assert anomalies["metadata_invalid"][0]["path"] == f"{base}/cours/invalid.tex"
    assert anomalies["duplicate_ids"] == [
        {
            "id": "DUPLICATE-ID",
            "paths": [
                f"{base}/cours/valid.tex",
                f"{base}/methodes/duplicate.tex",
            ],
        }
    ]
    assert anomalies["blocking_statuses"] == [
        {
            "chapter": "1NSI-TEST",
            "id": None,
            "manual": "1NSI",
            "path": f"{base}/contrat.yaml",
            "scope": "contract",
            "status": "draft",
        },
        {
            "chapter": "1NSI-TEST",
            "id": "DUPLICATE-ID",
            "manual": "1NSI",
            "path": f"{base}/cours/valid.tex",
            "scope": "object",
            "status": "needs_review",
        },
        {
            "chapter": "1NSI-TEST",
            "id": "DUPLICATE-ID",
            "manual": "1NSI",
            "path": f"{base}/methodes/duplicate.tex",
            "scope": "object",
            "status": "generated",
        },
    ]


def test_only_explicitly_approved_status_is_publishable(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1NSI", "1NSI-TEST")
    sources = {
        f"{base}/contrat.yaml": _contract("1NSI-TEST", "1NSI", capacities=1),
        f"{base}/cours/approved.tex": _meta(
            id="APPROVED", chapitre="1NSI-TEST", status="approved"
        ),
        f"{base}/cours/generated.tex": _meta(
            id="GENERATED", chapitre="1NSI-TEST", status="generated"
        ),
        f"{base}/cours/spaces.tex": _meta(
            id="SPACES", chapitre="1NSI-TEST", status=" approved "
        ),
        f"{base}/cours/arbitrary.tex": _meta(
            id="ARBITRARY", chapitre="1NSI-TEST", status="publie-peut-etre"
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    anomalies = inventory["anomalies"]

    assert [item["id"] for item in anomalies["blocking_statuses"]] == [
        "ARBITRARY",
        "GENERATED",
        "SPACES",
    ]
    assert anomalies["invalid_statuses"] == [
        {
            "normalized_status": "publie-peut-etre",
            "path": f"{base}/cours/arbitrary.tex",
            "reason": "statut inconnu",
            "scope": "object",
            "source_status": "publie-peut-etre",
        },
        {
            "normalized_status": "approved",
            "path": f"{base}/cours/spaces.tex",
            "reason": "statut non canonique",
            "scope": "object",
            "source_status": " approved ",
        },
    ]
    chapter = inventory["manuals"]["1NSI"]["chapters"]["1NSI-TEST"]
    assert chapter["statuses"] == {
        "approved": 2,
        "generated": 1,
        "publie-peut-etre": 1,
    }
    by_id = {item["id"]: item for item in chapter["objects"]}
    assert by_id["SPACES"]["status"] == "approved"
    assert by_id["SPACES"]["status_valid"] is False
    assert by_id["APPROVED"]["publishable"] is True
    assert by_id["SPACES"]["publishable"] is False


def test_all_math_and_nsi_object_schema_statuses_are_recognized_but_only_approved_publishes(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1NSI", "1NSI-TEST")
    statuses = (
        "approved",
        "draft",
        "generated",
        "manual_review",
        "needs_review",
        "ready",
        "rejected",
        "verified",
    )
    sources = {f"{base}/contrat.yaml": _contract("1NSI-TEST", "1NSI", capacities=1)}
    for status in statuses:
        sources[f"{base}/cours/{status}.tex"] = _meta(
            id=f"STATUS-{status}", chapitre="1NSI-TEST", status=status
        )
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    anomalies = inventory["anomalies"]
    chapter = inventory["manuals"]["1NSI"]["chapters"]["1NSI-TEST"]

    assert anomalies["invalid_statuses"] == []
    assert {item["id"] for item in anomalies["blocking_statuses"]} == {
        f"STATUS-{status}" for status in statuses if status != "approved"
    }
    assert {
        item["source_status"]: item["publishable"] for item in chapter["objects"]
    } == {status: status == "approved" for status in statuses}


def test_contract_status_vocabulary_is_separate_and_requires_explicit_approval(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    contract_statuses = ("approved", "complete", "draft", "valide")
    sources = {}
    for status in contract_statuses:
        chapter = f"1SPE-TEST-{status.upper()}"
        base = _chapter_path("1SPE", chapter)
        sources[f"{base}/contrat.yaml"] = _contract(
            chapter, "1SPE", capacities=1
        ).replace("statut: approved", f"statut: {status}")
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    anomalies = inventory["anomalies"]

    assert anomalies["invalid_statuses"] == []
    assert {
        (item["chapter"], item["status"]) for item in anomalies["blocking_statuses"]
    } == {
        ("1SPE-TEST-COMPLETE", "complete"),
        ("1SPE-TEST-DRAFT", "draft"),
        ("1SPE-TEST-VALIDE", "valide"),
    }


def test_only_well_formed_contract_capacities_are_counted_and_each_error_is_reported(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-CAPACITES")
    contract_path = f"{base}/contrat.yaml"
    _write(
        tmp_path / contract_path,
        """chapitre: 1SPE-CAPACITES
niveau: 1SPE
statut: approved
capacites:
  - {code: C1, ref_capacite: 1SPE-CAPACITES-C1}
  - entree-non-objet
  - {code: C3, ref_capacite: ""}
  - {code: C4, ref_capacite: 4}
""",
    )
    second_chapter = _chapter_path("1SPE", "1SPE-CAPACITES-NON-LISTE")
    second_contract = f"{second_chapter}/contrat.yaml"
    _write(
        tmp_path / second_contract,
        """chapitre: 1SPE-CAPACITES-NON-LISTE
niveau: 1SPE
statut: approved
capacites: pas-une-liste
""",
    )
    _track(tmp_path, contract_path, second_contract)

    inventory = inventory_module.build_inventory(tmp_path)
    first = inventory["manuals"]["1SPE"]["chapters"]["1SPE-CAPACITES"]
    second = inventory["manuals"]["1SPE"]["chapters"]["1SPE-CAPACITES-NON-LISTE"]

    assert first["counts"]["capacites"] == 1
    assert [capacity["ref_capacite"] for capacity in first["capacities"]] == [
        "1SPE-CAPACITES-C1"
    ]
    assert second["counts"]["capacites"] == 0
    assert inventory["anomalies"]["invalid_capacities"] == [
        {
            "index": None,
            "path": second_contract,
            "reason": "capacites doit etre une liste",
        },
        {
            "index": 1,
            "path": contract_path,
            "reason": "capacite doit etre un objet",
        },
        {
            "index": 2,
            "path": contract_path,
            "reason": "ref_capacite doit etre un texte non vide",
        },
        {
            "index": 3,
            "path": contract_path,
            "reason": "ref_capacite doit etre un texte non vide",
        },
    ]


def test_path_meta_and_contract_context_mismatches_are_explicit(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-CONTEXTE")
    contract_path = f"{base}/contrat.yaml"
    object_path = f"{base}/cours/c1.tex"
    _write(
        tmp_path / contract_path,
        _contract("1SPE-AUTRE", "TSPE", capacities=1),
    )
    _write(
        tmp_path / object_path,
        _meta(
            id="1SPE-CONTEXTE-COURS-C1",
            chapitre="1SPE-META-AUTRE",
            status="approved",
        ),
    )
    _track(tmp_path, contract_path, object_path)

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["anomalies"]["context_mismatches"] == [
        {
            "actual": "1SPE-AUTRE",
            "expected": "1SPE-CONTEXTE",
            "field": "chapitre",
            "path": contract_path,
            "scope": "contract",
        },
        {
            "actual": "TSPE",
            "expected": "1SPE",
            "field": "niveau",
            "path": contract_path,
            "scope": "contract",
        },
        {
            "actual": "1SPE-META-AUTRE",
            "expected": "1SPE-CONTEXTE",
            "field": "chapitre",
            "path": object_path,
            "scope": "object",
        },
    ]


def test_duplicate_capacity_references_are_detected_across_chapters(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    first_chapter = "1SPE-PREMIER"
    second_chapter = "1SPE-SECOND"
    first = f"{_chapter_path('1SPE', first_chapter)}/contrat.yaml"
    second = f"{_chapter_path('1SPE', second_chapter)}/contrat.yaml"
    shared_reference = "1SPE-CAPACITE-PARTAGEE"
    _write(
        tmp_path / first,
        _contract(first_chapter, "1SPE", capacities=1).replace(
            f"{first_chapter}-C1", shared_reference
        ),
    )
    _write(
        tmp_path / second,
        _contract(second_chapter, "1SPE", capacities=1).replace(
            f"{second_chapter}-C1", shared_reference
        ),
    )
    _track(tmp_path, first, second)

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["anomalies"]["duplicate_capacity_refs"] == [
        {
            "occurrences": [
                {
                    "chapter": first_chapter,
                    "index": 0,
                    "manual": "1SPE",
                    "path": first,
                },
                {
                    "chapter": second_chapter,
                    "index": 0,
                    "manual": "1SPE",
                    "path": second,
                },
            ],
            "ref_capacite": shared_reference,
        }
    ]


def test_unknown_chapter_prefix_is_never_silently_ignored(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = "NSI/chapitres/INCONNU-TEST"
    sources = {
        f"{base}/contrat.yaml": _contract("INCONNU-TEST", "INCONNU", capacities=1),
        f"{base}/cours/c1.tex": _meta(
            id="INCONNU-TEST-C1", chapitre="INCONNU-TEST", status="approved"
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["anomalies"]["unknown_chapter_prefixes"] == [
        {
            "chapter": "INCONNU-TEST",
            "path": f"{base}/contrat.yaml",
            "reason": "prefixe de chapitre sans manuel canonique",
        },
        {
            "chapter": "INCONNU-TEST",
            "path": f"{base}/cours/c1.tex",
            "reason": "prefixe de chapitre sans manuel canonique",
        },
    ]
    assert all(not manual["chapters"] for manual in inventory["manuals"].values())


def test_source_digest_uses_only_tracked_relevant_sources(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    contract = f"{base}/contrat.yaml"
    course = f"{base}/cours/c1.tex"
    readme = "README.md"
    _write(tmp_path / contract, _contract("1SPE-TEST", "1SPE", capacities=1))
    _write(tmp_path / course, _meta())
    _write(tmp_path / readme, "Documentation sans effet sur le contenu\n")
    _track(tmp_path, contract, course, readme)

    first = inventory_module.build_inventory(tmp_path)["source_digest"]
    _write(tmp_path / f"{base}/cours/untracked.tex", _meta(id="UNTRACKED"))
    assert inventory_module.build_inventory(tmp_path)["source_digest"] == first

    _write(tmp_path / readme, "Documentation modifiee\n")
    assert inventory_module.build_inventory(tmp_path)["source_digest"] == first

    _write(tmp_path / course, _meta(status="approved"))
    assert inventory_module.build_inventory(tmp_path)["source_digest"] != first


def test_reference_graph_reports_missing_correction_and_broken_meta_and_latex_targets(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    contract = f"{base}/contrat.yaml"
    exercise = f"{base}/exercices/1SPE-TEST-EX-001.tex"
    course = f"{base}/cours/10_cours.tex"
    missing_correction = "chapitres/1SPE-TEST/corriges/1SPE-TEST-CO-001.tex"
    missing_source = "corpus/source-absente.md"
    missing_input = "chapitres/1SPE-TEST/cours/fragment-absent.tex"
    _write(tmp_path / contract, _contract("1SPE-TEST", "1SPE", capacities=1))
    _write(
        tmp_path / exercise,
        _meta(
            id="1SPE-TEST-EX-001",
            type_objet="exercice",
            fichier_tex="chapitres/1SPE-TEST/exercices/1SPE-TEST-EX-001.tex",
            corrige_tex=missing_correction,
            sources_inspiration=[missing_source],
        ),
    )
    _write(
        tmp_path / course,
        _meta(id="1SPE-TEST-COURS-C1", status="approved")
        + f"\\input{{{missing_input.removesuffix('.tex')}}}\n",
    )
    _track(tmp_path, contract, exercise, course)

    inventory = inventory_module.build_inventory(tmp_path)
    anomalies = inventory["anomalies"]

    assert {
        (item["source"], item["cible"], item["champ"], item["raison"])
        for item in anomalies["broken_meta_references"]
    } == {
        (
            exercise,
            f"Mathematiques/manuel-maths/{missing_correction}",
            "corrige_tex",
            "chemin META absent des sources suivies",
        ),
    }
    assert anomalies["unavailable_inspiration_sources"] == [
        {
            "source": exercise,
            "cible": f"Mathematiques/manuel-maths/{missing_source}",
            "champ": "sources_inspiration[0]",
            "raison": "source d'inspiration absente des sources suivies",
        }
    ]
    assert anomalies["broken_latex_references"] == [
        {
            "champ": "input",
            "cible": f"Mathematiques/manuel-maths/{missing_input}",
            "raison": "cible LaTeX absente des sources suivies",
            "source": course,
        }
    ]
    assert anomalies["missing_corrections"] == [
        {
            "champ": "corrige_tex",
            "cible": f"Mathematiques/manuel-maths/{missing_correction}",
            "raison": "aucun corrige suivi ne resout cet exercice",
            "source": exercise,
        }
    ]
    assert any(
        edge["source"] == exercise
        and edge["champ"] == "fichier_tex"
        and edge["resolved"] is True
        for edge in inventory["reference_graph"]
    )


def test_reverse_and_conventional_correction_links_prevent_false_missing_reports(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1NSI", "1NSI-TEST")
    sources = {
        f"{base}/contrat.yaml": _contract("1NSI-TEST", "1NSI", capacities=1),
        f"{base}/exercices/1NSI-TEST-EX-001.tex": _meta(
            id="1NSI-TEST-EX-001",
            chapitre="1NSI-TEST",
            type_objet="exercice",
            status="approved",
        ),
        f"{base}/corriges/1NSI-TEST-CO-001.tex": _meta(
            id="1NSI-TEST-CO-001",
            chapitre="1NSI-TEST",
            type_objet="corrige",
            status="approved",
        ),
        f"{base}/exercices/1NSI-TEST-EX-002.tex": _meta(
            id="1NSI-TEST-EX-002",
            chapitre="1NSI-TEST",
            type_objet="exercice",
            status="approved",
        ),
        f"{base}/corriges/correction-libre.tex": _meta(
            id="CORRECTION-LIBRE",
            chapitre="1NSI-TEST",
            type_objet="corrige",
            exercice_ref="1NSI-TEST-EX-002",
            status="approved",
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["anomalies"]["missing_corrections"] == []
    assert {
        (link["exercise_id"], link["correction_id"], link["mode"])
        for link in inventory["correction_links"]
    } == {
        ("1NSI-TEST-EX-001", "1NSI-TEST-CO-001", "id_convention"),
        ("1NSI-TEST-EX-002", "CORRECTION-LIBRE", "reverse_meta"),
    }


def test_meta_capacity_references_resolve_local_codes_and_report_unknown_ids(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    contract = f"{base}/contrat.yaml"
    course = f"{base}/cours/10_cours.tex"
    _write(tmp_path / contract, _contract("1SPE-TEST", "1SPE", capacities=1))
    _write(
        tmp_path / course,
        _meta(
            id="1SPE-TEST-COURS-C1",
            status="approved",
            capacites=["C1", "1SPE-TEST-C9"],
        ),
    )
    _track(tmp_path, contract, course)

    inventory = inventory_module.build_inventory(tmp_path)

    edges = [
        item for item in inventory["reference_graph"] if item["kind"] == "capacity"
    ]
    assert edges == [
        {
            "champ": "capacites[0]",
            "cible": "1SPE-TEST-C1",
            "kind": "capacity",
            "resolved": True,
            "source": course,
        },
        {
            "champ": "capacites[1]",
            "cible": "1SPE-TEST-C9",
            "kind": "capacity",
            "resolved": False,
            "source": course,
        },
    ]
    assert inventory["anomalies"]["broken_meta_references"] == [
        {
            "champ": "capacites[1]",
            "cible": "1SPE-TEST-C9",
            "raison": "capacite META absente du contrat du chapitre",
            "source": course,
        }
    ]


def test_source_digest_includes_tracked_targets_reached_by_meta_graph(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1NSI", "1NSI-TEST")
    contract = f"{base}/contrat.yaml"
    course = f"{base}/cours/10_cours.tex"
    inspiration = "NSI/corpus/source.md"
    _write(tmp_path / contract, _contract("1NSI-TEST", "1NSI", capacities=1))
    _write(
        tmp_path / course,
        _meta(
            id="1NSI-TEST-COURS-C1",
            chapitre="1NSI-TEST",
            status="approved",
            sources_inspiration=["corpus/source.md"],
        ),
    )
    _write(tmp_path / inspiration, "version une\n")
    _track(tmp_path, contract, course, inspiration)

    first = inventory_module.build_inventory(tmp_path)
    _write(tmp_path / inspiration, "version deux\n")
    second = inventory_module.build_inventory(tmp_path)

    assert inspiration in first["source_files"]
    assert first["source_digest"] != second["source_digest"]


def test_analyze_assembler_reads_constants_and_variants_without_execution(
    tmp_path: Path, inventory_module
) -> None:
    assembler = tmp_path / "assemble.py"
    _write(
        assembler,
        """raise RuntimeError("ce module ne doit jamais etre execute")
ORDER = [("cours", "1*"), ("exercices", "*")]
CHAPITRES = ["1SPE-TEST", "1SPE-AUTRE"]
VARIANTES = ["complet", "methodes"]
ELEVE_EXCLUDES = {"corriges", "evaluations"}
parser.add_argument("--variant", choices=["eleve", "professeur"])
""",
    )

    analysis = inventory_module.analyze_assembler(assembler)

    assert analysis["constants"] == {
        "CHAPITRES": ["1SPE-TEST", "1SPE-AUTRE"],
        "ELEVE_EXCLUDES": ["corriges", "evaluations"],
        "ORDER": [["cours", "1*"], ["exercices", "*"]],
        "VARIANTES": ["complet", "methodes"],
    }
    assert analysis["variants"] == [
        "complet",
        "eleve",
        "methodes",
        "professeur",
    ]


def test_assemblies_follow_ast_globs_and_expose_duplicates_exclusions_and_orphans(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    chapter_assembler = "Mathematiques/manuel-maths/scripts/assemble.py"
    manual_assembler = "Mathematiques/manuel-maths/scripts/assemble_manuel.py"
    sources = {
        f"{base}/contrat.yaml": _contract("1SPE-TEST", "1SPE", capacities=1),
        f"{base}/cours/10_cours.tex": _meta(id="1SPE-TEST-COURS-C1", status="approved"),
        f"{base}/exercices/1SPE-TEST-EX-001.tex": _meta(
            id="1SPE-TEST-EX-001", type_objet="exercice", status="approved"
        ),
        f"{base}/corriges/1SPE-TEST-CO-001.tex": _meta(
            id="1SPE-TEST-CO-001",
            type_objet="corrige",
            exercice_id="1SPE-TEST-EX-001",
            status="approved",
        ),
        chapter_assembler: """ORDER = [("cours", "*"), ("cours", "1*"), ("exercices", "*")]
VARIANTS = ["complet"]
""",
        manual_assembler: """CHAPITRES = ["1SPE-TEST"]
ORDER = [("cours", "1*"), ("exercices", "*")]
VARIANTS = ["professeur", "eleve"]
ELEVE_EXCLUDES = {"evaluations", "corriges"}
""",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    assemblies = {item["assembly_id"]: item for item in inventory["assemblies"]}
    chapter = assemblies["math:chapter:1SPE-TEST:complet"]
    professor = assemblies["math:manual:1SPE:professeur"]

    assert chapter["included_objects"] == [
        f"{base}/cours/10_cours.tex",
        f"{base}/exercices/1SPE-TEST-EX-001.tex",
    ]
    assert chapter["excluded_source_types"] == ["corrige"]
    assert professor["chapters"] == ["1SPE-TEST"]
    assert inventory["anomalies"]["duplicate_assembly_objects"] == [
        {
            "champ": "math:chapter:1SPE-TEST:complet",
            "cible": f"{base}/cours/10_cours.tex",
            "raison": "2 regles de glob selectionnent le meme objet; l'assembleur le deduplique",
            "source": chapter_assembler,
        }
    ]
    assert inventory["anomalies"]["unassembled_objects"] == [
        {
            "champ": "assemblages_declares",
            "cible": f"{base}/corriges/1SPE-TEST-CO-001.tex",
            "raison": "objet META exclu de tous les assemblages declares",
            "source": f"{base}/corriges/1SPE-TEST-CO-001.tex",
        }
    ]
    manual_model = inventory["manuals"]["1SPE"]
    chapter_model = manual_model["chapters"]["1SPE-TEST"]
    assert manual_model["declared_variants"] == {
        "chapter": ["complet"],
        "manual": ["eleve", "professeur"],
        "static": [],
    }
    assert chapter_model["declared_variants"] == manual_model["declared_variants"]


def test_manual_assembler_gaps_and_chapters_outside_manual_are_explicit(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapters = (
        ("TSPE", "TSPE-TEST", "TSPE"),
        ("1NSI", "1NSI-TEST", "1NSI"),
        ("TNSI", "TNSI-TEST", "TNSI"),
    )
    sources: dict[str, str] = {}
    for manual, chapter, level in chapters:
        base = _chapter_path(manual, chapter)
        sources[f"{base}/contrat.yaml"] = _contract(chapter, level, capacities=1)
        sources[f"{base}/cours/10_cours.tex"] = _meta(
            id=f"{chapter}-COURS-C1",
            chapitre=chapter,
            status="approved",
        )
    sources["Mathematiques/manuel-maths/scripts/assemble.py"] = (
        'ORDER = [("cours", "1*")]\nVARIANTS = ["complet"]\n'
    )
    sources["NSI/scripts/assemble.py"] = (
        'ORDER = [("cours", "1*")]\nVARIANTS = ["complet"]\n'
    )
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    gaps = inventory["anomalies"]["missing_assemblers"]

    assert {
        (item["cible"], item["champ"], item["raison"])
        for item in gaps
        if item["champ"] == "manuel"
    } == {
        ("1NSI", "manuel", "aucun assembleur de manuel suivi"),
        ("1SPE", "manuel", "aucun assembleur de manuel suivi"),
        ("TNSI", "manuel", "aucun assembleur de manuel suivi"),
        ("TSPE_2026_2027", "manuel", "aucun assembleur de manuel suivi"),
    }
    assert {
        item["cible"] for item in inventory["anomalies"]["chapters_not_in_manual"]
    } == {"1NSI-TEST", "TNSI-TEST", "TSPE-TEST"}


def test_pdf_inventory_uses_only_tracked_files_and_reports_unavailable_page_count(
    tmp_path: Path, inventory_module, monkeypatch: pytest.MonkeyPatch
) -> None:
    _init_repository(tmp_path)
    tracked_pdf = "Mathematiques/manuel-maths/build/tracked.pdf"
    untracked_pdf = "NSI/build/untracked.pdf"
    _write(tmp_path / tracked_pdf, "pas un vrai pdf")
    _write(tmp_path / untracked_pdf, "pas un vrai pdf")
    _track(tmp_path, tracked_pdf)
    monkeypatch.setattr(
        inventory_module,
        "_page_count_with_pdfinfo",
        lambda _path: (None, "pdfinfo indisponible"),
    )
    monkeypatch.setattr(
        inventory_module,
        "_page_count_with_python",
        lambda _path: (None, "lecteur PDF Python indisponible"),
    )

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["pdfs"] == [
        {
            "chapter": None,
            "manual": None,
            "page_count": None,
            "page_count_method": None,
            "path": tracked_pdf,
            "reason": ("pdfinfo indisponible; lecteur PDF Python indisponible"),
            "scope": None,
            "status": "page_count_unavailable",
            "variant": None,
        }
    ]
    assert inventory["anomalies"]["unattributed_pdfs"] == [
        {
            "champ": "attribution",
            "cible": tracked_pdf,
            "raison": "PDF suivi sans attribution fiable a un livrable",
            "source": tracked_pdf,
        }
    ]


def test_pdf_inventory_prefers_pdfinfo_page_count(
    tmp_path: Path, inventory_module, monkeypatch: pytest.MonkeyPatch
) -> None:
    _init_repository(tmp_path)
    tracked_pdf = "NSI/build/MANUEL_1NSI_eleve.pdf"
    _write(tmp_path / tracked_pdf, "contenu simule")
    _track(tmp_path, tracked_pdf)
    monkeypatch.setattr(
        inventory_module,
        "_page_count_with_pdfinfo",
        lambda _path: (27, None),
    )

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["pdfs"] == [
        {
            "chapter": None,
            "manual": "1NSI",
            "page_count": 27,
            "page_count_method": "pdfinfo",
            "path": tracked_pdf,
            "reason": None,
            "scope": "manual",
            "status": "counted",
            "variant": "eleve",
        }
    ]


def test_missing_tracked_pdf_has_deterministic_checkout_status(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    tracked_pdf = "NSI/build/deleted.pdf"
    _write(tmp_path / tracked_pdf, "contenu indexe puis supprime")
    _track(tmp_path, tracked_pdf)
    (tmp_path / tracked_pdf).unlink()

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["pdfs"] == [
        {
            "chapter": None,
            "manual": None,
            "page_count": None,
            "page_count_method": None,
            "path": tracked_pdf,
            "reason": "fichier PDF suivi absent du checkout",
            "scope": None,
            "status": "page_count_unavailable",
            "variant": None,
        }
    ]


def test_recursive_static_latex_assembly_counts_duplicates_and_assembles_correction(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    exercise = f"{base}/exercices/1SPE-TEST-EX-001.tex"
    correction = f"{base}/corriges/1SPE-TEST-CO-001.tex"
    root_tex = "Mathematiques/manuel-maths/build/maquette-v5/maquette.tex"
    section = "Mathematiques/manuel-maths/parts/section.tex"
    template = "Mathematiques/manuel-maths/gabarits/chapitre_master.tex"
    orphan = "Mathematiques/manuel-maths/extras/perdu.tex"
    sources = {
        f"{base}/contrat.yaml": _contract("1SPE-TEST", "1SPE", capacities=1),
        exercise: _meta(
            id="1SPE-TEST-EX-001", type_objet="exercice", status="approved"
        ),
        correction: _meta(
            id="1SPE-TEST-CO-001",
            type_objet="corrige",
            exercice_id="1SPE-TEST-EX-001",
            status="approved",
        ),
        root_tex: """\\documentclass{article}
\\begin{document}
\\input{parts/section}
\\input{parts/section}
\\end{document}
""",
        section: """\\input{chapitres/1SPE-TEST/exercices/1SPE-TEST-EX-001}
\\input{chapitres/1SPE-TEST/corriges/1SPE-TEST-CO-001}
""",
        template: "%%CONTENT%%\n",
        orphan: "Texte non reference sans META\n",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    first = inventory_module.build_inventory(tmp_path)
    first_digest = first["source_digest"]
    assemblies = {item["assembly_id"]: item for item in first["assemblies"]}
    static_id = f"math:static:{root_tex}"

    assert assemblies[static_id]["included_objects"] == [exercise, correction]
    assert first["manuals"]["1SPE"]["declared_variants"]["static"] == ["maquette-v5"]
    assert first["manuals"]["1SPE"]["chapters"]["1SPE-TEST"]["declared_variants"][
        "static"
    ] == ["maquette-v5"]
    assert first["anomalies"]["unassembled_objects"] == []
    assert {
        (item["champ"], item["cible"])
        for item in first["anomalies"]["duplicate_assembly_objects"]
    } == {(static_id, exercise), (static_id, correction)}
    assert first["anomalies"]["orphan_files"] == [
        {
            "champ": "reachability",
            "cible": orphan,
            "raison": "fichier LaTeX suivi sans META, non reference et hors assemblage",
            "role": "latex_source",
            "source": orphan,
        }
    ]
    assert template not in {
        item["cible"] for item in first["anomalies"]["orphan_files"]
    }
    assert root_tex in first["source_files"]
    assert section in first["source_files"]

    _write(tmp_path / section, sources[section] + "% modification suivie\n")
    assert inventory_module.build_inventory(tmp_path)["source_digest"] != first_digest


def test_all_relevant_tracked_tex_sources_are_scanned_for_broken_inputs(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    master = "NSI/gabarits/master.tex"
    _write(tmp_path / master, "\\input{transversal/absent}\n")
    _track(tmp_path, master)

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["anomalies"]["broken_latex_references"] == [
        {
            "champ": "input",
            "cible": "NSI/transversal/absent.tex",
            "raison": "cible LaTeX absente des sources suivies",
            "source": master,
        }
    ]
    assert master in inventory["source_files"]


def test_orphan_reachability_ignores_edges_from_unreachable_sources_and_cycles(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    first = "NSI/extras/cycle-a.tex"
    second = "NSI/extras/cycle-b.tex"
    leaf = "NSI/extras/leaf.tex"
    sources = {
        first: "\\input{extras/cycle-b}\n",
        second: "\\input{extras/cycle-a}\n",
        leaf: "Contenu sans racine\n",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    orphans = {item["cible"] for item in inventory["anomalies"]["orphan_files"]}

    assert orphans == {first, second, leaf}


def test_latex_reference_uses_source_relative_target_when_it_is_tracked(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    master = "Mathematiques/manuel-maths/gabarits/reference/main.tex"
    part = "Mathematiques/manuel-maths/gabarits/reference/chapters/part.tex"
    _write(tmp_path / master, "\\documentclass{article}\n\\input{chapters/part}\n")
    _write(tmp_path / part, "Partie suivie\n")
    _track(tmp_path, master, part)

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["anomalies"]["broken_latex_references"] == []
    assert any(
        edge["source"] == master and edge["cible"] == part and edge["resolved"] is True
        for edge in inventory["reference_graph"]
    )


def test_missing_declared_manual_chapter_is_broken_and_never_covered(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    assembler = "Mathematiques/manuel-maths/scripts/assemble_manuel.py"
    sources = {
        f"{base}/contrat.yaml": _contract(chapter, "1SPE", capacities=1),
        f"{base}/cours/10_cours.tex": _meta(id="1SPE-TEST-COURS-C1", status="approved"),
        assembler: """CHAPITRES = ["1SPE-TEST", "1SPE-ABSENT", "INCONNU-CHAP"]
ORDER = [("cours", "1*")]
VARIANTS = ["professeur"]
""",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    manual = next(
        item
        for item in inventory["assemblies"]
        if item["assembly_id"] == "math:manual:1SPE:professeur"
    )

    assert manual["chapters"] == ["1SPE-TEST"]
    assert inventory["anomalies"]["broken_assembly_references"] == [
        {
            "champ": "CHAPITRES[1]",
            "cible": "1SPE-ABSENT",
            "raison": "chapitre declare par l'assembleur absent des sources suivies",
            "source": assembler,
        },
        {
            "champ": "CHAPITRES[2]",
            "cible": "INCONNU-CHAP",
            "raison": "prefixe de chapitre inconnu dans CHAPITRES",
            "source": assembler,
        },
    ]


def test_exercise_glob_order_places_all_hints_after_primary_exercises(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    base = _chapter_path("1SPE", "1SPE-TEST")
    assembler = "Mathematiques/manuel-maths/scripts/assemble.py"
    paths = [
        f"{base}/exercices/1SPE-TEST-EX-001.tex",
        f"{base}/exercices/1SPE-TEST-EX-001-CDP.tex",
        f"{base}/exercices/1SPE-TEST-EX-002.tex",
        f"{base}/exercices/1SPE-TEST-EX-002-CDP.tex",
    ]
    sources = {
        f"{base}/contrat.yaml": _contract("1SPE-TEST", "1SPE", capacities=1),
        paths[0]: _meta(id="EX-1", type_objet="exercice", status="approved"),
        paths[1]: _meta(id="CDP-1", type_objet="coup_de_pouce", status="approved"),
        paths[2]: _meta(id="EX-2", type_objet="exercice", status="approved"),
        paths[3]: _meta(id="CDP-2", type_objet="coup_de_pouce", status="approved"),
        assembler: 'ORDER = [("exercices", "*")]\nVARIANTS = ["complet"]\n',
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    assembly = next(
        item
        for item in inventory["assemblies"]
        if item["assembly_id"] == "math:chapter:1SPE-TEST:complet"
    )

    assert assembly["included_objects"] == [paths[0], paths[2], paths[1], paths[3]]


def test_pdf_page_count_falls_back_to_python_reader(
    tmp_path: Path, inventory_module, monkeypatch: pytest.MonkeyPatch
) -> None:
    _init_repository(tmp_path)
    pdf = "Mathematiques/manuel-maths/build/MANUEL_1SPE_professeur.pdf"
    _write(tmp_path / pdf, "contenu simule")
    _track(tmp_path, pdf)
    monkeypatch.setattr(
        inventory_module,
        "_page_count_with_pdfinfo",
        lambda _path: (None, "pdfinfo indisponible"),
    )
    monkeypatch.setattr(
        inventory_module,
        "_page_count_with_python",
        lambda _path: (19, None),
    )

    artifact = inventory_module.build_inventory(tmp_path)["pdfs"][0]

    assert artifact["page_count"] == 19
    assert artifact["page_count_method"] == "python"
    assert artifact["manual"] == "1SPE"
    assert artifact["scope"] == "manual"
    assert artifact["variant"] == "professeur"


def test_chapter_pdf_attribution_aggregates_pages_and_variants(
    tmp_path: Path, inventory_module, monkeypatch: pytest.MonkeyPatch
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    pdf = "Mathematiques/manuel-maths/build/1SPE-TEST/" "1SPE-TEST_methodes.pdf"
    sources = {
        f"{base}/contrat.yaml": _contract(chapter, "1SPE", capacities=1),
        f"{base}/cours/10_cours.tex": _meta(id="1SPE-TEST-COURS-C1", status="approved"),
        pdf: "contenu simule",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)
    monkeypatch.setattr(
        inventory_module,
        "_page_count_with_pdfinfo",
        lambda _path: (8, None),
    )

    inventory = inventory_module.build_inventory(tmp_path)
    artifact = inventory["pdfs"][0]
    manual = inventory["manuals"]["1SPE"]
    chapter_model = manual["chapters"][chapter]

    assert artifact["manual"] == "1SPE"
    assert artifact["chapter"] == chapter
    assert artifact["scope"] == "chapter"
    assert artifact["variant"] == "methodes"
    expected_compiled = {
        "chapter": ["methodes"],
        "manual": [],
        "static": [],
    }
    assert manual["compiled_variants"] == expected_compiled
    assert chapter_model["compiled_variants"] == expected_compiled
    assert manual["compiled_artifacts"] == [artifact]
    assert chapter_model["compiled_artifacts"] == [artifact]
    assert "compiled_pages" not in manual
    assert "compiled_pages" not in chapter_model
    assert "variants" not in manual
    assert "variants" not in chapter_model


def test_meta_graph_resolves_capacity_prerequisite_method_and_hint_families(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    contract = f"{base}/contrat.yaml"
    method_one = f"{base}/methodes/1SPE-TEST-ME-001.tex"
    method_two = f"{base}/methodes/1SPE-TEST-ME-002.tex"
    hint = f"{base}/exercices/1SPE-TEST-EX-001-CDP.tex"
    exercise = f"{base}/exercices/1SPE-TEST-EX-001.tex"
    _write(
        tmp_path / contract,
        _contract(chapter, "1SPE", capacities=1)
        + "prerequis:\n  - {code: R1, libelle: Prerequis}\n",
    )
    sources = {
        method_one: _meta(
            id="1SPE-TEST-ME-001", type_objet="methode", status="approved"
        ),
        method_two: _meta(
            id="1SPE-TEST-ME-002", type_objet="methode", status="approved"
        ),
        hint: _meta(
            id="1SPE-TEST-EX-001-CDP",
            type_objet="coup_de_pouce",
            status="approved",
        ),
        exercise: _meta(
            id="1SPE-TEST-EX-001",
            type_objet="exercice",
            status="approved",
            capacites_codes=["C1", "R1"],
            methodes=["M1", "1SPE-TEST-ME-002"],
            coups_de_pouce=[
                "1SPE-TEST-EX-001-CDP",
                "chapitres/1SPE-TEST/exercices/1SPE-TEST-EX-001-CDP.tex",
            ],
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, contract, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    edges = {
        (edge["champ"], edge["cible"], edge["kind"], edge["resolved"])
        for edge in inventory["reference_graph"]
        if edge["source"] == exercise
    }

    assert ("capacites_codes[0]", "1SPE-TEST-C1", "capacity", True) in edges
    assert (
        "capacites_codes[1]",
        "1SPE-TEST:prerequis:R1",
        "prerequisite",
        True,
    ) in edges
    assert ("methodes[0]", "1SPE-TEST-ME-001", "method", True) in edges
    assert ("methodes[1]", "1SPE-TEST-ME-002", "method", True) in edges
    assert ("coups_de_pouce[0]", "1SPE-TEST-EX-001-CDP", "hint_id", True) in edges
    assert ("coups_de_pouce[1]", hint, "hint_path", True) in edges


def test_meta_graph_reports_unknown_and_invalid_reference_forms_by_family(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    contract = f"{base}/contrat.yaml"
    exercise = f"{base}/exercices/1SPE-TEST-EX-001.tex"
    _write(tmp_path / contract, _contract(chapter, "1SPE", capacities=1))
    _write(
        tmp_path / exercise,
        _meta(
            id="1SPE-TEST-EX-001",
            type_objet="exercice",
            status="approved",
            capacites_codes=["C9", 9],
            methodes=["M9", {"invalide": True}],
            coups_de_pouce=["CDP-INCONNU", False],
        ),
    )
    _track(tmp_path, contract, exercise)

    inventory = inventory_module.build_inventory(tmp_path)

    broken_fields = {
        item["champ"] for item in inventory["anomalies"]["broken_meta_references"]
    }
    invalid_fields = {
        item["champ"] for item in inventory["anomalies"]["invalid_meta_references"]
    }
    assert {"capacites_codes[0]", "methodes[0]", "coups_de_pouce[0]"} <= broken_fields
    assert {"capacites_codes[1]", "methodes[1]", "coups_de_pouce[1]"} <= invalid_fields


def test_method_aliases_use_meta_then_verified_id_suffix_without_positional_fallback(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    contract = f"{base}/contrat.yaml"
    method_one = f"{base}/methodes/1SPE-TEST-ME-001.tex"
    method_three = f"{base}/methodes/1SPE-TEST-ME-003.tex"
    explicit = f"{base}/methodes/methode-explicite.tex"
    exercise = f"{base}/exercices/1SPE-TEST-EX-001.tex"
    sources = {
        contract: _contract(chapter, "1SPE", capacities=1),
        method_one: _meta(
            id="1SPE-TEST-ME-001", type_objet="methode", status="approved"
        ),
        method_three: _meta(
            id="1SPE-TEST-ME-003", type_objet="methode", status="approved"
        ),
        explicit: _meta(
            id="1SPE-TEST-METHODE-ALPHA",
            type_objet="methode",
            methodes=["M7"],
            status="approved",
        ),
        exercise: _meta(
            id="1SPE-TEST-EX-001",
            type_objet="exercice",
            methodes=["M2", "M3", "M7"],
            status="approved",
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    edges = {
        (edge["champ"], edge["cible"], edge["resolved"])
        for edge in inventory["reference_graph"]
        if edge["source"] == exercise
    }

    assert ("methodes[0]", "M2", False) in edges
    assert ("methodes[1]", "1SPE-TEST-ME-003", True) in edges
    assert ("methodes[2]", "1SPE-TEST-METHODE-ALPHA", True) in edges


def test_missing_and_duplicate_method_aliases_are_reported(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    sources = {
        f"{base}/contrat.yaml": _contract(chapter, "1SPE", capacities=1),
        f"{base}/methodes/sans-alias.tex": _meta(
            id="1SPE-TEST-METHODE-SANS-ALIAS",
            type_objet="methode",
            status="approved",
        ),
        f"{base}/methodes/doublon-a.tex": _meta(
            id="1SPE-TEST-METHODE-A",
            type_objet="methode",
            methodes=["M4"],
            status="approved",
        ),
        f"{base}/methodes/doublon-b.tex": _meta(
            id="1SPE-TEST-METHODE-B",
            type_objet="methode",
            methodes=["M4"],
            status="approved",
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    issues = inventory["anomalies"]["broken_meta_references"]

    assert any(
        item["source"].endswith("sans-alias.tex")
        and "alias de methode absent" in item["raison"]
        for item in issues
    )
    assert (
        sum("alias de methode ambigu ou duplique" in item["raison"] for item in issues)
        >= 2
    )


def test_physical_chapter_drives_assembly_even_when_meta_chapter_mismatches(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    physical = "1SPE-PHYSIQUE"
    base = _chapter_path("1SPE", physical)
    course = f"{base}/cours/10_cours.tex"
    assembler = "Mathematiques/manuel-maths/scripts/assemble.py"
    sources = {
        f"{base}/contrat.yaml": _contract(physical, "1SPE", capacities=1),
        course: _meta(
            id="OBJ-MISMATCH",
            chapitre="1SPE-META-AUTRE",
            status="approved",
        ),
        assembler: 'ORDER = [("cours", "1*")]\nVARIANTS = ["complet"]\n',
        "Mathematiques/manuel-maths/gabarits/chapitre_master.tex": "%%CONTENT%%\n",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    item = inventory["manuals"]["1SPE"]["chapters"][physical]["objects"][0]
    assembly = next(
        value
        for value in inventory["assemblies"]
        if value["assembly_id"] == f"math:chapter:{physical}:complet"
    )

    assert item["path_chapter"] == physical
    assert assembly["included_objects"] == [course]
    assert inventory["anomalies"]["context_mismatches"]


def test_assembler_choices_name_is_resolved_and_invalid_declarations_do_not_cover(
    tmp_path: Path, inventory_module
) -> None:
    valid = tmp_path / "valid.py"
    _write(
        valid,
        """ORDER = [("cours", "*")]
VARIANTS = ["complet", "methodes"]
parser.add_argument("--variant", choices=VARIANTS)
""",
    )
    assert inventory_module.analyze_assembler(valid)["variants"] == [
        "complet",
        "methodes",
    ]

    repository = tmp_path / "repo"
    _init_repository(repository)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    assembler = "Mathematiques/manuel-maths/scripts/assemble.py"
    sources = {
        f"{base}/contrat.yaml": _contract(chapter, "1SPE", capacities=1),
        f"{base}/cours/10_cours.tex": _meta(status="approved"),
        assembler: 'ORDER = "invalide"\nVARIANTS = []\n',
    }
    for path, content in sources.items():
        _write(repository / path, content)
    _track(repository, *sources)

    inventory = inventory_module.build_inventory(repository)

    assert inventory["assemblies"] == []
    assert any(
        item["source"] == assembler
        for item in inventory["anomalies"]["assembler_invalid"]
    )
    assert any(
        item["cible"] == "1SPE" and item["champ"] == "chapitre"
        for item in inventory["anomalies"]["missing_assemblers"]
    )


def test_dynamic_assembler_dependencies_are_included_and_missing_ones_are_broken(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    chapter_assembler = "Mathematiques/manuel-maths/scripts/assemble.py"
    manual_assembler = "Mathematiques/manuel-maths/scripts/assemble_manuel.py"
    master = "Mathematiques/manuel-maths/gabarits/chapitre_master.tex"
    transversal = "Mathematiques/manuel-maths/transversal/page_de_garde.tex"
    contract = f"{base}/contrat.yaml"
    sources = {
        contract: _contract(chapter, "1SPE", capacities=1),
        f"{base}/cours/10_cours.tex": _meta(status="approved"),
        master: "%%CONTENT%%\n",
        transversal: "Page de garde\n",
        chapter_assembler: 'ORDER = [("cours", "1*")]\nVARIANTS = ["complet"]\n',
        manual_assembler: """CHAPITRES = ["1SPE-TEST"]
ORDER = [("cours", "1*")]
VARIANTS = ["professeur"]
parts.append("\\\\input{transversal/page_de_garde}")
""",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    assemblies = {item["assembly_id"]: item for item in inventory["assemblies"]}

    assert {master, contract} <= set(
        assemblies[f"math:chapter:{chapter}:complet"]["included_files"]
    )
    assert {transversal, contract} <= set(
        assemblies["math:manual:1SPE:professeur"]["included_files"]
    )
    assert not inventory["anomalies"]["broken_assembly_references"]

    (tmp_path / master).unlink()
    inventory = inventory_module.build_inventory(tmp_path)
    assert any(
        item["cible"] == master
        for item in inventory["anomalies"]["broken_assembly_references"]
    )


def test_fstring_documentclass_is_a_dynamic_assembly_dependency(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    assembler = "Mathematiques/manuel-maths/scripts/assemble_manuel.py"
    collection_class = "Mathematiques/manuel-maths/gabarits/nexus-manuel.cls"
    sources = {
        f"{base}/contrat.yaml": _contract(chapter, "1SPE", capacities=1),
        f"{base}/cours/10_cours.tex": _meta(status="approved"),
        collection_class: "\\NeedsTeXFormat{LaTeX2e}\n",
        assembler: '''CHAPITRES = ["1SPE-TEST"]
ORDER = [("cours", "1*")]
VARIANTS = ["professeur"]
master = f"""\\\\documentclass{{gabarits/nexus-manuel}}
\\\\begin{{document}}
{content}
\\\\end{{document}}
"""
''',
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    assembly = next(
        item
        for item in inventory["assemblies"]
        if item["assembly_id"] == "math:manual:1SPE:professeur"
    )

    assert collection_class in assembly["included_files"]
    assert not inventory["anomalies"]["broken_assembly_references"]

    (tmp_path / collection_class).unlink()
    inventory = inventory_module.build_inventory(tmp_path)
    assert any(
        item["cible"] == collection_class
        for item in inventory["anomalies"]["broken_assembly_references"]
    )


def test_generic_chapter_engine_exists_without_claiming_manual_coverage(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    assembler = "NSI/scripts/assemble.py"
    master = "NSI/gabarits/chapitre_master.tex"
    sources = {
        assembler: 'ORDER = [("cours", "*")]\nVARIANTS = ["complet"]\n',
        master: "%%CONTENT%%\n",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    missing = inventory["anomalies"]["missing_assemblers"]

    assert not any(
        item["cible"] == "TNSI" and item["champ"] == "chapitre" for item in missing
    )
    assert any(
        item["cible"] == "TNSI" and item["champ"] == "manuel" for item in missing
    )
    assert not any(
        item["manual"] == "TNSI" and item["scope"] == "chapter"
        for item in inventory["assemblies"]
    )


def test_duplicate_chapter_declaration_preserves_multiple_inclusion_and_reports_it(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    course = f"{base}/cours/10_cours.tex"
    assembler = "Mathematiques/manuel-maths/scripts/assemble_manuel.py"
    sources = {
        f"{base}/contrat.yaml": _contract(chapter, "1SPE", capacities=1),
        course: _meta(status="approved"),
        assembler: """CHAPITRES = ["1SPE-TEST", "1SPE-TEST"]
ORDER = [("cours", "1*")]
VARIANTS = ["professeur"]
""",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    assembly = next(
        item
        for item in inventory["assemblies"]
        if item["assembly_id"] == "math:manual:1SPE:professeur"
    )

    assert assembly["chapters"] == [chapter, chapter]
    assert assembly["included_objects"] == [course, course]
    assert any(
        item["cible"] == course and "chapitre duplique" in item["raison"]
        for item in inventory["anomalies"]["duplicate_assembly_objects"]
    )


def test_latex_comment_parser_preserves_escaped_percent(inventory_module) -> None:
    source = r"Texte 50\% puis \input{visible} % \input{ignore}"

    assert inventory_module._latex_inputs(source) == [("input", "visible")]


def test_static_latex_cycle_is_reported_and_deep_chain_is_iterative(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    project = "NSI"
    root_tex = f"{project}/build/root.tex"
    sources = {
        root_tex: "\\documentclass{article}\n\\input{chain/0000}\n",
    }
    depth = 1050
    for index in range(depth):
        current = f"{project}/chain/{index:04d}.tex"
        following = f"chain/{index + 1:04d}" if index + 1 < depth else "chain/0000"
        sources[current] = f"\\input{{{following}}}\n"
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)

    assert inventory["anomalies"]["latex_cycles"]
    assert any(
        item["champ"] == f"nsi:static:{root_tex}"
        for item in inventory["anomalies"]["latex_cycles"]
    )


def test_source_digest_distinguishes_empty_from_missing_tracked_file(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    source = "NSI/gabarits/empty.tex"
    _write(tmp_path / source, "")
    _track(tmp_path, source)

    present = inventory_module.build_inventory(tmp_path)["source_digest"]
    (tmp_path / source).unlink()
    missing = inventory_module.build_inventory(tmp_path)["source_digest"]

    assert present != missing


def test_pdfinfo_timeout_is_bounded_and_reported(
    tmp_path: Path, inventory_module, monkeypatch: pytest.MonkeyPatch
) -> None:
    pdf = tmp_path / "slow.pdf"
    _write(pdf, "contenu")

    def timeout_runner(*_args, **kwargs):
        assert kwargs["timeout"] == inventory_module.PDFINFO_TIMEOUT_SECONDS
        raise subprocess.TimeoutExpired("pdfinfo", kwargs["timeout"])

    monkeypatch.setattr(inventory_module.subprocess, "run", timeout_runner)

    assert inventory_module._page_count_with_pdfinfo(pdf) == (
        None,
        f"pdfinfo timeout ({inventory_module.PDFINFO_TIMEOUT_SECONDS}s)",
    )


def test_report_claims_reconcile_chapter_table_and_keep_unknown_pages_open(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    report = "Mathematiques/manuel-maths/RAPPORT_FINAL_1SPE.md"
    sources = {
        f"{base}/contrat.yaml": _contract(chapter, "1SPE", capacities=1),
        f"{base}/exercices/ex-1.tex": _meta(
            id="1SPE-TEST-EX-001", type_objet="exercice", status="approved"
        ),
        f"{base}/exercices/ex-2.tex": _meta(
            id="1SPE-TEST-EX-002", type_objet="exercice", status="approved"
        ),
        report: """# RAPPORT FINAL — Manuel de Mathematiques Premiere Specialite

### Chapitres (1)

| # | Chapitre | Exercices | Pages (chap) |
|---|---|---:|---:|
| 1 | Chapitre de test | 2 | 12 |
| | **Total** | **2** | **12** |
""",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    reconciliation = inventory["report_reconciliation"]
    claims = reconciliation["claims"]

    chapter_exercises = next(
        claim
        for claim in claims
        if claim["scope"] == "chapter:1SPE-TEST"
        and claim["metric"] == "exercices_principaux"
    )
    assert chapter_exercises == {
        "calculated": 2,
        "declared": 2,
        "evidence": "manuals.1SPE.chapters.1SPE-TEST.counts.exercices_principaux",
        "etat": "confirme",
        "line": 7,
        "metric": "exercices_principaux",
        "path": report,
        "raw": "| 1 | Chapitre de test | 2 | 12 |",
        "scope": "chapter:1SPE-TEST",
    }
    chapter_pages = next(
        claim
        for claim in claims
        if claim["scope"] == "chapter:1SPE-TEST"
        and claim["metric"] == "pages_compilees"
    )
    assert chapter_pages["declared"] == 12
    assert chapter_pages["calculated"] is None
    assert chapter_pages["etat"] == "ouvert"
    assert chapter_pages in reconciliation["claims_non_resolues"]
    assert reconciliation["summary"] == {
        "confirme": 3,
        "contredit": 0,
        "ouvert": 2,
    }


def test_report_claims_flag_numeric_and_completeness_contradictions(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1NSI-TEST"
    base = _chapter_path("1NSI", chapter)
    report = "NSI/DIRECTIVES_EN_COURS.md"
    sources = {
        f"{base}/contrat.yaml": _contract(chapter, "1NSI", capacities=1).replace(
            "statut: approved", "statut: draft"
        ),
        f"{base}/exercices/ex-1.tex": _meta(
            id="1NSI-TEST-EX-001",
            chapitre=chapter,
            type_objet="exercice",
            status="needs_review",
        ),
        report: """# DIRECTIVES EN COURS

- [x] PILOTE 1NSI-TEST : LOT 0→7 complet (3 ex, 1 corriges,
      2 CDP, 4 QCM, 5 rem, 6 eval, 7 TD, 8 projets).
      Gates strict VERT, 165 tests.
""",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    claims = inventory_module.build_inventory(tmp_path)["report_reconciliation"][
        "claims"
    ]

    exercises = next(
        claim for claim in claims if claim["metric"] == "exercices_principaux"
    )
    assert exercises["path"] == report
    assert exercises["line"] == 3
    assert exercises["scope"] == "chapter:1NSI-TEST"
    assert exercises["declared"] == 3
    assert exercises["calculated"] == 1
    assert exercises["etat"] == "contredit"
    completeness = next(claim for claim in claims if claim["metric"] == "completude")
    assert completeness["declared"] is True
    assert completeness["calculated"] is False
    assert completeness["etat"] == "contredit"
    tests = next(claim for claim in claims if claim["metric"] == "tests_passes")
    assert tests["line"] == 5
    assert tests["declared"] == 165
    assert tests["calculated"] is None
    assert tests["etat"] == "ouvert"


def test_report_source_routing_prefers_history_and_ignores_generated_outputs(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    root_report = "ETAT_COLLECTION.md"
    history = "audit/historique/ETAT_COLLECTION_AVANT_P0.md"
    generated = "audit/AUDIT_CONSOLIDE.md"
    math_report = "Mathematiques/manuel-maths/ETAT_COLLECTION.md"
    sources = {
        root_report: "# Ancien etat\n",
        history: "# Archive de l'ancien etat\n",
        generated: "<!-- AUTO-GENERE PAR inventory_collection.py -->\n",
        math_report: "# Etat mathematiques\n",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)
    tracked = inventory_module.git_tracked_files(tmp_path)

    assert inventory_module.report_source_paths(tmp_path, tracked) == (
        history,
        math_report,
    )


def test_report_claim_spanning_multiple_chapters_stays_open(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    first = "1SPE-PREMIER"
    second = "1SPE-SECOND"
    sources = {
        f"{_chapter_path('1SPE', first)}/contrat.yaml": _contract(
            first, "1SPE", capacities=1
        ),
        f"{_chapter_path('1SPE', second)}/contrat.yaml": _contract(
            second, "1SPE", capacities=1
        ),
        "ETAT_COLLECTION.md": (
            "| Manuel | Etat |\n"
            "|---|---|\n"
            "| Mathématiques Première | 1SPE-PREMIER et 1SPE-SECOND : "
            "30 exercices |\n"
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    claim = next(
        claim
        for claim in inventory_module.build_inventory(tmp_path)[
            "report_reconciliation"
        ]["claims"]
        if claim["metric"] == "exercices_principaux"
    )

    assert claim["scope"] == "unresolved:portee_chapitres_ambigue"
    assert claim["calculated"] is None
    assert claim["etat"] == "ouvert"


def test_deliverable_matrix_covers_all_mission_variants_and_blocks_publication(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    sources = {
        f"{base}/contrat.yaml": _contract(chapter, "1SPE", capacities=1),
        f"{base}/cours/c1.tex": _meta(status="approved"),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    matrix = inventory["deliverable_matrix"]

    assert list(matrix["manuals"]) == ["1NSI", "1SPE", "TNSI", "TSPE_2026_2027"]
    assert set(matrix["manuals"]["1SPE"]["variants"]) == {
        "banque_evaluations",
        "livret_methodes",
        "livret_remediation",
        "manuel_eleve",
        "manuel_professeur",
    }
    assert set(matrix["manuals"]["1NSI"]["variants"]) == {
        "evaluations",
        "livret_methodes",
        "manuel_eleve",
        "manuel_professeur",
        "projets",
        "remediations",
        "version_amenagee",
    }
    assert set(matrix["manuals"]["TNSI"]["variants"]) == {
        "banque_ecrite",
        "banque_pratique",
        "manuel_eleve",
        "manuel_professeur",
        "projets",
        "remediations",
        "version_amenagee",
    }
    assert matrix["manuals"]["1SPE"]["current"]["chapter_count"] == 1
    assert matrix["manuals"]["1SPE"]["objective"]["target_chapters"] == 10
    assert matrix["manuals"]["1SPE"]["publication_eligible"] is False
    assert any(
        blocker["code"] == "chapitres_manquants"
        for blocker in matrix["manuals"]["1SPE"]["blockers"]
    )
    assert all(
        variant["state"] == "absent"
        for variant in matrix["manuals"]["1SPE"]["variants"].values()
    )


def test_deliverable_matrix_blocks_needs_review_and_checks_model_coherence(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1NSI-TEST"
    base = _chapter_path("1NSI", chapter)
    sources = {
        f"{base}/contrat.yaml": _contract(chapter, "1NSI", capacities=1),
        f"{base}/cours/c1.tex": _meta(
            id="1NSI-TEST-C1",
            chapitre=chapter,
            status="needs_review",
        ),
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    inventory = inventory_module.build_inventory(tmp_path)
    manual = inventory["deliverable_matrix"]["manuals"]["1NSI"]

    assert manual["publication_eligible"] is False
    assert any(
        blocker["code"] == "statuts_non_approuves" for blocker in manual["blockers"]
    )
    assert inventory["coherence_checks"] == {
        "artifact_cardinality": {"ok": True, "violations": []},
        "chapter_manual_sums": {"ok": True, "violations": []},
        "status_distribution": {"ok": True, "violations": []},
    }

    inventory["manuals"]["1NSI"]["totals"]["sections_cours"] += 1
    checks = inventory_module.validate_inventory_coherence(inventory)
    assert checks["chapter_manual_sums"]["ok"] is False
    assert checks["chapter_manual_sums"]["violations"] == [
        {
            "calculated": 1,
            "declared": 2,
            "manual": "1NSI",
            "metric": "sections_cours",
        }
    ]

    inventory["manuals"]["1NSI"]["totals"]["sections_cours"] -= 1
    inventory["manuals"]["1NSI"]["statuses"] = {"approved": 1}
    checks = inventory_module.validate_inventory_coherence(inventory)
    assert checks["status_distribution"]["ok"] is False

    inventory["pdfs"].append(
        {
            "chapter": None,
            "manual": "1NSI",
            "page_count": 10,
            "page_count_method": "pdfinfo",
            "path": "MANUEL_1NSI_v1.pdf",
            "reason": None,
            "scope": "manual",
            "status": "counted",
            "variant": "eleve",
        }
    )
    checks = inventory_module.validate_inventory_coherence(inventory)
    assert checks["artifact_cardinality"]["ok"] is False
    assert checks["artifact_cardinality"]["violations"] == [
        {
            "actual": 0,
            "expected": 1,
            "manual": "1NSI",
            "scope": "manual",
        }
    ]


def test_report_continuation_scope_does_not_leak_after_a_blank_line(
    tmp_path: Path, inventory_module
) -> None:
    _init_repository(tmp_path)
    chapter = "1SPE-TEST"
    base = _chapter_path("1SPE", chapter)
    report = "Mathematiques/manuel-maths/DIRECTIVES_EN_COURS.md"
    sources = {
        f"{base}/contrat.yaml": _contract(chapter, "1SPE", capacities=1),
        f"{base}/exercices/ex-1.tex": _meta(
            id="1SPE-TEST-EX-001", type_objet="exercice", status="approved"
        ),
        report: """# Etat 1SPE
- 1SPE-TEST : 1 exercice.
Suite enveloppee : 1 exercice.

- Regle generale : 2 exercices par case.
- Référence v4.1 corrigé.
- 1SPE-TEST : 3 ex remédiation.
""",
    }
    for path, content in sources.items():
        _write(tmp_path / path, content)
    _track(tmp_path, *sources)

    claims = inventory_module.build_inventory(tmp_path)["report_reconciliation"][
        "claims"
    ]
    wrapped = [claim for claim in claims if claim["line"] == 3]
    general = [claim for claim in claims if claim["line"] == 5]

    assert wrapped[0]["scope"] == "chapter:1SPE-TEST"
    assert wrapped[0]["etat"] == "confirme"
    assert general[0]["scope"] == "directive:collection"
    assert general[0]["metric"] == "seuil_exercices_declares"
    assert general[0]["calculated"] is None
    assert general[0]["etat"] == "ouvert"
    assert not any(
        claim["line"] == 6 and claim["metric"] == "corriges" for claim in claims
    )
    remediation = next(claim for claim in claims if claim["line"] == 7)
    assert remediation["scope"] == "chapter:1SPE-TEST"
    assert remediation["metric"] == "exercices_remediation_declares"
    assert remediation["calculated"] is None
    assert remediation["etat"] == "ouvert"


def test_real_reports_expose_known_exercise_contradictions(inventory_module) -> None:
    inventory = inventory_module.build_inventory(ROOT)
    claims = inventory["report_reconciliation"]["claims"]

    total = next(
        claim
        for claim in claims
        if claim["path"] == "Mathematiques/manuel-maths/RAPPORT_FINAL_1SPE.md"
        and claim["scope"] == "manual:1SPE"
        and claim["metric"] == "exercices_principaux"
        and claim["declared"] == 471
    )
    assert total["calculated"] == 464
    assert total["etat"] == "contredit"
    trigonometrie = next(
        claim
        for claim in claims
        if claim["scope"] == "chapter:1SPE-TRIGONOMETRIE"
        and claim["metric"] == "exercices_principaux"
    )
    assert trigonometrie["declared"] == 50
    assert trigonometrie["calculated"] == 20
    assert trigonometrie["etat"] == "contredit"
    directive_completeness = next(
        claim
        for claim in claims
        if claim["path"] == "Mathematiques/manuel-maths/DIRECTIVES_EN_COURS.md"
        and claim["line"] == 50
        and claim["metric"] == "completude"
    )
    assert directive_completeness["declared"] is True
    assert directive_completeness["calculated"] is False
    assert directive_completeness["etat"] == "contredit"
