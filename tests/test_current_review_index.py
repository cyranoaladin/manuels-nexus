"""Mutations of the current view: evidence must not survive changed content."""
from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


@pytest.fixture
def gate():
    path = ROOT / "scripts/build_current_review_index.py"
    assert path.is_file(), "current review index producer missing"
    spec = importlib.util.spec_from_file_location("current_review_index_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def corpus(tmp_path):
    chapter = "1SPE-FIXTURE"
    directory = tmp_path / "Mathematiques/manuel-maths/chapitres" / chapter
    source = directory / "methodes/FIX-ME-001.tex"
    source.parent.mkdir(parents=True)
    meta = {"id": "FIX-ME-001", "type_objet": "methode", "status": "generated",
            "chapitre": chapter, "capacites_codes": ["C1"]}
    source.write_text('% META: ' + json.dumps(meta) + '\nLa dérivée de $x^2$ est $2x$.\n')
    (directory / "contrat.yaml").write_text("chapitre: 1SPE-FIXTURE\n")
    inv = {"manuals": {"1SPE": {"chapters": {chapter: {
        "contract_path": str((directory / "contrat.yaml").relative_to(tmp_path)),
        "objects": [{"id": meta["id"], "path": str(source.relative_to(tmp_path)),
                     "metadata": meta}],
    }}}}}
    return tmp_path, source, inv


def build(gate, corpus, **kwargs):
    root, source, inventory = corpus
    return gate.build(root, inventory, reviews=kwargs.pop("reviews", []),
                      retired=kwargs.pop("retired", []),
                      new_paths={str(source.relative_to(root))}, **kwargs)


def review_for(index):
    row = index["objects"][0]
    return {
        "review_id": "FIX-INDEPENDENT-001",
        "reviewer": {"actor_id": "independent-test-reviewer", "is_human": False,
                     "independent_from_author": True},
        "object_id": row["object_id"], "path": row["path"],
        "source_sha256": row["source_sha256"],
        "semantic_digest": row["semantic_digest"],
        "dependency_digest": row["dependency_digest"],
        "dimensions": {name: {"state": "VALIDATED_BY_EVIDENCE",
                              "rationale": "Reviewed the actual source independently."}
                       for name in row["required_review_dimensions"]},
    }


def test_every_current_object_is_unique_and_pending_without_review(gate, corpus):
    result = build(gate, corpus)
    assert result["summary"]["CURRENT_REVIEW_INDEX_TOTAL"] == 1
    assert result["summary"]["NEW_AUTHORING_REVIEW_PENDING"] == 1
    assert result["objects"][0]["human_approval"] == "PENDING"
    assert {d["state"] for d in result["objects"][0]["reviews"].values()} == {"PENDING"}


def test_an_uncommitted_new_source_is_still_new_authoring(gate, corpus, monkeypatch):
    root, source, _ = corpus
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=Fixture",
                    "-c", "user.email=fixture@example.invalid", "commit", "-q",
                    "--allow-empty", "-m", "test baseline"], check=True)
    baseline = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    monkeypatch.setattr(gate, "DECONTAMINATION_COMMIT", baseline)
    assert str(source.relative_to(root)) in gate._new_paths(root)


def test_data_review_is_never_closed_by_unchecked_applicability(gate, corpus):
    result = build(gate, corpus)
    row = result["objects"][0]
    assert "DATA_REVIEW" in row["required_review_dimensions"]
    assert row["reviews"]["DATA_REVIEW"]["state"] == "PENDING"


def test_duplicate_canonical_object_is_refused(gate, corpus):
    root, source, inv = corpus
    objects = inv["manuals"]["1SPE"]["chapters"]["1SPE-FIXTURE"]["objects"]
    objects.append(copy.deepcopy(objects[0]))
    with pytest.raises(ValueError, match="duplicate"):
        build(gate, corpus)


