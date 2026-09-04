"""INT-006 : la ré-observation 1NSI explique un changement de source set par
ensembles exacts (ajoutés, retirés, modifiés), attribués aux commits de cause.

Chaque test construit un dépôt git minimal portant un chapitre 1NSI, scelle les
registres d'attente sur un premier état, puis fait évoluer le contenu par
commits. Le producteur doit attribuer chaque chemin, échouer fermé sur tout
chemin qu'aucun commit n'explique, et refuser de déplacer une revue humaine.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
PRODUCER = ROOT / "scripts/build_1nsi_pending_state_reobservation.py"
REVIEW_MODULE = ROOT / "scripts/review_1nsi_content.py"
CHAPTER = "1NSI-FIX"

BOUND_CONSTANTS = {
    "NSI_ROOT": "NSI",
    "CAMPAIGN_TARGET": "audit/1NSI_CONTENT_REVIEW_CAMPAIGN_STATE.json",
    "STATUS_TARGET": "audit/1NSI_STATUS_GOVERNANCE_PENDING.json",
    "JSON_TARGET": "audit/1NSI_PENDING_STATE_REOBSERVATION.json",
    "MD_TARGET": "audit/1NSI_PENDING_STATE_REOBSERVATION.md",
    "POLICY_PATH": "audit/1NSI_CONTENT_REVIEW_POLICY.yaml",
    "FINDINGS_PATH": "audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml",
    "REGISTRY_PATH": "audit/1NSI_CONTENT_REVIEWS.json",
    "ADGK_CONTRACT": f"NSI/chapitres/{CHAPTER}/contrat.yaml",
    "STATUS_POLICY": "audit/1NSI_STATUS_GOVERNANCE.yaml",
    "HUMAN_REVIEW_ROOT": "audit/reviews/human",
}


def _load_producer() -> Any:
    spec = importlib.util.spec_from_file_location("reobservation_under_test", PRODUCER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Repo:
    """Un dépôt 1NSI minimal, piloté commit par commit."""

    def __init__(self, root: Path, producer: Any, monkeypatch: pytest.MonkeyPatch) -> None:
        self.root = root
        self.producer = producer
        root.mkdir(parents=True, exist_ok=True)
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.name", "Fixture")
        self.git("config", "user.email", "fixture@example.invalid")
        monkeypatch.setattr(producer, "ROOT", root)
        for name, relative in BOUND_CONSTANTS.items():
            monkeypatch.setattr(producer, name, root / relative)
        monkeypatch.setattr(producer, "REVIEW_MODULE", REVIEW_MODULE)
        self._scaffold()

    # -- plumbing ---------------------------------------------------------
    def git(self, *arguments: str) -> str:
        result = subprocess.run(
            ["git", *arguments], cwd=self.root, capture_output=True, text=True, check=True
        )
        return result.stdout.strip()

    def write(self, relative: str, text: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def remove(self, relative: str) -> None:
        (self.root / relative).unlink()

    def commit(self, message: str) -> str:
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message)
        return self.git("rev-parse", "HEAD")

    def head(self) -> str:
        return self.git("rev-parse", "HEAD")

    # -- content ----------------------------------------------------------
    def source_path(self, name: str, section: str = "cours", chapter: str = CHAPTER) -> str:
        return f"NSI/chapitres/{chapter}/{section}/{chapter}-{name}.tex"

    def source(
        self,
        name: str,
        body: str = "corps",
        *,
        section: str = "cours",
        status: str = "needs_review",
        chapter: str = CHAPTER,
        object_id: str | None = None,
    ) -> str:
        meta = {
            "id": object_id or f"{chapter}-{name}",
            "chapitre": chapter,
            "status": status,
            "type_objet": section,
            "capacites": [],
        }
        relative = self.source_path(name, section, chapter)
        self.write(relative, f"% META: {json.dumps(meta)}\n{body}\n")
        return relative

    def _scaffold(self) -> None:
        self.write(
            f"NSI/chapitres/{CHAPTER}/contrat.yaml",
            f"chapitre: {CHAPTER}\nstatut: draft\ncapacites: []\n",
        )
        self.write(
            "audit/1NSI_CONTENT_REVIEW_POLICY.yaml",
            "official_sources: []\ncontractual_documents: []\n"
            "decision: fixture\nverdicts: []\nprohibited_transitions: []\n"
            "review_dimensions: []\ncapacity_matrix: {}\nscope_guard: {}\n"
            "allowlist: []\nprotocol_digest: sha256:none\n",
        )
        self.write("audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml", "findings: []\n")
        self.write(
            "audit/1NSI_CONTENT_REVIEWS.json",
            json.dumps({"publication_approval": False, "entries": []}) + "\n",
        )
        self.write(
            "audit/1NSI_STATUS_GOVERNANCE.yaml", "prohibited_transitions: [approved]\n"
        )

    # -- registers --------------------------------------------------------
    def seal(self, message: str = "observe the pending registers") -> str:
        """Écrit les registres sur l'état courant et les commet : le baseline."""

        module = self.producer.load_review_module()
        sources = module.discover_sources(self.root)
        campaign_path = self.producer.CAMPAIGN_TARGET
        if campaign_path.is_file():
            campaign = json.loads(campaign_path.read_text(encoding="utf-8"))
        else:
            campaign = {
                "artifact_name": "1NSI_CONTENT_REVIEW_CAMPAIGN_STATE",
                "created": "2026-08-19",
                "status": "PENDING_REVIEW_RERUN",
                "reason": "campagne scellée, en attente",
                "no_go_carrier": "release-strict",
                "sealed": {"sealing_commit": "5d8bedd9", "sealed_sources_count": 2},
                "observed": {},
            }
        campaign["observed"] = self.producer.observe_campaign(module, sources)
        status_path = self.producer.STATUS_TARGET
        if status_path.is_file():
            status = json.loads(status_path.read_text(encoding="utf-8"))
        else:
            status = {
                "artifact_name": "1NSI_STATUS_GOVERNANCE_PENDING",
                "created": "2026-08-19",
                "status": "PENDING_HUMAN_REVIEW",
                "reason": "statuts figés, en attente",
                "no_go_carrier": "release-strict",
            }
        status.update(self.producer.observe_status())
        campaign_path.write_text(json.dumps(campaign, indent=2) + "\n", encoding="utf-8")
        status_path.write_text(json.dumps(status, indent=2) + "\n", encoding="utf-8")
        return self.commit(message)

    def build(self, write: bool = False) -> dict[str, Any]:
        return self.producer.build(write)

    def registers_bytes(self) -> tuple[str, str]:
        return _sha(self.producer.CAMPAIGN_TARGET), _sha(self.producer.STATUS_TARGET)

    def human_review(self, chapter: str, **state: Any) -> None:
        directory = self.root / "audit/reviews/human" / chapter
        payload = {
            "chapter_id": chapter,
            "human_content_approval": "PENDING",
            "qcm_human_approval": "PENDING",
            "publication_approval": False,
            "review_a": {"role": "EXPERT_NSI", "state": "PENDING_UNASSIGNED", "verdict": None},
            "review_b": {
                "role": "EXPERT_PROGRAMME_PEDAGOGIE",
                "state": "PENDING_UNASSIGNED",
                "verdict": None,
            },
        }
        payload.update(state)
        self.write(f"audit/reviews/human/{chapter}/REVIEW_STATE.json", json.dumps(payload))
        directory.mkdir(parents=True, exist_ok=True)


