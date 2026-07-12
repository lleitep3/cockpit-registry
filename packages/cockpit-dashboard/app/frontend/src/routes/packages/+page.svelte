<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';

	type InstalledPackage = {
		name: string;
		version: string | null;
		description: string | null;
		status: string;
	};

	type RegistryPackage = {
		name: string;
		version: string;
		author: string;
		description: string;
		category: string;
		status: string;
		registry: string;
	};

	type Job = {
		id: string;
		status: string;
		progress: number;
		messages: string[];
	};

	let tab = $state<'installed' | 'registry'>('installed');
	let installed = $state<InstalledPackage[] | null>(null);
	let registry = $state<RegistryPackage[] | null>(null);
	let query = $state('');
	let selected = $state<RegistryPackage | InstalledPackage | null>(null);
	let job = $state<Job | null>(null);
	let drawerOpen = $state(false);

	async function load() {
		try {
			const [instRes, regRes] = await Promise.all([
				api.get<{ packages: InstalledPackage[] }>('/api/v1/packages').catch(() => ({ packages: [] })),
				api.get<{ packages: RegistryPackage[] }>('/api/v1/packages/registry').catch(() => ({ packages: [] })),
			]);
			installed = instRes.packages;
			registry = regRes.packages;
		} catch (e) {
			installed = [];
			registry = [];
		}
	}

	onMount(() => {
		load();
		const interval = setInterval(load, 30000);
		return () => clearInterval(interval);
	});

	function filteredInstalled() {
		if (!installed) return [];
		const q = query.toLowerCase();
		return installed.filter((p) => p.name.toLowerCase().includes(q) || (p.description || '').toLowerCase().includes(q));
	}

	function filteredRegistry() {
		if (!registry) return [];
		const q = query.toLowerCase();
		return registry.filter((p) =>
			p.name.toLowerCase().includes(q) ||
			(p.description || '').toLowerCase().includes(q) ||
			p.category.toLowerCase().includes(q)
		);
	}

	function openDetail(pkg: RegistryPackage | InstalledPackage) {
		selected = pkg;
		drawerOpen = true;
	}

	async function install(name: string) {
		try {
			const res = await api.post<{ job_id: string; error?: string }>('/api/v1/packages/install', { name });
			if (res.error) {
				alert(res.error);
				return;
			}
			job = { id: res.job_id, status: 'running', progress: 0, messages: [] };
			streamJob(res.job_id);
		} catch (e) {
			alert(e instanceof Error ? e.message : 'Erro ao instalar');
		}
	}

	function streamJob(jobId: string) {
		const source = new EventSource(`/api/v1/packages/jobs/${jobId}/stream`);
		source.onmessage = (event) => {
			try {
				const data = JSON.parse(event.data) as Job;
				job = data;
				if (data.status === 'completed' || data.status === 'failed') {
					source.close();
					load();
				}
			} catch {
				// ignore
			}
		};
		source.onerror = () => source.close();
	}

	function isInstalled(name: string) {
		return installed?.some((p) => p.name === name) ?? false;
	}
</script>

<svelte:head>
	<title>Pacotes | Cockpit Dashboard</title>
	<meta name="description" content="Gerenciador de pacotes do cockpit" />
</svelte:head>

