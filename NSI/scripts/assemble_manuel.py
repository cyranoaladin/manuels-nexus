"""Assemble les variantes canoniques des manuels NSI (1NSI et TNSI).

Le livre courant est selectionne par `select_book`. Par defaut 1NSI, afin que
tout appel existant conserve son comportement. Le manifeste
`manifests/books/<BOOK_ID>.json` fait foi pour la liste et l'ordre des
chapitres : c'est la meme chaine pour les deux niveaux, pas une architecture
paralelle.
"""

from __future__ import annotations

import argparse
from collections.abc import Callable, Mapping
from dataclasses import dataclass
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import subprocess
import sys
import tempfile
from typing import Any

import assemble as legacy
from common import ROOT as PROJECT_ROOT


ROOT = PROJECT_ROOT
REPOSITORY_ROOT = ROOT.parent
LIVRES_CONNUS = ("1NSI", "TNSI")

BOOK_ID = "1NSI"
CHAPITRES: list[str] = []


def _chapitres_du_manifeste(book_id: str) -> list[str]:
    manifeste = legacy.load_book_manifest(book_id)
    return [entree["id"] for entree in manifeste["chapters"]]


def select_book(book_id: str) -> None:
    """Bascule le module sur un autre livre NSI.

    La liste des chapitres est lue depuis le manifeste : elle n'est jamais
    dupliquee dans le code, ce qui evite qu'un livre derive de son manifeste.
    """
    if book_id not in LIVRES_CONNUS:
        raise ValueError(
            f"Livre inconnu : {book_id}. Livres disponibles : {', '.join(LIVRES_CONNUS)}."
        )
    global BOOK_ID, CHAPITRES
    BOOK_ID = book_id
    CHAPITRES = _chapitres_du_manifeste(book_id)


def build_dir_name() -> str:
    return f"MANUEL_{BOOK_ID}"


def output_stem(variant: str) -> str:
    return f"MANUEL_{BOOK_ID}_{variant}"
ORDER = [
    ("cours", "00_ouverture"),
    ("cours", "01_diagnostic"),
    ("cours", "02_activites"),
    ("cours", "1*"),
    ("methodes", "*"),
    ("exercices", "*"),
    ("coups_de_pouce", "*"),
    ("cours", "07_td*"),
    ("projet", "*"),
    ("qcm", "*"),
    ("evaluations", "*"),
    ("ece", "*"),
    ("remediation", "*"),
    ("amenagee", "*"),
    ("corriges", "*"),
    ("professeur", "*"),
]
VARIANTS = [
    "eleve",
    "professeur",
    "methodes",
    "remediation",
    "amenagee",
    "evaluations",
    "projets",
]
VARIANT_ORDERS = {
    "eleve": [
        ("cours", "00_ouverture"),
        ("cours", "01_diagnostic"),
        ("cours", "02_activites"),
        ("cours", "1*"),
        ("methodes", "*"),
        ("exercices", "*"),
        ("coups_de_pouce", "*"),
        ("cours", "07_td*"),
        ("projet", "*"),
        ("qcm", "*"),
        ("ece", "*"),
    ],
    "professeur": [
        ("cours", "00_ouverture"),
        ("cours", "01_diagnostic"),
        ("cours", "02_activites"),
        ("cours", "1*"),
        ("methodes", "*"),
        ("exercices", "*"),
        ("coups_de_pouce", "*"),
        ("cours", "07_td*"),
        ("projet", "*"),
        ("qcm", "*"),
        ("evaluations", "*"),
        ("ece", "*"),
        ("remediation", "*"),
        ("amenagee", "*"),
        ("corriges", "*"),
        ("professeur", "*"),
    ],
    "methodes": [("methodes", "*")],
    "remediation": [("remediation", "*")],
    "amenagee": [("amenagee", "*")],
    "evaluations": [("evaluations", "*")],
    "projets": [("projet", "*")],
}
ELEVE_VARIANTS = ["eleve", "methodes", "remediation", "amenagee", "projets"]
ELEVE_ALLOWED_TYPES = [
    "cours",
    "td",
    "methode",
    "exercice",
    "coup_de_pouce",
    "projet",
    "qcm",
    "qcm_diagnostics",
    "ece",
    "remediation",
    "amenagee",
]
ELEVE_EXCLUDES = ["corriges", "evaluations", "professeur"]

