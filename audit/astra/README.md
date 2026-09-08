# Delta de la contre-revue externe Astra

Les documents Astra restent exclusivement hors du dépôt. La matrice conserve
leurs noms, SHA256 et localisations de contrôles, sans recopier leurs textes.
`MAPPED` signifie « contrôle explicitement classé », jamais « réussi ».

`ASTRA_DELTA_MATRIX_ee4475fdb.json` est l'observation initiale historique du
HEAD `ee4475fdb7e2891eae2ddb04f259d6ed930a963e`. Sa provenance interne a capturé
ce HEAD réellement présent au lancement, malgré le nom `299dca1bb` donné au
fichier temporaire de travail. Les preuves du corpus sont restées identiques
pendant le relevé. Le helper temporaire a ensuite été intégré, avec vérificateur
et tests de mutation, dans `scripts/build_astra_delta_matrix.py`.

Le delta compte 273 contrôles classés : 1 couvert (identité Git observée),
64 partiels, 179 non couverts et 29 différés au candidat final après freeze.
Les 51 contrôles `*-REV-3` partiels prouvent seulement la présence du chapitre
et sa sélection déclarée ; aucune revue pédagogique ou visuelle n'en découle.

Les 51 chemins de chapitres Astra sont un sous-ensemble exact des 52 chapitres
contractuels et sélectionnés. Le seul ajout est `NSI/chapitres/TNSI-PROJET`,
explicitement inscrit dans le manifeste TNSI et son contrat de démarche de projet.

Le détecteur courant a effectivement parcouru 3445 corps pédagogiques : aucune
contamination par corps identiques entre chapitres, 11 groupes intrachapitre à
qualifier. L'artefact antérieur était périmé pour la population (3357 corps).
Les 973 blobs Git des objets retirés ont été comparés aux sources courantes de
leur chapitre cible : aucun ancien corps ne subsiste. Cependant 218 identifiants
ont été réutilisés pour des contenus différents : une liaison de preuve doit
identifier la génération de contenu par digest. Le runtime PDF reste à observer.

Pour vérifier l'intégrité historique, sans affirmer de fraîcheur courante :

```bash
python -B scripts/build_astra_delta_matrix.py \
  --external-root "$HOME/Documents/Manuels_Nexus_AUDITS_EXTERNES/astra_2026-09-07" \
  --verify-snapshot audit/astra/ASTRA_DELTA_MATRIX_ee4475fdb.json
```

Pour une nouvelle mesure, une fois les sources committées et stables, donner
`--output audit/astra/ASTRA_DELTA_MATRIX_<HEAD>.json` à la place de
`--verify-snapshot`. Le producteur refuse une mutation concurrente, des sources
non committées et le remplacement d'une observation existante différente.
La garde porte aussi sur les assembleurs, manifests, normalizer, fixtures,
registres et politiques lus, ainsi que les refs Git parcourues par le scanner.
Un corps retiré réapparu ne conserve pas le statut obsolète. Une différence
inexpliquée de chapitres reste non réconciliée ; l'explication du projet TNSI
n'est héritée que tant que le digest de son contrat effectivement lu est identique.
L'identité du HEAD fait foi dans le contenu, indépendamment du nom choisi.
Aucun CURRENT, sign-off humain, verdict scientifique collectif ou receipt de
release n'est créé.
