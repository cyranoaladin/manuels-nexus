#!/usr/bin/env python3
"""Chaque exigence officielle est-elle reellement enseignee dans le manuel ?

C'est une question differente de celle du rattachement. Le rattachement demande
si les capacites internes du projet sont correctement raccrochees au BO ; il se
juge sur des referentiels. Celle-ci demande si l'eleve trouve, dans le manuel,
de quoi apprendre ce que le programme exige ; elle se juge sur les OBJETS --
un paragraphe de cours, une demonstration redigee, un exercice, une evaluation.

Un attendu officiel n'a pas besoin d'un atome interne pour etre couvert. Les
referentiels du projet encodent surtout des capacites ; une connaissance peut
etre parfaitement traitee dans un fichier de cours sans avoir jamais recu de
code C*. Exiger un atome par attendu ferait apparaitre comme manquant ce qui
est enseigne, et pousserait a fabriquer des centaines d'atomes vides pour
faire tomber un compteur.

La preuve emprunte donc deux chemins, tous deux publies :

  DECLARED_CAPACITY  l'objet declare la capacite, elle-meme rattachee au BO ;
  CONTENT_MATCH      aucun atome ne porte l'attendu, mais un objet d'un
                     chapitre qui traite cette partie du programme en contient
                     les termes. Le rapprochement est publie avec les termes
                     trouves et ceux qui manquent.

Le verdict depend de la NATURE de l'attendu, pas d'un pourcentage global. Une
demonstration exigible n'est pas couverte par un exercice qui utilise le
resultat : il faut que la preuve soit ecrite. Un automatisme n'est pas couvert
par une seule lecon : le programme demande qu'il soit entretenu sur l'annee.
Un exemple d'algorithme demande un travail algorithmique, pas la copie de cet
exemple-la.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

from manual_objects import (
    Objet,
    charger_contrats,
    charger_objets,
    charger_transversaux,
)
from programme_normativity import (
    EXPECTED_CAPACITY,
    PRESCRIBED_ALGORITHMIC_WORK,
    REQUIRED_AUTOMATISM,
    REQUIRED_CONTENT,
    REQUIRED_DEMONSTRATION,
    TRANSVERSAL_REQUIREMENT,
)

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "audit" / "OFFICIAL_PROGRAMME_INVENTORY.json"
BINDING = ROOT / "audit" / "OFFICIAL_PROGRAMME_BINDING.json"
OUT = ROOT / "audit" / "OFFICIAL_TO_MANUAL_COVERAGE.json"

#: Un automatisme se travaille sur l'annee : le BO ecrit qu'il n'a « pas
#: vocation a faire l'objet d'un chapitre d'enseignement specifique ». Le
#: trouver dans un seul chapitre ne suffit donc pas a le dire entretenu.
CHAPITRES_MINIMAUX_POUR_UN_AUTOMATISME = 2
#: Rapprochement par contenu : part des mots distinctifs qu'un objet doit
#: contenir, et nombre minimal exige. Le plafond compte autant que la part :
#: sans lui, un attendu enonce en une longue phrase -- « Lire un graphique, un
#: histogramme, un diagramme en barres ou circulaire, un diagramme en boite ou
#: toute autre representation... » -- devenait introuvable parce qu'aucun
#: objet ne reprend seize mots sur seize.
PART_DE_TERMES_REQUISE = 0.5
TERMES_MINIMAUX = 2
TERMES_SUFFISANTS = 4
#: Mots trop repandus dans un manuel de mathematiques pour distinguer quoi que
#: ce soit. Les garder ferait « trouver » n'importe quel attendu partout.
BANALS = {
    "fonction", "fonctions", "calcul", "calculer", "nombre", "nombres",
    "utiliser", "determiner", "exemple", "exemples", "probleme", "problemes",
    "point", "points", "valeur", "valeurs", "forme", "cas", "deux", "donnee",
    "donnees", "resoudre", "etudier", "connaitre", "partir", "ensemble",
}


def _sans_accents(texte: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKD", texte) if not unicodedata.combining(c)
    )


def termes_distinctifs(libelle: str) -> set[str]:
    mots = re.findall(r"[a-z0-9]+", _sans_accents(libelle).lower())
    return {m for m in mots if len(m) >= 5 and m not in BANALS}


def _slug_preambule(intitule: str) -> str:
    """Forme d'identifiant utilisee par les objets pour citer le preambule."""
    return re.sub(
        r"[^A-Z0-9]+", "-", _sans_accents(intitule).upper()
    ).strip("-")


