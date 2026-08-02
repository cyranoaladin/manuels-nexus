"""Assemblage du manuel complet 1SPE : transversal + 10 chapitres.

Variantes :
  --variant professeur  (tout : cours, exercices, corriges, evaluations, baremes)
  --variant eleve       (sans corriges ni baremes d'evaluation)
"""
import argparse
import hashlib
import json
import os
import re
import secrets
import stat
import subprocess
import sys
import tempfile
from collections.abc import Callable, Mapping
from pathlib import Path
from types import FunctionType
from typing import Any

import yaml

from common import ROOT
from pdf_integrity import verify_pdf

CHAPITRES = [
    "1SPE-SUITES",
    "1SPE-SECOND-DEGRE",
    "1SPE-DERIVATION-LOCAL",
    "1SPE-DERIVATION-GLOBAL",
    "1SPE-EXPONENTIELLE",
    "1SPE-TRIGONOMETRIE",
    "1SPE-PRODUIT-SCALAIRE",
    "1SPE-GEOMETRIE-REPEREE",
    "1SPE-PROBA-COND",
    "1SPE-VARIABLES-ALEATOIRES",
]

ORDER = [
    ("cours", "00_ouverture"), ("cours", "01_diagnostic"), ("cours", "02_activites"),
    ("cours", "1*"), ("methodes", "*"), ("exercices", "*"),
    ("cours", "07_td*"), ("qcm", "*"), ("evaluations", "*"), ("remediation", "*"),
]

ELEVE_EXCLUDES = {"corriges", "evaluations"}

REPRODUCIBILITY_CONFIG = Path(
    "Mathematiques/manuel-maths/config/reproducible-build.json"
)
REPRODUCIBILITY_FIELDS = {
    "schema_version",
    "source_commit",
    "source_date_epoch",
}
CONTROLLED_ENVIRONMENT = {
    "FORCE_SOURCE_DATE": "1",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "PYTHONHASHSEED": "0",
}


class AssemblyError(RuntimeError):
    """Failure that prevents a compiled PDF from becoming observed evidence."""


def _active_runner(runner: Callable[..., Any] | None) -> Callable[..., Any]:
    return subprocess.run if runner is None else runner


def _run_with_environment(
    runner: Callable[..., Any],
    environment: Mapping[str, str],
    command: list[str],
    **kwargs: Any,
) -> Any:
    return runner(command, env=dict(environment), **kwargs)


