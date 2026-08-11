---
title: "P03 - Cours - Conversion d'encodages texte"
level: "premiere"
sequence_id: "P03"
document_type: "cours"
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

# P03 - Cours - Conversion d'encodages texte

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-DATA-BASE-05B : convertir un fichier texte dans différents formats d'encodage.

## Prérequis
- Connaître la notion de bit et d'octet.
- Savoir ouvrir et lire un fichier texte en Python.
- Distinguer caractère et octet.
- Connaître la table ASCII (0-127).

## Séance(s) correspondante(s)
- P03-S1 à P03-S5 : support rattaché aux séances prêtes de la progression.

## Situation-problème concrète
Un fichier texte contenant des caractères accentués (menu d’un restaurant) s'affiche avec des symboles incompréhensibles (mojibake) lorsqu'on l'ouvre sur un autre ordinateur. Comment convertir un fichier texte dans différents formats d'encodage pour garantir un affichage correct ?

## Activité d’entrée
1. Ouvrir un fichier synthétique `menu.txt` contenant « Entrée : crème brûlée » dans un éditeur hexadécimal.
2. Observer les octets correspondant au caractère `é`.
3. Comparer l'affichage du même fichier ouvert en Latin-1 puis en UTF-8.
4. Constater le problème de mojibake.

## Définitions et formalisation

### Définition D1 : ASCII (American Standard Code for Information Interchange)
Encodage sur 7 bits (128 caractères). Chaque caractère est représenté par un octet dont le bit de poids fort est 0. Couvre les lettres non accentuées, chiffres et symboles courants. Exemple : `A` = 0x41, `z` = 0x7A.

### Définition D2 : Latin-1 (ISO-8859-1)
Extension de l'ASCII sur 8 bits (256 caractères). Les 128 premiers codes sont identiques à l'ASCII. Les codes 128-255 couvrent les caractères accentués des langues d'Europe occidentale. Chaque caractère occupe exactement 1 octet.

- Exemple : `é` = 0xE9 (233 en décimal), `è` = 0xE8, `ù` = 0xF9.

### Définition D3 : UTF-8 (Unicode Transformation Format - 8 bits)
Encodage à longueur variable compatible avec ASCII. Un caractère occupe 1 à 4 octets selon son point de code Unicode.

| Plage de points de code | Octets | Préfixe binaire |
|---|---|---|
| U+0000 à U+007F | 1 | `0ddddddd` |
| U+0080 à U+07FF | 2 | `110ddddd 10dddddd` |
| U+0800 à U+FFFF | 3 | `1110dddd 10dddddd 10dddddd` |
| U+10000 à U+10FFFF | 4 | `11110ddd 10dddddd 10dddddd 10dddddd` |

- Exemple : `é` (U+00E9) en UTF-8 = 0xC3 0xA9 (2 octets).

### Définition D4 : Mojibake
Affichage de caractères incohérents causé par une discordance entre l'encodage utilisé pour écrire le fichier et celui utilisé pour le lire. Exemple : `é` encodé en UTF-8 (0xC3 0xA9) lu en Latin-1 donne `Ã©`.

## Comparaison au niveau des octets

| Caractère | Point de code | ASCII | Latin-1 | UTF-8 |
|---|---|---|---|---|
| `A` | U+0041 | 0x41 (1 octet) | 0x41 (1 octet) | 0x41 (1 octet) |
| `é` | U+00E9 | -- (absent) | 0xE9 (1 octet) | 0xC3 0xA9 (2 octets) |
| `è` | U+00E8 | -- (absent) | 0xE8 (1 octet) | 0xC3 0xA8 (2 octets) |
| `ù` | U+00F9 | -- (absent) | 0xF9 (1 octet) | 0xC3 0xB9 (2 octets) |

Observation : les caractères ASCII (0-127) ont le même encodage dans les trois systèmes. Les caractères accentués diffèrent entre Latin-1 (1 octet) et UTF-8 (2 octets ou plus).

## Méthode de conversion en Python

Pour convertir un fichier texte dans différents formats d'encodage en Python, on procède en deux étapes :

1. **Lire** le fichier avec l'encodage source.
2. **Écrire** le contenu dans un nouveau fichier avec l'encodage cible.

