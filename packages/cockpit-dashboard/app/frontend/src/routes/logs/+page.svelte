<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';

	type Insight = {
		total: number;
		successful: number;
		failed: number;
		success_rate: number;
		avg_duration_ms: number;
		total_duration_ms: number;
		commands: { command: string; count: number; avg_duration_ms: number }[];
		error_types: { error_type: string; count: number }[];
		slowest_commands: { command: string; avg_duration_ms: number; max_duration_ms: number }[];
		timeline: { date: string; success: number; error: number }[];
	};

	let insights = $state<Insight | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let commandFilter = $state('');
	let statusFilter = $state<'all' | 'success' | 'error'>('all');

	async function load() {
		try {
			loading = true;
			error = null;
			insights = await api.get<Insight>('/api/v1/logs/insights');
		} catch (e) {
			error = e instanceof Error ? e.message : 'Erro ao carregar insights';
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		load();
		const interval = setInterval(load, 30000);
		return () => clearInterval(interval);
	});

	function filteredCommands() {
		if (!insights) return [];
		const term = commandFilter.toLowerCase();
		return insights.commands.filter((c) => c.command.toLowerCase().includes(term));
	}

	function filteredErrors() {
		if (!insights) return [];
		if (statusFilter === 'success') return [];
		return insights.error_types;
	}
</script>

<svelte:head>
	<title>Logs & Insights | Cockpit Dashboard</title>
	<meta name="description" content="Análise de logs e métricas de execução do cockpit" />
</svelte:head>

<div class="space-y-6">
	<div>
		<h1 class="text-3xl font-bold tracking-tight">Logs & Insights</h1>
		<p class="text-muted-foreground mt-1">Análise de execuções e métricas do cockpit.</p>
	</div>

	{#if loading && !insights}
		<p class="text-muted-foreground">Carregando...</p>
	{:else if error}
		<div class="rounded-lg border border-red-800 bg-red-950/30 p-4 text-red-200">
			{error}
		</div>
	{:else if insights}
		<!-- KPIs -->
		<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
			<div class="rounded-xl border border-border bg-card/50 p-6">
				<div class="text-sm text-muted-foreground">Total de Execuções</div>
				<div class="text-2xl font-bold mt-1">{insights.total}</div>
			</div>
			<div class="rounded-xl border border-border bg-card/50 p-6">
				<div class="text-sm text-muted-foreground">Taxa de Sucesso</div>
				<div class="text-2xl font-bold mt-1 text-emerald-400">{insights.success_rate}%</div>
			</div>
			<div class="rounded-xl border border-border bg-card/50 p-6">
				<div class="text-sm text-muted-foreground">Erros</div>
				<div class="text-2xl font-bold mt-1 text-red-400">{insights.failed}</div>
			</div>
			<div class="rounded-xl border border-border bg-card/50 p-6">
				<div class="text-sm text-muted-foreground">Duração Média</div>
				<div class="text-2xl font-bold mt-1">{insights.avg_duration_ms}ms</div>
			</div>
		</div>

		<!-- Timeline -->
		{#if insights.timeline.length > 0}
			<div class="rounded-xl border border-border bg-card/50 p-6">
				<h2 class="text-lg font-semibold mb-4">Atividade ao Longo do Tempo</h2>
				<div class="flex items-end gap-1 h-32">
					{#each insights.timeline as day}
						<div class="flex-1 flex flex-col gap-1 min-w-[2rem]">
							<div
								class="bg-emerald-500 rounded-t"
								style="height: {Math.max(4, (day.success / (day.success + day.error || 1)) * 100)}%"
							></div>
							<div
								class="bg-red-500 rounded-b"
								style="height: {Math.max(4, (day.error / (day.success + day.error || 1)) * 100)}%"
							></div>
							<div class="text-[10px] text-muted-foreground text-center truncate" title={day.date}>
								{day.date.slice(5)}
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<div class="grid gap-4 lg:grid-cols-2">
			<!-- Comandos mais executados -->
			<div class="rounded-xl border border-border bg-card/50 p-6">
				<div class="flex items-center justify-between mb-4">
					<h2 class="text-lg font-semibold">Comandos</h2>
					<input
						type="text"
						placeholder="Filtrar comando..."
						class="rounded-md border border-border bg-background px-3 py-1 text-sm"
						bind:value={commandFilter}
					/>
				</div>
				<ul class="space-y-2">
					{#each filteredCommands() as cmd}
						<li class="flex items-center justify-between rounded-lg border border-border bg-background/50 px-3 py-2">
							<span class="font-medium">{cmd.command}</span>
							<div class="text-right text-sm text-muted-foreground">
								<div>{cmd.count} execuções</div>
								<div>média {cmd.avg_duration_ms}ms</div>
							</div>
						</li>
					{:else}
						<li class="text-muted-foreground">Nenhum comando encontrado.</li>
					{/each}
				</ul>
			</div>

			<!-- Erros -->
			<div class="rounded-xl border border-border bg-card/50 p-6">
				<h2 class="text-lg font-semibold mb-4">Erros por Tipo</h2>
				<ul class="space-y-2">
					{#each filteredErrors() as err}
						<li class="flex items-center justify-between rounded-lg border border-border bg-background/50 px-3 py-2">
							<span class="font-medium text-red-300">{err.error_type}</span>
							<span class="text-sm text-muted-foreground">{err.count} ocorrências</span>
						</li>
					{:else}
						<li class="text-muted-foreground">Nenhum erro registrado.</li>
					{/each}
				</ul>
			</div>
		</div>

		<!-- Comandos mais lentos -->
		{#if insights.slowest_commands.length > 0}
			<div class="rounded-xl border border-border bg-card/50 p-6">
				<h2 class="text-lg font-semibold mb-4">Comandos Mais Lentos</h2>
				<div class="overflow-x-auto">
					<table class="w-full text-sm">
						<thead class="border-b border-border text-muted-foreground">
							<tr>
								<th class="py-2 text-left">Comando</th>
								<th class="py-2 text-right">Duração Média</th>
								<th class="py-2 text-right">Duração Máxima</th>
							</tr>
						</thead>
						<tbody class="divide-y divide-border">
							{#each insights.slowest_commands as cmd}
								<tr>
									<td class="py-2 font-medium">{cmd.command}</td>
									<td class="py-2 text-right">{cmd.avg_duration_ms}ms</td>
									<td class="py-2 text-right">{cmd.max_duration_ms}ms</td>
								</tr>
							{/each}
						</tbody>
					</table>
				</div>
			</div>
		{/if}
	{/if}
</div>
