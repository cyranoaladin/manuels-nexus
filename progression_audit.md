# Audit des progressions annuelles

- Statut global : NON PUBLIABLE.
- Objet : vérifier que les progressions Première et Terminale s'appuient sur le calendrier Tunisie 2026-2027 et réservent au moins un quart de l'horaire aux projets.
- Décision : ne pas générer de nouvelles séquences.
- Limite : cet audit vérifie la planification annuelle ; il ne remplace pas une revue pédagogique et scientifique des documents.

## Synthèse

| Point contrôlé | Première | Terminale | Décision |
|---|---|---|---|
| Calendrier Tunisie 2026-2027 utilisé | oui | oui | acceptable pour prototype |
| Horaire annuel estimé | 140 h | 210 h | hypothèse explicite |
| Projet minimal requis | 35 h | 52,5 h | seuil 25 % |
| Projet planifié | 43 h | 60 h | seuil dépassé |
| Ratio projet | 30,7 % | 28,6 % | conforme au seuil de planification |
| Toutes les capacités YAML identifiées sont planifiées | oui | oui | planification uniquement |
| Séquences pilotes publiées | non | non | non publiable |
| Ressources Drive intégrées localement | non | non | bloqueur publication |

## Points acceptables pour le prototype

- Le calendrier mensuel est intégré, avec Ramadan du 8 février au 7 mars, Aïd al-Fitr du 8 au 10 mars et Aïd al-Adha les 17 et 18 mai.
- Les progressions ne se limitent plus à quelques dizaines d'heures : elles utilisent une hypothèse annuelle de 140 h en Première et 210 h en Terminale.
- Les projets sont annualisés, jalonnés et explicitement reliés aux séquences.
- Les périodes sensibles allègent les évaluations lourdes et favorisent révision, accompagnement ou travail guidé.

## Bloquants maintenus

- Les ressources Drive sont référencées mais non intégrées localement.
- Les documents pédagogiques restent en revue de fond.
- Aucune capacité ne doit être déclarée `covered`.
- Aucune ressource ne doit passer en publication.
- Les deux séquences pilotes restent trop larges pour une publication directe.

## Décisions sur les séquences pilotes

### Première

La séquence `premiere/sequences/s01_representation_donnees/` est conservée comme prototype de consolidation. La progression découpe son contenu : bits et bases en P01, complément à deux et booléens en P02, texte et encodage en P03, types construits en P04, tables CSV en P05-P06, tests en P07. Les flottants, tables CSV, recherche, tri et fusion sont planifiés dans des séquences dédiées et ne sont pas couverts par le pilote seul.

### Terminale

La séquence `terminale/sequences/s01_structures_donnees_interfaces_implementations/` est conservée comme prototype de consolidation. La progression sépare structures abstraites, POO, piles/files/dictionnaires, graphes, BFS/DFS et ABR. T-ALGO-02 reste `partial` tant que la séquence graphes dédiée n'a pas été produite et relue. T-ALGO-01 n'est pas porté par la séquence pilote structures.

## Contrôles attendus

- `check_progression_calendar_alignment.py` doit échouer si une progression n'utilise pas le calendrier, oublie une séquence imposée, réintroduit l'ancien nom Terminale ou ne planifie pas une capacité du YAML.
- `check_project_quarter_requirement.py` doit échouer si les projets représentent moins de 25 % de l'horaire ou si les plans projet ne contiennent pas micro-projets, jalons, livrables, carnet de bord, soutenance, grille, différenciation, groupes, RGPD, données fictives et oral.

## Prochaine action unique recommandée

Relire pédagogiquement et scientifiquement les deux séquences pilotes à partir de ces progressions, sans créer de nouvelle séquence tant que cette revue n'est pas effectuée.
