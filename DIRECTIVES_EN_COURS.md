# DIRECTIVES EN COURS — lu à CHAQUE démarrage de session (CLAUDE.md §0)

Règle de flux permanente : aucun arrêt volontaire, aucun « dois-je continuer ? », aucun tour
terminé par un résumé. Rapport de LOT + commit + tâche suivante, en continu, jusqu'à
RAPPORT_FINAL.md. Cocher ici chaque directive exécutée avec le hash du commit.

## Check-list INSTALLATION (PROMPT_INSTALLATION_NSI.md)

- [x] Phase A : connexion corpus (lien symbolique, .env, scripts patches, gitignore, test readonly)
- [x] Phase B : synchronisation charte (4 gabarits + 2 docs depuis maths, InputIfFileExists, fix doublons)
- [x] Phase C : adaptation pipeline (harvest reecrit, convert_programme_yaml adapte, F11, mapping docs/09)
- [x] Phase D : smoke tests (referentiel 114 caps, harvest P04 21 fichiers, tests Python OK, accents OK, compilation OK)
- [x] Addendum C.6 : gates corpus transposes (7 scripts dans gates_corpus/, make gates-corpus, tous verts)
- [x] Addendum R7 hors ligne : referentiel confronte aux textes officiels (94 contenus, 1 ecart mineur)
- [x] Addendum scrapers : inventaire + repli documente sur crawl.py (docs/10)
- [x] Addendum MCP-corpus RAG : joignable mais cle absente, mode fichiers retenu

## Check-list active

- [x] PHASE 0 : bootstrap — env, connexion corpus, referentiels generes, git init/commit.
- [x] PILOTE 1NSI-TYPES-CONSTRUITS : LOT 0 → R → 2 → 3 → 4 → 5 → 6 → 7 (a6cdcd8, 050557e, LOT-7).
- [ ] PAUSE UNIQUE AUTORISÉE : validation humaine du pilote (CDC §7.3) — produire le PDF,
      lister les points de jugement (figures mémoire, densité codereference, équilibre
      transposition/réécriture) dans PILOTE_A_VALIDER.md, puis attendre.
- [ ] Après validation : Première chapitres 1, 3–10 (boucle complète chacun, sans arrêt).
- [ ] Terminale chapitres 1–12 + blocs ECE/écrit.
- [ ] LOTs FINAUX des deux manuels (blocs transversaux, assemblages, déclinaisons dont
      livret professeur, harmonisation inter-manuels, RAPPORT_FINAL.md).

## Directives qualité permanentes (héritées du run maths — ne pas ré-apprendre ces leçons)

- Sections de cours : 40–70 lignes de .tex, jamais moins. Exemple + contre-exemple après
  chaque définition. Erreurs fréquentes réparties par section, format « copie fautive + correction ».
- Coups de pouce : fichiers séparés {ID}-CDP.tex, jamais dans l'énoncé (R9).
- Production par capacité en UNE passe d'écriture, puis UNE passe de gates, un commit par
  capacité au message exact. make chapter une fois par LOT, pas par objet.
- Adversarial : passe distincte, relecture depuis le disque, timestamps réels, contrôles cités.
- Accents français partout dans les libellés imprimés (R10).
- ◆◆ = format examen contextualisé 2-3 questions ; ◆◆◆ = prise d'initiative réelle ;
  corrigés ◆◆/◆◆◆ : 10-20 lignes, calculs/raisonnements intermédiaires, conclusion.
