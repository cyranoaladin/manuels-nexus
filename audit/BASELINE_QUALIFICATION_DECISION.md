# Décision humaine — qualification de la baseline Phase 0

<a id="decision-baseline-debt-regression-control-2026-07-30"></a>

## Décision approuvée

| Champ | Valeur |
|---|---|
| Identifiant | `baseline-debt-regression-control-2026-07-30` |
| Date | 30 juillet 2026 |
| `baseline_purpose` | `debt_regression_control` |
| `release_acceptance` | `false` |
| `provisional` demandé après gel | `false` |
| Représentation | une disposition individuelle par fingerprint |
| Approbateur | Alaeddine Ben Rhouma |
| Rôle | Direction scientifique et éditoriale Nexus Réussite |

Cette approbation autorise uniquement le gel d’un état de dette comme référence
de non-régression. Elle ne constitue ni une autorisation de publication ou de
release, ni une validation mathématique, visuelle ou réglementaire.

Référence durable de la décision :

`audit/BASELINE_QUALIFICATION_DECISION.md#decision-baseline-debt-regression-control-2026-07-30`

## État approuvé

| Élément | Valeur |
|---|---|
| HEAD observé | `27082043c45fc405299e335f6eb7475f01288e27` |
| Branche | `finalisation/collection-v1` |
| `source_digest` | `sha256:13f39224d54e05eead87e36d08ccf660e4925902ab30381a5104a4256622da8a` |
| `model_digest` | `sha256:be9f9565253225a3ba194b1b81039f847067a809066fd72124263876b04a0e60` |
| Fingerprints actifs | 2 461 |
| Déjà qualifiés par preuve versionnée | 4 |
| Lot à qualifier | 2 457 |
| `baseline_ready` | 9 contrôles verts sur 10 |
| Seul contrôle rouge | `disposition_coverage` |
| `--fail-on-new` | code 5, baseline provisoire |
| `--release-strict` | code 7, 69 raisons déterministes |

L’identité approuvée du lot est le SHA-256 du tableau JSON minifié, encodé en
UTF-8, des 2 457 fingerprints non qualifiés triés :

`sha256:ee6220cca262a6d5f331e7e86c514960c859f3b452c46ce24ac714ad521f13e8`

Le nombre, cette empreinte et les digests du modèle doivent être recalculés et
rester identiques avant toute matérialisation. Toute variation doit produire un
nouveau rapport explicatif avant le gel.

## Propriétaires autorisés

```yaml
owners:
  direction_scientifique_programme:
    scope:
      - mathematics
      - official_programme
      - demonstrations
      - qcm
      - corrections
      - numerical_results
  direction_editoriale_pedagogique:
    scope:
      - pedagogy
      - nexus_mastery_loop
      - student_teacher_variants
      - remediation
      - editorial_content
      - terminology
  ingenierie_build_qualite:
    scope:
      - metadata
      - inventory
      - assemblies
      - latex
      - python
      - ci
      - pdf
      - visual_baselines
```

## Contrat de non-régression

La baseline définitive doit :

- enregistrer chaque fingerprint individuel ;
- interdire toute anomalie nouvelle ou augmentation d’occurrences ;
- interdire la réapparition d’une anomalie `fixed` ;
- interdire l’aggravation de sévérité ;
- détecter une substitution à total constant ;
- signaler une disparition comme amélioration sans faire échouer le gate ;
- conserver les fingerprints résolus dans l’historique.

Une baseline connue ne rend jamais une dette acceptable pour une release.
`--fail-on-new` contrôle les régressions ; `--release-strict` demeure
l’autorité de publication.

## Dispositions autorisées

Les seules valeurs autorisées sont :

- `open_debt` ;
- `generated_dependency` ;
- `harvest_candidate` ;
- `intentional_reuse` ;
- `false_positive` ;
- `accepted_exception` ;
- `fixed`.

Contraintes :

- `false_positive` exige une reproduction et une preuve ;
- `accepted_exception` est interdite dans la politique initiale et nécessite
  une nouvelle décision humaine explicite ;
