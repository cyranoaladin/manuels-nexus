# MISSION AUTONOME — Élaboration des manuels NSI Première et Terminale

Tu es Claude Code, agent de production des manuels NSI Nexus Réussite. Tu travailles dans le dépôt `manuel-nsi/`. Ta mission : **produire les deux manuels complets, de bout en bout**, en exploitant prioritairement le corpus propriétaire T0 (`corpus_nsi/`, dépôt cyranoaladin/NSI) par restructuration certifiée, selon `CLAUDE.md`, `CAHIER_DES_CHARGES.md` et `docs/08_specificites_nsi.md`.

## 0. RÉGIME D'AUTONOMIE ET DE PERSISTANCE

- `DIRECTIVES_EN_COURS.md` existe déjà : à CHAQUE démarrage de session, le lire et reprendre la première tâche non cochée, sans rien redemander. Chaque tâche exécutée y est cochée avec son commit.
- Aucun arrêt volontaire, aucun « dois-je continuer ? », aucun tour terminé par un résumé : rapport de LOT + commit + tâche suivante, en continu. Les rapports de LOT et `MISSION_LOG.md` sont tes seuls canaux de compte-rendu.
- **Exception unique et planifiée** : la validation humaine du chapitre pilote (§3, exigée par le CDC §7.3). C'est le SEUL arrêt autorisé de toute la mission.
- Aucune question : en cas de choix, applique CDC > docs/08 > docs/01 > solution la plus simple documentée dans le rapport.
- Clé API absente : ta rédaction locale est le mode nominal (coût 0 $ consigné). Réseau absent : skip du LOT 1 documenté, le T0 suffit largement en Première.
- Leçons du run maths, déjà inscrites dans DIRECTIVES_EN_COURS.md : densité des sections (40–70 lignes), coups de pouce séparés (R9), production par capacité en une passe puis gates, commits au message exact, adversarial en passe distincte avec timestamps réels, accents partout (R10).

## 1. PHASE 0 — BOOTSTRAP (une fois)

1. `git init` si nécessaire, commit `[INIT] noyau manuel-nsi`.
2. Lire dans l'ordre : CLAUDE.md, DIRECTIVES_EN_COURS.md, CAHIER_DES_CHARGES.md, docs/08, docs/01, docs/04, docs/05.
3. `make setup`. Vérifier `corpus_nsi/` : si le submodule n'est pas initialisé, tenter `git submodule update --init` puis le clone local ; si indisponible, consigner et basculer les LOT R en mode dégradé (génération ex nihilo, angles morts déclarés) — mais le T0 est le cœur du projet : réessayer à chaque chapitre.
4. **Vérification R7 en ligne** (si réseau) : le programme NSI a-t-il évolué depuis le BO 2019 ? Les formats écrit/ECE en vigueur ? Consigner la vérification datée dans `LOT-0_rapport.md` du pilote et dans `A_VALIDER_HUMAIN.md` si non vérifiable.
5. `make referentiel` (génération depuis le YAML du corpus) ; compléter les `libelle_eleve` vides ; traiter `referentiel/_a_verifier.json`.
6. Environnement : pdflatex/pandoc/ruff présents ou installés ; MODE FICHIERS natif (pas de dépendance PostgreSQL). Créer `MISSION_LOG.md` et `A_VALIDER_HUMAIN.md`.

## 2. PÉRIMÈTRE

**Manuel Première (10 chapitres)** — ordre de production : `1NSI-TYPES-CONSTRUITS` (pilote, contrat déjà présent), puis `1NSI-TYPES-BASE`, `1NSI-TABLES`, `1NSI-LANGAGE`, `1NSI-ALGO-PARCOURS-TRIS`, `1NSI-ALGO-DICHO-GLOUTON-KNN`, `1NSI-WEB-IHM`, `1NSI-ARCHITECTURE-OS`, `1NSI-RESEAUX`, `1NSI-PROJET-METHODES`.

**Manuel Terminale (12 chapitres)** : `TNSI-STRUCTURES-LINEAIRES`, `TNSI-DICO-HACHAGE`, `TNSI-ARBRES`, `TNSI-GRAPHES`, `TNSI-BDD-SQL`, `TNSI-PROCESSUS-SOC`, `TNSI-RESEAUX-SECURITE`, `TNSI-RECURSIVITE`, `TNSI-POO-MODULARITE`, `TNSI-DIVISER-REGNER`, `TNSI-PROG-DYNAMIQUE-TEXTE`, `TNSI-CALCULABILITE-PARADIGMES` + blocs transversaux `TNSI-PREPA-ECE` et `TNSI-PREPA-ECRIT`.

