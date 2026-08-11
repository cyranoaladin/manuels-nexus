# SKILLS.md — Compétences de production du corpus NSI

## 1. Objectif du fichier

Ce fichier définit les compétences opérationnelles nécessaires pour produire, auditer et publier les ressources NSI du dépôt.

Chaque compétence décrit :

* son objectif ;
* ses entrées ;
* ses sorties ;
* ses critères d’acceptation ;
* ses erreurs bloquantes.

## 1.1. Liste canonique des compétences

Compétences essentielles : inventorier les ressources ; mapper le programme officiel ;
rédiger cours ; rédiger trace ; rédiger TD ; rédiger TP ; rédiger évaluation ;
rédiger corrigé ; produire QCM ; produire guide professeur ; contrôler la qualité
pédagogique ; contrôler la qualité technique ; publier ; juger la substance ;
connecter le corpus au RAG ; intégrer `/AUDIT` ; réconcilier couverture programme ;
rendre une unité chartée ; piloter les gates ; scraper/classifier les sources.

## 2. Métadonnées communes obligatoires

## 2.1. Recherche de sources locales

Avant toute recherche dans un Drive distant, utiliser le miroir local `Documents_DRIVE`
placé à côté du dépôt, ou le dossier indiqué par `NSI_DOCUMENTS_DRIVE_ROOT`. Le chemin local
consulté doit être reporté dans `source`, `Source possible`, `drive_inventory.csv` ou le
registre de documents manquants. Cette substitution ne vaut pas validation pédagogique : un
fichier importé ou adapté depuis `Documents_DRIVE` reste `needs_review` jusqu’à relecture
humaine et contrôles QA.

**Attention aux placeholders génériques.** Des `objectifs` de la forme « Objectif O1 – Identifier précisément la représentation ou la structure en jeu » sont des **placeholders génériques** et constituent une erreur qualité bloquante, pas un objectif valide. Leur présence dans un document doit être détectée et corrigée avant toute promotion de statut.

Chaque document pédagogique doit commencer par un bloc de métadonnées.

```yaml
---
title: ""
level: "premiere | terminale"
sequence_id: ""
document_type: "cours | trace | td | tp | corrige | evaluation | guide_prof | fiche_methode | aides | qcm | projet"
status: "draft | needs_content | needs_review | validated_pedagogy | validated_science | validated_technical | published"
version: "0.1.0"
authors:
  - ""
official_program:
  source: ""
  rubrique: ""
  capacities:
    - ""
prerequisites:
  - ""
learning_objectives:
  - ""
duration: ""
difficulty: "socle | standard | approfondissement"
differentiation:
  fragile:
    - ""
  standard:
    - ""
  expert:
    - ""
assessment:
  formative: true
  summative: false
private_data: false
last_review:
  pedagogy: ""
  science: ""
  technical: ""
---
```

Un document sans métadonnées complètes ne peut pas être publié.

## 3. Skill : inventorier les ressources

### Objectif

Construire un inventaire exhaustif et fiable des ressources.

### Entrées

* dossiers Drive ;
* dépôt local ;
* PDF ;
* fichiers LaTeX ;
* Markdown ;
* scripts Python ;
* notebooks ;
* images ;
* CSV ;
* évaluations ;
* corrigés.

### Sorties

* `manifest.csv`
* `inventory_report.md`
* `duplicates_report.md`
* `reuse_candidates.md`
* `obsolete_report.md`

### Critères d’acceptation

* chaque fichier a un chemin, un type, un niveau, un thème, un statut ;
* les doublons sont détectés par hash de contenu ;
* les fichiers techniques parasites sont exclus ;
* les ressources contenant des données personnelles sont signalées ;
* les fichiers non classés sont listés séparément.

### Erreurs bloquantes

* inventaire limité au dépôt nouvellement généré ;
* inventaire qui ignore les ressources Drive ;
* doublons détectés uniquement par nom ;
* fichiers `__pycache__` indexés comme ressources pédagogiques.

## 4. Skill : mapper le programme officiel

### Objectif

Relier chaque capacité officielle à des ressources réelles.

### Entrées

* programmes officiels ;
* `manifest.csv` ;
* documents pédagogiques.

### Sorties

* `coverage.md`
* `programme_matrix_premiere.md`
* `programme_matrix_terminale.md`
* `missing_capabilities.md`

### Critères d’acceptation

Une capacité peut être marquée `covered` uniquement si elle est présente dans :

* le cours ;
* une activité ;
* un exercice ;
* une évaluation ;
* un corrigé.

Sinon elle doit être marquée :

* `absent` ;
* `partial` ;
* `needs_review`.

### Erreurs bloquantes

* marquer une capacité couverte à partir du seul titre d’un document ;
* associer une séquence entière à toutes les capacités d’un thème ;
* confondre présence d’un fichier et couverture pédagogique.

