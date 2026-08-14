#!/usr/bin/env python3
"""Judge campaign: evaluate capacity coverage through OpenRouter.

Execution is synchronous and sorted by sequence. Every successful billed
generation is journalled before its verdict is parsed or validated.

V0d — Coverage derivation (ref: scripts/check_program_coverage.py L40-62):
  The coverage engine does NOT read judge verdicts. covered=0 until the lead
  promotes file statuses to validated_pedagogy.

J2d — Validate-before-save: each verdict passes the hardened checker BEFORE
  writing. If invalid, ONE retry with error feedback. If still invalid, the
  verdict is saved as needs_content with the error noted.

SECRETS: OpenRouter configuration comes from the environment or ``.env.rag``.
"""

from __future__ import annotations

import argparse
from collections.abc import Mapping, Sequence
import fcntl
import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

CORPUS_ROOT = Path(__file__).resolve().parents[1]
try:
    CHECKOUT_ROOT = next(parent for parent in CORPUS_ROOT.parents if (parent / ".git").exists())
except StopIteration as exc:
    raise RuntimeError("checkout root not found for nexus_external") from exc

checkout_path = str(CHECKOUT_ROOT)
while checkout_path in sys.path:
    sys.path.remove(checkout_path)
sys.path.insert(0, checkout_path)

import nexus_external  # noqa: E402
from nexus_external.openrouter_client import (  # noqa: E402
    OpenRouterCompletion,
    OpenRouterError,
    chat_completion,
)

expected_external = (CHECKOUT_ROOT / "nexus_external").resolve()
loaded_external = Path(nexus_external.__file__).resolve().parent
if loaded_external != expected_external:
    raise ImportError(
        "nexus_external loaded outside current checkout: "
        f"expected {expected_external}, got {loaded_external}"
    )

corpus_path = str(CORPUS_ROOT)
for managed_path in (corpus_path, checkout_path):
    while managed_path in sys.path:
        sys.path.remove(managed_path)
sys.path.insert(0, corpus_path)
sys.path.insert(1, checkout_path)

import yaml  # noqa: E402

from scripts._qa_common import (  # noqa: E402
    SUPPORTS_DIR,
    read_frontmatter,
)
from scripts.check_substance_anchors import (  # noqa: E402
    parse_sections,
    validate_verdict_data,
)
from scripts.rag_core import resolve_env_file  # noqa: E402

ROOT = CORPUS_ROOT

PROGRAMME_FILE = ROOT / "00_programmes_officiels" / "programme_nsi_2019.yaml"
OUTPUT_DIR = ROOT / "substance_reviews" / "campaign"

# ── Verdict schema (sorted keys for byte-stability) ──
VERDICT_SCHEMA = {
    "type": "object",
    "required": ["proof_course", "proof_practice", "proof_correction", "comment"],
    "properties": {
        "proof_course": {
            "type": "object",
            "required": ["present", "file", "anchor", "quote"],
            "properties": {
                "present": {"type": "boolean"},
                "file": {"type": ["string", "null"]},
                "anchor": {"type": ["string", "null"]},
                "quote": {"type": ["string", "null"]},
            },
        },
        "proof_practice": {
            "type": "object",
            "required": ["present", "file", "anchor", "quote"],
            "properties": {
                "present": {"type": "boolean"},
                "file": {"type": ["string", "null"]},
                "anchor": {"type": ["string", "null"]},
                "quote": {"type": ["string", "null"]},
            },
        },
        "proof_correction": {
            "type": "object",
            "required": ["present", "file", "anchor", "quote"],
            "properties": {
                "present": {"type": "boolean"},
                "file": {"type": ["string", "null"]},
                "anchor": {"type": ["string", "null"]},
                "quote": {"type": ["string", "null"]},
            },
        },
        "comment": {"type": "string"},
    },
}