def racine(terme: str) -> str:
    """Radical grossier, pour ne pas dependre des flexions.

    Le programme ecrit « Expressions booleennes » la ou le cours ecrit « une
    expression booleenne » : chercher la forme exacte declarait absent un
    contenu present. Deux caracteres de moins suffisent a franchir la plupart
    des accords, sans confondre des notions distinctes.
    """
    return terme[: max(5, len(terme) - 2)]


def charger_lignes_officielles() -> dict[str, list[str]]:
    """Pour chaque attendu, les autres attendus de SA ligne du tableau.

    Le BO de NSI place sur une meme ligne un contenu, les capacites qui le
    mettent en oeuvre et les commentaires qui l'eclairent. C'est une unite
    reglementaire, pas trois enonces voisins.
    """
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    voisins: dict[str, list[str]] = {}
    for entree in index["documents"]:
        charge = json.loads((ROOT / entree["inventory_path"]).read_text(encoding="utf-8"))
        for ligne in charge.get("row_bindings", []):
            tous = (
                ligne["content_items"]
                + ligne["capacity_items"]
                + ligne["commentary_items"]
            )
            for oid in tous:
                voisins[oid] = [autre for autre in tous if autre != oid]
    return voisins


def charger_officiels() -> tuple[list[dict[str, Any]], dict[str, str]]:
    index = json.loads(INDEX.read_text(encoding="utf-8"))
    items: list[dict[str, Any]] = []
    autorites: dict[str, str] = {}
    for entree in index["documents"]:
        if not entree["applies_to_edition"]:
            continue
        autorites[entree["manual"]] = entree["authority_ref"]
        charge = json.loads((ROOT / entree["inventory_path"]).read_text(encoding="utf-8"))
        items.extend(charge["items"])
    return items, autorites


