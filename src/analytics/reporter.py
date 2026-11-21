"""
ATTACHORA Analytics & Reporting Engine
Calculates operational KPIs, category frequencies, storage savings, and exportable CSVs
directly from SQLite database records.
"""

from io import StringIO
from typing import Any, Dict, List
import pandas as pd
from src.database.db_manager import DatabaseManager


class AnalyticsReporter:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_summary_metrics(self) -> Dict[str, Any]:
        """Calculates core operational KPIs strictly from live database records."""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()

            # Total detected
            cursor.execute("SELECT COUNT(*) FROM attachments")
            total_detected = cursor.fetchone()[0]

            # Total organized
            cursor.execute("SELECT COUNT(*), COALESCE(SUM(file_size), 0) FROM attachments WHERE status = 'Organized'")
            org_row = cursor.fetchone()
            total_organized = org_row[0]
            total_storage_organized = org_row[1]

            # Awaiting approval
            cursor.execute("SELECT COUNT(*) FROM attachments WHERE status IN ('Pending Approval', 'Detected')")
            awaiting_approval = cursor.fetchone()[0]

            # Duplicates detected / skipped
            cursor.execute("SELECT COUNT(*), COALESCE(SUM(file_size), 0) FROM attachments WHERE status IN ('Duplicate', 'Skipped')")
            dup_row = cursor.fetchone()
            duplicates_count = dup_row[0]
            storage_saved = dup_row[1]

            # Failed operations
            cursor.execute("SELECT COUNT(*) FROM operations WHERE status = 'Failed'")
            failed_count = cursor.fetchone()[0]

            # Restored operations
            cursor.execute("SELECT COUNT(*) FROM operations WHERE status = 'Restored'")
            restored_count = cursor.fetchone()[0]

        return {
            "total_detected": total_detected,
            "total_organized": total_organized,
            "awaiting_approval": awaiting_approval,
            "duplicates_count": duplicates_count,
            "failed_count": failed_count,
            "restored_count": restored_count,
            "total_storage_organized_bytes": total_storage_organized,
            "total_storage_organized_mb": round(total_storage_organized / (1024 * 1024), 2),
            "storage_saved_bytes": storage_saved,
            "storage_saved_mb": round(storage_saved / (1024 * 1024), 2),
        }

    def get_category_distribution(self) -> pd.DataFrame:
        """Returns frequency of attachments by category."""
        with self.db.get_connection() as conn:
            query = """
                SELECT category, COUNT(*) as count, COALESCE(SUM(file_size), 0) as total_bytes
                FROM attachments
                GROUP BY category
                ORDER BY count DESC
            """
            df = pd.read_sql_query(query, conn)
            if df.empty:
                return pd.DataFrame(columns=["category", "count", "total_bytes"])
            df["total_mb"] = (df["total_bytes"] / (1024 * 1024)).round(2)
            return df

    def get_top_senders(self, limit: int = 10) -> pd.DataFrame:
        """Returns top email senders by attachment volume."""
        with self.db.get_connection() as conn:
            query = """
                SELECT e.sender_email, e.sender, COUNT(a.id) as attachment_count, COALESCE(SUM(a.file_size), 0) as total_bytes
                FROM emails e
                JOIN attachments a ON e.id = a.email_id
                GROUP BY e.sender_email
                ORDER BY attachment_count DESC
                LIMIT ?
            """
            df = pd.read_sql_query(query, conn, params=(limit,))
            if df.empty:
                return pd.DataFrame(columns=["sender_email", "sender", "attachment_count", "total_bytes"])
            df["total_mb"] = (df["total_bytes"] / (1024 * 1024)).round(2)
            return df

    def get_processing_timeline(self) -> pd.DataFrame:
        """Returns daily attachment counts over time."""
        with self.db.get_connection() as conn:
            query = """
                SELECT SUBSTR(created_at, 1, 10) as processing_date, COUNT(*) as count
                FROM attachments
                GROUP BY processing_date
                ORDER BY processing_date ASC
            """
            df = pd.read_sql_query(query, conn)
            return df

    def export_operations_csv(self) -> str:
        """Generates CSV text representation of all operations for export."""
        with self.db.get_connection() as conn:
            query = """
                SELECT o.id as operation_id, o.timestamp, o.operation_type, o.status,
                       a.original_filename, o.final_filename, o.source_path, o.destination_path,
                       a.category, a.file_size, a.sha256, e.sender_email, e.subject, o.error_message
                FROM operations o
                JOIN attachments a ON o.attachment_id = a.id
                JOIN emails e ON a.email_id = e.id
                ORDER BY o.id DESC
            """
            df = pd.read_sql_query(query, conn)
            buf = StringIO()
            df.to_csv(buf, index=False)
            return buf.getvalue()


# Singleton analytics reporter
REPORTER = AnalyticsReporter(db=DatabaseManager())
