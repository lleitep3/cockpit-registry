# cockpit-dashboard

Mini-app visual que mostra o estado atual do AICockpit em tempo real.

## Instalação

```bash
cockpit pkg install cockpit-dashboard
```

## Uso

```bash
# Abre o dashboard no browser
cockpit dashboard open

# Para o dashboard
cockpit dashboard stop

# Ver logs
cockpit dashboard logs
```

## Painéis

| Painel | Informações |
|--------|-------------|
| **Status Geral** | Versão do cockpit, status ativo/inativo, uptime |
| **Providers** | Providers ativos (antigravity, devin, goose, etc.) |
| **Pacotes** | Pacotes instalados no `~/.cockpit/packages/` |
| **Registries** | Registries registrados em `~/.cockpit/registries.yml` |
| **Knowledge Base** | Documentos cadastrados no `~/.cockpit/kb/` |

## Stack

| Camada | Tecnologia |
|--------|------------|
| Frontend | SvelteKit + Tailwind CSS |
| Backend | FastAPI (Python 3.12) |

## URLs

- Frontend: http://localhost:3000
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs

## Workspace

O mini-app é copiado para:

```
~/.cockpit/workspace/cockpit-dashboard/
├── app/
│   ├── backend/
│   └── frontend/
├── .venv/
└── .env
```

Sem Docker. Para stacks com banco de dados, use o boilerplate do `cockpit-mini-apps` com DB.
