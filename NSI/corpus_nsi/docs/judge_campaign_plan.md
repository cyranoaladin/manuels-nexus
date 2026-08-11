# Plan de campagne de jugement — capacités NSI

**Statut** : PLAN (lecture seule — aucun verdict produit)
**Décision** : appartient au lead
**Date** : 2026-07-05
**Pré-requis** : PR C (#67) et PR A6 (#68) mergées

---

## a) Inventaire des capacités à juger

**Source** : `python -m scripts.check_program_coverage` → `coverage.md`

### Résumé

| Statut | Nombre |
|---|---|
| needs_review | 111 |
| partial | 3 |
| **Total à juger** | **114** |

### Par séquence

#### Première (55 capacités)

| Séquence | needs_review | partial | Capacités |
|---|---|---|---|
| P00 | 1 | 0 | P-LANG-01 |
| P01 | 1 | 0 | P-DATA-BASE-01 |
| P02 | 3 | 0 | P-DATA-BASE-02A, 02B, 04 |
| P03 | 3 | 0 | P-DATA-BASE-03, 05A, 05B |
| P04 | 8 | 0 | P-DATA-CONSTR-01, 02A-D, 03A-C |
| P05 | 2 | 0 | P-TABLE-01, 02 |
| P06 | 2 | 0 | P-TABLE-03, 04 |
| P07 | 6 | 0 | P-LANG-02, 03A-C, 04, 05 |
| P08 | 9 | 0 | P-IHM-01A-B, 02, 03A-C, 04A-C |
| P09 | 5 | 0 | P-ARCH-01A-B, 03A-C |
| P10 | 5 | 0 | P-ARCH-02A-C, 04A-B |
| P11 | 2 | 0 | P-ALGO-01A-B |
| P12 | 4 | 0 | P-ALGO-02A-D |
| P13 | 3 | 0 | P-ALGO-03, 04, 05 |
| P14 | 1 | 0 | P-HIST-01 |

#### Terminale (59 capacités)

| Séquence | needs_review | partial | Capacités |
|---|---|---|---|
| T00 | 1 | 0 | T-LANG-03A |
| T01 | 3 | 0 | T-STRUCT-01A-C |
| T02 | 1 | 1 | T-STRUCT-02A (nr), 02B (partial) |
| T03 | 3 | 0 | T-STRUCT-03A-C |
| T04 | 2 | 0 | T-LANG-02A-B |
| T05 | 5 | 0 | T-STRUCT-04A-B, T-ALGO-01A-B, 01D |
| T06 | 2 | 1 | T-ALGO-01E-F (nr), 01C (partial) |
| T07 | 4 | 0 | T-STRUCT-05A-D |
| T08 | 3 | 1 | T-ALGO-02B-D (nr), 02A (partial) |
| T09 | 4 | 0 | T-BDD-01A-C, 02 |
| T10 | 8 | 0 | T-BDD-03A-H |
| T11 | 4 | 0 | T-ARCH-01, 02A-C |
| T12 | 1 | 0 | T-ARCH-03 |
| T13 | 2 | 0 | T-ARCH-04A-B |
| T14 | 5 | 0 | T-LANG-03B-C, 04A-B, 05 |
| T15 | 3 | 0 | T-LANG-01A-C |
| T16 | 1 | 0 | T-ALGO-03 |
| T17 | 1 | 0 | T-ALGO-04 |
| T18 | 1 | 0 | T-ALGO-05 |
| T19 | 2 | 0 | T-HIST-01A-B |

### Fichiers d'évidence par capacité

Toutes les 111 capacités needs_review disposent des 4 types d'évidence
(cours, td/tp, eval, corrigé). Les 3 partial ont des preuves manquantes :

| Capacité | Preuves présentes | Preuves manquantes |
|---|---|---|
| T-STRUCT-02B | cours, td, eval | corrigé, tp, trace |
| T-ALGO-01C | tp, eval, corrigé | cours, td, trace |
| T-ALGO-02A | cours, trace, td, tp, eval, corrigé | séquence évaluée complète (application seule) |

---

## b) Backlog substance pré-jugement (résidus PR C)

### 1. T04 cours — section T-LANG-02B

**Situation** : Le cours T04 (récursivité) déclare T-LANG-02B en frontmatter.
Le corps contient du contenu sur la terminaison (preuve par variant décroissant)
et la trace d'appels (pile d'appels, `Suivre les appels de somme([4,1,3])`),
mais aucune section titrée `#méthode — analyser un appel récursif`.

**Recommandation** : CONSERVER la déclaration. Le contenu existant (terminaison,
trace/pile d'appels, variant décroissant) exerce réellement T-LANG-02B. Ajouter
une ancre `#methode-analyser-un-appel-recursif` devant le contenu existant
améliorerait le verdict du juge mais n'est pas bloquant — le contenu est là.

**Décision lead** : produire la section titrée OU accepter le contenu actuel.

### 2. Enrichissement des 2 exercices « templés »

**P-DATA-CONSTR-02D** (itérer sur tableau) — Exercice 2 du TD P04 :
« expliquer liste de relevés à partir de `[18, 20, 19]` → 19 ».
L'exercice implique le calcul de la moyenne (itération), mais ne montre
pas de boucle `for` explicite. L'erreur fréquente EF2 (« Parcourir les
indices quand les valeurs suffisent ») confirme l'intention.

**Enrichissement optionnel** : ajouter à l'énoncé « Écrire une boucle `for`
qui calcule la moyenne des relevés » — rendrait le verdict plus certain.

