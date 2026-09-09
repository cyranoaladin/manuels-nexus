# Propriété intellectuelle et données personnelles — 9 septembre 2026

Constat préalable à toute publication. Le dépôt distant est **public**.

## Propriété intellectuelle : aucun emprunt détecté

**Aucune figure tierce n'est incorporée dans les manuels.** Les sources de
chapitres ne contiennent **zéro `\includegraphics`** : toutes les figures sont
construites en TikZ, dans le dépôt. Il n'y a donc pas de capture, pas d'extrait
scanné, pas d'illustration importée.

Les 190 fichiers PNG suivis se répartissent en deux familles, toutes deux
produites par le projet :

| Famille | Nombre | Nature |
|---|---:|---|
| Rendus de pages pour revue visuelle (`audit/`, `validations/`) | 187 | images produites par la chaîne de compilation du dépôt |
| Logos Nexus Réussite (`logo.png`, `logo_slogan_nexus.png`, `logo_nexus.png`) | 3 | identité de la collection |

**Sources officielles : provenance tracée.** `NSI/sources/SOURCES.md` enregistre
pour chaque texte le numéro d'arrêté, l'URL du BO, l'URL de l'annexe officielle
et le SHA-256 vérifié de la copie locale, avec une note explicite précisant que
cela atteste l'identité et l'authenticité de la copie, **pas** son applicabilité
à l'édition 2026-2027.

## Données personnelles

**Secrets : aucun.** `gitleaks` signale 2 942 résultats sur les 1 526 commits
jamais poussés ; les 109 valeurs distinctes ont été inspectées une par une :
108 sont des identifiants de chapitres (`1SPE-DERIVATION-GLOBAL`, …) et la
dernière est un SHA d'objet arbre Git. Zéro secret réel. `trufflehog` confirme :
**0 secret vérifié et 0 non vérifié** sur 162 141 fragments et 278 Mo.

**Numéros de téléphone : aucun.** Les motifs détectés sont des sous-chaînes de
condensats SHA-256.

**Adresses électroniques.** Les seules adresses réelles proviennent d'un unique
fichier, `Mathematiques/manuel-maths/sources/txt/BO2026_n14_complet.txt`, qui
est le texte intégral du Bulletin officiel. Les coordonnées qu'il contient
(fédération sportive, contacts de recrutement) ont été publiées par l'État dans
un bulletin public, et ce fichier était **déjà sur `origin/main` avant cette
consolidation**. Aucune donnée d'élève, aucun fichier nominatif, aucun `.env`,
aucune base de données.

## Un point à arbitrer par une décision humaine

Trois fichiers de traçabilité du corpus NSI portent **49 liens Google Drive**
vers des documents personnels :

- `NSI/corpus_nsi/drive_inventory.csv`
- `NSI/corpus_nsi/drive_quarantine_manifest.csv`
- `NSI/corpus_nsi/drive_sources.yml`

Ils sont **publics sur `origin` depuis le 11 août 2026** ; cette consolidation
ne les a pas introduits. Un lien Drive de la forme `/file/d/<id>/view` donne
accès au document **si son partage est réglé sur « toute personne disposant du
lien »**. Le réglage de ces 49 documents n'a pas été testé : les ouvrir aurait
signifié accéder aux fichiers privés de l'auteur.

Ce point n'est pas tranché ici. Il appelle une vérification humaine du partage
de ces documents, et, le cas échéant, une décision : restreindre le partage
côté Drive, ou retirer les identifiants du dépôt — étant entendu qu'un retrait
du fichier ne les efface pas de l'historique Git.

## Verdict

Rien n'interdit la publication au titre de la propriété intellectuelle ni des
données personnelles, **sous réserve** de l'arbitrage humain ci-dessus sur les
49 liens Drive.
