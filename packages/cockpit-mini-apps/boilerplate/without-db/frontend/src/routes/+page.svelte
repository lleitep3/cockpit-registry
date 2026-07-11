<script lang="ts">
	import { api } from '$lib/api';
	import { onMount } from 'svelte';

	let status = $state<{ status: string; db: string } | null>(null);
	let loading = $state(true);

	onMount(async () => {
		try {
			status = await api.get<{ status: string; db: string }>('/health');
		} catch {
			status = { status: 'error', db: 'error' };
		} finally {
			loading = false;
		}
	});
</script>

<svelte:head>
	<title>{{PROJECT_NAME_TITLE}}</title>
	<meta name="description" content="Mini-app {{PROJECT_NAME_TITLE}}" />
</svelte:head>

<div class="space-y-6">
	<div>
		<h1 class="text-3xl font-bold tracking-tight">{{PROJECT_NAME_TITLE}}</h1>
		<p class="text-muted-foreground mt-1">Bem-vindo ao seu mini-app.</p>
	</div>

	<!-- Status cards -->
	<div class="grid gap-4 md:grid-cols-3">
		<div class="rounded-lg border border-border bg-card p-4">
			<p class="text-sm font-medium text-muted-foreground">API</p>
			{#if loading}
				<p class="text-2xl font-bold mt-1 text-muted-foreground">...</p>
			{:else}
				<p class="text-2xl font-bold mt-1 {status?.status === 'ok' ? 'text-green-500' : 'text-red-500'}">
					{status?.status === 'ok' ? 'Online' : 'Offline'}
				</p>
			{/if}
		</div>

		<div class="rounded-lg border border-border bg-card p-4">
			<p class="text-sm font-medium text-muted-foreground">Banco de Dados</p>
			{#if loading}
				<p class="text-2xl font-bold mt-1 text-muted-foreground">...</p>
			{:else}
				<p class="text-2xl font-bold mt-1 {status?.db === 'ok' ? 'text-green-500' : 'text-red-500'}">
					{status?.db === 'ok' ? 'Conectado' : 'Erro'}
				</p>
			{/if}
		</div>

		<div class="rounded-lg border border-border bg-card p-4">
			<p class="text-sm font-medium text-muted-foreground">Swagger</p>
			<a
				href={`${import.meta.env.VITE_API_URL ?? 'http://localhost:8000'}/docs`}
				target="_blank"
				rel="noopener noreferrer"
				class="text-lg font-semibold mt-1 text-primary hover:underline inline-block"
			>
				Abrir Docs →
			</a>
		</div>
	</div>

	<div class="rounded-lg border border-border bg-card p-6">
		<h2 class="text-xl font-semibold mb-2">Começando</h2>
		<p class="text-muted-foreground text-sm">
			Este é o boilerplate do cockpit-mini-apps. Edite os arquivos em
			<code class="bg-muted px-1 py-0.5 rounded text-xs">frontend/src/routes/</code> para o frontend
			e <code class="bg-muted px-1 py-0.5 rounded text-xs">backend/app/</code> para a API.
		</p>
		<a href="/items" class="mt-4 inline-flex items-center text-sm text-primary hover:underline">
			Ver exemplo de CRUD →
		</a>
	</div>
</div>
