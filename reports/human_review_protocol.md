# Protocole de revue humaine NSI

Statut du dépôt : NON_RELEASE_READY. Ce protocole prépare la validation humaine mais ne valide aucune ressource à lui seul.

## Objectif

La revue humaine vérifie qu'une ressource `needs_review` peut être examinée sans confondre complétude documentaire, exactitude scientifique, qualité pédagogique et publication.

## Périmètre minimal

Pour chaque ressource relue :

1. identifier le niveau, la séquence, la notion et les capacités officielles ;
2. lire le support élève et les documents professeur associés ;
3. vérifier les exercices, corrigés, barèmes, remédiations et versions aménagées ;
4. contrôler l'absence de données personnelles ;
5. consigner les décisions dans un rapport de revue horodaté.

## Décisions possibles

- `needs_review` maintenu : correction ou relecture complémentaire nécessaire ;
- `validated_science` proposé : exactitude scientifique relue, sans validation pédagogique ;
- `validated_pedagogy` proposé : exploitation classe relue, sans publication automatique ;
- `validated_technical` proposé : code et tests relus ;
- `published` proposé uniquement après validation pédagogique, scientifique, technique, RGPD et décision de publication.

## Preuves attendues

Chaque décision doit citer :

- fichier relu ;
- version ou commit ;
- relecteur ;
- date ;
- points vérifiés ;
- anomalies restantes ;
- décision signée ou explicitement horodatée.

## Blocage

Sans revue humaine tracée, les statuts restent `needs_review`, `covered` reste `0`, `validated_*` reste `0` et `published` reste `0`.
