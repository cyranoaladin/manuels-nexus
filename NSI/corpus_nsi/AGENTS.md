# AGENTS.md — Corpus NSI Première / Terminale

## 1. Mission générale

Ce dépôt vise à produire un corpus pédagogique complet, rigoureux et exploitable pour l’enseignement de spécialité NSI en Première et Terminale.

La priorité absolue n’est pas la quantité de fichiers produits, mais la qualité pédagogique, scientifique, académique, éditoriale et technique de chaque document.

Aucun document ne doit être une coquille vide, une fiche superficielle, une paraphrase approximative du programme ou un remplissage automatique. Chaque ressource doit avoir une vraie valeur d’enseignement pour les élèves et une vraie valeur d’exploitation pour le professeur.

## 2. Règles non négociables

1. Ne jamais déclarer une capacité officielle “couverte” sans preuve documentaire précise.
2. Ne jamais marquer un document comme validé si son contenu n’a pas été relu selon les critères du présent dépôt.
3. Ne jamais générer massivement des séquences avant validation d’une séquence pilote.
4. Ne jamais produire de document pédagogique sans :

   * objectifs ;
   * prérequis ;
   * capacités officielles ;
   * situation-problème ;
   * contenu disciplinaire substantiel ;
   * exercices ;
   * différenciation ;
   * corrigé ou indications de correction ;
   * métadonnées complètes.
