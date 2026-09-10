# Rapport de vérification — HGGSP, édition pédagogique 1.0

**Session visée : 2027. Actualisation documentaire : 8 septembre 2026.**

## 1. Résultat de la fabrication

Les cinq volumes ont été assemblés à partir des mêmes sources canoniques, exportés en PDF et HTML, puis ouverts et contrôlés. Les **505 contrôles exécutés réussissent ; aucun échec n’est enregistré**. Ce résultat porte sur les contrôles décrits ci-dessous : il ne signifie pas que tout jugement scientifique ou pédagogique a été validé par un tiers.

| Volume | Pages physiques du PDF | Taille en octets |
|---|---:|---:|
| Manuel du cycle terminal | 156 | 1 468 072 |
| Première — Parcours N1 | 95 | 941 929 |
| Compagnon d’autocorrection | 82 | 363 972 |
| Épreuves blanches et corrigés | 46 | 214 641 |
| Sujets seuls | 18 | 106 830 |

La pagination comprend les couvertures. Les volumes se recoupent volontairement : l’extraction Première reprend les mêmes chapitres que le cycle et les sujets seuls reprennent les énoncés des blancs. Leur somme ne constitue donc pas un décompte de pages inédites.

## 2. Contenu effectivement présent

Les onze thèmes comportent une introduction, deux axes et un objet de travail conclusif. Les **78 jalons** sont reliés à une section développée du cours dans la matrice de couverture. Les fichiers de chapitres représentent **33 076 mots selon le comptage lexical du vérificateur**, ou 34 767 éléments séparés par des espaces ; ces décomptes ne sont ni une mesure de qualité ni un remplacement de la lecture. Les banques sont comptées séparément.

La banque avancée comprend **88 exercices, 55 QCM, 11 diagnostics, 11 activités et 11 nouveaux tests**, avec réponses et éléments d’autocorrection. Les douze méthodes, six remédiations et les corrections de leurs six microtests sont présentes. Le module 00 et ses activités/corrections s’ajoutent à ce corpus.

Les neuf blancs comprennent cinq compositions N1 et quatre écrits N2. Dans chacun de ces quatre écrits, les deux dissertations portent sur deux thèmes distincts et l’étude critique sur un troisième thème, tous pris dans le périmètre 2027. **Les huit dissertations proposées sont corrigées**, y compris l’option qui ne serait pas choisie pendant la simulation. Chaque étude critique possède sa correction. Les barèmes pédagogiques sont annoncés comme tels.

Le carnet rassemble neuf cartes ou schémas nouvellement produits. Le registre comporte **129 références et renvois**, dont des sources réglementaires, institutionnelles et des renvois aux ressources d’accompagnement. Il ne s’agit pas de 129 ouvrages intégralement lus : les types et limites sont déclarés.

## 3. Provenance : ce qui est récupéré et ce qui est nouveau

Le manuscrit historique intégral et ses anciens corrigés n’ont pas été retrouvés. Les matériaux réutilisés comprennent le module 00, le référentiel, 32 énoncés d’exercices, 20 QCM, quatre nouveaux tests et un fragment d’ouverture de P01. Sept témoins sont conservés inchangés sous `sources/originaux/` ; leurs empreintes ont été vérifiées.

Les développements manquants, les compléments de banque, les méthodes et remédiations, tous les corrigés avancés, les neuf blancs et les neuf figures sont des rédactions ou réalisations nouvelles. La banque identifie les adaptations. Les données illisibles de T06-E3 ont été remplacées par un nouveau jeu fictif, explicitement déclaré comme tel. Aucun texte nouveau n’est présenté comme un ancien fichier retrouvé. Le détail figure dans `PROVENANCE_EDITORIALE.md`.

## 4. Vérification réglementaire et documentaire

Les programmes officiels de Première et Terminale et leurs jalons ont servi de référentiel. Le format terminal se fonde sur la note du **27 août 2025, BO n° 33 du 4 septembre 2025, NOR MENE2521923N**, applicable à compter de 2026 : quatre heures, dissertation et étude critique notées chacune sur dix, trois thèmes distincts entre les deux dissertations et l’étude critique. La rotation des années impaires conduit à **T02, T04, T05 et T06 en 2027**. T01 et T03 restent enseignés dans l’ouvrage.

La composition N1 est distinguée de la dissertation terminale : deux heures, sur un axe ou un objet conclusif du programme de Première, spécialité non poursuivie. Les coefficients 8 pour cette spécialité et 16 pour la spécialité terminale sont distingués. Le Grand oral est traité selon le format 20 minutes de préparation et 20 minutes d’oral, avec coefficient 8 en voie générale à partir de 2027 et articulation des deux questions avec les deux spécialités conservées.

Les références S01 à S10 du registre identifient les textes utiles. Le cadre pédagogique N1/N2 ne crée aucune autorisation administrative. L’âge, les dispenses, les notes acquises et le calendrier tunisien du candidat ne sont pas présumés. Le manuel prépare HGGSP, non l’ensemble du baccalauréat. Aucun sujet futur officiel n’est annoncé.

