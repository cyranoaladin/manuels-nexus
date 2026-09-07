#!/usr/bin/env python3
"""Ce qu'un exercice doit CONTENIR pour servir une capacite donnee.

Une capacite n'est pas un code : c'est un geste mathematique. « Je sais
determiner les diviseurs d'un entier et le PGCD de deux entiers » demande des
entiers, une divisibilite, un algorithme d'Euclide. Un exercice sur la
convexite de `1/(1+x)` ne la sert pas, quel que soit le code inscrit dans son
META.

Ce module declare, capacite par capacite, les MARQUEURS MATHEMATIQUES dont la
presence est necessaire. Ce ne sont pas des mots-cles de rapprochement flou :
chaque signature est ecrite a la main, lisible, et contestable ligne a ligne.
Un marqueur est une expression reguliere appliquee au corps LaTeX et au bloc
oracle -- ce que l'eleve lit et ce que la machine verifie.

`REQUIRED` : au moins un marqueur de CHAQUE groupe doit apparaitre. Les
groupes expriment une conjonction de natures ; les alternatives a l'interieur
d'un groupe expriment les ecritures acceptables d'une meme notion.

`FORBIDDEN` : des marqueurs dont la presence, seule, revele un contenu d'un
autre domaine. On les emploie avec parcimonie -- un exercice d'arithmetique a
parfaitement le droit de deriver une fonction en chemin.

Une capacite sans signature n'est pas declaree alignee : elle est declaree
NON VERIFIEE, et le registre le dit.
"""

from __future__ import annotations

#: L'unite imaginaire s'ecrit de deux facons dans le corpus : `\mathrm{i}`
#: dans les chapitres recents, `i` tout court ailleurs. Un marqueur qui n'en
#: connait qu'une refuserait la moitie des enonces.
UNITE_IMAGINAIRE = r"\\mathrm\{i\}|(?<![A-Za-z\\])i(?![A-Za-z])"

