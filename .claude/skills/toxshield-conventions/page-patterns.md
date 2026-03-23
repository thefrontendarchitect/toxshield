# Page Layout Patterns

**Authoritative source:** `src/app/(app)/layout.tsx`.

## App Layout Structure

All protected pages are wrapped in the app layout:

```tsx
// src/app/(app)/layout.tsx
<div className="flex flex-col h-screen">
  <TerminalHeader />
  <div className="flex flex-1 overflow-hidden">
    <Sidebar />
    <main className="flex-1 overflow-y-auto p-6">{children}</main>
  </div>
</div>
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
  if (error) return <div className="text-danger-red">{error}</div>;
  // Empty state
  if (!data) return <div className="text-text-secondary">No data yet.</div>;

  // Content
  return (/* ... */);
}
```

## Card Pattern

```tsx
<div className="bg-surface-1 border border-surface-3 rounded-lg p-4">
  <h3 className="font-mono text-sm text-toxic-green">{title}</h3>
  <p className="text-text-secondary mt-1">{content}</p>
</div>
```

## Route Groups

| Group | Path | Auth Required | Layout |
|-------|------|---------------|--------|
| `(app)` | `/dashboard`, `/analyze`, `/people/*`, `/settings` | Yes | TerminalHeader + Sidebar |
| `(auth)` | `/login`, `/signup` | No | Centered auth layout |
| Root | `/` | No | Landing page (no sidebar) |

## Navigation

Sidebar navigation items (from `src/components/layout/sidebar.tsx`):

| Route | Label | Icon |
|-------|-------|------|
| `/dashboard` | Dashboard | `>` |
| `/analyze` | New Analysis | `+` |
| `/people` | People | `#` |
| `/settings` | Settings | `*` |
