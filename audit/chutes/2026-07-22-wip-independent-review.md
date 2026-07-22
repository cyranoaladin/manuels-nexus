# Revue Chutes indépendante du WIP — 2026-07-22

## Paramètres

- Outil : `mcp__chutes__chutes_chat_complete`
- Modèle : `unsloth/Mistral-Nemo-Instruct-2407-TEE`
- Température : `0`
- Maximum de tokens : `4096`
- Données transmises : extraits techniques minimaux et résumé anonymisé des
  tests ; aucun secret, token, fichier `.env` ou donnée personnelle.

## Conclusions de la revue

Chutes identifie l'absence de `SOURCE_ROLES.yaml` et le traitement incomplet de
la valeur par défaut comme cause probable des inventaires vides. La revue
anticipe ensuite les incompatibilités des renderers et l'absence des gates CLI.
Elle recommande de vérifier la classification en premier, de relancer les tests,
puis de contrôler les fonctions secondaires.

## Vérification locale

Le diagnostic local confirme que `_collect_role_patterns()` retourne :

```text
patterns= {}
default= transversal
order= []
```

Le test direct du pipeline de rendu confirme aussi :

```text
TypeError: _render_inventory_markdown() got an unexpected keyword argument 'marker'
```

## Recommandations retenues

- traiter la classification comme premier correctif ;
- exécuter d'abord un test de régression minimal ;
- relancer ensuite les 73 tests pour révéler les défauts masqués ;
- traiter les renderers et la CLI seulement après le retour historique au vert.

## Recommandation rejetée

La proposition d'ajouter `SOURCE_ROLES.yaml` aux dépôts temporaires des tests est
rejetée. Le générateur public fonctionnait sans ce fichier au HEAD de référence ;
les fixtures ne doivent pas masquer une régression du fallback. Le correctif
sera apporté à `_collect_role_patterns()` et couvert par un nouveau test.
