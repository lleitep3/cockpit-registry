<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';

	type ErrorDetail = {
		timestamp: string;
		command: string;
		args: string[];
		exit_code: number;
		duration_ms: number;
		user: string;
		version: string;
		language: string;
		error: string;
		error_type: string;
	};

	type CommandErrorRate = {
		command: string;
		total: number;
		failed: number;
		rate: number;
	};

	type GeneratedInsight = {
		type: 'success' | 'info' | 'warning' | 'error';
		title: string;
		description: string;
	};

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
		recent_errors: ErrorDetail[];
		command_error_rates: CommandErrorRate[];
		generated_insights: GeneratedInsight[];
	};

	let insights = $state<Insight | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);
	let commandFilter = $state('');
	let activeTab = $state<'errors' | 'performance'>('errors');
	let selectedError = $state<ErrorDetail | null>(null);

	type AIDiagnosis = {
		diagnosis: string;
		suggested_fix: string;
		kb_reference: string | null;
	};

	let diagnosing = $state(false);
	let aiDiagnosis = $state<AIDiagnosis | null>(null);

	async function diagnoseError(error: ErrorDetail) {
		diagnosing = true;
		aiDiagnosis = null;
		try {
			aiDiagnosis = await api.post<AIDiagnosis>('/api/v1/logs/diagnose', {
				command: error.command,
				error_msg: error.error,
				error_type: error.error_type,
				args: error.args
			});
		} catch (e) {
			console.error('Failed to diagnose', e);
		} finally {
			diagnosing = false;
		}
	}

	let fixing = $state(false);

	async function executeAutoFix(command: string) {
		fixing = true;
		try {
			const res = await api.post<{ success: boolean; stdout?: string; stderr?: string; error?: string }>('/api/v1/logs/autofix', { command });
			if (res.success) {
				alert('Comando executado com sucesso!\n\n' + (res.stdout || ''));
			} else {
				alert('Falha ao executar comando:\n\n' + (res.stderr || res.error || 'Erro desconhecido'));
			}
		} catch (e) {
			alert('Erro na requisição: ' + (e instanceof Error ? e.message : 'desconhecido'));
		} finally {
			fixing = false;
		}
	}

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

	// Derived states
	const maxDailyExecutions = $derived(() => {
		if (!insights || insights.timeline.length === 0) return 1;
		return Math.max(...insights.timeline.map((t) => t.success + t.error));
	});

	function filteredCommands() {
		if (!insights) return [];
		const term = commandFilter.toLowerCase();
		return insights.commands.filter((c) => c.command.toLowerCase().includes(term));
	}

	// Filter and sort by highest failure rate
	function filteredErrorRates() {
		if (!insights) return [];
		const term = commandFilter.toLowerCase();
		return insights.command_error_rates.filter((c) => c.command.toLowerCase().includes(term));
	}
</script>

<svelte:head>
	<title>Logs & Insights | Cockpit Dashboard</title>
	<meta name="description" content="Análise de logs e métricas de execução do cockpit" />
</svelte:head>

