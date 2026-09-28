# Workflow: investigação de performance

1. Definir sintoma, SLO, operação, período, volume e baseline comparável.
2. Obter dois snapshots separados por carga representativa; não subtrair após reset,
   troca de servidor, recriação de objeto ou mudança de versão. CLI não calcula deltas.
3. Examinar atividade agregada, locks, transações longas, conexões e crescimento.
   A coleta padrão não captura bloqueadores individuais nem SQL: investigação extra
   deve permanecer limitada e sanitizada.
4. Se pg_stat_statements já existir, verificar versão da extensão, preload, acesso e
   instante de reset. Presença no catálogo não prova coleta funcional. Consultar
   agregados por queryid/dbid/userid/toplevel: calls, total_exec_time, rows, blocos,
   temporários. Não exportar query text por padrão; queryid sozinho não é chave global.
   Médias agregadas não fornecem p95/p99. Não habilitar/resetar extensão no diagnóstico.
5. Correlacionar top consumo total e latência com planos, estimativas/linhas reais,
   loops, sorts temporários e buffers. Sanitizar planos: podem conter literais.
6. Formular hipótese; testar uma alteração em clone/carga representativa; comparar
   mesmas consultas, parâmetros, concorrência e cache. Documentar efeitos colaterais.
7. Mudança aprovada segue safe-change.md. Após rollout verificar SLO, erro, locks,
   escrita e espaço no período definido. Reverter se critérios forem violados.

Não há regras universais de shared_buffers/work_mem, índices ou particionamento.
Considere memória por operação e concorrência, orçamento do host e pool de conexões.
