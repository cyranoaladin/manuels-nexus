---
title: "T13 - td - chiffrement et HTTPS"
level: "terminale"
sequence_id: "T13"
document_type: "td"
status: "needs_review"
version: "0.7.0"
source: "BO 2019"
source_creation: "generated_from_program"
theme: "chiffrement et HTTPS"
notion: "chiffrement et HTTPS"
private_data: false
official_program:
  capacities:
    - "T-ARCH-04A"
    - "T-ARCH-04B"
---

# T13 - TD - chiffrement et HTTPS

## Objectifs

- Distinguer les objectifs de sécurité assurés par HTTPS : confidentialité, intégrité et authentification du serveur.
- Décrire les principes du chiffrement symétrique et du chiffrement asymétrique et justifier leur usage combiné dans HTTPS.
- Expliquer le rôle du certificat, de l'autorité de certification et de la chaîne de confiance dans l'établissement d'une connexion TLS.

## Consigne commune

Travaillez sur papier. Chaque réponse doit nommer les objets cryptographiques manipulés (clé publique, clé privée, clé de session, certificat) et préciser leur rôle. Une réponse sans justification ou sans référence aux données fournies ne suffit pas. Les corrections détaillées sont réservées aux repères enseignant.

## Progression socle / standard / approfondissement

- Socle : exercices 1 et 2, pour identifier les objectifs de sécurité et comparer HTTP et HTTPS.
- Standard : exercices 3 à 6, pour décrire le chiffrement, les certificats, les anomalies et le déroulé TLS.
- Approfondissement : exercices 7 et 8, pour distinguer les outils cryptographiques et corriger des raisonnements faux.

## Exercices

### Exercice 1

- **Identifier les objectifs de sécurité.**
- Type : lecture/analyse.
- Capacité officielle : T-ARCH-04A.
- Données : un navigateur affiche un cadenas fermé en se connectant à `https://banque.example`. Un attaquant intercepte les paquets réseau entre le client et le serveur.
- Consigne : nommez les trois objectifs de sécurité visés par HTTPS (confidentialité, intégrité, authentification du serveur). Pour chacun, expliquez en une phrase ce qui est protégé et ce que l'attaquant ne peut pas faire.
- Indice socle : confidentialité signifie que l'attaquant ne peut pas lire le contenu ; intégrité signifie qu'il ne peut pas le modifier sans détection.
- Critère de réussite : les trois objectifs sont nommés et reliés à un risque concret ; « tout est secret » n'est pas accepté comme réponse unique.

#### Repères enseignant — continuité de preuve

- Consigne : nommer confidentialité, intégrité, authentification ; traiter aussi `HTTP sans TLS` si nécessaire.

### Exercice 2

- **Comparer HTTP et HTTPS.**
- Type : lecture/analyse.
- Capacité officielle : T-ARCH-04B.
- Données : deux captures réseau simplifiées.
  - Capture A (HTTP, port 80) : `GET /compte?id=4217`, cookie de session visible, réponse en clair.
  - Capture B (HTTPS, port 443) : `ClientHello`, `ServerHello`, puis données chiffrées illisibles.
- Consigne : pour chaque capture, indiquez ce qu'un attaquant situé sur le réseau peut lire. Expliquez pourquoi le cookie est exposé dans la capture A mais pas dans la capture B. Précisez quel protocole intervient entre TCP et HTTP dans la capture B.
- Critère de réussite : la réponse distingue ce qui est visible et ce qui est protégé dans chaque capture ; le rôle de TLS est nommé.

#### Repères enseignant — continuité de preuve

- Consigne : comparer visibilité HTTP et protection HTTPS ; traiter aussi `HTTP sans TLS` si nécessaire.

### Exercice 3

- **Chiffrement symétrique et asymétrique.**
- Type : production/écriture.
- Capacité officielle : T-ARCH-04A.
- Données : le serveur `banque.example` possède une paire de clés `Kpub_serveur` (publique) et `Kpriv_serveur` (privée). Le client génère une clé de session `Ksession` pour chiffrer les échanges.
- Consigne : expliquez pourquoi le client chiffre `Ksession` avec `Kpub_serveur` avant de l'envoyer. Ensuite, expliquez pourquoi les données applicatives (requêtes, réponses) sont chiffrées avec `Ksession` (symétrique) et non directement avec `Kpub_serveur` (asymétrique). Donnez au moins une raison liée aux performances.
- Critère de réussite : le rôle de chaque clé est nommé ; la raison pour laquelle HTTPS combine les deux types de chiffrement est explicitée.

