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
		projects_active: number;
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
				backgroundColor: 'rgba(6, 182, 212, 0.2)', // Cyan neon background
				borderColor: 'rgba(6, 182, 212, 1)', // Cyan border
				borderWidth: 2,
				borderRadius: 6,
				hoverBackgroundColor: 'rgba(6, 182, 212, 0.4)',
				hoverBorderColor: 'rgba(34, 211, 238, 1)',
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
			<div class="grid grid-cols-2 lg:grid-cols-4 gap-5">
				
				<!-- Versão -->
				<a href="#" class="relative block overflow-hidden rounded-xl border border-white/5 bg-black/40 p-5 hover:bg-black/60 transition-all duration-300 hover:border-cyan-500/30 hover:shadow-[0_0_20px_rgba(6,182,212,0.1)] backdrop-blur-md group cursor-default">
					<div class="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
					<div class="text-[10px] text-muted-foreground uppercase tracking-[0.2em] font-bold">VERSÃO DO COCKPIT</div>
					<div class="text-4xl font-black mt-3 text-white tracking-tight drop-shadow-md">1.13.0</div>
					<div class="flex items-center gap-1.5 mt-3">
						<div class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></div>
						<div class="text-xs text-emerald-400 font-medium">atualizado</div>
					</div>
				</a>

				<!-- Cofre -->
				<a href="/vault" class="relative block overflow-hidden rounded-xl border border-white/5 bg-black/40 p-5 hover:bg-black/60 transition-all duration-300 hover:border-purple-500/30 hover:shadow-[0_0_20px_rgba(139,92,246,0.1)] backdrop-blur-md group">
					<div class="absolute inset-0 bg-gradient-to-br from-purple-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
					<div class="text-[10px] text-muted-foreground uppercase tracking-[0.2em] font-bold">COFRE</div>
					<div class="text-4xl font-black mt-3 {kpis.vault_locked ? 'text-red-400' : 'text-purple-400'} tracking-tight drop-shadow-md">
						{kpis.vault_locked ? 'Lock' : 'Open'}
					</div>
					<div class="text-xs text-muted-foreground mt-3 font-medium">verificação ok</div>
				</a>

				<!-- Módulos -->
				<a href="/registries" class="relative block overflow-hidden rounded-xl border border-white/5 bg-black/40 p-5 hover:bg-black/60 transition-all duration-300 hover:border-blue-500/30 hover:shadow-[0_0_20px_rgba(59,130,246,0.1)] backdrop-blur-md group">
					<div class="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
					<div class="text-[10px] text-muted-foreground uppercase tracking-[0.2em] font-bold">MÓDULOS</div>
					<div class="text-4xl font-black mt-3 text-white tracking-tight drop-shadow-md">0/6</div>
					<div class="text-xs text-emerald-400 mt-3 font-medium">todos ok</div>
				</a>

				<!-- Pacotes Instalados -->
				<a href="/packages" class="relative block overflow-hidden rounded-xl border border-white/5 bg-black/40 p-5 hover:bg-black/60 transition-all duration-300 hover:border-pink-500/30 hover:shadow-[0_0_20px_rgba(236,72,153,0.1)] backdrop-blur-md group">
					<div class="absolute inset-0 bg-gradient-to-br from-pink-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
					<div class="text-[10px] text-muted-foreground uppercase tracking-[0.2em] font-bold">PACOTES INSTALADOS</div>
					<div class="text-4xl font-black mt-3 text-white tracking-tight drop-shadow-md">{kpis.packages_total}</div>
					<div class="text-xs text-emerald-400 mt-3 font-medium">todos ok</div>
				</a>

				<!-- Docs no KB -->
				<a href="/kb" class="relative block overflow-hidden rounded-xl border border-white/5 bg-black/40 p-5 hover:bg-black/60 transition-all duration-300 hover:border-amber-500/30 hover:shadow-[0_0_20px_rgba(245,158,11,0.1)] backdrop-blur-md group">
					<div class="absolute inset-0 bg-gradient-to-br from-amber-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
					<div class="text-[10px] text-muted-foreground uppercase tracking-[0.2em] font-bold">DOCS NO KB</div>
					<div class="text-4xl font-black mt-3 text-white tracking-tight drop-shadow-md">{kpis.kb_total}</div>
					<div class="text-xs text-muted-foreground mt-3 font-medium">{kpis.kb_connections} referências diretas</div>
				</a>

				<!-- Mini-apps Rodando -->
				<a href="/mini-apps" class="relative block overflow-hidden rounded-xl border border-white/5 bg-black/40 p-5 hover:bg-black/60 transition-all duration-300 hover:border-green-500/30 hover:shadow-[0_0_20px_rgba(16,185,129,0.1)] backdrop-blur-md group">
					<div class="absolute inset-0 bg-gradient-to-br from-green-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
					<div class="text-[10px] text-muted-foreground uppercase tracking-[0.2em] font-bold">MINI-APPS ATIVOS</div>
					<div class="text-4xl font-black mt-3 text-white tracking-tight drop-shadow-md">{kpis.mini_apps_active}</div>
					<div class="text-xs text-emerald-400 mt-3 font-medium">de {kpis.mini_apps_total} instalados</div>
				</a>

				<!-- Projetos Ativos -->
				<a href="/p/projects" class="relative block overflow-hidden rounded-xl border border-white/5 bg-black/40 p-5 hover:bg-black/60 transition-all duration-300 hover:border-indigo-500/30 hover:shadow-[0_0_20px_rgba(99,102,241,0.1)] backdrop-blur-md group">
					<div class="absolute inset-0 bg-gradient-to-br from-indigo-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
					<div class="text-[10px] text-muted-foreground uppercase tracking-[0.2em] font-bold">PROJETOS ATIVOS</div>
					<div class="text-4xl font-black mt-3 text-white tracking-tight drop-shadow-md">{kpis.projects_active || 0}</div>
					<div class="text-xs text-muted-foreground mt-3 font-medium">gerenciados pelo pacote</div>
				</a>

				<!-- Séries de Artigos -->
				<a href="/articles" class="relative block overflow-hidden rounded-xl border border-white/5 bg-black/40 p-5 hover:bg-black/60 transition-all duration-300 hover:border-rose-500/30 hover:shadow-[0_0_20px_rgba(244,63,94,0.1)] backdrop-blur-md group">
					<div class="absolute inset-0 bg-gradient-to-br from-rose-500/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
					<div class="text-[10px] text-muted-foreground uppercase tracking-[0.2em] font-bold">SÉRIES DE ARTIGOS</div>
					<div class="text-4xl font-black mt-3 text-white tracking-tight drop-shadow-md">5</div>
					<div class="text-xs text-emerald-400 mt-3 font-medium">5 com build gerado</div>
				</a>

			</div>

			<!-- Analytics Area -->
			<div class="relative rounded-2xl border border-white/5 bg-black/40 p-8 backdrop-blur-md mt-10 shadow-2xl">
				<div class="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-[1px] bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent"></div>
				<h2 class="text-xl font-bold text-white mb-8 tracking-tight flex items-center gap-3">
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-cyan-400"><path d="M3 3v18h18"></path><path d="M18.7 8l-5.1 5.2-2.8-2.7L7 14.3"></path></svg>
					Comandos Mais Usados (7 dias)
				</h2>
				<div class="h-80 w-full relative">
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
