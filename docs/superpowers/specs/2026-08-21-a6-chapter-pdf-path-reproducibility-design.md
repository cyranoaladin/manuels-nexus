# A6 — reproductibilité PDF du producteur chapitre

## Contexte et défaut observé

Le candidat A6 `bcac52aa9d0f5385b470410320b082ae6f3bd321` est
disqualifié. Fresh A compile `TCOMPL-CALCULS-AIRES`, variante `complet`, avec
le même environnement A4, le même master, les mêmes sources, 18 pages et le
même texte que le worktree candidat, mais obtient un SHA PDF différent.
La seule différence est le trailer `/ID`. Deux runs dans un même clone sont
stables ; deux racines absolues distinctes ne le sont pas.

Cause racine : `scripts/assemble.py` ne fixe pas `\pdfvariable trailerid`.
LuaTeX produit donc une identité stable intra-racine sous
`SOURCE_DATE_EPOCH`, mais dépendante du chemin. `assemble_manuel.py` possède
déjà le contrat A4 correct et path-independent.

## Décision

Le producteur chapitre réutilise exactement la fonction métier A4
`pdf_trailer_identity`. Cette règle est extraite dans un module commun ciblé ;
`assemble_manuel.py` la réexporte pour compatibilité et `assemble.py` l'utilise
directement. Aucun second algorithme de trailer n'est introduit et aucun autre
refactor PDF n'est autorisé dans ce lot.

Pour un chapitre, la préimage contient :

- schéma et version producteur A4 ;
- identité `chapter:<chapter-id>` ;
- variante ;
- master final avant injection du trailer ;
- union ordonnée du graphe runtime exhaustif effectivement lu par LuaTeX et
  des autorités lues par le producteur Python (objets, contrat et gabarit).
  Le wrapper et la classe commune appartiennent au recorder runtime ; la
  charte et le pont canoniques sont ajoutés conservativement au préimage sans
  être chargés par le producteur chapitre, afin de ne provoquer aucun
  changement visuel hors autorisation.

Le graphe n'est pas une liste maintenue à la main. Le producteur effectue une
passe de découverte `-recorder`, dont le PDF provisoire est jeté, puis parse
le `.fls`. Chaque entrée interne au dépôt doit être un fichier Git suivi,
lisible, résolu sans évasion par lien symbolique et identifié par une clé Git
relative canonique unique. Un support requis absent, une résolution hors
racine d'autorité, une collision de clé ou une dépendance interne non classée
fait échouer le build. Les dépendances externes TeX appartiennent à la
toolchain scellée ; les sorties générées sont confinées au répertoire de build
et exclues explicitement. La passe finale `-recorder` doit retrouver exactement
le même graphe runtime brut et les mêmes hashes, avant l'union des autorités
déclarées, sinon le build échoue.

Le producteur exige en outre les chemins exacts des autorités canoniques qu'il
déclare. L'union de préimage ne peut pas masquer une disparition dans le
recorder runtime, car l'égalité brute est vérifiée en premier.

Toutes les passes s'exécutent dans un staging privé sous la cible canonique.
Les sorties `.fls` sont fermées : staging courant, ou transients sous
`TEXMFVAR`/`TEXMFSYSVAR`, uniquement. Après préflight staged, master, log,
recorder final et optionnels présents sont publiés transactionnellement ; les
optionnels absents sont supprimés, puis le PDF est publié en dernier. Le
cleanup staging appartient à la transaction et toute erreur restaure toutes
les destinations depuis un backup sécurisé extérieur au staging. Tous les
backups sont créés et validés avant la première mutation. Après publication
complète et cleanup staging réussi, l'état canonique est engagé : un échec de
cleanup du backup ne déclenche plus de rollback, mais laisse une quarantaine
explicitement signalée avec son chemin sur stderr.

Les chemins absolus, cwd, racine temporaire, horloge, run ID, HEAD, PDF
antérieur, build outputs et attestations sont exclus. Remplacer un ancien PDF
suivi ne modifie donc jamais la préimage source.

## Injection et comportement

`assemble.py` écrit d'abord un master de découverte après substitution de tous
les placeholders. Après la passe jetable et la validation du graphe, il calcule
l'identité sur le même master sans trailer, puis écrit le master final. Il
injecte une seule ligne
`\pdfvariable trailerid{[<ID> <ID>]}` immédiatement après
`\documentclass`. Une injection impossible ou multiple est une erreur de
production fail-closed.

L'environnement reproductible reste celui de l'autorité A4 :
`SOURCE_DATE_EPOCH=1785962466`, `FORCE_SOURCE_DATE=1`, `TZ=UTC`,
`LC_ALL=C.UTF-8`, `LANG=C.UTF-8`, `PYTHONHASHSEED=0`. Le correctif ne remplace
pas ce contrôle ; il ferme la seule donnée résiduelle dépendante du chemin.

## Tests et preuves

Le cycle RED reproduit deux racines absolues distinctes avec le même chapitre
et observe des PDF différents avant correction. Le GREEN exige des octets
identiques. Les dix cas mandatés ont une matrice explicite : les cas 1 à 5 et
10 compilent réellement un PDF ; mutation puis restauration prouvent le retour
exact au trailer et au SHA d'origine. Le cas 6 compile les variantes élève et
professeur via le contrat partagé et exige des résultats déterministes mais
distincts lorsque contenu ou variante diffère. Les cas 7 et 8 prouvent la
séparation chapitre/version producteur ; le cas 9 prouve qu'un ancien PDF
suivi est hors préimage ; le cas 10 utilise deux vrais worktrees Git.

Des mutations couvrent chaque classe de dépendance observée et les erreurs
fail-closed : support manquant, entrée interne non suivie, sortie de racine,
collision de clé et graphe découverte/final divergent. La suite A4 autoritaire
`tests/test_pdf_reproducibility.py` (PDF1 à PDF10) est rejouée intégralement
après l'extraction du helper ; aucun contrat manuel n'est affaibli.

Le diagnostic réel est archivé dans
`audit/A6_CHAPTER_PDF_PATH_REPRODUCIBILITY.md`. Après GREEN, le chapitre réel
TCOMPL est compilé dans deux clones neufs et doit produire le même SHA avant
tout replay global.

## Scellement

Le correctif, ses tests et le diagnostic sont atomiques. Les artefacts
manifeste/inventaire sont ensuite rafraîchis si leur digest le requiert. Une
nouvelle attestation remplace le candidat disqualifié, puis Fresh A et Fresh B
sont recréés de zéro au nouveau SHA. A6 n'est PASS que si tests, inventaire,
gates, masters, pages, digests et PDF concordent.

## Hors périmètre immédiat

Aucune source pédagogique, statut, qualification, baseline, oracle visuel ou
décision humaine n'est modifiée. Les dettes structurelles suivantes ne
commencent qu'après le nouveau PASS hermétique A6.
