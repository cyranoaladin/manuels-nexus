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

Chaque subprocessus de production reçoit un environnement reproductible défini
par le contrôle versionné
`Mathematiques/manuel-maths/config/reproducible-build.json`. Ce fichier fermé
contient exactement `schema_version=1`, un `source_commit` Git de 40 caractères
hexadécimaux et son `source_date_epoch` entier positif. Il est créé et commité
après l'instrumentation, avant le premier PDF. L'assembleur vérifie que le
commit existe, qu'il est ancêtre de HEAD et que son timestamp Git est exactement
l'epoch déclaré.

Le contrôle fournit les valeurs suivantes :

- `SOURCE_DATE_EPOCH` vaut le `source_date_epoch` versionné ;
- `FORCE_SOURCE_DATE=1` ;
- `TZ=UTC` ;
- `LC_ALL=C.UTF-8` ;
- `PYTHONHASHSEED=0`.

L'environnement du processus appelant ne peut pas remplacer ces cinq valeurs.
Le commit qui ajoute le PDF ne modifie jamais le contrôle : les deux builds
utilisent donc la même valeur, même si leurs HEAD et timestamps diffèrent. Un
test LuaLaTeX minimal reproduit cette séquence avec deux commits et deux
`run_id`, exige des PDF octet-identiques et retrouve les deux IDs distincts dans
les journaux. Si la distribution TeX conserve encore une métadonnée optionnelle
variable, celle-ci doit être supprimée ou normalisée dans le maître avant la
matérialisation ; aucun post-traitement opaque du PDF n'est autorisé.

L'interface de commande ajoute un mode de type `--record-observed`. Dans ce
mode, l'assembleur :

1. génère un `run_id` aléatoire de 128 bits, encodé par 32 caractères
   hexadécimaux minuscules, et invalide tout reçu temporaire antérieur ;
2. écrit ce `run_id` et les marqueurs dans le maître généré ;
3. exécute chaque passe avec `-recorder` ;
4. arrête le pipeline dès qu'une passe échoue ;
5. exécute le préflight PDF ;
6. écrit atomiquement le rapport de préflight puis le reçu ;
7. appelle `scripts/build_manifest.py --receipt ...` comme frontière CLI
   séparée ; lors du premier build, cette transaction remplace l'enveloppe vide
   périmée par l'enveloppe courante et ajoute le build en une seule écriture ;
8. propage tout échec sans déclarer le build observé.

Le mode ordinaire peut produire le PDF, mais il ne produit pas de preuve
canonique de publication.

### Marqueurs ordonnés

Chaque `\input` d'objet est entouré de deux marqueurs de journal dont le token
est le SHA-256 tronqué à 40 caractères hexadécimaux du chemin canonique relatif
à la racine Git :

```text
NEXUS_OBJECT_BEGIN:<token>
NEXUS_OBJECT_END:<token>
```

Ce protocole est celui déjà contractualisé par `scripts/build_manifest.py` et
ses tests ; ce lot ne crée pas de second format ni de migration de marqueurs.

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
- des chemins d'objets canoniques, sans lien symbolique ni segment `..`, résolus
  sous la racine du dépôt.

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

- le `run_id` commun au maître, au journal et au reçu ;
- le chemin canonique du PDF ;
- son SHA-256 et son nombre de pages ;
- l'état des contrôles exécutés ;
- les versions observées de LuaLaTeX, `pdfinfo`, `pdffonts` et Python.

Le maître contient `NEXUS_BUILD_RUN:<run_id>`. LuaLaTeX l'inscrit dans le
journal et le `.fls` prouve l'ouverture de ce maître. Le digest du PDF est
recalculé juste avant l'écriture du reçu. Le recorder recalcule également les
preuves depuis les fichiers ; il ne fait pas confiance à un simple booléen
fourni par l'assembleur.

### Reçu post-préflight

Le reçu respecte le contrat déjà défini dans `scripts/build_manifest.py` :

- `manual` et `variant` ;
- `compile_succeeded` et `preflight_succeeded` ;
- `pdf_path`, `log_path`, `fls_path`, `preflight_report` ;
- `generated_dependencies` ;
- `tool_versions` ;
- `gates`.

Le contrat est étendu par les champs obligatoires exacts suivants :

- `run_id` : 32 caractères hexadécimaux minuscules ;
- `master_path` : chemin canonique du maître LaTeX sous la racine Git ;
- `evidence_sha256` : objet fermé contenant exactement `master`, `log`, `fls`,
  `pdf` et `preflight`, chacun sous la forme `sha256:<64 hex>`.
- `reproducibility` : objet fermé contenant le chemin constant du contrôle,
  `source_commit`, `source_date_epoch` et les quatre valeurs constantes
  `FORCE_SOURCE_DATE`, `TZ`, `LC_ALL`, `PYTHONHASHSEED`.

Le rapport de préflight contient le même `run_id`, le même chemin PDF, le même
digest, la pagination, les contrôles et les versions d'outils. Le recorder :

1. ouvre chaque preuve par les primitives confinées existantes ;
2. compare son digest au champ `evidence_sha256` ;
3. vérifie le `run_id` dans le maître, le journal et le préflight ;
4. vérifie que le maître figure parmi les `INPUT` du `.fls` ;
5. recharge le contrôle de reproductibilité, revérifie le commit, l'epoch et
   l'égalité avec le préflight et le reçu ;
6. recalcule localement les versions de LuaLaTeX, `pdfinfo`, `pdffonts` et
   Python, puis exige leur égalité avec le rapport et le reçu ;
7. relit et re-hashe toutes les preuves dans le validateur transactionnel juste
   avant le remplacement du manifeste.

Le digest du rapport est placé dans le reçu après l'écriture atomique du
rapport ; le rapport ne se hashe pas lui-même. Le reçu est ensuite écrit
atomiquement. Cette direction unique évite tout cycle cryptographique.

