# A6 — master manuel canonique indépendant du run

## Défaut observé

Le scellement Fresh A / Fresh B au SHA
`139df05260a61dc5680be252231a67fd1ee57f71` produit des PDF TCOMPL
octet-identiques, mais pas des masters octet-identiques. Les seuls octets
différents sont ceux de la ligne `NEXUS_BUILD_RUN:<32 hex>` :

- élève : `72c513a2…` dans A, `867070ea…` dans B ;
- professeur : `0dabd90f…` dans A, `392571e6…` dans B.

Le producteur génère un token aléatoire, le sérialise dans le master canonique,
puis le validateur de receipt exige ce même token dans le master et dans le
journal. Il s'agit donc d'une dépendance contractuelle à corriger, pas d'un
simple artefact de test.

## Autorité et décision

Le mandat publish-ready exige simultanément :

- un `run_id` d'exécution aléatoire et non rejouable ;
- un log, un préflight et un receipt liés à ce `run_id` ;
- un master canonique identique pour les mêmes sources, indépendamment du
  `run_id`, du chemin et du worktree ;
- un PDF identique pour les mêmes sources.

Cette spécification supersède uniquement la clause historique qui exigeait le
token concret dans le master. Elle ne réécrit pas l'attestation historique A4.

Les producteurs Math et NSI portent le même **protocole conceptuel de hook
LuaTeX constant**. Une copie de leur environnement A4 scellé reçoit
`NEXUS_BUILD_RUN=<32 hex>` uniquement pour les trois appels LuaLaTeX. Le
hook :

1. lit cette variable ;
2. rejette une valeur absente ou différente de 32 hexadécimaux minuscules ;
3. écrit exactement une ligne `NEXUS_BUILD_RUN:<id>` dans le journal ;
4. n'écrit aucun octet dans le document rendu.

Le master ne contient jamais le token concret. Le base environment reste
inchangé et ne reçoit pas la variable : Git, `pdfinfo`, `pdffonts`, Python et
le recorder de manifeste ne la voient jamais.

## Alternatives rejetées

### Normaliser le master après compilation

Rejeté. Le master hashé et publié ne serait plus celui ouvert dans le `.fls`.
La chaîne `master -> FLS -> log -> PDF -> receipt` deviendrait fausse.

### Rendre le run ID déterministe

Rejeté. Une identité de contenu et une identité d'exécution ont des fonctions
différentes. Un run ID déterministe perd son unicité, facilite le rejeu d'une
preuve stale et contredit le contrat de receipt.

## Flux de données

1. Le producteur charge le contrôle A4 et construit l'environnement de base
   fermé : `PATH`, `HOME`, `SOURCE_DATE_EPOCH`, `FORCE_SOURCE_DATE`, `TZ`,
   `LC_ALL`, `PYTHONHASHSEED`.
2. Il génère un `run_id` aléatoire validé par `[0-9a-f]{32}`.
3. Le renderer Math et le renderer observé NSI produisent un master sans
   argument ni octet dépendant du run.
4. Un helper copie l'environnement de base, ajoute la seule clé
   `NEXUS_BUILD_RUN`, puis cette copie est passée aux trois appels LuaLaTeX.
5. Le hook constant du master écrit le token dans le journal. Une variable
   finale absente ou mal formée fait échouer LuaLaTeX avec `-halt-on-error`.
6. Le `.fls` prouve toujours l'ouverture du master canonique ; le receipt
   conserve son digest exact.
7. Le validateur commun de manifeste exige pour Math **et** NSI :
   - le hook constant unique et intact dans le master ;
   - aucun token concret `NEXUS_BUILD_RUN:<32 hex>` dans le master ;
   - exactement le `run_id` du receipt dans le log ;
   - le même `run_id` dans le préflight et le receipt ;
   - le master parmi les `INPUT` du `.fls` ;
   - tous les digests de preuve inchangés.

## Compatibilité et migration

Le shape du receipt, du préflight et du build manifest reste inchangé. Aucun
receipt ou préflight n'est suivi par Git et `audit/BUILD_MANIFEST.json` est
vide. Il n'existe donc aucune migration de donnée autorisée ou nécessaire.
Les deux producteurs observés actifs, Math et NSI, migrent atomiquement vers
le hook. Une ancienne preuve dont le master contient un token concret est
rejetée et doit être reconstruite par `--record-observed`.

