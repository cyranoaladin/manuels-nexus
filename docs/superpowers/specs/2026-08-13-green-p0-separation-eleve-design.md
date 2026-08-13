# Green P0 — Séparation élève/professeur et renvois résolus

## Statut

- Date : 13 août 2026.
- Base contractuelle : jalon Red `c50e455e` et ses quinze cas élève.
- Branche prévue : `green/p0-student-separation`.
- Lane principale : séparation élève/professeur.
- Lane disciplinaire préalable : deux incohérences QCM P0, isolées dans un
  commit `[MATH]` et soumises à une revue mathématique indépendante.
- Décision humaine : correction Green séparée ; les quatre PDF intermédiaires
  1SPE/TSPE ne peuvent être versionnés qu'après approbation visuelle explicite.

## Objectif

Rendre verts les quinze contrats élève sans supprimer de matériel professeur,
sans masquer les fuites et sans remplacer les renvois provisoires par du vide.
La séparation devient structurelle, les JSON restent l'unique source des QCM
concernés, et la politique de contrôle possède une seule implémentation.

Le lot traite aussi les deux évaluations TSPE qui exposent actuellement un ID
interne et un barème. Il ne prétend pas corriger les débordements : les PDF
versionnés à cette étape portent l'identité explicite
`wave0-separation-intermediate` et restent **NO-GO** jusqu'au lot overflow.

## Causes racines reproduites

### Politique divergente

`assemble_manuel.student_text_violations()` et
`build_manifest._student_text_violations()` possèdent deux jeux de regex
différents. Ils manquent les formulations observées et le filtre Mathématiques
produit quatre faux positifs sur des consignes élèves.

### QCM mixtes et source canonique

Huit objets `type_objet: qcm` contiennent à la fois questions élèves et
matériel professeur :

- `1SPE-SUITES-QCM` ;
- `1SPE-SECDEG-QCM` ;
- `1SPE-DERIVATION-LOCAL-QCM` ;
- `1SPE-DERIVATION-GLOBAL-QCM` ;
- `1SPE-EXPONENTIELLE-QCM` ;
- `1SPE-PRODUIT-SCALAIRE-QCM` ;
- `1SPE-VARALEA-QCM` ;
- `TSPE-CONTINUITE-QCM`.

Chacun possède déjà un `*-QCM.json` complet. Ces JSON sont canoniques ; les
TeX sont des sorties dérivées. Le générateur produit actuellement une seule
sortie TeX mixte, ce qui rend impossible une exclusion par objet.

### Deux incohérences mathématiques bloquantes

La migration ne peut pas régénérer aveuglément les huit QCM :

1. `1SPE-EXPONENTIELLE/Q9` : le JSON donne correctement
   \(e^{2,5}<e^{\sqrt 7}\) avec la réponse A, tandis que le TeX courant inverse
   les libellés A/B et marque ainsi une réponse fausse ;
2. `1SPE-PRODUIT-SCALAIRE/Q8` : les réponses B « orthogonaux » et C « de même
   norme » sont vraies simultanément, bien que le QCM annonce une seule réponse.

Ces deux défauts sont consignés comme P0. Avant toute régénération :

1. des tests de régression doivent échouer sur le rendu actuel ;
2. l'option C de Produit scalaire doit devenir un distracteur mathématiquement
   faux dans le JSON canonique et dans le TeX transitoire ;
3. le TeX transitoire Exponentielle doit être remis en cohérence avec son JSON ;
4. un reviewer mathématique indépendant doit approuver énoncé, quatre options,
   réponse et diagnostics des deux questions ;
5. ces corrections sont committées seules sous `[MATH]`.

Un tableau de migration compare, pour les huit QCM, nombre de questions,
options, réponses et diagnostics entre JSON et rendu courant. Toute divergence
autre que les deux P0 approuvés arrête la régénération pour revue, au lieu de
choisir silencieusement une version.

### Évaluations TSPE mixtes

Les objets suivants sont autorisés dans la variante élève mais impriment un ID
interne, le mot « Barème », le total et les points de chaque exercice :

- `TSPE-DERIVATION-CONVEXITE-EV-A.tex` ;
- `TSPE-DERIVATION-CONVEXITE-EV-B.tex`.

Leurs objets `corrige_evaluation` sont déjà réservés au professeur. La cause
est donc un contenu enseignant placé dans l'énoncé élève, pas une erreur du
filtre d'inclusion.

### Renvois provisoires

Les 63 appels `\refExos{M…}` retombent sur la définition historique
`(renvois exercices M…)`. Les codes `M1`, `M2`, etc. sont réutilisés entre
chapitres, alors que la classe v5 utilise actuellement une clé globale. Une clé
limitée au code méthode provoquerait donc des collisions.

### Contrat de maquette v5

`build/maquette-v5/manifest.json`, `build/maquette-v5/maquette.tex` et
`test_maquette_v5.py::test_qcm_hash_is_immutable` ne connaissent qu'un fichier
QCM Dérivation locale. Leur migration doit être atomique avec le split ; un
test historique ne peut pas être supprimé ou affaibli.

