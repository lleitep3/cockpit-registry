# PostgreSQL: capacidade, mudanças e recuperação

Contexto: dba-postgres. Revisado em 2026-09-28; referência PostgreSQL 16.

pg_total_relation_size inclui tabela, índices e TOAST. Somar relações não mede todo o
cluster: diferenciar banco, WAL, temporários, backups e disco provisionado. Em tabelas
particionadas, um schema pode excluir partições localizadas em outros schemas. Medir
taxa de crescimento antes de recomendar capacidade e confirmar cobrança real do serviço.
[Funções de tamanho](https://www.postgresql.org/docs/16/functions-admin.html).

Auditoria, prévias e recibos de idempotência podem crescer mais que o domínio. Definir
prazos por finalidade/contrato, política de retenção e responsabilidade; não apagar
histórico nem escolher prazo legal por inferência. Particionamento deve atender volume,
consultas e manutenção demonstrados, não apenas expectativa de crescimento.

CREATE INDEX CONCURRENTLY reduz bloqueio de escrita, mas tem restrições, espera por
transações e pode deixar índice inválido após falha. Verificar estado antes de repetir;
DDL concorrente não deve ser colocado cegamente em migration transacional.
[CREATE INDEX](https://www.postgresql.org/docs/16/sql-createindex.html).

Backup precisa de teste de restauração em destino isolado e validação de dados/objetos.
Definir RPO/RTO e mecanismos de recuperação compatíveis. Uma cópia não comprova restore;
rollback de migration não recupera dados descartados.
[Backup e restauração](https://www.postgresql.org/docs/16/backup.html).

Privilégios mínimos e TLS conforme ambiente. O coletor usa perfil explícito e transação
read-only, mas isso não é sandbox para código hostil do mesmo usuário. Não dar superuser
para facilitar diagnóstico. Com acesso parcial, documentar a lacuna e prosseguir no
que é verificável. Nunca logar URL de conexão ou senha.