def _load_reproducibility_control(
    git_root: Path,
    *,
    runner: Callable[..., Any],
) -> tuple[dict[str, object], dict[str, object], dict[str, str]]:
    config_path = git_root / REPRODUCIBILITY_CONFIG
    try:
        payload = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AssemblyError("contrôle de reproductibilité indisponible") from error
    if not isinstance(payload, dict) or set(payload) != REPRODUCIBILITY_FIELDS:
        raise AssemblyError("contrôle de reproductibilité non fermé")

    schema_version = payload.get("schema_version")
    source_commit = payload.get("source_commit")
    source_date_epoch = payload.get("source_date_epoch")
    if type(schema_version) is not int or schema_version != 1:
        raise AssemblyError("schema_version de reproductibilité invalide")
    if (
        not isinstance(source_commit, str)
        or re.fullmatch(r"[0-9a-f]{40}", source_commit) is None
    ):
        raise AssemblyError("source_commit de reproductibilité invalide")
    if type(source_date_epoch) is not int or source_date_epoch <= 0:
        raise AssemblyError("source_date_epoch de reproductibilité invalide")

    environment = os.environ.copy()
    environment.update(CONTROLLED_ENVIRONMENT)
    environment["SOURCE_DATE_EPOCH"] = str(source_date_epoch)

    common_options = {
        "capture_output": True,
        "text": True,
        "errors": "replace",
        "check": False,
    }
    try:
        commit = _run_with_environment(
            runner,
            environment,
            [
                "git",
                "-C",
                str(git_root),
                "cat-file",
                "-e",
                f"{source_commit}^{{commit}}",
            ],
            **common_options,
        )
        ancestor = _run_with_environment(
            runner,
            environment,
            [
                "git",
                "-C",
                str(git_root),
                "merge-base",
                "--is-ancestor",
                source_commit,
                "HEAD",
            ],
            **common_options,
        )
        timestamp = _run_with_environment(
            runner,
            environment,
            [
                "git",
                "-C",
                str(git_root),
                "show",
                "-s",
                "--format=%ct",
                source_commit,
            ],
            **common_options,
        )
    except OSError as error:
        raise AssemblyError("validation Git du contrôle indisponible") from error
    if commit.returncode != 0:
        raise AssemblyError("source_commit absent du dépôt")
    if ancestor.returncode != 0:
        raise AssemblyError("source_commit non ancêtre de HEAD")
    if timestamp.returncode != 0:
        raise AssemblyError("timestamp Git du source_commit indisponible")
    try:
        git_timestamp = int(timestamp.stdout.strip())
    except (AttributeError, ValueError) as error:
        raise AssemblyError("timestamp Git du source_commit invalide") from error
    if git_timestamp != source_date_epoch:
        raise AssemblyError("source_date_epoch différent du timestamp Git")

    reproducibility = {
        "config_path": REPRODUCIBILITY_CONFIG.as_posix(),
        "source_commit": source_commit,
        "source_date_epoch": source_date_epoch,
        "force_source_date": "1",
        "timezone": "UTC",
        "locale": "C.UTF-8",
        "pythonhashseed": "0",
    }
    return payload, reproducibility, environment


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
    return "sha256:" + digest.hexdigest()


def _atomic_write_json(destination: Path, payload: Mapping[str, object]) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    descriptor, raw_temporary = tempfile.mkstemp(
        dir=destination.parent,
        prefix=f".{destination.name}.",
        suffix=".tmp",
    )
    temporary = Path(raw_temporary)
    try:
        stream = os.fdopen(
            descriptor,
            "w",
            encoding="utf-8",
            newline="\n",
        )
        descriptor = -1
        with stream:
            json.dump(
                payload,
                stream,
                ensure_ascii=False,
                indent=2,
                sort_keys=True,
            )
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(destination)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        temporary.unlink(missing_ok=True)


def _git_relative_path(path: Path, git_root: Path, *, exists: bool) -> str:
    root = git_root.resolve(strict=True)
    if exists:
        candidate = path.resolve(strict=True)
    else:
        candidate = path.parent.resolve(strict=True) / path.name
    try:
        relative = candidate.relative_to(root)
    except ValueError as error:
        raise AssemblyError("preuve hors du dépôt Git") from error
    if any(part in {"", ".", ".."} for part in relative.parts):
        raise AssemblyError("chemin de preuve non canonique")
    return relative.as_posix()


class _ControlledSubprocessProxy:
    def __init__(
        self,
        runner: Callable[..., Any],
        environment: Mapping[str, str],
    ) -> None:
        self._runner = runner
        self._environment = environment

    def run(self, command: list[str], **kwargs: Any) -> Any:
        kwargs.pop("env", None)
        completed = _run_with_environment(
            self._runner,
            self._environment,
            command,
            **kwargs,
        )
        if kwargs.get("check") and completed.returncode != 0:
            raise subprocess.CalledProcessError(
                completed.returncode,
                command,
                output=getattr(completed, "stdout", None),
                stderr=getattr(completed, "stderr", None),
            )
        return completed


def _verify_pdf_with_environment(
    pdf_path: Path,
    log_path: Path,
    *,
    runner: Callable[..., Any],
    environment: Mapping[str, str],
) -> int:
    callback = verify_pdf
    if isinstance(callback, FunctionType) and callback.__module__ == "pdf_integrity":
        controlled_globals = dict(callback.__globals__)
        controlled_globals["subprocess"] = _ControlledSubprocessProxy(
            runner,
            environment,
        )
        callback = FunctionType(
            callback.__code__,
            controlled_globals,
            callback.__name__,
            callback.__defaults__,
            callback.__closure__,
        )
        callback.__kwdefaults__ = verify_pdf.__kwdefaults__
    return callback(pdf_path, log_path)


