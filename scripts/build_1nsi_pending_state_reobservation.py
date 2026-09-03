#!/usr/bin/env python3
"""Ré-observation des deux registres d'attente 1NSI : mesurer, ne rien décider.

Deux registres déclarent l'état COURANT d'une campagne de revue 1NSI restée en
attente : `audit/1NSI_CONTENT_REVIEW_CAMPAIGN_STATE.json` et
`audit/1NSI_STATUS_GOVERNANCE_PENDING.json`. Les suites 1NSI comparent leur
contenu à l'arbre vivant et échouent, exprès, dès que les deux divergent.

Le commit `2d522877` a retiré 44 cours qui dupliquaient ou usurpaient un autre
objet. La décision de contenu était prise et elle est committée ; les deux
registres, eux, n'ont pas été ré-observés. Quinze tests échouent donc sur la
même cause, et la cause est une OMISSION D'OBSERVATION, pas un défaut de
contenu.

Ce producteur ré-observe. Il recalcule les champs `observed*` avec les fonctions
mêmes que les tests utilisent, et il ne touche à rien d'autre :

* les champs `sealed*` sont des faits historiques — le commit de scellement, le
  nombre de sources scellées, les condensats d'alors. Ils sont laissés
  identiques, et le producteur échoue s'il les voit changer ;
* `status`, `no_go_carrier` et la nature de l'attente ne sont pas touchés : la
  campagne reste `PENDING`, la revue humaine reste due, et rien ici ne la
  rapproche d'une approbation ;
* `reason` reçoit une ligne datée qui NOMME la cause de la ré-observation.

Ce que ce producteur ne fait pas, et ne doit jamais faire : rendre une suite
verte en modifiant du contenu 1NSI. Il ne lit aucun `.tex` pour le changer.

Métriques bloquantes : `SEALED_FIELDS_MUTATED`, `UNEXPLAINED_DELTA`.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
NSI_ROOT = ROOT / "NSI"
CAMPAIGN_TARGET = ROOT / "audit/1NSI_CONTENT_REVIEW_CAMPAIGN_STATE.json"
STATUS_TARGET = ROOT / "audit/1NSI_STATUS_GOVERNANCE_PENDING.json"
JSON_TARGET = ROOT / "audit/1NSI_PENDING_STATE_REOBSERVATION.json"
MD_TARGET = ROOT / "audit/1NSI_PENDING_STATE_REOBSERVATION.md"
GENERATED_BY = "scripts/build_1nsi_pending_state_reobservation.py"

REVIEW_MODULE = ROOT / "scripts/review_1nsi_content.py"
POLICY_PATH = ROOT / "audit/1NSI_CONTENT_REVIEW_POLICY.yaml"
FINDINGS_PATH = ROOT / "audit/1NSI_CONTENT_REVIEW_FINDINGS.yaml"
REGISTRY_PATH = ROOT / "audit/1NSI_CONTENT_REVIEWS.json"
ADGK_CONTRACT = ROOT / "NSI/chapitres/1NSI-ALGO-DICHO-GLOUTON-KNN/contrat.yaml"
STATUS_POLICY = ROOT / "audit/1NSI_STATUS_GOVERNANCE.yaml"
ALGORITHM_CHAPTERS = {"1NSI-ALGO-PARCOURS-TRIS", "1NSI-ALGO-DICHO-GLOUTON-KNN"}
META = re.compile(r"^% META: (\{.*\})\s*$", re.MULTILINE)

# Les champs qui portent l'histoire : leur valeur ne dépend pas de l'arbre
# courant, et une ré-observation qui les bougerait aurait réécrit le passé.
CAMPAIGN_SEALED_KEY = "sealed"
IMMUTABLE_TOP_LEVEL = ("artifact_name", "created", "status", "no_go_carrier")


class ReobservationError(RuntimeError):
    """Une preuve manque, ou un fait scellé aurait bougé."""


def _reject(message: str) -> None:
    raise ReobservationError(message)


def digest(value: Any) -> str:
    return "sha256:" + hashlib.sha256(
        json.dumps(value, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


def file_digest(path: Path) -> str:
    if not path.is_file():
        _reject(f"preuve absente : {path.relative_to(ROOT)}")
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def load_review_module() -> Any:
    specification = importlib.util.spec_from_file_location(
        "review_1nsi_content_for_reobservation", REVIEW_MODULE
    )
    if specification is None or specification.loader is None:
        _reject(f"module de revue illisible : {REVIEW_MODULE}")
    module = importlib.util.module_from_spec(specification)
    sys.modules[specification.name] = module
    specification.loader.exec_module(module)
    return module


def observe_campaign(module: Any) -> dict[str, Any]:
    """Les champs `observed` du registre de campagne, recalculés."""

    import yaml

    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
    sources = module.discover_sources(ROOT)
    identifiers = sorted(source["id"] for source in sources)
    # Filtre repris LITTERALEMENT de la suite qui le verifie : les sources
    # « contract: » ne sont pas des objets d'algorithmique, et les compter
    # ferait diverger le condensat.
    algorithm_ids = sorted(
        source["id"]
        for source in sources
        if source.get("chapter") in ALGORITHM_CHAPTERS
        and not str(source["id"]).startswith("contract:")
    )
    findings = module.load_findings(FINDINGS_PATH)
    finding_ids = sorted(finding["id"] for finding in findings)
    only_findings = sorted(set(finding_ids) - set(identifiers))
    only_sources = sorted(set(identifiers) - set(finding_ids))
    # Les sources « contract: » decrivent un contrat de chapitre, pas un objet
    # publiable : c'est la difference que ce compteur porte depuis l'origine
    # (861 sources declarees pour 851 objets, soit dix contrats).
    object_sources = [
        source for source in sources if not str(source["id"]).startswith("contract:")
    ]
    return {
        "protocol_digest_current": module.compute_protocol_digest(ROOT, policy),
        "sources_count": len(sources),
        "sources_ids_digest": digest(identifiers),
        "object_sources_count": len(object_sources),
        "algorithm_scope_count": len(algorithm_ids),
        "algorithm_scope_ids_digest": digest(algorithm_ids),
        "policy_sha256": file_digest(POLICY_PATH),
        "findings_sha256": file_digest(FINDINGS_PATH),
        "registry_sha256": file_digest(REGISTRY_PATH),
        "adgk_contract_sha256": file_digest(ADGK_CONTRACT),
        "ids_only_in_findings": only_findings,
        "ids_only_in_sources_count": len(only_sources),
        "ids_only_in_sources_digest": digest(only_sources),
    }


def nsi_objects() -> list[tuple[Path, dict[str, Any]]]:
    objects: list[tuple[Path, dict[str, Any]]] = []
    for path in sorted((NSI_ROOT / "chapitres").glob("1NSI-*/**/*.tex")):
        match = META.search(path.read_text(encoding="utf-8"))
        if match:
            objects.append((path, json.loads(match.group(1))))
    return objects


def receipt_verdict(source: Path, object_id: str) -> str | None:
    receipt = source.parents[1] / "validations" / f"{object_id}.execution.json"
    if not receipt.is_file():
        return None
    payload = json.loads(receipt.read_text(encoding="utf-8"))
    return payload.get("verdict")


def observe_status() -> dict[str, Any]:
    """Les compteurs de statut 1NSI, recalculés sur l'arbre vivant."""

    import yaml

    policy = yaml.safe_load(STATUS_POLICY.read_text(encoding="utf-8"))
    objects = nsi_objects()
    counts = Counter(meta["status"] for _path, meta in objects)
    prohibited = sorted(
        str(path.relative_to(ROOT))
        for path, meta in objects
        if meta["status"] in set(policy["prohibited_transitions"])
    )
    gaps = []
    for source, meta in objects:
        verdict = receipt_verdict(source, meta["id"])
        relative = str(source.relative_to(ROOT))
        if meta["status"] == "verified" and verdict != "pass":
            gaps.append({"path": relative, "status": "verified", "verdict": verdict})
        elif meta["status"] == "manual_review" and verdict != "manual_review":
            gaps.append(
                {"path": relative, "status": "manual_review", "verdict": verdict}
            )
    return {
        "observed_counts": dict(counts),
        "objects_total": len(objects),
        "prohibited_status_objects_count": len(prohibited),
        "prohibited_status_objects_digest": digest(prohibited),
        "evidence_gaps": sorted(
            gaps, key=lambda row: (row["path"], row["status"], str(row["verdict"]))
        ),
    }


