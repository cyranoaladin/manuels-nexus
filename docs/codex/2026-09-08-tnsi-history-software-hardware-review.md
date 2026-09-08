# TNSI — rôles du logiciel et du matériel

Correction documentaire et pédagogique du 8 septembre 2026, lot B après `987caad07`. Observation de travail liée aux digests ci-dessous. L'auteur des corrections est Codex `review_forensics`, indépendant des auteurs des sources reprises ; une contre-revue fraîche des corrections reste nécessaire. Aucun texte officiel, statut humain, receipt historique ou ledger courant n'est modifié par ce lot.

## Défauts réellement corrigés

Le corrigé de l'évaluation B affirmait que les machines des années 1950 étaient quasi dédiées à une tâche, puis que le logiciel déterminait entièrement le comportement actuel avec une flexibilité quasi illimitée. Les documents contredisent l'opposition : le Mark I, livré en 1944, lit des instructions sur bande et effectue plusieurs types de calculs ; l'IBM 701 de 1952 est polyvalent. Le cours, l'évaluation et la remédiation C02 distinguent maintenant la programmabilité ancienne, les couches d'abstraction et les contraintes matérielles. Sources : [Harvard, fonctionnement du Mark I](https://chsi.harvard.edu/harvard-ibm-mark-1-function), [Harvard, usages](https://chsi.harvard.edu/harvard-ibm-mark-1-use), [Harvard, livraison de 1944](https://chsi.harvard.edu/harvard-ibm-mark-1-about), [IBM, série 700](https://www.ibm.com/history/700).

