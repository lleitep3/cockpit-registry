<script lang="ts">
	import '../app.css';
	import { ModeWatcher, toggleMode } from 'mode-watcher';
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { onMount } from 'svelte';
	import { api } from '$lib/api';

	let { children } = $props();

	const baseNav = [
		{ href: '/', label: 'Overview', icon: 'home' },
		{ href: '/packages', label: 'Gerenciar Pacotes', icon: 'package' },
		{ href: '/registries', label: 'Registries', icon: 'server' },
		{ href: '/vault', label: 'Vault', icon: 'lock' },
		{ href: '/kb', label: 'Knowledge Base', icon: 'book' },
		{ href: '/mini-apps', label: 'Mini-Apps', icon: 'cpu' },
		{ href: '/logs', label: 'Logs & Insights', icon: 'chart' },
	];

	let packageNav = $state<{ href: string; label: string; icon: string }[]>([]);
	let nav = $derived([...baseNav, ...packageNav]);

	let sidebarOpen = $state(true);
	let mobileOpen = $state(false);
	let commandOpen = $state(false);
	let commandQuery = $state('');

	function iconSvg(name: string) {
		const map: Record<string, string> = {
			home: '<path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/>',
			package: '<line x1="16.5" y1="9.4" x2="7.5" y2="4.21"/><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/>',
			lock: '<rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/>',
			book: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>',
			cpu: '<rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="14" x2="23" y2="14"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="14" x2="4" y2="14"/>',
			chart: '<line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>',
			server: '<rect x="2" y="2" width="20" height="8" rx="2" ry="2"/><rect x="2" y="14" width="20" height="8" rx="2" ry="2"/><line x1="6" y1="6" x2="6.01" y2="6"/><line x1="6" y1="18" x2="6.01" y2="18"/>',
			layout: '<rect x="3" y="3" width="18" height="18" rx="2" ry="2"/><line x1="3" y1="9" x2="21" y2="9"/><line x1="9" y1="21" x2="9" y2="9"/>',
			// Default box icon for dynamic packages
			box: '<path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>',
		};
		return map[name] || map['box'];
	}

	function openCommand() {
		commandOpen = true;
		commandQuery = '';
	}

	function closeCommand() {
		commandOpen = false;
	}

	function navigateTo(href: string) {
		commandOpen = false;
		mobileOpen = false;
		goto(href);
	}

	function filteredNav() {
		const q = commandQuery.toLowerCase();
		if (!q) return nav;
		return nav.filter((item) => item.label.toLowerCase().includes(q));
	}

	function onKeydown(e: KeyboardEvent) {
		if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
			e.preventDefault();
			commandOpen = !commandOpen;
		}
		if (e.key === 'Escape') {
			commandOpen = false;
			mobileOpen = false;
		}
	}

	onMount(async () => {
		window.addEventListener('keydown', onKeydown);
		try {
			const res = await api.get<{ packages: { name: string; description?: string; has_dashboard?: boolean; icon?: string }[] }>('/api/v1/packages');
			if (res && res.packages) {
				const dashboardPkgs = res.packages.filter(p => p.has_dashboard);
				packageNav = dashboardPkgs.map((pkg) => ({
					href: `/p/${pkg.name}`,
					label: pkg.name.charAt(0).toUpperCase() + pkg.name.slice(1),
					icon: pkg.icon || 'box'
				}));
			}
		} catch (err) {
			console.error('Failed to fetch packages:', err);
		}
		return () => window.removeEventListener('keydown', onKeydown);
	});

	const breadcrumbs = $derived(() => {
		const current = nav.find((item) => item.href === page.url.pathname);
		return current ? [current.label] : ['Dashboard'];
	});
</script>

<ModeWatcher defaultMode="dark" />