def test_inventory_cannot_omit_a_current_source(gate, corpus):
    corpus[2]["manuals"]["1SPE"]["chapters"]["1SPE-FIXTURE"]["objects"] = []
    with pytest.raises(ValueError, match="source set"):
        build(gate, corpus)


def test_digest_bound_review_closes_only_machine_review(gate, corpus):
    review = review_for(build(gate, corpus))
    result = build(gate, corpus, reviews=[review])
    assert result["summary"]["NEW_AUTHORING_REVIEW_PENDING"] == 0
    assert result["objects"][0]["human_approval"] == "PENDING"


@pytest.mark.parametrize("field", ["evidence_note", "oracle_receipt"])
@pytest.mark.parametrize("mutation", ["changed", "removed"])
def test_referenced_review_evidence_cannot_change_or_disappear(gate, corpus, field, mutation):
    root = corpus[0]
    evidence = root / "audit/read-evidence.json"
    evidence.parent.mkdir()
    evidence.write_text('{"scope": "actual independent reading"}')
    review = review_for(build(gate, corpus))
    review[field] = {"path": str(evidence.relative_to(root)),
                     "sha256": gate.sha256(evidence.read_bytes())}
    valid = build(gate, corpus, reviews=[review])
    assert valid["summary"]["NEW_AUTHORING_REVIEW_PENDING"] == 0
    assert valid["input_digests"][str(evidence.relative_to(root))] == review[field]["sha256"]
    if mutation == "removed":
        evidence.unlink()
    else:
        evidence.write_text('{"scope": "different source, no reading"}')
    stale = build(gate, corpus, reviews=[review])
    assert stale["summary"]["NEW_AUTHORING_REVIEW_PENDING"] == 1
    assert stale["summary"]["CURRENT_REVIEW_INDEX_STALE_EVIDENCE"] == 0
    assert stale["rejected_review_evidence"][0]["reason"] == "STALE_SUPPORTING_EVIDENCE"


@pytest.mark.parametrize("kind", ["td", "cours"])
def test_embedded_correction_requires_alignment_review(gate, kind):
    dimensions = gate._required_dimensions(
        "1SPE", {"type_objet": kind},
        r"\begin{exercice}{Q1} Tracer la courbe.\end{exercice}"
        r"\begin{corrige}{Q1} Sa description.\end{corrige}",
    )
    assert "CORRECTION_ALIGNMENT_REVIEW" in dimensions


def test_td_without_named_exercise_environment_still_requires_a_correction(gate):
    dimensions = gate._required_dimensions(
        "1SPE", {"type_objet": "td"},
        r"\begin{enumerate}\item Calculer la distance au segment.\end{enumerate}",
    )
    assert "CORRECTION_ALIGNMENT_REVIEW" in dimensions


def test_finding_in_an_additional_review_dimension_prevents_closure(gate, corpus):
    review = review_for(build(gate, corpus))
    review["dimensions"]["FIGURE_REVIEW"] = {
        "state": "PENDING", "rationale": "The requested graph is missing."
    }
    result = build(gate, corpus, reviews=[review])
    assert result["summary"]["NEW_AUTHORING_REVIEW_PENDING"] == 1
    assert "FIGURE_REVIEW" in result["objects"][0]["required_review_dimensions"]


def test_changed_sign_invalidates_the_old_review(gate, corpus):
    review = review_for(build(gate, corpus))
    source = corpus[1]
    source.write_text(source.read_text().replace("$2x$", "$-2x$"))
    result = build(gate, corpus, reviews=[review])
    assert result["summary"]["NEW_AUTHORING_REVIEW_PENDING"] == 1
    assert result["rejected_review_evidence"][0]["reason"] == "STALE_SOURCE_DIGEST"
    assert result["summary"]["CURRENT_REVIEW_INDEX_STALE_EVIDENCE"] == 0


def test_changed_contract_invalidates_the_old_review(gate, corpus):
    review = review_for(build(gate, corpus))
    (corpus[1].parent.parent / "contrat.yaml").write_text("capacites: [C2]\n")
    result = build(gate, corpus, reviews=[review])
    assert result["rejected_review_evidence"][0]["reason"] == "STALE_DEPENDENCY_DIGEST"
    assert result["summary"]["NEW_AUTHORING_REVIEW_PENDING"] == 1