GOLD_EXAMPLES = """

=== EXEMPLE 1 (3/3 proofs) ===
Capacité : P-DATA-BASE-01 — Passer de la représentation d'une base dans une autre.
Verdict :
{"proof_course": {"present": true, "file": "03_progressions/supports/premiere/P01/P01_cours_conversions_bases.md", "anchor": "#méthode-de-conversion", "quote": "Enchaîner divisions par 2 puis lire les restes de bas en haut."}, "proof_practice": {"present": true, "file": "03_progressions/supports/premiere/P01/P01_td_conversions_bases.md", "anchor": "#exercice-1", "quote": "Convertir 13 en base 2 en appliquant la méthode des divisions."}, "proof_correction": {"present": true, "file": "03_progressions/supports/premiere/P01/P01_corrige_conversions_bases.md", "anchor": "#corrigé-exercice-1", "quote": "13 = 1101 en base 2."}, "comment": "Cours enseigne la méthode, TD la fait pratiquer, corrigé fournit la réponse."}

=== EXEMPLE 2 (0/3 — contenu ne correspond pas au libellé) ===
Capacité : P-HIST-01 — Situer dans le temps les principaux événements de l'histoire de l'informatique.
Verdict :
{"proof_course": {"present": false, "file": null, "anchor": null, "quote": null}, "proof_practice": {"present": false, "file": null, "anchor": null, "quote": null}, "proof_correction": {"present": false, "file": null, "anchor": null, "quote": null}, "comment": "Contenu porte sur un projet énergie solaire, pas sur l'histoire de l'informatique."}

=== EXEMPLE 3 (2/3 — cours manquant) ===
Capacité : T-ALGO-01C — Parcourir un arbre en ordres infixe, préfixe ou suffixe.
Verdict :
{"proof_course": {"present": false, "file": null, "anchor": null, "quote": null}, "proof_practice": {"present": true, "file": "03_progressions/supports/terminale/T06/T06_TP_arbres_binaires_recherche.md", "anchor": "#trace-attendue-détaillée", "quote": "Parcours infixe attendu (T-ALGO-01C) : [1, 3, 6, 8, 10, 14]."}, "proof_correction": {"present": true, "file": "03_progressions/supports/terminale/T06/T06_corrige_arbres_binaires_recherche.md", "anchor": "#exercice-3", "quote": "Méthode : parcours infixe (gauche, racine, droite) — T-ALGO-01C."}, "comment": "TP et corrigé exercent le parcours infixe. Pas de cours dédié."}

=== EXEMPLE 4 (3/3 avec itération explicite) ===
Capacité : P-DATA-CONSTR-02D — Itérer sur les éléments d'un tableau.
Verdict :
{"proof_course": {"present": true, "file": "03_progressions/supports/premiere/P04/P04_trace_types_construits.md", "anchor": "#repère-2---liste-de-relevés", "quote": "À retenir : parcourir les valeurs et calculer une moyenne."}, "proof_practice": {"present": true, "file": "03_progressions/supports/premiere/P04/P04_td_types_construits.md", "anchor": "#exercice-2", "quote": "Écrire une boucle for valeur in releves qui calcule la moyenne."}, "proof_correction": {"present": true, "file": "03_progressions/supports/premiere/P04/P04_corrige_types_construits.md", "anchor": "#corrigé-exercice-2", "quote": "parcourir les valeurs et calculer une moyenne."}, "comment": "Trace enseigne l'itération, TD fait pratiquer avec boucle for."}"""

