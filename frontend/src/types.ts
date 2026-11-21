export interface RuleMatch {
  rule_id: number;
  rule_name: string;
  destination: string;
  proposed_filename: string;
  priority: number;
  reason: string;
}

export interface Attachment {
  id: number;
  email_id: number;
  original_filename: string;
  stored_filename: string;
  mime_type: string;
  extension: string;
  file_size: number;
  sha256: string;
  category: string;
  classification_method: string;
  classification_reason: string;
  confidence: number;
  original_path: string;
  current_path: string;
  status: string;
  created_at: string;
  sender: string;
  sender_email: string;
  subject: string;
  received_at: string;
  mailbox_name: string;
  rule_match: RuleMatch;
  duplicate_status: string;
}

export interface SummaryMetrics {
  awaiting_review: number;
  ready_to_file: number;
  duplicates_count: number;
  need_attention: number;
  total_detected: number;
  total_organized: number;
  storage_organized_mb: number;
  storage_saved_mb: number;
  last_scan: string;
}

export interface FilingRule {
  id: number;
  rule_name: string;
  conditions_json: string;
  destination: string;
  filename_template: string;
  priority: number;
  enabled: number;
}

export interface OperationRecord {
  id: number;
  attachment_id: number;
  operation_type: string;
  source_path: string;
  destination_path: string;
  previous_filename: string;
  final_filename: string;
  status: string;
  error_message: string;
  timestamp: string;
  original_filename: string;
  category: string;
  sender: string;
  sender_email: string;
  sha256: string;
}
