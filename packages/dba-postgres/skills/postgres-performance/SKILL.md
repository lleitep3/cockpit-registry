---
name: postgres-performance
description: Investiga lentidão, locks, índices, autovacuum e capacidade PostgreSQL usando janelas, planos e workload representativo. Use em diagnóstico e propostas de otimização; não prescreve tuning por receita ou aplica mudanças automaticamente.
---
# Performance PostgreSQL

Siga [investigação](../dba-postgres/references/performance.md) e
`~/.cockpit/packages/dba-postgres/kb/guides/postgres-performance.md`.

Fixe sintoma/SLO e janela. Colete baseline com dba-postgres. Correlacione métricas
aplicacionais (newrelic-analyzer se disponível) com consulta, espera e recursos do banco.
Separar latência média de cauda; throughput de duração; cache de disco físico;
estimativas de linhas de contagens reais; locks de CPU/IO. Não assumir causalidade.

Inspecione plano estimado sanitizado antes de executar a consulta. EXPLAIN ANALYZE
executa: só com autorização de execução e orçamento de carga, preferencialmente
em clone representativo. ROLLBACK não garante reversão de efeitos externos/sequence.

Sem reset conhecido/janela representativa, zero idx_scan não autoriza DROP INDEX.
Bloat requer medição específica; n_dead_tup não é percentual de disco desperdiçado.
Cada proposta deve ter evidência, confiança, benefício esperado, custo de escrita,
lock/IO, experimento, critério de aceite e rollback. Uma mudança por experimento.
