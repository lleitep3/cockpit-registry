<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';

	type DoctorCheck = {
		check_name: string;
		status: 'ok' | 'warning' | 'error';
		message: string;
		fixable: boolean;
		fix_command: string;
	};

	type DoctorResult = {
		passed: boolean;
		checks: DoctorCheck[];
		duration_ms?: number;
		error?: string;
	};

	type KpiResult = {
		vault_locked: boolean;
		packages_total: number;
		packages_upgradable: number;
		mini_apps_total: number;
		mini_apps_active: number;
		kb_total: number;
		kb_connections: number;
		executions_total: number;
		executions_success_rate: number;
		executions_failed: number;
	};

	let doctor = $state<DoctorResult | null>(null);
	let kpis = $state<KpiResult | null>(null);
	let loading = $state(true);
	let error = $state<string | null>(null);

	async function load() {
		try {
			loading = true;
			error = null;
			const [doctorRes, kpiRes] = await Promise.all([
				api.get<DoctorResult>('/api/v1/overview/doctor').catch(() => null),
				api.get<KpiResult>('/api/v1/overview/kpi').catch(() => null),
			]);
			doctor = doctorRes;
			kpis = kpiRes;
		} catch (e) {
			error = e instanceof Error ? e.message : 'Erro ao carregar overview';
		} finally {
			loading = false;
		}
	}

	onMount(() => {
		load();
		const interval = setInterval(load, 30000);
		return () => clearInterval(interval);
	});

	function statusIcon(status: string) {
		if (status === 'ok') return '✓';
		if (status === 'warning') return '!';
		return '✗';
	}

	function statusClass(status: string) {
		if (status === 'ok') return 'text-emerald-400';
		if (status === 'warning') return 'text-amber-400';
		return 'text-red-400';
	}
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

	{#if loading && !kpis && !doctor}
		<p class="text-muted-foreground">Carregando...</p>
	{:else if error}
		<div class="rounded-lg border border-red-800 bg-red-950/30 p-4 text-red-200">
			{error}
		</div>
	{:else}
		<!-- KPIs -->
		{#if kpis}
			<div class="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
				<a href="/vault" class="rounded-xl border border-border bg-card/50 p-6 hover:bg-card/80 transition-colors">
					<div class="text-sm text-muted-foreground">Vault</div>
					<div class="text-2xl font-bold mt-1 {kpis.vault_locked ? 'text-red-400' : 'text-emerald-400'}">
						{kpis.vault_locked ? 'Bloqueado' : 'Desbloqueado'}
					</div>
				</a>
				<a href="/packages" class="rounded-xl border border-border bg-card/50 p-6 hover:bg-card/80 transition-colors">
					<div class="text-sm text-muted-foreground">Pacotes</div>
					<div class="text-2xl font-bold mt-1">{kpis.packages_total}</div>
					{#if kpis.packages_upgradable > 0}
						<div class="text-xs text-amber-400 mt-1">{kpis.packages_upgradable} atualizações</div>
					{/if}
				</a>
				<a href="/mini-apps" class="rounded-xl border border-border bg-card/50 p-6 hover:bg-card/80 transition-colors">
					<div class="text-sm text-muted-foreground">Mini-Apps</div>
					<div class="text-2xl font-bold mt-1">{kpis.mini_apps_active}/{kpis.mini_apps_total}</div>
					<div class="text-xs text-muted-foreground mt-1">ativos</div>
				</a>
				<a href="/kb" class="rounded-xl border border-border bg-card/50 p-6 hover:bg-card/80 transition-colors">
					<div class="text-sm text-muted-foreground">Knowledge Base</div>
					<div class="text-2xl font-bold mt-1">{kpis.kb_total}</div>
					<div class="text-xs text-muted-foreground mt-1">{kpis.kb_connections} conexões</div>
				</a>
				<a href="/logs" class="rounded-xl border border-border bg-card/50 p-6 hover:bg-card/80 transition-colors">
					<div class="text-sm text-muted-foreground">Execuções</div>
					<div class="text-2xl font-bold mt-1">{kpis.executions_total}</div>
					<div class="text-xs {kpis.executions_failed > 0 ? 'text-red-400' : 'text-emerald-400'} mt-1">
						{kpis.executions_success_rate}% sucesso ({kpis.executions_failed} erros)
					</div>
				</a>
			</div>
		{/if}

		<!-- Doctor -->
		{#if doctor}
			<div class="rounded-xl border border-border bg-card/50 p-6">
				<div class="flex items-center justify-between mb-4">
					<h2 class="text-lg font-semibold">Diagnósticos</h2>
					{#if doctor.passed}
						<span class="text-emerald-400 text-sm font-medium">Tudo ok</span>
					{:else}
						<span class="text-red-400 text-sm font-medium">Falhas detectadas</span>
					{/if}
				</div>
				{#if doctor.error}
					<div class="text-red-400 text-sm mb-4">{doctor.error}</div>
				{/if}
				<ul class="space-y-2">
					{#each doctor.checks as check}
						<li class="flex items-center gap-3 rounded-lg border border-border bg-background/50 px-3 py-2">
							<span class="text-lg {statusClass(check.status)}">{statusIcon(check.status)}</span>
							<div class="flex-1">
								<div class="font-medium">{check.check_name}</div>
								<div class="text-xs text-muted-foreground">{check.message}</div>
							</div>
							{#if check.fixable}
								<button class="text-xs bg-primary text-primary-foreground px-2 py-1 rounded">Corrigir</button>
							{/if}
						</li>
					{/each}
				</ul>
			</div>
		{/if}
	{/if}
</div>