# ── J2c: Hardened protocol ──
PROTOCOLE_JUGE = """Tu es un juge pédagogique NSI. Pour chaque capacité officielle du programme,
tu reçois le libellé officiel et les extraits des fichiers d'évidence.
Chaque extrait est précédé de son chemin === chemin/fichier.md === et du tag [CAPACITÉ: X-Y-Z].

Réponds UNIQUEMENT en JSON valide (sans markdown, sans backticks), conforme au schéma ci-dessous.

RÈGLES DE CITATION (J2c — CRITIQUES, le vérificateur mécanique rejette les infractions) :
1. "quote" doit être une SOUS-CHAÎNE VERBATIM de l'extrait : conserver la casse, le gras (**),
   les puces (- ), les backticks (`). NE PAS reformuler, NE PAS concaténer, NE PAS inventer.
2. "quote" DOIT contenir au moins 25 caractères de contenu réel (pas un label comme "P-ALGO-01A").
3. Chaque rôle (cours/practice/correction) doit avoir une citation DISTINCTE — JAMAIS la même.
4. "anchor" DOIT être copié VERBATIM depuis la ligne [ANCRES VALIDES: ...] du fichier cité.
   Ne JAMAIS construire un slug depuis un titre — utiliser UNIQUEMENT les ancres inventoriées.
5. "file" = chemin EXACT copié depuis la ligne === chemin ===.
6. Ne citer que des sections dont le TAG [CAPACITÉ: ...] correspond à la capacité jugée.
   Si le tag ne correspond pas, chercher dans les autres extraits. Si aucun extrait ne correspond,
   mettre present: false.
7. Si aucune preuve solide n'existe pour un rôle → present: false honnête. JAMAIS de remplissage.
8. proof_correction cite EXCLUSIVEMENT un fichier corrigé ou barème (nom contenant "corrige" ou
   "bareme"), avec une ancre depuis SON inventaire [ANCRES VALIDES]. Ne JAMAIS citer un fichier
   TD/TP/cours pour le rôle correction.

RÈGLES DE VERDICT :
- proof_course : le COURS ou la TRACE enseigne la capacité (définition, méthode, explication)
- proof_practice : le TD ou TP fait PRATIQUER (exercice réel avec consigne et production attendue)
- proof_correction : le corrigé ou l'évaluation permet de SE CORRIGER (réponse, barème, correction)
- present: false si le contenu ne correspond PAS au libellé officiel (étiquette administrative seule)
- "comment" : justification en 1-3 phrases, ≤ 400 caractères, phrase complète

"""

SYSTEM_TEXT = (
    PROTOCOLE_JUGE
    + "SCHÉMA JSON ATTENDU :\n"
    + json.dumps(VERDICT_SCHEMA, sort_keys=True, ensure_ascii=False, indent=2)
    + "\n\nEXEMPLES DE VERDICTS CORRECTS :"
    + GOLD_EXAMPLES
)

def load_programme() -> dict[str, dict[str, str]]:
    data = yaml.safe_load(PROGRAMME_FILE.read_text(encoding="utf-8"))
    entries: dict[str, dict[str, str]] = {}
    for level in ("premiere", "terminale"):
        for cap in data["programmes"].get(level, []):
            cap_attendue = cap.get("capacite_attendue", [""])
            cap_id = str(cap["id"])
            entries[cap_id] = {
                "id": cap_id,
                "intitule": cap_attendue[0] if isinstance(cap_attendue, list) else str(cap_attendue),
                "contenu": str(cap.get("contenu", "")),
                "rubrique": str(cap.get("rubrique", "")),
                "niveau": level,
            }
    return entries


def extract_body(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:]
    return text


def find_sequences_for_capacity(cap_id: str) -> list[str]:
    prefix_pattern = re.compile(r"[PT]\d{2}")
    sequences: set[str] = set()
    for level_dir in [SUPPORTS_DIR / "premiere", SUPPORTS_DIR / "terminale"]:
        if not level_dir.is_dir():
            continue
        for seq_dir in sorted(level_dir.iterdir()):
            if not seq_dir.is_dir() or not prefix_pattern.fullmatch(seq_dir.name):
                continue
            for md_path in seq_dir.rglob("*.md"):
                if "contracts" in md_path.parts:
                    continue
                fm = read_frontmatter(md_path)
                official = fm.get("official_program")
                if not isinstance(official, dict):
                    continue
                caps = official.get("capacities", [])
                if isinstance(caps, list) and cap_id in {str(c) for c in caps if isinstance(c, str)}:
                    sequences.add(seq_dir.name)
                    break
    return sorted(sequences)


