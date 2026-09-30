# Vercel for Cockpit

Contas nomeadas, tokens no vault do Cockpit, API e CLI oficial. Linux com Bash e Python 3.10+; outros sistemas não foram validados. Requer um Cockpit com `config` e injeção de segredos no processo filho. Versões antigas falham sem criar arquivo de credenciais alternativo.

## Autenticação

```sh
cockpit vercel auth m2b --scope lleitelab --token
cockpit vercel accounts
cockpit vercel accounts --profile m2b
cockpit vercel status --profile m2b
```

`--token` abre entrada oculta; também é o comportamento padrão sem a flag. Não aceita o valor em argv: o dispatcher e o histórico de shell podem registrar argumentos. Para automação, encaminhe a saída de um gerenciador de segredos para `cockpit vercel auth m2b --scope lleitelab --token-stdin`. Nunca cole o token em chat, arquivo do projeto ou argumento.

Ao renovar sem --scope, o comando preserva o scope já salvo; em um perfil novo, usa o apelido como slug. O apelido `m2b` é local. `lleitelab` é o slug da equipe Vercel. Não há conta padrão implícita. Metadata pública e referências ficam no namespace vercel; token real fica no keyring do sistema através do Cockpit. `auth` confirma armazenamento, não validade remota. `status` consulta a equipe selecionada.

Se o vault estiver bloqueado, use o fluxo oficial `cockpit vault unlock --help` e desbloqueie o namespace vercel. Nunca desabilite o cofre para contornar a falha. Proteção de namespace não isola código hostil executado pelo mesmo usuário do sistema.

## Atalhos e API

```sh
cockpit vercel doctor
cockpit vercel projects --profile m2b
cockpit vercel deployments --profile m2b --limit 10
cockpit vercel inspect --profile m2b dpl_EXEMPLO
cockpit vercel api --profile m2b GET /v9/projects
cockpit vercel api --profile m2b PATCH /v9/projects/prj_EXEMPLO --body-file settings.json --apply
cockpit vercel docs
```

API usa somente https://api.vercel.com, recusa redirects e impõe o scope do perfil. Campos sensíveis conhecidos são mascarados. Endpoints de credenciais/env exigem ferramenta dedicada/painel. Não há retries automáticos; timeout de escrita tem resultado desconhecido e exige reconciliação antes de repetir. Paginação vem na resposta; não promete inventário completo.

## CLI oficial

Instale uma versão fixa da CLI fora do pacote ou no projeto (exemplo validado: vercel@62.0.0). Defina `VERCEL_CLI` para o caminho do executável quando não estiver no PATH. Não há instalação global automática. Para guardar o caminho por conta: `cockpit config --namespace vercel --profile m2b set cli_path /caminho/vercel`.

```sh
cockpit vercel cli --profile m2b -- project ls
cockpit vercel cli --profile m2b -- deploy --yes
cockpit vercel cli --profile m2b -- inspect gps-exemplo.vercel.app
```

O token chega à CLI por ambiente do processo filho, não por argv. O wrapper fixa scope e modo não interativo, remove IDs de projeto/org herdados, recusa overrides de conta, API, token e debug. Use diretório vinculado à equipe correta. Saída é capturada e o token selecionado é mascarado; outros dados sensíveis emitidos por comandos arbitrários não têm garantia de redação. Não use comandos que exportem segredos para arquivos/logs sem necessidade explícita.

`deploy` gera preview por padrão na CLI; produção requer a escolha explícita correspondente. Um preview remoto ainda pode gerar custo. Confira conta, diretório, commit, plano, acesso e limites antes de executar.

## Criação de tokens

O primeiro token é criado em https://vercel.com/account/tokens. Sessão OAuth de `vercel login` não consegue gerar tokens. Quando já existir um token clássico com escopo de conta e houver autorização:

```sh
cockpit vercel token-create --profile bootstrap --name cockpit-evaluation --save-as evaluation --project prj_EXEMPLO
```

O token novo é capturado em memória e enviado ao vault sem ser impresso. `--project` é opcional, usa ID e reduz escopo conforme regras do provedor. Sem esse argumento o token pode ser amplo: escolher deliberadamente. Se houver erro de gravação após criação remota, conferir Account Tokens e reconciliar antes de repetir. O adaptador não cria expiração não suportada pela CLI/API nem promete permissões menores que as concedidas pelo provedor.

## Verificação e distribuição

```sh
bash tests/run_test.sh
cockpit cockpit-builder validate /caminho/vercel
```

Testes locais simulam API e processos: seleção de conta, token fora de argv, redaction, erro/timeout, redirecionamento recusado, dependência ausente e vault bloqueado. Não comprovam autenticação ou implantação real. A skill fornece referências oficiais atualizadas em vez de copiar manuais.
