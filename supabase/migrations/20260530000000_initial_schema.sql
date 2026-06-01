-- =============================================================================
-- AI Career Copilot — Initial Schema
-- Migration: 20260530000000_initial_schema.sql
--
-- Tables
--   profiles                    — extended user info (1:1 with auth.users)
--   resumes                     — one row per uploaded PDF, supports version history
--   extracted_skills            — per-skill rows with confidence for analytics
--   jd_matches                  — full result of a Resume ↔ JD comparison
--   job_recommendation_sessions — one row per /recommend-jobs call
--   job_recommendations         — individual jobs returned in a session
--   saved_jobs                  — user-bookmarked jobs
--   skill_gap_analyses          — results of /skill-gap calls
--   ats_scores                  — future ATS scoring (schema defined now)
--
-- RLS is enabled on every table. Users own their rows exclusively.
-- The backend service role bypasses RLS — user_id is always set explicitly.
-- =============================================================================


-- =============================================================================
-- EXTENSIONS
-- =============================================================================

-- pgcrypto supplies gen_random_uuid() used for primary keys
create extension if not exists pgcrypto;


-- =============================================================================
-- TABLE: profiles
-- One row per authenticated user. Created automatically via trigger on signup.
-- Stores display info that auth.users does not carry.
-- =============================================================================

create table public.profiles (
  -- Primary key mirrors auth.users.id for a guaranteed 1-to-1 relationship.
  id           uuid        not null references auth.users (id) on delete cascade,
  full_name    text,
  avatar_url   text,
  created_at   timestamptz not null default now(),
  updated_at   timestamptz not null default now(),

  constraint profiles_pkey primary key (id)
);

comment on table public.profiles is
  'Extended user profile — created automatically when a user signs up.';

-- Index on id is provided by the primary key; no extra index needed.


-- =============================================================================
-- TRIGGER: auto-create profile on signup
-- =============================================================================

create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer          -- runs with definer's privileges so it can write to profiles
set search_path = public  -- pin search_path to prevent privilege escalation
as $$
begin
  insert into public.profiles (id, full_name, avatar_url)
  values (
    new.id,
    new.raw_user_meta_data ->> 'full_name',
    new.raw_user_meta_data ->> 'avatar_url'
  );
  return new;
end;
$$;

create trigger on_auth_user_created
  after insert on auth.users
  for each row
  execute procedure public.handle_new_user();


-- =============================================================================
-- TRIGGER: keep updated_at current on profiles
-- =============================================================================

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

create trigger profiles_set_updated_at
  before update on public.profiles
  for each row
  execute procedure public.set_updated_at();


-- =============================================================================
-- TABLE: resumes
-- One row per file upload. Multiple rows per user = version history.
-- The `is_active` flag marks the resume used for new analyses.
-- Files are stored in Supabase Storage at resumes/{user_id}/{id}.pdf
-- =============================================================================

create table public.resumes (
  id                uuid        not null default gen_random_uuid(),
  user_id           uuid        not null references auth.users (id) on delete cascade,

  -- File metadata
  original_filename text        not null,
  storage_path      text        not null,            -- full path inside the 'resumes' bucket
  file_size_bytes   int,
  file_hash         text,                            -- MD5 of file bytes, for dedup detection

  -- Extracted data (denormalised for fast dashboard queries)
  skills            text[]      not null default '{}',
  total_skills      int         not null default 0,

  -- Version management
  version           int         not null default 1,
  is_active         boolean     not null default true, -- latest active resume for this user

  uploaded_at       timestamptz not null default now(),

  constraint resumes_pkey primary key (id)
);

comment on table public.resumes is
  'One row per uploaded PDF. Supports version history. '
  'skills[] is denormalised here for fast reads; full confidence data is in extracted_skills.';
comment on column public.resumes.storage_path is
  'Path inside the ''resumes'' storage bucket. Convention: resumes/{user_id}/{id}.pdf';
comment on column public.resumes.is_active is
  'True for the most recent resume. Set to false when a newer upload replaces it.';

