# Chutes — smoke test de la preuve de build ordonnée

Date : 2026-08-02

Périmètre : Phase 0.1, contrat de croisement des marqueurs d'objets du journal
LaTeX avec les entrées réellement ouvertes du traceur `.fls`.

## Disponibilité

Le MCP Chutes a répondu à la liste des modèles et annoncé treize modèles
réellement disponibles. La consultation a été tentée avec le modèle listé
`unsloth/Mistral-Nemo-Instruct-2407-TEE`, à température `0`.

Le message ne contenait ni secret, ni donnée personnelle, ni contenu
éditorial. Il demandait uniquement une revue adversariale anonymisée des
invariants BEGIN/END, des chemins canoniques et de la double preuve journal/FLS.

## Résultat

L'appel a été refusé avant inférence avec un statut HTTP 402 pour quota de
compte épuisé. Aucun texte de modèle ni avis indépendant n'a été produit.

Les détails financiers et l'adresse contenus dans l'erreur brute ne sont pas
recopiés dans le dépôt.

## Disposition

Statut : `blocked_external_quota`.

Chutes restant consultatif, le lot est contrôlé exclusivement par les preuves
locales : tests RED/GREEN, mutations négatives des marqueurs, validation du
croisement avec le FLS, lint, typage et gates Phase 0. La consultation devra
être relancée lorsque le quota sera rétabli.