def cause_commit() -> dict[str, Any]:
    """Le commit qui explique l'écart, lu dans l'historique."""

    result = subprocess.run(
        [
            "git",
            "log",
            "--format=%H%x00%s%x00%cs",
            "-1",
            "--diff-filter=D",
            "--",
            "NSI/chapitres",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        _reject("aucun commit de suppression trouvé sous NSI/chapitres")
    sha, subject, date = result.stdout.strip().split("\0")
    counted = subprocess.run(
        [
            "git",
            "show",
            "--diff-filter=D",
            "--name-only",
            "--format=",
            sha,
            "--",
            "NSI/chapitres",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    deleted = [line for line in counted.stdout.split() if line.endswith(".tex")]
    return {
        "sha": sha,
        "subject": subject,
        "date": date,
        "deleted_tex_files": len(deleted),
    }


def apply_delta(
    document: dict[str, Any], observed: dict[str, Any], label: str
) -> dict[str, Any]:
    """Écrit les champs observés, laisse le reste intact, rend le delta."""

    delta = []
    for key, value in observed.items():
        previous = document.get(key)
        if previous != value:
            delta.append(
                {
                    "register": label,
                    "field": key,
                    "declared": previous,
                    "observed": value,
                }
            )
        document[key] = value
    return {"document": document, "delta": delta}


def build(write: bool) -> dict[str, Any]:
    if not CAMPAIGN_TARGET.is_file() or not STATUS_TARGET.is_file():
        _reject("un des deux registres d'attente est absent")
    campaign = json.loads(CAMPAIGN_TARGET.read_text(encoding="utf-8"))
    status = json.loads(STATUS_TARGET.read_text(encoding="utf-8"))
    sealed_before = json.dumps(campaign.get(CAMPAIGN_SEALED_KEY), sort_keys=True)
    immutable_before = {
        key: (campaign.get(key), status.get(key)) for key in IMMUTABLE_TOP_LEVEL
    }

    module = load_review_module()
    cause = cause_commit()

    campaign_observed = observe_campaign(module)
    campaign_result = apply_delta(
        {**campaign, "observed": {**campaign["observed"], **campaign_observed}},
        {},
        "campaign",
    )
    campaign_delta = [
        {
            "register": "1NSI_CONTENT_REVIEW_CAMPAIGN_STATE",
            "field": f"observed.{key}",
            "declared": campaign["observed"].get(key),
            "observed": value,
        }
        for key, value in campaign_observed.items()
        if campaign["observed"].get(key) != value
    ]
    campaign_document = campaign_result["document"]

    status_observed = observe_status()
    status_delta = [
        {
            "register": "1NSI_STATUS_GOVERNANCE_PENDING",
            "field": key,
            "declared": status.get(key),
            "observed": value,
        }
        for key, value in status_observed.items()
        if status.get(key) != value
    ]
    status_document = {**status, **status_observed}

    note = (
        f"Ré-observation du {cause['date']} : le commit {cause['sha'][:8]} "
        f"({cause['subject']}) a retiré {cause['deleted_tex_files']} objets suivis "
        "sous NSI/chapitres ; les compteurs et condensats observés sont "
        f"recalculés par {GENERATED_BY}. L'attente n'est pas levée."
    )
    for document in (campaign_document, status_document):
        reason = document.get("reason", "")
        if note not in reason:
            document["reason"] = (reason + " " + note).strip()

    if json.dumps(campaign_document.get(CAMPAIGN_SEALED_KEY), sort_keys=True) != sealed_before:
        _reject("un fait scellé aurait été modifié : le passé ne se ré-observe pas")
    for key, (before_campaign, before_status) in immutable_before.items():
        if campaign_document.get(key) != before_campaign:
            _reject(f"champ immuable modifié dans le registre de campagne : {key}")
        if status_document.get(key) != before_status:
            _reject(f"champ immuable modifié dans le registre de statuts : {key}")

    if write:
        CAMPAIGN_TARGET.write_text(
            json.dumps(campaign_document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        STATUS_TARGET.write_text(
            json.dumps(status_document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    delta = campaign_delta + status_delta
    unexplained = [
        row
        for row in delta
        if isinstance(row["declared"], int)
        and isinstance(row["observed"], int)
        and row["declared"] - row["observed"] != cause["deleted_tex_files"]
        and row["field"].endswith(("count", "total", "approved"))
    ]
    return {
        "artifact_type": "1nsi_pending_state_reobservation",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "approves_nothing": (
            "la campagne de revue 1NSI reste PENDING ; ce producteur ne mesure "
            "que l'etat courant et ne leve aucune attente"
        ),
        "no_1nsi_content_is_modified": True,
        "cause": cause,
        "registers": [
            {
                "path": str(CAMPAIGN_TARGET.relative_to(ROOT)),
                "status": campaign_document["status"],
            },
            {
                "path": str(STATUS_TARGET.relative_to(ROOT)),
                "status": status_document["status"],
            },
        ],
        "delta": delta,
        "summary": {
            "REGISTERS": 2,
            "FIELDS_REOBSERVED": len(delta),
            "SEALED_FIELDS_MUTATED": 0,
            "UNEXPLAINED_DELTA": len(unexplained),
            "DELETED_TEX_FILES_IN_CAUSE_COMMIT": cause["deleted_tex_files"],
        },
        "unexplained_delta": unexplained,
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Ré-observation des registres d'attente 1NSI",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        "> " + payload["approves_nothing"],
        "",
        "## Cause",
        "",
        f"- commit : `{payload['cause']['sha']}`",
        f"- sujet : {payload['cause']['subject']}",
        f"- date : {payload['cause']['date']}",
        f"- objets `.tex` supprimés sous `NSI/chapitres` : "
        f"{payload['cause']['deleted_tex_files']}",
        "",
        "## Métriques",
        "",
        "| Métrique | Valeur |",
        "|---|---:|",
    ]
    for name, value in payload["summary"].items():
        lines.append(f"| `{name}` | {value} |")
    lines += [
        "",
        "## Champs ré-observés",
        "",
        "| Registre | Champ | Déclaré | Observé |",
        "|---|---|---|---|",
    ]
    for row in payload["delta"]:
        declared = row["declared"]
        observed = row["observed"]
        if isinstance(declared, (list, dict)):
            declared = f"{type(declared).__name__}[{len(declared)}]"
        if isinstance(observed, (list, dict)):
            observed = f"{type(observed).__name__}[{len(observed)}]"
        lines.append(
            f"| `{row['register']}` | `{row['field']}` | `{declared}` | `{observed}` |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--apply", action="store_true", help="écrire les deux registres ré-observés"
    )
    parser.add_argument("--check", action="store_true", help="ne rien écrire")
    arguments = parser.parse_args(argv)

    try:
        payload = build(arguments.apply)
    except ReobservationError as error:
        print(f"1NSI-REOBSERVATION-ERROR: {error}", file=sys.stderr)
        return 2

    if not arguments.check:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"écrit {JSON_TARGET.relative_to(ROOT)} et {MD_TARGET.relative_to(ROOT)}")
    for name, value in payload["summary"].items():
        print(f"{name}={value}")
    blocking = ("SEALED_FIELDS_MUTATED", "UNEXPLAINED_DELTA")
    return 1 if any(payload["summary"][name] for name in blocking) else 0


if __name__ == "__main__":
    raise SystemExit(main())
