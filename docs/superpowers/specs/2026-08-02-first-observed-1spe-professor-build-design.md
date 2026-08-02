# Premier build observé 1SPE professeur — Design

## Statut et décision humaine

Design approuvé le 2 août 2026 pour la branche
`finalisation/collection-v1`.

La décision autorise :

- le branchement du premier assembleur réel sur les marqueurs Phase 0 ;
- la compilation avec `-recorder` ;
- la production du reçu post-préflight ;
- le versionnement du PDF professeur et de son manifeste observé ;
- les tests, commits et push sur la branche dédiée.

Elle n'autorise aucune modification de baseline visuelle. Elle ne vaut ni
validation scientifique, ni validation éditoriale, ni acceptation de
publication. `release_acceptance=false` demeure obligatoire et le manuel de
Mathématiques Première spécialité reste **NO-GO publication**.

## Objectif

Relier l'assembleur réel
`Mathematiques/manuel-maths/scripts/assemble_manuel.py` au contrat Phase 0 de
build observé, puis produire une preuve reproductible pour la variante
`professeur` : PDF réel, journal LaTeX, trace `.fls`, préflight PDF, reçu
atomique et enregistrement dans `audit/BUILD_MANIFEST.json`.

Ce lot prouve qu'un assemblage déclaré de 870 objets a effectivement été ouvert
dans l'ordre attendu pendant une compilation réelle. Il ne prouve pas à lui
seul l'exactitude mathématique, la conformité complète au programme, la qualité
pédagogique, l'identité inter-machine ou l'aptitude à l'impression.

## Périmètre

### Inclus

- variante professeur de `MANUEL_1SPE` uniquement ;
- émission de marqueurs BEGIN/END autour de chaque objet inclus ;
- trois passes LuaLaTeX avec `-recorder` ;
- arrêt immédiat à la première passe en échec ;
- contrôles PDF déjà fournis par `verify_pdf` ;
- rapport de préflight lié au digest du PDF ;
- reçu de build écrit seulement après compilation et préflight réussis ;
- activation de `scripts/build_manifest.py --receipt` ;
- validation sécurisée du reçu contre le journal, le `.fls`, l'inventaire et
  le PDF ;
- versionnement direct du PDF professeur et du manifeste canonique ;
- tests ciblés, gates Phase 0 et mise à jour de la PR existante.

### Exclus

- variante élève ;
- autres manuels et autres producteurs de PDF ;
- corrections scientifiques ou éditoriales du contenu ;
- changement de gabarit, mise en page ou oracle raster ;
- qualification complète imprimeur ;
- validation des sept dimensions de publication ;
- passage de `release-strict` au vert ;
- prétention de reproductibilité binaire entre systèmes différents.

## Approches évaluées

### 1. Git direct avec double build — retenue

Le PDF est ajouté explicitement malgré les règles d'ignorance, avec un plafond
de sécurité avant commit. Un second build, exécuté depuis le commit qui contient
déjà ce PDF, doit produire exactement les mêmes octets. Le manifeste observé
est ensuite enregistré contre ce commit source et commité séparément.

Cette approche répond directement à la demande de versionner le PDF et son
manifeste sans introduire une infrastructure nouvelle.

### 2. Git LFS — écartée pour ce lot

Git LFS n'est ni configuré ni installé dans le dépôt. Son introduction serait
une migration d'infrastructure plus large que ce premier raccordement et
modifierait les conditions de clone et de CI.

### 3. Artefact de release — écartée

Un artefact distant éviterait de grossir l'historique Git, mais ne satisferait
pas la demande explicite de versionner le PDF avec son manifeste dans la
branche.

## Architecture retenue

### Producteur réel

L'assembleur conserve son rôle : collecter les chapitres, écrire le maître
LaTeX, lancer LuaLaTeX et vérifier le PDF. Le mode d'enregistrement observé est
explicite afin qu'un build de développement ordinaire ne modifie jamais un
artefact d'audit suivi par Git.

L'interface de commande ajoute un mode de type `--record-observed`. Dans ce
mode, l'assembleur :

1. invalide tout reçu temporaire antérieur à l'exécution ;
2. écrit les marqueurs dans le maître généré ;
3. exécute chaque passe avec `-recorder` ;
4. arrête le pipeline dès qu'une passe échoue ;
5. exécute le préflight PDF ;
6. écrit atomiquement le rapport de préflight puis le reçu ;
7. appelle `scripts/build_manifest.py --receipt ...` comme frontière CLI
   séparée ;
8. propage tout échec sans déclarer le build observé.

Le mode ordinaire peut produire le PDF, mais il ne produit pas de preuve
canonique de publication.

### Marqueurs ordonnés

