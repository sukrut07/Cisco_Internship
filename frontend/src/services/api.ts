import {
  Case,
  AuditLogEntry,
  ResponsibleAIMismatch,
  SystemHealthMetric,
  ReviewDecision,
  VerificationResult
} from '../types';
import rawCases from './cases_data.json';

// Rich hero case details for CASE-004
const HERO_CASE_004: Case = {
  case_id: 'CASE-004',
  category: 'IP_ADDRESSING',
  title: 'Interface Administratively Shut Down',
  symptom: 'PC1 cannot communicate with any device. The switch port connected to R1 Gi0/1 shows no link. The uplink between SW1 and R1 is suspected to be down.',
  topology: 'PC1 (192.168.1.10/24) -> SW1 (Fa0/1, Gi0/1) -> R1 (Gi0/1 shutdown) -> Server1 (10.0.0.100/24)',
  show_outputs: {
    'show ip interface brief':
`Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0    192.168.1.1     YES manual up                    up
GigabitEthernet0/1    10.0.0.1        YES manual administratively down down`,
    'show interfaces GigabitEthernet0/1':
`GigabitEthernet0/1 is administratively down, line protocol is down 
  Hardware is CN Gigabit Ethernet, address is 0019.5678.9abc
  Internet address is 10.0.0.1/30
  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec,
     reliability 255/255, txload 1/255, rxload 1/255
  Encapsulation ARPA, loopback not set
  Keepalive set (10 sec)
  Full-duplex, 1000Mb/s, media type is RJ45
  output flow-control is unsupported, input flow-control is unsupported
  ARP type: ARPA, ARP Timeout 04:00:00
  Last input never, output 00:00:03, output clear never
  Last clearing of "show interface" counters never
  Input queue: 0/75/0/0 (size/max/drops/flushes); Total output drops: 0`
  },
  expected_fault: 'Interface GigabitEthernet0/1 is administratively shut down',
  expected_osi_layer: 'Layer 1',
  osi_layer: 'Layer 1',
  concept: 'Interface Status',
  severity: 'CRITICAL',
  expected_fix: [
    'Enter configuration mode on R1 (conf t)',
    'Select target interface: interface GigabitEthernet0/1',
    'Enable interface: no shutdown',
    'Verify status: show ip interface brief | include GigabitEthernet0/1',
    'Send verification ICMP echo from PC1 to Server1 (ping 10.0.0.100)'
  ],
  next_command: 'show ip interface brief',
  tags: ['interface', 'shutdown', 'physical', 'layer1', 'cisco-ios'],
  devices: [
    { name: 'PC1', ip: '192.168.1.10', mask: '255.255.255.0', gateway: '192.168.1.1' },
    { name: 'SW1', status: 'Active Layer 2 Switch' },
    { name: 'R1', ip: '192.168.1.1 / 10.0.0.1', status: 'Gi0/1 Admin Down' },
    { name: 'Server1', ip: '10.0.0.100', mask: '255.255.255.0' }
  ],
  status: 'REVIEW_REQUIRED',
  fusion_status: 'CONFLICT', // AI vs Rule Engine nuance on Layer 1 vs 3
  ai_diagnosis: {
    root_cause: 'Interface GigabitEthernet0/1 on Core Router R1 is manually disabled (administratively down), severing the physical uplink to Server1.',
    confidence: 96,
    osi_layer: 'Layer 1 - Physical',
    viability_score: 94,
    explanation: 'Parsing `show ip interface brief` indicates `administratively down` state on Gi0/1. The line protocol is down due to explicit administrative shutdown rather than a physical cable fault. Enabling the interface via `no shutdown` restores the circuit path.',
    citations: [
      {
        id: 'cite-001',
        source_command: 'show ip interface brief',
        snippet: 'GigabitEthernet0/1    10.0.0.1        YES manual administratively down down',
        line_numbers: 'Line 3',
        significance: 'Direct proof of administrative disablement flag on R1 uplink interface'
      },
      {
        id: 'cite-002',
        source_command: 'show interfaces GigabitEthernet0/1',
        snippet: 'GigabitEthernet0/1 is administratively down, line protocol is down',
        line_numbers: 'Line 1',
        significance: 'Line protocol state confirms interface disabled at hardware management tier'
      }
    ],
    recommended_fix: [
      'configure terminal',
      'interface GigabitEthernet0/1',
      'no shutdown',
      'end',
      'write memory'
    ],
    next_command: 'show ip interface brief'
  },
  rule_results: [
    {
      id: 'rule-01',
      name: 'check_interface_admin_status',
      status: 'FAIL',
      layer: 'Layer 1',
      expected: 'Status: up',
      actual: 'Status: administratively down',
      note: 'Triggered deterministic alert: R1 Gi0/1 is shut down.'
    },
    {
      id: 'rule-02',
      name: 'check_line_protocol_status',
      status: 'FAIL',
      layer: 'Layer 2',
      expected: 'Protocol: up',
      actual: 'Protocol: down',
      note: 'Protocol down cascading from admin shutdown state.'
    },
    {
      id: 'rule-03',
      name: 'check_ip_assignment',
      status: 'PASS',
      layer: 'Layer 3',
      expected: 'Valid IP assigned',
      actual: '10.0.0.1/30 assigned',
      note: 'IP configuration valid.'
    },
    {
      id: 'rule-04',
      name: 'check_duplex_speed_mismatch',
      status: 'PASS',
      layer: 'Layer 1',
      expected: 'Full-duplex, 1000Mb/s',
      actual: 'Full-duplex, 1000Mb/s',
      note: 'No duplex or speed negotiation anomalies.'
    }
  ],
  created_at: '2026-08-30T10:14:00Z',
  updated_at: '2026-08-30T10:14:00Z'
};

