from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "Mathematiques" / "manuel-maths"
CHAPTER = MANUAL / "chapitres" / "1SPE-SUITES"
PYTHON = CHAPTER / "python"

LISTING_PATTERN = re.compile(
    r"\\lstinputlisting\[language=Python\]"
    r"\{chapitres/1SPE-SUITES/python/([^}]+\.py)\}"
)

TEX_LISTINGS = {
    "cours/01_diagnostic.tex": (
        "1SPE-SUITES-DIAGNOSTIC-R5-SOMME.py",
        "1SPE-SUITES-DIAGNOSTIC-R5-RECURRENCE.py",
    ),
    "cours/07_td_contextualise.tex": (
        "1SPE-SUITES-TD-CONTEXTUALISE-LECTURE.py",
        "1SPE-SUITES-TD-CONTEXTUALISE-VALEURS.py",
        "1SPE-SUITES-TD-CONTEXTUALISE-DEMI-VIE.py",
    ),
    "cours/07_td_fil_rouge.tex": (
        "1SPE-SUITES-TD-FIL-ROUGE-CROISEMENT.py",
    ),
    "cours/16_C7_algorithmique.tex": (
        "1SPE-SUITES-CR-016-TERME.py",
        "1SPE-SUITES-CR-016-SOMME.py",
        "1SPE-SUITES-CR-016-SEUIL.py",
    ),
    "methodes/1SPE-SUITES-ME-007.tex": (
        "1SPE-SUITES-ME-007-CAPITAL.py",
        "1SPE-SUITES-ME-007-SEUIL.py",
    ),
    "evaluations/1SPE-SUITES-EV-A.tex": ("1SPE-SUITES-EV-A-SEUIL.py",),
    "evaluations/1SPE-SUITES-EV-B.tex": ("1SPE-SUITES-EV-B-SEUIL.py",),
}

PROGRAMS = {
    "1SPE-SUITES-DIAGNOSTIC-R5-SOMME.py": (
        """s = 0
for k in range(1, 5):
    s = s + k
print(s)
""",
        "10\n",
    ),
    "1SPE-SUITES-DIAGNOSTIC-R5-RECURRENCE.py": (
        """u = 3
for i in range(4):
    u = 2 * u + 1
print(u)
""",
        "63\n",
    ),
    "1SPE-SUITES-TD-CONTEXTUALISE-LECTURE.py": (
        """q = 0.9879
M = 100
n = 0
while M > 50:
    M = q * M
    n = n + 1
print("Demi-vie :", n, "siecles")
print("Masse :", round(M, 2), "g")
""",
        "Demi-vie : 57 siecles\nMasse : 49.96 g\n",
    ),
    "1SPE-SUITES-TD-CONTEXTUALISE-VALEURS.py": (
        """q = 0.9879
for n in range(0, 101, 10):
    M_n = 100 * q**n
    print(f"n = {n} siecles : M_n = {round(M_n, 2)} g")
""",
        """n = 0 siecles : M_n = 100.0 g
n = 10 siecles : M_n = 88.54 g
n = 20 siecles : M_n = 78.39 g
n = 30 siecles : M_n = 69.4 g
n = 40 siecles : M_n = 61.45 g
n = 50 siecles : M_n = 54.41 g
n = 60 siecles : M_n = 48.17 g
n = 70 siecles : M_n = 42.65 g
n = 80 siecles : M_n = 37.76 g
n = 90 siecles : M_n = 33.43 g
n = 100 siecles : M_n = 29.6 g
""",
    ),
    "1SPE-SUITES-TD-CONTEXTUALISE-DEMI-VIE.py": (
        """q = 0.9879
M = 100.0
n = 0
while M > 50:
    M = q * M
    n = n + 1
print("Demi-vie :", n, "siecles, soit", n * 100, "ans")
print("Masse atteinte :", round(M, 2), "g")
""",
        "Demi-vie : 57 siecles, soit 5700 ans\nMasse atteinte : 49.96 g\n",
    ),
    "1SPE-SUITES-TD-FIL-ROUGE-CROISEMENT.py": (
        """n = 10
A = 200 * n
B = 1000 * 1.004**n
while B <= A:
    n = n + 1
    A = 200 * n
    B = 1000 * 1.004**n
print("Premier mois de depassement apres le rang 10 : n =", n)
print("A_n =", A, "euros")
print("B_n =", round(B, 2), "euros")
""",
        (
            "Premier mois de depassement apres le rang 10 : n = 1415\n"
            "A_n = 283000 euros\n"
            "B_n = 283924.99 euros\n"
        ),
    ),
    "1SPE-SUITES-CR-016-TERME.py": (
        """def terme(u0, n):
    u = u0
    for k in range(n):
        u = 2 * u + 1
    return u

print(terme(3, 5))
""",
        "127\n",
    ),
    "1SPE-SUITES-CR-016-SOMME.py": (
        """def somme(u0, q, n):
    u = u0
    S = u0
    for k in range(n):
        u = q * u
        S = S + u
    return S

print(somme(2, 3, 4))
""",
        "242\n",
    ),
    "1SPE-SUITES-CR-016-SEUIL.py": (
        """def recherche_seuil(u0, q, seuil):
    u = u0
    n = 0
    while u <= seuil:
        u = q * u
        n = n + 1
    return n, u

n, val = recherche_seuil(1, 1.05, 2)
print(f"n = {n}, u_n = {val:.4f}")
""",
        "n = 15, u_n = 2.0789\n",
    ),
    "1SPE-SUITES-ME-007-CAPITAL.py": (
        """def capital(n):
    u = 1500
    for k in range(n):
        u = 1.04 * u
    return u

print(round(capital(10), 2))
""",
        "2220.37\n",
    ),
    "1SPE-SUITES-ME-007-SEUIL.py": (
        """u = 1500
n = 0
while u < 3000:
    u = 1.04 * u
    n = n + 1
print("Rang :", n)
print("Capital :", round(u, 2))
""",
        "Rang : 18\nCapital : 3038.72\n",
    ),
    "1SPE-SUITES-EV-A-SEUIL.py": (
        """u = 800
n = 0
while u < 1200:
    u = 1.05 * u
    n = n + 1
print(n)
""",
        "9\n",
    ),
    "1SPE-SUITES-EV-B-SEUIL.py": (
        """u = 1000
n = 0
while u < 1500:
    u = 1.04 * u
    n = n + 1
print(n)
""",
        "11\n",
    ),
}


