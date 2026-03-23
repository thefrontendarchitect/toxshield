# /audit-fix — Audit Changed Files, Fix Violations, Verify & Push

Run the full audit -> fix -> typecheck -> build -> push pipeline on changed files.

## Usage
```
/audit-fix              # Audit all uncommitted changes
/audit-fix --staged     # Audit only staged changes
/audit-fix --last       # Audit changes in the last commit
```

## Pipeline (ALL phases are mandatory — do NOT skip any)

### Phase 1: Identify Changed Files

Determine which files changed based on the mode:
- Default: `git diff --name-only HEAD` (all uncommitted changes)
- `--staged`: `git diff --cached --name-only`
- `--last`: `git diff --name-only HEAD~1 HEAD`

Categorize files:
- **Frontend/Components**: files under `src/components/`, `src/app/` (`.tsx`)
- **API/Server**: files under `src/app/api/`, `src/lib/`, `src/middleware.ts` (`.ts`)
- **Types**: files under `src/types/` (`.ts`)
- **Other**: skip (config, docs, etc.)

If no auditable files changed, report "No auditable changes found" and stop.

### Phase 2: Run Auditors

Launch auditor agents **in parallel** based on what changed:

- **If frontend files changed**: Launch `frontend-principles-auditor` targeting changed files
- **If API/server files changed**: Launch `backend-principles-auditor` targeting changed files

Wait for all auditors to complete.

### Phase 3: Consolidate Violations

Collect all violations from auditor results. Present a summary:

```
## Audit Results

### Frontend Violations (N found)
- [file:line] Description

### API/Server Violations (N found)
- [file:line] Description

Proceeding to fix all violations...
```

If zero violations found, skip to Phase 6.

### Phase 4: Fix All Violations

Implement fixes for every violation identified:
- Fix in **changed files only** — do not expand scope
- For design token violations, replace with ToxShield theme tokens (surface-*, toxic-green, etc.)
- For missing auth checks, add supabase.auth.getUser()
- For missing validation, add Zod schemas
- For type issues, add proper TypeScript types

### Phase 5: Typecheck

Run `npx tsc --noEmit`. If errors found:
1. Fix type errors
2. Re-run typecheck
3. Repeat until clean (max 3 iterations)

### Phase 6: Build Verification

Run `npm run build`. If build fails:
1. Fix build errors
2. Re-run build
3. Repeat until clean (max 3 iterations)

### Phase 7: Commit & Push

1. Stage changed files: `git add <specific files>`
2. Commit: `fix: resolve audit violations in [list of areas]`
3. Push to current branch

Report final summary:
```
## Audit-Fix Complete
- Violations found: N
- Violations fixed: N
- Typecheck: PASS
- Build: PASS
- Commit: <hash>
- Pushed to: <branch>
```
