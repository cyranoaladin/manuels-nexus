#!/usr/bin/env python3
"""Index des objets pedagogiques reellement presents dans les manuels.

La couverture d'un programme ne se prouve pas dans un referentiel : elle se
prouve dans les objets que l'eleve a sous les yeux -- un paragraphe de cours,
un exercice, une demonstration, une evaluation. Ce module les recense et
retablit, pour chacun, les capacites internes qu'il sert.

Deux chemins mènent d'un objet a une capacite, et les deux sont lus :

  `capacites`        l'objet nomme directement les atomes du referentiel ;
  `capacites_codes`  il nomme les codes de son chapitre (C1, C2...), qu'il
                     faut resoudre dans le contrat du chapitre.

Le second chemin est le plus repandu et le seul disponible pour beaucoup
d'objets : l'ignorer priverait de preuve la majorite du manuel.
"""
from __future__ import annotations

import json
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
RACINES = ("Mathematiques/manuel-maths/chapitres", "NSI/chapitres")
META = re.compile(r"^%\s*META:\s*(\{.*\})\s*$", re.M)

#: Role pedagogique par type d'objet. Un meme attendu officiel peut etre
#: enseigne a un endroit et reinvesti ailleurs : distinguer les roles evite de
#: compter dix exercices comme un enseignement, et un unique paragraphe de
#: cours comme un entrainement.
ROLES: dict[str, str] = {
    "cours": "PRIMARY_TEACHING",
    "methode": "SUPPORTING_EVIDENCE",
    "algorithme": "SUPPORTING_EVIDENCE",
    "experimentation": "SUPPORTING_EVIDENCE",
    "td": "SUPPORTING_EVIDENCE",
    "projet": "SUPPORTING_EVIDENCE",
    "exercice": "REINVESTMENT",
    "corrige": "REINVESTMENT",
    "coup_de_pouce": "REINVESTMENT",
    "qcm": "ASSESSMENT",
    "qcm_diagnostics": "ASSESSMENT",
    "evaluation": "ASSESSMENT",
    "corrige_evaluation": "ASSESSMENT",
    "banque_ecrite": "ASSESSMENT",
    "banque_pratique": "ASSESSMENT",
    "remediation": "REMEDIATION",
    "amenagee": "REMEDIATION",
}


#: Pages transversales et manuels qui les integrent, tels que l'assembleur les
#: monte (`Mathematiques/manuel-maths/scripts/assemble_manuel.py`). Elles ne
#: vivent pas dans `chapitres/` et n'ont pas d'en-tete META, mais elles portent
#: du contenu que le programme exige : le vocabulaire ensembliste et logique,
#: les automatismes statistiques, le memo Python. Les ignorer faisait declarer
#: absents des attendus qui sont enseignes en annexe -- « formuler la
#: reciproque d'une implication, la contraposee » en est l'exemple exact.
TRANSVERSAUX: dict[str, tuple[str, ...]] = {
    "1SPE": (
        "transversal/formulaire.tex",
        "transversal/logique_raisonnement.tex",
        "transversal/statistiques_automatismes.tex",
        "transversal/memo_python.tex",
    ),
    "TSPE": (
        "transversal/logique_raisonnement.tex",
        "transversal/memo_python.tex",
    ),
    "TCOMPL": (
        "transversal/logique_raisonnement.tex",
        "transversal/memo_python.tex",
    ),
}
RACINE_MATHS = "Mathematiques/manuel-maths"