- `fixed` exige un test de régression ;
- `intentional_reuse` exige une preuve éditoriale et l’identification de la
  variante ;
- une anomalie inconnue reste bloquante et non qualifiée ;
- aucune disposition ne supprime l’anomalie brute.

## Politique de qualification approuvée

La politique est versionnée dans
`audit/BASELINE_QUALIFICATION_POLICY.yaml`. Elle matérialise une entrée
individuelle dans `audit/ANOMALY_DISPOSITIONS.yaml` et ne modifie jamais les
anomalies brutes.

Règles initiales :

1. Les statuts `generated`, `draft`, `needs_review`, `needs_math_review`,
   `needs_program_review`, `needs_editorial_review` et
   `needs_visual_review` restent `open_debt`. Les trois contrats actuellement
   marqués `complete`, mais non `approved`, restent également `open_debt` sous
   la responsabilité `ingenierie_build_qualite`; cette règle stricte ne
   reconnaît pas `complete` comme publiable.
2. Le propriétaire d’un contenu mathématique, QCM, résultat numérique ou
   corrigé est `direction_scientifique_programme`.
3. Le propriétaire d’un objet pédagogique, d’une remédiation ou d’une variante
   élève/professeur est `direction_editoriale_pedagogique`.
4. Le propriétaire d’un contrat, d’une métadonnée, d’un assemblage, d’un
   artefact, d’un PDF ou d’une référence technique est
   `ingenierie_build_qualite`.
5. Un chapitre ou livrable manquant est `open_debt`, propriétaire
   `direction_editoriale_pedagogique`; si seul l’assembleur manque, le
   propriétaire est `ingenierie_build_qualite`.
6. Une correction absente est `open_debt`, propriétaire
   `direction_scientifique_programme`.
7. Une référence META ou LaTeX réellement cassée est `open_debt`,
   propriétaire `ingenierie_build_qualite`.
8. Un `_harvest/**/*.candidate.tex` est `harvest_candidate`, propriétaire
   `direction_editoriale_pedagogique`, `release_blocking: false`, mais demeure
   contrôlé séparément et non publiable.
9. Une dépendance générée n’est `generated_dependency` que si son producteur
   est identifié et testé. Sinon elle reste `open_debt`.
10. Une répétition n’est `intentional_reuse` qu’avec preuve éditoriale,
    absence de doublon involontaire dans le PDF et variante identifiée. Sinon
    elle reste `open_debt`.

Tout fingerprint ne correspondant à aucune règle doit être écrit dans
`audit/UNQUALIFIED_ANOMALIES.json` et
`audit/UNQUALIFIED_ANOMALIES.md`. Tant que ce registre n’est pas vide,
`baseline_ready` et le gel doivent échouer.

## Ordre d’exécution obligatoire

1. Recalculer le nombre et l’empreinte du jeu encore non qualifié, puis les
   comparer à la présente décision avant toute écriture.
2. Matérialiser exactement ce jeu par règles déterministes.
3. Prouver que les fingerprints dispositionnés sont exactement ceux du jeu
   approuvé, sans doublon ni fingerprint inconnu.
4. Vérifier les propriétaires, dispositions, preuves conditionnelles et
   anomalies non qualifiées.
5. Tester et committer la politique et les dispositions sans appeler
   `--update-baseline`.
6. Depuis un worktree propre, exécuter les dix préconditions et produire
   `audit/BASELINE_FREEZE_REPORT.md`.
7. Appeler explicitement `--update-baseline` avec la raison et l’approbateur
   ci-dessous.
8. Démontrer `--validate-model = 0`, `--fail-on-new = 0` et
   `--release-strict = 7`.

Raison du gel :

> État initial qualifié de la dette existante après stabilisation de la Phase
> 0, utilisé exclusivement pour détecter les régressions et les nouvelles
> anomalies.

Approbateur du gel : `Alaeddine Ben Rhouma`.

La CI ne met jamais à jour la baseline. La baseline visuelle reste un processus
distinct et aucune empreinte visuelle n’est approuvée par la présente décision.
