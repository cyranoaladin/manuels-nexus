"""Assemblage (R5/F06) : génère le .tex maître d'un chapitre depuis les objets,
dans l'ordre des 9 temps du gabarit, puis compile (LuaLaTeX ×2).

Déclinaisons : --variant complet|methodes|parcours1|remediation
"""
import argparse
import fcntl
import hashlib
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from collections.abc import Iterable, Mapping
from pathlib import Path

import yaml

from common import ROOT
from pdf_integrity import verify_pdf
from pdf_reproducibility import pdf_trailer_identity

ORDER = [  # les 9 temps du gabarit (docs/01 Partie 3)
    ("cours", "00_ouverture"), ("cours", "01_diagnostic"), ("cours", "02_activites"),
    ("cours", "1*"), ("methodes", "*"), ("exercices", "*"),
    ("cours", "07_td*"), ("qcm", "*"), ("evaluations", "*"), ("remediation", "*"),
]
CLI_VARIANTS = ("complet", "methodes", "parcours1", "remediation")
CHAPTER_TOC_VARIANTS = ("complet", "parcours1")
CHAPTER_TOC_BLOCK = "\\tableofcontents\n\\clearpage\n"
PROVED_TOOLCHAIN_VARIABLES = (
    "TEXMFDIST",
    "TEXMFVAR",
    "TEXMFSYSVAR",
    "TEXMFSYSCONFIG",
)
CANONICAL_RENDER_AUTHORITIES = (
    "gabarits/common/nexus-manuel.cls",
    "gabarits/common/nexus-charte.sty",
    "gabarits/common/nexus-pont.sty",
)
A4_REPRODUCIBLE_ENVIRONMENT = {
    "SOURCE_DATE_EPOCH": "1785962466",
    "FORCE_SOURCE_DATE": "1",
    "TZ": "UTC",
    "LC_ALL": "C.UTF-8",
    "LANG": "C.UTF-8",
    "PYTHONHASHSEED": "0",
}
CHAPTER_ID_RE = re.compile(r"[A-Z0-9]+(?:-[A-Z0-9]+)*")


def sealed_build_environment(
    source: Mapping[str, str] | None = None,
) -> dict[str, str]:
    """Return the strict common allowlist for Git, kpsewhich and LuaLaTeX."""
    original = os.environ if source is None else source
    environment: dict[str, str] = {}
    for required in ("PATH", "HOME"):
        if not original.get(required):
            raise ValueError(f"variable d'environnement requise absente: {required}")
        environment[required] = original[required]
    environment.update(A4_REPRODUCIBLE_ENVIRONMENT)
    return environment


def _validate_chapter_id(chap: str) -> str:
    if CHAPTER_ID_RE.fullmatch(chap) is None:
        raise ValueError(f"identifiant de chapitre invalide: {chap!r}")
    return chap


def _ensure_real_directory(path: Path, *, label: str) -> Path:
    absolute = Path(os.path.abspath(path))
    try:
        mode = absolute.lstat().st_mode
    except FileNotFoundError:
        absolute.mkdir()
        mode = absolute.lstat().st_mode
    if stat.S_ISLNK(mode):
        raise ValueError(f"répertoire {label} symbolique interdit: {absolute}")
    if not stat.S_ISDIR(mode):
        raise ValueError(f"répertoire {label} non régulier: {absolute}")
    if absolute.resolve(strict=True) != absolute:
        raise ValueError(f"chemin {label} contenant un lien symbolique: {absolute}")
    return absolute


def _safe_build_target(root: Path, *, chap: str) -> Path:
    safe_root = _ensure_real_directory(root, label="ROOT")
    build_root = _ensure_real_directory(safe_root / "build", label="ROOT/build")
    return _ensure_real_directory(build_root / chap, label="build chapitre")