#### Repères enseignant — continuité de preuve

- Consigne : protéger Ksession par asymétrique puis utiliser symétrique pour données ; traiter aussi `clé publique non vérifiée` si nécessaire.

### Exercice 4

- **Certificat et autorité de certification.**
- Type : production/écriture.
- Capacité officielle : T-ARCH-04B.
- Données : le certificat présenté par `banque.example` contient les champs suivants.

| Champ | Valeur |
|---|---|
| Domaine | banque.example |
| Clé publique | Kpub_serveur |
| Émetteur | Autorité-Test |
| Validité | 2025-01-01 au 2026-12-31 |
| Signature | signée par la clé privée d'Autorité-Test |

- Consigne : expliquez comment le navigateur vérifie ce certificat. Précisez le rôle de chaque champ dans la décision d'accepter ou de refuser la connexion. Décrivez ce que signifie « chaîne de confiance » en une phrase.
- Critère de réussite : la vérification porte sur le domaine, la date de validité, la signature de l'émetteur et la confiance dans l'autorité ; le certificat n'est pas confondu avec le chiffrement des données.

#### Repères enseignant — continuité de preuve

- Consigne : vérifier certificat avec domaine, validité, signature et chaîne de confiance ; traiter aussi `certificat expiré` si nécessaire.

### Exercice 5

- **Mini-scénarios de certificat invalide.**
- Type : cas limite.
- Capacité officielle : T-ARCH-04A.
- Données : quatre situations rencontrées par un navigateur.

| Scénario | Certificat présenté |
|---|---|
| A | Domaine : `boutique.example`, mais l'utilisateur visite `banque.example` |
| B | Validité : 2023-01-01 au 2024-12-31, date actuelle : 2026-03-15 |
| C | Certificat auto-signé : l'émetteur est le serveur lui-même |
| D | Émetteur : « Autorité-Inconnue », absente de la liste de confiance du navigateur |

- Consigne : pour chaque scénario, indiquez si le navigateur doit accepter ou refuser la connexion. Justifiez en nommant le champ défaillant et le risque associé.
- Critère de réussite : les quatre scénarios sont refusés avec une justification distincte pour chacun ; « certificat invalide » sans précision ne suffit pas.

#### Repères enseignant — continuité de preuve

- Consigne : décider chaque scénario de certificat invalide ; traiter aussi `certificat expiré` si nécessaire.

### Exercice 6