La fonction Math `render_master` perd l'argument `run_id`. La fonction NSI qui
instrumente le master observé perd également cet argument. Tous leurs
consommateurs sont internes au dépôt ; garder un argument ignoré créerait une
fausse API de compatibilité.

## Sécurité et erreurs fail-closed

- Le helper d'environnement refuse tout run ID mal formé.
- Il copie la map scellée au lieu de la muter.
- La variable n'est transmise qu'aux trois compilations LuaLaTeX.
- Une variable hôte portant le même nom est ignorée et remplacée par le token
  généré par le producteur. Seule une valeur explicitement fournie au helper
  ou finalement visible par le hook et mal formée provoque un rejet.
- Le hook est validé comme une ligne de protocole exacte ; hook absent,
  dupliqué ou altéré est refusé.
- Un ancien master avec token concret est refusé, même si ses digests ont été
  recalculés.
- Les vérifications de journal, FLS, PDF, préflight et receipt restent fermées.

## Preuves TDD

Le RED doit reproduire le défaut réel avant toute modification de production :

1. deux `render_master`/builds avec des run IDs distincts donnent actuellement
   deux masters différents ;
2. Fresh A / Fresh B ont déjà fourni les hashes divergents ci-dessus.

Le GREEN exige :

- masters byte-identiques pour deux run IDs distincts ;
- master avec un hook constant unique et aucun token concret ;
- deux compilations LuaHBTeX réelles du même master avec deux environnements
  de run : PDF identiques, logs portant chacun uniquement leur ID ;
- variable absente, majuscule, trop courte ou trop longue dans l'environnement
  final : rejet ; variable hôte hostile : écrasée et absente des preuves ;
- seuls les trois appels LuaLaTeX voient la variable ;
- recorder : hook + log exact acceptés ; ancien master concret, hook absent,
  dupliqué ou modifié, log/preflight incohérent : rejet ;
- vrais modes `--record-observed` 1NSI et TNSI compatibles avec le nouveau
  validator commun ;
- matrice pure des quatre manuels Math et des deux manuels NSI, chacun en
  élève/professeur, prouvant que le master ne dépend pas du run ;
- suites PDF1–PDF10, assembleur observé et build-manifest intégralement vertes.

Deux compilations réelles comparent aussi l'ancien `\typeout` et le nouveau
hook avec la même préimage. Le nouveau hook ne peut pas être accepté sur la
seule égalité A/B : les PDF TCOMPL reconstruits doivent rester identiques aux
PDF canoniques connus :

- élève : `6212a21b273605d416a35337b7f26c10ca78289c02b465d7b13924e32f9abd0f` ;
- professeur : `d14ec54cdd5641ce13739316f2ec5b3e92d11039aa1b43bab9b2a3b822bb4a3b`.

Les smokes 1NSI doivent de même rester identiques à
`7396cc0051fe488d3dad1f00537d919bbdac13eb839770784acace3edea24d39`
et `d91512273ee8753e3590bc236267ddc12e4b1310610f4f5bdb8ffacc9ac9bc31`.
Une divergence exige une analyse binaire, textuelle et visuelle ; elle n'est
jamais qualifiée de reproductible au seul motif que A et B divergent de la
même façon.

## Scellement A6

Après le commit source :

1. compiler TCOMPL élève/professeur deux fois dans deux clones sans hardlinks,
   ainsi que les smokes 1NSI élève/professeur ;
2. exiger master, PDF, pages, texte et trailer A == B ;
3. rafraîchir le manifeste vide et l'inventaire par commits séparés si leurs
   digests sont stale ;
4. rejouer les suites root, Math, NSI, A1–A6 et tous les gates ;
5. recréer Fresh A et Fresh B de zéro au nouveau SHA ;
6. mettre à jour l'attestation seulement après l'égalité complète.

Le défaut `assemble_livrets.py` similaire est consigné comme dette distincte.
Il n'est pas masqué ni mélangé au protocole des six manuels et douze variantes.
Le lot A6 prouve les cibles réellement affectées TCOMPL/1NSI et la matrice
pure des douze variantes ; le rebuild intégral des douze PDF reste le gate T10,
pas une conclusion dérivée des seuls smokes A6.
