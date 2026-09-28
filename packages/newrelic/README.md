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
User API key; o modo de análise não cria nem imprime credenciais; configure keys salva no cofre.
Conta/região podem vir de NEW_RELIC_ACCOUNT_ID/NEW_RELIC_REGION. Região padrão US.
Não use credenciais expostas ou pendentes de rotação.

Os comandos de análise só enviam consultas com templates GraphQL fixos.
O comando explícito configure keys cria credenciais após confirmação. Não é uma fronteira
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

## Perfis multi-conta

`cockpit newrelic profiles add partilhar-dev --account 8554578 --region US --vault-key newrelic-partilhar-dev`
registra somente metadados locais; não salva um token nem concede permissões New Relic.
Para guardar uma chave válida, rode em terminal privado:
`cockpit newrelic --profile partilhar-dev profiles auth` (entrada oculta pelo cofre).
Nunca use --value ou cole chave no chat. Cofre bloqueado deve ser desbloqueado pelo
proprietário; o pacote respeita o bloqueio, sem namespace alternativo ou fallback.

`cockpit newrelic profiles list` lista metadados, sem consultar segredos.
`cockpit newrelic --profile partilhar-dev account` verifica acesso real.
`cockpit newrelic --profile partilhar-dev synthetics` consulta o ambiente selecionado.
Crie outros perfis para outras contas/regiões. Cada referência de cofre pode ter uma
chave distinta; privilégios reais pertencem ao usuário New Relic, não ao nome do perfil.
Não existe perfil padrão implícito. Perfil não combina com --account/--region nem
variáveis NEW_RELIC_* legadas, evitando mistura involuntária de conta e chave.
Metadados ficam em ~/.cockpit/newrelic/profiles.json (0600); token no cofre Cockpit.
O pacote não altera permissões do token, nem cria/rotaciona chaves no New Relic.
Perfis são usados pela CLI de análise; Terraform continua usando suas variáveis
efêmeras e configuração de conta/região revisada, conforme o builder.

## Configuração guiada de chaves (Linux + Chrome)

```sh
cockpit newrelic configure browser
cockpit newrelic configure keys
# Ou com destino e tipos explícitos:
cockpit newrelic configure keys --profile partilhar-dev --types user license
# Para IA/automação: prévia sem efeitos externos
cockpit newrelic configure keys --profile partilhar-dev --types user license --plan
```

`configure browser` instala Playwright em ~/.cockpit/newrelic/runtime (venv privado).
Chrome/Chromium do sistema é necessário. `configure keys` pergunta o perfil, permite
cadastrar conta/região, verifica cofre desbloqueado e exige digitar a confirmação
CREATE <conta> <perfil>. User é o padrão; license/browser são opt-in. Não há --yes.
O cofre deve ser desbloqueado pessoalmente; não são alteradas suas proteções.

Sem uma User key válida, abre Chrome via CDP em loopback, porta efêmera e perfil
persistente exclusivo por perfil Cockpit. O usuário completa login/MFA/CAPTCHA.
A sessão é reutilizada nas próximas execuções. Não copia cookies, não conecta no
Chrome pessoal e não consulta APIs internas autenticadas por cookies. Chrome 136+
requer user-data-dir separado para depuração. O processo lançado é encerrado ao final.

A UI cria apenas a User key, confirmando conta e tipo antes de submeter. Em seguida
valida acesso pela API oficial. License/Browser são criadas pela API NerdGraph com
essa User key, e suas referências/IDs são registrados no perfil. Chaves User válidas
são reutilizadas; referências ingest existentes são conferidas no cofre. O fluxo não
revoga chaves remotas antigas nem prova que a aplicação está enviando telemetria.

Segredos são enviados ao prompt oculto do vault através de PTY (sem argumento --value),
com conferência de leitura de volta; não ficam em JSON, prints, snapshots ou traces.
DEBUG/PWDEBUG são recusados. Metadata/journal são 0600; navegador fica em diretório
privado. Se houver falha após submissão, o journal bloqueia nova criação: conferir a
chave no New Relic e recuperar/revogar manualmente antes de resolver o journal. Não
apagar o journal cegamente para tentar de novo. Nenhuma repetição automática de mutation.

Compatibilidade da UI foi testada numa fixture local por CDP; a tela real pode mudar.
Login negado, políticas administrativas, captcha e mudança de seletor interrompem o
fluxo. O comando não é alternativa para contornar bloqueios de acesso do navegador.
Validação real de criação e ingestão ainda pendente no ambiente autorizado.

Fontes: https://developer.chrome.com/blog/remote-debugging-port e
https://docs.newrelic.com/docs/apis/nerdgraph/examples/use-nerdgraph-manage-license-keys-user-keys/

## Namespace do vault (0.3.1)

Todas as leituras/gravações usam explicitamente `--namespace newrelic`, inclusive
autenticação de perfis e bootstrap de chaves. Não há fallback para o vault legado
nem para outro pacote. O bloqueio do cofre e grants do core continuam valendo.

Perfis antigos mantêm seus metadados, mas uma chave salva sem namespace precisa
ser migrada pelo operador para `newrelic`, usando entrada oculta/`--stdin`, ou
reautenticada com `cockpit newrelic --profile NOME profiles auth`. Não passar token
em argumento ou chat, não apagar a referência anterior antes de verificar a nova.
O pacote não pode fazer migração automática do vault global: isso violaria o
contrato de isolamento. Após migração, verificar `account` e consulta agregada.
