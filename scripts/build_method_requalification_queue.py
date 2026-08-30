#!/usr/bin/env python3
"""File de re-qualification des fiches methode perimees par les accents.

La campagne diacritiques a modifie des fiches dont la qualification humaine
etait liee au sha256 du fichier. Le gate les declare STALE, ce qui est le
comportement voulu : une decision humaine porte sur un texte precis, et le
texte a change.

Cet artefact ne reconstitue AUCUNE approbation. Il produit la liste de travail
du relecteur humain et, pour chaque fiche, une information verifiable qui lui
fait gagner du temps sans decider a sa place : le changement est-il
EXCLUSIVEMENT diacritique ? La reponse est calculee en depouillant les deux
versions de leurs accents et en les comparant octet a octet. `ACCENT_ONLY`
signifie que rien d'autre n'a bouge -- ni un chiffre, ni une formule, ni un
mot. Cela reste une information, pas une autorisation : seul l'humain peut
re-qualifier.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import unicodedata
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
DISPOSITIONS = ROOT / "audit/ANOMALY_DISPOSITIONS.yaml"
OUT_JSON = ROOT / "audit/METHOD_REQUALIFICATION_QUEUE.json"
OUT_MD = ROOT / "audit/METHOD_REQUALIFICATION_QUEUE.md"


def strip_accents(text: str) -> str:
    decomposed = unicodedata.normalize("NFD", text)
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


def classify_change(before: str, after: str) -> str:
    """ACCENT_ONLY seulement si le texte desaccentue est rigoureusement egal."""

    if before == after:
        return "UNCHANGED"
    if strip_accents(before) == strip_accents(after):
        return "ACCENT_ONLY"
    return "SUBSTANTIVE_CHANGE"


def _blob_at(rev: str, relative: str) -> str | None:
    result = subprocess.run(
        ["git", "show", f"{rev}:{relative}"],
        cwd=ROOT,
        capture_output=True,
    )
    if result.returncode != 0:
        return None
    return result.stdout.decode("utf-8")


def _qualified_blob(relative: str, qualified_sha: str) -> str | None:
    """Contenu du fichier a la revision ou son sha256 valait `qualified_sha`."""

    revisions = subprocess.run(
        ["git", "rev-list", "HEAD", "--", relative],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    for revision in revisions.stdout.split():
        blob = subprocess.run(
            ["git", "show", f"{revision}:{relative}"],
            cwd=ROOT,
            capture_output=True,
        )
        if blob.returncode != 0:
            continue
        if hashlib.sha256(blob.stdout).hexdigest() == qualified_sha:
            return blob.stdout.decode("utf-8")
    return None


def build_queue() -> dict[str, Any]:
    """La comparaison se fait contre le texte exact qui a ete qualifie.

    Deux references plus commodes sont fausses. HEAD est instable : sitot la
    correction commitee, il porte le texte modifie et le changement s'evanouit.
    `baseline_sha` ne convient pas davantage : c'est la baseline du jeu
    d'anomalies, et non la revision du contenu -- 72 fiches n'y existent meme
    pas encore.

    Ce que la decision humaine a reellement fige, c'est `method_source_sha`.
    On remonte donc l'historique du fichier jusqu'a la revision dont le
    contenu porte ce condense : c'est, par construction, le texte approuve.
    """

    document = yaml.safe_load(DISPOSITIONS.read_text(encoding="utf-8"))
    dispositions = document.get("dispositions", document)

    items: list[dict[str, Any]] = []
    current = 0
    for fingerprint, record in sorted(dispositions.items()):
        qualified_sha = record.get("method_source_sha")
        if not qualified_sha:
            continue
        relative = str(record.get("source", ""))
        path = ROOT / relative
        if not path.is_file():
            items.append(
                {
                    "fingerprint": fingerprint,
                    "source": relative,
                    "state": "SOURCE_MISSING",
                    "qualified_source_sha": qualified_sha,
                }
            )
            continue
        after = path.read_text(encoding="utf-8")
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual == qualified_sha:
            current += 1
            continue
        before = _qualified_blob(relative, qualified_sha)
        items.append(
            {
                "fingerprint": fingerprint,
                "manual": record.get("manual"),
                "chapter": record.get("chapter"),
                "source": relative,
                "state": "STALE",
                "qualified_source_sha": qualified_sha,
                "current_source_sha": actual,
                "change_class": (
                    classify_change(before, after)
                    if before is not None
                    else "PREVIOUS_REVISION_UNAVAILABLE"
                ),
                "review_packet": record.get("review_packet"),
                "owner": record.get("owner"),
                "release_blocking": True,
                "requalification": "REQUIRED_HUMAN",
            }
        )

    stale = [item for item in items if item["state"] == "STALE"]
    classes: dict[str, int] = {}
    for item in stale:
        classes[item["change_class"]] = classes.get(item["change_class"], 0) + 1
    chapters: dict[str, int] = {}
    for item in stale:
        chapters[str(item["chapter"])] = chapters.get(str(item["chapter"]), 0) + 1

    return {
        "artifact_type": "method_requalification_queue",
        "schema_version": 1,
        "approves_nothing": True,
        "machine_cannot_requalify": True,
        "cause": (
            "campagne diacritiques editoriales : la correction des formes non "
            "ambigues modifie le texte qualifie, donc le sha lie a la decision"
        ),
        "compared_against": "method_source_sha de chaque qualification",
        "totals": {
            "method_qualifications": current + len(items),
            "still_current": current,
            "stale_requiring_human_requalification": len(stale),
        },
        "change_classes": dict(sorted(classes.items())),
        "stale_by_chapter": dict(sorted(chapters.items())),
        "items": items,
    }


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def render_markdown(payload: dict[str, Any]) -> str:
    totals = payload["totals"]
    lines = [
        "# File de re-qualification des fiches méthode",
        "",
        "Artefact généré. Il **n'approuve rien** et ne peut pas re-qualifier :",
        "seule une décision humaine rétablit une qualification périmée.",
        "",
        f"- qualifications liées à une fiche méthode : {totals['method_qualifications']}",
        f"- encore à jour : {totals['still_current']}",
        f"- **périmées, à re-qualifier par un humain : "
        f"{totals['stale_requiring_human_requalification']}**",
        "",
        "## Nature du changement",
        "",
        "`ACCENT_ONLY` signifie que les deux versions, dépouillées de leurs",
        "accents, sont rigoureusement identiques : aucune formule, aucun",
        "chiffre, aucun mot n'a bougé. C'est une information pour le relecteur,",
        "pas une autorisation.",
        "",
    ]
    for name, count in payload["change_classes"].items():
        lines.append(f"- `{name}` : {count}")
    lines += ["", "## Par chapitre", ""]
    for chapter, count in payload["stale_by_chapter"].items():
        lines.append(f"- {chapter} : {count}")
    lines.append("")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    payload = build_queue()
    if args.write:
        OUT_JSON.write_text(render_json(payload), encoding="utf-8")
        OUT_MD.write_text(render_markdown(payload), encoding="utf-8")
    totals = payload["totals"]
    print(
        f"qualifications {totals['method_qualifications']} | a jour "
        f"{totals['still_current']} | perimees "
        f"{totals['stale_requiring_human_requalification']} | "
        f"{payload['change_classes']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
