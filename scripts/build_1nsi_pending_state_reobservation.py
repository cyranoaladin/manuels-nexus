#!/usr/bin/env python3
"""Ré-observation des deux registres d'attente 1NSI : mesurer, ne rien décider.

Deux registres déclarent l'état COURANT d'une campagne de revue 1NSI restée en
attente : `audit/1NSI_CONTENT_REVIEW_CAMPAIGN_STATE.json` et
`audit/1NSI_STATUS_GOVERNANCE_PENDING.json`. Les suites 1NSI comparent leur
contenu à l'arbre vivant et échouent, exprès, dès que les deux divergent.

Ce producteur ré-observe. Il recalcule les champs `observed*` avec les fonctions
mêmes que les tests utilisent, et il ne touche à rien d'autre :

* les champs `sealed*` sont des faits historiques — le commit de scellement, le
  nombre de sources scellées, les condensats d'alors. Ils sont laissés
  identiques, et le producteur échoue s'il les voit changer ;
* `status`, `no_go_carrier` et la nature de l'attente ne sont pas touchés : la
  campagne reste `PENDING`, la revue humaine reste due, et rien ici ne la
  rapproche d'une approbation ;
* `reason` reçoit une ligne datée qui NOMME la cause de la ré-observation.

L'écart entre l'état déclaré et l'arbre courant est expliqué par ENSEMBLES
exacts, jamais par un compte net (INT-006) :

* `OLD_SOURCE_SET` est relu dans l'arbre git du commit qui a écrit les
  registres (le dernier état observé), et son condensat doit être celui que ce
  commit a déclaré — sinon l'état déclaré ne décrit aucun arbre connu ;
* `CURRENT_SOURCE_SET` est l'arbre de travail ;
* `ADDED`, `REMOVED`, `MODIFIED_EXISTING` (même chemin, corps différent) sont
  attribués chemin par chemin aux commits de cause de la plage
  `baseline..HEAD` restreinte à `NSI/chapitres`, et l'état d'arrivée de chaque
  chemin doit être exactement celui que HEAD porte : un fichier non commis
  n'explique rien ;
* un fichier hors du périmètre des sources (reçu de validation, fichier hors
  `NSI/chapitres`) n'explique ni ne bloque rien.

Un changement de source set touchant un chapitre qui porte déjà une revue
humaine (reçu, verdict, approbation) n'est jamais ré-observé automatiquement :
`AUTO_REOBSERVATION_FORBIDDEN`, rien n'est écrit.

Ce que ce producteur ne fait pas, et ne doit jamais faire : rendre une suite
verte en modifiant du contenu 1NSI. Il ne lit aucun `.tex` pour le changer.

Métriques bloquantes : `SEALED_FIELDS_MUTATED`, `UNEXPLAINED_DELTA`
(somme de `UNEXPLAINED_ADDITIONS`, `UNEXPLAINED_REMOVALS`,
`UNEXPLAINED_MODIFICATIONS`). Rien n'est écrit tant qu'une métrique bloque.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import io
import json
import re
import subprocess
import sys
import tarfile
import tempfile
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
HUMAN_REVIEW_ROOT = ROOT / "audit/reviews/human"
ALGORITHM_CHAPTERS = {"1NSI-ALGO-PARCOURS-TRIS", "1NSI-ALGO-DICHO-GLOUTON-KNN"}
META = re.compile(r"^% META: (\{.*\})\s*$", re.MULTILINE)

# Le périmètre exact des sources : ce que `discover_sources` énumère, et rien
# d'autre. Les commits de cause sont lus sur ce préfixe seulement.
SOURCE_SCOPE = "NSI/chapitres"

# Les champs qui portent l'histoire : leur valeur ne dépend pas de l'arbre
# courant, et une ré-observation qui les bougerait aurait réécrit le passé.
CAMPAIGN_SEALED_KEY = "sealed"
IMMUTABLE_TOP_LEVEL = ("artifact_name", "created", "status", "no_go_carrier")

# Les états d'une revue humaine qui signifient « personne n'a encore rien
# regardé » : tout autre état est un travail humain qu'une ré-observation
# automatique déplacerait sur du contenu qu'il n'a pas vu.
HUMAN_STATE_UNTOUCHED = {None, "PENDING_UNASSIGNED"}
HUMAN_APPROVAL_UNTOUCHED = {None, "PENDING"}


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


def blob_sha1(data: bytes) -> str:
    """Le condensat que git donne à ce contenu : comparable à `ls-tree`."""

    return hashlib.sha1(b"blob %d\0" % len(data) + data).hexdigest()


def _git(*arguments: str, binary: bool = False) -> Any:
    result = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        capture_output=True,
        text=not binary,
        check=False,
    )
    if result.returncode != 0:
        error = result.stderr if isinstance(result.stderr, str) else result.stderr.decode()
        _reject(f"git {' '.join(arguments)} : {error.strip()}")
    return result.stdout


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


def observe_campaign(module: Any, sources: list[dict[str, Any]]) -> dict[str, Any]:
    """Les champs `observed` du registre de campagne, recalculés."""

    import yaml

    policy = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
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


# --------------------------------------------------------------------------
# Source set : ancien état, état courant, écart par ensembles.
# --------------------------------------------------------------------------


def source_records(sources: list[dict[str, Any]]) -> dict[str, dict[str, str]]:
    """Le source set sous forme comparable : chemin → identité et condensat."""

    return {
        source["path"]: {
            "id": source["id"],
            "chapter": source["chapter"],
            "source_sha256": source["source_sha256"],
        }
        for source in sources
    }


def baseline_commit() -> str:
    """Le dernier commit qui a écrit les registres : l'état déclaré vient de là."""

    relative = [str(CAMPAIGN_TARGET.relative_to(ROOT)), str(STATUS_TARGET.relative_to(ROOT))]
    output = _git("log", "-1", "--format=%H", "--", *relative).strip()
    if not output:
        _reject("aucun commit n'a jamais écrit les registres d'attente 1NSI")
    return output


