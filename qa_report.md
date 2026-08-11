# QA Report

## Résumé

- Statut global : NON PUBLIABLE
- Ressources inventoriées : 615
- Ressources needs_review : 615
- Ressources publiables : 0
- Source generated : 607
- Source adapted_from_drive : 7
- Source import_partiel : 1
- Source inspiration_drive : 0
- Source drive : 0
- Lignes drive_inventory.csv : 22
- Couverture covered : 0
- Couverture needs_review : 111
- Couverture partial : 3
- Couverture absent : 0
- Archive pédagogique à transmettre : dist/source_clean.tar.gz
- Archive globale contenant .git : interdite comme livraison principale
- L’archive principale de livraison est dist/source_clean.tar.gz. Toute archive contenant .git/ est interdite comme livraison pédagogique.
- make audit : PASS prototype uniquement si exécuté après génération de ce rapport
- QUALITY_GATES_PASS : qualité interne contrôlée par scripts/check_quality_gates.py.
- PACKAGE_AUDIT_PASS : paquet source propre attendu via make package-audit.
- EXTRACTED_SOURCE_AUDIT_PASS : audit source extrait attendu sans dépendance Git.
- RELEASE_AUDIT_STATUS : RELEASE_AUDIT_FAIL
- FINAL_STATUS = NON_RELEASE_READY
- Raison : Drive partiellement intégré ; publication bloquée par ressources restantes non auditées / absentes / sensibles.
- Drive est partiellement intégré.
- L’audit portable ne vérifie pas les fichiers bruts Drive.
- L’audit local vérifie les fichiers bruts Drive lorsque le miroir Documents_DRIVE est présent.
- Le dépôt reste NON_RELEASE_READY.
- Audit externe /AUDIT : absent en mode portable
- Arbre canonique de production : 03_progressions/supports/.
- Arbres premiere/sequences/ et terminale/sequences/ : pilotes de référence, pas canon de production.
- Drive integrated_adapted : 6
- Drive inspiration_only : 1
- Drive rejected_sensitive : 5
- Drive missing_local_copy : 7
- Drive deferred : 3
- Drive quarantined : 0
- Plan Drive restant : 15/15 ressources non soldées documentées.
- Décision : ne pas générer de nouvelles séquences
- Lots Drive planifiés : P05 traitement_tables complet ; T01 TAD complet ; T18 Boyer-Moore complet ; P12 tri/complexité ; P13 glouton.
- ZIP exploitable sans `.git` : dist/nsi-enseignement_source_clean.zip, archive séparée du livrable pédagogique de référence.

## Commandes de référence

```bash
make audit
make package-audit
make --no-print-directory release-audit
```

## Dernier blocage release observé

```text
Le vrai make release-audit est exécuté séparément.
python -m scripts.check_drive_mapping_release
- rendus_eleves: rejected_sensitive - Dossier de rendus élèves interdit en livraison pédagogique.
- .git: rejected_sensitive - Dossier Git Drive interdit en ressource pédagogique.
- .venv: rejected_sensitive - Environnement virtuel interdit en ressource pédagogique.
- TP_SOC.tex: missing_local_copy - Fichier TP_SOC.tex absent ; dossier SoC alternatif repéré mais non repris dans ce lot.
- Séquence1_Histoire de l'informatique: missing_local_copy - Dossier exact absent du miroir local ; pas de contenu inventé.
- NotesEleves.csv: rejected_sensitive - Nom et contenu suggèrent des notes élèves ; ressource exclue.
- Fichier_Eleves.csv: rejected_sensitive - Nom suggère fichier élèves ; ressource exclue.
- Séquence6_Arbres binaires: deferred - Dossier local trouvé ; audit différé pour éviter intégration partielle non relue.
```

## Bloquants restants

- Drive partiellement intégré : voir `reports/drive_enrichment_report.md` et `drive_inventory.csv` pour les décisions par ressource.
- Ressources Drive absentes localement : 7.
- Ressources Drive différées : 3.
- Ressources Drive rejetées sensibles : 5.
- Toutes les ressources restent en revue ou non publiables.
- Aucune capacité n'est covered.
- Documents professeurs encore en needs_review.
- Revue pédagogique et scientifique humaine absente.
- Séances opérationnelles ou reliées : 222.
- Séances théoriques ou non reliées : 0.

## Politique /AUDIT

- Dossier /AUDIT : absent en mode portable.
- Usage : documentation d'audit externe et stratégique.
- Exclusion : non compté comme corpus pédagogique, non compté dans `manifest.csv`, non utilisé comme preuve dans `coverage.md`.
- Intégration : les prototypes repris sont adaptés dans `scripts/`, testés et versionnés.

## Arbre canonique

- Canon de production : `03_progressions/supports/`.
- Fiches : `03_progressions/fiches_cours/`.
- Pilotes de référence : `premiere/sequences/` et `terminale/sequences/`.
- Politique : `content_tree_policy.md`.

