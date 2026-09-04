#!/usr/bin/env python3
"""Deux constructions indépendantes, les mêmes octets — preuve de candidat.

Un manuel qu'on ne peut pas refabriquer à l'identique n'est pas livrable : ce
que l'imprimeur reçoit doit être ce que le dépôt décrit, aujourd'hui et dans
six mois. La reproductibilité se prouve donc en construisant DEUX fois et en
comparant les octets, pas en faisant confiance au pipeline.

Ce que ce module constate, et rien de plus : deux constructions successives des
mêmes entrées de manuel donnent des PDF byte-identiques. Le statut est donc
`PIPELINE_DETERMINISM_CANDIDATE_EVIDENCE` : une preuve que le pipeline est
déterministe, et rien de plus. Elle ne devient pas une preuve de RELEASE ; si
les sources finales produisent ces mêmes empreintes, elle se réutilisera par
égalité d'empreinte, sinon un A/B final au SHA figé est dû.

Les deux constructions n'ont pas été lancées au même commit : entre elles, des
artefacts d'audit ont été livrés. Ce n'est PAS une preuve plus forte qu'un
double clean-room au même SHA -- c'est une preuve d'une autre chose, plus
faible pour la release : que le pipeline est déterministe à jeu d'entrées
manuel constant. La preuve de release, elle, se fera depuis
`1SPE_FINAL_CONTENT_SHA`, dans deux clean rooms indépendantes.

Le fait que les entrées soient identiques n'est pas raconté, il est mesuré :
les empreintes d'arbre Git des répertoires sources du manuel et l'empreinte de
la configuration de construction sont enregistrées pour A et pour B.

Métriques bloquantes : `VARIANTS_COMPARED`, `VARIANTS_DIFFERING`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import ROOT  # noqa: E402

JSON_TARGET = ROOT / "audit/1SPE_CANDIDATE_REPRODUCIBILITY.json"
MD_TARGET = ROOT / "audit/1SPE_CANDIDATE_REPRODUCIBILITY.md"
GENERATED_BY = "scripts/build_1spe_candidate_reproducibility.py"

BUILD = ROOT / "Mathematiques/manuel-maths/build/MANUEL_1SPE"
VARIANTS = ("eleve", "professeur")
STATUS = "PIPELINE_DETERMINISM_CANDIDATE_EVIDENCE"

# Les répertoires qui portent les entrées du manuel. Leur empreinte d'arbre Git
# EST le condensat de leur contenu : deux commits qui les partagent ont
# exactement les mêmes entrées, et cela se vérifie plutôt que se raconte.
MANUAL_INPUT_TREES = (
    "Mathematiques/manuel-maths/chapitres",
    "Mathematiques/manuel-maths/gabarits",
    "gabarits/common",
)
BUILD_CONFIGURATION_FILES = (
    "Mathematiques/manuel-maths/config/reproducible-build.json",
    "Mathematiques/manuel-maths/scripts/assemble_manuel.py",
)


class ReproducibilityError(RuntimeError):
    """Une preuve manque : la comparaison ne peut pas être faite."""


def _git_object(commit: str, path: str) -> str | None:
    result = subprocess.run(
        ["git", "rev-parse", f"{commit}:{path}"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def input_set_digest(commit: str) -> dict[str, Any]:
    """Le condensat des ENTRÉES du manuel à ce commit, mesuré et non déclaré."""

    trees = {path: _git_object(commit, path) for path in MANUAL_INPUT_TREES}
    configuration = {
        path: _git_object(commit, path) for path in BUILD_CONFIGURATION_FILES
    }
    if any(value is None for value in {**trees, **configuration}.values()):
        raise ReproducibilityError(f"entrées introuvables au commit {commit}")
    return {
        "manual_input_trees": trees,
        "manual_input_set_digest": "sha256:"
        + hashlib.sha256(
            "".join(f"{k}={trees[k]};" for k in sorted(trees)).encode("utf-8")
        ).hexdigest(),
        "build_configuration": configuration,
        "build_configuration_digest": "sha256:"
        + hashlib.sha256(
            "".join(
                f"{k}={configuration[k]};" for k in sorted(configuration)
            ).encode("utf-8")
        ).hexdigest(),
    }


def _digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def _page_count(path: Path) -> int:
    try:
        import fitz  # noqa: PLC0415
    except ModuleNotFoundError as error:  # pragma: no cover - dépendance
        raise ReproducibilityError("PyMuPDF (fitz) est requis") from error
    with fitz.open(path) as document:
        return document.page_count


def build_evidence(runs: dict[str, dict[str, str]]) -> dict[str, Any]:
    """`runs` : pour chaque variante, l'empreinte observée à la construction A."""

    variants: list[dict[str, Any]] = []
    for variant in VARIANTS:
        pdf = BUILD / f"MANUEL_1SPE_{variant}.pdf"
        if not pdf.is_file():
            raise ReproducibilityError(f"PDF absent : {pdf}")
        if variant not in runs:
            raise ReproducibilityError(f"aucune empreinte A pour {variant}")
        after = _digest(pdf)
        before = runs[variant]["pdf_sha256"]
        variants.append(
            {
                "variant": variant,
                "pdf_path": str(pdf.relative_to(ROOT)),
                "source_sha_a": runs[variant]["source_sha"],
                "source_sha_b": runs[variant]["source_sha_b"],
                "pdf_sha256_a": before,
                "pdf_sha256_b": after,
                "identical": before == after,
                "page_count": _page_count(pdf),
            }
        )
    differing = [row for row in variants if not row["identical"]]
    commit_a = variants[0]["source_sha_a"]
    commit_b = variants[0]["source_sha_b"]
    inputs_a = input_set_digest(commit_a)
    inputs_b = input_set_digest(commit_b)
    return {
        "artifact_type": "1spe_candidate_reproducibility",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "status": STATUS,
        "approves_nothing": True,
        "why_this_is_not_release_evidence": (
            "Les candidats courants sont PRINT_CANDIDATE_REPRODUCIBLE et ne "
            "vont pas dans TO_PRINTER : la couche de barème commenté n'est pas "
            "intégrée, 54 items attendent un jugement pédagogique, les revues "
            "de chapitre ne sont pas closes et le D7 n'est pas approuvé."
        ),
        "this_is_weaker_than_a_final_clean_room_pair": (
            "Deux constructions à des commits différents dont les entrées "
            "manuel coïncident prouvent le DÉTERMINISME DU PIPELINE. Ce n'est "
            "pas plus fort qu'un double clean-room au même "
            "1SPE_FINAL_CONTENT_SHA -- c'est plus faible, et cela ne remplace "
            "pas la preuve de release, qui reste due."
        ),
        "inputs_a": inputs_a,
        "inputs_b": inputs_b,
        "input_sets_coincide": (
            inputs_a["manual_input_set_digest"]
            == inputs_b["manual_input_set_digest"]
            and inputs_a["build_configuration_digest"]
            == inputs_b["build_configuration_digest"]
        ),
        "variants": variants,
        "summary": {
            "VARIANTS_COMPARED": len(variants),
            "VARIANTS_DIFFERING": len(differing),
            "IDENTICAL": len(variants) - len(differing),
            "PAGE_COUNTS": {row["variant"]: row["page_count"] for row in variants},
            "INPUT_SETS_COINCIDE": (
                inputs_a["manual_input_set_digest"]
                == inputs_b["manual_input_set_digest"]
            ),
            "BUILD_CONFIGURATIONS_COINCIDE": (
                inputs_a["build_configuration_digest"]
                == inputs_b["build_configuration_digest"]
            ),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Reproductibilité des candidats — 1SPE",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"Statut : `{payload['status']}`.",
        "",
        f"> {payload['why_this_is_not_release_evidence']}",
        "",
        f"> {payload['this_is_weaker_than_a_final_clean_room_pair']}",
        "",
        f"Condensat des entrées A : `{payload['inputs_a']['manual_input_set_digest']}`",
        f"Condensat des entrées B : `{payload['inputs_b']['manual_input_set_digest']}`",
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
        "## Comparaison",
        "",
        "| Variante | Pages | SHA source A | SHA source B | PDF A | PDF B | A == B |",
        "|---|---:|---|---|---|---|---|",
    ]
    for row in payload["variants"]:
        lines.append(
            f"| {row['variant']} | {row['page_count']} | "
            f"`{row['source_sha_a'][:10]}` | `{row['source_sha_b'][:10]}` | "
            f"`{row['pdf_sha256_a'][7:19]}` | `{row['pdf_sha256_b'][7:19]}` | "
            f"{'oui' if row['identical'] else '**NON**'} |"
        )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs", type=Path, required=True, help="JSON des runs A")
    parser.add_argument("--check", action="store_true", help="ne rien écrire")
    arguments = parser.parse_args(argv)

    try:
        runs = json.loads(arguments.runs.read_text(encoding="utf-8"))
        payload = build_evidence(runs)
    except (ReproducibilityError, OSError, json.JSONDecodeError) as error:
        print(f"1SPE-CANDIDATE-REPRODUCIBILITY-ERROR: {error}", file=sys.stderr)
        return 2

    if not arguments.check:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"écrit {JSON_TARGET.name} et {MD_TARGET.name}")
    for name, value in payload["summary"].items():
        print(f"{name}={value}")
    return 1 if payload["summary"]["VARIANTS_DIFFERING"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