<div class="space-y-6">
	<div>
		<h1 class="text-3xl font-bold tracking-tight">Pacotes</h1>
		<p class="text-muted-foreground mt-1">Gerencie pacotes instalados e explore o registry.</p>
	</div>

	<!-- Tabs -->
	<div class="flex items-center gap-2 border-b border-border">
		<button
			class="px-4 py-2 text-sm font-medium transition-colors border-b-2"
			class:text-foreground={tab === 'installed'}
			class:text-muted-foreground={tab !== 'installed'}
			class:border-primary={tab === 'installed'}
			class:border-transparent={tab !== 'installed'}
			onclick={() => (tab = 'installed')}
		>
			Instalados
		</button>
		<button
			class="px-4 py-2 text-sm font-medium transition-colors border-b-2"
			class:text-foreground={tab === 'registry'}
			class:text-muted-foreground={tab !== 'registry'}
			class:border-primary={tab === 'registry'}
			class:border-transparent={tab !== 'registry'}
			onclick={() => (tab = 'registry')}
		>
			Registry
		</button>
	</div>

	<!-- Search -->
	<div class="flex gap-2">
		<input
			type="text"
			placeholder="Buscar pacote..."
			class="flex-1 rounded-md border border-border bg-background px-3 py-2 text-sm"
			bind:value={query}
		/>
	</div>

	<!-- Job progress -->
	{#if job}
		<div class="rounded-xl border border-border bg-card/50 p-4">
			<div class="flex items-center justify-between mb-2">
				<span class="font-medium">Instalação: {job.status}</span>
				<span class="text-sm text-muted-foreground">{job.progress}%</span>
			</div>
			<div class="h-2 rounded-full bg-muted overflow-hidden">
				<div class="h-full bg-primary transition-all" style="width: {job.progress}%"></div>
			</div>
			{#if job.messages.length > 0}
				<div class="mt-2 text-xs text-muted-foreground">{job.messages[job.messages.length - 1]}</div>
			{/if}
		</div>
	{/if}

	<!-- List -->
	<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
		{#if tab === 'installed'}
			{#each filteredInstalled() as pkg}
				<button
					class="text-left rounded-xl border border-border bg-card/50 p-5 hover:bg-card/80 transition-colors"
					onclick={() => openDetail(pkg)}
				>
					<div class="flex items-center justify-between mb-2">
						<span class="font-semibold">{pkg.name}</span>
						{#if pkg.version}
							<span class="text-xs font-mono text-muted-foreground">v{pkg.version}</span>
						{/if}
					</div>
					{#if pkg.description}
						<p class="text-sm text-muted-foreground line-clamp-2">{pkg.description}</p>
					{/if}
					<div class="mt-3 text-xs text-emerald-400">{pkg.status}</div>
				</button>
			{:else}
				{#if installed === null}
					<p class="text-muted-foreground col-span-full">Carregando...</p>
				{:else}
					<p class="text-muted-foreground col-span-full">Nenhum pacote instalado.</p>
				{/if}
			{/each}
		{:else}
			{#each filteredRegistry() as pkg}
				<div class="rounded-xl border border-border bg-card/50 p-5 hover:bg-card/80 transition-colors">
					<div class="flex items-center justify-between mb-2">
						<span class="font-semibold">{pkg.name}</span>
						<span class="text-xs font-mono text-muted-foreground">v{pkg.version}</span>
					</div>
					{#if pkg.description}
						<p class="text-sm text-muted-foreground line-clamp-2">{pkg.description}</p>
					{/if}
					<div class="mt-3 flex items-center justify-between">
						<span class="text-xs text-muted-foreground">{pkg.category}</span>
						{#if isInstalled(pkg.name)}
							<span class="text-xs text-emerald-400">Instalado</span>
						{:else}
							<button
								class="text-xs bg-primary text-primary-foreground px-2 py-1 rounded"
								onclick={() => install(pkg.name)}
							>
								Instalar
							</button>
						{/if}
					</div>
				</div>
			{:else}
				{#if registry === null}
					<p class="text-muted-foreground col-span-full">Carregando...</p>
				{:else}
					<p class="text-muted-foreground col-span-full">Nenhum pacote encontrado.</p>
				{/if}
			{/each}
		{/if}
	</div>
</div>

<!-- Drawer -->
{#if drawerOpen && selected}
	<div class="fixed inset-0 z-50 bg-black/50" onclick={() => (drawerOpen = false)} role="presentation"></div>
	<div class="fixed inset-y-0 right-0 z-50 w-full max-w-md bg-slate-900 border-l border-border p-6 overflow-y-auto shadow-2xl">
		<div class="flex items-center justify-between mb-6">
			<h2 class="text-xl font-bold">{selected.name}</h2>
			<button class="text-muted-foreground hover:text-foreground" onclick={() => (drawerOpen = false)}>✕</button>
		</div>
		{#if 'version' in selected && selected.version}
			<div class="mb-2 text-sm text-muted-foreground">Versão: {selected.version}</div>
		{/if}
		{#if 'category' in selected}
			<div class="mb-2 text-sm text-muted-foreground">Categoria: {selected.category}</div>
		{/if}
		{#if 'registry' in selected}
			<div class="mb-2 text-sm text-muted-foreground">Registry: {selected.registry}</div>
		{/if}
		{#if selected.description}
			<p class="text-sm text-muted-foreground mb-6">{selected.description}</p>
		{/if}
		{#if 'author' in selected && selected.author}
			<div class="text-sm text-muted-foreground mb-6">Autor: {selected.author}</div>
		{/if}
		{#if tab === 'registry' && selected && 'name' in selected && !isInstalled(selected.name)}
			<button class="w-full bg-primary text-primary-foreground py-2 rounded-md" onclick={() => { install(selected.name); drawerOpen = false; }}>
				Instalar
			</button>
		{/if}
	</div>
{/if}