## 5. Contrôles automatiques réellement exécutés

Le détail des **505 contrôles** est dans `CONTROLES_FINAUX.json`. Le script `production/verifier.py` peut les réexécuter sur le paquet. Ils portent sur :

- l’unicité des identifiants et la présence des onze thèmes, 78 jalons, documents, activités, exercices, QCM, solutions et reprises ; les références documentaires codées et les correspondances ;
- les neuf blancs et les formats N1/N2, la distinction des trois thèmes en N2 et la présence des deux dissertations corrigées ;
- les sept originaux, les neuf illustrations, l’ouverture des cinq PDF, l’incorporation des polices, les liens internes et les destinations des signets, y compris le rapprochement entre le titre d’un signet et le texte de sa page cible ;
- l’absence détectée de texte hors page, de caractère de remplacement, de glyphe manquant, de référence LaTeX non résolue ou de débordement horizontal dans les journaux finaux ; les ancres, liens et images des versions HTML ;
- l’absence des blocs de correction dans le volume Sujets seuls.

Un seuil de texte par jalon ne prouve pas l’exhaustivité d’une explication. Ces contrôles ne sont pas les 730 tests historiques de l’ancienne tentative ; aucune réexécution de ces anciens tests n’est revendiquée.

## 6. Revue visuelle des exports finaux

Une revue itérative a conduit à corriger les symboles, les numéros de sommaire, les destinations de signets, les encadrés des schémas, les placements de figures et les espaces de ponctuation. La dernière passe a examiné **29 pages physiques des PDF finaux**, identifiés par leur empreinte SHA-256 dans `INSPECTION_VISUELLE.json`.

| Fichier | Pages physiques inspectées dans la dernière passe |
|---|---|
| HGGSP_2027_Manuel_Cycle_terminal | 1, 3, 23, 33, 89, 98, 116, 136, 137, 138, 141, 144 |
| HGGSP_2027_Niveau_1_Premiere | 1, 20, 94 |
| HGGSP_2027_Compagnon_Autocorrection | 1, 17, 67, 70 |
| HGGSP_2027_Epreuves_blanches_et_corriges | 1, 7, 23, 24, 25, 43 |
| HGGSP_2027_Epreuves_Sujets_seuls | 1, 11, 14, 16 |

Les pages ont été rendues avec MuPDF/PyMuPDF puis examinées visuellement. Les échantillons couvrent les couvertures, le sommaire, des ouvertures de cours, des tableaux, les documents, des cartes/schémas et leurs légendes, des calculs d’autocorrection, des QCM et les deux dissertations et l’étude critique d’un blanc. Aucun chevauchement, texte tronqué ou caractère manquant n’a été détecté sur ces pages. La poursuite de certains tableaux à la page suivante reste lisible.

Cette liste atteste une **revue visuelle ciblée**, pas la lecture visuelle exhaustive de toutes les pages et pas une certification PDF/UA.

## 7. Portabilité et intégrité du paquet

Les entrées canoniques sont sous `sources/`. Les assemblages sous `production/assemblages/` et les exports sont générés. Les scripts calculent leurs chemins depuis leur propre emplacement, sans dépendance à l’ancien `_hggsp_work/`. Les cinq journaux LaTeX finaux sont conservés sous `verification/journaux/`. Les dépendances et commandes figurent dans `LISEZMOI.md`.

L’archive ne contient ni fichiers de police, ni environnement virtuel, ni caches Python, ni fichiers temporaires LaTeX. Les polices utilisées dans les PDF sont incorporées. Les illustrations nécessaires sont livrées ; leur régénération est facultative. Aucun script n’effectue de publication, de modification distante ou de téléchargement automatique.

Un manifeste SHA-256 décrit les fichiers livrés, à l’exception de lui-même. Le contrôle de l’archive vérifie le CRC, les tailles et les empreintes. Un rapport de contrôle de livraison externe accompagne l’archive. La consultation locale commence par `index.html` ; les volumes HTML sont utilisables hors connexion, hors consultation de leurs liens bibliographiques externes.

## 8. Limites et statut éditorial

**Statut : édition 1.0 livrée ; couverture rédactionnelle des onze thèmes et des 78 jalons contrôlée ; cinq volumes fabriqués ; aucun échec des contrôles exécutés.**

L’ouvrage n’a pas fait l’objet d’une relecture disciplinaire indépendante ni d’une homologation ministérielle. Les documents adaptés et synthèses éditoriales ne sont pas des citations authentiques d’acteurs. Les exemples contemporains sont arrêtés à la date de cette édition et devront être actualisés lorsque nécessaire. Une utilisation éditoriale commerciale exige aussi une vérification appropriée des droits et crédits. La qualité pédagogique ne se réduit pas aux compteurs ; une expérimentation avec des candidats peut encore conduire à des améliorations.

Le paquet ne présente donc pas ces limites comme des contrôles déjà validés. Aucune anomalie technique bloquante n’a été identifiée dans le périmètre effectivement vérifié.
