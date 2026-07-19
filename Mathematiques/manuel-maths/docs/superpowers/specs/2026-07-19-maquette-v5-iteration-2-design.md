# Maquette v5 — Itération 2 : conception

## But, périmètre et invariants

Produire une maquette de validation de 15 pages à partir des objets existants de
`1SPE-DERIVATION-LOCAL`, sans modifier leur texte, la classe v4.1, la production
TSPE ou le QCM source. La v5 reste une couche isolée composée d'une classe, d'un
manifeste, d'un générateur de renvois, d'un contrôleur et de tests dédiés.

La séquence physique est fixe : ouverture p.1 ; cours p.2–5 ; blanche p.6 ;
méthodes p.7–8 ; exercices p.9–10 ; QCM p.11–12 ; corrigés QCM et diagnostics
p.13 ; blanche p.14 ; corrigés compacts p.15. Aucun déploiement n'est autorisé.
Le rapport final conserve la pause `EN ATTENTE DE « MAQUETTE V5 VALIDÉE »`.

Les vingt exercices déjà assemblés en itération 1 restent les vingt contenus de
l'itération 2. Seul leur ordre d'affichage change afin que les trois applications
de M1 portent les numéros visibles 1, 2 et 7. La densité attendue reste onze
badges p.9 et neuf p.10, avec filet central sur les deux pages.

## Architecture et responsabilités

- `gabarits/nexus-manuel-v5.cls` définit les marks de rubrique, gabarits v5,
  garde-fous de marge, badges, pages blanches et contextes QCM/corrigés.
- `build/maquette-v5/manifest.json` fige exclusivement des IDs META canoniques,
  chemins source, ordre, pages, folios, pictogrammes et chaînes attendues.
- `scripts/build_maquette_v5.py` valide le manifeste et les META puis produit
  `build/maquette-v5/renvois.tex`. Il ne lit le corps des objets que pour trouver
  la META et ne copie aucun contenu éditorial.
- `build/maquette-v5/maquette.tex` reste déclaratif : ouverture, enregistrements
  d'annotations v5 et `\input` des objets inchangés.
- `scripts/check_maquette_v5.py` orchestre génération, trois passes LuaLaTeX,
  extraction PDF, comparaison raster et génération PNG 150 dpi.
- `tests/test_maquette_v5.py` couvre les contrats unitaires, fixtures LaTeX et
  l'acceptation réelle.

## Manifeste normatif

Le manifeste est un objet JSON de `version: 2` avec les champs suivants :

```json
{
  "version": 2,
  "source_chapter": "1SPE-DERIVATION-LOCAL",
  "output_pdf": "build/maquette-v5/maquette.pdf",
  "expected_pages": 15,
  "blank_pages": [6, 14],
  "course_files": [
    "chapitres/1SPE-DERIVATION-LOCAL/cours/10_C1_taux_variation.tex",
    "chapitres/1SPE-DERIVATION-LOCAL/cours/11_C2_nombre_derive.tex"
  ],
  "methods": [
    "1SPE-DERLOCAL-ME-001",
    "1SPE-DERLOCAL-ME-002",
    "1SPE-DERLOCAL-ME-003",
    "1SPE-DERLOCAL-ME-004"
  ],
  "rendered_method": {
    "id": "1SPE-DERLOCAL-ME-001",
    "applications": [
      "1SPE-DERLOCAL-EX-001",
      "1SPE-DERLOCAL-EX-002",
      "1SPE-DERLOCAL-EX-005"
    ]
  },
  "exercise_order": [
    "1SPE-DERLOCAL-EX-001", "1SPE-DERLOCAL-EX-002",
    "1SPE-DERLOCAL-EX-007", "1SPE-DERLOCAL-EX-008",
    "1SPE-DERLOCAL-EX-009", "1SPE-DERLOCAL-EX-010",
    "1SPE-DERLOCAL-EX-005", "1SPE-DERLOCAL-EX-003",
    "1SPE-DERLOCAL-EX-004", "1SPE-DERLOCAL-EX-006",
    "1SPE-DERLOCAL-EX-011", "1SPE-DERLOCAL-EX-012",
    "1SPE-DERLOCAL-EX-013", "1SPE-DERLOCAL-EX-014",
    "1SPE-DERLOCAL-EX-015", "1SPE-DERLOCAL-EX-016",
    "1SPE-DERLOCAL-EX-017", "1SPE-DERLOCAL-EX-018",
    "1SPE-DERLOCAL-EX-019", "1SPE-DERLOCAL-EX-020"
  ],
  "exercise_page_counts": {"9": 11, "10": 9},
  "pictograms": {
    "1SPE-DERLOCAL-EX-005": "calculatrice",
    "1SPE-DERLOCAL-EX-006": "python",
    "1SPE-DERLOCAL-EX-015": "calculatrice"
  },
  "qcm": {
    "file": "chapitres/1SPE-DERIVATION-LOCAL/qcm/1SPE-DERIVATION-LOCAL-QCM.tex",
    "sha256": "cb34cb2351761e1c60d15eb5b95bcbc656c718fb19b6dca15290e3df3384b9e3"
  },
  "compact_corrections": [
    "1SPE-DERLOCAL-EX-001", "1SPE-DERLOCAL-EX-002",
    "1SPE-DERLOCAL-EX-003", "1SPE-DERLOCAL-EX-004",
    "1SPE-DERLOCAL-EX-005"
  ],
  "chapter_toc": [
    ["Ouverture", 1], ["Diagnostic", 2], ["Activités", 3],
    ["Cours", 5], ["Méthodes", 9], ["Entraînement", 13],
    ["TD", 23], ["Auto-évaluation", 27], ["Évaluation", 31]
  ],
  "required_strings": [
    "S'entraîner : ex. 1, 2, 7 p. 9",
    "→ M1 · Corrigé p. 15"
  ]
}
```

