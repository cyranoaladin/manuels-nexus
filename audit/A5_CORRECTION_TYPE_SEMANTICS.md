# A5 — sémantique de `correction`, `corrige` et `source_role`

## Conclusion

- **field concerned by A0** = `% META.type_objet`, projeté sous le nom interne
  historique `source_type` par le consommateur de liens exercice/corrigé ;
- **field concerned by A5** = le même `% META.type_objet`, lu par le
  classifieur de l'ontologie canonique ;
- **same semantic dimension** = **YES** ;
- **conflict** = **NO**.

A0 et A5 portent donc sur la même dimension sémantique, mais sur deux
responsabilités compatibles. A0 reconnaît une valeur brute dans le graphe de
relations ; A5 décide son interprétation taxonomique canonique, avec des
contraintes de contexte fail-closed.

## Les trois notions à ne pas confondre

### `SOURCE_TYPE_CORRECTION`

`SOURCE_TYPE_CORRECTION` désigne ici l'observation brute
`META.type_objet=correction`. Le nom `source_type` est un nom de variable
historique dans `scripts/inventory_collection.py` ; il ne désigne pas le rôle
de confiance du fichier. L'inventaire conserve cette valeur brute dans
`object.source_type`, notamment pour la traçabilité et pour le consommateur de
liens exercice/corrigé introduit en A0.

En A0, le support de `correction` signifiait seulement que ce consommateur
acceptait la valeur brute aux côtés de `corrige`, `corrige_evaluation` et
`evaluation_corrige`. Il ne déclarait pas `correction` comme type canonique
autonome.

### `OBJECT_TYPE_CORRECTION`

`OBJECT_TYPE_CORRECTION` est l'entrée d'alias exacte, dépréciée et
contextuelle de l'ontologie A5 :

```text
correction -> corrige
```

Cette résolution n'est autorisée que dans la section `corriges`, avec le rôle
source `production_object` et sans sous-type. Il n'existe ni correspondance
floue, ni acceptation de valeurs ressemblantes, ni conversion générique d'un
type inconnu.

### `OBJECT_TYPE_CORRIGE`

`OBJECT_TYPE_CORRIGE` est le type pédagogique canonique. Sa représentation
canonique est `META.type_objet=corrige`, sa catégorie d'inventaire est
`corriges`, et son comportement d'assemblage protège la séparation entre
versions élève et professeur.

La normalisation A5 conserve `META.type_objet=correction` comme valeur brute
observée et produit `corrige` comme cible sémantique canonique. Elle n'efface
donc pas la provenance historique et ne contredit pas A0.

## Dimension orthogonale : `source_role`

Le vrai rôle source est attribué indépendamment par `audit/SOURCE_ROLES.yaml`.
Pour les objets pédagogiques de production concernés ici, il vaut
`production_object`. Il répond à la question « quel niveau de confiance et de
participation au modèle possède ce fichier ? », alors que `type_objet` répond
à la question « quel objet pédagogique ce fichier représente-t-il ? ».

Ainsi :

- `type_objet=correction` avec `source_role=production_object` peut se résoudre
  vers le type canonique `corrige` dans la section autorisée ;
- `source_role=correction` est invalide et ne peut pas remplacer un type
  d'objet ;
- `type_objet=production_object` est inconnu et ne peut pas remplacer un rôle
  source.

## Preuve de non-régression

Le test d'intégration
`test_correction_raw_type_alias_and_source_role_remain_orthogonal` construit
deux couples exercice/corrigé réels, l'un avec la valeur brute `correction`,
l'autre avec le type canonique `corrige`. Il vérifie simultanément :

1. la conservation des deux valeurs brutes dans les objets inventoriés ;
2. leur convergence non ambiguë vers `corrige` et le compteur `corriges` ;
3. leur rôle source indépendant `production_object` ;
4. la résolution réelle des deux liens de correction ;
5. le rejet d'une permutation entre type d'objet et rôle source ;
6. la détection de la régression lorsque l'alias est retiré de l'ontologie de
   la fixture : seule la valeur brute `correction` devient alors
   `unclassified_types`, tandis que son lien A0 reste résolu et que `corrige`
   reste canonique.

Cette mutation démontre que le test dépend bien du classifieur de production
et non d'une allowlist locale ou d'une assertion tautologique.
