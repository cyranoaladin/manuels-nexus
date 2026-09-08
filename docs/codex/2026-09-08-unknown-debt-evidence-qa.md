# Compteurs inconnus dans l'agrégateur de dette

Lot QA distinct du consommateur programme. Les nouvelles valeurs `null` de contrôles non évalués déclenchaient `int(None)` dans `build_zero_technical_debt._required`. En outre, un booléen faux et `0.5` devenaient artificiellement zéro par coercition.

Le consommateur accepte maintenant uniquement un entier non négatif. Une absence ou une valeur malformée inscrit la clé exacte dans `missing_or_malformed_evidence`, augmente la dette de preuve et bloque `all_product_debts_zero` et le CLI. Aucun P0 ou défaut produit n'est inventé. Le nombre produit conservé est seulement le sous-total des compteurs connus ; `debt_measurement_status=INCOMPLETE_EVIDENCE` l'indique explicitement. Une vraie valeur de défaut reste comptée comme dette produit.

Le rendu Markdown affichait auparavant `CLEARED (0)` pour chaque ligne, quelle que soit la valeur mesurée. Il utilise maintenant le même statut calculé que le JSON et rend visible la dette de preuve. Les sous-totaux incomplets ne sont jamais affichés comme clôturés.

Régression sur fixtures temporaires cohérentes : **6 échecs / 1 succès** avant correction (`/tmp/nsi-unknown-evidence-red.log`), puis **7 succès**, aucun skip/xfail :

`python -m pytest tests/test_zero_debt_unknown_evidence.py -q --junitxml=/tmp/nsi-unknown-evidence-green.xml`

Cas : preuve complète, `null`, texte `NOT_EVALUATED`, booléen faux, entier négatif, flottant et vraie dette produit. Le test observe aussi le RC du CLI et le rendu du programme. Ruff et `git diff --check` passent. Aucun artefact de collection, registre de findings ou statut humain n'a été modifié ; cette observation ne certifie pas les anciens agrégats suivis.

## Contre-revue indépendante

`/root` a lu le producteur, le diff, les sept tests et cette note. Réexécution sur fixtures : `python -m pytest -q tests/test_zero_debt_unknown_evidence.py --junitxml=/tmp/root-zero-debt-qa1c.xml` : **7 succès**, aucun échec, erreur ou skip. La portée vérifiée est le traitement des compteurs inconnus et leur affichage, sans audit général des producteurs amont ou de leur fraîcheur. Aucune approbation humaine.

Empreintes observées :

```json
{
  "scripts/build_zero_technical_debt.py": "sha256:503bdc23cee2feb1b3c67dfb7f7417a501f4c6262c45b991e7443deff80cfedc",
  "tests/test_zero_debt_unknown_evidence.py": "sha256:1ece6b3a6f15da96ecbdb4f2653afb6d857a0b05843bea24e411ebf0c0477fef",
  "/tmp/root-zero-debt-qa1c.xml": "sha256:237b3a452171b6424351cd711b8db2552321508e565270e4c94dfb9f64f45be8"
}
```
