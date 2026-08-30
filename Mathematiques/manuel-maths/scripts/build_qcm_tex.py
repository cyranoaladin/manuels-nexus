#!/usr/bin/env python3
"""Genere le .tex d'un QCM depuis son .json, qui fait seul autorite.

La revue de contenu 1NSI a releve comme defaut P1 recurrent des QCM livres
« sans cle » : pas de reponse correcte tracee, pas de diagnostic par
distracteur, pas de renvoi de remediation. Maintenir a la main deux fichiers
paralleles (.tex pour l'impression, .json pour la plateforme) fait de plus
diverger les deux versions.

Ce script rend le .json canonique et en derive le .tex, en deux variantes :

- variante eleve : les questions seules, sans reponse ;
- variante professeur : les memes questions, suivies de la cle et, pour chaque
  distracteur, l'erreur diagnostiquee et le renvoi de remediation.

Usage :
    python3 scripts/build_qcm_tex.py --chap TSPE-CONTINUITE
    python3 scripts/build_qcm_tex.py --chap TSPE-CONTINUITE --check
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

RACINE = Path(__file__).resolve().parents[1]
LETTRES = ("A", "B", "C", "D")


def _entete(chapitre: str, source: str) -> str:
    meta = json.dumps(
        {
            "id": f"{chapitre}-QCM",
            "chapitre": chapitre,
            "type_objet": "qcm",
            "genere_depuis": source,
            "status": "generated",
        },
        ensure_ascii=False,
    )
    return f"% META: {meta}\n% Fichier genere par scripts/build_qcm_tex.py — ne pas editer a la main.\n"


#: Balisage inline autorise dans un champ texte de QCM. Tout le reste est
#: refuse : « responsabilite de l'auteur » n'est pas un contrat verifiable,
#: et une macro inconnue peut tronquer ou deformer le rendu sans erreur.
MACROS_TEXTE_AUTORISEES = frozenset({"code", "emph", "textbf", "textit", "verb"})

_MACRO = re.compile(r"\\([a-zA-Z]+)")


class QcmMarkupError(ValueError):
    """Balisage non autorise dans un champ texte de QCM."""


def valider_balisage_texte(champ: str, valeur: str) -> None:
    """Refuse toute macro hors liste blanche en dehors du mode mathematique."""

    if not isinstance(valeur, str):
        return
    hors_math = "".join(re.split(r"\$[^$]*\$", valeur))
    inconnues = sorted(
        {m.group(1) for m in _MACRO.finditer(hors_math)} - MACROS_TEXTE_AUTORISEES
    )
    if inconnues:
        raise QcmMarkupError(
            f"{champ} : balisage non autorise en texte : "
            + ", ".join("\\" + name for name in inconnues)
            + f" (autorise : {', '.join(sorted(MACROS_TEXTE_AUTORISEES))})"
        )


def _clean_text(s: str, champ: str = "champ") -> str:
    if not isinstance(s, str):
        return s
    valider_balisage_texte(champ, s)
    s = s.replace("`^`", "\\code{\\textasciicircum}")
    parts = s.split('$')
    for i in range(0, len(parts), 2):
        # Hors mode mathematique, ces caracteres ne sont jamais du balisage
        # legitime dans un champ de QCM : le producteur les possede.
        # Mesure a l'appui : sans echappement, # & } { font echouer la
        # compilation, et % avale silencieusement la fin de la ligne -- plus
        # dangereux qu'une erreur, car la perte de contenu passe inapercue.
        # { } et \ restent a l'auteur : ils portent du balisage reel
        # (\code{...} par exemple), et le smoke de compilation est le garde-fou.
        # ~ est un espace insecable en LaTeX : « X ~ B(n,p) » s'imprime
        # « X B(n,p) » et le symbole « suit la loi » disparait sans erreur.
        parts[i] = parts[i].replace("~", "\\textasciitilde{}")
        parts[i] = parts[i].replace("%", "\\%")
        parts[i] = parts[i].replace("#", "\\#")
        parts[i] = parts[i].replace("&", "\\&")
        parts[i] = parts[i].replace("_", "\\_")
        parts[i] = parts[i].replace("^", "\\textasciicircum{}")
    return "$".join(parts)


def rendre(donnees: dict) -> str:
    chapitre = donnees["chapitre"]
    titre = donnees.get("titre", "Faire le point")
    questions = donnees.get("questions", [])
    out = [_entete(chapitre, donnees["_source"]), f"\n\\section*{{\\textcolor{{chapcolor}}{{\\MakeUppercase{{{titre}}}}}}}\n"]
    out.append(
        "\n\\begin{center}\n\\textit{Pour chaque question, une seule réponse est exacte.}\n"
        "\\end{center}\n\n\\begin{enumerate}\n"
    )

    capacite_courante = None
    for question in questions:
        if question["capacite"] != capacite_courante:
            capacite_courante = question["capacite"]
            out.append(f"\n\\item[] \\textbf{{Capacité {capacite_courante}}}\n")
        enonce = _clean_text(
            question.get("enonce") or question.get("texte", ""),
            f"{question.get('id')}/enonce",
        )
        out.append(f"\n\\item \\textbf{{[{question['id']}]}} {enonce}\n")
        out.append("  \\begin{enumerate}[label=\\Alph*.]\n")
        raw_opts = question.get("options") or {}
        if isinstance(raw_opts, list):
            opts = {LETTRES[i]: raw_opts[i] for i in range(min(len(raw_opts), len(LETTRES)))}
        elif isinstance(raw_opts, dict):
            opts = raw_opts
        else:
            opts = {}
        for lettre in LETTRES:
            if lettre in opts:
                opt_text = _clean_text(opts[lettre], f"{question.get('id')}/options.{lettre}")
                out.append(f"    \\item {opt_text}\n")
        out.append("  \\end{enumerate}\n")
    out.append("\n\\end{enumerate}\n")

    # Cle professeur : reponses, erreurs diagnostiquees et renvois. La source
    # TeX est commune aux deux variantes ; le drapeau est defini par le gabarit
    # canonique et ferme toute la zone reservee.
    out.append(
        "\n% NEXUS-QCM-TEACHER-ONLY-BEGIN\n"
        "\\ifnxVersionProfesseur\n"
        "\\clearpage\n\\section*{Clé de correction — réservée au professeur}\n\n"
    )
    out.append("\\begin{center}\n\\begin{tabular}{lll}\n\\hline\n")
    out.append("Question & Capacité & Réponse exacte \\\\\n\\hline\n")
    for question in questions:
        out.append(f"{question['id']} & {question['capacite']} & \\textbf{{{question['correcte']}}} \\\\\n")
    out.append("\\hline\n\\end{tabular}\n\\end{center}\n\n")

    out.append("\\subsection*{Diagnostic des réponses erronées}\n\n\\begin{itemize}\n")
    for question in questions:
        out.append(f"  \\item \\textbf{{{question['id']}}}\n  \\begin{{itemize}}\n")
        for lettre in LETTRES:
            diagnostic = question["diagnostics"].get(lettre)
            if diagnostic:
                err_txt = _clean_text(
                    diagnostic['erreur'], f"{question.get('id')}/diagnostics.{lettre}"
                )
                raw_renvoi = diagnostic.get('renvoi')
                renvoi_txt = (
                    _clean_text(raw_renvoi.strip())
                    if isinstance(raw_renvoi, str) and raw_renvoi.strip()
                    else ""
                )
                renvoi_suffix = (
                    f" \\emph{{Renvoi : {renvoi_txt}.}}"
                    if renvoi_txt
                    else ""
                )
                out.append(
                    f"    \\item \\textbf{{{lettre}}} — {err_txt}"
                    f"{renvoi_suffix}\n"
                )
        out.append("  \\end{itemize}\n")
    out.append(
        "\\end{itemize}\n"
        "\\fi\n"
        "% NEXUS-QCM-TEACHER-ONLY-END\n"
    )
    return "".join(out)


def rendre_diagnostics(donnees: dict, identifiant: str) -> str:
    """Rend la fiche de diagnostics destinee a l'ELEVE, depuis la meme source.

    Certains chapitres offrent, apres le QCM, une fiche que l'eleve consulte
    lui-meme pour comprendre son erreur. Ecrite a la main, elle finit par
    contredire la cle : le chapitre pilote 1NSI annoncait « Q1 : reponse B »
    quand la source canonique portait A. Deux artefacts qui affirment des
    reponses differentes dans le meme manuel valent moins que pas de fiche du
    tout. Elle derive donc du .json, comme le QCM lui-meme.
    """

    chapitre = donnees["chapitre"]
    meta = json.dumps(
        {
            "id": identifiant,
            "chapitre": chapitre,
            "type_objet": "qcm_diagnostics",
            "genere_depuis": donnees["_source"],
            "status": "generated",
        },
        ensure_ascii=False,
    )
    out = [
        f"% META: {meta}\n"
        "% Fichier genere par scripts/build_qcm_tex.py — ne pas editer a la main.\n",
        "\n\\section*{\\textcolor{chapcolor}{\\MakeUppercase{Diagnostics du QCM}}}\n",
        "\n\\textit{Compare tes réponses à la clé, puis lis le diagnostic de "
        "chaque réponse que tu n'as pas choisie correctement.}\n",
    ]
    for question in donnees["questions"]:
        qid = question["id"]
        out.append(
            f"\n\\textbf{{{qid}.}} Réponse : \\textbf{{{question['correcte']}}}.\n"
        )
        out.append("\\begin{itemize}[nosep]\n")
        for lettre in LETTRES:
            diagnostic = (question.get("diagnostics") or {}).get(lettre)
            if not diagnostic:
                continue
            erreur = _clean_text(
                diagnostic["erreur"], f"{qid}/diagnostics.{lettre}"
            )
            renvoi = diagnostic.get("renvoi")
            suffixe = (
                f" \\emph{{Renvoi : {_clean_text(renvoi.strip())}.}}"
                if isinstance(renvoi, str) and renvoi.strip()
                else ""
            )
            out.append(f"  \\item Si {lettre} — {erreur}{suffixe}\n")
        out.append("\\end{itemize}\n")
    return "".join(out)


def valider(donnees: dict) -> list[str]:
    """Controles bloquants avant generation."""
    erreurs = []
    vus = set()
    for question in donnees["questions"]:
        qid = question["id"]
        if qid in vus:
            erreurs.append(f"{qid} : identifiant en double")
        vus.add(qid)
        options = question.get("options") or sorted(set(question.get("diagnostics", {}).keys()) | {question["correcte"]})
        if question["correcte"] not in options:
            erreurs.append(f"{qid} : la reponse correcte ne figure pas parmi les options")
        for lettre in options:
            if lettre == question["correcte"]:
                if lettre in question["diagnostics"]:
                    erreurs.append(f"{qid} : la bonne reponse ne doit pas porter de diagnostic d'erreur")
                continue
            diagnostic = question["diagnostics"].get(lettre)
            if not diagnostic:
                erreurs.append(f"{qid} : distracteur {lettre} sans diagnostic")
    return erreurs


#: Les chapitres NSI vivent hors de `manuel-maths`, mais partagent le meme
#: contrat : le .json fait autorite, le .tex en derive. Le generateur les sert
#: tous les deux plutot que d'exister en deux exemplaires divergents.
RACINES_CHAPITRES = (
    RACINE / "chapitres",
    RACINE.parents[1] / "NSI" / "chapitres",
)


def resoudre_dossier_qcm(chapitre: str) -> Path | None:
    for racine in RACINES_CHAPITRES:
        dossier = racine / chapitre / "qcm"
        if dossier.is_dir():
            return dossier
    return None


def _racine_de(source: Path) -> Path:
    """Racine du depot dont `source` releve, pour un chemin `_source` stable."""

    for racine in RACINES_CHAPITRES:
        if racine in source.parents:
            return racine.parent
    return RACINE


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--chap", required=True)
    parseur.add_argument(
        "--check",
        action="store_true",
        help="ne rien ecrire ; signaler une divergence entre le .json et le .tex",
    )
    args = parseur.parse_args()

    dossier = resoudre_dossier_qcm(args.chap)
    if dossier is None:
        print(f"[QCM] chapitre inconnu : {args.chap}", file=sys.stderr)
        return 2
    sources = sorted(dossier.glob("*-QCM.json"))
    if len(sources) != 1:
        print(
            f"[QCM] {args.chap} : attendu un seul *-QCM.json, trouve {len(sources)}",
            file=sys.stderr,
        )
        return 2
    source = sources[0]
    cible = source.with_suffix(".tex")

    donnees = json.loads(source.read_text(encoding="utf-8"))
    erreurs = valider(donnees)
    if erreurs:
        for erreur in erreurs:
            print(f"[QCM] {erreur}", file=sys.stderr)
        return 2

    donnees["_source"] = str(source.relative_to(_racine_de(source)))
    rendu = rendre(donnees)
    if args.check:
        actuel = cible.read_text(encoding="utf-8") if cible.exists() else ""
        if actuel != rendu:
            print(f"[QCM] {cible} diverge de sa source {source.name}", file=sys.stderr)
            return 1
        print(f"[QCM] {args.chap} : .tex synchrone avec .json ({len(donnees['questions'])} questions)")
        return 0

    cible.write_text(rendu, encoding="utf-8")
    print(f"[QCM] {cible} genere depuis {source.name} ({len(donnees['questions'])} questions)")

    # La fiche de diagnostics n'existe que dans certains chapitres. La produire
    # partout ajouterait un objet non prevu ; ne pas la produire la laisserait
    # contredire la cle. On regenere donc celle qui existe deja.
    for compagnon in sorted(dossier.glob("*-QCM-DIAG.tex")):
        compagnon.write_text(
            rendre_diagnostics(donnees, compagnon.stem), encoding="utf-8"
        )
        print(f"[QCM] {compagnon} regenere depuis la meme source")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