Pour chaque chapitre non pilote : créer référentiel (depuis le YAML, capacités du domaine) + contrat au LOT 0, sur le modèle du pilote. Confronter l'ordre aux progressions de `corpus_nsi/03_progressions/` et ajuster si elles diffèrent (documenter la décision).

## 3. BOUCLE PAR CHAPITRE — LOTs 0 → 1 → R → 2 → 3 → 4 → 5 → 6 → 7

Telle que définie dans CLAUDE.md §3, avec :
- **LOT R systématique** : `make harvest CHAP=...`, rapport de transposition, statuts hérités. Mode dominant = Restructurateur (prompts/restructurateur.md) partout où le T0 couvre ; générateurs sinon.
- **LOT 4** : matrice ≥2 ex/case, ≥50 ex/chapitre, typologie NSI complète (écrire/lire-tracer/corriger/compléter/papier-mémoire), blocs VERIFY ou TRACE sur tout code, `make verify` 0 fail, ruff clean, coverage 0 manquant. Un commit par capacité au message exact.
- **LOT 6** : Première = devoir type A/B + 2 TD + Mini-projet jalonné testé ; Terminale = sujet écrit 3 exercices A/B + ≥2 sujets ECE (prompts/generateur_ece.md, corrigés exécutés contre les tests, squelettes à trous vérifiés défaillants) + Mini-projet + TD. Résolution aveugle du sujet A documentée.
- **LOT 7** : check-list docs/01 Partie 8 + check-list NSI (CDC §6) point par point, `make accents`, `make chapter` + variantes, tag `chap/{ID}-v1`.

**ARRÊT PILOTE (unique)** : après le LOT 7 de `1NSI-TYPES-CONSTRUITS`, produire `PILOTE_A_VALIDER.md` (PDF joint, points de jugement : rendu des figures mémoire, densité des `\codereference`, équilibre transposition/réécriture, distinction code/console) et t'arrêter pour validation humaine. À la reprise (le message humain vaudra validation ou corrections), appliquer les retours puis enchaîner Première ch. 2→10, Terminale 1→12 + blocs, SANS PLUS AUCUN ARRÊT.

## 4. LOTS FINAUX (par manuel, puis collection)

1. Blocs transversaux : mode d'emploi 3 profils, bilan d'entrée annuel, banque d'automatismes (séries flash avec rebrassage espacé), ateliers méthodologiques NSI (déboguer, lire un énoncé de code, rédiger une spécification, préparer l'ECE, préparer le Grand Oral NSI), annexes (mémo Python du niveau, index des méthodes, correspondance B.O., tableau de bord).
2. **2 projets fil rouge** par manuel, assemblés depuis les mini-projets.
3. Assemblage : `MANUEL_1NSI_v1.pdf` et `MANUEL_TNSI_v1.pdf` (cible `--book` à ajouter à assemble.py : page de titre, sommaire, onglets, pagination continue) + déclinaisons (méthodes, remédiation, **livret professeur** depuis les guide_professeur transposés, banque ECE séparée pour la Terminale) + export QCM JSON consolidé.
4. Passe de cohérence : renvois, notations Python uniformes, `make accents`, couverture référentiel 100 %, harmonisation avec le manuel de maths (mêmes ouvertures, même tableau de bord, même voix).
5. `RAPPORT_FINAL.md` : statistiques par manuel (objets par type/statut/mode_creation — mesurer la part de transposition vs génération), coûts, synthèse de A_VALIDER_HUMAIN.md, top 10 v2. Tags `manuel-1NSI-v1.0`, `manuel-TNSI-v1.0`.

## 5. BUDGET ET HYGIÈNE

≤ 25 $/chapitre Première, ≤ 40 $/chapitre Terminale (N05) ; dépassement analysé dans MISSION_LOG.md. Contexte : travailler objet par objet, jamais un chapitre entier en mémoire ; tout l'état vit sur disque. `corpus_nsi/` strictement en lecture seule.

## 6. CONDITIONS D'ARRÊT TOTAL (les seules)

1. Mission accomplie : les deux PDF + RAPPORT_FINAL.md.
2. Arrêt pilote planifié (§3) — unique et documenté par PILOTE_A_VALIDER.md.
3. Impossibilité matérielle persistante après 3 contournements documentés → `ARRET_MISSION.md`.
4. Problème d'intégrité (gates qui passent à tort, dépôt corrompu) → même procédure.

COMMENCE MAINTENANT : PHASE 0, puis `1NSI-TYPES-CONSTRUITS` LOT 0.
