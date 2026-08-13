# Audit de passation — état du projet au 13 août 2026

## Identification

- État audité : `1d0c3fdaa24f17d938696b615d23373579042b95`.
- Branche : `integration/1spe-bo2026-traceability`.
- Situation initiale : arbre propre, 16 commits devant la branche distante et
  39 commits devant `main`.
- Périmètre : six manuels, chaîne LaTeX/PDF, charte v5/v6, sources de vérité,
  assemblages, inventaires, tests et gates de publication.
- Nature de l'audit : lecture seule. Aucun contenu scientifique, pédagogique ou
  graphique n'a été modifié pendant l'établissement de ce rapport.

## Verdict

La collection est **NO-GO publication**.

Les douze PDF canoniques existent et sont lisibles, mais la migration vers la
charte v6 n'est ni complète ni démontrée par une chaîne de build observée. La
source de vérité reste contradictoire, les gates de gouvernance sont rouges et
des contenus réservés au professeur sont présents dans des éditions élèves.

Il est interdit de rendre les gates verts par suppression, `skip`, `xfail` ou
acceptation globale des nouvelles anomalies. Les empreintes doivent être
examinées et qualifiées individuellement.

## État quantifié de la collection

| Manuel | Chapitres | Objets | PDF canoniques | Pages élève/professeur |
|---|---:|---:|---:|---:|
| `1SPE` | 10 | 1 401 | 2 | 361 / 601 |
| `TSPE_2026_2027` | 11 | 768 | 2 | 179 / 250 |
| `TCOMPL` | 9 | 150 | 2 | 66 / 80 |
| `TEXPERTES` | 5 | 93 | 2 | 42 / 52 |
| `1NSI` | 10 | 339 | 2 | 109 / 171 |
| `TNSI` | 6 | 109 | 2 | 48 / 67 |
| **Total** | **51** | **2 860** | **12** | **2 026 pages** |

- Aucun chapitre n'est démontré `READY`.
- 2 911 entrées objet/contrat ont un statut bloquant pour la publication.
- `--release-strict` expose 67 bloqueurs.
- L'inventaire recense aussi 10 PDF de corpus non attribués, distincts des 12
  livrables canoniques.

Sources de mesure : `audit/INVENTAIRE_COLLECTION.json`,
`audit/INVENTAIRE_COLLECTION.md` et `ETAT_COLLECTION.md`.

## P0 observés

### 1. Fuites dans les éditions élèves

- Le PDF élève 1SPE contient sept pages « Correction et diagnostics » avec les
  réponses, aux pages 57, 110, 145, 183, 219, 262 et 350.
- Le PDF élève TSPE contient une clé de correction réservée au professeur, des
  barèmes et l'identifiant interne `TSPE-DERIVATION-CONVEXITE`.
- Le contrôle `student_text_violations()` ne couvre pas les formulations
  « Correction et diagnostics », « Réponses correctes », `Bareme`, « clé de
  correction » ni les renvois provisoires.

Cause représentative :
`Mathematiques/manuel-maths/chapitres/1SPE-SUITES/qcm/1SPE-SUITES-QCM.tex`
inclut la grille de correction sans discrimination de variante à partir de la
ligne 395.

### 2. Contenu coupé et débordements majeurs

- Le QCM Suites 1SPE génère un `Overfull \hbox` de `163.04901 pt` et un
  `Overfull \vbox` de `110.95308 pt` ; le bas du tableau est coupé.
- Un autre tableau atteint `224.38853 pt` de dépassement.
- L'ouverture « Géométrie dans l'espace » du TSPE dépasse verticalement
  d'environ `127.741 pt` lorsque les seize capacités sont composées.
- Le préflight Mathématiques accepte ces PDF ; le préflight NSI appliqué au
  même défaut le refuse.

Preuve représentative :
`Mathematiques/manuel-maths/build/MANUEL_1SPE/MANUEL_1SPE_eleve.log`, lignes
5927-5935.

### 3. Renvois provisoires et identifiants internes

