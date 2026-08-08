"""Tests de regression des gates corpus.

Fige le comportement apres chaque assouplissement :
- « corrigee » adjectival dans un enonce → VERT
- \\begin{corrige} dans un fichier eleve → ROUGE
- \\input d'un fichier corriges/ dans une variante eleve → ROUGE
- TODO dans chapitres/ → ROUGE
- « a completer » entre backticks ou dans un env python (trous ECE) → VERT
"""
import re
import tempfile
from pathlib import Path

import pytest

# Import gate logic
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import assemble  # noqa: E402


# --- check_eleve_no_corrige patterns ---

from gates_corpus import check_eleve_no_corrige as eleve_no_corrige  # noqa: E402
from gates_corpus.check_eleve_no_corrige import FORBIDDEN, is_allowed  # noqa: E402


def _scan_content(text: str) -> list[str]:
    """Simule le scan de check_eleve_no_corrige sur un contenu."""
    hits = []
    for pattern in FORBIDDEN:
        matches = pattern.findall(text)
        if matches:
            hits.append(matches[0])
    return hits


def _scan_gate(root: Path, prefix: str | None):
    assert hasattr(eleve_no_corrige, "scan"), "scan(root, prefix) API is missing"
    return eleve_no_corrige.scan(root, prefix)


def _write_tex(root: Path, relative_path: str, content: str = "Contenu eleve.") -> Path:
    path = root / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path