def test_reused_retired_id_with_new_content_stays_current_without_inheritance(gate, corpus):
    before = build(gate, corpus)["objects"][0]
    retired = [{"object_id": before["object_id"], "path": before["path"],
                "body_digest": before["body_digest"], "retirement_reason": "fixture"}]
    source = corpus[1]
    source.write_text(source.read_text().replace("$x^2$", "$x^3$").replace("$2x$", "$3x^2$"))
    result = build(gate, corpus, retired=retired)
    assert result["summary"]["CURRENT_REVIEW_INDEX_TOTAL"] == 1
    assert result["summary"]["CURRENT_REVIEW_INDEX_RETIRED_OBJECTS"] == 0
    assert result["objects"][0]["historical_versions"]
    assert result["summary"]["NEW_AUTHORING_REVIEW_PENDING"] == 1


def test_reintroduced_retired_body_is_refused(gate, corpus):
    before = build(gate, corpus)["objects"][0]
    with pytest.raises(ValueError, match="retired content"):
        build(gate, corpus, retired=[{"object_id": before["object_id"],
              "path": before["path"], "body_digest": before["body_digest"]}])


def test_authentic_source_of_a_retired_clone_is_not_itself_retired(gate, corpus):
    before = build(gate, corpus)["objects"][0]
    result = build(gate, corpus, retired=[{
        "object_id": "OTHER-REMOVED-001", "path": "elsewhere/removed.tex",
        "body_digest": before["body_digest"],
    }])
    assert result["summary"]["CURRENT_REVIEW_INDEX_TOTAL"] == 1


@pytest.mark.parametrize("mutation", ["human_identity", "human_verdict", "unknown_dimension"])
def test_independent_review_cannot_forge_human_authority_or_dimensions(gate, corpus, mutation):
    review = review_for(build(gate, corpus))
    if mutation == "human_identity":
        review["reviewer"]["is_human"] = True
    elif mutation == "human_verdict":
        review["dimensions"]["SCIENTIFIC_REVIEW"]["state"] = "HUMAN_APPROVED"
    else:
        review["dimensions"]["SELF_APPROVAL"] = {"state": "VALIDATED_BY_EVIDENCE"}
    with pytest.raises(ValueError):
        build(gate, corpus, reviews=[review])


def test_partial_review_keeps_other_dimensions_pending(gate, corpus):
    review = review_for(build(gate, corpus))
    review["dimensions"] = {"SCIENTIFIC_REVIEW": review["dimensions"]["SCIENTIFIC_REVIEW"]}
    result = build(gate, corpus, reviews=[review])
    assert result["objects"][0]["reviews"]["SCIENTIFIC_REVIEW"]["state"] == "VALIDATED_BY_EVIDENCE"
    assert result["summary"]["NEW_AUTHORING_REVIEW_PENDING"] == 1


def test_sources_changing_during_read_are_refused(gate, corpus, monkeypatch):
    original = gate._review_evidence

    def mutate(*args, **kwargs):
        corpus[1].write_text(corpus[1].read_text() + "A changed assertion.\n")
        return original(*args, **kwargs)

    monkeypatch.setattr(gate, "_review_evidence", mutate)
    with pytest.raises(ValueError, match="changed during"):
        build(gate, corpus)


def test_derived_historical_outputs_cannot_change_current_evidence(gate, corpus):
    before = build(gate, corpus)
    audit = corpus[0] / 'audit'
    audit.mkdir()
    (audit / 'NON_FORMALIZABLE_REVIEW_CLOSURE.json').write_text('{"summary":{"PENDING":0}}')
    after = build(gate, corpus)
    assert gate.comparable(before) == gate.comparable(after)


