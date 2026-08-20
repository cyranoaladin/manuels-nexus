# PRE-A6 validation du modèle et A6 `context_mismatches` — design approuvé

## Périmètre et condition d’entrée

Le lot part exclusivement du SHA A5
`761508d923d74fd3d93fc055b3f3b1857fb251e1`. PRE-A6 doit expliquer et
fermer les neuf échecs `--validate-model` avant toute correction A6. Si cette
fermeture exige une nouvelle décision humaine, A6 ne démarre pas.

Le lot ne modifie ni la baseline de référence, ni les statuts métier, ni les
89 méthodes `needs_review`, ni leurs packets, ni une signature ou une décision
humaine. Il ne traite aucune autre catégorie active.

## PRE-A6 — neuf qualifications APT

Les neuf échecs ne sont pas neuf décisions manquantes. Ils proviennent du
commit `2c100f0dab1a9cf67fb1a553f5fb501664e68cf7`, qui a renommé exactement neuf
objets 1NSI de l’identité AGT vers APT sans matérialiser leur qualification
historique sous les nouveaux fingerprints. Les neuf couples avant/après sont
bijectifs : même manuel, même chapitre, même catégorie `blocking_statuses`,
même statut et même sémantique de dette. Sept sources sont byte-identiques ;
deux ne diffèrent que par la migration exacte des identifiants AGT vers APT.

Chaque failure est donc classée `ID_MIGRATION_FINGERPRINT_DRIFT`. La
correction mécanique autorisée ne crée ni ne persiste neuf nouvelles
qualifications. Un registre de migrations d’identité exactes référence les
couples ancien/nouveau et leurs seules preuves mécaniques. Son schéma interdit
explicitement tout champ de décision (`qualified`, `approved_by`,
`decision_ref`, `owner`, `disposition`, `qualification_digest`, etc.).
L’analyseur projette en mémoire le
record historique sur le fingerprint courant seulement après validation de la
bijectivité, des hashes sources/transformations et de l’identité des champs de
décision humaine : `approved_by`, `decision_ref`, `baseline_sha`, `owner`,
règle de politique, `qualification_policy_digest` et
`qualification_digest`. L’ancien record reste l’unique qualification
persistée.

Cette opération ne renouvelle pas une qualification, ne change pas son sens et
ne crée aucune approbation. La baseline, le registre de dispositions et les
statuts restent byte-identiques. Le fallback historique global
`ADGK/AGT -> APT` est retiré : il contredisait l’arbitrage A4 séparant ADGK et
APT et masquait les neuf défauts dans `fail-on-new`.

Le registre est un contrôle versionné obligatoire : schéma enregistré,
chargement YAML à clés uniques, propriétés additionnelles interdites,
`control_digest`, chargement depuis le dépôt cible et inclusion dans
`source_digest`/l’identité du modèle. Une mutation rend donc les artefacts
stale. Une migration est rejetée si l’ancien fingerprint n’est pas qualifié et
présent dans la baseline, si la cible possède déjà sa propre disposition ou si
le moindre invariant mécanique ou humain diverge.
Les preuves individuelles sont scellées dans
`audit/PRE_A6_VALIDATE_MODEL_FORENSICS.{json,md}`.

## Sémantique `correction` entre A0 et A5

A0 et A5 concernent tous deux la valeur brute `% META.type_objet`, appelée
historiquement `source_type` dans une partie de l’analyseur. A0 acceptait
`correction` dans le consommateur de relations exercice/corrigé ; il n’en
faisait pas un type canonique. A5 conserve la valeur brute et la normalise par
l’alias exact, déprécié et contextuel `correction -> corrige`.

Il s’agit donc de la même dimension sémantique, mais de deux responsabilités
compatibles : consommation d’une relation en A0, classification canonique en
A5. Le vrai rôle source reste une dimension orthogonale, ici
`production_object`. Un test d’intégration empêchera désormais de confondre
`type_objet`, type canonique et `source_role`.

## A6 — arbitrage des trois contextes