Cardinalités : quatre méthodes canoniques distinctes ; vingt exercices
canoniques distincts ; deux ou trois applications pour une paire nominale ;
trois pictogrammes dont la valeur est `python` ou `calculatrice` ; neuf couples
sommaire/folio ; cinq corrigés compacts ; deux pages blanches.

Une META est la première ligne `% META:` trouvée parmi les dix premières lignes.
Pour un exercice, `id`, `type_objet="exercice"`, `methodes` non vide et conforme
à `M[0-9]+`, `parcours` entier 1–3, `duree_min` entier positif, `fichier_tex` et
`corrige_tex` relatifs existants sont obligatoires ; `fichier_tex` désigne le
fichier effectivement lu. Pour une méthode, `id`, `type_objet="methode"` et
`methodes` non vide conforme suffisent. META absente/invalide, ID dupliqué,
chemin absolu, chemin hors racine ou ID de manifeste inconnu donne le code CLI 2
sans traceback.

Une liste de zéro ou une application dont les IDs sont tous connus est valide
mais déclenche la dégradation `NEXUS-V5-PAIRING-FALLBACK`. Deux ou trois IDs
connus rendent la paire ; quatre applications ou un ID inconnu rendent le
manifeste invalide (code 2).

## Navigation et pages blanches

La classe crée une classe de marks dédiée `nxrubrique`. `\rubrique{...}` écrit ce
mark ; en-tête et onglet lisent le mark résolu de la page expédiée, jamais une
globale. La séquence est toujours `\clearpage`, puis éventuelle page blanche,
puis `\rubrique{nouvelle}`. Une commande de page vide expédie explicitement une
boîte TeX sans glyphe (`\vbox to \textheight{\vfil}`) sous
`\thispagestyle{blanche}` ; le décor est un tracé TikZ `remember picture,overlay`
ancré sur `current page` à `opacity=0.04`. Le style n'a ni folio ni en-tête.

Après suppression du form-feed (`\f`) et des espaces Unicode, `pdftotext` des
pages 6 et 14 doit être vide. Aucun `diamond`, `⋄`, `◆` ou nœud textuel n'existe
dans l'implémentation de la page blanche.

## Ouverture et cours

`\ouverturechapitreV` réutilise strictement les quatre blocs textuels existants
et ajoute le bandeau, le décor, l'onglet OUVERTURE et les neuf entrées/folios du
manifeste. Aucun `??` n'est accepté après trois passes.

Le cours conserve ses deux `\input` inchangés. La classe fournit un registre
`\coursVocab{titre}{terme}{définition existante}` et
`\coursRenvoi{titre}{méthode}{page}` utilisé par la maquette pour attacher deux
notes marginales à des définitions existantes, sans réémettre le terme dans le
corps. Ces annotations reprennent mot pour mot des formulations déjà présentes.
Les notes utilisent interligne 10 pt, filet 0,4 pt, espace vertical minimal 9 pt
et s'alignent sur les multiples de 4,5 pt de la grille.