@dataclass
class Objet:
    object_id: str
    chapter: str
    manual: str
    kind: str
    role: str
    path: str
    atoms: tuple[str, ...] = ()
    codes: tuple[str, ...] = ()
    #: Presence d'une demonstration redigee dans le corps de l'objet. Une
    #: demonstration exigible ne peut pas etre prouvee par le seul nom d'un
    #: theoreme ; il faut que la preuve soit ecrite quelque part.
    has_written_proof: bool = False
    #: Presence d'un travail algorithmique effectif (algorithme, programme).
    has_algorithmic_work: bool = False
    #: L'objet enonce-t-il ce que l'algorithme prend en entree et rend en
    #: sortie, ou le probleme qu'il resout ? Un bloc de code sans objectif
    #: enonce ne se travaille pas : il se recopie.
    algorithmic_objective: bool = False
    #: L'objet demande-t-il quelque chose a l'eleve -- une demarche a suivre,
    #: un travail a faire ? Un algorithme qu'on ne fait qu'admirer n'est pas
    #: un travail algorithmique.
    algorithmic_activity: bool = False
    #: ... et si un travail est demande, la reponse est-elle donnee ?
    algorithmic_answers: bool = False
    #: Une tache est-elle explicitement demandee ? Elle seule appelle une
    #: correction.
    algorithmic_task: bool = False
    #: L'objet publie-t-il du code Python ? Ce cas exige un oracle executable.
    publishes_python: bool = False
    #: Presence d'un oracle executable. Un programme publie sans verification
    #: n'engage personne.
    has_executable_oracle: bool = False
    #: Presence d'un algorithme MONTRE A L'ELEVE. La distinction n'est pas
    #: cosmetique : un bloc « BEGIN-VERIFY » est un controle interne que le
    #: lecteur ne voit jamais, et presque tous les corriges en portent un. Les
    #: compter comme travail algorithmique rendait la mesure vide -- trois
    #: mille objets sur trois mille cinq cents « faisaient de l'algorithmique »
    #: --, et permettait a n'importe quelle partie du programme de paraitre
    #: servie par un algorithme qu'elle n'expose pas.
    shows_algorithmic_work: bool = False
    text_length: int = 0
    #: Chemin du corrige declare par un exercice. Un corrige ne redeclare pas
    #: toujours les capacites de son exercice : sans ce lien, il apparaitrait
    #: comme un objet sans rattachement alors qu'il sert exactement le meme
    #: attendu.
    linked_correction: str = ""
    #: Alignement declare par l'objet lui-meme. Certains objets s'annoncent
    #: « OPTIONAL_EXTENSION — Approfondissement, vers la Terminale » : ils ne
    #: relevent pas du programme de l'annee et le disent. Ignorer cette
    #: declaration les faisait passer pour des objets sans justification.
    #: Presence d'exemples travailles dans le corps de l'objet. Un attendu
    #: n'a pas besoin d'une fiche methode pour etre mis en pratique : il a
    #: besoin d'un entrainement adapte, et un exemple redige en est un. Les
    #: pages transversales du manuel en portent seize pour la seule logique,
    #: sans aucun exercice separe.
    has_worked_examples: bool = False
    #: Prerequis que l'objet remet en place, declares par lui-meme. Le lien
    #: est structurel : le chercher par les mots du libelle faisait manquer
    #: une fiche intitulee « Calcul litteral » pour un prerequis nomme
    #: « Calcul litteral : mise en equation, resolution ».
    prerequis_testes: tuple[str, ...] = ()
    programme_alignment: str = ""
    extension_label: str = ""


@dataclass
class Contrat:
    chapter: str
    manual: str
    theme: str
    #: code local -> identifiant d'atome du referentiel
    aliases: dict[str, str] = field(default_factory=dict)
    #: codes declares sans alias officiel, avec la facette qu'ils portent
    facettes: dict[str, dict[str, Any]] = field(default_factory=dict)


