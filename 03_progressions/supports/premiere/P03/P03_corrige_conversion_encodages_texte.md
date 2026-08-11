---
title: "P03 - Corrige - Conversion d'encodages texte"
level: "premiere"
sequence_id: "P03"
document_type: "corrige"
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

# P03 - Corrige - Conversion d'encodages texte

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-DATA-BASE-05B : convertir un fichier texte dans différents formats d'encodage.

## Prérequis
- Avoir passé l'évaluation correspondante.

---

## Corrigé de l'évaluation

### Question 1 — Identification et conversion (5 points)

Exercice fondamental portant sur la reconnaissance d'encodage et la conversion manuelle.

**1. (1 pt)** Le fichier est encodé en **Latin-1** (ISO-8859-1).

Justification : l'octet 0xEA correspond au caractère `ê` en Latin-1 et occupe un seul octet. En UTF-8, `ê` serait encodé sur 2 octets (0xC3 0xAA). Puisque 0xEA apparaît seul (suivi de 0x63 = `c`), il ne s'agit pas d'UTF-8.

**2. (2 pts)** Conversion en UTF-8 :

| Caractère | Latin-1 | UTF-8 |
|---|---|---|
| `P` | 0x50 | 0x50 |
| `ê` | 0xEA | 0xC3 0xAA |
| `c` | 0x63 | 0x63 |
| `h` | 0x68 | 0x68 |
| `e` | 0x65 | 0x65 |

Séquence UTF-8 : `50 C3 AA 63 68 65`

**3. (2 pts)** Code Python pour convertir un fichier texte dans différents formats d'encodage :

```python
with open("titre.txt", "r", encoding="latin-1") as f:
    contenu = f.read()

with open("titre_utf8.txt", "w", encoding="utf-8") as f:
    f.write(contenu)
```

---

### Question 2 — Analyse d'erreur (5 points)

Exercice de diagnostic portant sur les exceptions de décodage.

**1. (2 pts)** Oui, ce code provoque une **`UnicodeDecodeError`**.

Explication : le fichier `note.txt` est encodé en Latin-1. Le caractère `É` est stocké comme l'octet 0xC9 en Latin-1. Lorsque Python tente de décoder cet octet en UTF-8, il attend une séquence multi-octets commençant par 0xC9 (qui en UTF-8 signifie « début d’une séquence de 2 octets »), mais l'octet suivant (0x76 = `v`) ne commence pas par `10` comme l'exige UTF-8. Python lève donc une `UnicodeDecodeError`.

**2. (1 pt)** Code corrigé :

```python
with open("note.txt", "r", encoding="latin-1") as f:
    contenu = f.read()
```

**3. (2 pts)** Si on utilise `encoding="latin-1"` pour la lecture ET `encoding="latin-1"` pour l'écriture, le fichier est lu correctement puis réécrit dans le même encodage. Il n'y a **aucune conversion** : le fichier de sortie est toujours en Latin-1, identique au fichier d'entrée. Pour convertir, il faut utiliser un encodage **différent** en écriture (par exemple `encoding="utf-8"`).

---

### Question 3 — Cas limite et justification (5 points)

Exercice avancé sur les limites de chaque encodage.

**1. (2 pts)** Oui, le fichier est **identique** en ASCII, Latin-1 et UTF-8.

Justification : tous les caractères de `Hello 2026` ont des points de code entre U+0020 et U+007A, donc dans la plage ASCII (0x00-0x7F). Or :
- ASCII encode ces caractères sur 1 octet chacun.
- Latin-1 est une extension d'ASCII : les 128 premiers codes sont identiques.
- UTF-8 est compatible ASCII : les caractères 0x00-0x7F sont encodés sur 1 octet, identique à ASCII.

Les octets sont donc strictement les mêmes : `48 65 6C 6C 6F`.

**2. (1 pt)** La conversion Latin-1 → UTF-8 ne modifie **rien**. Le fichier de sortie contient exactement les mêmes octets que le fichier d'entrée, car tous les caractères sont dans la plage ASCII commune.

**3. (2 pts)** Le tiret cadratin `—` (U+2014) **ne peut pas** être encodé en Latin-1.