## Architecture de la politique unique

Un module racine `scripts/student_text_policy.py` expose une fonction pure :

```python
def student_text_violations(text: str) -> list[str]:
    ...
```

Les fonctions publiques existantes restent disponibles et délèguent à ce
module afin de préserver leurs appelants et messages métier.

La politique retourne les raisons stables suivantes :

- `identifiant interne` ;
- `corrigé` ;
- `barème enseignant` ;
- `note enseignant` ;
- `renvoi provisoire`.

Elle reconnaît les variantes de casse et d'accent des formulations du contrat
Red, ainsi que les préfixes internes `1SPE-`, `TSPE-` et `1NSI-`. Elle ne
signale pas les verbes et adjectifs légitimes des six contre-exemples du
recorder ni le septième contre-exemple Mathématiques.

Le module n'extrait pas le texte et n'accède pas au système de fichiers. Les
assembleurs et recorders restent responsables de `pdftotext`, de ses erreurs
et de la levée de leur exception métier.

## Génération structurelle des huit QCM

`build_qcm_tex.py` conserve chaque JSON comme seule autorité et rend deux
sorties déterministes :

1. `qcm/<nom>-QCM.tex`, ID historique et `type_objet: qcm`, contenant seulement
   titre, consigne, questions et options élèves ;
2. `diagnostics/<nom>-QCM-DIAGNOSTICS.tex`, ID
   `<chapitre>-QCM-DIAGNOSTICS` et `type_objet: qcm_diagnostics`, contenant la
   clé, les diagnostics et les renvois professeur.

La seconde sortie est un corps sans `\clearpage` ni marque de rubrique. Le
dossier `diagnostics/` est ordonné immédiatement après `qcm/` dans le master
professeur et absent de la variante élève. La frontière appartient à
l'assembleur, qui émet dans cet ordre : `\clearpage`, puis
`\rubrique{Corrigés}`, puis l'input diagnostics, puis un second `\clearpage`
avant toute rubrique ou ouverture suivante. L'ordre inverse à l'entrée est
interdit, car il contaminerait la rubrique de la page QCM précédente ;
l'absence de coupure à la sortie attribuerait prématurément « Évaluation » à la
dernière page diagnostics. L'exclusion élève est verrouillée à la fois par le
dossier et par `ELEVE_ALLOWED_TYPES`, défense en profondeur.

Le générateur valide les données avant écriture, écrit les deux temporaires
dans leur dossier de destination puis les remplace atomiquement. En mode
`--check`, il compare les deux sorties. Une sortie manquante ou divergente rend
la commande rouge.

`test_qcm_source_unique.py` couvre les deux sorties des huit chapitres et
vérifie :

- IDs et `type_objet` ;
- synchronisation exacte avec le JSON ;
- absence de clé/diagnostic dans le QCM élève ;
- conservation de chaque réponse et diagnostic dans la sortie professeur ;
- inclusion professeur et exclusion élève ;
- titre et rubrique « Corrigés » dans le PDF professeur ;
- rubrique « Auto-évaluation » sur la page précédant la transition et rubrique
  « Corrigés » sur la première et la dernière page diagnostics ;
- rubrique attendue sur la première page de l'objet qui suit, sans contenu
  diagnostics partagé sur cette page.

## Migration atomique de la maquette v5

Dans le même commit que le split Dérivation locale :

1. le manifeste référence séparément les fichiers `student` et `diagnostics`
   avec leurs deux SHA-256 ;
2. la maquette inclut le QCM élève au point historique puis reproduit la
   frontière sémantique `\clearpage`, `\rubrique{Corrigés}`, input diagnostics
   et `\clearpage` de sortie à l'emplacement exact de l'ancien suffixe
   professeur ;
3. le test d'immutabilité vérifie les deux hashes ;
4. la concaténation des deux corps rend le même contenu professeur que
   l'ancien fichier combiné ;
5. le nombre de pages et les hashes PNG historiques restent inchangés.

Si le split ou les deux corrections mathématiques modifient une page de la
maquette, l'exécution s'arrête et produit un diff avant/après. Aucun hash PNG
ni baseline n'est mis à jour sans une approbation humaine distincte.

## Séparation des évaluations TSPE

Les deux énoncés élève sont réécrits uniquement sur leur présentation :

- titre public « Évaluation A — Dérivation et convexité » ou « Évaluation B —
  Dérivation et convexité » ;
- durée visible ;
- aucun ID interne, mot « Barème », total ou nombre de points par exercice.

Les points supprimés sont transférés explicitement dans les deux objets
`corrige_evaluation`, qui affichent pour le professeur le total de 20 points et
la ventilation de 5 points par exercice. Les métadonnées internes
`bareme_total` restent traçables sans être imprimées dans la variante élève.

Des tests structurels vérifient les quatre objets. Les extractions PDF exigent
l'absence des marqueurs dans TSPE élève et leur présence dans TSPE professeur.

## Résolution canonique des 63 renvois