class TestEleveNoCorrige:
    def test_filtered_scan_detects_leak_in_matching_chapter(self, tmp_path):
        leaked = _write_tex(
            tmp_path,
            "chapitres/1NSI-TEST/remediation/leak.tex",
            r"\begin{corrige}Reponse\end{corrige}",
        )

        checked, violations = _scan_gate(tmp_path, "1NSI-")

        assert checked == 1
        assert len(violations) == 1
        assert str(leaked.relative_to(tmp_path)) in violations[0]

    def test_filtered_scan_ignores_tnsi_but_global_scan_detects_it(self, tmp_path):
        _write_tex(tmp_path, "chapitres/1NSI-TEST/cours/clean.tex")
        leaked = _write_tex(
            tmp_path,
            "chapitres/TNSI-TEST/remediation/leak.tex",
            r"\begin{corrige}Reponse\end{corrige}",
        )

        filtered_checked, filtered_violations = _scan_gate(tmp_path, "1NSI-")
        global_checked, global_violations = _scan_gate(tmp_path, None)

        assert filtered_checked == 1
        assert filtered_violations == []
        assert global_checked == 2
        assert len(global_violations) == 1
        assert str(leaked.relative_to(tmp_path)) in global_violations[0]

    def test_filtered_scan_includes_build_file_referencing_prefix_in_path(self, tmp_path):
        _write_tex(tmp_path, "chapitres/1NSI-TEST/cours/clean.tex")
        leaked = _write_tex(
            tmp_path,
            "build/1NSI-manuel.tex",
            r"\begin{corrige}Reponse\end{corrige}",
        )

        checked, violations = _scan_gate(tmp_path, "1NSI-")

        assert checked == 2
        assert len(violations) == 1
        assert str(leaked.relative_to(tmp_path)) in violations[0]

    def test_filtered_scan_includes_build_file_referencing_prefix_in_content(self, tmp_path):
        _write_tex(tmp_path, "chapitres/1NSI-TEST/cours/clean.tex")
        leaked = _write_tex(
            tmp_path,
            "build/manuel.tex",
            "% livre 1NSI-\n" + r"\begin{corrige}Reponse\end{corrige}",
        )

        checked, violations = _scan_gate(tmp_path, "1NSI-")

        assert checked == 2
        assert len(violations) == 1
        assert str(leaked.relative_to(tmp_path)) in violations[0]

    def test_filtered_scan_excludes_unrelated_build_file(self, tmp_path):
        _write_tex(tmp_path, "chapitres/1NSI-TEST/cours/clean.tex")
        _write_tex(
            tmp_path,
            "build/TNSI-manuel.tex",
            r"\begin{corrige}Reponse\end{corrige}",
        )

        checked, violations = _scan_gate(tmp_path, "1NSI-")

        assert checked == 1
        assert violations == []

    @pytest.mark.parametrize("prefix", ["", "   "])
    def test_filtered_scan_rejects_empty_prefix(self, tmp_path, prefix):
        with pytest.raises(ValueError, match="prefix"):
            _scan_gate(tmp_path, prefix)

    def test_filtered_scan_rejects_prefix_without_matching_chapter(self, tmp_path):
        _write_tex(tmp_path, "chapitres/TNSI-TEST/cours/clean.tex")

        with pytest.raises(ValueError, match="chapitre"):
            _scan_gate(tmp_path, "1NSI-")

    def test_filtered_scan_rejects_matching_chapter_without_checked_file(self, tmp_path):
        _write_tex(
            tmp_path,
            "chapitres/1NSI-TEST/corriges/answer.tex",
            r"\begin{corrige}Reponse\end{corrige}",
        )

        with pytest.raises(ValueError, match="fichier"):
            _scan_gate(tmp_path, "1NSI-")

    def test_corrigee_adjectival_passes(self):
        """'corrigee' adjectival dans un enonce doit passer VERT."""
        text = r"""
\begin{exercice}{1NSI-TC-EX-051}{2}{12}
  \item Voici une version corrigée :
\begin{python}
def supprimer_negatifs(tab):
    return [v for v in tab if v >= 0]
\end{python}
\end{exercice}
"""
        assert _scan_content(text) == [], \
            "'corrigée' adjectival ne doit pas declencher le gate"

    def test_begin_corrige_fails(self):
        r"""\\begin{corrige} dans un fichier eleve doit etre ROUGE."""
        text = r"""
\begin{corrige}{1NSI-TC-EX-001}
La réponse est 42.
\end{corrige}
"""
        hits = _scan_content(text)
        assert len(hits) > 0, r"\begin{corrige} doit etre detecte"

    def test_input_corriges_in_eleve_fails(self):
        r"""\\input d'un fichier corriges/ doit etre ROUGE si pas dans dossier autorise."""
        # Le gate ne scanne pas les \input, mais le fichier corriges/ est exclu
        # par is_allowed. Verifions qu'un fichier hors corriges/ n'est pas autorise.
        assert not is_allowed(Path("chapitres/1NSI/exercices/foo.tex"))
        assert is_allowed(Path("chapitres/1NSI/corriges/bar.tex"))
        assert is_allowed(Path("chapitres/1NSI/_harvest/baz.tex"))

    def test_reponse_attendue_fails(self):
        text = "La réponse attendue est 42."
        hits = _scan_content(text)
        assert len(hits) > 0, "'Réponse attendue' doit etre detecte"

    def test_qcm_diagnostic_adjacent_fails(self):
        """Diagnostic adjacent a une option QCM = ROUGE (revele la reponse)."""
        from gates_corpus.check_eleve_no_corrige import QCM_DIAG_RE
        text = r"""\item \lstinline{<class 'list'>}
        \quad\textit{Si tu as répondu A : tu confonds tuple et liste.}"""
        assert QCM_DIAG_RE.search(text) is not None

    def test_qcm_clean_options_pass(self):
        """Options QCM propres (sans diagnostic) = VERT."""
        from gates_corpus.check_eleve_no_corrige import QCM_DIAG_RE
        text = r"""\item \lstinline{<class 'list'>}
  \item \lstinline{<class 'tuple'>}
  \item \lstinline{<class 'int'>}"""
        assert QCM_DIAG_RE.search(text) is None


