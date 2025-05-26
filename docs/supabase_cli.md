# Supabase Migration Flow for Solo Devs

## 1. Install Supabase CLI

```bash
brew install supabase/tap/supabase
```

## 2. Login & Initialize Supabase in Your Project Directory

Go to your project folder and run:

```bash
supabase login
```

Then:

```bash
supabase init
```

This sets up a `supabase/` folder (with config and, later, migration files).

## 3. Link to Your Supabase Project

You need your **project ref** (find it in the project’s dashboard URL or settings, looks like `abcd1234`):

```bash
supabase link --project-ref <your-project-ref>
```

This tells the CLI which project to use by default.

## 4. Pull Current Schema Into Migration Files (if you have tables already)

If you created tables in the dashboard already:

```bash
supabase db pull
```

This will:

- Generate SQL files in `supabase/migrations/`
- These files represent your current schema
- **Commit these to git!**

## 5. Make Schema Changes Using Migrations

1. **Create a new migration:**

   ```bash
   supabase migration new add_profiles_table
   ```

   This will make a new `.sql` file in `supabase/migrations/`.

2. **Edit that file** with your schema changes.
   Example to add a `profiles` table:

   ```sql
   CREATE TABLE profiles (
     id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
     user_id uuid NOT NULL,
     bio text
   );
   ```

3. **Apply it to your database:**

   ```bash
   supabase db push
   ```

   This runs the migration on your connected Supabase project.

## 6. Check Everything Works

- Use the **Supabase dashboard** to see your new table/column/etc.
- Run your app to make sure nothing broke.

## 7. Repeat for All Future Schema Changes

- Every time you add or change something:

  - Create a migration: `supabase migration new <description>`
  - Edit migration SQL
  - Apply with: `supabase db push`
  - Test

## 8. Good Practices Even When Solo

- **Always pull the latest schema** (`supabase db pull`) if you make changes in the Dashboard directly (but CLI is better!).
- **Keep migrations small:** 1 change per file if possible.
- **Commit migration files to git:** So you can always track what changed, when, and why.
- **Supabase dashboard** has backups (on paid plans) and you can export your schema/data.
- You can manually tweak or roll back changes by editing migrations or applying the “reverse” SQL.

## Real-World Example Flow

1. You want to add a `profile_picture` column to `profiles`.

   ```bash
   supabase migration new add_profile_picture
   ```

   In the new SQL file:

   ```sql
   ALTER TABLE profiles ADD COLUMN profile_picture text;
   ```

   Apply it:

   ```bash
   supabase db push
   ```

2. Now you want to remove a column?

   - New migration file:

   ```sql
   ALTER TABLE profiles DROP COLUMN profile_picture;
   ```

   - Push again.

## Handy Commands Cheat Sheet

| Task                         | Command                             |
| ---------------------------- | ----------------------------------- |
| Login to Supabase            | `supabase login`                    |
| Init project config          | `supabase init`                     |
| Link to your project         | `supabase link --project-ref <ref>` |
| Pull current db schema       | `supabase db pull`                  |
| Create a new migration file  | `supabase migration new <desc>`     |
| Apply all pending migrations | `supabase db push`                  |
| See current migrations       | `ls supabase/migrations/`           |
