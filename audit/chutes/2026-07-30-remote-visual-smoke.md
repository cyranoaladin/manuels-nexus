# Chutes — smoke test de reprise distante et visuelle

Date : 2026-07-30

Périmètre : validation distante de la Phase 0 et revue adversariale des huit
divergences visuelles.

## Disponibilité

La liste des modèles a répondu et annoncé 15 modèles réellement disponibles.
Deux consultations indépendantes ont ensuite été tentées :

1. audit du défaut de configuration GitHub Actions, avec l'annotation exacte et
   l'absence de jobs/artefacts ;
2. audit prépresse conservateur des preuves requises avant un verdict
   `expected_change`.

Modèles appelés :

- `Qwen/Qwen3.5-397B-A17B-TEE` ;
- `deepseek-ai/DeepSeek-V3.2-TEE`.

## Résultat

Les deux appels ont été refusés avant inférence avec un statut HTTP 402 pour
quota de compte épuisé. Aucun texte de modèle, avis indépendant ou décision
disciplinaire n'a été produit.

Les détails financiers et l'adresse contenus dans l'erreur brute ne sont pas
recopiés dans le dépôt. Aucun secret ni donnée personnelle n'a été transmis.

## Disposition

Statut : `blocked_external_quota`.

Chutes restant consultatif, la reprise s'appuie uniquement sur les preuves
locales : annotation GitHub, API Actions, hashes, métriques ImageMagick,
rerastérisation Poppler, inspection des planches, couche textuelle et
empreintes de polices. La décision humaine sur les baselines reste obligatoire.
