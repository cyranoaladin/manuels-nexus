#!/usr/bin/env python3
"""Dashboard historique de préparation, non autoritaire pour la release.

Le verdict autoritaire est désormais
`audit/PUBLISH_READINESS_CHAPTER_MATRIX.json`. Cette vue conserve ses anciens
indicateurs éditoriaux, mais ne consomme pas toutes les preuves clone,
cross-discipline et sémantiques : elle ne peut donc jamais émettre READY.

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
import subprocess
from collections.abc import Mapping
from dataclasses import dataclass, field, asdict
from pathlib import Path

import yaml

try:
    from scripts.capacity_identity import (
        CapacityIdentityResolver,
        PREREQUISITE,
        UnresolvedCapacityIdentity,
    )
except ModuleNotFoundError:  # exécution directe depuis scripts/
    from capacity_identity import (  # type: ignore[no-redef]
        CapacityIdentityResolver,
        PREREQUISITE,
        UnresolvedCapacityIdentity,
    )

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
    authority: str = "NON_AUTHORITATIVE_LEGACY_DASHBOARD"
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
    qcm_capacities_assessed: list = field(default_factory=list)
    qcm_capacities_missing: list = field(default_factory=list)
    remediation_status: str = "absent"
    evaluation_A: bool = False
    evaluation_B: bool = False
    scientific_review: dict = field(default_factory=dict)
    unbound_receipts: dict = field(default_factory=dict)
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


def _variantes_du_manifeste(builds: list) -> dict[str, set[str]]:
    """Les variantes attestées, lues sur le manifeste et sur rien d'autre."""

    variantes: dict[str, set[str]] = {}
    for build in builds:
        if not isinstance(build, Mapping):
            return {}
        manuel = build.get("manual")
        variante = build.get("variant")
        if not isinstance(manuel, str) or not isinstance(variante, str):
            return {}
        variantes.setdefault(manuel, set()).add(variante)
    return variantes


