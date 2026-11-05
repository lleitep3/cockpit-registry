---
name: vercel
description: "Gerencia contas, projetos e deployments Vercel pelo Cockpit, com tokens no vault, CLI oficial e API. Use para configurar acesso, publicar, inspecionar ou operar Vercel."
---

# Vercel pelo Cockpit

Use `cockpit vercel --help`, `doctor` e `accounts` antes de operar. Perfil é explícito; confirme slug/ID da equipe e projeto. Alias local pode diferir do slug: `auth m2b --scope lleitelab`. Não assuma conta pelo nome da pasta ou por uma sessão do navegador.

## Acesso

- Leia [contas e tokens](references/accounts.md) para autenticar, renovar ou gerar token.
- `auth ALIAS --token` lê valor oculto; `--token-stdin` recebe pipe seguro. Não aceitar valor do token no chat ou argv.
- Segredos pertencem ao `cockpit config`/vault no namespace vercel. Não criar .env como fallback.
- `accounts` mostra metadata; `status --profile ALIAS` verifica equipe via API. Cofre bloqueado, 401 e 403 são falhas distintas. Não contornar login/MFA nem copiar cookies.
- Criação de token é mutação: usar apenas quando solicitada; capture no vault com `token-create`. Login OAuth não cria o primeiro token.

## Operação

Use atalhos `projects`, `deployments`, `inspect`, ou `api METHOD /path` com perfil. API de escrita exige `--apply`; o sinalizador é intenção da chamada, não substitui autorização da tarefa. Leia [operação e publicação](references/operations.md) para mudanças.

Para funções não expostas, `cli --profile ALIAS -- COMANDO` usa a CLI oficial. Confira `VERCEL_CLI` e versão instalada; não instale globalmente nem passe flags que troquem conta/API/token. Não inferir sucesso por exit 0 sem verificar recurso.

Antes de publicar: identificar conta, projeto, ambiente, commit, arquivos servidos, acesso, custo incremental e rollback. Aproveite autorização já dada; não repetir confirmações. Começar por preview quando esse for o escopo. Verificar URLs protegidas, HTML, erros e fluxos básicos com dados sintéticos. Repo privado não implica site privado. Não promover ambiente de avaliação a produção de clientes.

Em timeout/erro de escrita, consultar estado antes de repetir; não repetir criação de token ou projeto cegamente. Não executar carga ou pentest sem condições e autorização do provedor. Relatar separadamente evidência local simulada, API real, deployment e CI.

## Referências

Leia [índice oficial](references/docs.md) para a área relevante. Reconsulte preços, planos, flags e limites quando necessário. Regras do provedor podem mudar; não tratar Hobby como plano comercial. Arquitetura e dados de SaaS não são resolvidos apenas pela hospedagem estática.