def sources_at_commit(module: Any, commit: str) -> dict[str, dict[str, str]]:
    """Le source set tel que l'arbre de `commit` le porte, lu par `discover_sources`."""

    archive = _git("archive", "--format=tar", commit, "--", SOURCE_SCOPE, binary=True)
    with tempfile.TemporaryDirectory(prefix="1nsi-reobservation-") as scratch:
        with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
            tar.extractall(scratch, filter="data")
        return source_records(module.discover_sources(Path(scratch)))


def declared_sources_digest(commit: str) -> str:
    """Le condensat des identités que `commit` a déclaré observer."""

    relative = str(CAMPAIGN_TARGET.relative_to(ROOT))
    payload = json.loads(_git("show", f"{commit}:{relative}"))
    return payload["observed"]["sources_ids_digest"]


def committed_blobs(commit: str) -> dict[str, str]:
    """Chemin → condensat git du contenu, pour tout `NSI/chapitres` à `commit`."""

    blobs: dict[str, str] = {}
    for line in _git("ls-tree", "-r", commit, "--", SOURCE_SCOPE).splitlines():
        meta, _tab, path = line.partition("\t")
        blobs[path] = meta.split()[2]
    return blobs


def net_changes(baseline: str) -> dict[str, str]:
    """Chemin → A/D/M entre l'arbre observé et HEAD, renommages traités en D+A."""

    changes: dict[str, str] = {}
    output = _git(
        "diff", "--name-status", "--no-renames", baseline, "HEAD", "--", SOURCE_SCOPE
    )
    for line in output.splitlines():
        status, _tab, path = line.partition("\t")
        changes[path] = status[:1]
    return changes


def cause_commits(baseline: str) -> list[dict[str, Any]]:
    """Les commits de `baseline..HEAD` qui touchent le périmètre, avec leurs chemins."""

    output = _git(
        "log",
        "--reverse",
        "--no-renames",
        "--name-status",
        "--format=%x01%H%x00%s%x00%cs",
        f"{baseline}..HEAD",
        "--",
        SOURCE_SCOPE,
    )
    commits: list[dict[str, Any]] = []
    for block in output.split("\x01"):
        if not block.strip():
            continue
        header, _newline, body = block.partition("\n")
        sha, subject, date = header.split("\0")
        changes: dict[str, str] = {}
        for line in body.splitlines():
            if not line.strip():
                continue
            status, _tab, path = line.partition("\t")
            changes[path] = status[:1]
        commits.append({"sha": sha, "subject": subject, "date": date, "changes": changes})
    return commits


def last_source_commit() -> dict[str, Any]:
    """La dernière mutation committée du périmètre, quand la plage de cause est vide."""

    output = _git("log", "-1", "--format=%H%x00%s%x00%cs", "--", SOURCE_SCOPE).strip()
    if not output:
        _reject(f"aucun commit n'a jamais touché {SOURCE_SCOPE}")
    sha, subject, date = output.split("\0")
    return {"sha": sha, "subject": subject, "date": date}


