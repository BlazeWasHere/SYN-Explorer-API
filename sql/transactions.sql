CREATE TABLE IF NOT EXISTS txs (
    from_tx_hash bytea PRIMARY KEY,
    to_tx_hash bytea UNIQUE,
    from_address bytea NOT NULL,
    to_address bytea NOT NULL,
    sent_value varchar NOT NULL,
    received_value varchar,
    pending boolean DEFAULT true,
    from_chain_id bigint NOT NULL CHECK (from_chain_id > 0),
    to_chain_id bigint NOT NULL CHECK (to_chain_id > 0),
    sent_time bigint NOT NULL,
    received_time bigint,
    sent_token bytea NOT NULL,
    received_token bytea,
    swap_success boolean
);

CREATE TABLE IF NOT EXISTS lost_txs (
    to_tx_hash bytea PRIMARY KEY,
    to_address bytea NOT NULL,
    received_value varchar NOT NULL,
    to_chain_id bigint NOT NULL CHECK (to_chain_id > 0),
    received_time bigint,
    received_token bytea,
    swap_success boolean
);

CREATE INDEX IF NOT EXISTS idx_from_address ON txs(from_address);

CREATE INDEX IF NOT EXISTS idx_to_address ON txs(to_address);

CREATE INDEX IF NOT EXISTS idx_lost_to_address on lost_txs(to_address);