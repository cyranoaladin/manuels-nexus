from __future__ import annotations

import copy
import importlib.util
import json
from itertools import combinations
from pathlib import Path
import subprocess

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_residual_true_new_forensics.py"
INITIAL_JSON = ROOT / "audit" / "TRUE_NEW_18_FORENSICS.json"
INITIAL_MD = ROOT / "audit" / "TRUE_NEW_18_FORENSICS.md"
INVENTORY = ROOT / "audit" / "INVENTAIRE_COLLECTION.json"
REMOVED_FINGERPRINTS = {
    "265dbdeec1fc2b62",
    "2e189d4bed9a9520",
    "7c204b3da8fcb9a9",
    "e79a0d7257787b02",
    "fac802b8993558c3",
}


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _load_module():
    assert SCRIPT.is_file(), "le générateur résiduel doit exister"
    spec = importlib.util.spec_from_file_location(
        "build_residual_true_new_forensics",
        SCRIPT,
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _inventory_copy(tmp_path: Path) -> Path:
    target = tmp_path / "INVENTAIRE_COLLECTION.json"
    target.write_bytes(INVENTORY.read_bytes())
    return target


def test_builds_exact_residual_without_mutating_frozen_inputs(tmp_path: Path) -> None:
    module = _load_module()
    frozen_before = {
        INITIAL_JSON: INITIAL_JSON.read_bytes(),
        INITIAL_MD: INITIAL_MD.read_bytes(),
    }

    reports = module.build_reports(ROOT)
    module.write_reports(reports, tmp_path)
    first_bytes = {
        path.name: path.read_bytes() for path in sorted(tmp_path.iterdir())
    }
    module.write_reports(reports, tmp_path)

    assert {path.name: path.read_bytes() for path in sorted(tmp_path.iterdir())} == (
        first_bytes
    )
    assert {path: path.read_bytes() for path in frozen_before} == frozen_before
    assert set(first_bytes) == {
        "CURRENT_ANOMALY_SET_ALGEBRA_RESIDUAL.json",
        "CURRENT_ANOMALY_SET_ALGEBRA_RESIDUAL.md",
        "RESIDUAL_TRUE_NEW_FORENSICS.json",
        "RESIDUAL_TRUE_NEW_FORENSICS.md",
    }

    residual = reports["residual_forensics"]
    algebra = reports["residual_algebra"]
    forensic_source_sha = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    assert residual["forensic_source_sha"] == forensic_source_sha
    assert algebra["forensic_source_sha"] == forensic_source_sha
    expected_counts = {
        "TRUE_NEW_INITIAL": 18,
        "FIXED": 0,
        "REMOVED": 5,
        "REVIEW_CLOSED": 0,
        "CONTENT_FINDINGS_FIXED": 5,
        "NEW_AFTER_TRIAGE": 0,
        "RESIDUAL_TRUE_NEW": 13,
    }
    assert residual["counts"] == expected_counts
    assert algebra["counts"] == expected_counts
    assert len(residual["entries"]) == 13
    assert algebra["equalities"] == {
        "initial_still_active_open_debt": True,
        "no_new_after_triage": True,
        "residual_equation": True,
    }
    assert set(algebra["sets"]["REMOVED"]) == REMOVED_FINGERPRINTS
    assert algebra["sets"]["NEW_AFTER_TRIAGE"] == []
    full = algebra["full_current_algebra"]
    # Chaque dette declaree separement est un composant NOMME et disjoint de
    # l'algebre courante, jamais fondu dans le residuel gele des 18. La
    # campagne en ajoute un par chapitre qui cree des objets.
    # 2248 depuis le 2026-08-30 : deux corriges d'evaluation a
    # 1NSI-TYPES-CONSTRUITS et le QCM de TNSI-PROJET, chacun porte par son
    # registre. Chaque terme de l'equation a une autorite contractuelle.
    # 2293 depuis la reconstruction de TSPE-GEOMETRIE-ESPACE : 45 objets que
    # la machine a verifies et qu'aucun humain n'a relus, portes par leur
    # propre registre plutot que fondus dans un terme existant.
    # 2325 depuis la reconstruction couplee 1NSI : 36 objets neufs portes par
    # leur registre. APPROVED_TRANSITION_NEW passe de 9 a 5 : quatre
    # empreintes ont ete SUPERSEDEES par la reecriture des evaluations, et une
    # empreinte que la reecriture a fait disparaitre ne peut plus figurer dans
    # la partition courante.
    # 2325 apres la correction identitaire APT : trois empreintes du gel
    # designaient un etat INTERMEDIAIRE (chemin APT, identite AGT encore
    # declaree) que le commit a08f7ed0 a corrige ; elles sont retirees contre
    # la preuve de leur remplacement actif. Quatorze objets passent par
    # ailleurs des ensembles geles vers le registre de dette couplee, parce
    # qu'ils ont change : ils restent bloquants des deux cotes, seule leur
    # classe d'imputation bouge.
    #
    # L'equation n'est plus epinglee sous forme litterale : ce qui est
    # verrouille, c'est qu'elle SOMME au total courant, et qu'aucun terme ne
    # soit ni oublie ni compte deux fois.
    total, _, terms = full["cardinality_equation"].partition(" = ")
    parts = [int(term) for term in terms.split(" + ")]
    assert int(total) == full["cardinalities"]["CURRENT_ACTIVE"]
    assert sum(parts) == int(total)
    assert full["cardinalities"]["CURRENT_ACTIVE"] == 2325
    assert full["cardinalities"]["TRUE_NEW"] == 13
    assert full["cardinalities"]["VARALEA_C6C7_REVIEW_DEBT_12"] == 12
    assert full["cardinalities"]["EXPONENTIELLE_C1_METHOD_REVIEW_DEBT_1"] == 1
    assert full["cardinalities"]["NSI_TC_EVAL_CORRIGES_REVIEW_DEBT_2"] == 2
    assert full["cardinalities"]["TNSI_PROJET_QCM_REVIEW_DEBT_1"] == 1
    assert full["cardinalities"]["TSPE_GEOESPACE_AUTHORED_REVIEW_DEBT_45"] == 45
    # Le registre couple suit le corpus : son cardinal est celui du registre
    # committe, jamais un quota fige.
    coupled = json.loads(
        (ROOT / "audit/NSI_COUPLED_ALGORITHMICS_REVIEW_DEBT.json").read_text(
            encoding="utf-8"
        )
    )
    assert (
        full["cardinalities"]["NSI_COUPLED_ALGORITHMICS_REVIEW_DEBT"]
        == coupled["count"]
    )
    declared = (
        "VARALEA_C6C7_REVIEW_DEBT_12",
        "EXPONENTIELLE_C1_METHOD_REVIEW_DEBT_1",
        "NSI_TC_EVAL_CORRIGES_REVIEW_DEBT_2",
        "TNSI_PROJET_QCM_REVIEW_DEBT_1",
        "TSPE_GEOESPACE_AUTHORED_REVIEW_DEBT_45",
        "NSI_COUPLED_ALGORITHMICS_REVIEW_DEBT",
    )
    # La dette de revue se partitionne : aucune intersection deux a deux, y
    # compris avec le residuel gele. Le test n'echantillonnait que deux
    # paires ; une dette comptee deux fois passait donc inapercue.
    partition = {name: set(full["sets"][name]) for name in declared}
    partition["TRUE_NEW"] = set(full["sets"]["TRUE_NEW"])
    for left, right in combinations(sorted(partition), 2):
        assert partition[left].isdisjoint(partition[right]), (left, right)
    assert sum(len(members) for members in partition.values()) == len(
        set().union(*partition.values())
    )
    assert full["equalities"]["current_partition"] is True
    assert full["equalities"]["current_partition_pairwise_disjoint"] is True
    assert full["unknown_count"] == 0

    required = {
        "fingerprint",
        "object_id",
        "path",
        "category",
        "why_legitimate",
        "why_cannot_close",
        "current_review_state",
        "owner",
        "closure_phase",
        "release_acceptance",
        "source_sha",
        "triage_class",
        "reason_created",
        "class_b_eligibility",
    }
    assert all(required <= set(entry) for entry in residual["entries"])
    assert all(
        entry["triage_class"] == "LEGITIMATE_REVIEW_DEBT"
        and entry["current_review_state"]
        == "PENDING_QUALIFIED_OPEN_DEBT"
        and entry["release_acceptance"] is False
        and entry["source_sha"].startswith("sha256:")
        and "qualified=true" in entry["why_cannot_close"]
        for entry in residual["entries"]
    )
    assert all(
        all(value in {"PASS", "NO"} for value in entry["class_b_eligibility"].values())
        for entry in residual["entries"]
    )


def test_supersession_requires_exact_current_replacement_in_declared_ledger(
    tmp_path: Path,
) -> None:
    module = _load_module()
    audit = tmp_path / "audit"
    audit.mkdir()
    migration = {
        "migrations": {
            "a" * 16: {
                "superseded_by_rewrite": True,
                "superseded_declared_in": "audit/REWRITE.json",
                "current_source": "chapter/eval.tex",
                "current_object_id": "EV-A",
                "chapter": "1NSI-X",
            }
        }
    }
    (audit / "ANOMALY_IDENTITY_MIGRATIONS.yaml").write_text(
        yaml.safe_dump(migration), encoding="utf-8"
    )
    (audit / "REWRITE.json").write_text(
        json.dumps(
            {
                "entries": [
                    {
                        "fingerprint": "b" * 16,
                        "path": "chapter/other.tex",
                        "object_id": "EV-A",
                        "chapter": "1NSI-X",
                        "origin": "REWRITTEN_STALE_APPROVAL",
                        "human_approval_invalidated_by_rewrite": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="remplacement courant exact"):
        module._superseded_by_rewrite(tmp_path, current_active={"b" * 16})


def test_check_reuses_frozen_source_sha_only_for_report_only_commits(
    tmp_path: Path,
) -> None:
    module = _load_module()
    repo = tmp_path / "repo"
    audit = repo / "audit"
    audit.mkdir(parents=True)
    _git(repo, "init")
    _git(repo, "config", "user.email", "tests@example.invalid")
    _git(repo, "config", "user.name", "Tests")
    (repo / "source.txt").write_text("source\n", encoding="utf-8")
    _git(repo, "add", "source.txt")
    _git(repo, "commit", "-m", "source")
    source_sha = _git(repo, "rev-parse", "HEAD")

    for names in module.OUTPUT_NAMES.values():
        (audit / names["json"]).write_text(
            json.dumps({"forensic_source_sha": source_sha}) + "\n",
            encoding="utf-8",
        )
        (audit / names["md"]).write_text("report\n", encoding="utf-8")
    _git(repo, "add", "audit")
    _git(repo, "commit", "-m", "reports")

    assert module._forensic_source_sha_for_check(repo, audit) == source_sha

    (repo / "source.txt").write_text("changed\n", encoding="utf-8")
    with pytest.raises(ValueError, match="sources modifiées depuis le gel"):
        module._forensic_source_sha_for_check(repo, audit)

    (repo / "source.txt").write_text("source\n", encoding="utf-8")
    (repo / "untracked-object.yaml").write_text("new: object\n", encoding="utf-8")
    with pytest.raises(ValueError, match="sources modifiées depuis le gel"):
        module._forensic_source_sha_for_check(repo, audit)


def test_build_revalidates_source_snapshot_after_projection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    module = _load_module()
    repo = tmp_path / "repo"
    audit = repo / "audit"
    audit.mkdir(parents=True)
    _git(repo, "init")
    _git(repo, "config", "user.email", "tests@example.invalid")
    _git(repo, "config", "user.name", "Tests")
    (repo / "source.txt").write_text("source\n", encoding="utf-8")
    _git(repo, "add", "source.txt")
    _git(repo, "commit", "-m", "source")
    source_sha = _git(repo, "rev-parse", "HEAD")

    def mutate_during_build(*args, **kwargs):
        (repo / "late-object.yaml").write_text("late: object\n", encoding="utf-8")
        return {}

    monkeypatch.setattr(module, "build_reports", mutate_during_build)
    with pytest.raises(ValueError, match="sources modifiées depuis le gel"):
        module._build_reports_with_stable_source(repo, audit, source_sha)


def test_rejects_any_unexpected_active_unqualified_fingerprint(
    tmp_path: Path,
) -> None:
    module = _load_module()
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    inventory["anomaly_qualifications"]["ffffffffffffffff"] = {
        "blocking": True,
        "categories": ["blocking_statuses"],
        "category": "blocking_statuses",
        "disposition": "open_debt",
        "fingerprint": "ffffffffffffffff",
        "occurrence_count": 1,
        "qualified": False,
        "raw_identities": ["f" * 64],
    }
    mutated = tmp_path / "inventory-extra.json"
    mutated.write_text(json.dumps(inventory), encoding="utf-8")

    with pytest.raises(
        ValueError,
        match="ensemble actif non qualifié inattendu",
    ):
        module.build_reports(ROOT, inventory_path=mutated)


def test_rejects_a_qualified_residual_that_stops_blocking_release(
    tmp_path: Path,
) -> None:
    module = _load_module()
    inventory = copy.deepcopy(json.loads(INVENTORY.read_text(encoding="utf-8")))
    initial = json.loads(INITIAL_JSON.read_text(encoding="utf-8"))
    fingerprint = next(
        entry["fingerprint"]
        for entry in initial["entries"]
        if entry["triage_class"] == "LEGITIMATE_REVIEW_DEBT"
    )
    qualification = inventory["anomaly_qualifications"][fingerprint]
    qualification["blocking"] = False
    qualification["release_blocking"] = False
    mutated = tmp_path / "inventory-non-blocking.json"
    mutated.write_text(json.dumps(inventory), encoding="utf-8")

    with pytest.raises(ValueError, match="non bloquante ou clôturée"):
        module.build_reports(ROOT, inventory_path=mutated)


def test_projects_a_review_closed_initial_fingerprint(
    tmp_path: Path,
) -> None:
    module = _load_module()
    inventory = copy.deepcopy(
        json.loads(INVENTORY.read_text(encoding="utf-8"))
    )
    initial = json.loads(INITIAL_JSON.read_text(encoding="utf-8"))
    fingerprint = next(
        entry["fingerprint"]
        for entry in initial["entries"]
        if entry["triage_class"] == "LEGITIMATE_REVIEW_DEBT"
    )
    inventory["anomaly_qualifications"].pop(fingerprint)
    mutated = tmp_path / "inventory-review-closed.json"
    mutated.write_text(json.dumps(inventory), encoding="utf-8")

    reports = module.build_reports(ROOT, inventory_path=mutated)
    assert reports["residual_forensics"]["counts"]["REVIEW_CLOSED"] == 1
    assert reports["residual_forensics"]["counts"]["RESIDUAL_TRUE_NEW"] == 12


def test_projects_a_fixed_initial_fingerprint(tmp_path: Path) -> None:
    module = _load_module()
    inventory = copy.deepcopy(json.loads(INVENTORY.read_text(encoding="utf-8")))
    initial = json.loads(INITIAL_JSON.read_text(encoding="utf-8"))
    fingerprint = next(
        entry["fingerprint"]
        for entry in initial["entries"]
        if entry["triage_class"] == "FIX_NOW"
    )
    inventory["anomaly_qualifications"].pop(fingerprint)
    mutated = tmp_path / "inventory-fixed.json"
    mutated.write_text(json.dumps(inventory), encoding="utf-8")

    reports = module.build_reports(ROOT, inventory_path=mutated)
    counts = reports["residual_forensics"]["counts"]
    assert counts["FIXED"] == 1
    assert counts["CONTENT_FINDINGS_FIXED"] == 5
    assert counts["RESIDUAL_TRUE_NEW"] == 12


def _supersession_fixture(tmp_path: Path, *, entry: dict) -> Path:
    """Une supersession minimale et VALIDE, sauf pour ce que le test change."""
    audit = tmp_path / "audit"
    audit.mkdir(exist_ok=True)
    source = tmp_path / "chapter" / "eval.tex"
    source.parent.mkdir(parents=True, exist_ok=True)
    source.write_text("contenu reecrit\n", encoding="utf-8")
    (audit / "ANOMALY_IDENTITY_MIGRATIONS.yaml").write_text(
        yaml.safe_dump(
            {
                "migrations": {
                    "a" * 16: {
                        "superseded_by_rewrite": True,
                        "superseded_declared_in": "audit/REWRITE.json",
                        "current_source": "chapter/eval.tex",
                        # Identite telle qu'elle etait AVANT la reecriture.
                        "current_object_id": "1NSI-AGT-EVAL-B",
                        "chapter": "1NSI-X",
                        "current_source_sha256": "sha256:" + "0" * 64,
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    (audit / "REWRITE.json").write_text(
        json.dumps({"entries": [entry]}), encoding="utf-8"
    )
    return tmp_path


def test_supersession_joins_on_the_path_when_the_rewrite_renamed_the_object() -> None:
    """Une reecriture PEUT changer l'identifiant declare de l'objet.

    C'est precisement le cas AGT -> APT : joindre le remplacement sur
    `object_id` rendait la supersession introuvable des que la reecriture
    corrigeait la META. Le chemin, lui, ne bouge pas.
    """
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = _supersession_fixture(
            Path(tmp),
            entry={
                "fingerprint": "b" * 16,
                "path": "chapter/eval.tex",
                "object_id": "1NSI-APT-EVAL-B",
                "chapter": "1NSI-X",
                "origin": "REWRITTEN_STALE_APPROVAL",
                "human_approval_evidence": True,
                "human_approval_invalidated_by_rewrite": True,
            },
        )
        module = _load_module()
        assert module._superseded_by_rewrite(
            root, current_active={"b" * 16}
        ) == {"a" * 16}


def test_supersession_accepts_a_rewrite_that_never_carried_human_approval() -> None:
    """`verified` est une preuve MACHINE : la reecrire n'invalide aucune
    approbation humaine, et exiger le drapeau contraire obligerait le registre
    a declarer une approbation qui n'a jamais existe."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = _supersession_fixture(
            Path(tmp),
            entry={
                "fingerprint": "b" * 16,
                "path": "chapter/eval.tex",
                "object_id": "1NSI-APT-EVAL-B",
                "chapter": "1NSI-X",
                "origin": "REWRITTEN_PREVIOUSLY_MACHINE_VERIFIED",
                "human_approval_evidence": False,
                "human_approval_invalidated_by_rewrite": False,
            },
        )
        module = _load_module()
        assert module._superseded_by_rewrite(
            root, current_active={"b" * 16}
        ) == {"a" * 16}


def test_supersession_rejects_a_stale_approval_that_is_not_declared_invalid() -> None:
    """La garantie inverse tient : une approbation humaine reelle qui aurait
    survecu a la reecriture reste refusee."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = _supersession_fixture(
            Path(tmp),
            entry={
                "fingerprint": "b" * 16,
                "path": "chapter/eval.tex",
                "object_id": "1NSI-APT-EVAL-B",
                "chapter": "1NSI-X",
                "origin": "REWRITTEN_STALE_APPROVAL",
                "human_approval_evidence": True,
                "human_approval_invalidated_by_rewrite": False,
            },
        )
        module = _load_module()
        with pytest.raises(ValueError, match="remplacement courant exact"):
            module._superseded_by_rewrite(root, current_active={"b" * 16})


def _corrections_fixture(tmp_path: Path, corrections: dict) -> Path:
    audit = tmp_path / "audit"
    audit.mkdir(exist_ok=True)
    (audit / "ANOMALY_IDENTITY_CORRECTIONS.yaml").write_text(
        yaml.safe_dump({"corrections": corrections}), encoding="utf-8"
    )
    return tmp_path


def test_identity_corrections_retire_a_stale_fingerprint_against_its_replacement() -> None:
    """Une empreinte perimee ne part QUE si son remplacement est actif.

    L'ancre gelee ne peut pas connaitre une identite corrigee apres son gel.
    Le controle nomme la paire ; le producteur la reverifie contre
    l'inventaire courant, il ne la croit pas sur parole.
    """
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = _corrections_fixture(
            Path(tmp),
            {
                "a" * 16: {
                    "path": "chapter/cours.tex",
                    "corrected_fingerprint": "b" * 16,
                }
            },
        )
        module = _load_module()
        assert module._identity_corrections(
            root,
            current_active={"b" * 16},
            paths_by_fingerprint={"b" * 16: "chapter/cours.tex"},
        ) == {"a" * 16}


def test_identity_correction_is_refused_when_the_replacement_is_not_active() -> None:
    """Sans remplacement actif, l'objet a DISPARU : ce n'est plus une
    correction d'identite, et l'absorber silencieusement masquerait une
    suppression."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = _corrections_fixture(
            Path(tmp),
            {
                "a" * 16: {
                    "path": "chapter/cours.tex",
                    "corrected_fingerprint": "b" * 16,
                }
            },
        )
        module = _load_module()
        with pytest.raises(ValueError, match="remplacement"):
            module._identity_corrections(
                root, current_active=set(), paths_by_fingerprint={}
            )


def test_identity_correction_is_refused_when_the_stale_fingerprint_is_still_active() -> None:
    """Si l'empreinte perimee est encore active, rien n'a ete corrige."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = _corrections_fixture(
            Path(tmp),
            {
                "a" * 16: {
                    "path": "chapter/cours.tex",
                    "corrected_fingerprint": "b" * 16,
                }
            },
        )
        module = _load_module()
        with pytest.raises(ValueError, match="encore active"):
            module._identity_corrections(
                root,
                current_active={"a" * 16, "b" * 16},
                paths_by_fingerprint={"b" * 16: "chapter/cours.tex"},
            )


def test_identity_correction_is_refused_when_the_replacement_names_another_path() -> None:
    """L'appariement est 1:1 SUR LE CHEMIN : un remplacement qui designe un
    autre fichier n'est pas le meme objet."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = _corrections_fixture(
            Path(tmp),
            {
                "a" * 16: {
                    "path": "chapter/cours.tex",
                    "corrected_fingerprint": "b" * 16,
                }
            },
        )
        module = _load_module()
        with pytest.raises(ValueError, match="chemin"):
            module._identity_corrections(
                root,
                current_active={"b" * 16},
                paths_by_fingerprint={"b" * 16: "chapter/autre.tex"},
            )
