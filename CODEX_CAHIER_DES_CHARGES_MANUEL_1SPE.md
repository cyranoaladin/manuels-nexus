# CAHIER DES CHARGES ET PLAN D’ACTION CODEX
## Manuel Nexus Réussite — Mathématiques Première spécialité — Édition 2026-2027

**Statut :** document contractuel de travail
**Version :** 1.0 — 29 juillet 2026
**Périmètre principal :** manuel élève, manuel professeur, ressources associées, chaîne LaTeX, scripts, tests, CI, préflight PDF
**Décision actuelle :** **NO-GO publication** tant que tous les gates de la présente spécification ne sont pas satisfaits
**Référence auditée :** `MANUEL_1SPE_eleve.pdf`, 369 pages
**Branche de travail connue lors de la rédaction :** `finalisation/collection-v1`
**Ancien jalon connu :** `f500166605d0891e148511a9c124fda9769c5f85`
**Important :** Codex doit toujours relever le `HEAD` réel au démarrage et ne jamais supposer que ce jalon est encore courant.

---

# 1. Mission

Transformer le dépôt `manuels-nexus` en une chaîne éditoriale et logicielle fiable permettant de produire un manuel de Mathématiques de Première spécialité :

- mathématiquement exact ;
- strictement conforme au programme français applicable à la rentrée 2026-2027 ;
- explicitement préparatoire à l’épreuve anticipée de mathématiques de la session 2027 ;
- différenciant par une pédagogie Nexus réellement opérationnelle ;
- visuellement premium, stable et lisible ;
- décliné en versions élève et professeur réellement séparées ;
- reproductible depuis un clone propre ;
- validé automatiquement et humainement ;
- publiable en PDF numérique et en impression.

Le présent document ne demande pas une simple correction cosmétique du PDF actuel. Il impose une **refonte contrôlée**, sans régression, des contenus, de l’architecture pédagogique, des assemblages, des tests et du design.

---

# 2. Hiérarchie des sources et autorité

En cas de contradiction, appliquer l’ordre suivant :

1. textes officiels en vigueur ;
2. présent cahier des charges ;
3. `AGENTS.md` applicable au fichier modifié ;
4. schémas, contrats et gates machine validés ;
5. décisions humaines consignées et approuvées ;
6. rapports générés à partir des sources ;
7. anciens rapports, messages d’agents ou affirmations historiques.

## 2.1 Sources réglementaires minimales

Codex doit télécharger, dater, empreinter et référencer les sources officielles utilisées :

- programme de Mathématiques Première spécialité applicable en 2026-2027 :
  `https://www.education.gouv.fr/bo/2026/Hebdo14/MENE2602917A`
- annexe officielle du programme :
  `https://www.education.gouv.fr/sites/default/files/document/Annexe%20%E2%80%93%20Programme%20d%26%23039%3Benseignement%20de%20sp%C3%A9cialit%C3%A9%20de%20math%C3%A9matiques%20de%20la%20classe%20de%20premi%C3%A8re%20de%20la%20voie%20g%C3%A9n%C3%A9rale-515408.pdf`
- modalités de l’épreuve anticipée de Mathématiques à compter de la session 2027 :
  `https://www.education.gouv.fr/bo/2025/Hebdo24/MENE2515469N`

Toute autre source doit être qualifiée : officielle, institutionnelle, scientifique, éditoriale ou inspiration. Une source d’inspiration ne peut jamais justifier seule une affirmation réglementaire.

---

# 3. Principes non négociables

## 3.1 Exactitude

- Aucune erreur mathématique connue ne peut rester dans un artefact de release.
- Aucun résultat numérique ne peut être publié sans vérification indépendante.
- Aucun code Python ne peut être affiché sans être syntaxiquement valide et réellement exécuté.
- Aucun exemple ne doit contredire la définition qu’il illustre.
- Une démonstration annoncée comme exigible doit être rigoureuse, complète et adaptée au niveau.
- Une notion hors programme ne doit jamais être présentée comme exigible.

## 3.2 Traçabilité

