---
title: "P03 - TP - Conversion d'encodages texte"
level: "premiere"
sequence_id: "P03"
document_type: "tp"
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

# P03 - TP - Conversion d'encodages texte

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-DATA-BASE-05B : convertir un fichier texte dans différents formats d'encodage.

## Prérequis
- Savoir utiliser `open()` en Python avec le paramètre `encoding`.
- Connaître les encodages ASCII, Latin-1, UTF-8.

## Matériel nécessaire
- Python 3
- Éditeur de texte ou IDE (Thonny, VS Code)

## Préparation : création des fichiers de test

Exécuter le code suivant pour créer les fichiers synthétiques utilisés dans le TP :

```python
# Création d’un fichier Latin-1 de test
with open("texte_latin1.txt", "w", encoding="latin-1") as f:
    f.write("Café crème\nSpécialité française\nÀ bientôt\n")

# Création d’un fichier UTF-8 de test
with open("texte_utf8.txt", "w", encoding="utf-8") as f:
    f.write("Café crème\nSpécialité française\nÀ bientôt\n")

# Création d’un fichier ASCII pur
with open("texte_ascii.txt", "w", encoding="ascii") as f:
    f.write("Hello World\nPython 2026\n")
```

---

## Exercice 1 — Lire un fichier Latin-1 et écrire en UTF-8 (O1, O2)

L'objectif est de convertir un fichier texte dans différents formats d'encodage, ici de Latin-1 vers UTF-8.

### Partie A : Conversion simple

1. Concevoir et coder la fonction `convertir_latin1_vers_utf8(source, cible)` qui :
   - lit le fichier `source` avec l'encodage `latin-1`,
   - écrit le contenu dans le fichier `cible` avec l'encodage `utf-8`.

```python
def convertir_latin1_vers_utf8(source, cible):
    # À compléter
    pass
```

2. Tester avec `convertir_latin1_vers_utf8("texte_latin1.txt", "resultat_utf8.txt")`.

### Partie B : Vérification

3. Écrire un code qui lit `resultat_utf8.txt` en mode binaire (`"rb"`) et affiche les octets en hexadécimal pour vérifier que `é` est bien encodé 0xC3 0xA9.

```python
with open("resultat_utf8.txt", "rb") as f:
    octets = f.read()
    print(" ".join(f"{b:02X}" for b in octets))
```

4. Comparer la taille en octets du fichier source et du fichier converti. Expliquer la différence.

---

## Exercice 2 — Détecter l'encodage d’un fichier (O3)

On ne connaît pas toujours l'encodage d’un fichier. Une méthode simple consiste à tenter de lire en UTF-8 : si aucune erreur ne survient, le fichier est probablement en UTF-8 ; sinon, on essaie Latin-1.

1. Implémenter la fonction `detecter_encodage(fichier)` qui :
   - tente de lire le fichier en UTF-8,
   - si une `UnicodeDecodeError` se produit, conclut que le fichier est probablement en Latin-1,
   - retourne la chaîne `"utf-8"` ou `"latin-1"`.

```python
def detecter_encodage(fichier):
    # À compléter
    pass
```

2. Tester sur `texte_latin1.txt`, `texte_utf8.txt` et `texte_ascii.txt`.

3. Expliquer pourquoi cette méthode n'est pas infaillible. Donner un exemple de fichier Latin-1 qui serait accepté par le décodeur UTF-8 sans erreur.

---

## Exercice 3 — Script de conversion par lot (O2, O4)

Écrire un script complet qui convertit tous les fichiers `.txt` d’un dossier de Latin-1 vers UTF-8.

1. Écrire une fonction `conversion_lot(dossier_source, dossier_cible)` qui :
   - parcourt les fichiers `.txt` du dossier source (utiliser `os.listdir()`),
   - convertit chaque fichier de Latin-1 vers UTF-8,
   - écrit les fichiers convertis dans le dossier cible,
   - gère les `UnicodeDecodeError` en affichant un message d'avertissement et en passant au fichier suivant.

```python
import os

def conversion_lot(dossier_source, dossier_cible):
    os.makedirs(dossier_cible, exist_ok=True)
    # À compléter
    pass
```

2. Tester le script en créant un dossier `test_lot/` avec trois fichiers synthétiques :
   - `fichier1.txt` en Latin-1 contenant `Forêt`
   - `fichier2.txt` en Latin-1 contenant `Noël`
   - `fichier3.txt` en ASCII contenant `Hello`

3. Vérifier que les fichiers convertis s'ouvrent correctement en UTF-8.

4. **Cas limite** : ajouter un fichier contenant uniquement des caractères ASCII. Vérifier que la conversion ne modifie pas les octets.

---

## Exercice 4 — Conversion avec rapport (O4)

Améliorer le script de l'exercice 3 pour qu'il produise un rapport de conversion.

1. La fonction doit retourner un dictionnaire avec :
   - `"convertis"` : liste des noms de fichiers convertis avec succès,
   - `"erreurs"` : liste des noms de fichiers ayant provoqué une erreur,
   - `"inchanges"` : liste des fichiers dont les octets n'ont pas changé (ASCII pur).

```python
def conversion_lot_avec_rapport(dossier_source, dossier_cible):
    rapport = {"convertis": [], "erreurs": [], "inchanges": []}
    # À compléter
    return rapport
```

2. Afficher le rapport sous forme lisible.

## Critères de réussite
- La conversion Latin-1 → UTF-8 est fonctionnelle et vérifiable au niveau des octets.
- La détection d'encodage gère correctement `UnicodeDecodeError`.
- Le script de conversion par lot traite tous les fichiers et signale les erreurs.
- Aucune donnée personnelle n'est utilisée (fichiers synthétiques uniquement).


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

## Séance(s) correspondante(s)

Séance dédiée.

## Tests attendus

Vérifier le résultat avec les jeux de tests fournis.

## Exemple d’exécution

Exécuter le script de conversion et vérifier que le fichier de sortie s'affiche sans mojibake.

## Livrable vérifiable

Script Python convertissant un fichier d'un encodage à un autre avec gestion des erreurs.

## Consigne technique détaillée

Utiliser open() avec le paramètre encoding pour lire et écrire les fichiers dans l'encodage demandé.


## Starter code

```python
# Compléter les fonctions ci-dessous
```

