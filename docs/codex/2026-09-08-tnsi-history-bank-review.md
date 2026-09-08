# TNSI — banque écrite, programme comme donnée et chronologie

Lot C du 8 septembre 2026, préparé par Codex `review_forensics`. Base observée : `e5a97527fc9bb286a1da997a33774f58cd854161` ; le worktree contient les corrections décrites et d'autres travaux indépendants. Portée : `WORKTREE_BOUND_BY_INPUT_DIGESTS`, avec les empreintes ci-dessous ; ce n'est pas une certification du seul HEAD. L'énoncé, les cinq réponses, la critique, le barème et les quatre programmes ont été lus entièrement. La contre-revue indépendante du contenu corrigé reste à effectuer. Aucun statut humain ni receipt de release n'est créé.

## Défauts et corrections déterminables

L'ancien corrigé déduisait l'universalité de quelques exécutions d'un petit interpréteur et imposait une chaîne causale historique à partir de l'ordre des années. Il assimilait aussi la fonction Python à un matériel et les machines antérieures au programme enregistré à des dispositifs monotâches. Ces conclusions n'étaient établies ni par les exemples ni par les documents. L'assertion comparant une fonction à elle-même ne vérifiait aucune propriété.

Le texte distingue maintenant trois questions : représenter un programme comme une donnée ; exécuter plusieurs programmes avec les mêmes règles ; établir l'universalité d'un modèle. Les deux premières sont illustrées. La troisième ne découle pas des trois exemples : notre langage réduit n'a ni branchement ni boucle. La réponse ne revendique pas une preuve générale de non-universalité par tests. L'exécuteur est explicitement un logiciel écrit en Python, et le dictionnaire ne prétend pas reproduire tous les organes d'un ordinateur.

La question 5 compare la représentation et le stockage des instructions avec l'intégration électronique du processeur. Elle accepte une critique justifiée de la causalité supposée. Le programme enregistré n'est plus présenté comme la naissance de toute programmabilité, et une puce de processeur n'est pas confondue avec un ordinateur complet.

Le code imprimé ne disposait pas de compagnons `.py` explicites. Quatre fichiers réels sont désormais liés par `PYTHON-SOURCE`. L'interpréteur exige exactement les instructions annoncées et rejette les formes inconnues ou mal formées par `ValueError`. Le domaine annoncé est un dictionnaire d'adresses entières et d'instructions textuelles ; aucune garantie n'est ajoutée pour des objets Python arbitraires hors de ce domaine.

## Affirmations documentaires, indépendantes de Python

