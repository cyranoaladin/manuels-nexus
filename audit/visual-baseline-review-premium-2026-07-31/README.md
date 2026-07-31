# Revue approuvée — onglets premium de la maquette V5

Statut : **APPROUVÉ POUR MISE À JOUR DE LA BASELINE VISUELLE**.

## Historique de la décision

Le premier prototype adaptatif a été refusé humainement : les bandes étaient
jugées trop massives et le rendu insuffisamment net.

Un second prototype premium a ensuite été conçu avec :

- une largeur visible de 10 mm ;
- un fond bleu nuit `#16233B` ;
- un liseré indigo de 0,7 pt ;
- des angles arrondis de 1,1 mm ;
- un texte blanc vectoriel de 5,5 pt ;
- une longueur adaptative avec un minimum de 14 mm ;
- un contrôle visuel sur des recadrages individuels à 600 ppp.

Les pages 1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 12, 15 ont été inspectées et
approuvées humainement.

## Mise à jour des références

| Page | Hash avant | Hash approuvé | Décision |
|---:|---|---|---|
| 1 | `a3a5ea8b94c92028fad069d3ac11708bbfb51c883efbc2b6a011e69ff0592fd2` | `f6e8e2f7fd212f2c2a30e157e1ca54c04e07e99989e4973d97d166bf8aa29f21` | approuvé |
| 2 | `83eaaf15bad92a303ce8c367c3dffd498fea505930aaf4be6b06322bd2d07d10` | `fdb7d7be2aba4ecbe0b6384216ac99225e4d9134f89fd0ec78bd5600045e1c8d` | approuvé |
| 3 | `4247bbe4325551dd26164476f9773fc8a11f1a131f3481a8da39e60b8e95c1c1` | `929de90de73fd84b374d3a9532127412b2d7b84f567a2a05496ad53e45a23b28` | approuvé |
| 4 | `8229c5aaa4bcec461bf8442c4c448655315a4fb2fedf11a0052dcebdfb8c93c2` | `ea0c65d97887080748e086f8f28d320bc9e275353913d5fd4ce1ab0518661efa` | approuvé |
| 5 | `54d58a7128379386bfb32f79f6e8b0a3e8ea1916cdd785df748044fac2fcd30a` | `5af5aa84251dda5ed60b939150e9d7d54d29ab685940b6dc6e6013adc1af456b` | approuvé |
| 7 | `0f091b2b8488f89de66884cc22b238450264791875568f8116e4e0bc65cf6280` | `8c074523fc9a748d600cab68f2a39f6160c3a0b16c573c40e44e8a77c5c4fa26` | approuvé |
| 8 | `13ff6daab5f2d5fbd999af3e3f433f7bc92f2fc89f2adfd39f72bdf368e2b70f` | `aaa00f8b119290b299796bf5aa46d4be57ce73fcc353149a449d1bfb0b64a1b9` | approuvé |
| 9 | `ccda0af7007a15ecf3b895b5cb60a2f658bcee78e7a725acad4d6590f54135c3` | `9194d44098884daa94903d15e30aa9b64c6ea6a8d6f7828e617986d5228daafe` | approuvé |
| 10 | `4466330daf59618c2ab25947e244e08da3fcca1f446516af378f8884778e52d1` | `874bf8e82ba491b6ec1cda722a83eb9004b8d92b435cb69550f689b45c96bff5` | approuvé |
| 11 | `7f114a2b9d958da28ec7eb8d3a7b568ba7bd755cc872c9721ba388fc93e0f130` | `9cf0230785abda7d7c5b6bd402f5c5e39346c2bf25936f674e9004c079e7c5be` | approuvé |
| 12 | `3517dc008fd517f5c9c3858c2e5ba7bd3ce39ac677d4522d1e524d3e20d9f44f` | `d4bd8e068b34160549a731272de8d9285a276018ed507bede03e1dbcfe2350c7` | approuvé |
| 15 | `11de1dad17368d27af7bf1ead77d3afad27188785806821bd01bdc5a1b1a9141` | `d47612afe936bbc82576388107f34ebce8d547344c93176019cc7462a4677591` | approuvé |

Les pages 6 et 14 sont inchangées. La page 13 conserve son traitement
spécifique de diagnostics.

## Preuves conservées

- PDF de contrôle non suivi dans Git ; empreinte conservée dans `manifest.json` : `6281466a508788d7ee9a795c52d42d341fdd63d6956540437d18670ff6dd0991` ;
- `planche-onglets-premium.png` : première planche approuvée ;
- `planche-onglets-pages-02-05.png` : seconde planche approuvée ;
- `crops/` : douze recadrages individuels à 600 ppp ;
- `manifest.json` : empreintes, contrat graphique, versions d’outils et
  portée exacte de la décision.

## Contrôles validés

- Maquette V5 : **100 tests réussis** ;
- Inventaire sous `CI=true` : **422 tests réussis** ;
- Ruff, périmètre exact de la CI : **vert** ;
- `git diff --check` : **vert**.

Cette approbation autorise uniquement la nouvelle baseline visuelle. Elle ne
constitue pas une approbation de merge, de release ou du contenu mathématique.
