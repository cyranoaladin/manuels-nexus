<!-- AUTO-GENÉRÉ PAR inventory_collection.py -->
# Baseline d’anomalies — état provisoire

Cette baseline est volontairement `provisional: true`. Elle ne constitue ni un
gel de dette, ni une preuve de qualité, et ne peut pas rendre `--fail-on-new`
vert.

| Champ | Valeur |
|---|---|
| Fingerprint | version 1 |
| HEAD observé | `4be55db74e1b916f0a815c3f726c14657d2e1df3` |
| Empreinte précédente | aucune |
| Nouvelle empreinte | `sha256:0152049cee17b72ad05a5b31e046bb4e35d80467dd82109d80bbe4328ef634be` |
| Anomalies actives qualifiées enregistrées | 4 |
| Anomalies actives non qualifiées exclues du registre actif | 2 457 |
| Fingerprints résolus | 0 |

Les quatre entrées actives proviennent de décisions humaines versionnées :
trois réutilisations intentionnelles de la maquette v5 et la dépendance générée
`renvois.tex`. Aucune qualification n’a été inventée pour les 2 457 autres
fingerprints.

## État des dix préconditions

| Check `baseline_ready` | État observé | Preuve ou blocage |
|---|---|---|
| `phase0_tests` | vert | `357 passed` le 30 juillet 2026 |
| `artifact_schemas` | vert ciblé | schéma baseline et contrôles JSON/YAML validés |
| `renderers` | rouge transitoire | artefacts gérés à régénérer après le commit du générateur |
| `object_counts` | vert ciblé | cohérence couverte par la suite Phase 0 |
| `harvest_candidates` | vert ciblé | 19 candidats classés `harvest_candidate` |
| `generated_renvois` | vert | rôle et preuve humaine versionnée |
| `intentional_reuse_decisions` | vert | trois objets, preuve et décision Git |
| `disposition_coverage` | rouge | 2 457 fingerprints actifs sans qualification complète |
| `fingerprint_determinism` | vert ciblé | stabilité et mutations contractuelles testées |
| `validate_model` | rouge transitoire | artefacts gérés encore alignés sur le générateur précédent |

La commande `--update-baseline` n’a pas été exécutée depuis le worktree sale.
Le futur gel définitif devra partir d’un commit propre, recalculer ces dix checks
et produire une transition auditée avec raison et approbateur humains.