// Combine all 35 cases with HERO_CASE_004 prioritized
export const INITIAL_MOCK_CASES: Case[] = ((rawCases as unknown) as Case[]).map((c: Case) => {
  if (c.case_id === 'CASE-004') return HERO_CASE_004;
  return c;
});

export const INITIAL_AUDIT_LOGS: AuditLogEntry[] = [
  {
    id: 'aud-001',
    timestamp: '2026-08-30T10:14:02Z',
    case_id: 'CASE-004',
    action_type: 'CASE_CREATED',
    actor: 'Lab Engine / Packet Tracer Gateway',
    details: 'Received diagnostic telemetry for R1 & SW1 topology',
    status: 'INFO'
  },
  {
    id: 'aud-002',
    timestamp: '2026-08-30T10:14:04Z',
    case_id: 'CASE-004',
    action_type: 'RULE_ENGINE_EVALUATED',
    actor: 'NetSage RuleEngine v2.4',
    details: 'Evaluated 4 Layer 1-3 deterministic rules; 2 FAIL, 2 PASS',
    status: 'WARNING'
  },
  {
    id: 'aud-003',
    timestamp: '2026-08-30T10:14:07Z',
    case_id: 'CASE-004',
    action_type: 'DIAGNOSIS_GENERATED',
    actor: 'NetSage AI (DeepSeek / Gemini Grounded)',
    details: 'Generated root cause with 96% confidence and 2 verified citations',
    status: 'SUCCESS'
  },
  {
    id: 'aud-004',
    timestamp: '2026-08-30T10:14:08Z',
    case_id: 'CASE-004',
    action_type: 'REVIEW_STARTED',
    actor: 'System Policy Router',
    details: 'Mandatory Human-in-the-Loop Gateway triggered. Execution halted.',
    status: 'INFO'
  }
];

export const INITIAL_RESPONSIBLE_AI_MISMATCHES: ResponsibleAIMismatch[] = [
  {
    id: 'mismatch-01',
    case_id: 'CASE-003',
    title: 'Duplicate IP vs Stale ARP Entry',
    ai_root_cause: 'AI diagnosed physical switch port flapping',
    human_decision: 'EDITED',
    human_root_cause: 'Static IP collision between PC1 and rogue printer',
    correction_reason: 'AI prioritized interface flap counter over secondary ARP entry with duplicate MAC.',
    osi_layer: 'Layer 3',
    confidence: 76,
    timestamp: '2026-08-29T16:20:00Z'
  },
  {
    id: 'mismatch-02',
    case_id: 'CASE-012',
    title: 'MTU Black Hole Detection',
    ai_root_cause: 'AI suggested OSPF MTU ignore command',
    human_decision: 'REJECTED',
    human_root_cause: 'Adjusted physical tunnel MTU to 1400 instead of bypassing OSPF check',
    correction_reason: 'Bypassing OSPF MTU check would lead to fragmentation drops for large frames.',
    osi_layer: 'Layer 3',
    confidence: 68,
    timestamp: '2026-08-29T14:10:00Z'
  }
];

export const SYSTEM_HEALTH_METRICS: SystemHealthMetric[] = [
  {
    name: 'AI Reasoning Engine',
    value: 'Operational (Gemini / Anthropic / Mock)',
    status: 'OPERATIONAL',
    latencyMs: 380,
    lastChecked: 'Just now'
  },
  {
    name: 'Deterministic Rule Engine',
    value: '11/11 Rules Loaded & Active',
    status: 'OPERATIONAL',
    latencyMs: 12,
    lastChecked: 'Just now'
  },
  {
    name: 'Cisco CLI Parser & Lexer',
    value: 'IOS 15.x / XE / NX-OS Supported',
    status: 'OPERATIONAL',
    latencyMs: 25,
    lastChecked: 'Just now'
  },
  {
    name: 'Human Gateway Enforcement',
    value: 'Strict Mode: Auto-Execution Disabled',
    status: 'OPERATIONAL',
    lastChecked: 'Active Policy'
  }
];

// In-Memory Storage
let storedCases: Case[] = JSON.parse(JSON.stringify(INITIAL_MOCK_CASES));
let storedAuditLogs: AuditLogEntry[] = JSON.parse(JSON.stringify(INITIAL_AUDIT_LOGS));
let storedMismatches: ResponsibleAIMismatch[] = JSON.parse(JSON.stringify(INITIAL_RESPONSIBLE_AI_MISMATCHES));

let shouldSimulateApiError = false;

