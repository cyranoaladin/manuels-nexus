---
title: "Revue de substance - S01 Représentation des données"
level: "premiere"
sequence_id: "s01_representation_donnees"
document_type: "revue_substance"
status: "needs_review"
version: "0.3.0"
source: "Relecture interne S01 du 26 juin 2026"
notion: "revue de substance avec preuves citées"
learning_objectives:
  - "Vérifier les preuves cours, entraînement et correction pour chaque capacité visée."
private_data: false
---

# Revue de substance — S01 Représentation des données

Date de revue : 26 juin 2026.

---

CAPACITÉ : P-DATA-BASE-01 — Passer de la représentation d'une base dans une autre.

PREUVE COURS : « Dans toute écriture positionnelle, le poids d'un chiffre dépend de sa position. Ainsi, l'écriture 1011₂ se décompose en 1×2³ + 0×2² + 1×2¹ + 1×2⁰, soit 8 + 0 + 2 + 1 = 11₁₀. [...] Pour convertir un entier positif de la base 10 vers la base 2, on effectue des divisions successives par 2 en notant chaque reste, puis on lit les restes du dernier au premier. » (cours_eleve.md#bases-2-10-et-16)
   -> enseigne réellement la capacité ? oui

PREUVE ENTRAÎNEMENT : « Convertir 18₁₀, 31₁₀, 42₁₀ en base 2. Convertir 1010₂, 1111₂, 100000₂ en base 10. Convertir 2A₁₆ et FF₁₆ en base 10. Justifier chaque conversion avec les puissances utilisées. » (td.md#exercice-1---socle---bases)
   -> l'élève s'entraîne réellement sur cette capacité ? oui

PREUVE CORRECTION : « 18₁₀ = 10010₂ (16 + 2). 31₁₀ = 11111₂ (16 + 8 + 4 + 2 + 1). [...] Justification : développer avec les puissances ou relire les restes des divisions. » (corrige.md#exercice-1--conversions-de-bases)
   -> l'élève peut s'auto-corriger ? oui

VERDICT : needs_review
JUSTIFICATION : Le cours enseigne la méthode des divisions successives et le développement positionnel avec un exemple corrigé détaillé (45₁₀). Le TD fait pratiquer sur 8 valeurs dans les trois bases. Le corrigé fournit chaque résultat avec la justification par les puissances.

---

CAPACITÉ : P-DATA-BASE-02B — Évaluer un codage binaire d'entier relatif et utiliser le complément à deux.

PREUVE COURS : « Pour encoder un entier négatif −x sur n bits, on calcule 2ⁿ − x. Par exemple, pour coder −5 sur 8 bits : 256 − 5 = 251, et 251₁₀ = 11111011₂. Pour décoder une valeur binaire dont le bit de poids fort vaut 1, on interprète d'abord la suite comme un entier positif, puis on soustrait 2ⁿ. » (cours_eleve.md#entiers-relatifs-et-complément-à-deux)
   -> enseigne réellement la capacité ? oui

PREUVE ENTRAÎNEMENT : « Sur 8 bits, encoder 5, −1, −7, −128. Sur 8 bits, décoder 00000101, 11111111, 11111001, 10000000. Donner l'intervalle représentable sur 4 bits. Dire pourquoi −9 ne se code pas sur 4 bits. » (td.md#exercice-3---standard---complément-à-deux)
   -> l'élève s'entraîne réellement sur cette capacité ? oui

PREUVE CORRECTION : « −1 sur 8 bits : 11111111 (car 256 − 1 = 255). [...] Décodage : 11111111 → 255 − 256 = −1 [...] Sur 4 bits, l'intervalle est [−8 ; 7]. −9 est hors de cet intervalle, donc non représentable. » (corrige.md#exercice-3--complément-à-deux)
   -> l'élève peut s'auto-corriger ? oui

VERDICT : needs_review
JUSTIFICATION : Le cours détaille l'encodage et le décodage avec l'exemple −5 sur 8 bits et donne la formule de l'intervalle. Le TD fait pratiquer sur 4 encodages et 4 décodages. Le corrigé détaille chaque étape, y compris l'intervalle et le cas hors borne.

---

CAPACITÉ : P-DATA-BASE-04 — Dresser la table d'une expression booléenne.

PREUVE COURS : « Une table de vérité est un outil systématique qui liste toutes les combinaisons possibles des variables d'entrée et le résultat de l'expression pour chacune. Avec une variable, il y a 2 lignes ; avec deux variables, 4 lignes. [...] [Table complète de a and not b avec 4 lignes et colonnes intermédiaires.] » (cours_eleve.md#booléens-et-tables-de-vérité)
   -> enseigne réellement la capacité ? oui

PREUVE ENTRAÎNEMENT : « Dresser la table de vérité de a and b. Dresser la table de vérité de a or b. Dresser la table de vérité de a and not b. Comparer or inclusif et xor. » (td.md#exercice-4---socle---booléens)
   -> l'élève s'entraîne réellement sur cette capacité ? oui

PREUVE CORRECTION : « Table de vérité de not a or b : [table 4 lignes] Seul le cas a = True, b = False donne False. [...] L'expression (a and b) or (a and not b) se simplifie en a. En effet, (a and b) or (a and not b) = a and (b or not b) = a and True = a. » (corrige.md#exercice-intégré-3--tables-de-vérité-p-data-base-04)
   -> l'élève peut s'auto-corriger ? oui

VERDICT : needs_review
JUSTIFICATION : Le cours fournit un exemple complet avec colonnes intermédiaires. Le TD demande de dresser trois tables distinctes. Le corrigé donne les tables complètes avec une simplification algébrique.

---

CAPACITÉ : P-DATA-BASE-05A — Identifier l'intérêt des systèmes d'encodage de texte.

PREUVE COURS : « ASCII est un ancien encodage qui attribue un code numérique à 128 caractères [...] incapable de représenter les lettres accentuées du français, les caractères arabes, chinois, ou les émojis. Unicode résout ce problème en attribuant un point de code unique à un très grand nombre de caractères. [...] UTF-8 est l'encodage le plus courant d'Unicode en octets. Il utilise un nombre variable d'octets par caractère. » (cours_eleve.md#texte-ascii-et-unicode)
   -> enseigne réellement la capacité ? oui

PREUVE ENTRAÎNEMENT : « Avec Python, on obtient ord("A") = 65 et ord("é") = 233. Expliquer ce que représente ce nombre. Comparer "A".encode("utf-8") et "é".encode("utf-8"). Dire pourquoi compter les caractères ne suffit pas toujours pour connaître le nombre d'octets. » (td.md#exercice-5---standard---texte)
   -> l'élève s'entraîne réellement sur cette capacité ? oui

PREUVE CORRECTION : « 65 et 233 sont des points de code Unicode. "A" est codé sur un seul octet en UTF-8 (car son code est < 128), tandis que "é" est codé sur deux octets. Le nombre de caractères ne suffit donc pas à déduire le nombre d'octets en mémoire. » (corrige.md#exercice-5--texte-et-encodage)
   -> l'élève peut s'auto-corriger ? oui

VERDICT : needs_review
JUSTIFICATION : Le cours distingue clairement caractère, point de code et encodage, avec un exemple Python concret (A = 1 octet, é = 2 octets). Le TD fait comparer les représentations. Le corrigé explique la distinction et la raison de la différence de taille.

---

CAPACITÉ : P-DATA-CONSTR-01 — Écrire une fonction renvoyant un p-uplet de valeurs.

PREUVE COURS : « L'intérêt principal du tuple dans le cadre du programme est qu'une fonction peut renvoyer un p-uplet — c'est-à-dire plusieurs valeurs regroupées en un seul objet retourné. [...] def milieu(p1, p2): return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2) [...] Le tuple permet de renvoyer les deux coordonnées du milieu en un seul objet. » (cours_eleve.md#tuples-et-p-uplets)
   -> enseigne réellement la capacité ? oui

PREUVE ENTRAÎNEMENT : « On représente un point par (x, y). Écrire une fonction milieu(p1, p2) qui renvoie le point milieu. [...] Justifier pourquoi le point est mieux représenté par un tuple que par deux variables isolées. » (td.md#exercice-6---socle---tuples-et-listes)
   -> l'élève s'entraîne réellement sur cette capacité ? oui

PREUVE CORRECTION : « def milieu(p1, p2): return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2). Le tuple est adapté au point car il regroupe exactement deux coordonnées liées dans un ordre fixé, et on n'a pas besoin de les modifier après création. » (corrige.md#exercice-6--tuples-et-listes-p-data-constr-01-p-data-constr-02a)
   -> l'élève peut s'auto-corriger ? oui

VERDICT : needs_review
JUSTIFICATION : Le cours montre explicitement une fonction qui renvoie un tuple avec le mot-clé return. Le TD demande d'écrire cette fonction et de justifier le choix du tuple. Le corrigé donne le code, la justification et une variante acceptable.

---

CAPACITÉ : P-DATA-CONSTR-02A — Lire, modifier, construire et itérer sur des tableaux.

PREUVE COURS : « On peut lire un élément (notes[0]), le modifier (notes[1] = 14), ajouter un élément en fin de liste (notes.append(18)), ou parcourir tous les éléments avec une boucle for. [...] Une compréhension de liste permet de construire une liste à partir d'une règle concise. Par exemple, [x*x for x in range(5)] produit la liste [0, 1, 4, 9, 16]. » (cours_eleve.md#listes-et-tableaux-python)
   -> enseigne réellement la capacité ? oui

PREUVE ENTRAÎNEMENT : « On représente des températures par une liste. Écrire une compréhension qui ajoute 1 à chaque température. [...] Écrire une compréhension de liste qui double chaque élément de [3, 5, 8]. Écrire une boucle qui additionne tous les éléments d'une liste nombres. » (td.md#exercice-6---socle---tuples-et-listes et cours_eleve.md#exercice-intégré-4)
   -> l'élève s'entraîne réellement sur cette capacité ? oui

PREUVE CORRECTION : « La compréhension [t + 1 for t in temperatures] convient pour ajouter 1. [...] [x * 2 for x in [3, 5, 8]] produit [6, 10, 16]. Boucle de somme : total = 0 ; for n in nombres: total += n. Variante : total = sum(nombres). » (corrige.md#exercice-intégré-4--listes-p-data-constr-02a)
   -> l'élève peut s'auto-corriger ? oui

VERDICT : needs_review
JUSTIFICATION : Le cours enseigne lecture, modification, ajout, boucle for et compréhension de liste avec des exemples spécifiques. Le TD et l'exercice intégré 4 font pratiquer ces opérations. Le corrigé donne les résultats avec variantes acceptables.

---

CAPACITÉ : P-DATA-CONSTR-03A — Construire et parcourir un dictionnaire.

PREUVE COURS : « stock = {"stylo": 18, "cahier": 5} associe la clé "stylo" à la valeur 18. On accède ensuite au stock de stylos par stock["stylo"]. [...] Les méthodes keys(), values() et items() permettent de parcourir un dictionnaire. [...] [Exemple complet de comptage de votes avec construction itérative du dictionnaire.] » (cours_eleve.md#dictionnaires)
   -> enseigne réellement la capacité ? oui

PREUVE ENTRAÎNEMENT : « On dispose de votes = ["A", "B", "A", "C", "A", "B"]. Construire le dictionnaire des effectifs. Identifier la clé de plus grand effectif. Expliquer pourquoi un dictionnaire est adapté à cette tâche. » (td.md#exercice-7---standard---dictionnaires)
   -> l'élève s'entraîne réellement sur cette capacité ? oui

PREUVE CORRECTION : « Résultat attendu : {"A": 3, "B": 2, "C": 1}. La clé de plus grand effectif est "A". Un dictionnaire est adapté car on associe chaque choix à son effectif et on y accède directement par le nom du choix. » (corrige.md#exercice-7--dictionnaires-p-data-constr-03a)
   -> l'élève peut s'auto-corriger ? oui

VERDICT : needs_review
JUSTIFICATION : Le cours montre la construction, l'accès par clé et le parcours avec keys/values/items sur un exemple concret (stock, puis comptage de votes). Le TD demande de construire un dictionnaire et de justifier le choix. Le corrigé donne le résultat, la justification et une variante acceptable.

---

CAPACITÉ : P-LANG-04 — Utiliser des jeux de tests.

PREUVE COURS : « Un test vérifie qu'une fonction produit le résultat attendu pour une entrée choisie. Un cas limite est une valeur particulière qui risque de révéler une erreur de programmation. [...] Conversions de base : tester avec 0 (traitement spécial dans beaucoup d'algorithmes), avec 1 (plus petit entier non nul), et avec la plus grande valeur autorisée. [...] Un jeu de tests ne prouve jamais que la fonction est correcte dans tous les cas possibles, mais un bon jeu de tests — couvrant des cas ordinaires et des cas limites — réduit considérablement le risque. » (cours_eleve.md#tests-et-cas-limites)
   -> enseigne réellement la capacité ? oui

PREUVE ENTRAÎNEMENT : « Tester mentalement mystere(6). Identifier le cas limite non géré. Proposer une correction. Proposer trois tests. » (td.md#exercice-9---analyse-de-code)
   -> l'élève s'entraîne réellement sur cette capacité ? oui

PREUVE CORRECTION : « Le cas limite non géré est n = 0 : la boucle while n > 0 ne s'exécute pas, et la fonction renvoie une chaîne vide au lieu de "0". Correction : ajouter if n == 0: return "0". Trois tests pertinents : mystere(0) (cas limite), mystere(1) (plus petit non nul), mystere(6) (cas ordinaire). » (corrige.md#exercice-9--analyse-de-code-p-lang-04)
   -> l'élève peut s'auto-corriger ? oui

VERDICT : needs_review
JUSTIFICATION : Le cours définit test et cas limite, donne des exemples spécifiques par notion et explique les limites d'un jeu de tests. Le TD demande d'analyser une fonction, d'identifier un cas limite non géré et de proposer trois tests. Le corrigé fournit le cas limite, la correction et les trois tests avec justifications.

---

## Synthèse

| Capacité | Verdict |
|----------|---------|
| P-DATA-BASE-01 | needs_review |
| P-DATA-BASE-02B | needs_review |
| P-DATA-BASE-04 | needs_review |
| P-DATA-BASE-05A | needs_review |
| P-DATA-CONSTR-01 | needs_review |
| P-DATA-CONSTR-02A | needs_review |
| P-DATA-CONSTR-03A | needs_review |
| P-LANG-04 | needs_review |

**8/8 capacités avec preuves citées, statut needs_review en attente de validation pédagogique et scientifique indépendante.**
