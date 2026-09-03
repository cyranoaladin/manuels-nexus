# Assignation et instructions de revue — manuel 1SPE

> **Cette vue est derivee et sans autorite. L'autorite machine reste le packet JSON canonique.**

Ce document est commun aux dix chapitres et aux deux roles. Il ne nomme personne : les noms humains seront renseignes a l'assignation.

## 1. Ce qui est decide, et par qui

- L'unite de decision est le CHAPITRE : 10 chapitres x 2 roles = 20 verdicts, pas des centaines de signatures objet par objet.
- rappel porte par chacune des vingt vues : « Aucun humain n'a encore approuve ce chapitre : REVIEW_DELTA_BASELINE = NONE. Le perimetre de revue est le CHAPITRE COURANT ENTIER. Les listes ci-dessous dirigent l'attention, elles ne reduisent pas le perimetre. »
- CONTENT_APPROVAL_BINDS_TO = SEMANTIC_DIGEST : l'approbation porte sur l'empreinte semantique du chapitre, rappelee en tete de chaque vue ; l'approbation graphique releve de la porte D7, independante.
- Les deux roles sont independants. Un role ne conclut pas pour l'autre.

## 2. Les deux roles

| Packet | Role | Objet du jugement |
| --- | --- | --- |
| A | `EXPERT_MATHEMATIQUE` | exactitude scientifique du contenu |
| B | `EXPERT_PROGRAMME_PEDAGOGIE` | conformite au programme et qualite pedagogique |

## 3. Modele d'assignation

Un enregistrement d'assignation par (chapitre, role). Les champs d'identite restent vides tant qu'aucune personne n'est nommee ; ils sont renseignes hors de cette vue, dans le packet canonique.

```yaml
assignation:
  manuel: 1SPE
  chapitre: <CHAPITRE>            # un identifiant de la liste ci-dessous
  role: <EXPERT_MATHEMATIQUE | EXPERT_PROGRAMME_PEDAGOGIE>
  packet_canonique: audit/reviews/human/<CHAPITRE>/packet-<A|B>-<ROLE>.json
  vue_de_lecture: audit/reviews/human/<CHAPITRE>/view-<A|B>-<ROLE>.md
  empreinte_ensemble_objets: <object_set_digest du packet>
  empreinte_semantique: <semantic_review_digest du packet>
  etat: PENDING_UNASSIGNED       # inchange tant que personne n'est nommee
  assigne_a: null                # renseigne a l'assignation, hors de cette vue
  assigne_le: null
  rendu_le: null
  verdict: null                  # rendu dans le packet canonique, jamais ici
```

## 4. Instructions de revue

1. Lire le chapitre entier dans l'ordre d'assemblage donne par la vue, PDF a l'appui. Le perimetre est le chapitre courant entier.
2. Traiter la checklist de son role, point par point.
3. Utiliser les listes consolidees de la vue pour diriger l'attention : objets de science humaine requise pour le role A, cellules capacite x role et richesse pour le role B. Ces listes ne bornent pas la lecture.
4. Verifier que l'empreinte semantique rappelee par la vue est bien celle du packet : si le contenu du chapitre a change, le dossier est perime et la revue doit repartir du gel courant.
5. Consigner chaque constat avec l'identifiant d'objet concerne et le point de checklist correspondant.
6. Rendre un verdict unique pour le chapitre, dans le packet JSON canonique. Verdicts autorises : `APPROVED` / `CHANGES_REQUESTED` / `REJECTED`.
7. Ne rien approuver sur la base de cette vue seule : elle est derivee.

## 5. Ce qu'une vue ne fait pas

- elle ne porte aucun verdict ;
- elle ne nomme aucun relecteur et ne cree aucun identifiant de relecteur ;
- elle ne reduit aucun perimetre ;
- elle ne reproduit pas les cles declarees des QCM : l'expert etablit la reponse par lui-meme, puis la compare a la source canonique ;
- elle ne remplace jamais le packet JSON canonique.

## 6. Les vingt dossiers

| Chapitre | Vue du role A | Vue du role B |
| --- | --- | --- |
| `1SPE-DERIVATION-GLOBAL` | `audit/reviews/human/1SPE-DERIVATION-GLOBAL/view-A-EXPERT_MATHEMATIQUE.md` | `audit/reviews/human/1SPE-DERIVATION-GLOBAL/view-B-EXPERT_PROGRAMME_PEDAGOGIE.md` |
| `1SPE-DERIVATION-LOCAL` | `audit/reviews/human/1SPE-DERIVATION-LOCAL/view-A-EXPERT_MATHEMATIQUE.md` | `audit/reviews/human/1SPE-DERIVATION-LOCAL/view-B-EXPERT_PROGRAMME_PEDAGOGIE.md` |
| `1SPE-EXPONENTIELLE` | `audit/reviews/human/1SPE-EXPONENTIELLE/view-A-EXPERT_MATHEMATIQUE.md` | `audit/reviews/human/1SPE-EXPONENTIELLE/view-B-EXPERT_PROGRAMME_PEDAGOGIE.md` |
| `1SPE-GEOMETRIE-REPEREE` | `audit/reviews/human/1SPE-GEOMETRIE-REPEREE/view-A-EXPERT_MATHEMATIQUE.md` | `audit/reviews/human/1SPE-GEOMETRIE-REPEREE/view-B-EXPERT_PROGRAMME_PEDAGOGIE.md` |
| `1SPE-PROBA-COND` | `audit/reviews/human/1SPE-PROBA-COND/view-A-EXPERT_MATHEMATIQUE.md` | `audit/reviews/human/1SPE-PROBA-COND/view-B-EXPERT_PROGRAMME_PEDAGOGIE.md` |
| `1SPE-PRODUIT-SCALAIRE` | `audit/reviews/human/1SPE-PRODUIT-SCALAIRE/view-A-EXPERT_MATHEMATIQUE.md` | `audit/reviews/human/1SPE-PRODUIT-SCALAIRE/view-B-EXPERT_PROGRAMME_PEDAGOGIE.md` |
| `1SPE-SECOND-DEGRE` | `audit/reviews/human/1SPE-SECOND-DEGRE/view-A-EXPERT_MATHEMATIQUE.md` | `audit/reviews/human/1SPE-SECOND-DEGRE/view-B-EXPERT_PROGRAMME_PEDAGOGIE.md` |
| `1SPE-SUITES` | `audit/reviews/human/1SPE-SUITES/view-A-EXPERT_MATHEMATIQUE.md` | `audit/reviews/human/1SPE-SUITES/view-B-EXPERT_PROGRAMME_PEDAGOGIE.md` |
| `1SPE-TRIGONOMETRIE` | `audit/reviews/human/1SPE-TRIGONOMETRIE/view-A-EXPERT_MATHEMATIQUE.md` | `audit/reviews/human/1SPE-TRIGONOMETRIE/view-B-EXPERT_PROGRAMME_PEDAGOGIE.md` |
| `1SPE-VARIABLES-ALEATOIRES` | `audit/reviews/human/1SPE-VARIABLES-ALEATOIRES/view-A-EXPERT_MATHEMATIQUE.md` | `audit/reviews/human/1SPE-VARIABLES-ALEATOIRES/view-B-EXPERT_PROGRAMME_PEDAGOGIE.md` |

10 chapitres x 2 roles = 20 verdicts.
