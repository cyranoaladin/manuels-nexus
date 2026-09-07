"""La classification des 89 qualifications périmées doit être recalculable.

Ces 89 blocages sont, depuis la correction de l'étage `check`, le seul obstacle
que le gate rencontre. La décision de re-qualifier appartient à l'humain — la
file le dit elle-même, `machine_cannot_requalify: true`. Ce que la machine peut
faire, et doit faire avant de solliciter cette décision, c'est établir les
faits : ces modifications changent-elles autre chose que des accents ?

Le test ne fait pas confiance à l'étiquette déposée. Il retrouve la version
qualifiée dans l'historique par son empreinte, désaccentue les deux versions,
et recompare. Sur les 89, l'accord doit être total.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import unicodedata
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "audit/METHOD_REQUALIFICATION_QUEUE.json"


def _strip_accents(text: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )


def _blob_with_digest(relative: str, digest: str) -> str | None:
    revisions = subprocess.run(
        ["git", "log", "--all", "--format=%H", "--", relative],
        cwd=ROOT, capture_output=True, text=True, check=True,
    ).stdout.split()
    for revision in revisions:
        blob = subprocess.run(
            ["git", "show", f"{revision}:{relative}"], cwd=ROOT, capture_output=True,
        )
        if blob.returncode:
            continue
        text = blob.stdout.decode("utf-8")
        if hashlib.sha256(text.encode("utf-8")).hexdigest() == digest:
            return text
    return None


@pytest.fixture(scope="module")
def queue():
    return json.loads(QUEUE.read_text(encoding="utf-8"))


def test_the_queue_approves_nothing(queue) -> None:
    assert queue["approves_nothing"] is True
    assert queue["machine_cannot_requalify"] is True


def test_every_item_is_stale_and_none_is_silently_current(queue) -> None:
    states = {item["state"] for item in queue["items"]}
    assert states == {"STALE"}
    assert len(queue["items"]) == 89


def test_every_classification_is_independently_reproducible(queue) -> None:
    """L'étiquette déposée est recalculée depuis l'historique, pas crue."""
    desaccords = []
    introuvables = []
    for item in queue["items"]:
        relative = item["source"]
        current = (ROOT / relative).read_text(encoding="utf-8")
        assert hashlib.sha256(current.encode("utf-8")).hexdigest() == \
            item["current_source_sha"], relative
        before = _blob_with_digest(relative, item["qualified_source_sha"])
        if before is None:
            introuvables.append(relative)
            continue
        if before == current:
            recomputed = "UNCHANGED"
        elif _strip_accents(before) == _strip_accents(current):
            recomputed = "ACCENT_ONLY"
        else:
            recomputed = "SUBSTANTIVE_CHANGE"
        if recomputed != item["change_class"]:
            desaccords.append((relative, item["change_class"], recomputed))
    assert introuvables == []
    assert desaccords == []


def test_the_split_is_eighty_six_and_three(queue) -> None:
    """Le partage est mesuré, et c'est lui qui sera soumis à l'humain."""
    import collections

    classes = collections.Counter(i["change_class"] for i in queue["items"])
    assert classes == {"ACCENT_ONLY": 86, "SUBSTANTIVE_CHANGE": 3}


def test_a_substantive_change_can_never_be_called_accent_only() -> None:
    """La frontière est exacte : un seul caractère non diacritique suffit."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import build_method_requalification_queue as producer

    assert producer.classify_change("é", "e") == "ACCENT_ONLY"
    assert producer.classify_change("é", "é") == "UNCHANGED"
    assert producer.classify_change("2x", "3x") == "SUBSTANTIVE_CHANGE"
    assert producer.classify_change("é2", "e3") == "SUBSTANTIVE_CHANGE"
