"""Regressions scientifiques P0 pour les cours 1NSI."""
import contextlib
from fractions import Fraction
import hashlib
import importlib.util
import io
import re
import runpy
import subprocess
import sys
from pathlib import Path

import pytest


NSI_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = NSI_ROOT.parent
COURSE = NSI_ROOT / "chapitres/1NSI-LANGAGE/cours/1NSI-LANG-COURS-C4.tex"
PYTHON_SOURCE = NSI_ROOT / "chapitres/1NSI-LANGAGE/code/maximum_bugue.py"
MINIMUM_CORRECTION = (
    NSI_ROOT / "chapitres/1NSI-LANGAGE/corriges/1NSI-LANGAGE-RE-C4-CORRIGE.tex"
)
MINIMUM_REMEDIATION = (
    NSI_ROOT / "chapitres/1NSI-LANGAGE/remediation/1NSI-LANGAGE-RE-C4.tex"
)
MINIMUM_SOURCE = NSI_ROOT / "chapitres/1NSI-LANGAGE/code/minimum.py"
AVANCEMENT_COURSE = (
    NSI_ROOT
    / "chapitres/1NSI-PROJET-METHODES/cours/1NSI-PM-COURS-C2.tex"
)
AVANCEMENT_SOURCE = (
    NSI_ROOT / "chapitres/1NSI-PROJET-METHODES/code/avancement.py"
)
WEIGHTED_MEAN_COURSE = (
    NSI_ROOT
    / "chapitres/1NSI-PROJET-METHODES/cours/1NSI-PM-COURS-C3.tex"
)
WEIGHTED_MEAN_SOURCE = (
    NSI_ROOT
    / "chapitres/1NSI-PROJET-METHODES/code/moyenne_ponderee.py"
)
TABLE_JOIN_COURSE = (
    NSI_ROOT / "chapitres/1NSI-TABLES/cours/1NSI-TAB-COURS-C4.tex"
)
TABLE_JOIN_SOURCE = NSI_ROOT / "chapitres/1NSI-TABLES/code/fusionner.py"
TABLE_JOIN_ALL_CORRECTION = (
    NSI_ROOT / "chapitres/1NSI-TABLES/corriges/1NSI-TAB-CO-005.tex"
)
TABLE_JOIN_ALL_SOURCE = (
    NSI_ROOT / "chapitres/1NSI-TABLES/code/fusionner_tout.py"
)
WEB_SERVER_COURSE = (
    NSI_ROOT / "chapitres/1NSI-WEB-IHM/cours/1NSI-WEB-COURS-C2.tex"
)
WEB_POST_CORRECTION = (
    NSI_ROOT / "chapitres/1NSI-WEB-IHM/corriges/1NSI-WEB-CO-004.tex"
)
ARCHITECTURE_COURSE = (
    NSI_ROOT
    / "chapitres/1NSI-ARCHITECTURE-OS/cours/1NSI-ARCHOS-COURS-C1.tex"
)
THERMOSTAT_COURSE = (
    NSI_ROOT / "chapitres/1NSI-RESEAUX/cours/1NSI-RES-COURS-C3.tex"
)
THERMOSTAT_SOURCE = (
    NSI_ROOT / "chapitres/1NSI-RESEAUX/code/thermostat_ihm.py"
)
FLOAT_EQUALITY_CORRECTION = (
    NSI_ROOT
    / "chapitres/1NSI-TYPES-BASE/corriges/1NSI-TYPES-BASE-RE-C3-CORRIGE.tex"
)
GRID_COPY_COURSE = (
    NSI_ROOT
    / "chapitres/1NSI-TYPES-CONSTRUITS/cours/1NSI-TC-COURS-C5.tex"
)
GRID_COPY_SOURCE = (
    NSI_ROOT
    / "chapitres/1NSI-TYPES-CONSTRUITS/code/copier_grille_deux_niveaux.py"
)
GRID_COPY_EXERCISE_053 = (
    NSI_ROOT
    / "chapitres/1NSI-TYPES-CONSTRUITS/exercices/1NSI-TC-EX-053.tex"
)
GRID_COPY_ANSWER_053 = (
    NSI_ROOT
    / "chapitres/1NSI-TYPES-CONSTRUITS/corriges/1NSI-TC-CO-053.tex"
)
GRID_COPY_EXERCISE_054 = (
    NSI_ROOT
    / "chapitres/1NSI-TYPES-CONSTRUITS/exercices/1NSI-TC-EX-054.tex"
)
GRID_COPY_ANSWER_054 = (
    NSI_ROOT
    / "chapitres/1NSI-TYPES-CONSTRUITS/corriges/1NSI-TC-CO-054.tex"
)
REVIEW_SCRIPT = REPO_ROOT / "scripts/review_1nsi_content.py"

_REVIEW_SPEC = importlib.util.spec_from_file_location(
    "review_1nsi_content", REVIEW_SCRIPT
)
assert _REVIEW_SPEC is not None and _REVIEW_SPEC.loader is not None
review_module = importlib.util.module_from_spec(_REVIEW_SPEC)
_REVIEW_SPEC.loader.exec_module(review_module)


MARKED_MAXIMUM_SEQUENCE = re.compile(
    r"(?m)^% PYTHON-SOURCE: code/maximum_bugue\.py\n"
    r"\\begin\{python\}(?P<python>.*?)\\end\{python\}\n\n"
    r"\\begin\{console\}(?P<console>.*?)\\end\{console\}\n\n"
    r"% BEGIN-TRACE\n(?P<trace>.*?)% EXPECTED\n(?P<expected>.*?)% END-TRACE",
    re.DOTALL,
)


def _uncomment(block: str) -> str:
    return "\n".join(re.sub(r"^%\s?", "", line) for line in block.splitlines())


def test_von_neumann_diagram_uses_one_bidirectional_bus() -> None:
    assert ARCHITECTURE_COURSE.is_file()

    tex = ARCHITECTURE_COURSE.read_text(encoding="utf-8")
    diagram_match = re.search(
        r"\\begin\{tikzpicture\}(?P<diagram>.*?)\\end\{tikzpicture\}",
        tex,
        re.DOTALL,
    )
    assert diagram_match is not None
    diagram = diagram_match.group("diagram")

    assert "bus/.style=" in diagram
    assert "liaison/.style=" in diagram
    assert "<->" in diagram
    assert diagram.count(r"\draw[bus]") == 1
    assert diagram.count(r"\draw[liaison]") == 4
    for component in ("uc", "mem", "entree", "sortie"):
        assert re.search(
            rf"\\draw\[liaison\] \({component}\.(?:north|south)\) -- ",
            diagram,
        )
    assert r"\draw[fleche]" not in diagram