// Helper simulation delay
const delay = (ms: number = 300) => new Promise(resolve => setTimeout(resolve, ms));

export const api = {
  setSimulateApiError(val: boolean) {
    shouldSimulateApiError = val;
  },

  getSimulateApiError() {
    return shouldSimulateApiError;
  },

  async getCases(): Promise<Case[]> {
    await delay(350);
    if (shouldSimulateApiError) {
      throw new Error('503 Service Unavailable: Simulated Network Failure in Cisco Lab API.');
    }
    return [...storedCases];
  },

  async getCaseById(caseId: string): Promise<Case | undefined> {
    await delay(250);
    if (shouldSimulateApiError) {
      throw new Error('503 Service Unavailable: Simulated Network Failure.');
    }
    return storedCases.find(c => c.case_id.toLowerCase() === caseId.toLowerCase());
  },

  async submitReview(caseId: string, decision: ReviewDecision): Promise<Case> {
    await delay(400);
    const index = storedCases.findIndex(c => c.case_id.toLowerCase() === caseId.toLowerCase());
    if (index === -1) throw new Error(`Case ${caseId} not found`);

    const c = storedCases[index];
    c.review = decision;
    c.status = decision.decision === 'REJECTED' ? 'REJECTED' : decision.decision;
    c.updated_at = new Date().toISOString();

    // Log audit
    storedAuditLogs.unshift({
      id: `aud-${Date.now()}`,
      timestamp: new Date().toISOString(),
      case_id: c.case_id,
      action_type: 'REVIEW_DECISION_RECORDED',
      actor: decision.reviewer || 'Network Engineer (Human)',
      details: `Review decision: ${decision.decision}. Note: ${decision.notes || 'No remarks'}`,
      status: decision.decision === 'REJECTED' ? 'WARNING' : 'SUCCESS'
    });

    // If edited or rejected, add to responsible AI mismatch list
    if (decision.decision === 'EDITED' || decision.decision === 'REJECTED') {
      storedMismatches.unshift({
        id: `mismatch-${Date.now()}`,
        case_id: c.case_id,
        title: c.title,
        ai_root_cause: c.ai_diagnosis.root_cause,
        human_decision: decision.decision,
        human_root_cause: decision.edited_root_cause || c.expected_fault,
        correction_reason: decision.notes || 'Human engineer overrode AI recommendation.',
        osi_layer: c.osi_layer,
        confidence: c.ai_diagnosis.confidence,
        timestamp: new Date().toISOString()
      });
    }

    return { ...c };
  },

  async approveFix(caseId: string): Promise<Case> {
    await delay(350);
    const index = storedCases.findIndex(c => c.case_id.toLowerCase() === caseId.toLowerCase());
    if (index === -1) throw new Error(`Case ${caseId} not found`);

    const c = storedCases[index];
    c.status = 'FIX_APPROVED';
    c.updated_at = new Date().toISOString();

    storedAuditLogs.unshift({
      id: `aud-${Date.now()}`,
      timestamp: new Date().toISOString(),
      case_id: c.case_id,
      action_type: 'FIX_PLAN_APPROVED',
      actor: 'Network Operations Lead',
      details: `Approved implementation steps for ${c.case_id}. Ready for live verification.`,
      status: 'SUCCESS'
    });

    return { ...c };
  },

  async saveVerificationResult(caseId: string, result: VerificationResult): Promise<Case> {
    await delay(400);
    const index = storedCases.findIndex(c => c.case_id.toLowerCase() === caseId.toLowerCase());
    if (index === -1) throw new Error(`Case ${caseId} not found`);

    const c = storedCases[index];
    c.verification = result;
    c.status = result.all_passed ? 'RESOLVED' : 'FAILED';
    c.updated_at = new Date().toISOString();

    storedAuditLogs.unshift({
      id: `aud-${Date.now()}`,
      timestamp: new Date().toISOString(),
      case_id: c.case_id,
      action_type: result.all_passed ? 'CASE_RESOLVED' : 'VERIFICATION_EXECUTED',
      actor: 'Automated Verification Pipeline',
      details: result.all_passed
        ? `Case ${c.case_id} successfully verified and resolved.`
        : `Verification checks failed for ${c.case_id}.`,
      status: result.all_passed ? 'SUCCESS' : 'FAILURE'
    });

    return { ...c };
  },

  async getAuditLogs(): Promise<AuditLogEntry[]> {
    await delay(250);
    return [...storedAuditLogs];
  },

  async getResponsibleAIMismatches(): Promise<ResponsibleAIMismatch[]> {
    await delay(250);
    return [...storedMismatches];
  },

  async getSystemHealth(): Promise<SystemHealthMetric[]> {
    await delay(200);
    return [...SYSTEM_HEALTH_METRICS];
  },

  resetDemoState(): void {
    shouldSimulateApiError = false;
    storedCases = JSON.parse(JSON.stringify(INITIAL_MOCK_CASES));
    storedAuditLogs = JSON.parse(JSON.stringify(INITIAL_AUDIT_LOGS));
    storedMismatches = JSON.parse(JSON.stringify(INITIAL_RESPONSIBLE_AI_MISMATCHES));
  }
};
