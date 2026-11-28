-- KOMAROVA_CORE · Supabase private media archive
-- Applied to Supabase project bcotusztvddzbnwefnrq as migration create_private_media_archive_v1.
-- Creates a private bucket and owner-scoped records. Does not migrate or delete archive data.

create table if not exists public.archive_items (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete restrict,
  material_id text not null unique,
  storage_path text not null unique,
  bucket_id text not null default 'komarova_core_private',
  original_filename text not null,
  title text,
  description text,
  captured_at timestamptz,
  item_type text not null check (item_type in ('photo', 'video', 'audio', 'document')),
  mime_type text not null,
  size_bytes bigint not null check (size_bytes > 0),
  sha256 char(64) not null check (sha256 ~ '^[0-9a-f]{64}
  original_material_id text,
  person_id text,
  event_id text,
  place_id text,
  record_status text not null default 'stored_original'
    check (record_status in ('stored_original', 'derived', 'quarantined', 'verified', 'rejected')),
  created_at timestamptz not null default now()
);

alter table public.archive_items add column if not exists description text;
alter table public.archive_items add column if not exists captured_at timestamptz;

create index if not exists archive_items_user_created_idx
  on public.archive_items (user_id, created_at desc);
create index if not exists archive_items_person_idx
  on public.archive_items (person_id);
create index if not exists archive_items_event_idx
  on public.archive_items (event_id);
create index if not exists archive_items_place_idx
  on public.archive_items (place_id);
create index if not exists archive_items_sha256_idx
  on public.archive_items (sha256);
create unique index if not exists archive_items_user_sha256_unique
  on public.archive_items (user_id, sha256);

alter table public.archive_items enable row level security;
grant select, insert on table public.archive_items to authenticated;

drop policy if exists "archive_items_select_own" on public.archive_items;
create policy "archive_items_select_own"
  on public.archive_items for select to authenticated
  using ((select auth.uid()) = user_id);

drop policy if exists "archive_items_insert_own" on public.archive_items;
create policy "archive_items_insert_own"
  on public.archive_items for insert to authenticated
  with check ((select auth.uid()) = user_id);

-- No UPDATE policy: original metadata cannot be silently overwritten from the public client.
-- No DELETE policy: archive records are not deletable from this first release.

insert into storage.buckets (id, name, public, file_size_limit)
values ('komarova_core_private', 'komarova_core_private', false, 52428800)
on conflict (id) do update
set public = false,
    file_size_limit = excluded.file_size_limit;

drop policy if exists "komarova_storage_select_own" on storage.objects;
create policy "komarova_storage_select_own"
  on storage.objects for select to authenticated
  using (
    bucket_id = 'komarova_core_private'
    and (storage.foldername(name))[1] = (select auth.uid())::text
  );

drop policy if exists "komarova_storage_insert_own" on storage.objects;
create policy "komarova_storage_insert_own"
  on storage.objects for insert to authenticated
  with check (
    bucket_id = 'komarova_core_private'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

-- No UPDATE policy: uploads use x-upsert=false and preserve originals.
-- No DELETE policy: deletion is deliberately withheld pending backup/restore controls.
),
  original_material_id text,
  person_id text,
  event_id text,
  place_id text,
  record_status text not null default 'stored_original',
  created_at timestamptz not null default now()
);

alter table public.archive_items add column if not exists description text;
alter table public.archive_items add column if not exists captured_at timestamptz;

create index if not exists archive_items_user_created_idx
  on public.archive_items (user_id, created_at desc);
create index if not exists archive_items_person_idx
  on public.archive_items (person_id);
create index if not exists archive_items_event_idx
  on public.archive_items (event_id);
create index if not exists archive_items_place_idx
  on public.archive_items (place_id);
create index if not exists archive_items_sha256_idx
  on public.archive_items (sha256);
create unique index if not exists archive_items_user_sha256_unique
  on public.archive_items (user_id, sha256);

alter table public.archive_items enable row level security;
grant select, insert on table public.archive_items to authenticated;

drop policy if exists "archive_items_select_own" on public.archive_items;
create policy "archive_items_select_own"
  on public.archive_items for select to authenticated
  using (user_id = auth.uid());

drop policy if exists "archive_items_insert_own" on public.archive_items;
create policy "archive_items_insert_own"
  on public.archive_items for insert to authenticated
  with check (user_id = auth.uid());

-- No UPDATE policy: original metadata cannot be silently overwritten from the public client.
-- No DELETE policy: archive records are not deletable from this first release.

insert into storage.buckets (id, name, public, file_size_limit)
values ('komarova_core_private', 'komarova_core_private', false, 52428800)
on conflict (id) do update
set public = false,
    file_size_limit = excluded.file_size_limit;

drop policy if exists "komarova_storage_select_own" on storage.objects;
create policy "komarova_storage_select_own"
  on storage.objects for select to authenticated
  using (
    bucket_id = 'komarova_core_private'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

drop policy if exists "komarova_storage_insert_own" on storage.objects;
create policy "komarova_storage_insert_own"
  on storage.objects for insert to authenticated
  with check (
    bucket_id = 'komarova_core_private'
    and (storage.foldername(name))[1] = auth.uid()::text
  );

-- No UPDATE policy: uploads use x-upsert=false and preserve originals.
-- No DELETE policy: deletion is deliberately withheld pending backup/restore controls.
