# Naming Conventions

## Pastas e Arquivos

| Tipo | Convenção | Exemplos |
|------|-----------|---------|
| Pastas do projeto | `kebab-case` | `todo-app`, `link-shortener`, `user-manager` |
| Arquivos Python | `snake_case` | `item_service.py`, `user_model.py` |
| Arquivos Svelte | `PascalCase` | `ItemCard.svelte`, `UserTable.svelte` |
| Arquivos TypeScript | `camelCase` | `api.ts`, `stores.ts` |
| Rotas SvelteKit | `kebab-case` (pastas) | `routes/my-items/+page.svelte` |

## Python

```python
# Módulos e packages: snake_case
item_service.py
user_repository.py

# Classes: PascalCase
class ItemService:
class UserRepository:

# Funções e variáveis: snake_case
async def get_item_by_id(item_id: int) -> Item:
current_user: User

# Constantes: SCREAMING_SNAKE_CASE
MAX_ITEMS_PER_PAGE = 100
DEFAULT_DB_TIMEOUT = 30

# Privado: underscore inicial
async def _validate_item(item: Item) -> bool:
```

## TypeScript / Svelte

```typescript
// Interfaces e Types: PascalCase
interface ItemRead {
  id: number
  name: string
}
type ApiResponse<T> = { data: T } | { error: string }

// Componentes Svelte: PascalCase
ItemCard.svelte
UserTable.svelte
StatusBadge.svelte

// Hooks / composables: camelCase com 'use' prefix
function useItems() {}

// Constantes: SCREAMING_SNAKE_CASE
const MAX_ITEMS_PER_PAGE = 20
```

## Variáveis de Ambiente

```env
# SCREAMING_SNAKE_CASE sempre
FRONTEND_PORT=3000
BACKEND_PORT=8000
DATABASE_URL=postgresql+asyncpg://...
LOG_FORMAT=pretty
DEBUG=true
DB_USER=miniapp
DB_PASS=miniapp
DB_NAME=miniapp
```

## Nome do Projeto

O nome do projeto deve ser `kebab-case` e descrever o que o mini-app faz:

| Descrição do usuário        | Nome sugerido      |
|-----------------------------|--------------------|
| "app de tarefas"            | `todo-app`         |
| "encurtador de links"       | `link-shortener`   |
| "gerenciador de usuários"   | `user-manager`     |
| "dashboard de vendas"       | `sales-dashboard`  |
| "controle de estoque"       | `inventory-control`|

Se o nome não for fornecido, use o formato: `mini-app-YYYYMMDD` (ex: `mini-app-20260711`).

## Entidade de Domínio

O boilerplate usa `Item` como entidade de exemplo. Ao criar um mini-app real, renomeie:

| Boilerplate    | Mini-app real              |
|----------------|----------------------------|
| `Item`         | `Task`, `Product`, `User`  |
| `item.py`      | `task.py`, `product.py`    |
| `/api/v1/items`| `/api/v1/tasks`            |
| `items` (tabela)| `tasks` (tabela)          |

## Rotas da API

Use substantivos no plural, `kebab-case`, versionadas:

```
/api/v1/items           ✅
/api/v1/item            ❌ (singular)
/api/v1/getItems        ❌ (verbo)
/api/v1/todo-items      ✅ (kebab-case)
/api/v1/todoItems       ❌ (camelCase)
```
