# Guide des agents de composition

| # | Agent | Prompt | Entrées | Sorties | Modèle | Gates aval |
|---|---|---|---|---|---|---|
| 1 | Curateur | prompts/curateur.md | contrat.yaml + MCP corpus | dossier_curation.json | Sonnet | validation humaine |
| 2 | Rédacteur-Cours | prompts/redacteur_cours.md | curation + référentiel | cours/*.tex | Opus (strate 1/★), Sonnet (strate 2) | conformité, compilation, similarité, revue humaine |
| 3 | Rédacteur-Méthodes | prompts/redacteur_methodes.md | curation + cours | methodes/*.tex | Sonnet | compilation, similarité |
| 4 | Générateur-Exercices | prompts/generateur_exercices.md | curation + méthodes | exercices/*.tex (+ coups de pouce) | Sonnet (◆/◆◆), Opus (◆◆◆) | sympy, similarité, couverture |
| 5 | Rédacteur-Corrigés | prompts/redacteur_corriges.md | énoncés SEULS | corriges/*.tex | Sonnet | sympy, adversarial (échantillon) |
| 6 | Générateur-QCM | prompts/generateur_qcm.md | curation (erreurs types) | qcm/*.json + *.tex, remediation/*.tex | Sonnet/Haiku | lien distracteur↔erreur (revue) |
| 7 | Vérificateur adversarial | prompts/verificateur_adversarial.md | objet + référentiel | verdict JSON dans validations/ | Opus/Fable | — |

## Règles d'injection de contexte (toutes productions)
1. Le contrat du chapitre (toujours).
2. Le dossier de curation de la capacité concernée (jamais le dossier entier : bruit).
3. `docs/05_conventions_latex.md` + les macros pertinentes de la classe.
4. À partir du 2e chapitre : 2–3 objets `ready` du chapitre pilote, même type, comme few-shot.
5. La `usage_policy` de chaque chunk transmis, rappelée en tête de message.

## Boucle de régénération
Objet en `fail` (sympy ou similarité) → régénération avec le verdict en contexte, 3 tentatives max, puis `manual_review`. Ne jamais modifier le test pour faire passer l'objet.

## Agents spécifiques NSI
| # | Agent | Prompt | Rôle | Gates aval |
|---|---|---|---|---|
| 8 | Restructurateur | prompts/restructurateur.md | Transposition T0 → gabarit (mode dominant) | exécution, compilation, TODO résolus |
| 9 | Générateur ECE | prompts/generateur_ece.md | Sujets épreuve pratique Terminale | corrigé exécuté contre les tests ; squelette à trous qui échoue |

Ordre de préférence en production : Restructurateur (si sources T0) > Générateur (adaptation/ex nihilo).
