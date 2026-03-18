-- schema.sql
-- Canonical DDL for archive_inventory.db
-- Civil Engineering knowledge index
-- Schema version: 2

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS schema_version (
    version     INTEGER NOT NULL,
    applied_at  TEXT    NOT NULL,
    description TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS authority_levels (
    authority_level TEXT PRIMARY KEY NOT NULL
);

INSERT OR IGNORE INTO authority_levels (authority_level) VALUES ('WSDOT');
INSERT OR IGNORE INTO authority_levels (authority_level) VALUES ('AASHTO');
INSERT OR IGNORE INTO authority_levels (authority_level) VALUES ('supporting');
INSERT OR IGNORE INTO authority_levels (authority_level) VALUES ('derived');

CREATE TABLE IF NOT EXISTS source_kinds (
    source_kind TEXT PRIMARY KEY NOT NULL
);

INSERT OR IGNORE INTO source_kinds (source_kind) VALUES ('manual');
INSERT OR IGNORE INTO source_kinds (source_kind) VALUES ('reference');
INSERT OR IGNORE INTO source_kinds (source_kind) VALUES ('artifact');
INSERT OR IGNORE INTO source_kinds (source_kind) VALUES ('note');
INSERT OR IGNORE INTO source_kinds (source_kind) VALUES ('report');

CREATE TABLE IF NOT EXISTS record_types (
    record_type TEXT PRIMARY KEY NOT NULL
);

INSERT OR IGNORE INTO record_types (record_type) VALUES ('manual');
INSERT OR IGNORE INTO record_types (record_type) VALUES ('reference_note');
INSERT OR IGNORE INTO record_types (record_type) VALUES ('precedent');
INSERT OR IGNORE INTO record_types (record_type) VALUES ('decision_driver');
INSERT OR IGNORE INTO record_types (record_type) VALUES ('discovery_report');
INSERT OR IGNORE INTO record_types (record_type) VALUES ('intake_item');

CREATE TABLE IF NOT EXISTS relationship_types (
    relationship_type TEXT PRIMARY KEY NOT NULL
);

INSERT OR IGNORE INTO relationship_types (relationship_type) VALUES ('governs');
INSERT OR IGNORE INTO relationship_types (relationship_type) VALUES ('supports');
INSERT OR IGNORE INTO relationship_types (relationship_type) VALUES ('impacts');
INSERT OR IGNORE INTO relationship_types (relationship_type) VALUES ('distills_to');
INSERT OR IGNORE INTO relationship_types (relationship_type) VALUES ('reports_on');

CREATE TABLE IF NOT EXISTS tag_types (
    tag_type TEXT PRIMARY KEY NOT NULL
);

INSERT OR IGNORE INTO tag_types (tag_type) VALUES ('discipline');
INSERT OR IGNORE INTO tag_types (tag_type) VALUES ('topic');
INSERT OR IGNORE INTO tag_types (tag_type) VALUES ('decision_type');

CREATE TABLE IF NOT EXISTS sources (
    id              INTEGER PRIMARY KEY,
    title           TEXT    NOT NULL,
    authority_level TEXT    NOT NULL,
    source_kind     TEXT    NOT NULL,
    path            TEXT    NOT NULL UNIQUE,
    status          TEXT    NOT NULL DEFAULT 'active',
    last_reviewed   TEXT,
    notes           TEXT,
    created_at      TEXT    NOT NULL,
    updated_at      TEXT    NOT NULL,
    FOREIGN KEY (authority_level) REFERENCES authority_levels (authority_level),
    FOREIGN KEY (source_kind) REFERENCES source_kinds (source_kind)
);

CREATE TABLE IF NOT EXISTS knowledge_items (
    id               INTEGER PRIMARY KEY,
    title            TEXT    NOT NULL,
    record_type      TEXT    NOT NULL,
    authority_level  TEXT    NOT NULL,
    summary          TEXT,
    confidence_basis TEXT,
    output_path      TEXT,
    created_at       TEXT    NOT NULL,
    updated_at       TEXT    NOT NULL,
    FOREIGN KEY (record_type) REFERENCES record_types (record_type),
    FOREIGN KEY (authority_level) REFERENCES authority_levels (authority_level)
);

CREATE TABLE IF NOT EXISTS tags (
    id        INTEGER PRIMARY KEY,
    tag_type  TEXT NOT NULL,
    tag_value TEXT NOT NULL,
    FOREIGN KEY (tag_type) REFERENCES tag_types (tag_type),
    UNIQUE (tag_type, tag_value)
);

CREATE TABLE IF NOT EXISTS source_tags (
    id        INTEGER PRIMARY KEY,
    source_id INTEGER NOT NULL,
    tag_id    INTEGER NOT NULL,
    FOREIGN KEY (source_id) REFERENCES sources (id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE,
    UNIQUE (source_id, tag_id)
);

CREATE TABLE IF NOT EXISTS knowledge_item_tags (
    id                INTEGER PRIMARY KEY,
    knowledge_item_id INTEGER NOT NULL,
    tag_id            INTEGER NOT NULL,
    FOREIGN KEY (knowledge_item_id) REFERENCES knowledge_items (id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE,
    UNIQUE (knowledge_item_id, tag_id)
);

CREATE TABLE IF NOT EXISTS knowledge_item_sources (
    id                INTEGER PRIMARY KEY,
    knowledge_item_id INTEGER NOT NULL,
    source_id         INTEGER NOT NULL,
    FOREIGN KEY (knowledge_item_id) REFERENCES knowledge_items (id) ON DELETE CASCADE,
    FOREIGN KEY (source_id) REFERENCES sources (id) ON DELETE CASCADE,
    UNIQUE (knowledge_item_id, source_id)
);

CREATE TABLE IF NOT EXISTS relationships (
    id                INTEGER PRIMARY KEY,
    from_type         TEXT NOT NULL,
    from_id           INTEGER NOT NULL,
    to_type           TEXT NOT NULL,
    to_id             INTEGER NOT NULL,
    relationship_type TEXT NOT NULL,
    FOREIGN KEY (relationship_type) REFERENCES relationship_types (relationship_type)
);

CREATE TABLE IF NOT EXISTS report_runs (
    id                        INTEGER PRIMARY KEY,
    request_summary           TEXT NOT NULL,
    report_path               TEXT NOT NULL,
    governing_sources_summary TEXT NOT NULL,
    created_at                TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS validation_results (
    id       INTEGER PRIMARY KEY,
    run_at   TEXT    NOT NULL,
    passed   INTEGER NOT NULL,
    details  TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_sources_authority_level ON sources (authority_level);
CREATE INDEX IF NOT EXISTS idx_sources_source_kind ON sources (source_kind);
CREATE INDEX IF NOT EXISTS idx_sources_path ON sources (path);
CREATE INDEX IF NOT EXISTS idx_knowledge_items_record_type ON knowledge_items (record_type);
CREATE INDEX IF NOT EXISTS idx_knowledge_items_authority_level ON knowledge_items (authority_level);
CREATE INDEX IF NOT EXISTS idx_knowledge_items_output_path ON knowledge_items (output_path);
CREATE INDEX IF NOT EXISTS idx_tags_type_value ON tags (tag_type, tag_value);
CREATE INDEX IF NOT EXISTS idx_source_tags_source_id ON source_tags (source_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_item_tags_knowledge_item_id ON knowledge_item_tags (knowledge_item_id);
CREATE INDEX IF NOT EXISTS idx_knowledge_item_sources_knowledge_item_id ON knowledge_item_sources (knowledge_item_id);
CREATE INDEX IF NOT EXISTS idx_relationships_from_ref ON relationships (from_type, from_id);
CREATE INDEX IF NOT EXISTS idx_relationships_to_ref ON relationships (to_type, to_id);
CREATE INDEX IF NOT EXISTS idx_relationships_type ON relationships (relationship_type);
CREATE INDEX IF NOT EXISTS idx_report_runs_report_path ON report_runs (report_path);