- Chaque capacité doit pointer vers sa source officielle.
- Chaque objet pédagogique doit avoir un identifiant interne stable.
- Chaque objet publié doit avoir un statut explicite.
- Chaque correction doit être reliée à un exercice.
- Chaque PDF doit posséder un manifeste de build.
- Chaque décision humaine doit être datée, justifiée et attribuée.
- Une affirmation « terminé », « complet », « conforme » ou « prêt » doit être prouvée par les gates correspondants.

## 3.3 Non-destruction

Interdictions permanentes :

- `git reset --hard`;
- `git clean`;
- `git restore` sur un travail non audité ;
- `git checkout --`;
- `git push --force` ou `--force-with-lease`;
- réécriture d’historique ;
- déplacement d’un tag publié ;
- suppression d’une preuve historique sans décision consignée ;
- remplacement automatique de références visuelles pour faire passer un test.

## 3.4 Séparation des responsabilités

- Les scripts produisent et contrôlent.
- Les rapports décrivent ce qui a été réellement produit.
- Les agents proposent et vérifient.
- Les validations humaines approuvent les dimensions qui ne peuvent pas être automatisées.
- La baseline de dette empêche l’aggravation ; elle ne transforme jamais une dette connue en qualité acceptable.

---

# 4. Livrables finaux obligatoires

## 4.1 Édition élève

- `MANUEL_1SPE_ELEVE_2026-2027_v1.0.0.pdf`
- aucun corrigé complet ;
- aucun barème enseignant ;
- aucun identifiant technique interne visible ;
- renvois éditoriaux résolus ;
- signets et liens internes ;
- métadonnées PDF ;
- sommaire cliquable ;
- navigation cohérente ;
- formulaire conforme au programme ;
- mémo Python réellement enseigné dans le manuel.

## 4.2 Édition professeur

- `MANUEL_1SPE_PROFESSEUR_2026-2027_v1.0.0.pdf`
- corrigés détaillés ;
- barèmes ;
- erreurs anticipées ;
- stratégies alternatives ;
- conseils de différenciation ;
- critères de réussite ;
- liens vers la matrice du programme ;
- indications pour l’épreuve anticipée.

## 4.3 Ressources séparées

- livret des méthodes ;
- livret de remédiation ;
- banque d’évaluations ;
- banque d’automatismes ;
- sujets complets d’épreuve anticipée ;
- corrigés et barèmes ;
- matrice de conformité ;
- registre de décisions ;
- manifeste de release ;
- rapports de préflight numérique et imprimeur.

---

# 5. Registre initial des défauts bloquants

Codex doit confirmer chaque défaut dans les sources actuelles, localiser toutes ses occurrences et produire un test de régression. La liste ci-dessous n’est pas exhaustive : l’absence d’un défaut dans cette liste ne vaut pas approbation.

## 5.1 Exactitude mathématique — P0

### MATH-001 — Définition des suites géométriques

Corriger toute affirmation imposant nécessairement `q ≠ 0`, `u0 ≠ 0` ou déclarant qu’une suite géométrique ne peut pas avoir de terme nul.

Distinguer :

- définition : `u_{n+1} = q u_n` ;
- caractérisation par quotient, uniquement lorsque le dénominateur est non nul.

Propager la correction dans :

- cours ;
- méthodes ;
- exercices ;
- QCM ;
- distracteurs ;
- diagnostics ;
- remédiations ;
- corrigés ;
- formulaire.

### MATH-002 — Suite `(-1)^n`

Supprimer la contradiction affirmant que `(-1)^n` n’est pas géométrique. Elle est géométrique de raison `-1`.

### MATH-003 — Valeurs du capital à 4 %

Recalculer toutes les valeurs et sorties associées à `1500 × 1,04^n`. Vérifier le rang de seuil et les arrondis.

### MATH-004 — Boîte en carton

La fonction `x(30-2x)(20-2x)` est cubique et son développement est exact, non approximatif. Ne pas prétendre résoudre son maximum exact avec les seuls outils du second degré.

Choisir entre :

- remplacer la situation d’ouverture par une vraie optimisation quadratique ;
- conserver la boîte comme exploration numérique annonçant la dérivation, sans fausse conclusion.

### MATH-005 — Démonstration des racines

