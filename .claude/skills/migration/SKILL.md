---
name: migration
description: Create and manage Supabase database migrations safely. Use when adding or modifying database tables.
argument-hint: [description]
disable-model-invocation: true
allowed-tools: Bash(npx supabase *), Read, Write, Edit, Glob
---

# Supabase Migration Helper

Create and manage Supabase SQL migrations for ToxShield.

## Arguments

- `$0` - Migration description (use underscores, e.g., `add_tags_table`)

## Migration Location

```
supabase/migrations/
├── 001_create_profiles.sql
├── 002_create_people.sql
├── 003_create_analyses.sql
├── 004_create_inputs.sql
├── 005_rls_policies.sql
└── NNN_$0.sql              # New migration
```

## Migration Workflow

### Step 1: Check Existing Migrations

Review current migrations:
```bash
ls -la supabase/migrations/
```

### Step 2: Create Migration File

Create `supabase/migrations/NNN_$0.sql` where NNN is the next sequential number.

### Step 3: Write SQL

Follow ToxShield conventions:
- UUID primary keys
- `user_id` foreign key to `auth.users(id)` with `ON DELETE CASCADE`
- `created_at` and `updated_at` timestamps
- Enable RLS on every table
- Create RLS policies for user isolation

### Step 4: Apply Migration

```bash
npx supabase db push    # Push to remote
# or
npx supabase db reset   # Reset local (destructive)
```

### Step 5: Update TypeScript Types

Update `src/types/database.ts` to match new schema.

## Common Migration Patterns

### Add New Table

```sql
-- NNN_create_tags.sql
CREATE TABLE tags (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  person_id UUID NOT NULL REFERENCES people(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  color TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Enable RLS
ALTER TABLE tags ENABLE ROW LEVEL SECURITY;

-- RLS policies
CREATE POLICY "Users can manage own tags" ON tags
  FOR ALL USING (auth.uid() = user_id);

-- Index for common queries
CREATE INDEX idx_tags_person_id ON tags(person_id);
CREATE INDEX idx_tags_user_id ON tags(user_id);
```

### Add Column

```sql
-- NNN_add_notes_to_people.sql
ALTER TABLE people ADD COLUMN notes TEXT;
```

### Add Foreign Key

```sql
-- NNN_add_category_to_analyses.sql
ALTER TABLE analyses ADD COLUMN category_id UUID REFERENCES categories(id);
CREATE INDEX idx_analyses_category_id ON analyses(category_id);
```

### Data Migration

```sql
-- NNN_backfill_risk_levels.sql
UPDATE analyses
SET risk_level = CASE
  WHEN toxicity_score < 4 THEN 'low'
  WHEN toxicity_score < 7 THEN 'moderate'
  ELSE 'high'
END
WHERE risk_level IS NULL;
```

## RLS Policy Patterns

### User Can Only See Own Data
```sql
CREATE POLICY "Users can view own data" ON table_name
  FOR SELECT USING (auth.uid() = user_id);
```

### User Can Insert Own Data
```sql
CREATE POLICY "Users can insert own data" ON table_name
  FOR INSERT WITH CHECK (auth.uid() = user_id);
```

### User Can Update Own Data
```sql
CREATE POLICY "Users can update own data" ON table_name
  FOR UPDATE USING (auth.uid() = user_id);
```

### User Can Delete Own Data
```sql
CREATE POLICY "Users can delete own data" ON table_name
  FOR DELETE USING (auth.uid() = user_id);
```

## Existing ToxShield Schema

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `profiles` | User profiles | id, display_name, avatar_url |
| `people` | Tracked subjects | name, relationship, current_toxicity_score, current_risk_level, is_toxic |
| `analyses` | AI analysis results | toxicity_score, detected_traits (JSONB), pattern_analysis, protection_strategies (JSONB) |
| `inputs` | Source data | input_type, content, raw_file_url, metadata (JSONB) |

## Safety Checklist

Before applying to production:
- [ ] Migration tested locally
- [ ] RLS policies added for new tables
- [ ] Indexes added for foreign keys and common queries
- [ ] TypeScript types updated in `src/types/database.ts`
- [ ] No data loss operations without backup
- [ ] Large table operations batched if needed

## File Naming Convention

Sequential numbering: `NNN_description.sql`
- `006_add_tags_table.sql`
- `007_add_sharing_tokens.sql`