def source_set_delta(module: Any, sources: list[dict[str, Any]]) -> dict[str, Any]:
    """ADDED / REMOVED / MODIFIED_EXISTING, chacun attribué à ses commits de cause."""

    baseline = baseline_commit()
    old = sources_at_commit(module, baseline)
    old_digest = digest(sorted(record["id"] for record in old.values()))
    declared = declared_sources_digest(baseline)
    if old_digest != declared:
        _reject(
            f"l'état déclaré par {baseline[:8]} ({declared}) ne décrit pas l'arbre "
            f"de ce commit ({old_digest}) : aucun ancien source set autoritaire"
        )
    current = source_records(sources)

    added = sorted(set(current) - set(old))
    removed = sorted(set(old) - set(current))
    unchanged = sorted(set(old) & set(current))
    modified = [
        path
        for path in unchanged
        if old[path]["source_sha256"] != current[path]["source_sha256"]
    ]

    head_blobs = committed_blobs("HEAD")
    net = net_changes(baseline)
    commits = cause_commits(baseline)
    touching: dict[str, list[str]] = {}
    for commit in commits:
        for path in commit["changes"]:
            touching.setdefault(path, []).append(commit["sha"])

    def working_blob(path: str) -> str:
        return blob_sha1((ROOT / path).read_bytes())

    rows: list[dict[str, Any]] = []

    def attribute(path: str, change: str, before: dict | None, after: dict | None) -> None:
        expected = {"added": "A", "removed": "D", "modified": "M"}[change]
        committed = net.get(path)
        if change == "removed":
            uncommitted = path in head_blobs
        else:
            uncommitted = head_blobs.get(path) != working_blob(path)
        if uncommitted:
            reason = "l'état d'arrivée diffère de HEAD : modification non commise"
            explained = False
        elif committed != expected:
            reason = (
                f"aucun commit de cause ne porte ce changement ({expected} attendu, "
                f"{committed or 'rien'} entre {baseline[:8]} et HEAD)"
            )
            explained = False
        else:
            reason = None
            explained = True
        rows.append(
            {
                "path": path,
                "change": change,
                "chapter": (after or before or {}).get("chapter"),
                "id": (after or before or {}).get("id"),
                "before": before and {"source_sha256": before["source_sha256"], "id": before["id"]},
                "after": after and {"source_sha256": after["source_sha256"], "id": after["id"]},
                "cause_commits": touching.get(path, []),
                "explained": explained,
                "reason": reason,
            }
        )

    for path in added:
        attribute(path, "added", None, current[path])
    for path in removed:
        attribute(path, "removed", old[path], None)
    for path in modified:
        attribute(path, "modified", old[path], current[path])

    removed_ids = {old[path]["id"]: path for path in removed}
    identity_moves = sorted(
        (
            {"id": current[path]["id"], "from": removed_ids[current[path]["id"]], "to": path}
            for path in added
            if current[path]["id"] in removed_ids
        ),
        key=lambda move: move["id"],
    )

    unexplained = {
        kind: sorted(row["path"] for row in rows if row["change"] == kind and not row["explained"])
        for kind in ("added", "removed", "modified")
    }
    affected_chapters = sorted({row["chapter"] for row in rows if row["chapter"]})
    return {
        "baseline_commit": baseline,
        "old_set": {"count": len(old), "ids_digest": old_digest, "paths_digest": digest(sorted(old))},
        "current_set": {
            "count": len(current),
            "ids_digest": digest(sorted(record["id"] for record in current.values())),
            "paths_digest": digest(sorted(current)),
        },
        "added": added,
        "removed": removed,
        "modified_existing": modified,
        "unchanged_count": len(unchanged) - len(modified),
        "identity_moves": identity_moves,
        "cause_commits": [
            {key: value for key, value in commit.items() if key != "changes"}
            for commit in commits
        ],
        "attribution": rows,
        "unexplained": unexplained,
        "affected_chapters": affected_chapters,
    }


