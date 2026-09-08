"""Modèles géométriques réels, domaines et preuve d'optimalité globale."""
from pathlib import Path
import sympy as s
from tests.test_prodscal_remaining_scientific_regressions import _run_fixture

ROOT=Path(__file__).resolve().parents[1]
D=ROOT/'Mathematiques/manuel-maths/chapitres/1SPE-DERIVATION-GLOBAL'
COURSE=D/'cours/14_C5_optimisation.tex'
METHOD=D/'methodes/1SPE-DERGLOBAL-ME-005.tex'


def printed(path):
    return '\n'.join(line for line in path.read_text().splitlines() if not line.lstrip().startswith('%'))


def test_optimization_method_checks_derivability_and_boundaries():
    for path in [COURSE,METHOD]:
        text=printed(path)
        assert 'bornes incluses' in text
        assert 'dérivabilité' in text


def test_fixed_hypotenuse_is_completed_by_actual_triangle_data():
    text=printed(METHOD)
    assert '$AB=6$ cm' in text and '$AC=8$ cm' in text
    assert '$BC=10$ cm' in text
    assert r'$h=8-\frac43x$' in text
    assert r'$x\in]0\,;\,6[$' in text
    assert '$12$ cm²' in text
    x=s.symbols('x',real=True)
    area=x*(8-s.Rational(4,3)*x)
    assert s.expand(12-area-s.Rational(4,3)*(x-3)**2) == 0


def test_agm_uses_three_areas_with_a_fixed_product():
    text=printed(COURSE)
    assert '$r^2 + r^2 + h$' not in text
    assert r'S(r)=2\pi r^2+\frac{500}{r}+\frac{500}{r}' in text
    assert r'500\,000\pi' in text
    assert 'égaux' in text


def test_open_rectangle_bounds_are_not_claimed_as_admissible_rectangles():
    text=printed(COURSE)
    assert r'\begin{array}{|c|ccccccc|}' not in text
    assert 'rectangles dégénérés' in text
    assert 'exclus' in text


def test_cylinder_oracle_rejects_an_omitted_end_disc(tmp_path):
    source=COURSE.read_text()
    intact=_run_fixture(tmp_path,'cours/14_C5_optimisation.tex',source)
    assert intact.returncode==0,intact.stdout+intact.stderr
    valid='surface = 2*pi*r**2 + 2*pi*r*height'
    assert valid in source
    mutated=source.replace(valid,'surface = pi*r**2 + 2*pi*r*height',1)
    assert _run_fixture(tmp_path,'cours/14_C5_optimisation.tex',mutated).returncode==1


def test_triangle_oracle_rejects_the_old_unrelated_height(tmp_path):
    source=METHOD.read_text()
    intact=_run_fixture(tmp_path,'methodes/1SPE-DERGLOBAL-ME-005.tex',source)
    assert intact.returncode==0,intact.stdout+intact.stderr
    valid='height = 8-Rational(4, 3)*x'
    assert valid in source
    mutated=source.replace(valid,'height = 10-x',1)
    assert _run_fixture(tmp_path,'methodes/1SPE-DERGLOBAL-ME-005.tex',mutated).returncode==1
