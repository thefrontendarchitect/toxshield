---
name: deploy-check
description: Validate that the app is ready for deployment by running all checks (typecheck, lint, build).
disable-model-invocation: true
context: fork
agent: general-purpose
allowed-tools: Bash(pnpm *), Read
---

# Pre-Deployment Validation

Run all validation checks to ensure ToxShield is ready for deployment.

## Validation Steps

### 1. TypeScript Check

```bash
npx tsc --noEmit
```

Expected: No type errors

### 2. Lint Check

```bash
pnpm lint
```

Expected: No lint errors (warnings acceptable)

### 3. Build

```bash
pnpm build
```

Expected: Successful build with no errors

### 4. Check Build Output

Verify `.next/` directory exists:
```bash
ls -la .next/
```

## Environment Checklist

Before deployment, verify:

- [ ] `.env.local` has correct `NEXT_PUBLIC_SUPABASE_URL` for production
- [ ] `.env.local` has correct `NEXT_PUBLIC_SUPABASE_ANON_KEY` for production
- [ ] `ANTHROPIC_API_KEY` is set (server-side only, not NEXT_PUBLIC_)
- [ ] Supabase project has correct RLS policies enabled
- [ ] Supabase Auth configured with production redirect URLs

## Deployment Targets

### Vercel (Recommended)
```bash
# Auto-deployed from git, or:
npx vercel deploy
```

### Other Platforms
```bash
pnpm build
# Deploy .next/ output
```

## Common Issues

### Build Fails with Module Not Found
- Run `pnpm install` to ensure dependencies
- Check `tsconfig.json` paths

### Environment Variable Errors
- `NEXT_PUBLIC_*` vars available client-side
- `ANTHROPIC_API_KEY` must NOT have `NEXT_PUBLIC_` prefix
- Check `.env.local` exists and is populated

### Supabase Connection Errors
- Verify Supabase project is running
- Check URL and anon key match the project
- Ensure RLS policies allow the operations needed

## Post-Deployment

1. Verify app loads at production URL
2. Test login/signup flow
3. Test analysis submission (requires working Claude API key)
4. Check dashboard loads with real data
5. Verify auth redirects work correctly

## Report Format

```
## Deployment Readiness Report

### TypeScript: PASS / FAIL
[Details if failed]

### Lint: PASS / FAIL
[Details if failed]

### Build: PASS / FAIL
[Details if failed]

### Overall: READY / NOT READY
[Summary and any blocking issues]
```