def _builds_observes() -> dict[str, set[str]]:
    manifeste = RACINE / "audit/BUILD_MANIFEST.json"
    try:
        apercu = json.loads(manifeste.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    builds = apercu.get("builds") if isinstance(apercu, Mapping) else None
    if not isinstance(builds, list) or not builds:
        return {}

    try:
        try:
            from scripts import inventory_collection
        except ModuleNotFoundError:  # exécution directe depuis scripts/
            import inventory_collection  # type: ignore[no-redef]
        inventaire = inventory_collection.build_inventory(
            RACINE,
            require_git_provenance=True,
        )
    except (
        ModuleNotFoundError,
        OSError,
        ValueError,
        subprocess.SubprocessError,
    ):
        # L'inventaire exige une provenance Git propre. Répondre « aucune
        # construction observée » quand il ne peut pas tourner rendait ce
        # producteur non déterministe : ses PROPRES écritures salissent
        # l'arbre, si bien qu'il s'annonçait périmé aussitôt après s'être
        # écrit, et que `build_eleve` basculait d'un passage à l'autre.
        # Le manifeste, lui, dit ce qu'il atteste indépendamment de l'état de
        # l'arbre -- et il a été validé par son propre producteur au moment où
        # il l'a écrit.
        return _variantes_du_manifeste(builds)

    observes = inventaire.get("observed_builds")
    if not isinstance(observes, list):
        return _variantes_du_manifeste(builds)
    variantes: dict[str, set[str]] = {}
    for build in observes:
        if not isinstance(build, Mapping):
            return {}
        manuel = build.get("manual")
        variante = build.get("variant")
        if not isinstance(manuel, str) or not isinstance(variante, str):
            return {}
        variantes.setdefault(manuel, set()).add(variante)
    return variantes


def analyser(
    dossier: Path,
    versions: dict,
    builds_observes: Mapping[str, set[str]],
    *,
    resolver: CapacityIdentityResolver | None = None,
) -> Chapitre:
    nom = dossier.name
    resolver = resolver or CapacityIdentityResolver.from_corpora((dossier.parent,))
    ch = Chapitre(chapter_id=nom, manual_id=manuel_de(nom))
    ch.programme_version = versions.get(ch.manual_id or "")

    # --- contrat et capacités -------------------------------------------------
    contrat_path = dossier / "contrat.yaml"
    capacites: list[str] = []
    if contrat_path.exists():
        contrat = yaml.safe_load(contrat_path.read_text(encoding="utf-8")) or {}
        brut = str(contrat.get("statut", "absent")).split("#")[0].strip()
        ch.contract_status = brut or "absent"
        identities = resolver.capacities_of(nom)
        capacites = [identity.local_code for identity in identities]
        mappees = [identity for identity in identities if identity.official_ref]
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
            for code in resolver.resolve_meta_codes(nom, meta):
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
        json_qcm = sorted(qcm.glob("*-QCM.json"))
        tex_qcm = list(qcm.glob("*-QCM.tex"))
        if len(json_qcm) > 1:
            ch.qcm_status = "multiple_sources"
            ch.qcm_capacities_missing = sorted(capacites)
        elif json_qcm:
            donnees = json.loads(json_qcm[0].read_text(encoding="utf-8"))
            if donnees.get("chapitre") != nom:
                raise ValueError(f"{nom}: chapitre QCM incoherent")
            questions = donnees.get("questions", [])
            assessed: set[str] = set()
            for question in questions:
                resolution = resolver.resolve(nom, question.get("capacite"))
                if resolution.rule == PREREQUISITE:
                    raise UnresolvedCapacityIdentity(
                        f"{nom}/{question.get('id')}: prerequis utilise "
                        "comme capacite QCM"
                    )
                assessed.add(resolution.identity.local_code)
            ch.qcm_capacities_assessed = sorted(assessed)
            ch.qcm_capacities_missing = sorted(set(capacites) - assessed)
            manquants = sum(
                1
                for q in questions
                for lettre in (q.get("options") or {})
                if lettre != q.get("correcte") and lettre not in (q.get("diagnostics") or {})
            )
            if manquants:
                ch.qcm_status = f"diagnostics_incomplets:{manquants}"
            elif ch.qcm_capacities_missing:
                ch.qcm_status = (
                    "capacites_manquantes:" + ",".join(ch.qcm_capacities_missing)
                )
            else:
                ch.qcm_status = "source_unique"
        elif tex_qcm:
            ch.qcm_status = "tex_seul"

    remediation = dossier / "remediation"
    if remediation.exists():
        nb = len(list(remediation.glob("*.tex")))
        ch.remediation_status = "absent" if nb == 0 else ("partielle" if nb < ch.capabilities_total else "complete")

    evals = dossier / "evaluations"
    if evals.exists():
        variants: set[str] = set()
        for source in sorted(evals.glob("*.tex")):
            meta = _meta(source)
            if meta.get("type_objet") != "evaluation":
                continue
            resolver.resolve_meta_codes(nom, meta)
            version = str(meta.get("version") or "").strip().upper()
            object_id = str(meta.get("id") or "").strip().upper()
            if version in {"A", "B"}:
                variants.add(version)
            elif re.search(r"-(?:EV|EVAL)-A$", object_id):
                variants.add("A")
            elif re.search(r"-(?:EV|EVAL)-B$", object_id):
                variants.add("B")
        ch.evaluation_A = "A" in variants
        ch.evaluation_B = "B" in variants

    # --- statuts des objets ---------------------------------------------------
    # Un objet `generated` n'a franchi aucune revue : le pipeline de statuts
    # interdit qu'il paraisse dans une release. On les compte donc a part.
    for sous in (
        "cours",
        "methodes",
        "exercices",
        "corriges",
        "qcm",
        "remediation",
        "evaluations",
    ):
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
    # Un recu ne vaut preuve que s'il NOMME la source qu'il atteste et porte
    # son condensat : il meurt alors avec elle. Le recu SymPy le fait ; les
    # recus de similarite et les rapports adversariaux ne nomment rien et
    # survivraient a une reecriture complete du contenu. Les additionner dans
    # un meme `pass` publiait un total qui ressemblait a une preuve sans en
    # etre une -- 262 annonces pour 122 preuves reelles sur 1SPE-SUITES.
    #
    # Ils ne sont pas effaces pour autant : les taire echangerait un total
    # trompeur contre un silence. Ils sortent nommes, par gate, et un echec
    # y reste bloquant.
    validations = dossier / "validations"
    verdicts: dict[str, int] = {}
    non_lies: dict[str, dict[str, int]] = {}
    if validations.exists():
        for recu in sorted(validations.glob("*.json")):
            try:
                donnees = json.loads(recu.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            verdict = str(donnees.get("verdict", "inconnu"))
            if donnees.get("source_sha256"):
                verdicts[verdict] = verdicts.get(verdict, 0) + 1
                continue
            gate = str(donnees.get("gate") or "").strip()
            if not gate:
                # Un recu sans gate declare est nomme par son suffixe de
                # fichier : `<objet>.adversarial.json` -> `adversarial`.
                suffixes = recu.name.split(".")
                gate = suffixes[-2] if len(suffixes) > 2 else "inconnu"
            seau = non_lies.setdefault(gate, {})
            seau[verdict] = seau.get(verdict, 0) + 1
    ch.scientific_review = dict(sorted(verdicts.items()))
    ch.unbound_receipts = {
        gate: dict(sorted(seau.items())) for gate, seau in sorted(non_lies.items())
    }

    if ch.capabilities_total and ch.capabilities_mapped == ch.capabilities_total:
        ch.programme_review = "capacites_toutes_rattachees"
    elif ch.capabilities_total:
        ch.programme_review = "rattachement_incomplet"

    # --- builds ---------------------------------------------------------------
    variantes_observees = builds_observes.get(ch.manual_id or "", set())
    ch.student_build = "eleve" in variantes_observees
    ch.teacher_build = "professeur" in variantes_observees

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
    echecs_non_lies = sum(
        seau.get("fail", 0) for seau in ch.unbound_receipts.values()
    )
    if echecs_non_lies:
        # Ce recu ne prouve rien, mais son echec reste un signal : il ne doit
        # pas devenir muet du seul fait qu'on a cesse de le compter comme
        # preuve.
        b.append(f"{echecs_non_lies} verdict(s) en echec sur des recus non lies")
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
    # Ce dashboard ne porte plus l'autorité de release. Même si ses critères
    # historiques sont satisfaits, la matrice verticale reste le seul gate.
    ch.release_ready = False
    return ch


def collecter() -> list[Chapitre]:
    versions = _versions_programme()
    builds_observes = _builds_observes()
    resolver = CapacityIdentityResolver.from_corpora(RACINES_CHAPITRES)
    chapitres = []
    for base in RACINES_CHAPITRES:
        if not base.exists():
            continue
        for dossier in sorted(base.iterdir()):
            if dossier.is_dir() and (dossier / "contrat.yaml").exists():
                chapitres.append(
                    analyser(
                        dossier,
                        versions,
                        builds_observes,
                        resolver=resolver,
                    )
                )
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
                    "authority": "NON_AUTHORITATIVE_LEGACY_DASHBOARD",
                    "authoritative_successor": "audit/PUBLISH_READINESS_CHAPTER_MATRIX.json",
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
