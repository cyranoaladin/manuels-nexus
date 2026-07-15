# DIRECTIVES EN COURS — Check-list de production

À chaque reprise de session, reprendre la première tâche non cochée sans rien redemander.

## Règle de flux

Un tour ne se termine jamais par un résumé ni une question. Rapport de LOT + commit + tâche suivante, en continu. Fin de tour = RAPPORT_FINAL.md uniquement.

---

## Check-list

- [x] **0. PERSISTANCE** — Créer ce fichier + modifier CLAUDE.md. Commit [META].
  - Commit : _(à remplir)_

- [ ] **1. HOTFIX ACCENTS** — Restaurer tous les accents dans nexus-manuel.cls et docs/06_charte_graphique.md. Recompiler 3 chapitres, vérifier accents sur PNG. Commit [CHARTE][HOTFIX] accents.
  - Commit : _

- [ ] **2. LOT 3ter — IDENTITÉ VISUELLE NEXUS RÉUSSITE**
  - [ ] 2a. Icônes propriétaires TikZ (gabarits/nexus-icons.tex), remplacement des \ding partout.
  - [ ] 2b. Signature de chapitre : bandeau TikZ ouverture + onglet de tranche + miniature en-tête.
  - [ ] 2c. Figures mathématiques (gabarits/nexus-figures.tex) + style pgfplots + figures Dérivation (4), Suites (2), Second degré (3). Règle permanente : capacité graphique ⇒ ≥2 figures cours, ≥1 exercices.
  - [ ] 2d. Ligne éditoriale (docs/07_ligne_editoriale.md) : tutoiement méthodes/CDP/QCM, cours impersonnel, voix Nexus.
  - [ ] 2e. GATE VISUEL v3 : 5 PNG Dérivation locale, inspection, charte.visual.json. Commit [CHARTE][LOT-3ter].
  - Commit : _

- [ ] **3. PRODUCTION SANS ARRÊT**
  - [ ] 3a. Matrice C1 Dérivation locale complète (4 ex manquants ◆◆/◆◆◆ + corrigés + CDP). Commit honnête.
  - [ ] 3b. C2→C5 avec figures dans exercices graphiques. Coverage 0 manquant.
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
