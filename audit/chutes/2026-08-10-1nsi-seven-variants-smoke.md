# Smoke test Chutes - sept variantes 1NSI

Date : 2026-08-10

Perimetre : revue finale de la generalisation de l'assembleur aux sept variantes
canoniques 1NSI, sans intervention sur TNSI.

## Smoke test

- Outil appele : `chutes_list_models`, limite 100.
- Resultat : echec avant inventaire des modeles, car l'interpreteur Python
  configure pour le serveur MCP Chutes est absent.
- Consequence : aucun modele n'est atteste disponible et aucune consultation
  distante n'a ete lancee.

## Disposition

Chutes reste consultatif. La validation repose sur les tests locaux, les builds
observes, les preflights PDF, les gates de collection et une revue independante
locale. Aucun gate n'a ete affaibli ou ignore pour compenser l'indisponibilite.
