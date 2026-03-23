# Plan File Template — Issue Resolver

> **Used by**: `.claude/agents/linear-issue-resolver.md` (Phase 3)
> **Location**: `.claude/plans/{ISSUE-ID}-fix.md` (e.g., `.claude/plans/GH-42-fix.md`)

When creating a fix plan, use the Write tool to create the plan file with this exact structure:

---

```markdown
# Fix: {Issue Title}

> **Issue**: [{ISSUE-ID}]({issue-url})
> **Status**: PENDING REVIEW
> **Created**: {YYYY-MM-DD}

## Root Cause Analysis

### The Problem
{Observed behavior — what the user sees, what's broken, with specifics.}

### Investigation
{Code paths traced, file paths with line numbers, relevant queries/state examined.}

### Root Cause
{WHY it broke — the underlying issue, not just a symptom description. Connect the code path to the failure.}

## Proposed Fix

### Approach
{Strategy description + why this approach over alternatives. If multiple approaches were considered, briefly note why others were rejected.}

### Files to Modify

| File | Change Description |
|------|--------------------|
| `src/path/to/file1.ts` | {What changes and why} |
| `src/path/to/file2.tsx` | {What changes and why} |

### Implementation Steps
1. {Specific, actionable step with file path}
2. {Next step}
3. {Continue as needed}

### Risk Assessment
- **What could break**: {Potential regressions or side effects}
- **API route impact**: {Does this change API behavior or response shape?}
- **Database concerns**: {Any Supabase migration, RLS policy, or data format changes?}
- **AI prompt impact**: {Does this change Claude prompts or structured output schemas?}

## Testing Strategy

### Verification Steps
1. {How to manually verify the fix}
2. {Expected behavior after fix}

### Automated Test Coverage
- {What tests should be added or updated}
- {Regression areas to verify}

## Reproduction Context
- **URL**: {Exact URL where bug was observed, e.g., http://localhost:3000/dashboard}
- **Screenshot path**: {Path to reproduction screenshot(s), or "None"}
```

---

## Status Values

The `Status` field in the plan header tracks the plan lifecycle:

| Status | Meaning |
|--------|---------|
| `PENDING REVIEW` | Plan written, awaiting user approval |
| `APPROVED ({date})` | User approved, ready for implementation |
| `CHANGES REQUESTED` | User requested modifications (temporary — update plan then back to PENDING REVIEW) |
| `IMPLEMENTED` | Fix has been implemented per this plan |

## Rules

1. **One file per issue** — naming convention: `.claude/plans/{ISSUE-ID}-fix.md`
2. **Never paste full plan in chat** — post a 2-3 sentence summary with the file path
3. **Edit, don't rewrite** — when user requests changes, use the Edit tool on the existing file
4. **Update status on approval** — change `PENDING REVIEW` → `APPROVED ({date})` after user approves
5. **Update on deviation** — if implementation requires deviating from the plan, update the plan file first and inform the user