def verdict(
    normativity: str,
    roles: Counter[str],
    chapitres_de_reinvestissement: set[str],
    demonstration_redigee: bool,
    travail_algorithmique: bool,
    travail_algorithmique_de_la_partie: bool = False,
    exemple_impose: bool = True,
) -> tuple[str, str]:
    """Verdict et motif, selon ce que la nature de l'attendu exige reellement."""
    enseigne = roles.get("PRIMARY_TEACHING", 0) > 0
    appuye = roles.get("SUPPORTING_EVIDENCE", 0) > 0
    pratique = roles.get("REINVESTMENT", 0) > 0
    evalue = roles.get("ASSESSMENT", 0) > 0
    rien = not any(roles.values())

    if normativity == TRANSVERSAL_REQUIREMENT:
        # Le manuel ne peut pas prouver qu'un etablissement consacrera un quart
        # de l'horaire aux projets, ni que les professeurs veilleront a leur
        # ambition. Declarer ces phrases « couvertes » ou « manquantes » serait
        # deux fois faux : elles ne s'adressent pas au manuel. Ce qui se juge
        # ici est le SOUTIEN qu'il apporte.
        return (
            "INSTITUTIONAL_IMPLEMENTATION_REQUIREMENT",
            (
                "le manuel fournit de quoi conduire cette exigence"
                if (roles.get("PRIMARY_TEACHING", 0) or roles.get("SUPPORTING_EVIDENCE", 0))
                else "aucun objet du manuel n'outille cette exigence"
            ),
        )
        # Un manuel ne peut pas prouver qu'un etablissement consacrera
        # reellement un quart de l'horaire aux projets. Il peut fournir de
        # quoi les conduire ; le declarer « satisfait par le livre » serait
        # une fausse preuve.
        if rien:
            return "MISSING", "aucun objet du manuel n'outille cette exigence"
        if enseigne or appuye:
            return (
                "MANUAL_SUPPORT_PRESENT",
                "le manuel fournit de quoi conduire cette exigence ; sa mise "
                "en oeuvre effective releve de l'etablissement et n'est pas "
                "certifiable par un manuel",
            )
        return "PARTIAL", "objets presents, mais aucun support d'enseignement"

    if normativity == PRESCRIBED_ALGORITHMIC_WORK and not exemple_impose:
        # Le BO intitule cette rubrique « Exemples d'algorithme ». Ce qu'il
        # prescrit est un travail algorithmique sur la partie concernee ; il
        # ne demande pas que ce soit CET algorithme-la. Exiger l'exemple cite
        # transformerait une illustration en obligation que le texte ne porte
        # pas -- et declarerait manquant un chapitre qui fait le travail
        # autrement.
        if travail_algorithmique:
            return (
                "COMPLETE",
                "l'exemple cite par le programme est lui-meme traite",
            )
        if travail_algorithmique_de_la_partie:
            return (
                "COMPLETE",
                "le travail algorithmique prescrit est present dans la partie "
                "concernee ; le programme nomme un exemple, il ne l'impose pas",
            )
        return (
            "MISSING",
            "aucun travail algorithmique dans la partie concernee",
        )

    if rien:
        return "MISSING", "aucun objet du manuel ne porte cet attendu"

    if normativity == REQUIRED_DEMONSTRATION:
        if demonstration_redigee:
            return "COMPLETE", "la demonstration est redigee dans un objet du manuel"
        return (
            "PARTIAL",
            "des objets portent cet attendu, mais aucun ne contient de "
            "demonstration redigee : le nom d'un theoreme ne demontre rien",
        )

    if normativity == PRESCRIBED_ALGORITHMIC_WORK:
        if travail_algorithmique:
            return "COMPLETE", "un objet porte un travail algorithmique effectif"
        return (
            "PARTIAL",
            "des objets portent cet attendu, mais aucun ne comporte "
            "d'algorithme ni de programme",
        )

    if normativity == REQUIRED_AUTOMATISM:
        if len(chapitres_de_reinvestissement) >= CHAPITRES_MINIMAUX_POUR_UN_AUTOMATISME:
            return (
                "COMPLETE",
                f"entretenu dans {len(chapitres_de_reinvestissement)} chapitres",
            )
        return (
            "PARTIAL",
            "present mais concentre : le programme demande un entretien "
            "reparti sur l'annee, pas une lecon isolee",
        )

    if normativity == REQUIRED_CONTENT:
        if enseigne:
            return "COMPLETE", "traite dans un objet de cours"
        return (
            "PARTIAL",
            "aborde par des objets du manuel, mais aucun cours ne l'expose",
        )

    if normativity == EXPECTED_CAPACITY:
        if enseigne and (pratique or appuye):
            return "COMPLETE", "enseigne et mis en pratique"
        if enseigne:
            return "PARTIAL", "enseigne, mais sans exercice ni methode"
        if pratique or appuye or evalue:
            return "PARTIAL", "pratique ou evalue, mais jamais enseigne"
        return "PARTIAL", "objets presents, roles insuffisants"

    return "OUT_OF_SCOPE_ENRICHMENT", "attendu non obligatoire"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)

    items, autorites = charger_officiels()
    voisins_de_ligne = charger_lignes_officielles()
    par_official_id = {i["official_id"]: i for i in items}
    liaison = json.loads(BINDING.read_text(encoding="utf-8"))
    contrats = charger_contrats()
    objets = charger_objets(contrats) + charger_transversaux()

    # atome -> objets qui le servent
    par_atome: dict[str, list[Objet]] = defaultdict(list)
    for objet in objets:
        for atome in objet.atoms:
            par_atome[atome].append(objet)

    # Certains objets citent une capacite du preambule sous la forme
    # « BO-PREAMBULE-DEMARCHE-DE-PROJET ». Cet identifiant n'existe dans aucun
    # referentiel, mais il nomme sans ambiguite une partie du preambule que
    # l'inventaire officiel porte. Le resoudre evite de laisser sans preuve
    # une exigence que le manuel outille reellement.
    objets_par_partie_de_preambule: dict[tuple[str, str], list[Objet]] = defaultdict(
        list
    )
    for objet in objets:
        for atome in objet.atoms:
            if atome.startswith("BO-PREAMBULE-"):
                objets_par_partie_de_preambule[
                    (objet.manual, atome.removeprefix("BO-PREAMBULE-"))
                ].append(objet)

    # attendu officiel -> atomes rattaches de facon etablie
    atomes_par_item: dict[str, list[str]] = defaultdict(list)
    for lien in liaison["bindings"]:
        if lien["binding_method"] not in ("ANCHOR", "VERBATIM", "CONTEXT"):
            continue
        for oid in lien.get("official_ids") or [lien["official_id"]]:
            atomes_par_item[oid].append(lien["atom_id"])

    # partie officielle -> chapitres qui la traitent (via la portee des themes)
    chapitres_par_partie: dict[tuple[str, str], set[str]] = defaultdict(set)
    theme_de_chapitre = {c.chapter: (c.manual, c.theme) for c in contrats.values()}
    portee_de_theme: dict[tuple[str, str], list[str]] = {}
    for lien in liaison["bindings"]:
        if lien.get("theme_scope"):
            portee_de_theme[(lien["manual"], lien["theme"])] = lien["theme_scope"]["scopes"]
    for chapitre, (manuel, theme) in theme_de_chapitre.items():
        for partie in portee_de_theme.get((manuel, theme), []):
            chapitres_par_partie[(manuel, partie)].add(chapitre)

    # Une partie du programme fait-elle l'objet d'un travail algorithmique,
    # quel qu'en soit l'exemple ?
    algorithmique_par_partie: dict[tuple[str, str], bool] = {}
    objets_algorithmiques_par_partie: dict[tuple[str, str], list[Objet]] = {}
    objets_par_chapitre_tmp: dict[str, list[Objet]] = defaultdict(list)
    for objet in objets:
        objets_par_chapitre_tmp[objet.chapter].append(objet)
    for (manuel_p, partie), chapitres_p in chapitres_par_partie.items():
        trouves = [
            o
            for chap in sorted(chapitres_p)
            for o in objets_par_chapitre_tmp.get(chap, [])
            if o.has_algorithmic_work
        ]
        algorithmique_par_partie[(manuel_p, partie)] = bool(trouves)
        objets_algorithmiques_par_partie[(manuel_p, partie)] = trouves

    objets_par_chapitre: dict[str, list[Objet]] = defaultdict(list)
    for objet in objets:
        objets_par_chapitre[objet.chapter].append(objet)
    textes: dict[str, str] = {}

    lignes: list[dict[str, Any]] = []
    for item in items:
        manuel = item["manual"]
        atomes = sorted(set(atomes_par_item.get(item["official_id"], [])))
        servants: dict[str, Objet] = {}
        for atome in atomes:
            for objet in par_atome.get(atome, []):
                servants[objet.object_id] = objet
        if item["official_section"] == "Préambule":
            cle_partie = _slug_preambule(item["official_subsection"] or "")
            for objet in objets_par_partie_de_preambule.get((manuel, cle_partie), []):
                servants[objet.object_id] = objet

        preuve = "DECLARED_CAPACITY" if servants else None
        termes_trouves: list[str] = []
        termes_absents: list[str] = []

        if not servants and voisins_de_ligne.get(item["official_id"]):
            # Preuve par la ligne officielle. Un objet qui prouve une capacite
            # soeur ne prouve PAS le contenu par heritage : il faut que son
            # corps traite reellement le sujet de la ligne. Le vocabulaire
            # examine est celui de la ligne entiere -- contenu, capacites,
            # commentaires --, parce que c'est ce que le BO y a mis ensemble.
            vocabulaire: set[str] = set()
            for autre in [item["official_id"], *voisins_de_ligne[item["official_id"]]]:
                voisin = par_official_id.get(autre)
                if voisin is not None:
                    vocabulaire |= termes_distinctifs(voisin["official_wording"])
            seuil_ligne = min(
                len(vocabulaire),
                TERMES_SUFFISANTS,
                max(TERMES_MINIMAUX, math.ceil(len(vocabulaire) * PART_DE_TERMES_REQUISE)),
            ) if vocabulaire else 0
            candidats: dict[str, Objet] = {}
            for autre in voisins_de_ligne[item["official_id"]]:
                for atome_voisin in atomes_par_item.get(autre, []):
                    for objet in par_atome.get(atome_voisin, []):
                        candidats[objet.object_id] = objet
            for objet in candidats.values():
                texte = textes.get(objet.path)
                if texte is None:
                    texte = _sans_accents(
                        (ROOT / objet.path).read_text(encoding="utf-8", errors="replace")
                    ).lower()
                    textes[objet.path] = texte
                presents = [t for t in vocabulaire if racine(t) in texte]
                if seuil_ligne and len(presents) >= seuil_ligne:
                    servants[objet.object_id] = objet
                    termes_trouves = sorted(set(termes_trouves) | set(presents))
            if servants:
                preuve = "OFFICIAL_ROW_EVIDENCE"
                termes_absents = sorted(vocabulaire - set(termes_trouves))


        if not servants:
            # Aucun atome ne porte cet attendu : on cherche dans les chapitres
            # qui traitent cette partie du programme. La recherche est bornee
            # par la portee -- sans cela, un mot suffisamment courant
            # « trouverait » l'attendu dans n'importe quel chapitre.
            partie = item["official_subsection"] or item["official_section"] or ""
            termes = termes_distinctifs(item["official_wording"])
            # Quand aucun chapitre ne se rattache a cette partie, la recherche
            # s'etend a tout le manuel. C'est le cas des automatismes, que le
            # programme veut justement repartis et qui n'ont donc pas de
            # chapitre a eux : borner la recherche a une portee inexistante
            # revenait a ne rien chercher, et a declarer manquant ce qui est
            # peut-etre travaille partout.
            # Le seuil est borne par le nombre de termes disponibles : un
            # attendu qui n'en compte que deux doit pouvoir etre trouve, et
            # exiger un minimum absolu le rendait introuvable par principe.
            # Le seuil est borne par le nombre de termes disponibles : un
            # attendu qui n'en compte que deux doit pouvoir etre trouve, et un
            # minimum absolu le rendait introuvable par principe. Il est aussi
            # plafonne : un attendu enonce en seize mots ne peut pas exiger
            # seize concordances. Entre les deux, la moitie des termes -- deux
            # sur cinq laissaient passer « Demi-vie d'un echantillon de grande
            # taille d'atomes radioactifs » sur les seuls mots « echantillon »,
            # « grande » et « taille ».
            exigence = min(
                len(termes),
                TERMES_SUFFISANTS,
                max(TERMES_MINIMAUX, math.ceil(len(termes) * PART_DE_TERMES_REQUISE)),
            ) if termes else 0
            portee_connue = chapitres_par_partie.get((manuel, partie))
            tous = sorted(
                {c for c, (m, _) in theme_de_chapitre.items() if m == manuel}
                | {o.chapter for o in objets if o.manual == manuel}
            )
            # On cherche d'abord la ou l'attendu devrait etre, puis, si rien
            # n'y repond, dans tout le manuel. Une notion enoncee dans une
            # partie est souvent enseignee dans une autre -- « Limites de
            # suites » figure parmi les contenus mobilises par le theme
            # « Calculs d'aires » mais s'enseigne ailleurs --, et s'arreter a
            # la premiere recherche la declarait absente du manuel entier.
            passes = (
                [(sorted(portee_connue), "CONTENT_MATCH"), (tous, "CONTENT_MATCH_MANUAL_WIDE")]
                if portee_connue
                else [(tous, "CONTENT_MATCH_MANUAL_WIDE")]
            )
            if termes:
                for a_fouiller, etiquette in passes:
                    for chapitre in a_fouiller:
                        for objet in objets_par_chapitre.get(chapitre, []):
                            texte = textes.get(objet.path)
                            if texte is None:
                                texte = _sans_accents(
                                    (ROOT / objet.path).read_text(
                                        encoding="utf-8", errors="replace"
                                    )
                                ).lower()
                                textes[objet.path] = texte
                            presents = [t for t in termes if racine(t) in texte]
                            if len(presents) >= exigence:
                                servants[objet.object_id] = objet
                                termes_trouves = sorted(
                                    set(termes_trouves) | set(presents)
                                )
                    if servants:
                        preuve = etiquette
                        termes_absents = sorted(termes - set(termes_trouves))
                        break
                else:
                    termes_absents = sorted(termes)

        # Quand la prescription algorithmique est satisfaite par le travail
        # de la partie plutot que par l'exemple cite, ce sont ces objets-la qui
        # en portent la preuve : sans eux, la matrice affirmerait une
        # couverture sans designer ce qui la couvre.
        if (
            not servants
            and item["official_normativity"] == "PRESCRIBED_ALGORITHMIC_WORK"
            and not item.get("exact_example_imposed", True)
        ):
            partie_item = item["official_subsection"] or item["official_section"] or ""
            appuis = objets_algorithmiques_par_partie.get((manuel, partie_item), [])
            if appuis:
                servants = {o.object_id: o for o in appuis}
                preuve = "ALGORITHMIC_WORK_IN_THE_SAME_PART"

        indecidable = (
            not servants
            and not atomes
            and not termes_distinctifs(item["official_wording"])
        )
        roles: Counter[str] = Counter(o.role for o in servants.values())
        chapitres = {o.chapter for o in servants.values()}
        reinvestissement = {
            o.chapter for o in servants.values()
            if o.role in ("REINVESTMENT", "ASSESSMENT", "SUPPORTING_EVIDENCE")
        }
        if indecidable:
            # Le libelle ne porte aucun mot distinctif : « Calcul de cos , sin
            # , cos , sin . 4 4 3 3 », ou la notation mathematique n'a pas
            # survecu a l'extraction. Declarer l'attendu absent serait affirmer
            # ce qu'on n'a pas pu chercher.
            statut, motif = (
                "UNDECIDABLE_BY_CONTENT_MATCH",
                "aucun mot distinctif dans le libelle officiel : la recherche "
                "par contenu ne peut ni conclure a la presence ni conclure a "
                "l'absence",
            )
        else:
            statut, motif = verdict(
                item["official_normativity"],
                roles,
                reinvestissement,
                any(o.has_written_proof for o in servants.values()),
                any(o.has_algorithmic_work for o in servants.values()),
                travail_algorithmique_de_la_partie=algorithmique_par_partie.get(
                    (
                        manuel,
                        item["official_subsection"] or item["official_section"] or "",
                    ),
                    False,
                ),
                exemple_impose=item.get("exact_example_imposed", True),
            )
        lignes.append({
            "official_id": item["official_id"],
            "manual": manuel,
            "authority_ref": autorites.get(manuel),
            "official_section": item["official_section"],
            "official_subsection": item["official_subsection"],
            "official_heading": item["official_heading"],
            "official_wording": item["official_wording"],
            "official_normativity": item["official_normativity"],
            "mandatory": item["mandatory"],
            "internal_atoms": atomes,
            "evidence_kind": preuve,
            "matched_terms": termes_trouves,
            "missing_terms": termes_absents,
            "chapters": sorted(chapitres),
            "objects_by_role": {
                role: sorted(
                    o.object_id for o in servants.values() if o.role == role
                )
                for role in sorted(roles)
            },
            "object_count": len(servants),
            "coverage_status": statut,
            "coverage_reason": motif,
        })

    obligatoires = [r for r in lignes if r["mandatory"]]
    par_manuel: dict[str, Any] = {}
    for manuel in sorted({r["manual"] for r in lignes}):
        du_manuel = [r for r in obligatoires if r["manual"] == manuel]
        par_nature: dict[str, dict[str, int]] = {}
        for ligne in du_manuel:
            stat = par_nature.setdefault(
                ligne["official_normativity"],
                {"COMPLETE": 0, "PARTIAL": 0, "MISSING": 0, "MANUAL_SUPPORT_PRESENT": 0},
            )
            stat[ligne["coverage_status"]] = stat.get(ligne["coverage_status"], 0) + 1
        par_manuel[manuel] = {
            "authority_ref": autorites[manuel],
            "mandatory_items": len(du_manuel),
            "by_normativity": dict(sorted(par_nature.items())),
        }

    # Exigence de qualite propre a la collection, distincte du programme. Le BO
    # nomme des « Exemples d'algorithme » sans les imposer : ils ne comptent
    # donc pas au denominateur des obligations. Mais une partie du programme
    # que ces exemples accompagnent doit, dans un bon manuel, offrir un travail
    # algorithmique reel -- et cela se controle a part, sous son propre nom,
    # pour qu'aucune exigence maison ne passe pour une exigence ministerielle.
    parties_avec_exemples: dict[tuple[str, str], list[str]] = defaultdict(list)
    for item in items:
        if item["local_kind"] == "ALGORITHM_EXAMPLE":
            parties_avec_exemples[
                (
                    item["manual"],
                    item["official_subsection"] or item["official_section"] or "",
                )
            ].append(item["official_id"])
    qualite_algorithmique = [
        {
            "manual": manuel,
            "official_part": partie,
            "algorithm_examples_cited_by_the_programme": len(ids),
            "manual_has_algorithmic_work": bool(
                algorithmique_par_partie.get((manuel, partie))
            ),
            "standard": "NEXUS_ALGORITHMIC_QUALITY_STANDARD",
        }
        for (manuel, partie), ids in sorted(parties_avec_exemples.items())
    ]

    resume = {
        "OFFICIAL_REQUIRED_COMPLETE": sum(
            1 for r in obligatoires if r["coverage_status"] == "COMPLETE"
        ),
        "OFFICIAL_REQUIRED_PARTIAL": sum(
            1 for r in obligatoires if r["coverage_status"] == "PARTIAL"
        ),
        "OFFICIAL_REQUIRED_MISSING": sum(
            1 for r in obligatoires if r["coverage_status"] == "MISSING"
        ),
        "OFFICIAL_REQUIRED_INSTITUTIONAL": sum(
            1 for r in obligatoires
            if r["coverage_status"] == "INSTITUTIONAL_IMPLEMENTATION_REQUIREMENT"
        ),
        "OFFICIAL_REQUIRED_UNDECIDABLE_BY_CONTENT_MATCH": sum(
            1 for r in obligatoires
            if r["coverage_status"] == "UNDECIDABLE_BY_CONTENT_MATCH"
        ),
        "mandatory_items": len(obligatoires),
        "evidence_by_declared_capacity": sum(
            1 for r in obligatoires if r["evidence_kind"] == "DECLARED_CAPACITY"
        ),
        "evidence_by_content_match": sum(
            1 for r in obligatoires if r["evidence_kind"] == "CONTENT_MATCH"
        ),
        "evidence_by_content_match_manual_wide": sum(
            1 for r in obligatoires
            if r["evidence_kind"] == "CONTENT_MATCH_MANUAL_WIDE"
        ),
        "objects_indexed": len(objets),
        "statuses_cover_every_mandatory_item": True,
        "NEXUS_ALGORITHMIC_QUALITY_PARTS": len(qualite_algorithmique),
        "NEXUS_ALGORITHMIC_QUALITY_PARTS_WITHOUT_WORK": sum(
            1 for q in qualite_algorithmique if not q["manual_has_algorithmic_work"]
        ),
    }
    assert (
        resume["OFFICIAL_REQUIRED_COMPLETE"]
        + resume["OFFICIAL_REQUIRED_PARTIAL"]
        + resume["OFFICIAL_REQUIRED_MISSING"]
        + resume["OFFICIAL_REQUIRED_INSTITUTIONAL"]
        + resume["OFFICIAL_REQUIRED_UNDECIDABLE_BY_CONTENT_MATCH"]
        == resume["mandatory_items"]
    ), "un attendu obligatoire sans statut echapperait au compte"

    charge = {
        "artifact_type": "official_to_manual_coverage",
        "schema_version": 1,
        "generated_by": "scripts/build_official_to_manual_coverage.py",
        "question": (
            "Chaque exigence officielle obligatoire est-elle reellement "
            "enseignee dans le manuel ?"
        ),
        "evidence_kinds": {
            "DECLARED_CAPACITY": "l'objet declare une capacite rattachee au BO",
            "CONTENT_MATCH": (
                "aucun atome ne porte l'attendu ; un objet d'un chapitre qui "
                "traite cette partie du programme en contient les termes"
            ),
            "ALGORITHMIC_WORK_IN_THE_SAME_PART": (
                "le programme nomme un exemple d'algorithme sans l'imposer ; "
                "la partie concernee comporte un travail algorithmique, porte "
                "par les objets listes"
            ),
            "OFFICIAL_ROW_EVIDENCE": (
                "un objet qui prouve une capacite de la MEME LIGNE du tableau "
                "officiel traite materiellement le sujet de cette ligne. Le BO "
                "y place ensemble un contenu et les capacites qui le mettent en "
                "oeuvre : les traiter separement fait declarer absent un "
                "contenu que le cours d'a cote enseigne. Ce n'est pas un "
                "heritage : le corps de l'objet doit porter le vocabulaire de "
                "la ligne."
            ),
            "CONTENT_MATCH_MANUAL_WIDE": (
                "aucun chapitre ne se rattache a cette partie du programme : "
                "la recherche a porte sur tout le manuel. C'est le cas des "
                "automatismes, que le programme veut repartis et qui n'ont "
                "donc pas de chapitre a eux"
            ),
        },
        "summary": resume,
        "per_manual": par_manuel,
        "nexus_algorithmic_quality_standard": {
            "nature": (
                "exigence de qualite de la collection, PAS une obligation du "
                "programme : le BO nomme des exemples d'algorithme sans les "
                "imposer. Ce controle verifie qu'une partie accompagnee de tels "
                "exemples comporte bien un travail algorithmique dans le manuel."
            ),
            "parts": qualite_algorithmique,
        },
        "rows": lignes,
    }
    texte = json.dumps(charge, ensure_ascii=False, indent=2) + "\n"
    if args.check:
        if not OUT.exists() or OUT.read_text(encoding="utf-8") != texte:
            print(f"DIVERGENT : {OUT.relative_to(ROOT)}")
            return 1
        print("Matrice de couverture conforme au generateur.")
        return 0
    OUT.write_text(texte, encoding="utf-8")

    for manuel, detail in par_manuel.items():
        print(f"\n{manuel} ({detail['authority_ref']}) — "
              f"{detail['mandatory_items']} attendus obligatoires")
        for nature, stat in detail["by_normativity"].items():
            morceaux = " ".join(
                f"{cle}={val}" for cle, val in stat.items() if val
            )
            print(f"   {nature:<30s} {morceaux}")
    print()
    for cle, valeur in resume.items():
        print(f"{cle} = {valeur}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
