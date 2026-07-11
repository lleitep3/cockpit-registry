# Frontend Guide — SvelteKit + shadcn-svelte

## Stack

| Tecnologia       | Versão   | Papel                              |
|------------------|----------|------------------------------------|
| SvelteKit        | latest   | Framework full-stack               |
| Svelte           | 5.x      | UI reativa com runes               |
| shadcn-svelte    | latest   | Componentes acessíveis e estilizados |
| Tailwind CSS     | 4.x      | Utilitários CSS                    |
| mode-watcher     | latest   | Toggle dark/light mode             |
| TypeScript       | 5.x      | Tipagem estática                   |
| Vite             | latest   | Build tool (via SvelteKit)         |

## Svelte 5 — Runes

Use sempre runes no Svelte 5. Nunca use a sintaxe legada (`writable`, `$:`, etc.).

```svelte
<script lang="ts">
  // Estado local reativo
  let count = $state(0)
  let doubled = $derived(count * 2)

  // Efeito colateral
  $effect(() => {
    console.log('count changed:', count)
  })

  // Props do componente
  let { title, onClose }: { title: string; onClose: () => void } = $props()
</script>
```

## Theming — Dark/Light Mode

O theming é gerenciado pelo `mode-watcher`. Já vem configurado no boilerplate.

### Como funciona

- `ModeWatcher` no `+layout.svelte` gerencia a classe `.dark` no `<html>`
- Persiste a preferência no `localStorage`
- Respeita `prefers-color-scheme` do sistema por padrão
- Anti-FOUC: script inline no `app.html`

### Toggle de tema

```svelte
<script lang="ts">
  import { toggleMode, mode } from 'mode-watcher'
</script>

<button onclick={toggleMode}>
  {#if $mode === 'dark'}🌙 Dark{:else}☀️ Light{/if}
</button>
```

### Classes Tailwind para tema

```svelte
<!-- Adapta automaticamente com dark: prefix -->
<div class="bg-white dark:bg-zinc-900 text-black dark:text-white">
  Conteúdo
</div>
```

## Componentes shadcn-svelte disponíveis no boilerplate

| Componente | Uso |
|------------|-----|
| `Button`   | Ações, submits, navegação |
| `Card`     | Container de conteúdo |
| `Table`    | Listagens de dados |
| `Input`    | Formulários |
| `Badge`    | Status, tags, labels |
| `Toast`    | Notificações temporárias |

### Uso dos componentes

```svelte
<script lang="ts">
  import { Button } from '$lib/components/ui/button'
  import * as Card from '$lib/components/ui/card'
  import { Badge } from '$lib/components/ui/badge'
</script>

<Card.Root>
  <Card.Header>
    <Card.Title>Título</Card.Title>
  </Card.Header>
  <Card.Content>
    <Badge variant="default">ativo</Badge>
    <Button onclick={() => {}}>Ação</Button>
  </Card.Content>
</Card.Root>
```

## `$lib/api.ts` — Fetch Helper

```typescript
const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000'

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!res.ok) throw new Error(`API error ${res.status}: ${await res.text()}`)
  return res.json() as Promise<T>
}

export const api = {
  get:    <T>(path: string) => request<T>(path),
  post:   <T>(path: string, body: unknown) => request<T>(path, { method: 'POST', body: JSON.stringify(body) }),
  patch:  <T>(path: string, body: unknown) => request<T>(path, { method: 'PATCH', body: JSON.stringify(body) }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
}
```

## Estrutura de Rotas SvelteKit

```
src/routes/
├── +layout.svelte      # layout global (ModeWatcher, navbar, toggle tema)
├── +layout.ts          # configurações do layout
├── +page.svelte        # home (/)
└── items/
    ├── +page.svelte    # listagem (/items)
    └── [id]/
        └── +page.svelte  # detalhe (/items/123)
```

## Carregamento de Dados

```typescript
// routes/items/+page.ts
import { api } from '$lib/api'
import type { PageLoad } from './$types'

export const load: PageLoad = async () => {
  const items = await api.get<Item[]>('/api/v1/items')
  return { items }
}
```

```svelte
<!-- routes/items/+page.svelte -->
<script lang="ts">
  import type { PageData } from './$types'
  let { data }: { data: PageData } = $props()
</script>

{#each data.items as item}
  <p>{item.name}</p>
{/each}
```
