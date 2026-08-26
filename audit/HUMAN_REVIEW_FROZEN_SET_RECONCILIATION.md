# Réconciliation de l'ensemble gelé — 1SPE-SUITES

**Statut : `SUPERSEDED_ROOT_CAUSE_FOUND`.** Remplacé par
`audit/1SPE_SUITES_REVIEW_FREEZE_CORRECTION_DECISION.md`.

> **Correction.** L'hypothèse « 161 = 156 + les 5 fiches `FR-R`, donc double
> comptage » consignée plus bas est **fausse**. La comparaison des objets Git
> entre `761508d9` et `c667f12b` montre **0 doublon aux deux commits** : 161 est
> le compte du même chapitre à `c667f12b`, qui ajoute la capacité **C8** et les
> cinq objets qui l'implémentent (`CR-017`, `ME-008`, `EX-051`, `CO-051`,
> `RE-C8`). Les tableaux ci-dessous sont conservés tels quels comme trace de
> l'analyse initiale.

La section 2 de la décision humaine du 2026-08-26 déclare l'ensemble gelé de
`1SPE-SUITES` comme suit :

```
object_count       = 161
object_set_digest  = sha256:67d8006298299b44029de8ba8f85b500d9b3619997a0c596e63c20e1cffeee2d
```

Ni la valeur ni le digest ne sont reproductibles à partir du dépôt au commit
`761508d9`. Le digest déclaré n'apparaît dans aucun artefact du dépôt et aucun
algorithme d'énumération documenté ne produit 161 objets.

## Ce que la machine énumère réellement

Règle appliquée par `scripts/human_review_governance.py` : *un objet publishable
= exactement un bloc `% META` dans un répertoire éditorial déclaré par
l'assembleur du manuel, y compris les objets insérés transitivement par
`\input` depuis un objet de premier niveau*. L'ordre d'assemblage et la
visibilité élève/professeur sont repris de l'assembleur réel
(`assemble_manuel.collect_chapter`), ce qu'un test vérifie objet par objet.
`1SPE-SUITES` ne porte aucun objet imbriqué : ses 156 objets sont tous de
premier niveau.

```
object_count              = 156
object_set_digest         = sha256:9d9ab4b6f290c1629c3b77f79a8b73c7c6af751f7b0483630392ceecc0c569f7
semantic_review_digest    = sha256:9b7e3fceb0b8a0f004dfdf08940055af66ea1a898410a94a3e8a8ea95cb0cd37
programme_authority_digest= sha256:172cd283ef2404b2957f7042a2a0dcd33bd2996968ee8b8619a8ef18888e4840
repository_source_sha     = 761508d923d74fd3d93fc055b3f3b1857fb251e1
```

| Type d'objet | Nombre |
|---|---:|
| `exercice` | 50 |
| `corrige` | 50 |
| `coup_de_pouce` | 21 |
| `remediation` | 12 (7 `RE-C*` + 5 `FR-R*`) |
| `cours` | 11 |
| `methode` | 7 |
| `evaluation` | 2 |
| `corrige_evaluation` | 2 |
| `qcm` | 1 |
| **Total** | **156** |

Visibilité : 104 objets dans la variante élève, 156 dans la variante professeur,
0 objet non assemblé. Le QCM porte 21 questions.

## Hypothèses examinées pour l'écart de 5

| Hypothèse | Valeur | Verdict |
|---|---:|---|
| `objects_total` de `audit/CHAPTER_READINESS_1SPE_SUITES.json` | 155 | rejetée — c'est 156 moins l'objet `qcm` |
| 156 objets META + les 5 fiches `FR-R1..FR-R5` | 161 | rejetée — les 5 fiches portent déjà un `% META` et sont déjà comptées dans les 12 objets `remediation` ; les recompter serait un double comptage |
| 156 objets META + `contrat.yaml` + QCM JSON + `dossier_curation.json` | 159 | rejetée — ces fichiers entrent dans le digest sémantique comme sources de chapitre, pas comme membres de l'*object set* |
| 156 objets META − l'objet `qcm` + les 21 questions | 176 | rejetée |

L'hypothèse « 161 = 156 + les 5 `FR-R*` » est la seule qui tombe juste
numériquement, et c'est précisément celle qu'un double comptage explique. Elle
n'est donc pas retenue comme reconstruction : la machine ne fabrique pas une
concordance.

## Effet contractuel

Tant que ce point n'est pas tranché :

- aucun reviewer n'est assigné sur `1SPE-SUITES` ;
- aucun reçu ne peut être enregistré — un test le verrouille
  (`test_no_receipt_may_be_recorded_while_the_frozen_set_is_unreconciled`) ;
- aucun statut d'objet n'est promu ;
- les packets A et B émis portent l'ensemble machine de 156 objets et sont
  marqués `PENDING_UNASSIGNED`.

## Décision attendue de l'humain

1. **Soit** confirmer que l'ensemble gelé contractuel est l'ensemble machine de
   156 objets, digest `sha256:9d9ab4b6…`, et corriger les valeurs de la
   section 2 de la décision.
2. **Soit** fournir l'algorithme d'énumération qui produit 161 objets et le
   digest `sha256:67d80062…`, afin que la machine le reproduise et le verrouille
   par un test.