Chaque `\input` d'objet est entouré de deux marqueurs de journal dont le token
est le SHA-256 tronqué à 40 caractères hexadécimaux du chemin canonique relatif
à la racine Git :

```text
NEXUS-BUILD-OBJECT-BEGIN <token>
NEXUS-BUILD-OBJECT-END <token>
```

Le chemin hashé inclut donc le préfixe
`Mathematiques/manuel-maths/...`, et non le seul chemin relatif au sous-projet.
La longueur de 40 caractères évite le repli de ligne LuaHBTeX tout en conservant
une marge de collision très supérieure au besoin de l'assemblage.

La validation exige simultanément :

- exactement 870 couples équilibrés ;
- un ordre identique à l'assemblage déclaré
  `math:manual:1SPE:professeur` ;
- aucune duplication, omission ou inversion ;
- la présence de chaque source correspondante dans les entrées du `.fls` ;
- des chemins résolus sous la racine du dépôt, y compris en présence de liens
  symboliques ou de segments `..`.

Les marqueurs prouvent l'ordre sémantique demandé ; le `.fls` prouve l'ouverture
effective des fichiers par le moteur. Aucun des deux signaux ne remplace l'autre.

### Compilation et préflight

Les trois passes utilisent LuaLaTeX avec :

```text
-interaction=nonstopmode -halt-on-error -recorder
```

Le code vérifie le retour de chaque passe, et pas seulement celui de la
dernière. Le PDF final doit ensuite satisfaire les contrôles existants de
lisibilité, d'absence d'actifs manquants et d'incorporation des polices.

Le rapport de préflight est une sortie machine atomique qui contient au
minimum :

- le chemin canonique du PDF ;
- son SHA-256 et son nombre de pages ;
- l'état des contrôles exécutés ;
- les versions observées de LuaLaTeX, `pdfinfo`, `pdffonts` et Python.

Le digest est recalculé juste avant l'écriture du reçu. Le recorder recalcule
également les preuves depuis les fichiers ; il ne fait pas confiance à un
simple booléen fourni par l'assembleur.

### Reçu post-préflight

Le reçu respecte le contrat déjà défini dans `scripts/build_manifest.py` :

- `manual` et `variant` ;
- `compile_succeeded` et `preflight_succeeded` ;
- `pdf_path`, `log_path`, `fls_path`, `preflight_report` ;
- `generated_dependencies` ;
- `tool_versions` ;
- `gates`.

Pour ce premier producteur, `generated_dependencies` peut être vide : le maître
LaTeX généré par Python n'est pas une sortie déclarée par le `.fls` et n'entre
pas dans la liste des objets suivis.

Le reçu et le rapport utilisent une écriture temporaire dans le même répertoire
puis un remplacement atomique. Aucun reçu de succès ne subsiste après une
erreur de compilation, de préflight ou d'enregistrement. Le journal, le `.fls`,
le reçu et le rapport restent des artefacts techniques ignorés ; seuls le PDF
canonique et `audit/BUILD_MANIFEST.json` sont versionnés.

### Enregistrement canonique

`record_from_receipt()` cesse d'être une sentinelle « non intégrée ». Il charge
le reçu, reconstruit l'inventaire courant, dérive les preuves indépendamment et
appelle la transaction existante `record_successful_build()`.

La transaction refuse notamment :

- un dépôt sale au moment de l'observation ;
- une branche ou un manuel inattendu ;
- un reçu antérieur au journal, au `.fls`, au PDF ou au préflight ;
- un digest ou un nombre de pages incohérent ;
- un objet manquant, surnuméraire ou désordonné ;
- une source ouverte hors racine ;
- un `.fls`, journal ou rapport modifié pendant la validation ;
- une version d'outil absente ;
- un préflight qui ne couvre pas le digest du PDF courant.

L'intégration globale des producteurs reste partielle. Le schéma et
l'inventaire distinguent `not_integrated`, `partial` et `integrated`, ainsi que
les producteurs intégrés et ceux restant à raccorder. Le gate de release ne
considère la dimension intégrée que lorsque tous les producteurs requis ont le
statut `integrated`. Le raccordement du seul professeur 1SPE ne supprime donc
pas le bloqueur collection.

## Provenance Git sans cycle auto-référentiel

Le manifeste ne peut pas contenir comme provenance le SHA du commit qui le
contient lui-même. La règle de lecture devient donc : le SHA de provenance du
build doit être un ancêtre du HEAD courant, jamais une simple chaîne arbitraire.

Cette tolérance est accompagnée de validations fortes et cumulatives :