### Compléments (couverture étendue)

La couverture doit indexer `03_progressions/supports/**` et produire `coverage_sources.md` traçant la provenance de chaque association capacité → ressource. Avant de déclarer une capacité `absent`, distinguer explicitement :

* **trou de contenu** : aucune ressource n’enseigne cette capacité ;
* **trou d’étiquetage** : le contenu existe probablement dans une autre séquence mais n’est pas étiqueté avec la bonne `capacity_id`.

Cette distinction est obligatoire pour éviter de produire du contenu redondant.

## 5. Skill : rédiger un cours élève

### Objectif

Produire un cours complet, clair, rigoureux et exploitable.

### Structure obligatoire

1. Situation-problème.
2. Objectifs.
3. Prérequis.
4. Activité d’introduction.
5. Formalisation.
6. Définitions.
7. Exemples corrigés.
8. Traces d’exécution ou schémas si pertinent.
9. Méthodes.
10. Erreurs fréquentes.
11. Exercices courts.
12. Synthèse.
13. Auto-évaluation.
14. Ouverture ou approfondissement.

### Critères d’acceptation

* au moins trois exemples corrigés ;
* au moins un contre-exemple ou piège ;
* vocabulaire scientifique précis ;
* aucune approximation non signalée ;
* cohérence avec le programme ;
* exercices intégrés ;
* renvoi vers TD/TP/évaluation.

### Erreurs bloquantes

* simple résumé ;
* absence d’exemples ;
* absence d’exercices ;
* contenu déclaratif sans activité ;
* cours non lié aux capacités officielles.

## 6. Skill : rédiger une trace écrite

### Objectif

Produire une synthèse mémorisable, structurée et utilisable par les élèves.

### Structure obligatoire

1. Notions essentielles.
2. Définitions.
3. Méthodes.
4. Exemples minimaux.
5. Points de vigilance.
6. À savoir refaire.
7. Auto-positionnement.

### Critères d’acceptation

* trace courte mais complète ;
* pas de surcharge ;
* formulations précises ;
* utilisable comme support de révision.

## 7. Skill : rédiger un TD

### Objectif

Construire une progression d’exercices.

### Structure obligatoire

1. Exercices de consolidation.
2. Exercices d’application directe.
3. Exercices d’analyse de code.
4. Exercices d’écriture de code.
5. Exercices de justification.
6. Exercice d’approfondissement.
7. Barème ou niveau de difficulté.

### Critères d’acceptation

* exercices progressifs ;
* consignes précises ;
* corrigé complet disponible ;
* lien clair avec les capacités officielles ;
* différenciation visible.

### Erreurs bloquantes

* exercices non corrigés ;
* exercices sans progression ;
* questions trop vagues ;
* exercices hors programme non signalés.

## 8. Skill : rédiger un TP

### Objectif

Produire une activité pratique complète.

### Structure obligatoire

1. Contexte.
2. Objectif du TP.
3. Fichiers fournis.
4. Travail attendu.
5. Étapes guidées.
6. Tests à réaliser.
7. Livrable attendu.
8. Critères de réussite.
9. Aides progressives.
10. Extension avancée.

### Critères d’acceptation

* TP réalisable en durée annoncée ;
* code testable ;
* consignes non ambiguës ;
* jeu de tests fourni ;
* livrable clair ;
* corrigé ou solution professeur disponible.

### Erreurs bloquantes

* TP sans fichier ou sans code ;
* consignes impossibles à exécuter ;
* absence de tests ;
* absence de corrigé professeur.

## 9. Skill : rédiger une évaluation

### Objectif

Produire une évaluation fiable, équilibrée et exploitable.

### Structure obligatoire

1. Durée.
2. Matériel autorisé.
3. Compétences évaluées.
4. Barème.
5. Questions de restitution.
6. Questions d’analyse.
7. Questions de programmation.
8. Questions de justification.
9. Question de synthèse.
10. Corrigé détaillé.

### Critères d’acceptation

* barème explicite ;
* difficulté progressive ;
* questions alignées sur le cours ;
* pas de piège gratuit ;
* corrigé complet ;
* grille de compétences.

### Erreurs bloquantes

* évaluation sans corrigé ;
* barème absent ;
* question hors programme non signalée ;
* évaluation uniquement déclarative.

## 10. Skill : rédiger un corrigé

### Objectif

Produire un corrigé explicatif, pas seulement une liste de réponses.

### Structure obligatoire

1. Réponse attendue.
2. Justification.
3. Méthode.
4. Erreurs fréquentes.
5. Variante acceptable.
6. Barème détaillé si évaluation.

### Critères d’acceptation

* toutes les questions sont corrigées ;
* les raisonnements sont explicités ;
* le code est testé ;
* les erreurs fréquentes sont mentionnées.

