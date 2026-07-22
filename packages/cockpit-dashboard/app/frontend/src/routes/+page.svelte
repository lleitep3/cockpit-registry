<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import { Bar } from 'svelte-chartjs';
	import {
		Chart as ChartJS,
		Title,
		Tooltip,
		Legend,
		BarElement,
		CategoryScale,
		LinearScale,
	} from 'chart.js';

	ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale);

	type TopCommand = {
		command: string;
		count: number;
		avg_duration_ms: number;
	};

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
		top_commands: TopCommand[];
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

	let chartData = $derived({
		labels: kpis?.top_commands.map((c) => c.command) || [],
		datasets: [
			{
				label: 'Uso nos últimos 7 dias',
				data: kpis?.top_commands.map((c) => c.count) || [],
				backgroundColor: 'rgba(239, 68, 68, 0.7)', // Neon orange/red matching UI
				borderColor: 'rgba(239, 68, 68, 1)',
				borderWidth: 1,
				borderRadius: 4,
			}
		]
	});
	
	const chartOptions = {
		responsive: true,
		maintainAspectRatio: false,
		scales: {
			y: {
				beginAtZero: true,
				grid: {
					color: 'rgba(255, 255, 255, 0.05)',
				},
				ticks: { color: 'rgba(255, 255, 255, 0.6)' }
			},
			x: {
				grid: {
					display: false
				},
				ticks: { color: 'rgba(255, 255, 255, 0.6)' }
			}
		},
		plugins: {
			legend: {
				display: false
			},
			tooltip: {
				backgroundColor: 'rgba(0, 0, 0, 0.8)',
				titleColor: '#fff',
				bodyColor: '#fff',
				borderColor: 'rgba(255, 255, 255, 0.1)',
				borderWidth: 1
			}
		}
	};
</script>

<svelte:head>
	<title>Overview | Cockpit Dashboard</title>
</svelte:head>

<div class="space-y-8">
	<!-- KPI Grid -->
	{#if loading && !kpis && !doctor}
		<p class="text-muted-foreground">Carregando...</p>
	{:else if error}
		<div class="rounded-lg border border-red-800 bg-red-950/30 p-4 text-red-200">
			{error}
		</div>
	{:else}
		{#if kpis}
			<div class="grid grid-cols-2 lg:grid-cols-4 gap-4">
				
				<!-- Versão -->
				<div class="rounded-xl border border-border/50 bg-card/40 p-4 hover:bg-card/60 transition-colors backdrop-blur-sm">
					<div class="text-xs text-muted-foreground uppercase tracking-wider font-semibold">VERSÃO DO COCKPIT</div>
					<div class="text-3xl font-bold mt-2 text-gray-100">1.13.0</div>
					<div class="text-xs text-emerald-400 mt-2 font-medium">atualizado</div>
				</div>

				<!-- Cofre -->
				<div class="rounded-xl border border-border/50 bg-card/40 p-4 hover:bg-card/60 transition-colors backdrop-blur-sm">
					<div class="text-xs text-muted-foreground uppercase tracking-wider font-semibold">COFRE</div>
					<div class="text-3xl font-bold mt-2 {kpis.vault_locked ? 'text-red-400' : 'text-emerald-400'}">
						{kpis.vault_locked ? 'Bloqueado' : 'Destravado'}
					</div>
					<div class="text-xs text-muted-foreground mt-2 font-medium">verificação ok</div>
				</div>

				<!-- Módulos -->
				<div class="rounded-xl border border-border/50 bg-card/40 p-4 hover:bg-card/60 transition-colors backdrop-blur-sm">
					<div class="text-xs text-muted-foreground uppercase tracking-wider font-semibold">MÓDULOS</div>
					<div class="text-3xl font-bold mt-2 text-gray-100">0/6</div>
					<div class="text-xs text-emerald-400 mt-2 font-medium">todos ok</div>
				</div>

				<!-- Pacotes Instalados -->
				<div class="rounded-xl border border-border/50 bg-card/40 p-4 hover:bg-card/60 transition-colors backdrop-blur-sm">
					<div class="text-xs text-muted-foreground uppercase tracking-wider font-semibold">PACOTES INSTALADOS</div>
					<div class="text-3xl font-bold mt-2 text-gray-100">{kpis.packages_total}</div>
					<div class="text-xs text-emerald-400 mt-2 font-medium">todos ok</div>
				</div>

				<!-- Docs no KB -->
				<div class="rounded-xl border border-border/50 bg-card/40 p-4 hover:bg-card/60 transition-colors backdrop-blur-sm">
					<div class="text-xs text-muted-foreground uppercase tracking-wider font-semibold">DOCS NO KB</div>
					<div class="text-3xl font-bold mt-2 text-gray-100">{kpis.kb_total}</div>
					<div class="text-xs text-muted-foreground mt-2 font-medium">{kpis.kb_connections} referências diretas</div>
				</div>

				<!-- Mini-apps Rodando -->
				<div class="rounded-xl border border-border/50 bg-card/40 p-4 hover:bg-card/60 transition-colors backdrop-blur-sm">
					<div class="text-xs text-muted-foreground uppercase tracking-wider font-semibold">MINI-APPS RODANDO</div>
					<div class="text-3xl font-bold mt-2 text-gray-100">{kpis.mini_apps_active}</div>
					<div class="text-xs text-emerald-400 mt-2 font-medium">de {kpis.mini_apps_total} instalados</div>
				</div>

				<!-- Projetos Ativos -->
				<div class="rounded-xl border border-border/50 bg-card/40 p-4 hover:bg-card/60 transition-colors backdrop-blur-sm">
					<div class="text-xs text-muted-foreground uppercase tracking-wider font-semibold">PROJETOS ATIVOS</div>
					<div class="text-3xl font-bold mt-2 text-gray-100">4</div>
					<div class="text-xs text-muted-foreground mt-2 font-medium">10 workspaces cruzados</div>
				</div>

				<!-- Séries de Artigos -->
				<div class="rounded-xl border border-border/50 bg-card/40 p-4 hover:bg-card/60 transition-colors backdrop-blur-sm">
					<div class="text-xs text-muted-foreground uppercase tracking-wider font-semibold">SÉRIES DE ARTIGOS</div>
					<div class="text-3xl font-bold mt-2 text-gray-100">5</div>
					<div class="text-xs text-emerald-400 mt-2 font-medium">5 com build gerado</div>
				</div>

			</div>

			<!-- Analytics Area -->
			<div class="rounded-xl border border-border/50 bg-card/40 p-6 backdrop-blur-sm mt-8">
				<h2 class="text-lg font-semibold text-gray-200 mb-6 tracking-tight">Comandos mais usados (7 dias)</h2>
				<div class="h-64 w-full">
					{#if kpis.top_commands && kpis.top_commands.length > 0}
						<Bar data={chartData} options={chartOptions} />
					{:else}
						<div class="flex items-center justify-center h-full text-muted-foreground">
							Nenhum dado de execução encontrado
						</div>
					{/if}
				</div>
			</div>
		{/if}
	{/if}
</div>
