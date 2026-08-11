#!/usr/bin/env python3
"""Calcule l'état de préparation de chaque chapitre de la collection.

La complétude d'un chapitre n'est jamais déclarée à la main : elle est
recalculée ici depuis l'arbre réel — contrats, référentiels, objets produits,
reçus de vérification, PDF construits.

Seuil d'exercices (décision éditoriale du 2026-08-11, remplace le seuil
uniforme de 50) :

    C = nombre de capacités du chapitre
    TARGET_EXERCISES = min(50, max(24, 6 * C))

Indépendamment du total, chaque capacité doit disposer d'au moins 3 exercices
dédiés et apparaître dans au moins deux parcours. Les QCM, diagnostics,
remédiations, évaluations, projets et fiches méthodes sont complémentaires :
ils ne comptent jamais dans TARGET_EXERCISES.

Usage :
    python3 scripts/chapter_readiness.py                  # tous les chapitres
    python3 scripts/chapter_readiness.py --chap TSPE-CONTINUITE
    python3 scripts/chapter_readiness.py --json audit/CHAPTER_READINESS.json
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field, asdict
from pathlib import Path

import yaml

RACINE = Path(__file__).resolve().parents[1]

# Un chapitre appartient au manuel dont il porte le préfixe.
PREFIXES = (
    ("1SPE-", "1SPE"),
    ("TSPE-", "TSPE_2026_2027"),
    ("TCOMPL-", "TCOMPL"),
    ("TEXP-", "TEXPERTES"),
    ("1NSI-", "1NSI"),
    ("TNSI-", "TNSI"),
)

RACINES_CHAPITRES = (
    RACINE / "Mathematiques/manuel-maths/chapitres",
    RACINE / "NSI/chapitres",
)

MIN_EXERCICES_PAR_CAPACITE = 3
MIN_PARCOURS_PAR_CAPACITE = 2
PLANCHER_EXERCICES = 24
EXERCICES_PAR_CAPACITE = 6
PLAFOND_EXERCICES = 50

META = re.compile(r"% META:\s*(\{.*?\})\s*$", re.MULTILINE | re.DOTALL)


def manuel_de(chapitre: str) -> str | None:
    for prefixe, manuel in PREFIXES:
        if chapitre.startswith(prefixe):
            return manuel
    return None


def _meta(chemin: Path) -> dict:
    try:
        texte = chemin.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return {}
    trouve = META.search(texte)
    if not trouve:
        return {}
    try:
        return json.loads(trouve.group(1))
    except json.JSONDecodeError:
        return {}


def cible_exercices(nb_capacites: int) -> int:
    if nb_capacites <= 0:
        return PLANCHER_EXERCICES
    return min(PLAFOND_EXERCICES, max(PLANCHER_EXERCICES, EXERCICES_PAR_CAPACITE * nb_capacites))


@dataclass
class Chapitre:
    chapter_id: str
    manual_id: str | None
    programme_version: str | None = None
    capabilities_total: int = 0
    capabilities_mapped: int = 0
    course_status: str = "absent"
    exercise_count: int = 0
    target_exercises: int = 0
    capability_min_exercises: dict = field(default_factory=dict)
    capabilities_below_min: list = field(default_factory=list)
    capabilities_single_parcours: list = field(default_factory=list)
    parcours_ratio: dict = field(default_factory=dict)
    objects_total: int = 0
    objects_generated: int = 0
    objects_reviewed: int = 0
    correction_count: int = 0
    hints_count: int = 0
    methods_count: int = 0
    qcm_status: str = "absent"
    remediation_status: str = "absent"
    evaluation_A: bool = False
    evaluation_B: bool = False
    scientific_review: dict = field(default_factory=dict)
    programme_review: str = "non_verifie"
    contract_status: str = "absent"
    student_build: bool = False
    teacher_build: bool = False
    pdf_preflight: str = "non_execute"
    blocking_findings: list = field(default_factory=list)
    readiness_percent: float = 0.0
    release_ready: bool = False


def _versions_programme() -> dict:
    chemin = RACINE / "docs/programmes/PROGRAMMES_2026_2027.yaml"
    if not chemin.exists():
        return {}
    registre = yaml.safe_load(chemin.read_text(encoding="utf-8")) or {}
    return {
        m["manual_id"]: str(m.get("programme_version"))
        for m in registre.get("manuels", [])
    }


def _pdfs_construits() -> set[str]:
    trouves = set()
    for base in (RACINE / "Mathematiques/manuel-maths/build", RACINE / "NSI/build"):
        if base.exists():
            for pdf in base.rglob("*.pdf"):
                trouves.add(pdf.name.lower())
    return trouves


def analyser(dossier: Path, versions: dict, pdfs: set[str]) -> Chapitre:
    nom = dossier.name
    ch = Chapitre(chapter_id=nom, manual_id=manuel_de(nom))
    ch.programme_version = versions.get(ch.manual_id or "")

    # --- contrat et capacités -------------------------------------------------
    contrat_path = dossier / "contrat.yaml"
    capacites: list[str] = []
    if contrat_path.exists():
        contrat = yaml.safe_load(contrat_path.read_text(encoding="utf-8")) or {}
        brut = str(contrat.get("statut", "absent")).split("#")[0].strip()
        ch.contract_status = brut or "absent"
        capacites = [c["code"] for c in (contrat.get("capacites") or []) if c.get("code")]
        mappees = [
            c for c in (contrat.get("capacites") or [])
            if c.get("ref_capacite")
        ]
        ch.capabilities_total = len(capacites)
        ch.capabilities_mapped = len(mappees)
    ch.target_exercises = cible_exercices(ch.capabilities_total)

    # --- exercices ------------------------------------------------------------
    dossier_ex = dossier / "exercices"
    par_capacite: dict[str, int] = {c: 0 for c in capacites}
    parcours_par_capacite: dict[str, set] = {c: set() for c in capacites}
    compte_parcours: dict[str, int] = {}
    if dossier_ex.exists():
        for fichier in sorted(dossier_ex.glob("*.tex")):
            if "CDP" in fichier.name:
                ch.hints_count += 1
                continue
            ch.exercise_count += 1
            meta = _meta(fichier)
            parcours = str(meta.get("parcours", "?"))
            compte_parcours[parcours] = compte_parcours.get(parcours, 0) + 1
            for code in meta.get("capacites_codes") or []:
                par_capacite[code] = par_capacite.get(code, 0) + 1
                parcours_par_capacite.setdefault(code, set()).add(parcours)

    ch.capability_min_exercises = dict(sorted(par_capacite.items()))
    ch.capabilities_below_min = [
        c for c, n in par_capacite.items() if n < MIN_EXERCICES_PAR_CAPACITE
    ]
    ch.capabilities_single_parcours = [
        c for c, p in parcours_par_capacite.items() if len(p) < MIN_PARCOURS_PAR_CAPACITE
    ]
    total = ch.exercise_count or 1
    ch.parcours_ratio = {
        p: round(100 * n / total) for p, n in sorted(compte_parcours.items())
    }

    # --- autres objets --------------------------------------------------------
    ch.correction_count = len(list((dossier / "corriges").glob("*.tex"))) if (dossier / "corriges").exists() else 0
    ch.methods_count = len(list((dossier / "methodes").glob("*.tex"))) if (dossier / "methodes").exists() else 0

    cours = dossier / "cours"
    if cours.exists():
        nb = len(list(cours.glob("*.tex")))
        ch.course_status = "absent" if nb == 0 else ("minimal" if nb < ch.capabilities_total else "structure")

    qcm = dossier / "qcm"
    if qcm.exists():
        json_qcm = list(qcm.glob("*-QCM.json"))
        tex_qcm = list(qcm.glob("*-QCM.tex"))
        if json_qcm:
            donnees = json.loads(json_qcm[0].read_text(encoding="utf-8"))
            questions = donnees.get("questions", [])
            manquants = sum(
                1
                for q in questions
                for lettre in (q.get("options") or {})
                if lettre != q.get("correcte") and lettre not in (q.get("diagnostics") or {})
            )
            ch.qcm_status = "source_unique" if manquants == 0 else f"diagnostics_incomplets:{manquants}"
        elif tex_qcm:
            ch.qcm_status = "tex_seul"

    remediation = dossier / "remediation"
    if remediation.exists():
        nb = len(list(remediation.glob("*.tex")))
        ch.remediation_status = "absent" if nb == 0 else ("partielle" if nb < ch.capabilities_total else "complete")

    evals = dossier / "evaluations"
    if evals.exists():
        noms = [f.name for f in evals.glob("*.tex")]
        ch.evaluation_A = any("EV-A" in n and "corrige" not in n for n in noms)
        ch.evaluation_B = any("EV-B" in n and "corrige" not in n for n in noms)

    # --- statuts des objets ---------------------------------------------------
    # Un objet `generated` n'a franchi aucune revue : le pipeline de statuts
    # interdit qu'il paraisse dans une release. On les compte donc a part.
    for sous in ("cours", "methodes", "exercices", "corriges", "remediation", "evaluations"):
        rep = dossier / sous
        if not rep.exists():
            continue
        for fichier in rep.rglob("*.tex"):
            statut = str(_meta(fichier).get("status", "")).lower()
            if not statut:
                continue
            ch.objects_total += 1
            if statut == "generated":
                ch.objects_generated += 1
            elif statut in ("verified", "reviewed", "ready", "approved", "published"):
                ch.objects_reviewed += 1

    # --- revue scientifique ---------------------------------------------------
    validations = dossier / "validations"
    verdicts: dict[str, int] = {}
    if validations.exists():
        for recu in validations.glob("*.json"):
            try:
                donnees = json.loads(recu.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            verdict = str(donnees.get("verdict", "inconnu"))
            verdicts[verdict] = verdicts.get(verdict, 0) + 1
    ch.scientific_review = dict(sorted(verdicts.items()))

    if ch.capabilities_total and ch.capabilities_mapped == ch.capabilities_total:
        ch.programme_review = "capacites_toutes_rattachees"
    elif ch.capabilities_total:
        ch.programme_review = "rattachement_incomplet"

    # --- builds ---------------------------------------------------------------
    # Les noms de PDF ne reprennent pas toujours l'identifiant du manuel tel
    # quel : TSPE_2026_2027 se materialise en MANUEL_TSPE_2026-2027_*.pdf. On
    # compare donc sur une forme normalisee, sans separateurs.
    def _normaliser(valeur: str) -> str:
        return re.sub(r"[^a-z0-9]", "", valeur.lower())

    manuel = _normaliser(ch.manual_id or "")
    normalises = {_normaliser(nom): nom for nom in pdfs}
    ch.student_build = any(
        manuel and manuel in cle and "eleve" in cle for cle in normalises
    )
    ch.teacher_build = any(
        manuel and manuel in cle and "professeur" in cle for cle in normalises
    )

    # --- constats bloquants ---------------------------------------------------
    b = ch.blocking_findings
    if ch.capabilities_total == 0:
        b.append("aucune capacite declaree au contrat")
    if ch.capabilities_mapped < ch.capabilities_total:
        b.append(
            f"{ch.capabilities_total - ch.capabilities_mapped} capacite(s) sans ref_capacite officielle"
        )
    if ch.exercise_count < ch.target_exercises:
        b.append(f"exercices {ch.exercise_count}/{ch.target_exercises}")
    if ch.capabilities_below_min:
        b.append(
            f"capacites sous {MIN_EXERCICES_PAR_CAPACITE} exercices : {', '.join(sorted(ch.capabilities_below_min))}"
        )
    if ch.capabilities_single_parcours:
        b.append(
            f"capacites sur un seul parcours : {', '.join(sorted(ch.capabilities_single_parcours))}"
        )
    if ch.correction_count < ch.exercise_count:
        b.append(f"corriges {ch.correction_count}/{ch.exercise_count}")
    if ch.course_status != "structure":
        b.append(f"cours {ch.course_status}")
    if ch.qcm_status != "source_unique":
        b.append(f"qcm {ch.qcm_status}")
    if ch.remediation_status != "complete":
        b.append(f"remediation {ch.remediation_status}")
    if not (ch.evaluation_A and ch.evaluation_B):
        b.append("evaluation A/B incomplete")
    if verdicts.get("fail"):
        b.append(f"{verdicts['fail']} verdict(s) scientifique(s) en echec")
    if ch.objects_generated:
        b.append(f"{ch.objects_generated}/{ch.objects_total} objets encore au statut generated")
    if ch.contract_status in ("draft", "absent"):
        b.append(f"contrat {ch.contract_status}")
    if not ch.teacher_build or not ch.student_build:
        b.append("build manuel incomplet")

    # --- score ----------------------------------------------------------------
    criteres = [
        ch.capabilities_total > 0,
        ch.capabilities_total > 0 and ch.capabilities_mapped == ch.capabilities_total,
        ch.exercise_count >= ch.target_exercises,
        not ch.capabilities_below_min,
        not ch.capabilities_single_parcours,
        ch.correction_count >= ch.exercise_count > 0,
        ch.course_status == "structure",
        ch.methods_count > 0,
        ch.qcm_status == "source_unique",
        ch.remediation_status == "complete",
        ch.evaluation_A and ch.evaluation_B,
        not verdicts.get("fail"),
        ch.objects_total > 0 and ch.objects_generated == 0,
        ch.student_build,
        ch.teacher_build,
    ]
    ch.readiness_percent = round(100 * sum(criteres) / len(criteres), 1)
    ch.release_ready = all(criteres) and not b
    return ch


def collecter() -> list[Chapitre]:
    versions = _versions_programme()
    pdfs = _pdfs_construits()
    chapitres = []
    for base in RACINES_CHAPITRES:
        if not base.exists():
            continue
        for dossier in sorted(base.iterdir()):
            if dossier.is_dir() and (dossier / "contrat.yaml").exists():
                chapitres.append(analyser(dossier, versions, pdfs))
    return chapitres


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--chap", help="limiter a un chapitre")
    parseur.add_argument("--json", help="ecrire le rapport JSON a ce chemin")
    args = parseur.parse_args()

    chapitres = collecter()
    if args.chap:
        chapitres = [c for c in chapitres if c.chapter_id == args.chap]
        if not chapitres:
            print(f"chapitre inconnu : {args.chap}")
            return 2

    print(f"{'chapitre':36s}{'manuel':16s}{'ex':>7s}{'cible':>7s}{'prets':>8s}")
    for ch in chapitres:
        print(
            f"{ch.chapter_id:36s}{ch.manual_id or '?':16s}"
            f"{ch.exercise_count:7d}{ch.target_exercises:7d}{ch.readiness_percent:7.1f}%"
        )

    prets = sum(1 for c in chapitres if c.release_ready)
    print(f"\n{len(chapitres)} chapitres | release_ready = {prets}")

    if args.json:
        cible = RACINE / args.json
        cible.parent.mkdir(parents=True, exist_ok=True)
        cible.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "generated_by": "scripts/chapter_readiness.py",
                    "chapters": [asdict(c) for c in chapitres],
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        print(f"rapport ecrit : {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
