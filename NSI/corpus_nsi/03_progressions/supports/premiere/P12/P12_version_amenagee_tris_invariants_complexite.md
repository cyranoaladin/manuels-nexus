---
title: "P12 - version_amenagee - tris, invariants et complexité"
level: "premiere"
sequence_id: "P12"
document_type: "version_amenagee"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "tris, invariants et complexité"
notion: "tris, invariants et complexité"
private_data: false
official_program:
  capacities:
    - "P-ALGO-02A"
    - "P-ALGO-02B"
    - "P-ALGO-02C"
    - "P-ALGO-02D"
---

# P12 - Version aménagée - tris, invariants et complexité

## Aides intégrées

- Donnée de départ : `temps = [42, 17, 23, 17, 9]`.
- Mots utiles : clé, préfixe trié, suffixe, décalage, minimum, échange, invariant.
- Méthode guidée : commencer par nommer la zone déjà ordonnée, puis décrire une seule action avant de recopier l'état suivant.
- Tableau conseillé : `avant le tour | action observée | après le tour`.

## Parcours guidé — insertion

1. Entoure la clé lorsque `i = 1` : `____`.
2. Dans la liste `[42, 17, 23, 17, 9]`, barre la ou les valeurs plus grandes que la clé qui doivent être décalées.
3. Complète la liste après l'insertion : `[____, ____, 23, 17, 9]`.
4. Écris avec tes mots ce qui est garanti dans la partie située avant `i`.

Espace de réponse :

```text
Avant le tour :
Action :
Après le tour :
```

## Parcours guidé — sélection

1. Dans `stocks = [31, 8, 26, 14, 19]`, souligne le minimum du premier suffixe.
2. Note son indice, puis dessine l'échange éventuel sans écrire la liste triée complète à l'avance.
3. Après le deuxième tour, vérifie que les deux premières positions sont les deux plus petites valeurs.

## Aides graduées

- Socle : utiliser les étiquettes « gauche déjà triée » et « reste à explorer ».
- Standard : rédiger une phrase d'invariant avec les mots « avant le tour » et « après le tour ».
- Approfondissement : suivre l'ordre de deux doublons `17` portant des étiquettes différentes et expliquer ce que devient cet ordre.

## Vérification personnelle

- Ai-je écrit au moins un état intermédiaire, et pas seulement une liste finale ?
- Ai-je distingué un décalage d'un échange ?
- Ai-je traité un cas limite parmi liste vide, un élément, liste déjà triée ou liste inversée ?
