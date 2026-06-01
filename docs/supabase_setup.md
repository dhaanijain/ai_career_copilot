# Supabase Setup — AI Career Copilot

## Architecture Overview

```
Browser (Next.js)
  ├── @supabase/supabase-js  — Auth (JWT), direct DB reads via RLS
  └── Fetch API              — Calls FastAPI backend

FastAPI Backend
  ├── supabase-py (service role) — All DB writes, Storage uploads
  └── app/config/supabase.py     — Client factory
```

The backend always uses the **service role key** for writes. This bypasses RLS and
allows the backend to set `user_id` explicitly on every row — a safe, trusted server
pattern. The frontend uses the **anon key** with the user's JWT for reads, governed by RLS.

---

## Schema

### Tables

| Table | Rows represent | Rows deleted when |
|---|---|---|
| `profiles` | One per user | User deleted |
| `resumes` | One per PDF upload | Manually or user deleted |
| `extracted_skills` | One per skill per resume | Resume deleted (cascade) |
| `jd_matches` | One per /match-jd call | Manually or user deleted |
| `job_recommendation_sessions` | One per /recommend-jobs call | Manually or user deleted |
| `job_recommendations` | One per job in a session | Session deleted (cascade) |
| `saved_jobs` | User-bookmarked job | User removes bookmark |
| `skill_gap_analyses` | One per /skill-gap call | Manually or user deleted |
| `ats_scores` | One per ATS score run | Manually or user deleted |

### Key Relationships

```
auth.users
  └─ profiles            (1:1)
  └─ resumes             (1:N) — each upload is a new version
      └─ extracted_skills (1:N)
      └─ jd_matches       (1:N)
      └─ skill_gap_analyses (1:N)
      └─ ats_scores        (1:N)
      └─ job_recommendation_sessions (1:N)
          └─ job_recommendations (1:N)
              └─ saved_jobs (optional back-reference)
```

---

## Authentication Flow

```
1. User signs up → Supabase Auth creates auth.users row
2. on_auth_user_created trigger → inserts row into public.profiles
3. User receives JWT (access_token + refresh_token)
4. Frontend stores JWT in localStorage (auto-managed by supabase-js)
5. Frontend sends JWT in Authorization: Bearer <token> on every API call
6. FastAPI optional_user dependency validates JWT via Supabase auth.get_user()
7. If valid, user_id is extracted and passed to service layer
8. Service layer uses service role client to write rows with the correct user_id
```

---

## RLS Design

Every table has RLS enabled. The general rule: **users can only access rows where `user_id = auth.uid()`**.

- **profiles** — SELECT + UPDATE own row only (INSERT handled by trigger)
- **resumes** — SELECT + INSERT + UPDATE + DELETE own rows
- **extracted_skills / jd_matches / skill_gap_analyses / ats_scores** — SELECT + INSERT + DELETE (no UPDATE — append-only results)
- **saved_jobs** — SELECT + INSERT + UPDATE + DELETE (users manage their bookmarks)
- **storage.objects (resumes bucket)** — INSERT + SELECT + DELETE where `foldername[1] = auth.uid()`

The backend service role key bypasses all RLS — it is never sent to the browser.

---

## Storage Design

Bucket: **`resumes`** (private)

Path convention:
```
resumes/{user_id}/{resume_id}.pdf
```

The first path segment (`foldername[1]`) equals the owner's `user_id`, which makes
the storage RLS policies trivial and tamper-proof.

To generate a signed URL for a resume (valid 60 minutes):
```python
client.storage.from_("resumes").create_signed_url(storage_path, 3600)
```

---

## Environment Variables

### Backend (`.env` in project root)

| Variable | Description |
|---|---|
| `SUPABASE_URL` | `https://<ref>.supabase.co` |
| `SUPABASE_ANON_KEY` | Public anon key (safe, restricted by RLS) |
| `SUPABASE_SERVICE_ROLE_KEY` | Secret service role key — never expose to browser |
| `ADZUNA_APP_ID` | Adzuna Jobs API app ID |
| `ADZUNA_APP_KEY` | Adzuna Jobs API key |

### Frontend (`frontend/.env.local`)

| Variable | Description |
|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Same URL as backend |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Same anon key as backend |

Find these values: Supabase Dashboard → Project → Settings → API.

---

## Migration Commands

```bash
# Review what will be pushed (dry run)
supabase db push --dry-run

# Apply all pending migrations
supabase db push

# Check migration sync status
supabase migration list

# Create a new migration
supabase migration new <name>
```

---

## Local Development

1. Copy `.env.example` → `.env` and fill in all values.
2. Copy `frontend/.env.local` and fill in `NEXT_PUBLIC_` values.
3. Activate the Python venv: `venv\Scripts\activate`
4. Install Python deps: `pip install -r requirements.txt`
5. Start the backend: `uvicorn backend_api.main:app --reload`
6. Start the frontend: `cd frontend && npm run dev`

---

## Deployment Checklist

- [ ] `SUPABASE_SERVICE_ROLE_KEY` is in server environment only (not in any frontend env file)
- [ ] `frontend/.env.local` contains only `NEXT_PUBLIC_` prefixed vars
- [ ] RLS is enabled on all tables (`select relrowsecurity from pg_class where relname = 'resumes'`)
- [ ] Supabase Auth email confirmations configured (Settings → Auth)
- [ ] Supabase Storage `resumes` bucket is set to **private** (not public)
- [ ] Run `supabase migration list` to confirm Local == Remote for all migrations
