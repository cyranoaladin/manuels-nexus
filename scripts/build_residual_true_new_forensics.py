#!/usr/bin/env python3
"""Build the residual TRUE_NEW ledger without touching anomaly governance.

The builder is deliberately downstream-only: it reads the frozen initial
forensics and the current canonical inventory, then projects the still-open
review debt.  It never updates the inventory, manifest, baseline, policy or
oracle.
"""

from __future__ import annotations

import argparse
import hashlib
from itertools import combinations
import json
import os
from pathlib import Path

import yaml
import subprocess
import tempfile
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
INITIAL_JSON_REL = Path("audit/TRUE_NEW_18_FORENSICS.json")
INITIAL_MD_REL = Path("audit/TRUE_NEW_18_FORENSICS.md")
INVENTORY_REL = Path("audit/INVENTAIRE_COLLECTION.json")
INITIAL_ALGEBRA_REL = Path("audit/CURRENT_ANOMALY_SET_ALGEBRA.json")
#: Classes de dette declarees separement, posterieures au gel des 18. Elles ne
#: sont jamais fondues dans le modele residuel : chacune en est un composant
#: nomme, disjoint et explicitement bloquant pour la release. La campagne en
#: ajoute une par chapitre qui cree des objets ; les inscrire ici est le seul
#: moyen de les compter sans les qualifier.
DECLARED_DEBT_LEDGERS = (
    Path("audit/VARALEA_C6C7_REVIEW_DEBT_12.json"),
    Path("audit/EXPONENTIELLE_C1_METHOD_REVIEW_DEBT_1.json"),
    Path("audit/NSI_TC_EVAL_CORRIGES_REVIEW_DEBT_2.json"),
    Path("audit/TNSI_PROJET_QCM_REVIEW_DEBT_1.json"),
    Path("audit/TSPE_GEOESPACE_AUTHORED_REVIEW_DEBT_45.json"),
    Path("audit/NSI_COUPLED_ALGORITHMICS_REVIEW_DEBT.json"),
)

FROZEN_SHA256 = {
    INITIAL_JSON_REL: "4833f06833633d7d7d27cfb00de4f4c1bb4083288aa1cf784e5e08bc037c76b5",
    INITIAL_MD_REL: "337b2977665a4419e205cfa4d431a6a9c1b7deb89b3544cd9124057762608efd",
}
OUTPUT_NAMES = {
    "residual_forensics": {
        "json": "RESIDUAL_TRUE_NEW_FORENSICS.json",
        "md": "RESIDUAL_TRUE_NEW_FORENSICS.md",
    },
    "residual_algebra": {
        "json": "CURRENT_ANOMALY_SET_ALGEBRA_RESIDUAL.json",
        "md": "CURRENT_ANOMALY_SET_ALGEBRA_RESIDUAL.md",
    },
}

FIXED_SOURCE_SHA256 = {
    "18c7b3aa6301ef4c": "sha256:2b0ce4c358c7bbb084a448fd175145cf58f502c5ed1c40b01efa9dd040674b9e",
    "33e9818ffc70892c": "sha256:1f1cefa819c936611ce8ad4b46c0fc3e02f953e606a12827dc746de237542a33",
    "873a020438d7e00a": "sha256:af699a632f58b14ef2360503da4bd6d8b39d20cba15dafa41d779952253f20de",
    "8ca4f3f2a9212e39": "sha256:71d3048821fe1b5565f3bde13ddf8f7e32a4e78dc174b365472af7b367a7155f",
    "dc8e5dcc030bb539": "sha256:9193efce3be19cf93fb6fa44adfabba74126a2f96ef234fb58681972ae670fa1",
}

ALLOWED_EDITORIAL_REASONS = {
    "MANDATORY_PROGRAMME_GAP",
    "PEDAGOGICAL_CONTRACT_REQUIREMENT",
    "REQUIRED_REMEDIATION",
    "REQUIRED_ASSESSMENT",
    "APPROVED_OPTIONAL_EXTENSION",
    "OTHER_PROVED_EDITORIAL_NEED",
}

STRUCTURAL_DISQUALIFIERS = {
    "assembler_invalid",
    "broken_assembly_references",
    "broken_latex_references",
    "broken_meta_references",
    "chapters_not_in_manual",
    "context_mismatches",
    "contract_invalid",
    "contract_missing",
    "duplicate_assembly_objects",
    "duplicate_capacity_refs",
    "duplicate_ids",
    "invalid_capacities",
    "invalid_meta_references",
    "invalid_statuses",
    "latex_cycles",
    "metadata_invalid",
    "metadata_missing",
    "missing_assemblers",
    "missing_corrections",
    "orphan_files",
    "unassembled_objects",
    "unclassified_types",
    "unknown_chapter_prefixes",
}


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _source_sha(path: Path) -> str:
    if not path.is_file():
        raise ValueError(f"source résiduelle absente: {path}")
    return f"sha256:{_sha256_bytes(path.read_bytes())}"