Réécrire la démonstration depuis la forme canonique en traitant tous les signes de `a`. Utiliser :

`(x + b/(2a))² = Δ/(4a²)`.

Ne pas dépendre d’un raisonnement incomplet limité à `a > 0`.

### MATH-006 — Vérification du sommet

Corriger l’inversion suivante :

- si `a > 0`, les valeurs symétriques hors sommet sont supérieures ou égales au minimum `β`;
- si `a < 0`, elles sont inférieures ou égales au maximum `β`.

### MATH-007 — Notation `u(n)`

Ne pas déclarer `u(n)` non mathématique ou interdite. Présenter `u_n` comme convention privilégiée de rédaction, tout en reconnaissant les notations officielles.

### MATH-008 — Complexité

Ne pas affirmer sans modèle de coût que le calcul de `q^n` est simultanément `O(1)` et `O(log n)`. Soit préciser le modèle scolaire simplifié, soit retirer ce développement de la version élève.

## 5.2 Conformité programme — P0

### PROG-001 — Matrice officielle complète

Créer une matrice couvrant :

- algèbre ;
- analyse ;
- géométrie ;
- probabilités et statistiques ;
- logique et ensembles ;
- algorithmique et programmation ;
- automatismes ;
- épreuve anticipée.

Chaque ligne doit contenir une citation officielle, les pages et objets couvrant la capacité, les preuves machine et les validations humaines.

### PROG-002 — Forme canonique

Recentrer la compétence sur l’existence, la lecture et la complétion du carré dans les cas attendus. Ne pas transformer le calcul général systématique de `α` et `β` en automatisme central non justifié.

### PROG-003 — Exponentielle

Réécrire le chapitre en séparant strictement :

- attendu de Première ;
- approfondissement facultatif ;
- notions de Terminale.

Les limites, logarithmes, compositions générales et substitutions exponentielles ne doivent pas figurer dans le parcours obligatoire s’ils ne sont pas exigibles.

### PROG-004 — Listes Python

Introduire une progression réelle sur les listes :

- création ;
- ajout ;
- compréhension ;
- parcours ;
- exploitation dans les suites, données et simulations ;
- exercices ;
- évaluation ;
- remédiation.

Une page de mémo final ne suffit pas.

### PROG-005 — Statistiques et simulation

Intégrer les expérimentations officielles ou attendues :

- simulation d’une variable aléatoire ;
- moyenne d’échantillon ;
- répétition d’échantillons ;
- comparaison à l’espérance ;
- écart type ;
- expérimentation autour de `2σ/√n`;
- exploitation de listes Python.

### PROG-006 — Bernoulli et binomiale

Recentrer la Première sur les répétitions d’épreuves de Bernoulli dans le périmètre officiel. Requalifier ou déplacer la loi binomiale générale, les grands `n`, le triangle de Pascal et le binôme de Newton lorsqu’ils excèdent la cible.

### PROG-007 — Algorithmique

Construire une matrice des algorithmes du programme et des exemples officiels pertinents, notamment :

- listes de termes ;
- coefficients directeurs de sécantes ;
- méthode de Newton ;
- méthode d’Euler ;
- approximation de `π` ;
- Monte-Carlo ;
- statistiques et probabilités.

### PROG-008 — Épreuve anticipée

Créer un dispositif annuel explicite :

- automatismes sans calculatrice ;
- QCM conformes ;
- deux ou trois exercices indépendants ;
- sujets de 2 heures ;
- barèmes sur 6 + 14 points ;
- entraînements chronométrés ;
- sujets complets ;
- progression annuelle ;
- critères de réussite.

## 5.3 Édition élève/professeur — P0

### EDIT-001 — Corrigés dans la version élève

La version élève actuelle contient massivement des corrigés. Corriger l’architecture, pas seulement l’apparence.

Le build élève doit exclure par métadonnées :

- corrigés ;
- solutions ;
- barèmes ;
- réponses professeur ;
- notes de mise en œuvre.

Ajouter un test comparant les objets inclus dans les variantes.

### EDIT-002 — Identifiants internes visibles

Supprimer du rendu élève les identifiants tels que `1SPE-...`. Les conserver dans les métadonnées, manifests et outils internes.

