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
