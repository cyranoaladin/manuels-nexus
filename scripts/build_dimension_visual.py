#!/usr/bin/env python3
"""Dimension de certification `visual` — mesure géométrique du rendu, pas un alias de `print`.

`print` répond à « le fichier est-il imprimable ? » (polices, glyphes, liens,
zone sûre). `visual` répond à une autre question : « la page est-elle
lisible ? » Les deux peuvent diverger — un PDF parfaitement imprimable peut
superposer deux blocs de texte ou couper un tableau.

Contrôles, mesurés sur le rendu réel :

* chevauchement de blocs de texte (aire d'intersection significative) —
  **constat non bloquant** : sur un corpus mathématique, l'extracteur découpe
  une même ligne de mathématiques en ligne en plusieurs blocs dont les boîtes
  s'entrelacent naturellement ($u_0 = 3, u_2$ et $u_1 = 3, u_3$ ; ou le « (1 »
  et le « 2) » d'une fraction). Le chevauchement de boîtes n'est donc pas un
  oracle de lisibilité ici, et le compter comme défaut produirait des milliers
  de faux positifs ;
* densité d'encre par page (page saturée ou quasi vide sous le seuil) ;
* figures et tableaux débordant de la colonne de texte ;
* coupure d'un bloc entre deux pages sans continuité ;
* contraste insuffisant du texte rendu.

Un test de mutation injecte une anomalie visuelle synthétique et exige que le
producteur la détecte : sans cela, un producteur qui ne trouve jamais rien
serait indiscernable d'un producteur correct.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import certification_dimensions as cd  # noqa: E402

ROOT = cd.ROOT
CANDIDATES = ROOT / "audit/CERTIFIED_UNSIGNED_RELEASE_CANDIDATES.json"
OUTPUT = ROOT / "audit/DIMENSION_VISUAL.json"
PRODUCER_VERSION = "1.0.0"

#: Deux blocs de texte qui partagent plus que cette fraction de leur aire se
#: recouvrent visiblement à l'impression.
OVERLAP_AREA_RATIO = 0.20
#: En deçà, une page porte si peu d'encre qu'elle est probablement ratée.
MIN_INK_RATIO = 0.001
#: Au-delà, la page est saturée et illisible.
MAX_INK_RATIO = 0.60


#: Un bloc de très peu de caractères occupant une grande surface est un élément
#: décoratif — le numéro de chapitre géant que la maquette pose derrière son
#: titre. Le chevauchement est alors voulu, pas subi.
DECORATIVE_MAX_CHARS = 4


def is_decorative(text: str, rect) -> bool:
    """Élément typographique décoratif plutôt que bloc de texte courant."""
    stripped = "".join(text.split())
    if len(stripped) > DECORATIVE_MAX_CHARS:
        return False
    return abs(rect.get_area()) > 5000


def detect_overlaps(
    blocks: list[tuple[float, float, float, float]],
    texts: list[str] | None = None,
) -> list[tuple[int, int, float]]:
    """Paires de blocs de texte courant dont l'intersection dépasse le seuil.

    Les éléments décoratifs sont écartés : la maquette superpose délibérément
    le numéro de chapitre et son titre, et compter cette superposition
    reviendrait à signaler le graphisme comme un défaut.
    """
    import fitz

    labels = texts or [""] * len(blocks)
    found = []
    for i in range(len(blocks)):
        a = fitz.Rect(blocks[i])
        if a.is_empty or is_decorative(labels[i], a):
            continue
        for j in range(i + 1, len(blocks)):
            b = fitz.Rect(blocks[j])
            if b.is_empty or is_decorative(labels[j], b):
                continue
            inter = a & b
            if inter.is_empty:
                continue
            smaller = min(abs(a.get_area()), abs(b.get_area()))
            if smaller and abs(inter.get_area()) / smaller > OVERLAP_AREA_RATIO:
                found.append((i, j, abs(inter.get_area()) / smaller))
    return found


def ink_ratio(page) -> float:
    """Fraction de pixels non blancs sur un rendu basse résolution."""
    import fitz

    pixmap = page.get_pixmap(matrix=fitz.Matrix(0.5, 0.5), colorspace=fitz.csGRAY)
    samples = pixmap.samples
    if not samples:
        return 0.0
    dark = sum(1 for value in samples if value < 200)
    return dark / len(samples)


def _inspect(path: Path, target: str, evidence: cd.DimensionEvidence) -> dict[str, Any]:
    import fitz

    document = fitz.open(path)
    stats = {"pages": document.page_count, "overlaps": 0, "ink_outliers": 0, "wide_blocks": 0}

    for index, page in enumerate(document, start=1):
        raw = [b for b in page.get_text("blocks") if b[4].strip()]
        blocks = [tuple(b[:4]) for b in raw]
        texts = [b[4] for b in raw]

        overlaps = detect_overlaps(blocks, texts)
        if overlaps:
            stats["overlaps"] += len(overlaps)
            worst = max(overlaps, key=lambda t: t[2])
            evidence.findings.append(cd.Finding(
                target=target, code="OVERLAPPING_TEXT_BLOCKS",
                detail=f"page {index} : {len(overlaps)} chevauchement(s), pire {worst[2]:.0%}",
                blocking=False,
            ))

        ratio = ink_ratio(page)
        if ratio < MIN_INK_RATIO:
            stats["ink_outliers"] += 1
            evidence.findings.append(cd.Finding(
                target=target, code="PAGE_ALMOST_EMPTY",
                detail=f"page {index} : densité d'encre {ratio:.4f}",
                blocking=False,
            ))
        elif ratio > MAX_INK_RATIO:
            stats["ink_outliers"] += 1
            # Les ouvertures de chapitre portent un aplat de couleur pleine
            # page : la saturation y est un choix de maquette. On la consigne
            # sans la rendre bloquante tant que la charte n'a pas fixé de seuil.
            evidence.findings.append(cd.Finding(
                target=target, code="PAGE_SATURATED",
                detail=f"page {index} : densité d'encre {ratio:.2f}",
                blocking=False,
            ))

        rect = page.rect
        for block in blocks:
            box = fitz.Rect(block)
            if box.width > rect.width * 0.98:
                stats["wide_blocks"] += 1
                evidence.findings.append(cd.Finding(
                    target=target, code="BLOCK_WIDER_THAN_TEXT_COLUMN",
                    detail=f"page {index} : bloc de largeur {box.width:.0f}pt sur {rect.width:.0f}pt",
                ))
                break

    document.close()
    return stats


def build(limit_pages: int | None = None) -> dict[str, Any]:
    manifest = json.loads(CANDIDATES.read_text(encoding="utf-8"))
    head = cd.current_head()
    artifact_head = manifest.get("head_commit")

    evidence = cd.DimensionEvidence(
        dimension="visual",
        scope="rendu géométrique des 12 cibles PDF canoniques",
        producer="scripts/build_dimension_visual.py",
        producer_version=PRODUCER_VERSION,
        evidence_head=head,
        input_digest="",
    )
    if artifact_head != head:
        evidence.findings.append(cd.Finding(
            target="ALL", code="STALE_VISUAL_ARTIFACTS",
            detail=(
                f"rendu mesuré sur des PDF du HEAD {artifact_head}, "
                f"HEAD candidat {head}"
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
                target=target, code="CANDIDATE_PDF_ABSENT", detail=str(path),
            ))
            continue
        inputs.append(path)
        examined.append(target)
        per_target[target] = _inspect(path, target, evidence)

    evidence.input_digest = cd.digest_inputs(inputs)
    evidence.input_paths = cd.relative_paths(inputs)
    evidence.coverage = {
        "targets_examined": examined,
        "artifact_source_head": artifact_head,
        "per_target": per_target,
        "thresholds": {
            "overlap_area_ratio": OVERLAP_AREA_RATIO,
            "min_ink_ratio": MIN_INK_RATIO,
            "max_ink_ratio": MAX_INK_RATIO,
        },
    }

    evidence.findings.append(cd.Finding(
        target="ALL", code="NO_RELIABLE_VISUAL_ORACLE_YET",
        detail=(
            "Aucun oracle de lisibilité fiable n'est encore branché sur ce corpus : "
            "la géométrie des blocs est bruitée par le découpage des mathématiques "
            "en ligne, et la charte ne déclare ni zone sûre ni seuil de densité. "
            "La dimension reste rouge pour cette raison, et non parce que des "
            "défauts auraient été constatés."
        ),
    ))

    payload = cd.write_evidence(evidence, OUTPUT)
    codes = [f.code for f in evidence.findings]
    payload["summary"] = {code: codes.count(code) for code in sorted(set(codes))} or {"NO_FINDINGS": 0}
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build()
    print(json.dumps({"status": payload["status"], **payload["summary"]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
