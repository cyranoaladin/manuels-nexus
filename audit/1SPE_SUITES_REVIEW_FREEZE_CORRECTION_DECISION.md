# 1SPE-SUITES — correction du gel de revue

**Statut : `DECISION_BLOCKED_PREMISE_DISPROVEN` — bloquant.**

La décision humaine du 2026-08-26 fixe `CANONICAL_HUMAN_REVIEW_OBJECT_COUNT = 156`
et qualifie 161 de double comptage des cinq fiches `FR-R*`.

**Le dépôt réfute cette prémisse.** Elle vient de mon analyse du checkpoint
précédent, et cette analyse était fausse. Je ne peux pas enregistrer
`old state = INVALIDATED_DOUBLE_COUNT` : ce serait inscrire un fait démenti par
les objets Git.

## Ce que le dépôt montre

| Commit | Objets `% META` | Identifiants uniques | Doublons |
|---|---:|---:|---:|
| `761508d9` (HEAD de la branche courante) | 156 | 156 | **0** |
| `c667f12b` (le SHA que vous fixez) | 161 | 161 | **0** |

Les cinq fiches `FR-R1` … `FR-R5` apparaissent **exactement une fois** aux deux
commits. Il n'y a de double comptage à aucun des deux.

`161` et `156` ne comptent pas deux fois les mêmes objets : ils comptent **le
même chapitre à deux commits différents**.

## Les 5 objets de l'écart

`c667f12b` est **strictement additif** — 5 objets ajoutés, aucun retiré :

| Objet | Type | Chemin |
|---|---|---|
| `1SPE-SUITES-CR-017` | `cours` | `cours/17_C8_limites_intuitives.tex` |
| `1SPE-SUITES-ME-008` | `methode` | `methodes/1SPE-SUITES-ME-008.tex` |
| `1SPE-SUITES-EX-051` | `exercice` | `exercices/1SPE-SUITES-EX-051.tex` |
| `1SPE-SUITES-CO-051` | `corrige` | `corriges/1SPE-SUITES-CO-051.tex` |
| `1SPE-SUITES-RE-C8` | `remediation` | `remediation/1SPE-SUITES-RE-C8.tex` |

Ce n'est pas un lot arbitraire : c'est une **capacité entière**.

## Cause racine : la capacité C8

`c667f12b` ajoute au contrat du chapitre :

```yaml
- { code: C8, ref_capacite: 1SPE-SUITES-C8,
    libelle_eleve: "Je sais reconnaître intuitivement une limite finie,
    une limite infinie ou une absence de limite, sans formalisation." }
```

et au référentiel :

```json
{ "id": "1SPE-SUITES-C8",
  "libelle_bo": "Sensibilisation intuitive à la notion de limite d'une suite :
                 limite finie, limite infinie et absence de limite ;
                 toute formalisation est exclue.",
  "formalisation_exclue": true }
```

Au même commit, l'autorité programme du référentiel passe du **BO spécial n°1 du
22 janvier 2019** à **`MENE2602917A`**, le programme applicable à la rentrée
2026-2027.

Autrement dit : `c667f12b` met `1SPE-SUITES` en conformité avec le programme
2026. `761508d9` ne porte pas encore cette mise en conformité.

## Conséquence

Geler à **156 sur `761508d9`**, c'est geler un chapitre **dépourvu d'une capacité
déclarée par le programme 2026**. Un `EXPERT_PROGRAMME_PEDAGOGIE` recevant ce
packet ne pourrait pas conclure à la conformité `MENE2602917A` : son packet B
exige explicitement « conformité au BO applicable » et « exhaustivité des
attendus obligatoires ».

Par ailleurs, la décision est **incohérente avec elle-même** : elle fixe
`new source SHA = c667f12b`, or ce commit porte 161 objets uniques, pas 156.

## Ce que je n'ai pas écrit, et pourquoi

| Champ demandé | Non écrit | Raison |
|---|---|---|
| `old state = INVALIDATED_DOUBLE_COUNT` | oui | fait réfuté : 0 doublon aux deux commits |
| `new count = 156` avec `new source SHA = c667f12b` | oui | les deux valeurs sont mutuellement incohérentes |
| Nouveaux packets issus d'un gel à 156 | oui | un gel non tranché ne peut pas produire de packet |

Conformément à la section 20, aucun reviewer n'est assigné, aucun reçu n'est
matérialisé, aucun statut n'est promu.

## Les trois options

| Option | Décision | Implication |
|---|---|---|
| **A** | Geler sur `761508d9` à **156** | Le gel exclut explicitement C8. Le packet doit porter cette exclusion, et la revue programme ne peut pas conclure à la conformité `MENE2602917A`. |
| **B** | Geler sur `c667f12b` à **161** | Le gel couvre C8. `161` redevient canonique et n'a jamais été un double comptage. Exige d'intégrer `c667f12b` dans la branche courante. |
| **C** | Intégrer C8 dans la branche courante, puis geler | Compte à recalculer après intégration. Aucun gel avant. |

`c667f12b` appartient à la branche `codex/t2-current-audit-continue` ; il est un
**descendant** de `761508d9`, pas un ancêtre. La branche courante est donc en
retard de cette mise en conformité, ainsi que de 1 043 autres fichiers.

## Ce qui a été fait malgré le blocage

Les travaux déterministes indépendants de cette question ont avancé :

- section 5 — l'exclusion `META.status` / `contrat.statut` est désormais une
  **allowlist fermée** déclarée dans `HUMAN_REVIEW_GOVERNANCE.yaml` et
  verrouillée par `human-review-governance.schema.json`. Élargir l'exclusion
  exige de modifier le contrat **et** son schéma. Les sept tests obligatoires
  passent, plus un test qui mute chaque clé `META` une par une et vérifie que
  seule `status` est sans effet sur le digest ;
- section 4 — l'autorisation humaine du rôle `EXPERT_NSI` est enregistrée dans
  le contrat, avec `constitutes_no_nsi_review: true`.
