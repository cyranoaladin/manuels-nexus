# REGISTRE ET AUDIT DES DÉCISIONS DE CHARTE GRAPHIQUE

Ce document fige l'historique des décisions de maquette et identifie les régressions par rapport aux spécifications approuvées.

## 1. Chronologie des Maquettes et Extensions

- **v4 / v4.1** : Maquette originale (gabarit `nexus-manuel.cls` v4.1). Encadrés simples, onglets fixes.
- **v5** : Maquette avec onglets par chapitre, grille d'exercices à 2 colonnes 68mm et notes marginales.
- **v5.B-it2 (2026-07-20)** : Spécification validée de dimensionnement dynamique des onglets (`docs/superpowers/specs/2026-07-20-dynamic-rubric-tab-length-design.md`).
- **v6 / v6.7** : Maquette Premium unifiée avec boîtes `tcolorbox` à coins arrondis et ombre portée (HSL `chapcolor`).

## 2. Audit de la Régression Détectée : Dimensionnement des Onglets

| Propriété | Spécification Approuvée (2026-07-20) | Implémentation HEAD (`nexus-charte-v6.sty`) | Statut de Conformité |
| :--- | :---: | :---: | :---: |
| **Longueur minimale** | `16 mm` | `14 mm` | ❌ **RÉGRESSION** |
| **Padding longitudinal** | `+6 mm` (3 mm de chaque côté) | `+5 mm` | ❌ **RÉGRESSION** |
| **Taille de police** | `\fontsize{6}{6}` | `\fontsize{5.5}{5.5}` | ❌ **RÉGRESSION** |
| **Épaisseur onglet** | `12 mm` | `12 mm` | ✅ Conforme |
| **Couleur de fond** | Dynamique `\nxRubriqueCouleur` | Dynamique `\nxRubriqueCouleur` | ✅ Conforme |

## 3. Plan de Correction Requis en Phase C/E

1. Restaurer les valeurs exactes de la spécification du 20 juillet dans la classe canonique unifiée.
2. Écrire des tests de non-régression visuelle vérifiant le comportement sur les onglets courts (`COURS`) et longs (`AUTO-ÉVALUATION`).
3. Soumettre la baseline visuelle pour validation.
