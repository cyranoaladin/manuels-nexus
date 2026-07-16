"""Compile chaque objet LaTeX modifié dans une enveloppe temporaire."""

from __future__ import annotations

import argparse
import subprocess
import tempfile
from collections.abc import Callable, Sequence
from pathlib import Path
from types import SimpleNamespace


Run = Callable[..., SimpleNamespace]


def _wrapper(source: Path, project_root: Path) -> str:
    relative_source = source.resolve().relative_to(project_root.resolve()).as_posix()
    return "\n".join(
        (
            r"\documentclass{gabarits/nexus-manuel}",
            r"\begin{document}",
            rf"\input{{{relative_source}}}",
            r"\end{document}",
            "",
        )
    )


def compile_tex_files(
    files: Sequence[Path], project_root: Path, runner: Run = subprocess.run
) -> int:
    """Compile les fichiers fournis et retourne 1 au premier échec."""
    project_root = project_root.resolve()
    with tempfile.TemporaryDirectory(prefix="nexus-latex-") as tmp:
        output_dir = Path(tmp)
        for index, source in enumerate(files, start=1):
            source = source.resolve()
            wrapper = output_dir / f"check_{index:03d}.tex"
            wrapper.write_text(_wrapper(source, project_root), encoding="utf-8")
            command = [
                "lualatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                f"-output-directory={output_dir}",
                str(wrapper),
            ]
            result = runner(
                command,
                capture_output=True,
                text=True,
                cwd=project_root,
                errors="replace",
            )
            if result.returncode:
                print(f"Échec LaTeX : {source.relative_to(project_root)}")
                print((result.stdout + result.stderr)[-3000:])
                return 1
            print(f"LaTeX OK : {source.relative_to(project_root)}")
    return 0


def staged_tex_files(project_root: Path) -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR", "--", "chapitres/**/*.tex"],
        capture_output=True,
        text=True,
        cwd=project_root,
        check=True,
    )
    return [project_root / line for line in result.stdout.splitlines() if line]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--files", nargs="*", type=Path)
    args = parser.parse_args()
    project_root = Path(__file__).resolve().parents[1]
    files = args.files or staged_tex_files(project_root)
    if not files:
        print("Aucun objet LaTeX de chapitre indexé à vérifier.")
        return 0
    return compile_tex_files(files, project_root)


if __name__ == "__main__":
    raise SystemExit(main())
