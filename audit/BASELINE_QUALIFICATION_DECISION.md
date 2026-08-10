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

---

<a id="decision-baseline-debt-extension-origin-main-2026-08-02"></a>

## Extension approuvée après fusion de `origin/main`

| Champ | Valeur |
|---|---|
| Identifiant | `baseline-debt-extension-origin-main-2026-08-02` |
| Date | 2 août 2026 |
| Branche | `finalisation/collection-v1` |
| HEAD observé | `fb90e5c7cabb16c29c61bf4bdc1d5abae3f0121a` |
| `baseline_purpose` | `debt_regression_control` |
| `release_acceptance` | `false` |
| Approbateur | Alaeddine Ben Rhouma |
| Rôle | Direction scientifique et éditoriale Nexus Réussite |

L’approbateur autorise l’extension de la baseline Phase 0 aux 186 fingerprints
importés par la fusion de `origin/main`, exclusivement comme dette ouverte. Le
lot approuvé est identifié par :

- empreinte : `sha256:ac046f9784e3a492dbcb83dca74292ff0b503a19b52d09ebef51e5e94a299fe8` ;
- `blocking_statuses` : 134 ;
- `unassembled_objects` : 52 ;
- `direction_scientifique_programme` : 109 ;
- `direction_editoriale_pedagogique` : 25 ;
- `ingenierie_build_qualite` : 52.

Les 186 dispositions sont `open_debt` et restent bloquantes pour la release.
Cette décision n’approuve aucun contenu scientifique, éditorial, pédagogique,
visuel ou réglementaire. Elle autorise uniquement la matérialisation, la mise à
jour de la baseline de non-régression, les commits et le push sur
`finalisation/collection-v1`. Le manuel demeure **NO-GO publication**.

Digests observés avant matérialisation :

- source : `sha256:f2b46f25776ce98e2a52a422581532911045d861613ab652625a08b838d07545` ;
- modèle : `sha256:606142c55324affad412521536f294a913c4ba45d0d0e10e7fb785238cba58aa`.

---

<a id="decision-baseline-debt-extension-collection-2026-08-08"></a>

## Extension et réconciliation approuvées pour la collection

| Champ | Valeur |
|---|---|
| Identifiant | `baseline-debt-extension-collection-2026-08-08` |
| Date | 8 août 2026 |
| Branche | `finalisation/collection-v1` |
| HEAD observé | `a48e8e41fc3f6ef9274e564722d5155c8df401b7` |
| `baseline_purpose` | `debt_regression_control` |
| `release_acceptance` | `false` |
| Approbateur | Alaeddine Ben Rhouma |
| Rôle | Direction scientifique et éditoriale Nexus Réussite |

L’approbateur autorise exclusivement l’enregistrement des 981 fingerprints du
lot observé comme `open_debt`, tous bloquants pour la release. Le lot est
verrouillé par l’empreinte
`sha256:e2ec8130f85f690eda663ac556b61e63ffd7d98e422c71f0245b10112161887f`
et par les ventilations suivantes :

- `blocking_statuses` : 875 ;
- `unassembled_objects` : 82 ;
- `chapters_not_in_manual` : 15 ;
- `broken_meta_references` : 2 ;
- `unclassified_types` : 7 ;
- `direction_scientifique_programme` : 752 ;
- `direction_editoriale_pedagogique` : 98 ;
- `ingenierie_build_qualite` : 131.

L’approbateur autorise également la réconciliation exacte de la baseline
initiale d’empreinte
`sha256:714c859e7a56e8034e16b3d5c6beeee350848594351076ac256764c180e2e9ff` :
2 005 fingerprints actifs sont conservés sans modification et 642 anciens
fingerprints sont archivés dans `resolved`, pour un état final de 2 986 actifs.
Le jeu résolu est verrouillé par l’empreinte
`sha256:44397de4c98d70ce3575c04ea37322a403a29a3468bd29a23bffc938ed4908fc`.
Il inclut uniquement les trois remplacements appariés suivants :

