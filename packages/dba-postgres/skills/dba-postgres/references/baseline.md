# Workflow: inventário e baseline

1. Registrar pergunta, ambiente, PostgreSQL major, banco/schema e perfil selecionado.
2. Conferir perfil público com `cockpit config --namespace dba-postgres --profile PERFIL show`.
   Não imprimir senha. Confirmar que o destino corresponde ao ambiente solicitado.
3. Coletar: `cockpit dba-postgres collect --profile PERFIL --schema public --output baseline.json`.
   Arquivo novo obrigatório. SQL fixo disponível em `cockpit dba-postgres sql`.
4. Analisar: `cockpit dba-postgres analyze baseline.json --output relatorio-01`.
5. Verificar collected_at, server_version_num, database, schema, in_recovery,
   track_counts, database_stats.stats_reset e activity.unknown_state. Nulos significam
   informação ausente; atividade de outros usuários pode estar parcialmente oculta.
6. Validar DER contra migrations. Catálogo não contém intenção, autorização nem
   todas as regras de aplicação. Inspecionar CHECKs/triggers/RLS separadamente se necessário.
7. Entregar report.md, schema.mmd e findings.json. Adicionar contexto e grau de
   confiança. Não publicar automaticamente; metadados também podem ser sensíveis.

O coletor cobre um schema, 5000 tabelas/50000 itens por categoria, falhando ao atingir
o limite para não rotular dados truncados como completos. Sem varredura de linhas.
Timeout 10s por SQL, conexão 5s, processo 45s. Arquivos 0600 e relatório 0700 no Unix.

Antes de entregar o DER, aplicar e conferir o [estilo visual padrão](diagram-style.md).