#: chapitre -> code de capacite -> {"required": [[alternatives], ...],
#:                                  "forbidden": [marqueurs]}
SIGNATURES: dict[str, dict[str, dict[str, list]]] = {
    "TEXP-ARITHMETIQUE": {
        "C1": {
            "required": [
                [r"\bdiviseur", r"\bdivisibilit", r"\bdivise\b", r"\bPGCD\b",
                 r"\bpgcd\b", r"\bgcd\b"],
                [r"\b\d{2,}\b", r"\bentier"],
            ],
        },
        "C2": {
            "required": [
                [r"\bcongruen", r"\bmodulo\b", r"\\equiv", r"\\bmod\b"],
                [r"\binvers", r"\bcongruen", r"\\equiv", r"\\bmod\b"],
            ],
        },
        "C3": {
            "required": [
                [r"\bdivisibilit", r"\bpremier", r"\bprimalit", r"\bchiffr",
                 r"\bcrypt"],
            ],
            # Ces marqueurs ne manquent pas : ils PROUVENT un contenu
            # d'analyse. C'est exactement ce que le remplissage avait loge
            # sous cette capacite.
            "forbidden": [r"\\ln\b", r"convexit", r"variations de",
                          r"tableau de variations", r"point d'inflexion"],
        },
        "C4": {
            # Une equation diophantienne se reconnait a sa FORME : deux
            # inconnues entieres, coefficients entiers, second membre entier.
            # Exiger le mot « diophantienne » dans l'enonce reviendrait a
            # demander a l'exercice de se nommer lui-meme.
            "required": [
                [
                    r"\bdiophantienne\b",
                    r"\bB[ée]zout\b",
                    r"\d+\s*x\s*\+\s*\d+\s*y\s*=",
                    r"a\s*x\s*\+\s*b\s*y",
                ],
                # « entieres » porte un accent : un marqueur qui l'ignore ne
                # verrait pas la moitie des enonces du corpus.
                [r"enti[eèé]r", r"\\mathbb\{Z\}"],
            ],
        },
        "C5": {
            "required": [
                [r"\bB[ée]zout\b", r"au\s*\+\s*bv", r"\bPGCD\b"],
                [r"D[ée]montrer|Montrer|Prouver|d[ée]duire"],
            ],
        },
        "C6": {"required": [[r"\bGauss\b"], [r"D[ée]montrer|Montrer|Prouver"]]},
        "C7": {
            "required": [
                [r"\bpremiers?\b"],
                [r"\binfini", r"d[ée]composition", r"facteurs premiers"],
            ],
        },
        "C8": {"required": [[r"\bFermat\b"]]},
        "C9": {
            "required": [
                [r"\bdef\b", r"\bPython\b", r"\\begin\{python\}", r"\btexttt\b"],
                [r"Euclide", r"crible", r"[ÉE]ratosth", r"facteurs premiers",
                 r"\bB[ée]zout\b"],
            ],
        },
    },
    "TEXP-GRAPHES": {
        "C1": {
            "required": [
                [r"\bsommet", r"\bar[êe]te", r"\bdegr[ée]", r"\bgraphe\b"],
                [r"\bdegr[ée]", r"\bconnexe", r"\bcomplet", r"\bordre\b",
                 r"\bcha[îi]ne"],
            ],
            "forbidden": [r"convexit", r"tableau de variations"],
        },
        "C2": {
            "required": [
                [r"\bmod[ée]lis", r"\bgraphe\b"],
                [r"\bsommet", r"\bar[êe]te", r"\brencontre", r"\bliaison"],
            ],
        },
        "C3": {
            "required": [
                [r"matrice d'adjacence", r"\bmatrice\b"],
                [r"\badjacen", r"\bgraphe\b", r"\bsommet"],
            ],
        },
        "C4": {
            "required": [
                [r"\bchemins?\b", r"\blongueur\b"],
                [r"\bM\^?\{?[23n]", r"puissance", r"\bM\^2", r"matrice"],
            ],
        },
        "C5": {
            # Le corpus dit « chaine » aussi bien que « chemin », et note le
            # coefficient $(M^n)_{ij}$ sans employer le mot. Exiger le mot
            # reviendrait a refuser la notation mathematique.
            "required": [
                [r"D[ée]montrer|Montrer|r[ée]currence|V[ée]rifier"],
                [r"\bchemins?\b", r"\bcha[îi]nes?\b", r"coefficient",
                 r"\(M\^\{?\d*n?\}?\)_"],
            ],
        },
    },
    "TEXP-MATRICES-MARKOV": {
        "C1": {
            "required": [
                [r"\bmatrices?\b", r"\\begin\{pmatrix\}"],
                [r"\bproduit\b", r"\bsomme\b", r"\binverse", r"puissance",
                 r"\bA\^", r"\bAB\b"],
            ],
            "forbidden": [r"convexit", r"tableau de variations"],
        },
        "C2": {
            "required": [
                [r"\bmod[ée]lis", r"\bmatrice"],
                [r"\bmatrice", r"\\begin\{pmatrix\}"],
            ],
        },
        "C3": {
            "required": [
                [r"U_\{?n", r"suite de matrices", r"AU_n", r"A\s*U_n"],
                [r"\bsuite\b", r"r[ée]current", r"constante"],
            ],
        },
        "C4": {
            "required": [
                [r"\bMarkov\b", r"transition"],
                [r"\b[ée]tats?\b", r"graphe", r"distribution"],
            ],
        },
        "C5": {
            "required": [
                [r"\bMarkov\b", r"transition", r"\bT\^", r"\\pi_"],
                # La distribution se note `\pi_1`, `\pi_2`, `\pi_n` : exiger
                # l'indice `n` refuserait les enonces qui calculent des rangs.
                [r"distribution", r"\\pi_", r"transitions"],
            ],
        },
        "C6": {
            # « Rappeler pourquoi » demande la demonstration aussi surement
            # que « demontrer » : le corpus emploie les deux.
            "required": [
                [r"D[ée]montrer|Montrer|r[ée]currence|Justifier|Rappeler "
                 r"pourquoi|principe de la d[ée]monstration"],
                [r"\\pi_", r"distribution", r"transition"],
            ],
        },
        "C7": {
            "required": [
                [r"invariante?s?\b", r"\\pi\s*T\s*=\s*\\pi"],
                [r"distribution", r"\\pi"],
            ],
        },
    },
    "TEXP-COMPLEXES-ALGEBRE-GEOMETRIE": {
        "C1": {
            "required": [
                [UNITE_IMAGINAIRE, r"complexes?\b"],
                [r"\bcalculer\b", r"\bconjugu", r"\bproduit\b",
                 r"forme alg[ée]brique", r"partie r[ée]elle"],
            ],
            "forbidden": [r"convexit", r"tableau de variations"],
        },
        "C2": {
            "required": [
                [r"R[ée]soudre", r"\b[ée]quation", r"v[ée]rifiant"],
                [r"\bz\b", r"\\overline\{z\}", r"\\bar\s*z", UNITE_IMAGINAIRE],
            ],
        },
        "C3": {
            "required": [
                [r"D[ée]montrer|Montrer|r[ée]currence|D[ée]duire|"
                 r"d[ée]velopper|formule du bin[ôo]me"],
                [r"\\overline", r"conjugu", r"bin[ôo]me"],
            ],
        },
        "C4": {
            "required": [
                [r"\bmodule\b", r"\bargument\b", r"\baffixe\b"],
                [UNITE_IMAGINAIRE, r"complexe", r"\bOM\b"],
            ],
        },
        "C5": {
            "required": [
                [r"D[ée]montrer|Montrer|d[ée]duire"],
                [r"\bmodule\b", r"\|z\|", r"z\\overline\{z\}"],
            ],
        },
    },
    "TEXP-COMPLEXES-TRIGO-POLYNOMES": {
        "C1": {
            "required": [
                [r"forme trigonom", r"forme exponentielle", r"\\mathrm\{e\}\^",
                 r"\bexponentielle\b"],
                [r"\bmodule\b", r"\bargument\b", r"forme alg[ée]brique",
                 UNITE_IMAGINAIRE],
            ],
            "forbidden": [r"convexit", r"tableau de variations"],
        },
        "C2": {
            "required": [
                [r"\bEuler\b", r"\bMoivre\b"],
                [r"lin[ée]aris", r"puissance", r"\bcos\b", r"\bsin\b"],
            ],
        },
        "C3": {
            "required": [
                [r"D[ée]montrer|Montrer"],
                [r"produit scalaire", r"\\cos\(a", r"formule d'addition"],
            ],
        },
        "C4": {
            "required": [
                [r"R[ée]soudre", r"factoris", r"racine"],
                [r"\bz\^2", r"\bz\^3", r"polyn[ôo]me", r"degr[ée]"],
            ],
        },
        "C5": {
            "required": [
                [r"D[ée]montrer|Montrer|d[ée]duire"],
                [r"factoris", r"z\^n\s*-\s*a\^n", r"racines?\b"],
            ],
        },
        "C6": {
            "required": [
                [r"align", r"orthogonal", r"configuration", r"ensemble de points",
                 r"\baffixe"],
                [r"complexe", UNITE_IMAGINAIRE, r"\bz_", r"\baffixe"],
            ],
        },
        "C7": {
            "required": [
                [r"racines? [a-zé]+i?[èe]mes? de l'unit[ée]", r"de l'unit[ée]"],
                [r"polygone", r"\bcercle\b", r"\bsomme\b", r"r[ée]guli"],
            ],
        },
    },
    "TCOMPL-CALCULS-AIRES": {
        "C1": {"required": [[r"int[ée]grale", r"\\int"], [r"\baire\b", r"Chasles", r"sous la courbe"]]},
        "C2": {"required": [[r"encadr", r"estimer", r"rectangle"], [r"int[ée]grale", r"\\int", r"valeur moyenne"]]},
        "C3": {"required": [[r"\\int", r"int[ée]grale", r"valeur moyenne", r"\baire\b"], [r"Calculer", r"\baire\b"]]},
        "C4": {"required": [[r"primitive"], [r"forme usuelle", r"D[ée]terminer", r"reconnaissant", r"\bf\(x\)"]]},
        "C5": {"required": [[r"primitives?\b"], [r"constante", r"D[ée]montrer|Montrer|d[ée]duire"]]},
        "C6": {"required": [[r"\bF\(x\)", r"fonction int[ée]grale", r"\\int_a\^x"], [r"d[ée]riv", r"F'"]]},
    },
    "TCOMPL-CORRELATION-CAUSALITE": {
        "C1": {"required": [[r"nuage", r"point moyen"], [r"coordonn[ée]es", r"repr[ée]senter", r"\bG\b"]]},
        "C2": {"required": [[r"moindres carr[ée]s", r"r[ée]gression", r"corr[ée]lation"], [r"droite", r"covariance", r"coefficient"]]},
        "C3": {"required": [[r"changement de variable", r"\\ln", r"\bz\s*=\s*\\ln"], [r"ajustement", r"affine", r"mod[èe]le", r"lin[ée]aris", r"droite de r[ée]gression"]]},
        "C4": {"required": [[r"interpol", r"extrapol", r"estimer"], [r"ajustement", r"droite", r"\by\s*=\s*\d"]]},
        "C5": {"required": [[r"causalit[ée]", r"cause", r"corr[ée]lation"], [r"prouve|preuve|conclure|expliquer|variable tierce"]]},
    },
    "TCOMPL-ECHANTILLONNAGE": {
        "C1": {"required": [[r"Bernoulli", r"binomiale"], [r"situation", r"reconna[îi]tre", r"variable al[ée]atoire", r"loi\b"]]},
        "C2": {"required": [[r"Pascal", r"binomial"], [r"triangle", r"coefficient", r"\\binom"]]},
        "C3": {"required": [[r"P\(X", r"binomiale"], [r"Calculer", r"probabilit"]]},
        "C4": {"required": [[r"fluctuation", r"intervalle"], [r"binomiale", r"P\(X"]]},
        "C5": {"required": [[r"simul", r"Python", r"\\texttt"], [r"[ée]chantillon", r"moyenne"]]},
        "C6": {"required": [[r"esp[ée]rance", r"E\(X\)"], [r"D[ée]montrer|Montrer|calculer|d[ée]duire"]]},
        "C7": {"required": [[r"uniforme"], [r"esp[ée]rance", r"loi\b"]]},
    },
    "TCOMPL-INEGALITES": {
        "C1": {"required": [[r"Lorenz"], [r"courbe", r"construire", r"quantile", r"r[ée]partition"]]},
        "C2": {"required": [[r"Lorenz", r"L\(x\)"], [r"convexe", r"bissectrice", r"mod[ée]lis"]]},
        "C3": {"required": [[r"Gini"], [r"indice", r"in[ée]galit"]]},
        "C4": {"required": [[r"convexit[ée]", r"d[ée]riv[ée]e seconde", r"L''"], [r"Lorenz", r"L\(x\)", r"convexe"]]},
        "C5": {"required": [[r"\\int", r"int[ée]grale", r"aire"], [r"Gini", r"bissectrice", r"Lorenz"]]},
    },
    "TCOMPL-INFERENCE-BAYESIENNE": {
        "C1": {"required": [[r"probabilit"], [r"conditionnelle", r"arbre", r"sans remise", r"P\("]]},
        "C2": {"required": [[r"Bayes", r"a posteriori", r"P_\{?T"], [r"probabilit", r"test", r"pr[ée]valence"]]},
        "C3": {"required": [[r"P_M", r"P_\{?T", r"P_[A-Z]", r"a posteriori", r"conditionnement"], [r"distinguer|erreur|diff[ée]ren|sensibilit", r"P_[A-Z]\([A-Z]\).{0,200}P_[A-Z]\([A-Z]\)"]]},
        "C4": {"required": [[r"sensibilit[ée]", r"sp[ée]cificit[ée]", r"valeur pr[ée]dictive"], [r"test", r"probabilit", r"conditionnelle"]]},
        "C5": {"required": [[r"pr[ée]valence"], [r"valeur pr[ée]dictive", r"\bVPP\b", r"V\(p\)", r"d[ée]pistage"]]},
    },
    "TCOMPL-LOGARITHME-HISTORIQUE": {
        "C1": {"required": [[r"\\ln", r"logarithme"], [r"r[ée]ciproque", r"limite", r"d[ée]riv", r"exponentielle"]]},
        "C2": {"required": [[r"\\ln", r"logarithme"], [r"[ée]quation", r"in[ée]quation", r"[ée]quation fonctionnelle", r"Simplifier|R[ée]soudre"]]},
        "C3": {"required": [[r"seuil", r"\\ln", r"logarithme"], [r"g[ée]om[ée]trique", r"capital", r"placement", r"\bn\b"]]},
        "C4": {"required": [[r"D[ée]montrer|Montrer"], [r"\\ln\(ab\)", r"[ée]quation fonctionnelle", r"\\ln"]]},
        # « En deduire » a partir d'une relation admise EST une demarche de
        # demonstration : c'est la formulation ordinaire d'une deduction en
        # francais, et la capacite porte sur la preuve, pas sur le mot.
        "C5": {"required": [[r"D[ée]montrer|Montrer|[Ee]n d[ée]duire"], [r"d[ée]riv", r"1/x", r"\\dfrac\{1\}\{x\}"]]},
    },
    "TCOMPL-MODELES-EVOLUTION": {
        "C1": {"required": [[r"suite"], [r"mod[ée]lis", r"r[ée]currence", r"explicit", r"u_\{?n\s*\+\s*1\}?\s*="]]},
        "C2": {"required": [[r"g[ée]om[ée]trique"], [r"limite", r"somme", r"raison"]]},
        "C3": {"required": [[r"u_\{?n\+1\}?\s*=\s*f", r"r[ée]currente"], [r"graphi", r"conjectur", r"point fixe"]]},
        "C4": {"required": [[r"arithm[ée]tico", r"solution constante", r"suite constante"], [r"suite", r"r[ée]soudre|r[ée]solution|D[ée]terminer"]]},
        "C5": {"required": [[r"y'\s*=\s*ay", r"[ée]quation diff[ée]rentielle", r"y'\(t\)\s*=", r"y'\s*="], [r"solution", r"r[ée]soudre"]]},
        "C6": {"required": [[r"limite"], [r"suite", r"gendarmes", r"in[ée]galit"]]},
    },
    "TCOMPL-MODELES-FONCTION": {
        "C1": {"required": [[r"d[ée]riv", r"[a-z]'\(x\)"], [r"variation", r"limite", r"tableau"]]},
        "C2": {"required": [[r"tableau de variation", r"f\(x\)\s*=\s*k", r"solutions"], [r"[ée]quation", r"in[ée]quation", r"nombre de solutions"]]},
        "C3": {"required": [[r"balayage", r"dichotomie", r"encadrement", r"valeur approch"], [r"solution", r"[ée]quation"]]},
        "C4": {"required": [[r"convexe", r"concave", r"inflexion"], [r"graphi", r"courbe", r"reconna[îi]tre", r"lecture"]]},
        "C5": {"required": [[r"convexit[ée]", r"concavit[ée]", r"[a-z]''", r"d[ée]riv[ée]e seconde"], [r"[ée]tudier|Etudier|d[ée]duire"]]},
        "C6": {"required": [[r"nuage", r"point moyen"], [r"coordonn[ée]es", r"repr[ée]senter"]]},
        "C7": {"required": [[r"r[ée]gression", r"moindres carr[ée]s"], [r"droite", r"calcul", r"logiciel"]]},
    },
    "TCOMPL-TEMPS-ATTENTE": {
        "C1": {"required": [[r"g[ée]om[ée]trique"], [r"esp[ée]rance", r"m[ée]moire", r"loi\b"]]},
        "C2": {"required": [[r"g[ée]om[ée]trique", r"P\(X"], [r"Calculer", r"probabilit"]]},
        "C3": {"required": [[r"m[ée]moire"], [r"g[ée]om[ée]trique", r"P_\{?X", r"caract[ée]ris", r"m[ée]moire"]]},
        "C4": {"required": [[r"exponentielle"], [r"densit[ée]", r"r[ée]partition", r"esp[ée]rance", r"m[ée]moire"]]},
        "C5": {"required": [[r"densit[ée]"], [r"v[ée]rifier|probabilit|calculer"]]},
        "C6": {"required": [[r"esp[ée]rance", r"E\(X\)"], [r"exponentielle", r"int[ée]grale", r"\\int"]]},
        "C7": {"required": [[r"uniforme"], [r"densit[ée]", r"r[ée]partition", r"esp[ée]rance", r"variance"]]},
    },
    "TSPE-PROBABILITES": {
        "C3": {
            "required": [
                [r"binomiale", r"\\mathcal\{B\}", r"P\(X"],
                [r"seuil", r"comparer|comparaison", r"optimis", r"plus petit",
                 r"strat[ée]gie"],
            ],
            "forbidden": [r"convexit", r"point d'inflexion"],
        },
    },
    "TSPE-TRIGONOMETRIE": {
        "C1": {"required": [[r"\\cos", r"\\sin"], [r"[ée]quation", r"in[ée]quation", r"R[ée]soudre", r"D[ée]terminer les instants", r"sup[ée]rieure ou [ée]gale", r"inf[ée]rieure ou [ée]gale"]]},
        "C2": {"required": [[r"\\cos", r"\\sin"], [r"variation", r"optimum", r"maximum", r"[ée]tudier|Etudier"]]},
    },
}


def signature_for(chapter: str, capacity: str) -> dict[str, list] | None:
    return SIGNATURES.get(chapter, {}).get(capacity)


def declared_chapters() -> list[str]:
    return sorted(SIGNATURES)