5. Ne jamais intégrer de données personnelles d’élèves dans les ressources publiables.
6. Ne jamais indexer les fichiers techniques parasites : `__pycache__`, `.pyc`, `.aux`, `.log`, `.toc`, `.venv`, `.git`, fichiers temporaires.
7. Ne jamais copier une ressource dans plusieurs banques sans stratégie claire de référence, de lien symbolique ou de génération contrôlée.
8. Ne jamais confondre validation technique et validation pédagogique, ni mécanique et pédagogique : un gate vert sur la forme ne vaut pas preuve de fond.
9. Ne jamais remplacer une preuve de qualité par une simple phrase déclarative.
10. Ne jamais inventer une ressource, une source ou une couverture de programme.
11. Ne jamais affaiblir, élargir ou ajuster un contrôle pour le faire passer. Si un contrôle échoue, corriger le contenu, ou écrire un BLOCKER. Ajuster un test à ses données est interdit et constitue une fraude de gate.
12. Un pré-jugement mécanique (présence d'ancre, extraction de citation) n'est pas un jugement de substance. Aucun script déterministe ne peut être classé `blocking_substance` ni déclarer qu'une capacité est enseignée.
13. Une citation présente ne prouve rien si elle n'est pas pertinente pour la capacité visée. « Ancre vérifiée » ≠ « capacité enseignée ».

## 2.1. Source locale Drive

Les ressources issues du Drive doivent être recherchées localement dans le dossier
`Documents_DRIVE` placé à côté du dépôt, ou dans le dossier indiqué par
`NSI_DOCUMENTS_DRIVE_ROOT`, et non dans un Drive distant, tant que ce miroir local est
disponible. Toute réutilisation doit citer le chemin local consulté dans les métadonnées,
le registre ou le rapport d’inventaire. Une ressource repérée dans `Documents_DRIVE` reste
`needs_review` tant qu’elle n’a pas été auditée, nettoyée des données privées éventuelles
et alignée avec le programme.

## 2.2. Arbre canonique et politique `/AUDIT`

`03_progressions/supports/` est le canon de production. Les dossiers
`premiere/sequences/` et `terminale/sequences/` sont des pilotes historiques et des
exemples de style ; ils ne doivent pas masquer une absence dans `supports/`.

Le dossier `/AUDIT` et tout artefact de build (`dist/`, `01_build_reports/`, caches,
archives, exports temporaires) restent hors corpus pédagogique et hors index RAG.

## 3. Statuts autorisés

Les statuts autorisés sont strictement les suivants :

* `draft` : document en brouillon, non publiable ;
* `needs_content` : structure présente mais contenu insuffisant ;
* `needs_review` : contenu substantiel mais non relu ;
* `validated_pedagogy` : validé pédagogiquement ;
* `validated_science` : validé scientifiquement ;
* `validated_technical` : validé techniquement ;
* `published` : publiable élèves ;
* `archived` : conservé mais non actif ;
* `deprecated` : obsolète.

Les statuts vagues comme `create`, `moyenne`, `à refaçonner` ne doivent pas être utilisés comme statuts finaux.

## 4. Agents et responsabilités

### 4.1. Agent Inventaire

Responsabilités :

* parcourir toutes les ressources disponibles ;
* produire un inventaire exhaustif ;
* identifier les doublons réels par hash de contenu et non seulement par nom ;
* distinguer documents élèves, documents professeurs, corrigés, scripts, données, évaluations ;
* identifier les ressources incomplètes ;
* identifier les ressources exploitables immédiatement ;
* identifier les ressources obsolètes ;
* produire un rapport de tri.

Livrables :

* `manifest.csv`
* `inventory_report.md`
* `duplicates_report.md`
* `obsolete_report.md`
* `reuse_candidates.md`

Critère de validation :

* aucune ressource pédagogique ne doit être absente de l’inventaire ;
* aucun fichier technique parasite ne doit être listé comme ressource pédagogique ;
* les doublons doivent être détectés par contenu et non seulement par nom.

### 4.2. Agent Programme

Responsabilités :

* extraire les capacités officielles du programme de Première et Terminale ;
* construire une matrice de couverture ;
* associer chaque capacité à des documents précis ;
* vérifier que chaque association est justifiée par un contenu réel.

Livrables :

* `programme_matrix_premiere.md`
* `programme_matrix_terminale.md`
* `coverage.md`
* `missing_capabilities.md`

Critère de validation :

Une capacité est “couverte” seulement si elle apparaît dans :

* un cours ;
* une activité ou un TP ;
* un exercice ;
* une évaluation ;
* un corrigé ou une trace de correction.

Sinon elle reste `absent` ou `partial`.

### 4.3. Agent Auteur pédagogique

Responsabilités :

* produire des documents élèves complets ;
* rendre les notions accessibles sans les appauvrir ;
* construire une progression interne cohérente ;
* intégrer des exemples, contre-exemples, erreurs fréquentes et exercices.

Livrables par séquence :

* `cours_eleve.md`
* `trace_ecrite.md`
* `td.md`
* `tp.md`
* `fiche_methode.md`
* `aides_progressives.md`

Critère de validation :

Chaque document doit contenir un contenu substantiel, contextualisé, progressif et exploitable en classe.

### 4.4. Agent Scientifique

Responsabilités :

* vérifier la justesse des définitions ;
* vérifier les algorithmes ;
* vérifier les complexités ;
* vérifier les preuves ;
* vérifier les corrigés ;
* vérifier les limites du programme.

Critère de validation :

Aucune approximation scientifique ne doit rester dans un document publié.

### 4.5. Agent Code

Responsabilités :

* vérifier tous les scripts Python ;
* ajouter des tests unitaires ;
* ajouter des jeux de données si nécessaire ;
* vérifier le style, les annotations et la robustesse ;
* produire des exemples exécutables.

Livrables :

* fichiers `.py` propres ;
* tests unitaires ;
* jeux de tests ;
* documentation d’exécution.

Critère de validation :

Tout code fourni aux élèves doit être exécutable, testé et cohérent avec les objectifs pédagogiques.

### 4.6. Agent Évaluation

Responsabilités :

* concevoir les évaluations ;
* équilibrer connaissances, compréhension, analyse, programmation et justification ;
* fournir barèmes et corrigés ;
* aligner chaque question sur une capacité.

Livrables :

* `evaluation.md`
* `corrige.md`
* `bareme.md`
* `grille_competences.md`
* `qcm.json`

Critère de validation :

Aucune évaluation ne doit être publiée sans corrigé complet ni barème explicite.

### 4.7. Agent Différenciation

Responsabilités :

* prévoir des aides progressives ;
* prévoir des exercices de consolidation ;
* prévoir des extensions expertes ;
* prévoir des modalités d’accompagnement pour élèves fragiles ;
* prévoir des défis pour élèves avancés.

Critère de validation :

Chaque séquence doit proposer au moins trois niveaux d’entrée : socle, standard, approfondissement.

### 4.8. Agent Édition / UI-UX pédagogique

Responsabilités :

* harmoniser la mise en page ;
* garantir la lisibilité ;
* structurer les encadrés ;
* vérifier titres, numérotation, cohérence visuelle ;
* préparer les exports PDF ou HTML.

Critère de validation :

Un document doit être lisible, stable, imprimable et exploitable sur écran.

### 4.9. Agent QA final

Responsabilités :

* exécuter tous les contrôles ;
* vérifier la complétude ;
* vérifier les liens ;
* vérifier l’absence de fichiers parasites ;
* vérifier les statuts ;
* refuser toute publication si un critère critique échoue.

Livrables :

* `qa_report.md`
* `publication_blockers.md`
* `release_notes.md`

### 4.10. Agent RAG

Responsabilités :

* maintenir `rag_connection.md`, `.env.rag.example` et `rag_config.example.yml` ;
* vérifier que `.env.rag` reste ignoré et qu’aucun secret n’est committé ;
* exécuter `scripts/rag_smoke_test.py` ou documenter explicitement son skip sans config ;
* préparer les plans d’ingestion et les contrôles de métadonnées ;
* exclure `/AUDIT`, `dist/`, `.git/`, `Documents_DRIVE/` et les données élèves du corpus RAG interne ;
* alimenter le juge de substance avec des candidats issus de `nsi_corpus` ;
* produire `rag_coherence_report.md` ;
* ne jamais valider pédagogiquement une ressource.

Critère de validation :

`nsi_corpus` est la seule collection autorisée pour juger les preuves internes du corpus.
`rag_education` peut servir d'inspiration ou de comparaison externe, jamais de preuve de
couverture interne.

### 4.11. Agent Juge de substance

Responsabilités :

* pour chaque capacité, décider si le contenu l’enseigne, l’entraîne et permet de se corriger, en citant une preuve **pertinente** (pas un objectif générique) ;
* séparation stricte juge / auteur : l’instance qui juge n’est jamais celle qui a rédigé ;
* verdict par défaut `needs_content` ;
* toute citation d’objectif templaté (« Identifier précisément la représentation ou la structure en jeu ») comme preuve est un motif de rejet du verdict ;
* les sections candidates sont idéalement fournies par le RAG interne (collection `nsi_corpus`), pas extraites mécaniquement (première section du fichier).

Livrables :

* `_substance_review.json` conforme au schéma, vérifié par le veto d’ancres ET par un contrôle de pertinence (recouvrement lexical minimal entre la citation et l’intitulé officiel, à défaut du juge LLM).

Critère de validation :

Une capacité est `validated_pedagogy` seulement si les trois preuves (cours, entraînement, correction) sont pertinentes et que le relecteur (humain ou LLM) le confirme. Une citation identique réutilisée sur plusieurs capacités ou plusieurs rôles invalide le verdict.
Une validation LLM seule ne vaut jamais revue humaine et ne peut pas promouvoir `covered`,
`published` ou `validated_*`.

## 5. Définition d’une séquence complète

Une séquence complète contient au minimum :

* `sequence.yaml`
* `cours_eleve.md`
* `trace_ecrite.md`
* `td.md`
* `tp.md`
* `fiche_methode.md`
* `aides_progressives.md`
* `corrige.md`
* `guide_professeur.md`
* `evaluation.md`
* `bareme.md`
* `grille_competences.md`
* `qcm.json`
* `projet_associe.md`
* `python/`
* `tests/`
* `sources.md`

## 6. Définition de publication

Une séquence est publiable seulement si :

* tous les documents existent ;
* les métadonnées sont complètes ;
* le contenu pédagogique est substantiel ;
* les capacités officielles sont explicitement associées ;
* les exercices sont progressifs ;
* les corrigés sont complets ;
* les tests Python passent ;
* aucun fichier parasite n’est indexé ;
* aucune donnée personnelle n’est présente ;
* le rapport QA ne contient aucun blocage critique.

## 7. Commandes minimales de contrôle

```bash
python -m scripts.check_metadata
python -m scripts.check_links
python -m scripts.check_program_coverage
python -m scripts.check_quality_gates
python -m scripts.check_no_placeholders
python -m scripts.check_no_private_data
python -m scripts.run_python_tests
python -m scripts.generate_index
```

## 8. Règle de blocage

Si une information manque, si une ressource n’est pas disponible, si une couverture ne peut pas être prouvée ou si un document est trop superficiel, il faut écrire explicitement :

```text
BLOCKER: validation impossible pour cette ressource.
Raison :
Action nécessaire :
```

Il est interdit de masquer une lacune par une formulation vague.

## 9. Standard fail-closed pour les gates et tests de policy

Tout gate ou test de policy DOIT échouer (fail-closed) si son evidence est
absente. Un test qui vérifie `X not in body` doit d'abord assert que `body`
est non vide. Un test qui vérifie la présence d'un gate dans un étage Makefile
doit échouer si l'étage lui-même est introuvable.

Exemples :
- `test_package_audit_target_exists` : échoue si la cible package-audit
  est absente du Makefile (pas de pass silencieux).
- `test_mypy_ratchet` : échoue si mypy n'a pas produit de sortie
  reconnaissable (sentinel "no issues found" ou erreurs).
- `check_makefile_audit_policy` : échoue si la cible audit ou audit-core
  est absente.
