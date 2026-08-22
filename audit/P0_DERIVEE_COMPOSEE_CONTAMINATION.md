# P0 — contamination de contenu : `10_C1_derivee_composee.tex`

## Statut

**Trouvé** par le lot fork de construction de la matrice TEXPERTES (T2),
pendant la vérification croisée référentiel ↔ contenu réel. Contredit le
verdict "propre" initialement rendu par le lot TCOMPL (qui n'avait vérifié
que la formulation des `libelle_bo`, pas la présence de fichiers de contenu
étrangers). **Corrigé dans ce même lot.**

## Constat

Le fichier `cours/10_C1_derivee_composee.tex` — dont le corps traite
« Dérivée d'une fonction composée », un contenu d'analyse de Terminale
spécialité — existait, identique (corps octet-pour-octet, seul le `% META`
diffère), dans **11 emplacements** :

- l'original légitime : `Mathematiques/manuel-maths/chapitres/TSPE-DERIVATION-CONVEXITE/cours/10_C1_derivee_composee.tex` (capacité réelle `TSPE-DERCONV-C1`, `status: approved`) ;
- **10 copies erronées**, chacune `status: approved`, chacune déclarant
  faussement `capacites_codes: ["C1"]` pour son propre chapitre :
  - `TEXP-ARITHMETIQUE`, `TEXP-COMPLEXES-ALGEBRE-GEOMETRIE`,
    `TEXP-COMPLEXES-TRIGO-POLYNOMES`, `TEXP-GRAPHES`, `TEXP-MATRICES-MARKOV`
    (5 chapitres TEXPERTES) ;
  - `TCOMPL-TEMPS-ATTENTE`, `TCOMPL-ECHANTILLONNAGE`,
    `TCOMPL-MODELES-FONCTION`, `TCOMPL-INFERENCE-BAYESIENNE`,
    `TCOMPL-INEGALITES` (5 chapitres TCOMPL).

**Vérification faite avant correction** : chacun des 10 chapitres contaminés
possède déjà son propre fichier C1 correct et distinct, sous le nom
descriptif conforme à sa vraie capacité (ex. `TEXP-ARITHMETIQUE` a
`10_C1_divisibilite_pgcd.tex` ; `TCOMPL-ECHANTILLONNAGE` a
`10_C1_loi_binomiale.tex`). Le fichier contaminant n'est donc **pas** la
seule source de C1 pour ces chapitres — c'est un doublon de capacité pur,
sans aucune valeur pédagogique unique pour son emplacement, qui polluait le
manuel compilé.

**Portée confirmée dans l'inventaire avant suppression**
(`audit/INVENTAIRE_COLLECTION.json`, `assemblies[].included_objects`) : les
10 fichiers contaminants étaient inclus dans les assemblages
**chapitre ET manuel**, variantes élève et professeur des deux manuels :

```
math:manual:TEXPERTES:eleve       (5 chapitres)
math:manual:TEXPERTES:professeur  (5 chapitres)
math:manual:TCOMPL:eleve          (5 chapitres)
math:manual:TCOMPL:professeur     (5 chapitres)
```

Le manuel compilé, dans son état actuel, contenait donc réellement une
section « Dérivée d'une fonction composée » hors sujet dans 10 chapitres
d'arithmétique, de nombres complexes, de graphes, de matrices/Markov,
d'échantillonnage, d'inférence bayésienne, d'inégalités et de temps
d'attente — approuvée par erreur (`status: approved` sans vérification de
contenu réelle, très probablement une erreur mécanique de copie par lot
plutôt qu'une décision éditoriale informée sur ce contenu précis).

## Cause probable

Erreur mécanique de génération/copie par lot : le fichier de la capacité
TSPE-DERIVATION-CONVEXITE-C1 a été copié comme gabarit ou reste d'un script
dans 10 répertoires `cours/` sans rapport, sans que son contenu soit
remplacé par le contenu réellement dû à chacun. Aucune preuve d'une
décision éditoriale délibérée n'a été trouvée.

## Correctif

Suppression des 10 copies erronées. Aucun contenu unique supprimé (corps
identique à l'original TSPE, qui reste intact et inchangé à
`TSPE-DERIVATION-CONVEXITE/cours/10_C1_derivee_composee.tex`). Chaque
chapitre contaminé conserve son propre fichier C1 correct, inchangé.

| Fichier supprimé | Fichier C1 correct conservé dans le même chapitre |
|---|---|
| `TEXP-ARITHMETIQUE/cours/10_C1_derivee_composee.tex` | `10_C1_divisibilite_pgcd.tex` |
| `TEXP-COMPLEXES-ALGEBRE-GEOMETRIE/cours/10_C1_derivee_composee.tex` | `10_C1_algebre.tex` |
| `TEXP-COMPLEXES-TRIGO-POLYNOMES/cours/10_C1_derivee_composee.tex` | `10_C1_forme_exponentielle.tex` |
| `TEXP-GRAPHES/cours/10_C1_derivee_composee.tex` | `10_C1_vocabulaire_graphes.tex` |
| `TEXP-MATRICES-MARKOV/cours/10_C1_derivee_composee.tex` | `10_C1_operations_matrices.tex` |
| `TCOMPL-TEMPS-ATTENTE/cours/10_C1_derivee_composee.tex` | `10_C1_loi_geometrique.tex` |
| `TCOMPL-ECHANTILLONNAGE/cours/10_C1_derivee_composee.tex` | `10_C1_loi_binomiale.tex` |
| `TCOMPL-MODELES-FONCTION/cours/10_C1_derivee_composee.tex` | `10_C1_etude_fonction.tex` |
| `TCOMPL-INFERENCE-BAYESIENNE/cours/10_C1_derivee_composee.tex` | `10_C1_formule_bayes.tex` |
| `TCOMPL-INEGALITES/cours/10_C1_derivee_composee.tex` | `10_C1_courbe_lorenz.tex` |

## Gouvernance

Fixé comme correction déterministe (contenu dupliqué, erroné, sans valeur
unique, cause mécanique identifiée) — pas comme une décision éditoriale.
Aucune modification de statut/qualification/baseline. Signalé explicitement
comme P0 à l'utilisateur malgré la correction déjà appliquée, conformément
au mandat (§ stop condition B).

**Portée non exhaustivement vérifiée** : cette investigation a confirmé ce
seul motif de contamination (`10_C1_derivee_composee.tex`, 10 occurrences).
Une recherche plus large de doublons de contenu cross-manuel/cross-chapitre
similaires n'a pas été menée de façon exhaustive dans ce lot — signalé comme
risque résiduel possible, à couvrir par l'audit scientifique/pédagogique
systématique (T3/T4) plutôt que supposé clos.
