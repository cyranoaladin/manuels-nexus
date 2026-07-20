# Maquette v5 — correction de la page 13

## But et invariants

Corriger les superpositions et débordements de la page « Correction et
diagnostics » sans modifier son contenu éditorial, le fichier QCM source, les
pages 1–12 et 14–15, ni le total de 15 pages. La correction reste isolée dans la
classe v5, ses contrôles et les livrables de validation. Aucun déploiement n'est
autorisé.

Le fichier
`chapitres/1SPE-DERIVATION-LOCAL/qcm/1SPE-DERIVATION-LOCAL-QCM.tex` conserve son
SHA-256 canonique. La référence raster de l'itération 1, qui reproduit le défaut,
reste conservée comme preuve historique ; une nouvelle référence corrigée est
créée séparément après validation automatique et visuelle.

## Diagnostic confirmé

Après le `\newpage` du QCM, `faireLePoint` ferme la grille QCM puis rouvre un
`multicols` à deux colonnes. Le tableau source à quatre colonnes est ainsi placé
dans une largeur de demi-page alors qu'il a été écrit pour la pleine largeur.
LuaLaTeX mesure deux débordements : 314,99474 pt pour le tableau principal et
54,94688 pt pour la grille des réponses. Les réponses et le score occupent alors
la même zone que les premières lignes du tableau.

Le contrôle `compare -metric AE = 0` contre la référence itération 1 a transformé
ce rendu défectueux en oracle. Il vérifie la reproduction du défaut au lieu de
vérifier la qualité de composition.

## Composition retenue

La page 13 est composée en pleine largeur, hors `multicols`. L'interception du
`\newpage` du QCM effectue dans cet ordre :

1. fermeture de la grille QCM à deux colonnes ;
2. expédition de la page 12 ;
3. écriture du mark `Corrigés` et suppression locale de l'onglet ;
4. ouverture d'un contexte diagnostics pleine largeur ;
5. application locale de `\fontsize{6.6}{7.6}\selectfont`,
   `\tabcolsep=2pt` et `\arraystretch=1.08` ;
6. composition inchangée du tableau, de « Réponses correctes » et du score ;
7. fermeture du contexte avant la page blanche 14 ; la fermeture finale de
   `multicols` devient conditionnelle et n'est donc jamais appelée une seconde
   fois en mode diagnostics pleine largeur.

La typographie compacte, d'au moins 6,6 pt, est limitée au contexte diagnostics. Les textes, les
mathématiques, l'ordre des lignes et les renvois ne sont ni copiés ni réécrits.
Le tableau reste un tableau : aucune conversion en cartes, paysage ou page
supplémentaire.

## Instrumentation et acceptation

La classe écrit les marqueurs
`NEXUS-V5-DIAGNOSTICS-START` et `NEXUS-V5-DIAGNOSTICS-END`. Chacune des trois
passes LuaLaTeX doit contenir exactement une paire équilibrée. Le contrôleur
inspecte chaque intervalle et refuse tout `Overfull \\hbox` ou
`Overfull \\vbox`. Le marqueur END est écrit seulement après le `\clearpage`
qui expédie la page 13, afin d'inclure les avertissements produits au shipout.
L'acceptation PDF exige aussi :

- 15 pages ;
- `Correction et diagnostics`, les 15 lignes Q1 à Q15, les 45 diagnostics,
  `Réponses correctes`, `Score` et `Capacités à retravailler` sur la page 13 ;
- aucune des quatre chaînes propres aux diagnostics (`Correction et
  diagnostics`, `Réponses correctes`, `Score`, `Capacités à retravailler`) sur
  les pages 12 ou 14 ;
- une analyse `pdftotext -bbox-layout` segmentée en trois régions par les ancres
  `Correction et diagnostics`, `Réponses correctes` et `Score` ; Poppler pouvant
  restituer les colonnes dans un ordre documentaire différent de l'ordre visuel,
  chaque ligne est affectée à sa région par sa coordonnée verticale relativement
  aux ordonnées des ancres, jamais par sa position dans le flux XHTML : Q1–Q15
  et les 45 diagnostics doivent appartenir à la première région, la grille
  Q11–Q15 à la deuxième ; la dernière ligne
  du tableau (« placement de la virgule ») doit finir au moins 6 pt avant
  `Réponses correctes`, la dernière ligne de la grille Q11–Q15 au moins 6 pt
  avant `Score`, et toutes les boîtes du corps doivent rester dans
  `56.0 <= xMin`, `xMax <= 459.5` et `yMax <= 768.0` ; l'en-tête et le pied sont
  reconnus sémantiquement et exclus de ces bornes ;
- avant l'analyse XML, suppression ciblée des seuls caractères interdits par
  XML 1.0 (`0x00–0x08`, `0x0B`, `0x0C`, `0x0E–0x1F`) que Poppler peut émettre
  pour les cases `\square`; tabulation, CR et LF sont conservés ;
- aucune collision entre les boîtes de texte appartenant respectivement au
  tableau, à la grille des réponses et au score ;
- pages blanches 6 et 14 toujours vides ;
- un seul `Corrigés` extrait p.13 (en-tête, aucun onglet), puis l'onglet et le
  titre `Corrigés` restaurés p.15 ;
- hash du QCM source inchangé.

Le test historique contre `validations/v5-it1/page-13.png` est remplacé par les
critères de structure et de non-débordement. Après leur réussite et l'inspection
à pleine résolution, la page corrigée est copiée vers
`validations/v5-it2/page-13.png`. Le contrôleur vérifie son SHA-256 canonique et
exige ensuite `compare -metric AE = 0` entre cette référence et le rendu courant.

Pour garantir l'invariant hors p.13 sans dupliquer quatorze images, les SHA-256
des PNG 150 dpi actuellement validés pour les pages 1–12 et 14–15 sont figés
dans le test. Après régénération des 15 PNG `validations/v5/`, ces quatorze hashes
doivent rester identiques ; seule la page 13 peut changer.

## Vérification et livraison

La correction suit un cycle rouge/vert : un test compile d'abord le PDF actuel
et échoue sur les débordements et l'ordre des blocs ; la classe est ensuite
modifiée au minimum pour rendre ce test vert. Les tests v5 complets, le
contrôleur public, `make check-latex`, la suite globale et une inspection
visuelle de la page 13 sont exécutés avant toute conclusion.

Le rapport `MAQUETTE_V5_A_VALIDER.md` est mis à jour avec l'audit, le nouveau
hash de référence et la pause bloquante `MAQUETTE V5 VALIDÉE`. La branche et le
worktree isolés sont conservés ; aucun push ni déploiement n'est effectué.