## 11. Skill : produire un QCM

### Objectif

Créer un QCM utile pour l’apprentissage, pas seulement pour la vérification.

### Format obligatoire

Chaque question doit contenir :

* énoncé ;
* choix ;
* bonne réponse ;
* explication ;
* difficulté ;
* capacité officielle ;
* erreur ciblée.

### Critères d’acceptation

* distracteurs plausibles ;
* explication pour chaque réponse ;
* au moins trois niveaux de difficulté ;
* export JSON valide.

## 12. Skill : produire un guide professeur

### Objectif

Donner au professeur une vraie stratégie de séance.

### Structure obligatoire

1. Objectifs pédagogiques.
2. Durée.
3. Déroulé séance par séance.
4. Points de vigilance.
5. Difficultés prévisibles.
6. Différenciation.
7. Questions à poser.
8. Correction commentée.
9. Modalités d’évaluation.
10. Prolongements.

### Critères d’acceptation

* utilisable sans relire tous les fichiers ;
* timings crédibles ;
* remédiations prévues ;
* conseils concrets.

## 13. Skill : contrôler la qualité pédagogique

### Objectif

Refuser les documents superficiels.

### Critères minimaux

Un document est refusé si :

* il contient des sections vides ;
* il contient des formulations génériques ;
* il contient des placeholders ;
* il n’a pas d’exemples ;
* il n’a pas d’exercices ;
* il n’a pas de lien avec le programme ;
* il n’a pas de différenciation ;
* il n’a pas de corrigé associé quand nécessaire.

### Clause anti-fitting

Un contrôle ne doit jamais être assoupli pour passer. Les seuils sont justifiés *a priori* (par les exigences du programme et les attentes pédagogiques), pas calés *a posteriori* sur le corpus existant. Élargir une liste de marqueurs ou abaisser un seuil pour rendre un gate vert est interdit — c'est du fitting, pas de la qualité. Si un contrôle échoue, corriger le contenu ou écrire un BLOCKER.

### Commande cible

```bash
python -m scripts.check_quality_gates
```

## 14. Skill : contrôler la qualité technique

### Objectif

Garantir que tous les scripts et exemples fonctionnent.

### Critères

* code Python exécutable ;
* tests unitaires présents ;
* pas de dépendances non documentées ;
* pas de chemins absolus ;
* pas de fichiers parasites indexés ;
* pas de `__pycache__` dans les livrables.

## 15. Skill : publier

### Objectif

Produire une version propre pour les élèves et une version professeur.

### Critères

* seuls les documents `published` sont exportés ;
* les corrigés ne sont pas inclus dans le paquet élève ;
* les données personnelles sont absentes ;
* les PDF ou exports HTML sont générés ;
* l’index pédagogique est propre ;
* le rapport de publication est produit.

## 16. Skill : juger la substance d’une capacité

### Objectif

Statuer sur l’enseignement réel d’une capacité dans le corpus.

### Entrées

* intitulé officiel exact de la capacité (depuis `programme_nsi_2019.yaml`) ;
* contrat de l’unité (séquence, rôles attendus) ;
* sections candidates, idéalement fournies par le RAG interne (`nsi_corpus`) quand le smoke réel est vert, pas la première section du fichier.

### Sorties

* verdict cité par capacité : `validated_pedagogy`, `needs_content`, `needs_review` ;
* citation pertinente extraite du corpus avec `path` et `anchor` ;
* justification du verdict.

### Critères d’acceptation

* la citation enseigne *cette* capacité (pertinence vérifiée, pas un objectif générique) ;
* verdict `validated_pedagogy` seulement si les trois preuves (cours, entraînement, correction) sont pertinentes et que le relecteur (humain ou LLM) le confirme ;
* le juge n’est jamais l’auteur du contenu jugé.

### Erreurs bloquantes

* citer un objectif générique (« Objectif O1 – Identifier précisément… ») comme preuve ;
* réutiliser la même citation pour plusieurs capacités ou plusieurs rôles ;
* produire un verdict sans relecture qui prétende juger la substance ;
* utiliser un stub déterministe classé `blocking_substance`.

## 17. Skill : connecter le corpus au RAG

### Objectif

Établir et maintenir la connexion entre le corpus NSI et le magasin vectoriel RAG pour alimenter le juge de substance et l’oracle de cohérence.

### Backend vectoriel

* **Moteur** : ChromaDB v1.1.1
* **Collections observées ou prévues** :
  - `rag_education` : inspiration externe / Drive / ressources ouvertes, jamais preuve de couverture interne.
  - `nsi_corpus` : collection cible du corpus interne pour le juge de substance, mais son accès `/search` authentifié est bloqué tant que le timeout persiste.
  - `nsi_golden_examples` : collection éventuelle pour les pilotes `premiere/sequences` et `terminale/sequences`, avec `usable_for_coverage=false`.
  - `nsi_official` : textes officiels.
  - `nsi_annales` : annales publiques si licence OK.