Après PRE-A6 vert, l’inventaire frais doit encore mesurer exactement trois
`context_mismatches`. Les trois objets se trouvent physiquement sous
`TCOMPL-CALCULS-AIRES` tout en déclarant `TSPE-DERIVATION-CONVEXITE`.

L’autorité ne conclut pas à trois en-têtes TCOMPL erronés :

- les contrats affectent primitives/intégrales/aires à TCOMPL et
  dérivation/convexité à TSPE ;
- le corps des trois sources est intégralement TSPE ;
- deux sources conservent des identifiants internes `TSPE-DERCONV-*` ;
- chaque source possède déjà un jumeau canonique exact sous le chapitre TSPE,
  dont elle ne diffère que par le seul `META.id` ;
- les capacités TCOMPL actuellement résolues ne le sont que par leur mauvais
  emplacement physique ;
- aucune référence entrante, review ou liaison SHA ne dépend des trois copies.

Les trois cas sont donc `PATH_CONTEXT_DRIFT`. La correction minimale est la
suppression exacte des trois copies redondantes TCOMPL. Elle ne déplace, ne
retagge et ne modifie aucun contenu canonique TSPE. Les jumeaux TSPE restent
inchangés.

Cette suppression retire légitimement une section de cours et deux TD du
chapitre TCOMPL. Une éventuelle lacune pédagogique TCOMPL révélée demeure une
dette distincte ; A6 ne la masque pas par une reclassification.
`sections_cours -1` et `td -2` sont les seuls changements de modèle attendus.
Toute nouvelle anomalie primaire, tout fingerprint ajouté/reclassifié ou
`NEW_UNQUALIFIED>0` impose STOP au lieu d’une simple explication.

## Détection fail-closed

Les tests A6 utilisent les dimensions déjà autoritaires, sans inventer de
champs META `manual` ou `variant` :

- une revendication de chapitre erronée reste bloquante ;
- le manuel est dérivé du contrat et du préfixe de chapitre, pas d’un nouveau
  champ ad hoc ;
- une variante interdite est détectée par l’ontologie et l’assemblage déclaré ;
- une archive rendue atteignable en production reste bloquante ;
- aucun rapprochement de basename, edit-distance ou fuzzy matching ne peut
  établir un jumeau canonique.

Le cas réel de copie exacte est distingué du simple mauvais en-tête par une
preuve d’identité de contenu et un jumeau canonique exact. Sans cette preuve,
l’analyseur reste fermé et n’infère aucune action destructive.

## Reviews, inventaire et builds

Les neuf qualifications PRE-A6 n’affectent aucun packet de méthode. Les trois
copies A6 ne possèdent aucun packet ou receipt lié à leur SHA. Un scan explicite
doit néanmoins conserver les 89 bindings de méthodes frais et
`NEW_UNQUALIFIED=0`.

Après les commits de modèle/source, le manifeste canonique vide est rafraîchi
avec `build_manifest.py --refresh-empty`, puis les sorties d’inventaire sont
régénérées. Le delta A6 attendu retire exactement les trois fingerprints
`context_mismatches`; toute autre variation est expliquée, jamais forcée.

Les assemblages affectés sont TCOMPL chapitre `complet`/`parcours1` et manuel
`eleve`/`professeur`. Ces quatre variantes sont reconstruites, complétées par
un smoke NSI représentatif. Les 36 PDF suivis sont hashés avant/après et ne
sont jamais utilisés comme oracle visuel ni écrasés automatiquement.

## Critères de sortie

PRE-A6 exige `--validate-model=0`, sans changement de baseline, statut ou
décision humaine. A6 exige `context_mismatches=0`, `NEW_UNQUALIFIED=0`,
`unclassified_types=0` et les catégories techniques A1–A5 toujours nulles.
Les suites root, Math et NSI, les gates ciblés et les régressions A1–A5 doivent
être verts sans nouveau skip/xfail. Deux clones frais au même SHA doivent
produire les mêmes inventaires, gates et builds. `release-strict` reste rouge
uniquement pour la dette de publication existante. Le lot s’arrête ensuite.
