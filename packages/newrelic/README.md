# New Relic para Cockpit

Pacote local com `newrelic-builder`, `newrelic-analyzer` e `cockpit newrelic`.
Python >=3.10 (biblioteca padrão), Terraform >=1.10 para IaC. Sem MCP nem daemon.

## Uso

```sh
cockpit newrelic --help
cockpit newrelic --account 12345 --region US account
cockpit newrelic --account 12345 synthetics
cockpit newrelic --account 12345 apm
cockpit newrelic --account 12345 hosts
cockpit newrelic --account 12345 errors
cockpit newrelic --account 12345 incidents
cockpit newrelic --account 12345 nrql --file query.nrql
cockpit newrelic scaffold ./observability
```

Autenticação: NEW_RELIC_API_KEY **ou** NEW_RELIC_API_KEY_FILE, nunca ambos.
Arquivo deve pertencer ao usuário e ter modo 0600/0400. Use cofre para fornecer a
User API key; o pacote não cria, rotaciona, armazena ou imprime credenciais.
Conta/região podem vir de NEW_RELIC_ACCOUNT_ID/NEW_RELIC_REGION. Região padrão US.
Não use credenciais expostas ou pendentes de rotação.

CLI só envia operações de consulta com templates GraphQL fixos. Não é uma fronteira
de autorização: use roles de leitura no servidor. Resultado pode conter informação
sensível; prefira agregados e filtros. Não há retry automático, polling, logs HTTP ou
redirect de credenciais. Respostas limitadas a 2 MB; timeout de transporte 45 segundos.

Scaffold recusa diretório existente. Gera 9 recursos de disponibilidade HTTP, sem apply.
Terraform não instala agentes APM/host. CLI consulta essas fontes quando instrumentadas;
vazio não significa saudável. Não há garantia de custo zero: confirme plano e quotas.
API real e entrega de notificações precisam de validação após autorização de acesso.

## Testes

`python3 -m unittest discover -s tests -v`

Template derivado de partilhar-aba-infra PR #17; conta, email, URLs e credenciais são
configuráveis. Não contém state, tfvars reais nem dados clínicos.