* **Distance** : cosine, **dimension** : 768

### État actuel et prérequis d’ingestion

État bloquant : `/health` répond et `/search` sans token renvoie `HTTP 401`,
mais `/search` authentifié time out. Le dépôt ne déclare donc pas le RAG
fonctionnel et le juge de substance doit rester conservateur.

**Script d’ingestion** : `scripts/ingest_nsi_corpus.py`. Il prépare uniquement
`03_progressions/supports/` et `03_progressions/fiches_cours/` pour
`nsi_corpus`. Métadonnées canoniques par chunk : `path`, `level`,
`sequence_id`, `document_type`, `theme`, `notion`, `capacity_ids`, `status`,
`section_anchor`, `sha256`, `chunk_index`, `source_type`, `proof_scope`,
`private_data`. Les anciens champs `anchor` et `capacities` ne sont que des
alias de transition.

### Modèle d’embedding

* **Modèle** : `nomic-embed-text` (servi par Ollama v0.3.13)
* **Dimension** : 768 (correspond aux collections existantes)
* **Accès** : interne au Docker (Ollama sur port 11434 loopback) ; l’API `/search` embarque l’embedding

### Contrat de requête attendu

Requête minimale requise avant toute déclaration de fonctionnement :

```
POST https://rag-api.nexusreussite.academy/search
Headers:
  Content-Type: application/json
  Authorization: Bearer <RAG_API_KEY>
Body:
  {"q": "<texte>", "collection": "nsi_corpus", "k": 5, "include_documents": true}
```

Réponse attendue : `{"query", "collection", "k", "returned", "hits": [{"id", "metadata", "document", "score"}]}`.
Tant que cette réponse time out, le RAG reste bloquant.

Pour un accès direct à ChromaDB ou Ollama, un tunnel SSH est nécessaire (port 11435 pour éviter conflit Ollama local) :
`ssh -L 11435:127.0.0.1:11434 -L 8000:127.0.0.1:8000 root@<host>`

### Usage cible après smoke vert

1. **Juge de substance** : interroger `nsi_corpus` avec l’intitulé officiel de la capacité pour récupérer des sections candidates, puis appliquer le veto mécanique et la revue humaine.
2. **Oracle de cohérence inter-séquences** : proposer des divergences ou prérequis à auditer, sans promouvoir de statut.

### Variables de connexion

Voir `.env.rag.example` pour le modèle de configuration. **Ne jamais recopier de secret dans ce fichier ni dans aucun `.md`.**

### Critères d’acceptation

* `scripts/rag_smoke_test.py` passe sans erreur sur `/search` authentifié ;
* les secrets restent dans `.env.rag` (chmod 600, gitignoré) ;
* aucun secret n’apparaît dans les rapports, les logs, ni les fichiers committés.

### Erreurs bloquantes

* committer `.env.rag` ou un secret en clair ;
* utiliser des valeurs devinées au lieu de valeurs découvertes sur le serveur ;
* déclarer la connexion fonctionnelle sans preuve d’exécution (smoke test).

## 18. Skill : intégrer `/AUDIT`

### Objectif

Exploiter les rapports d’audit comme traces de pilotage sans les indexer comme ressources
pédagogiques ni les ingérer dans `nsi_corpus`.

### Critères

* `/AUDIT` reste hors corpus pédagogique ;
* les rapports peuvent nourrir les plans d’action ;
* aucune donnée sensible ou élève n’est réinjectée dans les supports.

## 19. Skill : réconcilier couverture programme

### Objectif

Transformer les statuts `absent` et `partial` en actions explicites sans promouvoir
`covered`.

### Critères

* chaque capacité absente possède une action suivante ;
* toute preuve reste documentaire tant qu’une revue humaine n’est pas tracée ;
* `covered = 0` est maintenu.

## 20. Skill : rendre une unité chartée

### Objectif

Produire les artefacts élève/professeur d’une unité pilote sans fuite de corrigé ni
régression de charte.

## 21. Skill : piloter les gates

### Objectif

Exécuter `audit-core`, distinguer `audit-metrics`, et refuser tout ajustement de gate
destiné à masquer une lacune.

## 22. Skill : scraper/classifier les sources

### Objectif

Classer chaque source avant usage pédagogique ou RAG.

### Critères

* pas de scraping aveugle ;
* pas de données élèves ;
* pas de source externe comme preuve de couverture interne ;
* chaque source a licence, statut RGPD, politique de réutilisation et collection cible.

## 23. Critère ultime

Un document doit pouvoir répondre à cette question :

> Un élève sérieux peut-il apprendre, s’entraîner, se corriger et progresser avec cette ressource ?

Si la réponse est non, le document n’est pas publiable.