create index resumes_user_id_idx     on public.resumes (user_id);
create index resumes_user_active_idx on public.resumes (user_id, is_active)
  where is_active = true;           -- partial index — fast lookup of current resume


-- =============================================================================
-- TABLE: extracted_skills
-- Granular per-skill rows extracted from a resume.
-- Enables analytics: "how many users know Python?", skill trend queries, etc.
-- The confidence value comes from rag_pipeline.extract_technical_skills().
-- =============================================================================

create table public.extracted_skills (
  id          uuid        not null default gen_random_uuid(),
  resume_id   uuid        not null references public.resumes (id) on delete cascade,
  user_id     uuid        not null references auth.users (id) on delete cascade,

  skill_name  text        not null,
  confidence  numeric(4, 2) not null default 0.0
                check (confidence >= 0 and confidence <= 1),

  -- 'skill_section' | 'faiss' — which pipeline pass found this skill
  source      text        not null default 'faiss',

  created_at  timestamptz not null default now(),

  constraint extracted_skills_pkey primary key (id),
  -- Prevent duplicate skills per resume
  constraint extracted_skills_resume_skill_uniq unique (resume_id, skill_name)
);

comment on table public.extracted_skills is
  'Individual skill rows extracted from a resume with confidence scores. '
  'Enables per-skill analytics without parsing the resumes.skills array.';

create index extracted_skills_resume_id_idx on public.extracted_skills (resume_id);
create index extracted_skills_user_id_idx   on public.extracted_skills (user_id);
create index extracted_skills_name_idx      on public.extracted_skills (skill_name);


-- =============================================================================
-- TABLE: jd_matches
-- One row per /match-jd API call.
-- Stores the full MatchResult from scoring_engine.score_match().
-- =============================================================================

create table public.jd_matches (
  id                 uuid        not null default gen_random_uuid(),
  user_id            uuid        not null references auth.users (id) on delete cascade,
  resume_id          uuid        not null references public.resumes (id) on delete cascade,

  -- Input
  jd_title           text,                           -- optional label the user gave the JD
  jd_text            text        not null,            -- raw job description text

  -- Scoring output (mirrors MatchResult.to_dict())
  match_score        numeric(6, 4) not null           -- 0.0 – 1.0
                       check (match_score >= 0 and match_score <= 1),
  match_score_pct    text        not null,            -- e.g. "43.8%"
  confidence         text        not null             -- 'high' | 'medium' | 'low'
                       check (confidence in ('high', 'medium', 'low')),
  resume_skill_count int         not null default 0,
  jd_skill_count     int         not null default 0,

  -- Structured results
  jd_skills          text[]      not null default '{}',
  exact_matches      text[]      not null default '{}',
  semantic_matches   jsonb       not null default '[]',  -- [{resume_skill, jd_skill, similarity}]
  missing_skills     text[]      not null default '{}',
  partially_matched  text[]      not null default '{}',
  recommendations    text[]      not null default '{}',

  created_at         timestamptz not null default now(),

  constraint jd_matches_pkey primary key (id)
);

comment on table public.jd_matches is
  'Full result of one Resume ↔ JD comparison (scoring_engine.MatchResult). '
  'semantic_matches JSONB: [{resume_skill, jd_skill, similarity}].';

create index jd_matches_user_id_idx   on public.jd_matches (user_id);
create index jd_matches_resume_id_idx on public.jd_matches (resume_id);
create index jd_matches_score_idx     on public.jd_matches (user_id, match_score desc);


-- =============================================================================
-- TABLE: job_recommendation_sessions
-- One row per /recommend-jobs API call.
-- Groups individual job_recommendations rows so history is queryable by session.
-- =============================================================================

create table public.job_recommendation_sessions (
  id             uuid        not null default gen_random_uuid(),
  user_id        uuid        not null references auth.users (id) on delete cascade,
  resume_id      uuid        not null references public.resumes (id) on delete cascade,

  -- Search parameters used in this session
  search_query   text        not null default 'Machine Learning Engineer',
  location_filter text       not null default 'India',
  top_n          int         not null default 5,

  -- Summary (denormalised from resume at call time)
  resume_skills  text[]      not null default '{}',
  total_fetched  int         not null default 0,   -- total jobs Adzuna returned
  total_ranked   int         not null default 0,   -- jobs that passed scoring

  created_at     timestamptz not null default now(),

  constraint job_recommendation_sessions_pkey primary key (id)
);

