# Chutes — smoke test et consultations Phase 0.1

Date : 2026-07-29

Périmètre : reprise Phase 0.1, voie `inventory/CI`

## Disponibilité

Le MCP Chutes répond à la liste des modèles. Quinze modèles ont été annoncés,
dont le modèle de contrôle demandé :

`unsloth/Mistral-Nemo-Instruct-2407-TEE`

La lecture des alias a échoué sur le magasin local d'identifiants, sans effet
sur l'identification directe du modèle.

## Smoke test imposé

Paramètres transmis :

- modèle : `unsloth/Mistral-Nemo-Instruct-2407-TEE`
- température : `0`
- maximum : `64` tokens
- message utilisateur exact :
  `Réponds exactement par CHUTES_MCP_OK, sans aucun autre texte.`

Résultat : **échec HTTP 402** avant génération, pour quota de compte dépassé.
Le service n'a renvoyé aucun texte de modèle.

Les détails financiers et l'adresse de paiement contenus dans l'erreur brute ne
sont pas recopiés dans le dépôt.

## Consultations A et B

Les consultations suivantes étaient prévues :

1. architecture Python et régressions, limitée au diff WIP, aux tests en échec
   et au contrat Phase 0.1 ;
2. audit adversarial du cadre de qualité, limité à `AGENTS.md`, à la structure
   du cahier des charges et aux gates.

Elles n'ont pas été envoyées après l'échec du smoke test : le quota est appliqué
au compte avant toute inférence, donc changer de modèle ne peut pas produire un
avis indépendant. Aucun secret ni donnée personnelle n'a été transmis.

## Disposition

Statut : `blocked_external_quota`.

Chutes restant consultatif, la mission continue avec reproduction locale,
tests, revue adversariale et preuves machine. Les deux consultations devront
être relancées lorsque le quota Chutes sera rétabli ; aucune approbation
disciplinaire critique ne pourra s'appuyer sur cette tentative.
