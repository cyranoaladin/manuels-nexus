# Pedagogical Blockers Report

- Statut global : NON PUBLIABLE.
- Décision : ne pas générer de nouvelles séquences.

## Bloquants explicitement suivis

- **Séances théoriques** : seules les premières tranches P00-P02 et T00-T02 disposent de supports réels. `check_session_referenced_files_exist.py` mesure désormais les séances prêtes, les séances théoriques et refuse les références génériques ou abandonnées.
- **Registre v2** : `missing_documents_register_v2.md` remplace le registre volumineux comme source de suivi opérationnel. Un document cité doit exister ou apparaître explicitement comme blocage, sans blanchir une séance non prête.
- **Noms de fichiers doublés** : des noms comme `P00_P00_cours.md` ou `T01_T01_cours.md` sont des erreurs de génération. `check_document_naming_conventions.py` interdit les préfixes doublés, les casses incohérentes et les extensions non autorisées.
- **Séances encore génériques** : le retour a identifié une répétition massive de gabarits ; `check_session_specificity.py` interdit les formulations génériques et les déroulés trop répétés.
- **Semaines incohérentes** : le retour a identifié des semaines impossibles ; `check_session_week_calendar_consistency.py` impose semaines scolaires 1 à 38, semaines civiles et cohérence avec les mois.
- **Absence d'évaluation en Première** : corrigée dans les séances et contrôlée par `check_evaluation_distribution.py`, mais la qualité des évaluations reste à relire.
- **`qa_report.md` obsolète** : `generate_qa_report.py` et `check_qa_report_freshness.py` pilotent désormais les chiffres à partir du manifest et de la couverture.
- **Bug `source=drive`** : `scripts/ingest_drive_export.py` ne doit plus être classé comme Drive ; `check_manifest_source_integrity.py` contrôle cette règle.
- **Archive globale contenant `.git/`** : politique documentée dans `delivery_policy.md`; seule `dist/source_clean.tar.gz` est livrable comme archive pédagogique. `NSI.tar` contenant `.git/` est interdit comme livraison principale.
- **`make audit` non portable hors environnement Git** : `make audit-source` fonctionne sans `.git/` sur `source_clean.tar.gz` ; `make audit-local` (alias `make audit`) nécessite Git.
- **Documents professeurs encore `needs_review`** : ils sont plus structurés mais non relus pédagogiquement et scientifiquement.
- **Ressources Drive non intégrées localement** : `release-audit` reste bloquant.
- **Fiches de cours annuelles** : les fiches P00-P14 et T00-T19 existent dans `03_progressions/fiches_cours/`, mais restent `needs_review`. Elles sont maintenant distinguées en fiches opérationnelles ou liées par le champ `readiness`; les liens vers TD/TP/évaluations absents sont explicitement inscrits dans `missing_documents_register_v2.md`. Elles aident la révision et ne prouvent pas une couverture publiable sans cours, TD/TP, corrigé, évaluation, barème et revue humaine.

## Séquences trop denses

- Première S01 reste trop large : représentations de base, booléens, texte, types construits et tests. La progression la découpe en P01 à P07.
- Terminale S01 reste trop dense : interfaces, POO, piles/files/dictionnaires, graphes et BFS. La progression la découpe en T01 à T08.

## Capacités absentes

La couverture atomique contient encore des capacités `absent`; aucune capacité n'est `covered`.

## Risques de surcharge cognitive

- Ramadan impose de maintenir février et début mars sur activités guidées, remédiation ou pratiques courtes.
- Juin ne doit pas lancer de chapitre lourd ; les séances de juin sont synthèse, oral, pratique ou projet.

## Points à traiter avant publication

- Intégration locale et audit vie privée des ressources Drive.
- Relecture scientifique des définitions et exemples.
- Alignement exact entre chaque TD/TP/évaluation et son corrigé professeur.
- Exports élève sans corrigé et sans contenu professeur.
- Création ou import contrôlé des supports prioritaires listés dans `missing_documents_register_v2.md`.
- Relecture humaine des fiches de cours créées et alignement avec les supports complets de chaque séquence.
- Rendre chaque séance pédagogiquement spécifique avec activité exacte, exercice exact, document exact, trace exacte, erreur fréquente ciblée, modalité de correction, différenciation concrète et livrable vérifiable.
