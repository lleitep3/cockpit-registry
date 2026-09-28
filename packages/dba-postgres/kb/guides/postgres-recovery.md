# PostgreSQL: recuperabilidade e disponibilidade

Contexto: dba-postgres. Revisado em 2026-09-28; referência PostgreSQL 17.

Backups lógicos, físicos e arquivamento contínuo resolvem necessidades distintas.
Definir RPO/RTO e ensaiar restore em destino isolado, com objetos e invariantes da
aplicação. Backup sem erro não comprova restauração. Globals e configuração precisam
ser considerados fora de um dump individual.
[Backup](https://www.postgresql.org/docs/17/backup.html).

PITR depende de backup físico e WAL suficiente até o alvo. pg_dump não fornece base
para replay WAL. Preservar timelines, metadados e chaves de criptografia; testar a cadeia.
[PITR](https://www.postgresql.org/docs/17/continuous-archiving.html).

Replica não substitui backup: erros lógicos podem se propagar. Slots podem reter WAL;
lag precisa ser interpretado por estado e janela. Promoção exige impedir escrita do
primário antigo e encaminhar clientes, além de planejar retorno/ressincronização.
[Standby/replicação](https://www.postgresql.org/docs/17/warm-standby.html).

Não prometer HA por adicionar um container ao Compose. Volumes persistentes não são
backup. Retenção, cópia independente e teste de desastre dependem do objetivo real.