Le build enregistré dans `audit/BUILD_MANIFEST.json` conserve le même objet
`reproducibility`. Le schéma du manifeste le rend obligatoire pour chaque build
observé, afin que l'identité binaire puisse être reliée à un epoch auditable et
non à l'environnement implicite de l'appelant.

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
- un objet déclaré, le maître ou une dépendance générée qui sort de la racine ;
- un `.fls`, journal ou rapport modifié pendant la validation ;
- une version d'outil absente ;
- un préflight qui ne couvre pas le digest du PDF courant.

Les entrées TeX Live et autres dépendances système absolues du `.fls` ne sont
pas des objets du dépôt : elles sont ignorées par le rapprochement des objets,
comme dans le recorder actuel. Leur environnement est représenté par les
versions d'outils. Cette tolérance ne s'applique jamais aux objets déclarés, au
maître ou aux dépendances générées explicitement revendiquées par le reçu.

L'intégration globale des producteurs conserve dans ce lot le statut
`not_integrated` et son schéma existant. Le professeur 1SPE est attesté dans
`observed_builds` et `observed_build_coverage`, mais ce premier raccordement ne
prétend pas définir l'univers exhaustif de tous les producteurs de la
collection. Le gate `build_receipt_producteurs_non_intégrés` reste donc rouge.
Une tâche ultérieure devra introduire un registre versionné des producteurs
requis et ne pourra calculer `integrated` que par égalité entre l'ensemble
requis et l'ensemble effectivement instrumenté — jamais par un scalaire libre.

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

Pour le premier build seulement, `record_from_receipt()` accepte comme état de
départ un manifeste valide dont `builds` est vide, même si son enveloppe est
périmée. La transaction démarre depuis un dépôt propre, dérive l'enveloppe
courante, ajoute le build et remplace le manifeste une seule fois. Un manifeste
non vide ou un état Git modifié conserve les contrôles stricts existants ; aucun
rafraîchissement intermédiaire sale n'est autorisé.

La dérivation ne passe pas d'abord par le chargeur strict, qui rejetterait
l'enveloppe vide périmée avant que la transaction puisse la remplacer. Après
`_validate_refresh_source_is_empty()` et la preuve d'un dépôt propre,
`record_from_receipt()` emploie explicitement
`_build_inventory_for_empty_manifest_refresh()`. Cette capacité interne est la
seule autorisée à ignorer les anciens digests d'un manifeste strictement vide.
Elle reste inaccessible aux manifestes non vides ou invalides et à la CLI
publique. L'inventaire borné ainsi obtenu est transmis à la dérivation des
preuves ; il n'est pas recalculé par le chemin strict avant l'écriture.

## Séquence de matérialisation

La séquence évite toute preuve construite depuis un état Git non versionné :

1. commiter l'instrumentation et ses tests — commit A ;
2. écrire le contrôle de reproductibilité à partir du SHA et du timestamp de A,
   puis le commiter seul — commit E ;
3. compiler depuis E et contrôler la taille du PDF ;
4. ajouter explicitement le PDF ignoré, puis le commiter seul — commit B ;
5. depuis B propre, recompiler en mode observé avec le contrôle inchangé ;
6. exiger que le PDF regénéré soit octet pour octet identique à celui de B ;
7. enregistrer le reçu contre B en remplaçant transactionnellement le manifeste
   vide périmé par l'enveloppe B et le premier build ;
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
- l'environnement des subprocessus écrase les cinq variables reproductibles
  par les valeurs du contrôle versionné ;
- un contrôle invalide, un commit absent/non ancêtre ou un epoch différent du
  timestamp Git est rejeté avant LuaLaTeX ;
- deux fixtures LuaLaTeX séparées par un commit d'artefact, avec des `run_id`
  différents mais le même contrôle, produisent des PDF octet-identiques et des
  journaux portant chacun leur propre ID.

### Recorder et provenance

- succès nominal depuis un commit propre ;
- usage exclusif de `_build_inventory_for_empty_manifest_refresh()` après
  validation d'un manifeste strictement vide ;
- rejet d'un manifeste non vide ou invalide avant toute dérivation permissive ;
- rejet des marqueurs manquants, dupliqués, inversés ou parasites ;
- rejet d'une ouverture d'objet revendiquée manquante, externe ou ambiguë dans
  le `.fls` ;
- chemins imbriqués et normalisés acceptés, liens symboliques et segments `..`
  rejetés pour les preuves du dépôt ;
- entrées TeX Live absolues ignorées sans être confondues avec des objets ;
- rejet d'un reçu ou rapport périmé ;
- rejet d'une modification entre préflight et enregistrement ;
- rejet d'un `run_id`, d'un digest de preuve ou d'une version d'outil
  incohérent ;
- rollback complet si l'écriture du manifeste échoue ;
- acceptation d'un SHA ancêtre avec digests et PDF identiques ;
- rejet d'un SHA non ancêtre, d'une branche différente et de toute dérive de
  source, modèle ou PDF ;
- maintien du statut global `not_integrated` et du gate release rouge ;
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
5. l'état global d'intégration reste `not_integrated` jusqu'à la définition
   déterministe de tous les producteurs requis ;
6. aucune baseline visuelle n'a changé ;
7. les gates de non-régression restent verts et `release-strict` reste rouge ;
8. les commits sont atomiques et poussés sur
   `finalisation/collection-v1` ;
9. la PR existante décrit les preuves et les limites sans annoncer le manuel
   prêt à publier.

La prochaine tâche atomique, hors de ce lot, sera choisie parmi le raccordement
de la variante élève et la levée d'un bloqueur scientifique ou éditorial, avec
son propre contrat de preuve.
