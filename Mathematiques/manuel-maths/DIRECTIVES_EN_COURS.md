# DIRECTIVES EN COURS — Check-list de production

À chaque reprise de session, reprendre la première tâche non cochée sans rien redemander.

## Règle de flux

Un tour ne se termine jamais par un résumé ni une question. Rapport de LOT + commit + tâche suivante, en continu. Fin de tour = RAPPORT_FINAL.md uniquement.

---

## Check-list

- [x] **0. PERSISTANCE** — Créer ce fichier + modifier CLAUDE.md. Commit [META].
  - Commit : ffc3d26

- [x] **1. HOTFIX ACCENTS** — Restaurer tous les accents dans nexus-manuel.cls et docs/06_charte_graphique.md. Recompiler 3 chapitres, vérifier accents sur PNG. Commit [CHARTE][HOTFIX] accents.
  - Commit : 7d9e7a7

- [x] **2. LOT 3ter — IDENTITÉ VISUELLE NEXUS RÉUSSITE**
  - [x] 2a. Icônes propriétaires TikZ (nexus-icons.tex) : 11 icônes, losanges redessinés.
  - [x] 2b. Signature de chapitre : bandeau, onglet, mini-losange en-tête.
  - [x] 2c. Figures pgfplots (nexus-figures.tex) + 5 figures Dérivation locale (C1–C5).
  - [x] 2d. Ligne éditoriale (docs/07_ligne_editoriale.md).
  - [x] 2e. GATE VISUEL v3 : 5 PNG inspectés PASS, 0 régression.
  - Commit : c61daa1

- [ ] **3. PRODUCTION SANS ARRÊT**
  - [x] 3a/3b. C1-C5 complets, 30 ex (6/capacité, 2/case), coverage 0 manquant.
    C1:fca6a93, C2:973a268, C3:b3e4057, C4:87ce22e, C5:0a29108.
    Reste : 20 ex supplémentaires pour atteindre 50 (E5).
  - [ ] 3c. LOT 5 : QCM ≥15 q, fiches R1–R5, remédiation 3 ex/capacité.
  - [ ] 3d. LOT 6 : Sujet A + barème, version B, 2 TD, résolution aveugle.
  - [ ] 3e. LOT 7 : check-list Partie 8, tag.
  - [ ] 3f. 1SPE-DERIVATION-GLOBAL LOT 0→7 puis suite du périmètre.

- [ ] **4. RAPPORT_FINAL.md** — Fin de tour.

## Exigences métier permanentes

- E5/F01 : ≥ 50 exercices par chapitre, ≥ 2 exercices par case capacité × parcours, ratio 40/40/20.
- Tout objet autonome : corrigé copie-modèle 10-20 lignes, méthode illustrée, diagnostic QCM, CDP séparés.
- Parcours ◆ = coups de pouce, ◆◆ = format examen contextualisé, ◆◆◆ = prise d'initiative/recherche.
- Public : élèves système français, candidats libres, autonomie maximale, zéro implicite de classe.
