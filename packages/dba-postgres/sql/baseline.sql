\set ON_ERROR_STOP on
BEGIN ISOLATION LEVEL REPEATABLE READ READ ONLY;
SET LOCAL search_path = pg_catalog;
SET LOCAL statement_timeout = '10s';
SET LOCAL lock_timeout = '2s';
SET LOCAL idle_in_transaction_session_timeout = '15s';
WITH relations AS (
 SELECT c.*, n.nspname FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
 WHERE n.nspname=:'schema' AND c.relkind IN ('r','p')
), tables AS (
 SELECT c.relname AS name, c.relkind, c.relispartition AS is_partition,
 c.relrowsecurity AS row_security,
 pg_total_relation_size(c.oid) AS total_bytes, pg_indexes_size(c.oid) AS index_bytes,
 s.n_live_tup, s.n_dead_tup, s.seq_scan, s.idx_scan,
 s.last_autovacuum, s.last_autoanalyze
 FROM relations c LEFT JOIN pg_stat_all_tables s ON s.relid=c.oid
 ORDER BY c.relname LIMIT 5000
), columns AS (
 SELECT c.relname AS table_name, a.attname AS name,
 format_type(a.atttypid,a.atttypmod) AS type, a.attnotnull AS required,
 EXISTS(SELECT 1 FROM pg_constraint k WHERE k.conrelid=c.oid
 AND k.contype='p' AND a.attnum=ANY(k.conkey)) AS primary_key
 FROM relations c JOIN pg_attribute a ON a.attrelid=c.oid
 WHERE a.attnum>0 AND NOT a.attisdropped ORDER BY c.relname,a.attnum LIMIT 50000
), constraints AS (
 SELECT c.relname AS table_name,k.conname AS name,k.contype AS type,
 k.convalidated AS validated,k.confmatchtype AS match_type,
 p.relname AS parent,pn.nspname AS parent_schema,
 ARRAY(SELECT a.attname::text FROM unnest(k.conkey) WITH ORDINALITY x(num,ord)
 JOIN pg_attribute a ON a.attrelid=k.conrelid AND a.attnum=x.num ORDER BY x.ord) AS columns,
 ARRAY(SELECT a.attname::text FROM unnest(k.confkey) WITH ORDINALITY x(num,ord)
 JOIN pg_attribute a ON a.attrelid=k.confrelid AND a.attnum=x.num ORDER BY x.ord) AS parent_columns
 FROM relations c JOIN pg_constraint k ON k.conrelid=c.oid
 LEFT JOIN pg_class p ON p.oid=k.confrelid LEFT JOIN pg_namespace pn ON pn.oid=p.relnamespace
 ORDER BY c.relname,k.conname LIMIT 50000
), indexes AS (
 SELECT c.relname AS table_name,ic.relname AS name,am.amname AS method,
 i.indisunique AS is_unique,i.indisvalid AS valid,i.indisready AS ready,
 i.indpred IS NOT NULL AS partial,i.indexprs IS NOT NULL AS expressions,
 ARRAY(SELECT a.attname::text FROM unnest(i.indkey) WITH ORDINALITY x(num,ord)
 LEFT JOIN pg_attribute a ON a.attrelid=c.oid AND a.attnum=x.num
 WHERE x.ord<=i.indnkeyatts ORDER BY x.ord) AS columns,
 s.idx_scan,pg_relation_size(ic.oid) AS bytes
 FROM relations c JOIN pg_index i ON i.indrelid=c.oid
 JOIN pg_class ic ON ic.oid=i.indexrelid JOIN pg_am am ON am.oid=ic.relam
 LEFT JOIN pg_stat_all_indexes s ON s.indexrelid=ic.oid
 ORDER BY c.relname,ic.relname LIMIT 50000
)
SELECT json_build_object(
 'format_version',1,'collected_at',clock_timestamp(),'schema',:'schema',
 'database',current_database(),'server_version_num',current_setting('server_version_num')::int,
 'in_recovery',pg_is_in_recovery(),'track_counts',current_setting('track_counts'),
 'database_stats',(SELECT json_build_object('stats_reset',stats_reset,'deadlocks',deadlocks,
 'temp_bytes',temp_bytes,'blks_read',blks_read,'blks_hit',blks_hit,
 'xact_commit',xact_commit,'xact_rollback',xact_rollback)
 FROM pg_stat_database WHERE datname=current_database()),
 'activity',(SELECT json_build_object('visible_sessions',count(*),
 'unknown_state',count(*) FILTER(WHERE state IS NULL),
 'waiting_on_lock',count(*) FILTER(WHERE wait_event_type='Lock'),
 'idle_in_transaction',count(*) FILTER(WHERE state='idle in transaction'))
 FROM pg_stat_activity WHERE datname=current_database() AND pid<>pg_backend_pid()),
 'pg_stat_statements_installed',EXISTS(SELECT 1 FROM pg_extension WHERE extname='pg_stat_statements'),
 'tables',COALESCE((SELECT json_agg(t) FROM tables t),'[]'::json),
 'columns',COALESCE((SELECT json_agg(t) FROM columns t),'[]'::json),
 'constraints',COALESCE((SELECT json_agg(t) FROM constraints t),'[]'::json),
 'indexes',COALESCE((SELECT json_agg(t) FROM indexes t),'[]'::json));
COMMIT;