def _create_private_staging(target: Path, *, stem: str) -> Path:
    staging = Path(tempfile.mkdtemp(prefix=f".{stem}.staging-", dir=target))
    if staging.is_symlink() or not staging.is_dir():
        raise ValueError(f"staging privé invalide: {staging}")
    return staging


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_root(root: Path, *, environment: Mapping[str, str]) -> Path:
    completed = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        env=dict(environment),
    )
    return Path(completed.stdout.strip()).resolve(strict=True)


def _tracked_paths(
    git_root: Path, *, environment: Mapping[str, str]
) -> frozenset[str]:
    completed = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=git_root,
        check=True,
        capture_output=True,
        env=dict(environment),
    )
    return frozenset(
        item.decode("utf-8")
        for item in completed.stdout.split(b"\0")
        if item
    )


def _proved_toolchain_roots(
    *, cwd: Path, environment: Mapping[str, str]
) -> dict[str, Path]:
    roots: dict[str, Path] = {}
    for variable in PROVED_TOOLCHAIN_VARIABLES:
        completed = subprocess.run(
            ["kpsewhich", f"-var-value={variable}"],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
            env=dict(environment),
        )
        value = completed.stdout.strip().removeprefix("!!").removesuffix("//")
        if not value or os.pathsep in value or any(token in value for token in "{}$"):
            raise ValueError(f"racine toolchain non canonique pour {variable}: {value!r}")
        root = Path(value).expanduser().resolve(strict=True)
        if not root.is_dir():
            raise ValueError(f"racine toolchain non répertoire pour {variable}: {root}")
        roots[variable] = root
    return roots


def _lexical_absolute(path: Path, *, cwd: Path) -> Path:
    raw = os.fspath(path if path.is_absolute() else cwd / path)
    return Path(os.path.abspath(raw))


def _canonical_tracked_source(
    path: Path,
    *,
    cwd: Path,
    git_root: Path,
    tracked_paths: frozenset[str],
    toolchain_roots: tuple[Path, ...],
) -> tuple[str, Path] | None:
    """Return a canonical tracked repository source, or ``None`` for toolchain.

    A path lexically inside the repository is always treated as a repository
    dependency. It therefore cannot silently become a toolchain dependency by
    being untracked, unreadable or redirected through a symlink.
    """
    candidate = _lexical_absolute(path, cwd=cwd)
    try:
        relative = candidate.relative_to(git_root)
    except ValueError:
        try:
            resolved_external = candidate.resolve(strict=True)
        except (OSError, RuntimeError) as error:
            raise ValueError(f"dépendance externe absente: {candidate}") from error
        if any(
            resolved_external == root or resolved_external.is_relative_to(root)
            for root in toolchain_roots
        ):
            mode = resolved_external.stat().st_mode
            if not stat.S_ISREG(mode) or not os.access(resolved_external, os.R_OK):
                raise ValueError(
                    f"dépendance toolchain illisible ou non régulière: {resolved_external}"
                )
            return None
        raise ValueError(f"dépendance externe non autorisée: {resolved_external}")

    cursor = git_root
    for part in relative.parts:
        cursor /= part
        try:
            mode = cursor.lstat().st_mode
        except FileNotFoundError as error:
            raise ValueError(f"dépendance interne absente: {relative.as_posix()}") from error
        if stat.S_ISLNK(mode):
            raise ValueError(
                f"dépendance interne symbolique interdite: {relative.as_posix()}"
            )

    resolved = candidate.resolve(strict=True)
    try:
        canonical = resolved.relative_to(git_root).as_posix()
    except ValueError as error:
        raise ValueError(
            f"dépendance interne hors racine: {relative.as_posix()}"
        ) from error
    if canonical != relative.as_posix():
        raise ValueError(f"chemin interne non canonique: {relative.as_posix()}")
    if canonical not in tracked_paths:
        raise ValueError(f"dépendance interne non suivie par Git: {canonical}")
    mode = resolved.stat().st_mode
    if not stat.S_ISREG(mode) or not os.access(resolved, os.R_OK):
        raise ValueError(f"dépendance interne illisible ou non régulière: {canonical}")
    return canonical, resolved


