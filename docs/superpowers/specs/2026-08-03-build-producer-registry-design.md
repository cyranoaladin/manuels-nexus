# Registre des producteurs de builds observés — design

Date : 3 août 2026

Statut : approuvé pour implémentation par Alaeddine Ben Rhouma (`go`).

## Problème

L'inventaire publie actuellement :

```json
{
  "entrypoint": "python scripts/build_manifest.py --receipt <build-receipt.json>",
  "status": "not_integrated"
}
```

Ce statut est codé en dur. Il conserve à juste titre le bloqueur
`build_receipt_producteurs_non_intégrés`, mais il ne permet ni de définir
l'ensemble des producteurs requis ni de prouver leur raccordement au recorder.
Deux builds 1SPE sont pourtant observés et les assemblages statiques identifient
leur assembleur réel.

Le correctif doit remplacer cette sentinelle par une preuve dérivée, sans
présumer de l'existence d'assembleurs encore absents pour les autres manuels et
sans transformer un PDF observé en preuve de publication.

## Périmètre atomique

Le lot couvre uniquement les producteurs des assemblages de portée `manual`
effectivement déclarés par l'inventaire. Les assemblages manquants de 1NSI,
TNSI et TSPE restent des dettes séparées de `release-strict`; ils ne sont pas
inventés dans le registre.

Le lot ne modifie :

- aucun contenu pédagogique ou mathématique ;
- aucune règle élève/professeur ;
- aucun PDF par retouche ;
- aucune baseline visuelle ;
- aucune acceptation de release.

## Contrôle versionné

Créer `audit/BUILD_PRODUCERS.yaml`, validé par
`audit/schemas/v1/build-producers.schema.json` et enregistré sous le type
`build_producers` dans `SCHEMA_REGISTRY`.

Le contrôle suit les invariants des autres contrôles Phase 0 :

- `artifact_type`, `schema_version`, `schema_ref` et `control_digest` ;
- liste non vide et ordonnée de producteurs ;
- identifiant stable et unique ;
- chemin canonique, relatif au dépôt, vers un fichier régulier suivi par Git ;
- entrypoint canonique du recorder racine ;
- liste non vide et sans doublon d'`assembly_ids` ;
- aucune propriété libre ou statut déclaratif `integrated`.

Le premier producteur requis est l'assembleur réel 1SPE :

```yaml
producer_id: math-1spe-manual
assembler: Mathematiques/manuel-maths/scripts/assemble_manuel.py
recorder: scripts/build_manifest.py
assembly_ids:
  - math:manual:1SPE:eleve
  - math:manual:1SPE:professeur
```

## Calcul de l'intégration

L'inventaire charge le registre en mode fail-closed et calcule trois ensembles :

1. `required_assembly_ids` : tous les assemblages statiques de portée `manual` ;
2. `registered_assembly_ids` : leur couverture exacte par le registre ;
3. `observed_assembly_ids` : les couples manuel/variante réellement présents
   dans `audit/BUILD_MANIFEST.json`, résolus vers leurs `assembly_id`.

Un producteur est intégré seulement si :

- son assembleur correspond exactement à l'assembleur de chaque assemblage
  qu'il revendique ;
- son recorder est l'entrypoint racine autorisé ;
- toutes ses identités déclarées possèdent un build observé valide ;
- il ne revendique aucun assemblage inconnu ;
- aucun assemblage manuel requis n'est absent ou couvert deux fois.

`observed_build_integration` devient une structure dérivée contenant au moins :

- `status` : `integrated` ou `not_integrated` ;
- `required_producers` et `integrated_producers` ;
- `missing_assembly_ids`, `unobserved_assembly_ids` et
  `unexpected_assembly_ids` ;
- l'entrypoint du recorder.

Le bloqueur générique disparaît uniquement lorsque `status == integrated`.
Les bloqueurs précis `assemblage_déclaré_absent` et `build_observé_absent`
restent gouvernés par leurs contrôles actuels.

## Migration des preuves observées

Le nouveau contrôle participe au modèle statique. Son introduction change donc
les digests de l'inventaire et rend les deux observations 1SPE historiques
périmées. La migration est volontairement séquencée :

1. tests et code du registre ;
2. manifeste observé vidé et artefacts d'inventaire régénérés ;
3. commit de l'instrumentation ;
4. réattestation professeur puis élève depuis un SHA propre ;
5. régénération finale de l'inventaire.

À aucun moment un build périmé n'est accepté par tolérance. Les PDF ne sont
modifiés que par l'assembleur reproductible existant et restent soumis au
préflight, au recorder et à la comparaison octet-identique. Aucune référence
visuelle n'est mise à jour.

## Erreurs et comportement fail-closed

Le modèle doit refuser explicitement :

- registre ou schéma absent une fois le contrôle versionné introduit ;
- `control_digest` incohérent ;
- producteur, assembleur ou `assembly_id` dupliqué ;
- chemin absolu, traversée, symlink, fichier absent ou non suivi ;
- assembleur différent de celui dérivé statiquement ;
- recorder différent de `scripts/build_manifest.py` ;
- assemblage inconnu ou couverture incomplète ;
- build observé absent pour un producteur autrement déclaré intégré.

Une erreur de contrôle invalide le modèle ; une couverture incomplète valide
mais réelle maintient `status: not_integrated` et le bloqueur de release.

## Stratégie de tests

Le développement suit RED/GREEN :

- schéma enregistré et Draft 2020-12 valide ;
- chargement nominal du registre ;
- rejet de chaque mutation de chemin, digest, doublon et référence ;
- calcul `integrated` pour les deux assemblages 1SPE observés ;
- calcul `not_integrated` si une variante n'est pas observée ;
- rejet d'un assembleur discordant ;
- gate de release sans bloqueur générique seulement pour la preuve complète ;
- conservation de tous les autres bloqueurs et dimensions non couvertes ;
- `--check`, `--validate-model`, `--fail-on-new` et contrat CI ;
- suite complète et génération double ;
- contrôle explicite qu'aucun chemin de baseline visuelle n'a changé.

## Critère d'acceptation

Le lot est accepté lorsque le statut d'intégration n'est plus codé en dur, que
la preuve 1SPE est dérivée du registre, des assemblages et des builds observés,
et que `release-strict` reste rouge uniquement pour les dettes réelles
restantes. Cette réussite ne vaut ni validation scientifique, ni validation
éditoriale, ni autorisation de publication.
