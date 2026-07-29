# AGENTS.md — Manuels Nexus Réussite

## Mission du dépôt

Ce dépôt produit des manuels scolaires Nexus Réussite. Toute modification doit préserver simultanément :

- exactitude disciplinaire ;
- conformité aux programmes officiels ;
- qualité pédagogique ;
- séparation élève/professeur ;
- stabilité LaTeX/PDF ;
- reproductibilité ;
- traçabilité.

Le manuel de Mathématiques Première spécialité est actuellement **NO-GO publication**.

## Document contractuel à lire

Avant tout travail concernant Mathématiques Première, lire intégralement :

`CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md`

Lire également les audits, matrices et décisions applicables dans `audit/` et `docs/codex/`.

Ne jamais considérer un ancien rapport ou un message d’agent comme source de vérité s’il contredit les sources, les builds ou les tests.

## Démarrage obligatoire

Avant toute modification :

```bash
git status --short --branch
git rev-parse HEAD
git log --oneline --decorate -15
git diff --stat
git diff --check
```

- Préserver tout WIP local.
- Ne pas changer de branche si des modifications non auditées existent.
- Ne pas restaurer, nettoyer ou stasher automatiquement.
- Identifier le document `AGENTS.md` ou `AGENTS.override.md` le plus proche du fichier modifié.

## Interdictions Git

Ne jamais exécuter sans instruction humaine explicite :

- `git reset --hard`
- `git clean`
- `git restore`
- `git checkout --`
- `git rebase`
- `git merge`
- `git push --force`
- `git push --force-with-lease`
- déplacement ou réécriture de tags
- fusion dans `main`

Travailler sur une branche dédiée. Les commits doivent être atomiques.

## Autorité

Ordre de priorité :

1. textes officiels ;
2. cahier des charges ;
3. présent fichier et éventuels fichiers plus proches ;
4. schémas et gates ;
5. décisions humaines approuvées ;
6. rapports générés ;
7. historiques.

## Exactitude mathématique

- Aucun contenu `generated`, `draft` ou `needs_*_review` n’est publiable.
- Vérifier les identités, valeurs, dérivées, racines, signes, probabilités et sorties.
- Utiliser SymPy lorsque pertinent, sans le substituer à une preuve.
- Toute correction d’erreur doit ajouter un test de régression.
- Les QCM, distracteurs, diagnostics, remédiations et corrigés doivent être cohérents entre eux.
- Un agent ne s’auto-approuve pas sur une correction disciplinaire critique.

## Programme 2026

Toute capacité doit être rattachée à une source officielle et à l’édition 2026-2027.

Points sensibles :

- forme canonique générale ;
- exponentielle ;
- logarithmes et limites ;
- listes Python ;
- simulations et statistiques ;
- répétitions de Bernoulli ;
- contenus de Terminale ;
- épreuve anticipée 2027.

Ne jamais présenter un approfondissement comme exigible.

## Version élève

La version élève ne doit contenir :

- aucun corrigé complet ;
- aucun barème ;
- aucune note professeur ;
- aucun identifiant interne `1SPE-*` visible ;
- aucun placeholder ;
- aucun renvoi provisoire.

## Python

- Le code publié provient de fichiers `.py`.
- Chaque fichier est parsé et exécuté.
- Les sorties sont générées et comparées.
- Interdire les guillemets typographiques et opérateurs mathématiques invalides dans le code.
- Tester les boucles et les seuils.

## LaTeX, design et PDF

- Aucun numéro de page métier codé en dur.
- Aucun chevauchement, débordement ou texte caché.
- Les notes marginales doivent avoir un fallback dans le flux principal.
- Les pages d’ouverture doivent accepter des titres et contenus variables.
- Les en-têtes doivent refléter la rubrique réelle.
- Le PDF final doit avoir signets, liens, métadonnées et polices incorporées.
- Toute baseline visuelle exige une approbation explicite et un diff avant/après.

## Boucle Nexus

Chaque capacité doit comporter, sauf justification approuvée :

1. diagnostic ;
2. orientation ;
3. cours essentiel ;
4. exemple expert ;
5. guidage estompé ;
6. entraînement ;
7. preuve de maîtrise ;
8. remédiation ;
9. re-test ;
10. réactivation ;
11. transfert.

## Chutes

Si le MCP Chutes est disponible :

- effectuer un smoke test ;
- utiliser seulement les modèles réellement disponibles ;
- ne transmettre aucun secret ou donnée personnelle ;
- consulter des expertises indépendantes ;
- vérifier localement chaque recommandation ;
- consigner les consultations utiles dans `audit/chutes/`.

Chutes est consultatif.

## Tests et gates

Avant commit :

```bash
git diff --check
git status --short
```

Exécuter les tests ciblés, puis les gates affectés.

Avant une PR de release :

- tests complets ;
- build élève ;
- build professeur ;
- préflight PDF ;
- comparaison des variantes ;
- contrôle visuel ;
- `--validate-model`;
- `--fail-on-new`;
- `--release-strict`.

`--release-strict` doit rester rouge tant que le manuel n’est pas réellement publiable.

## Commits

Préfixes :

- `[AUDIT]`
- `[MATH]`
- `[PROGRAMME]`
- `[PEDAGOGIE]`
- `[LATEX]`
- `[PYTHON]`
- `[PDF]`
- `[TESTS]`
- `[CI]`
- `[DOCS]`

Ne pas mélanger correction mathématique, refactorisation, baseline visuelle et migration de données dans un même commit.

## Code Review Rules

- Signaler toute erreur ou ambiguïté mathématique comme P0.
- Signaler toute capacité sans source officielle.
- Signaler tout contenu hors programme non étiqueté.
- Signaler toute fuite de corrigé vers la version élève.
- Signaler tout ID interne ou placeholder visible.
- Signaler tout code non exécuté ou sortie saisie manuellement.
- Signaler tout changement de référence visuelle sans preuve.
- Signaler tout gate affaibli, supprimé, ignoré ou transformé en `skip`/`xfail`.
- Signaler toute déclaration de complétude qui n’est pas dérivée d’un inventaire ou d’un build observé.
- Préférer une correction minimale, prouvée et testée.

## Compte rendu

Terminer chaque session avec :

```text
ÉTAT <SHA>
Branche :
Phase :
Commits :
Tests :
Gates verts :
Gates rouges :
P0 ouverts :
Décisions humaines :
PR :
Prochaine action :
```