### Méthode avec `open()`

```python
# Lire un fichier encodé en Latin-1
with open("fichier_latin1.txt", "r", encoding="latin-1") as f:
    contenu = f.read()

# Écrire le même contenu en UTF-8
with open("fichier_utf8.txt", "w", encoding="utf-8") as f:
    f.write(contenu)
```

### Méthode avec `.encode()` et `.decode()`

```python
# Lire les octets bruts
with open("fichier_latin1.txt", "rb") as f:
    octets = f.read()

# Décoder depuis Latin-1 puis encoder en UTF-8
texte = octets.decode("latin-1")
octets_utf8 = texte.encode("utf-8")

# Écrire les octets UTF-8
with open("fichier_utf8.txt", "wb") as f:
    f.write(octets_utf8)
```

## Exemples corrigés

### Exemple 1 — Identifier l'encodage d'un octet

On observe l'octet `0xE9` dans un fichier. En Latin-1, cet octet correspond au caractere `e accent aigu` (point de code U+00E9). En UTF-8, l'octet `0xE9` seul est invalide car il commence par le prefixe `1110`, qui annonce une sequence de 3 octets. Le decodage echoue si les octets de continuation sont absents. Ce cas illustre la difference fondamentale entre un encodage a longueur fixe (Latin-1, 1 octet par caractere) et un encodage a longueur variable (UTF-8, 1 a 4 octets par caractere).

### Exemple 2 — Convertir une chaine avec des caracteres accentues

La chaine `"Resume"` contient le caractere `e accent aigu` (point de code U+00E9). En Latin-1, la representation hexadecimale est `52 E9 73 75 6D E9` (6 octets). En UTF-8, la representation devient `52 C3 A9 73 75 6D C3 A9` (8 octets) car chaque `e accent aigu` est encode sur 2 octets au lieu d'un seul. Le decodage correct necessite de connaitre l'encodage source pour interpreter chaque octet ou sequence d'octets comme le bon caractere.

### Exemple 3 — Detecter et corriger un mojibake

Un fichier UTF-8 contenant `"Entree"` est ouvert par erreur en Latin-1. Les octets UTF-8 `C3 A9` (qui representent le caractere `e accent aigu`, point de code U+00E9) sont interpretes comme deux caracteres Latin-1 distincts : `A tilde` (0xC3) et `copyright` (0xA9). Le resultat affiche est un mojibake. Pour corriger, il faut re-encoder les octets bruts en utilisant le bon encodage source (UTF-8) puis ecrire dans l'encodage cible souhaite.

### Exemple corrigé complet

**Enonce** : Un fichier synthetique `produits.txt` contient la ligne `Cafe creme` encode en Latin-1. Convertir ce fichier en UTF-8.

**Étape 1** : Identifier l'encodage source. Le fichier est en Latin-1, donc `é` = 0xE9 et `è` = 0xE8.

**Étape 2** : Lire avec le bon encodage.

```python
with open("produits.txt", "r", encoding="latin-1") as f:
    contenu = f.read()
print(contenu)  # Affiche : Café crème
```

**Étape 3** : Écrire en UTF-8.

```python
with open("produits_utf8.txt", "w", encoding="utf-8") as f:
    f.write(contenu)
```

**Vérification** : Lire le fichier produit et examiner les octets.

```python
with open("produits_utf8.txt", "rb") as f:
    octets = f.read()
print(octets)
# b'Caf\xc3\xa9 cr\xc3\xa8me'
# é = 0xC3 0xA9, è = 0xC3 0xA8 → UTF-8 correct
```

## Gestion des erreurs : UnicodeDecodeError

Lorsque l'on tente de décoder un fichier avec le mauvais encodage, Python lève une exception `UnicodeDecodeError`.

```python
# Fichier encodé en Latin-1, lu par erreur en UTF-8
try:
    with open("fichier_latin1.txt", "r", encoding="utf-8") as f:
        contenu = f.read()
except UnicodeDecodeError as e:
    print(f"Erreur de décodage : {e}")
    # Stratégie : réessayer avec l'encodage correct
    with open("fichier_latin1.txt", "r", encoding="latin-1") as f:
        contenu = f.read()
```

