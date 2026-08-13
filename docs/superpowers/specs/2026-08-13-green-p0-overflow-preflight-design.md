# Green P0 — Débordements LaTeX et préflight Mathématiques

## Statut

- Date : 13 août 2026.
- Base contractuelle : jalon Red `c50e455e`, empilé sur le Green séparation.
- Branche prévue : `green/p0-overflow`.
- Lane : LaTeX/layout et PDF/preflight.
- Décision humaine : correction séparée, comparaison visuelle obligatoire,
  versionnement des PDF autorisé après approbation.
- Hors périmètre explicite : métadonnées métier PDF, signets et navigation
  globale, qui restent des gates de release rouges distincts.

## Objectif

Faire refuser tout `Overfull \hbox` et `Overfull \vbox` par le préflight
Mathématiques, puis corriger les causes réelles dans les quatre éditions
1SPE/TSPE afin que ce gate strict passe sans tolérance ni baseline.

Les quatre PDF `wave0-separation-intermediate` constituent l'entrée du lot.
Seul ce lot produit les quatre PDF Wave 0 finaux sans débordement ; il ne les
qualifie ni de builds observés ni de release candidates.

## État reproduit avant Green

Quatre recompilations fraîches à trois passes ont confirmé :

| Build | `Overfull \hbox` | `Overfull \vbox` |
|---|---:|---:|
| 1SPE élève | 17 | 2 |
| 1SPE professeur | 20 | 2 |
| TSPE élève | 7 | 2 |
| TSPE professeur | 9 | 2 |

Le test réel 1SPE élève du jalon Red reproduit 17 `hbox` et 2 `vbox` après
trois passes LuaLaTeX réussies.

Les grands débordements 1SPE sont notamment rattachés aux grilles professeur
des QCM mixtes :

- Suites : `163.04901 pt` et `110.95308 pt` ;
- Second degré : `224.38853 pt` ;
- Dérivation locale : `96.59883 pt` ;
- Dérivation globale : `113.43286 pt` ;
- Exponentielle : `116.94449 pt` ;
- Produit scalaire : `135.22061 pt` ;
- Variables aléatoires : `171.13678 pt`.

Le TSPE possède aussi un débordement d'ouverture « Géométrie dans l'espace »
d'environ `127.741 pt`. Les diagnostics sous 1 pt et ceux des éditions
professeur restent de vraies anomalies à qualifier, pas des tolérances
implicites.

Le lot rejoue immédiatement la matrice après le split élève/professeur. Ces
nouveaux comptes servent au diagnostic, mais aucun nombre d'anomalies non nul
ne devient un oracle acceptable.

## Gate de préflight

`Mathematiques/manuel-maths/scripts/pdf_integrity.py::verify_pdf()` retourne
`1` dès que le journal contient l'un des diagnostics :

- `Overfull \hbox` ;
- `Overfull \vbox`.

Le contrôle intervient avant l'appel à `pdffonts`. Le message d'erreur indique
le type de débordement et le chemin exact du journal. Le comportement reste
identique pour les assets ou glyphes manquants.

Les tests unitaires vérifient séparément :

1. `hbox` → code 1, message avec type et chemin ;
2. `vbox` → code 1, message avec type et chemin ;
3. en présence d'un `Overfull`, le runner de polices n'est jamais appelé ;
4. sans `Overfull`, le contrôle des polices continue normalement.

Aucun seuil, compteur maximal, whitelist de page, fingerprint de dette ou
option de contournement n'est ajouté.

## Environnement unique des builds contractuels

La matrice de test et l'assembleur de production utilisent le même helper de
build local. Ce helper :

- charge `config/reproducible-build.json` ;
- fixe `TZ`, `LC_ALL`, `SOURCE_DATE_EPOCH`, `PYTHONHASHSEED` et
  `FORCE_SOURCE_DATE` comme l'assembleur ;
