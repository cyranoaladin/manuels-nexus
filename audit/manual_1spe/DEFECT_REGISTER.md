# Registre des défauts — Mathématiques Première — chapitre Suites

Statut : **préparation documentaire seulement ; aucune correction
mathématique implémentée**.

Source contractuelle :
`CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md`, défauts MATH-001, MATH-002,
MATH-003 et MATH-007.

## Synthèse

| ID | Sévérité | Défaut | Reproduction | Statut | Test de régression requis |
|---|---|---|---|---|---|
| `1SPE-SUITES-MATH-001-DEFINITION` | P0 | définition limitée à `q != 0`, `u_0 != 0` | cours C3, lignes 10–16 et 34 | reproduit | accepter `q=0` et `u_0=0` |
| `1SPE-SUITES-MATH-001-Q-ZERO` | P0 | cas `q=0` exclu | cours C3 et diagnostic QCM | reproduit | suite de raison 0 |
| `1SPE-SUITES-MATH-001-ZERO-SEQUENCE` | P0 | suite nulle/terme nul déclarés impossibles | cours C3, QCM TeX et JSON | reproduit | suite nulle + QCM cohérent |
| `1SPE-SUITES-MATH-001-QUOTIENT` | P0 | quotient présenté comme définition générale | méthode M3, remédiation, évaluations A/B | reproduit | quotient seulement sous non-nullité |
| `1SPE-SUITES-MATH-002-MINUS-ONE` | P0 | `(-1)^n` dite non géométrique puis traitée comme telle | cours C4, ligne 62 | reproduit | raison `-1` et somme finie |
| `1SPE-SUITES-MATH-007-NOTATION-U-N` | P0 | `u(n)` déclarée non mathématique/interdite | cours C1 et QCM JSON | reproduit | reconnaître la notation fonctionnelle |
| `1SPE-SUITES-MATH-003-CAPITAL-4-PERCENT` | P0 | valeurs/sorties à 4 % à inventorier intégralement | contrôle ponctuel de M7 cohérent | reproduction exhaustive ouverte | source exécutable et comparaison des sorties |
| `1SPE-SUITES-MATH-001-PROPAGATION` | P0 | prémisses erronées propagées entre objets | QCM, diagnostics, méthode, remédiation, corrigés | reproduit | cohérence transversale + mutation |

## Constats mathématiques à préserver

- Définition : une suite est géométrique s'il existe un réel `q` tel que
  `u_{n+1}=q u_n`.
- Le cas `q=0` est valide.
- La suite nulle est géométrique.
- Un terme nul n'interdit pas le caractère géométrique ; il interdit seulement
  certains quotients.
- La caractérisation par `u_{n+1}/u_n=q` exige que le dénominateur soit non nul.
- La suite `(-1)^n` est géométrique de raison `-1`.
- `u_n` est la convention scolaire privilégiée, mais `u(n)` reste une notation
  fonctionnelle mathématique recevable.

## Capital à 4 %

Le contrôle ponctuel de
`methodes/1SPE-SUITES-ME-007.tex` donne :

| Valeur | Résultat observé |
|---|---:|
| `1500 × 1,04^10` | `2220,37` € |
| `1500 × 1,04^17` | `2923,55` € |
| `1500 × 1,04^18` | `3040,49` € |
| plus petit `n` tel que `1500 × 1,04^n >= 3000` | `18` |

Ces quatre valeurs sont cohérentes. MATH-003 reste néanmoins ouvert tant que
toutes les occurrences, sorties Python et variantes ne sont pas inventoriées,
exécutées et comparées par un test unique.

## Propagation obligatoire du futur lot

La correction devra couvrir ensemble :

- définition et propriétés du cours ;
- exemples et contre-exemples ;
- QCM, bonne réponse, distracteurs et diagnostics ;
- méthodes et arbres de décision ;
- exercices et évaluations ;
- remédiations et re-tests ;
- corrigés et commentaires de marge ;
- sorties Python et valeurs numériques.

Aucun fichier de contenu n'a été modifié dans ce lot. Une correction
disciplinaire future exigera des tests de régression, une revue mathématique
indépendante et un commit `[MATH]` distinct.
