# Maquette v5 — Itération 2 : conception

## But et périmètre

Produire une seconde maquette de 12 à 15 pages à partir des objets existants du chapitre `1SPE-DERIVATION-LOCAL`, sans réécriture de contenu et sans déploiement. La v4.1 reste la classe de production ; seule `nexus-manuel-v5.cls`, la maquette v5, son assembleur de démonstration, ses tests et ses livrables de validation changent.

La maquette doit corriger les huit défauts du verdict d'itération 1, conserver intacte la page de diagnostics validée et rester bloquée jusqu'au verdict exact « MAQUETTE V5 VALIDÉE ». Le verdict source est la directive utilisateur « MAQUETTE V5 — VERDICT ITÉRATION 1 + DIRECTIVE ITÉRATION 2 » du 18 juillet 2026 ; son état durable est recopié sous forme de matrice d'acceptation ci-dessous.

## Choix d'architecture

Trois approches ont été évaluées : corrections locales dans `maquette.tex`, modification de l'assembleur v4.1, ou couche v5 isolée. La couche v5 isolée est retenue : les corrections locales ne traiteraient pas les causes racines ; modifier v4.1 perturberait la production TSPE qui doit continuer en parallèle.

La responsabilité est répartie ainsi :

- `gabarits/nexus-manuel-v5.cls` porte les gabarits, les marks de rubrique, les pages blanches, les adaptations de macros existantes et les garde-fous de composition.
- `build/maquette-v5/manifest.json` fige les objets, leur ordre, les pages attendues, les pictogrammes de démonstration et les chaînes contrôlées.
- `scripts/build_maquette_v5.py` lit le manifeste et les lignes `% META:` des objets sélectionnés, valide leurs identifiants et génère la table LaTeX de renvois et de pictogrammes. Il ne copie ni ne réécrit le corps des objets.
- `build/maquette-v5/maquette.tex` ne contient que l'assemblage, les labels de rubrique et les applications sélectionnées par `\input`.
- `scripts/check_maquette_v5.py` compile et vérifie le PDF ; `tests/test_maquette_v5.py` couvre la génération et le contrôle d'intégration.

## Navigation synchronisée

Une classe de marks dédiée à la rubrique remplace la variable globale. `\rubrique{...}` émet un mark ; l'onglet et l'en-tête lisent le mark résolu pour la page expédiée. Le changement de rubrique est effectué après la coupure qui termine la rubrique précédente, de sorte qu'aucune page ne reçoit par anticipation le libellé suivant.

L'ouverture v5 est exposée par `\ouverturechapitreV{<titre>}{<capacités>}{<accroche>}{<temps>}`. Elle reprend les quatre arguments obligatoires de contenu de l'ouverture v4.1 et ajoute un bandeau, le décor géométrique du chapitre, un onglet « OUVERTURE » et un sommaire des neuf temps. Le sommaire reçoit les neuf labels déclarés dans le manifeste ; après les passes LaTeX, aucune valeur factice ou `??` ne doit rester.

## Pages blanches décorées

Le style `blanche` a des en-têtes et pieds réellement vides. Le motif est dessiné uniquement par TikZ en `remember picture,overlay`, ancré sur `current page`, avec `opacity=0.04`. Aucun glyphe, numéro de page ou caractère décoratif n'est émis. Une page blanche reste donc visuellement décorée mais son extraction `pdftotext -f N -l N` est vide après normalisation des espaces.

## Cours et méthodes

Le cours conserve la grille v4.1 à marge active. La classe v5 règle les notes marginales avec un filet, un interligne lisible et un espacement vertical minimal. Les blocs non sécables empêchent « Pour aller plus loin » d'être orphelin ; la maquette sélectionne les mêmes objets dans un ordre permettant de répartir les erreurs fréquentes sans modifier leur texte.

La méthode M1 est rendue par `\begin{methodePairee}{<ID méthode>}...\separationApplications...\end{methodePairee}` : objet méthode résolu à gauche, deux ou trois objets d'application existants à droite. Les annotations `\commentaireMarge` deviennent des appels numérotés dans la résolution et leurs légendes sont composées dans le bloc, jamais dans une marge absente. Une paire est incomplète si le manifeste ne fournit pas entre deux et trois IDs d'exercices existants ; la classe produit alors une fiche simple largeur avec le warning `NEXUS-V5-PAIRING-FALLBACK`, sans superposition.