@pytest.fixture
def producer() -> Any:
    return _load_producer()


@pytest.fixture
def repo(tmp_path: Path, producer: Any, monkeypatch: pytest.MonkeyPatch) -> Repo:
    """Un dépôt scellé sur {A, B}."""

    fixture = Repo(tmp_path / "repo", producer, monkeypatch)
    fixture.source("A", "corps de A")
    fixture.source("B", "corps de B")
    fixture.commit("initial content")
    fixture.seal()
    return fixture


def _rows(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["path"]: row for row in payload["source_set"]["attribution"]}


def _sets(payload: dict[str, Any]) -> dict[str, Any]:
    """Les ensembles et condensats, sans les SHA de commits (propres à chaque dépôt)."""

    source_set = payload["source_set"]
    old = {k: v for k, v in source_set["declared_historical"].items() if k != "commit"}
    return {
        "added": source_set["added"],
        "removed": source_set["removed"],
        "modified_existing": source_set["modified_existing"],
        "declared_historical": old,
        "observed_current": source_set["observed_current"],
    }


# ---------------------------------------------------------------- fixtures 9-10


def test_additions_only_are_attributed_to_their_cause_commit(repo: Repo) -> None:
    added = repo.source("C", "corps de C")
    cause = repo.commit("author C")

    payload = repo.build()

    assert payload["source_set"]["added"] == [added]
    assert payload["source_set"]["removed"] == []
    assert payload["source_set"]["modified_existing"] == []
    assert payload["summary"]["UNEXPLAINED_DELTA"] == 0
    assert payload["summary"]["SOURCES_ADDED"] == 1
    row = _rows(payload)[added]
    assert row["change"] == "added"
    assert row["cause_commits"] == [cause]
    assert row["before"] is None
    assert row["after"]["id"] == f"{CHAPTER}-C"
    assert payload["cause"]["sha"] == cause
    assert payload["state"] == "STALE_EXPLAINED"


