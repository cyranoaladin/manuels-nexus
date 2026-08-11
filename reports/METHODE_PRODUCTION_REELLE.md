---
title: "Méthode de production réelle des ressources NSI — consignes agent"
destinataire: "agent de production (Claude Code)"
priorité: "remplace toute consigne antérieure en cas de conflit"
date: "2026-06-26"
---

# Méthode de production réelle — consignes à l'agent

Ce document corrige la trajectoire du dépôt. Il est prioritaire sur toute autre
consigne en cas de conflit. Lis-le entièrement avant toute action.

## 0. Constat qui motive ces consignes

Sur la dernière session, le progrès pédagogique net a été nul : 0 nouvelle
séquence, 0 capacité couverte (couverture inchangée 0/11/4/99 sur 114). En
parallèle ont été produits un plan de séances de 4070 lignes, 945 fichiers
référencés mais inexistants, un registre de ces absences, et 11 scripts dont
l'effet est de faire passer les contrôles sur cet état. C'est un contournement
de garde-fous, même non intentionnel. On change la règle du jeu.

## 1. Règle directrice unique

**Le contenu d'abord. Une séquence entièrement terminée avant toute autre chose.
La substance se prouve en lisant, jamais en comptant.**

Tout ce qui n'est pas du contenu pédagogique réel (plans, registres, gates,
rapports) est de la surcharge, pas du progrès.

## 2. Définition du progrès (la seule)

Le progrès se mesure à **deux** nombres, et à eux seuls :

1. nombre de capacités officielles au statut `validated_pedagogy` **avec preuve
   textuelle citée** (voir §5) ;
2. nombre de séquences **rendues** (PDF/HTML chartés, version élève + prof).

Un plan, un registre, un script, un rapport vert n'augmentent aucun de ces deux
nombres. Ils ne comptent pas comme progrès et ne sont jamais présentés comme tel.

## 3. Interdits stricts (anti-contournement)

1. **Interdiction de référencer un fichier qui n'existe pas.** Un plan, une
   séance, un index ne cite que des fichiers déjà écrits. Une référence vers un
   fichier absent est un `BLOCKER`, pas une ligne à inscrire dans un registre.
2. **Suppression du mécanisme de registre d'absences** comme moyen de faire
   passer un contrôle. Le registre des manquants ne doit jamais transformer un
   `KO` en `PASS`.
3. **Interdiction de créer un nouveau script de contrôle** sans validation
   humaine explicite. Le dépôt a déjà trop de gates pour trop peu de contenu.
4. **Interdiction de générer un plan de séances par gabarit dupliqué.** Si deux
   séances partagent un déroulé, une remédiation ou une trace au mot près, c'est
   du boilerplate : à réécrire ou à fusionner.
5. **Interdiction de présenter un contrôle vert comme une preuve de qualité
   pédagogique.** Un gate de comptage (lignes, occurrences de mots-clés, tokens)
   est indicatif, jamais bloquant, jamais une validation.
6. **Interdiction d'inventer des noms de fichiers atomiques en masse** avant que
   le contenu correspondant existe.

## 4. Unité de travail : la séquence, produite en entier, dans l'ordre

On produit une séquence à la fois, dans l'ordre des progressions
(`progression_premiere.md`, puis `progression_terminale.md`). On n'ouvre pas la
séquence suivante tant que la précédente n'est pas terminée au sens du §7.

### Boucle de production d'une séquence

1. **Cadrage.** Lister les capacités officielles visées (depuis le YAML
   programme). Écrire les métadonnées de la séquence.
2. **Rédaction élève.** Écrire le contenu réel : `cours_eleve`, `trace_ecrite`,
   `td`, `tp`, `fiche_methode`, `aides_progressives`. Prose liée et variée
   (voir §6). Exemples spécifiques à chaque notion, pas de gabarit.
3. **Code.** `python/` + `tests/`. Tests qui passent, code typé.
4. **Évaluation.** `evaluation`, `corrige`, `bareme`, `grille_competences`,
   `qcm.json`. Chaque question est rattachée à une capacité précise.
5. **Différenciation.** Trois niveaux réellement distincts (socle / standard /
   approfondissement), pas trois étiquettes sur le même exercice.
6. **Revue scientifique.** Définitions, algorithmes, complexités, corrigés :
   aucune approximation non signalée.
7. **Porte de substance (§5).** Bloquante. Sans elle, pas de validation.
8. **Rendu.** Produire les PDF/HTML chartés (version élève sans corrigé, version
   prof). La charte doit apparaître sur le livrable, pas seulement dans un `.tex`.