def test_thermostat_exposes_tested_user_controls_and_state() -> None:
    assert THERMOSTAT_COURSE.is_file()
    assert THERMOSTAT_SOURCE.is_file()

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        namespace = runpy.run_path(str(THERMOSTAT_SOURCE))
    assert stdout.getvalue() == ""

    interface_thermostat = namespace["interface_thermostat"]
    lancer_ihm = namespace["lancer_ihm"]
    assert interface_thermostat("ON", 25) == (
        "temperature=25 C | mode=ON manuel | chauffage=ON"
    )
    assert interface_thermostat("OFF", 15) == (
        "temperature=15 C | mode=OFF manuel | chauffage=OFF"
    )
    assert interface_thermostat("AUTO", 15) == (
        "temperature=15 C | mode=AUTO | chauffage=ON"
    )

    affichages: list[str] = []
    lancer_ihm(22, lire=lambda _: "ON", ecrire=affichages.append)
    assert affichages == [
        "Commandes : AUTO | ON | OFF",
        "temperature=22 C | mode=ON manuel | chauffage=ON",
    ]

    with pytest.raises(ValueError) as error:
        interface_thermostat("CHAUD", 20)
    assert str(error.value) == "commande attendue : AUTO, ON ou OFF"

    source_code = THERMOSTAT_SOURCE.read_text(encoding="utf-8")
    assert source_code.isascii()
    assert "def traiter_evenement(" in source_code
    assert "def afficher_etat(" in source_code
    assert "def lancer_ihm(" in source_code

    tex = THERMOSTAT_COURSE.read_text(encoding="utf-8")
    sequence = re.compile(
        r"(?m)^% PYTHON-SOURCE: code/thermostat_ihm\.py\n"
        r"\\begin\{python\}(?P<python>.*?)\\end\{python\}",
        re.DOTALL,
    )
    matches = list(sequence.finditer(tex))
    assert len(matches) == 1, "la source canonique de l'IHM doit etre unique"
    assert matches[0].group("python") == f"\n{source_code}"

    verify_matches = list(
        re.finditer(
            r"% BEGIN-VERIFY\n(?P<verify>.*?)% END-VERIFY", tex, re.DOTALL
        )
    )
    assert len(verify_matches) == 1
    verify_code = _uncomment(verify_matches[0].group("verify"))
    assert verify_code.count(source_code.rstrip("\n")) == 1
    assert 'assert interface_thermostat("ON", 25)' in verify_code
    assert 'assert interface_thermostat("OFF", 15)' in verify_code
    assert 'assert interface_thermostat("AUTO", 15)' in verify_code
    assert "except ValueError as erreur:" in verify_code


def test_post_does_not_claim_to_prevent_server_side_logging() -> None:
    assert WEB_POST_CORRECTION.is_file()

    tex = WEB_POST_CORRECTION.read_text(encoding="utf-8")
    answer_match = re.search(
        r"\\textbf\{3\.\}(?P<answer>.*?)\\end\{corrige\}", tex, re.DOTALL
    )
    assert answer_match is not None
    answer = " ".join(answer_match.group("answer").split())

    assert "corps de la requête plutôt que dans l'URL" in answer
    assert "n'apparaissent donc pas dans l'historique des URL" in answer
    assert "serveur web, un proxy ou l'application" in answer
    assert "peuvent néanmoins journaliser le corps" in answer
    assert "HTTPS" in answer
    assert "minimiser les données" in answer
    assert "politique de journalisation" in answer
    assert (
        "évitant qu'elles ne se retrouvent dans l'historique ou les journaux"
        not in answer
    )


def test_full_table_join_preserves_duplicate_matching_rows() -> None:
    assert TABLE_JOIN_ALL_CORRECTION.is_file()
    assert TABLE_JOIN_ALL_SOURCE.is_file()

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        namespace = runpy.run_path(str(TABLE_JOIN_ALL_SOURCE))
    assert stdout.getvalue() == ""

    fusionner_tout = namespace["fusionner_tout"]
    resultat = fusionner_tout(
        [{"nom": "Amine", "classe": "1A"}, {"nom": "Lina", "classe": "1B"}],
        [
            {"nom": "Amine", "absence": "lundi"},
            {"nom": "Amine", "absence": "mardi"},
        ],
        "nom",
        {"absence": "aucune"},
    )
    assert resultat == [
        {"nom": "Amine", "classe": "1A", "absence": "lundi"},
        {"nom": "Amine", "classe": "1A", "absence": "mardi"},
        {"nom": "Lina", "classe": "1B", "absence": "aucune"},
    ]

    produit = fusionner_tout(
        [
            {"nom": "Amine", "groupe": "A"},
            {"nom": "Amine", "groupe": "B"},
        ],
        [
            {"nom": "Amine", "absence": "lundi"},
            {"nom": "Amine", "absence": "mardi"},
        ],
        "nom",
        {"absence": "aucune"},
    )
    assert produit == [
        {"nom": "Amine", "groupe": "A", "absence": "lundi"},
        {"nom": "Amine", "groupe": "A", "absence": "mardi"},
        {"nom": "Amine", "groupe": "B", "absence": "lundi"},
        {"nom": "Amine", "groupe": "B", "absence": "mardi"},
    ]

    source_code = TABLE_JOIN_ALL_SOURCE.read_text(encoding="utf-8")
    assert source_code.isascii()
    assert "setdefault(ligne2[cle], []).append(ligne2)" in source_code
    assert "{ligne[cle]: ligne for ligne in table2}" not in source_code

    tex = TABLE_JOIN_ALL_CORRECTION.read_text(encoding="utf-8")
    sequence = re.compile(
        r"(?m)^% PYTHON-SOURCE: code/fusionner_tout\.py\n"
        r"\\begin\{python\}(?P<python>.*?)\\end\{python\}",
        re.DOTALL,
    )
    matches = list(sequence.finditer(tex))
    assert len(matches) == 1, "la source canonique de la fusion doit etre unique"
    assert matches[0].group("python") == f"\n{source_code}"

    verify_matches = list(
        re.finditer(
            r"% BEGIN-VERIFY\n(?P<verify>.*?)% END-VERIFY", tex, re.DOTALL
        )
    )
    assert len(verify_matches) == 1
    verify_code = _uncomment(verify_matches[0].group("verify"))
    assert verify_code.count(source_code.rstrip("\n")) == 1
    assert '"absence": "lundi"' in verify_code
    assert '"absence": "mardi"' in verify_code


