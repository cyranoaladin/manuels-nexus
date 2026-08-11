---
title: "P03 - Trace - Conversion d'encodages texte"
level: "premiere"
sequence_id: "P03"
document_type: "trace"
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

# P03 - Trace - Conversion d'encodages texte

## Objectifs spécifiques
- Objectif O1 - Identifier précisément la représentation ou la structure en jeu.
- Objectif O2 - Appliquer une méthode disciplinaire complète.
- Objectif O3 - Justifier le résultat sur un cas différent.
- Objectif O4 - Contrôler un cas limite et corriger une erreur observée.

## Capacités officielles atomiques
- P-DATA-BASE-05B : convertir un fichier texte dans différents formats d'encodage.

## Prérequis
- Connaître la notion d'octet et de code hexadécimal.
- Savoir lire et écrire un fichier en Python.

## Table de référence des encodages

| Caractère | Point de code | ASCII | Latin-1 (ISO-8859-1) | UTF-8 |
|---|---|---|---|---|
| `A` | U+0041 | 0x41 | 0x41 | 0x41 |
| `a` | U+0061 | 0x61 | 0x61 | 0x61 |
| `0` | U+0030 | 0x30 | 0x30 | 0x30 |
| `é` | U+00E9 | -- | 0xE9 | 0xC3 0xA9 |
| `è` | U+00E8 | -- | 0xE8 | 0xC3 0xA8 |
| `ê` | U+00EA | -- | 0xEA | 0xC3 0xAA |
| `à` | U+00E0 | -- | 0xE0 | 0xC3 0xA0 |
| `ù` | U+00F9 | -- | 0xF9 | 0xC3 0xB9 |
| `ç` | U+00E7 | -- | 0xE7 | 0xC3 0xA7 |

**Règle** : les caractères ASCII (0x00-0x7F) sont identiques dans les trois encodages. Les caractères accentués occupent 1 octet en Latin-1 et 2 octets en UTF-8.

## Méthode de conversion : étapes

Pour convertir un fichier texte dans différents formats d'encodage, suivre ces étapes :

1. **Identifier** l'encodage source du fichier (ASCII, Latin-1 ou UTF-8).
2. **Lire** le fichier en précisant l'encodage source avec `open(fichier, "r", encoding="encodage_source")`.
3. **Écrire** le contenu dans un nouveau fichier avec l'encodage cible : `open(fichier, "w", encoding="encodage_cible")`.
4. **Vérifier** en relisant le fichier produit avec l'encodage cible.

### Code modèle

```python
# Conversion Latin-1 → UTF-8
with open("source.txt", "r", encoding="latin-1") as f:
    contenu = f.read()

with open("cible.txt", "w", encoding="utf-8") as f:
    f.write(contenu)
```

### Gestion d'erreur

```python
try:
    with open("source.txt", "r", encoding="utf-8") as f:
        contenu = f.read()
except UnicodeDecodeError:
    print("Encodage incorrect, essayer latin-1")
```

## Exemple corrigé

**Fichier** : `notes.txt` contenant `Résumé` encodé en Latin-1.

| Étape | Action | Résultat |
|---|---|---|
| 1 | Identifier l'encodage | Latin-1 (le `é` est stocké en 1 octet : 0xE9) |
| 2 | Lire | `open("notes.txt", "r", encoding="latin-1")` → chaîne `"Résumé"` |
| 3 | Écrire en UTF-8 | `open("notes_utf8.txt", "w", encoding="utf-8")` |
| 4 | Vérifier | Octets de `é` dans le fichier cible : 0xC3 0xA9 (UTF-8 correct) |

## Formules à retenir

- **Mojibake** : affichage incorrect dû à une discordance d'encodage (ex. : UTF-8 lu en Latin-1 → `Ã©` au lieu de `é`).
- **Cas limite** : un fichier purement ASCII est identique dans les trois encodages ; la conversion ne change rien.
- **UnicodeDecodeError** : exception levée quand les octets ne correspondent pas à l'encodage annoncé.


## Situation-problème

Un développeur web reçoit un fichier texte contenant des caractères accentués illisibles (mojibake). Il doit identifier l'encodage d'origine et convertir le fichier pour le rendre lisible.

## Activité d’entrée

Ouvrir un fichier texte encodé en Latin-1 dans un éditeur configuré en UTF-8. Observer le résultat et identifier les caractères mal affichés.

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
