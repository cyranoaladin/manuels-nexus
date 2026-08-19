# CIBLES DE MÉTHODES MANQUANTES — N EXACT

Décision éditoriale appliquée : la règle « une fiche méthode par capacité
(M_i ↔ C_i) » est CONSERVÉE ; aucune référence M2..Mn n'est supprimée pour
faire tomber le compteur. Version machine : `audit/MISSING_METHOD_TARGETS.json`
(les 59 cibles avec capacité, libellé élève, objets référents, autorité
programme).

## Invariant

```
unique missing method targets  N = 59
sum(inbound_reference_count)     = 470
```

(Les 476 références initiales = 470 restantes + 6 références M5 d'ADGK
retirées comme impossibles — architecture C↔M à 3 capacités, voir
`A4_ADGK_CANONICAL_STATUS.md`.)

## Répartition

| manuel | cibles | détail |
| --- | --- | --- |
| TCOMPL | 36 | 9 chapitres × M2..M5 |
| TEXPERTES | 20 | 5 chapitres × M2..M5 |
| 1NSI | 2 | ADGK M2 (C2/P-ALGO-05, gloutons), M3 (C3/P-ALGO-03, k-NN) |
| 1SPE | 1 | TRIGONOMETRIE M3 (C3 : formules d'addition/duplication — référentiel BO 2026) |

S'y ajoute la RÉÉCRITURE de `1NSI-ADGK-ME-001` (M1↔C1/P-ALGO-04,
dichotomie) dont le contenu actuel est contaminé (fiche maths « Dériver une
fonction composée » dans un chapitre NSI).

## Contraintes de production (arbitrage)

- chaque M_i traite exactement C_i de SON chapitre, sous l'autorité
  programme de `PROGRAM_AUTHORITY_2026_2027.md` (TCOMPL/TEXP : programmes
  2019 en vigueur pour 2026-2027 ; 1SPE : programme 2026 ; NSI : 2019) ;
- format Nexus obligatoire (Quand l'utiliser / Méthode pas à pas / Exemple
  entièrement rédigé / Pièges / Vérifier son résultat / S'entraîner) ;
- contenu spécifique à la capacité — gabarit générique, placeholder, TODO,
  hors-programme : INTERDITS ;
- vérification scientifique avant intégration (SymPy/exécution réelle) avec
  rapport par méthode (`audit/reviews/methods/...`) ;
- statut initial `needs_review` — AUCUNE auto-approbation ; la dette de
  review reste visible dans release-strict ;
- production par petits lots (par chapitre), jamais 100 fichiers en un
  commit ; après chaque chapitre : tests ciblés, inventaire read-only,
  delta broken_meta, fail-on-new (NEW_SINCE_PREVIOUS = 0), build si
  disponible, `git diff --check`, commit atomique.
