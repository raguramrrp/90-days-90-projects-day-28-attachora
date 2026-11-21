"""
ATTACHORA Lightweight Local Machine Learning Classifier
Uses TF-IDF feature extraction with Multinomial Naive Bayes trained on filename
tokens, MIME types, and feedback logs. Free, local, and retrainable.
"""

from typing import Dict, List, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

# Baseline realistic training corpus
BASELINE_SAMPLES = [
    # Invoices
    ("invoice_2026_vendor_payment.pdf", "application/pdf", "Invoices"),
    ("tax_invoice_acme_corp_nov.pdf", "application/pdf", "Invoices"),
    ("billing_statement_aws_cloud.pdf", "application/pdf", "Invoices"),
    ("proforma_invoice_goods.pdf", "application/pdf", "Invoices"),
    ("inv_84920_electronics.pdf", "application/pdf", "Invoices"),
    # Receipts
    ("uber_trip_receipt_san_francisco.pdf", "application/pdf", "Receipts"),
    ("hotel_stay_folio_receipt.jpg", "image/jpeg", "Receipts"),
    ("starbucks_coffee_receipt_expense.png", "image/png", "Receipts"),
    ("hardware_store_receipt.pdf", "application/pdf", "Receipts"),
    ("payment_receipt_stripe_charge.pdf", "application/pdf", "Receipts"),
    # Resumes / CVs
    ("ragu_ram_ai_engineer_resume.pdf", "application/pdf", "Resumes / CVs"),
    ("john_doe_curriculum_vitae_2026.docx", "application/vnd.openxmlformats", "Resumes / CVs"),
    ("software_developer_cv_updated.pdf", "application/pdf", "Resumes / CVs"),
    ("candidate_resume_data_analyst.pdf", "application/pdf", "Resumes / CVs"),
    ("biodata_academic_application.docx", "application/vnd.openxmlformats", "Resumes / CVs"),
    # Reports
    ("annual_sustainability_report_2026.pdf", "application/pdf", "Reports"),
    ("quarterly_sales_performance_report_q3.pdf", "application/pdf", "Reports"),
    ("market_research_findings_summary.pdf", "application/pdf", "Reports"),
    ("cybersecurity_audit_report.pdf", "application/pdf", "Reports"),
    # Spreadsheets
    ("financial_model_projection.xlsx", "application/vnd.openxmlformats", "Spreadsheets"),
    ("ecommerce_order_items.csv", "text/csv", "Spreadsheets"),
    ("customer_churn_dataset.csv", "text/csv", "Spreadsheets"),
    ("budget_allocation_2027.xlsx", "application/vnd.openxmlformats", "Spreadsheets"),
    # Presentations
    ("investor_pitch_deck_series_a.pptx", "application/vnd.openxmlformats", "Presentations"),
    ("product_launch_roadmap.pptx", "application/vnd.openxmlformats", "Presentations"),
    ("keynote_tech_symposium.pptx", "application/vnd.openxmlformats", "Presentations"),
    # Code / Technical Files
    ("main_api_server.py", "text/x-python", "Code / Technical Files"),
    ("database_schema_migration.sql", "application/sql", "Code / Technical Files"),
    ("docker_compose_config.yml", "text/yaml", "Code / Technical Files"),
    ("frontend_app_bundle.js", "application/javascript", "Code / Technical Files"),
    # Archives
    ("backup_logs_nov_2026.zip", "application/zip", "Archives"),
    ("dataset_raw_images.tar.gz", "application/gzip", "Archives"),
    ("source_code_archive.zip", "application/zip", "Archives"),
    # Images
    ("company_logo_vector_highres.png", "image/png", "Images"),
    ("architecture_diagram_v2.jpg", "image/jpeg", "Images"),
    ("profile_avatar_thumbnail.png", "image/png", "Images"),
]


class LocalMLClassifier:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2), token_pattern=r"(?u)\b\w+\b")
        self.classifier = MultinomialNB(alpha=0.5)
        self.is_trained = False
        self._train_baseline()

    def _prepare_text(self, filename: str, mime_type: str, subject: Optional[str] = None) -> str:
        clean_name = filename.replace("_", " ").replace("-", " ").replace(".", " ")
        clean_mime = (mime_type or "").replace("/", " ").replace("-", " ")
        clean_subj = (subject or "").replace("_", " ").replace("-", " ")
        return f"{clean_name} {clean_mime} {clean_subj}".lower()

    def _train_baseline(self) -> None:
        texts = [self._prepare_text(fn, mime) for fn, mime, _ in BASELINE_SAMPLES]
        labels = [cat for _, _, cat in BASELINE_SAMPLES]
        X = self.vectorizer.fit_transform(texts)
        self.classifier.fit(X, labels)
        self.is_trained = True

    def predict(
        self,
        filename: str,
        mime_type: Optional[str] = None,
        subject: Optional[str] = None,
    ) -> Tuple[str, float]:
        """Predicts attachment category using TF-IDF + Naive Bayes.

        Returns (category, probability_confidence)
        """
        if not self.is_trained:
            self._train_baseline()

        text = self._prepare_text(filename, mime_type or "", subject)
        X = self.vectorizer.transform([text])
        probs = self.classifier.predict_proba(X)[0]
        max_idx = probs.argmax()
        category = self.classifier.classes_[max_idx]
        confidence = float(probs[max_idx])
        return category, round(confidence, 3)

    def retrain_with_feedback(self, feedback_records: List[Dict]) -> int:
        """Incorporates user correction feedback into the model."""
        texts = [self._prepare_text(fn, mime) for fn, mime, _ in BASELINE_SAMPLES]
        labels = [cat for _, _, cat in BASELINE_SAMPLES]

        added_count = 0
        for fb in feedback_records:
            fn = fb.get("original_filename") or ""
            mime = fb.get("mime_type") or ""
            corrected = fb.get("corrected_category")
            if fn and corrected:
                texts.append(self._prepare_text(fn, mime))
                labels.append(corrected)
                added_count += 1

        if added_count > 0:
            X = self.vectorizer.fit_transform(texts)
            self.classifier.fit(X, labels)
            self.is_trained = True

        return added_count


# Singleton ML classifier instance
ML_CLASSIFIER = LocalMLClassifier()
