"""La page doit dire ce que la source disait — et la mesure doit savoir le nier.

Deux corruptions ont traversé toute une campagne : `ewpage` imprimé en toutes
lettres, et du Python composé avec des guillemets courbes. Aucun contrôle
n'avait jamais lu la page.

Ce module vérifie le contrôle qui la lit. La partie décisive n'est pas qu'il
accepte un rendu fidèle — c'est qu'il refuse un rendu muté : un guillemet
courbé, une ligature fusionnée, un programme composé dans la fonte du texte.
Un contrôle qui ne sait pas dire non ne prouve rien.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_1spe_printed_fidelity as gate  # noqa: E402


# ---------------------------------------------------------------------------
#  Un manuel minuscule, entièrement sous contrôle
# ---------------------------------------------------------------------------

# Le programme témoin porte tout ce qu'une composition peut abîmer : une
# docstring, les deux sortes de guillemets, une f-string, un dictionnaire, un
# caractère échappé, et un opérateur que la fonte du code sait ligaturer.
FIXTURE_CODE = '''def resume(valeurs, seuil):
    """Renvoie les valeurs au-dessus du seuil."""
    if seuil <= 0:
        raise ValueError("seuil strictement positif")
    retenues = {"seuil": seuil, 'unite': "m\\u00b3"}
    for valeur in valeurs:
        print(f"v={valeur!r} > {seuil}")
    return retenues
'''

LISTING_SIZE = 7.54
BODY_SIZE = 9.46
NUMBER_SIZE = 5.32


class FakePage:
    def __init__(self, spans: list[dict[str, Any]]) -> None:
        self._spans = spans

    def get_text(self, kind: str = "text") -> Any:
        if kind == "dict":
            return {"blocks": [{"lines": [{"spans": self._spans}]}]}
        return " ".join(span["text"] for span in self._spans)


class FakeDocument:
    def __init__(self, pages: list[FakePage]) -> None:
        self._pages = pages
        self.page_count = len(pages)

    def __getitem__(self, index: int) -> FakePage:
        return self._pages[index]

    def __enter__(self) -> "FakeDocument":
        return self

    def __exit__(self, *_: object) -> None:
        return None


class FakeFitz:
    def __init__(self, documents: dict[str, FakeDocument]) -> None:
        self._documents = documents

    def open(self, path: Path) -> FakeDocument:
        return self._documents[Path(path).name]


def mono_spans(code: str, *, numbered: bool = False) -> list[dict[str, Any]]:
    """Le programme tel qu'un listing le pose : un span par ligne."""

    spans: list[dict[str, Any]] = []
    for number, line in enumerate(code.splitlines(), start=1):
        if numbered:
            spans.append(
                {
                    "font": "JetBrainsMono-Regular",
                    "size": NUMBER_SIZE,
                    "text": str(number),
                }
            )
        spans.append(
            {"font": "JetBrainsMono-Regular", "size": LISTING_SIZE, "text": line}
        )
    return spans


def body_spans(text: str) -> list[dict[str, Any]]:
    return [{"font": "TeXGyrePagella-Regular", "size": BODY_SIZE, "text": text}]