La clé métier est le tuple `(chapitre, code méthode)`, jamais le code `M…`
seul. Le label global prend une forme stable telle que
`nx:training:<chapitre>:<code-methode>`.

Pour chaque chapitre, l'assembleur :

1. active explicitement le chapitre avec une macro de contexte avant son
   ouverture ;
2. relève chaque code réellement appelé par `\refExos{M…}` dans les objets
   méthode ;
3. choisit, dans l'ordre d'assemblage, le premier exercice dont la métadonnée
   `methodes` contient ce code ;
4. si cette relation explicite manque, autorise seulement le fallback documenté
   par capacité commune pour `1SPE-EXPONENTIELLE` et
   `1SPE-VARIABLES-ALEATOIRES` ;
5. échoue sur zéro cible, chapitre incohérent ou label en double ;
6. place `\phantomsection\label{...}` immédiatement avant l'en-tête visible de
   l'exercice cible ;
7. rend `\refExos{M1}` comme hyperlien vers ce label et sa page calculée.

Le contexte actif empêche toute collision entre deux `M1`. Les trois passes
LuaLaTeX doivent produire zéro référence indéfinie. Les tests vérifient les 63
appels, l'unicité globale des labels, la résolution `.aux`, puis dans le PDF la
présence d'une annotation de lien dont la destination correspond à la page de
l'exercice cible. Un lien textuellement correct mais sans destination PDF est
rouge.

## Contrats PDF et identité intermédiaire

Les quatre éditions sont construites localement sans `--record-observed` :

- 1SPE élève et professeur ;
- TSPE élève et professeur.

Les PDF élèves excluent corrections, clés, réponses, barèmes enseignants, IDs
internes et chaînes `(renvois exercices M…)`. Les PDF professeurs conservent
grilles, diagnostics et barèmes déplacés.

Afin que les quinze contrats Red sur les PDF suivis deviennent réellement
verts, les quatre PDF peuvent être versionnés après revue visuelle. Ils sont
alors qualifiés `wave0-separation-intermediate` dans un manifeste d'approbation
et leurs comptes `Overfull` résiduels y sont déclarés. Ils ne sont ni des
releases candidates ni des builds observés. Le lot overflow empilé doit les
remplacer par les quatre PDF finaux sans débordement.

Le manifeste d'approbation porte au minimum SHA-256 avant/après des quatre PDF,
pages rasterisées, images et planches, versions d'outils, date, approbateur,
décision et dette résiduelle. Avant commit, un test recalcule les SHA et refuse
un PDF différent de l'artefact approuvé.

## TDD, mutations et validation

Les quinze cas Red deviennent verts. Des tests Red structurels supplémentaires
verrouillent :

- la source unique de politique ;
- les deux P0 mathématiques avant migration ;
- les deux sorties JSON-dérivées des huit QCM ;
- l'exclusion/inclusion des huit objets `qcm_diagnostics` ;
- la conservation des grilles dans le master professeur ;
- la séparation des deux évaluations TSPE ;
- la migration atomique de la maquette v5 ;
- la résolution exhaustive et navigable des 63 renvois ;
- l'échec explicite d'un renvoi sans cible.

Les tests historiques de contre-exemples restent verts. Une mutation injectant
`Clé de correction` dans un texte élève doit être refusée par l'assembleur et
le recorder. Une mutation supprimant la cible `(chapitre, M…)` doit faire
échouer l'assemblage. Une mutation réintroduisant une seconde bonne réponse au
QCM Produit scalaire doit faire échouer le test disciplinaire.

Les gates affectés incluent assemblage, QCM source unique, maquette v5,
inventaire, manifests, extractions PDF élèves/professeurs et
`git diff --check`.

## Commits attendus

1. `[TESTS] précise le contrat structurel des variantes` ;
2. `[MATH] corrige les deux incohérences QCM`, après revue indépendante ;
3. `[PYTHON] centralise la politique de séparation élève` ;
4. `[PYTHON] génère séparément QCM et diagnostics` ;
5. `[PEDAGOGIE] sépare les barèmes des évaluations TSPE` ;
6. `[LATEX] résout les renvois méthodes vers les exercices` ;
7. `[AUDIT] consigne la revue visuelle intermédiaire` ;
8. `[PDF] versionne les éditions séparées intermédiaires`, après approbation.

Les corrections mathématiques, la génération, le contenu structurel, le moteur
LaTeX, l'audit visuel et les PDF restent dans des commits distincts.

## Définition de terminé

Le lot est terminé lorsque les quinze contrats sont verts, les deux questions
QCM ont une revue mathématique indépendante, les huit grilles restent
accessibles uniquement dans les variantes professeur, les évaluations TSPE ne
fuient plus, les 63 renvois ont une destination PDF réelle, les quatre builds
réussissent, les contrôles historiques passent, les PDF intermédiaires sont
approuvés visuellement et deux revues indépendantes n'ont aucun blocage.

Les débordements déclarés, métadonnées PDF métier, signets et liens globaux
restent des gates de release rouges hors de cette définition. Seuls les liens
des 63 renvois sont exigés ici. Le manuel demeure **NO-GO publication**.
