# LOT 0 — Contrat 1NSI-WEB-IHM
Cinquieme chapitre du manuel Premiere NSI (5/10, mapping docs/09 :
1NSI-WEB-IHM <- P08). 9/9 capacites conformes (composants graphiques,
evenements, methodes de clic, execution client/serveur et ordre des
echanges, donnees memorisees cote client/cookies, transmission
chiffree HTTPS, formulaire Web, requetes GET/POST, choix du type de
requete selon la confidentialite). Referentiel source verifie
conforme au texte officiel du B.O.

Particularite de ce chapitre : contenu majoritairement conceptuel
(HTML/JS/HTTP), hors du perimetre executable en Python. Parti pris
documente : le code HTML/JS est presente a titre illustratif (non
execute) ; les mecanismes calculables (construction de requetes GET/
POST via urllib.parse, ordre des etapes client-serveur, gestion de
cookies) sont modelises et verifies par execution Python reelle. Un
exercice (EX-001/CO-001) est purement conceptuel et reste a bon droit
en statut manual_review (aucun code a executer).

Ecart assume vs docs/08_specificites_nsi.md (harvest T0 indisponible,
volume reduit) : meme calibrage que les chapitres precedents. Statut :
draft (auto-verifie, en attente de revue humaine).
