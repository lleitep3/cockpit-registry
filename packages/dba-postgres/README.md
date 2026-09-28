# DBA PostgreSQL — pacote Cockpit

Versão 0.1.0. Diagnóstico somente leitura, DER e revisões de modelo/performance
orientadas por evidências. Não aplica tuning, migrations ou exclusões.

## Conteúdo

| Parte | Entrega |
| --- | --- |
| dba-postgres | Skill coordenadora e diagnóstico |
| postgres-modeling | Invariantes, tenant, histórico e migrations |
| postgres-performance | Workload, planos, índices, locks e capacidade |
| 4 workflows | Baseline, revisão física, investigação e mudança segura |
| 4 guias KB | Evidências, modelagem, performance e operação, com fontes oficiais |
| CLI | Coleta fixa, análise offline, relatório, DER Mermaid e findings JSON |
| Templates | Revisões de modelo e performance |

[Demonstração sintética](examples/report.md) · [Plano](PLAN.md) · [Workflows](skills/dba-postgres/references/baseline.md) ·
[Base de conhecimento](kb/guides/postgres-evidence.md) · [Validação](VALIDATION.md)

## Uso offline

Python 3.10+, sem dependências Python externas:

```sh
cockpit dba-postgres analyze baseline.json --output relatorio-01
```

Gera `report.md`, `schema.mmd` e `findings.json`. Arquivos/pastas devem ser novos:
não sobrescreve evidência existente. `tests/fixtures/example.json` é um exemplo
sintético; o snapshot antigo do gerador específico de outro projeto não tem este contrato.

## Coleta por perfil explícito

Requer psql, conexão autorizada e Cockpit com `config exec`. Linux/Codex é o alvo
validado; outras plataformas e versões não executadas não têm garantia.
A consulta foi escrita para PostgreSQL 16–18; consulte VALIDATION.md para evidência real.

```sh
cockpit config --namespace dba-postgres --profile exemplo-dev set host HOST
cockpit config --namespace dba-postgres --profile exemplo-dev set port 5432
cockpit config --namespace dba-postgres --profile exemplo-dev set database BANCO
cockpit config --namespace dba-postgres --profile exemplo-dev set user USUARIO
cockpit config --namespace dba-postgres --profile exemplo-dev set sslmode verify-full
cockpit config --namespace dba-postgres --profile exemplo-dev secret password
cockpit config --namespace dba-postgres --profile exemplo-dev show
cockpit dba-postgres collect --profile exemplo-dev --schema public --output baseline.json
cockpit dba-postgres analyze baseline.json --output relatorio-01
```

Substituir HOST/BANCO/USUARIO. Configurar CA confiável padrão do libpq para verify-full.
A senha é digitada em entrada oculta e injetada só no processo filho. O comando não
cria perfil, concede privilégios ou usa credenciais implícitas. Não configurar produção
por conveniência. Falha do vault/acesso não tem fallback. `_collect` é detalhe interno,
não fronteira de segurança; perfis Cockpit são controles cooperativos do mesmo usuário.

`cockpit dba-postgres sql` exibe o SQL fixo para revisão. Não aceita SQL do usuário,
não exporta linhas, query text, planos ou senhas. Não instala pg_stat_statements.
Metadados continuam potencialmente sensíveis: revisar antes de compartilhar.

## Interpretação e limites

O relatório sinaliza PK ausente, constraints não validadas, índices inválidos e FKs
sem cobertura B-tree identificada. São candidatos de revisão, não comandos de correção.
Índices únicos parciais, regras de triggers e aplicação não definem cardinalidade global.
O DER não exporta views, funções, políticas RLS, defaults ou corpos de CHECKs.
Nomes incomuns são sanitizados no Mermaid; o JSON preserva os nomes originais.

Contadores são cumulativos e podem ser parciais/resetados. Não calcula deltas, bloat,
p95, economia ou tuning automático. Um relatório limpo não é auditoria completa.

## Desenvolvimento

```sh
cockpit cockpit-builder validate ~/.cockpit/local-registry/dba-postgres
~/.cockpit/local-registry/dba-postgres/tests/run_test.sh
```

Staging em local-registry; instalação copia pacote e skills para assets canônicos,
seguida de cockpit deploy. KB declarada no manifesto; ver INSTALL.md. Nunca editar
arquivos gerados por providers. Publicação em branch/PR próprio, sem merge automático.