**T-LANG-02B** (analyser programme récursif) — Exercice 4 du TD T04 :
« corriger terminaison pour `n` décroît vers 0 → preuve de terminaison ».
L'exercice analyse un programme récursif (terminaison), mais ne demande
pas explicitement de tracer l'arbre d'appels.

**Enrichissement optionnel** : ajouter « Tracer les 3 premiers appels
récursifs avec la valeur de `n` à chaque appel » — rendrait le verdict
plus solide.

**Décision lead** : enrichir AVANT la campagne (meilleur taux de covered)
OU lancer tel quel (le juge décidera).

---

## c) Protocole de jugement

### Entrée par capacité

Pour chaque capacité, le juge reçoit :

```
CAPACITÉ : {id} — {libellé officiel}
(source : programme_nsi_2019.yaml)

ÉVIDENCE COURS :
{extrait ancré du fichier cours, sections contenant l'ID ou le contenu lié}

ÉVIDENCE TD/TP :
{extrait ancré du fichier td/tp, exercice(s) contenant l'ID}

ÉVIDENCE ÉVALUATION :
{extrait ancré du fichier eval, question(s) contenant l'ID}
```

### Sortie attendue (JSON conforme au schéma existant)

```json
{
  "capacity_id": "P-DATA-BASE-01",
  "present": true,
  "proof_course": "#a-savoir-representation-en-base-2",
  "proof_practice": "#exercice-2-conversion-decimale-vers-binaire",
  "proof_correction": "#corrige-exercice-2",
  "comment": "Le cours explique la conversion, le TD la fait pratiquer, le corrigé la détaille."
}
```

### Contraintes

- `proof_*` : ancres `^#.+` pointant vers des titres **existants** dans les fichiers
- `present: true` interdit sans ancre existante (`check_substance_anchors` le vérifie)
- `present: false` autorisé avec `comment` expliquant le manque
- Verdicts en `needs_review` (pas en `covered`) tant que le lead n'a pas validé le modèle de juge
- Gate de sortie : `check_substance_anchors` PASS sur les nouveaux verdicts

---

## d) Options de juge — tableau coût/durée/qualité

### Mesures réelles

**Tokens moyens par dossier d'évidence** (3 échantillons) :
- P04 (8 caps, 15 fichiers) : ~4 632 tokens/cap
- T06 (3 caps, 10 fichiers) : ~3 076 tokens/cap
- P08 (9 caps, 12 fichiers) : ~1 654 tokens/cap
- **Moyenne** : ~3 120 tokens input / capacité

**Qwen2.5:1.5b local CPU** (1 verdict réel mesuré) :
- Durée : 12s / verdict
- Qualité : JSON minimal, pas d'ancres, verdicts incorrects (proof_practice=false
  malgré évidence présente). **Inutilisable** pour la campagne.

### Comparatif

| Option | Modèle | Coût | Durée estimée | Qualité |
|---|---|---|---|---|
| **(1) Recommandée** | Sonnet 4.6 Batch API | ~$0.76 (114 caps × ~3.1k in + ~500 out, tarif batch 50%) | ~10 min (batch async) | Haute — ancres vérifiables, JSON conforme |
| (2) Local CPU | Qwen2.5:1.5b | $0 | ~23 min (114 × 12s) | **Insuffisante** — pas d'ancres, verdicts faux |
| (3) Hybride | Haiku 4.5 tri → Sonnet 4.6 sur present:true | ~$0.40-0.60 | ~15 min | Bonne — Haiku filtre les absent, Sonnet confirme |

### Détail coût option (1) — Sonnet 4.6 Batch

```
Input :  114 caps × 3 120 tokens = 355 680 tokens × $1.50/MTok = $0.53
Output : 114 caps ×   500 tokens =  57 000 tokens × $4.00/MTok = $0.23
Total :  $0.76
```

### Recommandation

**Option (1)** — Sonnet 4.6 Batch API. Coût négligeable (<$1), qualité éprouvée
sur les 30 verdicts existants (`check_substance_anchors` PASS), durée ~10 min.
L'option Qwen locale est éliminée par la mesure (verdicts incorrects).
L'option hybride économise ~30% mais ajoute de la complexité sans gain qualitatif.

---

## e) Critère de sortie

### Après campagne de jugement

1. Exécuter la campagne avec le juge choisi par le lead
2. Vérifier `check_substance_anchors` PASS sur tous les nouveaux verdicts
3. Compter les verdicts `present: true` → `covered`
4. Lister les `present: false` avec leur manque précis (proof manquant)

### Objectif réaliste

Sur 114 capacités :
- **111 needs_review** avec évidence complète (cours+td+eval+corrigé) → fort taux de `covered` attendu
- **3 partial** avec preuves manquantes → `present: false` probable avec diagnostic

### Flip RELEASE_READY

**UNIQUEMENT** en PR dédiée lead, APRÈS :
- Campagne terminée
- covered = X documenté
- Non-covered listés avec manque précis
- Décision lead explicite

---

## Annexe : commandes de référence

```bash
# Générer l'inventaire
python -m scripts.check_program_coverage

# Vérifier les verdicts existants
python -m scripts.check_substance_anchors

# Estimer les tokens d'un dossier
wc -c 03_progressions/supports/premiere/P04/*.md | tail -1

# Alignment gate
python -m scripts.check_first_batch_alignment

# Tests complets
python -m pytest tests/ -x -q
```
