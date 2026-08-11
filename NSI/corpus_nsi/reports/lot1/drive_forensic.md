# Lot 1 - Phase 1A - Forensique Drive

Date: 2026-06-28
Base: `05fa3c8e4dae5b92ec4dc8ca106290ec26887960`
Mode: lecture seule des roots et du registre existant.

## Accès réel disponible

| Élément | Chemin | Existe | Fichiers |
|---|---:|---:|---:|
| Drive source | `Documents_DRIVE` adjacent au dépôt | oui | 0 |
| Banque centralisée | `scrapping_NSI/ressources_nsi_centralisees` | oui | 15906 |
| Quarantaine doublons Drive | `scrapping_NSI/ressources_nsi_centralisees/_doublons_drive` | oui | 291 |
| Quarantaine skipped Drive | `scrapping_NSI/ressources_nsi_centralisees/_skipped_drive` | oui | 38 |
| Registre migration | `scrapping_NSI/migration_registry.json` | oui | n/a |

## Registre existant

Le registre existe, mais il ne permet pas de reconstruire la provenance du
Drive réel vidé.

Structure observée:

- clés haut niveau: `entries`, `source_cache`, `updated_at`, `version`
- `entries`: 16041 entrées
- `source_cache`: 4835 entrées
- destinations présentes: 15577
- destinations absentes: 464
- hashes uniques dans la banque centralisée: 15614

Répartition des sources dans `entries`:

| Source | Entrées |
|---|---:|
| `ressources_nsi_centralisees` | 15577 |
| `/tmp` | 463 |
| `Documents_DRIVE` | 1 |

L'unique entrée contenant `Documents_DRIVE` pointe vers un dossier temporaire de
test, pas vers le Drive réel:

```text
/tmp/tmpw_mu6n0c/Documents_DRIVE/Algo_Premiere/Cours drive.pdf
```

Elle ne constitue donc pas une preuve de relocalisation des fichiers du Drive
réel `Documents_DRIVE` adjacent au dépôt.

## Réconciliation demandée

| Contrôle | Résultat |
|---|---|
| Total fichiers source-avant traçables | non disponible |
| Manifest/hash avant-migration du Drive réel | absent |
| Fichiers encore présents dans le Drive réel | 0 |
| Fichiers destination après migration | 15906 |
| `_doublons_drive` attendu 291 | 291, intact en volumétrie |
| `_skipped_drive` attendu 38 | 38, intact en volumétrie |
| Orphelins Drive identifiables par hash | impossible à établir sans manifest avant-migration |
| Hash manquants Drive | impossible à établir sans manifest avant-migration |

## Conclusion

**BASE PROBANTE INSUFFISANTE**

Je ne peux pas conclure `RELOCALISATION`, car aucune source probante ne donne la
liste hash + chemin des fichiers présents dans le Drive réel avant la migration.
La présence de 291 fichiers dans `_doublons_drive` et de 38 fichiers dans
`_skipped_drive` est cohérente avec le rapport attendu, mais ne prouve pas à elle
seule que tous les fichiers Drive ont été relocalisés.

Je ne peux pas conclure `PERTE RÉELLE` non plus, faute de manifest source-avant
permettant d'identifier des hashes attendus et absents.

## Données nécessaires pour conclure

Pour établir `RELOCALISATION` ou `PERTE RÉELLE`, il faut au moins un des éléments
suivants:

- snapshot pré-migration du Drive réel avec `chemin_source_original` et
  `hash_sha256`;
- sauvegarde du dossier `Documents_DRIVE` avant migration;
- registre de migration antérieur contenant les chemins réels portables
  `Documents_DRIVE/...` ou la valeur de `NSI_DOCUMENTS_DRIVE_ROOT`;
- logs d'exécution complets de l'organiseur indiquant chaque déplacement Drive,
  avec chemins portables ou variables d'environnement.

Conformément à la consigne, aucune Phase 1B / 2 / 3 ne doit être ouverte sans
arbitrage humain.
