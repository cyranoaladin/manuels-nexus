# Rapport pilote Substance RAG

Statut : pilote non validant. Les verdicts restent `needs_content` ou
`needs_review`; aucune capacité n'est promue.

## Doctrine

- System A : veto mécanique d'ancres et citations.
- System B : proposeur, jamais décideur.
- Collection de preuves internes : `nsi_corpus`.
- `rag_education` : inspiration externe uniquement.
- Revue humaine requise pour toute promotion.

## Smoke RAG

Le smoke réel doit être établi par :

```bash
python scripts/rag_smoke_test.py
```

Sans `.env.rag`, le résultat attendu en clone propre est
`RAG_SMOKE_TEST_SKIPPED_NO_CONFIG`.

## Capacités pilotes

| capacité | requête RAG | top-k | fichiers candidats | citations retenues | verdict proposé | veto éventuel | action suivante |
| --- | --- | --- | --- | --- | --- | --- | --- |
| P05 | Importer une table depuis un fichier CSV | 5 | à récupérer dans `nsi_corpus` | aucune dans ce rapport | needs_content | smoke/config à établir | exécuter juge avec `.env.rag` valide |
| P06 | Rechercher et trier des données en table | 5 | à récupérer dans `nsi_corpus` | aucune dans ce rapport | needs_content | smoke/config à établir | exécuter juge avec `.env.rag` valide |
| T06 | Distinguer interface et implémentation | 5 | à récupérer dans `nsi_corpus` | aucune dans ce rapport | needs_content | capacité absente dans `coverage.md` | enrichir T06 selon le plan d'écarts |
| T07 | Structures linéaires et recherches | 5 | à récupérer dans `nsi_corpus` | aucune dans ce rapport | needs_content | smoke/config à établir | exécuter juge avec `.env.rag` valide |
| T08 | Arbres binaires et mesures | 5 | à récupérer dans `nsi_corpus` | aucune dans ce rapport | needs_content | capacité absente dans `coverage.md` | enrichir T08/T10 selon le plan d'écarts |
| T10 | Récursivité et parcours d'arbres | 5 | à récupérer dans `nsi_corpus` | aucune dans ce rapport | needs_content | capacités absentes dans `coverage.md` | enrichir T10 selon le plan d'écarts |
| T17 | Protocoles réseau et routage | 5 | à récupérer dans `nsi_corpus` | aucune dans ce rapport | needs_content | smoke/config à établir | exécuter juge avec `.env.rag` valide |
| T18 | Algorithmique avancée et chaînes | 5 | à récupérer dans `nsi_corpus` | aucune dans ce rapport | needs_content | smoke/config à établir | exécuter juge avec `.env.rag` valide |

## Blocage assumé

Ce rapport ne remplace pas le smoke RAG ni une revue humaine. Il sert à fixer le
périmètre pilote et les requêtes à exécuter lorsque la configuration réelle est
disponible.
