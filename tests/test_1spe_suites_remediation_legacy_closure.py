from __future__ import annotations

import ast
import json
import re
import runpy
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "Mathematiques" / "manuel-maths"
CHAPTER = MANUAL / "chapitres" / "1SPE-SUITES"
REMEDIATION = CHAPTER / "remediation"
PYTHON = CHAPTER / "python"

LISTING_PATTERN = re.compile(
    r"\\lstinputlisting\[language=Python\]"
    r"\{chapitres/1SPE-SUITES/python/([^}]+\.py)\}"
)

REMEDIATION_DIAGNOSES = {
    "C1": "confondre formule explicite et relation de récurrence",
    "C2": "conclure à partir d'un préfixe",
    "C3": "oublier de vérifier la relation multiplicative",
    "C4": "mal compter le nombre de termes",
    "C5": "choisir une méthode sans vérifier ses conditions",
    "C6": "confondre évolution additive et multiplicative",
    "C7": "décaler le nombre d'itérations",
}

EXPECTED_LISTINGS = {
    "1SPE-SUITES-FR-R5.tex": (
        "1SPE-SUITES-FR-R5-EX1-TRACE.py",
        "1SPE-SUITES-FR-R5-EX2.py",
        "1SPE-SUITES-FR-R5-EX2-MODIFIE.py",
        "1SPE-SUITES-FR-R5-EX3-SEUIL.py",
        "1SPE-SUITES-FR-R5-EX4-SOMME.py",
        "1SPE-SUITES-FR-R5-EX4-CARRES.py",
    ),
    "1SPE-SUITES-RE-C7.tex": (
        "1SPE-SUITES-RE-C7-EX1-TERME.py",
        "1SPE-SUITES-RE-C7-EX2-SOMME.py",
        "1SPE-SUITES-RE-C7-EX2-ADAPTATION.py",
        "1SPE-SUITES-RE-C7-EX3-SEUIL.py",
    ),
}

EXPECTED_STDOUT = {
    "1SPE-SUITES-FR-R5-EX1-TRACE.py": "5\n7\n9\n11\n",
    "1SPE-SUITES-FR-R5-EX2.py": "243\n",
    "1SPE-SUITES-FR-R5-EX2-MODIFIE.py": "781250\n",
    "1SPE-SUITES-FR-R5-EX3-SEUIL.py": "10 1024\n",
    "1SPE-SUITES-FR-R5-EX4-SOMME.py": "55\n",
    "1SPE-SUITES-FR-R5-EX4-CARRES.py": "385\n",
    "1SPE-SUITES-RE-C7-EX1-TERME.py": "",
    "1SPE-SUITES-RE-C7-EX2-SOMME.py": "",
    "1SPE-SUITES-RE-C7-EX2-ADAPTATION.py": "",
    "1SPE-SUITES-RE-C7-EX3-SEUIL.py": "9 1551.3282159785163\n",
}


def _text(name: str) -> str:
    return (REMEDIATION / name).read_text(encoding="utf-8")


def _normalized(name: str) -> str:
    return " ".join(_text(name).split())


def test_c1_to_c7_keep_existing_objects_and_implement_the_real_remediation_loop() -> None:
    ordered_markers = (
        "Diagnostic de l'erreur",
        "Orientation",
        "Rappel ciblé",
        "Aide graduée",
        "Activité guidée",
        "Exercice autonome",
        "Revalidation",
    )

    for capacity, diagnosis in REMEDIATION_DIAGNOSES.items():
        name = f"1SPE-SUITES-RE-{capacity}.tex"
        source = _text(name)
        metadata = json.loads(source.splitlines()[0].removeprefix("% META: "))

        assert metadata["id"] == f"1SPE-SUITES-RE-{capacity}"
        assert metadata["capacites_codes"] == [capacity]
        assert metadata["status"] == "generated"
        assert diagnosis in source.lower()

        positions = [source.index(marker) for marker in ordered_markers]
        assert positions == sorted(positions)
        assert "Si l'erreur diagnostiquée" in source

        expected_ids = [
            f"1SPE-SUITES-RE-{capacity}-EX1",
            f"1SPE-SUITES-RE-{capacity}-EX2",
            f"1SPE-SUITES-RE-{capacity}-EX3",
        ]
        exercise_ids = re.findall(r"\\begin\{exercice\}\{([^}]+)\}", source)
        correction_ids = re.findall(r"\\begin\{corrige\}\{([^}]+)\}", source)
        assert exercise_ids == expected_ids
        assert correction_ids == expected_ids


def test_deterministic_scientific_and_editorial_findings_are_closed() -> None:
    c1 = _normalized("1SPE-SUITES-RE-C1.tex")
    assert r"v_{10} = 177\,149" in c1
    assert r"v_{11} = 3 \times 177\,149 - 4 = 531\,443" in c1
    assert "v_{10} = 5" not in c1
    assert "comportement particulier" not in c1

    c2 = _normalized("1SPE-SUITES-RE-C2.tex")
    assert "Ces trois différences ne suffisent pas" in c2
    assert "$v_4=0$" in c2
    assert "$v_{n+1}=v_n-3$ pour tout $n\\in\\mathbb{N}$" in c2

    c4 = _text("1SPE-SUITES-RE-C4.tex")
    assert "effectué à la fin du mois $k$" in c4
    assert "effectué au début du mois $k$" not in c4
    assert "(u_1+u_k)" not in c4

    c6 = _normalized("1SPE-SUITES-RE-C6.tex")
    assert r"$3$ & $1\,639$" in c6
    assert r"$4$ & $1\,688$" in c6
    assert r"$3$ & $1\,637$" not in c6
    assert r"$4$ & $1\,686$" not in c6
    assert "D_{n+1}-D_n=0{,}03A_n-30" in c6
    assert "salaire annuel (mensuel)" not in c6
    assert "salaire mensuel" in c6

    r2 = _text("1SPE-SUITES-FR-R2.tex")
    assert "Une bactérie se multiplie" in r2
    assert "round(C10) == 2688" in r2
    assert "2687.0" not in r2

    r3 = _text("1SPE-SUITES-FR-R3.tex")
    assert "h(x) = 2^x" not in r3
    assert "2**(-1)" not in r3
    assert "fonction affine" in r3


def test_all_published_remediation_programs_use_exact_canonical_sources() -> None:
    assert set(EXPECTED_STDOUT) == {
        name for names in EXPECTED_LISTINGS.values() for name in names
    }

    for tex_name, expected_names in EXPECTED_LISTINGS.items():
        source = _text(tex_name)
        assert tuple(LISTING_PATTERN.findall(source)) == expected_names


def test_remediation_python_sources_parse_run_and_match_outputs() -> None:
    for name, expected_stdout in EXPECTED_STDOUT.items():
        path = PYTHON / name
        source = path.read_text(encoding="utf-8")
        ast.parse(source)
        assert not any(character in source for character in "“”‘’×÷")

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

    term_namespace = runpy.run_path(
        str(PYTHON / "1SPE-SUITES-RE-C7-EX1-TERME.py")
    )
    assert term_namespace["terme"](0) == 1
    assert term_namespace["terme"](3) == 29

    sum_namespace = runpy.run_path(
        str(PYTHON / "1SPE-SUITES-RE-C7-EX2-SOMME.py")
    )
    assert sum_namespace["somme"](3) == 80

    adaptation_namespace = runpy.run_path(
        str(PYTHON / "1SPE-SUITES-RE-C7-EX2-ADAPTATION.py")
    )
    assert adaptation_namespace["somme"](3) == 425