`\erreurFrequente` devient insécable et tient un compteur par page réinitialisé
au shipout. Au troisième bloc candidat sur la même page, la classe force la
coupure avant le bloc ; ainsi aucune page 2–5 ne contient trois titres « Erreur
fréquente ». `\approfondissement` réserve la hauteur de son titre et de deux
lignes avec `needspace`; son titre ne peut être orphelin. L'acceptation contrôle
deux vocabularies, un renvoi, zéro page avec trois alertes et aucun grand blanc
final supérieur à 25 % de la hauteur utile.

## Méthode appariée et marges interdites

`methodePairee` compose l'`\input` inchangé de M1 à gauche et les `\input`
inchangés des applications 001, 002 et 005 à droite. `\commentaireMarge` devient
localement un appel ①, ② ou ③ dans la résolution ; les légendes correspondantes
sont regroupées sous l'exemple. `\refExos{M1}` est remplacé par la chaîne générée
exacte. Le corps des trois exercices est rendu par un adaptateur d'application,
sans badge technique ni corrigé.

Dans tout contexte où `marginparwidth=0pt` ou multicolonné, `\marginnote` n'appelle
jamais l'original. Son texte est accumulé et rendu en note de bas de bloc, et le
log reçoit `NEXUS-V5-MARGINNOTE-REDIRECTED`. Toute voie qui appellerait l'original
écrit d'abord `NEXUS-V5-MARGINNOTE-COLUMNS-EMITTED`; l'acceptation interdit ce
marqueur. Des fixtures compilent 0, 1, 2, 3 et 4 applications et vérifient
respectivement fallback, fallback, paire, paire, code 2.

## Exercices et renvois

Dans `grilleExercices`, l'environnement source `exercice` est adapté localement.
Son premier argument canonique sert uniquement de clé de lookup vers les macros
générées ; il n'est jamais composé. Le badge montre numéro, durée, difficulté
(1 = un plein + deux contours ; 2 = deux pleins + un contour ; 3 = trois pleins),
pictogramme éventuel et renvoi. Chaque exercice porte `\label{ex:<ID>}` et chaque
méthode `\label{meth:<ID>}`. Après la page blanche 14 et avant tout corrigé, le
bloc p.15 porte une seule fois `\label{corr:start}`.

La page 9 extrait onze badges, la page 10 neuf ; les vingt IDs techniques sont
absents du PDF. Le premier renvoi extrait est exactement
`→ M1 · Corrigé p. 15`; le renvoi M1 est exactement
`S'entraîner : ex. 1, 2, 7 p. 9`. Les deux pages gardent un filet central visible.

## QCM, diagnostics et corrigés

Le fichier QCM reste byte-identique au SHA-256 du manifeste. Dans les pages
11–12 seulement, `\dfrac` devient `\tfrac`, chaque item principal et ses réponses
sont groupés, et les coupures internes sont interdites.

Le `\newpage` unique du QCM est intercepté localement : il ferme le contexte
étroit, expédie p.12, écrit le mark `Corrigés` et restaure exactement géométrie,
polices et gabarit d'itération 1 avant les diagnostics. La page 13 rasterisée à
150 dpi doit avoir `compare -metric AE = 0` contre
`validations/v5-it1/page-13.png`. Cette référence provient du PDF du commit
`7d64cdc`, compilé avant toute modification it2, page 13 seule à 150 dpi.

Après p.14, `corrigesCompacts` écrit le mark `Corrigés`, un titre unique, le label
`corr:start` et trois colonnes. Les IDs de corrigés ne sont pas composés.

## Contrôle, livrables et acceptation

La commande publique est :

```bash
python3 scripts/check_maquette_v5.py --manifest build/maquette-v5/manifest.json
```

Elle produit la table de renvois, lance exactement trois LuaLaTeX, exige 15
pages, normalise `pdftotext` page par page, contrôle rubriques, sommaire, pages
blanches, deux chaînes, IDs absents, compte des badges, garde marginale, hash
QCM et comparaison page 13. Codes : 0 succès ; 1 compilation/acceptation ; 2
manifeste/META. Le succès imprime exactement :

`MAQUETTE V5: PASS — 15 pages; blanches 6,14; renvois 2/2; marginnote colonnes 0`

Le PDF local est `build/maquette-v5/maquette.pdf`. Les PNG 150 dpi sont
`validations/v5/page-01.png` à `page-15.png`. Le tableau AVANT/APRÈS de
`MAQUETTE_V5_A_VALIDER.md` contient : défaut, avant it1, après it2, preuve
automatique/visuelle, statut. Le commit final n'inclut que les artefacts v5 et
porte `[CHARTE][V5.B-it2]`; aucun push ni déploiement n'est effectué.
