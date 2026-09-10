# Couverture programme — tableau de bord

Fichier genere par `scripts/build_programme_dashboard.py`.
Ne pas editer : chaque valeur est relue dans l'artefact qui la produit.

| Compteur | Valeur | Artefact |
|---|---|---|
| `CANONICAL_OFFICIAL_ITEMS_APPLICABLE` | 965 | `audit/OFFICIAL_PROGRAMME_INVENTORY.json` :: official_items_applicable |
| `CANONICAL_OFFICIAL_ITEMS_MANDATORY` | 643 | `audit/OFFICIAL_PROGRAMME_INVENTORY.json` :: official_items_mandatory |
| `OFFICIAL_REFERENCES_VERIFIED` | 6/6 | `audit/OFFICIAL_PROGRAMME_INVENTORY.json` :: OFFICIAL_REFERENCES_VERIFIED |
| `INTERNAL_ATOMS` | 316 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / internal_atoms |
| `INTERNAL_ATOMS_CONFIRMED_PARENT` | 316 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / bound_confirmed |
| `INTERNAL_ATOMS_CONFIRMED_BY_CONTEXT` | 112 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / bound_by_context |
| `INTERNAL_ATOMS_AMBIGUOUS_REQUIRES_HUMAN` | 0 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / ambiguous_requires_human |
| `INTERNAL_ATOMS_UNRESOLVED` | 0 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / unbound |
| `INTERNAL_ATOM_WITHOUT_CONFIRMED_PARENT` | 0 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / INTERNAL_ATOM_WITHOUT_OFFICIAL_PARENT |
| `OFFICIAL_REQUIRED_UNMAPPED` | 342 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / OFFICIAL_REQUIRED_UNMAPPED |
| `OFFICIAL_ITEMS_CLAIMED_BY_SEVERAL_THEMES` | 5 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / UNJUSTIFIED_MULTIPLE_ASSIGNMENT |
| `UNJUSTIFIED_MULTIPLE_ASSIGNMENT` | 0 | `audit/MULTIPLE_ASSIGNMENT_RESOLUTION.json` :: summary / UNJUSTIFIED_MULTIPLE_ASSIGNMENT |
| `JUSTIFIED_DISTRIBUTED_COVERAGE` | 5 | `audit/MULTIPLE_ASSIGNMENT_RESOLUTION.json` :: summary / JUSTIFIED_DISTRIBUTED_COVERAGE |
| `WRONG_YEAR_USED_AS_AUTHORITY` | 0 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / WRONG_YEAR_USED_AS_AUTHORITY |
| `AUTHORITY_NAMESPACE_VIOLATION` | 0 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / AUTHORITY_NAMESPACE_VIOLATION |
| `REFERENTIAL_AUTHORITY_NOT_EXPLICIT` | 0 | `audit/OFFICIAL_PROGRAMME_BINDING.json` :: summary / REFERENTIAL_AUTHORITY_NOT_EXPLICIT |
| `DIFF_1SPE_ADDED_2026_MANDATORY` | 27 | `audit/1SPE_PROGRAMME_DIFF_2019_2026.json` :: summary / ADDED_2026_MANDATORY |
| `DIFF_1SPE_REMOVED_2026_MANDATORY` | 12 | `audit/1SPE_PROGRAMME_DIFF_2019_2026.json` :: summary / REMOVED_2026_MANDATORY |
| `MISLEADING_LIBELLE_BO_FIELDS_USED_AS_AUTHORITY` | 0 | `audit/LIBELLE_BO_AUTHORITY_GATE.json` :: summary / MISLEADING_LIBELLE_BO_FIELDS_USED_AS_AUTHORITY |
| `LIBELLE_BO_AUTHORITY_GATE` | PASS | `audit/LIBELLE_BO_AUTHORITY_GATE.json` :: summary / LIBELLE_BO_AUTHORITY_GATE |
| `OFFICIAL_REQUIRED_COMPLETE` | 599 | `audit/OFFICIAL_TO_MANUAL_COVERAGE.json` :: summary / OFFICIAL_REQUIRED_COMPLETE |
| `OFFICIAL_REQUIRED_PARTIAL` | 26 | `audit/OFFICIAL_TO_MANUAL_COVERAGE.json` :: summary / OFFICIAL_REQUIRED_PARTIAL |
| `OFFICIAL_REQUIRED_MISSING` | 0 | `audit/OFFICIAL_TO_MANUAL_COVERAGE.json` :: summary / OFFICIAL_REQUIRED_MISSING |
| `OFFICIAL_REQUIRED_INSTITUTIONAL` | 18 | `audit/OFFICIAL_TO_MANUAL_COVERAGE.json` :: summary / OFFICIAL_REQUIRED_INSTITUTIONAL |
| `OFFICIAL_REQUIRED_UNDECIDABLE_BY_CONTENT_MATCH` | 0 | `audit/OFFICIAL_TO_MANUAL_COVERAGE.json` :: summary / OFFICIAL_REQUIRED_UNDECIDABLE_BY_CONTENT_MATCH |
| `MANUAL_OBJECTS_INDEXED` | 3486 | `audit/OFFICIAL_TO_MANUAL_COVERAGE.json` :: summary / objects_indexed |
| `NEXUS_ALGORITHMIC_QUALITY_PARTS_WITHOUT_WORK` | 4 | `audit/OFFICIAL_TO_MANUAL_COVERAGE.json` :: summary / NEXUS_ALGORITHMIC_QUALITY_PARTS_WITHOUT_WORK |
| `NORMATIVITY_CREATED_BY_ATOMIZATION` | 0 | `audit/NORMATIVITY_PROVENANCE_GATE.json` :: summary / NORMATIVITY_CREATED_BY_ATOMIZATION |
| `MANDATORY_COUNT_BEFORE` | 643 | `audit/NORMATIVITY_PROVENANCE_GATE.json` :: summary / MANDATORY_COUNT_BEFORE |
| `MANDATORY_COUNT_AFTER` | 643 | `audit/NORMATIVITY_PROVENANCE_GATE.json` :: summary / MANDATORY_COUNT_AFTER |
| `CHANGED_NORMATIVITY_ITEMS` | 0 | `audit/NORMATIVITY_PROVENANCE_GATE.json` :: summary / CHANGED_NORMATIVITY_ITEMS |
| `AUTOMATISMS_1SPE_ADEQUATELY_REINVESTED` | 12 | `audit/1SPE_AUTOMATISMS_AUDIT.json` :: summary / AUTOMATISMS_1SPE_ADEQUATELY_REINVESTED |
| `AUTOMATISM_NOT_REINVESTED` | 5 | `audit/1SPE_AUTOMATISMS_AUDIT.json` :: summary / AUTOMATISM_NOT_REINVESTED |
| `ADDED_2026_TRULY_MISSING` | 0 | `audit/1SPE_REFORM_TRANSITION_AUDIT.json` :: summary / ADDED_TRULY_MISSING |
| `REMOVED_2019_CONTENT_STILL_PRESENTED_AS_REQUIRED` | 0 | `audit/1SPE_REFORM_TRANSITION_AUDIT.json` :: summary / REMOVED_2019_CONTENT_STILL_PRESENTED_AS_REQUIRED |
| `REMOVED_2019_CONTENT_REQUIRING_EDITORIAL_REVIEW` | 5 | `audit/1SPE_REFORM_TRANSITION_AUDIT.json` :: summary / REMOVED_2019_CONTENT_REQUIRING_EDITORIAL_REVIEW |
| `TNSI_PROGRAMME_MATRIX` | PASS | `audit/TNSI_EXAM_PREPARATION_MATRIX.json` :: summary / TNSI_PROGRAMME_MATRIX |
| `TNSI_EXAM_PREPARATION_MATRIX` | PASS | `audit/TNSI_EXAM_PREPARATION_MATRIX.json` :: summary / TNSI_EXAM_PREPARATION_MATRIX |
| `EXAM_ONLY_NOTIONS` | 0 | `audit/TNSI_EXAM_PREPARATION_MATRIX.json` :: summary / EXAM_ONLY_NOTIONS |
| `PREREQUISITES_ASSUMED_WITHOUT_SUPPORT` | 1 | `audit/1SPE_PREREQUISITE_SUPPORT.json` :: summary / PREREQUISITES_ASSUMED_WITHOUT_SUPPORT |
| `UNCLASSIFIED_OUT_OF_PROGRAMME_OBJECTS` | 169 | `audit/OBJECTS_TO_OFFICIAL_REVERSE_MAP.json` :: summary / UNCLASSIFIED_OUT_OF_PROGRAMME_OBJECTS |
| `FUTURE_PROGRAM_CONTAMINATION` | 0 | `audit/OBJECTS_TO_OFFICIAL_REVERSE_MAP.json` :: summary / WRONG_YEAR_OBJECTS |
| `OBJECTS_CITING_AN_UNKNOWN_CAPACITY` | 0 | `audit/OBJECTS_TO_OFFICIAL_REVERSE_MAP.json` :: summary / OBJECTS_CITING_AN_UNKNOWN_CAPACITY |