Le paramètre `errors` permet de gérer les cas limites :
- `errors="strict"` : lève une exception (comportement par défaut).
- `errors="replace"` : remplace les octets invalides par `�` (U+FFFD).
- `errors="ignore"` : supprime silencieusement les octets invalides.

## Cas limite
- Un fichier ne contenant que des caractères ASCII (0-127) donne exactement les mêmes octets en ASCII, Latin-1 et UTF-8. La conversion ne modifie rien.
- Un fichier UTF-8 contenant des caractères hors Latin-1 (par exemple `€`, U+20AC) ne peut pas être converti en Latin-1 sans perte.

## Résumé
Pour convertir un fichier texte dans différents formats d'encodage, il faut : (1) identifier l'encodage source, (2) lire le fichier avec cet encodage, (3) écrire le contenu avec l'encodage cible. Les erreurs de mojibake proviennent d’une discordance entre encodage d'écriture et de lecture.


## Exercices

### Exercice 1
Donner la représentation hexadécimale de la chaîne `"Noël"` en Latin-1 puis en UTF-8.

### Exercice 2
Un fichier contient les octets `42 6F 6E 6A 6F 75 72`. Est-il en ASCII, Latin-1 ou UTF-8 ? Justifier.

### Exercice 3
Écrire un programme Python qui lit un fichier `entree.txt` encodé en Latin-1 et le convertit en UTF-8 dans `sortie.txt`.

### Exercice 4
Un fichier UTF-8 contient le caractère `€` (U+20AC). Que se passe-t-il si on tente de le lire en Latin-1 ? Expliquer.

## Corrigé

### Corrigé exercice 1

Le résultat attendu pour `"Noël"` est :
- Latin-1 : `4E 6F EB 6C` (ë = 0xEB en Latin-1)
- UTF-8 : `4E 6F C3 AB 6C` (ë = 0xC3 0xAB en UTF-8)

### Corrigé exercice 2
Tous les octets sont dans la plage 0x00-0x7F (ASCII). La chaîne `"Bonjour"` est identique en ASCII, Latin-1 et UTF-8 car elle ne contient que des caractères ASCII.

### Corrigé exercice 3

La conversion donne `[0x4E, 0x6F, 0xC3, 0xAB, 0x6C]` en UTF-8. Le fichier `sortie.txt` encodé en UTF-8 contient donc les octets suivants :

```python
with open("entree.txt", "r", encoding="latin-1") as f:
    contenu = f.read()
with open("sortie.txt", "w", encoding="utf-8") as f:
    f.write(contenu)
```

### Corrigé exercice 4
Le caractère `€` est encodé sur 3 octets en UTF-8 : `E2 82 AC`. En Latin-1, ces 3 octets seraient interprétés comme 3 caractères distincts : `â`, `‚`, `¬`. C'est un exemple de mojibake.

## Erreurs fréquentes

- EF1 : confondre l'encodage Latin-1 et UTF-8 pour les caractères accentués.
- EF2 : oublier de spécifier le paramètre encoding lors de l'ouverture d'un fichier.
- EF3 : tenter de décoder des octets invalides sans gérer l'exception.


## Remédiation

- Si confusion encodage/contenu : reprendre le tableau comparatif ASCII/Latin-1/UTF-8 avec le même caractère `é`.
- Si erreur de conversion : tracer manuellement les octets d'un caractère accentué dans chaque encodage.
- Si mojibake non détecté : comparer visuellement la sortie attendue avec la sortie obtenue.

## Différenciation

- Socle : convertir un fichier ASCII (aucune difficulté, les encodages coïncident).
- Standard : convertir un fichier Latin-1 avec accents vers UTF-8.
- Expert : détecter automatiquement l'encodage d'un fichier inconnu et le convertir.

## Critères de réussite

- Identifier correctement l'encodage source d'un fichier à partir de ses octets.
- Écrire un programme de conversion qui produit un fichier lisible sans mojibake.
- Expliquer la différence entre ASCII, Latin-1 et UTF-8 en termes d'octets.
- Gérer les erreurs de décodage avec le paramètre `errors` de la fonction `open()`.
- Distinguer les cas où la conversion modifie les octets de ceux où elle les conserve.