def _git_head(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    head = result.stdout.strip()
    if len(head) != 40 or any(character not in "0123456789abcdef" for character in head):
        raise ValueError(f"SHA Git forensique invalide: {head!r}")
    return head


def _validate_git_sha(value: object) -> str:
    sha = str(value)
    if len(sha) != 40 or any(
        character not in "0123456789abcdef" for character in sha
    ):
        raise ValueError(f"SHA Git forensique invalide: {sha!r}")
    return sha


def _assert_source_snapshot(
    root: Path, output_dir: Path, forensic_source_sha: str
) -> None:
    root = root.resolve()
    output_dir = output_dir.resolve()
    forensic_source_sha = _validate_git_sha(forensic_source_sha)
    try:
        relative_output_dir = output_dir.relative_to(root)
    except ValueError as exc:
        raise ValueError("sortie forensique hors dépôt") from exc

    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", forensic_source_sha, "HEAD"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if ancestor.returncode != 0:
        raise ValueError("SHA forensique non ancêtre du HEAD courant")

    diff = subprocess.run(
        ["git", "diff", "--name-only", forensic_source_sha, "--"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    changed = {line for line in diff.stdout.splitlines() if line}
    untracked = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    changed.update(line for line in untracked.stdout.splitlines() if line)
    allowed = {
        (relative_output_dir / name).as_posix()
        for names in OUTPUT_NAMES.values()
        for name in names.values()
    }
    unexpected = sorted(changed - allowed)
    if unexpected:
        raise ValueError(
            "sources modifiées depuis le gel: " + ", ".join(unexpected)
        )


def _forensic_source_sha_for_check(root: Path, output_dir: Path) -> str:
    """Reuse a committed freeze only while no source changed after it.

    A report commit necessarily advances ``HEAD``.  Replacing the embedded
    source SHA with that report-only commit would make every committed report
    stale forever.  The frozen SHA is therefore retained only when it is an
    ancestor of ``HEAD`` and the complete worktree diff since that SHA is
    confined to the four generated forensic reports.
    """

    json_names = sorted(names["json"] for names in OUTPUT_NAMES.values())
    frozen_shas = {
        _validate_git_sha(
            _read_json(output_dir / name).get("forensic_source_sha")
        )
        for name in json_names
    }
    if len(frozen_shas) != 1:
        raise ValueError("SHA forensiques résiduels incohérents")
    frozen_sha = next(iter(frozen_shas))
    _assert_source_snapshot(root, output_dir, frozen_sha)
    return frozen_sha


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"JSON illisible: {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"racine JSON non objet: {path}")
    return value


SUSPENDED_QUALIFICATIONS_LEDGER = Path("audit/METHOD_REQUALIFICATION_QUEUE.json")


def _assignment_module():
    """Le resolveur d'imputation, charge une fois."""

    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "review_debt_assignment_for_residual",
        ROOT / "scripts/review_debt_assignment.py",
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _suspended_qualifications(root: Path) -> set[str]:
    """Empreintes dont la qualification est SUSPENDUE, non effacee.

    La campagne diacritiques a modifie des fiches methode apres leur
    qualification humaine. La decision portait sur un texte precis : elle ne
    s'applique plus, l'anomalie couverte redevient une dette ouverte, et
    l'empreinte reapparait comme active non qualifiee. Ce n'est ni une
    nouveaute ni une regression, mais une classe a part entiere -- nommee ici
    pour etre comptee sans jamais etre fondue dans le residuel.

    La qualification demeure sur le disque ; seule son application est
    suspendue, et seule une re-qualification humaine la retablit.
    """

    chemin = root / SUSPENDED_QUALIFICATIONS_LEDGER
    if not chemin.is_file():
        return set()
    registre = _read_json(chemin)
    if registre.get("approves_nothing") is not True:
        raise ValueError("le registre des qualifications suspendues approuve quelque chose")
    return {
        str(entry["fingerprint"])
        for entry in registre.get("items", [])
        if entry.get("state") == "STALE"
    }


def _declared_separate_debt(root: Path) -> dict[str, set[str]]:
    """Empreintes des dettes declarees separement, par registre.

    Chaque registre est une autorite d'OBSERVATION : il n'inscrit rien dans la
    baseline et ne qualifie rien. Les lire ici sert uniquement a ne pas
    confondre ces classes avec le residuel gele des 18, et a les compter
    separement les unes des autres.
    """

    declared: dict[str, set[str]] = {}
    seen: set[str] = set()
    for relative in DECLARED_DEBT_LEDGERS:
        ledger = _read_json(root / relative)
        name = str(ledger.get("ledger_id") or relative.stem)
        entries = ledger.get("entries")
        if not isinstance(entries, list) or len(entries) != ledger.get("count"):
            raise ValueError(f"registre {name} incoherent")
        fingerprints = {str(entry["fingerprint"]) for entry in entries}
        if len(fingerprints) != len(entries):
            raise ValueError(f"empreintes {name} non univoques")
        if fingerprints & seen:
            raise ValueError(f"registres de dette non disjoints: {name}")
        seen |= fingerprints
        if ledger.get("in_approved_baseline") is not False:
            raise ValueError(f"la dette {name} ne doit pas etre en baseline")
        if ledger.get("release_blocking") is not True:
            raise ValueError(f"la dette {name} doit rester bloquante")
        for entry in entries:
            if (
                entry.get("policy_disposition") != "open_debt"
                or entry.get("release_acceptance") is not False
                or entry.get("in_approved_baseline") is not False
            ):
                raise ValueError(
                    f"ligne {name} non conforme: {entry.get('fingerprint')}"
                )
        declared[name] = fingerprints
    return declared


#: Classes de reecriture admises comme remplacement d'une supersession. La
#: distinction entre approbation humaine perimee et simple verification
#: machine est portee par les champs, jamais par le nom de la classe.
_REWRITTEN_ORIGINS = frozenset(
    {
        "REWRITTEN",
        "REWRITTEN_STALE_APPROVAL",
        "REWRITTEN_PREVIOUSLY_MACHINE_VERIFIED",
    }
)


def _inventory_module():
    """L'empreinte est RECALCULEE par la fonction de l'inventaire.

    La recopier ici ferait diverger deux definitions de la meme identite.
    """

    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "inventory_collection_for_residual", ROOT / "scripts/inventory_collection.py"
    )
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _anomaly_paths_by_fingerprint(inventory: Mapping[str, Any]) -> dict[str, str]:
    """Chemin de chaque anomalie courante, indexe par son empreinte."""

    module = _inventory_module()
    mapping: dict[str, str] = {}
    anomalies = inventory.get("anomalies")
    if not isinstance(anomalies, Mapping):
        return mapping
    for category, values in sorted(anomalies.items()):
        for anomaly in values or []:
            if not isinstance(anomaly, Mapping):
                continue
            fingerprint = module._anomaly_fingerprint(
                anomaly, category=str(category)
            )
            path = anomaly.get("path") or anomaly.get("source")
            if path is not None:
                mapping[fingerprint] = str(path)
    return mapping


def _identity_corrections(
    root: Path,
    *,
    current_active: set[str],
    paths_by_fingerprint: Mapping[str, str],
) -> set[str]:
    """Empreintes qu'une CORRECTION D'IDENTITE a rendues caduques.

    L'algebre initiale est gelee : elle a fige un etat ou certains objets
    portaient encore une identite erronee. Corriger cette identite fait
    disparaitre l'empreinte figee, sans que l'objet ait bouge d'un octet et
    sans qu'aucune ancre puisse l'apprendre.

    Le controle nomme la paire ; RIEN n'est cru sur parole. Le producteur
    exige, contre l'inventaire COURANT :

    * que l'empreinte perimee ait bien quitte l'ensemble actif -- sinon rien
      n'a ete corrige ;
    * que son remplacement y soit, lui, present -- sinon l'objet a DISPARU,
      et absorber ce cas masquerait une suppression ;
    * que le remplacement designe EXACTEMENT le meme chemin -- l'appariement
      est un-pour-un sur le fichier, jamais sur une ressemblance ;
    * qu'aucune empreinte ne serve deux fois, dans un sens ou dans l'autre.

    Aucun objet ne quitte le blocage de release : il y reste sous son
    identite corrigee.
    """

    path = root / "audit/ANOMALY_IDENTITY_CORRECTIONS.yaml"
    if not path.is_file():
        return set()
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    corrections = payload.get("corrections")
    if not isinstance(corrections, Mapping):
        return set()

    stale_fingerprints: set[str] = set()
    replacements: set[str] = set()
    for stale, correction in sorted(corrections.items()):
        if not isinstance(correction, Mapping):
            raise ValueError(f"correction d'identite invalide: {stale}")
        stale = str(stale)
        replacement = str(correction.get("corrected_fingerprint", ""))
        declared_path = str(correction.get("path", ""))
        if not replacement or not declared_path:
            raise ValueError(f"correction d'identite incomplete: {stale}")
        if stale in current_active:
            raise ValueError(
                f"empreinte declaree corrigee encore active: {stale}"
            )
        if replacement not in current_active:
            raise ValueError(
                f"correction d'identite sans remplacement actif: {stale}"
            )
        if paths_by_fingerprint.get(replacement) != declared_path:
            raise ValueError(
                f"remplacement sur un autre chemin que celui declare: {stale}"
            )
        if stale in stale_fingerprints or replacement in replacements:
            raise ValueError(
                f"appariement de correction d'identite non un-pour-un: {stale}"
            )
        stale_fingerprints.add(stale)
        replacements.add(replacement)
    return stale_fingerprints


def _superseded_by_rewrite(
    root: Path, *, current_active: set[str]
) -> set[str]:
    """Empreintes qu'une REECRITURE a fait disparaitre, et rien d'autre.

    Une migration d'identite ne transporte une qualification qu'a travers une
    transformation qui preserve l'identite. Quand l'objet est reecrit, la
    migration est declaree `superseded_by_rewrite` : son empreinte quitte
    l'ensemble actif, et l'inventaire n'accepte cette sortie que si l'objet
    est simultanement declare comme dette de revue ouverte et bloquante.

    Ces empreintes ne sont donc ni resolues ni qualifiees : elles ont ete
    remplacees par une dette, et c'est cette dette qui figure dans les
    registres declares.
    """

    path = root / "audit/ANOMALY_IDENTITY_MIGRATIONS.yaml"
    if not path.is_file():
        return set()
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    migrations = payload.get("migrations")
    if not isinstance(migrations, Mapping):
        return set()
    superseded: set[str] = set()
    for fingerprint, migration in migrations.items():
        if not isinstance(migration, Mapping):
            continue
        if migration.get("superseded_by_rewrite") is not True:
            continue
        if not str(migration.get("superseded_declared_in", "")).strip():
            raise ValueError(
                f"supersession sans registre declare: {fingerprint}"
            )
        ledger_relative = Path(str(migration["superseded_declared_in"]))
        ledger_path = (root / ledger_relative).resolve()
        if not ledger_path.is_relative_to(root.resolve()) or not ledger_path.is_file():
            raise ValueError(
                f"registre de supersession absent ou hors dépôt: {fingerprint}"
            )
        ledger = _read_json(ledger_path)
        entries = ledger.get("entries")
        if not isinstance(entries, list):
            raise ValueError(f"registre de supersession sans entries: {fingerprint}")
        # La jointure se fait sur le CHEMIN, jamais sur l'identifiant declare :
        # une reecriture a precisement le droit de corriger la META, et c'est
        # le cas AGT -> APT. Exiger l'egalite des identifiants rendait la
        # supersession introuvable des que la reecriture faisait son travail.
        candidates = [
            entry
            for entry in entries
            if entry.get("path") == migration.get("current_source")
            and entry.get("chapter") == migration.get("chapter")
            and entry.get("origin") in _REWRITTEN_ORIGINS
            # Une approbation humaine reelle DOIT etre declaree perimee ; une
            # verification machine n'a jamais ete une approbation et ne peut
            # donc pas en perimer une. Le registre ne doit inventer ni l'une
            # ni l'autre.
            and entry.get("human_approval_invalidated_by_rewrite")
            is (entry.get("human_approval_evidence") is True)
            and str(entry.get("fingerprint")) in current_active
        ]
        if len(candidates) != 1:
            raise ValueError(
                f"supersession sans remplacement courant exact: {fingerprint}"
            )
        if str(fingerprint) in current_active:
            raise ValueError(
                f"ancienne empreinte supersédée encore active: {fingerprint}"
            )
        replacement = candidates[0]
        if str(replacement["fingerprint"]) == str(fingerprint):
            raise ValueError(
                f"remplacement de supersession sans nouvelle empreinte: {fingerprint}"
            )
        source_path = root / str(replacement["path"])
        if not source_path.is_file():
            raise ValueError(f"source de remplacement absente: {fingerprint}")
        frozen_sha = str(migration.get("current_source_sha256") or "")
        observed_sha = _source_sha(source_path)
        if frozen_sha and observed_sha == frozen_sha:
            raise ValueError(
                f"supersession déclarée sans réécriture observée: {fingerprint}"
            )
        superseded.add(str(fingerprint))
    return superseded


def _validate_frozen_inputs(root: Path) -> tuple[Path, Path]:
    paths = (root / INITIAL_JSON_REL, root / INITIAL_MD_REL)
    for path in paths:
        expected = FROZEN_SHA256[path.relative_to(root)]
        try:
            observed = _sha256_bytes(path.read_bytes())
        except OSError as exc:
            raise ValueError(f"artefact initial figé illisible: {path}") from exc
        if observed != expected:
            raise ValueError(
                "artefact initial figé modifié: "
                f"{path.relative_to(root)} attendu={expected} observé={observed}"
            )
    return paths


def _active_unqualified(qualifications: Mapping[str, Any]) -> set[str]:
    return {
        str(fingerprint)
        for fingerprint, qualification in qualifications.items()
        if isinstance(qualification, Mapping)
        and qualification.get("qualified") is False
        and qualification.get("disposition") == "open_debt"
    }


def _active_open_debt(qualifications: Mapping[str, Any]) -> set[str]:
    """Return active debt independently of its non-regression qualification."""

    return {
        str(fingerprint)
        for fingerprint, qualification in qualifications.items()
        if isinstance(qualification, Mapping)
        and qualification.get("disposition") == "open_debt"
    }


def _current_anomaly(
    inventory: Mapping[str, Any],
    *,
    category: str,
    path: str,
) -> Mapping[str, Any]:
    anomalies = inventory.get("anomalies")
    if not isinstance(anomalies, Mapping):
        raise ValueError("inventaire sans anomalies")
    values = anomalies.get(category)
    if not isinstance(values, list):
        raise ValueError(f"catégorie d'anomalie absente: {category}")
    matches = [
        item
        for item in values
        if isinstance(item, Mapping) and item.get("path") == path
    ]
    if len(matches) != 1:
        raise ValueError(
            f"anomalie courante non univoque: {category} {path} ({len(matches)})"
        )
    return matches[0]


def _initial_entry(
    *,
    root: Path,
    entry: Mapping[str, Any],
    inventory: Mapping[str, Any],
) -> dict[str, Any]:
    fingerprint = str(entry["fingerprint"])
    category = str(entry["anomaly_category"])
    path = str(entry["path"])
    anomaly = _current_anomaly(inventory, category=category, path=path)
    qualification = inventory["anomaly_qualifications"][fingerprint]
    if (
        qualification.get("disposition") != "open_debt"
        or qualification.get("blocking") is not True
        or qualification.get("release_blocking") is not True
    ):
        raise ValueError(
            f"dette résiduelle non bloquante ou clôturée: {fingerprint}"
        )
    current_sha = _source_sha(root / path)
    original_class = str(entry["triage_class"])
    content_fixed = original_class == "FIX_NOW"
    if content_fixed and FIXED_SOURCE_SHA256.get(fingerprint) != current_sha:
        raise ValueError(
            "preuve sémantique FIX_NOW absente ou source divergente: "
            f"{fingerprint} attendu={FIXED_SOURCE_SHA256.get(fingerprint)} "
            f"observé={current_sha}"
        )
    if original_class not in {"FIX_NOW", "LEGITIMATE_REVIEW_DEBT"}:
        raise ValueError(f"classe active résiduelle interdite: {fingerprint}")

    anomalies = inventory.get("anomalies")
    if not isinstance(anomalies, Mapping):
        raise ValueError("inventaire sans anomalies")
    structural_hits = sorted(
        category
        for category in STRUCTURAL_DISQUALIFIERS
        for item in anomalies.get(category, [])
        if isinstance(item, Mapping) and item.get("path") == path
    )
    if structural_hits:
        raise ValueError(
            f"conditions B structurelles en échec pour {fingerprint}: "
            + ", ".join(structural_hits)
        )
    if entry.get("structure_state") != "PASS":
        raise ValueError(f"structure_state non PASS: {fingerprint}")
    if entry.get("reason_created") not in ALLOWED_EDITORIAL_REASONS:
        raise ValueError(f"raison éditoriale B non prouvée: {fingerprint}")
    if not content_fixed and "FAIL" in str(entry.get("scientific_state")):
        raise ValueError(f"erreur scientifique connue en classe B: {fingerprint}")
    if not content_fixed and "FAIL" in str(entry.get("pedagogical_state")):
        raise ValueError(f"erreur pédagogique connue en classe B: {fingerprint}")

    if content_fixed:
        why_legitimate = (
            "Le finding initial est corrigé par une source au digest exact et par "
            "les tests de régression; seul le statut non approuvé reste ouvert."
        )
    else:
        why_legitimate = (
            "Le triage initial prouve une dette de revue éditoriale ou humaine "
            "légitime, toujours portée par le statut source courant."
        )

    return {
        "fingerprint": fingerprint,
        "object_id": str(entry["object_id"]),
        "path": path,
        "category": category,
        "manual": str(entry["manual"]),
        "chapter": str(entry["chapter"]),
        "object_type": str(entry["object_type"]),
        "source_status": str(anomaly.get("status", entry.get("status", ""))),
        "source_sha": current_sha,
        "initial_source_sha": str(entry["source_sha"]),
        "content_finding_fixed": content_fixed,
        "reason_created": str(entry["reason_created"]),
        "original_triage_class": original_class,
        "triage_class": "LEGITIMATE_REVIEW_DEBT",
        "class_b_eligibility": {
            "structure": "PASS",
            "programme_role_determined": "PASS",
            "wrong_year": "NO",
            "unsupported_claim": "NO",
            "duplicate": "NO",
            "orphan": "NO",
            "unassembled": "NO",
            "broken_refs": "NO",
            "placeholder": "NO",
            "known_science_error": "NO",
            "known_pedagogy_error": "NO",
            "student_teacher_leak": "NO",
            "known_layout_blocker": "NO",
        },
        "why_legitimate": why_legitimate,
        "why_cannot_close": (
            "La source reste non approuvée et la gouvernance exige une décision "
            "humaine après les contrôles machine; aucune approbation n'est forgée. "
            f"disposition={qualification['disposition']}, "
            f"qualified={str(qualification['qualified']).lower()}."
        ),
        "current_review_state": (
            "PENDING_QUALIFIED_OPEN_DEBT"
            if qualification.get("qualified") is True
            else "PENDING_UNQUALIFIED"
        ),
        "owner": str(entry["owner"]),
        "closure_phase": str(entry["intended_closure_phase"]),
        "release_acceptance": False,
}


def build_reports(
    root: Path = ROOT,
    *,
    inventory_path: Path | None = None,
    forensic_source_sha: str | None = None,
) -> dict[str, dict[str, Any]]:
    """Return both deterministic residual reports without writing files."""

    root = root.resolve()
    initial_json_path, initial_md_path = _validate_frozen_inputs(root)
    inventory_path = (
        inventory_path.resolve()
        if inventory_path is not None
        else root / INVENTORY_REL
    )
    initial = _read_json(initial_json_path)
    inventory = _read_json(inventory_path)

    initial_entries = initial.get("entries")
    if not isinstance(initial_entries, list) or len(initial_entries) != 18:
        raise ValueError("le ledger initial doit contenir exactement 18 lignes")
    initial_fingerprints = {
        str(entry.get("fingerprint"))
        for entry in initial_entries
        if isinstance(entry, Mapping)
    }
    if len(initial_fingerprints) != 18 or initial.get("true_new_initial") != 18:
        raise ValueError("les 18 fingerprints initiaux ne sont pas univoques")
    if initial.get("counts") != {
        "FIX_NOW": 5,
        "LEGITIMATE_REVIEW_DEBT": 8,
        "SHOULD_NOT_EXIST": 5,
    }:
        raise ValueError("triage initial 5/8/5 inattendu")

    qualifications = inventory.get("anomaly_qualifications")
    if not isinstance(qualifications, Mapping):
        raise ValueError("inventaire sans qualifications d'anomalies")
    active_unqualified = _active_unqualified(qualifications)
    active_open_debt = _active_open_debt(qualifications)
    declared_debt = _declared_separate_debt(root)
    separate_debt = set().union(*declared_debt.values()) if declared_debt else set()
    # L'imputation unique est decidee par UNE fonction, partagee par tous les
    # consommateurs : la corriger ici seulement laisserait le meme defaut
    # vivant ailleurs.
    suspended = _suspended_qualifications(root) - _assignment_module().demoted_by_precedence(
        declared_debt, {"SUSPENDED_QUALIFICATIONS": _suspended_qualifications(root)}
    )
    extra = sorted(
        active_unqualified - initial_fingerprints - separate_debt - suspended
    )
    if extra:
        raise ValueError(
            "ensemble actif non qualifié inattendu: "
            f"supplémentaires={extra}"
        )

    initial_by_fingerprint = {
        str(entry["fingerprint"]): entry for entry in initial_entries
    }
    should_not_exist = {
        fingerprint
        for fingerprint, entry in initial_by_fingerprint.items()
        if entry.get("triage_class") == "SHOULD_NOT_EXIST"
    }
    fix_now_fingerprints = {
        fingerprint
        for fingerprint, entry in initial_by_fingerprint.items()
        if entry.get("triage_class") == "FIX_NOW"
    }
    if fix_now_fingerprints != set(FIXED_SOURCE_SHA256):
        raise ValueError("preuves FIX_NOW non bijectives avec le ledger")
    for fingerprint in sorted(fix_now_fingerprints):
        path = root / str(initial_by_fingerprint[fingerprint]["path"])
        observed = _source_sha(path)
        if observed != FIXED_SOURCE_SHA256[fingerprint]:
            raise ValueError(
                "preuve sémantique FIX_NOW absente ou source divergente: "
                f"{fingerprint} attendu={FIXED_SOURCE_SHA256[fingerprint]} "
                f"observé={observed}"
            )
    removed = set()
    fixed = set()
    review_closed = set()
    for fingerprint, entry in initial_by_fingerprint.items():
        path_exists = (root / str(entry["path"])).exists()
        is_active = fingerprint in active_open_debt
        if fingerprint in should_not_exist:
            if fingerprint in qualifications or path_exists:
                raise ValueError(
                    f"objet SHOULD_NOT_EXIST encore présent: {fingerprint}"
                )
            removed.add(fingerprint)
            continue
        if not path_exists:
            raise ValueError(f"objet légitime supprimé: {fingerprint}")
        if is_active:
            continue
        qualification = qualifications.get(fingerprint, {})
        if entry.get("triage_class") == "FIX_NOW":
            fixed.add(fingerprint)
        elif (
            isinstance(qualification, Mapping)
            and (
                qualification.get("qualified") is True
                or qualification.get("disposition") != "open_debt"
            )
        ):
            review_closed.add(fingerprint)
        else:
            raise ValueError(f"fermeture sans preuve de revue: {fingerprint}")

    residual_fingerprints = (
        initial_fingerprints - removed - fixed - review_closed
    )
    active_residual_debt = active_open_debt & initial_fingerprints
    if active_residual_debt != residual_fingerprints:
        raise ValueError(
            "projection résiduelle incohérente: "
            f"attendu={sorted(residual_fingerprints)} "
            f"observé={sorted(active_residual_debt)}"
        )
    entries = [
        _initial_entry(
            root=root,
            entry=initial_by_fingerprint[fingerprint],
            inventory=inventory,
        )
        for fingerprint in sorted(residual_fingerprints)
    ]
    entries.sort(key=lambda entry: entry["fingerprint"])
    content_findings_fixed = len(fix_now_fingerprints)
    counts = {
        "TRUE_NEW_INITIAL": len(initial_fingerprints),
        "FIXED": len(fixed),
        "REMOVED": len(removed),
        "REVIEW_CLOSED": len(review_closed),
        "CONTENT_FINDINGS_FIXED": content_findings_fixed,
        "NEW_AFTER_TRIAGE": 0,
        "RESIDUAL_TRUE_NEW": len(residual_fingerprints),
    }

    initial_bytes = initial_json_path.read_bytes()
    inventory_bytes = inventory_path.read_bytes()
    input_digest = "sha256:" + _sha256_bytes(
        initial_bytes + b"\0" + initial_md_path.read_bytes() + b"\0" + inventory_bytes
    )
    forensic_source_sha = (
        _validate_git_sha(forensic_source_sha)
        if forensic_source_sha is not None
        else _git_head(root)
    )
    evidence = {
        "frozen_initial_json": str(INITIAL_JSON_REL),
        "frozen_initial_json_sha256": "sha256:" + FROZEN_SHA256[INITIAL_JSON_REL],
        "frozen_initial_md": str(INITIAL_MD_REL),
        "frozen_initial_md_sha256": "sha256:" + FROZEN_SHA256[INITIAL_MD_REL],
        "inventory": str(inventory_path.relative_to(root))
        if inventory_path.is_relative_to(root)
        else str(inventory_path),
        "inventory_sha256": "sha256:" + _sha256_bytes(inventory_bytes),
        "inventory_source_digest": inventory.get("source_digest"),
        "input_digest": input_digest,
    }
    residual_set = [entry["fingerprint"] for entry in entries]
    initial_algebra = _read_json(root / INITIAL_ALGEBRA_REL)
    try:
        frozen_sets = initial_algebra["set_algebra"]["sets"]
        unchanged = set(frozen_sets["UNCHANGED"])
        transition_old = set(frozen_sets["APPROVED_TRANSITION_OLD"])
        transition_new = set(frozen_sets["APPROVED_TRANSITION_NEW"])
        expected_review_debt = set(frozen_sets["EXPECTED_REVIEW_DEBT"])
        baseline = set(frozen_sets["BASELINE"])
        resolved_baseline = set(frozen_sets["RESOLVED_BASELINE"])
        surviving_baseline = set(frozen_sets["SURVIVING_BASELINE"])
    except (KeyError, TypeError) as exc:
        raise ValueError("algèbre initiale incomplète") from exc
    current_active = set(str(value) for value in qualifications)
    # Une empreinte que la reecriture a fait disparaitre ne peut plus figurer
    # dans la partition courante : son objet existe toujours, mais sous une
    # identite neuve et non qualifiee, portee par un registre de dette.
    superseded = _superseded_by_rewrite(root, current_active=current_active)
    orphaned = superseded - current_active
    # Une identite corrigee apres le gel fait disparaitre l'empreinte figee
    # sans que l'objet bouge : elle est retiree contre la preuve de son
    # remplacement actif, jamais parce qu'elle gene.
    paths_by_fingerprint = _anomaly_paths_by_fingerprint(inventory)
    corrected = _identity_corrections(
        root,
        current_active=current_active,
        paths_by_fingerprint=paths_by_fingerprint,
    )
    transition_new = transition_new - orphaned - corrected
    unchanged = unchanged - corrected
    expected_review_debt = expected_review_debt - corrected
    # Un objet entre dans un registre de dette DECLAREE des qu'il change. Les
    # ensembles geles, eux, le decrivent tel qu'il etait : sans cette
    # soustraction il appartiendrait a deux classes a la fois. Il reste
    # bloquant des deux cotes, seule sa classe d'imputation bouge.
    unchanged = unchanged - separate_debt
    expected_review_debt = expected_review_debt - separate_debt
    current_partition = (
        unchanged
        | transition_new
        | expected_review_debt
        | residual_fingerprints
        | separate_debt
    )
    current_components = (
        unchanged,
        transition_new,
        expected_review_debt,
        residual_fingerprints,
        *declared_debt.values(),
    )
    current_pairwise_disjoint = all(
        not left & right
        for left, right in combinations(current_components, 2)
    )
    if current_partition != current_active or not current_pairwise_disjoint:
        raise ValueError("l'algèbre CURRENT_ACTIVE résiduelle est incohérente")
    full_named_sets = {
        "BASELINE": baseline,
        "SURVIVING_BASELINE": surviving_baseline,
        "RESOLVED_BASELINE": resolved_baseline,
        "PREVIOUSLY_QUALIFIED_ACTIVE_DEBT": expected_review_debt,
        "EXPECTED_REVIEW_DEBT": expected_review_debt,
        "APPROVED_TRANSITION_OLD": transition_old,
        "APPROVED_TRANSITION_NEW": transition_new,
        "TRUE_NEW": residual_fingerprints,
        **declared_debt,
        "CURRENT_ACTIVE": current_active,
        "UNCHANGED": unchanged,
    }
    nonempty_intersections = []
    for left_name, right_name in combinations(full_named_sets, 2):
        intersection = (
            full_named_sets[left_name] & full_named_sets[right_name]
        )
        if intersection:
            nonempty_intersections.append(
                {
                    "left": left_name,
                    "right": right_name,
                    "cardinality": len(intersection),
                    "fingerprints": sorted(intersection),
                }
            )
    full_current_algebra = {
        "cardinalities": {
            name: len(values) for name, values in full_named_sets.items()
        },
        "cardinality_equation": (
            f"{len(current_active)} = {len(unchanged)} + "
            f"{len(transition_new)} + {len(expected_review_debt)} + "
            f"{len(residual_fingerprints)}"
            + "".join(f" + {len(values)}" for values in declared_debt.values())
        ),
        "equalities": {
            "baseline_partition": (
                baseline == resolved_baseline | surviving_baseline
            ),
            "current_partition": current_partition == current_active,
            "current_partition_pairwise_disjoint": current_pairwise_disjoint,
        },
        "sets": {
            name: sorted(values) for name, values in full_named_sets.items()
        },
        "nonempty_intersections": nonempty_intersections,
        "unknown_count": 0,
    }
    residual_forensics = {
        "schema_version": 1,
        "artifact_type": "residual_true_new_forensics",
        "baseline_modified": False,
        "policy_modified": False,
        "release_acceptance": False,
        "forensic_source_sha": forensic_source_sha,
        "counts": counts,
        "evidence": evidence,
        "entries": entries,
    }
    residual_algebra = {
        "schema_version": 1,
        "artifact_type": "current_anomaly_set_algebra_residual",
        "baseline_modified": False,
        "policy_modified": False,
        "release_acceptance": False,
        "forensic_source_sha": forensic_source_sha,
        "counts": counts,
        "equation": (
            "RESIDUAL_TRUE_NEW = TRUE_NEW_INITIAL - FIXED - REMOVED "
            "- REVIEW_CLOSED + NEW_AFTER_TRIAGE"
        ),
        "cardinality_equation": (
            f"{len(residual_fingerprints)} = {len(initial_fingerprints)} "
            f"- {len(fixed)} - {len(removed)} - {len(review_closed)} + 0"
        ),
        "equalities": {
            "initial_still_active_open_debt": (
                active_residual_debt == residual_fingerprints
            ),
            # Le modele residuel porte sur le gel des 18. La dette VARALEA
            # C6/C7 en est exclue par construction : elle est comptee, nommee
            # et bloquante dans son propre composant de l'algebre courante.
            # Les qualifications suspendues ne sont pas des nouveautes de
            # triage : leur classe est comptee a part et fermee par une
            # re-qualification humaine, jamais par le triage residuel.
            "no_new_after_triage": not (
                active_unqualified
                - initial_fingerprints
                - separate_debt
                - suspended
            ),
            "residual_equation": (
                len(residual_fingerprints)
                == len(initial_fingerprints)
                - len(fixed)
                - len(removed)
                - len(review_closed)
            ),
        },
        "sets": {
            "TRUE_NEW_INITIAL": sorted(initial_fingerprints),
            "FIXED": sorted(fixed),
            "REMOVED": sorted(removed),
            "REVIEW_CLOSED": sorted(review_closed),
            "NEW_AFTER_TRIAGE": [],
            "RESIDUAL_TRUE_NEW": residual_set,
            "EXCLUDED_DECLARED_SEPARATE_DEBT": {
                name: sorted(values) for name, values in declared_debt.items()
            },
        },
        "full_current_algebra": full_current_algebra,
        "evidence": evidence,
    }
    return {
        "residual_forensics": residual_forensics,
        "residual_algebra": residual_algebra,
    }


def _build_reports_with_stable_source(
    root: Path, output_dir: Path, forensic_source_sha: str
) -> dict[str, dict[str, Any]]:
    """Project reports only while the frozen source snapshot stays unchanged."""

    _assert_source_snapshot(root, output_dir, forensic_source_sha)
    reports = build_reports(
        root,
        forensic_source_sha=forensic_source_sha,
    )
    _assert_source_snapshot(root, output_dir, forensic_source_sha)
    return reports


def _json_text(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _md_cell(value: object) -> str:
    return str(value).replace("|", "\\|").replace("\n", " ")


def _forensics_markdown(payload: Mapping[str, Any]) -> str:
    lines = [
        "# Residual TRUE_NEW forensics",
        "",
        "Projection déterministe de la dette de revue active. Cette preuve ne modifie "
        "ni baseline, ni policy, ni oracle et n'accorde aucune acceptation release.",
        "",
        f"`FORENSIC_SOURCE_SHA = {payload['forensic_source_sha']}`",
        "",
        "## Counts",
        "",
    ]
    for key, value in payload["counts"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(
        [
            "",
            "## Residual entries",
            "",
            "| fingerprint | object_id | path | category | source status | source SHA | "
            "why legitimate | why cannot close | review state | owner | closure phase | "
            "release acceptance |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for entry in payload["entries"]:
        cells = [
            entry["fingerprint"],
            entry["object_id"],
            entry["path"],
            entry["category"],
            entry["source_status"],
            entry["source_sha"],
            entry["why_legitimate"],
            entry["why_cannot_close"],
            entry["current_review_state"],
            entry["owner"],
            entry["closure_phase"],
            str(entry["release_acceptance"]).lower(),
        ]
        lines.append("| " + " | ".join(_md_cell(value) for value in cells) + " |")
    return "\n".join(lines) + "\n"


def _algebra_markdown(payload: Mapping[str, Any]) -> str:
    lines = [
        "# Current anomaly set algebra — residual",
        "",
        f"`FORENSIC_SOURCE_SHA = {payload['forensic_source_sha']}`",
        "",
        f"`{payload['equation']}`",
        "",
        f"`{payload['cardinality_equation']}`",
        "",
        "## Counts",
        "",
    ]
    for key, value in payload["counts"].items():
        lines.append(f"- `{key}`: `{value}`")
    lines.extend(["", "## Sets", ""])
    for key, values in payload["sets"].items():
        rendered = ", ".join(f"`{value}`" for value in values) or "∅"
        lines.append(f"- `{key}`: {rendered}")
    full = payload["full_current_algebra"]
    lines.extend(
        [
            "",
            "## Algèbre CURRENT_ACTIVE recalculée",
            "",
            f"`{full['cardinality_equation']}`",
            "",
            f"- `CURRENT_ACTIVE`: `{full['cardinalities']['CURRENT_ACTIVE']}`",
            f"- `UNCHANGED`: `{full['cardinalities']['UNCHANGED']}`",
            "- `APPROVED_TRANSITION_NEW`: "
            f"`{full['cardinalities']['APPROVED_TRANSITION_NEW']}`",
            "- `EXPECTED_REVIEW_DEBT`: "
            f"`{full['cardinalities']['EXPECTED_REVIEW_DEBT']}`",
            f"- `TRUE_NEW`: `{full['cardinalities']['TRUE_NEW']}`",
            f"- `UNKNOWN`: `{full['unknown_count']}`",
            "",
            "`release_acceptance = false` — les "
            f"{payload['counts']['RESIDUAL_TRUE_NEW']} lignes restent une dette de revue.",
        ]
    )
    return "\n".join(lines) + "\n"


def render_reports(reports: Mapping[str, Mapping[str, Any]]) -> dict[str, str]:
    return {
        OUTPUT_NAMES["residual_forensics"]["json"]: _json_text(
            reports["residual_forensics"]
        ),
        OUTPUT_NAMES["residual_forensics"]["md"]: _forensics_markdown(
            reports["residual_forensics"]
        ),
        OUTPUT_NAMES["residual_algebra"]["json"]: _json_text(
            reports["residual_algebra"]
        ),
        OUTPUT_NAMES["residual_algebra"]["md"]: _algebra_markdown(
            reports["residual_algebra"]
        ),
    }


def _atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def write_reports(
    reports: Mapping[str, Mapping[str, Any]], output_dir: Path
) -> None:
    for name, content in sorted(render_reports(reports).items()):
        _atomic_write(output_dir / name, content)


def check_reports(
    reports: Mapping[str, Mapping[str, Any]], output_dir: Path
) -> list[str]:
    stale = []
    for name, content in sorted(render_reports(reports).items()):
        path = output_dir / name
        if not path.is_file() or path.read_text(encoding="utf-8") != content:
            stale.append(name)
    return stale


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    output_dir = (
        args.output_dir.resolve()
        if args.output_dir is not None
        else root / "audit"
    )
    forensic_source_sha = (
        _forensic_source_sha_for_check(root, output_dir)
        if args.check
        else _git_head(root)
    )
    reports = _build_reports_with_stable_source(
        root, output_dir, forensic_source_sha
    )
    if args.check:
        stale = check_reports(reports, output_dir)
        _assert_source_snapshot(root, output_dir, forensic_source_sha)
        if stale:
            print("stale: " + ", ".join(stale))
            return 1
        print("current: residual TRUE_NEW forensics")
        return 0
    write_reports(reports, output_dir)
    _assert_source_snapshot(root, output_dir, forensic_source_sha)
    print("written: " + ", ".join(sorted(render_reports(reports))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
