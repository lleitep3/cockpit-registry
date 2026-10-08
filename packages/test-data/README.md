# test-data

Pacote Cockpit 0.1.0: padrão reutilizável para schemas, seeds sintéticos e QA.
Entrega a skill `schema-seed-qa`, referências e templates. Não instala um motor
de geração nem opera bancos automaticamente. Suporte validado: Codex em Linux.

## Uso

Invocar `$schema-seed-qa` para criar ou revisar schemas e seeds. A skill distingue
capacidade implementada, contrato proposto e verificação não executada.
Os detalhes estão em `skills/schema-seed-qa/references/`; os modelos são genéricos.

## Fonte e instalação local

Staging canônico: `~/.cockpit/local-registry/test-data/`.
Copiar pacote para `~/.cockpit/packages/test-data/` e assets declarados aos
diretórios canônicos de skills/KB, preservando arquivos alheios; executar
`cockpit deploy`. Esse é o fluxo local de desenvolvimento, não publicação remota.

Para publicação futura, colocar em `packages/test-data` de um registry, atualizar
seu índice e validar uma PR exclusiva. Não executar `publish` sem revisar seu
comportamento de commit/push/PR e o destino autorizado.

## Validação

```bash
cockpit cockpit-builder validate ~/.cockpit/local-registry/test-data
python tests/validate_assets.py
```

O teste de assets precisa de PyYAML em ambiente virtual; valida portabilidade,
manifesto, referências e templates. Não comprova geração/carga de seeds.

## Origem

Skill criada no projeto Massa em 08/10/2026, antes sem pacote proprietário.
Este pacote incorpora o padrão genérico. Runbooks, catálogo e resultados do
Partilhar pertencem ao projeto e não são distribuídos pelo pacote.
`dba-postgres` continua responsável por suas quatro skills PostgreSQL;
`backend-development` por `api-developer` e `use-case-planner`.

## Dependências e recuperação

Sem dependência obrigatória de pacotes DBA/backend; recursos locais do projeto
determinam acesso a banco e gerador. Não requer secrets nem configuração própria.
Atualizações preservam receitas manuais. Em falha de distribuição, corrigir o
staging e repetir cópia/deploy; não excluir receitas ou restaurar bancos.
