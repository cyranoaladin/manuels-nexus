import hashlib
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import assemble  # noqa: E402


A4_REPRODUCIBLE_ENVIRONMENT = {
    "SOURCE_DATE_EPOCH": "1785962466",
    "FORCE_SOURCE_DATE": "1",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "LANG": "C.UTF-8",
    "PYTHONHASHSEED": "0",
}
TRAILER_ID_RE = re.compile(r"/ID\s*\[\s*<([0-9a-fA-F]+)>\s*<([0-9a-fA-F]+)>\s*\]")


def _write_path_reproducibility_fixture(seed: Path) -> None:
    scripts = seed / "scripts"
    scripts.mkdir(parents=True)
    for name in ("assemble.py", "common.py", "pdf_integrity.py", "pdf_reproducibility.py"):
        source = ROOT / "scripts" / name
        if source.is_file():
            shutil.copy2(source, scripts / name)

    (seed / ".gitignore").write_text(
        "build/\n__pycache__/\n*.pyc\n",
        encoding="utf-8",
    )
    gabarits = seed / "gabarits"
    common = gabarits / "common"
    common.mkdir(parents=True)
    (gabarits / "nexus-manuel.cls").write_text(
        r"""\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{nexus-manuel}[2026/08/21 Fixture Nexus wrapper]
\input{gabarits/common/nexus-manuel.cls}
""",
        encoding="utf-8",
    )
    (common / "nexus-manuel.cls").write_text(
        r"""\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{nexus-manuel-common}[2026/08/21 Fixture Nexus canonical class]
\LoadClass{article}
\input{gabarits/common/nexus-support.tex}
\newcommand{\ouverturechapitre}[4]{\section*{#1}#2\par#3\par#4}
\newcommand{\parcoursUn}{Parcours 1}
\newcommand{\parcoursDeux}{Parcours 2}
\newcommand{\parcoursTrois}{Parcours 3}
""",
        encoding="utf-8",
    )
    (common / "nexus-charte.sty").write_text(
        "\\NeedsTeXFormat{LaTeX2e}\n"
        "\\ProvidesPackage{nexus-charte}[2026/08/21 Fixture charte]\n"
        "\\input{gabarits/common/nexus-support.tex}\n",
        encoding="utf-8",
    )
    (common / "nexus-pont.sty").write_text(
        "\\NeedsTeXFormat{LaTeX2e}\n"
        "\\ProvidesPackage{nexus-pont}[2026/08/21 Fixture pont]\n",
        encoding="utf-8",
    )
    (common / "nexus-support.tex").write_text(
        "\\newcommand{\\nexusFixtureSupport}{support transitif suivi}\n",
        encoding="utf-8",
    )
    (gabarits / "chapitre_master.tex").write_text(
        r"""\documentclass{gabarits/nexus-manuel}
\def\nexuschapterid{%%CHAP%%}
\begin{document}
%%OPENING%%
%%CONTENT%%
\end{document}
""",
        encoding="utf-8",
    )
    for chapter_id, wording in (
        ("TCOMPL-TEST", "Même source, même variante, même environnement."),
        ("TCOMPL-AUTRE", "Un autre chapitre doit avoir une identité distincte."),
    ):
        chapter = seed / "chapitres" / chapter_id
        source = chapter / "cours" / "10_contenu.tex"
        source.parent.mkdir(parents=True)
        source.write_text(
            f"\\section{{Contenu identique}}{wording}\n",
            encoding="utf-8",
        )
        (chapter / "contrat.yaml").write_text(
            f"""titre: Chapitre de reproductibilité {chapter_id}
niveau: TCOMPL
capacites:
  - code: C1
    libelle_eleve: Vérifier un résultat déterministe
temps_estime_h:
  parcours1: 1
  parcours2: 1
  parcours3: 1
situation_accroche: Une même source doit produire les mêmes octets.
""",
            encoding="utf-8",
        )
    evidence = seed / "evidence"
    evidence.mkdir()
    (evidence / "old-output.pdf").write_bytes(b"tracked historical PDF bytes\n")
    subprocess.run(["git", "init", "-q"], cwd=seed, check=True)
    subprocess.run(["git", "add", "."], cwd=seed, check=True)
    subprocess.run(
        [
            "git",
            "-c",
            "user.name=Nexus Test",
            "-c",
            "user.email=nexus-test@example.invalid",
            "commit",
            "-qm",
            "fixture",
        ],
        cwd=seed,
        check=True,
    )


