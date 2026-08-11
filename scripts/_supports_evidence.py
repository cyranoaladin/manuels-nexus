#!/usr/bin/env python3
"""Indexation des preuves de couverture issues de l'arbre `03_progressions/supports/`.

Module ADDITIF : il ne modifie pas `_qa_common.py` (importé par ~137 scripts) et
réutilise ses primitives. Il fournit `iter_support_evidence()`, homologue de
`iter_declared_evidence()` mais pour le modèle « supports par unité ».

Différence de modèle :
  - les séquences pilotes déclarent des preuves ANCRÉES par capacité dans le
    frontmatter (`official_program.capacities[].evidence[]`) ;
  - les unités supports déclarent, par DOCUMENT, son `document_type`, son
    `status` et une liste plate `official_program.capacities` (des identifiants).
    La preuve est donc au niveau du fichier, son type vient du `document_type`.

Conséquence honnête : tant que les documents supports restent `needs_review`,
les capacités qu'ils couvrent remontent en `needs_review` (et non `covered`).
Le module ne fabrique aucune validation ; il rend visible l'existant.
"""

from __future__ import annotations

from collections import Counter
from typing import Any, Iterable

from scripts._qa_common import ROOT, Evidence, get_status, read_frontmatter

SUPPORTS_DIR = ROOT / "03_progressions" / "supports"

# `document_type` (frontmatter supports) -> type de preuve attendu par la
# logique de couverture (REQUIRED_EVIDENCE = cours, trace, td, tp, evaluation,
# corrige). Les types hors socle (bareme, remediation, version_amenagee) sont
# conservés pour la traçabilité mais ne comblent aucune preuve requise.
DOCTYPE_TO_EVIDENCE = {
    "cours": "cours",
    "trace": "trace",
    "td": "td",
    "tp": "tp",
    "tp_papier": "tp",
    "corrige": "corrige",
    "evaluation": "evaluation",
    "qcm": "qcm",
    "bareme": "bareme",
    "remediation": "remediation",
    "version_amenagee": "version_amenagee",
}


def _capacities_from_frontmatter(metadata: dict[str, Any]) -> list[str]:
    official = metadata.get("official_program")
    if not isinstance(official, dict):
        return []
    caps = official.get("capacities")
    if not isinstance(caps, list):
        return []
    out: list[str] = []
    for c in caps:
        if isinstance(c, str) and c.strip():
            out.append(c.strip())
        elif isinstance(c, dict) and c.get("id"):  # tolérance au format riche
            out.append(str(c["id"]).strip())
    return out


def iter_support_evidence() -> Iterable[Evidence]:
    """Émet une Evidence par (capacité, document support)."""
    if not SUPPORTS_DIR.exists():
        return
    for path in sorted(SUPPORTS_DIR.rglob("*.md")):
        # ignorer un éventuel dossier contracts/ (pas de frontmatter doc)
        if "contracts" in path.parts:
            continue
        metadata = read_frontmatter(path)
        if not metadata:
            continue
        doctype = str(metadata.get("document_type") or "").strip().strip('"')
        evidence_type = DOCTYPE_TO_EVIDENCE.get(doctype, doctype)
        status = get_status(metadata)
        rel = path.relative_to(ROOT).as_posix()
        for cap_id in _capacities_from_frontmatter(metadata):
            yield Evidence(
                capacity_id=cap_id,
                label="",
                file=rel,
                anchor="",  # modèle support : preuve au niveau fichier
                evidence_type=evidence_type,
                document_path=path,
                status=status,
            )


if __name__ == "__main__":
    from collections import Counter

    by_cap: dict[str, set[str]] = {}
    types: Counter[str] = Counter()
    for ev in iter_support_evidence():
        by_cap.setdefault(ev.capacity_id, set()).add(ev.evidence_type)
        types[ev.evidence_type] += 1
    print(f"capacités touchées par supports : {len(by_cap)}")
    print(f"preuves émises par type : {dict(types)}")
