"""Assemblage des livrets autonomes 1SPE : methodes, evaluations, remediation.

Chaque livret agrege le contenu du meme sous-dossier a travers les 10
chapitres 1SPE (MISSION_PRIORITAIRE §8) en un document autonome, nomme
``MANUEL_1SPE_<livret>.pdf`` pour etre reconnu par le modele d'inventaire
comme un livrable de portee manuel (cf. DELIVERABLE_SPECS["1SPE"]["variants"]
dans inventory_collection.py).

Reutilise sans la modifier l'infrastructure de compilation/verification
durcie de assemble_manuel.py (verrou exclusif, repertoire de build prive,
ecriture atomique, verification des empreintes, preflight PDF) : ce script
n'ajoute aucune logique transactionnelle propre.
"""

from __future__ import annotations

import argparse
import secrets
import subprocess
import sys
from pathlib import Path
from typing import Any

import yaml

import assemble_manuel as _manuel
from pdf_integrity import verify_pdf

ROOT = _manuel.ROOT

LIVRETS: dict[str, dict[str, str]] = {
    "methodes": {"subdir": "methodes", "titre": "Livret des méthodes"},
    "evaluations": {"subdir": "evaluations", "titre": "Banque d'évaluations"},
    "remediation": {"subdir": "remediation", "titre": "Livret de remédiation"},
}


class LivretError(_manuel.AssemblyError):
    """Raised when a standalone livret cannot be assembled or compiled."""


def collect_livret_chapter_files(chap_dir: Path, subdir: str) -> list[Path]:
    return sorted((chap_dir / subdir).glob("*.tex"))


def render_livret_master(
    livret: str,
    run_id: str,
    *,
    git_root: Path,
    tracked_paths: frozenset[str],
) -> str:
    if livret not in LIVRETS:
        raise LivretError("livret inconnu")
    spec = LIVRETS[livret]
    parts: list[str] = ["\\tableofcontents", "\\newpage"]
    chapters_with_content = 0
    for chap in _manuel.CHAPITRES:
        chap_dir = ROOT / "chapitres" / chap
        if not chap_dir.exists():
            continue
        files = collect_livret_chapter_files(chap_dir, spec["subdir"])
        if not files:
            continue
        contrat = yaml.safe_load(
            (chap_dir / "contrat.yaml").read_text(encoding="utf-8")
        )
        titre = contrat["titre"]
        inputs = "\n".join(
            _manuel.wrap_object_input(
                f.relative_to(ROOT).as_posix(),
                _manuel.canonical_tracked_path(
                    f.relative_to(git_root).as_posix(),
                    git_root,
                    tracked_paths,
                ),
            )
            for f in files
        )
        parts.append(f"% ===== {chap} =====")
        parts.append(f"\\chapter*{{{titre}}}")
        parts.append(f"\\addcontentsline{{toc}}{{chapter}}{{{titre}}}")
        parts.append(inputs)
        chapters_with_content += 1
    if chapters_with_content == 0:
        raise LivretError(f"aucun contenu {spec['subdir']} trouvé pour {livret}")

    content = "\n".join(parts)
    master = f"""% Livret 1SPE — {spec['titre']}
% Assemblé par scripts/assemble_livrets.py
\\documentclass{{gabarits/nexus-manuel}}
\\nxVersionProfesseurtrue
\\matiere{{Mathématiques}}\\niveau{{Première spécialité}}
\\title{{{spec['titre']} --- Première spécialité}}
\\begin{{document}}
\\typeout{{NEXUS_BUILD_RUN:{run_id}}}
\\begin{{titlepage}}
\\centering
\\vspace*{{4cm}}
{{\\titrefont\\Huge {spec['titre']}\\par}}
\\vspace{{1cm}}
{{\\Large Première spécialité --- Mathématiques\\par}}
\\vspace{{2cm}}
{{\\large Nexus Réussite\\par}}
\\end{{titlepage}}
{content}
\\end{{document}}
"""
    return master


