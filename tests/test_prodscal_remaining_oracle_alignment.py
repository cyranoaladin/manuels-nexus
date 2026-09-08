"""Les quatre anciens couples doivent vérifier leur contenu réel et leurs domaines."""
from pathlib import Path
import ast
import json
import re
import pytest

from tests.test_prodscal_remaining_scientific_regressions import _run_fixture

ROOT=Path(__file__).resolve().parents[1]
CHAPTER=ROOT/'Mathematiques/manuel-maths/chapitres/1SPE-PRODUIT-SCALAIRE'


def source(n,kind='EX'):
    folder='exercices' if kind=='EX' else 'corriges'
    return (CHAPTER/folder/f'1SPE-PRODSCAL-{kind}-{n:03}.tex').read_text()


def oracle(text):
    block=text.split('% BEGIN-VERIFY')[1].split('% END-VERIFY')[0]
    return '\n'.join(line[2:] for line in block.splitlines() if line.startswith('% '))


def printed(text):
    return '\n'.join(line for line in text.splitlines() if not line.lstrip().startswith('%'))


@pytest.mark.parametrize('n',[5,16,18,47])
def test_metadata_duration_matches_the_actual_exercise(n):
    text=source(n)
    metadata=json.loads(text.splitlines()[0].split('% META: ')[1])
    duration=int(re.search(r'\\begin\{exercice\}\{[^}]+\}\{\d+\}\{(\d+)\}',text).group(1))
    assert metadata['duree_min'] == duration
    assert metadata['status'] == 'generated'


def test_coordinate_oracle_uses_the_actual_four_vectors():
    assert 'repère orthonormé' in printed(source(5))
    for kind in ['EX','CO']:
        code=oracle(source(5,kind))
        assert 'A = Matrix([1, 2])' in code
        assert 'B = Matrix([3, 5])' in code
        assert 'C = Matrix([0, 6])' in code
        assert 'BA.dot(BC) == 3' in code
        assert '-17' not in code


@pytest.mark.parametrize('n',[16,18])
@pytest.mark.parametrize('kind',['EX','CO'])
def test_no_reflexive_assertion_or_simplify_wrapper_counts_as_proof(n,kind):
    tree=ast.parse(oracle(source(n,kind)))
    for node in ast.walk(tree):
        if isinstance(node,ast.Assert) and isinstance(node.test,ast.Compare):
            left=node.test.left
            if isinstance(left,ast.Call) and isinstance(left.func,ast.Name) and left.func.id=='simplify' and len(left.args)==1:
                left=left.args[0]
            for comparator in node.test.comparators:
                assert ast.dump(left) != ast.dump(comparator),'Reflexive assertion'


def test_polarization_data_are_realizable_vectors_not_only_scalar_repetition():
    for kind in ['EX','CO']:
        code=oracle(source(16,kind))
        assert 'u = Matrix([3, 0])' in code
        assert 'v = Matrix([Rational(5, 2), 5*sqrt(3)/2])' in code
        assert '(u+v).dot(u+v) == 49' in code
        assert 'u.dot(v)' in code


def test_orthogonality_equivalence_includes_zero_and_distinguishes_degenerate_geometry():
    ex=printed(source(18))
    co=printed(source(18,'CO'))
    assert 'vecteurs nuls' in ex
    assert 'non colinéaires' in ex and 'non dégénéré' in ex
    assert 'positives ou nulles' in co
    for kind in ['EX','CO']:
        code=oracle(source(18,kind))
        assert "real=True" in code and '(u+v).dot(u-v)' in code
        assert 'norm_u.is_nonnegative is True' in code
        assert 'domain=Interval(0, oo)' in code
        assert 'FiniteSet(r)' in code and 'FiniteSet(0)' in code


def test_cosine_rule_oracle_constructs_the_third_side_for_a_general_angle():
    for kind in ['EX','CO']:
        code=oracle(source(47,kind))
        assert "theta = symbols('theta', real=True)" in code
        assert 'AB = Matrix([c, 0])' in code
        assert 'AC = Matrix([b*cos(theta), b*sin(theta)])' in code
        assert 'BC = AC - AB' in code and 'BC.dot(BC)' in code
        assert 'trigsimp' in code


@pytest.mark.parametrize(('number', 'valid', 'invalid'), [
    (5, 'A = Matrix([1, 2])', 'A = Matrix([2, 2])'),
    (16, '5*sqrt(3)/2', '5*sqrt(3)/3'),
    (18, '(u+v).dot(u-v)', '(u+v).dot(u+v)'),
    (47, '(b**2+c**2-2*b*c*cos(theta))', '(b**2+c**2)'),
])
def test_actual_oracles_reject_each_relevant_calculation_mutation(
    tmp_path, number, valid, invalid,
):
    relative = f'exercices/1SPE-PRODSCAL-EX-{number:03}.tex'
    original = source(number)
    intact = _run_fixture(tmp_path, relative, original)
    assert intact.returncode == 0, intact.stdout + intact.stderr
    assert valid in original, 'The source no longer contains the calculation under test.'
    mutated = original.replace(valid, invalid, 1)
    rejected = _run_fixture(tmp_path, relative, mutated)
    assert rejected.returncode == 1, rejected.stdout + rejected.stderr