Dans tout contexte à marge nulle ou multicolonné, `\marginnote` est redirigé vers une note de bas de bloc et écrit `NEXUS-V5-MARGINNOTE-REDIRECTED`. L'appel de la primitive marginale dans ce contexte doit écrire `NEXUS-V5-MARGINNOTE-COLUMNS-EMITTED` avant émission ; le test exige l'absence de ce second marqueur.

## Exercices, META et renvois

Les fichiers d'exercices restent inclus tels quels. Dans `grilleExercices`, l'environnement `exercice` existant est localement adapté en badge compact : numéro visible, difficulté en losanges pleins/contour, durée, pictogramme éventuel et renvoi généré. L'ID technique n'est jamais émis dans la couche texte.

Le parseur accepte exactement la première ligne commençant par `% META:` dans les dix premières lignes du fichier, suivie d'un objet JSON sur une seule ligne. Pour un exercice, `id` (chaîne non vide et unique), `type_objet="exercice"`, `methodes` (liste non vide de codes `M[0-9]+`), `parcours` (entier 1 à 3), `duree_min` (entier strictement positif), `fichier_tex` et `corrige_tex` (chemins relatifs existants) sont obligatoires. Le chemin `fichier_tex` doit désigner le fichier lu. Pour une méthode, `id`, `type_objet="methode"` et `methodes` sont obligatoires. Toute META absente/invalide, tout doublon, chemin manquant ou référence inconnue est fatal et produit le code de sortie 2.

L'assembleur préserve l'ordre du manifeste et génère des déclarations indexées par ID ainsi que les labels stables `ex:<ID exercice>` et `meth:<ID méthode>`. Le début du bloc des corrigés porte le label unique `corr:start` : tous les badges de cet extrait renvoient à la page 15, début représentatif des corrigés de fin de manuel, même si seuls cinq corrigés sont montrés. Les vingt chemins `corrige_tex` doivent néanmoins exister.

Les renvois M1 sont construits à partir de la table : les IDs `EX-001`, `EX-002`, `EX-005`, placés aux positions visibles 1, 2 et 7 par le manifeste, donnent la chaîne exacte « S'entraîner : ex. 1, 2, 7 p. 9 ». Sous les badges, la chaîne contrôlée pour le premier exercice est « → M1 · Corrigé p. 15 » ; les suivants utilisent leur méthode META M1 à M4 et le même folio `corr:start`. Les pictogrammes ne sont pas inférés : le manifeste autorise seulement `python` ou `calculatrice` et les fixe pour `EX-005`, `EX-006` et `EX-015`, dont les tâches de conjecture/calcul/lecture graphique justifient cette démonstration.

## QCM et corrigés

Le contexte QCM force `\tfrac` pour les fractions en ligne et rend chaque item principal insécable. Les alternatives restent groupées avec leur question. La page de diagnostics validée conserve son contenu et son gabarit.

Le gabarit des corrigés utilise trois colonnes, un unique titre et le mark « CORRIGÉS ». Le changement de mark se fait après la page blanche précédente afin d'éviter le décalage « COURS » observé.

## Contrôles et livrables

## Manifeste reproductible

`build/maquette-v5/manifest.json` décrit cette séquence physique exacte : page 1 ouverture ; pages 2–5 cours ; page 6 blanche décorée ; pages 7–8 méthode M1 appariée ; pages 9–10 exercices ; pages 11–12 QCM ; page 13 diagnostics ; page 14 blanche décorée ; page 15 corrigés.

Les entrées sont figées ainsi :

