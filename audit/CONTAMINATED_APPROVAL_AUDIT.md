# Provenance des approbations contaminees

Une qualification de defaut n'est pas une approbation : elle nomme l'objet sans jamais valider son contenu.

| classe | objets |
| --- | --- |
| `VALID_HUMAN_APPROVAL_BOUND_TO_CONTAMINATED_CONTENT` | 0 |
| `MACHINE_OR_BULK_APPROVAL` | 0 |
| `APPROVAL_WITHOUT_RECEIPT` | 0 |
| `UNKNOWN_APPROVAL_PROVENANCE` | 0 |

- `CONTAMINATED_APPROVED_OBJECTS` : `0`
- `APPROVALS_INVALIDATED_CURRENT` : `0`
- `CONTAMINATED_APPROVAL_REUSED_FOR_NEW_CONTENT` : `0`

Le statut anterieur est conserve et requalifie historical_invalidated_by_contamination ; aucune de ces approbations ne peut etre reutilisee pour le contenu qui remplacera l'objet.