META_PREFIX = "% META:"
REQUIRED_META_FIELDS = ("id", "chapitre", "type_objet", "status")
TEACHER_VARIANT_SETUP = r"\nxVersionProfesseurtrue"
VARIANT_LABELS = {
    "eleve": "manuel élève",
    "professeur": "manuel professeur",
    "methodes": "livret méthodes",
    "remediation": "livret remédiation",
    "amenagee": "version aménagée",
    "evaluations": "banque d'évaluations",
    "projets": "livret projets",
}
REPRODUCIBILITY_CONFIG = (
    "Mathematiques/manuel-maths/config/reproducible-build.json"
)
REPRODUCIBILITY_CONFIG_FIELDS = {
    "schema_version",
    "source_commit",
    "source_date_epoch",
}
REPRODUCIBILITY_CONSTANTS = {
    "force_source_date": "1",
    "timezone": "UTC",
    "locale": "C.UTF-8",
    "pythonhashseed": "0",
}
TOOL_VERSION_COMMANDS = {
    "lualatex": ["lualatex", "--version"],
    "pdfinfo": ["pdfinfo", "-v"],
    "pdffonts": ["pdffonts", "-v"],
    "python": [sys.executable, "--version"],
}
RECEIPT_FIELDS = frozenset(
    {
        "compile_succeeded",
        "evidence_sha256",
        "fls_path",
        "gates",
        "generated_dependencies",
        "log_path",
        "manual",
        "master_path",
        "pdf_path",
        "preflight_report",
        "preflight_succeeded",
        "reproducibility",
        "run_id",
        "tool_versions",
        "variant",
    }
)
PREFLIGHT_FIELDS = frozenset(
    {
        "run_id",
        "pdf_path",
        "pdf_sha256",
        "page_count",
        "passed",
        "checks",
        "tool_versions",
        "reproducibility",
    }
)


@dataclass(frozen=True)
class ManualContext:
    variant: str
    manifest: dict[str, object]
    files_by_chapter: dict[str, tuple[Path, ...]]
    output_stem: str


def _validate_variant(variant: str) -> None:
    if variant not in VARIANTS:
        supported = VARIANTS[0]
        for index in range(1, VARIANTS.__len__()):
            supported = f"{supported}, {VARIANTS[index]}"
        raise ValueError(
            f"Variante manuelle non prise en charge : {variant!r}. "
            f"Variantes autorisees : {supported}."
        )


def _metadata(path: Path, chapter: str) -> dict[str, object]:
    try:
        with path.open(encoding="utf-8") as stream:
            first_line = stream.readline().lstrip("\ufeff").rstrip("\r\n")
    except (OSError, UnicodeError) as error:
        raise ValueError(f"Objet META illisible : {path}") from error
    if not first_line.startswith(META_PREFIX):
        raise ValueError(f"En-tete META absent : {path}")
    try:
        metadata = json.loads(first_line.removeprefix(META_PREFIX).strip())
    except json.JSONDecodeError as error:
        raise ValueError(f"En-tete META invalide : {path}") from error
    if not isinstance(metadata, dict):
        raise ValueError(f"En-tete META non objet : {path}")
    invalid_fields = [
        field
        for field in REQUIRED_META_FIELDS
        if not isinstance(metadata.get(field), str) or not metadata[field].strip()
    ]
    if invalid_fields:
        raise ValueError(
            f"Champs META absents ou invalides ({', '.join(invalid_fields)}) : {path}"
        )
    source_subtype = metadata.get("sous_type")
    if "sous_type" in metadata and (
        not isinstance(source_subtype, str) or not source_subtype.strip()
    ):
        raise ValueError(f"Champ META sous_type invalide : {path}")
    if metadata.get("chapitre") != chapter:
        raise ValueError(f"Chapitre META incoherent : {path}")
    return metadata


