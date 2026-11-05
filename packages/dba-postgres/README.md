# DBA PostgreSQL — pacote Cockpit

Versão 0.2.0. Insumos para atuação de DBA PostgreSQL: diagnóstico, modelagem,
performance, segurança, manutenção, recuperação, incidentes e upgrades. O CLI coleta
evidências e gera laboratório local; execução operacional segue workflows e escopo autorizado.

## Conteúdo

| Parte | Entrega |
| --- | --- |
| dba-postgres | Skill coordenadora e diagnóstico |
| postgres-modeling | Invariantes, tenant, histórico e migrations |
| postgres-performance | Workload, planos, índices, locks e capacidade |
| postgres-operations | Manutenção, segurança, recuperação, incidentes e upgrades |
| 10 workflows | Quatro de análise/mudança e seis operacionais, incluindo laboratório |
| 7 guias KB | Evidências, modelagem, performance, operação, segurança, recuperação e ciclo de vida |
| CLI | Coleta fixa, análise offline, relatório, DER Mermaid e findings JSON |
| Templates | Revisões de modelo, performance e operação |
| Boilerplate | PostgreSQL 17 + pgAdmin opcional, persistência e exercícios de backup/restore |

[Demonstração sintética](examples/report.md) · [Plano](PLAN.md) · [Workflows](skills/dba-postgres/references/baseline.md) ·
[Base de conhecimento](kb/guides/postgres-evidence.md) · [Validação](VALIDATION.md)

## Laboratório local

```sh
cockpit dba-postgres lab-init --output ./meu-lab
cd meu-lab
docker compose up -d --wait db
# Interface opcional:
docker compose --profile tools up -d --wait
```

[Guia do laboratório](boilerplates/local-postgres/README.md): senhas geradas em arquivos
privados, acesso loopback, volumes persistentes, backup/restore e coleta sem psql no host.
Não configura produção nem remove volumes automaticamente.

[Matriz completa de atuação](skills/dba-postgres/references/dba-scope.md) distingue
automação, procedimento guiado e capacidades ainda não homologadas.

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

`cockpit dba-postgres sql` exibe o SQL fixo para revisão.
`cockpit dba-postgres sql --kind operations` fornece agregados operacionais (PostgreSQL 17):
conexões, transações, freeze, slots e arquivamento. Sua saída é evidência complementar;
não é entrada do comando analyze. Métricas cluster-wide podem ser parcialmente ocultas
por privilégios e não demonstram sozinhas RPO, lag ou saúde. Não aceita SQL do usuário,
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
# Integração opcional, pasta nova; preserva volumes parados ao terminar:
python3 ~/.cockpit/local-registry/dba-postgres/tests/lab_integration.py --output /tmp/meu-teste-dba --with-tools
```

Staging em local-registry; instalação copia pacote e skills para assets canônicos,
seguida de cockpit deploy. KB declarada no manifesto; ver INSTALL.md. Nunca editar
arquivos gerados por providers. Publicação em branch/PR próprio, sem merge automático.

## Diagramas legíveis

DERs usam fundo branco opaco, texto escuro e cabeçalhos azul-claro.
[Paleta, exportação e exemplo genérico](skills/dba-postgres/references/diagram-style.md).
O gerador inclui o tema no Mermaid; conferir a renderização no visualizador utilizado.