def test_a_consumer_rejects_an_index_when_sources_have_changed(gate, corpus):
    index = build(gate, corpus)
    corpus[1].write_text(corpus[1].read_text().replace('$2x$', '$-2x$'))
    with pytest.raises(ValueError, match='changed'):
        gate.assert_current(corpus[0], index)


def test_new_authoring_consumer_uses_current_review_dimensions(gate, corpus, monkeypatch):
    import build_new_authoring_review_debt as consumer
    index = build(gate, corpus, reviews=[review_for(build(gate, corpus))])
    audit = corpus[0] / 'audit'
    audit.mkdir()
    (audit / 'CAPACITY_CONTENT_ALIGNMENT.json').write_text('{"assignments": []}')
    (audit / 'EX_CO_GRAPH.json').write_text('{"relations": []}')
    import build_current_review_index as public_gate
    monkeypatch.setattr(public_gate, 'build_fresh', lambda *a, **kw: index)
    result = consumer.build(corpus[0])
    assert result['summary']['NEW_AUTHORING_OBJECTS'] == 1
    assert result['summary']['NEW_AUTHORING_REVIEW_PENDING'] == 0
    assert result['entries'][0]['editorial_review'] == 'VALIDATED_BY_EVIDENCE'
    assert result['human_review_required'] is True


def test_nonformal_consumer_refuses_legacy_containment_credit(gate, corpus, monkeypatch):
    import build_non_formalizable_review_closure as consumer
    import build_current_review_index as public_gate
    index = build(gate, corpus)
    row = index['objects'][0]
    row['mathematics_classification'] = 'MATHEMATICAL_NON_FORMALIZABLE'
    monkeypatch.setattr(public_gate, 'build_fresh', lambda *a, **kw: index)
    old = {'objects': [{'path': row['path'], 'state': 'TRULY_NOT_REQUIRING_MATHEMATICAL_REVIEW',
                        'evidence': 'formula substring containment'}]}
    monkeypatch.setattr(public_gate, 'historical_payload', lambda *a: json.dumps(old).encode())
    result = consumer.build(corpus[0])
    assert result['summary']['MATHEMATICAL_NON_FORMALIZABLE_REVIEW_PENDING'] == 1
    assert result['objects'][0]['legacy_classification']['state'] == 'TRULY_NOT_REQUIRING_MATHEMATICAL_REVIEW'
    assert result['objects'][0]['state'] == 'PENDING'


def test_nonformal_consumer_closes_only_a_digest_bound_scientific_review(gate, corpus, monkeypatch):
    import build_non_formalizable_review_closure as consumer
    import build_current_review_index as public_gate
    index = build(gate, corpus, reviews=[review_for(build(gate, corpus))])
    index['objects'][0]['mathematics_classification'] = 'MATHEMATICAL_NON_FORMALIZABLE'
    monkeypatch.setattr(public_gate, 'build_fresh', lambda *a, **kw: index)
    monkeypatch.setattr(public_gate, 'historical_payload', lambda *a: b'{"objects": []}')
    result = consumer.build(corpus[0])
    assert result['summary']['MATHEMATICAL_NON_FORMALIZABLE_REVIEW_PENDING'] == 0
    assert result['objects'][0]['state'] == 'SEMANTICALLY_REVIEWED'
    assert result['objects'][0]['review']['review_id'] == 'FIX-INDEPENDENT-001'


def test_observation_distinguishes_a_worktree_from_an_exact_head(gate, corpus, monkeypatch):
    monkeypatch.setattr(gate.freshness, 'head_sha', lambda root: 'fixture-base-head')
    monkeypatch.setattr(gate, 'historical_payload', lambda *a: None)
    result = build(gate, corpus)
    assert result['observation']['base_head'] == 'fixture-base-head'
    assert 'worktree_status' in result['observation']
    assert result['observation']['scope'] == 'WORKTREE_BOUND_BY_INPUT_DIGESTS'


