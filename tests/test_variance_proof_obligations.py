"""A root or matching number does not prove the complete variance/sigma claim."""
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import audit_variance_sigma_consistency as A


def run(tmp_path, body, verify='', chapter_variances=None):
    path = tmp_path / 'FIXTURE.tex'
    path.write_text('% META: ' + json.dumps({'id': 'FIXTURE', 'chapitre': 'TEST',
                    'type_objet': 'corrige'}) + '\n' + verify + body)
    return A.audit_object(path, 'TEST', chapter_variances or [])


def test_explicit_root_is_compared_to_given_variance(tmp_path):
    findings = run(tmp_path, r'$V(X)=4$ et $\sigma(X)=\sqrt{9}$.')
    assert any(f.defect_class == 'ROOT_MISMATCH' and f.severity == 'P0' for f in findings)


@pytest.mark.parametrize('verify', [
    '% BEGIN-VERIFY\n% # number3944 only\n% END-VERIFY\n',
    '% BEGIN-VERIFY\n% assert 3944 == 3944\n% END-VERIFY\n',
    '% BEGIN-VERIFY\n% assert round(float(sqrt(15552000))) == 3944\n% END-VERIFY\n',
])
def test_unbound_unexecuted_oracle_text_is_not_evidence(tmp_path, verify):
    findings = run(tmp_path, r'$\sigma\approx3944$.', verify)
    assert any(f.severity == 'CERTIFICATION_BLOCKER' for f in findings)


def test_numeric_coincidence_elsewhere_is_not_evidence_inheritance(tmp_path):
    findings = run(tmp_path, r'$\sigma(X)=3$.', chapter_variances=[9])
    assert any(f.severity == 'CERTIFICATION_BLOCKER' for f in findings)


@pytest.mark.parametrize('body', [
    r'$V(X)=4=9$ et $\sigma(X)=3$.',
    r'$V(X)=9007199254740992=9007199254740993$.',
    r'$V(X)=4$. $\sigma(X)=2=3$.',
    r'$V(X)=np(1-p)=4=9$.',
])
def test_unequal_exact_links_are_detected_with_exact_arithmetic(tmp_path, body):
    findings = run(tmp_path, body)
    assert any(f.defect_class == 'EXACT_EQUALITY_MISMATCH'
               and f.severity == 'P0' for f in findings)


@pytest.mark.parametrize('body', [
    r'$V(X)=9$ et $\sigma(X)=\sqrt{9}$.',
    r'$V(X)=9/4$ et $\sigma(X)=\sqrt{9/4}$.',
    r'$V(X)=1+3=4$ et $\sigma(X)=\sqrt{4}=2$.',
    r'$V(X)=100*5/12=125/3\approx41{,}7$. $\sigma(X)\approx6{,}45$.',
])
def test_supported_consistent_relations_remain_verified(tmp_path, body):
    assert run(tmp_path, body) == []
