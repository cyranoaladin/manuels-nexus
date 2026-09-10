#!/usr/bin/env python3
"""Inventaire officiel extrait des textes du BO, sans lire le referentiel interne.

Le referentiel interne du depot decrit ce que les manuels PRETENDENT couvrir. Il
ne peut donc pas servir a verifier qu'ils couvrent le programme : ce serait
comparer une copie a elle-meme. Cet extracteur part du texte officiel et de lui
seul, et ne connait aucun identifiant de chapitre.

Ce que le BO distingue est conserve tel quel. Un programme de mathematiques ne
dit pas « capacite » partout : il separe des contenus, des capacites attendues,
des demonstrations exigibles, des exemples d'algorithme, des automatismes et des
approfondissements possibles. Tout ramener a « capacite » effacerait justement ce
qui separe ce qui doit etre su, su-faire, demontre, et ce qui est facultatif.

INVARIANT CENTRAL — aucune puce ne disparait en silence. Chaque ligne a puce du
corps du programme devient soit un item, soit un rejet explicite portant son
motif. `extracted + discarded == bullets_in_body` est verifie a la sortie : un
extracteur qui perdrait des lignes du texte officiel ne pourrait pas servir
d'autorite pour juger la couverture.

Les `official_id` sont des identifiants TECHNIQUES, forges ici pour le pipeline.
Le ministere n'en publie pas : chaque item porte donc
`locally_assigned_identifier: true`, et le libelle officiel reste la reference.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]

#: Rubriques du BO -> (nature, engage-t-il le manuel).
#: Les variantes singulier/pluriel sont toutes presentes : le texte alterne
#: « Exemples d'algorithme » et « Exemple d'algorithme » d'une section a l'autre,
#: et n'en connaitre qu'une forme ferait disparaitre cinq rubriques entieres.
RUBRIC_PATTERNS: tuple[tuple[str, str, bool], ...] = (
    (r"contenus?", "KNOWLEDGE", True),
    # Les themes d'etude de l'option complementaire portent leurs attendus
    # sous l'intitule « Contenus associes » et non « Contenus ».
    (r"contenus? associes?", "KNOWLEDGE", True),
    (r"capacites? attendues?( et commentaires)?", "EXPECTED_CAPACITY", True),
    (r"demonstrations?( attendues?| exigibles?)?", "DEMONSTRATION", True),
    # « Demonstrations possibles » : l'option complementaire propose des
    # demonstrations au professeur sans les exiger de l'eleve.
    (r"demonstrations? possibles?", "DEMONSTRATION", False),
    (r"exemples? d[’']?algorithmes?", "ALGORITHMIC_CAPACITY", True),
    (r"approfondissements? possibles?", "OPTIONAL_ENRICHMENT", False),
    (r"histoire des mathematiques", "HISTORY_CONTEXT", False),
    (r"objectifs?", "OBJECTIVE", False),
    # Les « problemes possibles » des options de terminale sont des pistes
    # d'etude offertes au professeur, pas des attendus opposables a l'eleve.
    (r"problemes? possibles?", "OPTIONAL_ENRICHMENT", False),
    (r"commentaires?", "COMMENTARY", False),
)

#: Sections de premier niveau connues, toutes editions confondues. Cette liste
#: sert de defaut ; la liste REELLEMENT appliquee est propre a chaque document
#: et se declare a l'appel. Les intitules se recoupent d'un programme a
#: l'autre sans designer la meme chose : « Probabilites » est une section a
#: part entiere du programme de terminale, mais un simple domaine
#: d'automatismes en premiere. Une liste unique et globale ferait donc perdre
#: a la premiere les automatismes de probabilites.
SECTION_NAMES = (
    "Vocabulaire ensembliste et logique",
    "Algorithmique et programmation",
    "Automatismes",
    "Algèbre",
    "Analyse",
    "Géométrie",
    "Probabilités et statistiques",
)

BULLET = re.compile("^[ \t\x0c]*[−–•*\\-\uf02d][ \t]+(\\S.*)$")
#: Marqueurs decoratifs precedant un titre de rubrique, a retirer avant analyse.
MARKERS = "\uf0b7\uf0be\u2022\uf0a7"
#: Glyphes de la zone a usage prive : ce qui reste d'une formule que `pdftotext`
#: n'a pas su transcrire. Leur presence est signalee item par item.
PRIVATE_USE = re.compile(r"[\ue000-\uf8ff]")
BODY_MARKER = "Programme"
#: Un titre est court et ne se termine pas par une ponctuation de phrase.
HEADING_MAX = 80


def strip_accents(texte: str) -> str:
    sans = unicodedata.normalize("NFKD", texte)
    return "".join(c for c in sans if not unicodedata.combining(c))


def normalise(texte: str) -> str:
    return re.sub(r"\s+", " ", strip_accents(texte)).strip().lower()


def sans_marqueur(nue: str) -> str:
    """Retire la puce decorative qui precede certains titres de rubrique."""
    return nue.lstrip(MARKERS).strip()


def match_rubric(ligne: str) -> tuple[str, str, bool] | None:
    cle = normalise(ligne).rstrip(" :")
    for motif, nature, obligatoire in RUBRIC_PATTERNS:
        if re.fullmatch(motif, cle):
            return ligne.strip(), nature, obligatoire
    return None


def is_heading(nue: str) -> bool:
    """Un titre du BO est court, sans ponctuation finale et sans phrase interne.

    Le troisieme critere ecarte les fragments de prose que `pdftotext` coupe au
    milieu d'un paragraphe : sans lui, « ... ou la notation E \\ A. On utilise la »
    devenait une sous-section fantome portant huit capacites reelles.
    """
    return (
        0 < len(nue) <= HEADING_MAX
        and not nue.endswith((".", ":", ";", ",", "!", "?"))
        and ". " not in nue
        and not BULLET.match(nue)
        and nue[0].isupper()
    )


#: Nature par defaut des puces d'une section quand le BO n'ouvre aucune rubrique
#: nommee. Le texte ne libelle pas toujours ses listes d'attendus : la « Notion
#: de liste » de 2026 enumere quatre capacites sous une simple prose, la ou
#: 2019 les rangeait sous « Capacites attendues ».
#:
#: Seule la partie « Automatismes » a une nature propre, parce que le BO la
#: nomme ainsi. Ailleurs, une liste non intitulee reste une capacite attendue :
#: lui inventer une categorie -- « capacite de programmation » pour la section
#: d'algorithmique, par exemple -- faisait apparaitre en 2026 quatre attendus
#: « ajoutes » et en 2019 les memes quatre « retires », alors que le texte est
#: mot pour mot le meme et que seul son intitule de rubrique avait bouge.
SECTION_DEFAULT_KIND: dict[str, str] = {
    "automatismes": "AUTOMATISM",
}
DEFAULT_KIND = "EXPECTED_CAPACITY"


def default_kind_for(section: str | None) -> str:
    return SECTION_DEFAULT_KIND.get(normalise(section or ""), DEFAULT_KIND)


def _slug(texte: str, longueur: int = 34) -> str:
    base = re.sub(r"[^A-Z0-9]+", "-", strip_accents(texte).upper()).strip("-")
    return base[:longueur].rstrip("-") or "ITEM"


@dataclass
class Ligne:
    numero: int
    page: int
    brute: str
    nue: str
    indent: bool
    #: Vrai si un saut de page precede immediatement cette ligne. Un saut de
    #: page separe au moins autant qu'une ligne vide, et le BO en met un devant
    #: certains titres de domaine (« Evolutions et variations »).
    page_break: bool = False
    #: Vrai si la ligne precedente etait vide. Dans ce texte, tout titre de
    #: sous-section est ainsi detache, jamais un sous-titre ni une ligne de prose.
    after_blank: bool = False


@dataclass
class Extraction:
    items: list[dict[str, Any]] = field(default_factory=list)
    discarded: list[dict[str, Any]] = field(default_factory=list)
    bullets_in_body: int = 0
    bullets_in_preamble: int = 0
    body_starts_at: int = 0
    pages: int = 0


def tokenise(text: str) -> list[Ligne]:
    """Numerote les lignes et suit les sauts de page (\\x0c) pour l'ancrage."""
    lignes: list[Ligne] = []
    page = 1
    # `splitlines` couperait aussi sur \x0c : les numeros de ligne ne
    # correspondraient plus au fichier et les sauts de page seraient invisibles.
    for numero, brute in enumerate(text.split("\n"), start=1):
        # Un saut de page en tete de ligne appartient a cette ligne : le
        # comptabiliser apres coup daterait la ligne de la page precedente.
        entete = len(brute) - len(brute.lstrip("\x0c"))
        page += entete
        sauts = brute.count("\x0c") - entete
        propre = brute.replace("\x0c", "")
        lignes.append(
            Ligne(
                numero=numero,
                page=page,
                brute=propre,
                nue=propre.strip(),
                indent=bool(propre) and propre[0] in " \t",
                page_break=bool(entete),
                after_blank=not lignes or not lignes[-1].nue,
            )
        )
        page += sauts
    return lignes


