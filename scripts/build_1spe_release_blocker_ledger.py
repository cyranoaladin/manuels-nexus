#!/usr/bin/env python3
"""Registre des bloqueurs de la release 1SPE : ce qui empêche d'imprimer.

Le registre ne contient que ce qui peut affecter le manuel 1SPE — son contenu
sémantique, sa preuve machine, sa revue humaine, sa fabrication, son rendu, ou
son artefact d'impression. La dette isolée d'un autre manuel n'y entre pas :
elle est nommée `OTHER_MANUAL_SCOPE_DEBT`, elle reste réelle, et elle ne bloque
pas une release limitée au 1SPE. Un artefact partagé, lui, y entre : le critère
est l'usage, jamais le répertoire.

Deux moitiés, et aucune n'est déclarative seule :

* les bloqueurs **dérivés** sont lus dans les métriques bloquantes des
  producteurs. Un producteur qui repasse à zéro fait disparaître son bloqueur,
  sans intervention ;
* les bloqueurs **constatés** sont décrits dans le docket
  `audit/1SPE_RELEASE_BLOCKER_DOCKET.json`, et chacun porte une VÉRIFICATION
  exécutable. Un constat qui ne se reproduit plus est marqué `RESOLVED` et
  sort du décompte ; un constat dont la vérification ne peut pas s'exécuter
  devient `UNVERIFIABLE`, ce qui est bloquant en soi.

Métriques : `OPEN_BLOCKERS`, `UNVERIFIABLE`, `HUMAN_DECISION_PENDING`,
`OTHER_MANUAL_SCOPE_DEBT`.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_source_surface import ROOT, relative  # noqa: E402

JSON_TARGET = ROOT / "audit/1SPE_RELEASE_BLOCKER_LEDGER.json"
MD_TARGET = ROOT / "audit/1SPE_RELEASE_BLOCKER_LEDGER.md"
DOCKET = ROOT / "audit/1SPE_RELEASE_BLOCKER_DOCKET.json"
GENERATED_BY = "scripts/build_1spe_release_blocker_ledger.py"

BUILD = ROOT / "Mathematiques/manuel-maths/build/MANUEL_1SPE"
VARIANTS = ("eleve", "professeur")

# Chaque entrée : artefact producteur, métrique bloquante, identifiant du
# bloqueur, portée, et ce que la valeur signifie.
DERIVED_SOURCES: tuple[dict[str, Any], ...] = (
    {
        # Cette metrique se lisait sur `..._ORPHAN_PAGE_AFTER` de la
        # ratification, qui mesure la construction RATIFIEE -- un etat
        # historique, fige, et desormais superseded. Un bloqueur vivant doit
        # etre juge sur la construction courante : c'est ce que mesure
        # 1SPE_CHAPTER_OPENER_SPAN, sur les PDF que l'assembleur vient de
        # produire.
        "artifact": "audit/1SPE_CHAPTER_OPENER_SPAN.json",
        "metric": "MULTI_PAGE_OPENERS",
        "blocker_id": "CHAPTER_OPENER_ORPHAN_PAGE",
        "scope": "1SPE_RELEASE_BLOCKER",
        "surface": "1SPE_PRINT_ARTIFACT",
        "meaning": (
            "une ouverture de chapitre deborde sur une page qui ne porte que "
            "« Temps estimes » ; \\vfill avale le debordement, le journal LaTeX "
            "reste muet, le defaut ne se voit que sur la page rendue"
        ),
        "closes_with": "MACHINE",
    },
    {
        "artifact": "audit/1SPE_PAGINATION_BASELINE_RATIFICATION.json",
        "metric": "UNINTENTIONAL_BLANK_PAGE",
        "blocker_id": "UNINTENTIONAL_BLANK_PAGE",
        "scope": "1SPE_RELEASE_BLOCKER",
        "surface": "1SPE_PRINT_ARTIFACT",
        "meaning": "une page blanche sans raison documentee",
        "closes_with": "MACHINE",
    },
    {
        "artifact": "audit/1SPE_PAGINATION_BASELINE_RATIFICATION.json",
        "metric": "CHAPTER_OPENING_FALSE_FOLIO_AFTER",
        "blocker_id": "CHAPTER_OPENING_FALSE_FOLIO",
        "scope": "1SPE_RELEASE_BLOCKER",
        "surface": "1SPE_PRINT_ARTIFACT",
        "meaning": "le sommaire annonce une page qui n'est pas l'ouverture",
        "closes_with": "MACHINE",
    },
    {
        "artifact": "audit/1SPE_ASSESSMENT_BAREME_TRANSCRIPTION.json",
        "metric": "ATTENTION_REQUIRED",
        "blocker_id": "ASSESSMENT_BAREME_HUMAN_DECISION",
        "scope": "HUMAN_DECISION_PENDING",
        "surface": "1SPE_HUMAN_REVIEW",
        "meaning": (
            "un sujet ne value pas ses questions : repartir son total est un "
            "jugement pedagogique, et le dossier est prepare, pas tranche"
        ),
        "closes_with": "EXPERT_PROGRAMME_PEDAGOGIE",
    },
    {
        "artifact": "audit/1SPE_ASSESSMENT_BAREME_TRANSCRIPTION.json",
        "metric": "CARRIER_CONTRADICTS_SUBJECT",
        "blocker_id": "BAREME_CONTRADICTS_ITS_SUBJECT",
        "scope": "1SPE_RELEASE_BLOCKER",
        "surface": "1SPE_SEMANTIC_CONTENT",
        "meaning": "un bareme professeur note une tache autrement que son sujet",
        "closes_with": "MACHINE",
    },
    {
        "artifact": "audit/1SPE_TEACHER_COMPLETENESS_METRICS.json",
        "metric": "TEACHER_MISSING_REQUIRED_CONTENT",
        "blocker_id": "TEACHER_MISSING_REQUIRED_CONTENT",
        "scope": "1SPE_RELEASE_BLOCKER",
        "surface": "1SPE_SEMANTIC_CONTENT",
        "meaning": "un objet note du manuel professeur n'a pas son bareme",
        "closes_with": "EXPERT_PROGRAMME_PEDAGOGIE",
    },
    {
        "artifact": "audit/1SPE_TEACHER_COMPLETENESS_METRICS.json",
        "metric": "STUDENT_TEACHER_ONLY_LEAKS",
        "blocker_id": "STUDENT_TEACHER_ONLY_LEAK",
        "scope": "1SPE_RELEASE_BLOCKER",
        "surface": "1SPE_SEMANTIC_CONTENT",
        "meaning": "un corrige, un bareme ou une cle a fuite vers la variante eleve",
        "closes_with": "MACHINE",
    },
    {
        "artifact": "audit/1SPE_RELEASE_TEST_GATE.json",
        "metric": "FAILURES_TOUCHING_1SPE",
        "blocker_id": "RELEASE_TEST_GATE_RED",
        "scope": "1SPE_RELEASE_BLOCKER",
        "surface": "1SPE_MACHINE_PROOF",
        "meaning": "un test du perimetre de release 1SPE echoue",
        "closes_with": "MACHINE",
    },
)


class LedgerError(RuntimeError):
    """Une preuve manque : le registre ne peut pas etre etabli."""


def _reject(message: str) -> None:
    raise LedgerError(message)


def head_sha() -> str:
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.strip()


def load_json(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


# ---------------------------------------------------------------------------
#  Vérifications exécutables des constats
# ---------------------------------------------------------------------------


def _check_margin_compositor_renders_nothing() -> dict[str, Any]:
    """Le compositeur capture des notes, et n'en dessine aucune.

    Le compte des captures est lu dans le journal du moteur ; le compte des
    notes rendues est lu dans le PDF, par le `/NXMarginID` que chaque Form
    marginal porte. Un ecart signifie que la note existe et ne s'imprime pas.
    """

    try:
        import pikepdf
    except ModuleNotFoundError:  # pragma: no cover - dependance de gate
        return {"verifiable": False, "reason": "pikepdf indisponible"}
    evidence = {}
    for variant in VARIANTS:
        log = BUILD / f"MANUEL_1SPE_{variant}.log"
        pdf = BUILD / f"MANUEL_1SPE_{variant}.pdf"
        if not log.is_file() or not pdf.is_file():
            return {"verifiable": False, "reason": f"build absent pour {variant}"}
        captured = log.read_text(encoding="utf-8", errors="replace").count(
            "NEXUS-MARGIN-CAPTURE:"
        )
        rendered = 0
        with pikepdf.Pdf.open(pdf) as document:
            for page in document.pages:
                resources = page.obj.get("/Resources", {})
                xobjects = resources.get("/XObject", {}) if resources else {}
                for name in xobjects or {}:
                    if "/NXMarginID" in xobjects[name]:
                        rendered += 1
        evidence[variant] = {"captured": captured, "rendered": rendered}
    still_true = all(
        row["captured"] > 0 and row["rendered"] == 0 for row in evidence.values()
    )
    return {"verifiable": True, "still_true": still_true, "evidence": evidence}


def _check_d7_bundle_targets_the_specimen() -> dict[str, Any]:
    """Existe-t-il un dossier D7 du MANUEL, et est-il complet ?

    Le constat porte sur l'absence d'un dossier pris dans le manuel, pas sur
    l'existence de celui de la maquette : les deux peuvent coexister.
    """

    specimen = ROOT / "scripts/build_d7_proof_bundle.py"
    specimen_text = specimen.read_text(encoding="utf-8") if specimen.is_file() else ""
    manual = load_json(ROOT / "audit/1SPE_D7_PROOF_BUNDLE.json")
    summary = (manual or {}).get("summary", {})
    complete = bool(manual) and (
        summary.get("PAGES_SELECTED") == summary.get("PAGES_REQUIRED")
        and summary.get("MISSING_CATEGORIES") == 0
        and summary.get("CATEGORIES_FOUND") == summary.get("CATEGORIES_REQUIRED")
    )
    return {
        "verifiable": True,
        "still_true": not complete,
        "evidence": {
            "specimen_bundle_targets_the_maquette": "maquette" in specimen_text
            and "MANUEL_1SPE" not in specimen_text,
            "manual_bundle_exists": bool(manual),
            "manual_bundle_summary": summary,
        },
    }


def _check_receipt_is_stale() -> dict[str, Any]:
    """Le recu de candidate d'impression decrit un autre etat que HEAD."""

    receipt = load_json(ROOT / "audit/1SPE_PRINT_CANDIDATE_BUILD_RECEIPT.json")
    if receipt is None:
        return {"verifiable": False, "reason": "recu absent"}
    declared = receipt.get("source_sha")
    current = head_sha()
    counts = {}
    variants = receipt.get("variants")
    if isinstance(variants, dict):
        for name, row in variants.items():
            counts[name] = row.get("page_count") if isinstance(row, dict) else row
    elif isinstance(variants, list):
        for row in variants:
            if isinstance(row, dict):
                counts[row.get("variant")] = row.get("page_count")
    # Le recu ne PEUT pas etre rafraichi par la machine seule, et il faut dire
    # pourquoi plutot que de laisser croire a un oubli. `--record-observed`
    # derive son recu du manifeste de build ; celui-ci atteste encore les deux
    # constructions de 363 et 635 pages, que la decision humaine du 3 septembre
    # declare superseded. Ecarter une attestation deja portee au manifeste
    # demande, par construction de `build_manifest.py`, une justification et un
    # approbateur HUMAINS -- et le nom d'un approbateur ne s'invente pas.
    manifest = load_json(ROOT / "audit/BUILD_MANIFEST.json") or {}
    recorded = manifest.get("builds")
    attested = (
        [
            f"{row.get('manual')}/{row.get('variant')} : {row.get('page_count')} pages"
            for row in recorded
            if isinstance(row, dict)
        ]
        if isinstance(recorded, list)
        else []
    )
    return {
        "verifiable": True,
        "still_true": declared != current,
        "evidence": {
            "receipt_source_sha": declared,
            "head": current,
            "receipt_page_counts": counts,
            "why_the_machine_cannot_close_it": (
                "Le manifeste de build atteste encore des constructions que la "
                "décision humaine du 2026-09-03 déclare superseded, et son "
                "source_digest ne décrit plus les sources courantes. "
                "`build_manifest.py --invalidate-stale` exige une justification "
                "et un approbateur humains, refuse en CI et exige un dépôt "
                "propre : c'est une décision, pas un calcul."
            ),
            "still_attested_builds": attested,
            "the_gesture_that_unblocks_it": (
                "python3 scripts/build_manifest.py --invalidate-stale "
                "--reason '<pourquoi>' --approved-by '<nom>' "
                "puis python3 Mathematiques/manuel-maths/scripts/"
                "assemble_manuel.py --manual 1SPE --variant <variante> "
                "--record-observed"
            ),
            "closes_with": "REAL_HUMAN_DECISION_REQUIRED",
        },
    }


