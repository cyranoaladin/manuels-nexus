"""Assemblage du manuel complet 1SPE : transversal + 10 chapitres.

Variantes :
  --variant professeur  (tout : cours, exercices, corriges, evaluations, baremes)
  --variant eleve       (sans corriges ni baremes d'evaluation)
"""
import argparse
import fcntl
import hashlib
import json
import os
import re
import secrets
import shutil
import stat
import subprocess
import sys
import tempfile
from collections.abc import Callable, Mapping
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import yaml

from common import ROOT
from pdf_integrity import verify_pdf

# L'analyseur statique (scripts/inventory_assembly.py) ne reconnait un
# "assembleur de manuel" que pour un fichier nomme exactement
# .../scripts/assemble_manuel.py et ne lit CHAPITRES qu'avec ast.literal_eval,
# qui exige un litteral pur (pas une expression referencant d'autres noms,
# meme une simple concatenation). CHAPITRES doit donc rester le seul et
# unique litteral source de verite, union de tous les manuels geres ici ; il
# est ensuite regroupe par manuel via le prefixe de chaque chapitre. Un seul
# tel fichier peut exister par repertoire scripts/, d'ou l'union ici plutot
# qu'un fichier separe par manuel.
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
    # Ordre officiel du perimetre TSPE corrige le 2026-08-05
    # (docs/10_perimetre_terminale.md, programme 2019 MENE1921247A).
    # Le chapitre 10bis TSPE-CONCENTRATION-LGN reste un point ouvert
    # A_VALIDER_HUMAIN (fusion dans TSPE-PROBABILITES ou chapitre distinct)
    # et n'est pas produit : il n'apparait donc pas ici.
    "TSPE-SUITES-LIMITES",
    "TSPE-LIMITES-FONCTIONS",
    "TSPE-CONTINUITE",
    "TSPE-DERIVATION-CONVEXITE",
    "TSPE-TRIGONOMETRIE",
    "TSPE-LOGARITHME",
    "TSPE-PRIMITIVES-EQDIFF",
    "TSPE-CALCUL-INTEGRAL",
    "TSPE-COMBINATOIRE",
    "TSPE-PROBABILITES",
    "TSPE-GEOMETRIE-ESPACE",
]
CHAPITRES_1SPE = [chap for chap in CHAPITRES if chap.startswith("1SPE-")]
CHAPITRES_TSPE = [chap for chap in CHAPITRES if chap.startswith("TSPE-")]

MANUAL_TEX_NAMES = {
    "1SPE": "MANUEL_1SPE",
    "TSPE_2026_2027": "MANUEL_TSPE_2026-2027",
}
MANUAL_CHAPTERS = {
    "1SPE": CHAPITRES_1SPE,
    "TSPE_2026_2027": CHAPITRES_TSPE,
}
MANUAL_TITLES = {
    "1SPE": "Manuel de mathématiques — Première spécialité",
    "TSPE_2026_2027": "Manuel de mathématiques — Terminale spécialité",
}

ORDER = [
    ("cours", "00_ouverture"), ("cours", "01_diagnostic"), ("cours", "02_activites"),
    ("cours", "1*"), ("methodes", "*"), ("exercices", "*"),
    ("cours", "07_td*"), ("qcm", "*"), ("evaluations", "*"), ("remediation", "*"),
    ("corriges", "*"),
]

ELEVE_EXCLUDES = {"corriges"}
ELEVE_ALLOWED_TYPES = {
    "algorithme",
    "cours",
    "coup_de_pouce",
    "evaluation",
    "experimentation",
    "exercice",
    "methode",
    "qcm",
    "remediation",
    "td",
}

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
PASSTHROUGH_ENVIRONMENT = ("PATH", "HOME")


class AssemblyError(RuntimeError):
    """Failure that prevents a compiled PDF from becoming observed evidence."""


FileFingerprint = tuple[int, int, int, int, int, int, int]
DirectoryFingerprint = tuple[int, int]


