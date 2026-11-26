-- KOMAROVA_CORE · Supabase private media archive
-- Run in Supabase SQL Editor for the intended project.
-- This creates a private bucket and owner-scoped records. It does not migrate or delete existing data.

create table if not exists public.archive_items (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete restrict,
  material_id text not null unique,
  storage_path text not null unique,
  bucket_id text not null default 'komarova_core_private',
  original_filename text not null,
  title text,
  item_type text not null check (item_type in ('photo', 'video', 'audio', 'document')),
  mime_type text not null,
  size_bytes bigint not null check (size_bytes > 0),
  sha256 char(64) not null,
  original_material_id text,
  person_id text,
  event_id text,
  place_id text,
  record_status text not null default 'stored_original',
  created_at timestamptz not null default now()
);

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

alter table public.archive_items enable row level security;

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