- Le PDF élève 1SPE contient 50 occurrences de
  `(renvois exercices M...)` sur 37 pages.
- Le PDF élève TSPE en contient 13 sur neuf pages.
- Ces chaînes sont produites par la commande provisoire `\refExos` des classes
  historiques et sont interdites dans une version élève publiable.

### 4. Référence officielle TSPE erronée

`docs/programmes/PROGRAMMES_2026_2027.yaml` et
`Mathematiques/manuel-maths/sources/SOURCES.md` attribuent au programme de
spécialité mathématiques de terminale le NOR `MENE1921262A`.

- `MENE1921262A` désigne officiellement les enseignements de spécialité de
  terminale STMG :
  <https://www.education.gouv.fr/bo/19/Special8/MENE1921262A.htm>.
- Le NOR du programme de spécialité mathématiques de terminale est
  `MENE1921246A` :
  <https://www.education.gouv.fr/bo/19/Special8/MENE1921246A.htm>.

La règle temporelle qui maintient le programme 2019 pour l'édition 2026-2027
est correcte : le programme publié en 2026 entre en application en 2027-2028.

## Charte graphique et architecture LaTeX

La chaîne de production observée est :

```text
nexus-manuel.cls historique
  -> nexus-manuel-v5.cls
    -> nexus-charte-v6.sty et modules v6
      -> nexus-pont-v6.sty
```

Neuf modules v5/v6 sont actuellement identiques entre Mathématiques et NSI,
mais ils restent dupliqués physiquement dans deux arborescences. La migration
est partielle :

- le pont remappe plusieurs boîtes de cours historiques ;
- il ne remappe pas l'ensemble des exercices, corrections et coups de pouce ;
- les ouvertures de chapitre Mathématiques et NSI utilisent des mécanismes
  différents ;
- les spécimens et plusieurs masters de chapitre utilisent encore la pile
  historique ;
- aucune revue visuelle exhaustive v6 des douze manuels n'est enregistrée.

Le gate `scripts/check_charte_sync.py` est rouge sur :

- `gabarits/nexus-manuel.cls` ;
- `scripts/pdf_integrity.py`.

Son périmètre ne contient toutefois pas les neuf modules v5/v6 réellement
partagés. Copier aveuglément la version Mathématiques vers NSI casserait les
composants de marges absents de NSI et confondrait noyau commun et surcharges
disciplinaires.

Architecture cible recommandée : une arborescence physique commune pour le
noyau LaTeX, accompagnée de surcharges Mathématiques et NSI explicites et
testées. Cette cible doit être scellée dans un addendum de conception avant la
migration.

## Source de vérité et reproductibilité

### Contradictions actives

- `SOURCE_DE_VERITE.md` impose deux éditions par manuel, soit 12 PDF, mais
  affiche encore 2 751 objets au lieu de 2 860.
- `audit/BUILD_PRODUCERS.yaml` déclare 22 assemblages : deux par manuel
  Mathématiques et sept par manuel NSI.
- Certaines variantes NSI déclarées sont vides ou non assemblables.
- `ETAT_COLLECTION_2026_2027.md` utilise un ancien total de 2 782 objets.
- `audit/UNQUALIFIED_ANOMALIES.*` annonce zéro anomalie non qualifiée alors que
  les gates courants en détectent 119.
- Plusieurs rapports historiques ne sont pas explicitement marqués comme
  supplantés.

### Builds

`audit/BUILD_MANIFEST.json` contient `"builds": []`. Aucun reçu canonique
`*.receipt.json` ni préflight `*.preflight.json` n'est présent. Les 12 PDF sont
donc des artefacts versionnés, mais pas des livrables reproductibles démontrés
au SHA audité.

Les quatre PDF NSI disposent de métadonnées, de 34 à 51 signets et de 34 à 52
liens. Les huit PDF Mathématiques ont des métadonnées vides, zéro signet et zéro
lien. Les douze PDF sont A4, passent `qpdf --check` et incorporent leurs
polices, mais ils ne sont pas balisés (`Tagged: no`).

