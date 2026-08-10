# Dix P0 scientifiques 1NSI - Design

## Objectif

Corriger séparément les dix P0 scientifiques découverts par la réattestation
`BUILD_MANIFEST`, avec une régression observée rouge puis verte pour chaque défaut,
un commit source atomique par P0 et une revue indépendante par correction. Cette
passe reste strictement limitée à 1NSI et ne vaut pas approbation de publication.

## Frontières atomiques

Chaque unité comprend son test de régression et la plus petite surface éditoriale
cohérente. Les exercices élève associés aux corrigés 053 et 054 appartiennent à la
même unité que leur corrigé afin de ne jamais publier un énoncé et une réponse aux
contrats contradictoires.

1. `1NSI-REV-LANG-COURS-C4-MAXIMUM-ZERO` : remplacer la fausse condition
   « valeur positive » par « valeur positive ou nulle » et distinguer les listes
   `[-5, 0, -8]` et `[-5, -1, -8]`.
2. `1NSI-REV-LANGAGE-RE-C4-LISTE-VIDE` : annoncer dans la remédiation que la liste
   est non vide et vérifier ce contrat dans le bloc exécutable.
3. `1NSI-REV-LANGAGE-RE-C4-CORRIGE-LISTE-VIDE` : documenter et vérifier la
   non-vacuité dans la réponse modèle, avec une régression sur `[]`.
4. `1NSI-REV-PM-COURS-C2-JALONS-VIDES` : exiger au moins un jalon avant la division
   par `len(jalons)` et tester `[]`.
5. `1NSI-REV-PM-COURS-C3-POIDS-NEGATIFS` : exiger des poids non négatifs et une
   somme strictement positive ; tester séparément un poids négatif et une somme
   nulle.
6. `1NSI-REV-TAB-COURS-C4-COLLISION-COLONNES` : exiger que les colonnes non-clés
   des deux tables soient disjointes et refuser explicitement une collision.
7. `1NSI-REV-WEB-SERVER-VISIBILITY-COURSE` : remplacer l'impossibilité absolue par
   le fait exact que le code serveur n'est normalement pas transmis au navigateur
   dans la réponse HTTP.
8. `1NSI-REV-TC-COURS-C5-COPIE-PROFONDE-INCOMPLETE` : enseigner une copie des deux
   premiers niveaux, indépendante sous la précondition de cellules scalaires atomiques
   non mutables, sans conteneur imbriqué.
9. `1NSI-REV-TC-CO-053-COPIE-PROFONDE-INCOMPLETE` : appliquer le même contrat à
   l'énoncé 053 et à son corrigé.
10. `1NSI-REV-TC-CO-054-COPIE-PROFONDE-INCOMPLETE` : appliquer le même contrat à
    l'énoncé 054, au nom de fonction et au corrigé.

La copie récursive et `copy.deepcopy` ne sont pas présentés comme exigibles. Les
cellules admises sont des valeurs scalaires atomiques non mutables comme des nombres,
booléens, chaînes ou `None`, jamais des tuples ou autres conteneurs susceptibles
d'enfermer une référence mutable. Sous ce contrat, les deux listes externes et chaque
ligne sont distinctes : les changements de structure et les réaffectations de cellules
dans la copie n'affectent pas l'original. Un contre-exemple avec une cellule contenant
une liste montre explicitement que la construction ne garantit rien hors contrat.

## Régressions

Un fichier ciblé `NSI/tests/test_1nsi_scientific_p0_regressions.py` contient dix
tests nommés d'après les comportements corrigés. Les tests textuels interdisent les
formulations absolues ou scientifiquement fausses. Les unités exécutables possèdent
une source canonique dédiée sous le dossier `code/` de leur chapitre : minimum,
avancement, moyenne pondérée, fusion et copie de grille. Les tests importent et
exécutent ces fichiers `.py`, puis exigent que le bloc Python rendu en LaTeX soit une
copie exacte de la source canonique applicable. Toute sortie publiée est capturée à
partir de cette exécution puis comparée exactement au bloc console rendu ; aucun
résultat n'est maintenu comme commentaire saisi manuellement. Aucun test n'est
affaibli, ignoré ou marqué `xfail`.

Pour chaque unité :

1. ajouter uniquement le test du P0 ;
2. l'exécuter et observer son échec pour la cause attendue ;
3. corriger la source minimale ;
4. exécuter le test ciblé, le vérificateur Python du chapitre et les gates affectés ;
5. committer le test, la source `.py` éventuelle et la source LaTeX ensemble ;
6. obtenir une revue indépendante avant de déclarer le P0 fermé.

## Revue indépendante

