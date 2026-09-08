"""Check an adaptation's source relationship, never historical truth.

The dates are taken from the parent's current correction. Matching them does
not prove dates or associations: those require the documented reading.
"""
import json
import re
from pathlib import Path

from NSI.scripts import verify_python as execution

ROOT = Path(__file__).resolve().parents[2]
CHAPTER = ROOT / 'NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE'
ADAPTED = CHAPTER / 'amenagee/TNSI-HIST-AM-EXTRAIT.tex'
PARENT_CORRECTION = CHAPTER / 'corriges/TNSI-HIST-CO-001.tex'
CHOICE_YEAR = re.compile(r'\\textbf\{[A-C]\.\}\s*\$(\d{4})\$')


def choices_match_parent(adapted, parent_correction):
    offered = CHOICE_YEAR.findall(adapted)
    parent = re.findall(r'\\textbf\{(\d{4})\}', parent_correction)
    return bool(parent) and len(offered) == len(parent) and sorted(offered) == sorted(parent)


def test_adapted_chronology_uses_the_current_parent_reference_set():
    assert choices_match_parent(ADAPTED.read_text(), PARENT_CORRECTION.read_text())


def test_changed_reference_set_in_an_adaptation_is_detected():
    text = ADAPTED.read_text()
    parent = PARENT_CORRECTION.read_text()
    assert choices_match_parent(text, parent)
    changed = CHOICE_YEAR.sub(
        lambda m: m.group(0).replace(m.group(1), str(int(m.group(1)) + 1)),
        text, count=1,
    )
    assert not choices_match_parent(changed, parent)


def test_declared_adaptation_parents_resolve_to_actual_source_objects():
    meta = json.loads(ADAPTED.read_text().splitlines()[0].removeprefix('% META: '))
    ids = []
    for path in (CHAPTER / 'exercices').glob('*.tex'):
        item = json.loads(path.read_text().splitlines()[0].removeprefix('% META: '))
        ids.append(item['id'])
    assert len(set(meta['derive_de'])) == len(meta['derive_de'])
    assert all(ids.count(parent) == 1 for parent in meta['derive_de'])


def test_adapted_documentary_questions_receive_no_execution_credit():
    result = execution.check_object(ADAPTED)
    assert result['verdict'] == 'manual_review'
    assert result['certifies_documentary_claims'] is False