Justification : Latin-1 couvre uniquement les points de code U+0000 à U+00FF. Le point de code U+2014 est hors de cette plage. Python lèverait une `UnicodeEncodeError`.

Solution : utiliser UTF-8, qui peut encoder tous les caractères Unicode. Le tiret cadratin `—` (U+2014) est encodé en UTF-8 sur 3 octets : 0xE2 0x80 0x94.

```python
with open("data.txt", "w", encoding="utf-8") as f:
    f.write("Hello 2026 — résumé")
```

---

### Question 4 — Conversion par lots et vérification (5 points)

Exercice de programmation portant sur la conversion automatisée de fichiers.

**1. (2 pts)** Programme Python :

```python
fichiers = [("fiche1.txt", "fiche1_utf8.txt"),
            ("fiche2.txt", "fiche2_utf8.txt")]

for source, dest in fichiers:
    with open(source, "r", encoding="latin-1") as f:
        contenu = f.read()
    with open(dest, "w", encoding="utf-8") as f:
        f.write(contenu)
```

**2. (1 pt)** Le mot `Noël` :
- En Latin-1 : `N` (0x4E), `o` (0x6F), `ë` (0xEB), `l` (0x6C) = **4 octets**.
- En UTF-8 : `N` (0x4E), `o` (0x6F), `ë` (0xC3 0xAB), `l` (0x6C) = **5 octets**.

La différence vient du caractère `ë` (U+00EB) qui passe de 1 octet en Latin-1 à 2 octets en UTF-8, car son point de code est supérieur à U+007F.

**3. (2 pts)** Le caractère `€` a le point de code U+20AC, qui dépasse la plage couverte par Latin-1 (U+0000 à U+00FF). Ce texte **ne peut pas** être encodé en Latin-1. Python lèverait une `UnicodeEncodeError`. Il faut utiliser **UTF-8**, qui couvre l'intégralité d'Unicode et encode `€` sur 3 octets (0xE2 0x82 0xAC).

---

### Exemple corrigé 5 — Compatibilité ASCII entre encodages

Le texte `Hello` contient uniquement des caractères ASCII (points de code U+0048 à U+006F). Les octets sont identiques en ASCII, Latin-1 et UTF-8, car ces trois encodages partagent la meme plage pour les 128 premiers caractères. La conversion ne modifie aucun octet.

---

## Corrigé du TD

### Corrigé exercice 1 — Identifier l'encodage à partir des octets

**Méthode** : On décompose chaque octet ou groupe d'octets en identifiant les séquences multi-octets caractéristiques de l'UTF-8 (octets commençant par 110ddddd suivis de 10dddddx).

**1.** Décomposition des octets :

| Octet(s) | Caractère |
|---|---|
| 0x44 | `D` |
| 0xC3 0xA9 | `é` (UTF-8) |
| 0x63 | `c` |
| 0xC3 0xA8 | `è` (UTF-8) |
| 0x73 | `s` |

Le mot est `Décès`.

**2.** L'encodage est **UTF-8**. Justification : les caractères accentués `é` et `è` sont encodés sur 2 octets chacun (0xC3 0xA9 et 0xC3 0xA8), ce qui est la signature UTF-8. En Latin-1, ils n'occuperaient qu'un seul octet chacun.

**3.** En Latin-1, les octets seraient : `44 E9 63 E8 73` (5 octets au lieu de 7).

**Résultat** : Le mot est `Décès`, encodé en UTF-8. En Latin-1, la séquence serait plus courte (5 octets au lieu de 7).



### Corrigé exercice 2 — Prédire le résultat d’une conversion

**Méthode** : On vérifie la correspondance Latin-1 de chaque octet, puis on applique les règles de conversion vers UTF-8 caractère par caractère.

**1.** En Latin-1, 0xEA correspond au point de code U+00EA, qui est bien le caractère `ê`. Confirmé.

**2.** Conversion en UTF-8 :
- `C` (0x43) → 0x43
- `r` (0x72) → 0x72
- `ê` (0xEA) → 0xC3 0xAA
- `p` (0x70) → 0x70
- `e` (0x65) → 0x65

