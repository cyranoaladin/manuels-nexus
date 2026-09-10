# Couverture programme — tableau de bord

Fichier genere par `scripts/build_programme_dashboard.py`.
Ne pas editer : chaque valeur est relue dans l'artefact qui la produit.

| Compteur | Valeur | Artefact |
|---|---|---|
| `CANONICAL_OFFICIAL_ITEMS_APPLICABLE` | 932 | `audit/OFFICIAL_PROGRAMME_INVENTORY.json` :: official_items_applicable |
| `CANONICAL_OFFICIAL_ITEMS_MANDATORY` | 694 | `audit/OFFICIAL_PROGRAMME_INVENTORY.json` :: official_items_mandatory |
| `OFFICIAL_REFERENCES_VERIFIED` | 6/6 | `audit/OFFICIAL_PROGRAMME_INVENTORY.json` :: OFFICIAL_REFERENCES_VERIFIED |
| `INTERNAL_ATOMS` | 313 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / internal_atoms |
| `INTERNAL_ATOMS_CONFIRMED_PARENT` | 159 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / bound_confirmed |
| `INTERNAL_ATOMS_PROPOSED` | 139 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / bound_proposed |
| `INTERNAL_ATOMS_UNRESOLVED` | 15 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / unbound |
| `INTERNAL_ATOM_WITHOUT_CONFIRMED_PARENT` | 154 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / INTERNAL_ATOM_WITHOUT_OFFICIAL_PARENT |
| `OFFICIAL_REQUIRED_UNMAPPED` | 537 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / OFFICIAL_REQUIRED_UNMAPPED |
| `UNJUSTIFIED_MULTIPLE_ASSIGNMENT` | 1 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / UNJUSTIFIED_MULTIPLE_ASSIGNMENT |
| `WRONG_YEAR_USED_AS_AUTHORITY` | 0 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / WRONG_YEAR_USED_AS_AUTHORITY |
| `AUTHORITY_NAMESPACE_VIOLATION` | 0 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / AUTHORITY_NAMESPACE_VIOLATION |
| `REFERENTIAL_AUTHORITY_NOT_EXPLICIT` | 0 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / REFERENTIAL_AUTHORITY_NOT_EXPLICIT |
| `DIFF_1SPE_ADDED_2026_MANDATORY` | 28 | `audit/1SPE_PROGRAMME_DIFF_2019_2026.json` :: summary / ADDED_2026_MANDATORY |
| `DIFF_1SPE_REMOVED_2026_MANDATORY` | 12 | `audit/1SPE_PROGRAMME_DIFF_2019_2026.json` :: summary / REMOVED_2026_MANDATORY |
| `AUTOMATISMS_1SPE_OFFICIAL` | 17 | `audit/1SPE_PROGRAMME_DIFF_2019_2026.json` :: summary / AUTOMATISMS_2026 |
| `MISLEADING_LIBELLE_BO_FIELDS_USED_AS_AUTHORITY` | 0 | `audit/LIBELLE_BO_AUTHORITY_GATE.json` :: summary / MISLEADING_LIBELLE_BO_FIELDS_USED_AS_AUTHORITY |
| `LIBELLE_BO_AUTHORITY_GATE` | PASS | `audit/LIBELLE_BO_AUTHORITY_GATE.json` :: summary / LIBELLE_BO_AUTHORITY_GATE |

## Comment lire ces compteurs

- **`INTERNAL_ATOMS_PROPOSED`** — rapprochements mesures, publies avec leurs concurrents ; ils ne valent pas couverture.
- **`INTERNAL_ATOM_WITHOUT_CONFIRMED_PARENT`** — atomes internes dont le parent officiel n'est pas etabli : la somme des propositions en attente et des atomes sans candidat.
- **`OFFICIAL_REQUIRED_UNMAPPED`** — rattachement non encore etabli — PAS un contenu absent du manuel. Les referentiels internes encodent surtout des capacites ; une connaissance peut etre parfaitement traitee dans un fichier de cours sans posseder d'atome dedie.
- **`AUTOMATISMS_1SPE_OFFICIAL`** — automatismes que le programme de 2026 enonce ; leur presence dans le manuel se juge ailleurs, sur les objets eux-memes.
- **`MISLEADING_LIBELLE_BO_FIELDS_USED_AS_AUTHORITY`** — champs dont le nom promet le texte du Bulletin officiel sans qu'aucun producteur ne l'ait verifie. Le champ `libelle_bo` du referentiel interne n'est verbatim que dans la moitie des cas : il est deprecie au profit de `libelle_interne`, et le texte officiel exact vit dans l'inventaire sous `official_wording`.
