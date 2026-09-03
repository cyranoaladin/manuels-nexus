# Décision humaine — invalidation du liage de build périmé (1SPE)

<a id="decision-1spe-build-manifest-invalidation-2026-09-03"></a>

- **Date** : 2026-09-03
- **Décision** : `INVALIDATE_STALE_BUILD_BINDING`
- **Autorisation** : `HUMAN_OPERATOR_EXPLICIT_GOVERNANCE_AUTHORIZATION`
- **Portée** : `PROVENANCE_AND_BUILD_BINDING_ONLY`

## Raison, telle que l'opérateur l'a formulée

> The observed 1SPE build receipts for the 363-page student candidate and 635-page teacher candidate are superseded and no longer describe the current source tree after ratified publication-critical layout/runtime corrections. Invalidate only the stale build binding so that new observed builds can be recorded against the current sources. This decision grants no content, human-review, D7, publication, or print approval.

## Ce que cette décision n'accorde pas

Cette décision ne vaut ni approbation de contenu, ni revue humaine, ni D7, ni publication, ni bon à tirer.

| Approbation | Accordée |
|---|---|
| `content_approval` | **non** |
| `human_review_approval` | **non** |
| `d7_approval` | **non** |
| `publication_approval` | **non** |
| `print_approval` | **non** |
| `isbn_authorized` | **non** |

## Pourquoi la machine ne pouvait pas trancher

`build_manifest.py --invalidate-stale` exige une justification et un approbateur humains, refuse en CI et n'accepte qu'un dépôt propre : écarter une attestation déjà portée au manifeste est une décision, pas un calcul.

## Constructions observées, désormais historiques

| Variante | Pages | SHA source | Empreinte du PDF | Disposition |
|---|---:|---|---|---|
| eleve | 363 | `60e7f5a8d185` | `11c74f79f1ce` | `SUPERSEDED_HISTORICAL` |
| professeur | 635 | `54ec678e0e64` | `cb166e3a51ba` | `SUPERSEDED_HISTORICAL` |

## Ce qui n'est pas fait

Le source_digest de l'ancien reçu n'est pas modifié pour coller au HEAD courant, et l'ancien PDF n'est pas requalifié comme courant. L'ancienne construction est invalidée ; une nouvelle est observée sur les sources courantes.

Le manifeste antérieur n'est ni réécrit ni supprimé : il reste atteignable au commit qui précède l'invalidation, et ce commit est nommé ici. Aucun champ n'est édité à la main.

