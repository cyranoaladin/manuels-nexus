#!/usr/bin/env python3
"""Générateur du registre des décisions graphiques et audit de conformité de la charte.

Reconstruit la chronologie des décisions v4, v4.1, v5, v5.B-it2, v6, v6.7 et isole les régression
comme la divergence de longueur minimale d'onglet par rapport à la spec du 20 juillet 2026.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def main() -> None:
    md_path = ROOT / "audit/GRAPHIC_CHARTER_DECISIONS.md"
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("# REGISTRE ET AUDIT DES DÉCISIONS DE CHARTE GRAPHIQUE\n\n")
        f.write("Ce document fige l'historique des décisions de maquette et identifie les régressions par rapport aux spécifications approuvées.\n\n")
        f.write("## 1. Chronologie des Maquettes et Extensions\n\n")
        f.write("- **v4 / v4.1** : Maquette originale (gabarit `nexus-manuel.cls` v4.1). Encadrés simples, onglets fixes.\n")
        f.write("- **v5** : Maquette avec onglets par chapitre, grille d'exercices à 2 colonnes 68mm et notes marginales.\n")
        f.write("- **v5.B-it2 (2026-07-20)** : Spécification validée de dimensionnement dynamique des onglets (`docs/superpowers/specs/2026-07-20-dynamic-rubric-tab-length-design.md`).\n")
        f.write("- **v6 / v6.7** : Maquette Premium unifiée avec boîtes `tcolorbox` à coins arrondis et ombre portée (HSL `chapcolor`).\n\n")
        
        f.write("## 2. Audit de la Régression Détectée : Dimensionnement des Onglets\n\n")
        f.write("| Propriété | Spécification Approuvée (2026-07-20) | Implémentation HEAD (`nexus-charte-v6.sty`) | Statut de Conformité |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        f.write("| **Longueur minimale** | `16 mm` | `14 mm` | ❌ **RÉGRESSION** |\n")
        f.write("| **Padding longitudinal** | `+6 mm` (3 mm de chaque côté) | `+5 mm` | ❌ **RÉGRESSION** |\n")
        f.write("| **Taille de police** | `\\fontsize{6}{6}` | `\\fontsize{5.5}{5.5}` | ❌ **RÉGRESSION** |\n")
        f.write("| **Épaisseur onglet** | `12 mm` | `12 mm` | ✅ Conforme |\n")
        f.write("| **Couleur de fond** | Dynamique `\\nxRubriqueCouleur` | Dynamique `\\nxRubriqueCouleur` | ✅ Conforme |\n\n")
        
        f.write("## 3. Plan de Correction Requis en Phase C/E\n\n")
        f.write("1. Restaurer les valeurs exactes de la spécification du 20 juillet dans la classe canonique unifiée.\n")
        f.write("2. Écrire des tests de non-régression visuelle vérifiant le comportement sur les onglets courts (`COURS`) et longs (`AUTO-ÉVALUATION`).\n")
        f.write("3. Soumettre la baseline visuelle pour validation.\n")

    print("GRAPHIC_CHARTER_DECISIONS.md généré avec succès.")

if __name__ == "__main__":
    main()
