# Workflow: revisão de modelo

Entrada: requisitos aprovados, fluxos/estados, DER atual, migrations e consultas críticas.

1. Mapear entidades e invariantes por transação, inclusive rascunho/conclusão.
2. Definir PK/FK/UNIQUE/CHECK/NOT NULL e demonstrar o que cada uma garante.
3. Tenant: impedir referência cruzada no banco quando requisito exigir; autorização
   continua necessária na aplicação. RLS precisa de política e teste próprios.
4. Tempo: separar vigente de histórico, definir início/fim, timezone e recorrência.
   Não materializar infinitamente uma agenda semanal sem horizonte operacional.
5. Comparar índices propostos com planos/consultas; contabilizar escrita e manutenção.
6. Produzir DER proposto separado, dicionário e mapa requisito → restrição → teste.
7. Definir migration expand/backfill/validate/contract conforme risco real. Não afirmar
   que down migration desfaz perdas. Dados existentes e compatibilidade fazem parte do plano.

Saída: decisão versionada, alternativas, lacunas e plano testável. Use template
`~/.cockpit/packages/dba-postgres/templates/model-review.md`.
