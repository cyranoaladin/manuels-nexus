# A5 `unclassified_types` — design approuvé

## Périmètre

A5 élimine exclusivement les 660 anomalies `unclassified_types` mesurées au
SHA source A4 `535d623703cb3d36ee66849fbd05e3fa0c18a31d`. Il ne modifie aucun
objet éditorial, statut, packet de revue, PDF de référence ou baseline.

Le snapshot frais établit trois valeurs réelles :

- `correction` : 653 ;
- `algorithme` : 3 ;
- `experimentation` : 4.

Les anciennes hypothèses `activite`, `methode_guidee` et `auto_evaluation`
ont zéro occurrence active. A5 ne décide pas définitivement de leur éventuelle
canonicité : elles restent inchangées, non reconnues et hors périmètre tant
qu’une autorité adaptée n’a pas levé leur ambiguïté.

## Autorité et dimensions

Une ontologie versionnée unique, `audit/CANONICAL_OBJECT_TYPE_ONTOLOGY.yaml`,
devient l’autorité exécutable de `% META.type_objet`. Sa documentation humaine
est `audit/CANONICAL_OBJECT_TYPE_ONTOLOGY.md` et son enveloppe est validée par
un schéma JSON versionné.

L’ontologie sépare :

- type pédagogique canonique ;
- alias historique exact ;
- sous-type ;
- section documentaire ;
- rôle source ;
- rôle/variante d’assemblage.

Les schémas `chunk_type` décrivent une dimension d’ingestion distincte. Ils
peuvent corroborer une décision, jamais gouverner `% META.type_objet`.

## Décisions des trois clusters

### `correction`

`correction` est un alias historique exact et déprécié de `corrige`. Il est
accepté uniquement en rôle `production_object`, sous la section `corriges`,
sans sous-type. La convergence ne fait perdre aucune information : 653/653
occurrences satisfont ces contraintes et 1386 pairs canoniques `corrige`
existent déjà. Les 653 sources restent byte-identiques.

### `algorithme`

`algorithme` est un type pédagogique canonique autonome. Il compte dans
`sections_cours` et n’est accepté qu’en rôle `production_object`, sous la
section `cours`, sans sous-type. L’assembleur Math le prend déjà explicitement
en charge.

### `experimentation`

`experimentation` est un type pédagogique canonique autonome de simulation et
statistiques. Il suit les mêmes contraintes techniques qu’`algorithme` et
compte dans `sections_cours`. L’assembleur le prend déjà en charge.

## Comportement fail-closed

L’analyseur charge et valide l’ontologie versionnée. Il résout uniquement les
alias déclarés, sans fuzzy matching et sans fallback générique. Un type inconnu,
une faute, un alias ambigu, une mauvaise section, un mauvais rôle ou un
sous-type interdit reste non classé. L’analyseur conserve la priorité des
sous-types existants pour les valeurs non concernées par A5.

## Tests

Les tests couvrent :

- types canoniques acceptés ;
- alias `correction -> corrige` accepté dans son contexte exact ;
- convergence légitime de plusieurs alias explicites ;
- alias ambigu rejeté ;
- faute et type inconnu rejetés ;
- mauvaise section, mauvais rôle et sous-type interdit rejetés ;
- intégration `build_inventory` des trois clusters ;
- invariant dépôt `unclassified_types=0` ;
- absence d’acceptation des trois anciennes hypothèses.

## Gouvernance et builds

Le manifeste de builds A4 est canoniquement vide. Après le commit du modèle,
`build_manifest.py --refresh-empty` rafraîchit seulement son enveloppe ; aucun
ancien build n’est rebaptisé et aucune preuve n’est forgée. Les douze PDF suivis
restent byte-identiques à la preuve A4. Des smoke builds Math et NSI sont joués
sans `--record-observed`.

Les 89 méthodes et leurs packets ne sont pas modifiés. Un scan explicite
vérifie `sha256(source) == disposition.method_source_sha ==
packet.source_sha256` et le digest du packet.

`release-strict` reste rouge pour les dettes de publication. Les neuf échecs
`validate-model` liés aux statuts APT sont préexistants et hors A5 ; ils sont
rapportés sans qualification ni promotion. `fail-on-new` doit rester vert avec
`NEW_UNQUALIFIED=0`.

## Ledger attendu

Le dry-run source est vide et doit rester exact :

```text
expected source changes = 0
actual source changes   = 0
analyzer/schema         = 660
structured migration    = 0
invalid source fixes    = 0
legacy aliases          = 653
other explicit types    = 7
```

Les 660 suppressions sont réalisées en trois clusters atomiques : 653 alias
`correction`, 3 types `algorithme`, puis 4 types `experimentation`.

## Critère de sortie

A5 est clos lorsque `unclassified_types=0`, les compteurs techniques exigés
restent nuls, les tests globaux n’ont aucun échec/skip/xfail nouveau, les smokes
sont reproductibles, et deux clones frais au même SHA produisent les mêmes
résultats. Aucun lot suivant n’est commencé.
