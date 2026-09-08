# TNSI — correction des repères chronologiques

Relecture documentaire du 8 septembre 2026 par Codex `review_forensics`, indépendante des auteurs des textes repris. Base avant correction : `2a9a845c23e0de7c6732bf407875a2a2649631b1`. Observation de travail liée aux empreintes des sources ci-dessous ; aucune approbation humaine, aucun receipt de release.

## Défauts observés et justification

Le cours `TNSI-HIST-CR-010` attribuait à Moore en 1965 un doublement tous les deux ans, dans une phrase l’assimilant à la croissance des performances. Son article de 1965 porte sur la complexité des circuits au coût par composant le plus favorable et indique « roughly a factor of two per year ». Son article de 1975 prévoit un rythme proche de deux ans avant la fin de la décennie. Les deux propositions et leur indicateur sont désormais distingués. Sources primaires lues : [Moore, Electronics 38(8), 19 avril 1965, deuxième page](https://download.intel.com/newsroom/2023/manufacturing/moores-law-electronics.pdf), [Moore, IEDM 1975, page imprimée 13](https://www.lithoguru.com/scientist/CHE323/Moore1975.pdf).

Le cours et le diagnostic QCM Q2/C assimilaient le réseau ARPANET de 1969 à Internet portant le Web vingt ans plus tard. Le texte distingue désormais ARPANET comme un précurseur et, dans le cours, la transition TCP/IP de 1983. L’institution à l’origine d’ARPANET documente les deux étapes : [DARPA, Evolution of ARPANET](https://www.darpa.mil/news/features/arpanet).

Le diagnostic Q1/D datait la naissance de Python de 1991. Il date désormais sa première diffusion publique de 1991 et sa création de 1989. La présentation de Guido van Rossum distingue Noël 1989 et février 1991 : [Python’s early days](https://legacy.python.org/doc/essays/ppt/jpf001/tsld006.htm). La proposition du Web en 1989, sa mise en œuvre en 1990 puis sa diffusion en 1991 sont distinguées dans le cours ; il ne s’agit pas de sa libération juridique en 1993. Source institutionnelle : [CERN, A short history of the Web](https://home.cern/science/computing/the-birth-of-the-web/short-history-web/).

Le diagnostic Q2/A prétendait que 1948 précédait toute interconnexion d’ordinateurs, sans preuve adaptée. Il cite maintenant un fait positif : la première exécution du Manchester Baby, ordinateur électronique à programme enregistré, en 1948. Le diagnostic Q1/B est précisé de la même façon. Source de l’université où cette machine a été construite : [The Manchester Small Scale Experimental Machine](https://curation.cs.manchester.ac.uk/computer50/www.computer50.org/mark1/new.baby.html).

Le diagnostic Q2/D ne prête plus à l’élève une datation implicite de la diffusion grand public : il donne le repère 1969 et l’écart arithmétique de 31 ans avec 2000.

Le repère 1936 est conservé : le [texte de Turing, paragraphe 6](https://www.cs.virginia.edu/~robins/Turing_Paper_1936.pdf) distingue le modèle général des machines de Turing et une machine particulière universelle qui simule les autres. Le cours reprend cette distinction et les accents ont été corrigés dans les passages intégralement relus. La synthèse des quatre concepts, issue du [programme officiel](https://www.education.gouv.fr/bo/19/Special8/MENE1921247A.htm), est explicitement attribuée à ce programme. Aucun atome officiel n’est modifié. Les décennies de la frise désignent l’essor ou la diversification des appareils, sans inventer une date exclusive d’apparition.

## Portée scientifique et limites

Les réponses Q1=A et Q2=B ont été retrouvées indépendamment à partir des documents. Les diagnostics B/C/D de Q1 et A/C/D de Q2 ont été relus après modification : ils distinguent le modèle de calcul, le Baby, ARPANET et les diffusions publiques. Aucun diagnostic ne prouve une date par le résultat d’un programme. Q3 et Q4 sont hors clôture de ce lot ; les simplifications sur les rôles du matériel et du logiciel sont traitées séparément. Le cours C2, les remédiations, évaluations et banque écrite restent hors de cette correction chronologique.

Les passages inchangés du cours C1 sur l’architecture de 1945 s’appuient sur le [rapport EDVAC du 30 juin 1945, paragraphes 2.3–2.5](https://real.mtak.hu/170042/1/Firstdraft.pdf). L’attribution concerne sa description, sans revendiquer une invention individuelle exclusive. Les quatre notions et les repères de première restent dans le périmètre du programme lu localement dans `NSI/sources/txt/BO2019_NSI_terminale.txt`.

## Vérification du rendu et de la liaison des preuves

Le JSON du QCM reste la source auteur ; son TeX a été régénéré par le producteur partagé canonique, sans le modifier :

```text
python Mathematiques/manuel-maths/scripts/build_qcm_tex.py --chap TNSI-HISTOIRE-INFORMATIQUE --check
python Mathematiques/manuel-maths/scripts/build_qcm_tex.py --chap TNSI-HISTOIRE-INFORMATIQUE
python Mathematiques/manuel-maths/scripts/build_qcm_tex.py --chap TNSI-HISTOIRE-INFORMATIQUE --check
```

Le premier contrôle, après correction du JSON et avant régénération, a échoué pour divergence du TeX. Le dernier a réussi pour les quatre questions. Les lettres correctes et les rattachements aux capacités des quatre questions n’ont pas changé.

`tests/test_tnsi_history_documentary_bindings.py` vérifie trois mutations de diagnostics qui conservent les options et la clé mais changent le digest, l’identité exacte avec le rendu canonique et le refus d’un rendu périmé après mutation d’un diagnostic dans une fixture temporaire. Ces cinq contrôles ont réussi. Ils contrôlent la liaison et la propagation du contenu ; ils ne constituent pas une preuve historique et n’attribuent aucun PASS documentaire.

Aucun programme du chapitre n’a été exécuté dans ce lot. Aucun ancien receipt n’a été réécrit. Les anciens digests ne peuvent pas être reliés aux textes corrigés par simple conservation des identifiants. La contre-revue finale et les dimensions pédagogiques, éditoriales et visuelles restent à établir pour les nouveaux contenus.

## Empreintes de la correction observée

- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/cours/10_C1_evenements_cles.tex` : `3c9fd106d11e8a42d9ffe826756774ecc4e76a115f54e35e595ca31a36eba54d`
- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/qcm/TNSI-HISTOIRE-INFORMATIQUE-QCM.json` : `2864ad4a96ee0c5d174b33312fff3899567af27ef9646e71b46acb0472b640e7`
- `NSI/chapitres/TNSI-HISTOIRE-INFORMATIQUE/qcm/TNSI-HISTOIRE-INFORMATIQUE-QCM.tex` : `77e87a1b0834cd8a015fea87800d82ed4129f4121e992a82f00db290c677c6f6`

## Contre-revue indépendante du lot corrigé

Root a lu le cours C1 intégral, les quatre questions, leurs options et diagnostics, le TeX dérivé complet et les cinq tests. Les pages primaires Moore1965 (copie Intel, p.2) et Moore1975 (p.13), Turing§6 ainsi que les pages DARPA, CERN, Manchester et la présentation de Guido van Rossum ont été consultées directement. Les deux dates de Moore concernent bien des rythmes distincts et la complexité des circuits, pas une égalité universelle de vitesse. Turing décrit une machine particulière universelle ; cette propriété n’est pas attribuée à toute machine du modèle. Les diagnostics Q1/Q2 sont conformes aux repères documentés, avec les écarts12,20et31ans vérifiés. Le dernier diagnostic Q2/D décrit désormais le repère et son écart, sans supposer le raisonnement du répondant. Les accents du cours ont été relus.

Les cinq tests de liaison/rendu ont passé dans la contre-vérification root, et le contrôle canonique QCM indique quatre questions synchrones. Ils ne prouvent aucune affirmation historique. La revue documentaire des changements C1/Q1/Q2 est validée par ces documents ; le QCM entier demeure en attente, notamment les généralisations et l’affirmation économique de Q3 traitées au lot suivant. Aucun crédit humain, aucun audit visuel final et aucune clôture de chapitre ne sont accordés.
