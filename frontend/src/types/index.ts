export type CaseState =
  | 'NEW'
  | 'EVIDENCE_COLLECTED'
  | 'ANALYZING'
  | 'DIAGNOSIS_READY'
  | 'REVIEW_REQUIRED'
  | 'ACCEPTED'
  | 'EDITED'
  | 'REJECTED'
  | 'FIX_APPROVED'
  | 'VERIFICATION'
  | 'RESOLVED'
  | 'FAILED';

export type Severity = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';

export type FusionStatus = 'AGREEMENT' | 'CONFLICT';

export type StatusType = 'PASS' | 'FAIL' | 'WARNING' | 'CRITICAL' | 'UNKNOWN' | 'PENDING';

export interface Device {
  name: string;
  ip?: string;
  mask?: string;
  gateway?: string;
  vlan?: number | string;
  status?: string;
}

export interface EvidenceCitation {
  id: string;
  source_command: string;
  snippet: string;
  line_numbers?: string;
  significance: string;
}

export interface Diagnosis {
  root_cause: string;
  confidence: number; // 0 - 100
  osi_layer: string;
  viability_score: number; // 0 - 100
  explanation: string;
  citations: EvidenceCitation[];
  recommended_fix: string[];
  next_command: string;
}

export interface RuleResult {
  id: string;
  name: string;
  status: 'PASS' | 'FAIL' | 'WARNING';
  layer: string;
  expected?: string;
  actual?: string;
  note?: string;
}

export interface ReviewDecision {
  decision: 'ACCEPTED' | 'EDITED' | 'REJECTED';
  reviewer: string;
  timestamp: string;
  notes: string;
  edited_fix?: string[];
  edited_root_cause?: string;
}

export interface VerificationCheck {
  id: string;
  description: string;
  target_device: string;
  command: string;
  status: 'PENDING' | 'RUNNING' | 'PASS' | 'FAIL';
  output_snippet?: string;
}

export interface VerificationResult {
  completed_at: string;
  checks: VerificationCheck[];
  all_passed: boolean;
  notes?: string;
}

export interface Case {
  case_id: string;
  category: string;
  title: string;
  symptom: string;
  topology: string;
  show_outputs: Record<string, string>;
  expected_fault: string;
  expected_osi_layer: string;
  osi_layer: string; // Layer 1, Layer 2, Layer 3, etc.
  concept: string; // e.g. "Interface Status", "VLAN Trunking"
  severity: Severity;
  expected_fix: string[];
  next_command: string;
  tags: string[];
  devices?: Device[];
  status: CaseState;
  fusion_status: FusionStatus;
  ai_diagnosis: Diagnosis;
  rule_results: RuleResult[];
  review?: ReviewDecision;
  verification?: VerificationResult;
  created_at: string;
  updated_at: string;
}

export interface AuditLogEntry {
  id: string;
  timestamp: string;
  case_id?: string;
  action_type:
    | 'CASE_CREATED'
    | 'EVIDENCE_COLLECTED'
    | 'DIAGNOSIS_GENERATED'
    | 'RULE_ENGINE_EVALUATED'
    | 'REVIEW_STARTED'
    | 'REVIEW_DECISION_RECORDED'
    | 'FIX_PLAN_APPROVED'
    | 'VERIFICATION_EXECUTED'
    | 'CASE_RESOLVED'
    | 'SYSTEM_SYNC';
  actor: string;
  details: string;
  status: 'SUCCESS' | 'WARNING' | 'FAILURE' | 'INFO';
}

export interface ResponsibleAIMismatch {
  id: string;
  case_id: string;
  title: string;
  ai_root_cause: string;
  human_decision: 'EDITED' | 'REJECTED';
  human_root_cause: string;
  correction_reason: string;
  osi_layer: string;
  confidence: number;
  timestamp: string;
}

export interface SystemHealthMetric {
  name: string;
  value: string | number;
  status: 'OPERATIONAL' | 'DEGRADED' | 'OFFLINE';
  latencyMs?: number;
  lastChecked: string;
}
