# A6 — forensique des `context_mismatches`

Snapshot analysé : `ca5c907d42bd2782596a2c715759f8d0bee9b9fa`.

La mesure fraîche a été obtenue avec :

```text
python scripts/inventory_collection.py --check --require-clean
exit = 0
A6_START_CONTEXT_MISMATCHES = 3
```

Les trois fingerprints mesurés sont exactement :

- `412440a833f2a67e` ;
- `d4d96a91fdd7f2ca` ;
- `dc3c58388e2cfe7c`.

Le fichier machine complet est
`audit/A6_CONTEXT_MISMATCH_FORENSICS.json`. Son inventaire source est
`audit/CURRENT_ANOMALIES_RAW.json`, SHA-256
`43354229fce31ebd628cabf536c65795bf8c2064b9fb28ed30d07966f3a516d2`.

## Interprétation des dimensions

Les sources concernées ne possèdent pas de champs META `manual` ou
`variant`. Le manuel détecté est donc dérivé du préfixe du chapitre physique
et de son contrat. Les variantes sont les assemblages exacts qui atteignent
la source. Aucun champ ad hoc n'est inventé.

Dans les trois cas, le filesystem et les assembleurs détectent TCOMPL, alors
que le `META.chapitre`, le corps, le contrat de contenu, le programme et un
jumeau canonique exact désignent TSPE. Ce faisceau d'autorités ne décrit pas
trois mauvais en-têtes : il prouve trois copies TSPE mal placées sous TCOMPL.

Les causes sont donc réparties ainsi :

- `PATH_CONTEXT_DRIFT` : 3 ;
- toutes les autres catégories autorisées : 0 ;
- `UNKNOWN` : 0.

## Autorités communes

Le contrat physique
`Mathematiques/manuel-maths/chapitres/TCOMPL-CALCULS-AIRES/contrat.yaml`
déclare le manuel `TCOMPL`, le chapitre `TCOMPL-CALCULS-AIRES` et les
capacités d'intégration, d'aires et de primitives. Le contrat sémantique
`Mathematiques/manuel-maths/chapitres/TSPE-DERIVATION-CONVEXITE/contrat.yaml`
déclare `TSPE-DERIVATION-CONVEXITE` et les capacités de dérivation composée,
d'étude de fonctions et de convexité.

Ces séparations sont confirmées par :

- `capacites_TCOMPL_CALCULS-AIRES.json`, SHA-256
  `886b58aaebd81a721a5f3a0af660f42a0ba97abc9be075645400d77b07f909a9` ;
- `capacites_TSPE_DERIVATION_CONVEXITE.json`, SHA-256
  `b635344f95297dd5a70b5506fde685a193777696ca678bf530a26a358080600d` ;
- l'assembleur de chapitre, SHA-256
  `623471e4c75995c57ac64239d6202ad08d0612aebf4f022db05a3c32e9eccb7f` ;
- l'assembleur de manuel, SHA-256
  `b31bfa645702a2012b7da4f790f1c37889bdd9f98786cf5461504819dea32dd8`.

Le manifeste canonique `audit/BUILD_MANIFEST.json` a `builds=[]`. Il ne porte
donc aucun receipt par objet. Ce fait est noté
`NOT_APPLICABLE_EMPTY_BUILD_MANIFEST`, et non `UNKNOWN`.

Les trois copies sont actuellement runtime-reachable dans les quatre
assemblages physiques suivants : chapitre `complet`, chapitre `parcours1`,
manuel TCOMPL `eleve` et manuel TCOMPL `professeur`. Chacun des jumeaux TSPE
est déjà runtime-reachable dans les quatre assemblages canoniques homologues :
chapitre TSPE `complet`, chapitre TSPE `parcours1`, manuel TSPE `eleve` et
manuel TSPE `professeur`.

Le graphe d'inventaire ne contient aucune référence entrante vers les trois
paths ou IDs TCOMPL, aucune arête sortante non-capacité et aucune référence
LaTeX `input/ref`. Un scan des packets sous `audit/reviews/**/*.review.json`
n'a trouvé ni path, ni ID, ni SHA source lié aux trois copies. Leur suppression
n'invalidera donc aucun packet. Après retrait exact de leurs faux liens de
capacités, chaque capacité TCOMPL C1 à C6 conserve entre 17 et 27 liens issus
d'autres objets.

## Cas 1 — `412440a833f2a67e`

