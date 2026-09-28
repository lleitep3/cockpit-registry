# PostgreSQL: manutenção e ciclo de vida

Contexto: dba-postgres. Revisado em 2026-09-28; referência PostgreSQL 17.

Rotina de DBA acompanha disponibilidade, integridade, desempenho, capacidade e
recuperabilidade. A frequência e os limiares dependem de SLA, carga e crescimento;
não confundir manutenção com executar VACUUM FULL periodicamente.

Vacuum atende reutilização, visibilidade e proteção contra wraparound. Transações
longas podem atrasar limpeza. Acompanhar idade de freeze e parâmetros efetivos, junto
com atividade e execução de autovacuum; contagem estimada de tuplas mortas não mede bloat.
[Manutenção](https://www.postgresql.org/docs/17/routine-vacuuming.html).

Major upgrade precisa de procedimento de migração; minor e major têm contratos
diferentes. Rever extensões/collation/clients, ensaiar e prever estatísticas e validação.
Não assumir que downgrade por tag de container recupera os dados escritos após cutover.
[Upgrades](https://www.postgresql.org/docs/17/upgrading.html).

Um laboratório pode usar limites pequenos e dados sintéticos para validar comandos.
Resultados de performance só são transferíveis com workload/recursos representativos.
Congelar exemplos de imagem por versão ajuda leitura; digest garante identidade da
imagem. Atualização exige revalidar layout de volume, bootstrap, restore e cliente.