def resolve_git_root(
    start: Path,
    *,
    runner: Callable[..., Any] | None = None,
    environment: Mapping[str, str] | None = None,
) -> Path:
    active_runner = _active_runner(runner)
    options: dict[str, Any] = {
        "check": True,
        "capture_output": True,
        "text": True,
    }
    if environment is not None:
        options["env"] = dict(environment)
    completed = active_runner(
        ["git", "-C", str(start), "rev-parse", "--show-toplevel"],
        **options,
    )
    return Path(completed.stdout.strip()).resolve(strict=True)


def load_tracked_paths(
    git_root: Path,
    *,
    runner: Callable[..., Any] | None = None,
    environment: Mapping[str, str] | None = None,
) -> frozenset[str]:
    active_runner = _active_runner(runner)
    options: dict[str, Any] = {
        "check": True,
        "capture_output": True,
        "encoding": "utf-8",
    }
    if environment is not None:
        options["env"] = dict(environment)
    completed = active_runner(
        ["git", "-C", str(git_root), "ls-files", "-z"],
        **options,
    )
    return frozenset(path for path in completed.stdout.split("\0") if path)


def canonical_tracked_path(
    raw_path: str | Path,
    git_root: Path,
    tracked_paths: frozenset[str] | None = None,
) -> str:
    raw = os.fspath(raw_path)
    candidate_path = Path(raw)
    if (
        not raw
        or raw != raw.strip()
        or candidate_path.is_absolute()
        or "\\" in raw
        or any(part in {"", ".", ".."} for part in raw.split("/"))
    ):
        raise ValueError("chemin suivi non canonique")

    root = git_root.resolve(strict=True)
    candidate = root
    for part in raw.split("/"):
        candidate /= part
        try:
            mode = candidate.lstat().st_mode
        except FileNotFoundError as error:
            raise ValueError("chemin suivi absent") from error
        if stat.S_ISLNK(mode):
            raise ValueError("chemin symbolique interdit")
    if not stat.S_ISREG(candidate.stat().st_mode):
        raise ValueError("chemin suivi non régulier")

    if tracked_paths is None:
        tracked_paths = load_tracked_paths(root)
    if raw not in tracked_paths:
        raise ValueError("chemin non suivi par Git")
    return raw


def object_trace_token(canonical_path: str) -> str:
    return hashlib.sha256(canonical_path.encode("utf-8")).hexdigest()[:40]


def wrap_object_input(input_path: str, canonical_path: str) -> str:
    token = object_trace_token(canonical_path)
    return "\n".join(
        [
            f"\\typeout{{NEXUS_OBJECT_BEGIN:{token}}}",
            f"\\input{{{input_path}}}",
            f"\\typeout{{NEXUS_OBJECT_END:{token}}}",
        ]
    )


def collect_chapter(chap_dir: Path, variant: str) -> list[Path]:
    files = []
    for sub, pat in ORDER:
        if variant == "eleve" and sub in ELEVE_EXCLUDES:
            continue
        candidats = sorted((chap_dir / sub).glob(f"{pat}.tex" if not pat.endswith("*") else pat + ".tex"))
        if sub == "exercices":
            files += [f for f in candidats if not f.name.endswith("-CDP.tex")]
            files += [f for f in candidats if f.name.endswith("-CDP.tex")]
        elif sub == "evaluations" and variant == "eleve":
            files += [f for f in candidats if "corrige" not in f.name]
        else:
            files += candidats
    seen, out = set(), []
    for f in files:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def ouverture_depuis_contrat(chap_dir: Path) -> str:
    contrat = yaml.safe_load((chap_dir / "contrat.yaml").read_text(encoding="utf-8"))
    capacites = "\n".join(
        f"\\item \\textbf{{{c['code']}}} --- {c['libelle_eleve']}"
        for c in contrat["capacites"]
    )
    temps = contrat.get("temps_estime_h", {})
    temps_tex = (
        f"\\parcoursUn~{temps.get('parcours1', '---')} h \\quad "
        f"\\parcoursDeux~{temps.get('parcours2', '---')} h \\quad "
        f"\\parcoursTrois~{temps.get('parcours3', '---')} h"
    )
    accroche = contrat.get("situation_accroche", "")
    return (
        f"\\ouverturechapitre{{{contrat['titre']}}}{{\\begin{{itemize}}\n{capacites}\n\\end{{itemize}}}}"
        f"{{{accroche}}}{{{temps_tex}}}\n\\clearpage"
    )