def test_deletions_only_keep_the_int004_behaviour(repo: Repo) -> None:
    removed = repo.source("C", "corps de C")
    repo.commit("author C")
    repo.seal()
    repo.remove(removed)
    cause = repo.commit("remove C")

    payload = repo.build()

    assert payload["source_set"]["removed"] == [removed]
    assert payload["source_set"]["added"] == []
    assert payload["summary"]["UNEXPLAINED_DELTA"] == 0
    row = _rows(payload)[removed]
    assert row["change"] == "removed"
    assert row["cause_commits"] == [cause]
    assert row["after"] is None
    assert row["before"]["id"] == f"{CHAPTER}-C"


def test_int004_replay_removal_of_five_redundant_copies_passes(repo: Repo) -> None:
    """TYPES-CONSTRUITS : cinq copies retirées d'un coup, rien d'ajouté."""

    copies = [repo.source(f"REMED-0{n}", "même corps", section="remediation") for n in range(1, 6)]
    kept = repo.source("REM", "même corps", section="remediation")
    repo.commit("six remediation objects")
    repo.seal()
    old_count = repo.build()["source_set"]["observed_current"]["count"]
    for copy in copies:
        repo.remove(copy)
    cause = repo.commit("remove five semantically redundant remediation copies")

    payload = repo.build()

    assert payload["source_set"]["removed"] == sorted(copies)
    assert payload["source_set"]["added"] == []
    assert payload["source_set"]["observed_current"]["count"] == old_count - 5
    assert kept not in _rows(payload)
    assert all(row["cause_commits"] == [cause] for row in _rows(payload).values())
    assert payload["summary"]["UNEXPLAINED_DELTA"] == 0
    assert payload["summary"]["SOURCES_REMOVED"] == 5


# ---------------------------------------------------------------- fixture 11


def test_mixed_change_with_zero_net_count_is_reported_by_sets(repo: Repo) -> None:
    c_path = repo.source("C", "corps de C")
    repo.commit("author C")
    repo.seal()
    old = repo.build()["source_set"]["observed_current"]
    repo.remove(c_path)
    d_path = repo.source("D", "corps de D")
    cause = repo.commit("replace C by D")

    payload = repo.build()
    current = payload["source_set"]["observed_current"]

    # Un compte net ne verrait rien : même cardinal, ensembles différents.
    assert current["count"] == old["count"]
    assert current["ids_digest"] != old["ids_digest"]
    assert payload["source_set"]["removed"] == [c_path]
    assert payload["source_set"]["added"] == [d_path]
    assert _rows(payload)[c_path]["cause_commits"] == [cause]
    assert _rows(payload)[d_path]["cause_commits"] == [cause]
    assert payload["summary"]["UNEXPLAINED_DELTA"] == 0
    assert payload["summary"]["SOURCES_ADDED"] == payload["summary"]["SOURCES_REMOVED"] == 1