def fichiers_suivis(motif: str) -> list[Path]:
    sortie = subprocess.run(
        ["git", "ls-files", "--", *RACINES],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.split("\n")
    return [ROOT / f for f in sortie if f.endswith(motif)]


def charger_contrats() -> dict[str, Contrat]:
    contrats: dict[str, Contrat] = {}
    for chemin in fichiers_suivis("contrat.yaml"):
        charge = yaml.safe_load(chemin.read_text(encoding="utf-8")) or {}
        contrat = Contrat(
            chapter=charge.get("chapitre", chemin.parent.name),
            manual=charge.get("niveau", ""),
            theme=charge.get("theme", ""),
        )
        for capacite in charge.get("capacites", []) or []:
            code = capacite.get("code")
            if not code:
                continue
            if capacite.get("ref_capacite"):
                contrat.aliases[code] = capacite["ref_capacite"]
            elif capacite.get("sans_alias_officiel"):
                contrat.facettes[code] = capacite["sans_alias_officiel"]
        contrats[contrat.chapter] = contrat
    return contrats


def charger_objets(contrats: dict[str, Contrat]) -> list[Objet]:
    objets: list[Objet] = []
    for chemin in fichiers_suivis(".tex"):
        texte = chemin.read_text(encoding="utf-8", errors="replace")
        trouve = META.search(texte)
        if not trouve:
            continue
        try:
            meta = json.loads(trouve.group(1))
        except json.JSONDecodeError:
            continue
        chapitre = meta.get("chapitre") or chemin.parents[1].name
        contrat = contrats.get(chapitre)
        codes = tuple(meta.get("capacites_codes") or ())
        atomes = set(meta.get("capacites") or ())
        if contrat:
            # Un code local ne vaut que par le contrat qui le definit : c'est
            # lui qui dit quelle capacite du referentiel il designe.
            atomes.update(
                contrat.aliases[c] for c in codes if c in contrat.aliases
            )
            # Un code declare « sans alias officiel » travaille une facette
            # d'une capacite portee par un code frere. Le contrat nomme ce
            # frere : l'objet sert donc bien cette capacite officielle, et
            # l'ignorer le faisait passer pour un objet sans rattachement.
            for code in codes:
                facette = contrat.facettes.get(code)
                if not facette:
                    continue
                porteur = facette.get("porte_par")
                if porteur and porteur in contrat.aliases:
                    atomes.add(contrat.aliases[porteur])
        kind = meta.get("type_objet", "?")
        objets.append(
            Objet(
                object_id=meta.get("id", chemin.stem),
                chapter=chapitre,
                manual=(contrat.manual if contrat else "") or _manuel_depuis(chapitre),
                kind=kind,
                role=ROLES.get(kind, "SUPPORTING_EVIDENCE"),
                path=str(chemin.relative_to(ROOT)),
                atoms=tuple(sorted(atomes)),
                codes=codes,
                has_written_proof=_porte_une_demonstration(texte),
                has_algorithmic_work=bool(
                    re.search(
                        r"\\begin\{python\}|\\begin\{algorithme\}|\\lstinputlisting"
                        r"|BEGIN-VERIFY|\\begin\{pseudocode\}",
                        texte,
                    )
                ),
                shows_algorithmic_work=bool(ALGORITHME_MONTRE.search(texte)),
                algorithmic_objective=bool(OBJECTIF_ALGORITHMIQUE.search(texte)),
                algorithmic_activity=bool(ACTIVITE_ALGORITHMIQUE.search(texte)),
                algorithmic_answers=bool(REPONSES_ALGORITHMIQUES.search(texte)),
                algorithmic_task=bool(TACHE_ALGORITHMIQUE.search(texte)),
                publishes_python=bool(CODE_PYTHON.search(texte)),
                has_executable_oracle="% BEGIN-VERIFY" in texte,
                text_length=len(texte),
                has_worked_examples=bool(EXEMPLE_TRAVAILLE.search(texte)),
                linked_correction=meta.get("corrige_tex", "") or "",
                prerequis_testes=tuple(meta.get("prerequis_testes") or ()),
                programme_alignment=meta.get("programme_alignment", "") or "",
                extension_label=meta.get("extension_label", "") or "",
            )
        )
    _propager_aux_corriges(objets)
    return objets


def _propager_aux_corriges(objets: list[Objet]) -> None:
    """Un corrige herite des capacites de l'exercice qui le declare."""
    par_chemin = {o.path: o for o in objets}
    for objet in objets:
        cible = objet.linked_correction
        if not cible or not objet.atoms:
            continue
        for prefixe in ("Mathematiques/manuel-maths/", "NSI/"):
            corrige = par_chemin.get(prefixe + cible)
            if corrige is not None and not corrige.atoms:
                corrige.atoms = objet.atoms
                break


def charger_transversaux() -> list[Objet]:
    """Les pages transversales, rattachees au manuel qui les integre."""
    objets: list[Objet] = []
    for manuel, chemins in TRANSVERSAUX.items():
        for relatif in chemins:
            chemin = ROOT / RACINE_MATHS / relatif
            if not chemin.is_file():
                continue
            texte = chemin.read_text(encoding="utf-8", errors="replace")
            objets.append(
                Objet(
                    object_id=f"{manuel}-TRANSVERSAL-{chemin.stem.upper()}",
                    chapter=f"{manuel}-TRANSVERSAL",
                    manual=manuel,
                    kind="transversal",
                    role="PRIMARY_TEACHING",
                    path=str(chemin.relative_to(ROOT)),
                    has_written_proof=_porte_une_demonstration(texte),
                    has_worked_examples=bool(EXEMPLE_TRAVAILLE.search(texte)),
                    has_algorithmic_work=bool(
                        re.search(r"\\begin\{python\}|\\begin\{algorithme\}", texte)
                    ),
                    shows_algorithmic_work=bool(ALGORITHME_MONTRE.search(texte)),
                    algorithmic_objective=bool(OBJECTIF_ALGORITHMIQUE.search(texte)),
                    algorithmic_activity=bool(ACTIVITE_ALGORITHMIQUE.search(texte)),
                    algorithmic_answers=bool(REPONSES_ALGORITHMIQUES.search(texte)),
                    algorithmic_task=bool(TACHE_ALGORITHMIQUE.search(texte)),
                    publishes_python=bool(CODE_PYTHON.search(texte)),
                    has_executable_oracle="% BEGIN-VERIFY" in texte,
                    text_length=len(texte),
                )
            )
    return objets


#: Marqueurs d'un objectif : entree/sortie annoncees, ou probleme pose.
OBJECTIF_ALGORITHMIQUE = re.compile(
    r"Entree\s*:|Entrée\s*:|Sortie\s*:|rend en sortie|Le probleme|Le problème"
    r"|\"\"\""                                    # docstring du programme
    r"|renvoie|retourne"
    r"|Pour (?:calculer|trouver|determiner|déterminer|obtenir|approcher"
    r"|estimer|simuler|chercher)"
)
#: Marqueurs d'une activite demandee a l'eleve, OU d'une interpretation du
#: resultat. Le programme demande « activite ou interpretation » : un
#: algorithme suivi d'un commentaire qui dit ce que le resultat signifie est
#: exploitable, meme sans question posee.
ACTIVITE_ALGORITHMIQUE = re.compile(
    r"Travail demande|Travail demandé|Demarche|Démarche"
    r"|\\erreurFrequente|\\margeAppui|\\exemple\b"
    r"|\\item\s+(?:Verifier|Vérifier|Reprendre|Calculer|Chercher|Comparer"
    r"|Simuler|Modifier|Estimer|Pousser|Changer|Compter|Utiliser|Ajouter|Faire)"
)

#: Marqueurs d'une TACHE explicitement demandee. C'est elle, et elle seule,
#: qui appelle une correction : une demarche a suivre n'a pas de « reponse ».
TACHE_ALGORITHMIQUE = re.compile(r"Travail demande|Travail demandé")

#: L'objet publie-t-il du code Python ? C'est ce cas, et lui seul, qui exige
#: un oracle executable.
CODE_PYTHON = re.compile(r"\\begin\{python\}|\\begin\{lstlisting\}")
#: Marqueurs d'une correction fournie pour le travail demande.
REPONSES_ALGORITHMIQUES = re.compile(
    r"Reponses|Réponses|Reponse a la|Réponse à la"
)

#: Marqueurs d'un algorithme effectivement expose au lecteur : un programme,
#: un algorithme en pseudo-code, un listing. Les blocs de verification
#: « BEGIN-VERIFY » en sont exclus a dessein : ils prouvent au producteur que
#: le contenu est juste, ils n'enseignent rien a l'eleve.
ALGORITHME_MONTRE = re.compile(
    r"\\begin\{python\}|\\begin\{sql\}|\\begin\{algorithme\}"
    r"|\\lstinputlisting|\\begin\{pseudocode\}|\\begin\{lstlisting\}"
)


#: Marqueurs d'une demonstration REDIGEE. La macro dediee ne suffit pas : le
#: manuel redige aussi ses demonstrations exigibles dans un bloc
#: d'approfondissement titre « Demonstrations exigibles », clos par un carre
#: de fin de preuve. Ne chercher que la macro faisait passer pour absentes des
#: demonstrations completes -- celle de 1 + 2 + ... + n par la methode de
#: Gauss, celle de la somme geometrique par telescopage.
#: Un exemple travaille : le manuel y montre la capacite a l'oeuvre. Un bloc
#: de code en est un pour une capacite de programmation -- « Parcourir une
#: liste » se montre en ecrivant la boucle, pas en la decrivant. Le memo Python
#: du manuel fonctionne ainsi : vingt-huit blocs, aucun exercice separe.
EXEMPLE_TRAVAILLE = re.compile(
    r"\\exempleRedige|\\exempleGuide|\\exemple\b|\\contreexemple"
    r"|\\begin\{verbatim\}|\\begin\{python\}|\\begin\{lstlisting\}"
)

MACRO_DE_PREUVE = re.compile(r"\\demonstration|\\begin\{demonstration\}|\\preuve")
#: Une demonstration TITREE : le manuel la redige aussi en prose, sous un titre
#: explicite, dans un bloc d'approfondissement ou une sous-section. Exiger la
#: macro dediee, ou un carre de fin de preuve, faisait passer pour absentes des
#: demonstrations completes -- la regle du produit, l'equation de la tangente,
#: la somme des n premiers entiers par la methode de Gauss.
TITRE_DE_PREUVE = re.compile(
    r"\\textbf\{\s*[Dd][ée]monstration"
    r"|\\subsection\*?\{\s*[Dd][ée]monstration"
    r"|\\paragraph\{\s*[Dd][ée]monstration"
    r"|[Dd][ée]monstration exigible"
)


def _porte_une_demonstration(texte: str) -> bool:
    return bool(MACRO_DE_PREUVE.search(texte) or TITRE_DE_PREUVE.search(texte))


def _manuel_depuis(chapitre: str) -> str:
    for prefixe in ("TEXPERTES", "TCOMPL", "TSPE", "TNSI", "1SPE", "1NSI"):
        if chapitre.startswith(prefixe):
            return prefixe
    return ""


if __name__ == "__main__":
    from collections import Counter

    contrats = charger_contrats()
    objets = charger_objets(contrats) + charger_transversaux()
    print(f"contrats de chapitre : {len(contrats)}")
    print(f"objets indexes       : {len(objets)}")
    print(f"  avec au moins une capacite resolue : "
          f"{sum(1 for o in objets if o.atoms)}")
    print("par manuel :", dict(Counter(o.manual for o in objets)))
    print("par role   :", dict(Counter(o.role for o in objets)))