def render_master(
    variant: str,
    run_id: str,
    *,
    git_root: Path | None = None,
    tracked_paths: frozenset[str] | None = None,
) -> str:
    if variant not in {"eleve", "professeur"}:
        raise ValueError("variante inconnue")
    if re.fullmatch(r"[0-9a-f]{32}", run_id) is None:
        raise ValueError("identifiant de build invalide")
    if git_root is None:
        git_root = resolve_git_root(ROOT)
    if tracked_paths is None:
        tracked_paths = load_tracked_paths(git_root)
    parts = []

    # Transversal front matter
    parts.append("\\input{transversal/page_de_garde}")
    parts.append("\\newpage")
    parts.append("\\input{transversal/avant_propos}")
    parts.append("\\newpage")
    parts.append("\\input{transversal/mode_emploi}")
    parts.append("\\newpage")
    parts.append("\\tableofcontents")
    parts.append("\\newpage")
    parts.append("\\input{transversal/index_capacites}")
    parts.append("\\newpage")

    # Chapters
    for chap in CHAPITRES:
        chap_dir = ROOT / "chapitres" / chap
        if not chap_dir.exists():
            print(f"SKIP {chap} (directory not found)")
            continue

        opening = ouverture_depuis_contrat(chap_dir)
        files = collect_chapter(chap_dir, variant)
        inputs = "\n".join(
            wrap_object_input(
                f.relative_to(ROOT).as_posix(),
                canonical_tracked_path(
                    f.relative_to(git_root).as_posix(),
                    git_root,
                    tracked_paths,
                ),
            )
            for f in files
        )
        parts.append(f"% ===== {chap} =====")
        parts.append(opening)
        parts.append(inputs)

    # Back matter
    parts.append("\\appendix")
    parts.append("\\clearpage")
    parts.append("\\input{transversal/formulaire}")
    parts.append("\\clearpage")
    parts.append("\\input{transversal/memo_python}")

    content = "\n".join(parts)

    titre_var = "professeur" if variant == "professeur" else "eleve"
    master = f"""% Manuel 1SPE — variante {titre_var}
% Assemble par scripts/assemble_manuel.py
\\documentclass{{gabarits/nexus-manuel}}
\\matiere{{Mathématiques}}\\niveau{{Première spécialité}}
\\title{{Manuel de mathématiques — Première spécialité — Édition {titre_var}}}
\\begin{{document}}
\\typeout{{NEXUS_BUILD_RUN:{run_id}}}
{content}
\\end{{document}}
"""
    return master