- isole `TEXMFVAR` dans le dossier temporaire ;
- lance LuaLaTeX avec `-recorder` ;
- compile trois passes ;
- conserve master, `.log`, `.fls`, PDF et sorties de préflight dans le dossier
  temporaire ;
- n'appelle jamais `--record-observed`.

Le CLI de production délègue au même helper : il n'existe pas un second chemin
de compilation dans les tests. Un test de contrat compare master, environnement
contrôlé, arguments LuaLaTeX et résultat du helper lorsqu'il est invoqué depuis
la matrice ou depuis l'orchestration locale. Toute divergence est rouge.

La matrice couvre :

- `1SPE` élève ;
- `1SPE` professeur ;
- `TSPE_2026_2027` élève ;
- `TSPE_2026_2027` professeur.

Chaque cas exige le succès des trois passes puis zéro `Overfull` horizontal ou
vertical. Une indisponibilité de LuaLaTeX, du fichier de configuration ou un
timeout est un échec, jamais un skip.

## Attribution auditable des diagnostics

Les marqueurs objet existants ne couvrent ni les ouvertures ni les diagnostics
différés par l'output routine. Le contrat ajoute trois niveaux :

1. `NEXUS_OBJECT_BEGIN/END:<trace-token-40-hex>` autour des objets, en
   conservant exactement le token SHA-256 tronqué partagé avec
   `build_manifest._object_trace_token` et les tests historiques ;
2. `NEXUS_OPENING_BEGIN/END:<chapitre>` autour de toute l'ouverture, le marqueur
   de fin étant émis **après** le `\clearpage` pour capturer les `vbox` de
   shipout ;
3. `NEXUS_PAGE_SHIPOUT:<page-absolue>:<chapitre>:<rubrique>:<contexte>` émis par
   un hook de shipout, où le contexte est le dernier objet ou l'ouverture.

Le parseur de journal attribue dans cet ordre :

1. diagnostic compris entre marqueurs objet → objet actif ;
2. diagnostic compris entre marqueurs ouverture → ouverture active ;
3. diagnostic émis entre deux marqueurs → diagnostic en attente, rattaché au
   prochain `NEXUS_PAGE_SHIPOUT` ;
4. si aucun shipout ne suit, repli explicite sur la ligne source TeX et la page
   absolue du journal ; une attribution inconnue reste bloquante.

Le master temporaire est accompagné d'une table versionnée dans la preuve de
diagnostic, `trace-token-40-hex → chemin canonique suivi`. Le parseur résout les
tokens avec cette table ; le chemin n'est jamais exposé dans le marqueur TeX.
Une collision, un token inconnu ou une divergence avec
`build_manifest._object_trace_token` est bloquante.

Des fixtures synthétiques couvrent notamment un `Overfull \vbox` entre
`NEXUS_OBJECT_END` et le marqueur suivant, ainsi que le `127.741 pt` de
l'ouverture TSPE. Aucun diagnostic ne peut être déclaré corrigé s'il reste
`unknown`.

Pour chaque diagnostic initial, le lot produit une table versionnée :

| fingerprint | variante | type | objet/ouverture | ancienne page | nouvelle page | cause | correctif | état |
|---|---|---|---|---:|---:|---|---|---|

La page ancienne provient du PDF intermédiaire de séparation ; la nouvelle page
provient du PDF final. La table rend les cibles visuelles calculables même si la
pagination change.

## Correction des causes

Pour chaque diagnostic restant après séparation :

1. lire le message, son attribution et ses lignes associées ;
2. comparer avec un composant équivalent sans débordement ;
3. formuler une hypothèse unique ;
4. ajouter un test minimal qui échoue ;
5. appliquer le plus petit correctif ;
6. rejouer le test local puis le build concerné ;
7. mettre à jour la ligne de diagnostic avec preuve et nouvel état.

Les changements globaux de format, marges, corps, interligne ou densité sont
hors périmètre sauf démonstration qu'ils constituent la cause racine et nouvelle
validation humaine. Les contenus mathématiques ne sont pas abrégés pour faire
tenir une page sans revue disciplinaire.

