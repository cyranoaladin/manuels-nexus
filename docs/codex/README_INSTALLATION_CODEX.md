# Installation de la configuration Codex

Ce dossier contient une configuration cohérente avec les mécanismes natifs de Codex :

- `AGENTS.md` : instructions durables chargées par Codex avant le travail ;
- `CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md` : spécification détaillée ;
- `.agents/skills/nexus-manual-quality/SKILL.md` : workflow réutilisable ;
- `.codex/rules/manuals.rules` : garde-fous de commandes, fonctionnalité expérimentale ;
- `docs/codex/` : gates et modèles de pilotage.

## 1. Copier dans le dépôt

Depuis le dossier extrait :

```bash
cp -a AGENTS.md CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md /chemin/vers/manuels-nexus/
cp -a .agents /chemin/vers/manuels-nexus/
cp -a .codex /chemin/vers/manuels-nexus/
mkdir -p /chemin/vers/manuels-nexus/docs/codex
cp -a docs/codex/. /chemin/vers/manuels-nexus/docs/codex/
```

Ne pas écraser un `AGENTS.md` existant sans comparer et fusionner son contenu.

## 2. Vérifier la confiance du projet

Les règles locales sous `.codex/rules/` ne se chargent que pour un projet de confiance.

Lancer Codex dans le worktree concerné et vérifier son statut.

## 3. Redémarrer Codex

Codex recharge la chaîne `AGENTS.md` au lancement. Les skills sont détectées automatiquement ; redémarrer Codex si la nouvelle skill n’apparaît pas.

## 4. Vérifier les instructions

Depuis la racine du dépôt :

```bash
codex --ask-for-approval never "Résume les instructions de projet actives et cite les fichiers chargés."
```

Selon la version locale, utiliser `codex` puis `/status` si cette forme de commande n’est pas acceptée.

## 5. Vérifier la skill

Dans Codex :

```text
/skills
```

ou invoquer explicitement :

```text
$nexus-manual-quality
```

## 6. Prompt de démarrage recommandé

```text
Utilise $nexus-manual-quality. Lis AGENTS.md et CODEX_CAHIER_DES_CHARGES_MANUEL_1SPE.md. Préserve le WIP, vérifie le HEAD et les gates, puis exécute la prochaine action atomique de la phase courante. Ne commence aucun nouveau contenu tant que les P0 structurels et mathématiques ne sont pas stabilisés.
```

## Pourquoi il n’y a pas de `rules.md`

`rules.md` n’est pas un nom spécial de Codex. Les instructions projet doivent être placées dans `AGENTS.md`. Les garde-fous de commandes utilisent des fichiers `.rules` sous un dossier `.codex/rules/`.
