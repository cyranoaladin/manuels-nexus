# Stratégie de scraping et collecte contrôlée

## Principe

Aucune source n'est scrapée ou ingérée sans classification préalable dans
`sources_catalog.yml`. Une source externe peut inspirer une activité, alimenter
une collection d'inspiration ou servir de comparaison, mais ne prouve jamais la
couverture interne du corpus.

## Couverture de collecte

- textes officiels et programmes ;
- annales publiques et sujets pratiques si licence compatible ;
- ressources pédagogiques ouvertes ;
- supports internes Drive après audit RGPD ;
- références scientifiques simples ;
- exemples de TP et QCM réutilisables seulement après réécriture autorisée.

## Interdictions

- pas de scraping aveugle ;
- pas de données élèves ;
- pas de documents sensibles ;
- pas de reproduction massive de contenus protégés ;
- pas de fichier `/AUDIT` comme corpus pédagogique ;
- pas de source externe comme preuve de couverture interne.

## Collections

- `nsi_corpus` : ressources internes produites ;
- `rag_education` : sources Drive, ressources externes et inspiration ;
- `nsi_official` : textes officiels ;
- `nsi_annales` : annales et sujets publics si licence compatible.
