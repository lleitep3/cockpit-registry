<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';

	type Source = {
		name: string;
		url: string;
	};

	type RegistryPackage = {
		name: string;
		version: string;
		author?: string;
		description?: string;
		category?: string;
		status?: string;
		registry: string;
	};

	type InstalledPackage = {
		name: string;
		version: string | null;
	};

	let sources = $state<Source[] | null>(null);
	let catalog = $state<RegistryPackage[] | null>(null);
	let installed = $state<InstalledPackage[] | null>(null);
	let query = $state('');
	let loading = $state(true);

	async function load() {
		try {
			loading = true;
			const [sourcesRes, catRes, instRes] = await Promise.all([
				api.get<{ sources: Source[] }>('/api/v1/packages/sources').catch(() => ({ sources: [] })),
				api.get<{ packages: RegistryPackage[] }>('/api/v1/packages/registry').catch(() => ({ packages: [] })),
				api.get<{ packages: InstalledPackage[] }>('/api/v1/packages').catch(() => ({ packages: [] }))
			]);
			sources = sourcesRes.sources;
			catalog = catRes.packages;
			installed = instRes.packages;
		} catch (e) {
			console.error(e);
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		load();
	});

	function filteredCatalog() {
		if (!catalog) return [];
		const q = query.toLowerCase();
		return catalog.filter(p => 
			p.name.toLowerCase().includes(q) || 
			(p.description || '').toLowerCase().includes(q)
		);
	}

	function isInstalled(name: string) {
		return installed?.some((p) => p.name === name) ?? false;
	}

	async function install(name: string) {
		// Mock API call to install
		alert(`Instalação do pacote ${name} disparada (mock). Verifique a aba pacotes instalados!`);
	}
</script>

<svelte:head>
	<title>Registries | Cockpit Dashboard</title>
</svelte:head>

<div class="space-y-8">
	<div>
		<h1 class="text-3xl font-bold tracking-tight">Registries</h1>
		<p class="text-muted-foreground mt-1">Fontes de pacotes do marketplace consultadas pelo seu cockpit, e o catálogo completo delas.</p>
	</div>

	<!-- Fontes Configuradas -->
	<div class="rounded-xl border border-border/50 bg-card/40 backdrop-blur-sm overflow-hidden">
		<div class="p-4 border-b border-border/50 flex justify-between items-center bg-background/20">
			<h2 class="font-semibold text-gray-200">{sources?.length || 0} fonte(s) configurada(s)</h2>
			<button class="bg-primary/90 hover:bg-primary text-primary-foreground px-4 py-2 text-sm font-medium rounded-md transition-colors">
				+ Adicionar fonte
			</button>
		</div>
		
		<div class="overflow-x-auto">
			<table class="w-full text-sm text-left">
				<thead class="text-xs uppercase text-muted-foreground bg-background/10 border-b border-border/50">
					<tr>
						<th class="px-6 py-3 font-semibold">Nome</th>
						<th class="px-6 py-3 font-semibold">URL</th>
						<th class="px-6 py-3 text-right font-semibold">Ação</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-border/30">
					{#if sources}
						{#each sources as source}
							<tr class="hover:bg-muted/10 transition-colors">
								<td class="px-6 py-4 font-medium text-gray-200">{source.name}</td>
								<td class="px-6 py-4 text-muted-foreground font-mono text-xs">{source.url || 'N/A'}</td>
								<td class="px-6 py-4 text-right">
									<button class="text-red-400 hover:text-red-300 text-xs font-medium">🗑 Remover</button>
								</td>
							</tr>
						{/each}
					{:else}
						<tr><td colspan="3" class="px-6 py-4 text-center text-muted-foreground">Carregando...</td></tr>
					{/if}
				</tbody>
			</table>
		</div>
	</div>

	<!-- Catálogo de Pacotes -->
	<div class="rounded-xl border border-border/50 bg-card/40 backdrop-blur-sm overflow-hidden">
		<div class="p-4 border-b border-border/50 bg-background/20">
			<h2 class="font-semibold text-gray-200 mb-4">{catalog?.length || 0} pacote(s) no catálogo</h2>
			<div class="flex gap-2">
				<div class="relative flex-1">
					<svg class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
						<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
					</svg>
					<input
						type="text"
						placeholder="Buscar pacote por nome (ex: jira, ods-*)"
						class="w-full pl-10 pr-4 py-2 bg-background/50 border border-border/50 rounded-md text-sm focus:outline-none focus:ring-1 focus:ring-primary transition-all"
						bind:value={query}
					/>
				</div>
				<button class="bg-primary/90 hover:bg-primary text-primary-foreground px-6 py-2 text-sm font-medium rounded-md transition-colors">
					Buscar
				</button>
			</div>
		</div>

		<div class="overflow-x-auto">
			<table class="w-full text-sm text-left">
				<thead class="text-xs uppercase text-muted-foreground bg-background/10 border-b border-border/50">
					<tr>
						<th class="px-6 py-3 font-semibold">Nome</th>
						<th class="px-6 py-3 font-semibold">Versão</th>
						<th class="px-6 py-3 font-semibold">Fonte</th>
						<th class="px-6 py-3 font-semibold">Status</th>
						<th class="px-6 py-3 font-semibold">Descrição</th>
						<th class="px-6 py-3 text-right font-semibold">Ação</th>
					</tr>
				</thead>
				<tbody class="divide-y divide-border/30">
					{#if catalog}
						{#each filteredCatalog() as pkg}
							{@const isInst = isInstalled(pkg.name)}
							<tr class="hover:bg-muted/10 transition-colors">
								<td class="px-6 py-4 font-semibold text-gray-200">{pkg.name}</td>
								<td class="px-6 py-4 text-muted-foreground font-mono text-xs">{pkg.version || '0.1.0'}</td>
								<td class="px-6 py-4">
									<span class="px-2.5 py-1 text-[10px] font-semibold tracking-wider border border-border/50 rounded-full text-muted-foreground uppercase bg-background/50">
										{pkg.registry}
									</span>
								</td>
								<td class="px-6 py-4">
									{#if isInst}
										<span class="px-2.5 py-1 text-[10px] font-semibold tracking-wider rounded-full text-emerald-400 bg-emerald-400/10 border border-emerald-400/20">INSTALADO</span>
									{:else}
										<span class="px-2.5 py-1 text-[10px] font-semibold tracking-wider rounded-full text-gray-400 bg-gray-400/10 border border-gray-400/20">DISPONÍVEL</span>
									{/if}
								</td>
								<td class="px-6 py-4 text-muted-foreground truncate max-w-[300px]" title={pkg.description}>
									{pkg.description || 'Pacote do local-registry sem descrição.'}
								</td>
								<td class="px-6 py-4 text-right">
									{#if !isInst}
										<button class="text-xs font-semibold text-primary hover:text-primary-foreground border border-primary/50 hover:bg-primary px-4 py-1.5 rounded transition-colors" onclick={() => install(pkg.name)}>
											↓ Instalar
										</button>
									{/if}
								</td>
							</tr>
						{/each}
					{:else}
						<tr><td colspan="6" class="px-6 py-4 text-center text-muted-foreground">Carregando catálogo...</td></tr>
					{/if}
				</tbody>
			</table>
		</div>
	</div>
</div>
