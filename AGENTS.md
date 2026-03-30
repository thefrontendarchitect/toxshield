# ToxShield — Project Instructions

## What is ToxShield?
AI-powered forensic behavioral analyzer. Users log descriptions of people in their lives, and Claude analyzes toxic personality patterns, producing shareable threat profiles with toxicity scores, detected traits, and protection strategies.

## Tech Stack
- **Framework**: Next.js 16.2.1 (App Router), React 19.2.4, TypeScript 5
- **Database & Auth**: Supabase (PostgreSQL + Supabase Auth with email/password & Google OAuth)
- **AI**: Anthropic Claude API (`claude-sonnet-4-5-20250514`) via `@anthropic-ai/sdk`
- **Styling**: Tailwind CSS 4 with Arcane theme (hextech aurora dark aesthetic)
- **Forms**: React Hook Form + Zod validation
- **Other**: Framer Motion, Recharts, date-fns, html2canvas, whatsapp-chat-parser
- **Package Manager**: pnpm

## Architecture
Single Next.js app (NOT a monorepo). No separate backend.

```
src/
  app/
    (app)/          # Protected routes (dashboard, analyze, people, settings)
    (auth)/         # Auth routes (login, signup)
    api/analyze/    # POST endpoint — main AI analysis pipeline
    auth/callback/  # Supabase OAuth callback
  components/       # React components (analysis/, dashboard/, insights/, layout/, people/, ui/)
  lib/
    ai/             # AI engine (engine.ts, prompts.ts, schemas.ts, scoring.ts)
    supabase/       # Supabase clients (client.ts, server.ts)
    parsers/        # Input parsers (WhatsApp, email — planned)
    utils/          # Utility functions
  types/            # TypeScript types (analysis.ts, database.ts, person.ts)
  middleware.ts     # Auth redirect middleware
supabase/
  migrations/       # SQL migration files (001-005)
```

## Database Tables (Supabase PostgreSQL)
- `profiles` — user profiles (auto-created on signup)
- `people` — tracked subjects (name, relationship, current_toxicity_score, risk_level)
- `analyses` — AI analysis snapshots (toxicity_score, detected_traits, protection_strategies, headline, tagline)
- `inputs` — source data (text_description, whatsapp_chat, email, sms, audio_transcription, incident)

## Design System
Arcane design — hextech energy on dark aurora:
- **Surfaces**: surface-0 (#080519), surface-1 (#0f0b28), surface-2 (#181340), surface-3 (#241e55)
- **Neon accents**: neon-cyan (#00b4ff, primary), neon-magenta (#ff2878, danger), neon-mint (#50ffa0, success)
- **Semantic aliases**: toxic-green = neon-mint, danger-red = neon-magenta, safe-blue = neon-cyan, warning-amber (#ffc832), critical-magenta (#dc3cff)
- **Text**: text-primary (#f0f6ff), text-secondary (#b8d4f0), dim (#7a9bc0), muted (#3a4f6a)
- **Fonts**: Inter (body via `--font-sans`) + JetBrains Mono (code via `--font-mono`) + Anton (display via `--font-display`)
- **Glows**: glow / glow-subtle / glow-intense (cyan), glow-magenta, glow-mint, text-glow / text-glow-magenta / text-glow-mint
- **Glass**: arcane-glass (frosted panels), arcane-glass-intense (modals), card-dashed (dossier cards)
- **Effects**: scanlines, cursor-blink, score-pulse, line-pulse, border-flash, touch-active, touch-ripple, arcane-particles
- **Palettes**: 5 themes via `data-palette` — Hextech Core (default), Jinx, Zaun, Piltover, Shimmer

## Key Patterns
- **Auth**: Supabase middleware checks auth on all routes except `/`, `/login`, `/signup`, `/auth/*`, `/api/*`
- **API Routes**: Zod validation + Supabase auth check + business logic + Supabase persistence
- **AI Integration**: Claude tool_use pattern for structured JSON output, validated with Zod
- **Layout**: `AppHeader` (fixed top, arcane-glass) + `BottomNav` (fixed bottom, dossier-icons) + `AuroraBackground` + `main` content area (mobile-first)
- **Env vars**: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `ANTHROPIC_API_KEY`

## Commands
```bash
pnpm dev         # Start dev server
pnpm build       # Production build
pnpm lint        # ESLint
pnpm tsc --noEmit # Type check
```