## Fiches de cours

- Les fiches de cours sont des ressources d’aide et de révision. Elles ne prouvent aucune couverture publiable.
- Une capacité ne peut être covered que si existent et sont relus : cours ou fiche, séance, TD ou TP, corrigé, évaluation, barème, remédiation, revue pédagogique humaine et revue scientifique humaine.
- Fiches attendues : 35 séquences avec au moins une fiche.
- Fiches créées : 44
- Séquences sans fiche : 0
- Capacités sans fiche : 0
- Fiches théoriques : 0
- Fiches liées : 0
- Fiches opérationnelles : 44
- Liens vers supports existants : 113
- Liens vers supports inscrits au registre : 0
- Statut : needs_review
- Effet couverture : aucun ; les fiches ne rendent aucune capacité covered.

## Couverture programme réconciliée

- `coverage.md` indexe désormais les preuves issues de `03_progressions/supports/**`.
- `coverage_sources.md` liste les fichiers sources par capacité.
- Couverture covered : 0
- Couverture needs_review : 111
- Couverture partial : 3
- Couverture absent : 0
- Décision : les preuves documentaires issues de `supports/` rendent visibles les capacités, mais ne créent aucune validation humaine.

## Juge de substance

- Verdicts pilotes vérifiés : 0
- Unités pilotes : P05, P06, T06, T07, T08, T10, T17, T18.
- Schéma : `substance_verdict.schema.json`.
- Index : `substance_reviews_index.md`.
- Verdict adverse : `substance_reviews/_adversarial/poisoned.verdict.json` doit être refusé.
- Verdict par défaut : `needs_content`; aucune ressource n'est promue par ce juge.

## Politique des gates

- Politique : `qa_gate_policy.md`.
- Noyau bloquant : structure, privacy, tests, substance.
- Les contrôles de comptage et de longueur restent indicatifs ou legacy.
- Le seul gate pédagogique bloquant est le garde-fou de substance vérifiable par ancres.

## Rendu charté pilote

- Cible : `make render-unit U=P05` puis `make render-unit U=T10`.
- Contrôle : `scripts/check_rendered_unit_artifacts.py --unit P05` et `--unit T10`.
- Versions élève : corrigés/barèmes filtrés.
- Versions prof : corrigés/barèmes présents.

## Échelle capacités officielles

- Capacités documented : 114
- Capacités practiced : 114
- Capacités assessed : 114
- Capacités linked_to_session : 114
- Capacités reviewed_pedagogy : 0
- Capacités reviewed_science : 0
- Capacités covered : 0
- Décision : documented/practiced/assessed ne valent pas validation humaine.

## TP papier / exécutables

- TP papier : 7
- TP exécutables : 39
- Ratio papier : 15.2%
- Opportunités de conversion exécutable signalées : 7
- Seuil strict opportunités restantes : 8
- État seuil strict : PASS
- Registre : `tp_executable_opportunity_register.md`.
- Les TP papier restent `needs_review` et ne remplacent pas une revue humaine.

## Séances opérationnelles / théoriques

- Séances opérationnelles ou reliées : 222
- Séances théoriques ou non reliées : 0
- Séances linked : 222
- Séances classroom_ready : 222
- Séances human_review_pending : 222
- Séances validated : 0
- `classroom_ready` signifie exploitable documentairement ; la revue humaine reste pending.
- Les séances théoriques restantes doivent être reliées explicitement aux supports produits avant publication.

## Cohérence pédagogique par séquence

- Séquences vérifiées : 35
- Erreurs de cohérence détectées : 0

## Revue humaine

- Ressources majeures à relire : 533
- Lignes dans `human_review_register.csv` : 533
- Ressources prioritaires vague 1 : 20
- Priorités vague 1 couvertes : P05, P06, P10, P12, P13, T06, T07, T08, T10, T17, T18
- Statut initial : pending pour science, pédagogie, accessibilité et technique.
- Aucune ligne du registre ne promeut `validated_*`, `published` ou `covered`.

## Fiches liées non opérationnelles

| Fiche | Support absent | Registre associé | Date cible | Impact pédagogique | Action suivante |
|---|---|---|---|---|---|
| Aucune fiche liée non opérationnelle. | - | - | - | - | - |

## Gates indicatifs encore en échec

| Fichier concerné | Erreur | Décision | Date cible de correction |
|---|---|---|---|
| Aucun échec indicatif observé pendant cette génération. | - | - | - |

Les dettes indicatives ouvertes sont aussi suivies dans `qa_debt_register.md` avec cause, risque, impact, responsable et critère de fermeture.

## Décisions

- Statut publication : NON.
- Statut covered : 0.
- Statut published : 0.
- Statut validated_* : 0.
- Archive pédagogique : dist/source_clean.tar.gz.
- Archive globale contenant .git : interdite comme livraison principale.