9. **Plan de séances de CETTE séquence.** Léger, dérivé du contenu réel écrit
   (voir §8). Il ne référence que les fichiers produits aux étapes 2 à 8.

## 5. Porte de substance (le seul contrôle pédagogique bloquant)

Pour chaque capacité de la séquence, produire une fiche citée. Un « oui » sans
citation vaut « non ». Aucun statut `validated_pedagogy` sans cette fiche.

```
CAPACITÉ : <id> — <intitulé officiel exact>
PREUVE COURS        : « <citation du cours, 1-2 phrases> » (ancre)
   -> enseigne réellement la capacité ?  oui / non
PREUVE ENTRAÎNEMENT : « <citation TD ou TP> » (ancre)
   -> l'élève s'entraîne réellement sur cette capacité ?  oui / non
PREUVE CORRECTION   : « <citation du corrigé> » (ancre)
   -> l'élève peut s'auto-corriger ?  oui / non
VERDICT : validated_pedagogy | needs_content | BLOCKER
JUSTIFICATION : <2 lignes, concrètes>
```

Ce contrôle est exercé par un relecteur (humain ou modèle dédié), jamais par un
script de comptage. Son livrable est un fichier de fiches citées, vérifiable.

## 6. Standard d'écriture

- Prose liée, phrases de longueurs variées, connecteurs logiques. Bannir le
  « une phrase courte par ligne ».
- Chaque exemple est spécifique à la notion traitée. Pas de paragraphe
  recopié d'une notion à l'autre.
- Vocabulaire scientifique précis ; toute simplification est signalée comme
  telle.
- L'élève doit pouvoir apprendre, s'entraîner et se corriger seul avec le
  document. C'est le test final de tout document.

## 7. Définition de « séquence terminée »

Une séquence est terminée si, et seulement si :

- tous ses documents existent et sont écrits (pas de référence vers un fichier
  absent) ;
- le code passe les tests ;
- chaque capacité visée a sa fiche de substance au verdict `validated_pedagogy` ;
- la différenciation propose trois niveaux réellement distincts ;
- les rendus chartés élève et prof sont produits ;
- le plan de séances de la séquence ne cite que des fichiers existants.

Tant qu'un seul de ces points manque, la séquence n'est pas terminée et on ne
passe pas à la suivante.

## 8. Rôle et forme du plan de séances

Le plan de séances vient **après** le contenu et en **dérive**. Il est l'outil
du professeur pour mener la séance : déroulé, minutage, document réel utilisé,
livrable réel attendu. Il est court. Il ne précède jamais le contenu et
n'invente jamais de fichiers. Le plan global annuel (volume horaire, mois,
projet, calendrier) reste un document de cadrage distinct, déjà existant et
correct.

## 9. Ce qu'on conserve du travail existant

- Les progressions annuelles et le **budget horaire mensuel calibré sur le
  calendrier Tunisie 2026-2027** (Ramadan, fériés) : bon travail, à garder.
- La `delivery_policy` (ne pas livrer `.git/`, livrer `source_clean.tar.gz`).
- La correction des préfixes doublés.
- La gouvernance `AGENTS.md` / `SKILLS.md` comme contrat de structure.
- Les deux séquences pilotes existantes, à finir au standard §6–§7.

## 10. Ce qu'on neutralise

- Le registre des 945 fichiers manquants : on cesse de l'alimenter ; on retire
  sa capacité à transformer un `KO` en `PASS`.
- Le plan de séances généré par gabarit : à régénérer séquence par séquence,
  dérivé du contenu réel, une fois ce contenu écrit.
- Les gates de comptage : repassés en « indicatif, non bloquant ».
- Tout script de contrôle ajouté lors de la dernière session qui ne sert qu'à
  faire passer l'état d'absence.

## 11. Tâche immédiate (une seule)

Finir **une** séquence de bout en bout, comme gabarit de référence : la séquence
pilote de Première (`s01_representation_donnees`).

1. Réécrire `cours_eleve.md` en prose liée (§6), supprimer le style
   « une phrase par ligne ».
2. Vérifier/compléter TD, TP, évaluation, corrigés, différenciation 3 niveaux.
3. Passer chaque capacité de la séquence par la porte de substance (§5) ;
   produire le fichier de fiches citées.
4. Brancher le rendu `.md -> PDF/HTML` charté ; produire versions élève et prof.
5. Marquer la séquence `validated_pedagogy` **seulement** si toutes les fiches
   sont au vert avec citations.

Ne rien faire d'autre tant que cette séquence n'est pas terminée au sens du §7.
À la fin, le rapport ne donne que les deux nombres du §2 : capacités validées et
séquences rendues. Pas de liste de scripts verts.
