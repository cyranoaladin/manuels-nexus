# Wave 0 — Lancement séparé des corrections Green P0

## Statut et décisions humaines

- Date : 13 août 2026.
- Jalon Red approuvé :
  `c50e455ec1bd3e0506e482e0e475abcd5451e5bb`.
- Branche documentaire : `wave0/p0-green-launch`.
- Décisions humaines :
  - validation du jalon Red ;
  - lancement de corrections Green séparées ;
  - approche A, avec branches et dépendances explicites ;
  - régénération et versionnement des PDF canoniques 1SPE et TSPE autorisés
    seulement après comparaison visuelle et approbation explicite.
- Verdict de publication : **NO-GO** tant que les autres gates de release
  restent rouges.

Le présent document orchestre trois sous-projets. Leurs exigences détaillées
restent dans leurs spécifications dédiées :

1. `2026-08-13-green-p0-programme-tspe-design.md` ;
2. `2026-08-13-green-p0-separation-eleve-design.md` ;
3. `2026-08-13-green-p0-overflow-preflight-design.md`.

## Objectif

Faire passer au vert les contrats P0 validés sans mélanger réglementation,
séparation éditoriale et mise en page. Chaque correction doit conserver sa
propre branche, son cycle TDD, ses commits, ses preuves et ses revues.

## Topologie des branches

```text
c50e455e  jalon Red validé et immuable
└── wave0/p0-green-launch
    ├── green/p0-programme-tspe
    └── green/p0-student-separation
        └── green/p0-overflow
```

`green/p0-programme-tspe` et `green/p0-student-separation` peuvent être
implémentées en parallèle. `green/p0-overflow` est empilée sur la séparation :
les grilles professeur actuellement mêlées aux QCM élèves sont aussi la cause
de plusieurs grands débordements.

La branche Red n'est ni amendée ni réécrite. La branche de lancement ne porte
que les spécifications et plans communs avant la création des branches Green.

## Frontières des trois lots

### Provenance TSPE

Le lot réglementaire corrige les références actives au programme de
mathématiques de Terminale. Il ne modifie aucun contenu pédagogique, PDF,
préflight, charte ou baseline.

### Séparation élève/professeur

Le lot éditorial centralise la politique de détection, corrige sous revue
indépendante deux P0 mathématiques préalables, fait générer séparément les deux
faces de huit QCM JSON-canoniques, retire les IDs/barèmes de deux évaluations
TSPE et résout les renvois provisoires par des cibles calculées. Après preuve
textuelle et approbation visuelle, il peut versionner quatre PDF portant
l'identité `wave0-separation-intermediate` et une dette `Overfull` explicite.
Il ne corrige pas les règles de mise en page générales et ne change pas la
référence réglementaire TSPE.

### Débordements et préflight

Le lot LaTeX/PDF refuse tout `Overfull`, rejoue les quatre builds après la
séparation, rattache les diagnostics restants à leur objet et corrige chaque
cause minimale. Il ne masque aucun diagnostic par une tolérance, une baseline
ou un changement global de densité. Il remplace les quatre PDF intermédiaires
par les PDF Wave 0 finaux sans débordement.

Les métadonnées métier PDF, signets, liens globaux et balisage ne font partie
d'aucun des contrats Red approuvés de ce lancement. Ils restent explicitement
rouges et bloquants pour la release ; Wave 0 ne les déclare pas corrigés.

## Discipline TDD commune

Chaque branche suit l'ordre suivant :

1. reprendre les contrats Red approuvés ;
2. ajouter un test Red plus précis si une frontière manque ;
3. observer l'échec pour la cause attendue ;
4. appliquer un correctif minimal ;
5. rendre verte la famille concernée ;
6. rejouer les tests historiques ciblés ;
7. effectuer une mutation adversariale ;
8. obtenir une revue de conformité puis une revue de qualité ;
9. committer atomiquement.

Aucun test ne peut être transformé en `skip`, `skipif` ou `xfail`. Aucun
wrapper ne convertit un code non nul en succès.

## Workflow des PDF et identité des artefacts

Les builds sont locaux et reproductibles, sans `--record-observed` dans les
worktrees. Les manifests observés ne sont jamais réécrits pour contourner leur
provenance de branche.

Le lot séparation produit, après approbation, l'état intermédiaire auditable.
Le lot overflow utilise exactement ces hashes comme état « avant » et produit
l'état final Wave 0. Les deux étapes possèdent un manifeste distinct.

Pour chaque PDF affecté et pour chaque étape :

1. compiler trois passes LuaLaTeX ;
2. exécuter les gates du lot : texte, journal, `qpdf` et polices ;
3. rasteriser les pages calculées par le diagnostic ou affectées ;
4. produire images, diffs et planche avant/après ;
5. créer un manifeste versionné portant les SHA-256 des PDF, images et
   planches, les versions d'outils, les pages/objets, date et décision ;
6. soumettre la planche et le manifeste à l'approbation humaine ;
7. recalculer les hashes et versionner seulement les artefacts approuvés.

Une approbation visuelle ne rend pas le build « observé » et ne met pas à jour
la baseline. Les métadonnées métier PDF, signets et liens globaux restent
rouges. Une baseline exige une décision distincte qui n'appartient pas à Wave
0.

## Gestion des erreurs et conditions d'arrêt

Le lot concerné s'arrête si :

- deux sources officielles applicables se contredisent ;
- une correction élève supprime le contenu professeur ;
- LuaLaTeX, Poppler ou un journal contractuel est indisponible ;
- la compilation échoue avant le contrôle métier attendu ;
- une correction réclame d'affaiblir un gate ;
- trois hypothèses techniques successives échouent ;
- un changement de baseline ou une décision visuelle non approuvée devient
  nécessaire.

Les échecs historiques étrangers au lot sont reproduits et rapportés
séparément. Ils ne sont ni corrigés opportunément ni masqués.

## Intégration et documentation finale

L'ordre d'intégration proposé est :

1. provenance TSPE ;
2. séparation élève/professeur ;
3. débordements empilés sur séparation ;
4. mise à jour du README racine et de l'état d'avancement ;
5. validation humaine avant toute fusion vers la branche d'intégration.

Les rapports datés restent historiques. Chaque lot corrige uniquement les
affirmations du README que sa propre preuve rend obsolètes. Une mise à jour
finale consolide ensuite les trois états sans recopier les registres ni les
rapports générés.

## Définition de terminé du lancement

Le lancement est terminé lorsque :

- les quatre spécifications sont approuvées et versionnées ;
- trois plans séparés sont approuvés et versionnés ;
- les branches Green sont créées depuis les points de départ prévus ;
- aucune production n'a été modifiée sur la branche documentaire ;
- chaque lot possède un responsable d'implémentation et deux reviewers
  indépendants ;
- les étapes d'approbation humaine des PDF sont explicitement planifiées.