- fingerprint : `412440a833f2a67e`
- manual_detected : `TCOMPL`
- manual_expected : `TSPE_2026_2027`
- variant_detected : chapitre TCOMPL `complet`/`parcours1`, manuel TCOMPL
  `eleve`/`professeur`
- variant_expected : chapitre TSPE `complet`/`parcours1`, manuel TSPE
  `eleve`/`professeur`
- chapter_detected : `TCOMPL-CALCULS-AIRES`
- chapter_expected : `TSPE-DERIVATION-CONVEXITE`
- object_id : `TCOMPL-AIRES-CR-010-DERIVEE`
- path :
  `Mathematiques/manuel-maths/chapitres/TCOMPL-CALCULS-AIRES/cours/10_C1_derivee_composee.tex`
- META context : chapitre TSPE, `type_objet=cours`, capacité C1,
  `status=approved`
- filesystem context : TCOMPL / `TCOMPL-CALCULS-AIRES` / `cours`, catégorie
  `sections_cours`
- manifest context : manifeste vide, aucun binding par objet
- assembler context : atteignable dans les quatre variantes TCOMPL; le jumeau
  l'est déjà dans les quatre variantes TSPE
- programme context : le corps enseigne la dérivée d'une fonction composée,
  exactement `TSPE-DERCONV-C1`; `TCOMPL-AIR-C1` concerne l'intégrale comme
  aire sous la courbe
- runtime reachable : `true`
- root cause : `PATH_CONTEXT_DRIFT`
- proposed action : après les tests rouges et la dernière vérification des
  hashes, supprimer uniquement cette copie TCOMPL; ne pas modifier le jumeau
  TSPE

Preuve de jumeau :

- copie SHA-256 :
  `fee6cebba0c56f889da23eb8615e98dcf3dda527fccaaa9c1a96e46b4239fa16` ;
- jumeau :
  `Mathematiques/manuel-maths/chapitres/TSPE-DERIVATION-CONVEXITE/cours/10_C1_derivee_composee.tex` ;
- jumeau SHA-256 :
  `bd0315825c9e99a30a8d29097762934e18d334638ca3b0a5955d42d27a6af51e` ;
- corps des deux fichiers SHA-256 :
  `8a9f30b5dd098d225ca0bd8d5273cc6ddb995d00aec4fff51db1317959a275a1` ;
- différence META : le seul champ `id`.

Références : aucune entrante; une sortie capacité, actuellement résolue vers
`TCOMPL-AIR-C1` par le path. Le jumeau résout canoniquement
`TSPE-DERCONV-C1`. Reviews et bindings SHA : zéro.

## Cas 2 — `d4d96a91fdd7f2ca`

- fingerprint : `d4d96a91fdd7f2ca`
- manual_detected : `TCOMPL`
- manual_expected : `TSPE_2026_2027`
- variant_detected : chapitre TCOMPL `complet`/`parcours1`, manuel TCOMPL
  `eleve`/`professeur`
- variant_expected : chapitre TSPE `complet`/`parcours1`, manuel TSPE
  `eleve`/`professeur`
- chapter_detected : `TCOMPL-CALCULS-AIRES`
- chapter_expected : `TSPE-DERIVATION-CONVEXITE`
- object_id : `TCOMPL-AIRES-COURS-07-FR`
- path :
  `Mathematiques/manuel-maths/chapitres/TCOMPL-CALCULS-AIRES/cours/07_td_fil_rouge.tex`
- META context : chapitre TSPE, `type_objet=cours`,
  `sous_type=td_fil_rouge`, capacités C1 à C6, `status=approved`
- filesystem context : TCOMPL / `TCOMPL-CALCULS-AIRES` / `cours`, catégorie
  `td`
- manifest context : manifeste vide, aucun binding par objet
- assembler context : atteignable dans les quatre variantes TCOMPL; le jumeau
  l'est déjà dans les quatre variantes TSPE
- programme context : étude de `x^2 exp(-x)` par dérivée, limites, variations,
  dérivée seconde, convexité et tangentes, soit TSPE C1 à C6, et non les
  capacités TCOMPL d'intégration/aires/primitives
- runtime reachable : `true`
- root cause : `PATH_CONTEXT_DRIFT`
- proposed action : après les tests rouges et la dernière vérification des
  hashes, supprimer uniquement cette copie TCOMPL; ne pas modifier le jumeau
  TSPE

Preuve de jumeau :