- **Déroulé simplifié d'une connexion TLS.**
- Type : justification.
- Capacité officielle : T-ARCH-04B.
- Données : les étapes suivantes, dans le désordre.
  1. Le serveur envoie son certificat contenant `Kpub_serveur`.
  2. Le client envoie un message `ClientHello` avec les algorithmes qu'il accepte.
  3. Les échanges suivants sont chiffrés avec `Ksession`.
  4. Le client vérifie le certificat (domaine, validité, signature de l'autorité).
  5. Le serveur répond par `ServerHello` avec l'algorithme retenu.
  6. Le client génère `Ksession`, la chiffre avec `Kpub_serveur` et l'envoie.
- Consigne : remettez ces étapes dans l'ordre chronologique. Pour chaque étape, indiquez si elle relève de l'authentification, de l'échange de clé ou du chiffrement des données. Expliquez pourquoi l'étape 4 doit précéder l'étape 6.
- Critère de réussite : l'ordre est correct ; le lien entre vérification du certificat et confiance dans la clé publique est explicité.

#### Repères enseignant — continuité de preuve

- Consigne : ordonner le déroulé TLS simplifié ; traiter aussi `clé publique non vérifiée` si nécessaire.

### Exercice 7

- **Distinguer chiffrement, hachage et signature.**
- Type : lecture/analyse.
- Capacité officielle : T-ARCH-04A.
- Données : trois situations.

| Situation | Description |
|---|---|
| S1 | Un serveur envoie un fichier et son empreinte SHA-256 pour que le client vérifie l'intégrité. |
| S2 | Le client chiffre `Ksession` avec `Kpub_serveur` pour que seul le serveur puisse la lire. |
| S3 | L'autorité de certification signe le certificat avec sa clé privée pour garantir son authenticité. |

- Consigne : pour chaque situation, identifiez l'outil cryptographique utilisé (chiffrement symétrique, chiffrement asymétrique, hachage ou signature numérique). Précisez la propriété de sécurité assurée (confidentialité, intégrité ou authentification) et la clé ou le mécanisme impliqué.
- Critère de réussite : chaque outil est correctement associé à sa situation et à sa propriété ; hachage et chiffrement ne sont pas confondus.

#### Repères enseignant — continuité de preuve

- Consigne : associer chaque situation à l'outil et la propriété ; traiter aussi `certificat expiré` si nécessaire.

### Exercice 8

- **Débogage de raisonnements faux.**
- Type : justification.
- Capacité officielle : T-ARCH-04B.
- Données : quatre affirmations d'élèves.

| Affirmation | Phrase |
|---|---|
| F1 | « HTTPS prouve que le site est honnête. » |
| F2 | « Le certificat chiffre les données envoyées au serveur. » |
| F3 | « La clé publique doit rester secrète, sinon n'importe qui peut déchiffrer. » |
| F4 | « Le cadenas dans le navigateur garantit l'absence d'arnaque. » |

- Consigne : pour chaque affirmation, expliquez pourquoi elle est fausse ou trompeuse. Proposez une reformulation correcte en utilisant le vocabulaire précis du cours (clé publique, clé privée, certificat, autorité de certification, chiffrement).
- Critère de réussite : chaque correction identifie la confusion précise et utilise le bon terme technique ; une simple négation (« c'est faux ») ne suffit pas.

#### Repères enseignant — continuité de preuve

- Consigne : corriger chaque raisonnement faux avec le vocabulaire précis ; traiter aussi `clé publique non vérifiée` si nécessaire.

## Erreurs fréquentes

- Croire que la clé publique doit rester secrète, en confondant clé publique et clé privée.
- Utiliser le chiffrement asymétrique pour toutes les données, sans comprendre le rôle de la clé de session.
- Ignorer le certificat et supposer que la clé publique reçue est automatiquement fiable.
- Confondre le certificat avec le chiffrement des données.
- Confondre hachage et chiffrement.

## Différenciation et aides graduées

- Aide socle : relire la définition de chaque objectif de sécurité avant de répondre ; comparer les deux captures ligne par ligne.
- Aide standard : dessiner un schéma client-serveur avec les clés échangées à chaque étape.
- Approfondissement : pour l'exercice 7, trouver un contre-exemple où le mauvais outil est appliqué ; pour l'exercice 8, rédiger une explication destinée à un camarade.

## Cas limites travaillés

- certificat expiré ;
- clé publique non vérifiée ;
- HTTP sans TLS ;
- certificat auto-signé ;
- domaine ne correspondant pas au certificat ;
- autorité de certification inconnue.

## Corrigé — repères enseignant

### Corrigé exercice 1

- Donnée utilisée : connexion à `https://banque.example` avec attaquant sur le réseau.
- Méthode : nommer chaque objectif de sécurité et le relier à une menace concrète.
- Résultat : confidentialité (l'attaquant ne lit pas le contenu), intégrité (l'attaquant ne modifie pas les données sans détection), authentification du serveur (le client vérifie qu'il communique bien avec `banque.example`).
- Contrôle : « tout est secret » ne couvre ni l'intégrité ni l'authentification ; les trois objectifs sont distincts.

### Corrigé exercice 2

- Donnée utilisée : capture A en HTTP sur le port 80 et capture B en HTTPS sur le port 443.
- Méthode : comparer ce qui est visible dans chaque capture pour l'attaquant.
- Résultat : en HTTP, l'URL complète, le cookie et la réponse sont lisibles ; en HTTPS, le contenu applicatif est un message chiffré avec Ksession, illisible pour l'attaquant. TLS s'intercale entre TCP et HTTP.
- Contrôle : le cookie est exposé en HTTP car aucune couche de chiffrement n'intervient ; en HTTPS, TLS chiffre avant la transmission.

### Corrigé exercice 3

- Donnée utilisée : `Kpub_serveur`, `Kpriv_serveur` et `Ksession`.
- Méthode : distinguer le rôle de l'asymétrique (échange sécurisé de clé) et du symétrique (chiffrement rapide des données).
- Résultat : le client chiffre `Ksession` avec `Kpub_serveur` pour que seul le serveur (détenteur de `Kpriv_serveur`) puisse la déchiffrer. Les données sont ensuite chiffrées avec `Ksession` car le chiffrement symétrique est bien plus rapide que l'asymétrique pour de grands volumes.
- Contrôle : utiliser uniquement l'asymétrique serait trop lent pour un échange HTTP complet ; la combinaison des deux est justifiée par les performances et la sécurité.

### Corrigé exercice 4

- Donnée utilisée : certificat de `banque.example` émis par Autorité-Test, valide jusqu'au 2026-12-31.
- Méthode : vérifier domaine, validité, signature de l'émetteur et présence de l'autorité dans la liste de confiance.
- Résultat : le navigateur vérifie que le domaine du certificat correspond à l'URL visitée, que la date courante est dans la période de validité, que la signature d'Autorité-Test est valide avec la clé publique d'Autorité-Test, et qu'Autorité-Test figure dans sa liste de confiance.
- Contrôle : le certificat prouve l'identité du serveur ; il ne chiffre pas les données lui-même. La chaîne de confiance signifie que la confiance dans le certificat repose sur la confiance dans l'autorité qui l'a signé.

### Corrigé exercice 5

- Donnée utilisée : quatre scénarios de certificat invalide.
- Méthode : identifier le champ défaillant dans chaque scénario et le risque associé.
- Résultat : A — refusé, le domaine ne correspond pas (risque : le serveur n'est pas celui attendu) ; B — refusé, le certificat est expiré (risque : la clé peut être compromise depuis) ; C — refusé, auto-signé sans tiers de confiance (risque : n'importe qui peut générer ce certificat) ; D — refusé, autorité inconnue (risque : l'identité du serveur n'est pas garantie par un tiers reconnu).
- Contrôle : chaque refus est relié à un champ précis et à un risque distinct ; la réponse ne se limite pas à « invalide ».

### Corrigé exercice 6

- Donnée utilisée : six étapes TLS dans le désordre.
- Méthode : rétablir l'ordre chronologique et classer chaque étape.
- Résultat : ordre correct : 2 (ClientHello — négociation), 5 (ServerHello — négociation), 1 (certificat — authentification), 4 (vérification — authentification), 6 (échange de Ksession — échange de clé), 3 (échanges chiffrés — chiffrement des données).
- Contrôle : l'étape 4 doit précéder l'étape 6 car le client doit vérifier que `Kpub_serveur` appartient bien au bon serveur avant de lui confier `Ksession` ; sinon un attaquant pourrait présenter sa propre clé publique.

### Corrigé exercice 7

- Donnée utilisée : trois cas S1, S2, S3.
- Méthode : associer chaque cas à l'outil cryptographique et à la propriété de sécurité.
- Résultat : S1 — hachage via SHA-256, intégrité (empreinte fixe, non réversible) ; S2 — chiffrement asymétrique via `Kpub_serveur`, confidentialité (seul le serveur avec `Kpriv_serveur` peut déchiffrer) ; S3 — signature numérique via la clé privée de l'autorité, authentification (la clé publique vérifie).
- Contrôle : le hachage ne chiffre pas (pas de clé, pas de déchiffrement) ; la signature utilise la clé privée du signataire, pas celle du destinataire.

### Corrigé exercice 8

- Donnée utilisée : quatre affirmations fausses d'élèves.
- Méthode : identifier la confusion et reformuler avec le vocabulaire précis.
- Résultat : F1 — HTTPS prouve que la connexion est chiffrée et que le serveur possède un certificat valide, pas qu'il est honnête (un site frauduleux peut avoir un certificat) ; F2 — le certificat prouve l'identité du serveur et transporte sa clé publique, il ne chiffre pas les données (c'est `Ksession` qui chiffre les données) ; F3 — la clé publique est faite pour être diffusée, c'est la clé privée qui doit rester secrète (seul le détenteur de la clé privée peut déchiffrer ce qui est chiffré avec la clé publique) ; F4 — le cadenas indique une connexion chiffrée avec un certificat vérifié, pas que le site est exempt d'arnaque (il faut vérifier le domaine et l'identité du site indépendamment).
- Contrôle : chaque correction utilise le terme technique précis et ne se limite pas à une négation.

## Critères de réussite observables

- Chaque objectif de sécurité est nommé et relié à une menace concrète.
- Le rôle de chaque clé (publique, privée, de session) est identifié dans l'échange HTTPS.
- Au moins un cas limite de la section précédente est décidé avec justification.