comment on table public.job_recommendation_sessions is
  'One row per /recommend-jobs call. Parent of job_recommendations rows.';

create index job_rec_sessions_user_id_idx on public.job_recommendation_sessions (user_id);


-- =============================================================================
-- TABLE: job_recommendations
-- One row per ranked job inside a session.
-- Mirrors JobRecommendation.to_dict() from recommendation_engine.py.
-- =============================================================================

create table public.job_recommendations (
  id               uuid        not null default gen_random_uuid(),
  session_id       uuid        not null
                     references public.job_recommendation_sessions (id) on delete cascade,
  user_id          uuid        not null references auth.users (id) on delete cascade,

  -- Job data from Adzuna
  title            text        not null,
  company          text        not null,
  location         text        not null,
  redirect_url     text        not null,

  -- Scoring (match_score is 0-100 integer, per recommendation_engine)
  match_score      int         not null default 0
                     check (match_score >= 0 and match_score <= 100),
  matching_skills  text[]      not null default '{}',
  semantic_matches jsonb       not null default '[]',
  missing_skills   text[]      not null default '{}',
  recommendations  text[]      not null default '{}',

  rank             int         not null default 1,  -- position in the ranked list (1 = best)

  created_at       timestamptz not null default now(),

  constraint job_recommendations_pkey primary key (id)
);

comment on table public.job_recommendations is
  'Individual ranked job from a recommendation session. '
  'semantic_matches JSONB: [{resume_skill, jd_skill, similarity}].';

create index job_recs_session_id_idx on public.job_recommendations (session_id);
create index job_recs_user_id_idx    on public.job_recommendations (user_id);
create index job_recs_score_idx      on public.job_recommendations (user_id, match_score desc);


-- =============================================================================
-- TABLE: saved_jobs
-- User-bookmarked job listings. May come from a recommendation session or be
-- added manually. recommendation_id is nullable to support manual saves.
-- =============================================================================

create table public.saved_jobs (
  id                uuid        not null default gen_random_uuid(),
  user_id           uuid        not null references auth.users (id) on delete cascade,

  -- Optional back-reference to the recommendation row it was saved from
  recommendation_id uuid        references public.job_recommendations (id) on delete set null,

  -- Denormalised job data — kept here so the job is still visible if the
  -- recommendation session is deleted
  title             text        not null,
  company           text        not null,
  location          text        not null,
  match_score       int         not null default 0
                      check (match_score >= 0 and match_score <= 100),
  redirect_url      text        not null,

  notes             text,                             -- user's free-text notes
  saved_at          timestamptz not null default now(),

  -- A user cannot save the same job (by URL) twice
  constraint saved_jobs_pkey primary key (id),
  constraint saved_jobs_user_url_uniq unique (user_id, redirect_url)
);

comment on table public.saved_jobs is
  'Bookmarked jobs. Denormalises job fields so records survive session deletion.';

create index saved_jobs_user_id_idx on public.saved_jobs (user_id);


-- =============================================================================
-- TABLE: skill_gap_analyses
-- One row per /skill-gap API call.
-- Mirrors skill_gap_service.analyze() output.
-- =============================================================================

create table public.skill_gap_analyses (
  id              uuid        not null default gen_random_uuid(),
  user_id         uuid        not null references auth.users (id) on delete cascade,
  resume_id       uuid        not null references public.resumes (id) on delete cascade,

  -- Input
  jd_text         text,                     -- null means built-in MODERN_TECH_REFERENCE was used
  reference_used  text        not null default 'built_in'
                    check (reference_used in ('custom', 'built_in')),

  -- Output (mirrors SkillGapResponse)
  match_score     numeric(5, 2) not null default 0
                    check (match_score >= 0 and match_score <= 100),
  resume_skills   text[]      not null default '{}',
  missing_skills  text[]      not null default '{}',
  semantic_gaps   jsonb       not null default '[]',  -- [{resume_skill, jd_skill, similarity}]
  recommendations text[]      not null default '{}',
  category_tips   jsonb       not null default '{}',  -- {category: tip_string}

  created_at      timestamptz not null default now(),

  constraint skill_gap_analyses_pkey primary key (id)
);

