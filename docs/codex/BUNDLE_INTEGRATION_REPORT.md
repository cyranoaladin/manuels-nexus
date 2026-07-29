# Rapport d'intégration du cadre Codex

Date de contrôle : 2026-07-29

Branche : `finalisation/collection-v1`

HEAD contrôlé : `20679de69a25d694196a2153f6f4d16fe4c4aa91`

Décision : **accepté avec corrections**

## Fichiers intégrés

| Source logique | Destination | SHA-256 | Contrôle |
|---|---|---|---|
| Instructions projet | `AGENTS.md` | `17bdd4ebabdb94f9a97dd460ad6fff950cca116f37a91bda19d6bfa61db7ec1d` | UTF-8, 6 095 octets |
| Cahier des charges 1SPE | `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md` | `31005df9a4105b4652779b6045333206e98883a58dab41a144f6919c85d2aa7d` | UTF-8, espaces de fin de ligne normalisés |
| Skill qualité | `.agents/skills/nexus-manual-quality/SKILL.md` | `a64cac91e70a09e2247a2e8d489c3a8c5033d394dacee17ad983e4acd54602a8` | front matter YAML valide |
| Règles de commandes | `.codex/rules/manuals.rules` | `7d2a15963ca09f06a0b232e30dea272bd1f9adea34ec89db3214c2db74a32569` | Starlark chargé par `codex execpolicy check` |
| Guide d'installation | `docs/codex/README_INSTALLATION_CODEX.md` | `849bccdc7caa657d90460c6fcfadc2a15d1316ea41a95ab67f657094850d24ee` | UTF-8 |
| Gates qualité | `docs/codex/QUALITY_GATES.md` | `3240ce9f2eb3e2ff1b25d85eb2eaddf0a1e4e11a44fccbf1197dc35c5cedbdb5` | UTF-8 |
| Modèle de registre | `docs/codex/ISSUE_REGISTER_TEMPLATE.md` | `3768d699ef4158bc0f8212c7b5fc797ad3412ce9f55f3935644e48e882cdda93` | UTF-8 |
| Modèle de matrice | `docs/codex/PROGRAMME_2026_MATRIX_TEMPLATE.md` | `3a39360607368c955c327035d84079bed91663e8c79668be61730957dff45cad` | UTF-8 |

Les destinations correspondent aux surfaces natives documentées par Codex :
instructions durables à la racine, skill sous `.agents/skills/` et règles
expérimentales sous `.codex/rules/`.

## Instructions applicables

- `AGENTS.md` est le seul fichier `AGENTS.md` ou `AGENTS.override.md` du dépôt.
- Il s'applique donc à la racine et à tous les fichiers actuellement concernés.
- Il référence explicitement le cahier des charges 1SPE.
- Sa taille reste sous la limite Codex par défaut de 32 Kio pour la chaîne
  d'instructions projet.
- La hiérarchie retenue pour cette mission reste : sources officielles, cahier
  des charges, `AGENTS.md`, schémas et gates, décisions humaines, rapports,
  historiques.

## Collisions et arbitrages

Les anciens `CLAUDE.md`, prompts autonomes et directives de production
revendiquent parfois une priorité locale et décrivent le manuel 1SPE comme
« complet ». Cette affirmation est contredite par le cahier des charges actuel,
les artefacts observés et le gate `release-strict`. Elle reste donc historique
et ne vaut pas preuve de publication.

Les directives historiques demandent aussi de poursuivre la production de
chapitres. Le cadre Codex impose au contraire de stabiliser d'abord la chaîne de
qualité. L'ordre contractuel courant écarte cette collision sans modifier les
documents historiques.

Les règles `git push` et `gh pr create` utilisent la décision `prompt`. Cela
constitue une garde de revue, pas une interdiction : la mission humaine courante
autorise explicitement le push de la branche dédiée et l'ouverture d'une draft
PR après satisfaction du gate de Phase 0.1.

## Chemins présents et livrables futurs

Tous les chemins nécessaires à l'activation du cadre existent. Les chemins
suivants, cités dans le cahier des charges, sont explicitement des livrables
futurs et non des dépendances d'installation manquantes :

- `audit/ANOMALIES_BASELINE.json`
- `audit/ANOMALY_DISPOSITIONS.yaml`
- `audit/SOURCE_ROLES.yaml`
- `audit/PROGRAMME_2026_MATRIX.json`
- `audit/PROGRAMME_2026_MATRIX.md`
- `audit/MATH_REVIEW_REGISTER.yaml`
- `audit/VISUAL_REVIEW_REGISTER.yaml`
- `audit/HUMAN_APPROVALS.yaml`
- `audit/BUILD_MANIFESTS/`
- `audit/RELEASE_CANDIDATE_REPORT.md`

Les schémas de Phase 0.1 sous `audit/schemas/v1/` existent déjà au HEAD réel,
ce qui confirme que l'historique a dépassé le jalon initial décrit dans la
mission.

## Validation de la skill

Le front matter se charge comme un mapping YAML comportant `name` et
`description`; le nom `nexus-manual-quality` correspond au dossier et le corps
est non vide. La skill a été détectée et appliquée dans la session courante :
voie initiale `inventory/CI`, préservation du WIP, reproduction avant
correction, usage consultatif de Chutes et validations adversariales.

La skill décrit le workflow et ne remplace ni le cahier des charges ni
`AGENTS.md`.

## Validation des règles

`codex-cli 0.146.0` charge le fichier sans erreur avec
`codex execpolicy check`. Les contrôles représentatifs donnent :

| Commande testée | Décision |
|---|---|
| `git reset --hard HEAD` | `forbidden` |
| `git push origin finalisation/collection-v1` | `prompt` |
| `gh pr create --draft` | `prompt` |
| `rm -rf /tmp/example` | `forbidden` |

## Limites de détection

- Codex construit la chaîne `AGENTS.md` au démarrage d'une session ; une session
  déjà ouverte doit être relancée pour prouver le rechargement depuis disque.
- Les skills sont sélectionnées à partir de leur nom et de leur description ;
  leur détection implicite reste dépendante de la formulation de la mission.
- Les règles projet ne se chargent que si la couche `.codex` du projet est
  approuvée comme fiable.
- Les `prefix_rule` renforcent les interdictions mais ne remplacent pas les
  instructions : le fichier ne peut pas exprimer à lui seul toutes les
  positions possibles de `--force`, les déplacements de tags ou les opérations
  Git composées.
- Les règles `prompt` peuvent nécessiter un traitement particulier dans une
  exécution non interactive avec politique d'approbation `never`.

## Conclusion

Le cadre est cohérent, de taille raisonnable, syntaxiquement exploitable et
adapté à la racine du dépôt. La seule correction appliquée au bundle est la
suppression de 12 fins de ligne contenant des espaces dans le cahier des charges
afin de satisfaire `git diff --check`; elle ne change aucune exigence. Les
collisions relevées concernent des déclarations historiques devenues non
autoritatives ou des limites explicites des mécanismes expérimentaux.
