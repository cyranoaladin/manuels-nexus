# Provenance des assemblages de livrables auxiliaires

- Livrables investigués : `6`
- Dérivés des sources canoniques : `4`
- Nouveaux assemblages requis : `2`
- Assemblages désormais déclarés : `4`
- Masters rédigés de zéro : `0`

| Livrable | Décision | Assemblage déclaré |
|---|---|---|
| `1SPE::livret_methodes` | `DERIVE_FROM_CURRENT_CANONICAL_SOURCES` | oui |
| `1SPE::livret_remediation` | `DERIVE_FROM_CURRENT_CANONICAL_SOURCES` | oui |
| `TSPE_2026_2027::livret_methodes` | `DERIVE_FROM_CURRENT_CANONICAL_SOURCES` | oui |
| `TSPE_2026_2027::livret_remediation` | `DERIVE_FROM_CURRENT_CANONICAL_SOURCES` | oui |
| `TNSI::banque_ecrite` | `NEW_ASSEMBLY_REQUIRED` | **non** |
| `TNSI::banque_pratique` | `NEW_ASSEMBLY_REQUIRED` | **non** |

## Justifications

- `1SPE::livret_methodes` — Les sources existent chapitre par chapitre et l'assembleur du manuel sait déjà parcourir les chapitres, poser les ouvertures et marquer les rubriques. Il manquait la déclaration de la variante, pas une recette.
- `1SPE::livret_remediation` — Les sources existent chapitre par chapitre et l'assembleur du manuel sait déjà parcourir les chapitres, poser les ouvertures et marquer les rubriques. Il manquait la déclaration de la variante, pas une recette.
- `TSPE_2026_2027::livret_methodes` — Les sources existent chapitre par chapitre et l'assembleur du manuel sait déjà parcourir les chapitres, poser les ouvertures et marquer les rubriques. Il manquait la déclaration de la variante, pas une recette.
- `TSPE_2026_2027::livret_remediation` — Les sources existent chapitre par chapitre et l'assembleur du manuel sait déjà parcourir les chapitres, poser les ouvertures et marquer les rubriques. Il manquait la déclaration de la variante, pas une recette.
- `TNSI::banque_ecrite` — L'assembleur NSI prévoit déjà un répertoire `ece` dans ses ordres `eleve` et `professeur`, mais aucun chapitre TNSI n'en possède : le créneau est déclaré, le contenu n'existe pas. Ce n'est donc pas un assemblage manquant mais du contenu manquant.
- `TNSI::banque_pratique` — Même constat que la banque écrite. Une banque pratique exige en outre un environnement d'exécution, des jeux de données, des cas de test et des corrigés exécutables : elle ne peut pas être dérivée des chapitres existants.
