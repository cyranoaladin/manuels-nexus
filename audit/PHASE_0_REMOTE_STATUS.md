# État distant de la Phase 0

Observation du 30 juillet 2026.

## Sauvegarde distante

| Élément | Valeur observée |
|---|---|
| Branche locale | `finalisation/collection-v1` |
| HEAD lors de la tentative | `298d1194eb248361a3eaf12b342ce170383dd384` |
| Branche distante | `origin/finalisation/collection-v1` |
| SHA distant | `20679de69a25d694196a2153f6f4d16fe4c4aa91` |
| Avance locale lors de la tentative | 37 commits |
| Commande | `git push -u origin finalisation/collection-v1` |
| Résultat | **NON EXÉCUTÉ — push non réalisé** |

Erreur exacte renvoyée avant création du processus :

```text
Rejected("approval required by policy, but AskForApproval is set to Never")
```

Aucun `--force`, tag, changement de `main` ou release n'a été exécuté.

## Draft PR

GitHub CLI est authentifié avec le compte actif `cyranoaladin`, mais aucune
draft PR n'a été ouverte : la branche distante ne contient pas les commits
locaux et une PR sur son ancien SHA serait trompeuse.

Après un push réussi, exécuter :

```bash
gh pr create \
  --repo cyranoaladin/manuels-nexus \
  --draft \
  --base main \
  --head finalisation/collection-v1 \
  --title "[Draft][Audit] Stabilisation Phase 0 de la collection Nexus" \
  --body "$(cat <<'EOF'
NO-GO merge.
NO-GO release.

- `--validate-model` : vert.
- `--fail-on-new` : vert après qualification et gel de la baseline.
- Cinq tests visuels : rouges, décision humaine requise sur huit pages.
- `--release-strict` : rouge, code 7, 69 raisons déterministes.
- Baseline : contrôle de non-régression uniquement ; `release_acceptance: false`.
- Aucun P0 mathématique traité.

Cette PR doit rester en draft et ne doit pas être fusionnée tant que les
divergences visuelles et la CI Phase 0 ne sont pas résolues.
EOF
)"
```

## CI distante

`gh run list --branch finalisation/collection-v1` ne retourne aucune exécution.
La CI distante du SHA local n'existe donc pas encore et ne peut pas être
qualifiée. Le workflow ne pourra démarrer qu'après sauvegarde de la branche.
