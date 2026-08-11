#!/usr/bin/env python3
"""Vérificateur d'ancres et de citations pour les verdicts du juge de substance.

Rôle : garde-fou MÉCANIQUE. Il ne juge jamais le sens d'une preuve — c'est le
travail du juge LLM. Il constate des faits vérifiables et a un droit de veto :

  1. le verdict est-il conforme au schéma JSON ?
  2. l'`official_label` concorde-t-il avec programme_nsi_2019.yaml ?
  3. chaque preuve déclarée `present` pointe-t-elle un fichier qui existe ?
  4. l'`anchor` correspond-elle à une section réelle (slug recalculé) ?
  5. la `quote` apparaît-elle littéralement DANS cette section ?
  6. la cohérence logique tient-elle (validated_pedagogy => 3 preuves vérifiées
     ET teaches=true ET aucun scientific_flag) ?

POUVOIR : le vérificateur ne PROMEUT jamais un verdict. Il peut le DÉGRADER :
si le juge a écrit validated_pedagogy mais qu'une preuve est invérifiable, le
verdict effectif retombe à needs_content (ou BLOCKER) et le détail est rapporté.

Sortie : rapport lisible + code retour 0 (aucun verdict dégradé) / 1 (dégradations)
/ 2 (erreur de schéma ou d'entrée). Pensé pour une cible Makefile / CI.

Usage :
    python check_substance_anchors.py VERDICT.json --repo-root /chemin/depot
    python check_substance_anchors.py VERDICT.json --repo-root . --json rapport.json

Dépendances : jsonschema (optionnel ; si absent, validation de schéma sautée
avec avertissement). Aucune autre dépendance externe.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import unicodedata
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

# --- slugifieur (dupliqué ici pour faire du script un fichier autonome) -------

def github_slug(title: str) -> str:
    s = unicodedata.normalize("NFC", title).strip().lower().replace("`", "")
    kept = [ch for ch in s if ch.isalnum() or ch in (" ", "-", "_")]
    return "".join(kept).replace(" ", "-")


HEADER_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FRONTMATTER_RE = re.compile(r"^---\s*$")


def split_frontmatter(text: str) -> str:
    """Retire un éventuel frontmatter YAML en tête pour ne pas slugifier
    des lignes qui ne sont pas des titres."""
    lines = text.splitlines()
    if lines and FRONTMATTER_RE.match(lines[0]):
        for i in range(1, len(lines)):
            if FRONTMATTER_RE.match(lines[i]):
                return "\n".join(lines[i + 1 :])
    return text


@dataclass
class Section:
    title: str
    slug: str
    level: int
    body: str  # texte de la section, du titre jusqu'au prochain titre de niveau <=


def parse_sections(md_text: str) -> dict[str, Section]:
    """Renvoie {slug -> Section}, doublons désambiguïsés à la GitHub.

    On ignore les titres situés à l'intérieur de blocs de code ```...```.
    """
    text = split_frontmatter(md_text)
    lines = text.splitlines()
    headers: list[tuple[int, int, str]] = []  # (line_idx, level, title)
    in_code = False
    for idx, line in enumerate(lines):
        if line.lstrip().startswith("```"):
            in_code = not in_code
            continue
        if in_code:
            continue
        m = HEADER_RE.match(line)
        if m:
            headers.append((idx, len(m.group(1)), m.group(2)))

    counts: dict[str, int] = {}
    sections: dict[str, Section] = {}
    for h_pos, (line_idx, level, title) in enumerate(headers):
        base = github_slug(title)
        n = counts.get(base, 0)
        slug = base if n == 0 else f"{base}-{n}"
        counts[base] = n + 1
        # corps : du titre jusqu'au prochain header de niveau <= au sien, de
        # sorte qu'une section englobe ses sous-sections (une citation placée
        # dans « ### Exercice 1 » compte comme preuve sous « ## Exercices »).
        end = len(lines)
        for nxt_idx, nxt_level, _ in headers[h_pos + 1:]:
            if nxt_level <= level:
                end = nxt_idx
                break
        body = "\n".join(lines[line_idx:end])
        sections[slug] = Section(title=title, slug=slug, level=level, body=body)
    return sections


# --- normalisation pour la comparaison de citations --------------------------

def normalize(s: str) -> str:
    """Normalise pour comparer une citation à un corps de section sans être
    piégé par la typographie (apostrophes, guillemets, espaces, NBSP)."""
    s = unicodedata.normalize("NFC", s)
    trans = {
        "\u2019": "'", "\u2018": "'", "\u02bc": "'",
        "\u00ab": '"', "\u00bb": '"', "\u201c": '"', "\u201d": '"',
        "\u00a0": " ", "\u202f": " ", "\u2009": " ",
        "\u2013": "-", "\u2014": "-",
    }
    s = "".join(trans.get(ch, ch) for ch in s)
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def normalize_for_match(s: str) -> str:
    """Normalisation typographique canonique pour la comparaison de citations.

    Appliquée aux DEUX côtés (citation ET corps de section). Transforme les
    variantes typographiques en forme canonique SANS altérer le contenu :
      - NFC Unicode
      - Apostrophes courbes/modificatrices/prime → apostrophe droite '
      - Guillemets « » " " → guillemet droit "
      - Tirets demi-cadratin/cadratin → tiret simple -
      - Espaces insécables/fines/quart → espace simple
      - Collapse d'espaces HORIZONTAUX multiples en un seul
      - Sauts de ligne PRÉSERVÉS (structure du document = contenu)

    Le strip de ** (gras Markdown) et la concaténation de lignes restent
    INTERDITS : le formatage Markdown est du contenu, pas de la typographie.

    Équivalence typographique = classe d'identité ; formatage Markdown = contenu.
    """
    s = unicodedata.normalize("NFC", s)
    trans = {
        "\u2019": "'", "\u2018": "'", "\u02bc": "'", "\u2032": "'",  # apostrophes
        "\u00ab": '"', "\u00bb": '"', "\u201c": '"', "\u201d": '"',  # guillemets
        "\u00a0": " ", "\u202f": " ", "\u2009": " ", "\u2005": " ",  # espaces
        "\u2013": "-", "\u2014": "-",                                # tirets
    }
    s = "".join(trans.get(ch, ch) for ch in s)
    # Collapse horizontal whitespace only — newlines preserved
    s = re.sub(r"[^\S\n]+", " ", s)
    # Strip leading/trailing space per line, then strip overall
    s = "\n".join(line.strip() for line in s.split("\n"))
    s = s.strip()
    return s


def citation_status(quote: str, body: str) -> tuple[str, float]:
    """Renvoie ('exact'|'normalized'|'absent', recouvrement[0..1]).

    Matching mécanique :
      1. sous-chaîne exacte (byte-identical) → 'exact'
      2. sous-chaîne après normalisation typographique (normalize_for_match
         sur les DEUX côtés) → 'normalized'
      3. sinon → 'absent'

    La casse est conservée (pas de lower-case). Le gras ** n'est pas strippé.
    """
    if quote in body:
        return "exact", 1.0
    nq, nb = normalize_for_match(quote), normalize_for_match(body)
    if nq and nq in nb:
        return "normalized", 1.0
    return "absent", 0.0


# --- chargement du programme officiel ----------------------------------------

def load_official_labels(repo_root: Path) -> dict[str, str]:
    """Mappe capacity_id -> intitulé officiel concaténé, depuis le YAML.

    Parsing tolérant sans dépendance PyYAML : on lit les blocs `- id:` et la
    liste `capacite_attendue:` qui suit. Suffisant pour la comparaison.
    """
    path = repo_root / "00_programmes_officiels" / "programme_nsi_2019.yaml"
    labels: dict[str, str] = {}
    if not path.exists():
        return labels
    cur_id = None
    grabbing = False
    buff: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        m_id = re.match(r"\s*-?\s*id:\s*(\S+)", raw)
        if m_id:
            if cur_id and buff:
                labels[cur_id] = " ".join(buff).strip()
            cur_id = m_id.group(1).strip().strip('"').strip("'")
            buff, grabbing = [], False
            continue
        if re.match(r"\s*capacite_attendue:\s*$", raw):
            grabbing = True
            continue
        if grabbing:
            m_item = re.match(r"\s*-\s+(.*\S)\s*$", raw)
            if m_item:
                buff.append(m_item.group(1).strip().strip('"').strip("'"))
            elif raw.strip() and not raw.startswith(" "):
                grabbing = False
    if cur_id and buff:
        labels[cur_id] = " ".join(buff).strip()
    return labels


# --- vérification d'une preuve -----------------------------------------------

@dataclass
class ProofCheck:
    role: str
    present: bool
    teaches: bool
    file_ok: bool = True
    anchor_ok: bool = True
    quote_ok: bool = True
    quote_method: str = ""
    messages: list[str] = field(default_factory=list)

    @property
    def verified(self) -> bool:
        """Une preuve est vérifiée si elle est présente et que les trois
        contrôles mécaniques passent. (teaches relève du juge, pas du
        vérificateur, mais il est exigé pour la promotion.)"""
        if not self.present:
            return False
        return self.file_ok and self.anchor_ok and self.quote_ok


CAP_ID_RE = re.compile(r"\b[PT]-[A-Z]+-\d+[A-Z]?\b")


def check_proof(role: str, ev: dict[str, Any], repo_root: Path,
                section_cache: dict[Path, dict[str, Section]],
                cap_id: str = "") -> ProofCheck:
    pc = ProofCheck(role=role, present=bool(ev.get("present")),
                    teaches=bool(ev.get("teaches")))
    if not pc.present:
        return pc

    file_rel = ev.get("file")
    anchor = str(ev.get("anchor") or "")
    quote = str(ev.get("quote") or "")

    if not isinstance(file_rel, str) or not file_rel:
        pc.file_ok = False
        pc.messages.append("present=true mais file manquant")
        return pc
    fpath = (repo_root / file_rel).resolve()

    # K2-TER-2: proof_correction must cite a corrige/bareme file or anchor
    # Convention: corpus uses both dedicated corrige files (P10) and
    # embedded corriges in TD files with #corrigé-exercice-N anchors (P07)
    if role == "correction" and pc.present:
        fname_lower = fpath.name.lower()
        anchor_lower = anchor.lower()
        is_corrige_file = "corrige" in fname_lower or "bareme" in fname_lower
        is_corrige_anchor = (anchor_lower.startswith("#corrigé-")
                             or anchor_lower.startswith("#corrige-")
                             or anchor_lower.startswith("#barème-")
                             or anchor_lower.startswith("#bareme-"))
        if not is_corrige_file and not is_corrige_anchor:
            pc.file_ok = False
            pc.messages.append(
                f"proof_correction cite {fpath.name} (ancre {anchor}) — "
                f"attendu : fichier corrige/bareme ou ancre #corrigé-*/#barème-*")
            return pc

    if not fpath.exists():
        pc.file_ok = False
        pc.messages.append(f"fichier introuvable : {file_rel}")
        return pc

    if fpath not in section_cache:
        section_cache[fpath] = parse_sections(fpath.read_text(encoding="utf-8"))
    sections = section_cache[fpath]

    slug = anchor.lstrip("#")
    section = sections.get(slug)
    if section is None:
        pc.anchor_ok = pc.quote_ok = False
        near = ", ".join(sorted(sections)[:6])
        pc.messages.append(
            f"ancre absente : {anchor} (ancres existantes p.ex. : {near})")
        return pc

    status, overlap = citation_status(quote, section.body)
    pc.quote_method = status
    if status == "absent":
        pc.quote_ok = False
        pc.messages.append(
            f"citation introuvable sous {anchor} "
            f"(recouvrement tokens {overlap:.0%}) — possible hallucination")
    elif status == "fuzzy":
        pc.messages.append(
            f"citation approximative sous {anchor} "
            f"(recouvrement {overlap:.0%}) — à resserrer")

    # K2-TER-1: cross-ID guard — quote must not cite a different capacity
    # unless that ID is a co-tag of the same file (legitimate co-occurrence)
    if cap_id and pc.quote_ok:
        # Read co-tags from YAML frontmatter (lightweight, no _qa_common dep)
        co_tags: set[str] = set()
        try:
            raw_text = fpath.read_text(encoding="utf-8", errors="replace")
            if raw_text.startswith("---"):
                end = raw_text.find("\n---", 3)
                if end > 0:
                    fm_text = raw_text[3:end]
                    for fm_id in CAP_ID_RE.findall(fm_text):
                        co_tags.add(fm_id)
        except OSError:
            co_tags = set()  # file unreadable — no co-tags known, strict check
        found_ids = set(CAP_ID_RE.findall(quote))
        foreign = found_ids - {cap_id} - co_tags
        if foreign:
            pc.quote_ok = False
            pc.messages.append(
                f"citation contient l'ID d'une autre capacité : "
                f"{', '.join(sorted(foreign))}")

    return pc


# --- vérification d'une capacité ---------------------------------------------

ROLE_KEYS = {
    "proof_course": "cours",
    "proof_practice": "entraînement",
    "proof_correction": "correction",
}


@dataclass
class CapacityResult:
    capacity_id: str
    declared_verdict: str
    effective_verdict: str
    label_ok: bool
    proofs: list[ProofCheck]
    downgraded: bool
    reasons: list[str]


def check_capacity(
    cap: dict[str, Any],
    repo_root: Path,
    official: dict[str, str],
    section_cache: dict[Path, dict[str, Section]],
) -> CapacityResult:
    cid = str(cap.get("capacity_id", "?"))
    declared = str(cap.get("verdict", "needs_content"))
    reasons: list[str] = []

    # 1. concordance de l'intitulé officiel
    label_ok = True
    off = official.get(cid)
    if off is not None:
        official_label = str(cap.get("official_label", ""))
        if normalize(official_label) not in normalize(off) \
           and normalize(off) not in normalize(official_label):
            label_ok = False
            reasons.append(
                f"official_label ne concorde pas avec le YAML pour {cid}")
    else:
        reasons.append(f"{cid} absent du programme YAML (à vérifier)")

    # 2. preuves
    proofs = [check_proof(ROLE_KEYS[k], cap.get(k, {}), repo_root, section_cache,
                          cap_id=cid)
              for k in ROLE_KEYS]
    for pc in proofs:
        for msg in pc.messages:
            reasons.append(f"[{pc.role}] {msg}")

    flags = cap.get("scientific_flags") or []
    if flags:
        reasons.append(f"{len(flags)} alerte(s) scientifique(s) signalée(s)")

    # 2b. citations dupliquées entre rôles
    seen_quotes: dict[str, str] = {}
    for pc in proofs:
        if not pc.present:
            continue
        role_key = [k for k, v in ROLE_KEYS.items() if v == pc.role][0]
        raw_quote = str(cap.get(role_key, {}).get("quote") or "")
        if not raw_quote:
            continue
        nq = normalize(raw_quote)
        if nq in seen_quotes:
            pc.quote_ok = False
            pc.messages.append(
                f"citation dupliquée (identique à {seen_quotes[nq]})")
            reasons.append(
                f"[{pc.role}] citation dupliquée (identique à {seen_quotes[nq]})")
        else:
            seen_quotes[nq] = pc.role

    # 2c. citation = simple étiquette du programme (template label)
    template_label_re = re.compile(
        r"^[A-Z0-9_.-]+\s*[-:]\s*\S.*$"
    )
    for pc in proofs:
        if not pc.present or not pc.quote_ok:
            continue
        role_key = [k for k, v in ROLE_KEYS.items() if v == pc.role][0]
        raw_quote = str(cap.get(role_key, {}).get("quote") or "").strip()
        if not raw_quote:
            continue
        # Match pattern "<ID> : <label>" where quote is just the capacity listing
        if template_label_re.match(raw_quote) and len(raw_quote.split()) <= 15:
            pc.quote_ok = False
            pc.messages.append(
                "citation = simple étiquette du programme (template label)")
            reasons.append(
                f"[{pc.role}] citation = étiquette administrative, pas un extrait de contenu")

    # 2d. teaches:true avec justification négative
    negative_patterns = [
        "ne correspond pas",
        "aucun contenu",
        "étiquette administrative",
    ]
    for pc in proofs:
        if not pc.present or not pc.teaches:
            continue
        role_key = [k for k, v in ROLE_KEYS.items() if v == pc.role][0]
        justification = str(cap.get(role_key, {}).get("justification") or "").lower()
        if not justification:
            continue
        for neg in negative_patterns:
            if neg in justification:
                pc.teaches = False
                pc.messages.append(
                    f"teaches=true contradicted by justification containing '{neg}'")
                reasons.append(
                    f"[{pc.role}] teaches=true contradicted by negative justification")
                break

    # 3. verdict effectif (le vérificateur ne promeut jamais)
    all_verified_and_teaches = all(p.verified and p.teaches for p in proofs)
    effective = declared
    if declared == "validated_pedagogy":
        if not label_ok or flags or not all_verified_and_teaches:
            effective = "needs_content"
            reasons.append(
                "DÉGRADÉ : validated_pedagogy non soutenu par 3 preuves "
                "vérifiées+enseignantes sans alerte scientifique")
    downgraded = effective != declared
    return CapacityResult(cid, declared, effective, label_ok, proofs,
                          downgraded, reasons)


# --- détection de doublons intra-fichier de capacity_id ----------------------

def check_intra_file_duplicates(verdict: dict[str, Any]) -> list[str]:
    """Vérifie qu'aucun capacity_id n'apparaît plus d'une fois dans un verdict.

    Fonction partagée, appelée par :
      (a) mode single-file de check_substance_anchors.py
      (b) mode batch de check_substance_anchors.py
      (c) validate_verdict_file() dans judge_campaign.py (import direct)
    """
    if not isinstance(verdict, dict):
        return []
    counts: dict[str, int] = {}
    for cap in verdict.get("capacities") or []:
        if not isinstance(cap, dict):
            continue
        cid = str(cap.get("capacity_id", ""))
        if cid:
            counts[cid] = counts.get(cid, 0) + 1
    return [
        f"DOUBLON intra-fichier : capacity_id {cid} apparaît {n} fois"
        for cid, n in sorted(counts.items()) if n > 1
    ]


def _check_verdict_root(verdict: Any) -> list[str]:
    """Guard: reject non-dict JSON roots gracefully.

    Shared by validate_verdict_data AND the CLI single-file/batch paths
    so that [], null, "str", 42 never reach verdict.get(...).
    """
    if not isinstance(verdict, dict):
        return [f"verdict JSON racine n'est pas un objet (type: {type(verdict).__name__})"]
    return []


def validate_verdict_data(
    verdict: Any,
    schema_path: Path,
    repo_root: Path | None = None,
) -> list[str]:
    """Validate a verdict: schema, intra-file duplicates, and anchors.

    Returns list of error messages (empty = valid, promotable).
    Fail-closed: infrastructure errors (jsonschema absent, schema file missing)
    are treated as blocking — never silently dropped.

    Parity contract: for any input, this function returns errors iff the CLI
    single-file mode (python -m scripts.check_substance_anchors FILE) would
    exit with code != 0. Same accept/reject decision.

    When repo_root is provided, also runs per-capacity anchor/quote checks.
    """
    root_errors = _check_verdict_root(verdict)
    if root_errors:
        return root_errors
    errors = validate_schema(verdict, schema_path)
    # Fail-closed: ANY schema error blocks deep checks. This includes:
    # - "schéma @" validation errors (proof_course:null, etc.)
    # - "jsonschema absent" (library not installed)
    # - "schéma introuvable" (schema file missing)
    # A malformed verdict must never reach check_capacity.
    dup_errors = check_intra_file_duplicates(verdict)
    all_errors = errors + dup_errors
    if all_errors:
        return all_errors
    # Full per-capacity checks (anchors, quotes, degradation, BLOCKER)
    if repo_root is not None:
        official = load_official_labels(repo_root)
        section_cache: dict[Path, dict[str, Section]] = {}
        capacities = verdict.get("capacities") or []
        for cap in capacities:
            if not isinstance(cap, dict):
                continue
            result = check_capacity(cap, repo_root, official, section_cache)
            # Invalid proofs (present but not verified)
            for p in result.proofs:
                if p.present and not p.verified:
                    for msg in p.messages:
                        all_errors.append(f"[{p.role}] {msg}")
            # Degradation (validated_pedagogy unsupported)
            if result.downgraded:
                all_errors.append(
                    f"{result.capacity_id}: DÉGRADÉ {result.declared_verdict}"
                    f" → {result.effective_verdict}")
            # BLOCKER verdict — always rejected (parity with CLI n_blocker)
            if result.effective_verdict == "BLOCKER":
                all_errors.append(
                    f"{result.capacity_id}: verdict BLOCKER")
    return all_errors


# --- détection de preuves invalides (present:true mais non vérifiées) --------

def has_invalid_present_proof(results: list[CapacityResult]) -> bool:
    """Returns True if any capacity has a proof where present=True but
    the proof is not verified (anchor_ok=false or quote_ok=false)."""
    for r in results:
        for p in r.proofs:
            if p.present and not p.verified:
                return True
    return False


# --- validation de schéma (optionnelle) --------------------------------------

def validate_schema(verdict: dict[str, Any], schema_path: Path) -> list[str]:
    try:
        import jsonschema  # type: ignore
    except ImportError:
        return ["jsonschema absent : validation de schéma sautée "
                "(pip install jsonschema pour l'activer)"]
    if not schema_path.exists():
        return [f"schéma introuvable : {schema_path}"]
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    errs: list[str] = []
    validator = jsonschema.Draft202012Validator(schema)
    for e in sorted(validator.iter_errors(verdict), key=lambda x: x.path):
        loc = "/".join(str(p) for p in e.path) or "(racine)"
        errs.append(f"schéma @ {loc} : {e.message}")
    return errs


# --- programme principal ------------------------------------------------------

def main() -> int:
    ap = argparse.ArgumentParser(description="Vérificateur d'ancres du juge de substance")
    ap.add_argument("verdict", type=Path, nargs="?", help="fichier verdict JSON")
    ap.add_argument("--repo-root", type=Path, default=Path("."),
                    help="racine du dépôt nsi-enseignement")
    ap.add_argument("--schema", type=Path,
                    default=Path(__file__).resolve().parents[1] / "substance_verdict.schema.json")
    ap.add_argument("--json", type=Path, default=None,
                    help="écrire le rapport machine dans ce fichier")
    args = ap.parse_args()

    repo_root = args.repo_root.resolve()
    if args.verdict is None:
        # All verdict files, wherever they live — no verdict escapes the gate
        # Canonical location: substance_reviews/ and in-sequence files
        # 01_build_reports/ copies are excluded (deduplicated in PR A2)
        review_globs = [
            "03_progressions/supports/**/_substance_review.json",
            "substance_reviews/**/*_substance_review.json",
        ]
        review_files: list[Path] = []
        for pattern in review_globs:
            review_files.extend(repo_root.glob(pattern))
        review_files = sorted(set(review_files))
        if not review_files:
            print("ERREUR : aucun _substance_review.json trouvé", file=sys.stderr)
            return 2
        # J6b: uniqueness guard — no two verdict files for the same capacity_id
        cap_id_to_files: dict[str, set[Path]] = {}
        failures: list[str] = []
        for rf in review_files:
            try:
                vdata = json.loads(rf.read_text(encoding="utf-8"))
                # J6-quater: shared root guard
                root_errs = _check_verdict_root(vdata)
                if root_errs:
                    failures.extend(f"{msg} dans {rf.relative_to(repo_root)}" for msg in root_errs)
                    continue
                # J6-ter: intra-file duplicates via shared function
                for msg in check_intra_file_duplicates(vdata):
                    failures.append(f"{msg} dans {rf.relative_to(repo_root)}")
                for cap in vdata.get("capacities", []):
                    if not isinstance(cap, dict):
                        continue
                    cid = str(cap.get("capacity_id", ""))
                    if cid:
                        cap_id_to_files.setdefault(cid, set()).add(rf)
            except (json.JSONDecodeError, OSError):
                continue  # skip unreadable verdict files
        # Inter-file duplicates
        for cid, files in sorted(cap_id_to_files.items()):
            if len(files) > 1:
                paths = ", ".join(str(f.relative_to(repo_root)) for f in files)
                failures.append(f"DOUBLON capacity_id {cid} dans {len(files)} fichiers : {paths}")
        for review in review_files:
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    str(review),
                    "--repo-root",
                    str(repo_root),
                    "--schema",
                    str(args.schema),
                ],
                cwd=repo_root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            if result.returncode != 0:
                failures.append(f"{review.relative_to(repo_root)}: code {result.returncode}\n{result.stdout}")
        poison = repo_root / "substance_reviews" / "_adversarial" / "poisoned.verdict.json"
        if poison.exists():
            result = subprocess.run(
                [
                    sys.executable,
                    str(Path(__file__).resolve()),
                    str(poison),
                    "--repo-root",
                    str(repo_root),
                    "--schema",
                    str(args.schema),
                ],
                cwd=repo_root,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
            )
            if result.returncode == 0:
                failures.append("test adverse empoisonné accepté à tort")
            else:
                print("test adverse du juge: PASS (verdict empoisonné refusé)")
        else:
            failures.append("verdict adverse absent: substance_reviews/_adversarial/poisoned.verdict.json")
        if failures:
            print("check_substance_anchors: KO")
            for failure in failures:
                print(f"- {failure}")
            return 1
        print(f"check_substance_anchors: PASS ({len(review_files)} verdicts vérifiés)")
        return 0

    try:
        verdict = json.loads(args.verdict.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERREUR entrée : {exc}", file=sys.stderr)
        return 2

    # J6-quater: shared root guard — same check as validate_verdict_data
    root_errors = _check_verdict_root(verdict)
    if root_errors:
        for msg in root_errors:
            print(f"ERREUR : {msg}", file=sys.stderr)
        return 2

    schema_msgs = validate_schema(verdict, args.schema)
    # Fail-closed: ANY schema error blocks deep checks (parity with validate_verdict_data)
    hard_schema_error = bool(schema_msgs)

    # J6-ter: intra-file duplicate check (shared function, single-file path)
    dup_msgs = check_intra_file_duplicates(verdict)
    for msg in dup_msgs:
        schema_msgs.append(msg)
    if dup_msgs:
        hard_schema_error = True

    # --- rapport lisible (header) ---
    unit = verdict.get("unit", "?")
    print(f"=== Vérification de substance — unité {unit} "
          f"({verdict.get('level','?')}) ===")
    print(f"juge: {verdict.get('judge_model','?')}  "
          f"auteur: {verdict.get('author_model','?')}")
    if verdict.get("judge_model") and verdict.get("judge_model") == verdict.get("author_model"):
        print("  ⚠ juge == auteur : séparation des rôles non respectée")
    for m in schema_msgs:
        print(f"  schéma: {m}")
    print()

    # J6-quater: schema errors block deep checks (parity with validate_verdict_data).
    # A capacity with proof_course:null must not reach check_capacity.
    if hard_schema_error:
        print("=== Bilan ===")
        print("Arrêt : erreur de schéma bloquante détectée.")
        return 2

    official = load_official_labels(repo_root)
    section_cache: dict[Path, dict[str, Section]] = {}
    results = [check_capacity(cap, repo_root, official, section_cache)
               for cap in verdict.get("capacities", [])]

    n_validated = n_needs = n_blocker = n_downgraded = 0
    for r in results:
        mark = {"validated_pedagogy": "✅", "needs_content": "🟠",
                "BLOCKER": "⛔"}.get(r.effective_verdict, "?")
        line = f"{mark} {r.capacity_id}: {r.effective_verdict}"
        if r.downgraded:
            line += f"  (déclaré {r.declared_verdict}, DÉGRADÉ)"
            n_downgraded += 1
        print(line)
        for pc in r.proofs:
            tag = "ok" if pc.verified else ("absente" if not pc.present else "INVALIDE")
            extra = f" [{pc.quote_method}]" if pc.quote_method else ""
            teach = "" if pc.teaches or not pc.present else " (teaches=false)"
            print(f"    - preuve {pc.role:12} : {tag}{extra}{teach}")
        for reason in r.reasons:
            print(f"      · {reason}")
        if r.effective_verdict == "validated_pedagogy":
            n_validated += 1
        elif r.effective_verdict == "BLOCKER":
            n_blocker += 1
        else:
            n_needs += 1
        print()

    print("=== Bilan ===")
    print(f"validées (effectif) : {n_validated}")
    print(f"needs_content       : {n_needs}")
    print(f"BLOCKER             : {n_blocker}")
    print(f"verdicts dégradés   : {n_downgraded}")

    if args.json:
        payload = {
            "unit": unit,
            "schema_messages": schema_msgs,
            "summary": {"validated": n_validated, "needs_content": n_needs,
                        "blocker": n_blocker, "downgraded": n_downgraded},
            "capacities": [
                {"capacity_id": r.capacity_id,
                 "declared": r.declared_verdict,
                 "effective": r.effective_verdict,
                 "downgraded": r.downgraded,
                 "label_ok": r.label_ok,
                 "reasons": r.reasons,
                 "proofs": [asdict(p) for p in r.proofs]}
                for r in results],
        }
        args.json.write_text(json.dumps(payload, ensure_ascii=False, indent=2),
                             encoding="utf-8")
        print(f"\nrapport machine écrit : {args.json}")

    n_invalid_proofs = sum(
        1 for r in results for p in r.proofs if p.present and not p.verified
    )
    if n_invalid_proofs:
        print(f"preuves invalides   : {n_invalid_proofs}")

    if hard_schema_error:
        return 2
    return 1 if n_downgraded or n_blocker or n_invalid_proofs else 0


if __name__ == "__main__":
    raise SystemExit(main())