def _pdf_page_count(
    pdf_path: Path,
    *,
    runner: Callable[..., Any],
    environment: Mapping[str, str],
) -> int:
    try:
        completed = _run_with_environment(
            runner,
            environment,
            ["pdfinfo", str(pdf_path)],
            capture_output=True,
            text=True,
            errors="replace",
            check=False,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise AssemblyError("pdfinfo indisponible") from error
    if completed.returncode != 0:
        raise AssemblyError("pdfinfo en échec")
    match = re.search(r"^Pages:\s*([0-9]+)\s*$", completed.stdout, re.MULTILINE)
    if match is None or int(match.group(1)) <= 0:
        raise AssemblyError("pagination PDF invalide")
    return int(match.group(1))


def _first_version_line(completed: Any, tool: str) -> str:
    if completed.returncode != 0:
        raise AssemblyError(f"collecte de version {tool} en échec")
    output = "\n".join(
        value
        for value in (
            getattr(completed, "stdout", ""),
            getattr(completed, "stderr", ""),
        )
        if isinstance(value, str) and value
    )
    for line in output.splitlines():
        normalized = " ".join(line.split())
        if normalized:
            return normalized
    raise AssemblyError(f"version {tool} absente")


def _collect_tool_versions(
    *,
    runner: Callable[..., Any],
    environment: Mapping[str, str],
) -> dict[str, str]:
    commands = {
        "lualatex": ["lualatex", "--version"],
        "pdfinfo": ["pdfinfo", "-v"],
        "pdffonts": ["pdffonts", "-v"],
        "python": [sys.executable, "--version"],
    }
    versions: dict[str, str] = {}
    for tool, command in commands.items():
        try:
            completed = _run_with_environment(
                runner,
                environment,
                command,
                capture_output=True,
                text=True,
                errors="replace",
                check=False,
                timeout=20,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise AssemblyError(f"collecte de version {tool} indisponible") from error
        versions[tool] = _first_version_line(completed, tool)
    return versions


def _publish_observed_evidence(
    *,
    variant: str,
    run_id: str,
    git_root: Path,
    tex_path: Path,
    pdf_path: Path,
    log_path: Path,
    fls_path: Path,
    report_path: Path,
    receipt_path: Path,
    page_count: int,
    tool_versions: Mapping[str, str],
    reproducibility: Mapping[str, object],
) -> None:
    canonical = {
        "master": _git_relative_path(tex_path, git_root, exists=True),
        "pdf": _git_relative_path(pdf_path, git_root, exists=True),
        "log": _git_relative_path(log_path, git_root, exists=True),
        "fls": _git_relative_path(fls_path, git_root, exists=True),
        "preflight": _git_relative_path(report_path, git_root, exists=False),
    }
    preflight_pdf_digest = _sha256_path(pdf_path)
    report = {
        "run_id": run_id,
        "pdf_path": canonical["pdf"],
        "pdf_sha256": preflight_pdf_digest,
        "page_count": page_count,
        "passed": True,
        "checks": {
            "verify_pdf": {"passed": True},
            "pdfinfo": {"passed": True},
            "pdffonts": {"passed": True},
        },
        "tool_versions": dict(tool_versions),
        "reproducibility": dict(reproducibility),
    }
    _atomic_write_json(report_path, report)

    evidence_sha256 = {
        "master": _sha256_path(tex_path),
        "log": _sha256_path(log_path),
        "fls": _sha256_path(fls_path),
        "preflight": _sha256_path(report_path),
        "pdf": _sha256_path(pdf_path),
    }
    if evidence_sha256["pdf"] != preflight_pdf_digest:
        raise AssemblyError("PDF modifié après le préflight")
    receipt = {
        "compile_succeeded": True,
        "fls_path": canonical["fls"],
        "gates": {
            "compile": {"passed": True},
            "preflight": {"passed": True},
        },
        "generated_dependencies": [],
        "log_path": canonical["log"],
        "manual": "1SPE",
        "pdf_path": canonical["pdf"],
        "preflight_report": canonical["preflight"],
        "preflight_succeeded": True,
        "tool_versions": dict(tool_versions),
        "variant": variant,
        "run_id": run_id,
        "master_path": canonical["master"],
        "evidence_sha256": evidence_sha256,
        "reproducibility": dict(reproducibility),
    }
    _atomic_write_json(receipt_path, receipt)


def main(
    variant: str,
    record_observed: bool = False,
    *,
    runner: Callable[..., Any] | None = None,
) -> int:
    build = ROOT / "build" / "MANUEL_1SPE"
    build.mkdir(parents=True, exist_ok=True)

    tex_name = f"MANUEL_1SPE_{variant}"
    tex_path = build / f"{tex_name}.tex"
    pdf_path = build / f"{tex_name}.pdf"
    log_path = build / f"{tex_name}.log"
    fls_path = build / f"{tex_name}.fls"
    report_path = build / f"{tex_name}.preflight.json"
    receipt_path = build / f"{tex_name}.receipt.json"

    if record_observed:
        try:
            receipt_path.unlink(missing_ok=True)
            report_path.unlink(missing_ok=True)
        except OSError as error:
            print(f"Impossible d'invalider les preuves périmées : {error}")
            return 1

    active_runner = _active_runner(runner)
    try:
        git_root = ROOT.parents[1].resolve(strict=True)
        _control, reproducibility, environment = _load_reproducibility_control(
            git_root,
            runner=active_runner,
        )
        tracked_paths = load_tracked_paths(
            git_root,
            runner=active_runner,
            environment=environment,
        )
        run_id = secrets.token_hex(16)
        master = render_master(
            variant,
            run_id,
            git_root=git_root,
            tracked_paths=tracked_paths,
        )
        tex_path.write_text(master, encoding="utf-8")
    except (AssemblyError, OSError, subprocess.SubprocessError, ValueError) as error:
        print(f"Assemblage refusé : {error}")
        return 1

    command = [
        "lualatex",
        "-interaction=nonstopmode",
        "-halt-on-error",
        "-recorder",
        f"-output-directory={build}",
        str(tex_path),
    ]
    for _pass_number in range(1, 4):
        try:
            proc = _run_with_environment(
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
            print(f"LuaLaTeX indisponible : {error}")
            return 1
        if proc.returncode != 0:
            output = getattr(proc, "stdout", "") or ""
            print(output[-3000:])
            return 1

    try:
        if _verify_pdf_with_environment(
            pdf_path,
            log_path,
            runner=active_runner,
            environment=environment,
        ):
            return 1
        page_count = _pdf_page_count(
            pdf_path,
            runner=active_runner,
            environment=environment,
        )
        tool_versions = _collect_tool_versions(
            runner=active_runner,
            environment=environment,
        )
    except (AssemblyError, OSError, subprocess.SubprocessError, ValueError) as error:
        print(f"Préflight refusé : {error}")
        return 1

    if not record_observed:
        print(f"PDF : {pdf_path}")
        return 0

    try:
        _publish_observed_evidence(
            variant=variant,
            run_id=run_id,
            git_root=git_root,
            tex_path=tex_path,
            pdf_path=pdf_path,
            log_path=log_path,
            fls_path=fls_path,
            report_path=report_path,
            receipt_path=receipt_path,
            page_count=page_count,
            tool_versions=tool_versions,
            reproducibility=reproducibility,
        )
    except (AssemblyError, OSError, ValueError) as error:
        receipt_path.unlink(missing_ok=True)
        print(f"Publication des preuves refusée : {error}")
        return 1

    recorder_command = [
        sys.executable,
        str(git_root / "scripts/build_manifest.py"),
        "--receipt",
        str(receipt_path),
    ]
    try:
        recorder = _run_with_environment(
            active_runner,
            environment,
            recorder_command,
            capture_output=True,
            text=True,
            errors="replace",
            check=False,
            cwd=git_root,
        )
    except OSError as error:
        receipt_path.unlink(missing_ok=True)
        print(f"Enregistrement observé indisponible : {error}")
        return 1
    if recorder.returncode != 0:
        receipt_path.unlink(missing_ok=True)
        output = getattr(recorder, "stderr", "") or getattr(
            recorder,
            "stdout",
            "",
        )
        if output:
            print(output[-3000:])
        return int(recorder.returncode)

    print(f"PDF : {pdf_path}")
    return 0


def build_argument_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--variant",
        default="professeur",
        choices=["professeur", "eleve"],
    )
    ap.add_argument("--record-observed", action="store_true")
    return ap


if __name__ == "__main__":
    args = build_argument_parser().parse_args()
    sys.exit(main(args.variant, record_observed=args.record_observed))