@pytest.mark.parametrize('code_source', ['inline_python', 'chapter_python_dependency'])
def test_mathematics_code_requires_an_execution_review(gate, corpus, code_source):
    if code_source == 'inline_python':
        corpus[1].write_text(corpus[1].read_text() + '\\begin{python}\nprint(1)\n\\end{python}\n')
    else:
        path = corpus[1].parent.parent / 'python/program.py'
        path.parent.mkdir()
        path.write_text('print(1)\n')
    row = build(gate, corpus)['objects'][0]
    assert 'CODE_EXECUTION_REVIEW' in row['required_review_dimensions']
    assert row['reviews']['CODE_EXECUTION_REVIEW']['state'] == 'PENDING'


def test_new_authoring_oracle_count_rejects_a_stale_source(gate, corpus):
    import build_new_authoring_review_debt as authoring
    root, source, _ = corpus
    directory = source.parent.parent
    validations = directory / "validations"
    validations.mkdir()
    (validations / (source.stem + ".sympy.json")).write_text(json.dumps({
        "objet_id": source.stem, "gate": "sympy", "verdict": "pass",
        "source_path": str(source.relative_to(root)), "source_sha256": gate.sha256(source.read_bytes()),
    }))
    source.write_text(source.read_text().replace("$2x$", "$-2x$"))
    assert authoring._oracle_verdict(directory.name, source.stem, root) == "stale"


@pytest.mark.parametrize('dependency', ['external_figure', 'programme_mapping'])
def test_figure_and_programme_dependencies_invalidate_old_reviews(gate, corpus, dependency):
    root, source, _ = corpus
    if dependency == 'external_figure':
        target = root / 'shared/plot.svg'
        source.write_text(source.read_text() + '\\includegraphics{shared/plot.svg}\n')
        before, after = '<svg>positive axis</svg>', '<svg>negative axis</svg>'
    else:
        target = root / 'audit/official_program_coverage/1SPE.json'
        before, after = '{"capacity":"C1"}', '{"capacity":"C2"}'
    target.parent.mkdir(parents=True)
    target.write_text(before)
    review = review_for(build(gate, corpus))
    target.write_text(after)
    result = build(gate, corpus, reviews=[review])
    assert result['summary']['NEW_AUTHORING_REVIEW_PENDING'] == 1
    assert result['rejected_review_evidence'][0]['reason'] == 'STALE_DEPENDENCY_DIGEST'


def test_external_dependency_cannot_escape_the_repository(gate, corpus):
    corpus[1].write_text(corpus[1].read_text() + '\\input{/outside/forbidden.tex}\n')
    with pytest.raises(ValueError, match='outside repository'):
        build(gate, corpus)


def test_missing_declared_dependency_is_not_silently_omitted(gate, corpus):
    corpus[1].write_text(corpus[1].read_text() + '\\lstinputlisting{missing.py}\n')
    with pytest.raises(ValueError, match='missing or ambiguous'):
        build(gate, corpus)


def test_old_aggregate_passes_do_not_replace_current_semantic_reviews(gate, corpus, monkeypatch):
    import build_new_authoring_review_debt as consumer
    import build_current_review_index as public_gate
    root, source, inventory = corpus
    obj = inventory['manuals']['1SPE']['chapters']['1SPE-FIXTURE']['objects'][0]
    exercise = source.parent.parent / 'exercices/FIX-ME-001.tex'
    exercise.parent.mkdir()
    source.rename(exercise)
    obj['path'] = str(exercise.relative_to(root))
    obj['metadata']['type_objet'] = 'exercice'
    exercise.write_text('% META: ' + json.dumps(obj['metadata']) + '\nCalculer la dérivée de $x^2$.\n')
    corpus = (root, exercise, inventory)
    index = build(gate, corpus)
    row = index['objects'][0]
    monkeypatch.setattr(public_gate, 'build_fresh', lambda *a, **kw: index)
    audit = corpus[0] / 'audit'
    audit.mkdir()
    (audit / 'CAPACITY_CONTENT_ALIGNMENT.json').write_text(json.dumps({'assignments': [
        {'object_id': row['object_id'], 'capacity': 'C1', 'state': 'ALIGNED'}]}))
    (audit / 'EX_CO_GRAPH.json').write_text(json.dumps({'relations': [
        {'exercise_id': row['object_id'], 'classifications': ['ANSWER_COVERAGE_ESTABLISHED']}]}))
    result = consumer.build(corpus[0])
    assert result['summary']['CAPACITY_SEMANTICALLY_PROVEN'] == 0
    assert result['summary']['ANSWER_COVERAGE_ESTABLISHED'] == 0
    assert result['summary']['ANSWER_COVERAGE_REVIEW_PENDING'] == 1
    assert result['summary']['CAPACITY_REVIEW_PENDING'] == 1
    assert result['summary']['NEW_AUTHORING_NEAR_CLONES'] is None
    assert result['summary']['NEAR_CLONE_REVIEW_STATUS'] == 'NOT_COMPUTED_BY_THIS_PRODUCER'