def _produced_paths(
    fls_path: Path,
    *,
    cwd: Path,
    staging: Path,
    git_root: Path,
    writable_toolchain_roots: tuple[Path, ...],
) -> frozenset[Path]:
    staging_root = staging.resolve(strict=True)
    outputs: set[Path] = set()
    for line in fls_path.read_text(encoding="utf-8", errors="strict").splitlines():
        if not line.startswith("OUTPUT "):
            continue
        output = _lexical_absolute(Path(line.removeprefix("OUTPUT ")), cwd=cwd)
        if output == staging_root or output.is_relative_to(staging_root):
            outputs.add(output)
            continue
        resolved = output.resolve(strict=False)
        if resolved == git_root or resolved.is_relative_to(git_root):
            raise ValueError(f"OUTPUT .fls non autorisé sous le dépôt: {output}")
        if any(
            resolved == root or resolved.is_relative_to(root)
            for root in writable_toolchain_roots
        ):
            continue
        raise ValueError(f"OUTPUT .fls non autorisé hors staging: {output}")
    return frozenset(outputs)


def merge_source_graphs(*graphs: Mapping[str, str]) -> dict[str, str]:
    """Merge canonical source maps, rejecting contradictory key collisions."""
    merged: dict[str, str] = {}
    for graph in graphs:
        for key, digest in graph.items():
            previous = merged.get(key)
            if previous is not None and previous != digest:
                raise ValueError(f"collision de clé canonique: {key}")
            merged[key] = digest
    return merged


def assert_source_graph_unchanged(
    discovery: Mapping[str, str], final: Mapping[str, str]
) -> None:
    if dict(discovery) != dict(final):
        removed = sorted(set(discovery) - set(final))
        added = sorted(set(final) - set(discovery))
        changed = sorted(
            key
            for key in set(discovery) & set(final)
            if discovery[key] != final[key]
        )
        raise ValueError(
            "graphe source changé entre découverte et compilation finale: "
            f"removed={removed}, added={added}, changed={changed}"
        )


def _recorder_source_graph(
    fls_path: Path,
    *,
    cwd: Path,
    staging: Path,
    master_path: Path,
    git_root: Path,
    tracked_paths: frozenset[str],
    toolchain_roots: tuple[Path, ...],
    writable_toolchain_roots: tuple[Path, ...],
) -> dict[str, str]:
    if not fls_path.is_file():
        raise ValueError(f"recorder LuaLaTeX absent: {fls_path}")
    generated_inputs = set(
        _produced_paths(
            fls_path,
            cwd=cwd,
            staging=staging,
            git_root=git_root,
            writable_toolchain_roots=writable_toolchain_roots,
        )
    )
    generated_inputs.add(_lexical_absolute(master_path, cwd=cwd))
    graph: dict[str, str] = {}
    for line in fls_path.read_text(encoding="utf-8", errors="strict").splitlines():
        if not line.startswith("INPUT "):
            continue
        raw_path = Path(line.removeprefix("INPUT "))
        if _lexical_absolute(raw_path, cwd=cwd) in generated_inputs:
            continue
        canonical = _canonical_tracked_source(
            raw_path,
            cwd=cwd,
            git_root=git_root,
            tracked_paths=tracked_paths,
            toolchain_roots=toolchain_roots,
        )
        if canonical is None:
            continue
        key, source = canonical
        graph = merge_source_graphs(graph, {key: _sha256_path(source)})
    if not graph:
        raise ValueError("graphe recorder interne vide")
    return graph


def _declared_source_graph(
    sources: Iterable[Path],
    *,
    cwd: Path,
    git_root: Path,
    tracked_paths: frozenset[str],
    toolchain_roots: tuple[Path, ...],
) -> dict[str, str]:
    graph: dict[str, str] = {}
    for source in sources:
        canonical = _canonical_tracked_source(
            source,
            cwd=cwd,
            git_root=git_root,
            tracked_paths=tracked_paths,
            toolchain_roots=toolchain_roots,
        )
        if canonical is None:
            raise ValueError(f"autorité déclarée hors racine: {source}")
        key, path = canonical
        graph = merge_source_graphs(graph, {key: _sha256_path(path)})
    return graph