def _check_bareme_commentary_absent() -> dict[str, Any]:
    """La couche « corrige-bareme commente » n'existe nulle part.

    Le contrat pedagogique la demande : pour chaque question, ce qui rapporte
    les points, les erreurs penalisees, les points de redaction. Aucun corrige
    d'evaluation ne la porte aujourd'hui, et elle ne se derive pas d'un sujet.
    """

    corrections = sorted(
        (ROOT / "Mathematiques/manuel-maths/chapitres").glob(
            "1SPE-*/evaluations/*-corrige.tex"
        )
    )
    if not corrections:
        return {"verifiable": False, "reason": "aucun corrige d'evaluation trouve"}
    marker = re.compile(r"erreurs? p[ée]nalis|points? de r[ée]daction", re.IGNORECASE)
    carrying = [
        relative(path)
        for path in corrections
        if marker.search(path.read_text(encoding="utf-8"))
    ]
    # La couche reste absente tant qu'un enseignant ne l'a pas ecrite : elle ne
    # se derive de rien. Ce qui PEUT etre fait l'est, et se lit ici : la demande
    # est preparee, question par question, enonce et reponse en face.
    request = load_json(ROOT / "audit/1SPE_BAREME_COMMENTARY_REQUEST.json")
    prepared = request["summary"] if request else {}
    return {
        "verifiable": True,
        "still_true": not carrying,
        "evidence": {
            "assessment_corrections": len(corrections),
            "carrying_commentary": len(carrying),
            "request_prepared_for": prepared.get("ASSESSMENTS_AWAITING_COMMENTARY"),
            "questions_awaiting_a_teacher": prepared.get(
                "QUESTIONS_AWAITING_COMMENTARY"
            ),
            "questions_without_a_prepared_request": prepared.get(
                "QUESTIONS_WITHOUT_A_PREPARED_REQUEST"
            ),
            "where": "audit/1SPE_BAREME_COMMENTARY_REQUEST/",
        },
    }


