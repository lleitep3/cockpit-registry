# test-data 0.3.0

Pacote Cockpit com Massa CLI 0.3.0, skill schema-seed-qa, workflow de QA e templates funcionais. PostgreSQL é a fonte de metadados; receitas YAML produzem JSONL reproduzível com chaves relacionadas coerentes.

## Instalação

Requer Python >=3.12 com venv, acesso ao índice Python e PostgreSQL local via Docker para extração. O post-install instala dependências fixadas em ambiente exclusivo do pacote. Para instalação manual: `sh scripts/install.sh`. `PYTHON` seleciona o interpretador.

## Uso

```sh
cockpit test-data --help
cockpit test-data schema inspect --help
cockpit test-data schema diff --before schema.yaml --after schema-next.yaml --output schema-diff.json --fail-on-change
cockpit test-data validate --schema schema.yaml --recipe generation.yaml
cockpit test-data generate --schema schema.yaml --recipe generation.yaml --format jsonl --output runs/demo
```

Copie `boilerplates/schema-seeds/schema.example.yaml` e `generation.example.yaml` para iniciar. A pasta de saída deve ser nova. Configure conexão em arquivo de ambiente ignorado pelo Git; nunca versione credenciais. A extração usa transação somente leitura.

## Atualização e rollback

Cada instalação cria um runtime novo em `${XDG_DATA_HOME:-~/.local/share}/cockpit/test-data/runtimes`, valida dependências e só então troca o link `.venv` atomicamente. Falhas preservam o runtime ativo. Runtimes anteriores são preservados: para rollback, aponte `.venv` para o runtime anterior. Dados do usuário devem ficar fora do diretório do pacote. O Cockpit substitui a pasta do pacote durante upgrade; os runtimes ficam fora dela. Se o post-install falhar após essa substituição, execute o instalador novamente ou restaure a versão do pacote pelo backup do Cockpit; o runtime anterior continua disponível. `TEST_DATA_RUNTIME_ROOT` permite definir outro diretório.

## Limites e QA

Suporta inteiros, booleanos, texto, UUID e timestamps; tipos restantes falham explicitamente. Checks SQL, triggers, índices parciais e collations exigem validação em banco descartável. Não carrega automaticamente o banco. Manifest registra hashes, versões e verificações executadas. Não inclui catálogo nem configuração privada do Partilhar.

Validação de assets: `bin/validate` com `PYTHON` apontando para interpretador com PyYAML. Testes do CLI: `.venv/bin/python -m unittest discover -s cli/tests`. Integração opcional usa `MASSA_TEST_ENV_FILE` com banco local descartável. O padrão e relatório de QA ficam na skill e no boilerplate.

## Comparação de schemas

`schema diff` compara catálogos v1 e produz JSON com alterações, caminhos, valores
anteriores/novos e hashes das entradas. Sem `--output`, escreve JSON na saída padrão.
Tabelas e campos renomeados aparecem como remoção/inclusão. Constraints, índices,
triggers e enums são comparados por nome; ordem da FK, campos e valores do enum
é preservada. Só `source.server_version` é ignorado. Metadados adicionais também
são comparados. Não classifica compatibilidade nem altera schema/receita/banco.

`--fail-on-change` retorna código 2 no Massa CLI se houver alterações; erros de
entrada retornam 1. O Cockpit instalado preservou o código 2 na verificação real. Para CI,
use o status e o campo `changed` do JSON para distinguir drift de erro de execução.