def _documentclass_source(master: str, *, root: Path) -> Path:
    matches = re.findall(
        r"^[ \t]*\\documentclass(?:\[[^]]*\])?\{([^}]+)\}",
        master,
        flags=re.MULTILINE,
    )
    if len(matches) != 1:
        raise ValueError("le master doit déclarer exactement une classe")
    target = Path(matches[0])
    return root / (os.fspath(target) + ("" if target.suffix else ".cls"))


def _require_recorder_authorities(
    recorder_graph: Mapping[str, str],
    *,
    wrapper_key: str,
) -> None:
    keys = set(recorder_graph)
    required_runtime = (wrapper_key, CANONICAL_RENDER_AUTHORITIES[0])
    missing = [key for key in required_runtime if key not in keys]
    if missing:
        raise ValueError(
            "autorité canonique exacte absente du recorder: " + ", ".join(missing)
        )


def _declared_render_authorities(
    *,
    wrapper_key: str,
    git_root: Path,
) -> list[Path]:
    """Return the exact wrapper/class/charter/bridge authority paths."""
    keys = (wrapper_key, *CANONICAL_RENDER_AUTHORITIES)
    missing = [key for key in keys if not (git_root / key).is_file()]
    if missing:
        raise ValueError(
            "autorité canonique exacte absente: " + ", ".join(missing)
        )
    return [git_root / key for key in dict.fromkeys(keys)]


def _inject_trailer_identity(master: str, identity: str) -> str:
    if "\\pdfvariable trailerid" in master:
        raise ValueError("le master sans trailer contient déjà une identité")
    pattern = re.compile(
        r"^[ \t]*\\documentclass(?:\[[^]]*\])?\{[^}]+\}[^\n]*(?:\n|$)",
        flags=re.MULTILINE,
    )
    matches = list(pattern.finditer(master))
    if len(matches) != 1:
        raise ValueError("injection trailer ambiguë: documentclass doit être unique")
    insertion = f"\\pdfvariable trailerid{{[<{identity}> <{identity}>]}}\n"
    end = matches[0].end()
    return master[:end] + insertion + master[end:]


def _compile_lualatex(
    tex_path: Path,
    *,
    build: Path,
    cwd: Path,
    environment: Mapping[str, str],
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "lualatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-recorder",
            f"-output-directory={build}",
            str(tex_path),
        ],
        capture_output=True,
        text=True,
        cwd=cwd,
        errors="replace",
        env=dict(environment),
    )


def _require_regular_nonsymlink(path: Path, *, label: str) -> None:
    try:
        mode = path.lstat().st_mode
    except FileNotFoundError as error:
        raise ValueError(f"{label} absent: {path}") from error
    if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
        raise ValueError(f"{label} non régulier ou symbolique: {path}")