def _check_refresh_script_corrupts_artifacts() -> dict[str, Any]:
    """Le rafraichisseur ecrit une chaine la ou le schema veut un entier.

    On lit les deux faits : ce que le script assigne, et ce que les artefacts
    declarent aujourd'hui. Le constat reste vrai tant que les deux divergent.
    """

    script = ROOT / "scripts/refresh_audit_reports.py"
    if not script.is_file():
        return {"verifiable": False, "reason": "script absent"}
    source = script.read_text(encoding="utf-8")
    assigns_string = '"schema_version"] = "2.0.0"' in source
    has_argument_parser = "argparse" in source
    integers = {}
    for name in ("audit/BUILD_MANIFEST.json", "audit/CHAPTER_READINESS.json"):
        payload = load_json(ROOT / name)
        integers[name] = isinstance(
            (payload or {}).get("schema_version"), int
        )
    return {
        "verifiable": True,
        "still_true": assigns_string and any(integers.values()),
        "evidence": {
            "script_assigns_string_schema_version": assigns_string,
            "script_has_argument_parser": has_argument_parser,
            "artifacts_declare_integer_schema_version": integers,
        },
    }


# Les chapitres du manuel 1SPE, lus la ou ils vivent : un repertoire par
# chapitre, et c'est ce que l'assembleur collecte.
def _manual_chapters() -> list[str]:
    base = ROOT / "Mathematiques/manuel-maths/chapitres"
    return sorted(
        path.name for path in base.glob("1SPE-*") if (path / "contrat.yaml").is_file()
    )


