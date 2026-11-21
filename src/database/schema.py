"""
ATTACHORA Database Schema Module
Defines relational tables, indices, and schema version management for SQLite.
"""

SCHEMA_VERSION = 1

CREATE_TABLES_SQL = """
-- Table: email_accounts
CREATE TABLE IF NOT EXISTS email_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_email TEXT NOT NULL UNIQUE,
    imap_host TEXT NOT NULL,
    imap_port INTEGER NOT NULL DEFAULT 993,
    mailbox TEXT NOT NULL DEFAULT 'INBOX',
    authentication_type TEXT NOT NULL DEFAULT 'password',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_sync_at TIMESTAMP,
    connection_status TEXT DEFAULT 'configured'
);

-- Table: emails
CREATE TABLE IF NOT EXISTS emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER,
    message_uid TEXT,
    message_id TEXT,
    sender TEXT,
    sender_email TEXT,
    subject TEXT,
    received_at TIMESTAMP,
    mailbox_name TEXT DEFAULT 'INBOX',
    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(account_id) REFERENCES email_accounts(id) ON DELETE SET NULL,
    UNIQUE(account_id, message_uid, message_id)
);

-- Table: attachments
CREATE TABLE IF NOT EXISTS attachments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id INTEGER NOT NULL,
    original_filename TEXT NOT NULL,
    stored_filename TEXT,
    mime_type TEXT,
    extension TEXT,
    file_size INTEGER NOT NULL,
    sha256 TEXT NOT NULL,
    category TEXT DEFAULT 'Other / Unclassified',
    classification_method TEXT DEFAULT 'deterministic',
    classification_reason TEXT,
    confidence REAL DEFAULT 1.0,
    original_path TEXT,
    current_path TEXT,
    status TEXT DEFAULT 'Detected', -- Detected, Pending Approval, Organized, Skipped, Duplicate, Failed, Restored
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(email_id) REFERENCES emails(id) ON DELETE CASCADE
);

-- Table: filing_rules
CREATE TABLE IF NOT EXISTS filing_rules (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_name TEXT NOT NULL,
    conditions_json TEXT NOT NULL,
    destination TEXT NOT NULL,
    filename_template TEXT DEFAULT '{original_filename}',
    priority INTEGER NOT NULL DEFAULT 10,
    enabled INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table: operations
CREATE TABLE IF NOT EXISTS operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attachment_id INTEGER NOT NULL,
    operation_type TEXT NOT NULL, -- Extract, Classify, Organize, Skip, Duplicate-Ref, Undo
    source_path TEXT,
    destination_path TEXT,
    previous_filename TEXT,
    final_filename TEXT,
    status TEXT NOT NULL, -- Detected, Pending Approval, Organized, Skipped, Duplicate, Failed, Restored
    error_message TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(attachment_id) REFERENCES attachments(id) ON DELETE CASCADE
);

-- Table: classification_feedback
CREATE TABLE IF NOT EXISTS classification_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attachment_id INTEGER NOT NULL,
    predicted_category TEXT NOT NULL,
    corrected_category TEXT NOT NULL,
    feedback_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(attachment_id) REFERENCES attachments(id) ON DELETE CASCADE
);

-- Table: sync_history
CREATE TABLE IF NOT EXISTS sync_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    account_id INTEGER,
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    messages_scanned INTEGER DEFAULT 0,
    attachments_detected INTEGER DEFAULT 0,
    status TEXT DEFAULT 'Running', -- Running, Completed, Failed
    error_message TEXT,
    FOREIGN KEY(account_id) REFERENCES email_accounts(id) ON DELETE SET NULL
);

-- Schema metadata table
CREATE TABLE IF NOT EXISTS schema_meta (
    key TEXT PRIMARY KEY,
    value TEXT
);

-- Performance indices
CREATE INDEX IF NOT EXISTS idx_attachments_sha256 ON attachments(sha256);
CREATE INDEX IF NOT EXISTS idx_attachments_category ON attachments(category);
CREATE INDEX IF NOT EXISTS idx_attachments_status ON attachments(status);
CREATE INDEX IF NOT EXISTS idx_emails_sender_email ON emails(sender_email);
CREATE INDEX IF NOT EXISTS idx_operations_attachment_id ON operations(attachment_id);
CREATE INDEX IF NOT EXISTS idx_operations_status ON operations(status);
CREATE INDEX IF NOT EXISTS idx_filing_rules_priority ON filing_rules(priority ASC);
"""

DEFAULT_RULES = [
    {
        "rule_name": "Invoices to Finance",
        "conditions_json": '{"logic": "AND", "rules": [{"field": "category", "operator": "equals", "value": "Invoices"}]}',
        "destination": "Finance/Invoices",
        "filename_template": "{date}_{category}_{original_filename}",
        "priority": 1,
        "enabled": 1,
    },
    {
        "rule_name": "Receipts to Expenses",
        "conditions_json": '{"logic": "AND", "rules": [{"field": "category", "operator": "equals", "value": "Receipts"}]}',
        "destination": "Finance/Receipts",
        "filename_template": "{date}_{original_filename}",
        "priority": 2,
        "enabled": 1,
    },
    {
        "rule_name": "Resumes to HR Pipeline",
        "conditions_json": '{"logic": "AND", "rules": [{"field": "category", "operator": "equals", "value": "Resumes / CVs"}]}',
        "destination": "HR/Resumes",
        "filename_template": "{sender}_{date}_{original_filename}",
        "priority": 3,
        "enabled": 1,
    },
    {
        "rule_name": "Spreadsheet Datasets",
        "conditions_json": '{"logic": "AND", "rules": [{"field": "category", "operator": "equals", "value": "Spreadsheets"}]}',
        "destination": "Documents/Spreadsheets",
        "filename_template": "{date}_{original_filename}",
        "priority": 4,
        "enabled": 1,
    },
    {
        "rule_name": "Presentations & Decks",
        "conditions_json": '{"logic": "AND", "rules": [{"field": "category", "operator": "equals", "value": "Presentations"}]}',
        "destination": "Documents/Presentations",
        "filename_template": "{subject}_{original_filename}",
        "priority": 5,
        "enabled": 1,
    },
    {
        "rule_name": "Corporate Reports",
        "conditions_json": '{"logic": "AND", "rules": [{"field": "category", "operator": "equals", "value": "Reports"}]}',
        "destination": "Reports",
        "filename_template": "{date}_{original_filename}",
        "priority": 6,
        "enabled": 1,
    },
    {
        "rule_name": "Code and Scripts",
        "conditions_json": '{"logic": "AND", "rules": [{"field": "category", "operator": "equals", "value": "Code / Technical Files"}]}',
        "destination": "Technical/Code",
        "filename_template": "{original_filename}",
        "priority": 7,
        "enabled": 1,
    },
    {
        "rule_name": "Media Images",
        "conditions_json": '{"logic": "AND", "rules": [{"field": "category", "operator": "equals", "value": "Images"}]}',
        "destination": "Media/Images",
        "filename_template": "{date}_{original_filename}",
        "priority": 8,
        "enabled": 1,
    },
    {
        "rule_name": "Compressed Archives",
        "conditions_json": '{"logic": "AND", "rules": [{"field": "category", "operator": "equals", "value": "Archives"}]}',
        "destination": "Archives",
        "filename_template": "{date}_{original_filename}",
        "priority": 9,
        "enabled": 1,
    },
]