def test_full_table_join_rejects_nonkey_column_collisions() -> None:
    assert TABLE_JOIN_ALL_CORRECTION.is_file()
    assert TABLE_JOIN_ALL_SOURCE.is_file()

    namespace = runpy.run_path(str(TABLE_JOIN_ALL_SOURCE))
    fusionner_tout = namespace["fusionner_tout"]
    message = "les colonnes hors cle doivent etre disjointes"

    with pytest.raises(ValueError) as matched_error:
        fusionner_tout(
            [{"nom": "Amine", "classe": "1A"}],
            [{"nom": "Amine", "classe": "1B"}],
            "nom",
            {"absence": "aucune"},
        )
    assert str(matched_error.value) == message

    with pytest.raises(ValueError) as default_error:
        fusionner_tout(
            [{"nom": "Lina", "absence": "inconnue"}],
            [],
            "nom",
            {"absence": "aucune"},
        )
    assert str(default_error.value) == message

    with pytest.raises(ValueError) as unmatched_error:
        fusionner_tout(
            [{"nom": "Amine", "classe": "1A"}],
            [{"nom": "Omar", "classe": "1B"}],
            "nom",
            {"absence": "aucune"},
        )
    assert str(unmatched_error.value) == message

    with pytest.raises(ValueError) as late_error:
        fusionner_tout(
            [{"nom": "Amine", "classe": "1A"}],
            [
                {"nom": "Amine", "absence": "lundi"},
                {"nom": "Amine", "classe": "1B"},
            ],
            "nom",
            {},
        )
    assert str(late_error.value) == message

    optimized_probe = """
import runpy
import sys

fusionner_tout = runpy.run_path(sys.argv[1])["fusionner_tout"]
try:
    fusionner_tout(
        [{"nom": "Amine", "classe": "1A"}],
        [{"nom": "Omar", "classe": "1B"}],
        "nom",
        {},
    )
except ValueError as error:
    if str(error) != "les colonnes hors cle doivent etre disjointes":
        raise RuntimeError(f"message inattendu: {error}")
else:
    raise RuntimeError("la collision doit etre refusee")
"""
    completed = subprocess.run(
        [
            sys.executable,
            "-I",
            "-O",
            "-c",
            optimized_probe,
            str(TABLE_JOIN_ALL_SOURCE),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr

    source_code = TABLE_JOIN_ALL_SOURCE.read_text(encoding="utf-8")
    guard = "if not colonnes1.isdisjoint(colonnes2):"
    assert guard in source_code
    assert source_code.index("colonnes1 =") < source_code.index("index2 =")
    assert source_code.index("colonnes2 =") < source_code.index("index2 =")
    assert ".update(colonne for colonne in defauts if colonne != cle)" in source_code
    assert f'raise ValueError("{message}")' in source_code
    assert "assert colonnes1.isdisjoint(colonnes2)" not in source_code

    tex = TABLE_JOIN_ALL_CORRECTION.read_text(encoding="utf-8")
    assert "colonnes hors clé doivent être disjointes" in tex
    verify_match = re.search(
        r"% BEGIN-VERIFY\n(?P<verify>.*?)% END-VERIFY", tex, re.DOTALL
    )
    assert verify_match is not None
    verify_code = _uncomment(verify_match.group("verify"))
    assert guard in verify_code
    assert "table_collision" in verify_code
    assert "defauts_collision" in verify_code
    assert "collision_sans_correspondance" in verify_code
    assert "produit" in verify_code
    assert f'assert str(erreur) == "{message}"' in verify_code


def test_float_equality_is_not_described_as_bitwise_comparison() -> None:
    assert FLOAT_EQUALITY_CORRECTION.is_file()

    tex = FLOAT_EQUALITY_CORRECTION.read_text(encoding="utf-8")
    compact_tex = " ".join(tex.split())
    assert "compare des\n\\textbf{bits}" not in tex
    assert "règles d'égalité de Python" in compact_tex
    assert "pas leurs représentations binaires bit à bit" in compact_tex
    assert "deux nombres flottants représentables distincts" in compact_tex
    assert "Chaque addition" not in compact_tex
    assert r"Le littéral \lstinline{0.1} est déjà stocké sous une valeur approchée" in (
        compact_tex
    )
    assert "les deux premières additions" in compact_tex
    assert "la troisième doit être arrondie" in compact_tex
    assert r"\lstinline{-0.0 == 0.0}" in tex
    assert r'\lstinline{float("nan") == float("nan")}' in tex

    x = 0.0
    additions_exactes = []
    for _ in range(3):
        somme_exacte_des_operandes = Fraction.from_float(x) + Fraction.from_float(
            0.1
        )
        x += 0.1
        additions_exactes.append(
            Fraction.from_float(x) == somme_exacte_des_operandes
        )
    assert additions_exactes == [True, True, False]
    assert x == 0.30000000000000004
    assert x != 0.3
    assert -0.0 == 0.0
    nan = float("nan")
    assert nan != nan


def _marked_maximum_sequence(tex: str) -> re.Match[str]:
    matches = list(MARKED_MAXIMUM_SEQUENCE.finditer(tex))
    assert len(matches) == 1, "la sequence Python marquee doit etre unique"
    return matches[0]


def test_marked_maximum_sequence_ignores_a_valid_decoy_before_the_marker() -> None:
    tex = r'''\begin{python}
print("decoy")
\end{python}

\begin{console}
decoy
\end{console}

% BEGIN-TRACE
% print("decoy")
% EXPECTED
% decoy
% END-TRACE

% PYTHON-SOURCE: code/maximum_bugue.py
\begin{python}
print("marked divergence")
\end{python}

\begin{console}
marked divergence
\end{console}

% BEGIN-TRACE
% print("marked divergence")
% EXPECTED
% marked divergence
% END-TRACE
'''

    sequence = _marked_maximum_sequence(tex)

    assert sequence.group("python") == '\nprint("marked divergence")\n'
    assert sequence.group("console") == "\nmarked divergence\n"
    assert _uncomment(sequence.group("trace")) == 'print("marked divergence")'
    assert _uncomment(sequence.group("expected")) == "marked divergence"


def test_maximum_zero_condition_includes_zero_for_nonempty_lists() -> None:
    assert COURSE.is_file()
    assert PYTHON_SOURCE.is_file()

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        namespace = runpy.run_path(str(PYTHON_SOURCE))
    assert stdout.getvalue() == "7\n"

    maximum_bugue = namespace["maximum_bugue"]
    assert maximum_bugue([3, 7, 2]) == 7
    assert maximum_bugue([-5, 0, -8]) == 0
    assert maximum_bugue([-5, -1, -8]) == 0

    source_code = PYTHON_SOURCE.read_text(encoding="utf-8")
    tex = COURSE.read_text(encoding="utf-8")
    sequence = _marked_maximum_sequence(tex)
    assert sequence.group("python") == f"\n{source_code}"
    assert sequence.group("console") == f"\n{stdout.getvalue()}"
    assert _uncomment(sequence.group("trace")) == source_code.rstrip("\n")
    assert _uncomment(sequence.group("expected")) == stdout.getvalue().rstrip("\n")

    course_record = {
        "id": "1NSI-LANG-COURS-C4",
        "path": "NSI/chapitres/1NSI-LANGAGE/cours/1NSI-LANG-COURS-C4.tex",
        "metadata": {},
        "scope": "object",
        "chapter": "1NSI-LANGAGE",
    }
    manifest = review_module.dependency_manifest(
        course_record, [course_record], REPO_ROOT
    )
    assert manifest["python"] == [
        {
            "path": "NSI/chapitres/1NSI-LANGAGE/code/maximum_bugue.py",
            "sha256": "sha256:"
            + hashlib.sha256(source_code.encode("utf-8")).hexdigest(),
        }
    ]

    frequent_error = re.search(r"\\erreurFrequente\{(.*?)\}\n", tex, re.DOTALL)
    assert frequent_error is not None
    error_text = " ".join(frequent_error.group(1).split())
    assert "liste est non vide" in error_text
    assert "valeur positive ou nulle" in error_text
    assert r"\max(\texttt{liste}) \geq 0" in error_text
    assert "[-5, 0, -8]" in error_text
    assert "[-5, -1, -8]" in error_text
    assert "contient au moins une valeur positive" not in error_text

    execution = review_module.execution_observation(course_record, REPO_ROOT)
    assert execution is not None
    assert execution["fresh_verdict"] == "pass"
    assert execution["matches_receipt"] is True
    assert execution["anomalies"] == []


def test_minimum_canonical_source_rejects_empty_list_and_matches_correction() -> None:
    assert MINIMUM_CORRECTION.is_file()
    assert MINIMUM_SOURCE.is_file()

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        namespace = runpy.run_path(str(MINIMUM_SOURCE))
    assert stdout.getvalue() == ""

    minimum = namespace["minimum"]
    assert minimum([5, 3, 8]) == 3
    assert minimum([42]) == 42
    assert minimum([-5, -1, -8]) == -8
    with pytest.raises(ValueError) as error:
        minimum([])
    assert str(error.value) == "liste doit etre non vide"

    source_code = MINIMUM_SOURCE.read_text(encoding="utf-8")
    assert 'raise ValueError("liste doit etre non vide")' in source_code
    assert "assert " not in source_code

    optimized_script = f"""
import runpy

minimum = runpy.run_path({str(MINIMUM_SOURCE)!r})["minimum"]
try:
    minimum([])
except ValueError as error:
    if str(error) != "liste doit etre non vide":
        raise RuntimeError(f"message inattendu: {{error}}")
else:
    raise RuntimeError("liste vide acceptee")
print("liste vide refusee")
"""
    optimized = subprocess.run(
        [sys.executable, "-O", "-c", optimized_script],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert optimized.returncode == 0, optimized.stdout + optimized.stderr
    assert optimized.stdout == "liste vide refusee\n"
    assert optimized.stderr == ""

    tex = MINIMUM_CORRECTION.read_text(encoding="utf-8")
    sequence = re.compile(
        r"(?m)^% PYTHON-SOURCE: code/minimum\.py\n"
        r"\\begin\{python\}(?P<python>.*?)\\end\{python\}",
        re.DOTALL,
    )
    matches = list(sequence.finditer(tex))
    assert len(matches) == 1, "la sequence Python marquee doit etre unique"
    assert matches[0].group("python") == f"\n{source_code}"

    correction_record = {
        "id": "1NSI-LANGAGE-RE-C4-CORRIGE",
        "path": "NSI/chapitres/1NSI-LANGAGE/corriges/1NSI-LANGAGE-RE-C4-CORRIGE.tex",
        "metadata": {},
        "scope": "object",
        "chapter": "1NSI-LANGAGE",
    }
    manifest = review_module.dependency_manifest(
        correction_record, [correction_record], REPO_ROOT
    )
    assert manifest["python"] == [
        {
            "path": "NSI/chapitres/1NSI-LANGAGE/code/minimum.py",
            "sha256": "sha256:"
            + hashlib.sha256(source_code.encode("utf-8")).hexdigest(),
        }
    ]

    assert '"type_objet": "corrige"' in tex.splitlines()[0]
    assert r"\textbf{Précondition : la liste est non vide.}" in tex
    assert "déclenchant" in tex
    assert "ValueError" in tex
    assert re.search(
        r"% BEGIN-VERIFY\n"
        r"% def minimum\(liste\):.*?"
        r"% assert minimum\(\[5, 3, 8\]\) == 3.*?"
        r"% try:.*?"
        r"%     minimum\(\[\]\).*?"
        r"% except ValueError as erreur:.*?"
        r'%     assert str\(erreur\) == "liste doit etre non vide".*?'
        r"% else:.*?"
        r"%     raise AssertionError.*?"
        r"% END-VERIFY",
        tex,
        re.DOTALL,
    )

    verification = subprocess.run(
        ["python", "scripts/verify_python.py", "--chap", "1NSI-LANGAGE", "--check"],
        cwd=NSI_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert verification.returncode == 0, verification.stdout + verification.stderr


def test_minimum_remediation_states_nonempty_precondition_and_matches_answer() -> None:
    assert MINIMUM_REMEDIATION.is_file()
    assert MINIMUM_SOURCE.is_file()

    source_code = MINIMUM_SOURCE.read_text(encoding="utf-8")
    tex = MINIMUM_REMEDIATION.read_text(encoding="utf-8")
    exercise = re.search(
        r"\\begin\{exercice\}.*?\\end\{exercice\}", tex, re.DOTALL
    )
    assert exercise is not None
    visible_text = exercise.group(0)
    normalized_visible = " ".join(visible_text.split())
    assert "liste non vide" in normalized_visible
    assert visible_text.index("liste non vide") < visible_text.index(r"\begin{python}")
    assert r"Le cas \lstinline{[]} est hors précondition." in visible_text
    assert "justifier" in visible_text.lower()
    assert "def minimum(liste):" not in visible_text
    assert 'assert len(liste) > 0, "liste doit etre non vide"' not in visible_text
    assert "AssertionError" not in visible_text

    marker = "% PYTHON-SOURCE: code/minimum.py"
    assert tex.count(marker) == 1
    verify_matches = list(
        re.finditer(
            r"% BEGIN-VERIFY\n(?P<verify>.*?)% END-VERIFY", tex, re.DOTALL
        )
    )
    assert len(verify_matches) == 1
    verify_match = verify_matches[0]
    verify_code = _uncomment(verify_match.group("verify"))
    canonical_code = source_code.rstrip("\n")
    assert verify_code.count(canonical_code) == 1
    outside_verify = tex[: verify_match.start()] + tex[verify_match.end() :]
    assert canonical_code not in outside_verify
    assert re.search(
        r"try:\n"
        r"    minimum\(\[\]\)\n"
        r"except ValueError as erreur:\n"
        r'    assert str\(erreur\) == "liste doit etre non vide"\n'
        r"else:\n"
        r"    raise AssertionError",
        verify_code,
    )

    remediation_record = {
        "id": "1NSI-LANGAGE-RE-C4",
        "path": "NSI/chapitres/1NSI-LANGAGE/remediation/1NSI-LANGAGE-RE-C4.tex",
        "metadata": {},
        "scope": "object",
        "chapter": "1NSI-LANGAGE",
    }
    manifest = review_module.dependency_manifest(
        remediation_record, [remediation_record], REPO_ROOT
    )
    assert manifest["python"] == [
        {
            "path": "NSI/chapitres/1NSI-LANGAGE/code/minimum.py",
            "sha256": "sha256:"
            + hashlib.sha256(source_code.encode("utf-8")).hexdigest(),
        }
    ]


def test_avancement_canonical_source_rejects_empty_milestones() -> None:
    assert AVANCEMENT_COURSE.is_file()
    assert AVANCEMENT_SOURCE.is_file()

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        namespace = runpy.run_path(str(AVANCEMENT_SOURCE))
    assert stdout.getvalue() == "40.0\nFonctionnalites completes\n"

    avancement = namespace["avancement"]
    prochain_jalon = namespace["prochain_jalon"]
    assert avancement.__doc__ is not None
    assert "Precondition : la liste contient au moins un jalon." in avancement.__doc__
    assert avancement(namespace["jalons"]) == 40.0
    assert avancement([{"nom": "Debut", "termine": False}]) == 0.0
    assert avancement([{"nom": "Fin", "termine": True}]) == 100.0
    with pytest.raises(ValueError) as error:
        avancement([])
    assert str(error.value) == "au moins un jalon est requis"
    assert prochain_jalon(namespace["jalons"]) == "Fonctionnalites completes"
    assert [jalon["nom"] for jalon in namespace["jalons"]] == [
        "Cahier des charges",
        "Prototype minimal",
        "Fonctionnalites completes",
        "Tests et correction de bugs",
        "Presentation finale",
    ]

    source_code = AVANCEMENT_SOURCE.read_text(encoding="utf-8")
    assert source_code.isascii()
    assert 'raise ValueError("au moins un jalon est requis")' in source_code
    assert "assert " not in source_code

    optimized_script = f"""
import contextlib
import io
import runpy

with contextlib.redirect_stdout(io.StringIO()):
    avancement = runpy.run_path({str(AVANCEMENT_SOURCE)!r})["avancement"]
try:
    avancement([])
except ValueError as error:
    if str(error) != "au moins un jalon est requis":
        raise RuntimeError(f"message inattendu: {{error}}")
else:
    raise RuntimeError("liste vide acceptee")
print("liste vide refusee")
"""
    optimized = subprocess.run(
        [sys.executable, "-O", "-c", optimized_script],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert optimized.returncode == 0, optimized.stdout + optimized.stderr
    assert optimized.stdout == "liste vide refusee\n"
    assert optimized.stderr == ""

    tex = AVANCEMENT_COURSE.read_text(encoding="utf-8")
    sequence = re.compile(
        r"(?m)^% PYTHON-SOURCE: code/avancement\.py\n"
        r"\\begin\{python\}(?P<python>.*?)\\end\{python\}\n\n"
        r"\\begin\{console\}(?P<console>.*?)\\end\{console\}",
        re.DOTALL,
    )
    matches = list(sequence.finditer(tex))
    assert len(matches) == 1, "la sequence Python marquee doit etre unique"
    assert matches[0].group("python") == f"\n{source_code}"
    assert matches[0].group("console") == f"\n{stdout.getvalue()}"

    course_record = {
        "id": "1NSI-PM-COURS-C2",
        "path": (
            "NSI/chapitres/1NSI-PROJET-METHODES/cours/"
            "1NSI-PM-COURS-C2.tex"
        ),
        "metadata": {},
        "scope": "object",
        "chapter": "1NSI-PROJET-METHODES",
    }
    manifest = review_module.dependency_manifest(
        course_record, [course_record], REPO_ROOT
    )
    assert manifest["python"] == [
        {
            "path": (
                "NSI/chapitres/1NSI-PROJET-METHODES/code/avancement.py"
            ),
            "sha256": "sha256:"
            + hashlib.sha256(source_code.encode("utf-8")).hexdigest(),
        }
    ]

    assert r"\textbf{Précondition : la liste des jalons est non vide.}" in tex
    assert "# 40.0" not in tex
    assert "# Fonctionnalites completes" not in tex
    verify_matches = list(
        re.finditer(
            r"% BEGIN-VERIFY\n(?P<verify>.*?)% END-VERIFY", tex, re.DOTALL
        )
    )
    assert len(verify_matches) == 1
    verify_code = _uncomment(verify_matches[0].group("verify"))
    assert verify_code.count(source_code.rstrip("\n")) == 1
    assert "assert avancement(jalons) == 40.0" in verify_code
    assert "assert avancement(jalons_non_commences) == 0.0" in verify_code
    assert "assert avancement(jalons_termines) == 100.0" in verify_code
    assert re.search(
        r"try:\n"
        r"    avancement\(\[\]\)\n"
        r"except ValueError as erreur:\n"
        r'    assert str\(erreur\) == "au moins un jalon est requis"\n'
        r"else:\n"
        r"    raise AssertionError",
        verify_code,
    )


def test_weighted_mean_rejects_invalid_weights_under_optimization() -> None:
    assert WEIGHTED_MEAN_COURSE.is_file()
    assert WEIGHTED_MEAN_SOURCE.is_file()

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        namespace = runpy.run_path(str(WEIGHTED_MEAN_SOURCE))
    assert stdout.getvalue() == ""

    moyenne_ponderee = namespace["moyenne_ponderee"]
    assert moyenne_ponderee([12, 15], [1, 3]) == 14.25

    invalid_cases = [
        (
            [12, 15, 18],
            [1, 2],
            "valeurs et poids doivent avoir la meme longueur",
        ),
        ([12, 15], [1, -0.5], "les poids doivent etre non negatifs"),
        ([12, 15], [1, float("nan")], "les poids doivent etre non negatifs"),
        ([12, 15], [0, 0], "la somme des poids doit etre strictement positive"),
        ([], [], "la somme des poids doit etre strictement positive"),
    ]
    for valeurs, poids, message in invalid_cases:
        with pytest.raises(ValueError) as error:
            moyenne_ponderee(valeurs, poids)
        assert str(error.value) == message

    optimized_script = f"""
import runpy

moyenne_ponderee = runpy.run_path({str(WEIGHTED_MEAN_SOURCE)!r})[
    "moyenne_ponderee"
]
cases = [
    ([12, 15, 18], [1, 2], "valeurs et poids doivent avoir la meme longueur"),
    ([12, 15], [1, -0.5], "les poids doivent etre non negatifs"),
    ([12, 15], [1, float("nan")], "les poids doivent etre non negatifs"),
    ([12, 15], [0, 0], "la somme des poids doit etre strictement positive"),
    ([], [], "la somme des poids doit etre strictement positive"),
]
for valeurs, poids, message in cases:
    try:
        moyenne_ponderee(valeurs, poids)
    except ValueError as error:
        if str(error) != message:
            raise RuntimeError(f"message inattendu: {{error}}")
    else:
        raise RuntimeError(f"entree invalide acceptee: {{valeurs}}, {{poids}}")
print("5 entrees invalides refusees")
"""
    optimized = subprocess.run(
        [sys.executable, "-O", "-c", optimized_script],
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    assert optimized.returncode == 0, optimized.stdout + optimized.stderr
    assert optimized.stdout == "5 entrees invalides refusees\n"
    assert optimized.stderr == ""

    source_code = WEIGHTED_MEAN_SOURCE.read_text(encoding="utf-8")
    assert source_code.isascii()
    assert "assert " not in source_code
    assert source_code.count("raise ValueError(") == 3

    tex = WEIGHTED_MEAN_COURSE.read_text(encoding="utf-8")
    sequence = re.compile(
        r"(?m)^% PYTHON-SOURCE: code/moyenne_ponderee\.py\n"
        r"\\begin\{python\}(?P<python>.*?)\\end\{python\}",
        re.DOTALL,
    )
    matches = list(sequence.finditer(tex))
    assert len(matches) == 1, "la sequence Python marquee doit etre unique"
    assert matches[0].group("python") == f"\n{source_code}"

    course_record = {
        "id": "1NSI-PM-COURS-C3",
        "path": (
            "NSI/chapitres/1NSI-PROJET-METHODES/cours/"
            "1NSI-PM-COURS-C3.tex"
        ),
        "metadata": {},
        "scope": "object",
        "chapter": "1NSI-PROJET-METHODES",
    }
    manifest = review_module.dependency_manifest(
        course_record, [course_record], REPO_ROOT
    )
    assert manifest["python"] == [
        {
            "path": (
                "NSI/chapitres/1NSI-PROJET-METHODES/code/"
                "moyenne_ponderee.py"
            ),
            "sha256": "sha256:"
            + hashlib.sha256(source_code.encode("utf-8")).hexdigest(),
        }
    ]

    assert "combinaison convexe" in tex
    assert r"\min(\texttt{valeurs})" in tex
    assert r"\max(\texttt{valeurs})" in tex
    assert "nécessairement non vide" in tex
    assert "moyenne_ponderee_bugue([12, 15, 18], [1, 2])" in tex
    assert "IndexError: list index out of range" in tex

    verify_matches = list(
        re.finditer(
            r"% BEGIN-VERIFY\n(?P<verify>.*?)% END-VERIFY", tex, re.DOTALL
        )
    )
    assert len(verify_matches) == 2
    verify_code = _uncomment(verify_matches[1].group("verify"))
    assert verify_code.count(source_code.rstrip("\n")) == 1
    assert "assert moyenne_ponderee([12, 15], [1, 3]) == 14.25" in verify_code
    for valeurs, poids, message in invalid_cases:
        if any(isinstance(poids_i, float) and poids_i != poids_i for poids_i in poids):
            call = 'moyenne_ponderee([12, 15], [1, float("nan")])'
        else:
            call = f"moyenne_ponderee({valeurs!r}, {poids!r})"
        assert call in verify_code
        assert f'assert str(erreur) == "{message}"' in verify_code
        assert "except ValueError as erreur:" in verify_code


def test_table_join_rejects_overlapping_nonkey_columns() -> None:
    assert TABLE_JOIN_COURSE.is_file()
    assert TABLE_JOIN_SOURCE.is_file()

    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        namespace = runpy.run_path(str(TABLE_JOIN_SOURCE))
    expected = [
        {"nom": "Ali", "age": 16, "seances": 12},
        {"nom": "Sami", "age": 15, "seances": 9},
        {"nom": "Yasmine", "age": 22, "seances": 15},
    ]
    assert namespace["resultat"] == expected
    assert stdout.getvalue() == f"{expected!r}\n"

    fusionner = namespace["fusionner"]
    table1 = [{"nom": "Ali"}, {"nom": "Sami", "age": 15}]
    table2 = [
        {"nom": "Ali", "seances": 12},
        {"nom": "Sami", "age": 16},
    ]
    with pytest.raises(ValueError) as error:
        fusionner(table1, table2, "nom")
    message = "les colonnes hors cle doivent etre disjointes"
    assert str(error.value) == message

    optimized_probe = """
import runpy
import sys

fusionner = runpy.run_path(sys.argv[1])["fusionner"]
table1 = [{"nom": "Ali"}, {"nom": "Sami", "age": 15}]
table2 = [{"nom": "Ali", "seances": 12}, {"nom": "Sami", "age": 16}]
try:
    fusionner(table1, table2, "nom")
except ValueError as error:
    if str(error) != "les colonnes hors cle doivent etre disjointes":
        raise RuntimeError(f"message inattendu: {error}")
else:
    raise RuntimeError("la collision doit etre refusee")
"""
    completed = subprocess.run(
        [sys.executable, "-I", "-O", "-c", optimized_probe, str(TABLE_JOIN_SOURCE)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr

    source_code = TABLE_JOIN_SOURCE.read_text(encoding="utf-8")
    assert source_code.isascii()
    assert source_code.index("colonnes1 =") < source_code.index("index2 =")
    assert source_code.index("colonnes2 =") < source_code.index("index2 =")
    guard = "if not colonnes1.isdisjoint(colonnes2):"
    assert source_code.index(guard) < source_code.index("index2 =")
    assert 'raise ValueError("les colonnes hors cle doivent etre disjointes")' in (
        source_code
    )
    assert "assert colonnes1.isdisjoint(colonnes2)" not in source_code
    assert "index2 = {ligne[cle]: ligne for ligne in table2}" in source_code

    tex = TABLE_JOIN_COURSE.read_text(encoding="utf-8")
    sequence = re.compile(
        r"(?m)^% PYTHON-SOURCE: code/fusionner\.py\n"
        r"\\begin\{python\}(?P<python>.*?)\\end\{python\}\n\n"
        r"\\begin\{console\}(?P<console>.*?)\\end\{console\}",
        re.DOTALL,
    )
    matches = list(sequence.finditer(tex))
    assert len(matches) == 1, "la sequence Python marquee doit etre unique"
    assert matches[0].group("python") == f"\n{source_code}"
    assert matches[0].group("console") == f"\n{stdout.getvalue()}"

    course_record = {
        "id": "1NSI-TAB-COURS-C4",
        "path": "NSI/chapitres/1NSI-TABLES/cours/1NSI-TAB-COURS-C4.tex",
        "metadata": {},
        "scope": "object",
        "chapter": "1NSI-TABLES",
    }
    manifest = review_module.dependency_manifest(
        course_record, [course_record], REPO_ROOT
    )
    assert manifest["python"] == [
        {
            "path": "NSI/chapitres/1NSI-TABLES/code/fusionner.py",
            "sha256": "sha256:"
            + hashlib.sha256(source_code.encode("utf-8")).hexdigest(),
        }
    ]

    assert "colonnes hors clé des deux tables doivent être disjointes" in tex
    assert "# [{'nom':" not in tex
    verify_matches = list(
        re.finditer(
            r"% BEGIN-VERIFY\n(?P<verify>.*?)% END-VERIFY", tex, re.DOTALL
        )
    )
    assert len(verify_matches) == 2
    verify_blocks = [_uncomment(match.group("verify")) for match in verify_matches]
    assert verify_blocks[0].count(source_code.rstrip("\n")) == 1
    for verify_code in verify_blocks:
        assert guard in verify_code
        assert 'raise ValueError("les colonnes hors cle doivent etre disjointes")' in (
            verify_code
        )
        assert "assert colonnes1.isdisjoint(colonnes2)" not in verify_code
        assert message in verify_code
    assert "assert resultat ==" in verify_blocks[0]
    assert re.search(
        r"try:\n"
        r"    fusionner\(table_collision1, table_collision2, \"nom\"\)\n"
        r"except ValueError as erreur:\n"
        rf'    assert str\(erreur\) == "{message}"\n'
        r"else:\n"
        r"    raise AssertionError",
        verify_blocks[0],
    )

    execution = review_module.execution_observation(course_record, REPO_ROOT)
    assert execution is not None
    assert execution["fresh_verdict"] == "pass"
    assert execution["matches_receipt"] is True
    assert execution["anomalies"] == []


def test_server_code_is_normally_not_sent_in_http_response() -> None:
    assert WEB_SERVER_COURSE.is_file()

    tex = WEB_SERVER_COURSE.read_text(encoding="utf-8")
    property_match = re.search(
        r"\\propriete\[Ce qui s'exécute où\]\{(?P<body>.*?)\n\}",
        tex,
        re.DOTALL,
    )
    assert property_match is not None
    property_text = " ".join(property_match.group("body").split())

    assert "s'exécute côté serveur" in property_text
    assert "n'est normalement pas transmis" in property_text
    assert "réponse HTTP destinée au navigateur" in property_text
    assert "l'utilisateur ne voit jamais ce code" not in property_text
    assert "publiées ou divulguées par une autre voie" in property_text
    assert "distinct de leur transmission par le protocole HTTP" not in property_text
    assert (
        "cet accès éventuel ne signifie pas qu'elles figurent dans la réponse HTTP "
        "générée par leur exécution"
        in property_text
    )


def test_grid_course_names_two_level_copy_and_states_atomic_cell_contract() -> None:
    assert GRID_COPY_COURSE.is_file()

    tex = GRID_COPY_COURSE.read_text(encoding="utf-8")
    assert "Pour une copie profonde" not in tex
    assert "copie des deux premiers niveaux" in tex
    assert "cellules sont des valeurs scalaires atomiques non mutables" in tex
    assert "les conteneurs imbriqués sont exclus" in tex
    assert r"\lstinline{[[[1]]]}" in tex
    assert "ne constitue pas une copie profonde générale" in tex

    assert GRID_COPY_SOURCE.is_file()
    stdout = io.StringIO()
    with contextlib.redirect_stdout(stdout):
        namespace = runpy.run_path(str(GRID_COPY_SOURCE))
    assert stdout.getvalue() == ""

    copier_grille_deux_niveaux = namespace["copier_grille_deux_niveaux"]
    grille = [[1, 2], [3, 4]]
    copie = copier_grille_deux_niveaux(grille)
    assert copie == grille
    assert copie is not grille
    assert all(ligne_copie is not ligne for ligne_copie, ligne in zip(copie, grille))
    copie[0][0] = 99
    assert grille == [[1, 2], [3, 4]]

    hors_contrat = [[[1]]]
    copie_hors_contrat = copier_grille_deux_niveaux(hors_contrat)
    assert copie_hors_contrat[0][0] is hors_contrat[0][0]
    copie_hors_contrat[0][0].append(2)
    assert hors_contrat == [[[1, 2]]]

    source_code = GRID_COPY_SOURCE.read_text(encoding="utf-8")
    expected_source = '''def copier_grille_deux_niveaux(grille):
    """Copie la liste externe et chaque ligne.

    Precondition : les cellules sont des valeurs scalaires atomiques non mutables,
    sans conteneur imbrique.
    """
    return [list(ligne) for ligne in grille]
'''
    assert source_code == expected_source
    assert source_code.isascii()

    sequence = re.compile(
        r"(?m)^% PYTHON-SOURCE: code/copier_grille_deux_niveaux\.py\n"
        r"\\begin\{codereference\}\{.*?\}\n"
        r"\\begin\{python\}(?P<python>.*?)\\end\{python\}",
        re.DOTALL,
    )
    matches = list(sequence.finditer(tex))
    assert len(matches) == 1, "la sequence Python marquee doit etre unique"
    assert matches[0].group("python") == f"\n{source_code}"

    course_record = {
        "id": "1NSI-TC-COURS-C5",
        "path": (
            "NSI/chapitres/1NSI-TYPES-CONSTRUITS/cours/"
            "1NSI-TC-COURS-C5.tex"
        ),
        "metadata": {},
        "scope": "object",
        "chapter": "1NSI-TYPES-CONSTRUITS",
    }
    manifest = review_module.dependency_manifest(
        course_record, [course_record], REPO_ROOT
    )
    assert manifest["python"] == [
        {
            "path": (
                "NSI/chapitres/1NSI-TYPES-CONSTRUITS/code/"
                "copier_grille_deux_niveaux.py"
            ),
            "sha256": "sha256:"
            + hashlib.sha256(source_code.encode("utf-8")).hexdigest(),
        }
    ]

    verify_matches = list(
        re.finditer(
            r"% BEGIN-VERIFY\n(?P<verify>.*?)% END-VERIFY", tex, re.DOTALL
        )
    )
    verify_blocks = [_uncomment(match.group("verify")) for match in verify_matches]
    matching_blocks = [
        block
        for block in verify_blocks
        if "def copier_grille_deux_niveaux" in block
    ]
    assert len(matching_blocks) == 1
    verify_code = matching_blocks[0]
    assert verify_code.count(source_code.rstrip("\n")) == 1
    assert "assert copie is not grille" in verify_code
    assert "assert all(" in verify_code
    assert "copie[0][0] = 99" in verify_code
    assert "assert grille == [[1, 2], [3, 4]]" in verify_code
    assert "hors_contrat = [[[1]]]" in verify_code
    assert "is hors_contrat[0][0]" in verify_code


def test_grid_exercise_053_and_answer_share_two_level_contract() -> None:
    assert GRID_COPY_EXERCISE_053.is_file()
    assert GRID_COPY_ANSWER_053.is_file()
    assert GRID_COPY_SOURCE.is_file()

    exercise = GRID_COPY_EXERCISE_053.read_text(encoding="utf-8")
    answer = GRID_COPY_ANSWER_053.read_text(encoding="utf-8")
    source_code = GRID_COPY_SOURCE.read_text(encoding="utf-8")

    shallow_program = """grille = [[1, 2], [3, 4]]
copie = list(grille)
copie[0][0] = 99
print(grille[0][0])
copie[0] = [10, 20]
print(grille[0])"""
    exercise_programs = re.findall(
        r"\\begin\{python\}\n(?P<python>.*?)\\end\{python\}",
        exercise,
        re.DOTALL,
    )
    assert exercise_programs[0] == shallow_program + "\n"
    assert "% EXPECTED\n% 99\n% [99, 2]\n% END-TRACE" in exercise
    assert "\\begin{console}\n99\n[99, 2]\n\\end{console}" in answer

    required_contract = (
        "copier_grille_deux_niveaux",
        "copie des deux premiers niveaux",
        "cellules sont des valeurs scalaires atomiques non mutables",
        "sans conteneur imbriqué",
        "modifications de la structure externe",
        "remplacements de lignes",
        "réaffectations de cellules",
        r"\lstinline{[[[1]]]}",
        "cellule-liste reste partagée",
    )
    for tex in (exercise, answer):
        normalized = " ".join(tex.split())
        for phrase in required_contract:
            assert phrase in normalized
        assert "% PYTHON-SOURCE: code/copier_grille_deux_niveaux.py" in tex
        assert "créer une copie profonde" not in normalized
        assert "aucune modification" not in normalized
        assert "la copie est bien profonde" not in normalized

    sequence = re.compile(
        r"(?m)^% PYTHON-SOURCE: code/copier_grille_deux_niveaux\.py\n"
        r"\\begin\{python\}(?P<python>.*?)\\end\{python\}",
        re.DOTALL,
    )
    matches = list(sequence.finditer(answer))
    assert len(matches) == 1, "le bloc Python du corrigé doit être unique"
    assert matches[0].group("python") == f"\n{source_code}"

    python_dependency = {
        "path": (
            "NSI/chapitres/1NSI-TYPES-CONSTRUITS/code/"
            "copier_grille_deux_niveaux.py"
        ),
        "sha256": "sha256:"
        + hashlib.sha256(source_code.encode("utf-8")).hexdigest(),
    }
    records = (
        {
            "id": "1NSI-TC-EX-053",
            "path": (
                "NSI/chapitres/1NSI-TYPES-CONSTRUITS/exercices/"
                "1NSI-TC-EX-053.tex"
            ),
            "metadata": {},
            "scope": "object",
            "chapter": "1NSI-TYPES-CONSTRUITS",
        },
        {
            "id": "1NSI-TC-CO-053",
            "path": (
                "NSI/chapitres/1NSI-TYPES-CONSTRUITS/corriges/"
                "1NSI-TC-CO-053.tex"
            ),
            "metadata": {},
            "scope": "object",
            "chapter": "1NSI-TYPES-CONSTRUITS",
        },
    )
    for record in records:
        manifest = review_module.dependency_manifest(record, [record], REPO_ROOT)
        assert manifest["python"] == [python_dependency]

    verify_matches = list(
        re.finditer(
            r"% BEGIN-VERIFY\n(?P<verify>.*?)% END-VERIFY", answer, re.DOTALL
        )
    )
    assert len(verify_matches) == 1
    verify_code = _uncomment(verify_matches[0].group("verify"))
    assert verify_code.count(source_code.rstrip("\n")) == 1
    assert "grille2 = [[1, 2], [3, 4]]" in verify_code
    assert "copie_deux_niveaux = copier_grille_deux_niveaux(grille2)" in verify_code
    assert "copie_deux_niveaux[0][0] = 99" in verify_code
    assert "assert grille2 == [[1, 2], [3, 4]]" in verify_code
    assert "hors_contrat = [[[1]]]" in verify_code
    assert "is hors_contrat[0][0]" in verify_code
    assert "assert hors_contrat == [[[1, 2]]]" in verify_code


def test_grid_exercise_054_uses_two_level_function_name_and_contract() -> None:
    assert GRID_COPY_EXERCISE_054.is_file()
    assert GRID_COPY_ANSWER_054.is_file()
    assert GRID_COPY_SOURCE.is_file()

    exercise = GRID_COPY_EXERCISE_054.read_text(encoding="utf-8")
    answer = GRID_COPY_ANSWER_054.read_text(encoding="utf-8")
    source_code = GRID_COPY_SOURCE.read_text(encoding="utf-8")
    scenario = """g = [[1, 2], [3, 4]]
c = copier_grille_deux_niveaux(g)
c[0][0] = 99
print(g[0][0])"""

    required_contract = (
        "copier_grille_deux_niveaux",
        "copie des deux premiers niveaux",
        "cellules sont des valeurs scalaires atomiques non mutables",
        "sans conteneur imbriqué",
        "modifications de la structure externe",
        "remplacements de lignes",
        "réaffectations de cellules",
        r"\lstinline{[[[1]]]}",
        "cellule-liste reste partagée",
        "hors contrat",
    )
    forbidden_claims = (
        "copie_profonde_grille",
        "copie entièrement",
        "copie profonde de la grille",
        "la copie est bien profonde",
        "Pour que la copie soit profonde",
        "aucune modification de la copie",
        "# doit afficher 1",
        "# affiche 1",
    )
    for tex in (exercise, answer):
        normalized = " ".join(tex.split())
        for phrase in required_contract:
            assert phrase in normalized
        for phrase in forbidden_claims:
            assert phrase not in normalized
        assert "% PYTHON-SOURCE: code/copier_grille_deux_niveaux.py" in tex
        assert "\\begin{console}\n1\n\\end{console}" in tex

    visible_exercise_programs = re.findall(
        r"\\begin\{python\}\n(?P<python>.*?)\\end\{python\}",
        exercise,
        re.DOTALL,
    )
    assert visible_exercise_programs == [scenario + "\n"]
    assert "def copier_grille_deux_niveaux" not in visible_exercise_programs[0]

    visible_answer_programs = re.findall(
        r"\\begin\{python\}\n(?P<python>.*?)\\end\{python\}",
        answer,
        re.DOTALL,
    )
    assert visible_answer_programs == [source_code, scenario + "\n"]

    python_dependency = {
        "path": (
            "NSI/chapitres/1NSI-TYPES-CONSTRUITS/code/"
            "copier_grille_deux_niveaux.py"
        ),
        "sha256": "sha256:"
        + hashlib.sha256(source_code.encode("utf-8")).hexdigest(),
    }
    records = (
        {
            "id": "1NSI-TC-EX-054",
            "path": (
                "NSI/chapitres/1NSI-TYPES-CONSTRUITS/exercices/"
                "1NSI-TC-EX-054.tex"
            ),
            "metadata": {},
            "scope": "object",
            "chapter": "1NSI-TYPES-CONSTRUITS",
        },
        {
            "id": "1NSI-TC-CO-054",
            "path": (
                "NSI/chapitres/1NSI-TYPES-CONSTRUITS/corriges/"
                "1NSI-TC-CO-054.tex"
            ),
            "metadata": {},
            "scope": "object",
            "chapter": "1NSI-TYPES-CONSTRUITS",
        },
    )
    for record in records:
        manifest = review_module.dependency_manifest(record, [record], REPO_ROOT)
        assert manifest["python"] == [python_dependency]

    for tex in (exercise, answer):
        trace_matches = list(
            re.finditer(
                r"% BEGIN-TRACE\n(?P<trace>.*?)% EXPECTED\n"
                r"(?P<expected>.*?)% END-TRACE",
                tex,
                re.DOTALL,
            )
        )
        assert len(trace_matches) == 1
        trace_code = _uncomment(trace_matches[0].group("trace"))
        expected = _uncomment(trace_matches[0].group("expected")) + "\n"
        assert trace_code == source_code.rstrip("\n") + "\n" + scenario
        stdout = subprocess.run(
            ["python", "-c", trace_code],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        assert stdout == expected == "1\n"

        verify_matches = list(
            re.finditer(
                r"% BEGIN-VERIFY\n(?P<verify>.*?)% END-VERIFY",
                tex,
                re.DOTALL,
            )
        )
        assert len(verify_matches) == 1
        verify_code = _uncomment(verify_matches[0].group("verify"))
        assert verify_code.count(source_code.rstrip("\n")) == 1
        assert scenario in verify_code
        assert "assert copie is not grille" in verify_code
        assert "assert all(" in verify_code
        assert "hors_contrat = [[[1]]]" in verify_code
        assert "is hors_contrat[0][0]" in verify_code
        assert "assert hors_contrat == [[[1, 2]]]" in verify_code
        subprocess.run(["python", "-c", verify_code], check=True)


@pytest.mark.parametrize(
    ("object_id", "relative_path"),
    (
        (
            "1NSI-TC-COURS-C5",
            "NSI/chapitres/1NSI-TYPES-CONSTRUITS/cours/1NSI-TC-COURS-C5.tex",
        ),
        (
            "1NSI-TC-EX-054",
            "NSI/chapitres/1NSI-TYPES-CONSTRUITS/exercices/1NSI-TC-EX-054.tex",
        ),
        (
            "1NSI-TC-CO-054",
            "NSI/chapitres/1NSI-TYPES-CONSTRUITS/corriges/1NSI-TC-CO-054.tex",
        ),
    ),
)
def test_grid_copy_execution_receipts_match_current_blocks(
    object_id: str, relative_path: str
) -> None:
    record = {
        "id": object_id,
        "path": relative_path,
        "metadata": {},
        "scope": "object",
        "chapter": "1NSI-TYPES-CONSTRUITS",
    }
    execution = review_module.execution_observation(record, REPO_ROOT)
    assert execution is not None
    assert execution["fresh_verdict"] == "pass"
    assert execution["matches_receipt"] is True
    assert execution["anomalies"] == []
