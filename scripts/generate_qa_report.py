#!/usr/bin/env python3
"""Generate qa_report.md from current manifest, coverage and Drive inventory."""
from __future__ import annotations

import csv
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from scripts._course_sheets_common import compute_sheet_readiness, course_sheet_links, frontmatter_capacities, planned_sequences, read_frontmatter, resource_exists, sheets_by_sequence
from scripts.check_capacity_status_ladder import analyze_capacity_status_ladder
from scripts.check_course_sheet_readiness_strict import analyze_course_sheet_readiness_strict
from scripts.check_drive_action_plan_completeness import analyze_drive_action_plan
from scripts.check_human_review_register import analyze_human_review_register
from scripts.check_human_review_wave_plan import analyze_human_review_wave_plan
from scripts.check_missing_register_actionability import load_register_rows
from scripts.check_paper_tp_justification import analyze_paper_tp_justification
from scripts.check_sequence_pedagogical_coherence import analyze_sequence_pedagogical_coherence
from scripts.check_session_classroom_operationality import analyze_session_classroom_operationality
from scripts.check_session_to_resource_alignment import analyze_session_to_resource_alignment
from scripts.check_tp_executable_opportunity import analyze_tp_executable_opportunity

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "manifest.csv"
COVERAGE = ROOT / "coverage.md"
DRIVE_INVENTORY = ROOT / "drive_inventory.csv"
REPORT = ROOT / "qa_report.md"


def count_manifest() -> tuple[int, Counter[str], Counter[str], int]:
    statuses: Counter[str] = Counter()
    sources: Counter[str] = Counter()
    publishable = 0
    total = 0
    with MANIFEST.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            total += 1
            statuses[row.get("statut", "")] += 1
            sources[row.get("source", "")] += 1
            if row.get("publishable") == "oui":
                publishable += 1
    return total, statuses, sources, publishable


def coverage_counts() -> dict[str, int]:
    counts: dict[str, int] = {}
    if not COVERAGE.exists():
        return counts
    for line in COVERAGE.read_text(encoding="utf-8").splitlines():
        if line.startswith("- ") and " : " in line:
            key, value = line[2:].split(" : ", 1)
            if value.strip().isdigit():
                counts[key.strip()] = int(value.strip())
    return counts


