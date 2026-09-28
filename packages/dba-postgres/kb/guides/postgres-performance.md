# PostgreSQL: performance baseada em análise

Contexto: dba-postgres. Revisado em 2026-09-28; referência PostgreSQL 16.

Otimizar a operação que viola um objetivo mensurável. Capturar volume, concorrência,
parâmetros, distribuição e latência de cauda na aplicação. Uma média de banco não é p95.
Locks globais podem serializar tráfego; medir espera antes de particionar o lock.

EXPLAIN estimado descreve a estratégia; ANALYZE executa a consulta. Comparar estimativas,
linhas, loops e buffers para localizar a hipótese. Seq scan pode ser adequado em tabela
pequena ou baixa seletividade. Plano contém detalhes/literais: sanitizar antes de publicar.
[Uso de EXPLAIN](https://www.postgresql.org/docs/16/using-explain.html).

pg_stat_statements agrega chamadas/tempos/blocos por identidade de consulta. Verificar
instalação, preload, privilégios, versão e reset antes de interpretar. Custo total e custo
por chamada respondem a perguntas diferentes; não habilitar nem resetar implicitamente.
[pg_stat_statements](https://www.postgresql.org/docs/16/pgstatstatements.html).

Índices exigem leitura e escrita: avaliar seletividade, chaves líderes, predicado,
expressões e redundância real. Zero scans em uma janela curta não autoriza remoção.
Contadores podem não cobrir réplicas ou tarefas raras. O detector de FK deste pacote
procura somente B-tree completo válido; resultado é candidato para revisão, não erro.

n_dead_tup é estimativa de tuplas, não medida de bloat. VACUUM comum permite reutilizar
espaço; não é promessa de redução do arquivo no sistema operacional. Autovacuum depende
do workload e transações; não desabilitar como tuning genérico.
[Vacuum rotineiro](https://www.postgresql.org/docs/16/routine-vacuuming.html).

Sem planos/workload, não prescrever work_mem, shared_buffers, particionamento ou novo
índice. Medir benefício e efeitos sobre escrita, IO, memória e locks no experimento.
