# NetSage AI — Frontend (React + TypeScript + Tailwind CSS)

> **NetSage AI**: AI-assisted Cisco network troubleshooting dashboard with evidence-grounded reasoning, deterministic rule verification (L1–L7), and mandatory Human-in-the-Loop authorization.

---

## 🚀 Quick Start (Onboard in < 2 Minutes)

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm run dev

# 4. Open in browser
http://localhost:5173
```

To validate TypeScript and build the production bundle:
```bash
npm run build
```

---

## 🧱 Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Framework** | React 19 + TypeScript | UI component architecture & strict type safety |
| **Bundler** | Vite 6 | Fast HMR & optimized production bundling |
| **Styling** | Tailwind CSS + Vanilla CSS Tokens | Curated dark glassmorphism design system |
| **Data Viz** | Recharts | Live category, severity, and bandwidth charts |
| **Animations** | Framer Motion | Fluid route transitions and toast interactions |
| **Icons** | Lucide React | Clean, scalable system iconography |
| **Routing** | React Router v7 | Client-side routing with route-level lazy loading |

---

## 📁 Architecture & Directory Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/              # Reusable UI primitives
│   │   │   ├── AmbientBackground.tsx    # 3-point ambient blur glow
│   │   │   ├── CircularScoreGauge.tsx   # SVG viability ring gauge
│   │   │   ├── CommandPalette.tsx       # Cmd/Ctrl+K fuzzy search modal
│   │   │   ├── ConfidenceMeter.tsx      # Stepped progress indicator
│   │   │   ├── ErrorBoundary.tsx        # Glass-styled error boundary
│   │   │   ├── GlassWrappers.tsx        # GlassPanel, GlassCard, GlassDeep
│   │   │   ├── GlowCard.tsx             # Dynamic mouse-tracking radial glow
│   │   │   ├── RuleResultCard.tsx       # L1-L7 rule evaluation cards
│   │   │   ├── SkeletonLoader.tsx       # Dark glass loading shimmer
│   │   │   ├── StatusBadge.tsx          # WCAG AA status badges
│   │   │   └── TerminalWindow.tsx       # Cisco IOS terminal console
│   │   └── layout/              # App layout & chrome
│   │       ├── AppFooter.tsx            # Live status & telemetry pills
│   │       ├── AppLayout.tsx            # Root layout + skip links + landmarks
│   │       ├── SideNavBar.tsx           # Collapsible sidebar navigation
│   │       └── TopAppBar.tsx            # Breadcrumb switcher & search
│   ├── context/
│   │   ├── CaseContext.tsx      # Global case state machine & demo reset
│   │   └── ToastContext.tsx     # Accessible live-region notifications
│   ├── hooks/
│   │   ├── useCase.ts           # Single case data & transition actions
│   │   ├── useCases.ts          # 35 cases list, filtering, CSV export, error retry
│   │   ├── useGlowEffect.ts     # Mouse reflection hook
│   │   └── useReviewFlow.ts     # Human-in-the-loop review & fix staging
│   ├── pages/                   # Lazy-loaded views
│   │   ├── AIWorkbench.tsx      # Reference diagnostic terminal (Hero CASE-004)
│   │   ├── AuditLogPage.tsx     # Compliance & event timeline
│   │   ├── CaseList.tsx         # 35 incidents explorer with CSV export
│   │   ├── Dashboard.tsx        # KPI metrics & live Recharts charts
│   │   ├── NetworkMapPage.tsx   # Interactive Packet Tracer topology graph
│   │   ├── NotFoundPage.tsx     # 404 handler
│   │   ├── ResponsibleAI.tsx    # Mismatch ledger & safety guardrails
│   │   ├── SupportPage.tsx      # Cisco CCNA command cheatsheet & docs
│   │   ├── SystemHealthPage.tsx # Engine latency & demo reset controller
│   │   ├── TrafficAnalysisPage.tsx # Bandwidth & packet drop inspection
│   │   └── VerificationPage.tsx # Live automated probe verification suite
│   ├── services/
│   │   ├── api.ts               # Isolated API interface & mock persistence
│   │   └── cases_data.json      # 35 seed Cisco lab cases
│   ├── styles/
│   │   └── tokens.css           # Design tokens, glass classes & typography scale
│   ├── types/
│   │   └── index.ts             # TypeScript domain models & state definitions
│   ├── App.tsx                  # App router with Suspense & lazy loading
│   └── main.tsx                 # Root DOM mount
├── tailwind.config.ts           # Color tokens & glow shadows
└── vite.config.ts               # Bundler configuration
```

---

## 🎨 Design System Tokens

The application follows a curated, high-contrast dark aesthetic:
- **Style Definitions**: [src/styles/tokens.css](./src/styles/tokens.css) & [tailwind.config.ts](./tailwind.config.ts)
- **Palette**:
  - `primary`: `#ffb59a` | `primary-container`: `#ff7a33` | `inverse-primary`: `#a73a00`
  - `secondary`: `#a5e7ff` | `tertiary`: `#4edea3` | `error`: `#ffb4ab`
  - `background` & `surface`: `#111317` | `surface-container`: `#1e2023`
- **Glass Surfaces**:
  - `.glass-panel`: rgba(30, 32, 35, 0.75) with 12px blur & 1px white/8% border
  - `.glass-card`: rgba(26, 28, 32, 0.65) with 10px blur
  - `.glass-deep`: rgba(17, 19, 23, 0.88) with 16px blur
  - `.glass-terminal`: rgba(10, 12, 16, 0.94) monospace container with traffic lights
- **Typography Scale**:
  - `Inter` for UI: `display-lg` (32px/700), `headline-md` (20px/600), `body-sm` (13px/400), `label-caps` (11px/700/uppercase)
  - `JetBrains Mono` for telemetry: `data-mono` (12px/400), `data-mono-bold` (12px/700)

---

## 🛡️ Core Human-in-the-Loop Troubleshooting Flow

```
Telemetry Stream (35 Seed Cases)
           │
           ▼
    Deterministic Rule Engine (11 L1-L7 Checks)
           │
           ▼
    AI Evidence Grounding (Root Cause + Citations)
           │
           ▼
 [ MANDATORY HUMAN GATEWAY ] ◄── Stops Autonomous Execution
           │
 ┌─────────┴─────────┐
 │ Accept / Edit / Reject
 └─────────┬─────────┘
           │
           ▼
 Staged Remediation Fix Plan
           │
           ▼
 Live Automated Probes (Ping Matrix & Protocol Checks)
           │
           ▼
 Verified & Resolved (Logged in Audit Ledger)
```

---

## 🔍 Key Judge-Facing Features

1. **Command Palette (`⌘K` / `Ctrl+K`)**: Instant fuzzy search across all 35 cases, routes, and diagnostic actions.
2. **Export to CSV**: One-click download from the Case Explorer generating `cases.csv` matching the assignment deliverable schema.
3. **Hero Case Conflict Detection**: Open `CASE-004` on the AI Workbench to observe real-time conflict handling between Rule Engine and AI reasoning.
4. **Resilience Testing**: Click "Simulate API Error" on Case Explorer to view graceful 503 error boundary handling and retry recovery.
5. **One-Click Demo Reset**: Reset all cases, reviews, and test runs to initial baseline from the sidebar or settings page.
