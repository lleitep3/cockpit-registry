# cockpit-mini-apps

Plataforma base para criação de mini-apps no workspace do cockpit. Com este pacote instalado, o agente consegue criar mini-apps completos (SvelteKit + FastAPI + PostgreSQL) com um único comando.

## Instalação

```bash
cockpit install cockpit-mini-apps
```

## Uso

### Criar um novo mini-app

```bash
# Com banco de dados (PostgreSQL)
cockpit mini-app new meu-projeto

# Sem banco de dados
cockpit mini-app new meu-projeto --no-db
```

O comando:
1. Copia o boilerplate para `~/.cockpit/workspace/mini-apps/meu-projeto/`
2. Detecta automaticamente podman ou docker
3. Sobe o ambiente com `podman-compose up --build -d` (ou `docker compose`)
4. Abre o browser em `http://localhost:3000`

### Outros comandos

```bash
# Listar mini-apps criados
cockpit mini-app list

# Abrir mini-app no browser
cockpit mini-app open meu-projeto

# Remover mini-app
cockpit mini-app remove meu-projeto
```

## Stack

| Camada    | Tecnologia                              |
|-----------|-----------------------------------------|
| Frontend  | SvelteKit + shadcn-svelte + Tailwind    |
| Theming   | mode-watcher (dark/light automático)    |
| Backend   | FastAPI async + SQLAlchemy 2.0 + asyncpg |
| DB        | PostgreSQL 16 (opcional, `--no-db`)     |
| Container | Podman (fallback: Docker)               |

## URLs do mini-app

| Serviço  | URL                          |
|----------|------------------------------|
| Frontend | http://localhost:3000        |
| API      | http://localhost:8000        |
| Swagger  | http://localhost:8000/docs   |
| ReDoc    | http://localhost:8000/redoc  |

## Workspace

Todos os mini-apps ficam em:

```
~/.cockpit/workspace/mini-apps/
└── meu-projeto/
    ├── frontend/
    ├── backend/
    ├── db/data/        # dados postgres (git-ignored)
    └── docker-compose.yml
```

## Skill do Agente

O pacote instala a skill `mini-app-builder`. O agente a ativa automaticamente quando você pede:

- "cria um mini-app de..."
- "faz uma POC de..."
- "quero um sisteminha que..."
- "cria um app rápido de..."
