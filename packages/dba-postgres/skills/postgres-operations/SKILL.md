---
name: postgres-operations
description: Planeja e conduz operação PostgreSQL, segurança, manutenção, backup/restauração, incidentes, replicação e upgrades com evidências e autorização do escopo. Use em tarefas de DBA operacional; não trata o laboratório Compose como arquitetura de produção nem automatiza ações destrutivas.
---
# Operação PostgreSQL

Leia a [matriz de atuação](../dba-postgres/references/dba-scope.md) e selecione o workflow.
Antes de agir: consultar KB, confirmar versão/ambiente/owner, mecanismo de acesso,
objetivo, autorização já existente, evidência e critério de sucesso. Reutilizar autorizações
da sessão; não pedir confirmações redundantes. Lacunas devem ser explícitas.

- Preparar local: [laboratório](../dba-postgres/references/local-lab.md).
- Rotina/saúde: [manutenção](../dba-postgres/references/maintenance.md).
- Privilégios/TLS/RLS: [segurança](../dba-postgres/references/security.md).
- Backup, restore e PITR: [recuperação](../dba-postgres/references/recovery.md).
- Indisponibilidade, disco/WAL e réplica: [incidente](../dba-postgres/references/incident.md).
- Mudança de versão: [upgrade](../dba-postgres/references/upgrade.md).

O CLI coleta metadados e gera laboratório; não executa manutenção, failover, restore
ou migração remota. Para execução autorizada, preparar comandos específicos da versão,
validar em clone, revisar impacto e seguir safe-change.md. Não confundir consulta somente
leitura com ausência de custo operacional. Reinício/failover muda disponibilidade;
restauração/exclusão muda dados. Confirmar apenas o que ainda não está autorizado.

Mapear responsabilidades com cloud-engineering/aws-expert para serviço gerenciado,
api-developer para migrations/consumidores e newrelic-analyzer para evidências da aplicação.
Não pressupor extensões, acesso a SO/superuser, backup do provedor ou réplica promovível.

Para qualquer DER ou diagrama, siga o [estilo visual padrão](../dba-postgres/references/diagram-style.md).
Use o exemplo genérico dessa referência; não incorporar schemas de clientes no pacote.
