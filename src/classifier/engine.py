"""
ATTACHORA Unified Classification Engine
Coordinates deterministic rules, MIME type inspection, and lightweight local ML fallback.
"""

from pathlib import Path
from typing import Any, Dict, Optional
from src.classifier.ml_classifier import ML_CLASSIFIER
from src.classifier.rules_classifier import classify_by_rules
from src.security.validator import guess_mime_and_extension


class ClassificationEngine:
    def __init__(self):
        self.ml_classifier = ML_CLASSIFIER

    def classify_attachment(
        self,
        filename: str,
        mime_type: Optional[str] = None,
        subject: Optional[str] = None,
        header_bytes: Optional[bytes] = None,
    ) -> Dict[str, Any]:
        """Classifies an attachment using deterministic rules first, followed by ML fallback."""
        guessed_mime, ext = guess_mime_and_extension(filename, header_bytes)
        effective_mime = mime_type if (mime_type and "/" in mime_type) else guessed_mime

        # 1. Deterministic Rule Matching
        rule_category, rule_reason, rule_confidence = classify_by_rules(
            filename=filename,
            mime_type=effective_mime,
            subject=subject,
        )

        # If deterministic rules found a specific category (not Other/Unclassified)
        if rule_category and rule_category != "Other / Unclassified":
            return {
                "category": rule_category,
                "classification_method": "Deterministic Rules",
                "classification_reason": rule_reason,
                "confidence": rule_confidence,
                "mime_type": effective_mime,
                "extension": ext,
                "file_type": ext.upper() if ext else "UNKNOWN",
            }

        # 2. Local ML Fallback for Ambiguous / Unclassified Files
        ml_category, ml_conf = self.ml_classifier.predict(
            filename=filename,
            mime_type=effective_mime,
            subject=subject,
        )

        if ml_conf >= 0.55 and ml_category != "Other / Unclassified":
            return {
                "category": ml_category,
                "classification_method": "Local ML (TF-IDF + Naive Bayes)",
                "classification_reason": f"Predicted via local token model with {ml_conf*100:.1f}% confidence",
                "confidence": ml_conf,
                "mime_type": effective_mime,
                "extension": ext,
                "file_type": ext.upper() if ext else "UNKNOWN",
            }

        # Default back to Other / Unclassified
        return {
            "category": "Other / Unclassified",
            "classification_method": "Deterministic Rules",
            "classification_reason": rule_reason or "No matching rule pattern or high-confidence ML classification",
            "confidence": 0.50,
            "mime_type": effective_mime,
            "extension": ext,
            "file_type": ext.upper() if ext else "UNKNOWN",
        }


# Singleton engine instance
CLASSIFIER = ClassificationEngine()
