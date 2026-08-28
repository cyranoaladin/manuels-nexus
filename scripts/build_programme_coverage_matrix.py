#!/usr/bin/env python3
"""Build the six-manual programme coverage matrix for edition 2026-2027."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
AUTHORITIES_PATH = ROOT / "audit" / "OFFICIAL_AUTHORITIES_2026_2027.json"
OUTPUT_JSON = ROOT / "audit" / "PROGRAMME_COVERAGE_MATRIX_2026_2027.json"
OUTPUT_MD = ROOT / "audit" / "PROGRAMME_COVERAGE_MATRIX_2026_2027.md"
META_RE = re.compile(r"^% META: (\{.*\})$", re.MULTILINE)

MANUAL_CONFIG = {
    "1SPE": {
        "root": "Mathematiques/manuel-maths",
        "chapter_prefix": "1SPE-",
        "reference_glob": "capacites_1SPE_*.json",
        "official_source": "Mathematiques/manuel-maths/sources/txt/BO2026_1SPE_specialite.txt",
    },
    "TSPE": {
        "root": "Mathematiques/manuel-maths",
        "chapter_prefix": "TSPE-",
        "reference_glob": "capacites_TSPE_*.json",
        "official_source": "Mathematiques/manuel-maths/sources/txt/BO2019_TSPE_specialite.txt",
    },
    "TCOMPL": {
        "root": "Mathematiques/manuel-maths",
        "chapter_prefix": "TCOMPL-",
        "reference_glob": "capacites_TCOMPL_*.json",
        "official_source": "Mathematiques/manuel-maths/sources/txt/BO2019_TCOMPL_optionnel.txt",
    },
    "TEXPERTES": {
        "root": "Mathematiques/manuel-maths",
        "chapter_prefix": "TEXP-",
        "reference_glob": "capacites_TEXPERTES_*.json",
        "official_source": "Mathematiques/manuel-maths/sources/txt/BO2019_TEXPERTES_optionnel.txt",
    },
    "1NSI": {
        "root": "NSI",
        "chapter_prefix": "1NSI-",
        "reference_glob": "capacites_1NSI_*.json",
        "official_source": "NSI/sources/BO2019_NSI_premiere.pdf",
    },
    "TNSI": {
        "root": "NSI",
        "chapter_prefix": "TNSI-",
        "reference_glob": "capacites_TNSI_*.json",
        "official_source": "NSI/sources/txt/BO2019_NSI_terminale.txt",
    },
}

NON_CAPACITY_CONTRACT_REFS = {
    "BO-PREAMBULE-DEMARCHE-DE-PROJET": {
        "obligation_type": "IMPLEMENTATION_GUIDANCE",
        "wording": "Une part d'au moins un quart de l'horaire de première est réservée à des projets conduits en groupes ; leur gestion inclut des points d'étape.",
        "section": "Démarche de projet",
    },
    "BO-PREAMBULE-COMPETENCES-METHODE": {
        "obligation_type": "OPTIONAL_EXTENSION",
        "wording": "Le contrat étend la mise au point et les jeux de tests officiels à une démarche explicite de débogage.",
        "section": "Mise au point de programmes",
    },
    "BO-PREAMBULE-COMPETENCES-ORALES": {
        "obligation_type": "IMPLEMENTATION_GUIDANCE",
        "wording": "Le préambule demande de développer les compétences orales par l'argumentation et l'explicitation du raisonnement.",
        "section": "Compétences orales",
    },
}

CATEGORY_FIELDS = {
    "cours": "course_sources",
    "methodes": "method_sources",
    "exercices": "exercise_sources",
    "evaluations": "assessment_sources",
    "qcm": "assessment_sources",
    "remediation": "remediation_sources",
}
EVIDENCE_FIELDS = (
    "course_sources",
    "method_sources",
    "exercise_sources",
    "assessment_sources",
    "remediation_sources",
)


def normalized(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return " ".join(re.findall(r"[a-z0-9]+", text.lower()))


def official_lines(path: Path) -> list[str]:
    if path.suffix.lower() == ".pdf":
        return subprocess.check_output(
            ["pdftotext", "-layout", str(path), "-"], text=True
        ).splitlines()
    return path.read_text(encoding="utf-8").splitlines()


def find_anchor(lines: list[str], wording: str, section: str, source_path: str) -> str:
    candidates = [wording, section]
    best_line, best_score = 1, -1
    normalized_lines = [normalized(line) for line in lines]
    for candidate in candidates:
        tokens = [token for token in normalized(candidate).split() if len(token) >= 4]
        if not tokens:
            continue
        for index, line in enumerate(normalized_lines, start=1):
            score = sum(token in line for token in tokens) / len(tokens)
            if score > best_score:
                best_line, best_score = index, score
    return f"{source_path}#text-line={best_line};section={section}"


def load_contracts(config: dict) -> tuple[dict[str, dict], list[dict]]:
    manual_root = ROOT / config["root"]
    by_ref: dict[str, dict] = {}
    extra: list[dict] = []
    for contract_path in sorted((manual_root / "chapitres").glob(f"{config['chapter_prefix']}*/contrat.yaml")):
        contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
        for capacity in contract.get("capacites", []):
            data = {
                "chapter": contract["chapitre"],
                "contract_capacity": capacity["code"],
                "ref_capacite": capacity["ref_capacite"],
                "student_wording": capacity.get("libelle_eleve", ""),
                "contract_path": str(contract_path.relative_to(ROOT)),
            }
            if capacity["ref_capacite"] in NON_CAPACITY_CONTRACT_REFS:
                extra.append(data)
            else:
                by_ref[capacity["ref_capacite"]] = data
    return by_ref, extra


def meta_capacity_refs(chapter_path: Path, contract: dict) -> dict[str, dict[str, set[str]]]:
    code_to_ref = {
        capacity["code"]: capacity["ref_capacite"] for capacity in contract.get("capacites", [])
    }
    evidence: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: defaultdict(set)
    )
    for folder, field in CATEGORY_FIELDS.items():
        directory = chapter_path / folder
        if not directory.exists():
            continue
        for source in sorted(directory.iterdir()):
            refs: set[str] = set()
            if source.suffix == ".tex":
                match = META_RE.search(source.read_text(encoding="utf-8", errors="replace"))
                if match:
                    metadata = json.loads(match.group(1))
                    for ref in metadata.get("capacites", []):
                        refs.add(code_to_ref.get(ref, ref))
                    for code in metadata.get("capacites_codes", []):
                        refs.add(code_to_ref.get(code, code))
            elif folder == "qcm" and source.suffix == ".json":
                payload = json.loads(source.read_text(encoding="utf-8"))
                for question in payload.get("questions", []):
                    ref = question.get("capacite")
                    if ref:
                        refs.add(code_to_ref.get(ref, ref))
            relative = str(source.relative_to(ROOT))
            for ref in refs:
                evidence[ref][field].add(relative)
    return evidence


def build_evidence(config: dict) -> dict[str, dict[str, set[str]]]:
    manual_root = ROOT / config["root"]
    all_evidence: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    for contract_path in sorted((manual_root / "chapitres").glob(f"{config['chapter_prefix']}*/contrat.yaml")):
        contract = yaml.safe_load(contract_path.read_text(encoding="utf-8"))
        chapter_evidence = meta_capacity_refs(contract_path.parent, contract)
        for ref, fields in chapter_evidence.items():
            for field, paths in fields.items():
                all_evidence[ref][field].update(paths)
    return all_evidence


def exam_alignment(authorities: dict) -> dict:
    output = {}
    for manual, data in authorities["manuals"].items():
        exam = data["DEFINITION_D_EPREUVE"]
        if manual == "1SPE":
            output[manual] = {"ASSESSMENT_REGIME": data["ASSESSMENT_REGIME"], **data["EXAM_ALIGNMENT"]}
        elif manual == "TNSI":
            output[manual] = {
                "ASSESSMENT_REGIME": data["ASSESSMENT_REGIME"],
                "written_duration_minutes": exam["written_duration_minutes"],
                "written_raw_scale": exam["written_raw_scale"],
                "written_weight": exam["written_weight"],
                "practical_duration_minutes": exam["practical_duration_minutes"],
                "practical_raw_scale": exam["practical_raw_scale"],
                "practical_weight": exam["practical_weight"],
                "candidate_conditions": {
                    "school": exam["school_candidates"],
                    "individual_and_out_of_contract": exam["individual_and_out_of_contract_candidates"],
                    "CNED_free_candidate": exam["CNED_free_candidate"],
                },
            }
        else:
            output[manual] = {"ASSESSMENT_REGIME": data["ASSESSMENT_REGIME"], **exam}
    return output


def build_payload() -> dict:
    authorities = json.loads(AUTHORITIES_PATH.read_text(encoding="utf-8"))
    atoms = []

    for manual, config in MANUAL_CONFIG.items():
        authority = authorities["manuals"][manual]["PROGRAMME_D_ENSEIGNEMENT"]
        official_source = ROOT / config["official_source"]
        lines = official_lines(official_source)
        contracts, extras = load_contracts(config)
        evidence = build_evidence(config)
        reference_root = ROOT / config["root"] / "referentiel"

        for reference_path in sorted(reference_root.glob(config["reference_glob"])):
            reference = json.loads(reference_path.read_text(encoding="utf-8"))
            section = reference.get("theme", reference_path.stem)
            for capacity in reference.get("capacites", []):
                ref = capacity["id"]
                contract = contracts.get(ref)
                fields = {
                    field: sorted(evidence[ref].get(field, set()))
                    for field in EVIDENCE_FIELDS
                }
                evidence_paths = sorted(
                    {str(reference_path.relative_to(ROOT)), *(fields["course_sources"]), *(fields["method_sources"]), *(fields["exercise_sources"]), *(fields["assessment_sources"]), *(fields["remediation_sources"])}
                )
                if contract:
                    evidence_paths.insert(0, contract["contract_path"])
                wording = capacity.get("libelle_bo") or capacity.get("contenu_bo") or capacity.get("libelle_eleve", "")
                structurally_mapped = bool(contract and any(fields.values()))
                atoms.append(
                    {
                        "atom_id": ref,
                        "official_document_id": authority["official_document_id"],
                        "NOR": authority["NOR"],
                        "official_section": section,
                        "official_page_or_anchor": "UNVERIFIED_CANDIDATE:"
                        + find_anchor(lines, wording, section, config["official_source"]),
                        "official_wording_or_short_paraphrase": wording,
                        "obligation_type": "MANDATORY_EXPECTED_CAPACITY",
                        "mandatory": True,
                        "mandatory_for_coverage": "YES",
                        "mandatory_justification": "Element listed in the official capacity registry derived from the applicable teaching programme.",
                        "manual": manual,
                        "chapter": contract["chapter"] if contract else None,
                        "contract_capacity": contract["contract_capacity"] if contract else None,
                        **fields,
                        "coverage_status": "STRUCTURALLY_MAPPED" if structurally_mapped else "MISSING",
                        "evidence_paths": evidence_paths,
                        "review_status": "OFFICIAL_ATOM_REDERIVATION_REQUIRED",
                    }
                )

        for extra in extras:
            official = NON_CAPACITY_CONTRACT_REFS[extra["ref_capacite"]]
            fields = {
                field: sorted(evidence[extra["ref_capacite"]].get(field, set()))
                for field in EVIDENCE_FIELDS
            }
            evidence_paths = sorted(
                {extra["contract_path"], *(fields["course_sources"]), *(fields["method_sources"]), *(fields["exercise_sources"]), *(fields["assessment_sources"]), *(fields["remediation_sources"])}
            )
            atoms.append(
                {
                    "atom_id": extra["ref_capacite"],
                    "official_document_id": authority["official_document_id"],
                    "NOR": authority["NOR"],
                    "official_section": official["section"],
                    "official_page_or_anchor": "UNVERIFIED_CANDIDATE:"
                    + find_anchor(lines, official["wording"], official["section"], config["official_source"]),
                    "official_wording_or_short_paraphrase": official["wording"],
                    "obligation_type": official["obligation_type"],
                    "mandatory": False,
                    "mandatory_for_coverage": "NO",
                    "mandatory_justification": "Official preamble guidance or a documented manual extension; not an autonomous mandatory programme capacity.",
                    "manual": manual,
                    "chapter": extra["chapter"],
                    "contract_capacity": extra["contract_capacity"],
                    **fields,
                    "coverage_status": "OUT_OF_SCOPE_WITH_PROOF",
                    "evidence_paths": evidence_paths,
                    "review_status": "OFFICIAL_ATOM_REDERIVATION_REQUIRED",
                }
            )

    atoms.sort(key=lambda atom: (atom["manual"], atom["chapter"] or "", atom["atom_id"]))
    mandatory = [atom for atom in atoms if atom["mandatory"]]
    status_counts = Counter(atom["coverage_status"] for atom in mandatory)
    by_manual = {}
    for manual in MANUAL_CONFIG:
        rows = [atom for atom in mandatory if atom["manual"] == manual]
        counts = Counter(atom["coverage_status"] for atom in rows)
        by_manual[manual] = {
            "candidate_internal_atoms": len(rows),
            "full": counts["FULL"],
            "partial": counts["PARTIAL"],
            "missing": counts["MISSING"],
            "structurally_mapped": counts["STRUCTURALLY_MAPPED"],
            "official_atom_rederivation_required": len(rows),
        }

    wrong_year = []
    for manual, data in authorities["manuals"].items():
        wrong = data["PROGRAMME_D_ENSEIGNEMENT"].get("wrong_year_document")
        if wrong:
            wrong_year.append({"manual": manual, **wrong, "classification": "WRONG_YEAR"})

    return {
        "artifact_type": "PROGRAMME_STRUCTURAL_CROSSWALK_DRAFT_2026_2027",
        "schema_version": 1,
        "status": "REJECTED_AS_PROGRAMME_COVERAGE_MATRIX",
        "edition": "2026-2027",
        "authority_namespaces": authorities["namespaces"],
        "manuals": list(MANUAL_CONFIG),
        "coverage_policy": {
            "FULL_requires_scientific_and_pedagogical_review": True,
            "structural_reference_is_not_FULL": True,
            "internal_referential_is_not_official_authority": True,
            "current_default": "STRUCTURALLY_MAPPED + OFFICIAL_ATOM_REDERIVATION_REQUIRED",
        },
        "exam_or_assessment_alignment": exam_alignment(authorities),
        "wrong_year_sources": wrong_year,
        "subject_2026_program_authority": False,
        "summary": {
            "official_authorities": "6/6",
            "programme_coverage_complete": False,
            "official_atoms_uninventoried": True,
            "candidate_atoms": len(atoms),
            "candidate_internal_atoms": len(mandatory),
            "mandatory_missing": None,
            "full": status_counts["FULL"],
            "partial": status_counts["PARTIAL"],
            "candidate_missing_within_internal_referentials": status_counts["MISSING"],
            "structurally_mapped": status_counts["STRUCTURALLY_MAPPED"],
            "out_of_scope_with_proof": sum(atom["coverage_status"] == "OUT_OF_SCOPE_WITH_PROOF" for atom in atoms),
            "wrong_year": len(wrong_year),
            "unsupported_claim": sum(atom["coverage_status"] == "UNSUPPORTED_CLAIM" for atom in atoms),
            "by_manual": by_manual,
        },
        "atoms": atoms,
    }


def render_markdown(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# Matrice de couverture des programmes — édition 2026-2027",
        "",
        "**STATUT : REJETÉ COMME MATRICE DE COUVERTURE OFFICIELLE.** Ce document est seulement un crosswalk candidat des référentiels internes. Il ne permet pas de conclure `MISSING=0`.",
        "",
        "Les trois autorités restent séparées : `PROGRAMME_D_ENSEIGNEMENT`, `DEFINITION_D_EPREUVE` et `SUJETS_D_EXAMEN`. Un sujet d'examen n'ajoute ni ne retire aucun atome de programme.",
        "",
        "## Synthèse",
        "",
        f"- Autorités officielles : **{summary['official_authorities']}**",
        f"- Candidats issus des référentiels internes : **{summary['candidate_internal_atoms']}**",
        f"- `STRUCTURALLY_MAPPED` dans ce périmètre interne : **{summary['structurally_mapped']}**",
        "- Inventaire des atomes officiels : **à refaire directement depuis les six textes**",
        "- `MANDATORY_MISSING` : **indéterminé tant que cette ré-atomisation n'est pas terminée**",
        f"- `FULL` : **{summary['full']}** — aucun renvoi structurel n'est auto-promu",
        f"- `OUT_OF_SCOPE_WITH_PROOF` : **{summary['out_of_scope_with_proof']}**",
        f"- `WRONG_YEAR` : **{summary['wrong_year']}**",
        f"- `UNSUPPORTED_CLAIM` : **{summary['unsupported_claim']}**",
        "",
        "## Couverture par manuel",
        "",
    ]
    for manual, data in summary["by_manual"].items():
        lines.append(
            f"- `{manual}` : {data['candidate_internal_atoms']} candidats internes ; "
            f"structurellement mappés={data['structurally_mapped']} ; FULL={data['full']}."
        )
    lines.extend(
        [
            "",
            "## Alignement examen / évaluation",
            "",
            "Le détail réglementaire par manuel est conservé dans `exam_or_assessment_alignment` du JSON. En particulier, TNSI stocke deux notes brutes sur 20 et les poids 0,75/0,25 — jamais des barèmes bruts 15/5.",
            "",
            "## Statut de preuve",
            "",
            "Les ancres lexicales sont préfixées `UNVERIFIED_CANDIDATE` et ne valent pas preuve officielle. Toutes les lignes restent `OFFICIAL_ATOM_REDERIVATION_REQUIRED`.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    json_text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    md_text = render_markdown(payload)
    if args.check:
        mismatches = [
            str(path.relative_to(ROOT))
            for path, expected in ((OUTPUT_JSON, json_text), (OUTPUT_MD, md_text))
            if not path.exists() or path.read_text(encoding="utf-8") != expected
        ]
        if mismatches:
            print("Artifacts out of date: " + ", ".join(mismatches))
            return 1
        print(f"Programme candidate crosswalk current: {payload['summary']['candidate_internal_atoms']} internal atoms; official matrix incomplete")
        return 0
    OUTPUT_JSON.write_text(json_text, encoding="utf-8")
    OUTPUT_MD.write_text(md_text, encoding="utf-8")
    print(f"Wrote rejected candidate crosswalk with {payload['summary']['candidate_internal_atoms']} internal atoms")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