# ---------------------------------------------------------------- fixture 12


def test_addition_without_cause_commit_fails_closed(repo: Repo) -> None:
    d_path = repo.source("D", "corps de D")
    repo.commit("author D")
    c_path = repo.source("C", "corps de C")  # jamais commis
    before = repo.registers_bytes()

    payload = repo.build(write=True)

    assert payload["state"] == "BLOCKED"
    assert payload["summary"]["UNEXPLAINED_ADDITIONS"] == 1
    assert payload["summary"]["UNEXPLAINED_DELTA"] == 1
    rows = _rows(payload)
    assert rows[c_path]["explained"] is False
    assert rows[c_path]["cause_commits"] == []
    assert rows[d_path]["explained"] is True
    assert [row["path"] for row in payload["unexplained_delta"]] == [c_path]
    # Fermé : rien n'a été écrit, même avec --apply.
    assert repo.registers_bytes() == before


def test_addition_committed_outside_the_source_scope_does_not_explain(repo: Repo) -> None:
    """Le chemin est ajouté dans l'arbre de travail, mais le commit ajoute autre chose."""

    repo.write("README.md", "hors périmètre\n")
    repo.commit("unrelated commit")
    c_path = repo.source("C", "corps de C")

    payload = repo.build()

    assert payload["source_set"]["added"] == [c_path]
    assert payload["summary"]["UNEXPLAINED_ADDITIONS"] == 1
    assert payload["summary"]["CAUSE_COMMITS"] == 0


def test_removal_without_cause_commit_fails_closed(repo: Repo) -> None:
    repo.remove(repo.source_path("B"))

    payload = repo.build(write=True)

    assert payload["summary"]["UNEXPLAINED_REMOVALS"] == 1
    assert payload["state"] == "BLOCKED"


# ---------------------------------------------------------------- fixture 13


def test_modified_existing_path_is_not_an_unchanged_object(repo: Repo) -> None:
    a_path = repo.source("A", "corps de A, corrigé")
    cause = repo.commit("fix A")

    payload = repo.build()

    assert payload["source_set"]["added"] == []
    assert payload["source_set"]["removed"] == []
    assert payload["source_set"]["modified_existing"] == [a_path]
    row = _rows(payload)[a_path]
    assert row["change"] == "modified"
    assert row["before"]["source_sha256"] != row["after"]["source_sha256"]
    assert row["cause_commits"] == [cause]
    assert payload["summary"]["UNEXPLAINED_DELTA"] == 0
    assert payload["summary"]["SOURCES_MODIFIED"] == 1


def test_uncommitted_modification_is_unexplained(repo: Repo) -> None:
    a_path = repo.source("A", "corps de A, brouillon non commis")

    payload = repo.build()

    assert payload["source_set"]["modified_existing"] == [a_path]
    assert payload["summary"]["UNEXPLAINED_MODIFICATIONS"] == 1
    assert "non commise" in _rows(payload)[a_path]["reason"]


def test_committed_then_locally_edited_addition_is_unexplained(repo: Repo) -> None:
    c_path = repo.source("C", "corps de C")
    repo.commit("author C")
    repo.source("C", "corps de C, retouché après le commit")

    payload = repo.build()

    assert payload["summary"]["UNEXPLAINED_ADDITIONS"] == 1
    assert "non commise" in _rows(payload)[c_path]["reason"]


# ---------------------------------------------------------------- fixture 14


def test_source_set_change_on_a_humanly_reviewed_scope_is_forbidden(
    repo: Repo, producer: Any
) -> None:
    repo.human_review(
        CHAPTER, review_a={"role": "EXPERT_NSI", "state": "RECEIVED", "verdict": "ACCEPTED"}
    )
    repo.source("C", "corps de C")
    repo.commit("author C on a reviewed chapter")
    before = repo.registers_bytes()

    with pytest.raises(producer.ReobservationError, match="AUTO_REOBSERVATION_FORBIDDEN"):
        repo.build(write=True)
    assert repo.registers_bytes() == before