Séquence UTF-8 : `43 72 C3 AA 70 65`

**3.** Code Python :

```python
with open("recette.txt", "r", encoding="latin-1") as f:
    contenu = f.read()

with open("recette_utf8.txt", "w", encoding="utf-8") as f:
    f.write(contenu)
```

**4.** Le fichier Latin-1 fait 5 octets. Le fichier UTF-8 fait 6 octets. Différence : `ê` passe de 1 octet (Latin-1) à 2 octets (UTF-8), soit +1 octet.

**Résultat** : La séquence UTF-8 obtenue est `43 72 C3 AA 70 65` (6 octets), soit un octet de plus que la version Latin-1.



### Corrigé exercice 3 — Justifier sur un cas différent

**Méthode** : On calcule les octets UTF-8 du mot, puis on vérifie si chaque caractère a un point de code dans la plage Latin-1 (U+0000 à U+00FF) pour déterminer si la conversion inverse est possible.

**1.** Octets UTF-8 de `Leçon` :
- `L` → 0x4C
- `e` → 0x65
- `ç` → 0xC3 0xA7
- `o` → 0x6F
- `n` → 0x6E

Séquence : `4C 65 C3 A7 6F 6E`

**2.** Oui, la conversion UTF-8 → Latin-1 est possible car tous les caractères (`L`, `e`, `ç`, `o`, `n`) ont des points de code dans la plage U+0000 à U+00FF couverte par Latin-1.

**3.** Octets Latin-1 : `4C 65 E7 6F 6E` (5 octets).

**4.** Le caractère `€` a le point de code U+20AC, qui est **hors** de la plage Latin-1 (U+0000 à U+00FF). La conversion UTF-8 → Latin-1 est donc **impossible** sans perte pour ce texte. Python lèverait une `UnicodeEncodeError`.

**Résultat** : La conversion de `Leçon` est possible (octets Latin-1 : `4C 65 E7 6F 6E`), mais celle d'un texte contenant `€` est impossible car U+20AC dépasse la plage Latin-1.



### Corrigé exercice 4 — Trouver et corriger l'erreur

**Méthode** : On compare l'encodage déclaré dans le code avec l'encodage réel du fichier pour identifier l'incohérence, puis on corrige l'argument `encoding`.

**1.** La ligne erronée est la première instruction `open()` :
```python
with open("donnees.txt", "r", encoding="utf-8") as f:
```
Le fichier est encodé en Latin-1, mais le code tente de le lire en UTF-8. L'octet 0xE9 (`é` en Latin-1) n'est pas une séquence UTF-8 valide dans ce contexte, ce qui provoque une `UnicodeDecodeError`.

**2.** Code corrigé :

```python
with open("donnees.txt", "r", encoding="latin-1") as f:
    contenu = f.read()

with open("donnees_conv.txt", "w", encoding="utf-8") as f:
    f.write(contenu)
```

**3.** Avec `errors="replace"`, Python remplacerait chaque octet invalide par le caractère de remplacement `�` (U+FFFD). Le `é` de `Début` serait remplacé par `�`, donnant `D�but`. L'information est perdue.

**4.** Le code original fonctionnerait sans erreur si le fichier ne contenait que des caractères ASCII (0x00-0x7F), par exemple `Debut` sans accent. En effet, les octets ASCII sont valides en UTF-8 comme en Latin-1. La « conversion » ne changerait rien, mais aucune erreur ne serait levée.

**Résultat** : Le code corrigé lit en `latin-1` et écrit en `utf-8`, produisant une conversion correcte du fichier `donnees.txt`.


## Situation-problème

Un développeur web reçoit un fichier texte contenant des caractères accentués illisibles (mojibake). Il doit identifier l'encodage d'origine et convertir le fichier pour le rendre lisible.

## Activité d’entrée

Ouvrir un fichier texte encodé en Latin-1 dans un éditeur configuré en UTF-8. Observer le résultat et identifier les caractères mal affichés.

## Exemple

Conversion collective du fichier synthétique contenant Noël de Latin-1 vers UTF-8 en traçant les octets.

## Exercices

