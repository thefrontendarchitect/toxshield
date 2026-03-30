# Page Layout Patterns

**Authoritative source:** `src/app/(app)/layout.tsx`.

## App Layout Structure

All protected pages are wrapped in the app layout:

```tsx
// src/app/(app)/layout.tsx
<>
  <AuroraBackground seed={hashString(pathname)} />
  <AppHeader title={title} showBackButton={isDetailPage} />
  <main className="bg-surface-0/60 grid-bg pt-[72px] pb-[100px] min-h-screen relative">
    <div className="px-4 py-6">{children}</div>
  </main>
  <BottomNav />
</>
```

## Page Structure

Pages go in `src/app/(app)/[feature]/page.tsx`:

```tsx
export default async function FeaturePage() {
  return (
    <div className="space-y-6">
      <h1 className="text-xl font-bold text-text-primary">Page Title</h1>
      {/* Page content */}
    </div>
  );
}
```

## Client Component Pattern (data fetching)

```tsx
'use client';

export default function FeaturePage() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Loading state
  if (loading) return <div className="text-text-secondary">Loading...</div>;
  // Error state
  if (error) return <div className="text-neon-magenta">{error}</div>;
  // Empty state
  if (!data) return <div className="text-text-secondary">No data yet.</div>;

  // Content
  return (/* ... */);
}
```

## Card Pattern

```tsx
<div className="arcane-glass p-4">
  <h3 className="font-mono text-sm text-neon-cyan">{title}</h3>
  <p className="text-text-secondary mt-1">{content}</p>
</div>
```

## Route Groups

| Group | Path | Auth Required | Layout |
|-------|------|---------------|--------|
| `(app)` | `/dashboard`, `/analyze`, `/people/*`, `/pulse`, `/settings` | Yes | AppHeader + BottomNav + AuroraBackground |
| `(auth)` | `/login`, `/signup` | No | Centered auth layout |
| Root | `/` | No | Landing page (no nav) |

## Navigation

Bottom navigation items (from `src/components/layout/bottom-nav.tsx`):

| Route | Label | Icon Component |
|-------|-------|---------------|
| `/dashboard` | DOSSIER | `FingerprintIcon` |
| `/analyze` | ANALYSIS | `BrainIcon` |
| `/people` | EVIDENCE | `EyeIcon` |
| `/pulse` | PULSE | `PulseIcon` |