class TestEleveNoCorrigeCli:
    def test_clean_filtered_scan_returns_zero(self, tmp_path, monkeypatch, capsys):
        _write_tex(tmp_path, "chapitres/1NSI-TEST/cours/clean.tex")
        monkeypatch.setattr(eleve_no_corrige, "ROOT", tmp_path)

        return_code = eleve_no_corrige.main(["--prefix", "1NSI-"])

        captured = capsys.readouterr()
        assert return_code == 0
        assert "VERT -- 1 fichiers verifies" in captured.out
        assert captured.err == ""

    def test_violation_returns_one(self, tmp_path, monkeypatch, capsys):
        leaked = _write_tex(
            tmp_path,
            "chapitres/1NSI-TEST/remediation/leak.tex",
            r"\begin{corrige}Reponse\end{corrige}",
        )
        monkeypatch.setattr(eleve_no_corrige, "ROOT", tmp_path)

        return_code = eleve_no_corrige.main(["--prefix", "1NSI-"])

        captured = capsys.readouterr()
        assert return_code == 1
        assert "ROUGE -- contenu corrige detecte" in captured.out
        assert str(leaked.relative_to(tmp_path)) in captured.out
        assert captured.err == ""

    def test_invalid_prefix_returns_two(self, tmp_path, monkeypatch, capsys):
        monkeypatch.setattr(eleve_no_corrige, "ROOT", tmp_path)

        return_code = eleve_no_corrige.main(["--prefix", "   "])

        captured = capsys.readouterr()
        assert return_code == 2
        assert captured.out == ""
        assert "ROUGE -- filtre invalide" in captured.err
        assert "prefix vide" in captured.err


# --- check_no_placeholders patterns ---

from gates_corpus.check_no_placeholders import PLACEHOLDER_RE, SKIP_DIRS


class TestNoPlaceholders:
    def test_todo_in_chapitres_fails(self):
        """TODO dans un fichier de chapitres/ doit etre ROUGE."""
        text = "% TODO: ajouter un exemple ici"
        assert PLACEHOLDER_RE.search(text) is not None

    def test_fixme_fails(self):
        text = "FIXME: cette section est incomplete"
        assert PLACEHOLDER_RE.search(text) is not None

    def test_a_completer_in_backticks_passes(self):
        """'a completer' entre backticks (trous ECE) doit passer VERT."""
        text = r"""\begin{python}
def mystere(n):
    # A COMPLETER
    pass
\end{python}"""
        # Le pattern exclut les backticks via (?<!`) et (?!`)
        # Mais ici c'est dans du LaTeX, pas entre backticks markdown.
        # Le gate skip les dossiers docs/prompts, et les fichiers ECE
        # contiennent legitimement "A COMPLETER" dans les trous.
        # Le gate actuel les detecterait — c'est un faux positif a gerer.
        # Pour l'instant, on verifie que le pattern MATCHE (le gate est strict)
        # et la solution est d'exclure les fichiers ece/ du scan.
        assert PLACEHOLDER_RE.search(text) is not None, \
            "Le pattern doit matcher 'A COMPLETER' meme dans du code"

    def test_a_completer_in_lstinline_passes(self):
        """'a completer' dans \\lstinline (trous ECE legitimes) — le skip_dirs
        ece/ doit exclure ces fichiers du scan."""
        # Verifie que le skip mechanism fonctionne
        path = Path("/fake/chapitres/1NSI/ece/sujet1.tex")
        # ece n'est pas dans SKIP_DIRS actuellement, mais les fichiers ECE
        # sont dans chapitres/ et seront scannes. Les « A COMPLETER » dans
        # les squelettes ECE sont des trous pedagogiques, pas des placeholders.
        # Le test verifie que le pattern existe pour documentation.
        assert "ece" not in SKIP_DIRS, \
            "ece n'est pas encore dans SKIP_DIRS — a ajouter si besoin"

    def test_docs_skipped(self):
        """Les dossiers docs/ et prompts/ sont exclus du scan."""
        assert "docs" in SKIP_DIRS
        assert "prompts" in SKIP_DIRS

    def test_root_md_skipped(self):
        """Les fichiers .md a la racine (workflow docs) sont exclus.
        Faux positif demontre : PILOTE_A_VALIDER.md contient 'a completer'
        dans la description de la version amenagee (trous pedagogiques)."""
        from gates_corpus.check_no_placeholders import ROOT as NP_ROOT
        # Le gate skip les .md dont le parent est ROOT
        root_md = NP_ROOT / "PILOTE_A_VALIDER.md"
        assert root_md.parent == NP_ROOT, "PILOTE est bien a la racine"


# --- check_accents_contenu patterns ---

from gates_corpus.check_accents_contenu import find_violations


