# Trajectoire de couverture — Phase 0

## Mesure de référence

Commande :

```bash
python -m pytest tests -q \
  --cov=scripts \
  --cov-branch \
  --cov-report=term \
  --cov-report=json:/tmp/nexus-p03-coverage.json
```

Mesure du 30 juillet 2026 :

| Indicateur | Couvert | Total | Taux |
|---|---:|---:|---:|
| Lignes | 4 556 | 5 799 | 78,57 % |
| Branches | 1 705 | 2 350 | 72,55 % |
| Combiné couverture.py | — | — | **76,83 %** |

Le seuil de non-baisse est fixé à `76.83` avec une précision de deux décimales.
Ce seuil est un plancher de Phase 0, pas un niveau suffisant pour une release.

La collecte initiale a aussi révélé un test de dépôt resté attaché à la
baseline provisoire. Son contrat a été aligné sur la baseline gelée et la suite
historique concernée repasse à 421 tests verts. L'exécution des lignes de
production était identique avant et après cette correction d'assertion.

## Couverture par module

| Module | Combinée | Lignes | Branches | Cible critique 85 % |
|---|---:|---:|---:|---|
| `baseline_qualification.py` | 82,18 % | 85,96 % | 74,29 % | non atteinte |
| `build_manifest.py` | 71,19 % | 75,55 % | 58,64 % | non atteinte |
| `check_charte_sync.py` | 58,33 % | 61,54 % | 50,00 % | hors cœur, dette |
| `ci_audit_collection.py` | 45,61 % | 44,36 % | 48,96 % | non atteinte |
| `inventory_assembly.py` | 90,80 % | 90,26 % | 91,78 % | atteinte |
| `inventory_collection.py` | 75,69 % | 77,60 % | 70,91 % | non atteinte |
| `inventory_graph.py` | 97,70 % | 98,66 % | 95,59 % | atteinte |
| `inventory_pdf.py` | 87,73 % | 89,08 % | 84,09 % | atteinte au combiné |
| `inventory_reports.py` | 95,76 % | 96,02 % | 95,19 % | atteinte |

## Branches critiques non couvertes

| Priorité | Domaine | Lacune principale | Protection attendue |
|---|---|---|---|
| P0.4 | baseline | erreurs CLI et validations négatives de `baseline_qualification.py` | tests subprocess avec codes et sorties exacts |
| P0.4 | transactions | préflight, échec partiel et récupération de `build_manifest.py` | injections d'échec avant/après remplacement |
| P0.4 | provenance | branches Git atypiques et erreurs d'artefacts dans `inventory_collection.py` | dépôts temporaires, SHA invalide, état sale |
| P0.4 | CI | dispatch et erreurs des sous-commandes de `ci_audit_collection.py` | tests CLI réels, artefacts présents même en échec |
| P0.5 | charte | erreurs d'entrée et sortie de `check_charte_sync.py` | fixtures minimales et chemins invalides |

## Règle d'évolution

- Toute baisse sous `76.83` échoue.
- Chaque lot de tests critiques doit relever le seuil dans le même commit que
  la couverture gagnée.
- Les modules de génération, baseline, provenance et transactions visent au
  minimum 85 % combinés, avec une couverture de branches explicite des chemins
  d'erreur.
- Les appels subprocess doivent être mesurés ou doublés par des tests unitaires
  des fonctions qu'ils exercent ; une exécution non mesurée ne vaut pas preuve
  de couverture.
- Le seuil global ne remplace ni les tests de mutation, ni les gates métier, ni
  les cinq contrôles visuels actuellement rouges.