REVIEW_ROLES = ("EXPERT_MATHEMATIQUE", "EXPERT_PROGRAMME_PEDAGOGIE")


def _check_chapter_review_packets_incomplete() -> dict[str, Any]:
    """Deux revues de role par chapitre : les dossiers existent-ils seulement ?

    Un verdict manquant est une attente. Un DOSSIER manquant est un blocage :
    le reviewer ne peut meme pas commencer.

    Ce controle cherchait les paquets sous `audit/*NEUTRAL_REVIEW_PACKET.json`
    et n'en trouvait aucun, parce que le producteur les ecrit ailleurs --
    `audit/reviews/human/<chapitre>/packet-<role>.json`. Il annoncait donc
    vingt dossiers manquants alors que les vingt existaient. L'autorite est
    desormais le producteur qui les compte, et une seule.
    """

    payload = load_json(ROOT / "audit/1SPE_HUMAN_PACKET_COMPLETENESS.json")
    if payload is None:
        return {
            "verifiable": False,
            "reason": "audit/1SPE_HUMAN_PACKET_COMPLETENESS.json absent",
        }
    summary = payload["summary"]
    missing = (
        summary["HUMAN_PACKETS_MISSING"]
        or summary["HUMAN_READING_VIEWS_MISSING"]
        or summary["PACKETS_WITHOUT_REQUIRED_FIELDS"]
    )
    return {
        "verifiable": True,
        "still_true": bool(missing),
        "evidence": {
            "expected": summary["HUMAN_PACKETS_EXPECTED"],
            "packets_present": summary["HUMAN_PACKETS_PRESENT"],
            "packets_missing": summary["HUMAN_PACKETS_MISSING"],
            "reading_views_missing": summary["HUMAN_READING_VIEWS_MISSING"],
            "packets_without_required_fields": summary[
                "PACKETS_WITHOUT_REQUIRED_FIELDS"
            ],
            "the_human_verdicts_themselves_remain_pending": True,
        },
    }


