-- PostgreSQL 17 operational aggregates; no query text or credential settings.
\set ON_ERROR_STOP on
BEGIN READ ONLY;
SET LOCAL search_path = pg_catalog;
SET LOCAL statement_timeout = '10s';
SET LOCAL lock_timeout = '2s';
SELECT json_build_object(
 'collected_at',clock_timestamp(),
 'server_version_num',current_setting('server_version_num')::int,
 'in_recovery',pg_is_in_recovery(),
 'database_xid_age',(SELECT age(datfrozenxid) FROM pg_database WHERE datname=current_database()),
 'freeze_max_age',current_setting('autovacuum_freeze_max_age')::bigint,
 'max_connections',current_setting('max_connections')::int,
 'connections_cluster',(SELECT count(*) FROM pg_stat_activity),
 'active_cluster',(SELECT count(*) FROM pg_stat_activity WHERE state='active'),
 'unknown_state_cluster',(SELECT count(*) FROM pg_stat_activity WHERE state IS NULL),
 'oldest_xact_seconds',(SELECT extract(epoch FROM clock_timestamp()-min(xact_start)) FROM pg_stat_activity WHERE pid<>pg_backend_pid()),
 'lock_waiters_cluster',(SELECT count(*) FROM pg_stat_activity WHERE wait_event_type='Lock'),
 'replication_connections',(SELECT count(*) FROM pg_stat_replication),
 'slots_total',(SELECT count(*) FROM pg_replication_slots),
 'inactive_slots',(SELECT count(*) FROM pg_replication_slots WHERE NOT active),
 'archiver',(SELECT json_build_object('archived_count',archived_count,'failed_count',failed_count,
 'last_archived_time',last_archived_time,'last_failed_time',last_failed_time,'stats_reset',stats_reset) FROM pg_stat_archiver)
);
COMMIT;
