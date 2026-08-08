# Gouvernance des 981 qualifications de dette - Conception

**Date :** 8 août 2026
**Branche :** `finalisation/collection-v1`
**Référence observée :** `a48e8e41fc3f6ef9274e564722d5155c8df401b7`
**Décideur humain :** Alaeddine Ben Rhouma
**Lane :** gouvernance de release

## 1. Objectif

Qualifier les 981 empreintes actuellement non gouvernées comme dette ouverte et
bloquante afin que les gates distinguent :

- la régression de dette, contrôlée par `--fail-on-new` ;
- la publiabilité réelle, contrôlée par `--release-strict`.

Cette qualification rend la dette traçable. Elle ne valide ni l'exactitude du
contenu, ni sa conformité au programme, ni sa qualité pédagogique, ni son
aptitude à la publication.

## 2. Hors périmètre

Cette passe ne doit pas :

- corriger ou approuver un objet pédagogique ;
- modifier les sources des manuels, notamment TNSI ;
- déclarer un manuel complet ou publiable ;
- transformer une anomalie en `accepted_exception`, `false_positive` ou `fixed` ;
- réduire, ignorer ou contourner `--release-strict` ;
- supprimer ou réécrire les dispositions historiques ;
- ouvrir le raccordement du mode livre TNSI avant le périmètre réel 12/12.

## 3. Lot observé et immuable

Le lot a été calculé depuis l'inventaire canonique au commit de référence. Son
contrat est :

- nombre d'empreintes : `981` ;
- empreinte du lot :
  `sha256:e2ec8130f85f690eda663ac556b61e63ffd7d98e422c71f0245b10112161887f` ;
- empreinte des sources :
  `sha256:590c51801b32a6661878de7956d1752b9f027bf2cd65ba2605e8120b682d91d3` ;
- empreinte du modèle :
  `sha256:8db8abe9a2882c827f4aee55f7584f082f1ea7f31647783e7f52697443055d22`.

Ventilation par catégorie :

| Catégorie | Nombre |
|---|---:|
| `blocking_statuses` | 875 |
| `unassembled_objects` | 82 |
| `chapters_not_in_manual` | 15 |
| `broken_meta_references` | 2 |
| `unclassified_types` | 7 |
| **Total** | **981** |

Les neuf nouveaux compagnons de correction 1NSI sont inclus dans les 82 objets
non assemblés. Leur qualification comme dette ne remet pas en cause la
séparation élève/professeur validée lors de la passe précédente.

La politique ne contractualise pas une ventilation par manuel : le champ brut
`manual` et l'inférence depuis les chemins n'ont pas la même sémantique. Le
contrat machine porte sur les empreintes, les catégories et les propriétaires.

Toute dérive du nombre, de l'empreinte ou de ces ventilations contractuelles
doit arrêter la matérialisation. Une dérive impose une nouvelle décision
humaine, pas une mise à jour implicite de la politique.

## 4. Décision humaine

Alaeddine Ben Rhouma approuve exclusivement l'enregistrement du lot exact comme
`open_debt`, avec `release_blocking: true`, pour le contrôle de régression.

Après constat de la dérive historique de baseline, Alaeddine Ben Rhouma
approuve également la réconciliation exacte décrite en section 7 : 642
empreintes antérieures absentes de l'inventaire courant sont archivées dans
`resolved`, dont les trois anciennes empreintes des remplacements appariés.
Cette transition préserve les preuves historiques et ne constitue pas une
validation des nouvelles empreintes correspondantes.

L'ancre contractuelle ajoutée au registre sera :

`decision-baseline-debt-extension-collection-2026-08-08`

Le registre doit rappeler explicitement que cette décision :

- n'approuve aucun contenu ;
- ne lève aucun P0 ;
- n'autorise aucune publication ;
- maintient la dette dans le calcul de `--release-strict`.

## 5. Stratégie retenue

Une extension gouvernée unique est retenue plutôt qu'une qualification manuelle
empreinte par empreinte ou plusieurs lots par manuel.

Cette stratégie est préférable parce qu'elle :

- verrouille exactement le jeu observé par des empreintes et des comptes ;
- applique des règles déterministes et auditables ;
- évite 981 décisions manuelles répétitives sans créer d'approbation implicite ;
- conserve une seule chronologie de baseline pour toute la collection ;
- échoue fermement si le jeu source évolue.

## 6. Extension de politique

Les règles existantes classent déjà 967 empreintes. Deux règles terminales sont
ajoutées sans modifier leur résultat :

1. `blocking-scientific-algorithm-experiment`
   - catégorie : `blocking_statuses` ;
   - types d'objet : `algorithme`, `experimentation` ;
   - propriétaire : `direction_scientifique_programme` ;
   - statut : `open_debt` ;
   - blocage release : vrai ;
   - justification : algorithme ou expérimentation scientifique sans statut de
     publication approuvé.
2. `unclassified-source-type`
   - catégorie : `unclassified_types` ;
   - propriétaire : `ingenierie_build_qualite` ;
   - statut : `open_debt` ;
   - blocage release : vrai ;
   - justification : type d'objet non classé dans la taxonomie canonique.

La ventilation attendue après extension est :

| Propriétaire | Nombre |
|---|---:|
| `direction_scientifique_programme` | 752 |
| `direction_editoriale_pedagogique` | 98 |
| `ingenierie_build_qualite` | 131 |
| **Total** | **981** |

La politique continue d'interdire les statuts d'acceptation ou de clôture pour
ce lot. `release_acceptance` reste faux.