### EDIT-003 — Renvois provisoires

Résoudre toutes les chaînes du type :

- `(renvois exercices M1)`;
- références de page codées en dur ;
- placeholders ;
- labels non résolus.

### EDIT-004 — Cohérence des neuf temps

Réconcilier la promesse éditoriale et la structure réelle. Définir un ordre canonique, variable seulement par règles explicites.

### EDIT-005 — Évaluations A/B

Prouver leur présence, leur comparabilité et leur séparation dans chaque chapitre, ou corriger l’avant-propos.

## 5.4 Python — P0

### CODE-001 — Guillemets typographiques

Interdire `“”`, `« »` et tout guillemet non ASCII dans les sources Python publiées.

### CODE-002 — Opérateurs invalides

Interdire `≤`, `≥`, `×`, `^` lorsqu’ils remplacent des opérateurs Python.

### CODE-003 — Source unique

Les blocs de code doivent provenir de fichiers `.py` testés. Ne pas recopier manuellement le code dans LaTeX.

### CODE-004 — Sorties

Chaque sortie imprimée doit être générée par l’exécution du fichier source correspondant et comparée en CI.

### CODE-005 — Sécurité et terminaison

Les boucles `while` doivent être testées avec :

- préconditions ;
- borne d’itérations en test ;
- cas limites ;
- risque de boucle infinie ;
- preuve du rang minimal.

## 5.5 Mise en page — P0

### DESIGN-001 — Notes marginales

Éliminer tous les chevauchements. Les notes marginales doivent être :

- optionnelles ;
- ancrées sémantiquement ;
- limitées en longueur ;
- déplacées automatiquement dans le flux principal lorsqu’elles ne tiennent pas ;
- absentes sous la taille minimale validée.

Pages de référence connues à inspecter : 13, 16, 18, 19, 20, 21, 48, 81, 83, 90, 91.

### DESIGN-002 — Ouvertures de chapitre

Rendre les ouvertures adaptatives. Corriger en particulier les comportements observés autour des pages 260 et 311 :

- contenu rejeté sur une page presque vide ;
- phrase coupée ;
- objectifs ou temps isolés ;
- couche texte du chapitre précédent masquée sous le fond.

### DESIGN-003 — En-têtes courants

Les pages de méthodes, exercices, QCM, remédiations et annexes doivent afficher la rubrique réelle, non le dernier sous-titre de cours rencontré.

### DESIGN-004 — Densité

Définir des limites mesurables :

- nombre maximal de composants majeurs par page ;
- taille minimale ;
- longueur maximale des encadrés ;
- ratio blanc/contenu ;
- limites de notes ;
- règles de coupure.

### DESIGN-005 — Représentations

Ajouter des graphiques, figures, schémas et visualisations lorsque le changement de registre est pédagogiquement nécessaire.

## 5.6 PDF et accessibilité — P0/P1

- signets ;
- liens internes ;
- table des matières cliquable ;
- métadonnées ;
- titre, auteur, édition, mots-clés ;
- ordre de lecture cohérent ;
- aucune couche textuelle invisible et incohérente ;
- polices incorporées ;
- aucun glyphe manquant ;
- version numérique optimisée ;
- préflight imprimeur ;
- stratégie de balisage accessible documentée.

---

# 6. Modèle pédagogique Nexus

La différenciation ne doit pas être une simple étiquette de difficulté.

## 6.1 Boucle Nexus de maîtrise

Chaque capacité `Ci` doit mettre en œuvre :

1. **Diagnostic** — 2 à 4 questions ciblées.
2. **Orientation** — règle de parcours objective.
3. **Cours essentiel** — contenu minimal exigible.
4. **Résolution experte** — exemple complet et commenté.
5. **Guidage estompé** — exemple voisin à compléter.
6. **Entraînement** — consolidation, maîtrise, approfondissement.
7. **Preuve de maîtrise** — exercice sans aide.
8. **Remédiation ciblée** — liée à une erreur observée.
9. **Re-test isomorphe** — données différentes, même structure.
10. **Réactivation** — J+7 et J+21.
11. **Transfert** — problème inter-capacités.

## 6.2 Contrat machine par capacité

