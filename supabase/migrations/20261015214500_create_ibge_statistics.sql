create table if not exists public.ibge_statistics (
    id uuid primary key default gen_random_uuid(),
    user_id uuid not null references auth.users (id) on delete cascade,
    total_municipios integer not null check (total_municipios >= 0),
    total_ok integer not null check (total_ok >= 0),
    total_nao_encontrado integer not null check (total_nao_encontrado >= 0),
    total_ambiguo integer not null check (total_ambiguo >= 0),
    total_erro_api integer not null check (total_erro_api >= 0),
    pop_total_ok bigint not null check (pop_total_ok >= 0),
    medias_por_regiao jsonb not null
        check (jsonb_typeof(medias_por_regiao) = 'object'),
    stats jsonb not null
        check (jsonb_typeof(stats) = 'object'),
    created_at timestamptz not null default now(),
    constraint ibge_statistics_status_totals_match
        check (
            total_municipios =
            total_ok + total_nao_encontrado + total_ambiguo + total_erro_api
        )
);

-- Upgrade tables created earlier with only id, stats, and created_at.
alter table public.ibge_statistics
    add column if not exists user_id uuid references auth.users (id) on delete cascade,
    add column if not exists total_municipios integer not null default 0,
    add column if not exists total_ok integer not null default 0,
    add column if not exists total_nao_encontrado integer not null default 0,
    add column if not exists total_ambiguo integer not null default 0,
    add column if not exists total_erro_api integer not null default 0,
    add column if not exists pop_total_ok bigint not null default 0,
    add column if not exists medias_por_regiao jsonb not null default '{}'::jsonb,
    add column if not exists stats jsonb not null default '{}'::jsonb,
    add column if not exists created_at timestamptz not null default now();

-- The existing table was empty before this migration, so no user ownership is lost.
alter table public.ibge_statistics
    alter column user_id set not null;

do $$
begin
    if not exists (
        select 1
        from pg_constraint
        where conrelid = 'public.ibge_statistics'::regclass
          and conname = 'ibge_statistics_total_municipios_check'
    ) then
        alter table public.ibge_statistics
            add constraint ibge_statistics_total_municipios_check
            check (total_municipios >= 0);
    end if;
    if not exists (
        select 1
        from pg_constraint
        where conrelid = 'public.ibge_statistics'::regclass
          and conname = 'ibge_statistics_total_ok_check'
    ) then
        alter table public.ibge_statistics
            add constraint ibge_statistics_total_ok_check
            check (total_ok >= 0);
    end if;
    if not exists (
        select 1
        from pg_constraint
        where conrelid = 'public.ibge_statistics'::regclass
          and conname = 'ibge_statistics_total_nao_encontrado_check'
    ) then
        alter table public.ibge_statistics
            add constraint ibge_statistics_total_nao_encontrado_check
            check (total_nao_encontrado >= 0);
    end if;
    if not exists (
        select 1
        from pg_constraint
        where conrelid = 'public.ibge_statistics'::regclass
          and conname = 'ibge_statistics_total_ambiguo_check'
    ) then
        alter table public.ibge_statistics
            add constraint ibge_statistics_total_ambiguo_check
            check (total_ambiguo >= 0);
    end if;
    if not exists (
        select 1
        from pg_constraint
        where conrelid = 'public.ibge_statistics'::regclass
          and conname = 'ibge_statistics_total_erro_api_check'
    ) then
        alter table public.ibge_statistics
            add constraint ibge_statistics_total_erro_api_check
            check (total_erro_api >= 0);
    end if;
    if not exists (
        select 1
        from pg_constraint
        where conrelid = 'public.ibge_statistics'::regclass
          and conname = 'ibge_statistics_pop_total_ok_check'
    ) then
        alter table public.ibge_statistics
            add constraint ibge_statistics_pop_total_ok_check
            check (pop_total_ok >= 0);
    end if;
    if not exists (
        select 1
        from pg_constraint
        where conrelid = 'public.ibge_statistics'::regclass
          and conname = 'ibge_statistics_medias_por_regiao_check'
    ) then
        alter table public.ibge_statistics
            add constraint ibge_statistics_medias_por_regiao_check
            check (jsonb_typeof(medias_por_regiao) = 'object');
    end if;
    if not exists (
        select 1
        from pg_constraint
        where conrelid = 'public.ibge_statistics'::regclass
          and conname = 'ibge_statistics_stats_check'
    ) then
        alter table public.ibge_statistics
            add constraint ibge_statistics_stats_check
            check (jsonb_typeof(stats) = 'object');
    end if;
    if not exists (
        select 1
        from pg_constraint
        where conrelid = 'public.ibge_statistics'::regclass
          and conname = 'ibge_statistics_status_totals_match'
    ) then
        alter table public.ibge_statistics
            add constraint ibge_statistics_status_totals_match
            check (
                total_municipios =
                total_ok + total_nao_encontrado + total_ambiguo + total_erro_api
            );
    end if;
end
$$;

create index if not exists ibge_statistics_user_created_at_idx
    on public.ibge_statistics (user_id, created_at desc);

alter table public.ibge_statistics enable row level security;

revoke all on public.ibge_statistics from anon, authenticated;
grant select, insert on public.ibge_statistics to authenticated;

drop policy if exists "Users can insert their own IBGE statistics"
    on public.ibge_statistics;
create policy "Users can insert their own IBGE statistics"
    on public.ibge_statistics
    for insert
    to authenticated
    with check (user_id = (select auth.uid()));

drop policy if exists "Users can read their own IBGE statistics"
    on public.ibge_statistics;
create policy "Users can read their own IBGE statistics"
    on public.ibge_statistics
    for select
    to authenticated
    using (user_id = (select auth.uid()));