Exercices de conversion entre encodages ASCII, Latin-1 et UTF-8 sur des fichiers synthétiques.

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

### Exemple corrigé 1 — Conversion Latin-1 vers UTF-8 du mot "Café"

Le mot `Café` en Latin-1 correspond aux octets `43 61 66 E9` (4 octets). En UTF-8, le caractère `é` (U+00E9) est encodé sur 2 octets : 0xC3 0xA9. La séquence UTF-8 est donc `43 61 66 C3 A9` (5 octets). La conversion ajoute un octet car `é` dépasse la plage ASCII.

### Corrigé exercice 5 — Identifier les octets hexadécimaux d'un mot accentué

**Méthode** : On convertit chaque caractère en son code hexadécimal dans l'encodage cible (Latin-1 puis UTF-8), en appliquant les règles d'encodage multi-octets pour les caractères au-delà de U+007F.

**1.** Octets Latin-1 de `Noël` :
- `N` → 0x4E
- `o` → 0x6F
- `ë` (U+00EB) → 0xEB
- `l` → 0x6C

Séquence : `4E 6F EB 6C` (4 octets).

**2.** Octets UTF-8 de `Noël` :
- `N` → 0x4E
- `o` → 0x6F
- `ë` (U+00EB) → 0xC3 0xAB
- `l` → 0x6C

Séquence : `4E 6F C3 AB 6C` (5 octets).

**3.** La version Latin-1 occupe 4 octets, la version UTF-8 occupe 5 octets. La différence vient du caractère `ë` qui passe de 1 octet en Latin-1 à 2 octets en UTF-8. Les caractères ASCII (`N`, `o`, `l`) occupent 1 octet dans les deux encodages.

**Résultat** : `Noël` occupe 4 octets en Latin-1 (`4E 6F EB 6C`) et 5 octets en UTF-8 (`4E 6F C3 AB 6C`).

---



### Corrigé exercice 6 — Détecter l'encodage d'un fichier inconnu

**Méthode** : On tente de décoder les octets avec chaque encodage candidat (Latin-1, UTF-8) et on vérifie lequel produit un texte cohérent en analysant la structure des séquences multi-octets.

**1.** En Latin-1, les octets `43 61 66 C3 A9` donnent : `C` (0x43), `a` (0x61), `f` (0x66), `Ã` (0xC3), `©` (0xA9). Le texte serait `cafÃ©`, ce qui n'a pas de sens.

**2.** En UTF-8, les octets donnent : `C` (0x43), `a` (0x61), `f` (0x66), `é` (0xC3 0xA9). Le texte est `café`.

**3.** L'encodage correct est **UTF-8**. L'octet 0xC3 commence par les bits `1100`, ce qui signifie en UTF-8 « début d'une séquence de 2 octets ». L'octet suivant 0xA9 commence par `10`, ce qui est bien un octet de continuation. La séquence 0xC3 0xA9 est une paire UTF-8 valide pour `é` (U+00E9).

**4.** Code Python :

```python
try:
    with open("menu.txt", "r", encoding="utf-8") as f:
        contenu = f.read()
    print("Encodage détecté : UTF-8")
except UnicodeDecodeError:
    with open("menu.txt", "r", encoding="latin-1") as f:
        contenu = f.read()
    print("Encodage détecté : Latin-1")
print(contenu)
```

**Résultat** : L'encodage correct est UTF-8. Le texte décodé est `café`. Le programme Python détecte automatiquement l'encodage en essayant UTF-8 en priorité.

---

### Corrigé exercice 7 — Conversion manuelle octet par octet

**Méthode** : On identifie chaque octet ou paire d'octets UTF-8, on détermine le caractère Unicode correspondant, puis on écrit l'octet Latin-1 équivalent pour chaque caractère.

**1.** Décomposition des octets UTF-8 de `français` :

| Octet(s) | Caractère |
|---|---|
| 0x66 | `f` |
| 0x72 | `r` |
| 0x61 | `a` |
| 0x6E | `n` |
| 0xC3 0xA7 | `ç` |
| 0x61 | `a` |
| 0x69 | `i` |
| 0x73 | `s` |