Chaque capacité doit posséder des objets ou preuves identifiables :

```yaml
capacity_id:
official_reference:
chapter:
diagnostic_ids:
course_ids:
method_ids:
guided_example_ids:
practice_ids:
mastery_check_ids:
remediation_ids:
retest_ids:
reactivation_ids:
transfer_ids:
teacher_notes_ids:
status:
reviewers:
```

Une capacité n’est pas complète si un maillon obligatoire manque.

## 6.3 Parcours

Les parcours doivent être définis par le type d’aide, pas seulement par la difficulté :

- **Consolidation** : étapes explicites, exemples proches, coups de pouce.
- **Maîtrise** : tâches standard, choix de méthode, rédaction.
- **Approfondissement** : transfert, recherche, démonstration ou modélisation.

Aucun contenu hors programme ne doit être nécessaire pour réussir le parcours Maîtrise.

---

# 7. Architecture éditoriale cible

## 7.1 Structure canonique d’un chapitre

1. ouverture ;
2. contrat de capacités ;
3. diagnostic de prérequis ;
4. orientation ;
5. cours essentiel ;
6. démonstrations exigibles ;
7. méthodes ;
8. exercices par capacité et parcours ;
9. TD ou fil rouge ;
10. auto-évaluation ;
11. diagnostic d’erreurs ;
12. remédiation ;
13. re-test ;
14. évaluation A ;
15. évaluation B ;
16. réactivation ;
17. ressources professeur.

La variante élève exclut les éléments professeur et les solutions complètes.

## 7.2 Statuts des contenus

Valeurs minimales :

- `draft`;
- `generated`;
- `needs_math_review`;
- `needs_program_review`;
- `needs_editorial_review`;
- `needs_visual_review`;
- `approved`;
- `deprecated`;
- `rejected`.

`generated` n’est jamais publiable.

## 7.3 Nommage

- identifiants internes stables et invisibles dans le PDF élève ;
- numéros éditoriaux calculés ;
- labels LaTeX ;
- pages calculées ;
- aucune page codée en dur ;
- aucune duplication silencieuse.

---

# 8. Architecture technique cible

## 8.1 Source unique

Les contenus doivent être pilotés par des manifests et métadonnées versionnés. La classe LaTeX ne doit pas coder :

- le nombre de pages ;
- les folios métier ;
- le nombre d’exercices ;
- les titres d’un chapitre pilote ;
- les pages des renvois ;
- les nombres de méthodes ;
- les pages blanches systématiques.

## 8.2 Assemblages déclarés et observés

Distinguer :

- `declared_assemblies` : analyse statique ;
- `observed_builds` : contenu réellement produit par le build.

Chaque build émet un manifeste :

```json
{
  "schema_version": 1,
  "git_sha": "...",
  "source_digest": "...",
  "manual": "1SPE",
  "variant": "eleve",
  "edition": "2026-2027",
  "included_objects": [],
  "excluded_objects": [],
  "generated_dependencies": [],
  "pdf_path": "...",
  "pdf_sha256": "...",
  "page_count": 0,
  "toolchain": {},
  "gates": {}
}
```

## 8.3 Reproductibilité

Créer une chaîne hermétique :

- Python verrouillé ;
- dépendances verrouillées ;
- TeX Live figé ;
- polices identifiées et empreintées ;
- Poppler/ImageMagick figés si utilisés dans les baselines ;
- locale et fuseau contrôlés ;
- commande unique de build.

Commandes cibles :

```bash
make setup
make quality
make manual-1spe-eleve
make manual-1spe-professeur
make preflight
make release-candidate
```

## 8.4 Écritures

Les générateurs doivent :

- refuser les sorties hors dépôt ;
- écrire dans des temporaires ;
- valider avant remplacement ;
- utiliser `os.replace`;
- gérer les exécutions concurrentes ;
- conserver l’ancien artefact en cas d’échec ;
- produire des sorties déterministes.

---

# 9. Validation mathématique et pédagogique

## 9.1 Double validation

Chaque chapitre doit être relu indépendamment par deux rôles :

- expert mathématique ;
- expert programme/pédagogie.