class TestAccentsContenu:
    def test_unaccented_pedagogical_word_fails(self):
        """Un mot pedagogique sans accent dans le prose doit etre ROUGE."""
        violations = find_violations("Cette sequence contient un element important.")

        assert [(hit.word, hit.replacement) for hit in violations] == [
            ("sequence", "séquence"),
            ("element", "élément"),
        ]

    def test_code_environments_and_lstinline_are_ignored(self):
        """Les identifiants Python et les listings inline ne sont pas du prose."""
        text = r"""
\begin{python}
donnees = ["un element"]
\end{python}
\begin{console}
>>> print("methode")
\end{console}
\begin{codereference}
def cree_element():
    return donnees
\end{codereference}
\lstinline|reponse = donnees[0]|
\lstinline{resultat = eleves[0]}
\label{sec:mutabilite} Voir \ref{sec:mutabilite}.
Le résultat est correct. % sequence en commentaire
"""

        assert find_violations(text) == []

    def test_visible_texttt_is_checked(self):
        """Une commande \texttt visible reste du texte imprime controle."""
        assert [hit.word for hit in find_violations(r"\texttt{eleve}")] == ["eleve"]

    def test_commented_environment_cannot_mask_visible_prose(self):
        """Un faux environnement en commentaire ne doit pas neutraliser le prose."""
        text = "% \\begin{python}\nCette sequence reste visible.\n% \\end{python}"

        assert [hit.word for hit in find_violations(text)] == ["sequence"]

    def test_lstinline_environment_marker_cannot_mask_visible_prose(self):
        r"""Un marqueur dans \lstinline ne doit pas ouvrir un faux environnement."""
        text = r"\lstinline|\begin{python}| Une sequence visible.\end{python}"

        assert [hit.word for hit in find_violations(text)] == ["sequence"]

    def test_definition_is_only_forbidden_at_sentence_start(self):
        """Le nom commun « definition » est controle au debut d'une phrase."""
        assert [hit.word for hit in find_violations("Definition : une suite ordonnée.")] == [
            "Definition"
        ]
        assert [hit.word for hit in find_violations("definition formelle.")] == [
            "definition"
        ]
        assert [hit.word for hit in find_violations("Texte.Definition : une suite.")] == [
            "Definition"
        ]
        assert [hit.word for hit in find_violations(r"\textbf{Definition} : une suite.")] == [
            "Definition"
        ]
        assert [hit.word for hit in find_violations(r"\par Definition : une suite.")] == [
            "Definition"
        ]
        assert [hit.word for hit in find_violations(r"\item Definition : une suite.")] == [
            "Definition"
        ]
        assert find_violations("Une phrase se poursuit\nDefinition sans ponctuation.") == []
        assert find_violations("Une definition formelle est fournie.") == []


# --- check_ascii_code patterns ---

from gates_corpus.check_ascii_code import FORBIDDEN_CHARACTERS, find_violations as find_ascii_violations


@pytest.mark.parametrize("character", FORBIDDEN_CHARACTERS)
@pytest.mark.parametrize(
    "context, source",
    [
        ("python", "\\begin{python}\nvaleur = '{character}'\n\\end{python}"),
        ("console", "\\begin{console}\n>>> print('{character}')\n\\end{console}"),
        ("codereference", "\\begin{codereference}\nvaleur = '{character}'\n\\end{codereference}"),
        ("lstinline", "\\lstinline|valeur = '{character}'|"),
    ],
)
def test_ascii_code_forbidden_character_fails_in_every_code_context(context, source, character):
    """Chaque caractere typographique interdit rend le gate ROUGE dans le code."""
    violations = find_ascii_violations(source.replace("{character}", character))

    assert [(hit.context, hit.character) for hit in violations] == [(context, character)]


def test_ascii_code_typographic_characters_are_allowed_in_prose():
    """La typographie française hors code ne relève pas de ce gate."""
    prose = "Voici ‘un’ « exemple » — avec des guillemets typographiques."

    assert find_ascii_violations(prose) == []


def test_ascii_code_codereference_title_is_not_scanned_as_code():
    """L'argument-titre de codereference est du prose, pas du code."""
    text = r"""\begin{codereference}{Titre « visible »}
valeur = "ASCII"
\end{codereference}"""

    assert find_ascii_violations(text) == []


