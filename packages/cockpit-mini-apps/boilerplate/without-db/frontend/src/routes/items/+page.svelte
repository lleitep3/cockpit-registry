<script lang="ts">
	import { api, ApiError } from '$lib/api';
	import type { Item, ItemCreate } from '$lib/types';
	import type { PageData } from './$types';
	import { invalidateAll } from '$app/navigation';

	let { data }: { data: PageData } = $props();

	let items = $derived(data.items);
	let showForm = $state(false);
	let newItem = $state<ItemCreate>({ name: '', description: '' });
	let creating = $state(false);
	let error = $state<string | null>(null);

	async function createItem() {
		if (!newItem.name.trim()) return;
		creating = true;
		error = null;
		try {
			await api.post('/api/v1/items', newItem);
			newItem = { name: '', description: '' };
			showForm = false;
			await invalidateAll();
		} catch (e) {
			error = e instanceof ApiError ? e.message : 'Erro ao criar item';
		} finally {
			creating = false;
		}
	}

	async function deleteItem(id: number) {
		if (!confirm('Remover este item?')) return;
		try {
			await api.delete(`/api/v1/items/${id}`);
			await invalidateAll();
		} catch (e) {
			error = e instanceof ApiError ? e.message : 'Erro ao remover item';
		}
	}
</script>

<svelte:head>
	<title>Items — {{PROJECT_NAME_TITLE}}</title>
</svelte:head>

<div class="space-y-6">
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-2xl font-bold tracking-tight">Items</h1>
			<p class="text-muted-foreground text-sm mt-1">{items.length} item(s) encontrado(s)</p>
		</div>
		<button
			onclick={() => (showForm = !showForm)}
			class="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors"
		>
			{showForm ? 'Cancelar' : '+ Novo Item'}
		</button>
	</div>

	{#if error}
		<div class="rounded-md bg-destructive/10 border border-destructive/30 p-3 text-sm text-destructive">
			{error}
		</div>
	{/if}

	<!-- Formulário de criação -->
	{#if showForm}
		<div class="rounded-lg border border-border bg-card p-4 space-y-3">
			<h2 class="font-semibold">Novo Item</h2>
			<input
				type="text"
				bind:value={newItem.name}
				placeholder="Nome *"
				class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
			/>
			<textarea
				bind:value={newItem.description}
				placeholder="Descrição (opcional)"
				rows={2}
				class="w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring resize-none"
			></textarea>
			<button
				onclick={createItem}
				disabled={creating || !newItem.name.trim()}
				class="rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
			>
				{creating ? 'Criando...' : 'Criar'}
			</button>
		</div>
	{/if}

	<!-- Lista de items -->
	{#if items.length === 0}
		<div class="rounded-lg border border-dashed border-border p-12 text-center">
			<p class="text-muted-foreground">Nenhum item ainda. Crie o primeiro!</p>
		</div>
	{:else}
		<div class="rounded-lg border border-border bg-card overflow-hidden">
			<table class="w-full text-sm">
				<thead class="border-b border-border bg-muted/50">
					<tr>
						<th class="px-4 py-3 text-left font-medium text-muted-foreground">ID</th>
						<th class="px-4 py-3 text-left font-medium text-muted-foreground">Nome</th>
						<th class="px-4 py-3 text-left font-medium text-muted-foreground hidden md:table-cell">Descrição</th>
						<th class="px-4 py-3 text-left font-medium text-muted-foreground hidden md:table-cell">Criado em</th>
						<th class="px-4 py-3 text-right font-medium text-muted-foreground">Ações</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-border">
					{#each items as item (item.id)}
						<tr class="hover:bg-muted/30 transition-colors">
							<td class="px-4 py-3 text-muted-foreground font-mono">#{item.id}</td>
							<td class="px-4 py-3 font-medium">
								<a href={`/items/${item.id}`} class="hover:text-primary hover:underline">
									{item.name}
								</a>
							</td>
							<td class="px-4 py-3 text-muted-foreground hidden md:table-cell">
								{item.description ?? '—'}
							</td>
							<td class="px-4 py-3 text-muted-foreground hidden md:table-cell">
								{new Date(item.created_at).toLocaleDateString('pt-BR')}
							</td>
							<td class="px-4 py-3 text-right">
								<button
									onclick={() => deleteItem(item.id)}
									class="text-xs text-destructive hover:underline"
								>
									Remover
								</button>
							</td>
						</tr>
					{/each}
				</tbody>
			</table>
		</div>
	{/if}
</div>
