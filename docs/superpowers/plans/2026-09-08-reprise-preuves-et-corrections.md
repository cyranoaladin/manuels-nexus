# Reprise des preuves et corrections déterminables

> Exécution par tâches indépendantes avec revue croisée. Autorisation : mandat
> humain de reprise, notamment §§33–35 ; aucune micro-approbation additionnelle.

**Objectif :** rendre les sources et les preuves courantes exactes avant de
reprendre la fermeture sémantique du corpus, sans publication.

**Architecture :** conserver les producteurs et référentiels canoniques.
Ajouter des observations de delta et un index dérivé des sources réellement
présentes. Les preuves historiques restent immuables ; seuls les bindings
actuels dûment justifiés peuvent être reconstruits. Aucun quota de volume.

**Outils :** Python, pytest, SymPy, JSON/YAML, sources TeX, Git local.

- [x] Relever l'état Git, environnement et inventaire propre initial.
- [x] Lire gouvernance et cahiers ; déléguer trois forensiques indépendantes.
- [x] Reproduire les compteurs et publier le checkpoint initial avec inconnues explicites.
- [ ] Finaliser le delta Astra : un contrôle par ID, empreintes des documents
  externes, preuves courantes et statut conservateur ; ne copier aucun document.
- [ ] Programme : écrire des tests rouges pour les fragments `#Qn`, les
  sources supprimées et les espaces d'identité du second degré ; corriger les
  producteurs concernés, vérifier les tests ciblés, puis committer séparément.
- [ ] Science : reproduire chaque contre-exemple avant correction TeX ; ajouter
  oracle adéquat et régression, faire relire le nouveau texte indépendamment,
  invalider les bindings anciens puis réexécuter les vérifications ciblées.
- [ ] QA : exercer `verify_sympy.verify_chapter` sur des copies temporaires
  des méthodes, comparer l'ensemble attendu à l'ensemble exécuté ; prouver
  par mutation qu'une assertion fausse et une omission de méthode sont détectées.
- [ ] Index : définir un objet courant par chemin/ID/digest du modèle frais ;
  tests rouges pour doublon, retrait, substitution et preuve périmée ; produire
  `CURRENT_REVIEW_INDEX` sans altérer les anciennes queues humaines.
- [ ] Revue : constituer des lots de textes effectivement lus ; résolution
  indépendante et cas limites ; evidence par dimension, jamais HUMAN_APPROVED.
- [ ] Recalculer les registres affectés après stabilisation des sources ;
  contrôles ciblés puis commits atomiques. Aucune régénération globale concurrente.
- [ ] Réévaluer les préconditions de full suite et freeze selon le mandat.

Chaque correction suit des pas bornés : reproduction/test rouge, changement
minimal, test vert, revue du diff et preuve d'invalidation, commit local. Les
lots scientifiques, programme, tests et registres sont distincts. Les travaux
visuels, builds finaux et approbations attendent les préconditions réelles.
