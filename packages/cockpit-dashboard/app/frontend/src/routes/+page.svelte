<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import StatusCard from '$lib/components/StatusCard.svelte';
	import ProvidersPanel from '$lib/components/ProvidersPanel.svelte';
	import PackagesPanel from '$lib/components/PackagesPanel.svelte';
	import RegistriesPanel from '$lib/components/RegistriesPanel.svelte';
	import KBPanel from '$lib/components/KBPanel.svelte';

	let status = $state<{ version: string; environment: string; active: boolean } | null>(null);
	let providers = $state<{ name: string; active?: boolean }[] | null>(null);
	let packages = $state<{ name: string; version?: string; description?: string }[] | null>(null);
	let registries = $state<{ name: string; url?: string }[] | null>(null);
	let documents = $state<{ name: string; category: string; path: string }[] | null>(null);

	async function load() {
		try {
			status = await api.get<{ version: string; environment: string; active: boolean }>('/api/v1/cockpit/status');
		} catch {
			status = { version: 'unknown', environment: 'unknown', active: false };
		}
		try {
			const res = await api.get<{ providers: { name: string; active?: boolean }[] }>('/api/v1/cockpit/providers');
			providers = res.providers;
		} catch {
			providers = [];
		}
		try {
			const res = await api.get<{ packages: { name: string; version?: string; description?: string }[] }>('/api/v1/cockpit/packages');
			packages = res.packages;
		} catch {
			packages = [];
		}
		try {
			const res = await api.get<{ registries: { name: string; url?: string }[] }>('/api/v1/cockpit/registries');
			registries = res.registries;
		} catch {
			registries = [];
		}
		try {
			const res = await api.get<{ documents: { name: string; category: string; path: string }[] }>('/api/v1/cockpit/kb');
			documents = res.documents;
		} catch {
			documents = [];
		}
	}

	onMount(() => {
		load();
		const interval = setInterval(load, 30000);
		return () => clearInterval(interval);
	});
</script>

<svelte:head>
	<title>Cockpit Dashboard</title>
	<meta name="description" content="Dashboard visual do AICockpit" />
</svelte:head>

<div class="space-y-6">
	<div>
		<h1 class="text-3xl font-bold tracking-tight">Cockpit Dashboard</h1>
		<p class="text-muted-foreground mt-1">Estado atual do AICockpit em tempo real.</p>
	</div>

	<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
		<StatusCard {status} />
		<ProvidersPanel {providers} />
		<PackagesPanel {packages} />
		<RegistriesPanel {registries} />
		<KBPanel {documents} />
	</div>
</div>