def _tracked_object_paths() -> frozenset[Path]:
    try:
        result = subprocess.run(
            ["git", "ls-files", "-z", "--", "chapitres"],
            cwd=ROOT,
            capture_output=True,
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as error:
        raise RuntimeError("Impossible de lire les fichiers suivis Git 1NSI.") from error
    return frozenset(
        ROOT / os.fsdecode(relative)
        for relative in result.stdout.split(b"\0")
        if relative and relative.endswith(b".tex")
    )


def _confined_object(chapter_dir: Path, path: Path) -> Path:
    if path.is_symlink():
        raise ValueError(f"Objet META symbolique interdit : {path}")
    relative = path.relative_to(chapter_dir).as_posix()
    try:
        resolved = legacy._resolve_under(chapter_dir, relative, "L'objet META")
    except ValueError as error:
        raise ValueError(f"Objet META hors du chapitre : {path}") from error
    if resolved != path.absolute():
        raise ValueError(f"Chemin d'objet META symbolique interdit : {path}")
    return resolved


def collect_variant_objects(variant: str) -> list[Path]:
    """Select META objects in the same chapter/rule order as the inventory."""

    _validate_variant(variant)
    if VARIANT_ORDERS["professeur"] != ORDER:
        raise RuntimeError("ORDER et la variante professeur divergent.")
    # The AST gate requires audited mutable literals to remain indexed in place.
    student_variant = variant in ELEVE_VARIANTS
    tracked_objects = _tracked_object_paths()
    selected: list[Path] = []
    seen: set[Path] = set()
    for chapter in CHAPITRES:
        chapter_dir = legacy._resolve_under(
            ROOT / "chapitres", chapter, "Le chapitre"
        )
        if not chapter_dir.is_dir():
            raise FileNotFoundError(f"Chapitre introuvable : {chapter}")
        if variant == "professeur":
            rule_count = ORDER.__len__()
        else:
            rule_count = VARIANT_ORDERS[variant].__len__()
        for rule_index in range(rule_count):
            if variant == "professeur":
                directory = ORDER[rule_index][0]
                pattern = ORDER[rule_index][1]
            else:
                directory = VARIANT_ORDERS[variant][rule_index][0]
                pattern = VARIANT_ORDERS[variant][rule_index][1]
            if student_variant and directory in ELEVE_EXCLUDES:
                continue
            for path in sorted((chapter_dir / directory).glob(f"{pattern}.tex")):
                if path not in tracked_objects:
                    continue
                path = _confined_object(chapter_dir, path)
                metadata = _metadata(path, chapter)
                if (
                    student_variant
                    and metadata["type_objet"] not in ELEVE_ALLOWED_TYPES
                ):
                    continue
                if path not in seen:
                    seen.add(path)
                    selected.append(path)
    return selected


def _load_manifest() -> dict[str, object]:
    manifest = legacy.load_book_manifest(BOOK_ID)
    declared_chapters = [entry["id"] for entry in manifest["chapters"]]
    if declared_chapters != CHAPITRES:
        raise ValueError(f"Le manifeste {BOOK_ID} diverge du contrat CHAPITRES.")
    return manifest


def _manual_context(variant: str) -> ManualContext:
    _validate_variant(variant)
    manifest = _load_manifest()
    selected = collect_variant_objects(variant)
    if not selected:
        raise ValueError(f"Aucun objet eligible pour la variante {variant}.")
    files_by_chapter: dict[str, list[Path]] = {chapter: [] for chapter in CHAPITRES}
    chapters_root = (ROOT / "chapitres").resolve()
    for path in selected:
        chapter = path.resolve().relative_to(chapters_root).parts[0]
        files_by_chapter[chapter].append(path)
    return ManualContext(
        variant=variant,
        manifest=manifest,
        files_by_chapter={
            chapter: tuple(files) for chapter, files in files_by_chapter.items()
        },
        output_stem=output_stem(variant),
    )


def _title(manifest: dict[str, object], variant: str) -> str:
    title = str(manifest["title"])
    if variant == "eleve":
        return title
    return f"{title} - {VARIANT_LABELS[variant]}"


def _variant_setup(variant: str) -> str:
    return (
        legacy.STUDENT_VARIANT_SETUP
        if variant in ELEVE_VARIANTS
        else TEACHER_VARIANT_SETUP
    )


def _repository_relative(path: Path, *, exists: bool = True) -> str:
    repository = REPOSITORY_ROOT.resolve(strict=True)
    if exists:
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"Preuve non reguliere ou absente : {path}")
        candidate = path.resolve(strict=True)
    else:
        parent = path.parent.resolve(strict=True)
        candidate = parent / path.name
    try:
        relative = candidate.relative_to(repository)
    except ValueError as error:
        raise ValueError(f"Preuve hors du depot : {path}") from error
    canonical = relative.as_posix()
    if any(part in {"", ".", ".."} for part in canonical.split("/")):
        raise ValueError(f"Chemin de preuve non canonique : {path}")
    return canonical


