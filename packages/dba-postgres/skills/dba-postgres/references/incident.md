# Workflow: incidente, replicação e continuidade

1. Confirmar impacto, ambiente, início, owner e ações autorizadas. Preservar evidência;
   não reiniciar por reflexo, limpar WAL ou encerrar sessões indiscriminadamente.
2. Classificar: conectividade/autenticação, exaustão de conexão, locks, CPU/IO, disco/WAL,
   recuperação, réplica ou corrupção. Correlacionar banco, host/provedor e aplicação.
3. Locks: identificar bloqueador raiz, duração/transação e operação envolvida. Cancelar
   consulta e encerrar sessão têm efeitos distintos; avaliar rollback e autorizar ação.
4. Disco/WAL: medir espaço real, crescimento, archive failures e slots atrasados.
   Nunca apagar arquivos de pg_wal. Remover slot pode impedir retomada da réplica:
   depende de investigação e plano de ressincronização.
5. Replicação: distinguir envio, flush e replay; nulos/idle não significam zero atraso.
   Síncrona altera disponibilidade/latência. Identificar replication slots e consumidores.
6. Failover: comprovar papel dos nós, fencing do antigo primário, RPO aceito, destino de
   clientes e plano de retorno. Prevenir dois primários; promoção é ação autorizada,
   não teste inofensivo. Não automatizado por este pacote.
7. Depois: confirmar integridade, erro/latência e replicação. Postmortem com cronologia,
   causa demonstrada versus hipótese, ações/owners e teste preventivo.

Suspeita de corrupção: preservar logs/backups, isolar impacto e consultar runbook da
versão/provedor. Não usar pg_resetwal como recuperação rotineira.
