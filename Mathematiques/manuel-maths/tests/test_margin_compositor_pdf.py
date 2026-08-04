from __future__ import annotations

import importlib.util
import json
import os
import re
import shutil
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import pytest


MANUAL_ROOT = Path(__file__).resolve().parents[1]
CLASS_PATH = MANUAL_ROOT / "gabarits" / "nexus-manuel.cls"
MAX_PASSES = 6
RUN_NONCE = "0123456789abcdef0123456789abcdef"
CAPTURE_RECORD = re.compile(r"NEXUS-MARGIN-CAPTURE:(nxm:[^:\s]+:[^:\s]+:\d{8})")
ANCHOR_RECORD = re.compile(r"NEXUS-MARGIN-ANCHOR:(nxm:[^:\s]+:[^:\s]+:\d{8})")
LINK_RECORD = re.compile(
    r"NEXUS-MARGIN-LINKS:(nxm:[^:\s]+:[^:\s]+:\d{8}):(\d+)"
)
MARKER_METADATA_RECORD = re.compile(
    r"NEXUS-MARGIN-MARKER-METADATA:(nxm:[^:\s]+:[^:\s]+:\d{8})"
)
EVALUATION_RECORD = re.compile(r"NEXUS-MARGIN-EVALUATIONS:(\d+)")
INTERNAL_ID_EVALUATION_RECORD = re.compile(
    r"NEXUS-MARGIN-INTERNAL-ID-EVALUATIONS:(\d+)"
)
REPORT_DECORATION_RECORD = re.compile(r"NEXUS-MARGIN-REPORT-DECORATION-SP:(\d+)")
BODY_SENTINEL_RECORD = re.compile(
    r"NEXUS-MARGIN-BODY-SENTINEL:([^:\s]+):(-?\d+):(-?\d+)"
)
VMODE_HLIST_RECORD = re.compile(r"NEXUS-MARGIN-VMODE-HLISTS:(\d+)")
VMODE_PREVDEPTH_BEFORE = re.compile(r"NEXUS-MARGIN-VMODE-PREVDEPTH-BEFORE:(-?\d+)")
VMODE_PREVDEPTH_AFTER = re.compile(r"NEXUS-MARGIN-VMODE-PREVDEPTH-AFTER:(-?\d+)")


