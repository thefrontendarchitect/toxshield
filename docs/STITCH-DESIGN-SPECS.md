# ToxShield Figma/Stitch Design Specs — 4 Final Screens

> **Source**: Google Stitch — ToxShield PRD (`stitch.withgoogle.com/projects/15182206433577544283`)
> **Format**: Mobile-first (390 x 884px)
> **Aesthetic**: Dark terminal/forensic case-file theme — "gritty intelligence dossier"

---

## Global Design System

### Colors
| Token | Hex (approx) | Usage |
|-------|-------------|-------|
| `surface-0` | `#0a0a0a` | Main background |
| `surface-1` | `#141414` | Cards, panels |
| `surface-2` | `#1e1e1e` | Elevated cards, input fields |
| `surface-3` | `#282828` | Borders, dividers |
| `text-primary` | `#e8e8e8` | Primary text |
| `text-secondary` | `#6b6b6b` | Secondary/muted text |
| `toxic-green` | `#00ff41` | Active states, accents |
| `danger-red` | `#e53e3e` | High-risk badges, warnings |
| `warning-amber` | `#d69e2e` | Moderate risk |
| `safe-blue` | `#4299e1` | Low risk, stable states |
| `critical-magenta` | `#d53f8c` | Critical status |
| Badge pink/salmon | `#f5c6c6` / `rgba(229,62,62,0.15)` | Badge backgrounds |

### Typography
| Element | Font | Size | Weight | Style |
|---------|------|------|--------|-------|
| App header title | JetBrains Mono | 18px | Bold | Uppercase, letter-spacing 2px |
| Section labels | JetBrains Mono | 11-12px | Medium | Uppercase, letter-spacing 3-4px, text-secondary |
| Large stat numbers | Inter / system | 64-72px | Black (900) | Italic |
| Card titles | JetBrains Mono | 16px | Bold | — |
| Body text | Inter | 14px | Regular | — |
| Small labels | JetBrains Mono | 10-11px | Medium | Uppercase |
| Badges | JetBrains Mono | 10px | Bold | Uppercase |
| Page hero text | Inter/system | 48-56px | Black (900) | Uppercase, compressed |
| Bottom nav labels | JetBrains Mono | 10px | Medium | Uppercase |

### Card Patterns
- **Dashed-border card**: `border: 1px dashed surface-3; background: surface-1; border-radius: 8px; padding: 20px`
- **Solid card**: `background: surface-1; border: 1px solid surface-3; border-radius: 8px`
- **Grid background**: Faint grid-line overlay on surface-0 (1px lines at ~40px intervals, opacity ~0.05)

### Global Elements
- **Status bar area**: Top 44px reserved (iOS safe area)
- **Bottom nav height**: 64px, fixed bottom
- **Content safe area**: 390px wide, scrollable vertically
- **Grid overlay**: Subtle dotted grid pattern across entire background

---

## Screen 1: Dashboard (Final) — "DOSSIER"

### Layout (top to bottom, scrollable)

#### 1.1 Header Bar
- **Height**: ~56px
- **Background**: `surface-0`
- **Left**: Folder icon (outline, 20px, text-secondary) + "CASE_FILE_0821" (JetBrains Mono, 18px, bold, white, uppercase)
- **Right**: Circular avatar thumbnail (32px, rounded-full, border 1px surface-3)
- **Padding**: 16px horizontal

