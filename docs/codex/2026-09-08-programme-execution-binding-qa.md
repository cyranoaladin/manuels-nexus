# Liaison des reçus consommés par le validateur programme

Observation de développement sur base `886a3be10497e1a9d9b3b3825c02220842da09d9`, worktree modifié. Cette note décrit un changement de consommateur et des fixtures temporaires ; elle ne certifie aucune nouvelle source du corpus, aucune date et aucune approbation humaine.

## Défaut reproduit et correction

Le producteur `build_programme_content_validation.py` créditait tout verdict `pass` ou `verified`, sans liaison de source ou méthode. Une disposition historique retrouvée par identifiant suffisait à classer un objet manuel sans défaut. Deux reçus du même objet ajoutaient deux crédits. Une assertion de barème pouvait ainsi faire apparaître une source historique entière comme scientifiquement vérifiée.

Le consommateur dérive désormais l'index courant avec `build_fresh`, vérifie à nouveau ses inputs à la fin, et exige le binder canonique de chaque reçu. L'identité, le digest de source, le protocole et ses dépendances doivent être courants. Les reçus illisibles, périmés, de portée forgée, de verdict inconnu, ou absents du corpus courant sont rejetés explicitement. Les liaisons dupliquées ne produisent aucun crédit.

La preuve d'exécution et la revue scientifique ont des compteurs distincts. Les dimensions scientifiques effectivement requises dans l'index doivent toutes être `VALIDATED_BY_EVIDENCE`, y compris la revue documentaire d'histoire TNSI. Les dimensions éditoriales, pédagogiques et les décisions humaines restent celles de l'index. Un objet contenant des claims exécutables exige en plus une exécution courante passée ; un texte documentaire sans code peut être relu sans inventer d'oracle. Un échec d'exécution reste bloquant.

Les dispositions adversariales antérieures sont visibles avec `current_credit=false`. Elles n'alimentent aucun défaut courant ou déclaration d'absence de défaut. Le nombre de défauts concrets et le contrôle sémantique des contenus hors programme deviennent `null` avec une portée `NOT_RECOMPUTED` / `NOT_EVALUATED` explicite : le vieux producteur ne calculait pas ces résultats. Le compteur historique `NON_FORMALIZABLE_NO_CONCRETE_DEFECT=0` signifie uniquement qu'aucune classification de ce nom ne reçoit de crédit ; il n'affirme pas une absence de défaut. La revue indépendante courante des objets manuels est comptée séparément.

Le contrôle programme préexistant reste structurel (atome déclaré, présence du fichier source), sans prétendre prouver la sémantique de tous les mappings. La population scientifique de ce consommateur reste celle des objets ayant des fichiers `.execution.json`, avec reçus rejetés séparés ; ce n'est pas un inventaire de toutes les assertions de la collection. Le CLI échoue sur faux rattachements, preuves rejetées, doublons, exécutions en échec et revues en attente dans cette portée.

## Vérification exécutée

Les fixtures utilisent le writer NSI canonique et le vrai producteur d'index ; aucun dictionnaire d'index contenant des PASS supposés n'est injecté. Le seul code exécuté est le petit programme temporaire lu par le test (`value = 2`, assertion correspondante). Les revues de fixture sont explicitement synthétiques et ne sont jamais déposées dans le ledger produit.

- Première régression sur le producteur antérieur : **13 échecs, 1 succès**, `/tmp/tnsi-programme-binding-red.log`.
- Renforcement du cas `manual_review` avec vrai code : **2 échecs, 18 succès**, `/tmp/tnsi-programme-binding-additional-red.log` (un cas d'observation du champ manquant et un vrai crédit indu).
- Commande finale : `python -m pytest tests/test_programme_execution_scope.py tests/test_documentary_execution_scope.py tests/test_current_scientific_receipt_binding.py -q --junitxml=/tmp/tnsi-programme-binding-green.xml` : **50 succès**, aucun skip/xfail.
- Ruff sur le producteur et le nouveau fichier de tests ; `git diff --check` : succès.

Mutations : source changée, `.py` changé, méthode changée, reçu documentaire forgé, verdict non autorisé, JSON illisible, double reçu, disposition ID-only, revue documentaire absente, note indépendante changée, échec d'exécution, verdict manuel malgré code, et changement de source/set de reçus/digest de reçu/input de couverture pendant l'observation. Un vrai cas positif de revue actuelle complète et un texte documentaire sans exécution empêchent un gate systématiquement rouge.

Empreintes au test :

```json
{
  "scripts/build_programme_content_validation.py": "sha256:27fb2b6c2ff258c2f040da8bd19d1cf206706fd9433dd0f647a5c2645b53938c",
  "tests/test_programme_execution_scope.py": "sha256:89ab8986f73092a2ceb1e611819bcb340ef2aea3bf9eb555c45c4a523c3b9cda",
  "scripts/scientific_receipt_binding.py": "sha256:1bf80892f2c2719b20ff26b6de0d13e2b2f904f662a4b1051e8add0ef0aff367",
  "scripts/build_current_review_index.py": "sha256:5b1b565c15f782b6f5830b748c2d200ffc1d62fd22e6488dbdd45e79db31fcfd"
}
```

L'artefact suivi `audit/PROGRAMME_CONTENT_VALIDATION.json` n'a pas été régénéré. Les anciens tests qui consomment cet artefact et imposent `>=400` n'ont pas été modifiés ni utilisés comme preuve actuelle. Les agrégateurs release/zero-debt consomment encore ses anciennes clés et doivent être relus avant une capture globale ; aucune clôture release n'est tirée de ce lot.

## Contre-revue indépendante

`/root` a lu le diff fonctionnel intégral, les vingt nouveaux tests et cette note. Les cas positifs utilisent le vrai writer et le vrai index de fixture ; les mutations conservent séparément les preuves d’exécution, les revues documentaires et les approbations humaines. Commande réexécutée : `python -m pytest -q tests/test_programme_execution_scope.py tests/test_documentary_execution_scope.py tests/test_current_scientific_receipt_binding.py --junitxml=/tmp/root-programme-execution-qa1b.xml` : **50 succès**, aucun échec, erreur ou skip. SHA256 du XML : `f281a5d28903510a4ff1834077519cfc0e59c7154249ff1d5f194c7078b91c0e`. Les quatre empreintes ci-dessus ont été vérifiées au moment de cette contre-revue.

Limite dépendante identifiée : le consommateur `build_zero_technical_debt.py` doit classer les compteurs `null` comme dette de preuve, au lieu de tenter `int(None)`. Cette correction distincte est en cours ; aucune capture globale n’est présentée comme valide entre-temps.
