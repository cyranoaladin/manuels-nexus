#!/usr/bin/env python3
"""Lie le gel historique 1SPE-SUITES a l'etat courant du depot.

Decision humaine du 2026-08-28 : le gel canonique reste c667f12b / 161 objets
et n'est PAS reemis parce que HEAD a avance. Le gel est une identite de
CONTENU, pas l'exigence que le depot reste a son commit d'origine.

Cet artefact est donc distinct du gel : il ne le modifie jamais, il declare si
l'etat courant lui est equivalent. Ni le SHA de HEAD ni le nom de branche
n'entrent dans le verdict.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_JSON = ROOT / "audit" / "1SPE_SUITES_CURRENT_FREEZE_BINDING.json"
OUTPUT_MD = ROOT / "audit" / "1SPE_SUITES_CURRENT_FREEZE_BINDING.md"

BINDING_CURRENT = "CURRENT_EQUIVALENT_TO_FROZEN_CONTENT"
BINDING_STALE = "STALE_CONTENT_CHANGED"

#: Regle de variante : ces objets ne parviennent jamais a l'eleve.
TEACHER_ONLY_MARKERS = ("/corriges/", "corrige")


def _freeze_module():
    path = ROOT / "scripts" / "build_1spe_suites_review_source_freeze.py"
    spec = importlib.util.spec_from_file_location("_suites_freeze", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, text=True, capture_output=True, check=True
    ).stdout.strip()


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def _content_projection(rows: list[dict[str, Any]]) -> str:
    """Projection comparable : ce qui est du contenu, rien de ce qui est du commit.

    git_blob_sha1 et source_commit_sha changent des que l'historique avance et
    ne disent rien du contenu ; ils sont donc exclus de la comparaison.
    """

    projected = [
        {
            "object_id": row["object_id"],
            "object_type": row.get("object_type"),
            "path": row["path"],
            "source_kind": row.get("source_kind"),
            "status": row.get("status"),
            "source_sha256": row["source_sha256"],
        }
        for row in rows
    ]
    projected.sort(key=lambda row: row["object_id"])
    return canonical_digest(projected)


def _is_teacher_only(path: str) -> bool:
    lowered = path.lower()
    return any(marker in lowered for marker in TEACHER_ONLY_MARKERS)


def _variant_partition(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    teacher = sorted(r["object_id"] for r in rows if _is_teacher_only(r["path"]))
    student = sorted(r["object_id"] for r in rows if not _is_teacher_only(r["path"]))
    return {"teacher_only": teacher, "student_visible": student}


def build_binding() -> dict[str, Any]:
    freeze_module = _freeze_module()
    freeze = freeze_module.build_freeze()
    rows = freeze["objects"]

    # --- identite binaire des sources du chapitre -----------------------------
    missing: list[str] = []
    modified: list[str] = []
    extra_ids: list[str] = []
    current_rows: list[dict[str, Any]] = []
    for row in rows:
        candidate = ROOT / row["path"]
        if not candidate.is_file():
            missing.append(row["object_id"])
            continue
        digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
        if digest != row["source_sha256"]:
            modified.append(row["object_id"])
        current_rows.append({**row, "source_sha256": digest})

    # --- aucun objet supplementaire dans le chapitre --------------------------
    # Tous les chemins que le gel lie, a quelque titre que ce soit : le QCM
    # genere est lie comme qcm.generated_tex et non comme objet, il n'est donc
    # pas un fichier supplementaire.
    frozen_paths = {row["path"] for row in rows}
    frozen_paths.add(freeze["contract"]["path"])
    frozen_paths.add(freeze["qcm"]["canonical"]["path"])
    frozen_paths.add(freeze["qcm"]["generated_tex"]["path"])
    frozen_paths.update(source["path"] for source in freeze["remediation"]["sources"])
    chapter_root = ROOT / freeze_module.CHAPTER_PREFIX
    observed_paths = {
        path.relative_to(ROOT).as_posix()
        for path in sorted(chapter_root.rglob("*"))
        if path.is_file() and path.suffix in {".tex", ".json"}
    }
    # Le gel ne retient que les objets porteurs d'un META (ou le QCM canonique) ;
    # un fichier supplementaire n'est un objet que s'il porte un META.
    supplementary = sorted(
        path
        for path in observed_paths - frozen_paths
        if path.endswith(".tex") and "% META:" in (ROOT / path).read_text(encoding="utf-8")
    )
    extra_ids.extend(supplementary)

    object_blob_identity_pass = not missing and not modified and not supplementary

    # --- identite semantique des sources couvertes ----------------------------
    covered = [freeze["contract"], freeze["qcm"]["canonical"], freeze["qcm"]["generated_tex"]]
    covered.extend(freeze["remediation"]["sources"])
    def _frozen_sha256(binding: dict[str, Any]) -> str:
        # Le gel nomme le condense "sha256" pour les liaisons nommees et
        # "source_sha256" pour les objets et les remediations.
        return binding.get("sha256") or binding["source_sha256"]

    semantic_drift = [
        binding["path"]
        for binding in covered
        if not (ROOT / binding["path"]).is_file()
        or hashlib.sha256((ROOT / binding["path"]).read_bytes()).hexdigest()
        != _frozen_sha256(binding)
    ]
    semantic_identity_pass = object_blob_identity_pass and not semantic_drift

    # --- identite de l'autorite programme, par projection de chapitre ---------
    authority_drift: list[str] = []
    for binding in freeze["programme_authority"]["sources"]:
        path = binding["path"]
        frozen_projection = freeze_module.programme_authority_projection(
            path, freeze_module._source_bytes(path)
        )
        current_projection = freeze_module.programme_authority_projection(
            path, freeze_module._current_bytes(path)
        )
        if frozen_projection != current_projection:
            authority_drift.append(path)
    programme_authority_identity_pass = not authority_drift

    # --- identite semantique des regles de variante ---------------------------
    frozen_partition = _variant_partition(rows)
    current_partition = _variant_partition(current_rows)
    qcm_tex = ROOT / freeze["qcm"]["generated_tex"]["path"]
    key_is_conditioned = False
    if qcm_tex.is_file():
        text = qcm_tex.read_text(encoding="utf-8")
        if "\\ifnxVersionProfesseur" in text and "Cle de correction" in text:
            key_is_conditioned = (
                text.index("\\ifnxVersionProfesseur")
                < text.index("Cle de correction")
                < text.rindex("\\fi")
            )
    variant_semantic_identity_pass = (
        frozen_partition == current_partition and key_is_conditioned
    )

    binding_state = (
        BINDING_CURRENT
        if object_blob_identity_pass
        and semantic_identity_pass
        and programme_authority_identity_pass
        and variant_semantic_identity_pass
        else BINDING_STALE
    )

    return {
        "artifact_type": "suites_current_freeze_binding",
        "schema_version": 1,
        "decision_ref": "decision humaine 2026-08-28 : conserver le gel c667f12b / 161",
        "freeze_source_sha": freeze["source_sha"],
        "freeze_object_count": freeze["counts"]["chapter_objects"],
        "freeze_object_set_digest": freeze["chapter_object_set_digest"],
        "current_repository_sha": _git("rev-parse", "HEAD"),
        "current_branch": {
            "value": _git("rev-parse", "--abbrev-ref", "HEAD"),
            "binding": "INFORMATIONAL_ONLY",
            "note": "le nom de branche n'entre dans aucun verdict",
        },
        "current_object_count": len(current_rows),
        "current_object_set_digest": _content_projection(current_rows),
        "digest_semantics": {
            "freeze_object_set_digest": "enveloppe historique du gel, inclut le blob Git et le commit d'origine ; non comparable a un autre commit",
            "comparable_pair": "freeze_content_projection vs current_object_set_digest",
            "excluded_from_comparison": ["git_blob_sha1", "source_commit_sha", "HEAD", "nom de branche", "chemin absolu", "worktree"],
        },
        "freeze_content_projection": _content_projection(rows),
        "object_blob_identity_pass": object_blob_identity_pass,
        "semantic_identity_pass": semantic_identity_pass,
        "programme_authority_identity_pass": programme_authority_identity_pass,
        "variant_semantic_identity_pass": variant_semantic_identity_pass,
        "binding_state": binding_state,
        "findings": {
            "missing_objects": missing,
            "modified_objects": modified,
            "supplementary_objects": supplementary,
            "covered_source_drift": semantic_drift,
            "programme_authority_drift": authority_drift,
        },
        "staleness_rules": {
            "head_advanced": "NOT_STALE",
            "branch_renamed": "NOT_STALE",
            "other_worktree": "NOT_STALE",
            "derived_envelope_refreshed": "NOT_STALE",
            "authority_line_of_another_chapter": "NOT_STALE",
            "covered_source_content_changed": "STALE_CONTENT_CHANGED",
            "object_added_or_removed": "STALE_CONTENT_CHANGED",
            "qcm_correction_or_remediation_changed": "STALE_CONTENT_CHANGED",
            "chapter_programme_mapping_changed": "STALE_CONTENT_CHANGED",
            "variant_visibility_changed": "STALE_CONTENT_CHANGED",
            "automatic_rebind": "FORBIDDEN",
        },
        "review_state": {
            "review_a": "PENDING_UNASSIGNED",
            "review_b": "PENDING_UNASSIGNED",
            "human_receipts": 0,
            "publication_approval": False,
        },
    }


#: Champs purement observationnels : ils bougent a chaque commit sans qu'aucun
#: contenu ne change. Les inclure dans la comparaison de fraicheur rendrait
#: l'artefact perime par le commit qui le publie.
VOLATILE_OBSERVATION_FIELDS = ("current_repository_sha", "current_branch")


def render_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def stable_projection(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in payload.items()
        if key not in VOLATILE_OBSERVATION_FIELDS
    }


def render_md(payload: dict[str, Any]) -> str:
    checks = (
        ("object_blob_identity_pass", "Identité binaire des 161 sources"),
        ("semantic_identity_pass", "Identité sémantique des sources couvertes"),
        ("programme_authority_identity_pass", "Identité de l'autorité programme (projection chapitre)"),
        ("variant_semantic_identity_pass", "Identité des règles de variante"),
    )
    lines = [
        "# 1SPE-SUITES — liaison courante du gel",
        "",
        "Le gel canonique reste `c667f12b` / 161 objets (décision humaine du",
        "2026-08-28). Cet artefact ne le modifie pas : il déclare si l'état",
        "courant du dépôt lui est équivalent **en contenu**.",
        "",
        f"- gel : `{payload['freeze_source_sha']}` · {payload['freeze_object_count']} objets",
        f"- digest du gel : `{payload['freeze_object_set_digest']}`",
        "- dépôt courant : constaté à la génération, **non contraignant**",
        "- branche observée : **INFORMATIONAL_ONLY**",
        f"- objets courants : {payload['current_object_count']}",
        "",
        "## Contrôles",
        "",
        "| Contrôle | Résultat |",
        "|---|---|",
    ]
    for key, label in checks:
        lines.append(f"| {label} | {'**PASS**' if payload[key] else '**FAIL**'} |")
    lines += [
        "",
        f"## État : `{payload['binding_state']}`",
        "",
        "Ni l'avancée de HEAD, ni un changement de nom de branche, ni un autre",
        "worktree, ni le rafraîchissement d'une enveloppe dérivée, ni l'édition",
        "d'une ligne d'autorité concernant un autre chapitre ne périment ce gel.",
        "Une édition du contenu couvert, un objet ajouté ou retiré, une",
        "modification du QCM, d'un corrigé, d'une remédiation, du mapping",
        "programme du chapitre ou d'une règle de variante le périment.",
        "Aucun rebind automatique.",
        "",
        "Revues A et B : `PENDING_UNASSIGNED`. Aucun reçu humain. Publication non approuvée.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verifier sans ecrire")
    args = parser.parse_args(argv)
    payload = build_binding()
    rendered_json = render_json(payload)
    rendered_md = render_md(payload)
    if args.check:
        if not OUTPUT_JSON.is_file():
            raise SystemExit("STALE: audit/1SPE_SUITES_CURRENT_FREEZE_BINDING.json")
        committed = json.loads(OUTPUT_JSON.read_text(encoding="utf-8"))
        if stable_projection(committed) != stable_projection(payload):
            raise SystemExit("STALE: audit/1SPE_SUITES_CURRENT_FREEZE_BINDING.json")
        if not OUTPUT_MD.is_file():
            raise SystemExit("STALE: audit/1SPE_SUITES_CURRENT_FREEZE_BINDING.md")
        print(f"PASS 1SPE-SUITES current freeze binding: {payload['binding_state']}")
        return 0
    OUTPUT_JSON.write_text(rendered_json, encoding="utf-8")
    OUTPUT_MD.write_text(rendered_md, encoding="utf-8")
    print(f"wrote {OUTPUT_JSON.name} / {OUTPUT_MD.name}: {payload['binding_state']}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
