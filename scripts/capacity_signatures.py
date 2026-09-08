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
    # ------------------------------------------------------------------
    # Signatures ecrites pour les vingt-sept chapitres qui n'en avaient pas.
    # Sans elles, neuf cent treize rattachements de capacite n'etaient prouves
    # que par la declaration du META : une preuve d'identite, pas de contenu.
    # ------------------------------------------------------------------
    "1SPE-DERIVATION-GLOBAL": {
        "C1": {"required": [[r"d[ée]riv", r"[A-Za-z]'"],
                            [r"x\^", r"racine", r"\\sqrt", r"inverse", r"puissance", r"\\d?frac",
                             r"t\^", r"valeur absolue", r"\|x\|"]]},
        "C2": {"required": [[r"d[ée]riv", r"[A-Za-z]'"],
                            [r"produit", r"quotient", r"somme", r"\\d?frac", r"\\times", r"uv"]]},
        "C3": {"required": [[r"tableau de variations", r"variations", r"sens de variation"],
                            [r"signe", r"d[ée]riv", r"[A-Za-z]'"]]},
        "C4": {"required": [[r"extremum", r"maximum", r"minimum", r"stationnaire", r"maximal", r"minimal",
                             r"optim"],
                            [r"d[ée]riv", r"[A-Za-z]'", r"annul"]]},
        "C5": {"required": [[r"optimis", r"maximal", r"minimal", r"aire", r"volume",
                             r"co[ûu]t", r"b[ée]n[ée]fice", r"p[ée]rim[èe]tre", r"maximum",
                             r"minimum", r"vitesse", r"mobile"],
                            [r"d[ée]riv", r"[A-Za-z]'"]]},
    },
    "1SPE-DERIVATION-LOCAL": {
        "C1": {"required": [[r"taux de variation", r"s[ée]cante"],
                            [r"pente", r"taux", r"\\frac\{f\("]]},
        "C2": {"required": [[r"nombre d[ée]riv", r"[A-Za-z]'\s*\(", r"ce nombre", r"taux de variation"],
                            [r"pente", r"vitesse", r"instantan", r"interpr[ée]t", r"taux de variation",
                             r"tend", r"limite", r"en d[ée]duire", r"\\dfrac\{f\(",
                             r"\+\s*h\)"]]},
        "C3": {"required": [[r"tangente"],
                            [r"graphi", r"lire", r"courbe", r"construire", r"tracer"]]},
        "C4": {"required": [[r"tangente"],
                            [r"[ée]quation", r"y\s*=", r"f'\("]]},
        "C5": {"required": [[r"approximation", r"approch"],
                            [r"f\(a\s*\+\s*h\)", r"voisinage", r"affine", r"lin[ée]aire", r"tangente",
                             r"erreur"]]},
    },
    "1SPE-EXPONENTIELLE": {
        "C1": {"required": [[r"exponentielle", r"\\mathrm\{e\}\^", r"\\exp"],
                            [r"d[ée]riv", r"[A-Za-z]'", r"unique", r"[ée]gale [àa] sa d[ée]riv"]]},
        "C2": {"required": [[r"exponentielle", r"\\mathrm\{e\}\^", r"\\exp"],
                            [r"produit", r"somme", r"puissance", r"quotient", r"inverse",
                             r"simplifi", r"propri[ée]t", r"\\times", r"\\d?frac", r"forme",
                             r"[Ff]actoris", r"d[ée]velopp", r"[ée]quation", r"in[ée]quation",
                             r"\\mathrm\{e\}\^\{2x\}"]]},
        "C3": {"required": [[r"exponentielle", r"\\mathrm\{e\}\^", r"\\exp"],
                            [r"croissance", r"signe", r"courbe", r"variations", r"g[ée]om[ée]trique",
                             r"ordre", r"[Rr]anger", r"comparer", r"positi", r"in[ée]quation",
                             r"\\leqslant", r"\\geqslant"]]},
        "C4": {"required": [[r"exponentielle", r"\\mathrm\{e\}\^", r"\\exp"],
                            [r"d[ée]riv", r"[A-Za-z]'"]]},
        "C5": {"required": [[r"exponentielle", r"\\mathrm\{e\}\^", r"\\exp"],
                            [r"croissance", r"d[ée]croissance", r"mod[èe]l", r"[ée]volution",
                             r"population", r"d[ée]sint[ée]gration", r"refroidissement",
                             r"concentration", r"capital", r"courbe", r"croiss", r"d[ée]croiss",
                             r"quantit", r"valeur initiale", r"taux"]]},
    },
    "1SPE-GEOMETRIE-REPEREE": {
        "C1": {"required": [[r"[ée]quation cart[ée]sienne", r"ax\s*\+\s*by", r"a\s*x\s*\+\s*b\s*y",
                             r"[ée]quation"],
                            [r"droite"]]},
        "C2": {"required": [[r"vecteur normal", r"vecteur directeur", r"\\vec\{n\}", r"parall[èe]l",
                             r"perpendiculaire", r"coefficient directeur", r"m[ée]diatrice"],
                            [r"droite", r"[ée]quation"]]},
        "C3": {"required": [[r"cercle"],
                            [r"rayon", r"centre", r"[ée]quation", r"\)\^2\s*\+",
                             r"int[ée]rieur", r"ext[ée]rieur"]]},
        "C4": {"required": [[r"position relative", r"parall[èe]l", r"intersection",
                             r"tangen", r"s[ée]cant", r"distance"],
                            [r"droite", r"cercle"]]},
        "C5": {"required": [[r"rep[èe]re", r"coordonn", r"[A-Z]\(\s*-?\d"],
                            [r"distance", r"milieu", r"droite", r"cercle", r"triangle",
                             r"parall[èe]l", r"orthogon", r"aire", r"quadrilat", r"nature"]]},
    },
    "1SPE-PROBA-COND": {
        "C1": {"required": [[r"P_\{?[A-Z]", r"P_\{", r"probabilit[ée] conditionnelle", r"sachant", r"parmi",
                             r"tableau", r"tabular"],
                            [r"probabilit", r"P\(", r"P_"]]},
        "C2": {"required": [[r"arbre"], [r"pond[ée]r", r"branche", r"probabilit"]]},
        "C3": {"required": [[r"probabilit[ée]s totales", r"partition", r"\\overline\{", r"[Ss]inon",
                             r"arbre", r"fournisseur", r"provien", r"origine", r"parmi",
                             r"L_\d", r"lots?\b"],
                            [r"probabilit", r"P\(", r"P_", r"tabular", r"effectif"]]},
        "C4": {"required": [[r"ind[ée]pendan"], [r"probabilit", r"[ée]v[ée]nement", r"P\("]]},
        "C5": {"required": [[r"probabilit", r"P\(", r"P_"],
                            [r"entreprise", r"usine", r"test", r"maladie", r"client",
                             r"sondage", r"classe", r"urne", r"lot", r"machine",
                             r"patient", r"[ée]l[èe]ve", r"atelier", r"transport",
                             r"g[ée]n[ée]tique", r"all[èe]le", r"enfant", r"parent",
                             r"pi[èe]ce", r"boule", r"jeu", r"\\og", r"pluie", r"m[ée]t[ée]o",
                             r"sensibilit", r"sp[ée]cificit", r"pr[ée]valence"]]},
    },
    "1SPE-PRODUIT-SCALAIRE": {
        "C1": {"required": [[r"produit scalaire", r"\\cdot", r"\\vec"],
                            [r"projection", r"analytique", r"coordonn", r"norme", r"\\vec",
                             r"\\\|"]]},
        "C2": {"required": [[r"produit scalaire", r"\\cdot", r"\\\|", r"\\vec"],
                            [r"bilin[ée]ar", r"sym[ée]tri", r"norme", r"d[ée]velopp", r"identit[ée]",
                             r"propri[ée]t", r"\\\|"]]},
        "C3": {"required": [[r"orthogon", r"perpendiculaire", r"angle", r"rectangle"],
                            [r"produit scalaire", r"\\cdot", r"\\vec", r"coordonn",
                             r"[A-Z]\(\s*-?\d"]]},
        "C4": {"required": [[r"m[ée]diatrice", r"hauteur", r"aire", r"triangle", r"cercle",
                             r"droite", r"lieu", r"projet"],
                            [r"produit scalaire", r"\\cdot", r"\\vec", r"coordonn", r"[A-Z]\(\s*-?\d"]]},
        "C5": {"required": [[r"Al-Kashi", r"al-Kashi", r"triangle", r"\\widehat", r"quadrilat", r"diagonale"],
                            [r"c[ôo]t[ée]", r"angle", r"\\cos", r"longueur", r"BC", r"AB"]]},
    },
    "1SPE-SECOND-DEGRE": {
        "C1": {"required": [[r"second degr[ée]", r"trin[ôo]me", r"polyn[ôo]me", r"x\^2", r"x\^\{2\}"],
                            [r"forme canonique", r"forme factoris", r"forme d[ée]velopp",
                             r"a\s*x\^2", r"reconna", r"passer"]]},
        "C2": {"required": [[r"sommet", r"axe de sym[ée]trie", r"parabole", r"maximal", r"maximum",
                             r"minimal", r"minimum", r"forme canonique"],
                            [r"variations", r"tableau", r"coordonn", r"x\^2", r"trin[ôo]me",
                             r"aire"]]},
        "C3": {"required": [[r"discriminant", r"\\Delta", r"[Rr][ée]soudre", r"racine", r"annul"],
                            [r"racine", r"solution", r"[ée]quation"]]},
        "C4": {"required": [[r"factoris", r"racine", r"\(x\s*[-+]\s*\d"],
                            [r"trin[ôo]me", r"second degr", r"racine", r"x\^2", r"signe"]]},
        "C5": {"required": [[r"in[ée]quation", r"\\geqslant", r"\\leqslant", r"\\geq", r"\\leq", r"signe"],
                            [r"second degr", r"signe", r"trin[ôo]me", r"x\^2", r"t\^2", r"hauteur"]]},
        "C6": {"required": [[r"aire", r"p[ée]rim[èe]tre", r"b[ée]n[ée]fice", r"co[ûu]t", r"hauteur",
                             r"trajectoire", r"enclos", r"rectangle", r"recette", r"profit"],
                            [r"maximal", r"minimal", r"optim", r"sommet"]]},
        "C7": {"required": [[r"somme", r"produit"], [r"racine"]]},
        "C8": {"required": [[r"signe"], [r"factoris", r"tableau de signes"]]},
    },
    "1SPE-SUITES": {
        "C1": {"required": [[r"u_\{?n", r"suite"],
                            [r"terme", r"calculer", r"r[ée]currence", r"explicit"]]},
        "C2": {"required": [[r"arithm[ée]tique"], [r"suite", r"raison", r"terme g[ée]n[ée]ral"]]},
        "C3": {"required": [[r"g[ée]om[ée]trique", r"raison", r"\\times\s*u_", r"q\^", r"quotient"],
                            [r"suite", r"raison", r"terme g[ée]n[ée]ral", r"u_\{?n"]]},
        "C4": {"required": [[r"somme"],
                            [r"suite", r"premiers entiers", r"g[ée]om[ée]trique", r"q\^", r"S_"]]},
        "C5": {"required": [[r"variation", r"croissante", r"d[ée]croissante", r"monotone"],
                            [r"suite", r"u_\{?n"]]},
        "C6": {"required": [[r"suite", r"u_\{?n"],
                            [r"population", r"capital", r"placement", r"[ée]volution", r"mod[èe]l",
                             r"ann[ée]e", r"mois", r"abonn", r"stock", r"d[ée]bit", r"jour",
                             r"semaine", r"volume", r"quantit", r"eau", r"r[ée]servoir"]]},
        "C7": {"required": [[r"Python", r"def\s", r"lstinline", r"python"],
                            [r"suite", r"u_\{?n", r"seuil", r"somme", r"terme"]]},
        "C8": {"required": [[r"limite", r"tend vers", r"\\lim", r"\\to", r"converge", r"\\infty",
                             r"devient grand", r"s'approche", r"proche de", r"grand",
                             r"long terme", r"comportement", r"stabilis"],
                            [r"suite", r"u_\{?n"]]},
    },
    "1SPE-TRIGONOMETRIE": {
        "C1": {"required": [[r"cercle trigonom[ée]trique", r"radian", r"degr[ée]", r"mesure principale",
                             r"\\pi"],
                            [r"angle", r"\\pi", r"[Cc]onver", r"orient", r"mesure"]]},
        "C2": {"required": [[r"\\cos", r"\\sin"],
                            [r"remarquable", r"\\pi", r"cercle", r"angle associ", r"identit[ée] fondamentale",
                             r"\\cos\^2"]]},
    },
    "1SPE-VARIABLES-ALEATOIRES": {
        "C1": {"required": [[r"variable al[ée]atoire", r"P\(X", r"loi de", r"\bX\s*=", r"variable \$X\$",
                             r"tableau de loi"],
                            [r"loi de probabilit", r"P\(X", r"[ée]v[ée]nement", r"\bloi\b",
                             r"tableau"]]},
        "C2": {"required": [[r"esp[ée]rance", r"E\(X", r"variance", r"V\(X", r"[ée]cart type",
                             r"\\sigma"],
                            [r"variable al[ée]atoire", r"X\b", r"loi"]]},
        "C3": {"required": [[r"Bernoulli", r"succ[èe]s", r"lance", r"tirage", r"[ée]preuve"],
                            [r"arbre", r"r[ée]p[ée]tition", r"[ée]preuve", r"ind[ée]pendant",
                             r"issue", r"loi", r"X_\d", r"lin[ée]arit"]]},
        "C4": {"required": [[r"aX\s*\+\s*b", r"lin[ée]arit", r"E\(aX", r"\d+X\s*[-+]"],
                            [r"esp[ée]rance", r"E\("]]},
        "C5": {"required": [[r"jeu", r"assurance", r"d[ée]cision", r"mise", r"gain", r"pari",
                             r"client", r"lot", r"prime", r"joueur", r"paie"],
                            [r"esp[ée]rance", r"variable al[ée]atoire", r"probabilit",
                             r"E\(", r"loi"]]},
        "C6": {"required": [[r"Python", r"def\s", r"random", r"simul"],
                            [r"[ée]chantillon", r"moyenne", r"variable al[ée]atoire"]]},
        "C7": {"required": [[r"fluctuation", r"[ée]chantillon"],
                            [r"moyenne", r"esp[ée]rance", r"\\sigma", r"[ée]cart"]]},
    },
    "TSPE-CONTINUITE": {
        "C1": {"required": [[r"valeurs interm[ée]diaires", r"TVI", r"admet", r"unique", r"s'annule",
                             r"existe", r"unicit", r"atteint", r"seuil", r"exactement",
                             r"nombre de solutions", r"racine"],
                            [r"solution", r"[ée]quation", r"continue", r"unicit", r"encadr", r"racine",
                             r"nul"]]},
        "C2": {"required": [[r"_\{n\s*\+\s*1\}", r"r[ée]currence", r"f\(u_"],
                            [r"continue", r"intervalle", r"suite", r"stable", r"f\(x\)\s*=", r"u_\{?n"]]},
    },
    "TSPE-DERIVATION-CONVEXITE": {
        "C1": {"required": [[r"compos[ée]e", r"\\circ", r"v\s*o\s*u", r"\\ln\s*\\?!?\s*\\?l?e?f?t?\(",
                             r"\\mathrm\{e\}\^\{", r"\\sqrt\{", r"\)\^\d", r"\)\^\{"],
                            [r"d[ée]riv", r"[A-Za-z]'"]]},
        "C2": {"required": [[r"variations", r"limite", r"[ée]tude", r"[ÉE]tudier", r"volume", r"maximal",
                             r"optimum", r"maximum", r"co[ûu]t", r"minimum", r"marginal"],
                            [r"d[ée]riv", r"[A-Za-z]'", r"x\^", r"\\ln", r"\\mathrm\{e\}",
                             r"volume", r"\\d?frac"]]},
        "C3": {"required": [[r"convexit", r"convexe", r"concave", r"\\mathrm\{e\}\^", r"\\ln", r"tangente"],
                            [r"in[ée]galit", r"\\geqslant", r"\\leqslant", r"\\geq", r"\\leq",
                             r"[Dd][ée]montrer"]]},
        "C4": {"required": [[r"allure", r"esquisser", r"courbe"],
                            [r"tableau de variations", r"f''", r"[A-Za-z]'", r"variations"]]},
        "C5": {"required": [[r"convexit", r"concav", r"inflexion"],
                            [r"graphi", r"lire", r"intervalle", r"courbe", r"probl[èe]me", r"minimum",
                             r"[Rr][ée]soudre", r"unique"]]},
        "C6": {"required": [[r"tangente", r"f'\(a\)\(x", r"f\(a\)\s*\+"],
                            [r"convex", r"f''", r"au-dessus"]]},
    },
    "TSPE-CALCUL-INTEGRAL": {
        "C1": {"required": [[r"encadr", r"estim", r"rectangle", r"graphi"],
                            [r"int[ée]grale", r"\\int", r"valeur moyenne"]]},
        "C2": {"required": [[r"primitive", r"parties", r"\\int"],
                            [r"int[ée]grale", r"\\int", r"[Cc]alculer"]]},
        "C3": {"required": [[r"majorer", r"minorer", r"comparaison", r"\\leqslant", r"\\geqslant",
                             r"\\leq", r"\\geq"],
                            [r"int[ée]grale", r"\\int"]]},
        "C4": {"required": [[r"aire"], [r"courbe", r"int[ée]grale", r"\\int"]]},
        "C5": {"required": [[r"suite", r"[IJ]_\{?n", r"r[ée]currence"],
                            [r"int[ée]grale", r"\\int"]]},
        "C6": {"required": [[r"int[ée]grale", r"\\int", r"valeur moyenne"],
                            [r"d[ée]bit", r"puissance", r"[ée]nergie", r"vitesse", r"distance",
                             r"co[ûu]t", r"population", r"concentration", r"masse",
                             r"consommation", r"pollu", r"temp[ée]rature"]]},
        "C7": {"required": [[r"fonction int[ée]grale", r"\\int_\w\^x", r"[A-Z]\(x\)\s*=\s*\\displaystyle",
                             r"[A-Z]\(x\)\s*=\s*\\int"],
                            [r"primitive", r"d[ée]riv", r"[Dd][ée]montrer", r"[Mm]ontrer",
                             r"aire"]]},
        "C8": {"required": [[r"parties"],
                            [r"[Dd][ée]montrer", r"d[ée]riv[ée]e d'un produit", r"\(uv\)'",
                             r"formule"]]},
    },
    "TSPE-COMBINATOIRE": {
        "C1": {"required": [[r"arbre", r"tableau", r"diagramme", r"ensemble", r"sous-ensemble"],
                            [r"d[ée]nombr", r"[Cc]ombien", r"probabilit", r"nombre total",
                             r"combinaison"]]},
        "C2": {"required": [[r"d[ée]nombr", r"combinaison", r"permutation", r"arrangement",
                             r"\\d?binom", r"parmi", r"nombre de mains", r"tirage"],
                            [r"principe", r"multiplicatif", r"additif", r"[Cc]ombien",
                             r"[Cc]alculer", r"\\binom", r"factorielle"]]},
        "C3": {"required": [[r"\\d?binom", r"parmi", r"sous-ensemble"],
                            [r"2\^", r"somme", r"[Ss]ommant", r"nombre total"]]},
        "C4": {"required": [[r"Pascal"], [r"\\binom", r"parmi", r"relation", r"triangle"]]},
    },
    "TSPE-GEOMETRIE-ESPACE": {
        "C1": {"required": [[r"combinaison lin[ée]aire", r"\\vec"],
                            [r"repr[ée]sent", r"figure", r"graphi", r"construire", r"placer"]]},
        "C2": {"required": [[r"d[ée]compos", r"combinaison lin[ée]aire"],
                            [r"\\vec", r"vecteur"]]},
        "C3": {"required": [[r"position relative", r"parall[èe]l", r"s[ée]cant", r"coplanaire",
                             r"intersection"],
                            [r"droite", r"plan"]]},
        "C4": {"required": [[r"base"], [r"\\vec", r"vecteur", r"plan", r"espace"]]},
        "C5": {"required": [[r"coordonn"], [r"\\vec", r"vecteur", r"base", r"figure"]]},
        "C6": {"required": [[r"align", r"colin[ée]a", r"parall[èe]l", r"coplanaire"],
                            [r"\\vec", r"point", r"vecteur"]]},
        "C7": {"required": [[r"produit scalaire", r"\\cdot"],
                            [r"orthogon", r"angle", r"longueur", r"espace"]]},
        "C8": {"required": [[r"distance"], [r"projet[ée]", r"orthogonal", r"plan", r"droite"]]},
        "C9": {"required": [[r"longueur", r"angle", r"aire", r"volume"],
                            [r"espace", r"t[ée]tra[èe]dre", r"cube", r"pyramide", r"triangle",
                             r"plan", r"pav[ée]"]]},
        "C10": {"required": [[r"orthogon", r"lieu"], [r"espace", r"plan", r"droite", r"point"]]},
        "C11": {"required": [[r"projet[ée]"],
                             [r"plus proche", r"distance", r"minimal", r"[Dd][ée]montrer", r"MH", r"MN",
                             r"sup[ée]rieur", r"[Jj]ustifier"]]},
        "C12": {"required": [[r"param[ée]tri"],
                             [r"droite", r"\\begin\{cases\}", r"t\s*\\in", r"\bt\b"]]},
        "C13": {"required": [[r"[ée]quation cart[ée]sienne", r"ax\s*\+\s*by\s*\+\s*cz"],
                             [r"plan", r"vecteur normal"]]},
        "C14": {"required": [[r"projet[ée]"], [r"coordonn", r"[Cc]alculer"]]},
        "C15": {"required": [[r"syst[èe]me", r"intersection", r"param[ée]tri"],
                            [r"[ée]quation", r"r[ée]soudre", r"lin[ée]aire"]]},
        "C16": {"required": [[r"[Dd][ée]montrer", r"[Mm]ontrer", r"[ÉEée]tabli"],
                             [r"[ée]quation cart[ée]sienne", r"plan", r"vecteur normal"]]},
    },
    "TSPE-LIMITES-FONCTIONS": {
        "C1": {"required": [[r"limite", r"\\lim"],
                            [r"croissances? compar", r"factoris", r"op[ée]ration", r"usuelle",
                             r"\\infty", r"pr[ée]pond", r"\\d?frac", r"\\to"]]},
        "C2": {"required": [[r"asymptote", r"\bAH\b", r"\bAV\b"],
                            [r"limite", r"\\lim", r"horizontale", r"verticale", r"position",
                             r"courbe", r"domaine", r"\\mathcal\{C\}"]]},
        "C3": {"required": [[r"croissances? compar", r"\\mathrm\{e\}\^"],
                            [r"exponentielle", r"\\mathrm\{e\}\^", r"x\^", r"[Dd][ée]montrer",
                             r"\\lim"]]},
    },
    "TSPE-LOGARITHME": {
        "C1": {"required": [[r"\\ln", r"logarithme", r"\\mathrm\{e\}\^"],
                            [r"propri[ée]t", r"[ée]quation", r"in[ée]quation", r"produit",
                             r"quotient", r"puissance", r"transform", r"simplifi"]]},
        "C2": {"required": [[r"\\ln", r"logarithme", r"\\mathrm\{e\}\^"],
                            [r"probl[èe]me", r"seuil", r"mod[èe]l", r"population", r"capital",
                             r"d[ée]sint[ée]gration", r"pH", r"d[ée]cibel", r"placement",
                             r"ann[ée]e", r"concentration", r"bact[ée]rie", r"heure"]]},
        "C3": {"required": [[r"\\ln"],
                            [r"d[ée]riv", r"\\frac\{1\}\{x\}", r"1/x", r"[Dd][ée]montrer"]]},
        "C4": {"required": [[r"x\s*\\ln", r"\\ln x"], [r"limite", r"\\lim"]]},
    },
    "TSPE-PRIMITIVES-EQDIFF": {
        "C1": {"required": [[r"primitive"],
                            [r"r[ée]f[ée]rence", r"u'", r"forme", r"\\circ", r"[Cc]alculer",
                             r"[Dd][ée]terminer"]]},
        "C2": {"required": [[r"[ée]quation diff[ée]rentielle", r"[A-Za-z]'\s*\(?t?\)?\s*="],
                            [r"solution", r"constante", r"a\s*y\s*\+\s*b", r"r[ée]soudre",
                             r"refroidissement", r"Newton"]]},
        "C3": {"required": [[r"[ée]quation diff[ée]rentielle", r"y'\s*="],
                            [r"particuli", r"toutes les solutions"]]},
        "C4": {"required": [[r"primitive"],
                            [r"constante", r"[Dd][ée]montrer", r"diff[èe]rent"]]},
        "C5": {"required": [[r"y'\s*=\s*a\s*y", r"[ée]quation diff[ée]rentielle"],
                            [r"[Dd][ée]montrer", r"toutes les solutions", r"r[ée]solution",
                             r"[Rr][ée]soudre", r"y\(0\)", r"solution telle que", r"\(E\)",
                             r"en d[ée]duire", r"solution"]]},
    },
    "TSPE-SUITES-LIMITES": {
        "C1": {"required": [[r"convergen", r"divergen", r"limite", r"\\lim"],
                            [r"comparaison", r"gendarmes", r"monotone", r"born[ée]e", r"suite"]]},
        "C2": {"required": [[r"r[ée]currence"],
                            [r"[Dd][ée]montrer", r"[Mm]ontrer", r"initialisation", r"h[ée]r[ée]dit"]]},
        "C3": {"required": [[r"suite", r"[A-Za-z]_\{?n"],
                            [r"population", r"capital", r"[ée]volution", r"mod[èe]l", r"ann[ée]e",
                             r"mois", r"d[ée]bit", r"concentration", r"abonn", r"stock",
                             r"jour", r"semaine", r"volume", r"eau", r"r[ée]servoir",
                             r"quantit", r"temp[ée]rature", r"four", r"minute"]]},
        "C4": {"required": [[r"croissante"], [r"major", r"\\infty", r"[Dd][ée]montrer"]]},
        "C5": {"required": [[r"Bernoulli", r"q\^", r"\)\^n", r"\^\{n\}"],
                            [r"in[ée]galit", r"r[ée]currence", r"limite", r"\\lim", r"cours"]]},
        "C6": {"required": [[r"comparaison", r"\\geqslant", r"\\geq", r"\\leqslant", r"\\leq",
                             r"minor", r"major"],
                            [r"divergen", r"\\infty", r"th[ée]or[èe]me", r"\\lim"]]},
        "C7": {"required": [[r"exponentielle", r"\\mathrm\{e\}"],
                            [r"limite", r"\\lim", r"\\infty", r"[Dd][ée]montrer"]]},
    },
    "1NSI-ALGO-PARCOURS-TRIS": {
        "C1": {"required": [[r"recherche", r"occurrence", r"parcours"],
                            [r"tableau", r"liste", r"indice"]]},
        "C2": {"required": [[r"maximum", r"minimum", r"extremum", r"moyenne"],
                            [r"tableau", r"liste", r"parcours"]]},
        "C3": {"required": [[r"insertion"], [r"tri", r"tableau"]]},
        "C4": {"required": [[r"invariant"], [r"insertion", r"tri"]]},
        "C5": {"required": [[r"s[ée]lection"], [r"tri", r"tableau"]]},
        "C6": {"required": [[r"invariant"], [r"s[ée]lection", r"tri"]]},
    },
    "1NSI-TYPES-CONSTRUITS": {
        "C5": {"required": [[r"mutable", r"effet de bord", r"alias", r"modifi"],
                            [r"liste", r"dictionnaire", r"affectation", r"objet"]]},
    },
    "TNSI-ALGORITHMIQUE": {
        "C1": {"required": [[r"taille"], [r"arbre", r"n\\oe", r"noeud"]]},
        "C2": {"required": [[r"hauteur"], [r"arbre", r"n\\oe", r"noeud"]]},
        "C3": {"required": [[r"infixe", r"pr[ée]fixe", r"suffixe"], [r"arbre", r"parcours"]]},
        "C4": {"required": [[r"largeur"], [r"arbre", r"file"]]},
        "C5": {"required": [[r"recherch"], [r"arbre", r"cl[ée]"]]},
        "C6": {"required": [[r"ins[ée]r"], [r"arbre", r"cl[ée]"]]},
        "C7": {"required": [[r"largeur", r"_largeur", r"BFS"],
                            [r"graphe", r"file", r"sommet"]]},
        "C8": {"required": [[r"profondeur"], [r"graphe", r"pile", r"sommet"]]},
        "C9": {"required": [[r"cycle"], [r"graphe", r"sommet"]]},
        "C10": {"required": [[r"chemin"], [r"graphe", r"sommet"]]},
        "C11": {"required": [[r"diviser pour r[ée]gner", r"dpr"],
                             [r"r[ée]cursi", r"moiti", r"dichotom"]]},
        "C12": {"required": [[r"programmation dynamique", r"m[ée]mo[ïi]sation", r"memo"],
                             [r"sous-probl[èe]me", r"tableau", r"r[ée]currence", r"recalcul"]]},
        "C13": {"required": [[r"Boyer-Moore", r"boyer_moore"],
                             [r"motif", r"d[ée]calage", r"texte"]]},
    },
    "TNSI-ARCHITECTURES-MATERIELLES-SY": {
        "C1": {"required": [[r"syst[èe]me sur puce", r"SoC", r"puce"],
                            [r"composant", r"processeur", r"m[ée]moire", r"int[ée]gration"]]},
        "C2": {"required": [[r"processus"],
                            [r"cr[ée]ation", r"cr[ée]e", r"parent", r"enfant", r"arbre"]]},
        "C3": {"required": [[r"ordonnance", r"tourniquet", r"tranche"], [r"processus"]]},
        "C4": {"required": [[r"interblocage", r"attente"], [r"processus", r"ressource"]]},
        "C5": {"required": [[r"routage", r"route", r"paquet"],
                            [r"protocole", r"r[ée]seau", r"co[ûu]t", r"RIP", r"OSPF"]]},
        "C6": {"required": [[r"chiffr"], [r"sym[ée]trique", r"asym[ée]trique", r"cl[ée]"]]},
        "C7": {"required": [[r"HTTPS", r"cl[ée] sym[ée]trique"],
                            [r"asym[ée]trique", r"[ée]change", r"cl[ée] publique", r"cl[ée] priv"]]},
    },
    "TNSI-BASES-DE-DONNEES": {
        "C1": {"required": [[r"relation", r"attribut", r"domaine", r"cl[ée]", r"sch[ée]ma"],
                            [r"mod[èe]le relationnel", r"table", r"base"]]},
        "C2": {"required": [[r"structure", r"contenu"],
                            [r"CREATE TABLE", r"INSERT", r"base", r"table"]]},
        "C3": {"required": [[r"anomalie", r"redondance", r"d[ée]pendance", r"deux fois", r"faute de frappe",
                             r"unique table", r"d[ée]coupage"],
                            [r"sch[ée]ma", r"table", r"base"]]},
        "C4": {"required": [[r"SGBD"],
                            [r"persistance", r"concurrence", r"efficacit", r"s[ée]curis",
                             r"service"]]},
        "C5": {"required": [[r"SELECT"],
                            [r"FROM", r"WHERE", r"ORDER BY", r"composant", r"clause"]]},
        "C6": {"required": [[r"SELECT"], [r"FROM"]]},
        "C7": {"required": [[r"WHERE"], [r"SELECT"]]},
        "C8": {"required": [[r"JOIN"], [r"SELECT"]]},
        "C9": {"required": [[r"ORDER BY"], [r"SELECT"]]},
        "C10": {"required": [[r"INSERT"], [r"INTO", r"VALUES"]]},
        "C11": {"required": [[r"UPDATE"], [r"SET"]]},
        "C12": {"required": [[r"DELETE"], [r"FROM", r"WHERE"]]},
    },
    "TNSI-HISTOIRE-INFORMATIQUE": {
        "C1": {"required": [[r"\b1[89]\d\d\b", r"\b20[0-2]\d\b", r"chronolog", r"si[èe]cle"],
                            [r"Turing", r"ARPANET", r"ordinateur", r"informatique",
                             r"[ée]v[ée]nement"]]},
        "C2": {"required": [[r"logiciel", r"mat[ée]riel"],
                            [r"[ée]volution", r"r[ôo]le", r"g[ée]n[ée]ra", r"sp[ée]cialis",
                             r"couche"]]},
    },
    "TNSI-LANGAGES-ET-PROGRAMMATION": {
        "C1": {"required": [[r"programme"],
                            [r"donn[ée]e", r"argument", r"exec", r"source", r"compilateur",
                             r"interpr[ée]teur"]]},
        "C2": {"required": [[r"calculabilit", r"langage"],
                            [r"interpr[ée]teur", r"simul", r"ind[ée]pendan", r"m[êe]me"]]},
        "C3": {"required": [[r"arr[êe]t"],
                            [r"ind[ée]cidable", r"diagonal", r"contradiction"]]},
        "C4": {"required": [[r"r[ée]cursi"], [r"def\s", r"fonction", r"appel"]]},
        "C5": {"required": [[r"r[ée]cursi"],
                            [r"appel", r"cas de base", r"trace", r"analys", r"d[ée]rouler"]]},
        "C6": {"required": [[r"biblioth[èe]que", r"module", r"import", r"API"],
                            [r"utilis", r"appel", r"fonction"]]},
        "C7": {"required": [[r"documentation", r"docstring", r"help\("],
                            [r"module", r"fonction", r"biblioth[èe]que", r"API"]]},
        "C8": {"required": [[r"module"],
                            [r"document", r"docstring", r"__name__", r"cr[ée]er"]]},
        "C9": {"required": [[r"paradigme", r"imp[ée]rati", r"fonctionnel", r"objet"],
                            [r"exemple", r"distinguer", r"style", r"comparer"]]},
        "C10": {"required": [[r"paradigme", r"imp[ée]rati", r"fonctionnel", r"objet", r"style"],
                             [r"choisir", r"adapt", r"champ", r"comparer", r"r[ée][ée]crire"]]},
        "C11": {"required": [[r"bug", r"erreur", r"d[ée]faut"],
                             [r"cause", r"effet de bord", r"indice", r"flottant",
                              r"d[ée]bogage", r"corriger", r"mutable"]]},
    },
    "TNSI-STRUCTURES-DONNEES": {
        "C1": {"required": [[r"interface", r"sp[ée]cifi"],
                            [r"op[ée]ration", r"pr[ée]condition", r"structure"]]},
        "C2": {"required": [[r"interface"], [r"impl[ée]mentation"]]},
        "C3": {"required": [[r"impl[ée]mentation"],
                            [r"deux", r"plusieurs", r"class\s", r"autre"]]},
        "C4": {"required": [[r"class\s"], [r"def\s", r"__init__", r"attribut", r"m[ée]thode"]]},
        "C5": {"required": [[r"attribut", r"m[ée]thode"], [r"class\s", r"self", r"objet"]]},
        "C6": {"required": [[r"pile", r"file", r"FIFO", r"LIFO"],
                            [r"empiler", r"d[ée]piler", r"enfiler", r"d[ée]filer", r"structure"]]},
        "C7": {"required": [[r"structure"],
                            [r"choisir", r"adapt", r"pile", r"file", r"dictionnaire", r"liste"]]},
        "C8": {"required": [[r"recherche"], [r"dictionnaire", r"liste"]]},
        "C9": {"required": [[r"arbre", r"arborescen"],
                            [r"situation", r"mod[ée]lis", r"hi[ée]rarch", r"identifier",
                             r"peigne", r"binaire", r"construire"]]},
        "C10": {"required": [[r"taille", r"hauteur", r"feuille"], [r"arbre"]]},
        "C11": {"required": [[r"graphe"],
                             [r"mod[ée]lis", r"situation", r"sommet", r"ar[êe]te"]]},
        "C12": {"required": [[r"matrice"], [r"graphe", r"adjacen"]]},
        "C13": {"required": [[r"successeur", r"adjacence", r"dictionnaire"], [r"graphe"]]},
        "C14": {"required": [[r"matrice", r"successeur"],
                             [r"convertir", r"passer", r"repr[ée]sentation", r"autre"]]},
    },
    "TSPE-PROBABILITES": {
        "C1": {"required": [[r"ind[ée]pendant", r"succession", r"[ée]preuve", r"r[ée]p[ée]tition",
                             r"remet", r"remise", r"[àa] nouveau", r"deux fois"],
                            [r"arbre", r"probabilit", r"P\("]]},
        "C2": {"required": [[r"Bernoulli", r"binomiale", r"\\mathcal\{B\}"],
                            [r"succ[èe]s", r"[ée]preuve", r"param[èe]tre", r"mod[ée]lis",
                             r"reconna"]]},
        "C3": {"required": [[r"binomiale", r"\\mathcal\{B\}", r"P\(X"],
                            [r"seuil", r"comparaison", r"comparer", r"optimis", r"plus petit",
                             r"au moins", r"strat[ée]gie"]]},
        "C4": {"required": [[r"binomiale", r"P\(X", r"\\binom"],
                            [r"calculatrice", r"Python", r"num[ée]rique", r"intervalle",
                             r"[Cc]alculer", r"\\leqslant"]]},
        "C5": {"required": [[r"Bernoulli", r"\\binom", r"binomiale"],
                            [r"[Dd][ée]montrer", r"coefficient", r"k\s*succ[èe]s", r"formule"]]},
        "C6": {"required": [[r"somme", r"d[ée]compos", r"X_\d", r"X_i"],
                            [r"variable al[ée]atoire", r"esp[ée]rance", r"E\(", r"Bernoulli"]]},
        "C7": {"required": [[r"esp[ée]rance", r"E\("],
                            [r"lin[ée]arit", r"somme", r"aX", r"X\s*\+\s*Y", r"\+\s*b"]]},
        "C8": {"required": [[r"variance", r"V\("],
                            [r"additivit", r"ind[ée]pendan", r"somme", r"\\sigma"]]},
        "C9": {"required": [[r"binomiale", r"\\mathcal\{B\}"],
                            [r"[Dd][ée]montrer", r"esp[ée]rance", r"variance", r"formule",
                             r"np", r"E\(X", r"V\(X"]]},
        "C10": {"required": [[r"Bienaym", r"Tchebychev", r"M_n", r"majoration de \$?V"],
                             [r"[ée]chantillon", r"in[ée]galit", r"taille", r"pr[ée]cision"]]},
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
