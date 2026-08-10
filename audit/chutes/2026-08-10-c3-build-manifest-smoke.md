# Smoke test Chutes - C3 et BUILD_MANIFEST

Date : 2026-08-10

Perimetre : correction du P0 C3 1NSI et migration de la gouvernance
`BUILD_MANIFEST`, sans intervention sur TNSI.

## Smoke test

- L'inventaire Chutes a retourne 13 modeles disponibles.
- Une completion minimale a ete demandee a `Qwen/Qwen3-32B-TEE` sans contenu
  du depot, secret ni donnee personnelle.
- La completion a echoue avant generation avec HTTP 402, quota epuise.
- Aucune expertise Chutes n'a donc ete produite ni utilisee.

## Disposition

Chutes reste consultatif. Les revues disciplinaires et de gouvernance sont
confiees a des agents independants locaux, puis verifiees par les tests et les
gates du depot. Aucun gate n'est affaibli, ignore ou transforme en succes pour
compenser cette indisponibilite.