- copie SHA-256 :
  `f2286b1bf0bed87192824ce9a2487e6c6ad2db215255b6f51101b613eb0fd836` ;
- jumeau :
  `Mathematiques/manuel-maths/chapitres/TSPE-DERIVATION-CONVEXITE/cours/07_td_fil_rouge.tex` ;
- jumeau SHA-256 :
  `186c26bd6e49ad103b6689a7e186670651110d429f4cd7ba6d91dcacdc1fa5ea` ;
- corps des deux fichiers SHA-256 :
  `342abf3729794d7ef832138ea88ec38ae1d9838d7a4fafacb8e2b14d8ac00a5a` ;
- différence META : le seul champ `id` ;
- identifiants internes conservés : `TSPE-DERCONV-COURS-07-FR-EX1` à
  `EX3`.

Références : aucune entrante; six sorties capacités, actuellement résolues
vers `TCOMPL-AIR-C1` à C6 par le path. Le jumeau résout canoniquement
`TSPE-DERCONV-C1` à C6. Reviews et bindings SHA : zéro.

## Cas 3 — `dc3c58388e2cfe7c`

- fingerprint : `dc3c58388e2cfe7c`
- manual_detected : `TCOMPL`
- manual_expected : `TSPE_2026_2027`
- variant_detected : chapitre TCOMPL `complet`/`parcours1`, manuel TCOMPL
  `eleve`/`professeur`
- variant_expected : chapitre TSPE `complet`/`parcours1`, manuel TSPE
  `eleve`/`professeur`
- chapter_detected : `TCOMPL-CALCULS-AIRES`
- chapter_expected : `TSPE-DERIVATION-CONVEXITE`
- object_id : `TCOMPL-AIRES-COURS-07-TC`
- path :
  `Mathematiques/manuel-maths/chapitres/TCOMPL-CALCULS-AIRES/cours/07_td_contextualise.tex`
- META context : chapitre TSPE, `type_objet=cours`,
  `sous_type=td_contextualise`, capacités C1/C2/C3/C6, `status=approved`
- filesystem context : TCOMPL / `TCOMPL-CALCULS-AIRES` / `cours`, catégorie
  `td`
- manifest context : manifeste vide, aucun binding par objet
- assembler context : atteignable dans les quatre variantes TCOMPL; le jumeau
  l'est déjà dans les quatre variantes TSPE
- programme context : optimisation d'un cylindre par dérivation et convexité,
  sans intégrale ni aire sous courbe, soit TSPE C1/C2/C3/C6 et non TCOMPL
  C1/C2/C3/C6
- runtime reachable : `true`
- root cause : `PATH_CONTEXT_DRIFT`
- proposed action : après les tests rouges et la dernière vérification des
  hashes, supprimer uniquement cette copie TCOMPL; ne pas modifier le jumeau
  TSPE

Preuve de jumeau :

- copie SHA-256 :
  `2a5e383fc6feedee0bd3018b6194bb1620b357c94ab349af449d98e0035637c0` ;
- jumeau :
  `Mathematiques/manuel-maths/chapitres/TSPE-DERIVATION-CONVEXITE/cours/07_td_contextualise.tex` ;
- jumeau SHA-256 :
  `c2a90a9ba7cb804821aa019bf2a686f044c5be2988ac8f0147b2157eb818f2c1` ;
- corps des deux fichiers SHA-256 :
  `a0a7e3ba484cbe69c8da103e23b010bf0b2f7cbc725f803ce82e496df8d8dfb4` ;
- différence META : le seul champ `id` ;
- identifiants internes conservés : `TSPE-DERCONV-COURS-07-TC-EX1` et
  `EX2`.

Références : aucune entrante; quatre sorties capacités, actuellement résolues
vers `TCOMPL-AIR-C1/C2/C3/C6` par le path. Le jumeau résout canoniquement les
quatre capacités TSPE homologues. Reviews et bindings SHA : zéro.

## Conclusion d'action

Le correctif autorisé n'est ni un `git mv`, ni une correction de META, ni une
tolérance d'analyseur. Après le test rouge A6, il devra supprimer exactement
les trois copies ci-dessus. Les trois jumeaux canoniques TSPE restent
inchangés. La conséquence de modèle attendue est limitée à
`sections_cours -1` et `td -2`; le delta d'anomalies devra rester
`removed=3`, `added=0`, `reclassified=0`.

Cette forensique n'a modifié ou supprimé aucune source.
