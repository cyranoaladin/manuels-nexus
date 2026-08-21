# Release-strict — dettes globales de collection

## Contexte

Au SHA `5a4c1da1fb880cf97baced76312cad8cdf821040`, A6 est clos mais
`release-strict` ne projette que les bloqueurs rattachés à un manuel. Les 12
`orphan_files` et les 22 `unattributed_pdfs` sont pourtant qualifiés
`blocking: true` et `release_blocking: true`; comme ils n'ont pas de manuel,
ils n'apparaissent dans aucune des 65 raisons release.

Ce lot corrige uniquement la projection du gate. Il ne modifie ni les
anomalies, ni leurs fingerprints, ni les qualifications, ni les statuts, ni
la baseline.

## Cause racine

Deux filtres historiques précèdent aujourd'hui la politique de qualification :

1. `BLOCKING_ANOMALY_CATEGORIES` agit comme une allowlist de catégories ;
2. `_manual_blockers` écarte toute anomalie pour laquelle
   `_anomaly_manual(...)` retourne `None`.

La première autorité est obsolète :
`audit/BASELINE_QUALIFICATION_POLICY.yaml` est désormais l'autorité qui
détermine si un fingerprint bloque la release. La seconde confond absence de
manuel avec absence de dette release.

## Décisions

### Autorité de blocage

Pour toute anomalie active, la vue
`inventory.anomaly_qualifications[fingerprint].blocking` est l'unique autorité
de blocage release.

- `blocking is False` est la seule exemption ;
- qualification absente, non-mapping, ou valeur `blocking` mal typée :
  blocage fail-closed ;
- aucune liste de catégories ne peut court-circuiter cette décision ;
- `BLOCKING_ANOMALY_CATEGORIES` peut subsister pour ses anciens contrôles de
  corpus, mais ne participe plus à une décision release.

### Partition de portée

Chaque anomalie bloquante appartient à exactement une portée :

- `_anomaly_manual(anomaly)` est un manuel canonique : raison portée manuel ;
- `_anomaly_manual(anomaly) is None` : raison portée `COLLECTION`.

Aucune inférence supplémentaire par basename ou préfixe flou n'est ajoutée.
Une anomalie globale dont le nom contient `1SPE` reste globale si les champs
canoniques ne permettent pas de l'attribuer.

### Raisons globales

Les anomalies globales sont agrégées par catégorie et triées. Le format
stable est :

```text
COLLECTION:anomalie:<category>:anomalies.<category>:<count>
```

Une catégorie contenant à la fois une anomalie manuelle et une anomalie
globale produit deux raisons exclusives, chacune avec son propre compte.

### Matrice de livrables

Les bloqueurs manuels et `_chapter_publication_eligible` parcourent toutes les
catégories et utilisent la même vue de qualification. La projection de claim
`_calculate_claim(..., "completude")`, qui délègue à cette fonction pour une
portée chapitre, est couverte par le même contrat. `publication_eligible`
exige désormais aussi `not blockers`, afin qu'un bloqueur release non
structurel ne puisse jamais coexister avec une éligibilité vraie.

Toute anomalie release-bloquante est une dette de structure du modèle de
publication. `phase0_structural_eligible` est donc faux dès qu'un blocker
`anomalie:*` existe pour le manuel. La dimension `structure` de
`release-strict` est également rouge lorsqu'une dette `COLLECTION` existe.

### Frontières

Ce lot ne :

- classe, déplace, remplace ou supprime aucun PDF ou fichier orphelin ;
- ne crée aucune qualification ;
- ne modifie aucune politique, disposition, baseline ou valeur de statut ;
- ne rend pas la release verte ;
- ne commence pas la décision de gouvernance sur
  `MANUELS_PDF_PUBLICATION/`.

## Delta attendu au dépôt courant

L'inventaire reste strictement inchangé : RAW `2308`, fingerprints et digests
identiques. `release-strict` ajoute exactement :

```text
COLLECTION:anomalie:orphan_files:anomalies.orphan_files:12
COLLECTION:anomalie:unattributed_pdfs:anomalies.unattributed_pdfs:22
```

Le compte passe de 65 à 67 raisons. RAW, fingerprints et digests
source/modèle restent inchangés, mais la provenance dérivée change
nécessairement : nouveau `head_sha`, nouveau hash de
`scripts/inventory_collection.py` dans `generator_files` et nouveau
`generator_sha256`. Avec la liste triée sérialisée par JSON compact UTF-8, le
digest attendu est :

```text
sha256:3927508fb5df28b546c997df19d24c4f8ab090b0adc52119751f573e5e5b4c3d
```

## Matrice de tests

1. `orphan_files` global qualifié bloquant : raison `COLLECTION`, structure
   rouge.
2. PDF global dont le basename contient un manuel : aucune attribution floue.
3. Catégorie connue absente de l'ancienne allowlist : elle bloque selon sa
   qualification.
4. Catégorie future arbitraire qualifiée bloquante : elle bloque.
5. Qualification absente, `None`, non-mapping ou `blocking` non booléen :
   blocage fail-closed. Les valeurs trompeuses `0`, `""`, `"false"`, `[]`,
   `{}` et `None` sont toutes exercées ; seule la valeur booléenne exacte
   `False` exempte.
6. `blocking: false` exact : aucune raison release.
7. Même catégorie, une anomalie manuelle et une globale : comptes `1` et `1`,
   aucun double comptage.
8. Déplacement du champ manuel : la portée change, le nombre d'occurrences est
   conservé.
9. Ordre des anomalies inversé : sortie byte-identique, raison agrégée unique.
10. Bloqueur manuel release non structurel synthétique :
    le fixture rend d'abord tous les autres critères vrais et prouve
    `publication_eligible is True`; l'ajout du seul blocker le fait passer à
    `False`. Ce test ne peut donc pas réussir seulement parce que les six
    dimensions de `PUBLICATION_GATE_TEMPLATE` valent normalement `False`.
11. Catégorie future bloquante sur un chapitre :
    `_chapter_publication_eligible` et le claim `completude` sont faux.
12. Dépôt réel : exactement deux raisons nouvelles, inventaire et
    qualifications inchangés.

## Critère de fermeture

Les tests ciblés, les régressions release/deliverable, `validate-model` et
`fail-on-new` sont verts. `release-strict` reste rouge, avec exactement 67
raisons et le digest attendu. L'arbre est propre après les commits atomiques.
