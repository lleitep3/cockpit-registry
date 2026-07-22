# cockpit-dashboard

Mini-app visual do estado atual do AICockpit.

## Comando

```bash
cockpit dashboard open
```

## O que é exibido

O dashboard lê arquivos locais do cockpit:

- `~/.cockpit/config.yml` — versão e configuração geral
- `~/.cockpit/packages/` — pacotes instalados
- `~/.cockpit/registries.yml` — registries registrados
- `~/.cockpit/kb/` — documentos da knowledge base

## Memória

Por padrão os containers usam o mínimo de memória possível:

- frontend: 64 MB
- backend: 64 MB

Não há banco de dados.
