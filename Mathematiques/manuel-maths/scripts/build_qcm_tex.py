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


def rendre(donnees: dict) -> str:
    chapitre = donnees["chapitre"]
    questions = donnees["questions"]
    out = [_entete(chapitre, donnees["_source"]), f"\n\\section*{{{donnees['titre']}}}\n"]
    out.append(
        "\n\\begin{center}\n\\textit{Pour chaque question, une seule reponse est exacte.}\n"
        "\\end{center}\n\n\\begin{enumerate}\n"
    )

    capacite_courante = None
    for question in questions:
        if question["capacite"] != capacite_courante:
            capacite_courante = question["capacite"]
            out.append(f"\n\\item[] \\textbf{{Capacite {capacite_courante}}}\n")
        out.append(f"\n\\item \\textbf{{[{question['id']}]}} {question['enonce']}\n")
        out.append("  \\begin{enumerate}[label=\\Alph*.]\n")
        for lettre in LETTRES:
            if lettre in question["options"]:
                out.append(f"    \\item {question['options'][lettre]}\n")
        out.append("  \\end{enumerate}\n")
    out.append("\n\\end{enumerate}\n")

    # Cle professeur : reponses, erreurs diagnostiquees et renvois.
    out.append("\n\\clearpage\n\\section*{Cle de correction — reservee au professeur}\n\n")
    out.append("\\begin{center}\n\\begin{tabular}{lll}\n\\hline\n")
    out.append("Question & Capacite & Reponse exacte \\\\\n\\hline\n")
    for question in questions:
        out.append(f"{question['id']} & {question['capacite']} & \\textbf{{{question['correcte']}}} \\\\\n")
    out.append("\\hline\n\\end{tabular}\n\\end{center}\n\n")

    out.append("\\subsection*{Diagnostic des reponses erronees}\n\n\\begin{itemize}\n")
    for question in questions:
        out.append(f"  \\item \\textbf{{{question['id']}}}\n  \\begin{{itemize}}\n")
        for lettre in LETTRES:
            diagnostic = question["diagnostics"].get(lettre)
            if diagnostic:
                out.append(
                    f"    \\item \\textbf{{{lettre}}} — {diagnostic['erreur']} "
                    f"\\emph{{Renvoi : {diagnostic['renvoi']}.}}\n"
                )
        out.append("  \\end{itemize}\n")
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
        if question["correcte"] not in question["options"]:
            erreurs.append(f"{qid} : la reponse correcte ne figure pas parmi les options")
        for lettre in question["options"]:
            if lettre == question["correcte"]:
                if lettre in question["diagnostics"]:
                    erreurs.append(f"{qid} : la bonne reponse ne doit pas porter de diagnostic d'erreur")
                continue
            diagnostic = question["diagnostics"].get(lettre)
            if not diagnostic:
                erreurs.append(f"{qid} : distracteur {lettre} sans diagnostic")
            elif not diagnostic.get("renvoi"):
                erreurs.append(f"{qid} : distracteur {lettre} sans renvoi de remediation")
    return erreurs


def main() -> int:
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--chap", required=True)
    parseur.add_argument(
        "--check",
        action="store_true",
        help="ne rien ecrire ; signaler une divergence entre le .json et le .tex",
    )
    args = parseur.parse_args()

    dossier = RACINE / "chapitres" / args.chap / "qcm"
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

    donnees["_source"] = str(source.relative_to(RACINE))
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
