---
name: github
description: "Use cockpit github commands for every GitHub interaction instead of calling gh directly."
---

# GitHub Skill

Este skill instrui a IA a sempre rotear operações no GitHub através do pacote `github-tools` do AICockpit.

## Regra de Ouro / Gold Rule

Sempre que precisar interagir com o GitHub (buscar código, issues, PRs, Actions, commits, comentar, aprovar ou resolver revisões), use `cockpit github <comando>` em vez de chamar `gh` diretamente.

## Comandos Disponíveis

```bash
# Configuração: salva o token no vault e (opcional) owner/repo padrão
cockpit github configure --token <TOKEN> --default-owner <OWNER> --default-repo <REPO>

# Passa qualquer comando para o gh com o token injetado
cockpit github run <gh args...>

# Actions
cockpit github actions list [--repo OWNER/REPO] [--limit N]
cockpit github actions watch <run-id> [--repo OWNER/REPO]
cockpit github actions logs <run-id> [--repo OWNER/REPO]

# Commits
cockpit github commits <branch> [--repo OWNER/REPO] [--limit N]

# Pull requests
cockpit github pr comment <pr> --body "..." [--repo OWNER/REPO]
cockpit github pr approve <pr> [--repo OWNER/REPO]
cockpit github pr resolve <pr> [--repo OWNER/REPO]
```

## Resolução Automática de Repositório

Se `--repo` não for passado, o comando tenta usar o owner/repo padrão configurado ou detecta o repositório a partir do diretório Git atual.

## Exemplos

- Listar workflows recentes: `cockpit github actions list --repo lleitep3/aicockpit --limit 5`
- Acompanhar execução: `cockpit github actions watch 123456789 --repo lleitep3/aicockpit`
- Logs de workflow: `cockpit github actions logs 123456789`
- Últimos commits na main: `cockpit github commits main --limit 10`
- Comentar em PR: `cockpit github pr comment 42 --body "LGTM"`
- Aprovar PR: `cockpit github pr approve 42`
- Resolver threads de change-request: `cockpit github pr resolve 42`