Chaque commit source reçoit une attestation d'un relecteur distinct de l'intégrateur.
Le relecteur vérifie la source complète, le cas limite, la cohérence élève/professeur,
le résultat des tests et l'absence de dérive TNSI. Une attestation refusée rouvre
l'unité et interdit de passer à sa clôture d'audit.

Chaque attestation durable consigne le SHA du commit source, les chemins et SHA-256
relus, l'identité et le modèle du reviewer, un `run_id` unique, le `session_id` utilisé,
l'identifiant de génération éventuel, le statut de cache, les commandes et résultats
observés, puis le verdict. Un `session_id` peut être partagé par les appels d'un même
lot pour favoriser le cache ; il ne remplace jamais l'identité unique du run. Un cache
`HIT` optimise un transport mais ne constitue jamais une nouvelle revue indépendante.

Les attestations unitaires ne remplacent pas les reçus canoniques. La migration du
protocole invalide les six reçus : `contracts`, `algorithms`, `systems-web`,
`language-project`, `data-basics-tables` et `types-construits`. Les six lots sont donc
réattestés avec six identités et six runs nouveaux, deux à deux distincts, puis scellés
ensemble avant reconstruction du registre.

Si OpenRouter est utilisé avec une clé valide, les appels répétés partagent un
`session_id` stable par lot et placent le contexte invariant avant la question
variable. Les modèles exigeant un cache explicite reçoivent un bloc
`cache_control: {type: ephemeral}` ; le cache de réponse OpenRouter n'est activé que
pour des requêtes strictement identiques. Aucune clé n'est écrite dans le dépôt, les
commandes, les audits ou l'historique shell.

## Variantes et compilation

Les sélections d'objets doivent prouver que les cours sont présents dans `eleve` et
`professeur`, les remédiations dans `remediation` et `professeur`, les corrigés dans
`professeur` seulement, et les exercices 053/054 dans `eleve` et `professeur`. Chaque
chapitre affecté est compilé dans un emplacement temporaire ; aucun PDF canonique et
aucune baseline visuelle ne sont promus dans cette passe.

## Gouvernance et builds

Les changements de sources invalident leurs enveloppes de revue et le manifeste de
build. Le manifeste étant vide, l'unique opération admissible est
`python scripts/build_manifest.py --refresh-empty`. Après les dix commits
disciplinaires et leurs attestations :

1. rafraîchir le `BUILD_MANIFEST` vide ;
2. migrer la policy dans un commit dédié avec une nouvelle base propre, le nouveau
   hash du manifeste et le nouveau `protocol_digest` ;
3. vérifier une première transition rouge bornée aux six anciennes enveloppes ;
4. réattester et sceller les six lots ;
5. vérifier une seconde transition rouge bornée aux anciennes provenances des findings ;
6. reconstruire les 349 findings et les sorties JSON/Markdown depuis les blobs
   scellés ;
7. resynchroniser uniquement les sorties d'inventaire réellement obsolètes ;
8. exécuter les suites complètes, `--verify-scope`, `--validate-model`,
   `--fail-on-new` et le refus attendu de `--release-strict`.

Les dix IDs P0 ciblés doivent disparaître des sorties canoniques. Tout autre delta,
notamment la fermeture collatérale possible de
`1NSI-REV-PM-COURS-C3-DENOMINATEUR` ou de dettes de provenance Python, est dérivé et
justifié par les nouvelles revues au lieu d'être forcé. Aucun statut n'est promu et
aucune décision de publication n'est prise dans cette passe.

## Garde TNSI

Le SHA initial immuable de la passe est
`bdd3285b75aeedf2c23382c58aacb0d99070a1b9`. Les contrôles suivis et non suivis
portent sur `NSI/chapitres/TNSI-*`, `NSI/referentiel/capacites_TNSI_*`,
`NSI/docs/11_perimetre_terminale.md`,
`NSI/sources/txt/BO2019_NSI_terminale.txt` et `NSI/build/MANUEL_TNSI*`. Ils restent
indépendants du futur SHA de base inscrit dans la policy.

## Critères d'acceptation

- dix commits source atomiques et identifiables ;
- dix cycles rouge/vert observés ;
- dix attestations indépendantes approuvées ;
- six lots réattestés avec six identités et runs distincts, puis scellés ensemble ;
- couverture exacte des 349 qualifications sans provenance obsolète ;
- zéro modification TNSI ;
- suites et gates de non-régression verts ;
- `--release-strict` toujours rouge pour des blocages réels.

L'ordre des deux unités de remédiation C4 commence par le corrigé, puis l'énoncé. Le
couple est contrôlé après chacun des deux commits afin de réduire la fenêtre de
divergence entre consigne et réponse modèle.