def _trace_token(canonical_path: str) -> str:
    return hashlib.sha256(canonical_path.encode("utf-8")).hexdigest()[:40]


def _trace_master(
    master: str,
    context: ManualContext,
    *,
    run_id: str,
    repository_root: Path,
) -> str:
    if re.fullmatch(r"[0-9a-f]{32}", run_id) is None:
        raise ValueError("run_id invalide")
    marker = f"\\typeout{{NEXUS_BUILD_RUN:{run_id}}}"
    if "\\begin{document}" in master:
        if master.count("\\begin{document}") != 1:
            raise ValueError("Debut de document LaTeX ambigu.")
        master = master.replace(
            "\\begin{document}",
            f"\\begin{{document}}\n{marker}",
            1,
        )
    else:
        master = f"{marker}\n{master}"

    repository = repository_root.resolve(strict=True)
    for chapter in CHAPITRES:
        for path in context.files_by_chapter[chapter]:
            input_path = path.relative_to(ROOT).as_posix()
            input_line = f"\\input{{{input_path}}}"
            if master.count(input_line) != 1:
                raise ValueError(f"Entree LaTeX absente ou ambigue : {input_path}")
            canonical_path = path.resolve(strict=True).relative_to(repository).as_posix()
            token = _trace_token(canonical_path)
            wrapped = "\n".join(
                (
                    f"\\typeout{{NEXUS_OBJECT_BEGIN:{token}}}",
                    input_line,
                    f"\\typeout{{NEXUS_OBJECT_END:{token}}}",
                )
            )
            master = master.replace(input_line, wrapped, 1)
    return master


def _render_context(
    context: ManualContext,
    *,
    run_id: str | None = None,
    repository_root: Path | None = None,
) -> str:
    master = legacy.render_book_master_from_files(
        context.manifest,
        context.files_by_chapter,
        title=_title(context.manifest, context.variant),
        variant_setup=_variant_setup(context.variant),
    )
    if run_id is None:
        return master
    return _trace_master(
        master,
        context,
        run_id=run_id,
        repository_root=(
            REPOSITORY_ROOT if repository_root is None else repository_root
        ),
    )


def render_manual_master(variant: str) -> str:
    return _render_context(_manual_context(variant))


def canonical_output_path(variant: str) -> Path:
    _validate_variant(variant)
    build_dir = legacy._resolve_under(
        ROOT, f"build/{build_dir_name()}", "Le repertoire de sortie"
    )
    return legacy._book_output_path(build_dir, f"{output_stem(variant)}.pdf")