def test_nonformal_render_does_not_lose_review_counts_or_claim_zero_findings():
    import build_non_formalizable_review_closure as consumer
    summary = {'MATHEMATICAL_NON_FORMALIZABLE_TOTAL': 2,
               'MATHEMATICAL_NON_FORMALIZABLE_REVIEW_PENDING': 1,
               'COVERED_BY_QCM_PROOF_CHAIN': 0, 'REVIEWED': 1,
               'DEFECTS_FOUND': None}
    rendered = consumer.render_md({'summary': summary,
        'by_type': {'methode': {'SEMANTICALLY_REVIEWED': 1, 'PENDING': 1}}})
    assert '| methode | 1 | 0 | 1 |' in rendered
    assert 'Non évalué par ce registre' in rendered


@pytest.mark.parametrize('kind', ['coup_de_pouce', 'amenagee', 'remediation'])
def test_satellites_require_review_of_their_parent_or_embedded_correction(gate, kind):
    dimensions = gate._required_dimensions('1SPE', {'type_objet': kind}, 'Aide ou remédiation.')
    assert 'CORRECTION_ALIGNMENT_REVIEW' in dimensions


def test_terminal_specialty_alias_binds_its_actual_programme_mapping(gate, corpus):
    root, source, inventory = corpus
    directory = source.parent.parent
    target = root / 'audit/official_program_coverage/TSPE.json'
    target.parent.mkdir(parents=True)
    target.write_text('{"manual":"TSPE"}')
    paths = gate._dependencies(root, {'contract_path': str((directory/'contrat.yaml').relative_to(root))}, 'TSPE_2026_2027')
    assert str(target.relative_to(root)) in paths


def test_actual_normative_text_and_registry_invalidate_programme_review(gate, corpus):
    root, source, _ = corpus
    registry = root / 'docs/programmes/PROGRAMMES_2026_2027.yaml'
    registry.parent.mkdir(parents=True)
    registry.write_text('sources:\n  OFFICIAL:\n    fichier: official.txt\nmanuels:\n  - manual_id: 1SPE\n    programme_source: OFFICIAL\n')
    official = root / 'official.txt'
    official.write_text('Applicable programme: derivative of the square.')
    review = review_for(build(gate, corpus))
    official.write_text('Changed official requirement.')
    result = build(gate, corpus, reviews=[review])
    assert result['rejected_review_evidence'][0]['reason'] == 'STALE_DEPENDENCY_DIGEST'


@pytest.mark.parametrize("filename", ["verify_sympy.py", "execution_protocol.py"])
def test_oracle_verifier_change_invalidates_its_review_binding(gate, corpus, filename):
    root, source, _ = corpus
    verifier = source.parents[3] / 'scripts' / filename
    verifier.parent.mkdir()
    verifier.write_text('assert executed_assertions > 0\n')
    review = review_for(build(gate, corpus))
    verifier.write_text('pass\n')
    result = build(gate, corpus, reviews=[review])
    assert result['rejected_review_evidence'][0]['reason'] == 'STALE_DEPENDENCY_DIGEST'
