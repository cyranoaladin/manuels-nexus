"""Exercise the printed arithmetic algorithms, their domains and source bindings."""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
RELATIVE = Path("Mathematiques/manuel-maths/chapitres/TEXP-ARITHMETIQUE")
CHAPTER = ROOT / RELATIVE
COURSE = "cours/10_C1_divisibilite_pgcd.tex"
METHOD = "methodes/TEXP-ARI-ME-009.tex"
CONGRUENCES = "cours/11_C2_congruences.tex"


@pytest.fixture
def corpus(tmp_path: Path) -> Path:
    target = tmp_path / RELATIVE
    for name in (COURSE, METHOD, CONGRUENCES):
        (target / name).parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(CHAPTER / name, target / name)
    if (CHAPTER / "python").is_dir():
        shutil.copytree(CHAPTER / "python", target / "python")
    return tmp_path


def _run(corpus: Path, source: str, assertions: str = "") -> subprocess.CompletedProcess[str]:
    text = (corpus / RELATIVE / source).read_text(encoding="utf-8")
    bodies = re.findall(r"% BEGIN-VERIFY\n(.*?)% END-VERIFY", text, re.S)
    assert bodies, f"missing oracle: {source}"
    script = "\n".join(
        re.sub(r"^% ?", "", line) for body in bodies for line in body.splitlines()
    )
    # These reviewed scripts only compute with controlled integers and read
    # their temporary source files. Reject Python socket operations as well.
    guard = (
        "import sys\n"
        "def reject_network(event, args):\n"
        "    if event.startswith('socket.'):\n"
        "        raise RuntimeError('network disabled for arithmetic regression')\n"
        "sys.addaudithook(reject_network)\n"
    )
    return subprocess.run(
        [sys.executable, "-I", "-c", guard + script + "\n" + assertions],
        cwd=corpus, text=True, capture_output=True, timeout=15,
    )


@pytest.mark.parametrize("source,name", [(COURSE, "euclide"), (METHOD, "euclide")])
def test_gcd_has_positive_sign_for_signed_and_zero_inputs(corpus: Path, source: str, name: str) -> None:
    result = _run(corpus, source, f"""
import math
for a in range(-20, 21):
    for b in range(-20, 21):
        if a or b:
            assert {name}(a, b) == math.gcd(a, b), (a, b)
""")
    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("source,name", [(COURSE, "euclide"), (METHOD, "euclide"), (METHOD, "bezout")])
def test_gcd_undefined_pair_is_rejected(corpus: Path, source: str, name: str) -> None:
    result = _run(corpus, source, f"""
try:
    {name}(0, 0)
except ValueError:
    pass
else:
    raise AssertionError('the course excludes (0, 0)')
""")
    assert result.returncode == 0, result.stderr


def test_bezout_identity_and_positive_gcd_for_both_signs(corpus: Path) -> None:
    result = _run(corpus, METHOD, """
import math
for a in range(-20, 21):
    for b in range(-20, 21):
        if a or b:
            d, u, v = bezout(a, b)
            assert d == math.gcd(a, b) and a*u + b*v == d, (a, b, d, u, v)
""")
    assert result.returncode == 0, result.stderr


def test_sieve_handles_small_bounds_and_prime_square(corpus: Path) -> None:
    result = _run(corpus, METHOD, """
for n in range(-2, 52):
    expected = [p for p in range(2, n+1)
                if all(p % divisor for divisor in range(2, p))]
    assert crible(n) == expected, n
assert 49 not in crible(49)
""")
    assert result.returncode == 0, result.stderr


def test_factorization_handles_one_and_rejects_outside_domain(corpus: Path) -> None:
    result = _run(corpus, METHOD, """
import math
assert decomposition(1) == {}
for n in range(2, 101):
    factors = decomposition(n)
    assert math.prod(p**power for p, power in factors.items()) == n
    assert all(power > 0 and p >= 2 and all(p % d for d in range(2, p))
               for p, power in factors.items())
for n in (-10, -1, 0):
    try:
        decomposition(n)
    except ValueError:
        pass
    else:
        raise AssertionError(('domain n >= 1', n))
""")
    assert result.returncode == 0, result.stderr