@pytest.fixture
def manual(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Any:
    """Un manuel complet en miniature, dont le rendu est ce qu'on lui donne."""

    math = tmp_path / "Mathematiques/manuel-maths"
    build = math / "build/MANUEL_1SPE"
    objects = math / "chapitres/1SPE-TEST/cours"
    build.mkdir(parents=True)
    objects.mkdir(parents=True)
    (objects / "10_code.tex").write_text(
        "\\begin{python}\n" + FIXTURE_CODE + "\\end{python}\n", encoding="utf-8"
    )
    # Le vocabulaire surveille est lu dans le corpus : une commande que le
    # manuel miniature n'emploie pas ne peut pas y etre surveillee.
    (objects / "05_transversal.tex").write_text(
        "\\section{Avant-propos}\n\\newpage\n"
        "\\section{Formulaire}\n\\newpage\n"
        "\\section{Index}\n\\newpage\n",
        encoding="utf-8",
    )
    for variant in gate.VARIANTS:
        (build / f"MANUEL_1SPE_{variant}.tex").write_text(
            "\\input{chapitres/1SPE-TEST/cours/10_code}\n", encoding="utf-8"
        )
        (build / f"MANUEL_1SPE_{variant}.pdf").write_bytes(b"%PDF-faux")

    monkeypatch.setattr(gate, "MATH", math)
    monkeypatch.setattr(gate, "BUILD", build)
    monkeypatch.setattr(gate, "ROOT", tmp_path)
    # Le controle connait desormais les six manuels : la racine d'inclusion et
    # le nom du maitre sont des reglages, et le manuel miniature doit les
    # porter aussi, sinon il lit les sources du vrai depot.
    monkeypatch.setattr(gate, "SOURCE_ROOT", math)
    monkeypatch.setattr(gate, "MASTER_STEM", "MANUEL_1SPE")
    for cached in (gate.latex_sources, gate.command_tails, gate.plain_words):
        cached.cache_clear()

    def install(pages: list[FakePage]) -> None:
        documents = {
            f"MANUEL_1SPE_{variant}.pdf": FakeDocument(pages)
            for variant in gate.VARIANTS
        }
        monkeypatch.setattr(gate, "_fitz", lambda: FakeFitz(documents))

    return install


# ---------------------------------------------------------------------------
#  Le rendu fidèle passe
# ---------------------------------------------------------------------------


def test_a_faithful_render_is_accepted(manual: Any) -> None:
    manual([FakePage(mono_spans(FIXTURE_CODE))])

    payload = gate.build()

    assert payload["summary"]["CODE_BLOCKS"] == 2
    assert payload["summary"]["CODE_BLOCK_FAITHFUL"] == 2
    assert payload["summary"]["CODE_BLOCK_NOT_FAITHFUL"] == 0
    assert payload["summary"]["SMART_QUOTE_IN_CODE_TOKEN"] == 0


def test_the_line_numbers_of_a_listing_do_not_break_the_comparison(
    manual: Any,
) -> None:
    """Les numéros sont composés dans la fonte du code sans en être."""

    manual([FakePage(mono_spans(FIXTURE_CODE, numbered=True))])

    assert gate.build()["summary"]["CODE_BLOCK_NOT_FAITHFUL"] == 0


def test_a_listing_cut_by_a_page_break_is_still_faithful(manual: Any) -> None:
    lines = FIXTURE_CODE.splitlines(keepends=True)
    manual(
        [
            FakePage(mono_spans("".join(lines[:4]))),
            FakePage(mono_spans("".join(lines[4:]))),
        ]
    )

    payload = gate.build()

    assert payload["summary"]["CODE_BLOCK_NOT_FAITHFUL"] == 0
    assert payload["variants"][0]["faithful"][0]["pages"] == [1, 2]


# ---------------------------------------------------------------------------
#  Le rendu muté échoue — c'est ce qui donne sa valeur au contrôle
# ---------------------------------------------------------------------------


def test_a_single_smartened_quote_makes_the_gate_fail(manual: Any) -> None:
    """La mutation exacte que la revue a trouvée dans le manuel livré."""

    mutated = FIXTURE_CODE.replace('"seuil strictement', "\u201dseuil strictement", 1)
    manual([FakePage(mono_spans(mutated))])

    payload = gate.build()

    assert payload["summary"]["CODE_BLOCK_NOT_FAITHFUL"] == 2
    assert payload["summary"]["SMART_QUOTE_IN_CODE_TOKEN"] == 2
    diagnosis = payload["variants"][0]["unfaithful"][0]["diagnosis"]
    assert '"seuil' in diagnosis["source_says"]
    assert "\u201dseuil" in diagnosis["page_says"]


def test_every_smartened_quote_shape_is_refused(manual: Any) -> None:
    for straight, curly in (('"', "\u201c"), ("'", "\u2018"), ("'", "\u2019")):
        manual([FakePage(mono_spans(FIXTURE_CODE.replace(straight, curly, 1)))])

        assert gate.build()["summary"]["CODE_BLOCK_NOT_FAITHFUL"] == 2, curly


def test_a_fused_programming_ligature_is_refused(manual: Any) -> None:
    """Ce qu'une liste noire de guillemets n'aurait jamais vu."""

    manual([FakePage(mono_spans(FIXTURE_CODE.replace("<=", "\u2264", 1)))])

    payload = gate.build()

    assert payload["summary"]["CODE_BLOCK_NOT_FAITHFUL"] == 2
    # Aucun guillemet n'est en cause : c'est la comparaison qui parle.
    assert payload["summary"]["SMART_QUOTE_IN_CODE_TOKEN"] == 0


def test_code_set_in_the_body_font_is_refused(manual: Any) -> None:
    """Les dix-sept programmes inclus par fichier étaient composés en serif."""

    manual([FakePage(body_spans(FIXTURE_CODE))])

    payload = gate.build()

    assert payload["summary"]["CODE_BLOCK_NOT_FAITHFUL"] == 2
    assert payload["variants"][0]["unfaithful"][0]["diagnosis"]["matched_prefix"] == 0


def test_a_dropped_backslash_inside_a_string_is_refused(manual: Any) -> None:
    """Une barre oblique perdue : c'est ainsi que `\\newpage` est devenu du texte."""

    assert "m\\u00b3" in FIXTURE_CODE
    manual([FakePage(mono_spans(FIXTURE_CODE.replace("m\\u00b3", "mu00b3", 1)))])

    assert gate.build()["summary"]["CODE_BLOCK_NOT_FAITHFUL"] == 2


def test_the_gate_returns_a_failure_code_when_the_render_is_muted(
    manual: Any, capsys: pytest.CaptureFixture[str]
) -> None:
    manual([FakePage(mono_spans(FIXTURE_CODE.replace('"', "\u201d", 1)))])

    assert gate.main(["--check"]) == 1
    assert "CODE_BLOCK_NOT_FAITHFUL=2" in capsys.readouterr().out


def test_the_gate_returns_success_on_a_faithful_render(
    manual: Any, capsys: pytest.CaptureFixture[str]
) -> None:
    manual([FakePage(mono_spans(FIXTURE_CODE))])

    assert gate.main(["--check"]) == 0
    assert "CODE_BLOCK_NOT_FAITHFUL=0" in capsys.readouterr().out


# ---------------------------------------------------------------------------
#  Ce que l'édition élève retient
# ---------------------------------------------------------------------------


def withhold_corrections(build: Path) -> None:
    """Ce que le maître de l'édition élève écrit vraiment pour vider un corrigé."""

    (build / "MANUEL_1SPE_eleve.tex").write_text(
        "\\RenewDocumentEnvironment{corrige}{m +b}{}{}\n"
        "\\input{chapitres/1SPE-TEST/cours/10_code}\n",
        encoding="utf-8",
    )


def test_a_correction_program_is_not_expected_in_the_student_edition(
    manual: Any, tmp_path: Path
) -> None:
    objects = tmp_path / "Mathematiques/manuel-maths/chapitres/1SPE-TEST/cours"
    (objects / "10_code.tex").write_text(
        "\\begin{corrige}{1SPE-TEST-CO-001}\n"
        "\\begin{python}\n" + FIXTURE_CODE + "\\end{python}\n"
        "\\end{corrige}\n",
        encoding="utf-8",
    )
    withhold_corrections(gate.BUILD)
    # La page ne montre rien : l'élève n'a pas le corrigé.
    manual([FakePage([])])

    payload = gate.build()
    eleve = next(row for row in payload["variants"] if row["variant"] == "eleve")

    assert eleve["emptied_environments"] == ["corrige"]
    assert len(eleve["withheld"]) == 1
    assert eleve["unfaithful"] == []
    assert payload["summary"]["WITHHELD_CODE_BLOCK_PRINTED"] == 0


def test_a_correction_leaking_into_the_student_edition_is_refused(
    manual: Any, tmp_path: Path
) -> None:
    """L'absence est le contrat ; la présence serait le défaut."""

    objects = tmp_path / "Mathematiques/manuel-maths/chapitres/1SPE-TEST/cours"
    (objects / "10_code.tex").write_text(
        "\\begin{corrige}{1SPE-TEST-CO-001}\n"
        "\\begin{python}\n" + FIXTURE_CODE + "\\end{python}\n"
        "\\end{corrige}\n",
        encoding="utf-8",
    )
    withhold_corrections(gate.BUILD)
    manual([FakePage(mono_spans(FIXTURE_CODE))])

    payload = gate.build()
    eleve = next(row for row in payload["variants"] if row["variant"] == "eleve")

    assert len(eleve["leaked"]) == 1
    assert payload["summary"]["WITHHELD_CODE_BLOCK_PRINTED"] == 1
    assert gate.main(["--check"]) == 1


# ---------------------------------------------------------------------------
#  Ce qui est composé dans la fonte du code sans être un programme
# ---------------------------------------------------------------------------


def annotation_spans(text: str) -> list[dict[str, Any]]:
    """Un identifiant d'objet en marge : fonte du code, taille d'annotation."""

    return [{"font": "JetBrainsMono-Regular", "size": 5.76, "text": text}]


def test_a_margin_annotation_inside_a_listing_does_not_break_it(
    manual: Any,
) -> None:
    """L'édition professeur pose l'identifiant de l'objet au milieu du programme."""

    lines = FIXTURE_CODE.splitlines(keepends=True)
    manual(
        [
            FakePage(
                mono_spans("".join(lines[:4]))
                + annotation_spans("1SPE-TEST-COURS-07-TC-")
                + mono_spans("".join(lines[4:]))
            )
        ]
    )

    assert gate.build()["summary"]["CODE_BLOCK_NOT_FAITHFUL"] == 0


def test_the_composition_size_is_read_from_the_class() -> None:
    """Aucun seuil inventé : la classe déclare à quelle taille elle compose."""

    assert gate.listing_font_size() == pytest.approx(8.5 * 0.89 * 0.98)


def test_a_class_that_does_not_declare_its_code_size_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    empty = tmp_path / "vide.cls"
    empty.write_text("\\ProvidesClass{vide}\n", encoding="utf-8")
    monkeypatch.setattr(gate, "CLASS", empty)
    gate.listing_font_size.cache_clear()

    with pytest.raises(gate.FidelityError, match="taille de composition"):
        gate.listing_font_size()

    gate.listing_font_size.cache_clear()


# ---------------------------------------------------------------------------
#  Les fragments de commande
# ---------------------------------------------------------------------------


def test_a_command_tail_printed_on_a_page_is_found(manual: Any) -> None:
    """Exactement le P0 : `\\newpage` amputé, visible en toutes lettres."""

    # « ewpage » : la queue que laisse un `\\newpage` prive de sa barre.
    manual([FakePage(mono_spans(FIXTURE_CODE) + body_spans("Avant-propos ewpage"))])

    payload = gate.build()
    fragments = payload["variants"][0]["visible_malformed_fragments"]

    assert [entry["fragment"] for entry in fragments] == ["ewpage"]
    assert fragments[0]["probably"] == ["newpage"]
    assert payload["summary"]["VISIBLE_MALFORMED_LATEX_FRAGMENT"] == 2


def test_a_command_tail_alone_on_a_source_line_is_found(
    manual: Any, tmp_path: Path
) -> None:
    objects = tmp_path / "Mathematiques/manuel-maths/chapitres/1SPE-TEST/cours"
    (objects / "20_avant_propos.tex").write_text(
        # La ligne du milieu porte « ewpage » seul, sans barre oblique : le
        # defaut exact trouve dans quatre objets transversaux du manuel.
        "Le mot de la fin.\n" + "ewpage" + "\n\\section{Suite}\n",
        encoding="utf-8",
    )
    gate.latex_sources.cache_clear()
    manual([FakePage(mono_spans(FIXTURE_CODE))])

    payload = gate.build()

    assert payload["summary"]["MALFORMED_FRAGMENT_IN_SOURCE"] == 1
    assert payload["source_fragments"][0]["fragment"] == "ewpage"


def test_a_tail_that_is_also_a_word_of_the_corpus_is_not_reported_from_a_page(
    manual: Any, tmp_path: Path
) -> None:
    """La limite du contrôle, écrite plutôt que sous-entendue.

    `angle` est la queue de `\\rangle` et un mot français. Sur une page, rien
    ne les distingue ; c'est le contrôle des sources qui couvre ce cas.
    """

    objects = tmp_path / "Mathematiques/manuel-maths/chapitres/1SPE-TEST/cours"
    (objects / "30_geometrie.tex").write_text(
        "\\rangle x \\rangle y \\rangle z et un angle droit.\n", encoding="utf-8"
    )
    gate.latex_sources.cache_clear()
    manual([FakePage(mono_spans(FIXTURE_CODE) + body_spans("un angle droit"))])

    payload = gate.build()

    assert payload["summary"]["VISIBLE_MALFORMED_LATEX_FRAGMENT"] == 0
    assert "surveillees dans les sources" in payload["the_vocabulary_is_read_not_listed"]


# ---------------------------------------------------------------------------
#  Ce que la classe déclare fait autorité
# ---------------------------------------------------------------------------


def test_the_declared_literate_substitutions_are_honoured() -> None:
    """Un tiret cadratin s'imprime en trois traits : la classe le déclare."""

    mapping = gate.literate_map()

    assert mapping["\u2014"] == "---"
    assert mapping["é"] == "é"
    assert gate.expected_rendering("a\u2014b", mapping) == "a---b"


def test_a_class_without_a_literate_table_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    empty = tmp_path / "vide.cls"
    empty.write_text("\\ProvidesClass{vide}\n", encoding="utf-8")
    monkeypatch.setattr(gate, "CLASS", empty)
    gate.literate_map.cache_clear()

    with pytest.raises(gate.FidelityError, match="literate"):
        gate.literate_map()

    gate.literate_map.cache_clear()


def test_an_unreadable_reference_is_counted_as_unknown(manual: Any) -> None:
    """Ce qu'on n'a pas pu lire n'est pas déclaré fidèle."""

    build = gate.BUILD
    for variant in gate.VARIANTS:
        (build / f"MANUEL_1SPE_{variant}.tex").write_text(
            "\\input{chapitres/1SPE-TEST/cours/10_code}\n"
            "\\input{chapitres/1SPE-TEST/cours/99_absent}\n",
            encoding="utf-8",
        )
    manual([FakePage(mono_spans(FIXTURE_CODE))])

    assert gate.build()["summary"]["UNKNOWN"] == 2


# ---------------------------------------------------------------------------
#  Le manuel livré
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def payload() -> dict[str, Any]:
    if not gate.JSON_TARGET.is_file():
        pytest.skip(f"artefact absent : {gate.JSON_TARGET}")
    return json.loads(gate.JSON_TARGET.read_text(encoding="utf-8"))


def test_the_delivered_manual_prints_what_its_sources_say(
    payload: dict[str, Any],
) -> None:
    summary = payload["summary"]
    for metric in gate.BLOCKING:
        assert summary[metric] == 0, (metric, summary[metric])
    # Chaque programme est soit retrouvé à l'identique, soit retenu comme la
    # variante le déclare. Aucun n'est simplement passé sous silence.
    assert (
        summary["CODE_BLOCK_FAITHFUL"] + summary["CODE_BLOCK_WITHHELD_AS_DECLARED"]
        == summary["CODE_BLOCKS"]
    )
    assert summary["CODE_BLOCK_FAITHFUL"] > 0


def test_every_published_program_was_really_compared(payload: dict[str, Any]) -> None:
    """Un compte de programmes fidèles ne vaut rien sans caractères comparés."""

    compared = 0
    for variant in payload["variants"]:
        assert variant["code_blocks"] > 0, variant["variant"]
        for entry in variant["faithful"]:
            # Un corrigé peut n'imprimer qu'une ligne (« return somme / n ») ;
            # ce qui compte est qu'aucune comparaison ne soit vide.
            assert entry["characters_compared"] > 5, entry["origin"]
            assert entry["pages"], entry["origin"]
            compared += entry["characters_compared"]
    assert compared > 5000, compared


def test_both_kinds_of_published_program_are_covered(payload: dict[str, Any]) -> None:
    """Les blocs écrits dans l'objet ET les fichiers inclus."""

    kinds = {
        entry["kind"]
        for variant in payload["variants"]
        for entry in variant["faithful"]
    }
    assert kinds == {"inline_python_environment", "included_python_file"}