def human_receipts_affected(chapters: list[str]) -> list[dict[str, Any]]:
    """Les revues humaines qu'un changement de source set déplacerait."""

    affected: list[dict[str, Any]] = []
    if REGISTRY_PATH.is_file():
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        if registry.get("publication_approval"):
            affected.append({"scope": "registry", "signals": ["publication_approval"]})
    for chapter in chapters:
        directory = HUMAN_REVIEW_ROOT / chapter
        if not directory.is_dir():
            continue
        signals: list[str] = []
        receipts = sorted((directory / "receipts").glob("*.json"))
        if receipts:
            signals.append(f"receipts:{len(receipts)}")
        state_path = directory / "REVIEW_STATE.json"
        if state_path.is_file():
            state = json.loads(state_path.read_text(encoding="utf-8"))
            for key in ("review_a", "review_b"):
                review = state.get(key) or {}
                if review.get("state") not in HUMAN_STATE_UNTOUCHED or review.get("verdict"):
                    signals.append(f"{key}:{review.get('state')}/{review.get('verdict')}")
            for key in ("human_content_approval", "qcm_human_approval"):
                if state.get(key) not in HUMAN_APPROVAL_UNTOUCHED:
                    signals.append(f"{key}:{state.get(key)}")
            if state.get("publication_approval"):
                signals.append("publication_approval")
        if signals:
            affected.append({"scope": chapter, "signals": signals})
    return affected