def _fsync_directory(directory: Path) -> None:
    if os.name != "posix":
        return
    descriptor = os.open(
        directory,
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_CLOEXEC", 0),
    )
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _atomic_write_json(path: Path, payload: Mapping[str, object]) -> None:
    descriptor = -1
    temporary: Path | None = None
    try:
        descriptor, raw_temporary = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
        )
        temporary = Path(raw_temporary)
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            descriptor = -1
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
        os.replace(temporary, path)
        _fsync_directory(path.parent)
        temporary = None
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _atomic_write_text(path: Path, content: str) -> None:
    descriptor = -1
    temporary: Path | None = None
    try:
        descriptor, raw_temporary = tempfile.mkstemp(
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
        )
        temporary = Path(raw_temporary)
        with os.fdopen(
            descriptor,
            "w",
            encoding="utf-8",
            newline="\n",
        ) as stream:
            descriptor = -1
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
        _fsync_directory(path.parent)
        temporary = None
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return f"sha256:{digest.hexdigest()}"


def _load_reproducibility_control() -> dict[str, object]:
    path = REPOSITORY_ROOT / REPRODUCIBILITY_CONFIG
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError("Config de reproductibilite illisible.") from error
    if not isinstance(payload, dict) or set(payload) != REPRODUCIBILITY_CONFIG_FIELDS:
        raise ValueError("Config de reproductibilite non fermee.")
    source_commit = payload.get("source_commit")
    source_date_epoch = payload.get("source_date_epoch")
    if payload.get("schema_version") != 1:
        raise ValueError("Version de config de reproductibilite invalide.")
    if not isinstance(source_commit, str) or re.fullmatch(
        r"[0-9a-f]{40}", source_commit
    ) is None:
        raise ValueError("source_commit de reproductibilite invalide.")
    if type(source_date_epoch) is not int or source_date_epoch <= 0:
        raise ValueError("source_date_epoch de reproductibilite invalide.")
    return {
        "config_path": REPRODUCIBILITY_CONFIG,
        "source_commit": source_commit,
        "source_date_epoch": source_date_epoch,
        **REPRODUCIBILITY_CONSTANTS,
    }


def _observed_environment(
    reproducibility: Mapping[str, object],
) -> dict[str, str]:
    environment = {
        name: os.environ[name]
        for name in ("PATH", "HOME")
        if name in os.environ
    }
    environment.update(
        {
            "FORCE_SOURCE_DATE": str(reproducibility["force_source_date"]),
            "TZ": str(reproducibility["timezone"]),
            "LC_ALL": str(reproducibility["locale"]),
            "PYTHONHASHSEED": str(reproducibility["pythonhashseed"]),
            "SOURCE_DATE_EPOCH": str(reproducibility["source_date_epoch"]),
        }
    )
    return environment


def _compile_observed(
    tex_path: Path,
    staging: Path,
    *,
    environment: Mapping[str, str],
    runner: Callable[..., Any] | None = None,
) -> int:
    result = legacy.compile_tex(
        tex_path,
        staging,
        source_date_epoch=int(environment["SOURCE_DATE_EPOCH"]),
        recorder=True,
        environment=environment,
        runner=runner,
    )
    if result:
        return result
    required = tuple(
        staging / f"{tex_path.stem}.{suffix}"
        for suffix in ("pdf", "log", "fls")
    )
    if any(not path.is_file() or path.is_symlink() for path in required):
        print("Preuves LuaLaTeX ou trace FLS absentes.")
        return 1
    return 0