def build_sequence_context(seq_id: str, cap_id: str) -> str:
    """Build context for a sequence, tagging each file with its declared capacities.

    J2b: NO truncation — full body. Each extrait tagged with [CAPACITÉ: ...] for
    anti cross-attribution.
    """
    level = "premiere" if seq_id.startswith("P") else "terminale"
    seq_dir = SUPPORTS_DIR / level / seq_id
    if not seq_dir.is_dir():
        return ""
    parts: list[str] = []
    for md_path in sorted(seq_dir.rglob("*.md")):
        if "contracts" in md_path.parts:
            continue
        fm = read_frontmatter(md_path)
        official = fm.get("official_program")
        file_caps: list[str] = []
        if isinstance(official, dict):
            raw = official.get("capacities", [])
            if isinstance(raw, list):
                file_caps = [str(c) for c in raw if isinstance(c, str)]
        # Only include files that declare the target capacity
        if cap_id not in file_caps:
            continue
        rel = md_path.relative_to(ROOT).as_posix()
        body = extract_body(md_path)
        cap_tag = ", ".join(file_caps)
        # K1-BIS-C: anchor inventory — list of valid slugs for this file
        sections = parse_sections(md_path.read_text(encoding="utf-8", errors="replace"))
        anchor_list = ", ".join(f"#{s}" for s in sorted(sections))
        parts.append(
            f"=== {rel} ===\n[CAPACITÉ: {cap_tag}]\n"
            f"[ANCRES VALIDES: {anchor_list}]\n{body}"
        )
    return "\n\n".join(parts)


def build_capacity_prompt(cap_id: str, programme: dict[str, dict[str, str]]) -> str:
    cap = programme[cap_id]
    return (
        f"CAPACITÉ À JUGER : {cap_id} — {cap['intitule']}\n"
        f"Rubrique : {cap['rubrique']}\n"
        f"Contenu : {cap['contenu']}\n\n"
        f"Analyse les extraits ci-dessus et produis le verdict JSON."
    )


def load_openrouter_config(
    environ: Mapping[str, str],
    env_path: Path,
) -> tuple[str, str]:
    """Resolve the two OpenRouter values without consulting generic dotenv."""

    api_key = environ.get("OPENROUTER_API_KEY", "").strip()
    model = environ.get("OPENROUTER_MODEL", "").strip()
    file_values: dict[str, str] = {}
    if env_path.is_file():
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            if key in {"OPENROUTER_API_KEY", "OPENROUTER_MODEL"}:
                file_values[key] = value.strip()
    if not api_key:
        api_key = file_values.get("OPENROUTER_API_KEY", "").strip()
    if not model:
        model = file_values.get("OPENROUTER_MODEL", "").strip()
    if not api_key or not model:
        raise OpenRouterError("configuration", model=model or "<invalid>")
    return api_key, model


def call_openrouter_judge(
    api_key: str,
    model: str,
    seq_context: str,
    capacity_prompt: str,
    *,
    transport: object | None = None,
) -> OpenRouterCompletion:
    user_content = (
        seq_context + "\n\n" + capacity_prompt
        if seq_context
        else capacity_prompt
    )
    return chat_completion(
        api_key=api_key,
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_TEXT},
            {"role": "user", "content": user_content},
        ],
        max_completion_tokens=2500,
        transport=transport,
    )


def build_usage_v2(
    *,
    cap: str,
    seq: str,
    attempt: int,
    judged_at: str,
    completion: OpenRouterCompletion,
) -> dict[str, object]:
    usage = completion.usage
    return {
        "schema_version": 2,
        "provider": "openrouter",
        "cap": cap,
        "seq": seq,
        "attempt": attempt,
        "judged_at": judged_at,
        "model": completion.model,
        "generation_id": completion.generation_id,
        "prompt_tokens": usage.prompt_tokens,
        "completion_tokens": usage.completion_tokens,
        "total_tokens": usage.total_tokens,
        "cached_tokens": usage.cached_tokens,
        "cache_write_tokens": usage.cache_write_tokens,
        "cost_usd": usage.cost,
    }


def build_failed_usage_v2(
    *,
    cap: str,
    seq: str,
    attempt: int,
    judged_at: str,
    model: str,
    error_category: str,
) -> dict[str, object]:
    return {
        "schema_version": 2,
        "provider": "openrouter",
        "cap": cap,
        "seq": seq,
        "attempt": attempt,
        "judged_at": judged_at,
        "model": model,
        "error_category": error_category,
    }