- cours : `cours/10_C1_taux_variation.tex`, puis `cours/11_C2_nombre_derive.tex` ;
- méthodes référencées : `ME-001` à `ME-004`; seule `ME-001` est rendue ; applications M1 : exercices `001`, `002`, `005` ;
- entraînement, dans l'ordre visible : `001`, `002`, `007`, `008`, `009`, `010`, `005`, `003`, `004`, `006`, puis `011` à `020`. Cet ordre rend les trois applications M1 sous les numéros 1, 2 et 7 sans falsifier leurs META ;
- auto-évaluation et diagnostics : `qcm/1SPE-DERIVATION-LOCAL-QCM.tex`, SHA-256 source `cb34cb2351761e1c60d15eb5b95bcbc656c718fb19b6dca15290e3df3384b9e3` ;
- corrigés compacts : corrigés `001` à `005`, dans l'ordre numérique ;
- pages dont le texte extrait doit être vide : `[6, 14]` ;
- neuf temps et folios éditoriaux figés dans ce même manifeste : Ouverture 1, Diagnostic 2, Activités 3, Cours 5, Méthodes 9, Entraînement 13, TD 23, Auto-évaluation 27, Évaluation 31. Il s'agit du sommaire maquetté du chapitre complet, pas des quinze pages de l'extrait ; aucune valeur n'est calculée à partir d'un placeholder.

## Matrice d'acceptation des huit défauts

| # | Défaut d'itération 1 | Composant responsable | Preuve d'itération 2 |
|---|---|---|---|
| 1 | Ouverture v4.1, sommaire et onglet absents | commande `\ouverturechapitreV` | page 1 inspectée ; neuf temps et folios extraits |
| 2 | Notes de cours écrasées/sans filet, erreurs empilées, bloc orphelin | grille cours v5 | pages 2–5 inspectées ; test source des blocs non sécables |
| 3 | Losanges réels dans les pages blanches | style `blanche` + overlay TikZ | `pdftotext` pages 6/14 vide |
| 4 | Onglets décalés | marks de rubrique dédiés | texte/onglets pages 2–15 et test de changement après coupure |
| 5 | Méthodes superposées, non appariées, placeholders | `methodePairee`, call-outs, table META | pages 7–8 ; renvoi exact ; log sans émission marginale |
| 6 | IDs visibles, difficultés/renvois/pictos absents | adaptateur `exercice` + table générée | pages 9–10 ; IDs absents du texte, badges/chaînes/pictos présents |
| 7 | Fractions QCM disloquées et items coupés | contexte QCM étroit | pages 11–12 inspectées ; `\tfrac`, blocs insécables |
| 8 | Corrigés : mark faux et titre doublé | contexte `corrigesCompacts` | page 15 inspectée ; un titre, mark CORRIGÉS |

Le fichier QCM source n'est jamais modifié ; son SHA-256 est vérifié avant compilation. La référence raster d'itération 1 est versionnée sous `validations/v5-it1/page-13.png`. La page 13 finale doit obtenir une différence absolue ImageMagick de zéro pixel contre cette référence ; l'absence de diff source QCM et ce résultat nul sont tous deux bloquants.

## Contrôle automatique et CLI

Le contrôle automatique doit :

1. exécuter `python3 scripts/build_maquette_v5.py --manifest build/maquette-v5/manifest.json --output build/maquette-v5/renvois.tex`, puis exactement trois passes LuaLaTeX ;
2. exiger exactement 15 pages, un code LuaLaTeX nul, aucune ligne `!`, `Undefined control sequence`, `LaTeX Warning: There were undefined references` ni `??` extrait ;
3. vérifier que les pages déclarées blanches ont un texte extrait vide ;
4. vérifier la présence des chaînes de renvoi générées dans le PDF ;
5. vérifier dans le log qu'aucun `\marginnote` n'a été émis en contexte deux colonnes ;
6. comparer la page 13 rasterisée à `validations/v5-it1/page-13.png` avec `compare -metric AE` et exiger `0` ;
7. produire `validations/v5/page-01.png` à `page-15.png` à 150 dpi et le tableau AVANT/APRÈS dans `MAQUETTE_V5_A_VALIDER.md`.

La commande publique est `python3 scripts/check_maquette_v5.py --manifest build/maquette-v5/manifest.json`. Elle produit la table, compile, contrôle et rend 0 en succès, 1 pour une compilation/acceptation invalide, 2 pour un manifeste/META invalide. La pause de déploiement est un état documentaire : le rapport conserve `PAUSE BLOQUANTE — EN ATTENTE DE « MAQUETTE V5 VALIDÉE »`; aucun code de déploiement n'est ajouté ni appelé.

Le commit final est limité aux artefacts v5 et porte le message `[CHARTE][V5.B-it2]`. Aucun script de déploiement, aucune classe v4.1, aucun chapitre TSPE et aucun fichier NSI ne sont modifiés.