Le cours situe la commercialisation de Fortran en 1957, sans faire naître alors la programmabilité. Il décrit le rôle de traduction du compilateur. Source : [IBM, Fortran](https://www.ibm.com/history/fortran). Le système GM-NAA est présenté comme enchaînant des travaux dès 1956, sans dater tous les systèmes d'exploitation des années 1960 : [Robert Patrick, récit du participant et références archivistiques](https://softwarepreservation.computerhistory.org/os/gm.html). Le partage et la protection sont documentés dans les années 1970 par [Ritchie et Thompson, version BSTJ de 1978, introduction et sections 3.5 et 5](https://www.nokia.com/bell-labs/about/dennis-m-ritchie/cacm.html). Cette édition est une révision du texte de 1974 ; ses nombres ne sont pas attribués rétroactivement à 1974.

Le four anonyme des années 1980 opposé à un four connecté moderne n'avait pas de modèle identifié ni de preuve. Il est remplacé par la comparaison du Mark I avec le téléchargement d'applications sur des iPhone compatibles en 2008, documenté par le [communiqué Apple du 14 juillet 2008](https://www.apple.com/newsroom/2008/07/14iPhone-App-Store-Downloads-Top-10-Million-in-First-Weekend/). Cette comparaison porte sur l'organisation et l'abstraction de la programmation : elle ne prétend pas que le Mark I était monotâche. Le coût relatif du logiciel, non documenté et sans périmètre comptable, est retiré. Aucun nombre d'applications n'est exigé ni utilisé comme métrique pédagogique.

La remédiation C01 confondait le modèle de Turing et l'architecture EDVAC et expliquait leur réalisation par une seule difficulté électronique. Elle distingue désormais les objectifs du [texte de Turing de 1936, paragraphe 6](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf), du [rapport EDVAC du 30 juin 1945, paragraphes 2.3–2.5](https://real.mtak.hu/170042/1/Firstdraft.pdf) et de la [réalisation du Manchester Baby en 1948](https://curation.cs.manchester.ac.uk/computer50/www.computer50.org/mark1/new.baby.html). La chronologie ne prouve pas une causalité exclusive.

La remédiation C02 n'affirme plus que chaque calcul de 1945 exigeait un recâblage. Sa classification matériel/logiciel est conservée, mais le corrigé explique pourquoi les deux matériels et trois logiciels choisis ne mesurent aucune évolution historique. L'exemple du capteur absent borne la polyvalence : un programme ne peut pas mesurer avec un capteur que la machine ne possède pas. Une estimation ou une donnée provenant d'un autre appareil serait une autre situation.

## Adéquation entre questions, réponses et capacités

Les deux capacités officielles et le contrat sont conservés. L'évaluation B demande ce que les compilateurs et systèmes ont changé, puis un exemple, les éléments invariants et une limite matérielle. Son corrigé répond à chacun de ces éléments et accepte d'autres exemples correctement justifiés. Il n'exige plus une opposition historiquement fausse. Le total est toujours 20 points ; la répartition indicative du second exercice donne 5 points par question.

QCM Q3 reste en C2 et demande désormais le rôle des compilateurs et systèmes. La réponse C est la prise en charge logicielle de la traduction et de la gestion des ressources. A impose à tort une tâche unique ; B fait disparaître le support matériel ; D supprime à tort la compatibilité. Chaque diagnostic réfute cette proposition précise. Les quatre options sont mutuellement distinguables.

QCM Q4 reste en C2 mais interroge explicitement l'ajout d'un service logiciel sur une infrastructure existante. D est correcte : le Web utilise Internet. A confond logiciel et disparition du matériel ; B invente un réseau physique indépendant ; C rend le Web de 1989 nécessaire à ARPANET de 1969. Les [documents CERN](https://home.cern/science/computing/the-birth-of-the-web/short-history-web/) et [DARPA](https://www.darpa.mil/news/features/arpanet) justifient ces distinctions. Les renvois B et C conduisent aussi à C1, car leurs confusions portent sur Internet/Web et sur la chronologie ; deux justifications explicites sont ajoutées au registre canonique des renvois croisés. Aucun seuil du contrôle n'est changé.

Le JSON auteur a été rendu par le générateur canonique partagé, sélectionné uniquement pour TNSI-HISTOIRE-INFORMATIQUE. Le TeX n'a pas été édité à la main. Les clés C et D résultent de la relecture des options ; leur conservation n'est pas une contrainte imposée à la preuve.

## Vérification exécutable et invalidation

Les remédiations C01 et C02 ne portent plus d'oracles de dates ou de classifications codées comme constantes. Le vérificateur les classe `manual_review`, sans crédit d'exécution ni approbation humaine. Les receipts du HEAD de reprise restent accessibles dans Git ; le binder refuse de les appliquer aux nouveaux digests avec `SOURCE_DIGEST_CHANGED`.

Les deux blocs VERIFY de l'évaluation B contrôlent uniquement l'arithmétique du barème : trois assertions réellement exécutées dans chaque objet, par `verify_python.check_object`, dans le confinement canonique sans réseau. `certifies_documentary_claims` demeure faux. Les répartitions sont exactes, y compris les demi-points avec `Fraction`. La première exécution de développement a détecté deux commentaires Python mal préfixés ; ces erreurs de syntaxe ont été corrigées, puis les deux blocs ont réussi. Aucun receipt du chapitre n'a été réécrit pour masquer cette séquence.

Les tests ajoutés changent un élément du barème en conservant le total attendu : les deux mutations échouent. Ils vérifient aussi que les remédiations sans calcul n'obtiennent aucun crédit machine et que leurs receipts historiques ne se relient pas au nouveau contenu. Le test des renvois croisés a d'abord échoué, puis réussi après ajout des deux justifications réelles. Les cinq tests existants du lot A continuent de contrôler les digests et le rendu ; aucun test lexical ne prétend prouver une date.

Commandes ciblées observées :

```text
python -m pytest tests/test_qcm_diagnostic_renvoi_audit.py tests/test_tnsi_history_documentary_bindings.py -q
python Mathematiques/manuel-maths/scripts/build_qcm_tex.py --chap TNSI-HISTOIRE-INFORMATIQUE --check
python -m ruff check tests/test_tnsi_history_documentary_bindings.py scripts/build_qcm_diagnostic_renvoi_audit.py --select F,E9
git diff --check
```

La première commande a produit 24 PASS. Les vérifications de code et de sources sont séparées de la revue documentaire. Aucun skip ni xfail n'a été ajouté.

## Limites et suite

Cette note remplace le périmètre Q3/Q4 des diagnostics précédents et documente les changements ; les digests du lot A pour l'ancien QCM restent historiques. Elle ne constitue pas une clôture scientifique, pédagogique, éditoriale ou visuelle globale du chapitre. La banque écrite comporte encore les défauts du lot C, et aucun build final ni contrôle de pages n'est effectué. La contre-revue indépendante des nouveaux digests et la décision humaine restent distinctes.

## Digests des sources relues

- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/cours/11_C2_evolution_logiciel_materiel.tex` : `32c92989e7a65e1f5c23b89de47683003c02b0616ef9c1b354a7117cf6990312`
- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/evaluations/TNSI-HIST-EVAL-B.tex` : `c2a0e6e2401eecab61c0af8af3860fb41f94c3e10478326607ca085287127f58`
- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/evaluations/TNSI-HIST-EVAL-B-corrige.tex` : `cefcb873af2010520cec02cf4ce434099cde1664b3555cabf0511cbdc77e2b8d`
- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/remediation/TNSI-HISTOIRE-INFORMATIQUE-RE-C01.tex` : `053e187e6351ffdbcc786e8ebe2065713bb32758922c7ccafc0965fcb8df97f1`
- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/remediation/TNSI-HISTOIRE-INFORMATIQUE-RE-C02.tex` : `3988f6da472c5fafa1a379611eec537d24387b9162a5880949db4313f2cde9bb`
- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/qcm/TNSI-HISTOIRE-INFORMATIQUE-QCM.json` : `ca0c0d3b096e3af72c8328818fbefba4edb20315730c40f00f7b4544bed70868`
- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/qcm/TNSI-HISTOIRE-INFORMATIQUE-QCM.tex` : `cafff95c67f5414b96f71269f271a07fa0de0b1236d497937357422c0789a082`

## Contre-revue indépendante des sources corrigées

Codex `/root`, distinct de l'auteur des corrections, a lu intégralement les sept sources ci-dessus, les quatre questions du QCM avec leurs seize options et douze diagnostics, le contrat et la rubrique Histoire du programme de Terminale NSI (lignes 127–151 du texte local). La distinction entre C1 (repères) et C2 (rôles du logiciel et du matériel) est conservée. Les réponses libres du corrigé B répondent aux demandes du sujet et bornent la polyvalence par la compatibilité et les ressources disponibles. Le classement de cinq objets n'est plus présenté comme mesure d'une évolution historique.

Les documents cités ont été ouverts indépendamment lors de cette contre-revue : Harvard confirme la livraison de 1944, la commande par bande et plusieurs usages du Mark I ; IBM documente l'annonce de 1952 et la polyvalence du 701, puis la diffusion commerciale de Fortran en 1957. Le témoignage de Robert Patrick situe la mise en production du système GM-NAA sur IBM 704 en 1956. Les sections 3.5 et 5 du texte de Ritchie et Thompson décrivent la protection et les processus ; l'introduction précise ses versions successives et la réédition révisée de 1978. Le communiqué Apple décrit le téléchargement et l'utilisation d'applications en 2008 et précise les conditions de mise à jour. Ces documents soutiennent les affirmations limitées du cours, sans reprendre leurs généralités promotionnelles.

Pour EDVAC, les paragraphes 2.3–2.5 distinguent instructions, contrôle et mémoire ; le paragraphe 14.1 du même rapport énonce explicitement la provenance commune en mémoire des instructions et des données numériques. Ce passage confirme la formulation de RE-C01. La lecture antérieure du paragraphe 6 de Turing, du document Manchester sur le Baby, des pages CERN et DARPA, et du témoignage du créateur de Python reste applicable aux affirmations inchangées : les deux questions QCM C1 ont aussi été relues dans leur contexte actuel. Aucune chronologie n'est déduite d'un programme Python.

Les clés Q3=C et Q4=D résultent de la lecture des propositions : les compilateurs et systèmes prennent en charge traduction et ressources ; le Web ajoute un service utilisant Internet. Les autres réponses font disparaître le matériel, imposent une tâche unique, suppriment la compatibilité, inventent un réseau physique séparé ou inversent la chronologie. Les diagnostics traitent ces erreurs précises. Les deux renvois vers C1 ont une justification pédagogique explicite et reviennent à l'objectif C2.

Vérifications exécutées par `/root` : les deux modules ciblés produisent **24 PASS en 0,91 s** ; le générateur canonique confirme les **quatre questions synchrones**. Les mutations arithmétiques deviennent rouges sans prétendre contrôler les dates. Les tests d'anciens receipts utilisent le commit de reprise ; les trois workflows concernés imposent effectivement `fetch-depth: 0`. Les sept empreintes de source ont été comparées aux fichiers présents avant commit.

Verdict de cette contre-revue bornée : `VALIDATED_BY_EVIDENCE` pour les affirmations scientifiques et documentaires lues et l'alignement des réponses de ce lot. Aucune approbation humaine n'est créée. Les défauts de la banque écrite, la vérification globale du chapitre et les contrôles des PDF demeurent ouverts ; cette note ne les clôt pas.