<div class="space-y-6 max-w-7xl mx-auto px-4 md:px-6">
	<!-- Top Header -->
	<div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
		<div>
			<h1 class="text-3xl font-bold tracking-tight bg-gradient-to-r from-white to-slate-400 bg-clip-text text-transparent">Logs & Insights</h1>
			<p class="text-muted-foreground mt-1">Análise em tempo real de execuções, erros e performance do cockpit.</p>
		</div>
		<button 
			onclick={load} 
			disabled={loading}
			class="inline-flex items-center gap-2 self-start md:self-auto rounded-md bg-secondary text-secondary-foreground hover:bg-secondary/80 px-4 py-2 text-sm font-medium border border-border transition-colors"
		>
			{#if loading}
				<svg class="animate-spin h-4 w-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
					<circle cx="12" cy="12" r="10" stroke-dasharray="30" stroke-dashoffset="10"></circle>
				</svg>
				Atualizando...
			{:else}
				<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M21.5 2v6h-6M21.34 15.57a10 10 0 1 1-.57-8.38l5.67-5.67"/>
				</svg>
				Atualizar
			{/if}
		</button>
	</div>

	{#if error}
		<div class="rounded-lg border border-destructive bg-destructive/10 p-4 text-destructive flex items-start gap-3">
			<svg class="h-5 w-5 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line>
			</svg>
			<div>
				<h4 class="font-semibold">Erro de Conexão</h4>
				<p class="text-sm mt-0.5">{error}</p>
			</div>
		</div>
	{/if}

	{#if insights}
		<!-- KPIs Grid -->
		<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
			<div class="rounded-xl border border-border bg-slate-900/40 backdrop-blur p-6 hover:border-border/80 transition-all">
				<div class="text-sm text-muted-foreground font-medium">Total de Execuções</div>
				<div class="text-3xl font-extrabold mt-2 text-white">{insights.total}</div>
			</div>
			<div class="rounded-xl border border-border bg-slate-900/40 backdrop-blur p-6 hover:border-border/80 transition-all">
				<div class="text-sm text-muted-foreground font-medium">Taxa de Sucesso</div>
				<div class="text-3xl font-extrabold mt-2 text-emerald-400">{insights.success_rate}%</div>
			</div>
			<div class="rounded-xl border border-border bg-slate-900/40 backdrop-blur p-6 hover:border-border/80 transition-all">
				<div class="text-sm text-muted-foreground font-medium">Execuções com Erro</div>
				<div class="text-3xl font-extrabold mt-2 text-red-400">{insights.failed}</div>
			</div>
			<div class="rounded-xl border border-border bg-slate-900/40 backdrop-blur p-6 hover:border-border/80 transition-all">
				<div class="text-sm text-muted-foreground font-medium">Duração Média</div>
				<div class="text-3xl font-extrabold mt-2 text-white">{insights.avg_duration_ms} ms</div>
			</div>
		</div>

		<!-- Smart Insights Panel -->
		{#if insights.generated_insights.length > 0}
			<div class="rounded-xl border border-border bg-slate-900/20 backdrop-blur p-6">
				<h2 class="text-lg font-bold text-white mb-4 flex items-center gap-2">
					<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
					</svg>
					Insights da Plataforma
				</h2>
				<div class="grid gap-3 md:grid-cols-2">
					{#each insights.generated_insights as item}
						<div class="rounded-lg border p-4 flex gap-3 text-sm transition-all
							{item.type === 'success' ? 'bg-emerald-950/20 border-emerald-900/50 text-emerald-300' : ''}
							{item.type === 'info' ? 'bg-blue-950/20 border-blue-900/50 text-blue-300' : ''}
							{item.type === 'warning' ? 'bg-amber-950/20 border-amber-900/50 text-amber-300' : ''}
							{item.type === 'error' ? 'bg-red-950/20 border-red-900/50 text-red-300' : ''}"
						>
							<div class="mt-0.5">
								{#if item.type === 'success'}
									<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
								{:else if item.type === 'warning' || item.type === 'error'}
									<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
								{:else}
									<svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
								{/if}
							</div>
							<div>
								<span class="font-semibold block">{item.title}</span>
								<span class="text-xs text-muted-foreground mt-1 block">{item.description}</span>
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Timeline Chart -->
		{#if insights.timeline.length > 0}
			<div class="rounded-xl border border-border bg-slate-900/40 backdrop-blur p-6">
				<h2 class="text-lg font-bold text-white mb-4">Atividade ao Longo do Tempo</h2>
				<div class="flex items-end gap-2 h-48 border-b border-border/60 pb-2 px-2 overflow-x-auto">
					{#each insights.timeline as day}
						{@const totalExecs = day.success + day.error}
						{@const heightPercent = (totalExecs / maxDailyExecutions()) * 100}
						<div class="flex-1 flex flex-col items-center group h-full justify-end relative min-w-[2.5rem]">
							<!-- Bar -->
							<div class="w-full flex flex-col justify-end rounded overflow-hidden shadow-inner" style="height: {heightPercent}%">
								{#if day.success > 0}
									<div 
										class="bg-emerald-500 w-full hover:brightness-110 transition-all cursor-pointer" 
										style="height: {(day.success / totalExecs) * 100}%"
									></div>
								{/if}
								{#if day.error > 0}
									<div 
										class="bg-red-500 w-full hover:brightness-110 transition-all cursor-pointer" 
										style="height: {(day.error / totalExecs) * 100}%"
									></div>
								{/if}
							</div>

							<!-- Label -->
							<div class="text-[10px] text-muted-foreground mt-2 text-center truncate w-full font-mono">
								{day.date.slice(5)}
							</div>

							<!-- Custom Hover Tooltip -->
							<div class="absolute bottom-full mb-2 hidden group-hover:block bg-slate-950/95 border border-border/80 text-white text-xs rounded-lg p-3 shadow-xl z-20 w-44">
								<div class="font-bold border-b border-border pb-1 mb-1 font-mono">{day.date}</div>
								<div class="flex justify-between mt-1 text-emerald-400">
									<span>Sucesso:</span>
									<span class="font-bold">{day.success}</span>
								</div>
								<div class="flex justify-between text-red-400">
									<span>Erros:</span>
									<span class="font-bold">{day.error}</span>
								</div>
								<div class="flex justify-between border-t border-border mt-1 pt-1 text-slate-300 font-semibold">
									<span>Total:</span>
									<span>{totalExecs}</span>
								</div>
							</div>
						</div>
					{/each}
				</div>
			</div>
		{/if}

		<!-- Tabs navigation -->
		<div class="border-b border-border flex gap-4">
			<button 
				class="py-2.5 px-1 font-medium text-sm border-b-2 transition-all"
				class:border-primary={activeTab === 'errors'}
				class:text-white={activeTab === 'errors'}
				class:border-transparent={activeTab !== 'errors'}
				class:text-muted-foreground={activeTab !== 'errors'}
				onclick={() => activeTab = 'errors'}
			>
				Erros & Logs Recentes
			</button>
			<button 
				class="py-2.5 px-1 font-medium text-sm border-b-2 transition-all"
				class:border-primary={activeTab === 'performance'}
				class:text-white={activeTab === 'performance'}
				class:border-transparent={activeTab !== 'performance'}
				class:text-muted-foreground={activeTab !== 'performance'}
				onclick={() => activeTab = 'performance'}
			>
				Estatísticas de Performance
			</button>
		</div>

		<!-- Tab Contents -->
		{#if activeTab === 'errors'}
			<div class="grid gap-6 lg:grid-cols-3">
				<!-- Recent Errors Logs List (Col Span 2) -->
				<div class="lg:col-span-2 rounded-xl border border-border bg-slate-900/40 p-6 space-y-4">
					<h2 class="text-lg font-bold text-white">Últimas Falhas Registradas</h2>
					
					<div class="divide-y divide-border overflow-hidden">
						{#each insights.recent_errors as err}
							<div class="py-3 flex flex-col md:flex-row md:items-center justify-between gap-3 text-sm">
								<div class="space-y-1">
									<div class="flex items-center gap-2">
										<span class="font-mono font-bold text-red-400 bg-red-950/40 px-2 py-0.5 rounded border border-red-900/50">{err.command}</span>
										{#if err.args.length > 0}
											<span class="text-xs text-muted-foreground font-mono bg-muted/40 px-1.5 py-0.5 rounded">{err.args.join(' ')}</span>
										{/if}
									</div>
									<div class="text-xs text-muted-foreground flex items-center gap-2 font-mono">
										<span>{new Date(err.timestamp).toLocaleTimeString()}</span>
										<span>•</span>
										<span>Usuário: {err.user}</span>
										<span>•</span>
										<span class="text-red-300 truncate max-w-xs">{err.error}</span>
									</div>
								</div>
								<button 
									onclick={() => selectedError = err}
									class="inline-flex items-center gap-1 text-xs font-semibold text-primary hover:text-primary/80 transition-colors self-start md:self-auto border border-primary/25 rounded px-2.5 py-1 bg-primary/5 hover:bg-primary/10"
								>
									Ver Detalhes (Trace)
								</button>
							</div>
						{:else}
							<div class="text-center py-8 text-muted-foreground">
								<svg class="h-8 w-8 mx-auto mb-2 text-emerald-500" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
									<path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
								</svg>
								Nenhuma falha de comando registrada recentemente!
							</div>
						{/each}
					</div>
				</div>

				<!-- Right column: Error type count summary -->
				<div class="rounded-xl border border-border bg-slate-900/40 p-6 space-y-4">
					<h2 class="text-lg font-bold text-white">Tipos de Erros</h2>
					<ul class="space-y-3">
						{#each insights.error_types as err}
							<li class="rounded-lg border border-border/80 bg-background/30 p-3 flex items-center justify-between">
								<div class="font-mono text-xs text-red-300 font-semibold truncate max-w-[70%]" title={err.error_type}>
									{err.error_type}
								</div>
								<div class="text-xs font-bold text-muted-foreground bg-muted px-2 py-1 rounded">
									{err.count} ocorrências
								</div>
							</li>
						{:else}
							<li class="text-muted-foreground text-center py-4">Nenhum erro registrado.</li>
						{/each}
					</ul>
				</div>
			</div>
		{:else if activeTab === 'performance'}
			<div class="grid gap-6 lg:grid-cols-2">
				<!-- Slowest executions -->
				<div class="rounded-xl border border-border bg-slate-900/40 p-6 space-y-4">
					<h2 class="text-lg font-bold text-white">Comandos Mais Lentos</h2>
					<div class="overflow-x-auto">
						<table class="w-full text-sm">
							<thead class="border-b border-border text-muted-foreground font-medium">
								<tr>
									<th class="py-2 text-left pb-3">Comando</th>
									<th class="py-2 text-right pb-3">Duração Média</th>
									<th class="py-2 text-right pb-3">Duração Máxima</th>
								</tr>
							</thead>
							<tbody class="divide-y divide-border">
								{#each insights.slowest_commands as cmd}
									<tr class="hover:bg-muted/10 transition-colors">
										<td class="py-3 font-mono font-bold text-slate-200">{cmd.command}</td>
										<td class="py-3 text-right text-amber-300 font-semibold font-mono">{cmd.avg_duration_ms} ms</td>
										<td class="py-3 text-right text-red-400 font-semibold font-mono">{cmd.max_duration_ms} ms</td>
									</tr>
								{/each}
							</tbody>
						</table>
					</div>
				</div>

				<!-- Command Error Rates & Stats -->
				<div class="rounded-xl border border-border bg-slate-900/40 p-6 space-y-4">
					<div class="flex items-center justify-between mb-2">
						<h2 class="text-lg font-bold text-white">Frequência e Falhas</h2>
						<input
							type="text"
							placeholder="Filtrar..."
							class="rounded-md border border-border bg-background px-3 py-1.5 text-xs w-40 outline-none focus:border-primary transition-colors"
							bind:value={commandFilter}
						/>
					</div>
					<div class="space-y-3 max-h-96 overflow-y-auto pr-1">
						{#each filteredErrorRates() as stat}
							<div class="rounded-lg border border-border/80 bg-background/30 p-3.5 space-y-2">
								<div class="flex items-center justify-between">
									<span class="font-mono font-bold text-slate-200">{stat.command}</span>
									{#if stat.rate > 0}
										<span class="text-xs px-2 py-0.5 rounded font-bold font-mono 
											{stat.rate >= 10 ? 'bg-red-950/50 text-red-400' : 'bg-amber-950/50 text-amber-400'}"
										>
											{stat.rate}% falha
										</span>
									{:else}
										<span class="text-xs px-2 py-0.5 rounded font-bold font-mono bg-emerald-950/50 text-emerald-400">
											100% ok
										</span>
									{/if}
								</div>
								<div class="flex justify-between text-xs text-muted-foreground font-mono">
									<span>Total: {stat.total} execuções</span>
									<span>Falhas: {stat.failed}</span>
								</div>
							</div>
						{:else}
							<div class="text-muted-foreground text-center py-4">Nenhum comando encontrado.</div>
						{/each}
					</div>
				</div>
			</div>
		{/if}
	{/if}
</div>

<!-- Detailed Error Trace Modal -->
{#if selectedError}
	<div class="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
		<div class="bg-slate-900 border border-border rounded-xl shadow-2xl max-w-2xl w-full max-h-[85vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-200">
			<!-- Header -->
			<div class="p-6 border-b border-border flex items-center justify-between bg-slate-950/50">
				<div>
					<h3 class="text-lg font-bold text-red-400 flex items-center gap-2">
						<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
							<circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line>
						</svg>
						Trace de Erro: {selectedError.command}
					</h3>
					<p class="text-xs text-muted-foreground mt-1 font-mono">{new Date(selectedError.timestamp).toLocaleString()}</p>
				</div>
				<button 
					class="text-muted-foreground hover:text-foreground p-1.5 rounded-md hover:bg-muted/40 transition-colors" 
					onclick={() => { selectedError = null; aiDiagnosis = null; diagnosing = false; }}
					aria-label="Fechar"
				>
					<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line>
					</svg>
				</button>
			</div>

			<!-- Content -->
			<div class="p-6 overflow-y-auto space-y-5">
				<!-- Context Table -->
				<div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs bg-slate-950/30 p-4 border border-border/50 rounded-lg">
					<div>
						<span class="text-muted-foreground block text-[10px] font-bold uppercase tracking-wider">Comando</span>
						<span class="font-mono mt-1 block font-extrabold text-sm text-slate-200">{selectedError.command}</span>
					</div>
					<div>
						<span class="text-muted-foreground block text-[10px] font-bold uppercase tracking-wider">Argumentos</span>
						<span class="font-mono mt-1 block font-semibold text-slate-300">{selectedError.args.join(' ') || '(nenhum)'}</span>
					</div>
					<div>
						<span class="text-muted-foreground block text-[10px] font-bold uppercase tracking-wider">Código de Saída</span>
						<span class="font-mono mt-1 block font-extrabold text-red-400">{selectedError.exit_code}</span>
					</div>
					<div>
						<span class="text-muted-foreground block text-[10px] font-bold uppercase tracking-wider">Duração de Execução</span>
						<span class="font-mono mt-1 block font-semibold text-slate-300">{selectedError.duration_ms} ms</span>
					</div>
					<div>
						<span class="text-muted-foreground block text-[10px] font-bold uppercase tracking-wider">Usuário OS</span>
						<span class="mt-1 block font-medium text-slate-300">{selectedError.user}</span>
					</div>
					<div>
						<span class="text-muted-foreground block text-[10px] font-bold uppercase tracking-wider">Versão / Idioma</span>
						<span class="mt-1 block font-medium text-slate-300">{selectedError.version} / {selectedError.language}</span>
					</div>
				</div>

				<!-- Error Type -->
				<div class="space-y-1.5">
					<span class="text-muted-foreground block text-[10px] font-bold uppercase tracking-wider">Classe de Exceção (Go Type)</span>
					<code class="text-xs px-2.5 py-1 bg-red-950/30 text-red-300 border border-red-900/50 rounded font-mono block select-all">
						{selectedError.error_type}
					</code>
				</div>

				<!-- Main Stack Trace / Message -->
				<div class="space-y-1.5">
					<div class="flex items-center justify-between">
						<span class="text-muted-foreground block text-[10px] font-bold uppercase tracking-wider">Mensagem de Erro (Stdout/Stderr)</span>
						<button 
							class="text-xs text-primary hover:text-primary/80 flex items-center gap-1 font-semibold transition-colors" 
							onclick={() => navigator.clipboard.writeText(selectedError.error)}
						>
							<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
							</svg>
							Copiar Trace
						</button>
					</div>
					<pre class="text-xs p-4 bg-slate-950 border border-border/80 rounded-lg overflow-x-auto font-mono text-red-200/90 select-all max-h-60 whitespace-pre-wrap leading-relaxed shadow-inner">{selectedError.error}</pre>
				</div>

				<!-- AI Auto-Fix Section -->
				<div class="space-y-2 border border-blue-900/50 bg-blue-950/10 p-4 rounded-xl relative overflow-hidden">
					<div class="absolute top-0 left-0 w-1 h-full bg-blue-500"></div>
					<div class="flex items-center justify-between">
						<h4 class="text-sm font-bold text-blue-400 flex items-center gap-2">
							<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
							</svg>
							IA Diagnóstico & Auto-Remediação
						</h4>
						{#if !aiDiagnosis && !diagnosing}
							<button class="text-xs bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded-md font-semibold transition-colors" onclick={() => diagnoseError(selectedError)}>
								Diagnosticar com IA
							</button>
						{/if}
						{#if diagnosing}
							<span class="text-xs text-blue-300 animate-pulse font-mono flex items-center gap-2">
								<svg class="animate-spin h-3 w-3" viewBox="0 0 24 24" fill="none"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>
								Analisando...
							</span>
						{/if}
					</div>
					{#if aiDiagnosis}
						<div class="mt-3 animate-in fade-in slide-in-from-top-2 duration-300">
							<p class="text-xs text-slate-300 leading-relaxed">{aiDiagnosis.diagnosis}</p>
							{#if aiDiagnosis.suggested_fix}
								<div class="mt-3 bg-slate-950 border border-slate-800 rounded-lg p-3">
									<span class="block text-[10px] font-bold text-muted-foreground uppercase tracking-wider mb-1">Comando Corretivo Sugerido</span>
									<div class="flex items-center justify-between">
										<code class="text-emerald-400 text-xs font-mono font-bold select-all">{aiDiagnosis.suggested_fix}</code>
										<button 
											class="text-xs bg-emerald-600 hover:bg-emerald-500 text-white px-3 py-1.5 rounded-md font-semibold transition-colors flex items-center gap-1 disabled:opacity-50" 
											onclick={() => executeAutoFix(aiDiagnosis!.suggested_fix)}
											disabled={fixing}
										>
											{#if fixing}
												<svg class="animate-spin h-3 w-3" viewBox="0 0 24 24" fill="none"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8H4z"></path></svg>
												Executando...
											{:else}
												<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
												Auto-Fix
											{/if}
										</button>
									</div>
								</div>
							{/if}
						</div>
					{/if}
				</div>
			</div>

			<!-- Footer -->
			<div class="p-6 border-t border-border bg-slate-950/30 flex justify-end">
				<button 
					class="bg-secondary hover:bg-secondary/80 border border-border text-secondary-foreground px-4 py-2 rounded-md text-sm font-semibold transition-all" 
					onclick={() => { selectedError = null; aiDiagnosis = null; diagnosing = false; }}
				>
					Fechar
				</button>
			</div>
		</div>
	</div>
{/if}