<div class="min-h-screen bg-background text-foreground flex">
	<!-- Sidebar desktop -->
	<aside
		class="hidden md:flex border-r border-border dark:bg-slate-900 bg-card flex-col transition-all duration-200"
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
				<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					{#if sidebarOpen}
						<polyline points="15 18 9 12 15 6" />
					{:else}
						<polyline points="9 18 15 12 9 6" />
					{/if}
				</svg>
			</button>
		</div>
		<nav class="flex-1 p-2 space-y-1">
			{#each baseNav as item}
				<a
					href={item.href}
					class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors"
					class:bg-primary={page.url.pathname === item.href}
					class:text-primary-foreground={page.url.pathname === item.href}
					class:text-muted-foreground={page.url.pathname !== item.href}
					class:hover:bg-muted={page.url.pathname !== item.href}
				>
					<svg class="w-5 h-5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
						{@html iconSvg(item.icon)}
					</svg>
					<span class:truncate={sidebarOpen} class:hidden={!sidebarOpen}>{item.label}</span>
				</a>
			{/each}

			{#if packageNav.length > 0}
				<div class="pt-4 pb-1 px-3 flex items-center">
					<span class="text-xs font-semibold text-muted-foreground uppercase tracking-wider" class:hidden={!sidebarOpen}>Pacotes</span>
					{#if !sidebarOpen}
						<div class="h-px bg-border w-full mt-2"></div>
					{/if}
				</div>
				{#each packageNav as item}
					<a
						href={item.href}
						class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors"
						class:bg-primary={page.url.pathname === item.href}
						class:text-primary-foreground={page.url.pathname === item.href}
						class:text-muted-foreground={page.url.pathname !== item.href}
						class:hover:bg-muted={page.url.pathname !== item.href}
					>
						<svg class="w-5 h-5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							{@html iconSvg(item.icon)}
						</svg>
						<span class:truncate={sidebarOpen} class:hidden={!sidebarOpen}>{item.label}</span>
					</a>
				{/each}
			{/if}
		</nav>
		<div class="p-4 border-t border-border mt-auto text-xs text-muted-foreground whitespace-nowrap overflow-hidden text-ellipsis flex flex-col gap-1">
			<span class:hidden={!sidebarOpen}>100% local - 127.0.0.1</span>
			<span class:hidden={!sidebarOpen} class="font-medium text-[10px]">V1.13.0</span>
		</div>
	</aside>

	<!-- Mobile drawer overlay -->
	{#if mobileOpen}
		<div class="fixed inset-0 z-40 bg-black/50 md:hidden" onclick={() => (mobileOpen = false)} role="presentation"></div>
		<aside class="fixed inset-y-0 left-0 z-50 w-64 dark:bg-slate-900 bg-card border-r border-border flex flex-col md:hidden">
			<div class="h-14 flex items-center px-4 border-b border-border justify-between">
				<span class="font-bold text-lg">Cockpit</span>
				<button class="text-muted-foreground hover:text-foreground" onclick={() => (mobileOpen = false)} aria-label="Fechar menu">
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
				</button>
			</div>
			<nav class="flex-1 p-2 space-y-1">
				{#each baseNav as item}
					<a
						href={item.href}
						class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors"
						class:bg-primary={page.url.pathname === item.href}
						class:text-primary-foreground={page.url.pathname === item.href}
						class:text-muted-foreground={page.url.pathname !== item.href}
						class:hover:bg-muted={page.url.pathname !== item.href}
						onclick={() => (mobileOpen = false)}
					>
						<svg class="w-5 h-5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
							{@html iconSvg(item.icon)}
						</svg>
						<span>{item.label}</span>
					</a>
				{/each}

				{#if packageNav.length > 0}
					<div class="pt-4 pb-1 px-3">
						<span class="text-xs font-semibold text-muted-foreground uppercase tracking-wider">Pacotes</span>
					</div>
					{#each packageNav as item}
						<a
							href={item.href}
							class="flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors"
							class:bg-primary={page.url.pathname === item.href}
							class:text-primary-foreground={page.url.pathname === item.href}
							class:text-muted-foreground={page.url.pathname !== item.href}
							class:hover:bg-muted={page.url.pathname !== item.href}
							onclick={() => (mobileOpen = false)}
						>
							<svg class="w-5 h-5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								{@html iconSvg(item.icon)}
							</svg>
							<span>{item.label}</span>
						</a>
					{/each}
				{/if}
			</nav>
			<div class="p-4 border-t border-border mt-auto text-xs text-muted-foreground whitespace-nowrap overflow-hidden text-ellipsis flex flex-col gap-1">
				<span>100% local - 127.0.0.1</span>
				<span class="font-medium text-[10px]">V1.13.0</span>
			</div>
		</aside>
	{/if}

	<div class="flex-1 flex flex-col min-w-0">
		<header class="h-14 border-b border-border bg-primary text-primary-foreground dark:bg-background/95 dark:text-foreground backdrop-blur flex items-center px-4 gap-4">
			<button class="md:hidden opacity-80 hover:opacity-100" onclick={() => (mobileOpen = true)} aria-label="Abrir menu">
				<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
			</button>
			<div class="flex-1 text-sm text-muted-foreground truncate">
				{#each breadcrumbs() as crumb, i}
					{#if i > 0}<span class="mx-2">/</span>{/if}
					<span>{crumb}</span>
				{/each}
			</div>
			<button
				class="hidden md:flex items-center gap-2 rounded-md border dark:border-border border-primary-foreground/20 dark:bg-background bg-primary-foreground/10 px-3 py-1.5 text-sm opacity-80 hover:opacity-100"
				onclick={openCommand}
			>
				<span>Buscar...</span>
				<kbd class="rounded dark:bg-muted bg-primary-foreground/20 px-1.5 text-xs">Ctrl K</kbd>
			</button>
			<button class="opacity-80 hover:opacity-100" onclick={toggleMode} aria-label="Toggle Theme">
				<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
				</svg>
			</button>
		</header>
		<main class="flex-1 overflow-y-auto p-6">
			{@render children()}
		</main>
	</div>
</div>

<!-- Command Palette -->
{#if commandOpen}
	<div class="fixed inset-0 z-50 flex items-start justify-center pt-20 bg-black/50" onclick={closeCommand} role="presentation">
		<div class="w-full max-w-lg rounded-xl border border-border dark:bg-slate-900 bg-card shadow-2xl overflow-hidden" onclick={(e) => e.stopPropagation()} role="dialog" aria-label="Command palette">
			<div class="border-b border-border p-3 flex items-center gap-2">
				<svg class="w-5 h-5 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
				<input
					type="text"
					class="flex-1 bg-transparent text-sm outline-none placeholder:text-muted-foreground"
					placeholder="Navegar para..."
					bind:value={commandQuery}
					autofocus
				/>
				<kbd class="rounded bg-muted px-1.5 text-xs text-muted-foreground">ESC</kbd>
			</div>
			<div class="max-h-80 overflow-y-auto p-2">
				{#if filteredNav().length === 0}
					<div class="p-4 text-sm text-muted-foreground text-center">Nenhuma página encontrada.</div>
				{:else}
					{#each filteredNav() as item}
						<button
							class="w-full flex items-center gap-3 rounded-lg px-3 py-2 text-sm text-left transition-colors hover:bg-muted"
							onclick={() => navigateTo(item.href)}
						>
							<svg class="w-4 h-4 text-muted-foreground" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
								{@html iconSvg(item.icon)}
							</svg>
							<span>{item.label}</span>
						</button>
					{/each}
				{/if}
			</div>
		</div>
	</div>
{/if}