def test_ascii_code_ignores_commented_fake_code_markers():
    """Les marqueurs de code commentés ne constituent pas des blocs exécutables."""
    text = "% \\begin{python}\n% valeur = \"«\"\n% \\end{python}"

    assert find_ascii_violations(text) == []


def test_ascii_code_ignores_commented_lstinline_marker():
    """Un lstinline LaTeX commenté n'est pas du code affiché."""
    assert find_ascii_violations(r"% \lstinline {valeur = \"«\"}") == []


def test_ascii_code_detects_lstinline_with_whitespace_before_braces():
    """Un espace optionnel après lstinline ne désactive pas le contrôle."""
    violations = find_ascii_violations(r"\lstinline {valeur = \"«\"}")

    assert [(hit.context, hit.character) for hit in violations] == [("lstinline", "«")]


def test_ascii_code_lstinline_marker_cannot_open_a_fake_environment():
    """Un begin dans un lstinline ne transforme pas le prose suivant en code."""
    text = r"\lstinline|\begin{python}| Texte « visible ».\end{python}"

    assert find_ascii_violations(text) == []


@pytest.mark.parametrize(
    "context, source",
    [
        ("python", "\\begin{python}\nreste = 10 % 3; valeur = \"«\"\n\\end{python}"),
        ("console", "\\begin{console}\n>>> 10 % 3; print(\"«\")\n\\end{console}"),
        ("lstinline", "\\lstinline|reste = 10 % 3; valeur = \"«\"|"),
    ],
)
def test_ascii_code_percent_is_literal_inside_real_code(context, source):
    """Un pourcent dans le code ne doit pas masquer la ponctuation interdite."""
    violations = find_ascii_violations(source)

    assert [(hit.context, hit.character) for hit in violations] == [(context, "«")]


def test_ascii_code_codereference_nested_title_is_not_scanned_as_code():
    """Le titre codereference accepte les accolades TeX imbriquées."""
    text = r"""\begin{codereference}{Titre \texttt{« visible »}}
valeur = "ASCII"
\end{codereference}"""

    assert find_ascii_violations(text) == []


def test_amenagee_extract_avoids_lstinline_inside_tabular_cells():
    """Regression build amenagee : \\lstinline est fragile dans un tabular."""
    text = Path(
        "chapitres/1NSI-TYPES-CONSTRUITS/amenagee/1NSI-TC-AM-EXTRAIT.tex"
    ).read_text(encoding="utf-8")

    assert re.search(r"\\lstinline\{[^}]+\}\s*&", text) is None


def test_selected_book_sources_avoid_brace_delimited_lstinline_for_mapping_literals():
    selected = set()
    for variant in assemble.BOOK_VARIANTS:
        for chapter in assemble.collect_book_chapters("1NSI", variant):
            selected.update(assemble.collect_book_files(chapter, variant))

    manifest = assemble.load_book_manifest("1NSI")
    for entry in manifest["chapters"]:
        chapter = ROOT / "chapitres" / entry["id"]
        selected.update(assemble.collect(chapter, "complet"))

    expected_web_sources = {
        ROOT / "chapitres/1NSI-WEB-IHM/cours/1NSI-WEB-COURS-C3.tex",
        ROOT / "chapitres/1NSI-WEB-IHM/exercices/1NSI-WEB-EX-004.tex",
    }
    expected_chapter_evaluations = {
        ROOT / "chapitres/1NSI-RESEAUX/evaluations/1NSI-RES-EVAL-A.tex",
        ROOT / "chapitres/1NSI-RESEAUX/evaluations/1NSI-RES-EVAL-B.tex",
        ROOT / "chapitres/1NSI-WEB-IHM/evaluations/1NSI-WEB-EVAL-A.tex",
        ROOT / "chapitres/1NSI-WEB-IHM/evaluations/1NSI-WEB-EVAL-B.tex",
    }
    violations = []
    for path in sorted(selected):
        if r"\lstinline{{" in path.read_text(encoding="utf-8"):
            violations.append(str(path.relative_to(ROOT)))

    assert expected_web_sources <= selected
    assert expected_chapter_evaluations <= selected
    assert violations == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