def _publish_staged_artifacts(
    *,
    staging: Path,
    target: Path,
    stem: str,
) -> None:
    mandatory = ("tex", "log", "fls", "pdf")
    optional = ("aux", "toc", "out")
    publication_order = ("tex", "log", "fls", *optional, "pdf")
    staged = {
        suffix: staging / f"{stem}.{suffix}"
        for suffix in publication_order
    }
    destinations = {
        suffix: target / f"{stem}.{suffix}"
        for suffix in publication_order
    }
    for suffix in mandatory:
        path = staged[suffix]
        _require_regular_nonsymlink(path, label=f"artefact staged {suffix}")
    for suffix in optional:
        path = staged[suffix]
        if path.exists() or path.is_symlink():
            _require_regular_nonsymlink(path, label=f"artefact staged {suffix}")

    lock_path = target / f".{stem}.publish.lock"
    lock_flags = os.O_CREAT | os.O_RDWR | getattr(os, "O_NOFOLLOW", 0)
    lock_fd = os.open(lock_path, lock_flags, 0o600)
    with os.fdopen(lock_fd, "a+b") as lock_stream:
        fcntl.flock(lock_stream.fileno(), fcntl.LOCK_EX)
        for suffix, path in destinations.items():
            try:
                mode = path.lstat().st_mode
            except FileNotFoundError:
                continue
            if stat.S_ISLNK(mode) or not stat.S_ISREG(mode):
                raise ValueError(
                    f"destination canonique {suffix} invalide: {path}"
                )
        backup = Path(
            tempfile.mkdtemp(prefix=f".{stem}.backup-", dir=target)
        )
        if backup.is_symlink() or not backup.is_dir():
            raise ValueError(f"backup transactionnel invalide: {backup}")
        originally_present = frozenset(
            suffix for suffix, destination in destinations.items()
            if destination.exists()
        )
        backups = {
            suffix: backup / destinations[suffix].name
            for suffix in originally_present
        }

        # Phase backup entièrement terminée avant la première mutation d'une
        # destination canonique. Une copie partielle n'est jamais un rollback.
        try:
            for suffix in publication_order:
                if suffix in originally_present:
                    shutil.copy2(destinations[suffix], backups[suffix])
            for suffix in originally_present:
                _require_regular_nonsymlink(
                    backups[suffix], label=f"backup transactionnel {suffix}"
                )
        except Exception:
            try:
                shutil.rmtree(backup)
            except OSError:
                pass
            raise

        try:
            # Le recorder final précède le PDF, artefact de release publié en
            # dernier. Les optionnels absents sont supprimés sous le verrou.
            for suffix in publication_order:
                source = staged[suffix]
                destination = destinations[suffix]
                if source.exists():
                    os.replace(source, destination)
                else:
                    destination.unlink(missing_ok=True)
            # Le cleanup staged fait partie de la transaction : tant qu'il
            # n'est pas réussi, les backups externes permettent le rollback.
            shutil.rmtree(staging)
        except Exception:
            missing_backups = [
                suffix for suffix in originally_present
                if not backups[suffix].is_file() or backups[suffix].is_symlink()
            ]
            if missing_backups:
                raise RuntimeError(
                    "rollback impossible, backups absents ou invalides: "
                    + ", ".join(sorted(missing_backups))
                )
            for suffix in reversed(publication_order):
                destination = destinations[suffix]
                if suffix in originally_present:
                    os.replace(backups[suffix], destination)
                else:
                    destination.unlink(missing_ok=True)
            try:
                shutil.rmtree(backup)
            except OSError:
                pass
            raise

        # La publication devient canonique après publication complète et
        # nettoyage du staging. Le backup n'est dès lors qu'une quarantaine :
        # son cleanup ne doit pas invalider ni restaurer le nouvel état.
        try:
            shutil.rmtree(backup)
        except OSError as error:
            print(
                "AVERTISSEMENT: publication canonique validée; "
                f"backup transactionnel conservé: {backup}: {error}",
                file=sys.stderr,
            )


def collect(chap_dir: Path, variant: str) -> list[Path]:
    if variant == "methodes":
        return sorted((chap_dir / "methodes").glob("*.tex"))
    if variant == "remediation":
        return sorted((chap_dir / "remediation").glob("*.tex"))
    files = []
    for sub, pat in ORDER:
        candidats = sorted((chap_dir / sub).glob(f"{pat}.tex" if not pat.endswith("*") else pat + ".tex"))
        if sub == "exercices":
            files += [f for f in candidats if not f.name.endswith("-CDP.tex")]
            files += [f for f in candidats if f.name.endswith("-CDP.tex")]
        else:
            files += candidats
    # dédoublonner en conservant l'ordre
    seen, out = set(), []
    for f in files:
        if f not in seen:
            seen.add(f)
            out.append(f)
    return out


def _configure_chapter_toc(master: str, *, variant: str) -> str:
    """Keep the chapter TOC only for variants that provide its entries."""
    if variant not in CLI_VARIANTS:
        raise ValueError(f"variante chapitre invalide: {variant}")
    if variant in CHAPTER_TOC_VARIANTS:
        return master
    return master.replace(CHAPTER_TOC_BLOCK, "", 1)