def test_a_receipt_file_alone_forbids_automatic_reobservation(
    repo: Repo, producer: Any
) -> None:
    repo.human_review(CHAPTER)
    repo.write(
        f"audit/reviews/human/{CHAPTER}/receipts/A-EXPERT_NSI.json",
        json.dumps({"verdict": "ACCEPTED"}),
    )
    repo.remove(repo.source_path("B"))
    repo.commit("remove B on a chapter that holds a receipt")

    with pytest.raises(producer.ReobservationError, match="AUTO_REOBSERVATION_FORBIDDEN"):
        repo.build()


def test_registry_publication_approval_forbids_automatic_reobservation(
    repo: Repo, producer: Any
) -> None:
    repo.write(
        "audit/1NSI_CONTENT_REVIEWS.json",
        json.dumps({"publication_approval": True, "entries": []}) + "\n",
    )
    repo.source("C", "corps de C")
    repo.commit("author C under an approved registry")

    with pytest.raises(producer.ReobservationError, match="AUTO_REOBSERVATION_FORBIDDEN"):
        repo.build()


def test_an_unassigned_review_state_does_not_block(repo: Repo) -> None:
    repo.human_review(CHAPTER)
    repo.source("C", "corps de C")
    repo.commit("author C on a chapter whose review is not started")

    payload = repo.build()

    assert payload["summary"]["HUMAN_RECEIPTS_AFFECTED"] == 0
    assert payload["summary"]["UNEXPLAINED_DELTA"] == 0


def test_a_review_on_another_chapter_is_out_of_scope(repo: Repo) -> None:
    repo.human_review(
        "1NSI-OTHER", review_b={"role": "X", "state": "RECEIVED", "verdict": "ACCEPTED"}
    )
    repo.source("C", "corps de C")
    repo.commit("author C")

    payload = repo.build()

    assert payload["summary"]["HUMAN_RECEIPTS_AFFECTED"] == 0
    assert payload["source_set"]["affected_chapters"] == [CHAPTER]


# ---------------------------------------------------------------- fixture 15


def test_a_cause_commit_touching_only_non_source_files_changes_nothing(repo: Repo) -> None:
    repo.write(f"NSI/chapitres/{CHAPTER}/validations/{CHAPTER}-A.execution.json", "{}")
    repo.write("README.md", "hors périmètre\n")
    repo.commit("receipts and docs only")

    payload = repo.build()

    assert payload["state"] == "CURRENT"
    assert payload["source_set"]["added"] == []
    assert payload["source_set"]["removed"] == []
    assert payload["source_set"]["modified_existing"] == []
    assert payload["summary"]["UNEXPLAINED_DELTA"] == 0


def test_non_source_files_in_a_cause_commit_neither_explain_nor_appear(repo: Repo) -> None:
    c_path = repo.source("C", "corps de C")
    repo.write(f"NSI/chapitres/{CHAPTER}/validations/{CHAPTER}-C.execution.json", "{}")
    repo.write("README.md", "hors périmètre\n")
    cause = repo.commit("author C with its receipt and a doc")

    payload = repo.build()

    assert list(_rows(payload)) == [c_path]
    assert _rows(payload)[c_path]["cause_commits"] == [cause]
    assert payload["summary"]["UNEXPLAINED_DELTA"] == 0


# ---------------------------------------------------------------- fixture 16