- **1936, modèle et universalité.** Le [texte original de Turing](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf) porte les dates de réception et de lecture en 1936, page imprimée 230. Le paragraphe 6, pages 241–242, décrit une machine qui utilise la description d'une autre machine pour en reproduire le calcul. Cela soutient la notion invoquée et la limite de notre illustration ; trois sorties particulières ne constituent pas cet argument. Verdict documentaire borné : soutenu.
- **1945, instructions et mémoire.** Le [rapport EDVAC daté du 30 juin 1945](https://real.mtak.hu/170042/1/Firstdraft.pdf), paragraphes 2.3–2.5 et 14.1, distingue contrôle, instructions et mémoire ; le paragraphe 14.1 fait provenir de M les ordres et le matériel numérique. Le repère concerne cette description d'architecture, sans attribuer toute invention de la programmabilité à cette année ni à un auteur unique. Verdict documentaire borné : soutenu.
- **1971, microprocesseur commercial.** Le [document Intel sur le 4004](https://download.intel.com/newsroom/archive/2025/en-us-2021-11-15-intel-marks-50th-anniversary-of-the-intel-4004.pdf), pages PDF 1–2, situe sa commercialisation en novembre 1971 et précise qu'il est un des quatre circuits conçus pour la calculatrice Busicom. La formulation porte sur une unité centrale intégrée, sans transformer cette puce en ordinateur complet. Verdict documentaire borné : soutenu.
- **1989, proposition du Web.** Le [récit du CERN](https://home.cern/science/computing/the-birth-of-the-web/short-history-web/) distingue la proposition de mars 1989, sa mise en œuvre et sa diffusion ultérieures. Le tableau dit bien « proposition du Web » ; il ne date pas sa diffusion publique de 1989. Verdict documentaire borné : soutenu.
- **Programmabilité avant 1945.** La [collection Harvard, livraison du Mark I](https://chsi.harvard.edu/harvard-ibm-mark-1-about) le date de 1944 ; sa [description du fonctionnement](https://chsi.harvard.edu/harvard-ibm-mark-1-function) explique la commande par instructions sur bande et différents usages. Ce contre-exemple réfute l'affirmation selon laquelle toutes les machines antérieures étaient monotâches. Il ne sert pas à démontrer une autre chaîne causale universelle. Verdict documentaire borné : soutenu.

Les extraits documentaires pertinents ont été lus, notamment le paragraphe 6 de Turing et le paragraphe 14.1 d'EDVAC. Aucune date ou attribution ne reçoit un crédit d'exécution. Les quatre dates du bloc VERIFY sont seulement les données du calcul d'écarts.

## Résolution et alignement pédagogique

Les écarts successifs sont 9, 26 et 18 ans, de somme 53. Dans le premier programme, l'accumulateur reçoit 5 puis 3 est ajouté : la seule sortie est `[8]`. Le second programme donne `[17]` par 10 + 7. Le troisième affiche d'abord 0 puis 1. Chaque appel réinitialise son accumulateur et sa liste de sortie ; parcourir les adresses triées garantit l'ordre annoncé, y compris avec des adresses non consécutives. Aucune affectation ne modifie le dictionnaire reçu. La boucle parcourt une liste finie de clés : dans le domaine annoncé, elle termine ou lève l'exception documentée.

Les questions 3 et 4 changent le dictionnaire et gardent le même exécuteur. Les réponses répondent à cette demande et expliquent les limites du rapprochement avec le programme enregistré et la machine universelle. La question 5 distingue les concepts avant d'évaluer la causalité. Le barème reste 4 + 5 + 4 + 3 + 4 = 20 points ; les 3 points de Q4 et les 4 points de Q5 récompensent désormais des éléments réellement demandés et justifiables.

Le contrat C1 renvoie à `T-HIST-01A` (situer des événements et protagonistes) et C2 à `T-HIST-01B` (évolution des rôles relatifs logiciel/matériel). La rubrique Histoire du [BO de Terminale NSI](https://www.education.gouv.fr/bo/19/Special8/MENE1921247A.htm), lue dans le texte local aux lignes 127–151, permet de construire ces repères avec les concepts. Cet exercice soutient les repères et la comparaison des rôles ; il ne couvre pas à lui seul tous les événements, protagonistes ou dimensions de C1/C2. Aucun atome officiel ni quota n'est modifié.

## Exécution et tests de régression

Le code a été lu avant toute exécution. `verify_python.check_object` a exécuté le bloc VERIFY avec le confinement canonique sans réseau et Ruff activé : **14 assertions réellement atteintes, zéro assertion échouée, quatre alignements de sources et quatre contrôles Ruff réussis**. Le protocole conserve `certifies_documentary_claims=false` et `certifies_complete_program_correctness=false`. La correspondance des AST lie les programmes ; elle ne prouve pas à elle seule qu'une fonction a été appelée. Ici, les appels et les assertions ont effectivement exercé CHARGER, AJOUTER, AFFICHER et le rejet.

Les probes indépendants exécutent la fonction effectivement imprimée : mémoire vide, affichage seul de l'accumulateur initial, adresses non consécutives en ordre d'insertion différent, opérandes négatifs, dictionnaire inchangé, remise à zéro entre appels et cinq instructions incorrectes. Avant correction, le test de liaison des sources et quatre rejets attendus échouaient : **5 FAILED, 6 PASSED**. Après correction et ajout des mutations : **13 PASSED**.

Deux mutations temporaires changent l'addition en soustraction. Si seul le `.py` change, l'alignement refuse le crédit. Si les trois représentations (`.py`, code imprimé et définition dans VERIFY) changent ensemble, leurs AST concordent mais les résultats attendus échouent. Le test ne se contente donc pas de comparer deux copies du même opérateur. Aucun test lexical ne prétend établir une date.

Commandes finales ciblées observées :

```text
python -m pytest NSI/tests/test_tnsi_history_interpreter.py -q
python -m ruff check NSI/tests/test_tnsi_history_interpreter.py NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/code --select F,E9
git diff --check
```

La première commande a produit **13 PASS en 2,60 s** lors de la relecture finale. Aucun skip ou xfail n'est ajouté. L'observation de développement est dans `/tmp/nexus_tnsi_history_bank_execution.json` ; elle n'est pas un receipt et n'est pas un artefact durable nécessaire pour réexécuter les tests ci-dessus. Les sources historiques sont conservées par Git. Aucun ancien receipt n'est transféré au nouveau contenu ; tout consommateur courant doit vérifier les nouveaux digests et la méthode.

## Limites et empreintes

Ce lot ne clôt pas le chapitre globalement. Son statut source `generated` n'est pas promu par l'auteur. Le rendu PDF, les coupures des listings, la séparation finale élève/professeur, le statut humain du contrat et l'accroche encore à réexaminer ne sont pas validés ici. La contre-revue indépendante du nouveau contenu reste distincte de ces tests et de toute approbation humaine.

Les SHA256 des sources, dépendances et implémentations effectivement relues sont listés ci-dessous. L'ajout des compagnons Python change les dépendances du chapitre ; les preuves qui couvrent ces dépendances doivent être recalculées ou relues selon leur portée réelle.

- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/banque_ecrite/TNSI-ECRIT-S6-EX3.tex` : `145c6ce7ae08692cbf8b28099678577d28c8402485f9778ebcb1fe904f7621a9`

- `NSI/tests/test_tnsi_history_interpreter.py` : `83f127c50d24a5f7dd27f345b792529b1939b653628d28a13fccc26ee78ca6e7`

- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/contrat.yaml` : `a0fe58ea6033423ee35d8ad401310e43945bafc0dc2375f04787023333dc5f48`

- `NSI/sources/txt/BO2019_NSI_terminale.txt` : `3cfce30c85fdc7ab78eb9acb39e43bcb33d6205e0c4205d4cb499f80c097f15b`

- `audit/official_program_coverage/TNSI.json` : `95608c6e9cbd5b42077d3d2a7056fe58e24c03c4d7ea57930f06dc3410b24b34`

- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/code/tnsi_hist_s6_ex3_programme_1.py` : `713a26b93fc5a43ee6137cdb52afa1fc71c5adc715f33501137a66998ff2ca0c`

- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/code/tnsi_hist_s6_ex3_interpreteur.py` : `92387aa080faaf6a25078ff8a9d5722d8cccc64037b76166f1771e4101ad3299`

- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/code/tnsi_hist_s6_ex3_programme_2.py` : `dcdc9a7dd7f4d0144245b0b926d0853fd6ab536939e48676e67b58a5fad3b375`

- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/code/tnsi_hist_s6_ex3_programme_3.py` : `278f118c2fc52c46eba9ca6e475b518eb7001b541c52900814d5b5fd95c5f521`

- `NSI/scripts/verify_python.py` : `66ef29b688bc64c81122db9604382d92fef741092ada14441855f1a0d2591675`

- `NSI/scripts/execution_protocol.py` : `71c6ee70eb91f1869c17b4087f35da75018a7e848e1038ec338a5c99810f95e5`

- `NSI/scripts/common.py` : `37822308dace9072c0bedccc3d73c4646dc9010aa859a64591a1fa7ad7338e53`

- `scripts/review_1nsi_content.py` : `e91ff3ae8aff09573a136c9e292b3975e316b9ba78d013ecdcc925c70935686f`

## Contre-revue indépendante `/root`

Le sujet, les cinq réponses, le barème, la critique, la portée pédagogique, les quatre fichiers Python et les treize tests ont été intégralement lus avant exécution. Les treize empreintes ci-dessus correspondent aux fichiers présents lors de la contre-revue. Les commandes ciblées produisent **13 PASS en 2,51 s**, y compris la mutation simultanée du `.py`, du listing et du bloc VERIFY : l'accord entre copies ne masque pas un résultat faux.

La résolution indépendante retrouve les écarts 9, 26 et 18, puis 53 ans au total. Pour le code, l'accumulateur représente après chaque adresse le dernier entier chargé, augmenté des additions suivantes ; chaque instruction AFFICHER copie sa valeur courante dans la sortie. Les clés triées forment une liste finie, les valeurs textuelles ne sont pas modifiées, et les variables locales sont recréées à chaque appel. Cela justifie l'ordre, la terminaison sur les entrées prévues, l'absence de mutation du dictionnaire et la remise à zéro, au-delà des seuls exemples. Les trois résultats `[8]`, `[17]` et `[0, 1]` suivent directement ces règles. Les formes d'instruction inconnues ou mal formées examinées sont rejetées ; aucune conclusion historique ou preuve d'universalité n'en est déduite.

Les documents Turing, EDVAC, Harvard et CERN déjà ouverts et relus pour le lot B soutiennent les affirmations conservées ici. Le document Intel cité a été ouvert indépendamment : ses pages 1–2 datent la commercialisation du 4004 de novembre 1971 et le situent parmi quatre circuits de la calculatrice. La distinction entre architecture à programme enregistré et intégration d'une unité centrale est donc pertinente ; l'ordre des dates ne prouve pas leur nécessité logique réciproque. Le barème total vaut 20 points et récompense les éléments effectivement demandés, y compris la critique de la causalité supposée.

Le corrigé est présent dans le même fichier que l'énoncé, ce qui a nécessité de contrôler sa destination réelle. Le sélecteur canonique `assemble_manuel`, configuré pour TNSI, exclut ce fichier du manuel élève et le sélectionne pour le manuel professeur et la banque écrite. Ce contrôle de sélection a été exécuté ; il ne remplace pas la recherche de contenus cachés dans les PDF finaux.

Verdict borné : `VALIDATED_BY_EVIDENCE` pour la lecture scientifique et documentaire, les réponses et le code de ce lot. Aucun statut `HUMAN_APPROVED`, receipt humain, gel ou verdict global du chapitre n'est créé. Les autres résidus documentaires du chapitre et les contrôles de rendu demeurent ouverts.