comment on table public.skill_gap_analyses is
  'Result of /skill-gap analysis. jd_text is null when built-in reference JD was used.';

create index skill_gap_user_id_idx   on public.skill_gap_analyses (user_id);
create index skill_gap_resume_id_idx on public.skill_gap_analyses (resume_id);


-- =============================================================================
-- TABLE: ats_scores
-- Future ATS (Applicant Tracking System) resume scoring.
-- Schema defined now so foreign keys are clean when the feature is built.
-- =============================================================================

create table public.ats_scores (
  id              uuid        not null default gen_random_uuid(),
  user_id         uuid        not null references auth.users (id) on delete cascade,
  resume_id       uuid        not null references public.resumes (id) on delete cascade,

  target_role     text,                     -- job title the ATS score is evaluated against
  ats_score       int         not null default 0
                    check (ats_score >= 0 and ats_score <= 100),
  format_score    int         not null default 0
                    check (format_score >= 0 and format_score <= 100),
  keyword_score   int         not null default 0
                    check (keyword_score >= 0 and keyword_score <= 100),
  clarity_score   int         not null default 0
                    check (clarity_score >= 0 and clarity_score <= 100),
  length_score    int         not null default 0
                    check (length_score >= 0 and length_score <= 100),
  feedback        jsonb       not null default '{}',  -- structured improvement notes

  created_at      timestamptz not null default now(),

  constraint ats_scores_pkey primary key (id)
);

comment on table public.ats_scores is
  'Future ATS scoring feature. Schema defined now; populated when feature is implemented.';

create index ats_scores_user_id_idx   on public.ats_scores (user_id);
create index ats_scores_resume_id_idx on public.ats_scores (resume_id);


-- =============================================================================
-- ROW LEVEL SECURITY
-- Every table is locked down so auth.uid() == user_id is the only way in.
-- The backend service role key bypasses RLS entirely — it always sets
-- user_id explicitly so no row is ever written without a valid owner.
-- =============================================================================


-- ── profiles ─────────────────────────────────────────────────────────────────
alter table public.profiles enable row level security;

-- Users can read their own profile
create policy "profiles: select own"
  on public.profiles for select
  using (auth.uid() = id);

-- Users can update their own profile (name, avatar)
create policy "profiles: update own"
  on public.profiles for update
  using (auth.uid() = id)
  with check (auth.uid() = id);

-- Insert is handled exclusively by the handle_new_user() trigger (security definer)
-- so no direct INSERT policy is needed for normal users.


-- ── resumes ──────────────────────────────────────────────────────────────────
alter table public.resumes enable row level security;

-- Users can list and read their own resumes (version history, skill dashboard)
create policy "resumes: select own"
  on public.resumes for select
  using (auth.uid() = user_id);

-- Users can upload a new resume row (backend also inserts via service role)
create policy "resumes: insert own"
  on public.resumes for insert
  with check (auth.uid() = user_id);

-- Users can soft-delete or update is_active flag on their own resumes
create policy "resumes: update own"
  on public.resumes for update
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

-- Users can delete their own resume records (cascades to skills, matches, etc.)
create policy "resumes: delete own"
  on public.resumes for delete
  using (auth.uid() = user_id);


-- ── extracted_skills ─────────────────────────────────────────────────────────
alter table public.extracted_skills enable row level security;

create policy "extracted_skills: select own"
  on public.extracted_skills for select
  using (auth.uid() = user_id);

create policy "extracted_skills: insert own"
  on public.extracted_skills for insert
  with check (auth.uid() = user_id);

create policy "extracted_skills: delete own"
  on public.extracted_skills for delete
  using (auth.uid() = user_id);


