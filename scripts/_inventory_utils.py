#!/usr/bin/env python3
"""Utilitaires partagés pour l’inventaire, la couverture et les contrôles qualité."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional
import csv
import hashlib
import re
import sys
import unicodedata
import yaml

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]

IGNORED_DIRS = {
    '.git',
    '.venv',
    '__pycache__',
    '.idea',
    '.vscode',
    '.pytest_cache',
    '.mypy_cache',
    '.ruff_cache',
    'node_modules',
    '.ipynb_checkpoints',
    'build',
    'dist',
    '01_build_reports',
    'AUDIT',
    'scrapping_NSI',
    'Documents_DRIVE',
    'nsi-enseignement',
}

IGNORED_SUFFIXES = {
    '.pyc',
    '.pyo',
    '.aux',
    '.log',
    '.out',
    '.toc',
    '.bbl',
    '.blg',
    '.synctex.gz',
    '.fdb_latexmk',
    '.fls',
    '.tmp',
    '.DS_Store',
    '.pdf',  # non-reproducible binary artifacts (pdflatex timestamps)
}

STATUT_ALLOWED = {
    'draft',
    'needs_content',
    'needs_review',
    'validated_pedagogy',
    'validated_science',
    'validated_technical',
    'published',
    'archived',
    'deprecated',
}

SOURCE_TYPE_DRIVE = 'drive'
SOURCE_TYPE_GENERATED = 'generated'

# Correspondance des statuts connus vers la grammaire autorisée.
# Les anciens statuts vagues n'y sont plus associés.
STATUS_NORMALIZATION = {
    'draft': 'draft',
    'needs_content': 'needs_content',
    'needs_review': 'needs_review',
    'validated_pedagogy': 'validated_pedagogy',
    'validated_science': 'validated_science',
    'validated_technical': 'validated_technical',
    'published': 'published',
    'archived': 'archived',
    'deprecated': 'deprecated',
}

SEQUENCE_DOCS = {
    'cours_eleve',
    'trace_ecrite',
    'td',
    'tp',
    'fiche_methode',
    'aides_progressives',
    'corrige',
    'guide_professeur',
    'evaluation',
    'projet_associe',
    'qcm',
}

SEQUENCE_NAME_ALIASES = {
    'cours_eleve': 'eleve',
    'trace_ecrite': 'eleve',
    'td': 'eleve',
    'tp': 'eleve',
    'fiche_methode': 'eleve',
    'aides_progressives': 'eleve',
    'corrige': 'corrige',
    'guide_professeur': 'professeur',
    'evaluation': 'eleve',
    'projet_associe': 'eleve',
    'qcm': 'eleve',
}

REQUIRED_METADATA_KEYS = (
    'statut',
    'niveau',
    'source',
)

PROGRAM_STEPS = ('couverture', 'cours', 'exercise', 'tp', 'evaluation')


def _normalize_for_status(raw: str) -> str:
    value = (raw or '').strip().lower()
    value = unicodedata.normalize('NFKD', value)
    value = ''.join(ch for ch in value if not unicodedata.combining(ch))
    value = value.replace('\u2011', '-')
    value = re.sub(r'\s+', ' ', value).strip()
    return value


def normalize_status(value: str) -> str:
    normalized = _normalize_for_status(value)
    if normalized in STATUS_NORMALIZATION:
        return STATUS_NORMALIZATION[normalized]
    if normalized in STATUT_ALLOWED:
        return normalized
    return 'needs_review'


def file_id_stem(path: Path) -> str:
    return path.stem.replace(' ', '_')


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1 << 16), b''):
            h.update(block)
    return h.hexdigest()


def parse_frontmatter(path: Path) -> Dict[str, Any]:
    """Parse le bloc YAML frontmatter (```--- ... ---```) d’un document."""
    try:
        text = path.read_text(encoding='utf-8', errors='replace')
    except Exception:
        return {}

    if not text.startswith('---'):
        return {}

    match = re.search(r'^---\s*\n(.*?)\n---\s*', text, re.S)
    if not match:
        return {}

    block = match.group(1).strip()
    if not block:
        return {}

    try:
        loaded = yaml.safe_load(block)
    except Exception:
        loaded = None

    if isinstance(loaded, dict):
        return {str(k): v for k, v in loaded.items()}

    # fallback minimal manuel, tolérant
    data: Dict[str, Any] = {}
    current_key: Optional[str] = None
    for raw in block.splitlines():
        line = raw.strip()
        if not line or line.startswith('#'):
            continue
        if line.startswith('- ') and current_key:
            prev = data.get(current_key)
            if isinstance(prev, list):
                prev.append(line[2:].strip())
            continue
        if ':' not in line:
            continue
        key, value = line.split(':', 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        if not value:
            data[key] = []
            continue
        if value.startswith('[') and value.endswith(']'):
            inner = value[1:-1].strip()
            if not inner:
                data[key] = []
            else:
                data[key] = [item.strip().strip('\"\'') for item in inner.split(',')]
        else:
            data[key] = value.strip().strip('\"')
    return data


def detect_level(path: Path) -> str:
    parts = path.parts
    if 'premiere' in parts:
        return 'premiere'
    if 'terminale' in parts:
        return 'terminale'
    if 'AGENTS.md' == path.name or 'SKILLS.md' == path.name:
        return 'interne'
    return 'interne'


def detect_sequence_id(path: Path, frontmatter: Dict[str, Any]) -> str:
    candidate = (frontmatter.get('sequence') or frontmatter.get('sequence_id') or '').strip() if frontmatter else ''
    if isinstance(candidate, list):
        candidate = candidate[0] if candidate else ''
    if candidate:
        return str(candidate)
    candidate = (frontmatter.get('id') or '')
    if isinstance(candidate, str):
        if candidate.startswith('S'):
            return candidate
    match = re.search(r'(s\d{2,3}_[a-z0-9_]+)', path.as_posix())
    if match:
        return match.group(1)
    return 'NA'


def extract_theme_and_notion(path: Path, frontmatter: Dict[str, Any]) -> tuple[str, str]:
    def _s(v: object) -> str:
        if isinstance(v, list):
            return ', '.join(str(x) for x in v)
        if v is None:
            return ''
        return str(v)

    theme = _s(frontmatter.get('theme') if frontmatter else '')
    notion = _s(frontmatter.get('notion') if frontmatter else '')
    if not theme:
        if 's01_representation_donnees' in path.as_posix():
            theme = 'Représentation des données'
        elif 's01_structures_donnees_interfaces_implementations' in path.as_posix():
            theme = 'Structures de données'
    return theme.strip(), notion.strip()


def classify_resource_type(path: Path) -> str:
    path_str = path.as_posix()
    if 'premiere/sequences' in path_str or 'terminale/sequences' in path_str:
        return 'sequence'
    if '/banques/' in path_str:
        return 'banque'
    if 'scripts' in path_str:
        return 'script'
    if path.suffix == '.py':
        if 'tests' in path.parts:
            return 'test'
        return 'python'
    if path.suffix in {'.md', '.tex', '.json', '.yml', '.yaml', '.csv', '.txt'}:
        return 'document'
    return 'document'


def resource_audience(path: Path, frontmatter: Dict[str, Any]) -> str:
    document_type = frontmatter.get('document_type') or frontmatter.get('type')
    if isinstance(document_type, str):
        lowered = document_type.lower().replace('_', ' ').replace('-', ' ').strip()
        if 'guide' in lowered and 'prof' in lowered:
            return 'professeur'
        if 'corrige' in lowered:
            return 'corrige'
        if 'qcm' in lowered:
            return 'eleve'
        if lowered in SEQUENCE_DOCS:
            return SEQUENCE_NAME_ALIASES.get(lowered.replace(' ', '_'), 'eleve')

    stem = path.stem.lower()
    if stem.startswith('guide_professeur'):
        return 'professeur'
    if 'guide_prof' in stem:
        return 'professeur'
    if 'corrige' in stem:
        return 'corrige'
    for token in SEQUENCE_DOCS:
        if stem == token or stem.startswith(token + '.'):
            return SEQUENCE_NAME_ALIASES.get(token, 'eleve')
    return 'mixte'


def is_pedagogical(path: Path) -> bool:
    return path.suffix in {'.md', '.tex', '.json'} and (
        'sequences' in path.parts or 'banques' in path.parts
        or 'progressions' in path.parts
        or 'modeles_documents' in path.parts
        or 'charte_graphique_et_pedagogique' in path.parts
    )


def is_publishable(path: Path) -> bool:
    if path.suffix not in {'.md', '.json'}:
        return False
    if any(token in path.parts for token in {'tests', 'scripts', '.venv', '01_build_reports'}):
        return False
    if path.name in {'AGENTS.md', 'SKILLS.md', 'quality_audit_s01.md'}:
        return False
    return True


DRIVE_SOURCE_KEYWORDS = ('drive.google', 'docs.google')


def _drive_quarantine_paths() -> set[str]:
    manifest = ROOT / 'drive_quarantine_manifest.csv'
    if not manifest.exists():
        return set()
    paths: set[str] = set()
    try:
        with manifest.open(encoding='utf-8', newline='') as handle:
            reader = csv.DictReader(handle)
            for row in reader:
                local = str(row.get('local_copy') or '').strip()
                digest = str(row.get('sha256') or '').strip()
                if local and len(digest) == 64:
                    paths.add(local)
    except Exception:
        return set()
    return paths


def detect_source_type(path: Path, frontmatter: Dict[str, Any] | None = None) -> str:
    relative = path.relative_to(ROOT).as_posix() if path.is_absolute() and ROOT in path.parents else path.as_posix()
    if isinstance(frontmatter, dict):
        origin = str(frontmatter.get('origin') or '').lower().strip()
        drive_url = str(frontmatter.get('drive_url') or '').lower().strip()
        if origin == 'drive' and any(keyword in drive_url for keyword in DRIVE_SOURCE_KEYWORDS):
            return SOURCE_TYPE_DRIVE
    if relative in _drive_quarantine_paths():
        return SOURCE_TYPE_DRIVE
    return SOURCE_TYPE_GENERATED


def evidence_category(path: Path, frontmatter: Dict[str, Any] | None = None) -> Optional[str]:
    n = path.name.lower()
    doc_type = (frontmatter or {}).get('document_type')
    if isinstance(doc_type, str):
        dt = _normalize_for_status(doc_type)
        if dt.startswith('cours'):
            return 'cours'
        if dt == 'trace':
            return 'trace'
        if dt in {'td', 'evaluation', 'evaluation'}:
            return 'td' if dt == 'td' else 'evaluation'
        if dt == 'tp':
            return 'tp'
        if 'corrige' in dt:
            return 'corrige'

    if 'evaluation' == n.replace('.md', ''):
        return 'evaluation'
    if n == 'td.md' or 'td' in n or '/banques/exercices/' in path.as_posix():
        return 'td'
    if '/projets/' in path.as_posix() or 'projet' in n:
        return 'exercise'
    if '/banques/tp/' in path.as_posix():
        return 'tp'
    if '/terminale/banques' in path.as_posix() or '/premiere/banques' in path.as_posix():
        # les fichiers de banques sont des ressources de pratique uniquement si typés explicitement en td/tp/cours
        if 'cours_eleve' in n or 'tp' in n:
            return 'tp'
    if n in {'cours_eleve.md', 'trace_ecrite.md'}:
        return 'trace' if n == 'trace_ecrite.md' else 'cours'
    if n == 'corrige.md' or 'corrige' in n:
        return 'corrige'
    if n in {'aides_progressives.md'}:
        return 'exercise'
    if 'qcm' in n:
        return 'autre'
    return None


def has_placeholder(text: str) -> bool:
    placeholders = [
        r'TODO',
        r'\bTBD\b',
        r'À\s*COMPLETER',
        r'A\s*COMPLETER',
        r'\bXXX\b',
        r'FIXME',
    ]
    pattern = re.compile('|'.join(placeholders), re.IGNORECASE)
    return bool(pattern.search(text))


def has_private_data(text: str) -> List[str]:
    patterns = {
        'email': re.compile(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}'),
        'phone': re.compile(r'\+?\d[\d\s().-]{7,}\d'),
    }
    hits: List[str] = []
    for name, reg in patterns.items():
        if reg.search(text):
            hits.append(name)
    return hits


def iter_files(root: Path) -> Iterable[Path]:
    """Enumerate files via git ls-files for CI reproducibility, rglob fallback."""
    import subprocess
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=str(root), capture_output=True, text=True,
    )
    if result.returncode == 0 and result.stdout:
        candidates = sorted(root / rel for rel in result.stdout.split("\0") if rel)
    else:
        candidates = sorted(root.rglob('*'))
    for path in candidates:
        if path.is_dir():
            continue
        if path.name in {
            'manifest.csv', 'manifest_tooling.csv',
            'inventory_report.md', 'duplicates_report.md',
            'coverage.md', 'coverage_sources.md',
            'privacy_report.md', 'quality_checklist.md',
        }:
            continue
        if path.name.startswith('.env') and path.name != '.env.rag.example':
            continue
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.suffix in IGNORED_SUFFIXES:
            continue
        if path.suffix == '' and path.name not in {'SKILLS.md', 'AGENTS.md', 'README.md'}:
            continue
        yield path


def split_keywords(text: str) -> List[str]:
    tokens = re.findall(r"[A-Za-zÀ-ÿ0-9']+", text.lower())
    stop = {
        'de', 'la', 'le', 'les', 'des', 'du', 'un', 'une', 'et', 'ou', 'à', 'au', 'aux', 'en',
        'dans', 'pour', 'avec', 'sur', 'par', 'qui', 'quoi', 'que', 'd', 'est', 'sont', 'etre', 'être',
        'au', 'on', 'nous', 'vous', 'ils', 'elles', 'que', 'l', 'ces', 'cet', 'cette', 'son', 'sa',
    }
    return sorted({t for t in tokens if len(t) >= 4 and t not in stop})
