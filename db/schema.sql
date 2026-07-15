-- Schéma PostgreSQL du noyau manuel-maths
-- Requiert : CREATE EXTENSION IF NOT EXISTS vector;

CREATE EXTENSION IF NOT EXISTS vector;

-- 1. Référentiel officiel (source de vérité, chargé depuis referentiel/*.json)
CREATE TABLE IF NOT EXISTS capacites (
    id            TEXT PRIMARY KEY,          -- ex. 1SPE-SUITES-C3
    niveau        TEXT NOT NULL,             -- 1SPE, TSPE, TEXP, 2GT...
    theme         TEXT NOT NULL,             -- SUITES, DERIVATION...
    libelle_bo    TEXT NOT NULL,             -- formulation officielle
    libelle_eleve TEXT NOT NULL,             -- "Je sais ..."
    demonstration_exigible BOOLEAN DEFAULT FALSE,
    algo_bo       TEXT,                      -- algorithme cité au B.O. le cas échéant
    bo_reference  TEXT NOT NULL              -- ex. "BO spécial n°1 du 22/01/2019, p.4"
);

-- 2. Corpus indexé
CREATE TABLE IF NOT EXISTS chunks (
    id            BIGSERIAL PRIMARY KEY,
    source_id     TEXT NOT NULL,             -- SRC-0042 (sources/registry.yaml)
    doc_url       TEXT NOT NULL,
    doc_hash      TEXT NOT NULL,
    chunk_type    TEXT NOT NULL CHECK (chunk_type IN
                   ('cours','methode','exercice','corrige','activite','evaluation','erreur_type','autre')),
    niveau        TEXT,
    theme         TEXT,
    capacites     TEXT[],                    -- ids probables
    difficulte    SMALLINT,                  -- 1..3
    usage_policy  TEXT NOT NULL,             -- verbatim | adaptation_attribution | inspiration_reformulation
    tier          TEXT NOT NULL,             -- T1..T5
    content_md    TEXT NOT NULL,             -- Markdown + LaTeX normalisé
    embedding     vector(1024),
    tsv           tsvector GENERATED ALWAYS AS (to_tsvector('french', content_md)) STORED,
    created_at    TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS chunks_embedding_idx ON chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS chunks_tsv_idx ON chunks USING gin (tsv);
CREATE INDEX IF NOT EXISTS chunks_filtres_idx ON chunks (tier, chunk_type, niveau, theme);

-- 3. Banque d'objets du manuel
CREATE TABLE IF NOT EXISTS objets (
    id            TEXT PRIMARY KEY,          -- ex. 1SPE-SUITES-EX-024
    chapitre      TEXT NOT NULL,
    type_objet    TEXT NOT NULL CHECK (type_objet IN
                   ('cours','methode','exercice','corrige','coup_de_pouce','qcm','td',
                    'evaluation','remediation','diagnostic','fiche_r')),
    capacites     TEXT[] NOT NULL,
    methodes      TEXT[],                    -- M* liées
    parcours      SMALLINT,                  -- 1=◆ 2=◆◆ 3=◆◆◆ (NULL si non applicable)
    competences   TEXT[],                    -- chercher, modéliser, représenter, calculer, raisonner, communiquer
    duree_min     SMALLINT,
    mode_creation TEXT CHECK (mode_creation IN ('adaptation','inspiration','ex_nihilo')),
    sources_inspiration TEXT[],              -- SRC-* / chunk ids (audit interne)
    parametres_sympy JSONB,                  -- variables + contraintes pour variantes
    fichier_tex   TEXT NOT NULL,             -- chemin relatif dans le dépôt
    status        TEXT NOT NULL DEFAULT 'draft'
                   CHECK (status IN ('draft','generated','verified','manual_review','ready','rejected')),
    created_at    TIMESTAMPTZ DEFAULT now(),
    updated_at    TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS objets_chapitre_idx ON objets (chapitre, type_objet, status);

-- 4. Validations (verdicts des gates)
CREATE TABLE IF NOT EXISTS validations (
    id            BIGSERIAL PRIMARY KEY,
    objet_id      TEXT NOT NULL REFERENCES objets(id),
    gate          TEXT NOT NULL CHECK (gate IN
                   ('sympy','similarity','conformite','compilation','adversarial','revue_humaine')),
    verdict       TEXT NOT NULL CHECK (verdict IN ('pass','fail','warning','manual_review')),
    details       JSONB,
    reviewer      TEXT,                      -- humain ou modèle
    created_at    TIMESTAMPTZ DEFAULT now()
);

-- 5. Vue de couverture capacités × parcours
CREATE OR REPLACE VIEW couverture AS
SELECT c.id AS capacite, p.parcours,
       COUNT(o.id) FILTER (WHERE o.type_objet='exercice' AND o.status IN ('verified','ready')) AS nb_exercices
FROM capacites c
CROSS JOIN (VALUES (1),(2),(3)) AS p(parcours)
LEFT JOIN objets o ON c.id = ANY(o.capacites) AND o.parcours = p.parcours
GROUP BY c.id, p.parcours;
