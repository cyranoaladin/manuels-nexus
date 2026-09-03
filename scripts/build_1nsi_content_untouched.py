#!/usr/bin/env python3
"""Le contenu 1NSI n'a pas bougé — et « contenu » est dit, pas supposé.

La campagne 1SPE avait une consigne permanente : ne toucher à aucun contenu
1NSI. Quinze échecs de tests 1NSI ont pourtant été refermés, par réobservation
seule. Ce module le prouve.

Le point de comparaison n'est pas choisi ici : c'est le commit que le dépôt a
lui-même enregistré comme la CAUSE de ces quinze échecs -- celui qui a retiré
44 cours 1NSI -- et qui est donc, par construction, la dernière mutation
légitime du contenu 1NSI. Il est lu dans
`audit/1NSI_PENDING_STATE_REOBSERVATION.json`, jamais recopié.

Ce qu'est le CONTENU, ici : les fichiers que l'assembleur 1NSI publie
réellement, plus les contrats et données pédagogiques du chapitre. Ce qu'il
n'est PAS : les gabarits typographiques, partagés avec les mathématiques et
maintenus identiques dans les trois copies ; les tests ; les artefacts
d'audit. Une charte modifiée change la MISE EN PAGE de la NSI, pas son
contenu, et le dire autrement serait aussi faux dans un sens que dans l'autre.

Les deux comptes sont donc publiés séparément et sans hiérarchie :
`CONTENT_FILES_CHANGED`, qui doit valoir zéro, et `SHARED_TEMPLATE_FILES_CHANGED`,
qui n'est pas bloquant mais doit rester lisible -- avec la liste.

Métrique bloquante : `CONTENT_FILES_CHANGED`.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import ROOT  # noqa: E402

JSON_TARGET = ROOT / "audit/1NSI_CONTENT_UNTOUCHED.json"
MD_TARGET = ROOT / "audit/1NSI_CONTENT_UNTOUCHED.md"
GENERATED_BY = "scripts/build_1nsi_content_untouched.py"

REOBSERVATION = ROOT / "audit/1NSI_PENDING_STATE_REOBSERVATION.json"

# Le contenu pédagogique de la NSI : ce que le manuel dit, et les données dont
# il le tire.
CONTENT_PREFIXES = (
    "NSI/chapitres/",
    "NSI/corpus/",
    "NSI/corpus_nsi/",
    "NSI/referentiel/",
    "NSI/db/",
    "NSI/sources/",
)
# La typographie, partagée et maintenue identique dans les trois copies : elle
# change la mise en page de la NSI, jamais son propos.
SHARED_TEMPLATE_PREFIXES = ("NSI/gabarits/",)


class ContentError(RuntimeError):
    """Une preuve manque : la comparaison ne peut pas être faite."""


def _git(*arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise ContentError(f"git {' '.join(arguments)} : {result.stderr.strip()}")
    return result.stdout


def cause_commit() -> dict[str, Any]:
    """La dernière mutation légitime du contenu 1NSI, telle que le dépôt la nomme."""

    if not REOBSERVATION.is_file():
        raise ContentError(f"registre de réobservation absent : {REOBSERVATION}")
    payload = json.loads(REOBSERVATION.read_text(encoding="utf-8"))
    cause = payload.get("cause") or {}
    sha = cause.get("sha")
    if not sha:
        raise ContentError("le registre de réobservation ne nomme aucune cause")
    # Le commit doit exister ici, sinon la comparaison ne prouverait rien.
    _git("cat-file", "-e", f"{sha}^{{commit}}")
    return cause


def changed_paths(base: str) -> list[str]:
    """Tout ce qui diffère du point de départ, y compris le travail non commis."""

    committed = _git("diff", "--name-only", base, "HEAD").split()
    working = _git("diff", "--name-only", "HEAD").split()
    untracked = _git("ls-files", "--others", "--exclude-standard").split()
    return sorted(set(committed) | set(working) | set(untracked))


MATHS_TEMPLATES = ROOT / "Mathematiques/manuel-maths/gabarits"
COMMON_TEMPLATES = ROOT / "gabarits/common"


def _label(path: Path) -> str:
    """Chemin lisible, y compris pour un double fabriqué hors du dépôt."""

    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def diverging_copies(paths: list[str]) -> list[dict[str, str]]:
    """Les copies qui ne sont plus des copies.

    La règle n'est pas inventée ici : `tests/test_canonical_resolution_chain.py`
    la porte déjà. Un adaptateur de discipline doit être identique entre les
    mathématiques et la NSI ; un module réellement recopié depuis
    `gabarits/common` doit en outre lui être identique. Le premier est un
    aiguillage, le second un double -- les confondre ferait crier à la
    divergence sur une redirection parfaitement saine.
    """

    divergent: list[dict[str, str]] = []
    for path in paths:
        name = Path(path).name
        nsi = ROOT / path
        maths = MATHS_TEMPLATES / name
        common = COMMON_TEMPLATES / name
        if not nsi.is_file():
            continue
        if maths.is_file() and maths.read_bytes() != nsi.read_bytes():
            divergent.append({"file": path, "differs_from": _label(maths)})
            continue
        is_wrapper = maths.is_file() and "gabarits/common/" in nsi.read_text(
            encoding="utf-8", errors="replace"
        )
        if not is_wrapper and common.is_file():
            if common.read_bytes() != nsi.read_bytes():
                divergent.append(
                    {"file": path, "differs_from": _label(common)}
                )
    return divergent


def classify(path: str) -> str | None:
    if path.startswith(SHARED_TEMPLATE_PREFIXES):
        return "SHARED_TEMPLATE"
    if path.startswith(CONTENT_PREFIXES):
        return "CONTENT"
    if path.startswith("NSI/"):
        return "TOOLING_OR_AUDIT"
    return None


def build() -> dict[str, Any]:
    cause = cause_commit()
    base = cause["sha"]
    buckets: dict[str, list[str]] = {
        "CONTENT": [],
        "SHARED_TEMPLATE": [],
        "TOOLING_OR_AUDIT": [],
    }
    for path in changed_paths(base):
        bucket = classify(path)
        if bucket is not None:
            buckets[bucket].append(path)

    divergent = diverging_copies(buckets["SHARED_TEMPLATE"])

    return {
        "artifact_type": "1nsi_content_untouched",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "what_content_means": (
            "Ce que l'assembleur 1NSI publie et les données pédagogiques dont "
            "il le tire. Pas les gabarits typographiques, partagés avec les "
            "mathématiques ; pas les tests ; pas les artefacts d'audit."
        ),
        "a_template_change_is_not_a_content_change": (
            "Une charte modifiée change la mise en page de la NSI, pas son "
            "propos. Les deux comptes sont publiés séparément."
        ),
        "baseline_is_read_not_chosen": (
            "audit/1NSI_PENDING_STATE_REOBSERVATION.json"
        ),
        "baseline": cause,
        "content_prefixes": list(CONTENT_PREFIXES),
        "shared_template_prefixes": list(SHARED_TEMPLATE_PREFIXES),
        "changed": buckets,
        "a_wrapper_is_not_a_copy": (
            "Un adaptateur de discipline redirige vers gabarits/common ; il "
            "doit être identique entre mathématiques et NSI, pas au module "
            "commun. Règle portée par tests/test_canonical_resolution_chain.py."
        ),
        "shared_template_copies_diverging": divergent,
        "summary": {
            "1NSI_CONTENT_CHANGED": "YES" if buckets["CONTENT"] else "NO",
            "CONTENT_FILES_CHANGED": len(buckets["CONTENT"]),
            "SHARED_TEMPLATE_FILES_CHANGED": len(buckets["SHARED_TEMPLATE"]),
            "SHARED_TEMPLATE_COPIES_DIVERGING": len(divergent),
            "TOOLING_OR_AUDIT_FILES_CHANGED": len(buckets["TOOLING_OR_AUDIT"]),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Contenu 1NSI — inchangé",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"> {payload['what_content_means']}",
        "",
        f"> {payload['a_template_change_is_not_a_content_change']}",
        "",
        f"Point de comparaison : `{payload['baseline']['sha'][:12]}` — "
        f"{payload['baseline']['subject']} ({payload['baseline']['date']}), "
        f"lu dans `{payload['baseline_is_read_not_chosen']}`.",
        "",
        "## Métriques",
        "",
        "| Métrique | Valeur |",
        "|---|---:|",
    ]
    for name, value in payload["summary"].items():
        lines.append(f"| `{name}` | {value} |")
    for bucket, paths in payload["changed"].items():
        lines += ["", f"## `{bucket}` — {len(paths)} fichier(s)", ""]
        lines += [f"- `{path}`" for path in paths] or ["_aucun_"]
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="ne rien écrire")
    arguments = parser.parse_args(argv)

    try:
        payload = build()
    except ContentError as error:
        print(f"1NSI-CONTENT-UNTOUCHED-ERROR: {error}", file=sys.stderr)
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
    for path in payload["changed"]["CONTENT"]:
        print(f"CONTENU-1NSI-MODIFIE {path}", file=sys.stderr)
    summary = payload["summary"]
    return (
        1
        if summary["CONTENT_FILES_CHANGED"]
        or summary["SHARED_TEMPLATE_COPIES_DIVERGING"]
        else 0
    )


if __name__ == "__main__":
    raise SystemExit(main())