def merge_usage_log(
    existing: Sequence[Mapping[str, object]],
    incoming: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Upsert schema-v2 generations while preserving every v1 row."""

    merged = [dict(entry) for entry in existing]
    for entry in incoming:
        replacement = dict(entry)
        generation_id = replacement.get("generation_id")
        position = next(
            (
                index
                for index, previous in enumerate(merged)
                if generation_id is not None
                and previous.get("schema_version") == 2
                and previous.get("generation_id") == generation_id
            ),
            None,
        )
        if position is None:
            merged.append(replacement)
        else:
            merged[position] = replacement
    return merged


def load_usage_log(
    log_path: Path,
    *,
    model: str,
) -> list[dict[str, object]]:
    """Load an existing journal without treating corruption as empty history."""

    if not log_path.exists():
        return []
    try:
        loaded = json.loads(log_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise OpenRouterError("protocol", model=model) from error
    if not isinstance(loaded, list) or not all(
        isinstance(entry, dict) for entry in loaded
    ):
        raise OpenRouterError("protocol", model=model)
    return loaded


def directory_open_flags() -> int:
    return os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)


def lock_open_flags() -> int:
    return os.O_RDWR | os.O_CREAT


def write_usage_log_atomic(
    log_path: Path,
    entries: Sequence[Mapping[str, object]],
) -> None:
    """Durably replace a usage journal from a distinct sibling temporary file."""

    payload = json.dumps(entries, ensure_ascii=False, indent=2)
    descriptor, temporary_name = tempfile.mkstemp(
        dir=log_path.parent,
        prefix=f".{log_path.name}.",
        suffix=".tmp",
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(payload)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary_path, log_path)
        directory_fd = os.open(log_path.parent, directory_open_flags())
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except Exception:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def append_usage_log_locked(
    log_path: Path,
    incoming: Sequence[Mapping[str, object]],
    *,
    model: str,
) -> list[dict[str, object]]:
    """Append generations without losing writes from concurrent processes."""

    lock_path = log_path.with_name(f".{log_path.name}.lock")
    lock_fd = os.open(lock_path, lock_open_flags(), 0o600)
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
        try:
            existing = load_usage_log(log_path, model=model)
            merged = merge_usage_log(existing, incoming)
            write_usage_log_atomic(log_path, merged)
            return merged
        finally:
            fcntl.flock(lock_fd, fcntl.LOCK_UN)
    finally:
        os.close(lock_fd)


ROLE_ERROR_PATTERNS = {
    "proof_course": re.compile(r"(?:\[cours\]|\bproof_course\b)", re.IGNORECASE),
    "proof_practice": re.compile(
        r"(?:\[entraînement\]|\bproof_practice\b)",
        re.IGNORECASE,
    ),
    "proof_correction": re.compile(
        r"(?:\[correction\]|\bproof_correction\b)",
        re.IGNORECASE,
    ),
}


def failed_proof_roles(errors: Sequence[str]) -> list[str]:
    """Attribute gate errors only through the protocol's anchored role markers."""

    error_text = "\n".join(errors)
    return [
        role
        for role, pattern in ROLE_ERROR_PATTERNS.items()
        if pattern.search(error_text)
    ]


def current_run_totals(
    current_entries: Sequence[Mapping[str, object]],
) -> dict[str, int | float]:
    return {
        "prompt_tokens": sum(int(entry["prompt_tokens"]) for entry in current_entries),
        "completion_tokens": sum(
            int(entry["completion_tokens"]) for entry in current_entries
        ),
        "total_tokens": sum(int(entry["total_tokens"]) for entry in current_entries),
        "cached_tokens": sum(int(entry["cached_tokens"]) for entry in current_entries),
        "cache_write_tokens": sum(
            int(entry["cache_write_tokens"]) for entry in current_entries
        ),
        "cost_usd": sum(
            cast(int | float, entry["cost_usd"]) for entry in current_entries
        ),
    }


def parse_campaign_verdict(content: str) -> dict[str, object]:
    payload = content.strip()
    if payload.startswith("```"):
        fence_start = "```json\n"
        fence_end = "\n```"
        if not payload.startswith(fence_start) or not payload.endswith(fence_end):
            raise ValueError("campaign verdict fence must be exactly ```json")
        payload = payload[len(fence_start) : -len(fence_end)]
    parsed = json.loads(payload)
    if not isinstance(parsed, dict):
        raise ValueError("campaign verdict must be a JSON object")
    return parsed


def _call_with_transport_retries(
    api_key: str,
    model: str,
    seq_context: str,
    capacity_prompt: str,
) -> OpenRouterCompletion:
    retryable = {"rate_limit", "timeout", "transport", "unavailable"}
    delays = (0, 2, 4)
    last_error: OpenRouterError | None = None
    for delay in delays:
        if delay:
            time.sleep(delay)
        try:
            return call_openrouter_judge(
                api_key,
                model,
                seq_context,
                capacity_prompt,
            )
        except OpenRouterError as error:
            last_error = error
            if error.category not in retryable:
                raise
    assert last_error is not None
    raise last_error


def format_verdict(cap_id: str, cap_info: dict[str, str], judge_result: dict[str, Any]) -> dict[str, Any]:
    """Format verdict. J2a: NO padding, NO truncation. Quotes are verbatim from the LLM."""
    def make_proof(role_key: str) -> dict[str, Any]:
        role_data = judge_result.get(role_key, {})
        if not isinstance(role_data, dict):
            return {"present": False, "file": None, "anchor": None, "quote": None, "teaches": False}
        present = bool(role_data.get("present", False))
        return {
            "present": present,
            "file": str(role_data.get("file", "")) if present else None,
            "anchor": str(role_data.get("anchor", "")) if present else None,
            "quote": str(role_data.get("quote", "")) if present else None,
            "teaches": present,
        }

    proofs = {
        "proof_course": make_proof("proof_course"),
        "proof_practice": make_proof("proof_practice"),
        "proof_correction": make_proof("proof_correction"),
    }
    present_count = sum(1 for p in proofs.values() if p.get("present"))
    verdict = "needs_review" if present_count else "needs_content"

    # J2e / J6c5: guard justification — descriptive string, never placeholder
    justification = str(judge_result.get("comment", ""))
    if not justification or len(justification) < 20:
        justification = (
            f"{present_count}/3 preuves vérifiées mécaniquement."
            if present_count
            else "0/3 : aucune preuve vérifiable dans les extraits."
        )
    if len(justification) > 400:
        # Truncate at last sentence boundary
        cut = justification[:400].rfind(".")
        justification = justification[:cut + 1] if cut > 100 else justification[:397] + "..."

    return {
        "capacity_id": cap_id,
        "official_label": cap_info["intitule"],
        **proofs,
        "verdict": verdict,
        "justification": justification,
        "scientific_flags": ["human_review_required"],
    }


SUBSTANCE_SCHEMA = ROOT / "substance_verdict.schema.json"


def should_preserve_existing_verdict(final_path: Path) -> bool:
    """Predicate: should an existing verdict on disk be preserved on API error?

    Returns True iff the file exists AND passes the full validation gate.
    Extracted as a named function so tests can exercise the actual decision
    logic (not a tautological reimplementation).
    """
    if not final_path.exists():
        return False
    return not validate_verdict_file(final_path)


def validate_verdict_file(verdict_path: Path) -> list[str]:
    """J2d: Full pre-promotion gate via direct import.

    Validates schema, intra-file duplicates, AND anchor/quote resolution
    against the corpus. Returns list of error messages (empty = valid).
    """
    try:
        verdict = json.loads(verdict_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"lecture/JSON impossible : {exc}"]
    return validate_verdict_data(verdict, SUBSTANCE_SCHEMA, repo_root=ROOT)


def _write_verdict_json(
    path: Path,
    cap_id: str,
    verdict: dict[str, Any],
    programme: dict[str, dict[str, str]],
    *,
    judge_model: str,
) -> None:
    """Write a verdict review JSON to the given path (no rename, no validation)."""
    review = {
        "schema_version": "1.0.0",
        "unit": "campaign",
        "level": programme[cap_id]["niveau"],
        "judged_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "judge_model": judge_model,
        "author_model": "campaign-tooling",
        "capacities": [verdict],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(review, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Judge campaign via OpenRouter")
    parser.add_argument("--cap-ids", type=str, default="", help="Comma-separated capacity IDs")
    parser.add_argument("--all", action="store_true", help="Judge all capacities")
    parser.add_argument("--dry-run", action="store_true", help="List capacities without calling API")
    parser.add_argument("--count-tokens", action="store_true", help="Count system block tokens")
    parser.add_argument("--force", action="store_true", help="Re-judge even if verdict file exists")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    programme = load_programme()

    if args.cap_ids:
        cap_ids = [c.strip() for c in args.cap_ids.split(",") if c.strip()]
    elif args.all:
        cap_ids = sorted(programme.keys())
    else:
        print("ERROR: specify --cap-ids or --all", file=sys.stderr)
        return 1

    selected = [c for c in cap_ids if c in programme]

    if args.dry_run:
        if args.count_tokens:
            sys_tokens = len(SYSTEM_TEXT) // 4
            print(f"System block: {len(SYSTEM_TEXT)} chars ~ {sys_tokens} tokens")
        print(f"Would judge {len(selected)} capacities:")
        seq_map: dict[str, list[str]] = {}
        for cap_id in selected:
            seqs = find_sequences_for_capacity(cap_id)
            seq_map.setdefault(seqs[0] if seqs else "?", []).append(cap_id)
        for seq_id in sorted(seq_map):
            print(f"  {seq_id}: {', '.join(seq_map[seq_id])}")
        return 0

    try:
        api_key, requested_model = load_openrouter_config(
            os.environ,
            resolve_env_file(CORPUS_ROOT),
        )
    except OpenRouterError as error:
        print(f"ERROR: OpenRouter {error.category}", file=sys.stderr)
        return 1

    def seq_sort_key(cid: str) -> str:
        seqs = find_sequences_for_capacity(cid)
        return seqs[0] if seqs else "zzz"

    selected.sort(key=seq_sort_key)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    results: list[dict[str, Any]] = []
    current_entries: list[dict[str, object]] = []
    seq_context_cache: dict[tuple[str, str], str] = {}  # (seq_id, cap_id) -> context
    log_path = args.output_dir / "_usage_log.json"
    try:
        load_usage_log(log_path, model=requested_model)
    except OpenRouterError as error:
        print(f"ERROR: OpenRouter {error.category}", file=sys.stderr)
        return 1

    for i, cap_id in enumerate(selected):
        seqs = find_sequences_for_capacity(cap_id)
        seq_id = seqs[0] if seqs else ""

        # J2b: context is per (seq, cap) — includes only files declaring this cap
        cache_key = (seq_id, cap_id)
        if cache_key not in seq_context_cache:
            seq_context_cache[cache_key] = build_sequence_context(seq_id, cap_id) if seq_id else ""
        seq_context = seq_context_cache[cache_key]

        if not seq_context:
            print(f"  [{i+1}/{len(selected)}] {cap_id}: no evidence, skipping")
            continue

        out_path = args.output_dir / f"{cap_id}_substance_review.json"
        if out_path.exists() and not args.force:
            print(f"  [{i+1}/{len(selected)}] {cap_id} ({seq_id}): skip (use --force)")
            continue

        cap_prompt = build_capacity_prompt(cap_id, programme)

        print(f"  [{i+1}/{len(selected)}] {cap_id} ({seq_id})...", end=" ", flush=True)
        final_path = args.output_dir / f"{cap_id}_substance_review.json"
        try:
            logical_prompt = cap_prompt
            verdict: dict[str, Any] | None = None
            promoted = False
            for logical_attempt in (1, 2):
                completion = _call_with_transport_retries(
                    api_key,
                    requested_model,
                    seq_context,
                    logical_prompt,
                )
                judged_at = (
                    datetime.now(timezone.utc)
                    .replace(microsecond=0)
                    .isoformat()
                    .replace("+00:00", "Z")
                )
                entry = build_usage_v2(
                    cap=cap_id,
                    seq=seq_id,
                    attempt=logical_attempt,
                    judged_at=judged_at,
                    completion=completion,
                )
                current_entries.append(entry)
                append_usage_log_locked(
                    log_path,
                    [entry],
                    model=requested_model,
                )

                try:
                    judge_result = parse_campaign_verdict(completion.content)
                except (json.JSONDecodeError, ValueError):
                    if logical_attempt == 1:
                        logical_prompt = cap_prompt + (
                            "\n\nFEEDBACK DU VÉRIFICATEUR : le verdict précédent "
                            "n'était pas un objet JSON valide."
                        )
                        continue
                    judge_result = {
                        "comment": "Verdict distant invalide après nouvelle tentative."
                    }

                verdict = format_verdict(cap_id, programme[cap_id], judge_result)
                tmp_path = final_path.with_suffix(".json.tmp")
                _write_verdict_json(
                    tmp_path,
                    cap_id,
                    verdict,
                    programme,
                    judge_model=requested_model,
                )
                errors = validate_verdict_file(tmp_path)
                if not errors:
                    tmp_path.replace(final_path)
                    promoted = True
                    break
                tmp_path.unlink(missing_ok=True)
                if logical_attempt == 1:
                    logical_prompt = cap_prompt + (
                        "\n\nFEEDBACK DU VÉRIFICATEUR :\n"
                        + "\n".join(errors[:5])
                    )
                    continue
                failed_roles = failed_proof_roles(errors)
                if not failed_roles:
                    print("gate error without role marker; not promoted")
                    break
                for role in failed_roles:
                    verdict[role] = {
                        "present": False,
                        "file": None,
                        "anchor": None,
                        "quote": None,
                        "teaches": False,
                    }
                valid_count = sum(
                    1
                    for role in ROLE_ERROR_PATTERNS
                    if verdict[role].get("present")
                )
                verdict["verdict"] = (
                    "needs_review" if valid_count else "needs_content"
                )
                verdict["justification"] = (
                    f"Auto-dégradé ({len(failed_roles)} rôle(s) invalide(s))."
                )
                _write_verdict_json(
                    tmp_path,
                    cap_id,
                    verdict,
                    programme,
                    judge_model=requested_model,
                )
                degraded_errors = validate_verdict_file(tmp_path)
                if not degraded_errors:
                    tmp_path.replace(final_path)
                    promoted = True
                else:
                    tmp_path.unlink(missing_ok=True)
                    print("degraded verdict failed validation; not promoted")
                break

            assert verdict is not None
            if promoted:
                results.append(verdict)
                present_count = sum(
                    1
                    for role in ROLE_ERROR_PATTERNS
                    if verdict[role].get("present")
                )
                print(f"{present_count}/3")
        except OpenRouterError as error:
            print(f"ERROR: OpenRouter {error.category}")
            failed_entry = build_failed_usage_v2(
                cap=cap_id,
                seq=seq_id,
                attempt=3 if error.category in {"rate_limit", "timeout", "transport", "unavailable"} else 1,
                judged_at=(
                    datetime.now(timezone.utc)
                    .replace(microsecond=0)
                    .isoformat()
                    .replace("+00:00", "Z")
                ),
                model=requested_model,
                error_category=error.category,
            )
            append_usage_log_locked(
                log_path,
                [failed_entry],
                model=requested_model,
            )
            if should_preserve_existing_verdict(final_path):
                print(f"  verdict existant préservé : {final_path.name}")
                existing = json.loads(final_path.read_text(encoding="utf-8"))
                results.append(existing.get("capacities", [{}])[0] if existing.get("capacities") else {})
            else:
                err_verdict = format_verdict(
                    cap_id,
                    programme[cap_id],
                    {"comment": f"OpenRouter indisponible ({error.category})."},
                )
                err_verdict["verdict"] = "needs_content"
                for role in ["proof_course", "proof_practice", "proof_correction"]:
                    err_verdict[role] = {"present": False, "file": None, "anchor": None, "quote": None, "teaches": False}
                tmp_path = final_path.with_suffix(".json.tmp")
                _write_verdict_json(
                    tmp_path,
                    cap_id,
                    err_verdict,
                    programme,
                    judge_model=requested_model,
                )
                tmp_path.replace(final_path)
                results.append(err_verdict)

    # Summary
    totals = current_run_totals(current_entries)

    print(f"\n{'='*60}")
    print(f"{len(results)} verdicts written to {args.output_dir}/")
    with_proofs = sum(1 for v in results if v["verdict"] == "needs_review")
    print(f"  needs_review (with proofs): {with_proofs}")
    print(f"  needs_content (no proofs): {len(results) - with_proofs}")
    print(f"\nOpenRouter usage for this run: {totals}")
    print(f"\nUsage log: {log_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