def test_reobservation_is_idempotent_and_current_afterwards(repo: Repo, producer: Any) -> None:
    repo.source("C", "corps de C")
    repo.commit("author C")

    applied = repo.build(write=True)
    assert applied["state"] == "REOBSERVED"
    assert applied["summary"]["FIELDS_REOBSERVED"] > 0
    after_apply = repo.registers_bytes()

    # Avant même de commettre les registres : CURRENT, rien ne bouge.
    check = repo.build(write=False)
    assert check["state"] == "CURRENT"
    assert check["summary"]["FIELDS_REOBSERVED"] == 0
    assert check["summary"]["UNEXPLAINED_DELTA"] == 0
    assert repo.registers_bytes() == after_apply

    again = repo.build(write=True)
    assert again["state"] == "CURRENT"
    assert repo.registers_bytes() == after_apply

    repo.commit("re-observe the registers")
    committed = repo.build(write=False)
    assert committed["state"] == "CURRENT"
    assert committed["source_set"]["added"] == []
    assert committed["summary"]["CAUSE_COMMITS"] == 0
    assert committed["cause"]["subject"] == "author C"


def test_cli_check_writes_nothing_and_apply_refuses_when_blocked(
    repo: Repo, producer: Any, capsys: pytest.CaptureFixture[str]
) -> None:
    repo.source("C", "corps de C")
    repo.commit("author C")
    before = repo.registers_bytes()

    assert producer.main(["--check"]) == 0
    assert repo.registers_bytes() == before
    assert not producer.JSON_TARGET.exists()
    assert "STATE=STALE_EXPLAINED" in capsys.readouterr().out

    repo.source("D", "non commis")
    assert producer.main(["--apply"]) == 1
    assert repo.registers_bytes() == before
    assert not producer.JSON_TARGET.exists()
    out = capsys.readouterr().out
    assert "STATE=BLOCKED" in out and "UNEXPLAINED added" in out

    repo.remove(repo.source_path("D"))
    assert producer.main(["--apply"]) == 0
    assert repo.registers_bytes() != before
    assert producer.JSON_TARGET.is_file() and producer.MD_TARGET.is_file()
    assert producer.main(["--check"]) == 0
    assert "STATE=CURRENT" in capsys.readouterr().out


# ---------------------------------------------------------------- fixture 17


