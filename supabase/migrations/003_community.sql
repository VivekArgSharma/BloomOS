alter table public.profiles
  add column if not exists username text,
  add column if not exists avatar_url text,
  add column if not exists bio text,
  add column if not exists is_public boolean not null default true,
  add column if not exists updated_at timestamptz not null default now();

create unique index if not exists profiles_username_idx on public.profiles (lower(username)) where username is not null;

create table if not exists public.community_posts (
  id uuid primary key default gen_random_uuid(),
  author_id uuid not null references auth.users (id) on delete cascade,
  body text not null check (char_length(trim(body)) between 1 and 2000),
  image_url text check (image_url is null or image_url ~ '^https://'),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.community_comments (
  id uuid primary key default gen_random_uuid(),
  post_id uuid not null references public.community_posts (id) on delete cascade,
  author_id uuid not null references auth.users (id) on delete cascade,
  body text not null check (char_length(trim(body)) between 1 and 1000),
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.community_post_likes (
  post_id uuid not null references public.community_posts (id) on delete cascade,
  user_id uuid not null references auth.users (id) on delete cascade,
  created_at timestamptz not null default now(),
  primary key (post_id, user_id)
);

create index if not exists community_posts_created_at_idx on public.community_posts (created_at desc);
create index if not exists community_posts_author_created_idx on public.community_posts (author_id, created_at desc);
create index if not exists community_comments_post_created_idx on public.community_comments (post_id, created_at asc);
create index if not exists community_post_likes_user_idx on public.community_post_likes (user_id);

alter table public.profiles enable row level security;
alter table public.community_posts enable row level security;
alter table public.community_comments enable row level security;
alter table public.community_post_likes enable row level security;

drop policy if exists "Profiles are readable by authenticated users" on public.profiles;
create policy "Profiles are readable by authenticated users"
on public.profiles for select to authenticated
using (is_public or auth.uid() = id);

drop policy if exists "Users manage own profile" on public.profiles;
create policy "Users manage own profile"
on public.profiles for all to authenticated
using (auth.uid() = id)
with check (auth.uid() = id);

drop policy if exists "Authenticated users read community posts" on public.community_posts;
create policy "Authenticated users read community posts"
on public.community_posts for select to authenticated
using (true);

drop policy if exists "Users create own community posts" on public.community_posts;
create policy "Users create own community posts"
on public.community_posts for insert to authenticated
with check (auth.uid() = author_id);

drop policy if exists "Users update own community posts" on public.community_posts;
create policy "Users update own community posts"
on public.community_posts for update to authenticated
using (auth.uid() = author_id)
with check (auth.uid() = author_id);

drop policy if exists "Users delete own community posts" on public.community_posts;
create policy "Users delete own community posts"
on public.community_posts for delete to authenticated
using (auth.uid() = author_id);

drop policy if exists "Authenticated users read community comments" on public.community_comments;
create policy "Authenticated users read community comments"
on public.community_comments for select to authenticated
using (true);

drop policy if exists "Users create own community comments" on public.community_comments;
create policy "Users create own community comments"
on public.community_comments for insert to authenticated
with check (auth.uid() = author_id);

drop policy if exists "Users update own community comments" on public.community_comments;
create policy "Users update own community comments"
on public.community_comments for update to authenticated
using (auth.uid() = author_id)
with check (auth.uid() = author_id);

drop policy if exists "Users delete own community comments" on public.community_comments;
create policy "Users delete own community comments"
on public.community_comments for delete to authenticated
using (auth.uid() = author_id);

drop policy if exists "Authenticated users read community likes" on public.community_post_likes;
create policy "Authenticated users read community likes"
on public.community_post_likes for select to authenticated
using (true);

drop policy if exists "Users create own community likes" on public.community_post_likes;
create policy "Users create own community likes"
on public.community_post_likes for insert to authenticated
with check (auth.uid() = user_id);

drop policy if exists "Users delete own community likes" on public.community_post_likes;
create policy "Users delete own community likes"
on public.community_post_likes for delete to authenticated
using (auth.uid() = user_id);
