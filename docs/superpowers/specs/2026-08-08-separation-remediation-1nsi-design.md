# Design — Séparation des remédiations et corrigés 1NSI

Date : 2026-08-08

## Objectif

Supprimer la dette des neuf sources `1NSI-*/remediation/*.tex` qui mélangent un
énoncé élève et son corrigé, sans modifier le contenu pédagogique, sans affaiblir
le gate élève et sans toucher aux cinq fichiers TNSI tant que le périmètre
Terminale n'atteint pas 12/12 chapitres.

## Périmètre observé

- neuf fichiers 1NSI contiennent chacun exactement un environnement `exercice`
  et un environnement `corrige` ;
- les blocs de vérification Python sont situés entre l'énoncé et le corrigé ;
- chaque chapitre concerné possède déjà un dossier `corriges/` ;
- cinq fichiers TNSI présentent la même dette, mais restent hors périmètre ;
- le gate `check_eleve_no_corrige.py` est global et doit rester rouge sur TNSI
  après cette passe.

## Décision

Pour chacun des neuf fichiers 1NSI :

1. conserver dans `remediation/` les métadonnées existantes, l'énoncé et le bloc
   `BEGIN-VERIFY`/`END-VERIFY` ;
2. déplacer le bloc `corrige` sans réécriture vers
   `corriges/<stem-source>-CORRIGE.tex` ;
3. ajouter au nouveau fichier des métadonnées explicites : identifiant unique
   égal au nom du fichier sans extension, `chapitre`, `type_objet: corrige`,
   `exercice_ref`, capacité héritée et statut `generated` ;
4. conserver le statut `generated` des deux objets : cette migration structurelle
   ne vaut ni revue disciplinaire ni autorisation de publication.

`exercice_ref` référence l'identifiant META de l'objet de remédiation d'origine,
car c'est l'identifiant résolu par l'inventaire de collection. L'environnement
`corrige` conserve, lui, l'identifiant de l'environnement `exercice` déplacé. Les
tests vérifient ces deux relations distinctes.

Le gabarit livre continue de neutraliser les environnements `corrige` comme
défense en profondeur, même si les quatre variantes 1NSI ne doivent plus en
sélectionner.

## Gate 1NSI

`check_eleve_no_corrige.py` reçoit un filtre optionnel
`--prefix 1NSI-`. Sans option, son comportement global reste inchangé. Le filtre
ne rend aucun motif admissible : il réduit seulement l'ensemble des chapitres
inspectés pour fournir une preuve indépendante que la dette 1NSI est résolue.
Il échoue si aucun chapitre ne correspond ou si aucun fichier n'est effectivement
inspecté.

Avec `--prefix`, les sources sous `chapitres/` sont limitées aux répertoires dont
le nom commence par le préfixe. Sous `build/`, seuls les fichiers dont le chemin
ou le contenu référence ce même préfixe sont inspectés. Les PDF livres restent
contrôlés séparément par le preflight PDF.

Les tests doivent démontrer que :

- les neuf fichiers `remediation/` ne contiennent plus de bloc `corrige` ;
- les neuf fichiers compagnons existent sous `corriges/` ;
- chaque `exercice_ref` résout vers l'ID META de sa remédiation et chaque
  environnement `corrige` reprend l'ID de l'environnement `exercice` ;
- le gate filtré 1NSI est vert ;
- un préfixe sans chapitre échoue au lieu de produire un faux vert ;
- une fuite injectée sous un chapitre `1NSI-*` reste détectée ;
- le gate global reste rouge uniquement à cause des cinq fichiers TNSI ;
- aucun fichier TNSI n'est modifié.

## Validation

- avant déplacement, calcul et enregistrement dans le test des SHA-256 des neuf
  blocs complets `\\begin{corrige}...\\end{corrige}` ;
- tests RED puis GREEN sur les neuf associations et égalité exacte de ces neuf
  SHA-256 après déplacement, hors nouvel en-tête META ;
- vérification Python des neuf chapitres concernés ;
- gate élève avec `--prefix 1NSI-` ;
- gate global observé rouge sur les seuls fichiers TNSI ;
- build des variantes `complet` et `remediation`, puis preflight PDF ;
- comparaison du texte, du nombre de pages et, si la compilation déterministe le
  permet, du SHA-256 avant/après ;
- `git diff --check` et contrôle explicite qu'aucun chemin TNSI ne figure au diff.

## Hors périmètre

- correction ou approbation pédagogique des contenus `generated` ;
- assemblage ou modification de TNSI ;
- création d'un livre professeur ;
- affaiblissement des motifs interdits ou ajout de `remediation` aux chemins
  autorisés du gate ;
- changement de baseline visuelle.