def _main_locked(
    livret: str,
    *,
    active_runner: Any,
    build: Path,
) -> int:
    tex_name = f"MANUEL_1SPE_{livret}"
    tex_path = build / f"{tex_name}.tex"
    pdf_path = build / f"{tex_name}.pdf"
    log_path = build / f"{tex_name}.log"
    fls_path = build / f"{tex_name}.fls"

    try:
        git_root = ROOT.parents[1].resolve(strict=True)
        _control, _reproducibility, environment = _manuel._load_reproducibility_control(
            git_root,
            runner=active_runner,
        )
        tracked_paths = _manuel.load_tracked_paths(
            git_root,
            runner=active_runner,
            environment=environment,
        )
        run_id = secrets.token_hex(16)
        master = render_livret_master(
            livret,
            run_id,
            git_root=git_root,
            tracked_paths=tracked_paths,
        )
    except (_manuel.AssemblyError, OSError, subprocess.SubprocessError, ValueError) as error:
        print(f"Assemblage refusé : {error}")
        return 1

    try:
        with _manuel._private_run_directory(build, tex_name, run_id) as run_directory:
            _manuel._atomic_write_text(tex_path, master)
            run_pdf_path = run_directory / pdf_path.name
            run_log_path = run_directory / log_path.name
            run_fls_path = run_directory / fls_path.name
            command = [
                "lualatex",
                "-interaction=nonstopmode",
                "-halt-on-error",
                "-recorder",
                f"-output-directory={run_directory}",
                str(tex_path),
            ]
            for pass_number in range(1, 4):
                try:
                    proc = _manuel._run_with_environment(
                        active_runner,
                        environment,
                        command,
                        capture_output=True,
                        text=True,
                        cwd=ROOT,
                        errors="replace",
                        check=False,
                    )
                except OSError as error:
                    raise LivretError("LuaLaTeX indisponible") from error
                if proc.returncode != 0:
                    output = getattr(proc, "stdout", "") or ""
                    detail = output[-3000:].strip()
                    message = f"LuaLaTeX en échec à la passe {pass_number}"
                    if detail:
                        message += f" : {detail}"
                    raise LivretError(message)

            candidate_fingerprints = _manuel._compiled_output_fingerprints(
                root=ROOT,
                tex_path=tex_path,
                log_path=run_log_path,
                fls_path=run_fls_path,
                pdf_path=run_pdf_path,
                run_id=run_id,
            )
            if verify_pdf(
                run_pdf_path,
                run_log_path,
                runner=active_runner,
                environment=environment,
            ):
                raise LivretError("préflight PDF en échec")
            page_count = _manuel._pdf_page_count(
                run_pdf_path,
                runner=active_runner,
                environment=environment,
            )
            _manuel._revalidate_fingerprints(candidate_fingerprints)

            for source, destination in (
                (run_log_path, log_path),
                (run_fls_path, fls_path),
                (run_pdf_path, pdf_path),
            ):
                _manuel._revalidate_fingerprints(candidate_fingerprints)
                _manuel._atomic_promote_file(source, destination)
            _manuel._revalidate_fingerprints(candidate_fingerprints)
    except (_manuel.AssemblyError, OSError, subprocess.SubprocessError, ValueError) as error:
        print(f"Build candidat refusé : {error}")
        return 1

    print(f"PDF : {pdf_path} ({page_count} pages)")
    return 0


def main(livret: str) -> int:
    active_runner = _manuel._active_runner(None)
    try:
        build = _manuel._secure_build_directory(ROOT)
        with _manuel._exclusive_build_lock(build, livret):
            return _main_locked(livret, active_runner=active_runner, build=build)
    except (_manuel.AssemblyError, OSError) as error:
        print(f"Build refusé : {error}")
        return 1


def build_argument_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    ap.add_argument("--livret", required=True, choices=sorted(LIVRETS))
    return ap


if __name__ == "__main__":
    args = build_argument_parser().parse_args()
    sys.exit(main(args.livret))
