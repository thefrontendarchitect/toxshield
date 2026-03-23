# ToxShield — Project Instructions

## What is ToxShield?
AI-powered forensic behavioral analyzer. Users log descriptions of people in their lives, and Claude analyzes toxic personality patterns, producing shareable threat profiles with toxicity scores, detected traits, and protection strategies.

## Tech Stack
- **Framework**: Next.js 16.2.1 (App Router), React 19.2.4, TypeScript 5
- **Database & Auth**: Supabase (PostgreSQL + Supabase Auth with email/password & Google OAuth)
- **AI**: Anthropic Claude API (`claude-sonnet-4-5-20250514`) via `@anthropic-ai/sdk`
- **Styling**: Tailwind CSS 4 with OKLch color theme (dark terminal aesthetic)
- **Forms**: React Hook Form + Zod validation
- **Other**: Framer Motion, Recharts, date-fns, html2canvas, whatsapp-chat-parser
- **Package Manager**: npm

## Architecture
Single Next.js app (NOT a monorepo). No separate backend.

```
src/
  app/
    (app)/          # Protected routes (dashboard, analyze, people, settings)
    (auth)/         # Auth routes (login, signup)
    api/analyze/    # POST endpoint — main AI analysis pipeline
    auth/callback/  # Supabase OAuth callback
  components/       # React components (analysis/, dashboard/, layout/, ui/)
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
Dark terminal aesthetic with neon accents:
- **Surfaces**: surface-0 (#0a0a0a), surface-1, surface-2, surface-3
- **Accents**: toxic-green (neon), danger-red, warning-amber, safe-blue, critical-magenta
- **Text**: text-primary, text-secondary, text-terminal (green)
- **Fonts**: Inter (body via `--font-sans`) + JetBrains Mono (code via `--font-mono`)
- **Effects**: glow-green, glow-red, glow-amber, text-glow-green, scanlines, cursor-blink

## Key Patterns
- **Auth**: Supabase middleware checks auth on all routes except `/`, `/login`, `/signup`, `/auth/*`, `/api/*`
- **API Routes**: Zod validation + Supabase auth check + business logic + Supabase persistence
- **AI Integration**: Claude tool_use pattern for structured JSON output, validated with Zod
- **Layout**: `TerminalHeader` (top) + `Sidebar` (left) + `main` content area
- **Env vars**: `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `ANTHROPIC_API_KEY`

## Commands
```bash
npm run dev      # Start dev server
npm run build    # Production build
npm run lint     # ESLint
npx tsc --noEmit # Type check
```
