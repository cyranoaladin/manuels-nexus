#!/usr/bin/env python3
"""Dimension de certification `regulation` — conformité aux programmes officiels.

Portée : les six manuels de la collection. Pour chacun, l'autorité réglementaire
est le référentiel de capacités déposé (`referentiel/capacites_*.json`), lui-même
adossé à un arrêté publié au BO.

Trois exigences, mesurées et non affirmées :

    WRONG_YEAR_AUTHORITY              autorités divergentes ou non identifiées
    OFFICIAL_REQUIREMENTS_UNCOVERED   capacités officielles sans aucun objet
    UNLABELLED_OUT_OF_PROGRAMME_CONTENT
                                      objets hors référentiel non étiquetés

La troisième distingue deux choses que confondrait un simple `set - set` : les
alias locaux de chapitre (`C1`, `TSPE-TRIGONOMETRIE-C1`) et les compétences du
préambule (`BO-PREAMBULE-*`) sont des espaces de nommage internes, pas du
contenu hors programme. Seul un code qui n'appartient ni au référentiel ni à ces
espaces, et qui n'est pas explicitement marqué `OPTIONAL_EXTENSION`, est un
constat bloquant.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict

import yaml
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import certification_dimensions as cd  # noqa: E402

ROOT = cd.ROOT
OUTPUT = ROOT / "audit/DIMENSION_REGULATION.json"
PRODUCER_VERSION = "1.0.0"

REFERENTIAL_DIRS = ("NSI/referentiel", "Mathematiques/manuel-maths/referentiel")
MANUAL_TO_LEVEL = {
    "1NSI": "1NSI", "TNSI": "TNSI", "1SPE": "1SPE",
    "TSPE_2026_2027": "TSPE", "TCOMPL": "TCOMPL", "TEXPERTES": "TEXPERTES",
}

NOR_PATTERN = re.compile(r"MEN[A-Z]\d{7}[A-Z]")

#: Une référence contient souvent une date de *vérification* (« Vérifié le
#: 2026-08-06 ») en plus de la date du programme. Confondre les deux faisait
#: conclure à une divergence d'autorité entre deux fichiers citant pourtant le
#: même arrêté. On tronque donc la chaîne au premier marqueur de vérification.
VERIFICATION_MARKER = re.compile(r"\bv[ée]rifi[ée]?e?\s+le\b", re.I)

#: Le programme lui-même est identifié par son bulletin : « BO spécial n°8 du
#: 25 juillet 2019 », « BO n° 14 du 2 avril 2026 ».
PROGRAMME_ISSUE = re.compile(
    r"BO\s*(?:sp[ée]cial\s*)?n\s*[°o]?\s*(\d+)\s+du\s+(\d{1,2})\s+"
    r"(janvier|f[ée]vrier|mars|avril|mai|juin|juillet|ao[ûu]t|septembre|octobre|novembre|d[ée]cembre)"
    r"\s+((?:19|20)\d{2})",
    re.I,
)
#: Espaces de nommage internes : alias de chapitre et compétences du préambule.
LOCAL_ALIAS = re.compile(r"^(C\d+|[A-Z0-9_]+-[A-Z0-9-]+-C\d+|BO-PREAMBULE-[A-Z-]+)$")
UNVERIFIED_MARKER = re.compile(r"a re-verifier|à re-vérifier", re.I)


def load_referentials() -> tuple[dict[str, dict[str, Any]], dict[str, list[dict[str, Any]]]]:
    capacities: dict[str, dict[str, Any]] = defaultdict(dict)
    authorities: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for directory in REFERENTIAL_DIRS:
        base = ROOT / directory
        if not base.is_dir():
            continue
        for path in sorted(base.glob("capacites_*.json")):
            payload = json.loads(path.read_text(encoding="utf-8"))
            level = payload.get("niveau")
            reference = str(payload.get("bo_reference", ""))
            marker = VERIFICATION_MARKER.search(reference)
            programme_part = reference[: marker.start()] if marker else reference
            issue = PROGRAMME_ISSUE.search(programme_part)
            # La provenance appartient au bloc `authority`, résolu depuis la
            # matrice ; le NOR n'a pas à être répété dans la phrase de
            # référence, ni injecté dans le texte de l'annexe officielle.
            declared_authority = payload.get("authority") or {}
            declared_nor = str(declared_authority.get("nor") or "")
            authorities[level].append({
                "file": str(path.relative_to(ROOT)),
                "bo_reference": reference,
                "authority": declared_authority,
                "nor": sorted(
                    set(NOR_PATTERN.findall(reference))
                    | ({declared_nor} if NOR_PATTERN.fullmatch(declared_nor) else set())
                ),
                "programme_issue": (
                    f"BO n°{issue.group(1)} du {issue.group(2)} {issue.group(3).lower()} "
                    f"{issue.group(4)}"
                    if issue else (declared_authority.get("bulletin") or None)
                ),
                "programme_year": issue.group(4) if issue else None,
                "self_declared_unverified": bool(UNVERIFIED_MARKER.search(reference)),
            })
            for capacity in payload.get("capacites", []):
                capacities[level][capacity["id"]] = {
                    "theme": payload.get("theme"),
                    "referential_file": path.name,
                    "contenu_bo": capacity.get("contenu_bo", ""),
                }
    return capacities, authorities


def chapter_code_map(chapter_dir: Path) -> dict[str, str]:
    """Traduction des codes locaux d'un chapitre vers les capacités officielles.

    Chaque `contrat.yaml` déclare `- {code: C1, ref_capacite: T-STRUCT-01A, …}`.
    Les objets ne portent souvent que le code local dans `capacites_codes` ;
    ignorer cette table reviendrait à déclarer non couvertes des capacités que
    le manuel enseigne réellement.
    """
    contract = chapter_dir / "contrat.yaml"
    if not contract.is_file():
        return {}
    try:
        payload = yaml.safe_load(contract.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError:
        return {}
    mapping: dict[str, list[str]] = {}
    for entry in payload.get("capacites") or []:
        if not isinstance(entry, dict) or not entry.get("code") or not entry.get("ref_capacite"):
            continue
        reference = entry["ref_capacite"]
        # Un code local peut couvrir plusieurs capacités officielles quand le
        # programme regroupe ou scinde une rubrique.
        references = reference if isinstance(reference, list) else [reference]
        mapping[str(entry["code"])] = [str(r) for r in references]
    return mapping


def declared_by_manual() -> dict[str, dict[str, list[str]]]:
    inventory = json.loads((ROOT / "audit/INVENTAIRE_COLLECTION.json").read_text(encoding="utf-8"))
    result: dict[str, dict[str, list[str]]] = {}
    for manual, mval in inventory.get("manuals", {}).items():
        codes: dict[str, list[str]] = defaultdict(list)
        for chapter, cval in mval.get("chapters", {}).items():
            local_map: dict[str, str] | None = None
            for obj in cval.get("objects", []):
                path = ROOT / obj["path"]
                if not path.is_file():
                    continue
                if local_map is None:
                    local_map = chapter_code_map(path.parent.parent)
                first = path.read_text(encoding="utf-8", errors="replace").split("\n", 1)[0]
                if not first.startswith("% META:"):
                    continue
                meta = json.loads(first[len("% META:"):])
                extension = (
                    meta.get("programme_alignment") == "OPTIONAL_EXTENSION"
                    or bool(meta.get("extension_codes"))
                )
                label = f"{obj['id']}|{'EXT' if extension else 'STD'}"
                for code in meta.get("capacites") or []:
                    codes[code].append(label)
                # Un objet peut ne porter que ses codes locaux : on les résout
                # par la table du contrat de chapitre.
                for code in meta.get("capacites_codes") or []:
                    official = (local_map or {}).get(str(code))
                    for resolved in official or [str(code)]:
                        codes[resolved].append(label)
        result[manual] = dict(codes)
    return result


def build() -> dict[str, Any]:
    capacities, authorities = load_referentials()
    declared = declared_by_manual()

    inputs = [ROOT / "audit/INVENTAIRE_COLLECTION.json"]
    for directory in REFERENTIAL_DIRS:
        inputs.extend(sorted((ROOT / directory).glob("capacites_*.json")))

    evidence = cd.DimensionEvidence(
        dimension="regulation",
        scope="les six manuels de la collection, contre leur référentiel de capacités déposé",
        producer="scripts/build_dimension_regulation.py",
        producer_version=PRODUCER_VERSION,
        evidence_head=cd.current_head(),
        input_digest=cd.digest_inputs(inputs),
        input_paths=cd.relative_paths(inputs),
    )

    examined = []
    coverage_rows = {}
    for manual, level in sorted(MANUAL_TO_LEVEL.items()):
        official = capacities.get(level, {})
        if not official:
            evidence.findings.append(cd.Finding(
                target=manual, code="NO_OFFICIAL_REFERENTIAL",
                detail=f"aucun référentiel déposé pour le niveau {level}",
            ))
            continue
        examined.append(manual)
        codes = declared.get(manual, {})

        # 1. autorité
        entries = authorities.get(level, [])
        nors = {tuple(e["nor"]) for e in entries if e["nor"]}
        missing_nor = [e["file"] for e in entries if not e["nor"]]
        unverified = [e["file"] for e in entries if e["self_declared_unverified"]]
        issues = {e["programme_issue"] for e in entries if e["programme_issue"]}
        undated = [e["file"] for e in entries if not e["programme_issue"]]
        if len(nors) > 1:
            evidence.findings.append(cd.Finding(
                target=manual, code="WRONG_YEAR_AUTHORITY",
                detail=f"NOR divergents dans un même niveau : {sorted(nors)}",
            ))
        if missing_nor:
            evidence.findings.append(cd.Finding(
                target=manual, code="AUTHORITY_NOR_ABSENT",
                detail=f"{len(missing_nor)} référentiel(s) sans NOR identifiable : {missing_nor[:3]}",
            ))
        if unverified:
            evidence.findings.append(cd.Finding(
                target=manual, code="AUTHORITY_SELF_DECLARED_UNVERIFIED",
                detail=f"{len(unverified)} référentiel(s) portent « à re-vérifier contre le BO »",
            ))
        if len(issues) > 1:
            per_issue = {
                issue: sorted(
                    Path(e["file"]).name for e in entries if e["programme_issue"] == issue
                )
                for issue in sorted(issues)
            }
            evidence.findings.append(cd.Finding(
                target=manual, code="PROGRAMME_AUTHORITY_DIVERGENCE",
                detail=(
                    "deux programmes différents cités dans un même niveau : "
                    + "; ".join(f"{k} -> {v}" for k, v in per_issue.items())
                ),
            ))
        if undated:
            evidence.findings.append(cd.Finding(
                target=manual, code="PROGRAMME_ISSUE_UNIDENTIFIABLE",
                detail=f"{len(undated)} référentiel(s) sans bulletin identifiable : {undated[:3]}",
            ))

        # 2. couverture
        uncovered = sorted(set(official) - set(codes))
        for code in uncovered:
            evidence.findings.append(cd.Finding(
                target=f"{manual}::{code}", code="OFFICIAL_REQUIREMENT_UNCOVERED",
                detail=f"{official[code]['theme']} — {official[code]['contenu_bo']}",
            ))

        # 3. contenu hors programme non étiqueté
        unlabelled = []
        for code, refs in sorted(codes.items()):
            if code in official or LOCAL_ALIAS.match(code):
                continue
            if all(ref.endswith("|EXT") for ref in refs):
                continue  # explicitement marqué OPTIONAL_EXTENSION
            unlabelled.append(code)
        for code in unlabelled:
            evidence.findings.append(cd.Finding(
                target=f"{manual}::{code}", code="UNLABELLED_OUT_OF_PROGRAMME_CONTENT",
                detail="code de capacité hors référentiel, sans marquage OPTIONAL_EXTENSION",
            ))

        coverage_rows[manual] = {
            "official_capacities": len(official),
            "covered": len(set(official) & set(codes)),
            "uncovered": len(uncovered),
            "unlabelled_out_of_programme": len(unlabelled),
        }

    evidence.coverage = {"targets_examined": examined, "per_manual": coverage_rows}
    payload = cd.write_evidence(evidence, OUTPUT)
    payload["summary"] = {
        "AUTHORITY_DIVERGENCES": sum(
            1 for f in evidence.findings
            if f.code in {"WRONG_YEAR_AUTHORITY", "PROGRAMME_AUTHORITY_DIVERGENCE"}
        ),
        "REGULATORY_SOURCES_WITHOUT_AUTHORITY": sum(
            1 for f in evidence.findings
            if f.code in {"AUTHORITY_NOR_ABSENT", "PROGRAMME_ISSUE_UNIDENTIFIABLE"}
        ),
        "REGULATORY_SOURCE_REVERIFY_PENDING": sum(
            1 for f in evidence.findings if f.code == "AUTHORITY_SELF_DECLARED_UNVERIFIED"
        ),
        "OFFICIAL_REQUIREMENTS_UNCOVERED": sum(
            1 for f in evidence.findings if f.code == "OFFICIAL_REQUIREMENT_UNCOVERED"
        ),
        "UNLABELLED_OUT_OF_PROGRAMME_CONTENT": sum(
            1 for f in evidence.findings if f.code == "UNLABELLED_OUT_OF_PROGRAMME_CONTENT"
        ),
    }
    OUTPUT.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        if not OUTPUT.is_file():
            print("DIMENSION_REGULATION check: MISSING")
            return 1
        previous = json.loads(OUTPUT.read_text(encoding="utf-8"))
        payload = build()
        if previous == payload:
            print("DIMENSION_REGULATION check: OK")
            return 0
        print("DIMENSION_REGULATION check: STALE")
        return 1
    payload = build()
    print(json.dumps({"status": payload["status"], **payload["summary"]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
