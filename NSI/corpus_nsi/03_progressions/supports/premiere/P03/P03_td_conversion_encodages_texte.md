---
title: "P03 - TD - Conversion d'encodages texte"
level: "premiere"
sequence_id: "P03"
document_type: "td"
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

# P03 - TD - Conversion d'encodages texte

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-DATA-BASE-05B : convertir un fichier texte dans différents formats d'encodage.

## Prérequis
- Connaître la table de correspondance ASCII, Latin-1, UTF-8.
- Savoir lire un code hexadécimal.

## Rappel : table de référence

| Caractère | Latin-1 | UTF-8 |
|---|---|---|
| `é` | 0xE9 | 0xC3 0xA9 |
| `è` | 0xE8 | 0xC3 0xA8 |
| `à` | 0xE0 | 0xC3 0xA0 |
| `ç` | 0xE7 | 0xC3 0xA7 |
| `ù` | 0xF9 | 0xC3 0xB9 |

---

### Exercice 1 — Identifier l'encodage à partir des octets (O1)

Objectif travaillé : O1

Un fichier synthétique `ville.txt` contient le mot `Décès`. On lit les octets suivants en hexadécimal :

```
44 C3 A9 63 C3 A8 73
```

**Questions :**
1. Identifier chaque octet et le caractère correspondant.
2. En déduire l'encodage utilisé (ASCII, Latin-1 ou UTF-8). Justifier.
3. Si le fichier était en Latin-1, quels octets attendrait-on pour le même mot ?

---

### Exercice 2 — Prédire le résultat d’une conversion (O2)

Objectif travaillé : O2

Un fichier synthétique `recette.txt` contient `Crêpe` encodé en Latin-1. Les octets sont :

```
43 72 EA 70 65
```

**Questions :**
1. Vérifier que 0xEA correspond bien à `ê` en Latin-1.
2. Donner la séquence d'octets obtenue après conversion en UTF-8.
3. Écrire le code Python complet pour réaliser cette conversion.
4. Combien d'octets le fichier UTF-8 contiendra-t-il ? Justifier la différence de taille.

---

### Exercice 3 — Justifier sur un cas différent (O3)

Objectif travaillé : O3

Un fichier synthétique `message.txt` contient le texte `Leçon` encodé en UTF-8.

**Questions :**
1. Donner les octets UTF-8 du mot `Leçon`.
2. On souhaite convertir ce fichier en Latin-1. Est-ce possible sans perte ? Justifier.
3. Écrire les octets Latin-1 attendus après conversion.
4. Un autre fichier contient le texte `Prix : 5€`. Peut-on convertir ce fichier d'UTF-8 vers Latin-1 ? Justifier en vérifiant si le caractère `€` (U+20AC) existe en Latin-1.

---

### Exercice 4 — Trouver et corriger l'erreur (O4)

Objectif travaillé : O4

Un élève a écrit le code suivant pour convertir un fichier texte dans différents formats d'encodage (de Latin-1 vers UTF-8) :

```python
with open("donnees.txt", "r", encoding="utf-8") as f:
    contenu = f.read()

with open("donnees_conv.txt", "w", encoding="utf-8") as f:
    f.write(contenu)
```

Le fichier `donnees.txt` contient `Début` encodé en Latin-1. L'exécution provoque une erreur `UnicodeDecodeError`.

**Questions :**
1. Identifier la ligne erronée et expliquer pourquoi l'erreur se produit.
2. Corriger le code.
3. Expliquer ce qui se passerait si on utilisait `errors="replace"` au lieu de corriger l'encodage. Quel caractère apparaîtrait à la place de `é` ?
4. Donner un cas où le code original fonctionnerait sans erreur malgré l'encodage incorrect. Justifier.


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

## Critères de réussite

Octets hexadécimaux corrects pour chaque encodage. Programme de conversion fonctionnel et testé.

## Séance(s) correspondante(s)

Séance dédiée.

### Exercice 5 — Identifier les octets hexadécimaux d'un mot accentué (O1)

Objectif travaillé : O1

On dispose du mot `Noël` encodé dans un fichier texte.

**Questions :**
1. Donner les octets hexadécimaux de `Noël` en Latin-1, sachant que `ë` a le point de code U+00EB.
2. Donner les octets hexadécimaux de `Noël` en UTF-8.
3. Combien d'octets chaque version occupe-t-elle ? Expliquer la différence.

---