- `9873ab6a1e11c673` vers `3276d95a8a9b8142` ;
- `63548ddb4dd6b1dd` vers `d51832bdeebf5d4a` ;
- `8fdec12020b7159b` vers `a96d99c614321acc`.

Cette autorisation sert uniquement au contrôle de non-régression de la dette.
Elle n’approuve aucun contenu scientifique, réglementaire, pédagogique,
éditorial ou visuel, ne lève aucun P0 et n’autorise aucune publication. Les 981
anomalies restent comptées par `--release-strict`, `release_acceptance` reste
`false` et le manuel de Mathématiques Première spécialité demeure **NO-GO
publication**.

Digests observés avant matérialisation :

- source : `sha256:590c51801b32a6661878de7956d1752b9f027bf2cd65ba2605e8120b682d91d3` ;
- modèle : `sha256:8db8abe9a2882c827f4aee55f7584f082f1ea7f31647783e7f52697443055d22`.

---

<a id="decision-baseline-status-governance-1nsi-2026-08-10"></a>

## Réconciliation approuvée après gouvernance des statuts 1NSI

| Champ | Valeur |
|---|---|
| Identifiant | `baseline-status-governance-1nsi-2026-08-10` |
| Date | 10 août 2026 |
| Branche | `finalisation/collection-v1` |
| HEAD observé | `afae475ee06e8510804c0065ccfd35dfa0199875` |
| `baseline_purpose` | `debt_regression_control` |
| `release_acceptance` | `false` |
| Approbateur | Alaeddine Ben Rhouma |
| Rôle | Direction scientifique et éditoriale Nexus Réussite |

L’instruction humaine « traiter séparément la gouvernance des 349 statuts »
autorise exclusivement la réconciliation mécanique des empreintes modifiées par
les 189 transitions de statut 1NSI déjà auditées. Les 189 nouvelles empreintes
restent `open_debt`, bloquantes pour la release, et sont verrouillées par
`sha256:6a994806a4a3b8c710fb0eb2e089e90e8666543b3380e4ccf0cf5268500f86ca` :

- `blocking_statuses` : 189 ;
- `direction_scientifique_programme` : 179 ;
- `direction_editoriale_pedagogique` : 10.

La transition exacte part d’une baseline de 2 986 empreintes actives et 642
empreintes résolues, d’empreinte
`sha256:ebe9580cae8f994a19bb82960762a845c19e2c9a6e006aae244dcebc26ca3bbb`.
Elle conserve 2 677 empreintes inchangées, remplace 189 empreintes de statut et
archive 309 anciennes empreintes dans `resolved`, pour un état final de 2 866
empreintes actives et 951 résolues. Le jeu résolu est verrouillé par
`sha256:b652287acfa1d91c62446b1dc3f251b46980ca6363968a14733b3e2e91bf3631` :

- 189 anciennes empreintes `blocking_statuses`, appariées aux 189 nouvelles ;
- 109 `unassembled_objects`, désormais intégrés aux variantes canoniques 1NSI ;
- 10 `chapters_not_in_manual`, désormais intégrés au manuel 1NSI ;
- 1 `missing_assemblers`, l’assembleur 1NSI étant désormais présent.

Les 189 paires sont listées intégralement dans la politique et verrouillées par
`sha256:b744f797cb072e7c1200b5e8c87a2ef7b16076578e53e1e70e15b764988ea3e0`.
Cette décision ne modifie aucune source TNSI, n’approuve aucun contenu
scientifique, réglementaire, pédagogique, éditorial ou visuel, ne lève aucun P0
et n’autorise aucune publication. Les 349 statuts 1NSI restent bloquants,
`release_acceptance` reste `false` et la collection demeure **NO-GO
publication**.

Digests observés avant matérialisation :

- source : `sha256:8fda81f750904276cff25878f84fb196ac3f1b26c30c62ec054f2f09ab691b81` ;
- modèle : `sha256:f273dd51de99b09c8ef3846c2974556ed9ce11a8cc5e8cc8cfb0820d42e51548`.
