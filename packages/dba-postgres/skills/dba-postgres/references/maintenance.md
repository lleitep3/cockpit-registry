# Workflow: manutenção e capacidade

Entrada: versão, topologia, SLO, criticidade, janela e histórico de métricas.

1. Coletar baseline e SQL operacional fixo, registrando permissões/ausências.
2. Conferir transações antigas, idade de freeze em relação aos parâmetros atuais,
   vacuum/analyze recentes e evolução de estimativas. Nunca interpretar n_dead_tup
   como espaço recuperável. Se houver risco de wraparound, priorizar runbook específico.
3. Analisar crescimento de tabelas/índices, WAL, arquivos temporários, slots e backups.
   Somar relações não mede disco provisionado. Definir margem e tendência, não limiar universal.
4. Revisar índices inválidos, estatísticas, bloat medido e consultas afetadas. Escolher
   vacuum/analyze/reindex somente com causa, orçamento de IO/locks e autorização.
5. Revisar conexões, pool, timeouts e memória por concorrência. Não copiar valores de
   laboratório para produção; pg_settings não descreve sozinho capacidade do host.
6. Definir frequência/owner/limiares adaptados e evidência de verificação. Este workflow
   não cria agendamento automático. Incluir restore periódico e teste de alertas.

Saída: plano por componente, impacto, critério de sucesso, recuperação e observação.
Consultar postgres-performance e postgres-operations KB antes de prescrever tuning.
