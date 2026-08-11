---
title: "P03 - Evaluation - Conversion d'encodages texte"
level: "premiere"
sequence_id: "P03"
document_type: "evaluation"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Données textuelles et approximation"
notion: "encodage, UTF-8, Latin-1, ASCII, conversion"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "P-DATA-BASE-05B"
---

# P03 - Evaluation - Conversion d'encodages texte

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-DATA-BASE-05B : convertir un fichier texte dans différents formats d'encodage.

## Prérequis
- Cours et TD sur les encodages ASCII, Latin-1, UTF-8.

## Consignes
- Durée : 15 minutes.
- Documents autorisés : aucun.
- Répondre sur la copie. Justifier chaque réponse.

## Rappel fourni

| Caractère | Latin-1 | UTF-8 |
|---|---|---|
| `é` | 0xE9 | 0xC3 0xA9 |
| `è` | 0xE8 | 0xC3 0xA8 |
| `ê` | 0xEA | 0xC3 0xAA |
| `ç` | 0xE7 | 0xC3 0xA7 |

---

### Question 1 — Identification et conversion (5 points)

Un fichier synthétique `titre.txt` contient le mot `Pêche` et les octets suivants :

```
50 EA 63 68 65
```

1. (1 pt) Dans quel encodage ce fichier est-il écrit ? Justifier.
2. (2 pts) Donner la séquence d'octets obtenue après conversion en UTF-8.
3. (2 pts) Écrire le code Python permettant de convertir un fichier texte dans différents formats d'encodage, ici de l'encodage identifié vers UTF-8.

---

### Question 2 — Analyse d'erreur (5 points)

On exécute le code suivant sur un fichier `note.txt` encodé en Latin-1 contenant `Évaluation` :

```python
with open("note.txt", "r", encoding="utf-8") as f:
    contenu = f.read()
```

1. (2 pts) Ce code provoque-t-il une erreur ? Si oui, laquelle et pourquoi ?
2. (1 pt) Corriger le code pour lire correctement le fichier.
3. (2 pts) Si on remplaçait `encoding="utf-8"` par `encoding="latin-1"` dans les deux opérations (lecture et écriture), expliquer ce qui se passerait. Le fichier serait-il réellement converti ?

---

### Question 3 — Cas limite et justification (5 points)

Un fichier synthétique `data.txt` contient uniquement le texte `Hello 2026` (sans accents).

1. (2 pts) Ce fichier est-il identique en ASCII, Latin-1 et UTF-8 ? Justifier au niveau des octets.
2. (1 pt) Que se passe-t-il si on applique la conversion Latin-1 → UTF-8 sur ce fichier ?
3. (2 pts) On modifie le texte en `Hello 2026 — résumé`. Le tiret cadratin `—` a le point de code U+2014. Peut-on encoder ce texte en Latin-1 ? Justifier et proposer une solution.


## Situation-problème

Un développeur web reçoit un fichier texte contenant des caractères accentués illisibles (mojibake). Il doit identifier l'encodage d'origine et convertir le fichier pour le rendre lisible.

## Activité d’entrée

Ouvrir un fichier texte encodé en Latin-1 dans un éditeur configuré en UTF-8. Observer le résultat et identifier les caractères mal affichés.

## Exemple

Conversion collective du fichier synthétique contenant Noël de Latin-1 vers UTF-8 en traçant les octets.

## Exercices

Exercices de conversion entre encodages ASCII, Latin-1 et UTF-8 sur des fichiers synthétiques.

## Corrigé

Les corrigés détaillés sont dans P03_corrige_conversion_encodages_texte.md.

## Erreurs fréquentes

- EF1 : confondre l'encodage Latin-1 et UTF-8 pour les caractères accentués.
- EF2 : oublier de spécifier le paramètre encoding lors de l'ouverture d'un fichier.
- EF3 : tenter de décoder des octets invalides sans gérer l'exception.


## Remédiation

Exercice de remédiation : convertir manuellement le mot Café en listant les octets Latin-1 puis UTF-8.

## Différenciation

- Socle : exercices de base.
- Standard : exercices complets.
- Expert : exercice d'approfondissement.


### Question 4 — Conversion par lots et vérification (5 points)

On dispose de deux fichiers encodés en Latin-1 :
- `fiche1.txt` contenant `Noël`
- `fiche2.txt` contenant `français`

1. (2 pts) Écrire un programme Python qui convertit ces deux fichiers de Latin-1 vers UTF-8. Les fichiers convertis seront nommés `fiche1_utf8.txt` et `fiche2_utf8.txt`.
2. (1 pt) Calculer le nombre d'octets de `Noël` en Latin-1 et en UTF-8. Justifier la différence.
3. (2 pts) On ajoute un troisième fichier `fiche3.txt` contenant le texte `Tarif : 20 \u20ac`. Ce fichier peut-il être encodé en Latin-1 ? Expliquer pourquoi et indiquer quel encodage utiliser.

---

## Barème

| Question | Points |
|---|---|
| Question 1 | 5 |
| Question 2 | 5 |
| Question 3 | 5 |
| Question 4 | 5 |
| **Total** | **20** |

## Critères de réussite

Octets hexadécimaux corrects pour chaque encodage. Programme de conversion fonctionnel et testé.

## Séance(s) correspondante(s)

Séance dédiée.
