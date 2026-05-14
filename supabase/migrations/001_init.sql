create extension if not exists pgcrypto;

create table if not exists public.profiles (
  id uuid primary key references auth.users (id) on delete cascade,
  name text,
  city text,
  created_at timestamptz not null default now()
);

create table if not exists public.gardens (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users (id) on delete cascade,
  name text not null,
  location_type text not null,
  city text,
  latitude double precision,
  longitude double precision,
  created_at timestamptz not null default now()
);

create table if not exists public.plants (
  id uuid primary key default gen_random_uuid(),
  garden_id uuid not null references public.gardens (id) on delete cascade,
  common_name text not null,
  species_name text not null,
  source text not null default 'catalog',
  care_profile jsonb not null,
  current_health_score integer not null default 8,
  recovery_mode boolean not null default false,
  added_at timestamptz not null default now()
);

create table if not exists public.daily_logs (
  id uuid primary key default gen_random_uuid(),
  plant_id uuid not null references public.plants (id) on delete cascade,
  photo_url text not null,
  observations text,
  analysis_json jsonb not null,
  created_at timestamptz not null default now()
);

create table if not exists public.daily_plans (
  id uuid primary key default gen_random_uuid(),
  plant_id uuid not null references public.plants (id) on delete cascade,
  date date not null,
  tasks jsonb not null,
  weather_snapshot jsonb not null,
  generated_by_ai boolean not null default true,
  unique (plant_id, date)
);

create table if not exists public.plant_catalog (
  id uuid primary key default gen_random_uuid(),
  common_name text not null,
  species_name text not null,
  difficulty text not null,
  tags text[] not null default '{}',
  care_profile jsonb not null,
  created_at timestamptz not null default now()
);

alter table public.gardens enable row level security;
alter table public.plants enable row level security;
alter table public.daily_logs enable row level security;
alter table public.daily_plans enable row level security;

create policy "Users access own gardens"
on public.gardens for all
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

create policy "Users access own plants"
on public.plants for all
using (
  exists (
    select 1 from public.gardens
    where public.gardens.id = public.plants.garden_id
      and public.gardens.user_id = auth.uid()
  )
)
with check (
  exists (
    select 1 from public.gardens
    where public.gardens.id = public.plants.garden_id
      and public.gardens.user_id = auth.uid()
  )
);

create policy "Users access own logs"
on public.daily_logs for all
using (
  exists (
    select 1 from public.plants
    join public.gardens on public.gardens.id = public.plants.garden_id
    where public.plants.id = public.daily_logs.plant_id
      and public.gardens.user_id = auth.uid()
  )
)
with check (
  exists (
    select 1 from public.plants
    join public.gardens on public.gardens.id = public.plants.garden_id
    where public.plants.id = public.daily_logs.plant_id
      and public.gardens.user_id = auth.uid()
  )
);

create policy "Users access own plans"
on public.daily_plans for all
using (
  exists (
    select 1 from public.plants
    join public.gardens on public.gardens.id = public.plants.garden_id
    where public.plants.id = public.daily_plans.plant_id
      and public.gardens.user_id = auth.uid()
  )
)
with check (
  exists (
    select 1 from public.plants
    join public.gardens on public.gardens.id = public.plants.garden_id
    where public.plants.id = public.daily_plans.plant_id
      and public.gardens.user_id = auth.uid()
  )
);
