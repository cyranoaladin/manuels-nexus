#!/usr/bin/env python3
"""Dimension de certification `print` — préflight des PDF, lié au HEAD candidat.

Portée : les cibles PDF déclarées `CANONICAL_RELEASE_PRODUCT` par
`RELEASE_DELIVERABLE_SCOPE_MATRIX`, prises dans le répertoire des candidats.

Une preuve ancienne ne peut pas verdir la dimension. Le producteur enregistre
donc `evidence_head` (le HEAD courant) **et** `artifact_source_head` (le HEAD
auquel les PDF ont été construits, tel que déclaré par le manifeste des
candidats). Toute divergence est un constat bloquant : le préflight décrit
alors des octets qui ne sont plus ceux du dépôt.

Contrôles réellement exécutés sur chaque PDF :
polices non incorporées, glyphes manquants, liens internes cassés, signets
cassés, pages blanches accidentelles, débordement hors zone d'impression sûre,
artefacts TeX visibles, fuite de contenu professeur dans une variante élève.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import certification_dimensions as cd  # noqa: E402

ROOT = cd.ROOT
CANDIDATES = ROOT / "audit/CERTIFIED_UNSIGNED_RELEASE_CANDIDATES.json"
OUTPUT = ROOT / "audit/DIMENSION_PRINT.json"
PRODUCER_VERSION = "1.0.0"

#: Marge de sécurité d'impression, en points PostScript (~10 mm).
#:
#: Cette valeur est **provisoire** : aucune charte du dépôt ne déclare de zone
#: sûre de rognage. `audit/1SPE_MARGIN_CONTENT_CONTRACT.json` déclare au
#: contraire les notes de marge comme `EXPECTED_VISIBLE_MARGIN_CONTENT`, donc
#: du contenu voulu. Les constats produits ici sont donc **non bloquants** et
#: attendent une spécification d'impression humaine ; les transformer en
#: bloqueurs reviendrait à inventer un seuil.
SAFE_MARGIN_PT = 28.35

#: Traces qu'un moteur TeX laisse quand une commande n'a pas été résolue.
TEX_ARTIFACT = re.compile(r"\?\?|\\[a-zA-Z]+\{|Overfull|Underfull|\[\?\]|<undefined>")

#: Marqueurs de contenu réservé à l'enseignant.
#:
#: On cible les **substantifs accentués** et les intitulés de rubrique, jamais
#: une forme conjuguée : « si l'on corrige une faute de frappe » est un énoncé
#: d'exercice parfaitement légitime dans une variante élève, et une recherche
#: sur « corrig[ée] » le signalait à tort.
TEACHER_MARKERS = re.compile(
    r"\bCorrigé[s]?\b|\bBarème[s]?\b|\bRéponse attendue\b|\bÉléments de correction\b"
)


def _pdffonts_non_embedded(path: Path) -> list[str]:
    result = subprocess.run(["pdffonts", str(path)], capture_output=True, text=True)
    if result.returncode != 0:
        return ["pdffonts a échoué"]
    offenders = []
    for line in result.stdout.splitlines()[2:]:
        columns = line.split()
        if len(columns) >= 5 and columns[-4] == "no":  # colonne "emb"
            offenders.append(columns[0])
    return offenders


def _is_deliberate_parity_page(document, index: int) -> bool:
    """Un verso blanc qui précède une ouverture de section est voulu.

    `\\cleardoublepage` insère une page paire vide pour que le chapitre suivant
    commence sur un recto. Compter ces pages comme accidentelles reviendrait à
    signaler la mise en page comme un défaut.
    """
    if index % 2 != 0:
        return False  # un recto blanc n'est jamais une page de parité
    if index >= document.page_count:
        return False
    following = document[index].get_text("text").strip()
    if not following:
        return False
    starts_section = any(
        level_title[2] == index + 1 for level_title in document.get_toc()
    )
    return starts_section or index <= 4  # les liminaires suivent la même règle


def _inspect(path: Path, variant: str, evidence: cd.DimensionEvidence, target: str) -> dict[str, Any]:
    import fitz

    document = fitz.open(path)
    stats = {"pages": document.page_count, "blank_pages": 0, "outside_safe_area": 0}

    for name in _pdffonts_non_embedded(path):
        evidence.findings.append(cd.Finding(
            target=target, code="MISSING_FONT",
            detail=f"police non incorporée : {name}",
        ))

    for index, page in enumerate(document, start=1):
        text = page.get_text("text")
        drawings = page.get_drawings()
        images = page.get_images()

        if not text.strip() and not drawings and not images:
            stats["blank_pages"] += 1
            if not _is_deliberate_parity_page(document, index):
                evidence.findings.append(cd.Finding(
                    target=target, code="ACCIDENTAL_BLANK_PAGE",
                    detail=f"page {index} sans texte, tracé ni image",
                ))

        if "�" in text or ".notdef" in text:
            evidence.findings.append(cd.Finding(
                target=target, code="MISSING_GLYPH",
                detail=f"page {index} contient un glyphe de remplacement",
            ))

        artifact = TEX_ARTIFACT.search(text)
        if artifact:
            evidence.findings.append(cd.Finding(
                target=target, code="VISIBLE_TEX_ARTIFACT",
                detail=f"page {index} : {artifact.group(0)!r}",
            ))

        rect = page.rect
        safe = fitz.Rect(
            rect.x0 + SAFE_MARGIN_PT, rect.y0 + SAFE_MARGIN_PT,
            rect.x1 - SAFE_MARGIN_PT, rect.y1 - SAFE_MARGIN_PT,
        )
        for block in page.get_text("blocks"):
            box = fitz.Rect(block[:4])
            if not box.is_empty and not safe.contains(box):
                stats["outside_safe_area"] += 1
                break  # on compte la page, on n'inonde pas la liste de constats

        for link in page.get_links():
            if link.get("kind") == fitz.LINK_GOTO and not (
                0 <= link.get("page", -1) < document.page_count
            ):
                evidence.findings.append(cd.Finding(
                    target=target, code="BROKEN_INTERNAL_LINK",
                    detail=f"page {index} pointe vers une page inexistante",
                ))

        if variant == "eleve":
            leak = TEACHER_MARKERS.search(text)
            if leak:
                evidence.findings.append(cd.Finding(
                    target=target, code="TEACHER_CONTENT_LEAK",
                    detail=f"page {index} : {leak.group(0)!r} dans une variante élève",
                ))

    for level, title, page_number in document.get_toc():
        if not 1 <= page_number <= document.page_count:
            evidence.findings.append(cd.Finding(
                target=target, code="BROKEN_BOOKMARK",
                detail=f"signet {title!r} vers la page {page_number}",
            ))

    document.close()
    return stats


def build() -> dict[str, Any]:
    manifest = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    artifact_head = manifest.get("head_commit")
    head = cd.current_head()

    evidence = cd.DimensionEvidence(
        dimension="print",
        scope="les 12 cibles PDF canoniques (manuels élève et professeur)",
        producer="scripts/build_dimension_print.py",
        producer_version=PRODUCER_VERSION,
        evidence_head=head,
        input_digest="",
    )

    if artifact_head != head:
        evidence.findings.append(cd.Finding(
            target="ALL", code="STALE_PREFLIGHT_ARTIFACTS",
            detail=(
                f"les PDF examinés ont été construits au HEAD {artifact_head}, "
                f"le HEAD candidat est {head} : ce préflight ne décrit pas le dépôt courant"
            ),
        ))

    inputs = [CANDIDATES]
    examined = []
    per_target = {}
    for record in manifest.get("records", []):
        path = ROOT / record["staged_candidate_path"]
        target = record["target_id"]
        if not path.is_file():
            evidence.findings.append(cd.Finding(
                target=target, code="CANDIDATE_PDF_ABSENT",
                detail=str(record["staged_candidate_path"]),
            ))
            continue
        inputs.append(path)
        examined.append(target)
        per_target[target] = _inspect(path, record.get("variant", ""), evidence, target)

    outside = sum(row.get("outside_safe_area", 0) for row in per_target.values())
    if outside:
        evidence.findings.append(cd.Finding(
            target="ALL", code="OUTSIDE_PROVISIONAL_SAFE_PRINT_AREA",
            detail=(
                f"{outside} page(s) portent un bloc à moins de {SAFE_MARGIN_PT:.0f}pt "
                "du bord. Seuil provisoire : aucune charte ne déclare de zone sûre, "
                "et les notes de marge sont contractuellement du contenu visible. "
                "Constat non bloquant, en attente d'une spécification d'impression."
            ),
            blocking=False,
        ))

    evidence.input_digest = cd.digest_inputs(inputs)
    evidence.input_paths = cd.relative_paths(inputs)
    evidence.coverage = {
        "targets_examined": examined,
        "artifact_source_head": artifact_head,
        "per_target": per_target,
    }

    payload = cd.render_evidence(evidence)
    codes = [f.code for f in evidence.findings]
    payload["summary"] = {
        code: codes.count(code) for code in sorted(set(codes))
    } or {"NO_FINDINGS": 0}
    return payload


def write(payload: dict[str, Any]) -> dict[str, Any]:
    """Depose la preuve. Seule etape qui touche le disque."""
    OUTPUT.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    if args.check:
        if not OUTPUT.is_file():
            print("DIMENSION_PRINT check: MISSING")
            return 1
        if json.loads(OUTPUT.read_text(encoding="utf-8")) != payload:
            print("DIMENSION_PRINT check: STALE")
            return 1
        print("DIMENSION_PRINT check: OK")
        return 0
    write(payload)
    print(json.dumps({"status": payload["status"], **payload["summary"]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