def _load_margin_contract():
    module_path = MANUAL_ROOT / "scripts" / "margin_contract.py"
    spec = importlib.util.spec_from_file_location(
        "margin_contract_for_compositor_test", module_path
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _atomic_write_json(path: Path, document: dict[str, Any]) -> None:
    contract = _load_margin_contract()
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(contract.canonical_json_bytes(document))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _assert_nonempty_capture_inventory(layout: dict[str, Any]) -> None:
    assert layout["notes"], "zero annotation capturée doit faire échouer la fixture"


def _run_private_passes(
    source: Path,
    output_directory: Path,
    *,
    variant: str = "eleve",
    marker_metadata: bool = True,
) -> list[dict[str, Any]]:
    contract = _load_margin_contract()
    previous = output_directory / "margin-layout.previous.json"
    next_layout = output_directory / "margin-layout.next.json"
    stable_layout = output_directory / "margin-stable-layout.json"
    observed: list[dict[str, Any]] = []

    for pass_number in range(1, MAX_PASSES + 1):
        next_layout.unlink(missing_ok=True)
        environment = os.environ.copy()
        environment.update(
            {
                "NEXUS_MARGIN_RUN_NONCE": RUN_NONCE,
                "NEXUS_MARGIN_VARIANT": variant,
                "NEXUS_MARGIN_PASS_NUMBER": str(pass_number),
                "NEXUS_MARGIN_LAYOUT_PREVIOUS": str(previous),
                "NEXUS_MARGIN_LAYOUT_NEXT": str(next_layout),
                "NEXUS_MARGIN_MARKER_METADATA": "1" if marker_metadata else "0",
            }
        )
        result = subprocess.run(
            [
                "lualatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-output-directory={output_directory}",
                str(source),
            ],
            cwd=MANUAL_ROOT,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout[-8000:] + result.stderr
        assert next_layout.is_file(), "inventaire de capture margin-layout.next.json absent"

        layout = json.loads(next_layout.read_text(encoding="utf-8"))
        contract.validate_margin_layout(layout)
        _assert_nonempty_capture_inventory(layout)
        assert layout["run_nonce"] == RUN_NONCE
        assert layout["variant"] == variant
        assert layout["pass_number"] == pass_number

        capture_ids = CAPTURE_RECORD.findall(result.stdout)
        anchor_ids = ANCHOR_RECORD.findall(result.stdout)
        observed.append(
            {
                "layout": layout,
                "capture_ids": capture_ids,
                "anchor_ids": anchor_ids,
                "stdout": result.stdout,
            }
        )

        os.replace(next_layout, previous)
        if layout["state"] == "stable":
            stable = contract.materialize_stable_layout(layout)
            contract.validate_stable_layout(stable)
            _atomic_write_json(stable_layout, stable)
            break
        assert layout["state"] in {"collecting", "changed"}
    else:
        pytest.fail("placements marginaux non stabilisés après six passes privées")

    assert stable_layout.is_file()
    assert (output_directory / f"{source.stem}.pdf").is_file()
    return observed


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_identical_anchor_captures_three_notes_once_on_every_private_pass(
    tmp_path: Path,
) -> None:
    fixture = tmp_path / "identical-anchor.tex"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel}
\nxVersionProfesseurfalse
\begin{document}
\noindent Ancre commune\margeAppui{Premier appui}%
\margeAppui{Deuxième appui}%
\margeAppui{Troisième appui}. Fin de ligne.
\vfill
\newpage
Seconde page témoin.
\end{document}
""",
        encoding="utf-8",
    )

    passes = _run_private_passes(fixture, tmp_path)
    expected_ids = [
        "nxm:eleve:appui:00000001",
        "nxm:eleve:appui:00000002",
        "nxm:eleve:appui:00000003",
    ]

    assert len(passes) >= 2
    for observed in passes:
        layout = observed["layout"]
        notes = layout["notes"]
        assert len(layout["pages"]) == 2
        assert [note["id"] for note in notes] == expected_ids
        assert len({note["semantic_digest"] for note in notes}) == 3
        assert len({note["origin_y_sp"] for note in notes}) == 1
        assert Counter(observed["capture_ids"]) == Counter(
            {note_id: 1 for note_id in expected_ids}
        )
        assert Counter(observed["anchor_ids"]) == Counter(
            {note_id: 1 for note_id in expected_ids}
        )

    assert [[note["id"] for note in item["layout"]["notes"]] for item in passes] == [
        expected_ids
    ] * len(passes)


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_vertical_mode_anchor_adds_no_hlist_and_preserves_prevdepth(
    tmp_path: Path,
) -> None:
    fixture = tmp_path / "vertical-anchor.tex"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel}
\nxVersionProfesseurfalse
\newdimen\nxPrevdepthBefore
\newdimen\nxPrevdepthAfter
\begin{document}
\setbox0=\vbox{%
  \hbox{Ligne avec descendantes gjpq}%
  \global\nxPrevdepthBefore=\prevdepth
  \penalty12345
  \nxMarginRailNote{appui}{Appui vertical unique}%
  \penalty12346
  \global\nxPrevdepthAfter=\prevdepth
  \hbox{Ligne suivante}%
}%
\directlua{
  local between = false
  local hlists = 0
  for current in node.traverse(tex.box[0].list) do
    local kind = node.type(current.id)
    if kind == "penalty" and current.penalty == 12345 then
      between = true
    elseif kind == "penalty" and current.penalty == 12346 then
      between = false
    elseif between and kind == "hlist" then
      hlists = hlists + 1
    end
  end
  texio.write_nl("term and log", "NEXUS-MARGIN-VMODE-HLISTS:" .. hlists)
}
\typeout{NEXUS-MARGIN-VMODE-PREVDEPTH-BEFORE:\number\nxPrevdepthBefore}
\typeout{NEXUS-MARGIN-VMODE-PREVDEPTH-AFTER:\number\nxPrevdepthAfter}
\box0
\newpage
Seconde page témoin.
\end{document}
""",
        encoding="utf-8",
    )

    passes = _run_private_passes(fixture, tmp_path)
    expected_id = "nxm:eleve:appui:00000001"

    for observed in passes:
        stdout = observed["stdout"]
        assert VMODE_HLIST_RECORD.findall(stdout) == ["0"]
        before = VMODE_PREVDEPTH_BEFORE.findall(stdout)
        after = VMODE_PREVDEPTH_AFTER.findall(stdout)
        assert len(before) == len(after) == 1
        assert int(before[0]) > 0
        assert before == after
        assert [note["id"] for note in observed["layout"]["notes"]] == [expected_id]
        assert observed["capture_ids"] == [expected_id]
        assert observed["anchor_ids"] == [expected_id]


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_blank_line_paragraph_break_inside_note_content_compiles(
    tmp_path: Path,
) -> None:
    fixture = tmp_path / "multi-paragraph-note.tex"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel}