def test_sets_and_digests_do_not_depend_on_creation_order(
    tmp_path: Path, producer: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    def scenario(order: list[str]) -> dict[str, Any]:
        fixture = Repo(tmp_path / f"repo-{'-'.join(order)}", producer, monkeypatch)
        for name in order:
            fixture.source(name, f"corps de {name}")
        fixture.commit("initial")
        fixture.seal()
        for name in reversed(order):
            fixture.source(f"N{name}", f"nouveau {name}")
        fixture.remove(fixture.source_path("A"))
        fixture.commit("mixed lot")
        return _sets(fixture.build())

    assert scenario(["A", "B", "C"]) == scenario(["C", "A", "B"])


# ---------------------------------------------------------------- fixture 18


def test_derived_outputs_are_not_inputs(repo: Repo, producer: Any) -> None:
    repo.source("C", "corps de C")
    repo.commit("author C")
    first = repo.build(write=False)

    assert producer.main(["--apply"]) == 0  # écrit registres + JSON + MD, rien n'est commis
    second = repo.build(write=False)

    assert _sets(second) == _sets(first)
    assert second["summary"]["UNEXPLAINED_DELTA"] == 0
    assert second["state"] == "CURRENT"


# ---------------------------------------------------------------- fixture 19


def test_web_ihm_like_lot_is_attributed_by_exact_sets(repo: Repo) -> None:
    """Grand retrait de clones, puis ajouts authentiques et évaluations modifiées."""

    clones = [repo.source(f"CLONE-{n:02d}", "copie synthétique") for n in range(1, 9)]
    stub = repo.source("METH-01", "stub", section="methodes")
    evals = [repo.source(f"EVAL-{k}", f"évaluation {k}", section="evaluations") for k in "AB"]
    repo.commit("filler and stubs")
    repo.seal()

    for clone in clones:
        repo.remove(clone)
    removal = repo.commit("remove synthetic filler copies")
    repo.seal("re-observe after the filler removal")

    methods = [repo.source(f"ME-00{n}", f"méthode {n}", section="methodes") for n in range(1, 5)]
    repo.remove(stub)
    authoring_1 = repo.commit("author four real méthodes and retire the stub")
    remediations = [
        repo.source(f"RE-C{n}", f"remédiation {n}", section="remediation") for n in range(1, 9)
    ]
    authoring_2 = repo.commit("author the eight missing remediations")
    for k in "AB":
        repo.source(f"EVAL-{k}", f"évaluation {k} étendue", section="evaluations")
    authoring_3 = repo.commit("extend both assessments")

    payload = repo.build()
    rows = _rows(payload)

    assert payload["source_set"]["added"] == sorted(methods + remediations)
    assert payload["source_set"]["removed"] == [stub]
    assert payload["source_set"]["modified_existing"] == sorted(evals)
    assert payload["summary"]["CAUSE_COMMITS"] == 3
    assert removal not in {sha for row in rows.values() for sha in row["cause_commits"]}
    assert all(rows[path]["cause_commits"] == [authoring_1] for path in methods + [stub])
    assert all(rows[path]["cause_commits"] == [authoring_2] for path in remediations)
    assert all(rows[path]["cause_commits"] == [authoring_3] for path in evals)
    assert payload["summary"]["UNEXPLAINED_DELTA"] == 0
    assert payload["summary"]["HUMAN_RECEIPTS_AFFECTED"] == 0
    assert payload["cause"]["sha"] == authoring_3

    repo.build(write=True)
    repo.commit("re-observe after the authoring lot")
    assert repo.build()["state"] == "CURRENT"


# ---------------------------------------------------------------- sealed fields


def test_sealed_and_immutable_fields_survive_reobservation(repo: Repo, producer: Any) -> None:
    campaign_before = json.loads(producer.CAMPAIGN_TARGET.read_text(encoding="utf-8"))
    status_before = json.loads(producer.STATUS_TARGET.read_text(encoding="utf-8"))
    repo.source("C", "corps de C")
    repo.commit("author C")

    payload = repo.build(write=True)

    campaign_after = json.loads(producer.CAMPAIGN_TARGET.read_text(encoding="utf-8"))
    status_after = json.loads(producer.STATUS_TARGET.read_text(encoding="utf-8"))
    assert campaign_after["sealed"] == campaign_before["sealed"]
    for key in producer.IMMUTABLE_TOP_LEVEL:
        assert campaign_after[key] == campaign_before[key]
        assert status_after[key] == status_before[key]
    assert campaign_after["observed"] != campaign_before["observed"]
    assert campaign_after["reason"].startswith(campaign_before["reason"])
    assert "ajouté 1, retiré 0 et modifié 0" in campaign_after["reason"]
    assert payload["summary"]["SEALED_FIELDS_MUTATED"] == 0
    registry = json.loads(producer.REGISTRY_PATH.read_text(encoding="utf-8"))
    assert registry["publication_approval"] is False


def test_a_declared_state_that_matches_no_tree_fails_closed(repo: Repo, producer: Any) -> None:
    campaign = json.loads(producer.CAMPAIGN_TARGET.read_text(encoding="utf-8"))
    campaign["observed"]["sources_ids_digest"] = "sha256:forged"
    producer.CAMPAIGN_TARGET.write_text(json.dumps(campaign) + "\n", encoding="utf-8")
    repo.commit("hand-edit the declared digest")

    with pytest.raises(producer.ReobservationError, match="aucun ancien source set autoritaire"):
        repo.build()


def test_a_rename_is_reported_as_removed_plus_added_with_an_identity_move(repo: Repo) -> None:
    old_path = repo.source_path("B")
    new_path = repo.source("B-RENAMED", "corps de B", object_id=f"{CHAPTER}-B")
    repo.remove(old_path)
    cause = repo.commit("move B")

    payload = repo.build()

    assert payload["source_set"]["removed"] == [old_path]
    assert payload["source_set"]["added"] == [new_path]
    assert payload["source_set"]["identity_moves"] == [
        {"id": f"{CHAPTER}-B", "from": old_path, "to": new_path}
    ]
    assert _rows(payload)[new_path]["cause_commits"] == [cause]
    assert payload["summary"]["UNEXPLAINED_DELTA"] == 0
