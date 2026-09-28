# Matriz de atuação DBA

O pacote orienta o ciclo completo de DBA PostgreSQL. Cobertura de instrução não
significa automação ou homologação de qualquer topologia. Ajustar à versão e ao serviço.

| Frente | Insumos e entrega | Caminho | Automação atual |
| --- | --- | --- | --- |
| Inventário/DER | Catálogo, versão, schema; mapa real | baseline.md | Coleta e DER |
| Modelagem/integridade | Invariantes, tenant, concorrência; modelo/migration | model-review.md | Revisão guiada |
| Performance | SLO, janela, planos, carga; experimento comparável | performance.md | Candidatos limitados de índice |
| Segurança | Roles, grants, HBA/TLS, RLS, classificação; matriz de acessos | security.md | Revisão guiada |
| Backup/DR | RPO/RTO, retenção, destino, restore; prova de recuperação | recovery.md | Ensaio manual local |
| Manutenção | Vacuum/analyze, freeze, índices, transações; plano de rotina | maintenance.md | SQL agregado auxiliar |
| Incidentes | Impacto, cronologia, locks, disco/WAL; mitigação e postmortem | incident.md | Coleta inicial |
| Replicação/HA | Topologia, lag, slots, fencing; plano de failover/retorno | incident.md | Sem failover automático |
| Upgrade/migração | Versões, extensões, collation, clientes; ensaio/cutover | upgrade.md | Sem upgrade automático |
| Capacidade/custo | Crescimento, WAL/backup, provisionamento; alternativas | maintenance.md | Tamanhos do schema |
| Provisionamento local | Compose, persistência, clientes; laboratório isolado | local-lab.md | lab-init |
| Governança | Owners, classificação, retenção, histórico, auditoria | security.md | Templates e KB |

Serviços gerenciados, ambientes on-premise e containers têm responsabilidades distintas.
Não configurar HA, compliance ou tuning universal com base somente neste boilerplate.
Toda tarefa termina com evidência, limitações, decisão e próximo passo verificável.