def _text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_all_remaining_rendered_programs_use_exact_canonical_sources() -> None:
    assert set(PROGRAMS) == {
        name for names in TEX_LISTINGS.values() for name in names
    }

    for relative_tex, expected_names in TEX_LISTINGS.items():
        source = _text(CHAPTER / relative_tex)
        assert r"\begin{python}" not in source
        assert r"\end{python}" not in source
        assert tuple(LISTING_PATTERN.findall(source)) == expected_names


def test_all_remaining_python_sources_parse_execute_and_match_exact_output() -> None:
    for name, (expected_source, expected_stdout) in PROGRAMS.items():
        path = PYTHON / name
        source = _text(path)
        assert ast.dump(ast.parse(source), include_attributes=False) == ast.dump(
            ast.parse(expected_source), include_attributes=False
        )
        completed = subprocess.run(
            [sys.executable, str(path)],
            cwd=MANUAL,
            text=True,
            capture_output=True,
            check=False,
            timeout=2,
        )
        assert completed.returncode == 0, completed.stderr
        assert completed.stderr == ""
        assert completed.stdout == expected_stdout


def test_outputs_agree_with_published_explanations_without_student_leaks() -> None:
    contextualised = _text(CHAPTER / "cours/07_td_contextualise.tex")
    fil_rouge = _text(CHAPTER / "cours/07_td_fil_rouge.tex")
    method = _text(CHAPTER / "methodes/1SPE-SUITES-ME-007.tex")
    evaluation_a = _text(CHAPTER / "evaluations/1SPE-SUITES-EV-A-corrige.tex")
    evaluation_b = _text(CHAPTER / "evaluations/1SPE-SUITES-EV-B-corrige.tex")

    assert all(token in contextualised for token in ("57 siecles", "49.96 g"))
    assert all(token in fil_rouge for token in ("n = 1415", "283\\,000", "283\\,925"))
    assert "Programme à exécuter et à analyser" in fil_rouge
    assert "Programme à compléter" not in fil_rouge
    assert all(
        token in method
        for token in (
            "2\\,220{,}37",
            "Rang : 18",
            "3038.72",
            "2\\,921{,}85",
            "3\\,038{,}72",
        )
    )
    assert r"\mathbf{n = 9}" in evaluation_a
    assert r"\mathbf{n = 11}" in evaluation_b

    diagnostic = _text(CHAPTER / "cours/01_diagnostic.tex")
    student_a = _text(CHAPTER / "evaluations/1SPE-SUITES-EV-A.tex")
    student_b = _text(CHAPTER / "evaluations/1SPE-SUITES-EV-B.tex")
    assert "Quelle valeur est affichée ?" in diagnostic
    assert "Le programme affiche 9" not in student_a
    assert "Le programme affiche 11" not in student_b