## Tests et gates observés

### Verts

- `git diff --check` ;
- `scripts/inventory_collection.py --check --require-clean` ;
- `qpdf --check` sur les 12 PDF ;
- polices incorporées sur les 12 PDF ;
- préflight NSI sur les quatre PDF NSI ;
- tests ciblés du pont et de la pile v5/v6.

### Rouges

- `python3 scripts/check_charte_sync.py` : code 1 ;
- `python3 scripts/inventory_collection.py --check --validate-model --require-clean` :
  code 6, 238 motifs ;
- `python3 scripts/inventory_collection.py --check --fail-on-new --require-clean` :
  code 5, 238 motifs ;
- `python3 scripts/inventory_collection.py --check --release-strict --require-clean` :
  code 7, 67 bloqueurs ;
- `python3 -m pytest tests -q` : 1 057 réussis, 9 échoués ;
- `python3 -m pytest -q` : collecte bloquée après 5 013 tests par la collision
  de deux modules de test nommés `assemble`.

Les 238 motifs des gates de baseline correspondent à 119 nouvelles empreintes
et 119 qualifications manquantes. Ils ne doivent pas être absorbés par une
régénération aveugle de la baseline.

## CI et orchestration

- Les workflows CI compilent des spécimens ou chapitres modifiés, pas les douze
  manuels complets et leurs deux variantes.
- Aucun orchestrateur racine ne construit exactement les douze éditions.
- NSI dispose de manifests de livre ; les listes de chapitres Mathématiques
  restent codées dans Python.
- Les tests du gate de synchronisation utilisent des fixtures artificielles et
  ne prouvent pas l'état réel des deux arborescences.

## Consultation externe

Le smoke test Chutes a retourné le catalogue des modèles disponibles. La
consultation indépendante a ensuite échoué avec HTTP 402 pour quota insuffisant.
Aucune recommandation Chutes n'a donc été retenue ni consignée comme preuve.

## Ordre de reprise recommandé

1. Sceller les 12 éditions canoniques : `élève` et `professeur` pour chacun des
   six manuels ; traiter les ressources annexes dans une filière distincte.
2. Écrire les tests rouges des fuites élève, débordements et préflights réels.
3. Corriger les fuites, contenus coupés, renvois et identifiants internes.
4. Corriger la référence BO TSPE et déposer les sources d'épreuve manquantes.
5. Réconcilier les 119 empreintes une par une sans affaiblir les gates.
6. Centraliser le noyau de charte et expliciter les surcharges disciplinaires.
7. Ajouter manifests Mathématiques et orchestrateur des 12 éditions.
8. Recompiler deux fois, enregistrer reçus et préflights, puis comparer les
   empreintes.
9. Soumettre chaque manuel à une revue visuelle et humaine séparée.

## Commandes minimales de reproduction

```bash
git status --short --branch
git rev-parse HEAD
git diff --check
python3 scripts/check_charte_sync.py
python3 scripts/inventory_collection.py --check --require-clean
python3 scripts/inventory_collection.py --check --validate-model --require-clean
python3 scripts/inventory_collection.py --check --fail-on-new --require-clean
python3 scripts/inventory_collection.py --check --release-strict --require-clean
python3 -m pytest tests -q
python3 -m pytest -q --collect-only
```

## Handoff

```text
ÉTAT 1d0c3fdaa24f17d938696b615d23373579042b95
Branche : integration/1spe-bo2026-traceability
Phase : audit complet avant reprise Wave 0
Commits de correction : aucun
Gates verts : clean, diff-check, inventory-check, qpdf, polices
Gates rouges : charte-sync, validate-model, fail-on-new, release-strict
P0 ouverts : fuites élève, contenu coupé, renvois/IDs, provenance BO
Décisions humaines requises : architecture commune de charte ; surface canonique
  des variantes ; approbation visuelle par manuel
Prochaine action : addendum de conception puis lot TDD de stabilisation
```
