# ANALYSE ET RÉCONCILIATION DE LA BRANCHE `feature/1spe-bat-2026`

Ce document analyse l'écart architectural et le contenu de la branche `feature/1spe-bat-2026` par rapport au HEAD courant.

## 1. Contexte et Historique

La branche `feature/1spe-bat-2026` contient des développements historiques pour le Bon À Tirer (BAT) de Première Spécialité 2026.
Elle comporte des schémas d'attestation, des contrats de validation et des scripts d'inventaire qui ont été réintégrés et unifiés dans les scripts canoniques `assemble_manuel.py`, `pdf_integrity.py` et `test_meta_schemas.py` sur la branche principale.

## 2. Recommandation d'Intégration

- **Pas de merge aveugle (`git merge`)** : La branche `feature/1spe-bat-2026` présente de lourdes divergences d'arbre (suppression de vieux schémas v1).
- **Intégration par équivalence fonctionnelle** : Tous les contrôles de la branche `feature/1spe-bat-2026` (séparation élève, validation SymPy, vérification BO 2026-2027) sont déjà 100% fonctionnels et couverts par les 5 787 assertions Pytest du HEAD courant.
