# ToxShield — Design PRD

> **Version**: 1.0
> **Date**: 2026-03-26
> **Status**: Draft
> **Author**: Product & Design

---

## Table of Contents

1. [Product Overview](#1-product-overview)
2. [Target Users & Personas](#2-target-users--personas)
3. [Core Value Proposition](#3-core-value-proposition)
4. [Information Architecture](#4-information-architecture)
5. [Screen Inventory & Specifications](#5-screen-inventory--specifications)
6. [Design System](#6-design-system)
7. [Interaction Patterns](#7-interaction-patterns)
8. [Data Visualization](#8-data-visualization)
9. [Content & Tone](#9-content--tone)
10. [Mobile & Responsive Strategy](#10-mobile--responsive-strategy)
11. [Accessibility](#11-accessibility)
12. [Feature Roadmap & Gaps](#12-feature-roadmap--gaps)
13. [Success Metrics](#13-success-metrics)

---

## 1. Product Overview

### What is ToxShield?

ToxShield is an AI-powered forensic behavioral analyzer. Users log descriptions of people in their lives — via text, WhatsApp chats, or Slack messages — and Claude AI produces detailed threat profiles with toxicity scores, detected behavioral traits, pattern analysis, and actionable protection strategies.

### Product Personality

ToxShield walks a deliberate tightrope: **dead-serious analysis wrapped in a darkly humorous, terminal-hacker aesthetic**. It feels like a classified intelligence tool — scanlines, monospace fonts, threat levels — but the tone is witty, relatable, and occasionally savage. The result is an app people *want* to share because it feels like a meme, but *keep using* because the analysis is genuinely insightful.

### Tagline

> "Know who's toxic before they know you know."

### Key Differentiators

| Differentiator | Description |
|----------------|-------------|
| **Dual-profile analysis** | Every analysis also mirrors the user's own behavioral patterns back to them — not just the subject |
| **Incremental intelligence** | Users keep adding data to the same person over time; the toxicity score evolves up or down |
| **Multi-source input** | Text descriptions, WhatsApp chat exports, Slack message dumps — with more formats planned |
| **Viral shareability** | Threat profiles are designed to be screenshot-worthy and shareable with headline + tagline hooks |
| **Self-reflection engine** | When the subject isn't actually toxic, the app gently redirects the user to examine their own approach |

---

## 2. Target Users & Personas

### Primary Persona: "The Venter" (18-35, social media native)

- **Context**: Just had a fight with a partner, friend, or coworker. Needs to process and validate feelings.
- **Entry point**: Sees a friend share a ToxShield threat profile on Instagram/TikTok. Clicks "Try Without Signing Up."
- **Core need**: Emotional validation + actionable framing of a confusing relationship dynamic.
- **Behavior**: Analyzes 1-2 people, shares results, may or may not convert to registered user.
- **Quote**: *"I knew my ex was gaslighting me but seeing it scored at 8.2 with a threat profile hit different."*

### Secondary Persona: "The Pattern Tracker" (25-45, reflective)

- **Context**: Has multiple complex relationships (toxic parent, difficult boss, problematic friend). Wants ongoing tracking.
- **Entry point**: Signs up after trying the demo. Logs 3-5 people over weeks.
- **Core need**: A personal dashboard that quantifies and tracks the toxicity in their environment over time.
- **Behavior**: Returns weekly to add new interactions, checks Environment Health %, uses "My Mirror" for self-awareness.
- **Quote**: *"My environment health went from 34% to 67% after I set boundaries with two people. ToxShield showed me the pattern."*

### Tertiary Persona: "The Curious Sharer" (any age)

- **Context**: Sees ToxShield content on social media. Wants to try it for fun/curiosity.
- **Entry point**: `/try` page (no signup required).
- **Core need**: Entertainment + social currency (shareable result).
- **Behavior**: One-time use. May share result. Low conversion to signup unless result resonates deeply.

---

## 3. Core Value Proposition

```
INPUT:  "My boss takes credit for my work, gaslights me in meetings,
         and guilt-trips me when I push back."

OUTPUT: ┌─────────────────────────────────────────────┐
        │  THREAT PROFILE: Your Boss                  │
        │  ─────────────────────────────────────       │
        │  Toxicity: 7.8/10  ●●●●●●●●○○              │
        │  Risk Level: HIGH                            │
        │  Headline: "The Credit Vampire"              │
        │                                              │
        │  Detected Traits:                            │
        │  ● Gaslighting (critical)                    │
        │  ● Credit stealing (high)                    │
        │  ● Guilt manipulation (high)                 │
        │                                              │
        │  Protection Strategies:                      │
        │  1. Document everything in writing            │
        │  2. CC others on key communications           │
        │  3. Practice grey-rocking in meetings         │
        │                                              │
        │  YOUR MIRROR:                                │
        │  You tend to absorb blame. Your language      │
        │  shows conflict avoidance patterns...         │
        └─────────────────────────────────────────────┘
```

**The loop**: Describe -> Analyze -> Understand -> Protect -> Share -> Return with more data

---

## 4. Information Architecture

### Sitemap

```
toxshield.app
│
├── / ............................ Landing page (public)
├── /try ......................... Demo analyzer (public, rate-limited)
├── /login ....................... Email/password + Google OAuth
├── /signup ...................... Registration
├── /auth/callback ............... OAuth redirect handler
│
└── [Authenticated App Shell]
    ├── /dashboard ............... Home: stats, health %, recent people
    ├── /analyze ................. New analysis (text / WhatsApp / Slack)
    ├── /people .................. Subject list (sorted, searchable)
    │   └── /people/:id ......... Individual threat profile
    │       ├── /add-info ....... Append new data to existing person
    │       └── /share .......... Shareable card (copy link / download)
    ├── /my-insights ............. "My Mirror" — user's own patterns
    └── /settings ................ Profile info
```

### Navigation Model

**Desktop**: Fixed sidebar (left, 224px) + fixed terminal header (top)

| Nav Item | Icon | Route |
|----------|------|-------|
| Dashboard | `>` | `/dashboard` |
| New Analysis | `+` | `/analyze` |
| People | `#` | `/people` |
| My Mirror | `◈` | `/my-insights` |
| Settings | `*` | `/settings` |
| Sign Out | `<` | (action) |

**Mobile**: Bottom tab bar (5 items) + simplified top header

### User Flows

#### Flow 1: First-Time Analysis (New User)

```
Landing → Sign Up → Dashboard (empty state) → New Analysis
  → Select mode (Text/WhatsApp/Slack)
  → Enter name + relationship + description
  → [Name match check] → Submit
  → Loading state (AI processing)
  → Threat Profile result
  → [Optional: Share / Add More Info]
  → Back to Dashboard (now populated)
```

#### Flow 2: Returning User — Update Existing Person

```
Dashboard → People list → Select person
  → View latest threat profile
  → "Add Info" button
  → Enter new interaction data
  → [Contextual analysis with history]
  → Updated threat profile (score may change)
```

#### Flow 3: Try Without Signup

```
Landing → "Try Without Signing Up"
  → /try page (text input only)
  → Submit description
  → Threat Profile result (in-memory, not saved)
  → CTA: "Sign up to save and track"
```

#### Flow 4: Share a Profile

```
Person profile → Share button
  → Share card preview (headline, score, top traits)
  → Copy link / Download image
  → Recipient views shared card
```

---

## 5. Screen Inventory & Specifications

### 5.1 Landing Page (`/`)

**Purpose**: Convert visitors to signups or demo tries.

**Layout**:
- Minimal terminal header: `toxshield — v1.0.0`
- Centered hero: large "TOXSHIELD" wordmark with text glow
- Subtitle: "FORENSIC BEHAVIORAL ANALYSIS"
- Value prop paragraph (monospace, muted)
- 3-column feature grid (Threat Profiles, Track Patterns, Stay Protected)
- 3 CTAs stacked: "START ANALYZING" (primary), "LOGIN" (secondary), "TRY WITHOUT SIGNING UP" (tertiary)
- Disclaimer footer

**Key Design Decisions**:
- No images or illustrations — pure typography-driven
- Monochrome palette reinforces the terminal aesthetic
- The feature grid is the only structured content; everything else is centered text
- CTA hierarchy is clear via visual weight (filled > outlined > ghost)

**Current State**: Implemented and functional.

---

### 5.2 Auth Pages (`/login`, `/signup`)

**Purpose**: Minimal-friction authentication.

**Supported Methods**:
- Email + password
- Google OAuth (one-click)

**Layout**:
- Centered card on dark background
- App wordmark at top
- Google OAuth button (prominent)
- Divider: "or"
- Email/password form fields
- Submit button
- Toggle link: "Already have an account?" / "Don't have an account?"

**Signup Success State**:
- Confirmation message: "Check your email to verify"
- Link back to login

**Current State**: Implemented and functional.

---

### 5.3 Dashboard (`/dashboard`)

**Purpose**: At-a-glance view of user's tracked environment.

**Sections**:

1. **Stats Grid** (3 cards, horizontal):
   - Total Subjects (count of people tracked)
   - High-Risk (count where risk_level = 'high')
   - Total Analyses (sum of all analysis runs)

2. **Environment Health** (prominent visualization):
   - Percentage (0-100%) calculated from aggregate toxicity scores
   - Higher = healthier environment
   - Penalizes high-risk individuals more heavily

3. **Recent Subjects** (list):
   - Each row: name, relationship, toxicity score circle, risk badge
   - Sorted by most recently analyzed
   - Click to view full threat profile

**Empty State**: When user has no people logged yet — prompt to create first analysis.

**Current State**: Implemented and functional.

---

### 5.4 Analyze Page (`/analyze`)

**Purpose**: Primary input interface for creating new analyses.

**Mode Selector** (tab-style toggle, 3 modes):

| Mode | Icon/Label | Input Type |
|------|-----------|------------|
| DESCRIBE | Text input | Free-text description of behavior |
| WHATSAPP | Chat upload | WhatsApp export file (.txt) or pasted chat |
| SLACK | Workplace | Slack message dump or pasted messages |

#### Text Mode (DESCRIBE)

**Fields**:
- **Name** (required): Text input with live person-match checking
  - If match found: "Person Match Banner" — "Is this the same [Name]?"
  - Options: "Yes, update them" / "No, different person" (generates quirky name alternatives)
- **Relationship** (required): Dropdown (Partner, Ex-Partner, Friend, Parent, Sibling, Boss, Coworker, Roommate, Acquaintance, Other)
- **Description** (required): Large textarea — "Describe their behavior, specific incidents, how they make you feel..."

#### WhatsApp Mode

**Fields**:
- **Name** (required): Same person-match behavior
- **Relationship** (required): Same dropdown
- **Chat input**: File upload (.txt) OR paste textarea
  - Parser extracts messages, identifies participants

#### Slack Mode

**Fields**:
- **Name** (required): Same person-match behavior
- **Relationship** (required): Same dropdown
- **Messages input**: File upload OR paste textarea
  - Workplace context prompt adjusts analysis for professional norms

**Submit Flow**:
1. Validate all fields (Zod + react-hook-form)
2. Show loading spinner with "Analyzing..." state
3. POST to `/api/analyze`
4. On success: render `ThreatProfile` component inline below the form
5. On error: show error alert

**Person Deduplication Logic**:
- On name blur: `GET /api/people/search?name={value}`
- If match: show banner with existing person's details
- User confirms same person → analysis becomes contextual (pulls history)
- User says different → quirky name suggestions (e.g., "John (The One Who Ghosted)")

**Current State**: Implemented and functional.

---

### 5.5 Threat Profile (Analysis Result)

**Purpose**: The core output — the viral, shareable artifact.

**Component**: `ThreatProfile` (rendered on analyze page after submission, and on `/people/:id`)

**Sections (top to bottom)**:

1. **Header**:
   - Person name + relationship badge
   - Headline (AI-generated, e.g., "The Emotional Hostage-Taker")
   - Tagline (AI-generated, e.g., "Uses guilt as currency and silence as punishment")

2. **Toxicity Ring** (circular score visualization):
   - Score: 0.0 - 10.0 (one decimal)
   - Ring color/fill scales with score
   - Animated on first render

3. **Risk Badge**:
   - LOW (blue tones) / MODERATE (amber tones) / HIGH (red tones)
   - Pill-shaped indicator

4. **Detected Traits** (list):
   - Each trait: name + severity level + description
   - Severity: low / moderate / high / critical
   - Visual encoding via opacity and weight (monochrome system)
   - Icons per trait

5. **Pattern Analysis** (text block):
   - 2-3 sentence forensic summary of behavioral patterns
   - References specific frameworks (DARVO, trauma bonding, etc.) where applicable

6. **Protection Strategies** (3 cards):
   - Priority: essential / recommended / optional
   - Each: title + description
   - Actionable, specific to the analyzed behavior

7. **Self-Reflection Card** (conditional):
   - Only shown when `is_toxic === false`
   - Compassionate message redirecting user to examine their own approach
   - Suggestions array for alternative perspectives

8. **User Insight Card** ("Your Mirror"):
   - Always shown
   - Communication style assessment
   - Emotional patterns observed
   - Boundary awareness level
   - Detected patterns (user's own)
   - Growth areas

**Current State**: Implemented and functional.

---

### 5.6 People List (`/people`)

**Purpose**: Browse and manage all tracked subjects.

**Layout**:
- Search/filter bar at top
- List of person cards sorted by toxicity score (descending) or most recent
- Each card: name, relationship, toxicity score (circular indicator), risk badge, analysis count
- Click card to navigate to `/people/:id`

**Current State**: Implemented and functional.

---

### 5.7 Person Detail (`/people/:id`)

**Purpose**: View the latest threat profile for a specific person.

**Layout**:
- **Person Header**: Name, relationship, analysis count, action buttons
  - "Add Info" button → `/people/:id/add-info`
  - "Share" button → `/people/:id/share`
- **Threat Profile**: Full analysis result (same component as 5.5)

**Current State**: Implemented and functional.

---

### 5.8 Add Info (`/people/:id/add-info`)

**Purpose**: Append new behavioral data to an existing person for re-analysis.

**Layout**: Same form as Analyze page, but:
- Name and relationship are pre-filled and locked
- Person ID is passed explicitly (no dedup needed)
- Analysis is contextual: pulls all previous inputs + latest analysis
- Score can move up OR down based on new information

**Current State**: Implemented and functional.

---

### 5.9 Share Page (`/people/:id/share`)

**Purpose**: Generate a shareable/downloadable threat profile card.

**Card Contents**:
- Person name (or alias)
- Toxicity score + ring
- Headline + tagline
- Top 3 traits
- ToxShield branding

**Actions**:
- Copy shareable link
- Download as image (html2canvas)

**Current State**: Implemented and functional.

---

### 5.10 My Mirror / My Insights (`/my-insights`)

**Purpose**: Aggregated self-awareness dashboard showing the USER's own behavioral patterns across all analyses.

**Sections**:

1. **Insights Summary**:
   - Boundary awareness breakdown (percentage across analyses)
   - All detected user patterns (aggregated)
   - Growth areas (recurring themes)

2. **Insights Timeline**:
   - Chronological list of analyses
   - Each entry: date, person analyzed, user's behavioral snapshot from that analysis
   - Shows evolution of user's own patterns over time

**Current State**: Implemented and functional.

---

### 5.11 Settings (`/settings`)

**Purpose**: View account information.

**Content**:
- Display name
- Email address
- User ID
- About/version text

**Current State**: Implemented (minimal). No edit capabilities, no preferences, no data management.

---

### 5.12 Try Page (`/try`)

**Purpose**: Zero-friction demo for unauthenticated users.

**Differences from Analyze page**:
- No auth required
- Text mode only (no WhatsApp/Slack)
- Rate limited: 10 analyses/hour per IP
- Results are not saved to database
- CTA to sign up after viewing result

**Current State**: Implemented and functional.

---

## 6. Design System

### 6.1 Visual Identity

**Aesthetic**: Dark terminal / hacker intelligence tool
**Mood**: Classified, cinematic, slightly dystopian — like a UI from a thriller movie

### 6.2 Color System

The current production build uses a **monochrome brutalist palette** (black, white, opacity variations). The Figma design system defines accent colors that are not yet fully deployed.

#### Production Palette (Monochrome)

| Token | Value | Usage |
|-------|-------|-------|
| `background` | `#0a0a0a` | Page background |
| `surface` | `#141414` | Cards, panels, sidebar |
| `white/[0.06]` | — | Borders, dividers |
| `white/[0.15-0.70]` | — | Text hierarchy via opacity |
| `white` | `#ffffff` | Primary buttons, high-emphasis text |

#### Planned Accent Palette (from Figma design system)

| Token | Hex | Usage |
|-------|-----|-------|
| `toxic-green` | `#00ff41` | Primary accent, neon highlights |
| `toxic-green-dim` | `#2d6b3a` | Muted green states |
| `danger-red` | `#e53e3e` | High-risk indicators |
| `warning-amber` | `#d69e2e` | Moderate-risk indicators |
| `safe-blue` | `#4299e1` | Low-risk indicators |
| `critical-magenta` | `#d53f8c` | Critical severity |

#### Design Decision: Color Strategy

The monochrome approach was chosen for v1 to maximize the brutalist aesthetic. Risk-level colors (from the Figma system) should be **selectively introduced** for data-dense screens (dashboard stats, risk badges, toxicity ring) while keeping the overall UI monochrome. This creates a powerful contrast: the app is black and white, but danger *glows*.

### 6.3 Typography

| Role | Font | Tailwind | Usage |
|------|------|----------|-------|
| Body | Inter | `font-sans` (default) | All standard text |
| Terminal | JetBrains Mono | `font-mono` | Nav, headings, scores, labels, code |

**Scale** (standard Tailwind CSS 4):

| Class | Size | Usage |
|-------|------|-------|
| `text-xs` | 12px | Badges, timestamps, fine print |
| `text-sm` | 14px | Secondary text, nav items, form labels |
| `text-base` | 16px | Body text (minimum accessible size) |
| `text-lg` | 18px | Section headings |
| `text-xl` | 20px | Page titles |
| `text-2xl` | 24px | Hero text |
| `text-5xl/6xl` | 48/60px | Landing page wordmark |

### 6.4 Effects & Animations

| Effect | Class | Description |
|--------|-------|-------------|
| Glow (subtle) | `glow-subtle` | Faint white box-shadow |
| Glow (intense) | `glow-intense` | Strong white box-shadow |
| Text glow | `text-glow` | White text-shadow for emphasis |
| Scanlines | `scanlines` | CRT-style horizontal line overlay |
| Cursor blink | `cursor-blink` | Terminal cursor animation |
| Score pulse | `score-pulse` | Toxicity score entrance animation |
| Touch ripple | `touch-ripple` | Mobile tap feedback |

### 6.5 Component Library

#### Layout Primitives

| Component | File | Description |
|-----------|------|-------------|
| `TerminalHeader` | `layout/terminal-header.tsx` | Fixed top bar with traffic-light dots + title |
| `Sidebar` | `layout/sidebar.tsx` | Fixed left nav (desktop), ASCII icons |
| `BottomNav` | `layout/bottom-nav.tsx` | Mobile tab bar |
| `AppHeader` | `layout/app-header.tsx` | Page-level header with optional back button |
| `PageContainer` | `layout/page-container.tsx` | Content wrapper with padding |

#### Data Display

| Component | File | Description |
|-----------|------|-------------|
| `ThreatProfile` | `analysis/threat-profile.tsx` | Full analysis result display |
| `ToxicityRing` | `analysis/toxicity-ring.tsx` | Circular score (0-10) |
| `RiskBadge` | `analysis/risk-badge.tsx` | LOW / MODERATE / HIGH pill |
| `TraitList` | `analysis/trait-list.tsx` | Detected traits with severity |
| `PatternAnalysis` | `analysis/pattern-analysis.tsx` | Behavioral summary text |
| `ProtectionStrategies` | `analysis/protection-strategies.tsx` | 3 strategy cards |
| `SelfReflectionCard` | `analysis/self-reflection-card.tsx` | Non-toxic redirect |
| `UserInsightCard` | `analysis/user-insight-card.tsx` | "Your Mirror" section |

#### Forms & Input

| Component | File | Description |
|-----------|------|-------------|
| `TextModeForm` | `analysis/text-mode-form.tsx` | Text description input |
| `ChatModeForm` | `analysis/chat-mode-form.tsx` | WhatsApp chat input |
| `SlackModeForm` | `analysis/slack-mode-form.tsx` | Slack messages input |
| `FormInput` | `ui/form-input.tsx` | Styled text input |
| `FormTextarea` | `ui/form-textarea.tsx` | Styled textarea |
| `FormSelect` | `ui/form-select.tsx` | Styled dropdown |
| `PersonMatchBanner` | `ui/person-match-banner.tsx` | Dedup confirmation banner |

#### Dashboard

| Component | File | Description |
|-----------|------|-------------|
| `StatsGrid` | `dashboard/stats-grid.tsx` | 3-stat card row |
| `EnvironmentHealth` | `dashboard/environment-health.tsx` | Health percentage display |

#### Feedback & State

| Component | File | Description |
|-----------|------|-------------|
| `Spinner` | `ui/spinner.tsx` | Loading indicator |
| `ErrorAlert` | `ui/error-alert.tsx` | Error display banner |

---

## 7. Interaction Patterns

### 7.1 Person Name Matching

The most complex interaction in the app. Prevents accidental duplicate profiles while allowing intentional ones.

```
User types name → onBlur → API search
  ├── No match → proceed normally
  └── Match found → show PersonMatchBanner
       ├── "Yes, same person" → set personId, analysis becomes contextual
       └── "No, different person" → generate quirky names
            └── User picks alternative → proceed with new name
```

**Quirky Name Examples**: "John (The One Who Ghosted)", "John (v2.0)", "John (Plot Twist Edition)"

### 7.2 Analysis Loading State

- Form becomes disabled
- Spinner replaces submit button
- "Analyzing..." label
- On completion: result renders below form with entrance animation
- Scroll to result

### 7.3 Mode Switching (Analyze Page)

- Tab-style toggle at top of form
- Switching modes resets form state
- Mode determines: input fields, prompt builder, parsing pipeline

### 7.4 Navigation

- **Desktop**: Click sidebar items. Active state indicated by icon color change.
- **Mobile**: Bottom tab bar. Same 5 items as sidebar.
- **Back navigation**: AppHeader shows back arrow on detail pages.

### 7.5 Share Flow

- "Share" button on person profile header
- Navigate to share page
- Preview card rendered
- "Copy Link" → clipboard API
- "Download" → html2canvas → PNG download

---

## 8. Data Visualization

### 8.1 Toxicity Ring

- **Type**: Circular progress indicator (SVG)
- **Range**: 0.0 - 10.0
- **Animation**: Animated fill on mount (score-pulse)
- **Size variants**: Large (profile page), small (list items)
- **Encoding**: Score value displayed in center; ring fill represents percentage of max

### 8.2 Environment Health

- **Type**: Percentage display (0-100%)
- **Calculation**: Weighted average of all tracked people's toxicity scores, with extra penalty for high-risk individuals
- **Display**: Large percentage number + label

### 8.3 Stats Grid

- **Type**: 3 metric cards
- **Metrics**: Total Subjects | High-Risk Count | Total Analyses
- **Style**: Monospace numbers, minimal cards

### 8.4 Insights Timeline

- **Type**: Vertical timeline (Recharts)
- **Data points**: Each analysis, chronologically ordered
- **Per point**: Date, person analyzed, user's behavioral patterns from that analysis

### 8.5 Trait Severity Encoding

Using the monochrome system, severity is communicated through:

| Severity | Symbol | Opacity | Font Weight |
|----------|--------|---------|-------------|
| Low | `○` | `white/5` bg | Normal |
| Moderate | `◐` | `white/8` bg | Normal |
| High | `●` | `white/12` bg | Bold |
| Critical | `◉` | `white/20` bg | Bold |

---

## 9. Content & Tone

### 9.1 Voice Principles

| Principle | Description | Example |
|-----------|-------------|---------|
| **Forensic precision** | Analysis language is clinical, specific, framework-referenced | "Exhibits DARVO pattern: Deny, Attack, Reverse Victim and Offender" |
| **Dark humor** | Headlines and taglines are savage but never cruel | Headline: "The Emotional Ponzi Scheme" |
| **Empathetic backbone** | Underneath the edge, the app genuinely cares about the user | Self-reflection: "Their behavior seems within healthy range. Let's look at what might be making this feel harder..." |
| **Terminal aesthetic** | UI copy uses terminal/hacker language | "THREAT PROFILE", "FORENSIC BEHAVIORAL ANALYSIS", "Agent" (instead of "User") |

### 9.2 AI-Generated Content Quality

The following fields are AI-generated per analysis:

| Field | Spec | Quality Bar |
|-------|------|-------------|
| `headline` | 2-5 words, catchy epithet | Must be memorable, shareable, slightly savage. E.g., "The Guilt Architect" |
| `tagline` | 1 sentence, behavioral summary | Must be specific to the analyzed behavior, not generic |
| `pattern_analysis` | 2-3 sentences | Must reference specific behavioral frameworks; reads like a forensic report |
| `protection_strategies` | 3 items with title + description | Must be actionable, specific, not generic self-help advice |
| `self_reflection` | Message + suggestions | Must be compassionate, not patronizing |
| `user_insight` | Multi-field assessment | Must reflect actual patterns visible in the user's input |

### 9.3 Relationship Labels

Available relationships (dropdown options):
Partner, Ex-Partner, Friend, Ex-Friend, Parent, Sibling, Child, Boss, Coworker, Roommate, Acquaintance, Other

### 9.4 Error Messages

Error messages should maintain the terminal aesthetic:

| Context | Message Style |
|---------|--------------|
| API failure | "Analysis failed. The AI couldn't process this input." |
| Rate limit (try page) | "Rate limit reached. Try again in {minutes} minutes." |
| Auth required | Redirect to login page |
| Validation | Inline field errors in standard form pattern |

---

## 10. Mobile & Responsive Strategy

### 10.1 Platform Support

| Platform | Status | Technology |
|----------|--------|------------|
| Web (desktop) | Production | Next.js + responsive CSS |
| Web (mobile) | Production | Responsive layout + touch optimizations |
| Android | Supported | Capacitor wrapper |
| iOS | Planned | Capacitor wrapper |

### 10.2 Responsive Breakpoints

| Breakpoint | Layout Change |
|------------|---------------|
| < 640px (mobile) | Sidebar hidden, BottomNav shown, single-column layouts |
| 640-1024px (tablet) | Sidebar collapsible, 2-column where appropriate |
| > 1024px (desktop) | Full sidebar, multi-column layouts |

### 10.3 Mobile-Specific Design

- **Minimum touch target**: 48px (enforced in CSS)
- **Safe area insets**: Respected for notch/home indicator
- **Touch feedback**: `touch-active` class with press animation
- **Touch ripple**: Visual ripple effect on interactive elements
- **Splash screen**: App-branded loading screen for Capacitor builds
- **Bottom navigation**: 5-item tab bar replacing sidebar

### 10.4 Mobile Optimizations

- Font minimum: 16px (prevents iOS zoom on focus)
- Form inputs: Full-width on mobile
- Feature grid on landing: stacks to single column
- CTA buttons: Stack vertically on mobile
- Analysis results: Full-width cards

---

## 11. Accessibility

### 11.1 Current Compliance

| Area | Status | Notes |
|------|--------|-------|
| Color contrast | Partial | Monochrome palette with low-opacity text may fail WCAG AA on some elements |
| Motion | Supported | `prefers-reduced-motion` disables animations |
| Touch targets | Good | 48px minimum enforced |
| Font size | Good | 16px minimum prevents zoom issues |
| Keyboard navigation | Needs audit | Not explicitly tested |
| Screen reader | Needs audit | ARIA labels not systematically applied |
| Focus indicators | Needs audit | May not be visible enough on dark background |

### 11.2 Accessibility Priorities

1. **P0**: Ensure all text meets WCAG AA contrast ratios (4.5:1 for body, 3:1 for large text)
2. **P1**: Add ARIA labels to all interactive elements, especially the ToxicityRing and RiskBadge
3. **P1**: Ensure keyboard navigation works through all flows
4. **P2**: Add skip-to-content link
5. **P2**: Test with screen readers (VoiceOver, NVDA)

---

## 12. Feature Roadmap & Gaps

### 12.1 Shipped Features (v1.0)

- [x] Text-based behavioral analysis
- [x] WhatsApp chat import and analysis
- [x] Slack message import and analysis
- [x] Person deduplication with quirky name disambiguation
- [x] Incremental analysis (add more data, score evolves)
- [x] Dual-profile analysis (subject + user mirror)
- [x] Threat profile with headline, tagline, traits, strategies
- [x] Self-reflection for non-toxic subjects
- [x] Dashboard with stats and environment health
- [x] People list with search
- [x] Individual person profiles
- [x] Share page (copy link + download image)
- [x] My Mirror / My Insights page
- [x] Try page (no signup required, rate-limited)
- [x] Google OAuth + email/password auth
- [x] Mobile-responsive design
- [x] Android Capacitor build support

### 12.2 Identified Gaps & Opportunities

#### High Priority

| Feature | Description | Impact |
|---------|-------------|--------|
| **Email import** | Parse email threads for analysis | Extends multi-source input story |
| **SMS/iMessage import** | Parse text message exports | High demand input source |
| **Audio transcription** | Voice description input (Whisper API) | Original plan.md requirement, lowers input friction |
| **Analysis history** | View all past analyses for a person, not just latest | Currently only latest analysis shown on person page |
| **Comparison view** | Compare two people's threat profiles side-by-side | Shareable, viral potential |
| **Push notifications** | Remind users to update profiles after time passes | Retention driver |
| **Onboarding flow** | Guided first-run experience | Improve activation rate |

#### Medium Priority

| Feature | Description | Impact |
|---------|-------------|--------|
| **Settings expansion** | Edit display name, notification preferences, data export/delete | Table stakes for a mature app |
| **Dark/light theme toggle** | Some users may prefer light mode | Accessibility win |
| **Analysis confidence score** | Show how confident the AI is in its assessment | Trust building |
| **Group analysis** | Analyze a group dynamic (e.g., friend group, team) | New analysis mode |
| **Trend charts** | Visualize toxicity score changes over time per person | Retention driver for Pattern Trackers |
| **Public profile page** | Shareable URL showing threat profile (privacy-considered) | Viral sharing without screenshot |

#### Low Priority / Experimental

| Feature | Description | Impact |
|---------|-------------|--------|
| **AI-powered advice chat** | Follow-up conversation about a specific person/situation | Engagement deepener |
| **Community patterns** | Anonymous aggregated insights ("People with this trait profile...") | Social proof / content |
| **Integration with therapy apps** | Export insights to journaling or therapy platforms | Niche but valuable |
| **Accent color introduction** | Selectively introduce toxic-green, danger-red, etc. from Figma system | Visual polish |

### 12.3 Technical Debt & Design Debt

| Area | Issue | Priority |
|------|-------|----------|
| Color system mismatch | Figma design system defines accent colors not used in production | Medium |
| Settings page | Minimal — no edit capabilities | Medium |
| Empty states | Dashboard and people list need better empty state designs | Medium |
| Error states | API errors could be more informative and on-brand | Low |
| Loading states | Could be more engaging (terminal-style progress messages) | Low |
| Keyboard shortcuts | No keyboard shortcut system | Low |
| Animation consistency | Some pages animate, others don't | Low |

---

## 13. Success Metrics

### 13.1 Activation Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Try-to-signup rate** | % of /try users who sign up | > 15% |
| **First analysis completion** | % of signups who complete first analysis | > 70% |
| **Time to first analysis** | Minutes from signup to first result | < 5 min |

### 13.2 Engagement Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **People per user** | Average tracked subjects per active user | > 3 |
| **Analyses per person** | Average analyses (incremental updates) per subject | > 2 |
| **Return rate (7-day)** | % of users who return within 7 days | > 30% |
| **My Mirror views** | % of active users who check My Mirror | > 25% |

### 13.3 Viral / Growth Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Share rate** | % of analyses that get shared | > 20% |
| **Share-to-visit rate** | % of shared links that get clicked | > 30% |
| **Visit-to-signup rate** | % of share-link visitors who sign up | > 10% |
| **Organic acquisition** | % of new users from shares vs. direct/paid | > 40% |

### 13.4 Quality Metrics

| Metric | Definition | Target |
|--------|-----------|--------|
| **Analysis satisfaction** | Thumbs up/down on analysis results (not yet implemented) | > 80% positive |
| **Add-info rate** | % of people who get updated with new info | > 15% |
| **Self-reflection engagement** | % of non-toxic results where user reads full reflection | > 50% |

---

## Appendix A: Database Schema Reference

```sql
profiles    (id, display_name, avatar_url, created_at, updated_at)
people      (id, user_id, name, relationship, current_toxicity_score,
             current_risk_level, is_toxic, analysis_count, created_at, updated_at)
analyses    (id, person_id, user_id, toxicity_score, risk_level, is_toxic,
             detected_traits, pattern_analysis, protection_strategies,
             self_reflection, headline, tagline, user_insight, input_summary,
             model_used, prompt_tokens, completion_tokens, created_at)
inputs      (id, analysis_id, person_id, user_id, input_type, content,
             raw_file_url, metadata, created_at)
```

## Appendix B: API Endpoints

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| POST | `/api/analyze` | Required | Run analysis (text/whatsapp/slack) |
| POST | `/api/try-analyze` | None | Demo analysis (rate-limited) |
| GET | `/api/people/search?name=` | Required | Search people by name |
| PATCH | `/api/people/:id` | Required | Update person name/relationship |
| DELETE | `/api/people/:id` | Required | Delete person |

## Appendix C: AI Analysis Frameworks

The AI engine references these behavioral psychology frameworks in its analysis:

- **DARVO** — Deny, Attack, Reverse Victim and Offender
- **Narcissistic Supply** — Attention/validation extraction patterns
- **Trauma Bonding** — Intermittent reinforcement cycles
- **Gaslighting** — Reality distortion techniques
- **Love Bombing** — Excessive affection as control mechanism
- **Grey Rocking** — Recommended defense strategy
- **JADE** — Justify, Argue, Defend, Explain (patterns to avoid)

---

*This document describes ToxShield as of 2026-03-26. It reflects both the current production state and planned evolution. All feature priorities are subject to change based on user feedback and business needs.*