def _active_runner(runner: Callable[..., Any] | None) -> Callable[..., Any]:
    return subprocess.run if runner is None else runner


def _run_with_environment(
    runner: Callable[..., Any],
    environment: Mapping[str, str],
    command: list[str],
    **kwargs: Any,
) -> Any:
    return runner(command, env=dict(environment), **kwargs)


def _allowlisted_environment(
    source: Mapping[str, str] | None = None,
) -> dict[str, str]:
    values = os.environ if source is None else source
    return {
        name: values[name]
        for name in PASSTHROUGH_ENVIRONMENT
        if name in values
    }


def _git_environment(
    environment: Mapping[str, str] | None = None,
) -> dict[str, str]:
    if environment is None:
        return _allowlisted_environment()
    allowed = set(PASSTHROUGH_ENVIRONMENT) | set(CONTROLLED_ENVIRONMENT) | {
        "SOURCE_DATE_EPOCH"
    }
    return {
        name: value
        for name, value in environment.items()
        if name in allowed and not name.startswith("GIT_")
    }


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

    environment = _allowlisted_environment()
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
            _git_environment(environment),
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
            _git_environment(environment),
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
            _git_environment(environment),
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
        _fsync_directory(destination.parent)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        temporary.unlink(missing_ok=True)


def _atomic_write_text(destination: Path, content: str) -> None:
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
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(destination)
        _fsync_directory(destination.parent)
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


def _secure_build_directory(
    manual_root: Path, subdirectory: str = "MANUEL_1SPE"
) -> Path:
    try:
        root_metadata = manual_root.lstat()
    except OSError as error:
        raise AssemblyError("racine du manuel indisponible") from error
    if stat.S_ISLNK(root_metadata.st_mode) or not stat.S_ISDIR(
        root_metadata.st_mode
    ):
        raise AssemblyError("racine du manuel non sûre")

    current = manual_root
    for component in ("build", subdirectory):
        candidate = current / component
        try:
            candidate.mkdir(mode=0o755)
        except FileExistsError:
            pass
        except OSError as error:
            raise AssemblyError("création du répertoire de build impossible") from error
        try:
            metadata = candidate.lstat()
        except OSError as error:
            raise AssemblyError("répertoire de build indisponible") from error
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise AssemblyError("composant symbolique ou non répertoire du build")
        current = candidate
    return current


