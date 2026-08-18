# A3 — IMPACT BUILD (HISTORICAL SNAPSHOT)

Impact de la résolution des 3 `duplicate_assembly_objects` sur les builds.
Référence : `audit/A3_DUPLICATE_ASSEMBLY_FORENSICS.md`.

## Périmètre affecté

Un seul assemblage est concerné :
`math:static:Mathematiques/manuel-maths/build/maquette-v5/maquette.tex`
(maquette éditoriale V5, variante unique `maquette-v5`, chapitre
`1SPE-DERIVATION-LOCAL`). Aucun manuel élève/professeur n'est touché : les
assembleurs des 6 manuels ne contiennent aucune des 3 anomalies, donc aucune
reconstruction élève/professeur n'est requise (§11 — « pas nécessairement
les 12 si seuls certains manuels sont affectés »).

## Nature de la résolution

INTENTIONAL_REUSE contractualisée : la correction porte sur l'ANALYSEUR
(registre `audit/ASSEMBLY_REUSE_CONTRACTS.yaml` + invariant bidirectionnel
`occurrence == attendu`). Le master, les 3 objets et le rendu sont
inchangés — aucun objet n'a été retiré du document.

| champ | valeur |
| --- | --- |
| manual | — (maquette, hors matrice manuels) |
| variant | maquette-v5 (unique) |
| before_pages | 15 |
| after_pages | 15 |
| page_delta | 0 |
| removed_duplicate_object | AUCUN (réutilisation déclarée, rien retiré) |
| expected_content_loss | **NONE** |
| all_other_objects_preserved | OUI |
| unique canonical objects before | 29 |
| unique canonical objects after | 29 |
| missing legitimate objects | 0 |

## Preuves

- Master : blob Git inchangé (`e549c5a2dd4c…`, aucun commit A3 ne touche un
  `.tex`).
- Rebuild depuis zéro post-A3 (producteur + 3 passes LuaLaTeX,
  `-recorder`) : 15 pages ; **les 15 rasters 300 dpi sont byte-identiques**
  aux rasters du build de référence à `018a0adb` (15/15 pages, diff pixel
  nul). Les octets du PDF varient entre exécutions (horodatage de création
  PDF) ; l'oracle déterministe du dépôt est le raster, prouvé stable.
- `maquette.fls` (runtime) : consomme `gabarits/common/nexus-manuel.cls`
  (`sha256 9a85c337…`) et `gabarits/common/nexus-charte.sty`
  (`sha256 2fc3970c…`) — canoniques, non modifiés par A3.
- Audit d'occurrences : EX-001/002/005 attendus 2, observés 2 (contrat) ;
  les 26 autres objets de l'assemblage attendus 1, observés 1.
- Étanchéité élève/professeur : sans objet pour cet assemblage
  (mono-variante) ; aucun assembleur de manuel modifié, aucune fuite
  possible introduite.
- `check_maquette_v5` échoue toujours volontairement sur les oracles
  visuels (« page 1 altérée ») — état hérité de la correction charte 12 mm,
  D7 BLOCKED, oracles non mis à jour (aucun rapport avec A3 : les rasters
  pré/post A3 sont identiques entre eux).

Un changement de pagination aurait été légitime si un doublon publié avait
été retiré ; ici la réutilisation est contractuelle, donc l'absence totale
de changement est le résultat attendu et vérifié.