## 7. Réconciliation de baseline

La baseline contient 2 647 empreintes actives alors que l'inventaire courant en
contient 2 986. La transition exacte est :

| Transition | Nombre |
|---|---:|
| Empreintes actives conservées | 2 005 |
| Empreintes ajoutées, jeu approuvé | 981 |
| Empreintes antérieures archivées dans `resolved` | 642 |
| Empreintes actives après transition | 2 986 |

Le jeu des 642 empreintes archivées est verrouillé par :

- empreinte du jeu :
  `sha256:44397de4c98d70ce3575c04ea37322a403a29a3468bd29a23bffc938ed4908fc` ;
- catégories :
  - `blocking_statuses`: 3 ;
  - `broken_meta_references`: 24 ;
  - `chapters_not_in_manual`: 3 ;
  - `missing_assemblers`: 1 ;
  - `unassembled_objects`: 611.

Trois transitions sont des remplacements appariés par leur locator stable :

| Ancienne empreinte | Nouvelle empreinte |
|---|---|
| `9873ab6a1e11c673` | `3276d95a8a9b8142` |
| `63548ddb4dd6b1dd` | `d51832bdeebf5d4a` |
| `8fdec12020b7159b` | `a96d99c614321acc` |

L'empreinte canonique de ces trois paires est
`sha256:eaa22aa607e9a9616f251cee24e8b639e9c958c639aac353b13fd01e18836dd1`.
Les trois nouvelles empreintes appartiennent au jeu approuvé des 981 et restent
`open_debt`, bloquantes. Les trois anciennes appartiennent au jeu des 642 et
sont conservées comme historique résolu.

La politique et son schéma doivent porter ce contrat de transition. Le mode
d'extension approuvée doit refuser :

- une empreinte ajoutée hors des 981 ;
- une empreinte archivée hors des 642 ;
- une paire modifiée différente des trois paires approuvées ;
- une régression depuis l'historique résolu ;
- une modification d'une empreinte conservée ;
- un ajout qui ne serait pas `open_debt` et bloquant.

Le contrat machine est stocké dans un objet `approved_transition` de la
politique avec les comptes avant/après, le compte et l'empreinte du jeu résolu,
sa ventilation par catégorie, les trois paires ordonnées et leur empreinte. Le
schéma `baseline-qualification-policy.schema.json` rend tous ces champs
obligatoires pour cette décision et en verrouille les valeurs approuvées.

## 8. Flux de données

La migration suit quatre états séparés et auditables :

1. **Décision, schéma et politique** : le registre, le schéma contractuel, la
   politique et les tests figent le lot et la réconciliation de baseline. Les
   anciennes dispositions restent intactes.
2. **Matérialisation** : le générateur ajoute les 981 dispositions `open_debt`
   et produit un rapport d'anomalies non qualifiées vide.
3. **Extension et réconciliation de baseline** : depuis un arbre propre, la
   commande approuvée ajoute exactement les 981 empreintes, archive exactement
   les 642 empreintes antérieures et régénère les rapports de décision.
4. **Inventaire canonique** : les six rapports canoniques sont régénérés si leur
   contenu dérive après la qualification.

Le changement d'empreinte de contrôle de la politique ne doit pas réécrire les
entrées antérieures : elles sont conservées comme preuves historiques
normalisées. Le nouveau jeu approuvé doit être exactement le jeu non qualifié au
commit de référence.

## 9. Atomicité des commits

Les changements seront séparés ainsi :

1. décision, schéma, politique, garde de réconciliation et tests du contrat ;
2. dispositions et rapports de matérialisation ;
3. baseline et rapports d'extension/réconciliation approuvée ;
4. rapports canoniques régénérés, seulement s'ils changent.

Une étape ne peut commencer que lorsque la précédente est vérifiée et commise.
La commande d'extension de baseline exige notamment un arbre Git propre.

## 10. Tests et gates

Les tests de régression doivent prouver :

- l'échec avant ajout des deux règles manquantes ;
- le classement déterministe des 14 cas auparavant sans règle ;
- le contrat exact des 981 empreintes, catégories et propriétaires ;
- le maintien de `open_debt` et `release_blocking: true` pour chaque entrée ;
- l'absence de suppression ou de modification historique hors de la transition
  approuvée ;
- la réconciliation exacte des 642 empreintes et des trois remplacements ;
- le refus de toute résolution, paire ou addition hors du contrat ;
- l'échec fermé en cas de dérive du jeu approuvé ;
- l'idempotence de la matérialisation et de la baseline.

État attendu en fin de passe :

- `--validate-model` : vert ;
- `--fail-on-new` : vert ;
- `--release-strict` : rouge, car la dette reste bloquante ;
- tests ciblés de qualification et d'inventaire : verts ;
- aucune source TNSI modifiée.

## 11. Critères d'acceptation

La passe est terminée uniquement si :

- les 981 empreintes exactes sont gouvernées et présentes dans la baseline ;
- aucune empreinte non approuvée n'est ajoutée ;
- les 642 empreintes antérieures exactes sont conservées dans `resolved` ;
- les trois remplacements exacts sont traçables dans le rapport de transition ;
- toutes les dispositions du lot sont ouvertes et bloquantes ;
- les rapports générés concordent avec les sources et la politique ;
- la régénération est idempotente ;
- les gates de modèle et de régression sont verts ;
- le gate de release reste rouge pour des raisons de contenu réelles ;
- le diff ne touche aucune source de manuel TNSI.
