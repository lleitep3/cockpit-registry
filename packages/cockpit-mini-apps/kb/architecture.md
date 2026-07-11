# Arquitetura dos Mini-Apps

## O que é um Mini-App

Mini-apps são sistemas rápidos, POCs ou aplicações básicas criadas pelo agente no workspace
do cockpit. São autocontidos, rodam via `docker-compose up` e seguem uma estrutura padronizada.

## Workspace

Todos os mini-apps ficam em:

```
~/.cockpit/workspace/mini-apps/
└── <nome-do-projeto>/
    ├── frontend/           # SvelteKit + shadcn-svelte
    ├── backend/            # FastAPI async
    ├── db/                 # apenas se tiver banco de dados
    │   └── data/           # dados postgres persistidos aqui
    └── docker-compose.yml
```

## Quando Incluir Banco de Dados

Use `--no-db` (sem banco) se o mini-app:
- É puramente demonstrativo (dados mockados no frontend)
- Processa dados em memória e não precisa persistir entre reinicializações
- Consome APIs externas apenas

Use **com banco** (padrão) se o mini-app:
- Precisa salvar registros criados pelo usuário
- Tem autenticação, histórico ou estado persistente
- É um CRUD real de qualquer entidade

## Comunicação entre Serviços

```
Browser → Frontend (localhost:3000)
            ↓ VITE_API_URL
Frontend → Backend API (localhost:8000)
            ↓ DATABASE_URL
Backend → PostgreSQL (localhost:5432)
```

O frontend chama o backend via `$lib/api.ts` usando `VITE_API_URL` (definido no env).
Dentro do docker network, o backend chama o db como `db:5432`.

## Portas Padrão

| Serviço  | Porta | Configurável via    |
|----------|-------|---------------------|
| Frontend | 3000  | FRONTEND_PORT       |
| Backend  | 8000  | BACKEND_PORT        |
| Postgres | 5432  | DB_PORT             |

## Decisões de Arquitetura

- **Sem autenticação**: mini-apps rodam localmente, não precisam de auth
- **Hot-reload em dev**: volumes montados nos containers para edição em tempo real
- **Dados persistidos no host**: `./db/data/` (nunca volume Docker anônimo)
- **Runtime detectado automaticamente**: podman (preferido) ou docker (fallback)