-- ── jd_matches ───────────────────────────────────────────────────────────────
alter table public.jd_matches enable row level security;

-- Analysis results are append-only — no UPDATE policy
create policy "jd_matches: select own"
  on public.jd_matches for select
  using (auth.uid() = user_id);

create policy "jd_matches: insert own"
  on public.jd_matches for insert
  with check (auth.uid() = user_id);

create policy "jd_matches: delete own"
  on public.jd_matches for delete
  using (auth.uid() = user_id);


-- ── job_recommendation_sessions ──────────────────────────────────────────────
alter table public.job_recommendation_sessions enable row level security;

create policy "job_rec_sessions: select own"
  on public.job_recommendation_sessions for select
  using (auth.uid() = user_id);

create policy "job_rec_sessions: insert own"
  on public.job_recommendation_sessions for insert
  with check (auth.uid() = user_id);

create policy "job_rec_sessions: delete own"
  on public.job_recommendation_sessions for delete
  using (auth.uid() = user_id);


-- ── job_recommendations ───────────────────────────────────────────────────────
alter table public.job_recommendations enable row level security;

create policy "job_recs: select own"
  on public.job_recommendations for select
  using (auth.uid() = user_id);

create policy "job_recs: insert own"
  on public.job_recommendations for insert
  with check (auth.uid() = user_id);

create policy "job_recs: delete own"
  on public.job_recommendations for delete
  using (auth.uid() = user_id);


-- ── saved_jobs ────────────────────────────────────────────────────────────────
alter table public.saved_jobs enable row level security;

-- Saved jobs are the one table users actively manage (add notes, bookmark, remove)
create policy "saved_jobs: select own"
  on public.saved_jobs for select
  using (auth.uid() = user_id);

create policy "saved_jobs: insert own"
  on public.saved_jobs for insert
  with check (auth.uid() = user_id);

create policy "saved_jobs: update own"
  on public.saved_jobs for update
  using (auth.uid() = user_id)
  with check (auth.uid() = user_id);

create policy "saved_jobs: delete own"
  on public.saved_jobs for delete
  using (auth.uid() = user_id);


-- ── skill_gap_analyses ────────────────────────────────────────────────────────
alter table public.skill_gap_analyses enable row level security;

create policy "skill_gap: select own"
  on public.skill_gap_analyses for select
  using (auth.uid() = user_id);

create policy "skill_gap: insert own"
  on public.skill_gap_analyses for insert
  with check (auth.uid() = user_id);

create policy "skill_gap: delete own"
  on public.skill_gap_analyses for delete
  using (auth.uid() = user_id);


-- ── ats_scores ────────────────────────────────────────────────────────────────
alter table public.ats_scores enable row level security;

create policy "ats_scores: select own"
  on public.ats_scores for select
  using (auth.uid() = user_id);

create policy "ats_scores: insert own"
  on public.ats_scores for insert
  with check (auth.uid() = user_id);

create policy "ats_scores: delete own"
  on public.ats_scores for delete
  using (auth.uid() = user_id);


-- =============================================================================
-- STORAGE — private 'resumes' bucket
-- Files are stored at:  resumes/{user_id}/{resume_id}.pdf
-- The first segment of the path (foldername[1]) is the owner's user_id.
-- =============================================================================

-- Create the bucket (private, no public read)
insert into storage.buckets (id, name, public)
values ('resumes', 'resumes', false)
on conflict (id) do nothing;

-- Users can upload files only into their own folder
create policy "storage resumes: upload own"
  on storage.objects for insert
  with check (
    bucket_id = 'resumes'
    and auth.uid()::text = (storage.foldername(name))[1]
  );

-- Users can read files from their own folder (for signed URL generation)
create policy "storage resumes: read own"
  on storage.objects for select
  using (
    bucket_id = 'resumes'
    and auth.uid()::text = (storage.foldername(name))[1]
  );

-- Users can delete their own resume files
create policy "storage resumes: delete own"
  on storage.objects for delete
  using (
    bucket_id = 'resumes'
    and auth.uid()::text = (storage.foldername(name))[1]
  );
