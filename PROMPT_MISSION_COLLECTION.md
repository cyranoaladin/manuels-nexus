# MISSION COLLECTION — Production des 4 manuels Nexus Réussite
## Mathématiques Première EDS · Mathématiques Terminale EDS · NSI Première · NSI Terminale

Tu es Claude Code. Tu travailles à la racine de `~/Documents/Manuels_Nexus/`, qui contient les deux projets : `Mathematiques/manuel-maths/` et `NSI/`. Ta mission : mener la collection à son terme — **quatre manuels complets, compilés, sous charte Nexus unifiée**. Ce prompt est le document de mission de niveau collection ; les CLAUDE.md, cahiers des charges, DIRECTIVES_EN_COURS et prompts de mission de chaque projet restent en vigueur et ce prompt les complète (en cas de conflit : ce prompt > CLAUDE.md projet > CDC > docs).

---

## 0. RÉGIME DE TRAVAIL (rappel consolidé, non négociable)

- **Persistance** : crée `DIRECTIVES_COLLECTION.md` à la racine de Manuels_Nexus, contenant la check-list du §2 ci-dessous. À chaque démarrage de session : lire ce fichier, puis le DIRECTIVES_EN_COURS.md du projet actif, reprendre la première tâche non cochée sans rien redemander. Chaque tâche cochée porte son commit.
- **Flux** : aucun arrêt volontaire, aucun « dois-je continuer ? », aucun tour terminé par un résumé. Rapport de LOT + commit + tâche suivante. Les fins de tour acceptées sont : `RAPPORT_FINAL_COLLECTION.md` écrit, ou une pause pilote planifiée (§0.1), ou `ARRET_MISSION.md` (impossibilité matérielle/intégrité après 3 contournements documentés).
- **§0.1 Pauses pilotes NON BLOQUANTES** (amendement au protocole NSI) : quand un pilote atteint son point de validation humaine, tu écris `PILOTE_A_VALIDER.md` + le PDF, **puis tu bascules immédiatement sur l'autre projet** au lieu de t'arrêter. À chaque frontière de chapitre, tu vérifies si un fichier `VALIDATION_PILOTE.md` (déposé par l'humain) ou un message humain est arrivé : si oui, tu appliques les retours puis tu reprends le projet concerné. La mission ne s'arrête totalement que si TOUS les fronts sont bloqués en attente humaine.
- **Qualité** (leçons acquises, déjà dans les DIRECTIVES projet — les relire) : sections 40–70 lignes ; exemple + contre-exemple après chaque définition ; erreurs fréquentes réparties, format copie fautive + correction ; coups de pouce en fichiers séparés ; production par capacité en une passe puis une passe de gates ; un commit par capacité au message exact ; adversarial en passe distincte, timestamps réels, contrôles cités ; accents partout ; figures obligatoires ; résolution aveugle des sujets ; toute sortie de code exécutée réellement (NSI R2) ; densité des corrigés ◆◆/◆◆◆.

## 1. ÉTAT DES LIEUX INITIAL (première action, une fois par session)

1. `git -C Mathematiques/manuel-maths log --oneline -15 && git -C Mathematiques/manuel-maths status` ; lire son `MISSION_LOG.md`, ses rapports de LOT, sa `DIRECTIVES_EN_COURS.md`. Établir : chapitres terminés (tags `chap/*-v1`), chapitre en cours et LOT exact, gates en échec éventuels.
2. Idem pour `NSI/` : état de l'installation (`INSTALLATION_rapport.md` présent ? smoke tests verts ?), état du pilote.
3. Écrire/mettre à jour `ETAT_COLLECTION.md` à la racine : tableau 4 manuels × (chapitres faits / en cours / restants / pauses en attente). Ce fichier se met à jour à chaque frontière de chapitre.
4. Ne JAMAIS refaire ce qui est fait : les tags et rapports font foi.

## 2. ORDRE DE PRODUCTION DE LA COLLECTION (check-list de DIRECTIVES_COLLECTION.md)

L'ordre optimise deux choses : sortir tôt les pauses pilotes (pour paralléliser validation humaine et production), et amortir chaque apprentissage sur les chapitres suivants.

- [ ] **J1 — NSI : installation** (si non faite) : exécuter `NSI/PROMPT_INSTALLATION_NSI` phases A→D + l'addendum gates du corpus (réutilisation des check_*.py, vérification R7 hors ligne contre les .txt officiels, scrapers existants, RAG existant). Gate : INSTALLATION_rapport.md, smoke tests verts.
- [ ] **J2 — NSI : pilote** `1NSI-TYPES-CONSTRUITS` LOT 0→7 → écrire PILOTE_A_VALIDER.md (avec extrait version aménagée) → **basculer sur maths sans attendre**.
- [ ] **J3 — Maths Première : achèvement**. Reprendre au point exact (état des lieux) : terminer le chapitre en cours, puis tous les chapitres restants jusqu'à `1SPE-VARIABLES-ALEATOIRES`, puis le LOT FINAL Première (blocs transversaux, harmonisation BO 2026 de Suites/Second degré, assemblage MANUEL_1SPE_v1.pdf + déclinaisons, RAPPORT_FINAL manuel).
- [ ] **J4 — Maths Terminale : bootstrap + production** (§3 ci-dessous), chapitre par chapitre.
- [ ] **J5 — NSI Première : chapitres 2→10** (dès validation du pilote reçue ; sinon continuer J4 et vérifier à chaque frontière).
- [ ] **J6 — NSI Terminale : chapitres 1→12 + blocs PREPA-ECE/ECRIT**.
- [ ] **J7 — LOTs FINAUX** : manuel NSI Première, manuel NSI Terminale, manuel maths Terminale (chacun : blocs transversaux, assemblage, déclinaisons dont livret professeur et version aménagée côté NSI, passe de cohérence).
- [ ] **J8 — COHÉRENCE COLLECTION** (§5) puis RAPPORT_FINAL_COLLECTION.md.

Les jalons J3/J4 et J5/J6 peuvent s'intercaler au gré des validations humaines reçues ; l'ordre INTERNE d'un manuel ne change jamais.

## 3. NOUVEAU CHANTIER — MANUEL MATHÉMATIQUES TERMINALE EDS

Le projet manuel-maths devient multi-niveaux : mêmes dépôt, classe, scripts, gates ; nouveaux référentiels et chapitres préfixés `TSPE-`.

### 3.1 Bootstrap (LOT 0 global Terminale)
1. **Vérification R7 renforcée** : le run Première a découvert le BO n°14 du 2 avril 2026. Vérifier en ligne si le programme de TERMINALE EDS a lui aussi été modifié (même BO ou autre) ; ancrer tous les référentiels `TSPE-*` sur le texte en vigueur, formulations mot à mot, sinon marquer « à re-vérifier » et consigner dans A_VALIDER_HUMAIN.md. Vérifier de même le format de l'épreuve écrite du bac en vigueur (structure, durée, calculatrice) avant tout LOT 6.
2. Créer `referentiel/capacites_TSPE_{THEME}.json` chapitre par chapitre (au LOT 0 de chacun, pas tous d'avance), démonstrations exigibles incluses — la Terminale en compte beaucoup : elles sont TOUTES rédigées intégralement en strate ★ (gate LOT 3).
3. Étendre `docs/09` (ou créer `docs/10_perimetre_terminale.md`) avec la liste ci-dessous et les prérequis croisés vers les chapitres de Première (les fiches R de Terminale renvoient aux chapitres du manuel de Première : c'est un argument produit de la collection).

### 3.2 Périmètre (ordre de production = progression pédagogique ; ajuster si le BO en vigueur diffère, en documentant)
1. `TSPE-SUITES-LIMITES` (limites de suites, récurrence — la démonstration par récurrence est un chapitre charnière : soigner M et ⚠)
2. `TSPE-LIMITES-FONCTIONS` 3. `TSPE-CONTINUITE` (TVI) 4. `TSPE-COMPLEMENTS-DERIVATION-CONVEXITE`
5. `TSPE-LOGARITHME` 6. `TSPE-PRIMITIVES-EQUATIONS-DIFF` 7. `TSPE-CALCUL-INTEGRAL`
8. `TSPE-COMBINATOIRE-DENOMBREMENT` 9. `TSPE-LOI-BINOMIALE` 10. `TSPE-SOMMES-VARIABLES-ALEATOIRES` 11. `TSPE-CONCENTRATION-LGN`
12. `TSPE-VECTEURS-DROITES-PLANS-ESPACE` 13. `TSPE-ORTHOGONALITE-PRODUIT-SCALAIRE-ESPACE` (+ représentations paramétriques/équations, à répartir 12/13 selon le BO).
Fonctions sinus/cosinus : vérifier leur position dans le programme en vigueur (Première vs Terminale) et trancher documenté.

### 3.3 Spécificités LOT 6 Terminale maths
- Sujets A/B au **format bac en vigueur** (vérifié R7), barème /20 par compétences, dont au moins un exercice croisant deux chapitres antérieurs (rebrassage).
- Chaque chapitre : 1 question 🗣 calibrée Grand Oral + 1 encadré « vers le supérieur » ★★ sobre.
- Bloc transversal final : « Préparation au bac » (2 sujets blancs complets couvrant l'année, copies types annotées faible/moyenne/excellente conformément au gabarit docs/01, calendrier de révision par parcours).
- Python : chaque chapitre où le programme le prévoit (suites, intégration/Monte-Carlo, binomiale, LGN) a ses exercices ⌨ avec blocs VERIFY sympy/numpy exécutés.

### 3.4 Ce qui NE change PAS
Gabarit 9 temps, matrice ≥2 ex/case et ≥50 ex/chapitre, ratio 40/40/20, charte v2 (signatures de chapitres à créer pour les 13 thèmes), figures pgfplots obligatoires (l'analyse de Terminale en est gourmande : limites, convexité, intégrales/aires — ≥ 8 par chapitre d'analyse), QCM diagnostiques, remédiation, versions B re-paramétrées, résolution aveugle, check-list LOT 7.

## 4. NSI — RIEN DE NOUVEAU, TOUT S'APPLIQUE

`NSI/PROMPT_MISSION_AUTONOME.md` + prompt d'installation + addendum corpus font foi : LOT R sur les contrats réels, restructuration T0 dominante, gates d'exécution (VERIFY/TRACE/ruff), gates transposés des check_*.py du corpus, version aménagée (F11), formats ECE avec squelettes vérifiés défaillants, mini-projets jalonnés, héritage des statuts needs_review. Seul amendement : la pause pilote devient non bloquante (§0.1).

## 5. COHÉRENCE DE COLLECTION (J8, avant le rapport final)

1. **Charte** : unique, synchronisée depuis manuel-maths (SYNC_CHARTE.md) ; vérifier que les 4 manuels compilent avec la MÊME version de la classe et des icônes ; onglets et signatures cohérents ; pages d'ouverture au même gabarit.
2. **Système élève commun** : tableau de bord identique (codage C/M/R, ◆), même voix éditoriale (docs/07), mêmes rubriques. Un élève qui a les deux manuels ne doit percevoir aucune rupture.
3. **Renvois croisés maths ↔ NSI** : les exercices ⌨ des manuels de maths renvoient aux chapitres NSI pertinents (« Python : voir manuel NSI Première, ch. Langage ») et réciproquement (complexité/logarithme, probabilités/données). Table des renvois dans chaque manuel, vérifiée à l'assemblage.
4. **Fiches R inter-manuels** : les prérequis de Terminale pointent vers les chapitres du manuel de Première correspondant (les deux matières).
5. **Contrôles globaux** : `make accents` sur les deux dépôts ; couverture référentiel 100 % × 4 ; grep des notations interdites ; numérotations et paginations propres ; A_VALIDER_HUMAIN.md consolidé au niveau collection (un fichier par projet + synthèse).
6. `RAPPORT_FINAL_COLLECTION.md` à la racine : les 4 PDF (+ déclinaisons), statistiques par manuel (objets par type/statut/mode_creation, part de transposition T0 côté NSI, coûts, temps), synthèse des points en attente de validation humaine, top 10 v2 par manuel, et la liste exacte des livrables avec chemins.

## 6. BUDGET ET LIVRABLES FINAUX

Budget indicatif : ≤ 40 $/chapitre maths, ≤ 25 $/chapitre NSI Première, ≤ 40 $/chapitre NSI Terminale ; dérives analysées dans les MISSION_LOG. Livrables : `MANUEL_1SPE_v1.pdf`, `MANUEL_TSPE_v1.pdf`, `MANUEL_1NSI_v1.pdf`, `MANUEL_TNSI_v1.pdf`, leurs déclinaisons (méthodes, remédiation, livret professeur, version aménagée NSI, banque ECE), les exports QCM JSON, et les quatre tags `manuel-*-v1.0`.

COMMENCE MAINTENANT : §1 état des lieux, puis la première case non cochée de DIRECTIVES_COLLECTION.md.