Les mêmes éléments ne peuvent pas être auto-approuvés par l’agent qui les a générés.

## 9.2 Vérifications symboliques

Utiliser SymPy lorsque pertinent pour :

- identités ;
- développements ;
- factorisations ;
- racines ;
- dérivées ;
- tableaux de signes ;
- sommes ;
- valeurs numériques ;
- égalités de corrigés.

SymPy ne remplace pas la validation d’une démonstration.

## 9.3 Résolution aveugle

Pour chaque chapitre :

- échantillon aléatoire d’exercices ;
- résolution à partir de l’énoncé seul ;
- comparaison au corrigé ;
- recherche d’ambiguïtés ;
- vérification des unités et arrondis ;
- contrôle du niveau.

## 9.4 Mutations

Les tests doivent prouver qu’ils détectent une erreur introduite volontairement :

- signe ;
- indice ;
- borne ;
- réponse QCM ;
- sortie Python ;
- inclusion d’un corrigé dans la version élève ;
- renvoi cassé ;
- code typographique invalide.

---

# 10. Validation visuelle

## 10.1 Rendu intégral

À chaque release candidate :

- rasteriser toutes les pages ;
- produire une planche-contact ;
- détecter les débordements ;
- inspecter les pages à forte densité ;
- vérifier les pages d’ouverture, méthodes, tableaux, code, géométrie, probabilités et annexes.

## 10.2 Baselines

Une baseline visuelle ne peut être mise à jour que par commande explicite avec :

- raison ;
- approbateur ;
- pages concernées ;
- montage avant/après ;
- versions des outils ;
- anciens et nouveaux hashes.

La CI ne met jamais à jour la baseline.

## 10.3 Impression

Tester :

- impression A4 à 100 % ;
- recto-verso ;
- niveaux de gris ;
- photocopie ;
- marges de reliure ;
- lignes fines ;
- contrastes ;
- lisibilité des petites tailles.

---

# 11. Baseline de dette

La baseline sert uniquement à empêcher l’aggravation.

`--fail-on-new` échoue pour :

- nouvelle anomalie ;
- augmentation ;
- réapparition d’un fingerprint corrigé ;
- aggravation de sévérité ;
- perte d’une disposition ;
- remplacement d’une anomalie par une autre à total constant.

Il ne doit pas échouer pour une disparition. Toute disparition est enregistrée dans l’historique afin que sa réapparition soit une régression.

Séparer :

- anomalies brutes ;
- dispositions ;
- baseline active ;
- historique des anomalies résolues.

La mise à jour de baseline doit être explicite, auditée et impossible depuis la CI.

---

# 12. Plan d’action

## Phase 0 — Sécurisation immédiate

### Objectif

Revenir à un état techniquement fiable avant de poursuivre les contenus.

### Actions

1. préserver et auditer tout WIP local ;
2. restaurer la suite de tests historique ;
3. stabiliser la source de vérité ;
4. corriger formats JSON/YAML ;
5. corriger renderers ;
6. ajouter provenance ;
7. sécuriser les écritures ;
8. ajouter classification et dispositions ;
9. brancher la CI ;
10. ouvrir une draft PR.

### Gate

- tests historiques verts ;
- nouveaux tests verts ;
- `--validate-model` vert ;
- `--fail-on-new` vert ;
- `--release-strict` rouge pour des raisons explicites ;
- aucun fichier généré invalide.

## Phase 1 — Référentiel 2026

### Actions

1. archiver les sources officielles ;
2. créer `PROGRAMME_2026_MATRIX.md/json`;
3. cartographier toutes les capacités ;
4. identifier absences, excès et ambiguïtés ;
5. décider officiellement des approfondissements ;
6. figer l’architecture de l’épreuve anticipée.

### Gate

- 100 % des lignes du programme couvertes ou explicitement justifiées ;
- aucune notion future présentée comme exigible ;
- approbation humaine du référentiel.

## Phase 2 — Corrections P0 du manuel

### Ordre

1. définitions et théorèmes ;
2. exemples et contre-exemples ;
3. démonstrations ;
4. résultats numériques ;
5. QCM et distracteurs ;
6. corrigés ;
7. code Python ;
8. variantes élève/professeur ;
9. renvois et IDs ;
10. PDF.

