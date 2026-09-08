"""Unsupported mathematical claims remain visible, never a zero-defect proof."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import audit_variance_sigma_consistency as audit


def write_object(directory, body):
    path = directory / 'FIXTURE.tex'
    path.write_text('% META: ' + json.dumps({'id': 'FIXTURE', 'chapitre': 'TEST',
                                           'type_objet': 'corrige'}) + '\n' + body)
    return path


def test_irrational_sigma_is_preserved_as_an_unverified_claim(tmp_path):
    body = r'$V(X)=4$ et $\sigma(X)=\sqrt{3}$.'
    assert len(audit.extract_claims(body)) == 2
    findings = audit.audit_object(write_object(tmp_path, body), 'TEST', [])
    assert any(f.defect_class == 'UNPARSED_MATHEMATICAL_CLAIM'
               and f.severity == 'CERTIFICATION_BLOCKER' for f in findings)


def test_even_a_correct_unsupported_radical_remains_unverified(tmp_path):
    findings = audit.audit_object(write_object(tmp_path,
        r'$V(X)=3$ et $\sigma(X)=\sqrt{3}$.'), 'TEST', [])
    assert not any(f.severity == 'P0' for f in findings)
    assert any(f.severity == 'CERTIFICATION_BLOCKER' for f in findings)


def test_unreadable_link_is_not_erased_by_a_readable_value(tmp_path):
    findings = audit.audit_object(write_object(tmp_path,
        r'$V(X)=4$ et $\sigma(X)=\sqrt{3}=2$.'), 'TEST', [])
    assert any(f.defect_class == 'UNPARSED_MATHEMATICAL_CLAIM' for f in findings)


def test_unsupported_variance_is_not_replaced_by_an_earlier_value(tmp_path):
    findings = audit.audit_object(write_object(tmp_path,
        r'$V(X)=4$. Puis $V(X)=\sqrt{3}$. Enfin $\sigma(X)=2$.'), 'TEST', [])
    assert any(f.defect_class == 'UNPARSED_MATHEMATICAL_CLAIM' for f in findings)
    assert any(f.defect_class == 'UNVERIFIED_VARIANCE_DEPENDENCY' for f in findings)


def test_no_number_in_a_claim_does_not_remove_it_from_the_population():
    claims = audit.extract_claims(r'$V(X)=np(1-p)$ et $\sigma(X)=\sqrt{V(X)}$.')
    assert len(claims) == 2


def test_cli_is_red_for_unverified_claim_even_without_product_p0(tmp_path, monkeypatch, capsys):
    chapter = tmp_path / 'TEST'
    chapter.mkdir()
    write_object(chapter, r'$V(X)=3$ et $\sigma(X)=\sqrt{3}$.')
    monkeypatch.setattr(audit, 'MATH_CHAPTERS', tmp_path)
    assert audit.main([]) == 1
    report = json.loads(capsys.readouterr().out)
    assert report['p0_count'] == 0
    assert report['unparsed_claim_count'] == 1
    assert report['certification_blocker_count'] == 1


def test_exact_rational_claims_still_verify(tmp_path):
    body = r'$V(X)=9/4$ et $\sigma(X)=3/2$.'
    assert len(audit.extract_claims(body)) == 2
    assert audit.audit_object(write_object(tmp_path, body), 'TEST', []) == []
