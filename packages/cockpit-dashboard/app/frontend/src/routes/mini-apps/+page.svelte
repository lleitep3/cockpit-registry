<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';

	type MiniApp = {
		name: string;
		path: string;
		backend_pid: number | null;
		frontend_pid: number | null;
		port: number | null;
		health: boolean;
		status: 'running' | 'stopped' | 'failing';
		uptime: number | null;
	};

	let apps = $state<MiniApp[] | null>(null);
	let selected = $state<MiniApp | null>(null);
	let logs = $state<string[]>([]);
	let logSource: EventSource | null = null;
	let service = $state<'backend' | 'frontend'>('backend');

	async function load() {
		try {
			const res = await api.get<{ mini_apps: MiniApp[] }>('/api/v1/mini-apps');
			apps = res.mini_apps;
		} catch {
			apps = [];
		}
	}

	onMount(() => {
		load();
		const interval = setInterval(load, 5000);
		return () => {
			clearInterval(interval);
			logSource?.close();
		};
	});

	function selectApp(app: MiniApp) {
		selected = app;
		logs = [];
		connectLogs(app.name);
	}

	function connectLogs(name: string) {
		logSource?.close();
		logSource = new EventSource(`/api/v1/mini-apps/${name}/logs/stream?service=${service}`);
		logSource.onmessage = (event) => {
			logs = [...logs, event.data];
		};
		logSource.onerror = () => logSource?.close();
	}

	async function action(name: string, action: 'start' | 'stop' | 'restart') {
		try {
			await api.post(`/api/v1/mini-apps/${name}/${action}`, {});
			await load();
		} catch (e) {
			alert(e instanceof Error ? e.message : 'Erro');
		}
	}

	function formatUptime(seconds: number | null) {
		if (seconds === null) return '-';
		const m = Math.floor(seconds / 60);
		const s = Math.floor(seconds % 60);
		return `${m}m ${s}s`;
	}

	function openApp(port: number | null) {
		if (port) window.open(`http://localhost:${port}`, '_blank');
	}
</script>

<svelte:head>
	<title>Mini-Apps | Cockpit Dashboard</title>
	<meta name="description" content="Console de mini-apps do cockpit" />
</svelte:head>

<div class="space-y-6 h-[calc(100vh-8rem)]">
	<div>
		<h1 class="text-3xl font-bold tracking-tight">Mini-Apps</h1>
		<p class="text-muted-foreground mt-1">Monitore e controle mini-apps locais.</p>
	</div>

	{#if apps === null}
		<p class="text-muted-foreground">Carregando...</p>
	{:else if apps.length === 0}
		<p class="text-muted-foreground">Nenhum mini-app encontrado.</p>
	{:else}
		<div class="grid gap-4 lg:grid-cols-3 h-full">
			<!-- Cards -->
			<div class="lg:col-span-1 space-y-3 overflow-y-auto pr-2">
				{#each apps as app}
					<button
						class="w-full text-left rounded-xl border border-border p-4 transition-colors"
						class:bg-primary={selected?.name === app.name}
						class:text-primary-foreground={selected?.name === app.name}
						class:bg-muted={selected?.name !== app.name}
						onclick={() => selectApp(app)}
					>
						<div class="flex items-center justify-between">
							<span class="font-semibold">{app.name}</span>
							<span class="text-xs flex items-center gap-1.5">
								<span class="h-2 w-2 rounded-full {app.status === 'running' ? 'bg-emerald-400' : app.status === 'failing' ? 'bg-red-400' : 'bg-slate-400'}"></span>
								{app.status}
							</span>
						</div>
						<div class="mt-2 text-xs opacity-80">
							Porta: {app.port || '-'} | Uptime: {formatUptime(app.uptime)}
						</div>
						<div class="mt-2 flex gap-2">
							{#if app.status !== 'running'}
								<button
									class="text-xs bg-emerald-500 text-white px-2 py-1 rounded"
									onclick={(e) => { e.stopPropagation(); action(app.name, 'start'); }}
								>Start</button>
								{:else}
								<button
									class="text-xs bg-red-500 text-white px-2 py-1 rounded"
									onclick={(e) => { e.stopPropagation(); action(app.name, 'stop'); }}
								>Stop</button>
								<button
									class="text-xs bg-slate-600 text-white px-2 py-1 rounded"
									onclick={(e) => { e.stopPropagation(); action(app.name, 'restart'); }}
								>Restart</button>
							{/if}
							{#if app.port && app.health}
								<button
									class="text-xs bg-primary text-primary-foreground px-2 py-1 rounded"
									onclick={(e) => { e.stopPropagation(); openApp(app.port); }}
								>Abrir</button>
							{/if}
						</div>
					</button>
				{/each}
			</div>

			<!-- Logs -->
			<div class="lg:col-span-2 flex flex-col rounded-xl border border-border bg-black p-4">
				<div class="flex items-center justify-between mb-3">
					<h2 class="font-semibold text-green-400 font-mono">
						{selected ? `Logs: ${selected.name}` : 'Selecione um mini-app'}
					</h2>
					{#if selected}
						<select
							class="bg-slate-900 border border-border text-xs rounded px-2 py-1"
							bind:value={service}
							onchange={() => connectLogs(selected!.name)}
						>
							<option value="backend">Backend</option>
							<option value="frontend">Frontend</option>
						</select>
					{/if}
				</div>
				<div class="flex-1 overflow-y-auto font-mono text-xs text-green-400 space-y-1">
					{#if selected}
						{#if logs.length === 0}
							<span class="text-slate-500">Aguardando logs...</span>
						{:else}
							{#each logs as line}
								<div class="break-all">{line}</div>
							{/each}
						{/if}
					{:else}
						<span class="text-slate-500">Selecione um mini-app para ver os logs.</span>
					{/if}
				</div>
			</div>
		</div>
	{/if}
</div>
