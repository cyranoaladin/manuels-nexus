# Cartographie Drive

## État

Les ressources Drive sont traitées depuis le miroir local `Documents_DRIVE`, résolu par `NSI_DOCUMENTS_DRIVE_ROOT` ou par le dossier `../Documents_DRIVE` voisin du dépôt.

Cette passe ne publie aucune ressource. Elle classe chaque ligne de `drive_inventory.csv` et trace les reprises effectives dans `support_source_trace.yml`.

## Synthèse de décision

- `integrated_adapted` : ressource locale adaptée dans un support existant, sans copie brute et avec hash.
- `inspiration_only` : ressource locale consultée comme inspiration, sans reprise dans un support.
- `rejected_sensitive` : ressource exclue pour donnée personnelle probable ou artefact technique.
- `missing_local_copy` : copie locale absente ; contenu non inventé.
- `deferred` : copie locale trouvée mais audit pédagogique/RGPD différé.
- `quarantined` : ressource à isoler avant toute reprise.

## Ressources effectivement adaptées

- `1_RdD_Entier naturel.pdf` → enrichissement de `premiere/sequences/s01_representation_donnees/cours_eleve.md`.
- `pays_monde.csv` → extrait non personnel et supports P05 tables CSV.
- `types_construits_python-v2.pdf` → fiche P04 tuples/types construits.
- `Séquence1_TAD_Théorie` → fiche T01 interface/TAD.
- `Séquence17_Boyer-Moore` → fiche T18 Boyer-Moore.

## Ressources refusées

- `rendus_eleves`
- `.git`
- `.venv`
- `NotesEleves.csv`
- `Fichier_Eleves.csv`

## Statut de release

`check_drive_mapping.py` accepte l’état prototype car les ressources sont classées et tracées.

`check_drive_mapping_release.py` reste bloquant tant que des ressources sont `missing_local_copy`, `deferred`, `quarantined` ou `rejected_sensitive`, et tant que les revues humaines et décisions de publication manquent.

FINAL_STATUS = NON_RELEASE_READY.
## Plan de lots Drive

| Lot | Source Drive | Extraction utile | Support(s) à modifier | Nature de reprise | Hash | RGPD | Statut |
|---|---|---|---|---|---|---|---|
| Lot Drive P05 : traitement_tables complet | `pays_monde.csv` | champs `PAYS`, `CAPITALE`, `CONTINENT`, `POPULATION`, ligne invalide | supports P05 tables CSV + extrait local | `adaptation_drive` + `import_partiel` | `57359dcc669fa30c547923cea12fd3d0cbe1268b5ecf200411e0e61dd855e958` | conforme, données géographiques non personnelles | needs_review |
| Lot Drive T01 : TAD complet | `Séquence1_TAD_Théorie` | interface pile/file, implémentation, invariant, tests de conformité | fiche T01 + supports T01 déjà reliés | `adaptation_drive` sur fiche, enrichissement local des supports | `8ffe9aafd46786fc86868d9c742b1aa3c5dfbe37ddce79f406a6127c991513bf` | conforme, dossier disciplinaire audité | needs_review |
| Lot Drive T18 : Boyer-Moore complet | `Séquence17_Boyer-Moore` | table du mauvais caractère, trace droite-gauche, pseudo-code | fiche T18 + TD/évaluation T18 | `adaptation_drive` sur fiche, enrichissement local des supports | `e325a488684eb9f2267791d20b686551e6aeebc660952ce48496d00a396b7084` | conforme, ressource disciplinaire | needs_review |
| Lot Drive P12 : tri / complexité | `Cours.pdf` | tris, invariants, coûts, jeux d’essai | supports P12 à auditer dans un lot dédié | `deferred` | `b215d415d71f1c48bab41ed7bef030f5e92da0b04cbacc54e63cf314360b9027` | à auditer avant reprise | needs_review |
| Lot Drive P13 : glouton | `2_TP.pdf` | problème glouton, critères de choix, contre-exemples | supports P13 à auditer dans un lot dédié | `deferred` | `75ddc3fc3503cd0141116205ac46e50f4c26328305953a5f280db71753a63885` | à auditer avant reprise | needs_review |
