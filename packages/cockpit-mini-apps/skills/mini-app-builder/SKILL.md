---
name: mini-app-builder
description: >
  Cria mini-apps completos (SvelteKit + FastAPI async + PostgreSQL opcional) no workspace
  do cockpit (~/.cockpit/workspace/mini-apps/). Ativar quando o usuário pedir uma POC,
  mini-app, sisteminha, app rápido, protótipo ou qualquer sistema básico.
triggers:
  - "cria um mini-app"
  - "faz uma POC"
  - "quero um sisteminha"
  - "cria um app básico"
  - "protótipo rápido"
  - "mini-app de"
  - "sistema simples"
---

# mini-app-builder

Use esta skill para criar mini-apps no workspace do cockpit seguindo os padrões definidos
na knowledge base do pacote.

## Fluxo de Criação

Siga **sempre** esta sequência quando o usuário pedir um mini-app:

### 1. Coletar requisitos

Pergunte (se não foi informado):
- **Nome do projeto**: sugerir kebab-case do que foi pedido (ex: "app de tarefas" → `todo-app`)
- **Precisa de banco de dados?**: o app precisa persistir dados entre reinicializações?

### 2. Criar o projeto

```bash
# Com banco de dados
cockpit mini-app new <nome>

# Sem banco de dados
cockpit mini-app new <nome> --no-db
```

O comando já:
- Copia o boilerplate correto para `~/.cockpit/workspace/mini-apps/<nome>/`
- Detecta podman ou docker automaticamente
- Sobe o ambiente (`podman-compose up --build -d`)
- Abre o browser em `http://localhost:3000`

### 3. Implementar as features no frontend

Edite os arquivos em `~/.cockpit/workspace/mini-apps/<nome>/frontend/src/`:
- Crie rotas SvelteKit em `routes/`
- Use componentes shadcn-svelte (Button, Card, Table, Input, Badge, Toast)
- Use Svelte 5 runes: `$state`, `$derived`, `$effect`, `$props`
- Use `$lib/api.ts` para chamadas ao backend

### 4. Implementar os endpoints no backend

Edite os arquivos em `~/.cockpit/workspace/mini-apps/<nome>/backend/app/`:
- Adapte `models/item.py` para o modelo do domínio
- Adapte `schemas/item.py` (Pydantic schemas)
- Adapte `routers/items.py` (endpoints CRUD)
- Adapte `services/item_service.py` (lógica de negócio)

### 5. Se tiver DB: criar migration

```bash
cd ~/.cockpit/workspace/mini-apps/<nome>
# Gerar migration após alterar os models
podman-compose exec backend alembic revision --autogenerate -m "initial"
podman-compose exec backend alembic upgrade head
```

### 6. Informar o usuário

```
✅ Mini-app <nome> criado e rodando!

Frontend:  http://localhost:3000
API:       http://localhost:8000
Swagger:   http://localhost:8000/docs
Logs:      podman-compose logs -f (dentro de ~/.cockpit/workspace/mini-apps/<nome>/)
```

## Referências da Knowledge Base

Consulte os guias em `kb/` para detalhes de implementação:

- `architecture.md` — visão geral e decisões de arquitetura
- `frontend-guide.md` — Svelte 5, SvelteKit, shadcn-svelte, theming
- `backend-guide.md` — FastAPI async, estrutura, logging, Swagger
- `database-guide.md` — PostgreSQL, Alembic, persistência de dados
- `docker-guide.md` — docker-compose, podman, hot-reload
- `naming-conventions.md` — convenções de nomes e estrutura
