---
title: "T03 - TP - Recherche liste vs dictionnaire"
level: "terminale"
sequence_id: "T03"
document_type: "tp"
status: "needs_review"
version: "0.4.1"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "Structures linéaires et tables associatives"
notion: "recherche, liste, dictionnaire, index, clé, complexité"
objectifs:
  - "Objectif O1 - Identifier précisément la représentation ou la structure en jeu"
  - "Objectif O2 - Appliquer une méthode disciplinaire complète"
  - "Objectif O3 - Justifier le résultat sur un cas différent"
  - "Objectif O4 - Contrôler un cas limite et corriger une erreur observée"
private_data: false
official_program:
  capacities:
    - "T-STRUCT-03C"
---

# TP — Mesurer la recherche dans une liste vs dans un dictionnaire

## Capacité visée

> Distinguer la recherche d’une valeur dans une liste et dans un dictionnaire.

---

## Objectif du TP

Vérifier expérimentalement que la recherche dans une liste est en O(n) et que la recherche dans un dictionnaire est en O(1), en mesurant les temps d'exécution pour des tailles croissantes et en traçant les courbes correspondantes.

---

## Partie 1 — Préparation des structures

**1.1.** Compléter la fonction suivante qui crée une liste et un dictionnaire de taille `n` :

```python
def creer_structures(n):
    """Renvoie une liste et un dictionnaire contenant les entiers de 0 à n-1."""
    liste = list(range(n))
    dico = {i: True for i in range(n)}
    return liste, dico
```

**1.2.** Vérifier que pour `n = 10`, la liste contient `[0, 1, ..., 9]` et le dictionnaire contient les clés `0` à `9`.

---

## Partie 2 — Mesure du temps de recherche

**2.1.** Compléter la fonction suivante qui mesure le temps de recherche d’un élément :

```python
import time

def mesurer_recherche(structure, cible, nb_essais=100):
    """Mesure le temps moyen de recherche de cible dans structure.

    Args:
        structure: liste ou dictionnaire
        cible: valeur (ou clé) à chercher
        nb_essais: nombre de répétitions pour la moyenne

    Returns:
        float: temps moyen en secondes
    """
    debut = time.perf_counter()
    for _ in range(nb_essais):
        cible in structure
    duree = time.perf_counter() - debut
    return duree / nb_essais
```

**2.2.** Tester cette fonction avec `n = 100_000` et `cible = n - 1` (pire cas pour la liste). Comparer les résultats pour la liste et le dictionnaire.

---

## Partie 3 — Collecte des mesures pour plusieurs tailles

**3.1.** Compléter le programme suivant qui mesure les temps de recherche pour des tailles croissantes :

```python
tailles = [1000, 5000, 10000, 50000, 100000, 500000, 1000000]
temps_liste = []
temps_dico = []

for n in tailles:
    liste, dico = creer_structures(n)
    cible = n - 1  # pire cas pour la liste

    t_liste = mesurer_recherche(liste, cible)
    t_dico = mesurer_recherche(dico, cible)

    temps_liste.append(t_liste)
    temps_dico.append(t_dico)

    print(f"n = {n:>10} | Liste: {t_liste:.6f} s | Dico: {t_dico:.8f} s")
```

**3.2.** Exécuter ce programme. Observer comment les temps évoluent quand `n` est multiplié par 10.

---

## Partie 4 — Tracé des courbes

**4.1.** Utiliser `matplotlib` pour tracer les deux courbes sur un même graphique :

```python
import matplotlib.pyplot as plt

plt.figure(figsize=(10, 6))
plt.plot(tailles, temps_liste, marker='o', label='Liste — O(n)')
plt.plot(tailles, temps_dico, marker='s', label='Dictionnaire — O(1)')
plt.xlabel('Taille de la structure (n)')
plt.ylabel('Temps de recherche (secondes)')
plt.title('Recherche : liste vs dictionnaire')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('recherche_liste_vs_dico.png', dpi=150)
plt.show()
```

**4.2.** Décrire en quelques phrases la forme de chaque courbe. Est-ce cohérent avec les complexités théoriques O(n) et O(1) ?

---

## Partie 5 — Analyse et conclusion

**5.1.** Compléter le tableau suivant à partir de vos mesures :

| Taille `n` | Temps liste (s) | Temps dico (s) | Rapport liste/dico |
|------------|-----------------|----------------|--------------------|
| 1 000 | | | |
| 10 000 | | | |
| 100 000 | | | |
| 1 000 000 | | | |

**5.2.** Le rapport liste/dico est-il constant quand `n` augmente ? Qu'est-ce que cela confirme ?

**5.3.** Rédiger une conclusion de 3 à 5 lignes expliquant dans quels cas on doit préférer un dictionnaire à une liste pour des opérations de recherche. Utiliser les termes **complexité**, **O(n)**, **O(1)** et **hachage**.

---

## Pour aller plus loin (bonus)

**6.1.** Mesurer le temps de `val in dico.values()` pour les mêmes tailles. Quelle complexité observe-t-on ? Expliquer pourquoi.

**6.2.** Tracer une troisième courbe pour `dico.values()` et comparer avec les deux précédentes.


## Objectifs


## Capacités officielles


## Prérequis


## Situation-problème

Un programme de correcteur orthographique doit vérifier si un mot appartient au dictionnaire français (300 000 mots). La recherche séquentielle prend trop de temps. Comment accélérer ?

## Activité d’entrée

Mesurer le temps de recherche de 10 000 mots dans une liste de 100 000 éléments, puis dans un dictionnaire de 100 000 clés. Comparer.

## Exemple

Démonstration collective du temps de recherche dans une liste de 100 000 éléments vs un dictionnaire de même taille.

## Exercices

Exercices de recherche dans des listes et dictionnaires avec analyse de complexité.

## Corrigé

Les corrigés détaillés sont dans T03_corrige_recherche_liste_dictionnaire.md.

## Erreurs fréquentes

- EF1 : confondre la complexité de recherche dans une liste (O(n)) et dans un dictionnaire (O(1)).
- EF2 : oublier que `val in dico.values()` est en O(n) et non O(1).
- EF3 : mélanger index de position (liste) et clé d'accès (dictionnaire).


## Remédiation

Exercice de remédiation : chronométrer manuellement 100 recherches dans une liste puis dans un dictionnaire et expliquer l'écart.

## Différenciation

- Socle : exercices de base.
- Standard : exercices complets.
- Expert : exercice d'approfondissement.

## Critères de réussite

- Critère de réussite : les mesures de temps confirment O(n) pour la liste et O(1) pour le dictionnaire.
- Critère de validation : l'élève justifie la différence de complexité par le mécanisme d'accès.
- Observable : le code de benchmark est correct et les résultats cohérents.


## Séance(s) correspondante(s)

Séance dédiée.

## Tests attendus

Vérifier le résultat avec les jeux de tests fournis.

## Exemple d’exécution

Exécuter le benchmark et vérifier que le dictionnaire est significativement plus rapide que la liste.

## Livrable vérifiable

Script Python mesurant et comparant les temps de recherche dans une liste et un dictionnaire.

## Consigne technique détaillée

Utiliser time.perf_counter() pour mesurer les durées et comparer les résultats.

## Cas limite

Tester avec des entrées vides et des cas extrêmes.


### Exercice 1 — Mesurer le temps de recherche dans une liste
Créer une liste de 100 000 éléments et mesurer le temps de recherche.

### Exercice 2 — Mesurer le temps de recherche dans un dictionnaire
Créer un dictionnaire de 100 000 clés et mesurer le temps de recherche.