\nxVersionProfesseurfalse
\begin{document}
Ancre\nxMarginRailNote{appui}{%
Premier paragraphe de la note.

Second paragraphe de la note, apr\`es une ligne vide.}%
\end{document}
""",
        encoding="utf-8",
    )

    passes = _run_private_passes(fixture, tmp_path)
    expected_id = "nxm:eleve:appui:00000001"

    for observed in passes:
        assert [note["id"] for note in observed["layout"]["notes"]] == [expected_id]
        assert observed["capture_ids"] == [expected_id]
        assert observed["anchor_ids"] == [expected_id]


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_breakable_fichemethode_captures_local_rich_note_once_in_all_modes(
    tmp_path: Path,
) -> None:
    fixture = tmp_path / "breakable-fichemethode.tex"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel}
\nxVersionProfesseurfalse
\usepackage{hyperref}
\newcounter{nxMarginFixtureEvaluations}
\newcount\nxFixtureRow
\newcommand{\nxBodySentinel}[1]{%
  \savepos
  \latelua{local x, y = pdf.getpos(); texio.write_nl("term and log",
    "NEXUS-MARGIN-BODY-SENTINEL:#1:" .. math.floor(x + 0.5) .. ":" ..
    math.floor(y + 0.5))}%
}
\begin{document}
\noindent Début du flux\nxBodySentinel{before}.
\nxMarginRailNote{appui}{Appui capturé en mode vertical.}
\noindent Ancre horizontale\nxMarginRailNote{commentaire}{Note horizontale.}
\begin{fichemethode}{T6}{Encadré cassable réel}
  \newcommand{\nxLocalRichPayload}{Macro locale $x^2+1$,
    \textcolor{coulRetenir}{couleur contrôlée} et
    \href{https://example.invalid/nexus-t8}{lien contrôlé}.}
  \nxFixtureRow=0
  \loop
    \par Ligne de méthode \the\nxFixtureRow\ : un contenu assez long force la
    coupure réelle de l'encadré sans saut de page manuel.
    \advance\nxFixtureRow by 1
  \ifnum\nxFixtureRow<38
  \repeat
  \commentaireMarge{\stepcounter{nxMarginFixtureEvaluations}\nxLocalRichPayload}
  \nxFixtureRow=0
  \loop
    \par Suite de méthode \the\nxFixtureRow\ : le contenu continue après la
    note capturée et maintient l'encadré sur sa seconde page.
    \advance\nxFixtureRow by 1
  \ifnum\nxFixtureRow<12
  \repeat
\end{fichemethode}
\noindent Fin du flux\nxBodySentinel{after}.
\typeout{NEXUS-MARGIN-EVALUATIONS:\arabic{nxMarginFixtureEvaluations}}
\end{document}
""",
        encoding="utf-8",
    )

    metadata_on_directory = tmp_path / "metadata-on"
    metadata_off_directory = tmp_path / "metadata-off"
    metadata_on_directory.mkdir()
    metadata_off_directory.mkdir()
    passes = _run_private_passes(
        fixture, metadata_on_directory, marker_metadata=True
    )
    passes_without_metadata = _run_private_passes(
        fixture, metadata_off_directory, marker_metadata=False
    )
    expected_ids = [
        "nxm:eleve:appui:00000001",
        "nxm:eleve:commentaire:00000002",
        "nxm:eleve:commentaire:00000003",
    ]

    assert len(passes) >= 2
    for observed in passes:
        layout = observed["layout"]
        assert len(layout["pages"]) == 2
        assert [note["id"] for note in layout["notes"]] == expected_ids
        assert observed["capture_ids"] == expected_ids
        assert observed["anchor_ids"] == expected_ids
        assert EVALUATION_RECORD.findall(observed["stdout"]) == ["1"]
        assert dict(LINK_RECORD.findall(observed["stdout"])) == {
            expected_ids[-1]: "1"
        }
        decoration_records = REPORT_DECORATION_RECORD.findall(observed["stdout"])
        assert len(decoration_records) == 1
        decoration_height_sp = int(decoration_records[0])
        assert decoration_height_sp > 0
        assert {
            note["report_decoration_height_sp"] for note in layout["notes"]
        } == {decoration_height_sp}
        assert MARKER_METADATA_RECORD.findall(observed["stdout"]) == expected_ids

    for observed in passes_without_metadata:
        assert [note["id"] for note in observed["layout"]["notes"]] == expected_ids
        assert observed["capture_ids"] == expected_ids
        assert observed["anchor_ids"] == expected_ids
        assert MARKER_METADATA_RECORD.findall(observed["stdout"]) == []

    assert len(passes[-1]["layout"]["pages"]) == len(
        passes_without_metadata[-1]["layout"]["pages"]
    )
    sentinels_with_metadata = BODY_SENTINEL_RECORD.findall(passes[-1]["stdout"])
    sentinels_without_metadata = BODY_SENTINEL_RECORD.findall(
        passes_without_metadata[-1]["stdout"]
    )
    assert [sentinel[0] for sentinel in sentinels_with_metadata] == [
        "before",
        "after",
    ]
    assert sentinels_with_metadata == sentinels_without_metadata


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_blank_page_and_reset_folio_keep_absolute_shipout_rail_parity(
    tmp_path: Path,
) -> None:
    fixture = tmp_path / "absolute-shipout-parity.tex"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel}
\nxVersionProfesseurfalse
\begin{document}
Première page\margeAppui{Note physique 1, folio logique 1.}
\newpage
\thispagestyle{empty}\null
\newpage
\setcounter{page}{1}
Troisième page physique\margeAppui{Note physique 3, folio logique réinitialisé à 1.}
\end{document}
""",
        encoding="utf-8",
    )

    passes = _run_private_passes(fixture, tmp_path)

    for observed in passes:
        pages = observed["layout"]["pages"]
        assert [page["shipout_index"] for page in pages] == [1, 2, 3]
        assert [page["folio"] for page in pages] == ["1", "2", "1"]
        assert [page["rail_side"] for page in pages] == ["right", "left", "right"]
        for page in pages:
            safe = page["safe_rect"]
            assert 0 < safe["left_sp"] < safe["right_sp"] < page["page_width_sp"]
            assert 0 < safe["top_sp"] < safe["bottom_sp"] < page["page_height_sp"]

        notes = observed["layout"]["notes"]
        assert [note["origin_shipout_index"] for note in notes] == [1, 3]
        assert [note["origin_folio"] for note in notes] == ["1", "1"]


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_declared_middle_reserve_rectangle_moves_note_below_obstacle(
    tmp_path: Path,
) -> None:
    fixture = tmp_path / "reserved-middle-obstacle.tex"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel}
\nxVersionProfesseurfalse
\providecommand{\nxMarginReserveRect}[5]{}
\begin{document}
\nxMarginReserveRect{fixture-middle}{%
  \dimexpr1in+\hoffset+\oddsidemargin+\textwidth+\marginparsep\relax}{5cm}{%
  \dimexpr1in+\hoffset+\oddsidemargin+\textwidth+\marginparsep+\marginparwidth\relax}{15cm}
\vspace*{7cm}
Obstacle médian\margeAppui{Cette note doit contourner le rectangle réservé.}
\newpage
Page de report disponible.
\end{document}
""",
        encoding="utf-8",
    )

    passes = _run_private_passes(fixture, tmp_path)

    for observed in passes:
        layout = observed["layout"]
        page = layout["pages"][0]
        assert len(page["obstacles"]) == 1
        obstacle = page["obstacles"][0]
        assert obstacle["id"] == "fixture-middle-p00000001"
        assert page["safe_rect"]["left_sp"] <= obstacle["left_sp"]
        assert obstacle["right_sp"] <= page["safe_rect"]["right_sp"]
        assert page["safe_rect"]["top_sp"] < obstacle["top_sp"]
        assert obstacle["bottom_sp"] < page["safe_rect"]["bottom_sp"]

        note = layout["notes"][0]
        assert note["origin_y_sp"] < obstacle["bottom_sp"]
        assert note["target_shipout_index"] == 1
        assert note["target_y_sp"] == obstacle["bottom_sp"] + 6 * 65536


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_oversized_unbreakable_horizontal_note_fails_with_exact_error(
    tmp_path: Path,
) -> None:
    fixture = tmp_path / "oversized-unbreakable.tex"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel}
\nxVersionProfesseurfalse
\begin{document}
Texte\nxMarginRailNote{appui}{\hbox{\rule{2\marginparwidth}{1pt}}}.
\end{document}
""",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment["NEXUS_MARGIN_VARIANT"] = "eleve"

    result = subprocess.run(
        [
            "lualatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={tmp_path}",
            str(fixture),
        ],
        cwd=MANUAL_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    output = result.stdout + result.stderr
    assert result.returncode != 0
    assert "NEXUS-MARGIN-ERROR:width:nxm:eleve:appui:00000001" in output


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_unbreakable_word_effective_extent_fails_with_exact_width_error(
    tmp_path: Path,
) -> None:
    fixture = tmp_path / "unbreakable-word.tex"
    unbreakable_word = "NEXUS" + "W" * 160
    fixture.write_text(
        rf"""\documentclass{{gabarits/nexus-manuel}}
\nxVersionProfesseurfalse
\begin{{document}}
Texte\nxMarginRailNote{{appui}}{{\texttt{{{unbreakable_word}}}}}.
\end{{document}}
""",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment["NEXUS_MARGIN_VARIANT"] = "eleve"

    result = subprocess.run(
        [
            "lualatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={tmp_path}",
            str(fixture),
        ],
        cwd=MANUAL_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    output = result.stdout + result.stderr
    assert "Overfull \\hbox" in output
    assert result.returncode != 0
    assert "NEXUS-MARGIN-ERROR:width:nxm:eleve:appui:00000001" in output


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_repeated_obstacle_base_id_is_qualified_by_absolute_shipout(
    tmp_path: Path,
) -> None:
    fixture = tmp_path / "repeated-page-obstacle.tex"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel}
\nxVersionProfesseurfalse
\begin{document}
\nxMarginReserveRect{header}{%
  \dimexpr1in+\hoffset+\oddsidemargin+\textwidth+\marginparsep\relax}{0pt}{%
  \dimexpr1in+\hoffset+\oddsidemargin+\textwidth+\marginparsep+\marginparwidth\relax}{1cm}
Recto\margeAppui{Note recto.}
\newpage
\nxMarginReserveRect{header}{%
  \dimexpr1in+\hoffset+\evensidemargin-\marginparsep-\marginparwidth\relax}{0pt}{%
  \dimexpr1in+\hoffset+\evensidemargin-\marginparsep\relax}{1cm}
Verso\margeAppui{Note verso.}
\end{document}
""",
        encoding="utf-8",
    )

    passes = _run_private_passes(fixture, tmp_path)

    for observed in passes:
        pages = observed["layout"]["pages"]
        assert [page["shipout_index"] for page in pages] == [1, 2]
        assert [[item["id"] for item in page["obstacles"]] for page in pages] == [
            ["header-p00000001"],
            ["header-p00000002"],
        ]


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_duplicate_obstacle_base_id_on_same_shipout_stays_fail_closed(
    tmp_path: Path,
) -> None:
    fixture = tmp_path / "duplicate-page-obstacle.tex"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel}
\nxVersionProfesseurfalse
\begin{document}
\nxMarginReserveRect{header}{1cm}{1cm}{2cm}{2cm}
\nxMarginReserveRect{header}{2cm}{2cm}{3cm}{3cm}
Texte\margeAppui{Note témoin.}
\end{document}
""",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment.update(
        {
            "NEXUS_MARGIN_VARIANT": "eleve",
            "NEXUS_MARGIN_RUN_NONCE": RUN_NONCE,
            "NEXUS_MARGIN_PASS_NUMBER": "1",
            "NEXUS_MARGIN_LAYOUT_NEXT": str(tmp_path / "margin-layout.next.json"),
        }
    )

    result = subprocess.run(
        [
            "lualatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={tmp_path}",
            str(fixture),
        ],
        cwd=MANUAL_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    output = result.stdout + result.stderr
    assert result.returncode != 0
    assert "NEXUS-MARGIN-ERROR:placement:header-p00000001" in output


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_oversized_vertical_note_fails_with_exact_height_error(
    tmp_path: Path,
) -> None:
    fixture = tmp_path / "oversized-vertical.tex"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel}
\nxVersionProfesseurfalse
\begin{document}
Texte\nxMarginRailNote{appui}{\vbox to 2\textheight{\hbox{Hauteur}\vfil}}.
\end{document}
""",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment["NEXUS_MARGIN_VARIANT"] = "eleve"

    result = subprocess.run(
        [
            "lualatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={tmp_path}",
            str(fixture),
        ],
        cwd=MANUAL_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    output = result.stdout + result.stderr
    assert result.returncode != 0
    assert "NEXUS-MARGIN-ERROR:height:nxm:eleve:appui:00000001" in output


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_unplaceable_note_fails_with_exact_placement_error(tmp_path: Path) -> None:
    fixture = tmp_path / "unplaceable-note.tex"
    next_layout = tmp_path / "margin-layout.next.json"
    fixture.write_text(
        r"""\documentclass{gabarits/nexus-manuel}
\nxVersionProfesseurfalse
\begin{document}
\nxMarginReserveRect{fixture-full-rail}{%
  \dimexpr1in+\hoffset+\oddsidemargin+\textwidth+\marginparsep\relax}{%
  \dimexpr1in+\voffset+\topmargin+\headheight+\headsep\relax}{%
  \dimexpr1in+\hoffset+\oddsidemargin+\textwidth+\marginparsep+\marginparwidth\relax}{%
  \dimexpr1in+\voffset+\topmargin+\headheight+\headsep+\textheight\relax}
Texte\nxMarginRailNote{appui}{Note sans placement possible.}.
\end{document}
""",
        encoding="utf-8",
    )
    environment = os.environ.copy()
    environment.update(
        {
            "NEXUS_MARGIN_VARIANT": "eleve",
            "NEXUS_MARGIN_RUN_NONCE": RUN_NONCE,
            "NEXUS_MARGIN_PASS_NUMBER": "1",
            "NEXUS_MARGIN_LAYOUT_NEXT": str(next_layout),
        }
    )

    result = subprocess.run(
        [
            "lualatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={tmp_path}",
            str(fixture),
        ],
        cwd=MANUAL_ROOT,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    output = result.stdout + result.stderr
    assert result.returncode != 0
    assert "NEXUS-MARGIN-ERROR:placement:nxm:eleve:appui:00000001" in output


@pytest.mark.skipif(shutil.which("lualatex") is None, reason="lualatex absent")
def test_variant_exercise_metadata_filters_internal_id_before_student_capture(
    tmp_path: Path,
) -> None:
    def build_variant(variant: str) -> list[dict[str, Any]]:
        is_professor = variant == "professeur"
        output_directory = tmp_path / variant
        output_directory.mkdir()
        fixture = output_directory / f"exercise-metadata-{variant}.tex"
        fixture.write_text(
            rf"""\documentclass{{gabarits/nexus-manuel}}
\nxVersionProfesseur{'true' if is_professor else 'false'}
\providecommand{{\icnChrono}}{{Chrono}}
\newcounter{{nxMarginInternalIdEvaluations}}
\newcommand{{\nxFixtureInternalId}}{{\stepcounter{{nxMarginInternalIdEvaluations}}1SPE-T6-INTERNAL}}
\begin{{document}}
\begin{{exercice}}{{\nxFixtureInternalId}}{{1}}{{7}}
Un exercice témoin pour la variante {variant}.
\end{{exercice}}
\typeout{{NEXUS-MARGIN-INTERNAL-ID-EVALUATIONS:\arabic{{nxMarginInternalIdEvaluations}}}}
\end{{document}}
""",
            encoding="utf-8",
        )
        return _run_private_passes(fixture, output_directory, variant=variant)

    student_passes = build_variant("eleve")
    professor_passes = build_variant("professeur")

    for observed in student_passes:
        notes = observed["layout"]["notes"]
        assert [note["role"] for note in notes] == ["chrono"]
        assert [note["id"] for note in notes] == ["nxm:eleve:chrono:00000001"]
        assert INTERNAL_ID_EVALUATION_RECORD.findall(observed["stdout"]) == ["0"]
        assert all(note["report_decoration_height_sp"] > 0 for note in notes)

    for observed in professor_passes:
        notes = observed["layout"]["notes"]
        assert [note["role"] for note in notes] == ["chrono", "professor-id"]
        assert [note["id"] for note in notes] == [
            "nxm:professeur:chrono:00000001",
            "nxm:professeur:professor-id:00000002",
        ]
        assert INTERNAL_ID_EVALUATION_RECORD.findall(observed["stdout"]) == ["1"]
        assert all(note["report_decoration_height_sp"] > 0 for note in notes)

    student_chrono_digest = student_passes[-1]["layout"]["notes"][0][
        "semantic_digest"
    ]
    professor_chrono_digest = professor_passes[-1]["layout"]["notes"][0][
        "semantic_digest"
    ]
    assert student_chrono_digest == professor_chrono_digest


def test_capture_inventory_oracle_rejects_zero_notes() -> None:
    with pytest.raises(AssertionError, match="zero annotation capturée"):
        _assert_nonempty_capture_inventory({"notes": []})


def test_public_margin_components_use_only_the_shared_rail_adapter() -> None:
    source = CLASS_PATH.read_text(encoding="utf-8")

    assert r"\nxMarginRailNote{appui}" in source
    assert r"\nxMarginRailNote{commentaire}" in source
    assert r"\nxMarginRailNote{vocab}" in source
    assert r"\nxMarginRailNote{chrono}" in source
    assert r"\nxMarginRailNote{professor-id}" in source
    assert r"\marginnote{" not in source
    assert "nexus-margin-rail.tex" in source
