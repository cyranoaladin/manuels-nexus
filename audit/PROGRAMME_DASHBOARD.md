# Couverture programme — tableau de bord

Fichier genere par `scripts/build_programme_dashboard.py`.
Ne pas editer : chaque valeur est relue dans l'artefact qui la produit.

| Compteur | Valeur | Artefact |
|---|---|---|
| `CANONICAL_OFFICIAL_ITEMS_APPLICABLE` | 932 | `audit/OFFICIAL_PROGRAMME_INVENTORY.json` :: official_items_applicable |
| `CANONICAL_OFFICIAL_ITEMS_MANDATORY` | 694 | `audit/OFFICIAL_PROGRAMME_INVENTORY.json` :: official_items_mandatory |
| `OFFICIAL_REFERENCES_VERIFIED` | 6/6 | `audit/OFFICIAL_PROGRAMME_INVENTORY.json` :: OFFICIAL_REFERENCES_VERIFIED |
| `INTERNAL_ATOMS` | 313 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / internal_atoms |
| `INTERNAL_ATOMS_CONFIRMED_PARENT` | 279 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / bound_confirmed |
| `INTERNAL_ATOMS_CONFIRMED_BY_CONTEXT` | 110 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / bound_by_context |
| `INTERNAL_ATOMS_AMBIGUOUS_REQUIRES_HUMAN` | 34 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / ambiguous_requires_human |
| `INTERNAL_ATOMS_UNRESOLVED` | 34 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / unbound |
| `INTERNAL_ATOM_WITHOUT_CONFIRMED_PARENT` | 34 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / INTERNAL_ATOM_WITHOUT_OFFICIAL_PARENT |
| `OFFICIAL_REQUIRED_UNMAPPED` | 418 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / OFFICIAL_REQUIRED_UNMAPPED |
| `UNJUSTIFIED_MULTIPLE_ASSIGNMENT` | 5 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / UNJUSTIFIED_MULTIPLE_ASSIGNMENT |
| `WRONG_YEAR_USED_AS_AUTHORITY` | 0 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / WRONG_YEAR_USED_AS_AUTHORITY |
| `AUTHORITY_NAMESPACE_VIOLATION` | 0 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / AUTHORITY_NAMESPACE_VIOLATION |
| `REFERENTIAL_AUTHORITY_NOT_EXPLICIT` | 0 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / REFERENTIAL_AUTHORITY_NOT_EXPLICIT |
| `DIFF_1SPE_ADDED_2026_MANDATORY` | 28 | `audit/1SPE_PROGRAMME_DIFF_2019_2026.json` :: summary / ADDED_2026_MANDATORY |
| `DIFF_1SPE_REMOVED_2026_MANDATORY` | 12 | `audit/1SPE_PROGRAMME_DIFF_2019_2026.json` :: summary / REMOVED_2026_MANDATORY |
| `AUTOMATISMS_1SPE_OFFICIAL` | 17 | `audit/1SPE_PROGRAMME_DIFF_2019_2026.json` :: summary / AUTOMATISMS_2026 |
| `MISLEADING_LIBELLE_BO_FIELDS_USED_AS_AUTHORITY` | 0 | `audit/LIBELLE_BO_AUTHORITY_GATE.json` :: summary / MISLEADING_LIBELLE_BO_FIELDS_USED_AS_AUTHORITY |
| `LIBELLE_BO_AUTHORITY_GATE` | PASS | `audit/LIBELLE_BO_AUTHORITY_GATE.json` :: summary / LIBELLE_BO_AUTHORITY_GATE |
| `OFFICIAL_REQUIRED_COMPLETE` | 619 | `audit/OFFICIAL_TO_MANUAL_COVERAGE.json` :: summary / OFFICIAL_REQUIRED_COMPLETE |
| `OFFICIAL_REQUIRED_PARTIAL` | 45 | `audit/OFFICIAL_TO_MANUAL_COVERAGE.json` :: summary / OFFICIAL_REQUIRED_PARTIAL |
| `OFFICIAL_REQUIRED_MISSING` | 13 | `audit/OFFICIAL_TO_MANUAL_COVERAGE.json` :: summary / OFFICIAL_REQUIRED_MISSING |
| `OFFICIAL_REQUIRED_INSTITUTIONAL` | 14 | `audit/OFFICIAL_TO_MANUAL_COVERAGE.json` :: summary / OFFICIAL_REQUIRED_INSTITUTIONAL |
| `OFFICIAL_REQUIRED_UNDECIDABLE_BY_CONTENT_MATCH` | 3 | `audit/OFFICIAL_TO_MANUAL_COVERAGE.json` :: summary / OFFICIAL_REQUIRED_UNDECIDABLE_BY_CONTENT_MATCH |
| `MANUAL_OBJECTS_INDEXED` | 3483 | `audit/OFFICIAL_TO_MANUAL_COVERAGE.json` :: summary / objects_indexed |

## Comment lire ces compteurs

- **`INTERNAL_ATOMS_CONFIRMED_BY_CONTEXT`** — rattachements etablis par la structure des deux sources : la partie du programme que le chapitre traite, et le libelle de l'attendu a l'interieur de cette partie. Ce n'est pas une approbation humaine ; la preuve est publiee avec chaque lien.
- **`INTERNAL_ATOMS_AMBIGUOUS_REQUIRES_HUMAN`** — atomes qu'aucune preuve objective ne tranche. Ils ne portent aucun parent et attendent un arbitrage ; chacun est classe (subdivision pedagogique, enrichissement, programme perime, atome obsolete).
- **`INTERNAL_ATOM_WITHOUT_CONFIRMED_PARENT`** — atomes internes dont le parent officiel n'est pas etabli : la somme des propositions en attente et des atomes sans candidat.
- **`OFFICIAL_REQUIRED_UNMAPPED`** — rattachement non encore etabli — PAS un contenu absent du manuel. Les referentiels internes encodent surtout des capacites ; une connaissance peut etre parfaitement traitee dans un fichier de cours sans posseder d'atome dedie.
- **`AUTOMATISMS_1SPE_OFFICIAL`** — automatismes que le programme de 2026 enonce ; leur presence dans le manuel se juge ailleurs, sur les objets eux-memes.
- **`MISLEADING_LIBELLE_BO_FIELDS_USED_AS_AUTHORITY`** — champs dont le nom promet le texte du Bulletin officiel sans qu'aucun producteur ne l'ait verifie. Le champ `libelle_bo` du referentiel interne n'est verbatim que dans la moitie des cas : il est deprecie au profit de `libelle_interne`, et le texte officiel exact vit dans l'inventaire sous `official_wording`.
- **`OFFICIAL_REQUIRED_MISSING`** — attendus obligatoires dont AUCUN objet du manuel ne porte la trace. A distinguer de OFFICIAL_REQUIRED_UNMAPPED, qui ne dit que l'absence de rattachement etabli entre le referentiel interne et le BO.
- **`OFFICIAL_REQUIRED_INSTITUTIONAL`** — exigences que le manuel ne peut pas certifier a lui seul -- « Un quart au moins de l'horaire total est reserve aux projets » releve de l'etablissement. Le manuel peut les outiller, pas les garantir.
- **`OFFICIAL_REQUIRED_UNDECIDABLE_BY_CONTENT_MATCH`** — attendus dont le libelle officiel ne porte aucun mot distinctif exploitable : la recherche par contenu ne peut ni conclure a la presence ni conclure a l'absence.