def _check_latex_warning_classes() -> dict[str, Any]:
    """Chaque ligne d'avertissement des journaux est-elle nommee et fermee ?

    Le docket declarait les classes et leur disposition, et ce controle
    confrontait ces declarations aux journaux. La declaration figeait un etat :
    trois classes y restaient « ouvertes » alors que les journaux courants ne
    portent plus aucune alerte. L'autorite est desormais la lecture VIVANTE et
    exhaustive des deux journaux produits.
    """

    payload = load_json(ROOT / "audit/1SPE_LATEX_LOG_WARNING_GATE.json")
    if payload is None:
        return {
            "verifiable": False,
            "reason": "audit/1SPE_LATEX_LOG_WARNING_GATE.json absent",
        }
    summary = payload["summary"]
    return {
        "verifiable": True,
        "still_true": bool(
            summary["LATEX_WARNINGS"] or summary["UNCLASSIFIED_WARNING_LINES"]
        ),
        "evidence": {
            "warnings": summary["LATEX_WARNINGS"],
            "unclassified": summary["UNCLASSIFIED_WARNING_LINES"],
            "declared_families": summary["DECLARED_FAMILIES"],
            "per_family": {
                name: detail["occurrences"]
                for name, detail in payload["families"].items()
            },
        },
    }


CHECKS: dict[str, Callable[[], dict[str, Any]]] = {
    "LATEX_WARNING_CLASSES_UNCLOSED": _check_latex_warning_classes,
    "CHAPTER_REVIEW_PACKETS_INCOMPLETE": _check_chapter_review_packets_incomplete,
    "REFRESH_AUDIT_REPORTS_CORRUPTS_TWO_ARTIFACTS": (
        _check_refresh_script_corrupts_artifacts
    ),
    "MARGIN_COMPOSITOR_RENDERS_NOTHING": _check_margin_compositor_renders_nothing,
    "D7_BUNDLE_TARGETS_THE_SPECIMEN_NOT_THE_MANUAL": _check_d7_bundle_targets_the_specimen,
    "PRINT_CANDIDATE_RECEIPT_STALE": _check_receipt_is_stale,
    "ASSESSMENT_BAREME_COMMENTARY_ABSENT": _check_bareme_commentary_absent,
}


# ---------------------------------------------------------------------------


def derived_blockers() -> list[dict[str, Any]]:
    rows = []
    for entry in DERIVED_SOURCES:
        payload = load_json(ROOT / entry["artifact"])
        if payload is None:
            rows.append(
                {
                    **entry,
                    "state": "UNVERIFIABLE",
                    "observed": None,
                    "reason": "artefact producteur absent ou illisible",
                }
            )
            continue
        summary = payload.get("summary", {})
        if entry["metric"] not in summary:
            rows.append(
                {
                    **entry,
                    "state": "UNVERIFIABLE",
                    "observed": None,
                    "reason": f"metrique {entry['metric']} absente de l'artefact",
                }
            )
            continue
        observed = summary[entry["metric"]]
        numeric = observed if isinstance(observed, int) else int(bool(observed))
        rows.append(
            {
                **entry,
                "state": "OPEN" if numeric else "CLOSED",
                "observed": observed,
                "evidence_path": entry["artifact"],
            }
        )
    return rows