### Gate

- zéro P0 ouvert ;
- tests de mutation associés ;
- revue mathématique indépendante.

## Phase 3 — Recentrage des chapitres

Priorité :

1. suites ;
2. second degré ;
3. exponentielle ;
4. probabilités/statistiques ;
5. algorithmique transversale ;
6. autres chapitres.

### Gate

- conformité programme ;
- cohérence interchapitres ;
- niveaux et volumes maîtrisés.

## Phase 4 — Boucle Nexus

Implémenter la boucle complète sur un chapitre pilote, puis sur tous les chapitres.

### Gate pilote

- diagnostic ;
- orientation ;
- cours ;
- méthode ;
- guidage estompé ;
- entraînement ;
- maîtrise ;
- remédiation ;
- re-test ;
- réactivation ;
- transfert.

## Phase 5 — Moteur éditorial

### Actions

- composants sémantiques ;
- notes adaptatives ;
- en-têtes contextuels ;
- ouvertures robustes ;
- navigation ;
- figures ;
- séparation variantes ;
- manifests observés.

### Gate

- aucun débordement ;
- aucune collision ;
- aucune couche texte cachée ;
- tests sur titres courts/longs et contenus courts/longs.

## Phase 6 — Épreuve anticipée

Créer :

- banque d’automatismes ;
- séquences sans calculatrice ;
- évaluations 6 + 14 ;
- sujets 2 h ;
- progression annuelle ;
- sujets complets ;
- barèmes ;
- copies commentées.

## Phase 7 — Préflight et release

### Actions

- build hermétique ;
- PDF élève/professeur ;
- preflight numérique ;
- preflight imprimeur ;
- épreuve papier ;
- validation finale ;
- checksums ;
- tags immuables ;
- notes de release.

---

# 13. Git, commits et PR

## 13.1 Branche

Ne jamais travailler directement sur `main`.

## 13.2 Commits

Un commit = une intention vérifiable.

Préfixes recommandés :

- `[AUDIT]`
- `[MATH]`
- `[PROGRAMME]`
- `[PEDAGOGIE]`
- `[LATEX]`
- `[PYTHON]`
- `[PDF]`
- `[TESTS]`
- `[CI]`
- `[DOCS]`

Ne pas mélanger :

- correction mathématique ;
- refactorisation ;
- baseline visuelle ;
- migration de métadonnées ;
- mise à jour réglementaire.

## 13.3 Avant commit

```bash
git status --short
git diff --check
git diff --stat
```

Puis exécuter les tests ciblés et les gates affectés.

## 13.4 PR

La draft PR doit contenir :

- périmètre ;
- risques ;
- preuves ;
- tests ;
- captures ou diffs visuels ;
- état des gates ;
- dettes restantes ;
- décisions humaines nécessaires.

Aucune fusion automatique dans `main`.

---

# 14. Utilisation de Chutes

Si le MCP Chutes est disponible :

1. effectuer un smoke test ;
2. utiliser uniquement les modèles réellement listés ;
3. anonymiser les données ;
4. consulter des rôles indépendants :
   - mathématiques ;
   - programme ;
   - pédagogie ;
   - LaTeX/design ;
   - Python/CI ;
   - audit adversarial ;
5. vérifier localement toute recommandation ;
6. consigner la consultation dans `audit/chutes/`.

Chutes est consultatif. Les tests, sources officielles et validations humaines font autorité.

---

# 15. Artefacts de pilotage obligatoires

Codex doit créer ou maintenir :

- `ETAT_COLLECTION.md` — synthétique ;
- `audit/INVENTAIRE_COLLECTION.json`;
- `audit/AUDIT_CONSOLIDE.md`;
- `audit/ANOMALIES_BASELINE.json`;
- `audit/ANOMALY_DISPOSITIONS.yaml`;
- `audit/SOURCE_ROLES.yaml`;
- `audit/PROGRAMME_2026_MATRIX.json`;
- `audit/PROGRAMME_2026_MATRIX.md`;
- `audit/MATH_REVIEW_REGISTER.yaml`;
- `audit/VISUAL_REVIEW_REGISTER.yaml`;
- `audit/HUMAN_APPROVALS.yaml`;
- `audit/BUILD_MANIFESTS/`;
- `audit/RELEASE_CANDIDATE_REPORT.md`.