def find_body_start(lignes: list[Ligne]) -> int:
    """Le corps commence au dernier titre isole « Programme ».

    Le sommaire en contient une premiere occurrence ; le preambule qui la suit
    est un texte de cadrage pedagogique, pas une liste d'attendus. Prendre la
    derniere occurrence, et non la premiere, evite d'inventorier le sommaire.
    """
    positions = [
        index
        for index, ligne in enumerate(lignes)
        if ligne.nue == BODY_MARKER and not ligne.indent
    ]
    if not positions:
        return 0
    return positions[-1] + 1


def extract(
    text: str,
    authority: str,
    manual: str,
    body_starts_at: int | None = None,
    section_names: tuple[str, ...] = SECTION_NAMES,
) -> Extraction:
    lignes = tokenise(text)
    depart = body_starts_at - 1 if body_starts_at else find_body_start(lignes)
    res = Extraction(body_starts_at=depart + 1, pages=max(ligne_.page for ligne_ in lignes))
    res.bullets_in_preamble = sum(1 for ligne_ in lignes[:depart] if BULLET.match(ligne_.brute))

    corps = lignes[depart:]
    res.bullets_in_body = sum(1 for ligne_ in corps if BULLET.match(ligne_.brute))

    # Les en-tetes et pieds de page se repetent a l'identique EN BORD DE PAGE.
    # Sans les ecarter, le bandeau « Mathematiques expertes, enseignement
    # optionnel, classe terminale, voie » devenait une sous-section du
    # programme et absorbait tous ses items. La position compte autant que la
    # repetition : « Probabilites » revient lui aussi plusieurs fois, mais au
    # milieu des pages, et c'est un vrai domaine d'automatismes -- le filtrer
    # sur la seule repetition lui faisait perdre ses items.
    par_page: dict[int, list[Ligne]] = {}
    for ligne_ in corps:
        if ligne_.nue:
            par_page.setdefault(ligne_.page, []).append(ligne_)
    en_bord: Counter[str] = Counter()
    for pleines in par_page.values():
        for ligne_ in pleines[:2] + pleines[-3:]:
            if not BULLET.match(ligne_.brute):
                en_bord[ligne_.nue] += 1
    courantes = {
        texte
        for texte, n in en_bord.items()
        if n >= 3
        and match_rubric(sans_marqueur(texte)) is None
        and normalise(sans_marqueur(texte)) not in {normalise(s) for s in section_names}
    }

    sections = {normalise(s): s for s in section_names}
    section: str | None = None
    subsection: str | None = None
    subheading: str | None = None
    rubric: tuple[str, str, bool] | None = None
    rubric_is_implicit = False
    en_automatismes = False

    tampon: list[str] = []
    ancre: Ligne | None = None
    rangs: dict[tuple[str | None, str | None, str], int] = {}
    precedente: Ligne | None = None
    apres_section = False

    def cloturer() -> None:
        nonlocal tampon, ancre
        if not tampon or ancre is None:
            tampon = []
            return
        libelle = re.sub(r"\s+", " ", " ".join(tampon)).strip()
        tampon = []
        if rubric is None:
            res.discarded.append({
                "line": ancre.numero,
                "page": ancre.page,
                "text": libelle,
                "reason": "BULLET_OUTSIDE_ANY_RUBRIC_AND_ANY_SUBSECTION",
                "explanation": (
                    "puce illustrative d'un paragraphe de cadrage : ni rubrique "
                    "d'attendus ni sous-section du programme n'est ouverte ici"
                ),
                "official_section": section,
                "official_subsection": subsection,
            })
            return
        titre, nature, obligatoire = rubric
        # Rang de la puce dans sa rubrique. C'est la coordonnee que citent les
        # ancrages du referentiel interne (« ... / Capacites attendues / puce 3 »)
        # et sans laquelle ces ancrages ne designent rien de resoluble.
        coord = (section, subsection, titre)
        rangs[coord] = rangs.get(coord, 0) + 1
        empreinte = hashlib.sha256(libelle.encode("utf-8")).hexdigest()[:8]
        res.items.append({
            # La nature fait partie de l'identifiant : le BO enonce parfois le
            # meme libelle en contenu et en demonstration exigible
            # (« Integration par parties. »), et ce sont deux attendus
            # distincts -- l'un a savoir, l'autre a demontrer.
            "official_id": "::".join([
                authority,
                _slug(section or "PROGRAMME"),
                _slug(subsection or titre),
                nature,
                empreinte,
            ]),
            "locally_assigned_identifier": True,
            "manual": manual,
            "authority_ref": authority,
            "official_section": section,
            "official_subsection": subsection,
            "official_subheading": subheading,
            "official_rubric": titre,
            "official_rubric_index": rangs[coord],
            "rubric_is_implicit_in_source": rubric_is_implicit,
            "official_wording": libelle,
            # Le BO 2019 compose ses formules en police Symbol ; `pdftotext`
            # ne sait pas toutes les transcrire. Un libelle qui en garde la
            # trace ne peut pas etre lu comme le texte officiel exact.
            "wording_contains_unmapped_glyphs": bool(PRIVATE_USE.search(libelle)),
            "kind": nature,
            "mandatory": obligatoire,
            "source_page_or_anchor": f"page={ancre.page};line={ancre.numero}",
        })

    def prochain_signifiant(depuis: int) -> Ligne | None:
        for suivante in corps[depuis + 1:]:
            if suivante.nue:
                return suivante
        return None

    for position, ligne in enumerate(corps):
        if not ligne.nue:
            cloturer()
            continue

        if ligne.nue in courantes:
            cloturer()
            continue

        puce = BULLET.match(ligne.brute)
        if puce:
            if rubric is None and (
                (precedente is not None and precedente.nue.endswith(":"))
                or subsection is not None
            ):
                # Le BO n'ouvre pas toujours une rubrique nommee : il introduit
                # ses attendus soit par une amorce (« Les eleves apprennent en
                # situation a : »), soit par la seule sous-section (« Notion de
                # liste »). Sans cette regle ces attendus disparaitraient, ou
                # -- pire -- heriteraient de la rubrique precedente et seraient
                # classes « Histoire des mathematiques ».
                amorce = precedente.nue.rstrip(" :") if precedente is not None else ""
                sur_amorce = precedente is not None and precedente.nue.endswith(":")
                rubric = (
                    amorce if amorce and sur_amorce else (subsection or ""),
                    default_kind_for(section),
                    True,
                )
                rubric_is_implicit = True
            cloturer()
            ancre = ligne
            tampon = [puce.group(1).strip()]
            continue

        # Les titres de rubrique du BO 2019 sont indentes, tout comme les
        # lignes de continuation d'un item. Les reconnaitre AVANT de traiter
        # les continuations evite qu'un « Capacites attendues » indente ne soit
        # avale dans le libelle de la puce qui le precede.
        cle_ligne = normalise(sans_marqueur(ligne.nue))
        rub_ligne = match_rubric(sans_marqueur(ligne.nue))
        if tampon and ligne.indent and cle_ligne not in sections and rub_ligne is None:
            tampon.append(ligne.nue)
            continue

        cloturer()
        if rubric_is_implicit:
            # Une rubrique implicite ne vaut que pour la liste qu'elle porte.
            rubric, rubric_is_implicit = None, False
        precedente = ligne
        cle = normalise(sans_marqueur(ligne.nue))

        if cle in sections:
            section, subsection, subheading, rubric = sections[cle], None, None, None
            en_automatismes = cle == normalise("Automatismes")
            apres_section = True
            continue

        rub = match_rubric(sans_marqueur(ligne.nue))
        if rub is not None:
            rubric, subheading = rub, None
            continue

        # Le titre s'apprecie une fois sa puce decorative retiree : le BO 2019
        # prefixe ses sous-sections d'un U+F0B7, et un titre juge sur ce
        # caractere-la ne commence jamais par une majuscule.
        titre_nu = sans_marqueur(ligne.nue)
        # Une ligne suivie d'une continuation de phrase n'est pas un titre.
        # `pdftotext` coupe parfois un paragraphe au milieu -- ici sur un
        # accent combinant -- et laisse un fragment qui a exactement la forme
        # d'un titre detache. Le prendre pour tel fabriquait une sous-section
        # officielle inexistante, « Pour le complementaire d'un sous-ensemble
        # A de E, on utilise la notation A », a laquelle onze items etaient
        # ensuite rattaches.
        apres = corps[position + 1] if position + 1 < len(corps) else None
        continuee = bool(
            apres
            and apres.nue
            and (
                apres.nue[0].islower()
                or unicodedata.combining(apres.nue[0])
                or unicodedata.category(apres.nue[0]) == "Mn"
            )
        )
        if continuee or not is_heading(titre_nu):
            apres_section = False
            continue  # prose de cadrage, deja retenue comme `precedente`

        # Un titre court est ambigu : nouvelle sous-section, ou sous-titre a
        # l'interieur de la rubrique courante ? Ce que le BO ecrit ensuite le
        # tranche. Un sous-titre est immediatement suivi des puces qu'il
        # regroupe (« Point de vue local ») ; une sous-section est suivie d'une
        # rubrique nommee ou d'un paragraphe de presentation.
        ouvrait_une_partie, apres_section = apres_section, False
        suivante = prochain_signifiant(position)
        suit_une_puce = suivante is not None and bool(BULLET.match(suivante.brute))
        # Un titre qui suit immediatement celui de sa partie en est detache
        # par cette partie meme : le premier theme d'etude de l'option
        # complementaire est colle a « Themes d'etude », sans blanc entre eux.
        detache = ligne.after_blank or ligne.page_break or ouvrait_une_partie
        if not detache and not suit_une_puce:
            # Ni titre detache, ni sous-titre gouvernant une liste : c'est une
            # ligne de prose que `pdftotext` a coupee au milieu d'un paragraphe.
            # La retenir comme sous-section fabriquerait un intitule officiel
            # qui n'existe pas dans le BO.
            continue
        if en_automatismes:
            # Dans « Automatismes » chaque titre est un domaine thematique, et
            # les domaines se succedent sans rubrique intercalaire : les traiter
            # en sous-titres les aurait tous fondus dans le premier.
            subsection, subheading, rubric = titre_nu, None, None
        elif suit_une_puce and rubric is not None:
            # Un titre suivi directement de puces, alors qu'une rubrique est
            # ouverte, regroupe ces puces a l'interieur de la rubrique : c'est
            # un sous-titre. Une sous-section, elle, s'ouvre toujours sur une
            # rubrique ou sur un paragraphe de presentation. Le critere ne peut
            # pas etre la seule presence d'un blanc au-dessus : le BO de 2019
            # detache « Point de vue local » d'une ligne vide, et le prendre
            # pour une sous-section faisait disparaitre « Derivation ».
            subheading = titre_nu
        else:
            subsection, subheading, rubric = titre_nu, None, None

    cloturer()
    return res


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--authority", required=True)
    parser.add_argument("--manual", required=True)
    parser.add_argument("--effective-from", required=True)
    parser.add_argument(
        "--sections",
        default=None,
        help="titres de section de CE document, separes par « | ». "
             "Les intitules varient d'un programme a l'autre et un meme "
             "intitule n'y a pas toujours le meme rang.",
    )
    parser.add_argument(
        "--body-starts-at",
        type=int,
        default=None,
        help="numero de ligne ou commence le programme, pour les textes qui "
             "n'ont pas de titre « Programme » isole",
    )
    parser.add_argument("--effective-until", default=None)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)

    source = args.source.resolve()
    res = extract(
        source.read_text(encoding="utf-8"),
        args.authority,
        args.manual,
        args.body_starts_at,
        tuple(args.sections.split("|")) if args.sections else SECTION_NAMES,
    )

    total = len(res.items) + len(res.discarded)
    if total != res.bullets_in_body:
        print(
            f"FATAL: {res.bullets_in_body} puces dans le corps mais {total} "
            f"comptabilisees ({len(res.items)} items + {len(res.discarded)} rejets)",
            file=sys.stderr,
        )
        return 2

    for item in res.items:
        item["effective_from"] = args.effective_from
        item["effective_until"] = args.effective_until

    charge = {
        "artifact_type": "official_programme_inventory",
        "schema_version": 1,
        "generated_by": "scripts/extract_official_programme.py",
        "manual": args.manual,
        "authority_ref": args.authority,
        "effective_from": args.effective_from,
        "effective_until": args.effective_until,
        "source_path": str(source.relative_to(ROOT)),
        "source_sha256": "sha256:" + hashlib.sha256(source.read_bytes()).hexdigest(),
        "identifiers_are_locally_assigned": True,
        "declared_sections": list(
            tuple(args.sections.split("|")) if args.sections else SECTION_NAMES
        ),
        "accounting": {
            "body_starts_at_line": res.body_starts_at,
            "pages": res.pages,
            "bullets_in_preamble_excluded": res.bullets_in_preamble,
            "bullets_in_body": res.bullets_in_body,
            "extracted_items": len(res.items),
            "discarded_bullets": len(res.discarded),
            "every_body_bullet_accounted_for": True,
        },
        "kind_counts": dict(sorted(Counter(i["kind"] for i in res.items).items())),
        "items": res.items,
        "discarded_bullets": res.discarded,
    }
    sortie = json.dumps(charge, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(sortie, encoding="utf-8")

    print(f"{args.manual} / {args.authority} : {len(res.items)} items officiels")
    print(f"   corps a partir de la ligne {res.body_starts_at}, {res.pages} pages")
    print(f"   puces corps {res.bullets_in_body} = items {len(res.items)}"
          f" + rejets {len(res.discarded)}"
          f"   (preambule exclu : {res.bullets_in_preamble} puces)")
    for nature, n in charge["kind_counts"].items():
        print(f"   {n:4d}  {nature}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