**2.** Séquence Latin-1 équivalente : `66 72 61 6E E7 61 69 73`.

**3.** En UTF-8 : 9 octets. En Latin-1 : 8 octets. La différence est de 1 octet, car `ç` passe de 2 octets (UTF-8) à 1 octet (Latin-1).

**Résultat** : La séquence Latin-1 équivalente est `66 72 61 6E E7 61 69 73` (8 octets), soit 1 octet de moins que la version UTF-8.

---



### Corrigé exercice 8 — Prédire une erreur de décodage

**Méthode** : On analyse la structure binaire de l'octet 0xE9 selon les règles UTF-8 pour déterminer combien d'octets de continuation sont attendus, puis on vérifie si les octets suivants respectent le format requis.

**1.** En UTF-8, l'octet 0xE9 commence par les bits `1110`, ce qui signifie « début d'une séquence de 3 octets ». Python attend donc deux octets de continuation (commençant par `10`). Or l'octet suivant est 0x74 (`t`), qui commence par `0111` et n'est pas un octet de continuation. Python lève une `UnicodeDecodeError`.

**2.** Avec `errors="ignore"`, les octets invalides sont silencieusement ignorés. Les deux occurrences de 0xE9 sont supprimées, et seul 0x74 (`t`) est décodé. Le texte obtenu est `t`.

**3.** Avec `errors="replace"`, chaque séquence invalide est remplacée par le caractère `\ufffd`. Le texte obtenu est `\ufffdt\ufffd` (le caractère de remplacement, puis `t`, puis un autre caractère de remplacement).

**Résultat** : L'octet 0xE9 provoque une `UnicodeDecodeError` en UTF-8. Avec `errors="ignore"` on obtient `t`, avec `errors="replace"` on obtient `\ufffdt\ufffd`.

---



### Exemple corrigé 2 — Vérification par lecture binaire

Pour vérifier qu'un fichier est bien encodé en UTF-8, on le lit en mode binaire (`"rb"`) et on compare les octets avec les valeurs attendues. Par exemple, pour `Noël` en UTF-8 : `4E 6F C3 AB 6C`. Si on observe `4E 6F EB 6C`, le fichier est en Latin-1 et non en UTF-8.

### Corrigé exercice 9 — Écrire un script de conversion complet

**1.** Programme Python :

```python
import os

with open("journal.txt", "rb") as f:
    octets_source = f.read()
taille_avant = len(octets_source)

with open("journal.txt", "r", encoding="latin-1") as f:
    contenu = f.read()

with open("journal_utf8.txt", "w", encoding="utf-8") as f:
    f.write(contenu)

taille_apres = os.path.getsize("journal_utf8.txt")
print(f"Taille avant (Latin-1) : {taille_avant} octets")
print(f"Taille après (UTF-8) : {taille_apres} octets")
```

**2.** Le texte `Résumé du procès` contient 16 caractères.
- En Latin-1 : chaque caractère occupe 1 octet, soit **16 octets**.
- En UTF-8 : les caractères `é` (x2), `è` occupent chacun 2 octets au lieu de 1, soit 16 + 3 = **19 octets**.

**3.** Le fichier UTF-8 est plus volumineux car les caractères accentués dont le point de code est supérieur à U+007F sont encodés sur 2 octets en UTF-8, alors qu'ils n'occupent qu'1 octet en Latin-1.

---



### Corrigé exercice 10 — Gérer les caractères hors plage Latin-1

**1.** Non. Le caractère `\u20ac` (U+20AC) a un point de code bien supérieur à U+007F (limite ASCII). L'encodage ASCII est donc impossible.

**2.** Non. Latin-1 couvre les points de code U+0000 à U+00FF. Le caractère `\u20ac` a le point de code U+20AC, qui est hors de cette plage. L'encodage Latin-1 est impossible. Python lèverait une `UnicodeEncodeError`.

**3.** Oui. UTF-8 peut encoder tout caractère Unicode. Le caractère `\u20ac` (U+20AC) est encodé sur 3 octets en UTF-8 : `E2 82 AC`.

**4.** Code Python :

