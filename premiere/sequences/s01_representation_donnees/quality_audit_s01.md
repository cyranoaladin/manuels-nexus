---
title: "Audit qualité - s01_representation_donnees"
niveau: premiere
source: "BO spécial n°1 du 22 janvier 2019 - NSI Première"
status: needs_review
version: "0.2.0"
notion: "représentation des données de base et types construits"
objectifs: "Auditer séparément les documents de la séquence pilote Première après refonte."
sequence: s01_representation_donnees
private_data: false
---

# Audit qualité - s01_representation_donnees

## Périmètre

Séquence auditée : `premiere/sequences/s01_representation_donnees/`.

Documents inspectés : [cours_eleve.md](./cours_eleve.md), [trace_ecrite.md](./trace_ecrite.md), [td.md](./td.md), [tp.md](./tp.md), [corrige.md](./corrige.md), [guide_professeur.md](./guide_professeur.md), [evaluation.md](./evaluation.md), [qcm.json](./qcm.json), [projet_associe.md](./projet_associe.md), [fiche_methode.md](./fiche_methode.md), [aides_progressives.md](./aides_progressives.md).

Fichiers techniques inspectés : [python/representation_tools.py](./python/representation_tools.py), [tests/test_representation_tools.py](./tests/test_representation_tools.py).

Statut général : `needs_review`.

Aucune publication n'est déclarée pour cette séquence.

## Décision sur le titre

La séquence est conservée comme pilote unique.

Le titre cible est : représentation des données de base et premiers types construits.

Limite assumée : les listes, tuples et dictionnaires sont introduits comme choix de représentation Python, pas comme séquence autonome sur les tables.

La partie tables de données n'est pas déclarée couverte par cette séquence.

## Profondeur du cours

Le cours traite les bits, bases 2, 10 et 16, entiers positifs, entiers relatifs en complément à deux, booléens, texte ASCII et Unicode, listes, tuples, dictionnaires et choix de représentation.

Chaque notion principale contient une définition, un exemple, un contre-exemple, un exercice intégré, une erreur fréquente et un lien vers le TD ou le TP.

Le cours reste dense pour une première séquence ; une relecture par enseignant est nécessaire pour vérifier le rythme en classe.

Point de vigilance : l'articulation entre représentation machine et types construits Python doit rester explicite à l'oral.

## Qualité scientifique

Les conversions de bases et le complément à deux sont traités avec des fonctions Python testées.

La distinction entre valeur, représentation et type Python est présente.

Les limites de plage en complément à deux sont abordées.

ASCII et Unicode sont distingués.

Point de vigilance : une relecture scientifique externe est encore nécessaire avant tout statut de publication.

## Progressivité

La progression va du bit vers les bases, puis vers les entiers, les booléens, le texte et les structures Python simples.

Les activités intégrées alternent manipulation papier, calcul, lecture de code et écriture de code.

Les aides progressives existent pour les élèves fragiles.

Point de vigilance : le passage vers les dictionnaires peut être exigeant si la classe n'a pas encore consolidé les listes.

## Exercices

Le TD comporte une progression socle, standard et expert.

Les exercices incluent conversion, complément à deux, booléens, texte, choix de représentation, lecture de code et écriture de code.

Les justifications sont demandées explicitement.

Point de vigilance : la correction doit être relue pour vérifier l'adéquation au barème de l'établissement.

## TP

Le TP mobilise le fichier [python/representation_tools.py](./python/representation_tools.py).

Il demande des tests, des cas limites et un livrable identifiable.

Les critères de réussite sont explicités.

Point de vigilance : vérifier en classe que l'environnement Python charge correctement le module local.

## Corrigé

Le corrigé couvre les exercices du TD, le TP et l'évaluation.

Il inclut des justifications, des variantes acceptables, des erreurs fréquentes et du code de référence.

Point de vigilance : les variantes de code doivent être testées si elles sont ajoutées ultérieurement.

## Guide professeur

Le guide précise objectifs, durée, scénario, difficultés prévisibles, remédiations, différenciation, questions orales, critères et prolongements.

Il signale les limites de périmètre.

Point de vigilance : le découpage séance par séance doit être ajusté aux contraintes locales.

## QCM

Le QCM contient au moins huit questions.

Les questions indiquent difficulté, capacité officielle, erreur ciblée, propositions et explications.

Point de vigilance : les distracteurs doivent être testés auprès d'élèves pour mesurer leur pertinence.

## Évaluation

L'évaluation contient durée, matériel autorisé, compétences évaluées, barème, questions progressives, programmation, justification, analyse de code et lien vers le corrigé.

Point de vigilance : l'épreuve peut nécessiter deux versions selon l'accès ou non à Python pendant l'évaluation.

## Différenciation

Les aides progressives proposent plusieurs niveaux de guidage.

La fiche méthode soutient le choix de représentation.

Le guide professeur propose des adaptations pour élèves fragiles et élèves avancés.

Point de vigilance : la différenciation reste à observer en situation réelle.

## Cohérence avec programme officiel

Les preuves explicites sont déclarées dans le frontmatter des documents pédagogiques.

Les capacités ciblées concernent représentation des données de base, types construits et écriture de fonctions simples.

Les capacités non attestées restent absentes ou partielles dans `coverage.md`.

La séquence ne doit pas être utilisée pour déclarer la couverture du traitement des tables.

## Bloquants restants

Aucune ressource Drive n'est intégrée.

Aucun statut final n'est attribué.

Une relecture pédagogique et scientifique externe reste nécessaire.

Les preuves de terrain en classe ne sont pas disponibles.

## Conclusion d'audit

La séquence est une base pilote en `needs_review`.

Elle n'est pas une ressource publiable.
