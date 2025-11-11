-- Schéma de la base de données du Registre PPE (PostgreSQL)

-- Table 1: source_document
-- Référentiel des sources collectées pour assurer la traçabilité.
CREATE TABLE IF NOT EXISTS source_document (
    source_id SERIAL PRIMARY KEY,
    url TEXT UNIQUE NOT NULL,
    title VARCHAR(512),
    snippet TEXT,
    publish_date DATE,
    raw_data_path TEXT -- Lien vers le Data Lake (stockage brut)
);

-- Table 2: pep_master
-- Enregistrement unique et maître pour chaque PPE (assure la déduplication).
CREATE TABLE IF NOT EXISTS pep_master (
    id UUID PRIMARY KEY,
    country_code VARCHAR(2) NOT NULL, -- Pour la modularité par pays
    master_name VARCHAR(255) NOT NULL,
    current_version_id UUID -- Clé étrangère vers la version la plus récente dans pep_version
);

-- Table 3: pep_version
-- Historique des versions (immuable) de chaque enregistrement PPE.
CREATE TABLE IF NOT EXISTS pep_version (
    version_id UUID PRIMARY KEY,
    pep_id UUID NOT NULL REFERENCES pep_master(id),
    data_jsonb JSONB NOT NULL, -- Contient le corps complet de l'enregistrement PPE (point 5)
    confidence_score NUMERIC(3, 2) NOT NULL,
    status VARCHAR(32) NOT NULL, -- 'active', 'former', 'under_review'
    first_seen TIMESTAMP WITH TIME ZONE NOT NULL,
    last_updated TIMESTAMP WITH TIME ZONE NOT NULL
);

-- Table 4: audit_log
-- Journal d'audit pour chaque modification ou action significative.
CREATE TABLE IF NOT EXISTS audit_log (
    log_id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    pep_id UUID REFERENCES pep_master(id),
    version_id UUID REFERENCES pep_version(version_id),
    actor VARCHAR(128) NOT NULL, -- 'System', 'Human', 'ETL_Process'
    source TEXT, -- URL ou nom du processus ETL
    reason TEXT NOT NULL -- Description de l'action (e.g., 'Nouveau PEP créé', 'Changement de poste')
);

-- Index pour optimiser les requêtes
CREATE INDEX IF NOT EXISTS idx_pep_version_pep_id ON pep_version(pep_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_pep_id ON audit_log(pep_id);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON audit_log(timestamp DESC);

-- Index pour la recherche rapide dans le JSONB (par exemple, sur le nom complet)

-- Mise à jour de la clé current_version_id dans pep_master après l'insertion dans pep_version
-- Note: En production, ceci serait géré par une fonction/trigger ou directement par la logique de l'application.
-- Pour la simulation, nous considérons que la logique ETL gère cette mise à jour.