def ouverture_depuis_contrat(chap_dir: Path) -> str:
    """Construit l'ouverture normalisée à partir du contrat du chapitre."""
    contrat = yaml.safe_load((chap_dir / "contrat.yaml").read_text(encoding="utf-8"))
    capacites = "\n".join(
        f"\\item \\textbf{{{capacite['code']}}} — {capacite['libelle_eleve']}"
        for capacite in contrat["capacites"]
    )
    temps = contrat.get("temps_estime_h", {})
    temps_tex = (
        f"\\parcoursUn~{temps.get('parcours1', '—')} h \\quad "
        f"\\parcoursDeux~{temps.get('parcours2', '—')} h \\quad "
        f"\\parcoursTrois~{temps.get('parcours3', '—')} h"
    )
    accroche = contrat.get("situation_accroche", "Situation d'accroche à découvrir dans le TD fil rouge.")
    return (
        f"\\ouverturechapitre{{{contrat['titre']}}}{{\\begin{{itemize}}\n{capacites}\n\\end{{itemize}}}}"
        f"{{{accroche}}}{{{temps_tex}}}\n\\clearpage"
    )


NIVEAU_LABELS = {
    "1SPE": "Première spécialité",
    "TSPE": "Terminale spécialité",
    "TCOMPL": "Terminale — Mathématiques complémentaires",
    "TEXPERTES": "Terminale — Mathématiques expertes",
}


def niveau_depuis_contrat(chap_dir: Path) -> str:
    contrat = yaml.safe_load((chap_dir / "contrat.yaml").read_text(encoding="utf-8"))
    code = contrat.get("niveau", "")
    return NIVEAU_LABELS.get(code, code or "Première spécialité")