Après trois hypothèses infructueuses sur une même cause, le lot s'arrête pour
réexamen architectural.

## Revue visuelle et manifeste immuable

La table de diagnostic pilote la rasterisation. Elle inclut au minimum :

- les pages des sept QCM 1SPE concernés ;
- l'ouverture TSPE « Géométrie dans l'espace » ;
- toute page touchée par un composant partagé ;
- ancienne et nouvelle page lorsqu'une correction déplace la pagination.

Un dossier versionné, par exemple
`audit/visual-wave0-green-p0-overflow-2026-08-13/`, contient :

- les images avant/après et diffs ;
- les planches-contact ;
- la table `diagnostic → variante → objet/ouverture → pages` ;
- un `manifest.json` avec SHA-256 des PDF intermédiaires et finaux, de chaque
  image et de chaque planche ;
- résolutions et versions de LuaLaTeX, Poppler, ImageMagick/Pillow et polices ;
- date, approbateur, rôle, décision et éventuelles réserves ;
- `baseline_updated: false`.

La revue vérifie lisibilité, absence de contenu coupé, hiérarchie, densité et
continuité pédagogique. Après décision humaine, un test recalcule toutes les
empreintes et prouve que les quatre PDF à committer sont exactement les
artefacts approuvés. Toute modification ultérieure invalide l'approbation.

La baseline visuelle du dépôt n'est pas modifiée. Une mise à jour de baseline
exigerait une décision distincte, hors Wave 0.

## TDD, mutations et gates

Les deux cas unitaires Red de `verify_pdf()` et le cas réel 1SPE élève deviennent
verts. Trois cas réels supplémentaires sont ajoutés Red avant les corrections
de production.

Mutations adversariales :

- injecter un `Overfull \hbox` dans un journal minimal rend `verify_pdf()`
  rouge, même si le runner `pdffonts` aurait réussi ;
- placer un `Overfull \vbox` entre deux marqueurs l'attribue au prochain
  shipout, jamais à l'objet précédent par défaut ;
- modifier un octet d'un PDF approuvé fait échouer le contrôle du manifeste.

Les validations comprennent :

- tests unitaires `test_pdf_integrity.py` ;
- tests du helper reproductible et du parseur de journal ;
- quatre builds contractuels ;
- préflight sur les quatre PDF ;
- tests de charte et d'assemblage affectés ;
- `qpdf --check` et polices incorporées ;
- `git diff --check` ;
- comparaison visuelle humaine et manifeste vérifié.

Les métadonnées métier, signets, liens globaux et balisage PDF ne sont ni
corrigés ni déclarés verts ici. `--release-strict` reste rouge pour ces dettes
et les autres bloqueurs non traités par ce lot.

## Commits attendus

1. `[TESTS] étend le contrat de débordement aux quatre éditions` ;
2. `[PDF] refuse les overfull au préflight mathématiques` ;
3. `[PYTHON] unifie le helper reproductible et attribue les diagnostics` ;
4. un ou plusieurs commits `[LATEX]` séparés par cause racine ;
5. `[AUDIT] consigne la revue visuelle sans changer la baseline` ;
6. `[PDF] régénère les éditions sans débordement`, après approbation.

Un commit ne mélange pas gate, helper, correction de charte, correction de
contenu, audit visuel et artefacts PDF.

## Définition de terminé

Le lot est terminé lorsque le préflight refuse toute fixture `Overfull`, que
les quatre builds utilisent le helper reproductible commun et réussissent avec
zéro `Overfull`, que chaque diagnostic possède une attribution et une ligne de
traçabilité, que `qpdf` et les polices passent, que le manifeste visuel est
approuvé et vérifié, que les PDF canoniques approuvés sont versionnés et que
deux revues indépendantes n'ont aucun blocage.

Les métadonnées PDF métier, signets, liens globaux, balisage et autres bloqueurs
release restent rouges. Le manuel demeure **NO-GO publication**.
