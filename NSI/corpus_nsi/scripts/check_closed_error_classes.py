#!/usr/bin/env python3
"""Gate: detect known closed error classes across the entire corpus.

Each error class is a grep pattern that should NOT appear in the corpus once fixed.
The gate runs BEFORE correction to prove detection, then must be EMPTY after fixes.

Error classes:
- TCO_NON_TERMINAL: TCO/tail-call invoked for non-terminal recursive call
- LOCALSTORAGE_DOMAIN: "même domaine" used for localStorage (should be "même origine")
- GREEDY_MONTANT_3: montant=3 as greedy counter-example (too small, trivial)
- ROTATION_CONSIGNE_REPONSE: response content in wrong exercise (mots-clés)

Exit codes:
    0: no closed error class detected (clean)
    1: at least one error class detected
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUPPORTS_DIR = ROOT / "03_progressions" / "supports"


def _scan_files() -> list[Path]:
    """Return all markdown files in supports."""
    return sorted(SUPPORTS_DIR.rglob("*.md"))


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


# ─── Error class detectors ───────────────────────────────────────────────────

def check_tco_non_terminal(files: list[Path]) -> list[str]:
    """RVW-016: TCO mentioned near non-terminal recursion (addition on stack)."""
    hits: list[str] = []
    # Group files by sequence directory to detect cross-file TCO+non-terminal
    seq_dirs: dict[Path, list[Path]] = {}
    for f in files:
        seq_dirs.setdefault(f.parent, []).append(f)

    for seq_dir, seq_files in seq_dirs.items():
        combined_text = "\n".join(_read(f) for f in seq_files)
        has_tco = re.search(r"(?i)tail.?call|TCO|optimisation.*terminal", combined_text)
        has_non_terminal = re.search(r"lst\[0\]\s*\+\s*\w+\(lst\[1:\]\)", combined_text)
        if has_tco and has_non_terminal:
            # Report on the file containing the TCO mention
            for f in seq_files:
                text = _read(f)
                lines = text.splitlines()
                for i, line in enumerate(lines, 1):
                    if re.search(r"(?i)tail.?call|TCO|optimisation.*terminal", line):
                        hits.append(f"{f.relative_to(ROOT)}:{i}: TCO invoqué pour appel non terminal")
    return hits


def check_localstorage_domain(files: list[Path]) -> list[str]:
    """RVW-017: 'même domaine' instead of 'même origine' for localStorage."""
    hits: list[str] = []
    pattern = re.compile(r"(?i)local\s*storage.*même\s+domaine|même\s+domaine.*local\s*storage", re.IGNORECASE)
    for f in files:
        text = _read(f)
        if "localStorage" not in text and "localstorage" not in text.lower():
            continue
        lines = text.splitlines()
        for i, line in enumerate(lines, 1):
            if pattern.search(line):
                hits.append(f"{f.relative_to(ROOT)}:{i}: localStorage 'même domaine' au lieu de 'même origine'")
    return hits


def check_greedy_montant_3(files: list[Path]) -> list[str]:
    """Greedy counter-example with montant=3 (trivial, should be larger)."""
    hits: list[str] = []
    pattern = re.compile(r"montant\s*=\s*3\b")
    for f in files:
        text = _read(f)
        if "glouton" not in text.lower() and "greedy" not in text.lower():
            continue
        lines = text.splitlines()
        for i, line in enumerate(lines, 1):
            if pattern.search(line):
                hits.append(f"{f.relative_to(ROOT)}:{i}: contre-exemple glouton avec montant=3 (trop trivial)")
    return hits


_STOPWORDS = frozenset(
    # Déterminants, pronoms, prépositions, auxiliaires
    "le la les un une des de du en et ou par pour sur dans avec sans "
    "au aux ce cette ces que qui quoi dont où est sont être avoir fait "
    "il elle on nous vous ils elles ne pas plus se sa son ses leur "
    "tout tous toute toutes même si bien aussi très peu trop assez "
    # Vocabulaire d'évaluation et de consigne
    "point points pt pts question exercice réponse attendue donnée "
    "consigne écrire donner indiquer justifier expliquer résultat "
    "méthode cas limite contrôle capacité officielle barème "
    "correct critère critères réussite observable justification "
    "corrigé livrable vérifiable visible attendu confondu "
    "objectif énoncé production type identifier résoudre corriger "
    "comparer partir préciser décrire calculer tracer construire "
    "choisir remplir chercher distinguer dessiner nommer associer "
    # Vocabulaire de format évaluation
    "lang data struct arch algo hist each deux trois quatre cinq "
    "six sept huit premier deuxième troisième ligne lignes colonne "
    "fichier code programme fonction variable valeur liste tableau "
    "élève base nombre texte mot char champ entrée sortie retour".split()
)


def _extract_domain_terms(text: str) -> set[str]:
    """Extract significant domain terms (3+ chars, not stopwords)."""
    words = re.findall(r"[a-zA-ZÀ-ÿ]{3,}", text.lower())
    return {w for w in words if w not in _STOPWORDS}


def check_rotation_consigne_reponse(files: list[Path]) -> list[str]:
    """Detect answer-in-wrong-slot rotations across ALL evaluations.

    Two-pass detection:
    1. T09-specific: schéma/instance question → clé primaire-only answer.
    2. Cross-question swap: for each eval, check if question i's answer
       matches question j's consigne better than question i's own consigne.
       This detects the actual pathology: answers swapped between questions.
    """
    hits: list[str] = []

    for f in files:
        if "evaluation" not in f.name:
            continue
        text = _read(f)

        # ── Pass 1: T09 specific ──
        if "T09" in f.name:
            blocks_t09 = re.split(r"^#{2,3}\s+Question\s+\d+", text, flags=re.M)
            for block in blocks_t09[1:]:
                if not re.search(r"schéma|instance", block[:200], re.I):
                    continue
                ans = re.search(r"Réponse attendue\s*:\s*(.+?)(?:\n-|\Z)", block, re.I | re.S)
                if not ans:
                    continue
                a = ans.group(1)
                if re.search(r"clé primaire", a, re.I) and not re.search(r"schéma|instance", a, re.I):
                    hits.append(f"{f.relative_to(ROOT)}: rotation T09 (schéma/instance → clé primaire)")
                    break

        # ── Pass 2: cross-question swap detection ──
        blocks = re.split(r"^#{2,3}\s+Question\s+\d+", text, flags=re.M)
        qa_pairs: list[tuple[int, set[str], set[str]]] = []
        for idx, block in enumerate(blocks[1:], 1):
            parts = re.split(r"Réponse attendue\s*:", block, maxsplit=1, flags=re.I)
            if len(parts) < 2:
                continue
            c_terms = _extract_domain_terms(parts[0][:300])
            a_terms = _extract_domain_terms(parts[1][:500])
            if len(c_terms) >= 3 and len(a_terms) >= 3:
                qa_pairs.append((idx, c_terms, a_terms))

        # For each answer, check if it fits another question's consigne
        # better than its own (Jaccard similarity)
        for qi, c_i, a_i in qa_pairs:
            own_sim = len(c_i & a_i) / len(c_i | a_i) if (c_i | a_i) else 0
            for qj, c_j, _a_j in qa_pairs:
                if qi == qj:
                    continue
                cross_sim = len(c_j & a_i) / len(c_j | a_i) if (c_j | a_i) else 0
                # Flag if answer fits another question 3x better AND own fit is very low
                if cross_sim > 0.25 and own_sim < 0.05 and cross_sim > 3 * max(own_sim, 0.01):
                    rel = f.relative_to(ROOT)
                    hits.append(
                        f"{rel}:Q{qi}: réponse probable de Q{qj} "
                        f"(sim_propre={own_sim:.2f}, sim_croisée={cross_sim:.2f})"
                    )
                    break  # one hit per question suffices

    return hits


def main() -> None:
    files = _scan_files()
    all_hits: list[str] = []

    checkers = [
        ("TCO_NON_TERMINAL", check_tco_non_terminal),
        ("LOCALSTORAGE_DOMAIN", check_localstorage_domain),
        ("GREEDY_MONTANT_3", check_greedy_montant_3),
        ("ROTATION_CONSIGNE_REPONSE", check_rotation_consigne_reponse),
    ]

    for name, checker in checkers:
        hits = checker(files)
        if hits:
            print(f"\n[{name}] {len(hits)} occurrence(s):")
            for h in hits:
                print(f"  {h}")
            all_hits.extend(hits)

    if all_hits:
        print(f"\ncheck_closed_error_classes: FAIL ({len(all_hits)} hit(s))")
        sys.exit(1)
    else:
        print("check_closed_error_classes: PASS (0 hits)")


if __name__ == "__main__":
    main()
