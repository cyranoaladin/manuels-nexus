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

- [x] **2f. INTÉGRITÉ — Ré-attestation PDF et restauration des correctifs v3.2.**
  - Commit : 410007f

- [x] **2g. INTÉGRITÉ E.2-E.4 — Rapprochements, chaîne complète, clôture.**
  - E.2 : 5 rapprochements nominatifs (0 écart objet), diff visuel, addendums LOT-7.
  - E.3 : test bout-en-bout, verify_pdf NSI, make specimen CI.
  - E.4 : PNG 150 dpi x4, tout vert, défaut ouvert cls:361.

- [ ] **3. PRODUCTION SANS ARRÊT**
  - [x] 3a/3b. C1-C5 complets, 30 ex (6/capacité, 2/case), coverage 0 manquant.
    C1:fca6a93, C2:973a268, C3:b3e4057, C4:87ce22e, C5:0a29108.
    Reste : 20 ex supplémentaires pour atteindre 50 (E5).
  - [x] 3c. LOT 5 : QCM 15q + FR-R1..R5 + RE-C1..C5 (30 ex remédiation). SymPy 143/143.
  - [x] 3d. LOT 6 : Eval A+B + corrigés + 2 TD. Résolution aveugle 0 divergence.
  - [x] 3e. LOT 7 : PDF 36p 240 Ko, check-list 7/8, inventaire 78 \input.
  - [ ] 3f. 1SPE-DERIVATION-GLOBAL LOT 0→7 puis suite du périmètre.

- [ ] **4. RAPPORT_FINAL.md** — Fin de tour.

## Exigences métier permanentes

**Règle de complétude** : un point de directive n'est réputé traité que si son livrable existe et est cité avec son chemin exact dans le rapport. Un tour ne se termine jamais sur une liste de restes : tant qu'il reste un point exécutable sans validation humaine, il est exécuté dans le même tour. Les seules fins de tour admises restent : rapport final, pause pilote non bloquante (avec bascule immédiate), ou ARRET_MISSION.md documenté.

> Le chat n'est pas un canal de reporting. Tout constat, verdict, explication
> ou état d'avancement s'écrit UNIQUEMENT dans les fichiers du dépôt
> (rapports de LOT, addendums, MISSION_LOG.md). La seule sortie chat
> autorisée est une ligne unique, à la fin du travail :
> « TERMINÉ <hash du dernier commit> — prochaine tâche : <tâche> »
> Toute autre phrase écrite dans le chat compte comme un contournement
> documenté au sens du protocole d'arrêt.

- E5/F01 : ≥ 50 exercices par chapitre, ≥ 2 exercices par case capacité × parcours, ratio 40/40/20.
- Tout objet autonome : corrigé copie-modèle 10-20 lignes, méthode illustrée, diagnostic QCM, CDP séparés.
- Parcours ◆ = coups de pouce, ◆◆ = format examen contextualisé, ◆◆◆ = prise d'initiative/recherche.
- Public : élèves système français, candidats libres, autonomie maximale, zéro implicite de classe.