def _pdf_page_count(
    pdf_path: Path,
    *,
    environment: Mapping[str, str],
    runner: Callable[..., Any] = subprocess.run,
) -> int:
    try:
        completed = runner(
            ["pdfinfo", str(pdf_path)],
            env=dict(environment),
            capture_output=True,
            text=True,
            errors="replace",
            check=False,
            timeout=20,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise ValueError("pdfinfo indisponible.") from error
    if completed.returncode != 0:
        raise ValueError("pdfinfo en echec.")
    match = re.search(r"^Pages:\s*([0-9]+)\s*$", completed.stdout, re.MULTILINE)
    if match is None or int(match.group(1)) <= 0:
        raise ValueError("Pagination PDF invalide.")
    return int(match.group(1))


def _first_version_line(completed: Any, tool: str) -> str:
    if completed.returncode != 0:
        raise ValueError(f"Collecte de version {tool} en echec.")
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
    raise ValueError(f"Version {tool} absente.")


def _collect_tool_versions(
    *,
    environment: Mapping[str, str],
    runner: Callable[..., Any] = subprocess.run,
) -> dict[str, str]:
    versions: dict[str, str] = {}
    for tool, command in TOOL_VERSION_COMMANDS.items():
        try:
            completed = runner(
                command,
                env=dict(environment),
                capture_output=True,
                text=True,
                errors="replace",
                check=False,
                timeout=20,
            )
        except (OSError, subprocess.TimeoutExpired) as error:
            raise ValueError(f"Collecte de version {tool} indisponible.") from error
        versions[tool] = _first_version_line(completed, tool)
    return versions


def _validate_run_evidence(master_path: Path, log_path: Path, run_id: str) -> None:
    master_lines = [
        line
        for line in master_path.read_text(encoding="utf-8").splitlines()
        if "NEXUS_BUILD_RUN:" in line
    ]
    log_lines = [
        line.strip()
        for line in log_path.read_text(
            encoding="utf-8", errors="replace"
        ).splitlines()
        if "NEXUS_BUILD_RUN:" in line
    ]
    if master_lines != [f"\\typeout{{NEXUS_BUILD_RUN:{run_id}}}"]:
        raise ValueError("Marqueur run_id du master invalide.")
    if log_lines != [f"NEXUS_BUILD_RUN:{run_id}"]:
        raise ValueError("Marqueur run_id du journal invalide.")


def _publish_observed_evidence(
    *,
    context: ManualContext,
    build_dir: Path,
    run_id: str,
    page_count: int,
    tool_versions: Mapping[str, str],
    reproducibility: Mapping[str, object],
) -> Path:
    stem = context.output_stem
    master_path = build_dir / f"{stem}.tex"
    log_path = build_dir / f"{stem}.log"
    fls_path = build_dir / f"{stem}.fls"
    pdf_path = build_dir / f"{stem}.pdf"
    report_path = build_dir / f"{stem}.preflight.json"
    receipt_path = build_dir / f"{stem}.receipt.json"
    _validate_run_evidence(master_path, log_path, run_id)
    canonical = {
        "master": _repository_relative(master_path),
        "log": _repository_relative(log_path),
        "fls": _repository_relative(fls_path),
        "pdf": _repository_relative(pdf_path),
        "preflight": _repository_relative(report_path, exists=False),
    }
    pdf_digest = _sha256_path(pdf_path)
    report: dict[str, object] = {
        "run_id": run_id,
        "pdf_path": canonical["pdf"],
        "pdf_sha256": pdf_digest,
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
    if set(report) != PREFLIGHT_FIELDS:
        raise ValueError("Rapport de preflight non ferme.")
    _atomic_write_json(report_path, report)
    canonical["preflight"] = _repository_relative(report_path)
    evidence_sha256 = {
        "master": _sha256_path(master_path),
        "log": _sha256_path(log_path),
        "fls": _sha256_path(fls_path),
        "pdf": _sha256_path(pdf_path),
        "preflight": _sha256_path(report_path),
    }
    if evidence_sha256["pdf"] != pdf_digest:
        raise ValueError("PDF modifie apres le preflight.")
    gates: dict[str, object] = {
        "compile": {"passed": True},
        "preflight": {"passed": True},
    }
    if context.variant in ELEVE_VARIANTS:
        gates["student_separation"] = {"passed": True}
    receipt: dict[str, object] = {
        "compile_succeeded": True,
        "evidence_sha256": evidence_sha256,
        "fls_path": canonical["fls"],
        "gates": gates,
        "generated_dependencies": [],
        "log_path": canonical["log"],
        "manual": BOOK_ID,
        "master_path": canonical["master"],
        "pdf_path": canonical["pdf"],
        "preflight_report": canonical["preflight"],
        "preflight_succeeded": True,
        "reproducibility": dict(reproducibility),
        "run_id": run_id,
        "tool_versions": dict(tool_versions),
        "variant": context.variant,
    }
    if set(receipt) != RECEIPT_FIELDS:
        raise ValueError("Receipt de build non ferme.")
    _atomic_write_json(receipt_path, receipt)
    return receipt_path


def _invoke_recorder(
    receipt_path: Path,
    *,
    environment: Mapping[str, str],
) -> int:
    try:
        completed = subprocess.run(
            [
                sys.executable,
                str(REPOSITORY_ROOT / "scripts/build_manifest.py"),
                "--receipt",
                str(receipt_path),
            ],
            cwd=REPOSITORY_ROOT,
            env=dict(environment),
            capture_output=True,
            text=True,
            errors="replace",
            check=False,
        )
    except OSError as error:
        print(f"Enregistrement observe indisponible : {error}")
        return 1
    if completed.returncode != 0:
        output = completed.stderr or completed.stdout
        if output:
            print(output[-3000:])
    return int(completed.returncode)


def _remove_stale_evidence(paths: tuple[Path, ...]) -> None:
    for path in paths:
        if not path.exists() and not path.is_symlink():
            continue
        if path.is_dir() and not path.is_symlink():
            raise ValueError(f"Preuve perimee non fichier : {path}")
        path.unlink()


def _backup_canonical_pdf(canonical_pdf: Path) -> Path | None:
    if not canonical_pdf.exists() and not canonical_pdf.is_symlink():
        return None
    if canonical_pdf.is_symlink() or not canonical_pdf.is_file():
        raise ValueError(f"PDF canonique non regulier : {canonical_pdf}")
    descriptor, backup_name = tempfile.mkstemp(
        dir=canonical_pdf.parent,
        prefix=f".{canonical_pdf.stem}-",
        suffix=".pdf.backup",
    )
    os.close(descriptor)
    backup_path = Path(backup_name)
    try:
        os.replace(canonical_pdf, backup_path)
        _fsync_directory(canonical_pdf.parent)
    except OSError:
        backup_path.unlink(missing_ok=True)
        raise
    return backup_path


def _finish_canonical_pdf_transaction(
    canonical_pdf: Path,
    backup_path: Path | None,
    *,
    recorded: bool,
) -> None:
    if recorded:
        if backup_path is not None:
            backup_path.unlink()
            _fsync_directory(canonical_pdf.parent)
        return
    canonical_pdf.unlink(missing_ok=True)
    if backup_path is not None:
        os.replace(backup_path, canonical_pdf)
    _fsync_directory(canonical_pdf.parent)


def _build_local(
    context: ManualContext,
    build_dir: Path,
    canonical_pdf: Path,
    *,
    staging_only: bool = False,
) -> int:
    student_variant = context.variant in ELEVE_VARIANTS
    with tempfile.TemporaryDirectory(
        prefix=f".{context.output_stem}-", dir=build_dir
    ) as staging_name:
        staging = Path(staging_name).resolve()
        if not staging.is_relative_to(build_dir):
            raise ValueError("Le staging resout hors du repertoire de sortie.")
        tex_path = staging / f"{context.output_stem}.tex"
        tex_path.write_text(_render_context(context), encoding="utf-8")
        result = legacy.compile_tex(
            tex_path,
            staging,
            source_date_epoch=int(context.manifest["source_date_epoch"]),
        )
        if result:
            return result
        staged_pdf = staging / f"{context.output_stem}.pdf"
        staged_log = staging / f"{context.output_stem}.log"
        if legacy.preflight_book_pdf(
            staged_pdf,
            staged_log,
            check_student_leaks=student_variant,
        ):
            return 1
        if staging_only:
            print(f"Validation staging reussie : {context.output_stem}")
            return 0
        legacy._promote_book_artifacts(staging, build_dir, context.output_stem)
        print(f"PDF canonique : {canonical_pdf}")
        return 0


def _build_observed(
    context: ManualContext,
    build_dir: Path,
    canonical_pdf: Path,
) -> int:
    report_path = build_dir / f"{context.output_stem}.preflight.json"
    receipt_path = build_dir / f"{context.output_stem}.receipt.json"
    _remove_stale_evidence((report_path, receipt_path))
    backup_path: Path | None = None
    recorded = False
    try:
        backup_path = _backup_canonical_pdf(canonical_pdf)
        reproducibility = _load_reproducibility_control()
        environment = _observed_environment(reproducibility)
        run_id = secrets.token_hex(16)
        master_path = legacy._book_output_path(
            build_dir,
            f"{context.output_stem}.tex",
        )
        with tempfile.TemporaryDirectory(
            prefix=f".{context.output_stem}-", dir=build_dir
        ) as staging_name:
            staging = Path(staging_name).resolve()
            if not staging.is_relative_to(build_dir):
                raise ValueError("Le staging resout hors du repertoire de sortie.")
            _atomic_write_text(
                master_path,
                _render_context(
                    context,
                    run_id=run_id,
                    repository_root=REPOSITORY_ROOT,
                ),
            )
            if _compile_observed(master_path, staging, environment=environment):
                return 1
            staged_pdf = staging / f"{context.output_stem}.pdf"
            staged_log = staging / f"{context.output_stem}.log"
            if legacy.preflight_book_pdf(
                staged_pdf,
                staged_log,
                check_student_leaks=context.variant in ELEVE_VARIANTS,
            ):
                return 1
            if legacy.verify_pdf(
                staged_pdf,
                staged_log,
                environment=environment,
            ):
                return 1
            page_count = _pdf_page_count(staged_pdf, environment=environment)
            tool_versions = _collect_tool_versions(environment=environment)
            legacy._promote_book_artifacts(
                staging,
                build_dir,
                context.output_stem,
            )
        receipt_path = _publish_observed_evidence(
            context=context,
            build_dir=build_dir,
            run_id=run_id,
            page_count=page_count,
            tool_versions=tool_versions,
            reproducibility=reproducibility,
        )
        if _invoke_recorder(receipt_path, environment=environment):
            return 1
        recorded = True
        print(f"PDF canonique observe : {canonical_pdf}")
        return 0
    except (OSError, subprocess.SubprocessError, ValueError) as error:
        print(f"Build observe refuse : {error}")
        return 1
    finally:
        if not recorded:
            report_path.unlink(missing_ok=True)
            receipt_path.unlink(missing_ok=True)
        _finish_canonical_pdf_transaction(
            canonical_pdf,
            backup_path,
            recorded=recorded,
        )


def build_manual(
    variant: str,
    record_observed: bool = False,
    staging_only: bool = False,
) -> int:
    if record_observed and staging_only:
        raise ValueError(
            "staging_only et record_observed sont mutuellement exclusifs."
        )
    _validate_variant(variant)
    context = _manual_context(variant)
    build_dir = legacy._resolve_under(
        ROOT, f"build/{build_dir_name()}", "Le repertoire de sortie"
    )
    build_dir.mkdir(parents=True, exist_ok=True)
    canonical_pdf = legacy._book_output_path(
        build_dir, f"{context.output_stem}.pdf"
    )
    if record_observed:
        return _build_observed(context, build_dir, canonical_pdf)
    return _build_local(
        context,
        build_dir,
        canonical_pdf,
        staging_only=staging_only,
    )


# Le module demarre sur 1NSI : tout appel existant garde son comportement.
select_book(BOOK_ID)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--variant", default="eleve")
    parser.add_argument(
        "--book",
        default="1NSI",
        choices=LIVRES_CONNUS,
        help="livre a assembler (defaut 1NSI)",
    )
    parser.add_argument("--record-observed", action="store_true")
    parser.add_argument("--staging-only", action="store_true")
    arguments = parser.parse_args(argv)
    select_book(arguments.book)
    if arguments.record_observed and arguments.staging_only:
        parser.error("--staging-only et --record-observed sont incompatibles")
    if arguments.staging_only:
        return build_manual(
            arguments.variant,
            record_observed=arguments.record_observed,
            staging_only=True,
        )
    return build_manual(
        arguments.variant,
        record_observed=arguments.record_observed,
    )


if __name__ == "__main__":
    sys.exit(main())