def drive_rows() -> int:
    if not DRIVE_INVENTORY.exists():
        return 0
    with DRIVE_INVENTORY.open(encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def drive_decision_counts() -> Counter[str]:
    counts: Counter[str] = Counter()
    if not DRIVE_INVENTORY.exists():
        return counts
    with DRIVE_INVENTORY.open(encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            counts[row.get("decision", "")] += 1
    return counts


def command_status(command: list[str]) -> tuple[int, list[str]]:
    result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    lines: list[str] = []
    for line in result.stdout.strip().splitlines():
        if line.startswith("make[") and "]: ***" in line:
            line = "make: ***" + line.split("]: ***", 1)[1]
        line = re.sub(r"Makefile:\d+: release-audit", "Makefile:release-audit", line)
        if "Entering directory" in line or "Leaving directory" in line:
            continue
        lines.append(line)
    return result.returncode, lines[-8:]


def indicative_gate_rows() -> list[tuple[str, str, str, str]]:
    rows: list[tuple[str, str, str, str]] = []
    for script in ["scripts.check_required_sections", "scripts.check_document_depth"]:
        code, tail = command_status([sys.executable, "-m", script])
        if code == 0:
            continue
        detail = "; ".join(line.removeprefix("- ").strip() for line in tail if line.strip())
        rows.append((
            script,
            detail or "échec indicatif observé",
            "Dette pédagogique connue ; reste non bloquant uniquement pour le prototype global.",
            "2026-07-15",
        ))
    return rows


def release_blocker_status() -> tuple[int, list[str]]:
    """Snapshot release blockers without depending on the transient report file.

    The real `make release-audit` still runs in the release workflow. During
    qa_report generation, running that target would make the snapshot depend on
    whether qa_report.md is already dirty, which can hide the actual Drive
    blocker behind check_git_clean.
    """
    checks = [
        "scripts.check_drive_mapping_release",
        "scripts.check_no_needs_review_for_release",
        "scripts.check_no_absent_coverage_for_release",
        "scripts.check_no_teacher_content_in_student_export",
        "scripts.check_validated_statuses",
    ]
    lines = [
        "Snapshot des bloqueurs release hors check_git_clean.",
        "Le vrai make release-audit est exécuté séparément.",
    ]
    for script in checks:
        code, tail = command_status([sys.executable, "-m", script])
        lines.append(f"python -m {script}")
        lines.extend(tail)
        if code != 0:
            return code, lines[-10:]
    return 0, lines[-10:]


def course_sheet_stats() -> dict[str, Any]:
    plans = planned_sequences(ROOT)
    by_sequence = sheets_by_sequence(ROOT)
    sheet_count = sum(len(paths) for paths in by_sequence.values())
    missing_sequences = [sequence for sequence in plans if not by_sequence.get(sequence)]
    missing_capacities: list[str] = []
    readiness: Counter[str] = Counter()
    existing_links = 0
    registered_links = 0
    for sequence, plan in plans.items():
        declared: set[str] = set()
        for sheet in by_sequence.get(sequence, []):
            declared.update(frontmatter_capacities(read_frontmatter(sheet)))
            links = course_sheet_links(sheet)
            readiness[compute_sheet_readiness(ROOT, links)] += 1
            for link in links:
                if link.is_resource and resource_exists(ROOT, link.file):
                    existing_links += 1
                elif link.is_resource:
                    registered_links += 1
        for capacity in sorted(plan.capacities):
            if capacity not in declared:
                missing_capacities.append(f"{sequence}:{capacity}")
    return {
        "expected": len(plans),
        "created": sheet_count,
        "missing_sequences": missing_sequences,
        "missing_capacities": missing_capacities,
        "readiness": readiness,
        "existing_links": existing_links,
        "registered_links": registered_links,
    }


def linked_course_sheet_rows() -> list[tuple[str, str, str, str, str]]:
    strict = analyze_course_sheet_readiness_strict(ROOT)
    register_rows, _ = load_register_rows(ROOT)
    register = {row.get("Fichier", ""): row for row in register_rows}
    rows: list[tuple[str, str, str, str, str]] = []
    for sheet, missing in sorted(strict.linked_missing.items()):
        for filename in missing:
            row = register.get(filename, {})
            rows.append(
                (
                    Path(sheet).name,
                    filename,
                    row.get("Date cible", "non renseignée"),
                    row.get("Impact pédagogique", "support absent ; fiche non opérationnelle"),
                    row.get("Décision", "créer"),
                )
            )
    return rows


def main() -> int:
    total, statuses, sources, publishable = count_manifest()
    cov = coverage_counts()
    release_code, release_tail = release_blocker_status()
    release_status = "RELEASE_AUDIT_FAIL" if release_code != 0 else "RELEASE_AUDIT_PASS"
    final_status = "NON_RELEASE_READY" if release_code != 0 else "RELEASE_READY"
    drive_counts = drive_decision_counts()
    indicative_rows = indicative_gate_rows()
    sheet_stats = course_sheet_stats()
    linked_rows = linked_course_sheet_rows()
    capacity_ladder = analyze_capacity_status_ladder(ROOT)
    capacity_counts = {
        "documented": sum(1 for row in capacity_ladder.rows.values() if row["documented"] == "oui"),
        "practiced": sum(1 for row in capacity_ladder.rows.values() if row["practiced"] == "oui"),
        "assessed": sum(1 for row in capacity_ladder.rows.values() if row["assessed"] == "oui"),
        "linked_to_session": sum(1 for row in capacity_ladder.rows.values() if row["linked_to_session"] == "oui"),
        "covered": sum(1 for row in capacity_ladder.rows.values() if row["covered"] == "oui"),
    }
    paper_tp = analyze_paper_tp_justification(ROOT)
    tp_opportunities = analyze_tp_executable_opportunity(ROOT, strict=True, max_opportunities=8)
    human_review = analyze_human_review_register(ROOT)
    human_wave = analyze_human_review_wave_plan(ROOT)
    session_alignment = analyze_session_to_resource_alignment(ROOT)
    session_classroom = analyze_session_classroom_operationality(ROOT)
    drive_plan = analyze_drive_action_plan(ROOT)
    sequence_coherence = analyze_sequence_pedagogical_coherence(ROOT)
    substance_reviews = sorted(ROOT.glob("03_progressions/supports/**/_substance_review.json"))
    audit_folder = ROOT.parent / "AUDIT"
    lines = [
        "# QA Report",
        "",
        "## Résumé",
        "",
        "- Statut global : NON PUBLIABLE",
        f"- Ressources inventoriées : {total}",
        f"- Ressources needs_review : {statuses.get('needs_review', 0)}",
        f"- Ressources publiables : {publishable}",
        f"- Source generated : {sources.get('generated', 0)}",
        f"- Source adapted_from_drive : {sources.get('adapted_from_drive', 0)}",
        f"- Source import_partiel : {sources.get('import_partiel', 0)}",
        f"- Source inspiration_drive : {sources.get('inspiration_drive', 0)}",
        f"- Source drive : {sources.get('drive', 0)}",
        f"- Lignes drive_inventory.csv : {drive_rows()}",
        f"- Couverture covered : {cov.get('covered', 0)}",
        f"- Couverture needs_review : {cov.get('needs_review', 0)}",
        f"- Couverture partial : {cov.get('partial', 0)}",
        f"- Couverture absent : {cov.get('absent', 0)}",
        "- Archive pédagogique à transmettre : dist/source_clean.tar.gz",
        "- Archive globale contenant .git : interdite comme livraison principale",
        "- L’archive principale de livraison est dist/source_clean.tar.gz. Toute archive contenant .git/ est interdite comme livraison pédagogique.",
        "- make audit : PASS prototype uniquement si exécuté après génération de ce rapport",
        "- QUALITY_GATES_PASS : qualité interne contrôlée par scripts/check_quality_gates.py.",
        "- PACKAGE_AUDIT_PASS : paquet source propre attendu via make package-audit.",
        "- EXTRACTED_SOURCE_AUDIT_PASS : audit source extrait attendu sans dépendance Git.",
        f"- RELEASE_AUDIT_STATUS : {release_status}",
        f"- FINAL_STATUS = {final_status}",
        "- Raison : Drive partiellement intégré ; publication bloquée par ressources restantes non auditées / absentes / sensibles.",
        "- Drive est partiellement intégré.",
        "- L’audit portable ne vérifie pas les fichiers bruts Drive.",
        "- L’audit local vérifie les fichiers bruts Drive lorsque le miroir Documents_DRIVE est présent.",
        "- Le dépôt reste NON_RELEASE_READY.",
        f"- Audit externe /AUDIT : {'présent comme documentation stratégique hors corpus' if audit_folder.exists() else 'absent en mode portable'}",
        "- Arbre canonique de production : 03_progressions/supports/.",
        "- Arbres premiere/sequences/ et terminale/sequences/ : pilotes de référence, pas canon de production.",
        f"- Drive integrated_adapted : {drive_counts.get('integrated_adapted', 0)}",
        f"- Drive inspiration_only : {drive_counts.get('inspiration_only', 0)}",
        f"- Drive rejected_sensitive : {drive_counts.get('rejected_sensitive', 0)}",
        f"- Drive missing_local_copy : {drive_counts.get('missing_local_copy', 0)}",
        f"- Drive deferred : {drive_counts.get('deferred', 0)}",
        f"- Drive quarantined : {drive_counts.get('quarantined', 0)}",
        f"- Plan Drive restant : {len(drive_plan.rows)}/{len(drive_plan.expected)} ressources non soldées documentées.",
        "- Décision : ne pas générer de nouvelles séquences",
        "- Lots Drive planifiés : P05 traitement_tables complet ; T01 TAD complet ; T18 Boyer-Moore complet ; P12 tri/complexité ; P13 glouton.",
        "- ZIP exploitable sans `.git` : dist/nsi-enseignement_source_clean.zip, archive séparée du livrable pédagogique de référence.",
        "",
        "## Commandes de référence",
        "",
        "```bash",
        "make audit",
        "make package-audit",
        "make --no-print-directory release-audit",
        "```",
        "",
        "## Dernier blocage release observé",
        "",
        "```text",
        *release_tail,
        "```",
        "",
        "## Bloquants restants",
        "",
        "- Drive partiellement intégré : voir `reports/drive_enrichment_report.md` et `drive_inventory.csv` pour les décisions par ressource.",
        f"- Ressources Drive absentes localement : {drive_counts.get('missing_local_copy', 0)}.",
        f"- Ressources Drive différées : {drive_counts.get('deferred', 0)}.",
        f"- Ressources Drive rejetées sensibles : {drive_counts.get('rejected_sensitive', 0)}.",
        "- Toutes les ressources restent en revue ou non publiables.",
        "- Aucune capacité n'est covered.",
        "- Documents professeurs encore en needs_review.",
        "- Revue pédagogique et scientifique humaine absente.",
        f"- Séances opérationnelles ou reliées : {session_alignment.operational_count}.",
        f"- Séances théoriques ou non reliées : {session_alignment.theoretical_count}.",
        "",
        "## Politique /AUDIT",
        "",
        f"- Dossier /AUDIT : {'présent à côté du dépôt' if audit_folder.exists() else 'absent en mode portable'}.",
        "- Usage : documentation d'audit externe et stratégique.",
        "- Exclusion : non compté comme corpus pédagogique, non compté dans `manifest.csv`, non utilisé comme preuve dans `coverage.md`.",
        "- Intégration : les prototypes repris sont adaptés dans `scripts/`, testés et versionnés.",
        "",
        "## Arbre canonique",
        "",
        "- Canon de production : `03_progressions/supports/`.",
        "- Fiches : `03_progressions/fiches_cours/`.",
        "- Pilotes de référence : `premiere/sequences/` et `terminale/sequences/`.",
        "- Politique : `content_tree_policy.md`.",
        "",
        "## Fiches de cours",
        "",
        "- Les fiches de cours sont des ressources d’aide et de révision. Elles ne prouvent aucune couverture publiable.",
        "- Une capacité ne peut être covered que si existent et sont relus : cours ou fiche, séance, TD ou TP, corrigé, évaluation, barème, remédiation, revue pédagogique humaine et revue scientifique humaine.",
        f"- Fiches attendues : {sheet_stats['expected']} séquences avec au moins une fiche.",
        f"- Fiches créées : {sheet_stats['created']}",
        "- Séquences sans fiche : "
        + (", ".join(sheet_stats["missing_sequences"]) if sheet_stats["missing_sequences"] else "0"),
        "- Capacités sans fiche : "
        + (", ".join(sheet_stats["missing_capacities"]) if sheet_stats["missing_capacities"] else "0"),
        f"- Fiches théoriques : {sheet_stats['readiness'].get('theoretical', 0)}",
        f"- Fiches liées : {sheet_stats['readiness'].get('linked', 0)}",
        f"- Fiches opérationnelles : {sheet_stats['readiness'].get('operational', 0)}",
        f"- Liens vers supports existants : {sheet_stats['existing_links']}",
        f"- Liens vers supports inscrits au registre : {sheet_stats['registered_links']}",
        "- Statut : needs_review",
        "- Effet couverture : aucun ; les fiches ne rendent aucune capacité covered.",
        "",
        "## Couverture programme réconciliée",
        "",
        "- `coverage.md` indexe désormais les preuves issues de `03_progressions/supports/**`.",
        "- `coverage_sources.md` liste les fichiers sources par capacité.",
        f"- Couverture covered : {cov.get('covered', 0)}",
        f"- Couverture needs_review : {cov.get('needs_review', 0)}",
        f"- Couverture partial : {cov.get('partial', 0)}",
        f"- Couverture absent : {cov.get('absent', 0)}",
        "- Décision : les preuves documentaires issues de `supports/` rendent visibles les capacités, mais ne créent aucune validation humaine.",
        "",
        "## Juge de substance",
        "",
        f"- Verdicts pilotes vérifiés : {len(substance_reviews)}",
        "- Unités pilotes : P05, P06, T06, T07, T08, T10, T17, T18.",
        "- Schéma : `substance_verdict.schema.json`.",
        "- Index : `substance_reviews_index.md`.",
        "- Verdict adverse : `substance_reviews/_adversarial/poisoned.verdict.json` doit être refusé.",
        "- Verdict par défaut : `needs_content`; aucune ressource n'est promue par ce juge.",
        "",
        "## Politique des gates",
        "",
        "- Politique : `qa_gate_policy.md`.",
        "- Noyau bloquant : structure, privacy, tests, substance.",
        "- Les contrôles de comptage et de longueur restent indicatifs ou legacy.",
        "- Le seul gate pédagogique bloquant est le garde-fou de substance vérifiable par ancres.",
        "",
        "## Rendu charté pilote",
        "",
        "- Cible : `make render-unit U=P05` puis `make render-unit U=T10`.",
        "- Contrôle : `scripts/check_rendered_unit_artifacts.py --unit P05` et `--unit T10`.",
        "- Versions élève : corrigés/barèmes filtrés.",
        "- Versions prof : corrigés/barèmes présents.",
        "",
        "## Échelle capacités officielles",
        "",
        f"- Capacités documented : {capacity_counts['documented']}",
        f"- Capacités practiced : {capacity_counts['practiced']}",
        f"- Capacités assessed : {capacity_counts['assessed']}",
        f"- Capacités linked_to_session : {capacity_counts['linked_to_session']}",
        "- Capacités reviewed_pedagogy : 0",
        "- Capacités reviewed_science : 0",
        f"- Capacités covered : {capacity_counts['covered']}",
        "- Décision : documented/practiced/assessed ne valent pas validation humaine.",
        "",
        "## TP papier / exécutables",
        "",
        f"- TP papier : {paper_tp.paper_count}",
        f"- TP exécutables : {paper_tp.executable_count}",
        f"- Ratio papier : {(paper_tp.paper_count / (paper_tp.paper_count + paper_tp.executable_count) * 100) if (paper_tp.paper_count + paper_tp.executable_count) else 0:.1f}%",
        f"- Opportunités de conversion exécutable signalées : {len(tp_opportunities.opportunities)}",
        "- Seuil strict opportunités restantes : 8",
        f"- État seuil strict : {'PASS' if not tp_opportunities.errors else 'KO'}",
        "- Registre : `tp_executable_opportunity_register.md`.",
        "- Les TP papier restent `needs_review` et ne remplacent pas une revue humaine.",
        "",
        "## Séances opérationnelles / théoriques",
        "",
        f"- Séances opérationnelles ou reliées : {session_alignment.operational_count}",
        f"- Séances théoriques ou non reliées : {session_alignment.theoretical_count}",
        f"- Séances linked : {session_classroom.linked_count}",
        f"- Séances classroom_ready : {session_classroom.classroom_ready_count}",
        f"- Séances human_review_pending : {session_classroom.human_review_pending_count}",
        f"- Séances validated : {session_classroom.validated_count}",
        "- `classroom_ready` signifie exploitable documentairement ; la revue humaine reste pending.",
        "- Les séances théoriques restantes doivent être reliées explicitement aux supports produits avant publication.",
        "",
        "## Cohérence pédagogique par séquence",
        "",
        f"- Séquences vérifiées : {sequence_coherence.checked_sequences}",
        f"- Erreurs de cohérence détectées : {len(sequence_coherence.errors)}",
        "",
        "## Revue humaine",
        "",
        f"- Ressources majeures à relire : {human_review.expected_count}",
        f"- Lignes dans `human_review_register.csv` : {human_review.registered_count}",
        f"- Ressources prioritaires vague 1 : {len(human_wave.resources)}",
        f"- Priorités vague 1 couvertes : {', '.join(sorted(human_wave.priority_hits))}",
        "- Statut initial : pending pour science, pédagogie, accessibilité et technique.",
        "- Aucune ligne du registre ne promeut `validated_*`, `published` ou `covered`.",
        "",
        "## Fiches liées non opérationnelles",
        "",
        "| Fiche | Support absent | Registre associé | Date cible | Impact pédagogique | Action suivante |",
        "|---|---|---|---|---|---|",
        *(
            [
                f"| `{sheet}` | `{support}` | `missing_documents_register_v2.md` | {target} | {impact.replace('|', '/')} | {decision} |"
                for sheet, support, target, impact, decision in linked_rows
            ]
            or ["| Aucune fiche liée non opérationnelle. | - | - | - | - | - |"]
        ),
        "",
        "## Gates indicatifs encore en échec",
        "",
        "| Fichier concerné | Erreur | Décision | Date cible de correction |",
        "|---|---|---|---|",
        *(
            [
                f"| `{script}` | {detail.replace('|', '/')} | {decision} | {date} |"
                for script, detail, decision, date in indicative_rows
            ]
            or ["| Aucun échec indicatif observé pendant cette génération. | - | - | - |"]
        ),
        "",
        "Les dettes indicatives ouvertes sont aussi suivies dans `qa_debt_register.md` avec cause, risque, impact, responsable et critère de fermeture.",
        "",
        "## Décisions",
        "",
        "- Statut publication : NON.",
        "- Statut covered : 0.",
        "- Statut published : 0.",
        "- Statut validated_* : 0.",
        "- Archive pédagogique : dist/source_clean.tar.gz.",
        "- Archive globale contenant .git : interdite comme livraison principale.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("generate_qa_report: wrote qa_report.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