- la branche enregistrée correspond à la branche courante ;
- le dépôt est propre pour enregistrer une observation ;
- le SHA enregistré existe et est ancêtre de HEAD ;
- les `source_digest` et `model_digest` courants sont identiques ;
- le PDF suivi existe et garde exactement son digest et son nombre de pages ;
- les dépendances générées et les preuves restent cohérentes.

Un SHA non ancêtre, une branche différente, une dérive de source, du modèle ou
du PDF invalide le build. Cette règle permet de commiter le manifeste après le
build sans affaiblir son rattachement au commit source.

## Séquence de matérialisation

La séquence évite toute preuve construite depuis un état Git non versionné :

1. commiter l'instrumentation et ses tests — commit A ;
2. compiler depuis A et contrôler la taille du PDF ;
3. ajouter explicitement le PDF ignoré, puis le commiter seul — commit B ;
4. depuis B propre, recompiler en mode observé ;
5. exiger que le PDF regénéré soit octet pour octet identique à celui de B ;
6. rafraîchir, si nécessaire, l'enveloppe vide du manifeste au SHA B ;
7. enregistrer le reçu contre B ;
8. commiter séparément `audit/BUILD_MANIFEST.json` — commit C ;
9. régénérer les rapports dérivés et les commiter séparément si leur contenu
   change — commit D.

Le PDF est refusé avant ajout si sa taille atteint 90 Mio, plafond conservateur
sous la limite dure de GitHub. Une taille anormalement élevée déclenche une
décision humaine, pas un contournement automatique.

## Tests et preuves obligatoires

### Assembleur

- les 870 marqueurs BEGIN/END sont émis dans l'ordre déclaré ;
- le token porte sur le chemin Git canonique ;
- `-recorder` est présent sur chaque passe ;
- un échec à la première ou deuxième passe arrête immédiatement les suivantes ;
- aucun reçu n'est écrit avant le préflight ;
- une erreur supprime ou invalide le reçu de succès antérieur ;
- l'écriture du rapport et du reçu est atomique ;
- le mode ordinaire ne modifie pas le manifeste d'audit ;
- le mode observé invoque la frontière CLI avec le reçu exact.

### Recorder et provenance

- succès nominal depuis un commit propre ;
- rejet des marqueurs manquants, dupliqués, inversés ou parasites ;
- rejet d'une ouverture `.fls` manquante, externe ou ambiguë ;
- chemins imbriqués, normalisés et liens symboliques testés ;
- rejet d'un reçu ou rapport périmé ;
- rejet d'une modification entre préflight et enregistrement ;
- rollback complet si l'écriture du manifeste échoue ;
- acceptation d'un SHA ancêtre avec digests et PDF identiques ;
- rejet d'un SHA non ancêtre, d'une branche différente et de toute dérive de
  source, modèle ou PDF ;
- maintien du gate release rouge tant que l'intégration globale est partielle ;
- blocage d'une publication si le PDF suivi n'a pas de build observé valide.

### Artefacts

- SHA-256 et pagination du PDF enregistrés et revérifiés ;
- PDF du second build identique octet pour octet au PDF versionné ;
- manifeste conforme à son schéma ;
- `--validate-model`, `--check` et `--fail-on-new` verts ;
- `--release-strict` rouge pour les dettes réelles et non à cause d'une erreur
  d'exécution ;
- `git diff --check` propre ;
- aucune modification sous les répertoires de baseline visuelle.

## Limites de la preuve

Deux builds identiques sur le même hôte attestent la déterminisme local du
pipeline dans cet environnement. Ils ne démontrent pas une reproductibilité
cross-plateforme : versions TeX, polices, locale et dépendances système sont
capturées comme preuves, pas neutralisées. La couverture complète des actifs
transitifs est limitée à ce que le `.fls`, l'inventaire et le préflight peuvent
observer.

## Critères d'acceptation du lot

Le lot est terminé uniquement si :

1. les tests ciblés et la suite Phase 0 affectée passent ;
2. le PDF professeur réel est suivi par Git et son second build est identique ;
3. un build observé valide figure dans `audit/BUILD_MANIFEST.json` ;
4. le reçu est postérieur à un préflight réussi et croisé avec le `.fls` ;
5. l'état d'intégration indique explicitement qu'il reste des producteurs ;
6. aucune baseline visuelle n'a changé ;
7. les gates de non-régression restent verts et `release-strict` reste rouge ;
8. les commits sont atomiques et poussés sur
   `finalisation/collection-v1` ;
9. la PR existante décrit les preuves et les limites sans annoncer le manuel
   prêt à publier.

La prochaine tâche atomique, hors de ce lot, sera choisie parmi le raccordement
de la variante élève et la levée d'un bloqueur scientifique ou éditorial, avec
son propre contrat de preuve.