```python
texte = "Le prix est de 15\u2009\u20ac"
with open("prix.txt", "w", encoding="utf-8") as f:
    f.write(texte)
```

C'est le seul encodage viable parmi ASCII, Latin-1 et UTF-8 car le symbole euro (U+20AC) dépasse la plage de Latin-1 (U+00FF) et a fortiori celle d'ASCII (U+007F). Seul UTF-8, qui couvre l'intégralité d'Unicode, peut représenter ce caractère.

---



### Exemple corrigé 3 — Diagnostic d'un mojibake

Quand un texte encodé en Latin-1 est lu en UTF-8, les caractères accentués apparaissent sous forme de séquences incohérentes. Par exemple, `é` (0xE9 en Latin-1) est interprété comme le début d'une séquence de 3 octets en UTF-8, ce qui provoque soit une erreur soit un affichage corrompu.

### Corrigé exercice 11 — Analyser un mojibake

**1.** En UTF-8, l'octet 0xE9 commence par les bits `1110`, ce qui indique le début d'une séquence de 3 octets. Python attend deux octets de continuation (commençant par `10`). Or le fichier se termine après 0xE9, ou l'octet suivant n'est pas un octet de continuation, ce qui rend la séquence invalide.

**2.** Avec `errors="replace"`, les trois premiers caractères ASCII `c`, `a`, `f` sont décodés normalement. L'octet 0xE9 provoque une erreur et est remplacé par `\ufffd`. Le texte affiché est `caf\ufffd`.

**3.** Pour retrouver le texte original, il faut lire le fichier en mode binaire puis décoder avec le bon encodage (Latin-1) :

```python
with open("fichier.txt", "rb") as f:
    octets = f.read()

texte_original = octets.decode("latin-1")
print(texte_original)  # Affiche : café
```

---



### Exemple corrigé 4 — Calcul de la taille après conversion

Pour le mot `français` : en Latin-1, 8 octets (un par caractère). En UTF-8, 9 octets car `ç` passe de 1 à 2 octets. La différence est toujours égale au nombre de caractères accentués dont le point de code dépasse U+007F.

### Corrigé exercice 12 — Conversion par lots de plusieurs fichiers

**1.** Programme Python :

```python
import os

fichiers = ["texte1.txt", "texte2.txt", "texte3.txt"]
os.makedirs("corpus_utf8", exist_ok=True)

for nom in fichiers:
    chemin_source = os.path.join("corpus", nom)
    chemin_dest = os.path.join("corpus_utf8", nom)

    with open(chemin_source, "r", encoding="latin-1") as f:
        contenu = f.read()

    with open(chemin_dest, "w", encoding="utf-8") as f:
        f.write(contenu)

    taille_source = os.path.getsize(chemin_source)
    taille_dest = os.path.getsize(chemin_dest)
    diff = taille_dest - taille_source
    print(f"{nom} : {taille_source} -> {taille_dest} octets (variation : +{diff})")
```

**2.** Calcul des tailles :

| Fichier | Contenu | Octets Latin-1 | Octets UTF-8 | Différence |
|---|---|---|---|---|
| `texte1.txt` | `àbientôt` | 9 | 11 | +2 (`à` et `ô` passent de 1 à 2 octets) |
| `texte2.txt` | `garçon` | 6 | 7 | +1 (`ç` passe de 1 à 2 octets) |
| `texte3.txt` | `maïs` | 4 | 5 | +1 (`ï` passe de 1 à 2 octets) |

**3.** Le script donne un message de confirmation via `print(...)` qui affiche le nom du fichier, la taille source, la taille destination et la variation. Le résultat attendu pour `texte1.txt` est `àbientôt : 9 -> 11 octets (variation : +2)`.




### Exemple corrigé complémentaire

Conversion du mot Français de Latin-1 (46 72 61 6E E7 61 69 73) en UTF-8 (46 72 61 6E C3 A7 61 69 73). Le ç (0xE7 en Latin-1) devient C3 A7 en UTF-8.


## Barème

| Exercice | Points |
|---|---|
| Exercices 1-4 | 2 pts chacun |
| Exercices 5-8 | 3 pts chacun |
| **Total** | **20** |