def test_printed_comparisons_are_valid_tex_and_euclidean_divisor_is_positive() -> None:
    for name in (COURSE, CONGRUENCES):
        text = (CHAPTER / name).read_text(encoding="utf-8")
        assert not re.search(r"\n\s*eq(?:0|1)\$", text), name
    course = (CHAPTER / COURSE).read_text(encoding="utf-8")
    assert r"b\in\mathbb{N}^*" in course
    assert r"\neq1" in (CHAPTER / CONGRUENCES).read_text(encoding="utf-8")


def test_digit_sum_congruence_does_not_treat_a_negative_sign_as_a_digit() -> None:
    text = (CHAPTER / CONGRUENCES).read_text(encoding="utf-8")
    assert -1 % 9 != sum(map(int, str(abs(-1)))) % 9
    claim = re.search(r"\\textbf\{un entier.*?\}", text).group()
    assert "entier naturel" in claim and "écriture décimale" in claim


def test_general_congruence_power_does_not_require_zero_to_the_zero() -> None:
    text = (CHAPTER / CONGRUENCES).read_text(encoding="utf-8")
    statement = re.search(r"En particulier, (.*?)\n", text).group(1)
    assert r"pour tout $k\in\mathbb{N}^*$" in statement


def test_printed_gcd_is_loaded_from_the_same_python_source() -> None:
    references = []
    for name in (COURSE, METHOD):
        text = (CHAPTER / name).read_text(encoding="utf-8")
        paths = re.findall(r"\\lstinputlisting\[language=Python\]\{([^}]+)\}", text)
        assert len(paths) == 1, f"one actual Python source expected: {name}"
        references.extend(paths)
    assert references[0] == references[1]
    assert (ROOT / "Mathematiques/manuel-maths" / references[0]).is_file()


@pytest.mark.parametrize("source", [COURSE, METHOD])
def test_changed_python_dependency_invalidates_the_tex_oracle(corpus: Path, source: str) -> None:
    assert _run(corpus, source).returncode == 0
    dependency = corpus / RELATIVE / "python/euclide.py"
    assert dependency.is_file(), "printed source must exist before mutation"
    original = dependency.read_text(encoding="utf-8")
    dependency.write_text(original.replace("return a", "return -a"), encoding="utf-8")
    changed = _run(corpus, source)
    assert changed.returncode != 0, "a receipt must not ignore its changed Python source"


@pytest.mark.parametrize("name,before,after", [
    ("euclide", "return a", "return -a"),
    ("bezout", "return abs(a), signe, 0", "return a, signe, 0"),
    ("crible", "range(p * p, n + 1, p)", "range(p * p + 1, n + 1, p)"),
    ("decomposition", "facteurs[n] = facteurs.get(n, 0) + 1", "facteurs[n] = facteurs.get(n, 0) + 2"),
])
def test_wrong_algorithm_fails_even_after_updating_its_source_digest(
    corpus: Path, name: str, before: str, after: str,
) -> None:
    assert _run(corpus, METHOD).returncode == 0
    dependency = corpus / RELATIVE / f"python/{name}.py"
    old_digest = hashlib.sha256(dependency.read_bytes()).hexdigest()
    original = dependency.read_text(encoding="utf-8")
    assert before in original
    dependency.write_text(original.replace(before, after), encoding="utf-8")
    new_digest = hashlib.sha256(dependency.read_bytes()).hexdigest()
    source = corpus / RELATIVE / METHOD
    source.write_text(source.read_text().replace(old_digest, new_digest), encoding="utf-8")
    result = _run(corpus, METHOD)
    assert result.returncode != 0, "the mathematical assertions must detect the wrong result"
    assert "AssertionError" in result.stderr
