# Registre v2 des supports manquants

Les supports P00-P05 et T00-T05 existent en version prototype renforcée et restent en `needs_review`.
Les supports P06-P09 / T06-T09 et P10-P14 / T10-T19 rattachés aux fiches de cours existent désormais en `needs_review`.
Ce registre ne transforme aucune fiche en preuve de couverture : il distingue les dettes actives, les dettes générales et les entrées abandonnées.

## Fiches de cours systématiques

Les fiches de cours annuelles ont été créées dans `03_progressions/fiches_cours/` pour P00-P14 et T00-T19. Elles restent toutes en `needs_review`; elles ne rendent aucune capacité `covered` et ne remplacent pas les cours, TD, TP, corrigés, évaluations ni barèmes.

| Niveau | Séquences | Fiches créées | Statut | Blocage si absent |
|---|---:|---:|---|---|
| premiere | P00-P14 | 21 | needs_review | oui |
| terminale | T00-T19 | 23 | needs_review | oui |

## Supports absents bloquant une fiche liée

Aucun support absent ne bloque actuellement une fiche de cours liée : les 44 fiches sont opérationnelles au sens strict, sans validation pédagogique ni couverture publiable.

| Fichier | Niveau | Séquence | Séance(s) | Type | Priorité | Statut | Responsable | Date cible | Source possible | Lien Drive éventuel | Dépendance | Décision | Blocage si absent | Fiche(s) concernée(s) | Impact pédagogique |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|


## Dettes pédagogiques générales non liées à une fiche opérationnelle

Ces lignes sont des dettes de production ou de mutualisation. Elles ne doivent pas entrer dans le calcul de readiness des fiches opérationnelles.

| Fichier | Niveau | Séquence | Séance(s) | Type | Priorité | Statut | Responsable | Date cible | Source possible | Lien Drive éventuel | Dépendance | Décision | Blocage si absent | Fiche(s) concernée(s) | Impact pédagogique |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| supports_projets_semestre2.md | mixte | projets | séances projet hors lot prêt | livrable projet | moyenne | absent | equipe NSI | 2027-03-15 | Documents_DRIVE/NSI_Tle/projet_biblio | NA | supports disciplinaires | importer | non | progression annuelle | Dette générale : limite le réemploi des projets du semestre 2, sans bloquer une fiche opérationnelle. |
| banque_remediation_semestre2.md | mixte | remédiation | séances de consolidation hors lot prêt | remediation | moyenne | absent | equipe NSI | 2027-03-30 | Documents_DRIVE | NA | retours évaluations | créer | non | progression annuelle | Dette générale : remédiations mutualisées encore absentes, sans bloquer une fiche opérationnelle. |
| check_first_batch_alignment.py (gate regex) | mixte | toutes | NA | gate | basse | dette | equipe NSI | prochaine PR gates | scripts/check_first_batch_alignment.py:93 | NA | regex exercice_sans_corrigé | créer | non | T07 exercice 3bis | Dette gate : la regex `(\d+)\b` (L93) ignore les suffixes non numériques (3bis, 4ter). Un exercice 3bis sans corrigé 3bis passe le gate silencieusement. Correction : remplacer par `(\d+\w*)` et comparer les identifiants complets. Test adverse : exercice 3bis dans TD sans corrigé 3bis → doit être ROUGE. |


## Archives / abandon

Ces lignes gardent trace d'associations incohérentes retirées du registre actif. Elles ne doivent plus être citées dans les séances ni dans les fiches opérationnelles.

| Fichier | Niveau | Séquence | Séance(s) | Type | Priorité | Statut | Responsable | Date cible | Source possible | Lien Drive éventuel | Dépendance | Décision | Blocage si absent | Fiche(s) concernée(s) | Impact pédagogique |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| P06_supports_logique_predicats.md | premiere | P06 | P06-S1 à P06-S6 | cours | haute | abandonné | equipe NSI | 2027-01-20 | Documents_DRIVE/Algo_Premiere | NA | P03-P05 | abandonner | non | aucune fiche opérationnelle | Association obsolète : le support ne correspond pas à P06 tables/recherche/tri et ne doit plus fausser la readiness. |
| P07_supports_web_client.md | premiere | P07 | P07-S1 à P07-S6 | tp | haute | abandonné | equipe NSI | 2027-02-10 | Documents_DRIVE/2_NSI/départ_Mercier | NA | P06 | abandonner | non | aucune fiche opérationnelle | Association obsolète : thème web client incompatible avec P07 fonctions/tests/spécifications. |
| P08_supports_reseaux.md | premiere | P08 | P08-S1 à P08-S7 | cours | haute | abandonné | equipe NSI | 2027-02-28 | Documents_DRIVE | NA | P07 | abandonner | non | aucune fiche opérationnelle | Association obsolète : thème réseaux incompatible avec les fiches P08 HTML/CSS/DOM et HTTP/formulaires. |
| T06_supports_graphes_parcours.md | terminale | T06 | T06-S1 à T06-S6 | cours | haute | abandonné | equipe NSI | 2027-01-20 | Documents_DRIVE/NSI_Tle | NA | T03-T05 | abandonner | non | aucune fiche opérationnelle | Association obsolète : graphes/parcours ne correspond pas à T06 arbres binaires de recherche. |
| T07_supports_bases_donnees.md | terminale | T07 | T07-S1 à T07-S6 | tp | haute | abandonné | equipe NSI | 2027-02-10 | Documents_DRIVE/NSI_Tle/Séquence3_Conception BDD relationnelle | NA | T06 | abandonner | non | aucune fiche opérationnelle | Association obsolète : bases de données ne correspond pas à T07 graphes modélisation/listes/matrices. |
| T08_supports_architecture_processus.md | terminale | T08 | T08-S1 à T08-S8 | cours | haute | abandonné | equipe NSI | 2027-02-28 | Documents_DRIVE/NSI_Tle/Séquence5_Architecture | NA | T07 | abandonner | non | aucune fiche opérationnelle | Association obsolète : architecture/processus ne correspond pas à T08 BFS/DFS/cycles/chemins. |