def _build_chapter(chap: str, variant: str) -> Path:
    _validate_chapter_id(chap)
    environment = sealed_build_environment()
    chap_dir = ROOT / "chapitres" / chap
    target = _safe_build_target(ROOT, chap=chap)
    files = collect(chap_dir, variant)
    if not files:
        raise ValueError("aucun objet à assembler")
    inputs = "\n".join(f"\\input{{{f.relative_to(ROOT)}}}" for f in files)
    ouverture = ouverture_depuis_contrat(chap_dir) if variant == "complet" else ""
    niveau = niveau_depuis_contrat(chap_dir)
    template_path = ROOT / "gabarits" / "chapitre_master.tex"
    contract_path = chap_dir / "contrat.yaml"
    master = template_path.read_text(encoding="utf-8")
    master = _configure_chapter_toc(master, variant=variant)
    master = (master.replace("%%CONTENT%%", inputs)
                    .replace("%%OPENING%%", ouverture)
                    .replace("%%NIVEAU%%", niveau)
                    .replace("%%CHAP%%", chap))
    stem = f"{chap}_{variant}"
    git_root = _git_root(ROOT, environment=environment)
    tracked_paths = _tracked_paths(git_root, environment=environment)
    toolchain = _proved_toolchain_roots(cwd=ROOT, environment=environment)
    toolchain_roots = tuple(dict.fromkeys(toolchain.values()))
    writable_toolchain_roots = tuple(
        dict.fromkeys(
            (toolchain["TEXMFVAR"], toolchain["TEXMFSYSVAR"])
        )
    )
    wrapper = _documentclass_source(master, root=ROOT)
    wrapper_source = _canonical_tracked_source(
        wrapper,
        cwd=ROOT,
        git_root=git_root,
        tracked_paths=tracked_paths,
        toolchain_roots=toolchain_roots,
    )
    if wrapper_source is None:
        raise ValueError(f"wrapper hors racine: {wrapper}")

    staging = _create_private_staging(target, stem=stem)
    try:
        tex_path = staging / f"{stem}.tex"
        tex_path.write_text(master, encoding="utf-8")
        # Passe de découverte jetable : son PDF ne porte aucune autorité.
        proc = _compile_lualatex(
            tex_path,
            build=staging,
            cwd=ROOT,
            environment=environment,
        )
        if proc.returncode != 0:
            diagnostic = (proc.stderr or proc.stdout).strip().splitlines()
            detail = diagnostic[-1] if diagnostic else "sans diagnostic"
            raise ValueError(f"LuaLaTeX découverte rc={proc.returncode}: {detail}")
        pdf_path = staging / f"{stem}.pdf"
        pdf_path.unlink(missing_ok=True)
        fls_path = staging / f"{stem}.fls"
        recorder_discovery = _recorder_source_graph(
            fls_path,
            cwd=ROOT,
            staging=staging,
            master_path=tex_path,
            git_root=git_root,
            tracked_paths=tracked_paths,
            toolchain_roots=toolchain_roots,
            writable_toolchain_roots=writable_toolchain_roots,
        )
        _require_recorder_authorities(
            recorder_discovery,
            wrapper_key=wrapper_source[0],
        )
        render_authorities = _declared_render_authorities(
            wrapper_key=wrapper_source[0],
            git_root=git_root,
        )
        declared = _declared_source_graph(
            [template_path, contract_path, *files, *render_authorities],
            cwd=ROOT,
            git_root=git_root,
            tracked_paths=tracked_paths,
            toolchain_roots=toolchain_roots,
        )
        source_graph = merge_source_graphs(recorder_discovery, declared)
        trailer_identity = pdf_trailer_identity(
            manual=f"chapter:{chap}",
            variant=variant,
            body=master,
            sources=source_graph,
        )
        tex_path.write_text(
            _inject_trailer_identity(master, trailer_identity),
            encoding="utf-8",
        )

        for _ in range(2):
            proc = _compile_lualatex(
                tex_path,
                build=staging,
                cwd=ROOT,
                environment=environment,
            )
            if proc.returncode != 0:
                diagnostic = (proc.stderr or proc.stdout).strip().splitlines()
                detail = diagnostic[-1] if diagnostic else "sans diagnostic"
                raise ValueError(f"LuaLaTeX final rc={proc.returncode}: {detail}")
        recorder_final = _recorder_source_graph(
            fls_path,
            cwd=ROOT,
            staging=staging,
            master_path=tex_path,
            git_root=git_root,
            tracked_paths=tracked_paths,
            toolchain_roots=toolchain_roots,
            writable_toolchain_roots=writable_toolchain_roots,
        )
        _require_recorder_authorities(
            recorder_final,
            wrapper_key=wrapper_source[0],
        )
        # Comparer le recorder brut AVANT l'union des autorités déclarées.
        assert_source_graph_unchanged(recorder_discovery, recorder_final)
        declared_final = _declared_source_graph(
            [template_path, contract_path, *files, *render_authorities],
            cwd=ROOT,
            git_root=git_root,
            tracked_paths=tracked_paths,
            toolchain_roots=toolchain_roots,
        )
        final_graph = merge_source_graphs(recorder_final, declared_final)
        assert_source_graph_unchanged(source_graph, final_graph)
        log_path = staging / f"{stem}.log"
        if verify_pdf(pdf_path, log_path):
            raise ValueError("préflight PDF staged en échec")
        _publish_staged_artifacts(staging=staging, target=target, stem=stem)
        return target / f"{stem}.pdf"
    finally:
        if staging.exists():
            shutil.rmtree(staging)


def main(chap: str, variant: str) -> int:
    if variant not in CLI_VARIANTS:
        print(f"Variante chapitre invalide: {variant}", file=sys.stderr)
        return 2
    try:
        pdf_path = _build_chapter(chap, variant)
    except (ValueError, OSError, subprocess.SubprocessError, yaml.YAMLError) as error:
        print(f"Erreur assemblage chapitre: {error}", file=sys.stderr)
        return 1
    print(f"PDF : {pdf_path}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--chap", required=True)
    ap.add_argument("--variant", default="complet",
                    choices=["complet", "methodes", "parcours1", "remediation"])
    args = ap.parse_args()
    sys.exit(main(args.chap, args.variant))
