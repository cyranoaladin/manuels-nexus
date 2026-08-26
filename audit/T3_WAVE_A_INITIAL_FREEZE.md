# T3 Wave A — gel initial

- `WAVE_A_SOURCE_SHA = 7b6140920c1e09d359bc7bf0d837192f3fe455da`
- `RESIDUAL_13 = 13` — `sha256:1abe51ad406752b1e09996020c1afb2db3982ac2741cf98ed7b2118f302ace98`
- `PREVIOUS_89 = 89` — `sha256:8daf2b85cecb556daa788056c66060ee6e0c20d00a09c976b9bac9f1bd9d8303`
- `RESIDUAL_13 ∩ PREVIOUS_89 = 0`
- `UNKNOWN = 0`
- Base : arbre Git immuable au SHA ci-dessus.
- Chronologie : matérialisation rétroactive après le premier lot TDD Suites ; les huit sources modifiées sont explicitement listées dans le JSON.

## Partition résiduelle

| Chapitre | Nombre |
|---|---:|
| `1SPE-EXPONENTIELLE` | 2 |
| `1SPE-SUITES` | 5 |
| `1SPE-VARIABLES-ALEATOIRES` | 4 |
| `TNSI-PROJET` | 2 |

## Treize fingerprints gelés

| Fingerprint | Chapitre | Objet |
|---|---|---|
| `18c7b3aa6301ef4c` | `1SPE-EXPONENTIELLE` | `1SPE-EXPO-COURS-C5` |
| `33e9818ffc70892c` | `1SPE-EXPONENTIELLE` | `1SPE-EXPO-COURS-C5-ALGORITHMES` |
| `47fd672690479f1f` | `1SPE-VARIABLES-ALEATOIRES` | `1SPE-VARALEA-ME-006` |
| `4b9a00c4ef815951` | `1SPE-SUITES` | `1SPE-SUITES-CR-017` |
| `634c54857f49fcc0` | `TNSI-PROJET` | `TNSI-PROJET-ANNUEL` |
| `80b7b42e7d6a78ba` | `1SPE-VARIABLES-ALEATOIRES` | `1SPE-VARALEA-CR-012` |
| `85454c002c0a1d6a` | `1SPE-SUITES` | `1SPE-SUITES-EX-051` |
| `873a020438d7e00a` | `1SPE-VARIABLES-ALEATOIRES` | `1SPE-VARALEA-ME-007` |
| `8ca4f3f2a9212e39` | `1SPE-SUITES` | `1SPE-SUITES-RE-C8` |
| `bd63d2a316c26b0c` | `TNSI-PROJET` | `TNSI-PROJET-CONTRACT` |
| `d6985b17d7cab316` | `1SPE-SUITES` | `1SPE-SUITES-ME-008` |
| `dc8e5dcc030bb539` | `1SPE-VARIABLES-ALEATOIRES` | `1SPE-VARALEA-CR-013` |
| `e8ac154947fefcdb` | `1SPE-SUITES` | `1SPE-SUITES-CO-051` |

L'intersection Wave A avec les 89 dettes antérieures est vide. La fermeture finale sera réconciliée à partir de ces deux sets gelés, sans double comptage.
