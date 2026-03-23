---
name: review-pr
description: Review current PR changes for code quality, ToxShield patterns, and security issues. Use before merging pull requests.
disable-model-invocation: true
context: fork
agent: Explore
allowed-tools: Bash(git *), Bash(gh *), Read, Grep, Glob
---

# Pull Request Review

Review the current branch changes against the main branch for code quality, pattern compliance, and security.

## Current Changes Context

**Changed files:**
!`git diff --name-only origin/main 2>/dev/null || git diff --name-only HEAD~5`

**Diff summary:**
!`git diff --stat origin/main 2>/dev/null || git diff --stat HEAD~5`

**Recent commits on this branch:**
!`git log --oneline origin/main..HEAD 2>/dev/null || git log --oneline -5`

## Review Checklist

### 1. Design Token Compliance
- [ ] No raw hex, oklch, or rgb values — use surface-*, toxic-green, danger-red, etc.
- [ ] No light-mode colors (bg-white, gray-*, etc.)
- [ ] Glow effects use CSS classes (glow-green, text-glow-green) not inline styles
- [ ] Font usage: Inter (default) + JetBrains Mono (font-mono for terminal)

### 2. API Route Quality
- [ ] Zod validation on all request bodies
- [ ] Supabase auth check (getUser()) on protected endpoints
- [ ] User isolation (filter by user_id on all queries)
- [ ] Proper error handling (try/catch, generic error messages)
- [ ] Correct HTTP status codes

### 3. TypeScript Quality
- [ ] No `any` types
- [ ] Types from `src/types/` (not inline)
- [ ] Supabase queries use `.returns<Type>()`
- [ ] Proper null/undefined handling

### 4. Supabase Patterns
- [ ] Server client for API routes/server components
- [ ] Client client for 'use client' components
- [ ] Error checking on Supabase responses
- [ ] RLS-compatible queries (user_id filters)

### 5. AI Integration (if applicable)
- [ ] Structured output via tool_use pattern
- [ ] Zod schema validation on AI responses
- [ ] Token usage tracked
- [ ] System prompt doesn't contain user data
- [ ] Proper error handling on Claude API calls

### 6. Security (OWASP Top 10)
- [ ] No hardcoded secrets or API keys
- [ ] `ANTHROPIC_API_KEY` not exposed to client (no NEXT_PUBLIC_ prefix)
- [ ] Input validation on all user inputs
- [ ] No XSS vulnerabilities
- [ ] No SQL injection (Supabase client handles this, but check raw queries)

### 7. Component Quality
- [ ] Dark theme consistent (surface-*, not white/light colors)
- [ ] Terminal elements use font-mono
- [ ] Components in correct category (analysis/, dashboard/, layout/, etc.)
- [ ] File size under 300 lines

### 8. Database (if migrations changed)
- [ ] Sequential migration numbering in supabase/migrations/
- [ ] RLS policies on new tables
- [ ] UUID primary keys
- [ ] Timestamp columns (created_at, updated_at)
- [ ] Proper foreign keys with cascades

## Review Output

For each issue found, provide:
1. **File and line number**
2. **Issue description**
3. **Suggested fix**
4. **Severity**: Critical / Warning / Info

Summarize with:
- Total issues by severity
- Overall assessment: Ready to merge / Needs changes / Needs discussion