def build(write: bool) -> dict[str, Any]:
    if not CAMPAIGN_TARGET.is_file() or not STATUS_TARGET.is_file():
        _reject("un des deux registres d'attente est absent")
    campaign = json.loads(CAMPAIGN_TARGET.read_text(encoding="utf-8"))
    status = json.loads(STATUS_TARGET.read_text(encoding="utf-8"))
    sealed_before = json.dumps(campaign.get(CAMPAIGN_SEALED_KEY), sort_keys=True)
    immutable_before = {
        key: (campaign.get(key), status.get(key)) for key in IMMUTABLE_TOP_LEVEL
    }

    # Les entrées sont figées AVANT toute sortie : l'arbre de travail des
    # sources, l'historique git, et rien de ce que ce producteur écrit.
    module = load_review_module()
    sources = module.discover_sources(ROOT)
    delta = source_set_delta(module, sources)
    changed = bool(delta["added"] or delta["removed"] or delta["modified_existing"])

    receipts = human_receipts_affected(delta["affected_chapters"]) if changed else []
    if receipts:
        _reject(
            "AUTO_REOBSERVATION_FORBIDDEN : le source set change sur un périmètre "
            "qui porte une revue humaine ; rien n'est déplacé automatiquement : "
            + json.dumps(receipts, ensure_ascii=False, sort_keys=True)
        )

    if delta["cause_commits"]:
        cause = dict(delta["cause_commits"][-1])
    else:
        cause = last_source_commit()
    cause["baseline"] = delta["baseline_commit"]
    cause["cause_commits_count"] = len(delta["cause_commits"])
    cause["sources_added"] = len(delta["added"])
    cause["sources_removed"] = len(delta["removed"])
    cause["sources_modified"] = len(delta["modified_existing"])

    campaign_observed = observe_campaign(module, sources)
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
    campaign_document = {**campaign, "observed": {**campaign["observed"], **campaign_observed}}

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

    if changed:
        shas = ", ".join(commit["sha"][:8] for commit in delta["cause_commits"]) or "aucun"
        note = (
            f"Ré-observation du {cause['date']} : depuis {delta['baseline_commit'][:8]}, "
            f"{len(delta['cause_commits'])} commit(s) de cause ({shas}) ont ajouté "
            f"{len(delta['added'])}, retiré {len(delta['removed'])} et modifié "
            f"{len(delta['modified_existing'])} sources sous {SOURCE_SCOPE} ; les "
            f"compteurs et condensats observés sont recalculés par {GENERATED_BY}. "
            "L'attente n'est pas levée."
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

    fields = campaign_delta + status_delta
    unexplained = delta["unexplained"]
    summary = {
        "REGISTERS": 2,
        "FIELDS_REOBSERVED": len(fields),
        "SEALED_FIELDS_MUTATED": 0,
        "CAUSE_COMMITS": len(delta["cause_commits"]),
        "SOURCES_ADDED": len(delta["added"]),
        "SOURCES_REMOVED": len(delta["removed"]),
        "SOURCES_MODIFIED": len(delta["modified_existing"]),
        "UNEXPLAINED_ADDITIONS": len(unexplained["added"]),
        "UNEXPLAINED_REMOVALS": len(unexplained["removed"]),
        "UNEXPLAINED_MODIFICATIONS": len(unexplained["modified"]),
        "UNEXPLAINED_DELTA": sum(len(paths) for paths in unexplained.values()),
        "HUMAN_RECEIPTS_AFFECTED": len(receipts),
    }
    blocked = bool(summary["SEALED_FIELDS_MUTATED"] or summary["UNEXPLAINED_DELTA"])
    # CURRENT : les registres portent déjà l'état observé, qu'ils soient commis
    # ou non ; l'écart de source set, s'il existe, reste rapporté et attribué.
    if blocked:
        state = "BLOCKED"
    elif not fields:
        state = "CURRENT"
    else:
        state = "REOBSERVED" if write else "STALE_EXPLAINED"

    if write and not blocked:
        CAMPAIGN_TARGET.write_text(
            json.dumps(campaign_document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        STATUS_TARGET.write_text(
            json.dumps(status_document, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    return {
        "artifact_type": "1nsi_pending_state_reobservation",
        "schema_version": 2,
        "generated_by": GENERATED_BY,
        "approves_nothing": (
            "la campagne de revue 1NSI reste PENDING ; ce producteur ne mesure "
            "que l'etat courant et ne leve aucune attente"
        ),
        "no_1nsi_content_is_modified": True,
        "state": state,
        "cause": cause,
        "source_set": {
            "declared_historical": {
                "commit": delta["baseline_commit"],
                **delta["old_set"],
            },
            "observed_current": delta["current_set"],
            "added": delta["added"],
            "removed": delta["removed"],
            "modified_existing": delta["modified_existing"],
            "unchanged_count": delta["unchanged_count"],
            "identity_moves": delta["identity_moves"],
            "cause_commits": delta["cause_commits"],
            "attribution": delta["attribution"],
            "affected_chapters": delta["affected_chapters"],
            "human_receipts_affected": receipts,
        },
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
        "delta": fields,
        "summary": summary,
        "unexplained_delta": [
            row for row in delta["attribution"] if not row["explained"]
        ],
    }


def render_markdown(payload: dict[str, Any]) -> str:
    source_set = payload["source_set"]
    lines = [
        "# Ré-observation des registres d'attente 1NSI",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        "> " + payload["approves_nothing"],
        "",
        f"État : `{payload['state']}`",
        "",
        "## Source set",
        "",
        f"- déclaré (historique) : commit `{source_set['declared_historical']['commit']}`, "
        f"{source_set['declared_historical']['count']} sources, "
        f"`{source_set['declared_historical']['ids_digest']}`",
        f"- observé (courant) : {source_set['observed_current']['count']} sources, "
        f"`{source_set['observed_current']['ids_digest']}`",
        f"- ajoutés : {len(source_set['added'])} ; retirés : {len(source_set['removed'])} ; "
        f"modifiés : {len(source_set['modified_existing'])} ; "
        f"inchangés : {source_set['unchanged_count']}",
        "",
        "## Commits de cause",
        "",
    ]
    if source_set["cause_commits"]:
        for commit in source_set["cause_commits"]:
            lines.append(f"- `{commit['sha']}` ({commit['date']}) {commit['subject']}")
    else:
        lines.append(
            f"- aucun depuis le dernier état observé ; dernière mutation du périmètre : "
            f"`{payload['cause']['sha']}` ({payload['cause']['subject']})"
        )
    lines += [
        "",
        "## Métriques",
        "",
        "| Métrique | Valeur |",
        "|---|---:|",
    ]
    for name, value in payload["summary"].items():
        lines.append(f"| `{name}` | {value} |")
    if source_set["attribution"]:
        lines += [
            "",
            "## Attribution par chemin",
            "",
            "| Chemin | Changement | Commits de cause | Expliqué |",
            "|---|---|---|---|",
        ]
        for row in source_set["attribution"]:
            shas = ", ".join(sha[:8] for sha in row["cause_commits"]) or "—"
            verdict = "oui" if row["explained"] else f"NON — {row['reason']}"
            lines.append(f"| `{row['path']}` | {row['change']} | {shas} | {verdict} |")
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
        payload = build(arguments.apply and not arguments.check)
    except ReobservationError as error:
        print(f"1NSI-REOBSERVATION-ERROR: {error}", file=sys.stderr)
        return 2

    blocking = ("SEALED_FIELDS_MUTATED", "UNEXPLAINED_DELTA")
    blocked = any(payload["summary"][name] for name in blocking)
    if not arguments.check and not blocked:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"écrit {JSON_TARGET.relative_to(ROOT)} et {MD_TARGET.relative_to(ROOT)}")
    print(f"STATE={payload['state']}")
    for name, value in payload["summary"].items():
        print(f"{name}={value}")
    for row in payload["unexplained_delta"]:
        print(f"UNEXPLAINED {row['change']} {row['path']} : {row['reason']}")
    return 1 if blocked else 0


if __name__ == "__main__":
    raise SystemExit(main())