#### 1.2 Total Subjects Card
- **Container**: Dashed border card, ~full width (margin 16px sides)
- **Label**: "TOTAL SUBJECTS" — JetBrains Mono, 11px, medium, uppercase, letter-spacing 3px, text-secondary
- **Number**: "1,402" — 64-72px, black/900 weight, italic, white
- **Change indicator**: "+24%" — 14px, salmon/pink color (#f5a6a6), positioned right of number
- **Watermark**: Fingerprint/spiral icon — 80px, opacity 0.1, positioned top-right of card
- **Subtext**: "New data ingestion from Sector 7-B completed at 0400hrs." — Inter 12px, text-secondary
- **Progress bars**: 4 horizontal bars at bottom of card, each ~25% width:
  - Bar 1: Full (white)
  - Bar 2: Full (white)
  - Bar 3: Full (white)
  - Bar 4: Partial (~60%, white with dark remainder)
  - Height: 4px, gap: 4px between bars, rounded-sm

#### 1.3 Environment Health Score Card
- **Container**: Dashed border card, full width (margin 16px)
- **Label**: "ENV. HEALTH SCORE" — same style as section labels
- **Visualization**: Broken heart icon
  - White heart shape, ~120px tall
  - Crack/fracture lines running through middle (black lines creating "shattered" effect)
  - "64%" text centered inside heart — 36px, bold, black text on white heart
  - Heart is split/fractured with visible crack lines
- **Status badge**: "CRITICAL FRACTURE DETECTED"
  - Background: salmon/pink (#f5c6c6)
  - Text: dark/black, JetBrains Mono, 10px, bold, uppercase
  - Padding: 4px 12px
  - Centered below heart

#### 1.4 High-Risk Threats Section
- **Container**: Solid card (surface-1), full width
- **Header**: "HIGH-RISK THREATS" — section label style (JetBrains Mono, 11px, uppercase, letter-spacing, text-secondary)
- **List items** (3 items, each separated by 1px divider line surface-3):

  **Item 1 — OMEGA-7-TOXIN**:
  - Name: "OMEGA-7-TOXIN" — JetBrains Mono, 16px, bold, white
  - Subtext: "DETECTED: LOND_SEC_01" — JetBrains Mono, 10px, text-secondary, uppercase
  - Right icon: Warning triangle — salmon/pink fill, 24px

  **Item 2 — VIRAL_LEAK_V2**:
  - Name: "VIRAL_LEAK_V2" — same as above
  - Subtext: "DETECTED: BERL_SEC_09"
  - Right icon: Warning triangle — salmon/pink fill

  **Item 3 — SYNTH_GAS_X**:
  - Name: "SYNTH_GAS_X" — same as above
  - Subtext: "STATUS: CONTAINED"
  - Right icon: Checkmark circle — outline, text-secondary

- **Row height**: ~64px each
- **Padding**: 16px horizontal, 12px vertical

#### 1.5 Subject Feed Section
- **Header**: "SUBJECT FEED" — 48-56px, black/900 weight, white, uppercase, Inter, bold with outline/stroke effect
- **Subtext**: "REAL-TIME SURVEILLANCE DATA // SECURE_CHANNEL_8" — JetBrains Mono, 10px, text-secondary, uppercase

#### 1.6 Subject Polaroid Cards (scrollable feed, 4 cards visible)
Each card is a **polaroid-style photo** with:
- **Photo container**: White border (8px), slightly rotated (2-5 degrees), drop shadow
  - Photo: B&W portrait, fills container
  - Tape strip at top center (white/translucent, 30px wide, 8px tall)
  - **ID label**: Bottom-left of photo — "ID: #8821-V" — JetBrains Mono, 11px, bold, black on white bg
- **Status badge**: Bottom-right, offset — e.g., "STABLE / 09:12" — salmon/cream bg, black text, JetBrains Mono 10px, rotated slightly
- **Name**: Below polaroid — "ELARA_VANCE" — JetBrains Mono, 16px, bold, italic, white, centered
- **Exposure**: "Primary Exposure: Lead_99" — Inter 12px, text-secondary, centered

**Card-specific badges/states**:
| Subject | ID | Status Badge | Badge Color | Exposure |
|---------|-----|-------------|-------------|----------|
| ELARA_VANCE | #8821-V | STABLE / 09:12 | Cream/beige | Lead_99 |
| KAI_RENARD | #9012-K | CRITICAL LEVEL | Pink/salmon (danger) | Mercury_X |
| SUBJECT_ZERO | #UNKNOWN | UNKNOWN_ORIGIN | White/cream | NA |
| MIRA_PATEL | #4432-P | RECOVERED | Pink/salmon | Arsenic_B |

#### 1.7 Bottom Navigation Bar
- **Height**: 64px
- **Background**: `surface-0` (very dark)
- **Layout**: 4 equal-width tabs, center-aligned icons + labels
- **Tabs**:

| Tab | Icon | Label | Active State |
|-----|------|-------|-------------|
| DOSSIER | Fingerprint | "DOSSIER" | White bg square behind icon, white text |
| ANALYSIS | Brain/head with gear | "ANALYSIS" | Icon only (outline, text-secondary) |
| EVIDENCE | Eye | "EVIDENCE" | Icon only (outline, text-secondary) |
| FILES | Document/clipboard | "FILES" | Icon only (outline, text-secondary) |

- **Icon size**: 24px
- **Label**: JetBrains Mono, 10px, uppercase
- **Active indicator**: White filled square/rounded-rect behind icon + text turns white
- **Inactive**: Icons outline-only, text-secondary color

---

## Screen 2: People (Final) — "PERSONNEL MONITORING"

### Layout (top to bottom)

#### 2.1 Header Bar
- Same as Dashboard: Folder icon + "CASE_FILE_0821" + avatar
- **Right icon**: Different avatar (man in suit, profile photo)

#### 2.2 Hero Section
- **Tag**: "SUBJECT REGISTRY" — JetBrains Mono, 10px, bold, uppercase
  - Background: white/cream, black text
  - Padding: 2px 8px
  - Position: top-left of hero area
- **Title**: "PERSONNEL MONITORING" — 42-48px, black/900 weight, white, uppercase
  - Line 1: "PERSONNEL"
  - Line 2: "MONITORING" (partially cut off at right, implying wide text)
  - Style: Compressed/condensed typeface, heavy weight
- **Quote block**:
  - Left border: 2px solid text-secondary (vertical line)
  - Text: *"Trust is a luxury the data suggests we cannot afford. Watch the fluctuations. Verify the anomalies."* — Inter 14px, italic, text-secondary
  - Padding-left: 16px from border

#### 2.3 Subject Profile Card (Arthur P. Vance)
- **Container**: Surface-1 card with rounded corners
- **Photo**: B&W portrait (hooded figure, dark/ominous), ~120px square, top-left
- **Risk badge**: "HIGH RISK" — overlapping top-right of photo
  - Background: salmon/pink
  - Text: black, JetBrains Mono, 10px, bold, uppercase
  - Slight rotation (~-3 degrees)
- **Name**: "ARTHUR P. VANCE" — JetBrains Mono, 24px, bold, uppercase
- **Relationship**: "RELATIONSHIP: PRIMARY BENEFICIARY / HOSTILE" — JetBrains Mono, 10px, uppercase, text-secondary
- **Metric badges** (inline, horizontal):
  - "MANIPULATION: 88%" — salmon/pink bg, black text, rounded-sm, JetBrains Mono 10px
  - "RELIABILITY: 12%" — same style
- **Analysis quote**: *"Subject has shown persistent patterns of gaslighting during weekly syncs. Suggest immediate isolation."* — Inter 13px, italic, text-secondary
- **Toxicity score ring**: Bottom of card
  - Circular progress ring, ~80px diameter
  - Score: "88" centered — 24px, bold, white
  - Label below: "TOX_SCORE" — JetBrains Mono, 10px, text-secondary
  - Ring color: white/light (near-full circle for 88/100)

#### 2.4 Bottom Navigation Bar
- Same as Dashboard (DOSSIER, ANALYSIS, EVIDENCE, FILES)

---

## Screen 3: Analyze (Final) — "ANALYZE INPUT_"

### Layout (top to bottom)

#### 3.1 Header Bar
- Same structure: Folder icon + "CASE_FILE_0821"
- **Right icon**: User/person icon (outline, surface-3 circle)

#### 3.2 Hero Section
- **Tag**: "SUBJECT: TOXIC INFLUENCE MAPPING" — JetBrains Mono, 10px, bold, uppercase
  - Background: white/cream, black text
  - Padding: 2px 8px
- **Title**: "ANALYZE INPUT_" — 42-48px, black/900 weight, white, uppercase
  - Line 1: "ANALYZE"
  - Line 2: "INPUT_" (with trailing underscore cursor)
  - Style: Same compressed heavy typeface
  - Background watermark: Scattered diagonal tape/cross shapes, opacity ~0.08
- **Description**: "Deconstruct the behavioral patterns of the target subject. Select your capture medium and input forensic data for real-time de-escalation mapping." — Inter 14px, regular, text-secondary, line-height 1.6

#### 3.3 Input Source Tabs
- **Layout**: Horizontal wrap, gap 8px
- **Tab buttons** (3 total):

| Tab | Label | Style |
|-----|-------|-------|
| DESCRIBE | "DESCRIBE" | Active: white bg, black text |
| WHATSAPP | "WHATSAPP" | Inactive: surface-2 bg, text-secondary, border surface-3 |
| SLACK | "SLACK" | Inactive: same |

- **Button style**: JetBrains Mono, 12px, uppercase, letter-spacing 2px
- **Padding**: 10px 20px
- **Border-radius**: 4px
- **Border**: 1px solid surface-3 (inactive), none (active)

#### 3.4 Form Fields
- **Field 1 — SUBJECT_NAME**:
  - Label: "SUBJECT_NAME" — JetBrains Mono, 10px, uppercase, text-secondary, letter-spacing 2px
  - Input: "IDENTITY UNKNOWN" — placeholder text, Inter 18px, text-secondary (lighter), surface-1 bg
  - Bottom border: 1px solid surface-3
  - No visible box border — underline-only style

- **Field 2 — RELATIONSHIP_TYPE**:
  - Label: "RELATIONSHIP_TYPE" — same label style
  - Input: "COLLEAGUE / PARTNER / ..." — placeholder, same style, truncated with ellipsis
  - Bottom border: 1px solid surface-3

- **Field 3 — BEHAVIORAL_DESCRIPTION** (implied, below fold):
  - Label: "DESCRIBE THE PATTERN OF..." — visible partially
  - Large textarea for behavioral input

#### 3.5 Bottom Navigation Bar
- Same as other screens

---

## Screen 4: My Mirror (Final) — "MY MIRROR"

### Layout (top to bottom)

#### 4.1 Header Bar
- Same structure: Folder icon + "CASE_FILE_0821" + avatar (man in hat/fedora)

#### 4.2 Hero Section
- **Title**: "MY MIRROR" — 48-56px, black/900 weight, white, uppercase, compressed
- **Status badge**: "STATUS: CRITICAL"
  - Background: salmon/pink
  - Text: black, JetBrains Mono, 10px, bold, uppercase
  - Padding: 4px 12px
  - Border-radius: 2px
- **Description**: "Reflecting the digital fallout. A forensic reconstruction of your psychological boundaries and exposure patterns over the last 30 days." — Inter 14px, regular, text-secondary, line-height 1.6

#### 4.3 Boundary Awareness Section
- **Container**: Surface-1 card, rounded-lg
- **Header row**:
  - Title: "BOUNDARY AWARENESS" — JetBrains Mono, 24px, bold, uppercase
  - Right icon: Shield icon (outline, 24px, text-secondary)
- **Subtitle**: "INTEGRITY OF DIGITAL DEFENSES" — JetBrains Mono, 10px, uppercase, text-secondary, letter-spacing 2px

#### 4.4 Boundary Category Cards (vertical stack)
Each category is a **dashed-border card** with an icon and status:

**Card 1 — WORK-LIFE**:
- **Container**: Dashed border, surface-1 bg, padding 20px, centered content
- **Icon**: Shield icon (solid, white, ~48px) centered
- **Status badge**: "FIXED" — positioned top-right
  - White bg, black text, JetBrains Mono 10px, bold
  - Slightly rotated
- **Label**: "WORK-LIFE" — JetBrains Mono, 12px, uppercase, text-secondary, centered below icon

**Card 2 — EMOTIONAL**:
- Same dashed card layout
- **Icon**: Heart icon (outline/filled, salmon/pink color, ~48px)
- **Status badge**: "BREACHED" — salmon/pink bg, dark text
  - Indicating compromised boundary
- **Label**: "EMOTIONAL"

**Card 3 — (implied additional categories below fold)**:
- Potentially: SOCIAL, FINANCIAL, DIGITAL categories
- Same card pattern

#### 4.5 Additional Sections (below fold, inferred from initial capture)
- More boundary category cards
- Possibly: Exposure timeline, pattern analysis, recovery metrics
- "STABLE" badge variant visible in initial capture

#### 4.6 Bottom Navigation Bar
- Same as other screens

---

## Shared Patterns & CSS Reference

### Polaroid Card CSS
```css
.polaroid {
  background: white;
  padding: 8px 8px 40px 8px;
  transform: rotate(-2deg); /* varies per card */
  box-shadow: 0 4px 20px rgba(0,0,0,0.5);
  position: relative;
}
.polaroid img {
  width: 100%;
  filter: grayscale(100%);
}
.polaroid .tape {
  position: absolute;
  top: -4px;
  left: 50%;
  transform: translateX(-50%);
  width: 30px;
  height: 8px;
  background: rgba(255,255,255,0.6);
}
```

### Dashed Card CSS
```css
.dashed-card {
  border: 1px dashed var(--surface-3);
  background: var(--surface-1);
  border-radius: 8px;
  padding: 20px;
}
```

### Status Badge CSS
```css
.badge {
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 1px;
  padding: 4px 12px;
  border-radius: 2px;
}
.badge-danger { background: #f5c6c6; color: #1a1a1a; }
.badge-stable { background: #f5f0e0; color: #1a1a1a; }
.badge-contained { background: transparent; border: 1px solid var(--surface-3); color: var(--text-secondary); }
```

### Grid Background CSS
```css
.grid-bg {
  background-image:
    linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px);
  background-size: 40px 40px;
}
```

### Bottom Navigation CSS
```css
.bottom-nav {
  position: fixed;
  bottom: 0;
  width: 100%;
  height: 64px;
  background: var(--surface-0);
  display: flex;
  align-items: center;
  justify-content: space-around;
}
.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  font-family: 'JetBrains Mono', monospace;
  font-size: 10px;
  text-transform: uppercase;
  color: var(--text-secondary);
}
.nav-item.active {
  color: white;
}
.nav-item.active .icon-wrap {
  background: white;
  border-radius: 8px;
  padding: 8px;
}
```

### Section Label CSS
```css
.section-label {
  font-family: 'JetBrains Mono', monospace;
  font-size: 11px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 3px;
  color: var(--text-secondary);
}
```

### Hero Title CSS
```css
.hero-title {
  font-size: 48px;
  font-weight: 900;
  text-transform: uppercase;
  color: white;
  line-height: 0.95;
  letter-spacing: -1px;
}
```