## Comment lire ces compteurs

- **`INTERNAL_ATOMS_CONFIRMED_BY_CONTEXT`** — rattachements etablis par la structure des deux sources : la partie du programme que le chapitre traite, et le libelle de l'attendu a l'interieur de cette partie. Ce n'est pas une approbation humaine ; la preuve est publiee avec chaque lien.
- **`INTERNAL_ATOMS_AMBIGUOUS_REQUIRES_HUMAN`** — atomes qu'aucune preuve objective ne tranche. Ils ne portent aucun parent et attendent un arbitrage ; chacun est classe (subdivision pedagogique, enrichissement, programme perime, atome obsolete).
- **`INTERNAL_ATOM_WITHOUT_CONFIRMED_PARENT`** — atomes internes dont le parent officiel n'est pas etabli : la somme des propositions en attente et des atomes sans candidat.
- **`OFFICIAL_REQUIRED_UNMAPPED`** — rattachement non encore etabli — PAS un contenu absent du manuel. Les referentiels internes encodent surtout des capacites ; une connaissance peut etre parfaitement traitee dans un fichier de cours sans posseder d'atome dedie.
- **`OFFICIAL_ITEMS_CLAIMED_BY_SEVERAL_THEMES`** — attendus revendiques par plusieurs themes internes. Le chiffre brut ne dit pas si c'est une faute : il faut regarder qui ENSEIGNE l'attendu et qui le reinvestit. Voir audit/MULTIPLE_ASSIGNMENT_RESOLUTION.json.
- **`UNJUSTIFIED_MULTIPLE_ASSIGNMENT`** — parmi eux, ceux qu'aucun contenu ne justifie : un theme qui se declare sans rien avoir derriere, ou un attendu pratique sans jamais etre enseigne.
- **`MISLEADING_LIBELLE_BO_FIELDS_USED_AS_AUTHORITY`** — champs dont le nom promet le texte du Bulletin officiel sans qu'aucun producteur ne l'ait verifie. Le champ `libelle_bo` du referentiel interne n'est verbatim que dans la moitie des cas : il est deprecie au profit de `libelle_interne`, et le texte officiel exact vit dans l'inventaire sous `official_wording`.
- **`OFFICIAL_REQUIRED_MISSING`** — attendus obligatoires dont AUCUN objet du manuel ne porte la trace. A distinguer de OFFICIAL_REQUIRED_UNMAPPED, qui ne dit que l'absence de rattachement etabli entre le referentiel interne et le BO.
- **`OFFICIAL_REQUIRED_INSTITUTIONAL`** — exigences que le manuel ne peut pas certifier a lui seul -- « Un quart au moins de l'horaire total est reserve aux projets » releve de l'etablissement. Le manuel peut les outiller, pas les garantir.
- **`OFFICIAL_REQUIRED_UNDECIDABLE_BY_CONTENT_MATCH`** — attendus dont le libelle officiel ne porte aucun mot distinctif exploitable : la recherche par contenu ne peut ni conclure a la presence ni conclure a l'absence.
- **`NEXUS_ALGORITHMIC_QUALITY_PARTS_WITHOUT_WORK`** — exigence de la COLLECTION, pas du programme : parties accompagnees d'exemples d'algorithme officiels ou le manuel n'offre aucun travail algorithmique.
- **`NORMATIVITY_CREATED_BY_ATOMIZATION`** — attendus publies comme obligatoires alors que la rubrique du BO dont ils viennent ne l'est pas. C'est le risque propre a toute chaine d'atomisation : personne ne ment, le niveau d'obligation est cree par le traitement.
- **`AUTOMATISM_NOT_REINVESTED`** — automatismes que le manuel travaille sans les repartir : le programme exclut qu'ils fassent l'objet d'un chapitre specifique et demande qu'ils soient entretenus sur l'annee. Aucun n'est absent du manuel.
- **`ADDED_2026_TRULY_MISSING`** — attendus ajoutes par la reforme qu'il faudrait ecrire. La dette de contenu ne se deduit pas du differentiel : un attendu ajoute au programme peut etre traite depuis des annees.
- **`PREREQUISITES_ASSUMED_WITHOUT_SUPPORT`** — prerequis qu'un chapitre declare mobiliser sans que rien, dans ce chapitre, ne permette a l'eleve de constater le manque ni d'y remedier. Le programme demande que les automatismes de seconde soient entretenus en premiere.
- **`UNCLASSIFIED_OUT_OF_PROGRAMME_OBJECTS`** — objets sans attendu ET sans statut : ni prerequis, ni enrichissement assume, ni entrainement a l'epreuve. Un manuel a le droit de depasser le programme ; il n'a pas le droit de le faire sans le dire.
- **`FUTURE_PROGRAM_CONTAMINATION`** — objets du manuel qui reprennent un attendu d'un programme ne regissant pas cette edition, sur des notions absentes du programme en vigueur.
- **`OBJECTS_CITING_AN_UNKNOWN_CAPACITY`** — objets qui se reclament d'une capacite absente de tout referentiel. L'objet parait rattache et ne l'est pas : personne ne s'en apercoit.