def _run_fixture_chapter(
    root: Path,
    *,
    chap: str = "TCOMPL-TEST",
    variant: str = "complet",
    extra_environment: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment.update(A4_REPRODUCIBLE_ENVIRONMENT)
    environment.update(extra_environment or {})
    return subprocess.run(
        [
            sys.executable,
            "scripts/assemble.py",
            "--chap",
            chap,
            "--variant",
            variant,
        ],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        timeout=120,
    )


def _compile_fixture_chapter(
    root: Path,
    *,
    chap: str = "TCOMPL-TEST",
    variant: str = "complet",
    extra_environment: dict[str, str] | None = None,
) -> Path:
    proc = _run_fixture_chapter(
        root,
        chap=chap,
        variant=variant,
        extra_environment=extra_environment,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    return root / "build" / chap / f"{chap}_{variant}.pdf"


def _compiled_observation(
    root: Path,
    *,
    chap: str = "TCOMPL-TEST",
    variant: str = "complet",
    extra_environment: dict[str, str] | None = None,
) -> tuple[bytes, tuple[str, str], int, bytes]:
    pdf = _compile_fixture_chapter(
        root,
        chap=chap,
        variant=variant,
        extra_environment=extra_environment,
    )
    return pdf.read_bytes(), _pdf_trailer_id(pdf), _pdf_pages(pdf), _pdf_text(pdf)


def _compile_shared_helper_master(
    root: Path,
    *,
    variant: str,
    semantic_body: str,
    run_marker: str,
    source_mtime: int,
) -> tuple[bytes, tuple[str, str], int, bytes]:
    root.mkdir(parents=True)
    identity = assemble.pdf_trailer_identity(
        manual="chapter:HELPER-FIXTURE",
        variant=variant,
        body=semantic_body,
        sources={
            "fixture/body.tex": hashlib.sha256(
                semantic_body.encode("utf-8")
            ).hexdigest()
        },
    )
    master = root / "master.tex"
    master.write_text(
        "\\documentclass{article}\n"
        f"\\pdfvariable trailerid{{[<{identity}> <{identity}>]}}\n"
        "\\begin{document}\n"
        f"\\typeout{{NEXUS_BUILD_RUN:{run_marker}}}\n"
        f"{semantic_body}\n"
        "\\end{document}\n",
        encoding="utf-8",
    )
    os.utime(master, (source_mtime, source_mtime))
    environment = os.environ.copy()
    environment.update(A4_REPRODUCIBLE_ENVIRONMENT)
    proc = subprocess.run(
        [
            "lualatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            f"-output-directory={root}",
            str(master),
        ],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert proc.returncode == 0, proc.stdout + proc.stderr
    pdf = root / "master.pdf"
    return pdf.read_bytes(), _pdf_trailer_id(pdf), _pdf_pages(pdf), _pdf_text(pdf)


def _pdf_pages(pdf: Path) -> int:
    output = subprocess.run(
        ["pdfinfo", str(pdf)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    match = re.search(r"^Pages:\s+(\d+)$", output, re.MULTILINE)
    assert match is not None
    return int(match.group(1))


def _pdf_text(pdf: Path) -> bytes:
    return subprocess.run(
        ["pdftotext", str(pdf), "-"],
        check=True,
        capture_output=True,
    ).stdout


def _pdf_trailer_id(pdf: Path) -> tuple[str, str]:
    output = subprocess.run(
        ["qpdf", "--show-object=trailer", str(pdf)],
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    match = TRAILER_ID_RE.search(output)
    assert match is not None
    return match.group(1).lower(), match.group(2).lower()


def test_chapter_toc_is_only_emitted_for_variants_with_entries(tmp_path):
    template = r"""\documentclass{article}
\begin{document}
\tableofcontents
\clearpage
%%CONTENT%%
\end{document}
"""
    expectations = {
        "complet": (r"\section{Cours}Contenu du cours.", True, 2),
        "parcours1": (r"\section{Cours}Contenu du parcours.", True, 2),
        "methodes": ("Contenu des méthodes.", False, 1),
        "remediation": ("Contenu de remédiation.", False, 1),
    }

    for variant, (content, expects_toc, expected_pages) in expectations.items():
        rendered = assemble._configure_chapter_toc(template, variant=variant)
        assert (r"\tableofcontents" in rendered) is expects_toc
        tex = tmp_path / f"{variant}.tex"
        tex.write_text(rendered.replace("%%CONTENT%%", content), encoding="utf-8")
        build = tmp_path / variant
        build.mkdir()
        for _ in range(2):
            result = subprocess.run(
                [
                    "lualatex",
                    "-interaction=nonstopmode",
                    "-halt-on-error",
                    f"-output-directory={build}",
                    str(tex),
                ],
                cwd=tmp_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            assert result.returncode == 0, result.stdout + result.stderr

        pdf = build / f"{variant}.pdf"
        text = _pdf_text(pdf)
        assert _pdf_pages(pdf) == expected_pages
        assert (b"Contents" in text) is expects_toc


def _neutralized_qdf(pdf: Path, output: Path) -> bytes:
    subprocess.run(
        ["qpdf", "--qdf", "--object-streams=disable", str(pdf), str(output)],
        check=True,
    )
    return re.sub(
        rb"/ID\s*\[\s*<[^>]+>\s*<[^>]+>\s*\]",
        b"/ID [ <NEUTRAL> <NEUTRAL> ]",
        output.read_bytes(),
    )


def test_assemble_uses_lualatex_for_the_nexus_v3_class(tmp_path, monkeypatch):
    calls = []

    def successful_runner(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(assemble.subprocess, "run", successful_runner)

    result = assemble._compile_lualatex(
        tmp_path / "chapter.tex",
        build=tmp_path / "build",
        cwd=tmp_path,
        environment={"PATH": "/usr/bin", "HOME": str(tmp_path)},
    )

    assert result.returncode == 0
    assert calls[0][0][0] == "lualatex"
    assert "-recorder" in calls[0][0]


def test_chapter_pdf_is_path_independent_across_absolute_git_roots(tmp_path):
    seed = tmp_path / "seed"
    seed.mkdir()
    _write_path_reproducibility_fixture(seed)
    root_a = tmp_path / "root-A"
    root_b = tmp_path / "root-B"
    subprocess.run(["git", "clone", "-q", "--no-local", str(seed), str(root_a)], check=True)
    subprocess.run(["git", "clone", "-q", "--no-local", str(seed), str(root_b)], check=True)

    pdf_a = _compile_fixture_chapter(root_a)
    pdf_b = _compile_fixture_chapter(root_b)
    pages_a = _pdf_pages(pdf_a)
    pages_b = _pdf_pages(pdf_b)
    text_a = _pdf_text(pdf_a)
    text_b = _pdf_text(pdf_b)
    trailer_a = _pdf_trailer_id(pdf_a)
    trailer_b = _pdf_trailer_id(pdf_b)
    qdf_a = _neutralized_qdf(pdf_a, tmp_path / "root-A.qdf")
    qdf_b = _neutralized_qdf(pdf_b, tmp_path / "root-B.qdf")
    bytes_a = pdf_a.read_bytes()
    bytes_b = pdf_b.read_bytes()

    assert pages_a == pages_b
    assert text_a == text_b
    assert qdf_a == qdf_b
    assert bytes_a == bytes_b, (
        "chapter PDF depends on the absolute Git root: "
        f"A sha256={hashlib.sha256(bytes_a).hexdigest()} trailer={trailer_a}; "
        f"B sha256={hashlib.sha256(bytes_b).hexdigest()} trailer={trailer_b}"
    )


def test_shared_helper_pdf_ignores_real_run_marker(tmp_path):
    first = _compile_shared_helper_master(
        tmp_path / "run-A",
        variant="eleve",
        semantic_body="Same rendered body.",
        run_marker="run-A",
        source_mtime=1_700_000_000,
    )
    second = _compile_shared_helper_master(
        tmp_path / "run-B",
        variant="eleve",
        semantic_body="Same rendered body.",
        run_marker="run-B",
        source_mtime=1_700_000_000,
    )

    assert first == second


def test_shared_helper_pdf_ignores_distinct_source_mtime_and_build_time(tmp_path):
    first = _compile_shared_helper_master(
        tmp_path / "clock-A",
        variant="eleve",
        semantic_body="Same rendered body.",
        run_marker="stable",
        source_mtime=1_600_000_000,
    )
    second = _compile_shared_helper_master(
        tmp_path / "clock-B",
        variant="eleve",
        semantic_body="Same rendered body.",
        run_marker="stable",
        source_mtime=1_700_000_000,
    )

    assert first == second


def test_shared_helper_pdf_ignores_distinct_real_launch_seconds(tmp_path):
    first_launch = int(time.time())
    first = _compile_shared_helper_master(
        tmp_path / "wall-clock-A",
        variant="eleve",
        semantic_body="Same rendered body.",
        run_marker="stable",
        source_mtime=1_700_000_000,
    )
    deadline = time.monotonic() + 1.1
    while int(time.time()) == first_launch and time.monotonic() < deadline:
        time.sleep(0.01)
    second_launch = int(time.time())
    second = _compile_shared_helper_master(
        tmp_path / "wall-clock-B",
        variant="eleve",
        semantic_body="Same rendered body.",
        run_marker="stable",
        source_mtime=1_700_000_000,
    )

    assert second_launch > first_launch
    assert first == second


def test_chapter_pdf_changes_for_relevant_source_and_restores_exactly(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _write_path_reproducibility_fixture(root)
    source = root / "chapitres" / "TCOMPL-TEST" / "cours" / "10_contenu.tex"
    original = source.read_bytes()

    before = _compiled_observation(root)
    source.write_bytes(original + b"% relevant mutation\n")
    during = _compiled_observation(root)
    source.write_bytes(original)
    after = _compiled_observation(root)

    assert during[0] != before[0]
    assert during[1] != before[1]
    assert after == before


def test_shared_helper_student_teacher_pdfs_are_deterministic_and_distinct(tmp_path):
    eleve_first = _compile_shared_helper_master(
        tmp_path / "eleve-A",
        variant="eleve",
        semantic_body="Student exercise only.",
        run_marker="student-A",
        source_mtime=1_700_000_000,
    )
    eleve_second = _compile_shared_helper_master(
        tmp_path / "eleve-B",
        variant="eleve",
        semantic_body="Student exercise only.",
        run_marker="student-B",
        source_mtime=1_700_000_000,
    )
    professeur_first = _compile_shared_helper_master(
        tmp_path / "professeur-A",
        variant="professeur",
        semantic_body="Student exercise and teacher correction.",
        run_marker="teacher-A",
        source_mtime=1_700_000_000,
    )
    professeur_second = _compile_shared_helper_master(
        tmp_path / "professeur-B",
        variant="professeur",
        semantic_body="Student exercise and teacher correction.",
        run_marker="teacher-B",
        source_mtime=1_700_000_000,
    )

    assert eleve_first == eleve_second
    assert professeur_first == professeur_second
    assert eleve_first[0] != professeur_first[0]
    assert eleve_first[1] != professeur_first[1]


def test_different_chapters_have_distinct_deterministic_pdfs(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _write_path_reproducibility_fixture(root)

    first = _compiled_observation(root, chap="TCOMPL-TEST")
    second = _compiled_observation(root, chap="TCOMPL-AUTRE")

    assert first[0] != second[0]
    assert first[1] != second[1]


def test_producer_schema_version_changes_pdf_identity(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _write_path_reproducibility_fixture(root)
    helper = root / "scripts" / "pdf_reproducibility.py"

    before = _compiled_observation(root)
    source = helper.read_text(encoding="utf-8")
    helper.write_text(
        source.replace("PDF_TRAILER_PRODUCER_SCHEMA_VERSION = 1", "PDF_TRAILER_PRODUCER_SCHEMA_VERSION = 2"),
        encoding="utf-8",
    )
    during = _compiled_observation(root)

    assert during[0] != before[0]
    assert during[1] != before[1]


def test_replacing_tracked_old_pdf_does_not_change_chapter_preimage(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _write_path_reproducibility_fixture(root)
    old_pdf = root / "evidence" / "old-output.pdf"

    before = _compiled_observation(root)
    old_pdf.write_bytes(b"replacement tracked PDF bytes\n")
    after = _compiled_observation(root)

    assert after == before


def test_chapter_pdf_is_identical_in_two_real_git_worktrees(tmp_path):
    seed = tmp_path / "seed"
    seed.mkdir()
    _write_path_reproducibility_fixture(seed)
    root_a = tmp_path / "worktree-A"
    root_b = tmp_path / "worktree-B"
    subprocess.run(["git", "worktree", "add", "-q", "--detach", str(root_a), "HEAD"], cwd=seed, check=True)
    subprocess.run(["git", "worktree", "add", "-q", "--detach", str(root_b), "HEAD"], cwd=seed, check=True)

    assert _compiled_observation(root_a) == _compiled_observation(root_b)


def test_every_source_dependency_class_changes_the_identity(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _write_path_reproducibility_fixture(root)
    before = _compiled_observation(root)
    dependencies = (
        root / "chapitres" / "TCOMPL-TEST" / "cours" / "10_contenu.tex",
        root / "chapitres" / "TCOMPL-TEST" / "contrat.yaml",
        root / "gabarits" / "chapitre_master.tex",
        root / "gabarits" / "nexus-manuel.cls",
        root / "gabarits" / "common" / "nexus-manuel.cls",
        root / "gabarits" / "common" / "nexus-charte.sty",
        root / "gabarits" / "common" / "nexus-pont.sty",
        root / "gabarits" / "common" / "nexus-support.tex",
    )

    for dependency in dependencies:
        original = dependency.read_bytes()
        comment = b"# dependency mutation\n" if dependency.suffix == ".yaml" else b"% dependency mutation\n"
        dependency.write_bytes(original + comment)
        mutated = _compiled_observation(root)
        dependency.write_bytes(original)
        restored = _compiled_observation(root)
        assert mutated[1] != before[1], dependency
        assert mutated[0] != before[0], dependency
        assert restored == before, dependency


def test_untracked_internal_input_is_rejected_fail_closed(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _write_path_reproducibility_fixture(root)
    untracked = root / "untracked-support.tex"
    untracked.write_text("support non suivi\n", encoding="utf-8")
    source = root / "chapitres" / "TCOMPL-TEST" / "cours" / "10_contenu.tex"
    source.write_text(source.read_text(encoding="utf-8") + "\\input{untracked-support.tex}\n", encoding="utf-8")

    proc = _run_fixture_chapter(root)

    assert proc.returncode != 0
    assert "non suivi" in proc.stdout + proc.stderr


def test_symlink_input_escaping_repository_is_rejected_fail_closed(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _write_path_reproducibility_fixture(root)
    outside = tmp_path / "outside.tex"
    outside.write_text("support extérieur\n", encoding="utf-8")
    symlink = root / "escaping-support.tex"
    symlink.symlink_to(outside)
    subprocess.run(["git", "add", "escaping-support.tex"], cwd=root, check=True)
    source = root / "chapitres" / "TCOMPL-TEST" / "cours" / "10_contenu.tex"
    source.write_text(source.read_text(encoding="utf-8") + "\\input{escaping-support.tex}\n", encoding="utf-8")

    proc = _run_fixture_chapter(root)

    assert proc.returncode != 0
    assert "symbolique" in proc.stdout + proc.stderr


def test_direct_external_input_outside_proved_toolchain_roots_is_rejected(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _write_path_reproducibility_fixture(root)
    outside = tmp_path / "outside.tex"
    outside.write_text("contenu extérieur qui changerait le PDF\n", encoding="utf-8")
    source = root / "chapitres" / "TCOMPL-TEST" / "cours" / "10_contenu.tex"
    source.write_text(
        source.read_text(encoding="utf-8") + f"\\input{{{outside}}}\n",
        encoding="utf-8",
    )

    proc = _run_fixture_chapter(root)

    assert proc.returncode != 0
    assert "externe non autorisée" in proc.stdout + proc.stderr


def test_texmf_override_cannot_turn_tmp_into_a_proved_toolchain_root(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _write_path_reproducibility_fixture(root)
    fake_sysconfig = tmp_path / "fake-texmf-sysconfig"
    fake_sysconfig.mkdir()
    outside = fake_sysconfig / "outside.tex"
    outside.write_text("contenu extérieur contrôlé par override\n", encoding="utf-8")
    source = root / "chapitres" / "TCOMPL-TEST" / "cours" / "10_contenu.tex"
    source.write_text(
        source.read_text(encoding="utf-8") + f"\\input{{{outside}}}\n",
        encoding="utf-8",
    )

    proc = _run_fixture_chapter(
        root,
        extra_environment={"TEXMFSYSCONFIG": str(fake_sysconfig)},
    )

    assert proc.returncode != 0
    assert "externe non autorisée" in proc.stdout + proc.stderr


def test_rogue_tex_under_build_is_not_misclassified_as_generated(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _write_path_reproducibility_fixture(root)
    rogue = root / "build" / "TCOMPL-TEST" / "rogue.tex"
    rogue.parent.mkdir(parents=True)
    rogue.write_text("contenu rogue sous build\n", encoding="utf-8")
    source = root / "chapitres" / "TCOMPL-TEST" / "cours" / "10_contenu.tex"
    source.write_text(
        source.read_text(encoding="utf-8")
        + "\\input{build/TCOMPL-TEST/rogue.tex}\n",
        encoding="utf-8",
    )

    proc = _run_fixture_chapter(root)

    assert proc.returncode != 0
    assert "non suivie" in proc.stdout + proc.stderr


def test_chapter_identifier_traversal_is_rejected_before_any_write(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _write_path_reproducibility_fixture(root)

    proc = _run_fixture_chapter(root, chap="../escape")

    assert proc.returncode != 0
    assert "identifiant de chapitre invalide" in proc.stdout + proc.stderr
    assert not (root / "escape").exists()


def test_symlink_build_target_outside_repository_is_rejected_without_write(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _write_path_reproducibility_fixture(root)
    outside = tmp_path / "outside-build-target"
    outside.mkdir()
    build = root / "build"
    build.mkdir()
    (build / "TCOMPL-TEST").symlink_to(outside, target_is_directory=True)

    proc = _run_fixture_chapter(root)

    assert proc.returncode != 0
    assert "symbolique" in proc.stdout + proc.stderr
    assert list(outside.iterdir()) == []


def test_symlink_build_root_outside_repository_is_rejected_without_write(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _write_path_reproducibility_fixture(root)
    outside = tmp_path / "outside-build-root"
    outside.mkdir()
    (root / "build").symlink_to(outside, target_is_directory=True)

    proc = _run_fixture_chapter(root)

    assert proc.returncode != 0
    assert "symbolique" in proc.stdout + proc.stderr
    assert list(outside.iterdir()) == []


def test_prior_canonical_artifacts_survive_post_discovery_failure(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _write_path_reproducibility_fixture(root)
    target = root / "build" / "TCOMPL-TEST"
    target.mkdir(parents=True)
    prior = {
        target / "TCOMPL-TEST_complet.tex": b"prior master\n",
        target / "TCOMPL-TEST_complet.log": b"prior log\n",
        target / "TCOMPL-TEST_complet.pdf": b"prior pdf\n",
    }
    for path, content in prior.items():
        path.write_bytes(content)
    untracked = root / "post-discovery-untracked.tex"
    untracked.write_text("force recorder rejection\n", encoding="utf-8")
    source = root / "chapitres" / "TCOMPL-TEST" / "cours" / "10_contenu.tex"
    source.write_text(
        source.read_text(encoding="utf-8")
        + "\\input{post-discovery-untracked.tex}\n",
        encoding="utf-8",
    )

    proc = _run_fixture_chapter(root)

    assert proc.returncode != 0
    assert "Traceback" not in proc.stderr
    for path, content in prior.items():
        assert path.read_bytes() == content
    assert list(target.glob(".*.staging-*")) == []


def test_private_staging_directories_are_distinct_and_not_symlinks(tmp_path):
    target = tmp_path / "target"
    target.mkdir()

    first = assemble._create_private_staging(target, stem="chapter_complet")
    second = assemble._create_private_staging(target, stem="chapter_complet")

    assert first != second
    assert first.parent == target
    assert second.parent == target
    assert first.is_dir() and not first.is_symlink()
    assert second.is_dir() and not second.is_symlink()


def test_atomic_publication_rolls_back_master_and_log_if_pdf_replace_fails(
    tmp_path, monkeypatch
):
    target = tmp_path / "target"
    target.mkdir()
    staging = assemble._create_private_staging(target, stem="chapter_complet")
    suffixes = ("tex", "log", "fls", "aux", "toc", "out", "pdf")
    old = {suffix: f"old-{suffix}".encode() for suffix in suffixes}
    new = {suffix: f"new-{suffix}".encode() for suffix in suffixes}
    for suffix in old:
        (target / f"chapter_complet.{suffix}").write_bytes(old[suffix])
        (staging / f"chapter_complet.{suffix}").write_bytes(new[suffix])
    real_replace = assemble.os.replace

    def failing_pdf_replace(source, destination):
        if Path(source) == staging / "chapter_complet.pdf":
            raise OSError("injected PDF publication failure")
        return real_replace(source, destination)

    monkeypatch.setattr(assemble.os, "replace", failing_pdf_replace)

    try:
        assemble._publish_staged_artifacts(
            staging=staging,
            target=target,
            stem="chapter_complet",
        )
    except OSError as error:
        assert "injected PDF publication failure" in str(error)
    else:  # pragma: no cover - assertion de contrat
        raise AssertionError("injected PDF replace failure was ignored")
    for suffix, content in old.items():
        assert (target / f"chapter_complet.{suffix}").read_bytes() == content


def test_backup_copy_failure_never_mutates_canonical_destinations(
    tmp_path, monkeypatch
):
    suffixes = ("tex", "log", "fls", "aux", "toc", "out", "pdf")
    old = {suffix: f"old-{suffix}".encode() for suffix in suffixes}
    real_copy2 = assemble.shutil.copy2
    for fail_at in (2, 3):
        target = tmp_path / f"target-{fail_at}"
        target.mkdir()
        staging = assemble._create_private_staging(
            target, stem="chapter_complet"
        )
        for suffix, content in old.items():
            (target / f"chapter_complet.{suffix}").write_bytes(content)
            (staging / f"chapter_complet.{suffix}").write_bytes(
                f"new-{suffix}".encode()
            )
        copies = 0

        def fail_backup_copy(source, destination, *args, **kwargs):
            nonlocal copies
            copies += 1
            if copies == fail_at:
                raise OSError(f"injected backup copy failure {fail_at}")
            return real_copy2(source, destination, *args, **kwargs)

        monkeypatch.setattr(assemble.shutil, "copy2", fail_backup_copy)

        try:
            assemble._publish_staged_artifacts(
                staging=staging,
                target=target,
                stem="chapter_complet",
            )
        except OSError as error:
            assert f"injected backup copy failure {fail_at}" in str(error)
        else:  # pragma: no cover - assertion de contrat
            raise AssertionError("partial backup failure was ignored")
        for suffix, content in old.items():
            assert (target / f"chapter_complet.{suffix}").read_bytes() == content
        assert staging.exists()
        assert list(target.glob(".chapter_complet.backup-*")) == []


def test_successful_publication_replaces_trace_outputs_and_removes_stale_optional(
    tmp_path,
):
    target = tmp_path / "target"
    target.mkdir()
    staging = assemble._create_private_staging(target, stem="chapter_complet")
    all_suffixes = ("tex", "log", "fls", "aux", "toc", "out", "pdf")
    current_suffixes = ("tex", "log", "fls", "aux", "toc", "pdf")
    for suffix in all_suffixes:
        (target / f"chapter_complet.{suffix}").write_bytes(
            f"old-{suffix}".encode()
        )
    for suffix in current_suffixes:
        (staging / f"chapter_complet.{suffix}").write_bytes(
            f"new-{suffix}".encode()
        )

    assemble._publish_staged_artifacts(
        staging=staging,
        target=target,
        stem="chapter_complet",
    )

    for suffix in current_suffixes:
        assert (target / f"chapter_complet.{suffix}").read_bytes() == (
            f"new-{suffix}".encode()
        )
    assert not (target / "chapter_complet.out").exists()
    assert not staging.exists()
    assert list(target.glob(".chapter_complet.backup-*")) == []


def test_backup_cleanup_failure_keeps_committed_publication_and_warns(
    tmp_path, monkeypatch, capsys
):
    target = tmp_path / "target"
    target.mkdir()
    staging = assemble._create_private_staging(target, stem="chapter_complet")
    suffixes = ("tex", "log", "fls", "aux", "toc", "out", "pdf")
    for suffix in suffixes:
        (target / f"chapter_complet.{suffix}").write_bytes(
            f"old-{suffix}".encode()
        )
        (staging / f"chapter_complet.{suffix}").write_bytes(
            f"new-{suffix}".encode()
        )
    real_rmtree = assemble.shutil.rmtree

    def fail_backup_cleanup(path, *args, **kwargs):
        candidate = Path(path)
        if ".backup-" in candidate.name:
            raise OSError("injected backup cleanup failure")
        return real_rmtree(path, *args, **kwargs)

    monkeypatch.setattr(assemble.shutil, "rmtree", fail_backup_cleanup)

    assemble._publish_staged_artifacts(
        staging=staging,
        target=target,
        stem="chapter_complet",
    )

    for suffix in suffixes:
        assert (target / f"chapter_complet.{suffix}").read_bytes() == (
            f"new-{suffix}".encode()
        )
    assert not staging.exists()
    residuals = list(target.glob(".chapter_complet.backup-*"))
    assert len(residuals) == 1
    assert capsys.readouterr().err.strip() == (
        "AVERTISSEMENT: publication canonique validée; "
        f"backup transactionnel conservé: {residuals[0]}: "
        "injected backup cleanup failure"
    )


def test_main_returns_success_when_only_committed_backup_cleanup_fails(
    tmp_path, monkeypatch, capsys
):
    root = tmp_path / "repo"
    root.mkdir()
    _write_path_reproducibility_fixture(root)
    real_rmtree = assemble.shutil.rmtree

    def fail_backup_cleanup(path, *args, **kwargs):
        candidate = Path(path)
        if ".backup-" in candidate.name:
            raise OSError("injected committed backup quarantine")
        return real_rmtree(path, *args, **kwargs)

    monkeypatch.setattr(assemble, "ROOT", root)
    monkeypatch.setattr(assemble.shutil, "rmtree", fail_backup_cleanup)

    assert assemble.main("TCOMPL-TEST", "complet") == 0

    target = root / "build" / "TCOMPL-TEST"
    residuals = list(target.glob(".TCOMPL-TEST_complet.backup-*"))
    assert len(residuals) == 1
    assert (target / "TCOMPL-TEST_complet.pdf").is_file()
    assert (target / "TCOMPL-TEST_complet.fls").is_file()
    captured = capsys.readouterr()
    assert captured.err.strip() == (
        "AVERTISSEMENT: publication canonique validée; "
        f"backup transactionnel conservé: {residuals[0]}: "
        "injected committed backup quarantine"
    )


def test_staging_cleanup_failure_rolls_back_every_canonical_artifact(
    tmp_path, monkeypatch
):
    target = tmp_path / "target"
    target.mkdir()
    staging = assemble._create_private_staging(target, stem="chapter_complet")
    suffixes = ("tex", "log", "fls", "aux", "toc", "out", "pdf")
    for suffix in suffixes:
        (target / f"chapter_complet.{suffix}").write_bytes(
            f"old-{suffix}".encode()
        )
        (staging / f"chapter_complet.{suffix}").write_bytes(
            f"new-{suffix}".encode()
        )
    real_rmtree = assemble.shutil.rmtree

    def failing_staging_cleanup(path, *args, **kwargs):
        if Path(path) == staging:
            raise OSError("injected staging cleanup failure")
        return real_rmtree(path, *args, **kwargs)

    monkeypatch.setattr(assemble.shutil, "rmtree", failing_staging_cleanup)

    try:
        assemble._publish_staged_artifacts(
            staging=staging,
            target=target,
            stem="chapter_complet",
        )
    except OSError as error:
        assert "injected staging cleanup failure" in str(error)
    else:  # pragma: no cover - assertion de contrat
        raise AssertionError("staging cleanup failure was ignored")
    for suffix in suffixes:
        assert (target / f"chapter_complet.{suffix}").read_bytes() == (
            f"old-{suffix}".encode()
        )


def test_main_reports_staging_cleanup_failure_without_traceback_and_rolls_back(
    tmp_path, monkeypatch, capsys
):
    root = tmp_path / "repo"
    root.mkdir()
    _write_path_reproducibility_fixture(root)
    target = root / "build" / "TCOMPL-TEST"
    target.mkdir(parents=True)
    suffixes = ("tex", "log", "fls", "aux", "toc", "out", "pdf")
    for suffix in suffixes:
        (target / f"TCOMPL-TEST_complet.{suffix}").write_bytes(
            f"old-{suffix}".encode()
        )
    real_rmtree = assemble.shutil.rmtree
    injected = False

    def one_shot_staging_failure(path, *args, **kwargs):
        nonlocal injected
        candidate = Path(path)
        if not injected and ".staging-" in candidate.name:
            injected = True
            raise OSError("injected transactional cleanup failure")
        return real_rmtree(path, *args, **kwargs)

    monkeypatch.setattr(assemble, "ROOT", root)
    monkeypatch.setattr(assemble.shutil, "rmtree", one_shot_staging_failure)

    assert assemble.main("TCOMPL-TEST", "complet") == 1
    captured = capsys.readouterr()
    assert "injected transactional cleanup failure" in captured.err
    assert "Traceback" not in captured.err
    for suffix in suffixes:
        assert (target / f"TCOMPL-TEST_complet.{suffix}").read_bytes() == (
            f"old-{suffix}".encode()
        )


def test_alternate_git_index_cannot_make_rogue_input_tracked(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _write_path_reproducibility_fixture(root)
    rogue = root / "rogue-from-alternate-index.tex"
    rogue.write_text("contenu accepté uniquement par un faux index\n", encoding="utf-8")
    alternate_index = tmp_path / "alternate-git-index"
    shutil.copy2(root / ".git" / "index", alternate_index)
    git_environment = os.environ.copy()
    git_environment["GIT_INDEX_FILE"] = str(alternate_index)
    subprocess.run(
        ["git", "add", "rogue-from-alternate-index.tex"],
        cwd=root,
        env=git_environment,
        check=True,
    )
    source = root / "chapitres" / "TCOMPL-TEST" / "cours" / "10_contenu.tex"
    source.write_text(
        source.read_text(encoding="utf-8")
        + "\\input{rogue-from-alternate-index.tex}\n",
        encoding="utf-8",
    )

    proc = _run_fixture_chapter(
        root,
        extra_environment={"GIT_INDEX_FILE": str(alternate_index)},
    )

    assert proc.returncode != 0
    assert "non suivie" in proc.stdout + proc.stderr


def test_fuzzy_named_charter_and_bridge_are_not_authorities(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _write_path_reproducibility_fixture(root)
    common = root / "gabarits" / "common"
    (common / "nexus-charte.sty").rename(common / "custom-charte.sty")
    (common / "nexus-pont.sty").rename(common / "custom-pont.sty")
    canonical_class = common / "nexus-manuel.cls"
    canonical_class.write_text(
        canonical_class.read_text(encoding="utf-8")
        .replace("gabarits/common/nexus-charte", "gabarits/common/custom-charte")
        .replace("gabarits/common/nexus-pont", "gabarits/common/custom-pont"),
        encoding="utf-8",
    )
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)

    proc = _run_fixture_chapter(root)

    assert proc.returncode != 0
    assert "autorité canonique exacte absente" in proc.stdout + proc.stderr


def test_missing_declared_support_is_rejected_fail_closed(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _write_path_reproducibility_fixture(root)
    (root / "gabarits" / "common" / "nexus-pont.sty").unlink()

    proc = _run_fixture_chapter(root)

    assert proc.returncode != 0


def test_non_historical_cli_variants_are_rejected_before_collection(monkeypatch):
    def forbidden_collect(*_args, **_kwargs):
        raise AssertionError("collect must not run for a rejected CLI variant")

    monkeypatch.setattr(assemble, "collect", forbidden_collect)

    assert assemble.main("IGNORED", "eleve") == 2
    assert assemble.main("IGNORED", "professeur") == 2


def test_cli_rejects_student_teacher_variants_without_creating_a_build(tmp_path):
    root = tmp_path / "repo"
    root.mkdir()
    _write_path_reproducibility_fixture(root)

    for variant in ("eleve", "professeur"):
        proc = subprocess.run(
            [
                sys.executable,
                "scripts/assemble.py",
                "--chap",
                "TCOMPL-TEST",
                "--variant",
                variant,
            ],
            cwd=root,
            capture_output=True,
            text=True,
        )
        assert proc.returncode == 2
        assert "invalid choice" in proc.stderr
        assert not (root / "build").exists()


def test_only_mandated_kpse_roots_can_be_external_toolchain_authorities():
    assert assemble.PROVED_TOOLCHAIN_VARIABLES == (
        "TEXMFDIST",
        "TEXMFVAR",
        "TEXMFSYSVAR",
        "TEXMFSYSCONFIG",
    )
    assert "TEXMFHOME" not in assemble.PROVED_TOOLCHAIN_VARIABLES
    assert "TEXMFLOCAL" not in assemble.PROVED_TOOLCHAIN_VARIABLES


def test_sealed_environment_removes_every_tex_font_and_lua_override():
    source = {
        "PATH": "/usr/bin",
        "HOME": "/tmp/cache-home",
        "SAFE_FLAG": "retained",
        "GIT_INDEX_FILE": "/tmp/alternate-index",
        "LD_PRELOAD": "/tmp/inject.so",
        "TEXMFSYSCONFIG": "/tmp/fake",
        "TEXMFHOME": "/tmp/home",
        "TEXINPUTS": "/tmp/tex",
        "LUAINPUTS": "/tmp/lua-inputs",
        "BIBINPUTS": "/tmp/bib",
        "OSFONTDIR": "/tmp/fonts",
        "FONTCONFIG_FILE": "/tmp/fonts.conf",
        "FONTCONFIG_PATH": "/tmp/fontconfig",
        "LUA_PATH": "/tmp/?.lua",
        "LUA_CPATH": "/tmp/?.so",
    }

    sealed = assemble.sealed_build_environment(source)

    assert sealed["PATH"] == source["PATH"]
    assert sealed["HOME"] == source["HOME"]
    for forbidden in set(source) - {"PATH", "HOME"}:
        assert forbidden not in sealed
    assert sealed == {
        "PATH": "/usr/bin",
        "HOME": "/tmp/cache-home",
        **A4_REPRODUCIBLE_ENVIRONMENT,
    }


def test_source_graph_collision_is_rejected():
    try:
        assemble.merge_source_graphs({"same.tex": "a"}, {"same.tex": "b"})
    except ValueError as error:
        assert "collision" in str(error)
    else:  # pragma: no cover - assertion de contrat
        raise AssertionError("a source graph collision must fail closed")


def test_discovery_final_graph_divergence_is_rejected():
    try:
        assemble.assert_source_graph_unchanged(
            {"source.tex": "before"},
            {"source.tex": "after"},
        )
    except ValueError as error:
        assert "changé" in str(error)
    else:  # pragma: no cover - assertion de contrat
        raise AssertionError("source graph drift must fail closed")


def test_unknown_fls_outputs_are_rejected(tmp_path):
    staging = tmp_path / "staging"
    staging.mkdir()
    writable = tmp_path / "texmf-var"
    writable.mkdir()
    repo_output = tmp_path / "repo-output.aux"
    external_output = tmp_path.parent / "unknown-output.tmp"

    for output in (repo_output, external_output):
        fls = staging / "chapter.fls"
        fls.write_text(f"OUTPUT {output}\n", encoding="utf-8")
        try:
            assemble._produced_paths(
                fls,
                cwd=tmp_path,
                staging=staging,
                git_root=tmp_path,
                writable_toolchain_roots=(writable,),
            )
        except ValueError as error:
            assert "OUTPUT .fls non autorisé" in str(error)
        else:  # pragma: no cover - assertion de contrat
            raise AssertionError(f"unknown recorder output accepted: {output}")


def test_staging_and_writable_toolchain_outputs_are_the_only_allowed_outputs(
    tmp_path,
):
    staging = tmp_path / "staging"
    staging.mkdir()
    writable = tmp_path / "texmf-var"
    writable.mkdir()
    staged_output = staging / "chapter.log"
    transient_output = writable / "m_t_x_t_e_s_t.tmp"
    fls = staging / "chapter.fls"
    fls.write_text(
        f"OUTPUT {staged_output}\nOUTPUT {transient_output}\n",
        encoding="utf-8",
    )

    assert assemble._produced_paths(
        fls,
        cwd=tmp_path,
        staging=staging,
        git_root=tmp_path / "repo",
        writable_toolchain_roots=(writable,),
    ) == frozenset({staged_output})


def test_declared_union_cannot_mask_runtime_object_disappearance(
    tmp_path, monkeypatch, capsys
):
    root = tmp_path / "repo"
    root.mkdir()
    _write_path_reproducibility_fixture(root)
    real_inject = assemble._inject_trailer_identity

    def removing_inject(master, identity):
        injected = real_inject(master, identity)
        return injected.replace(
            "\\input{chapitres/TCOMPL-TEST/cours/10_contenu.tex}",
            "% runtime object deliberately removed",
        )

    monkeypatch.setattr(assemble, "ROOT", root)
    monkeypatch.setattr(assemble, "_inject_trailer_identity", removing_inject)

    assert assemble.main("TCOMPL-TEST", "complet") == 1
    captured = capsys.readouterr()
    assert "graphe source changé" in captured.err
    assert "Traceback" not in captured.err


def test_real_source_mutation_between_discovery_and_final_is_rejected(
    tmp_path, monkeypatch, capsys
):
    root = tmp_path / "repo"
    root.mkdir()
    _write_path_reproducibility_fixture(root)
    source = root / "chapitres" / "TCOMPL-TEST" / "cours" / "10_contenu.tex"
    real_compile = assemble._compile_lualatex
    calls = 0

    def mutating_compile(tex_path, *, build, cwd, environment):
        nonlocal calls
        calls += 1
        if calls == 2:
            source.write_bytes(source.read_bytes() + b"% changed after discovery\n")
        return real_compile(
            tex_path,
            build=build,
            cwd=cwd,
            environment=environment,
        )

    monkeypatch.setattr(assemble, "ROOT", root)
    monkeypatch.setattr(assemble, "_compile_lualatex", mutating_compile)

    assert assemble.main("TCOMPL-TEST", "complet") == 1
    captured = capsys.readouterr()
    assert "graphe source changé" in captured.err
    assert "Traceback" not in captured.err