@contextmanager
def _exclusive_build_lock(
    build: Path, variant: str, tex_name_prefix: str = "MANUEL_1SPE"
) -> Any:
    lock_path = build / f".{tex_name_prefix}_{variant}.lock"
    flags = (
        os.O_RDWR
        | os.O_CREAT
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        descriptor = os.open(lock_path, flags, 0o600)
    except OSError as error:
        raise AssemblyError("verrou de build indisponible") from error
    locked = False
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_nlink != 1:
            raise AssemblyError("verrou de build non sûr")
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as error:
            raise AssemblyError("build concurrent déjà actif") from error
        locked = True
        yield
    finally:
        if locked:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        os.close(descriptor)


def _remove_private_run_directory(
    run_directory: Path,
    expected: DirectoryFingerprint,
) -> None:
    try:
        metadata = run_directory.lstat()
    except FileNotFoundError:
        return
    except OSError as error:
        raise AssemblyError("répertoire privé de build inaccessible") from error
    if (
        stat.S_ISLNK(metadata.st_mode)
        or not stat.S_ISDIR(metadata.st_mode)
        or (metadata.st_dev, metadata.st_ino) != expected
    ):
        raise AssemblyError("répertoire privé de build remplacé")
    try:
        shutil.rmtree(run_directory)
        _fsync_directory(run_directory.parent)
    except OSError as error:
        raise AssemblyError("nettoyage du build privé impossible") from error


@contextmanager
def _private_run_directory(
    build: Path,
    tex_name: str,
    run_id: str,
) -> Any:
    if re.fullmatch(r"[0-9a-f]{32}", run_id) is None:
        raise AssemblyError("run_id du build privé invalide")
    run_directory = build / f".{tex_name}.{run_id}.run"
    try:
        run_directory.mkdir(mode=0o700)
    except FileExistsError as error:
        raise AssemblyError("répertoire privé de build déjà présent") from error
    except OSError as error:
        raise AssemblyError("création du build privé impossible") from error

    created = False
    fingerprint: DirectoryFingerprint | None = None
    try:
        created = True
        os.chmod(run_directory, 0o700, follow_symlinks=False)
        metadata = run_directory.lstat()
        if (
            stat.S_ISLNK(metadata.st_mode)
            or not stat.S_ISDIR(metadata.st_mode)
            or stat.S_IMODE(metadata.st_mode) != 0o700
        ):
            raise AssemblyError("répertoire privé de build non sûr")
        fingerprint = (metadata.st_dev, metadata.st_ino)
        _fsync_directory(build)
        yield run_directory
    finally:
        if created and fingerprint is not None:
            _remove_private_run_directory(run_directory, fingerprint)


def _invalidate_outputs(paths: tuple[Path, ...]) -> None:
    for path in paths:
        try:
            metadata = path.lstat()
        except FileNotFoundError:
            continue
        except OSError as error:
            raise AssemblyError(f"sortie périmée inaccessible: {path.name}") from error
        if stat.S_ISDIR(metadata.st_mode):
            raise AssemblyError(f"sortie périmée non fichier: {path.name}")
        try:
            path.unlink()
        except OSError as error:
            raise AssemblyError(f"sortie périmée non invalidée: {path.name}") from error


def _fingerprint_regular_file(path: Path, role: str) -> FileFingerprint:
    try:
        metadata = path.lstat()
    except OSError as error:
        raise AssemblyError(f"{role} frais absent") from error
    if (
        stat.S_ISLNK(metadata.st_mode)
        or not stat.S_ISREG(metadata.st_mode)
        or metadata.st_nlink != 1
    ):
        raise AssemblyError(f"{role} non régulier, symbolique ou multi-lié")
    return (
        metadata.st_dev,
        metadata.st_ino,
        stat.S_IFMT(metadata.st_mode),
        metadata.st_nlink,
        metadata.st_size,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )


def _atomic_promote_file(source: Path, destination: Path) -> None:
    source_fingerprint = _fingerprint_regular_file(source, source.name)
    source_descriptor = -1
    destination_descriptor = -1
    temporary: Path | None = None
    try:
        source_descriptor = os.open(
            source,
            os.O_RDONLY
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0),
        )
        source_metadata = os.fstat(source_descriptor)
        if (
            not stat.S_ISREG(source_metadata.st_mode)
            or source_metadata.st_nlink != 1
            or (
                source_metadata.st_dev,
                source_metadata.st_ino,
                stat.S_IFMT(source_metadata.st_mode),
                source_metadata.st_nlink,
                source_metadata.st_size,
                source_metadata.st_mtime_ns,
                source_metadata.st_ctime_ns,
            )
            != source_fingerprint
        ):
            raise AssemblyError(f"source de promotion modifiée: {source.name}")

        destination_descriptor, raw_temporary = tempfile.mkstemp(
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
        )
        temporary = Path(raw_temporary)
        with (
            os.fdopen(source_descriptor, "rb") as source_stream,
            os.fdopen(destination_descriptor, "wb") as destination_stream,
        ):
            source_descriptor = -1
            destination_descriptor = -1
            shutil.copyfileobj(source_stream, destination_stream)
            destination_stream.flush()
            os.fsync(destination_stream.fileno())

        if _fingerprint_regular_file(source, source.name) != source_fingerprint:
            raise AssemblyError(f"source de promotion modifiée: {source.name}")
        temporary.replace(destination)
        _fsync_directory(destination.parent)
    finally:
        if source_descriptor >= 0:
            os.close(source_descriptor)
        if destination_descriptor >= 0:
            os.close(destination_descriptor)
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def _compiled_output_fingerprints(
    *,
    root: Path,
    tex_path: Path,
    log_path: Path,
    fls_path: Path,
    pdf_path: Path,
    run_id: str,
) -> dict[Path, FileFingerprint]:
    fingerprints = {
        tex_path: _fingerprint_regular_file(tex_path, "maître"),
        log_path: _fingerprint_regular_file(log_path, "journal"),
        fls_path: _fingerprint_regular_file(fls_path, "trace FLS"),
        pdf_path: _fingerprint_regular_file(pdf_path, "PDF"),
    }
    log = log_path.read_text(encoding="utf-8", errors="replace")
    if f"NEXUS_BUILD_RUN:{run_id}" not in log:
        raise AssemblyError("journal sans run_id courant")

    master = tex_path.resolve(strict=True)
    master_opened = False
    for line in fls_path.read_text(encoding="utf-8", errors="replace").splitlines():
        kind, separator, raw_path = line.partition(" ")
        if kind != "INPUT" or not separator:
            continue
        candidate = Path(raw_path.strip())
        if not candidate.is_absolute():
            candidate = root / candidate
        try:
            master_opened = candidate.resolve(strict=True) == master
        except OSError:
            master_opened = False
        if master_opened:
            break
    if not master_opened:
        raise AssemblyError("trace FLS sans maître courant")
    return fingerprints