### Exercice 6 — Détecter l'encodage d'un fichier inconnu (O2)

Objectif travaillé : O2

On reçoit un fichier `menu.txt` dont on ne connaît pas l'encodage. En lisant les octets bruts, on obtient :

```
43 61 66 C3 A9
```

**Questions :**
1. Tenter de décoder cette séquence en Latin-1. Quel texte obtient-on ?
2. Tenter de décoder cette séquence en UTF-8. Quel texte obtient-on ?
3. Quel est l'encodage correct ? Justifier en analysant la structure des octets.
4. Écrire un programme Python qui lit le fichier en essayant UTF-8 puis Latin-1 en cas d'erreur.

---

### Exercice 7 — Conversion manuelle octet par octet (O1)

Objectif travaillé : O1

Le mot `français` est encodé en UTF-8. Les octets sont :

```
66 72 61 6E C3 A7 61 69 73
```

**Questions :**
1. Identifier chaque octet ou groupe d'octets et le caractère correspondant.
2. Écrire la séquence d'octets équivalente en Latin-1.
3. Vérifier que le nombre total d'octets diminue. De combien ?

---

### Exercice 8 — Prédire une erreur de décodage (O4)

Objectif travaillé : O4

Un fichier `saison.txt` contient le mot `été` encodé en Latin-1. Les octets sont :

```
E9 74 E9
```

On exécute le code suivant :

```python
with open("saison.txt", "r", encoding="utf-8") as f:
    texte = f.read()
```

**Questions :**
1. Pourquoi ce code provoque-t-il une erreur ? Expliquer ce que Python attend après l'octet 0xE9 en UTF-8.
2. Que se passerait-il avec `errors="ignore"` ? Quel texte serait obtenu ?
3. Que se passerait-il avec `errors="replace"` ? Quel texte serait obtenu ?

---

### Exercice 9 — Écrire un script de conversion complet (O2)

On souhaite convertir un fichier `journal.txt` encodé en Latin-1 vers UTF-8, puis vérifier le résultat.

**Questions :**
1. Écrire un programme Python qui effectue la conversion et affiche le nombre d'octets avant et après.
2. Si le fichier contient `Résumé du procès`, combien d'octets le fichier Latin-1 contient-il ? Et le fichier UTF-8 ?
3. Expliquer pourquoi le fichier UTF-8 est plus volumineux.

---

### Exercice 10 — Gérer les caractères hors plage Latin-1 (O3)

Le texte `Le prix est de 15 \u2009\u20ac` contient le symbole euro (U+20AC).

**Questions :**
1. Ce texte peut-il être encodé en ASCII ? Justifier.
2. Ce texte peut-il être encodé en Latin-1 ? Justifier en vérifiant la plage de Latin-1.
3. Ce texte peut-il être encodé en UTF-8 ? Donner les octets UTF-8 du caractère `\u20ac` (3 octets : 0xE2 0x82 0xAC).
4. Écrire le code Python pour sauvegarder ce texte en UTF-8 et expliquer pourquoi c'est le seul encodage viable parmi les trois.

---

### Exercice 11 — Analyser un mojibake (O3)

Un fichier contenant `café` en Latin-1 (octets : `63 61 66 E9`) est ouvert par erreur en UTF-8. L'affichage produit un mojibake.

**Questions :**
1. Expliquer pourquoi l'octet 0xE9 pose problème en UTF-8 (que signifie un octet commençant par `1110` en UTF-8 ?).
2. Si on utilise `errors="replace"`, quel texte sera affiché ?
3. Proposer une méthode pour retrouver le texte original à partir du fichier corrompu. Écrire le code Python correspondant.

---

### Exercice 12 — Conversion par lots de plusieurs fichiers (O2)

On dispose de trois fichiers encodés en Latin-1 dans un dossier `corpus/` :
- `texte1.txt` contenant `àbientôt`
- `texte2.txt` contenant `garçon`
- `texte3.txt` contenant `maïs`

**Questions :**
1. Écrire un programme Python qui convertit ces trois fichiers en UTF-8 dans un dossier `corpus_utf8/`.
2. Pour chaque fichier, calculer le nombre d'octets en Latin-1 et en UTF-8.
3. Le programme doit afficher un message de confirmation pour chaque fichier converti, indiquant le nom du fichier et la variation de taille.

Critère de validation : chaque réponse est vérifiable par un contrôle explicite.

## Exercices numérotés

Voir les exercices 1 à 8 ci-dessus.

