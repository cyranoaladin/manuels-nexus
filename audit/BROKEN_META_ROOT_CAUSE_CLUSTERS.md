# Broken META Root-Cause Clusters

Regroupement par signature des 2 803 références META brisées.

| Cluster ID | Cluster Name | Count | Affected Manuals | Root Cause | Fix Strategy |
| --- | --- | --- | --- | --- | --- |
| `CLUSTER-META-01` | Missing Course/Exercise Target META ID | `2150` | `1NSI,1SPE,TNSI,TSPE_2026_2027` | Référence META explicite dans un exercice/méthode vers un ID non déclaré | Déclaration ou correction de l ID cible dans la source TeX |
| `CLUSTER-META-02` | Legacy NSI ID Pattern (ADGK) | `450` | `1NSI` | Ancien préfixe ADGK dans les fichiers de cours ou méthodes | Alignement sur le préfixe d identifiant APT |
| `CLUSTER-META-03` | Capacity Naming Variation | `203` | `1SPE,TSPE_2026_2027,TCOMPL,TEXPERTES` | Variante de majuscule/underscore dans le code de capacité officielle | Normalisation de la table d alias dans l analyseur d inventaire |