`ETAT_COLLECTION.md` ne doit pas devenir un dump exhaustif.

---

# 16. CI obligatoire

Créer une CI couvrant :

## 16.1 Structure

- schémas ;
- métadonnées ;
- IDs ;
- références ;
- corrections ;
- variantes ;
- manifests.

## 16.2 Mathématiques

- SymPy ;
- tests numériques ;
- cohérence QCM/corrigés ;
- exercices sans correction ;
- mutations.

## 16.3 Python

- `ast.parse`;
- exécution ;
- sorties ;
- lint ;
- type-check si pertinent ;
- interdiction des caractères invalides.

## 16.4 LaTeX/PDF

- compilation ;
- références ;
- overfull/underfull classifiés ;
- extraction de texte ;
- signets ;
- liens ;
- polices ;
- métadonnées ;
- nombre de pages ;
- raster ;
- diff visuel.

## 16.5 Variantes

- aucun corrigé dans élève ;
- tous les corrigés dans professeur ;
- aucune fuite d’objet ;
- différence attendue et documentée.

## 16.6 Reproductibilité

- deux builds successifs ;
- comparaison déterministe ;
- clone propre ;
- artefacts archivés.

---

# 17. Définition de « terminé »

Le manuel est terminé uniquement si toutes les conditions sont satisfaites :

1. conformité programme 100 % ;
2. zéro erreur mathématique connue ;
3. zéro code invalide ;
4. zéro sortie incohérente ;
5. zéro corrigé dans la version élève ;
6. zéro ID interne visible ;
7. zéro renvoi provisoire ;
8. zéro collision ou débordement ;
9. zéro page d’ouverture cassée ;
10. zéro en-tête trompeur ;
11. tous les contenus hors programme clairement séparés ;
12. boucle Nexus complète par capacité ;
13. épreuve anticipée intégrée ;
14. PDF navigable et correctement métadonné ;
15. build hermétique et reproductible ;
16. CI verte sur le SHA de release ;
17. épreuve papier validée ;
18. double revue disciplinaire ;
19. validations humaines archivées ;
20. artefacts et checksums archivés.

Le nombre de tests n’est pas une preuve suffisante si la couverture des gates est incomplète.

---

# 18. Format de compte rendu Codex

À la fin de chaque session, Codex doit fournir :

```text
ÉTAT <SHA>
Branche : ...
Phase : ...
Commits : ...
Tests ciblés : ...
Tests complets : ...
Gates verts : ...
Gates rouges : ...
P0 ouverts : ...
Décisions humaines requises : ...
PR : ...
Prochaine action atomique : ...
```

Ne jamais conclure « terminé » si un gate obligatoire est rouge.

---

# Annexe A — Procédure de démarrage

```bash
git status --short --branch
git rev-parse HEAD
git log --oneline --decorate -15
git diff --stat
```

Puis :

1. lire `AGENTS.md`;
2. lire le présent document ;
3. lire les audits courants ;
4. vérifier les WIP ;
5. tester Chutes si disponible ;
6. établir un plan atomique ;
7. exécuter le plus petit correctif à fort effet ;
8. tester ;
9. commit séparé ;
10. mettre à jour le pilotage.

---

# Annexe B — Critères de sévérité

- **P0** : erreur mathématique, non-conformité majeure, fuite de corrigé, code invalide, PDF illisible, perte de données, publication impossible.
- **P1** : lacune pédagogique ou réglementaire importante, navigation défectueuse, accessibilité majeure, reproductibilité non démontrée.
- **P2** : qualité éditoriale, cohérence, densité, performance, dette maintenable.
- **P3** : amélioration facultative et non bloquante.

---

# Annexe C — Critère de décision

En cas de doute :

- ne pas approuver ;
- documenter l’incertitude ;
- produire une preuve ;
- consulter un second regard ;
- préférer une correction petite et testée à une refonte massive non vérifiée ;
- ne pas produire de nouveaux chapitres sur une chaîne instable.