def _revalidate_fingerprints(
    expected: Mapping[Path, FileFingerprint],
) -> None:
    for path, fingerprint in expected.items():
        if _fingerprint_regular_file(path, path.name) != fingerprint:
            raise AssemblyError(f"preuve modifiée pendant le préflight: {path.name}")


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
    options["env"] = _git_environment(environment)
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
    options["env"] = _git_environment(environment)
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


def object_type(path: Path) -> str:
    """Read the closed student/professor routing discriminator from META."""

    try:
        lines = path.read_text(encoding="utf-8").splitlines()[:10]
    except (OSError, UnicodeError) as error:
        raise AssemblyError(f"META illisible: {path}") from error
    meta_lines = [
        line.removeprefix("% META:").strip()
        for line in lines
        if line.startswith("% META:")
    ]
    if len(meta_lines) != 1:
        raise AssemblyError(f"META absente ou ambiguë: {path}")
    try:
        payload = json.loads(meta_lines[0])
    except json.JSONDecodeError as error:
        raise AssemblyError(f"META JSON invalide: {path}") from error
    value = payload.get("type_objet") if isinstance(payload, dict) else None
    if not isinstance(value, str) or not value:
        raise AssemblyError(f"type_objet META invalide: {path}")
    return value


def collect_chapter(chap_dir: Path, variant: str) -> list[Path]:
    if variant not in {"eleve", "professeur"}:
        raise AssemblyError("variante inconnue")
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
    if variant == "eleve":
        files = [
            path
            for path in files
            if object_type(path) in ELEVE_ALLOWED_TYPES
        ]
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
    manual: str = "1SPE",
    git_root: Path | None = None,
    tracked_paths: frozenset[str] | None = None,
) -> str:
    if variant not in {"eleve", "professeur"}:
        raise ValueError("variante inconnue")
    if manual not in MANUAL_CHAPTERS:
        raise ValueError("manuel inconnu")
    if re.fullmatch(r"[0-9a-f]{32}", run_id) is None:
        raise ValueError("identifiant de build invalide")
    if git_root is None:
        git_root = resolve_git_root(ROOT)
    if tracked_paths is None:
        tracked_paths = load_tracked_paths(git_root)
    parts = []

    # Transversal front matter. Le texte 1SPE (avant-propos, mode d'emploi,
    # formulaire, memo Python) est ecrit pour la Premiere specialite et n'est
    # pas reutilisable tel quel pour un autre manuel : les manuels autres que
    # 1SPE recoivent une page de titre minimale a la place, sans prejuger de
    # leur futur contenu transversal propre.
    if manual == "1SPE":
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
    else:
        parts.append("\\tableofcontents")
        parts.append("\\newpage")

    # Chapters
    for chap in MANUAL_CHAPTERS[manual]:
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

    # Back matter (1SPE uniquement : formulaire et memo Python specifiques)
    if manual == "1SPE":
        parts.append("\\appendix")
        parts.append("\\clearpage")
        parts.append("\\input{transversal/formulaire}")
        parts.append("\\clearpage")
        parts.append("\\input{transversal/memo_python}")

    content = "\n".join(parts)

    titre_var = "professeur" if variant == "professeur" else "eleve"
    variant_configuration = (
        "\\nxVersionProfesseurtrue"
        if variant == "professeur"
        else "\n".join(
            (
                "\\nxVersionProfesseurfalse",
                "\\RenewDocumentEnvironment{corrige}{m +b}{}{}",
                "\\renewcommand{\\baremeIndicatif}[1]{}",
            )
        )
    )
    matiere_niveau = (
        "\\matiere{Mathématiques}\\niveau{Première spécialité}"
        if manual == "1SPE"
        else "\\matiere{Mathématiques}\\niveau{Terminale spécialité}"
    )
    master = f"""% {MANUAL_TITLES[manual]} — variante {titre_var}
% Assemble par scripts/assemble_manuel.py
\\documentclass{{gabarits/nexus-manuel}}
{variant_configuration}
{matiere_niveau}
\\title{{{MANUAL_TITLES[manual]} — Édition {titre_var}}}
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


def student_text_violations(text: str) -> list[str]:
    """Return stable P0 reasons found in extracted student PDF text."""

    checks = (
        ("identifiant interne", r"\b1SPE-[A-Z0-9]+(?:-[A-Z0-9]+)*"),
        ("corrigé", r"(?i:\bcorrig[ée]s?\b)"),
        ("barème enseignant", r"(?i:\bbar[èe]me indicatif\b)"),
        (
            "note enseignant",
            r"(?i:\b(?:note|réponse|reponse)\s+(?:professeur|enseignant)\b)",
        ),
    )
    return [reason for reason, pattern in checks if re.search(pattern, text)]


def _verify_student_pdf_text(
    pdf_path: Path,
    *,
    runner: Callable[..., Any],
    environment: Mapping[str, str],
) -> None:
    try:
        completed = _run_with_environment(
            runner,
            environment,
            ["pdftotext", "-layout", str(pdf_path), "-"],
            capture_output=True,
            text=True,
            errors="replace",
            check=False,
            timeout=60,
        )
    except (OSError, subprocess.TimeoutExpired) as error:
        raise AssemblyError("contrôle textuel élève indisponible") from error
    if completed.returncode != 0:
        raise AssemblyError("extraction textuelle élève en échec")
    violations = student_text_violations(completed.stdout)
    if violations:
        raise AssemblyError(
            "séparation élève rouge: " + ", ".join(violations)
        )


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
    manual: str,
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
    compiled_fingerprints: Mapping[Path, FileFingerprint],
) -> None:
    _revalidate_fingerprints(compiled_fingerprints)
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

    _revalidate_fingerprints(compiled_fingerprints)
    evidence_sha256 = {
        "master": _sha256_path(tex_path),
        "log": _sha256_path(log_path),
        "fls": _sha256_path(fls_path),
        "preflight": _sha256_path(report_path),
        "pdf": _sha256_path(pdf_path),
    }
    _revalidate_fingerprints(compiled_fingerprints)
    if evidence_sha256["pdf"] != preflight_pdf_digest:
        raise AssemblyError("PDF modifié après le préflight")
    gates: dict[str, object] = {
        "compile": {"passed": True},
        "preflight": {"passed": True},
    }
    if variant == "eleve":
        gates["student_separation"] = {"passed": True}
    receipt = {
        "compile_succeeded": True,
        "fls_path": canonical["fls"],
        "gates": gates,
        "generated_dependencies": [],
        "log_path": canonical["log"],
        "manual": manual,
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


def _main_locked(
    variant: str,
    record_observed: bool = False,
    *,
    manual: str = "1SPE",
    active_runner: Callable[..., Any],
    build: Path,
) -> int:
    tex_name = f"{MANUAL_TEX_NAMES[manual]}_{variant}"
    tex_path = build / f"{tex_name}.tex"
    pdf_path = build / f"{tex_name}.pdf"
    log_path = build / f"{tex_name}.log"
    fls_path = build / f"{tex_name}.fls"
    report_path = build / f"{tex_name}.preflight.json"
    receipt_path = build / f"{tex_name}.receipt.json"

    _invalidate_outputs((report_path, receipt_path))
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
            manual=manual,
            git_root=git_root,
            tracked_paths=tracked_paths,
        )
    except (AssemblyError, OSError, subprocess.SubprocessError, ValueError) as error:
        print(f"Assemblage refusé : {error}")
        return 1

    try:
        with _private_run_directory(build, tex_name, run_id) as run_directory:
            _atomic_write_text(tex_path, master)
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
                    raise AssemblyError("LuaLaTeX indisponible") from error
                if proc.returncode != 0:
                    output = getattr(proc, "stdout", "") or ""
                    detail = output[-3000:].strip()
                    message = f"LuaLaTeX en échec à la passe {pass_number}"
                    if detail:
                        message += f" : {detail}"
                    raise AssemblyError(message)

            candidate_fingerprints = _compiled_output_fingerprints(
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
                raise AssemblyError("préflight PDF en échec")
            if variant == "eleve":
                _verify_student_pdf_text(
                    run_pdf_path,
                    runner=active_runner,
                    environment=environment,
                )
            page_count = _pdf_page_count(
                run_pdf_path,
                runner=active_runner,
                environment=environment,
            )
            tool_versions = _collect_tool_versions(
                runner=active_runner,
                environment=environment,
            )
            _revalidate_fingerprints(candidate_fingerprints)

            for source, destination in (
                (run_log_path, log_path),
                (run_fls_path, fls_path),
                (run_pdf_path, pdf_path),
            ):
                _revalidate_fingerprints(candidate_fingerprints)
                _atomic_promote_file(source, destination)
            _revalidate_fingerprints(candidate_fingerprints)
            compiled_fingerprints = _compiled_output_fingerprints(
                root=ROOT,
                tex_path=tex_path,
                log_path=log_path,
                fls_path=fls_path,
                pdf_path=pdf_path,
                run_id=run_id,
            )
    except (AssemblyError, OSError, subprocess.SubprocessError, ValueError) as error:
        print(f"Build candidat refusé : {error}")
        return 1

    if not record_observed:
        print(f"PDF : {pdf_path}")
        return 0

    try:
        _publish_observed_evidence(
            variant=variant,
            manual=manual,
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
            compiled_fingerprints=compiled_fingerprints,
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


def main(
    variant: str,
    record_observed: bool = False,
    *,
    manual: str = "1SPE",
    runner: Callable[..., Any] | None = None,
) -> int:
    if manual not in MANUAL_TEX_NAMES:
        print("Build refusé : manuel inconnu")
        return 1
    active_runner = _active_runner(runner)
    try:
        build = _secure_build_directory(ROOT, MANUAL_TEX_NAMES[manual])
        with _exclusive_build_lock(build, variant, MANUAL_TEX_NAMES[manual]):
            return _main_locked(
                variant,
                record_observed,
                manual=manual,
                active_runner=active_runner,
                build=build,
            )
    except (AssemblyError, OSError, ValueError) as error:
        print(f"Build refusé : {error}")
        return 1


def build_argument_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--variant",
        default="professeur",
        choices=["professeur", "eleve"],
    )
    ap.add_argument(
        "--manual",
        default="1SPE",
        choices=sorted(MANUAL_TEX_NAMES),
    )
    ap.add_argument("--record-observed", action="store_true")
    return ap


if __name__ == "__main__":
    args = build_argument_parser().parse_args()
    sys.exit(
        main(
            args.variant,
            record_observed=args.record_observed,
            manual=args.manual,
        )
    )