def observed_blockers(docket: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for entry in docket.get("observed_findings", []) or []:
        check = CHECKS.get(entry["blocker_id"])
        if check is None:
            rows.append(
                {**entry, "state": "UNVERIFIABLE", "reason": "aucune verification"}
            )
            continue
        result = check()
        if not result.get("verifiable"):
            rows.append({**entry, "state": "UNVERIFIABLE", **result})
            continue
        rows.append(
            {
                **entry,
                "state": "OPEN" if result["still_true"] else "RESOLVED",
                "evidence": result.get("evidence"),
            }
        )
    return rows


def build() -> dict[str, Any]:
    docket = load_json(DOCKET)
    if docket is None:
        _reject(f"docket absent : {relative(DOCKET)}")
    rows = derived_blockers() + observed_blockers(docket)
    open_rows = [row for row in rows if row["state"] == "OPEN"]
    unverifiable = [row for row in rows if row["state"] == "UNVERIFIABLE"]
    human = [
        row
        for row in open_rows
        if row.get("scope") == "HUMAN_DECISION_PENDING"
        or row.get("closes_with", "").startswith("EXPERT")
        or row.get("closes_with") == "REAL_HUMAN_DECISION_REQUIRED"
    ]
    other_manual = [
        row for row in rows if row.get("scope") == "OTHER_MANUAL_SCOPE_DEBT"
    ]
    return {
        "artifact_type": "1spe_release_blocker_ledger",
        "schema_version": 1,
        "generated_by": GENERATED_BY,
        "source_sha": head_sha(),
        "scope_rule": (
            "n'entre au registre que ce qui peut affecter le contenu semantique, "
            "la preuve machine, la revue humaine, la fabrication, le rendu ou "
            "l'artefact d'impression du 1SPE ; le critere est l'usage, jamais le "
            "repertoire"
        ),
        "approves_nothing": True,
        "blockers": rows,
        "summary": {
            "TRACKED": len(rows),
            "OPEN_BLOCKERS": len(open_rows),
            "CLOSED": sum(1 for row in rows if row["state"] == "CLOSED"),
            "RESOLVED": sum(1 for row in rows if row["state"] == "RESOLVED"),
            "UNVERIFIABLE": len(unverifiable),
            "HUMAN_DECISION_PENDING": len(human),
            "OTHER_MANUAL_SCOPE_DEBT": len(other_manual),
            "OPEN_BLOCKER_IDS": sorted(row["blocker_id"] for row in open_rows),
        },
    }


def render_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Registre des bloqueurs de la release 1SPE",
        "",
        f"<!-- generated by {GENERATED_BY} -->",
        "",
        f"SHA : `{payload['source_sha']}`",
        "",
        "> " + payload["scope_rule"],
        "",
        "## Métriques",
        "",
        "| Métrique | Valeur |",
        "|---|---|",
    ]
    for name, value in payload["summary"].items():
        rendered = ", ".join(value) if isinstance(value, list) else value
        lines.append(f"| `{name}` | {rendered if rendered != [] else '—'} |")
    lines += [
        "",
        "## Bloqueurs",
        "",
        "| État | Identifiant | Portée | Surface | Ferme par | Observé |",
        "|---|---|---|---|---|---|",
    ]
    for row in payload["blockers"]:
        observed = row.get("observed")
        if observed is None:
            evidence = row.get("evidence")
            observed = json.dumps(evidence, ensure_ascii=False) if evidence else "—"
        lines.append(
            f"| **{row['state']}** | `{row['blocker_id']}` | {row.get('scope','—')} | "
            f"{row.get('surface','—')} | {row.get('closes_with','—')} | "
            f"{str(observed)[:80]} |"
        )
    lines += ["", "## Détail", ""]
    for row in payload["blockers"]:
        lines += [
            f"### `{row['blocker_id']}` — {row['state']}",
            "",
            f"- portée : `{row.get('scope', '—')}`",
            f"- surface : `{row.get('surface', '—')}`",
            f"- ferme par : `{row.get('closes_with', '—')}`",
            f"- signification : {row.get('meaning', '—')}",
        ]
        if row.get("evidence_path"):
            lines.append(f"- preuve : `{row['evidence_path']}`")
        if row.get("evidence"):
            lines.append(
                f"- mesure : `{json.dumps(row['evidence'], ensure_ascii=False)}`"
            )
        if row.get("reason"):
            lines.append(f"- motif : {row['reason']}")
        lines.append("")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="ne rien écrire")
    arguments = parser.parse_args(argv)

    try:
        payload = build()
    except LedgerError as error:
        print(f"1SPE-RELEASE-BLOCKER-LEDGER-ERROR: {error}", file=sys.stderr)
        return 2

    if not arguments.check:
        JSON_TARGET.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        MD_TARGET.write_text(render_markdown(payload), encoding="utf-8")
        print(f"écrit {relative(JSON_TARGET)} et {relative(MD_TARGET)}")
    for name, value in payload["summary"].items():
        print(f"{name}={value}")
    return 1 if payload["summary"]["UNVERIFIABLE"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
