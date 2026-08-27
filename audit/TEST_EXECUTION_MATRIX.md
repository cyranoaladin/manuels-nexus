# Matrice d'execution des tests

`SOURCE_SHA = bdbbb9090f01c6deb2d46354a2cd256a6aa3ee77`

Chaque resultat est lu dans une capture reelle, conservee sous
`audit/test_matrix_logs/`. Aucun code de sortie n'est masque par une pipeline.

| Commande | cwd | Statut | exit | passed | failed | errors | duree |
|---|---|---|---:|---:|---:|---:|---|
| `python -m pytest tests/ -q` | `NSI` | `SUPPORTED_CI` | 0 | 2204 | 0 | 0 | 06:49:40→06:50:59 |
| `python -m pytest tests/test_meta_schemas.py -q` | `Mathematiques/manuel-maths` | `SUPPORTED_CI` | 0 | 4053 | 0 | 0 | 06:50:59→06:51:17 |
| `python -m pytest tests/ -q` | `Mathematiques/manuel-maths` | `SUPPORTED_CANONICAL` | 0 | 4893 | 0 | 0 | 06:51:23→06:59:55 |
| `python -m pytest tests/ -q` | `.` | `SUPPORTED_CANONICAL` | 1 | 1942 | 2 | 0 | 21:08:19→21:40:33 |
| `python -m pytest --import-mode=importlib --cov=scripts` | `.` | `SUPPORTED_CI` | 1 | 9039 | 2 | 0 | 20:19:57→21:05:26 |

**3 / 5 commandes supportees vertes.**

## Une seule cause bloquante

Les deux commandes rouges echouent sur la **meme** cause unique, pas sur des
defauts distincts :

```
STALE freeze binding: audit/official_program_coverage/1SPE.json
```

Detail : `audit/1SPE_SUITES_FREEZE_AUTHORITY_BINDING_CONFLICT.json`. Ce n'est
pas un defaut de test : le gel signale correctement qu'une source d'autorite
qu'il lie a bouge.

## La collision d'imports n'existe plus

| | Avant | Maintenant |
|---|---:|---:|
| umbrella, echecs | 110 | **2** |
| umbrella, erreurs | 63 | **0** |

Les 63 erreurs etaient les suites NSI executees depuis la racine sur l'arbre
perime `761508d9`. Elles n'existent plus sur l'arbre canonique. Aucune
collision entre les modules `assemble` Math et NSI ne subsiste, et l'invocation
umbrella reste `--import-mode=importlib`.

`ambiguous_entrypoints = []` : les cinq commandes sont supportees et
documentees. Une commande lancee depuis un autre repertoire que son `cwd`
declare n'est pas un point d'entree du projet.

## Interruptions d'infrastructure, non comptees comme echecs

| Evenement | Classification | Diagnostic |
|---|---|---|
| `exit code 144` | `INFRA_EXECUTION_INTERRUPTED` | un `pkill -f` visant le motif pytest a aussi tue le shell hote du harnais ; run a 2 %, aucune ligne `FAILED` |
| 12 echecs supplementaires | `INFRA_EXECUTION_INTERRUPTED` | des artefacts ont ete ecrits dans l'arbre pendant l'execution ; `inventory` et `baseline` refusent sur depot sale. Rejoue propre : 16 → 2 |

Les deux logs sont conserves pour forensic, dont
`audit/test_matrix_logs/root_umbrella.dirty-tree.log`.
