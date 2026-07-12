<script lang="ts">
	import '../app.css';
	import { ModeWatcher } from 'mode-watcher';
	import { page } from '$app/state';

	let { children } = $props();

	const nav = [
		{ href: '/', label: 'Visão Geral' },
		{ href: '/logs', label: 'Logs & Insights' },
	];

	let sidebarOpen = $state(true);
</script>

<ModeWatcher defaultMode="dark" />

<div class="min-h-screen bg-background text-foreground flex">
	<aside
		class="border-r border-border bg-slate-900 flex flex-col transition-all duration-200"
		class:w-64={sidebarOpen}
		class:w-16={!sidebarOpen}
	>
		<div class="h-14 flex items-center px-4 border-b border-border">
			<span class="font-bold text-lg truncate" class:hidden={!sidebarOpen}>Cockpit</span>
			<button
				class="ml-auto text-muted-foreground hover:text-foreground"
				onclick={() => (sidebarOpen = !sidebarOpen)}
				aria-label={sidebarOpen ? 'Recolher menu' : 'Expandir menu'}
			>
				{sidebarOpen ? '◀' : '▶'}
			</button>
		</div>
		<nav class="flex-1 p-2 space-y-1">
			{#each nav as item}
				<a
					href={item.href}
					class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors"
					class:bg-primary={page.url.pathname === item.href}
					class:text-primary-foreground={page.url.pathname === item.href}
					class:text-muted-foreground={page.url.pathname !== item.href}
					class:hover:bg-muted={page.url.pathname !== item.href}
				>
					<span class="w-5 h-5 flex items-center justify-center">•</span>
					<span class:truncate={sidebarOpen} class:hidden={!sidebarOpen}>{item.label}</span>
				</a>
			{/each}
		</nav>
	</aside>

	<div class="flex-1 flex flex-col min-w-0">
		<header class="h-14 border-b border-border bg-background/95 backdrop-blur flex items-center px-4">
			<span class="font-bold text-lg">Cockpit Dashboard</span>
		</header>
		<main class="flex-1 overflow-y-auto p-6">
			{@render children()}
		</main>
	</div>
</div>
