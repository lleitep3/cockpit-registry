<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';

	let projects = $state<any[]>([]);
	let loading = $state(true);

	onMount(async () => {
		try {
			const res = await api.get<{ projects: any[] }>('/api/v1/projects');
			if (res && res.projects) {
				projects = res.projects;
			}
		} catch (err) {
			console.error('Failed to load projects:', err);
		} finally {
			loading = false;
		}
	});
</script>

<div class="flex flex-col gap-6">
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold tracking-tight">Projetos</h1>
			<p class="text-muted-foreground mt-1">Selecione um projeto para gerenciar.</p>
		</div>
	</div>

	{#if loading}
		<div class="text-center p-12 text-muted-foreground">Carregando projetos...</div>
	{:else if projects.length === 0}
		<div class="p-8 border border-dashed border-border rounded-xl text-center">
			<p class="text-muted-foreground mb-4">Nenhum projeto encontrado.</p>
			<code class="bg-muted px-2 py-1 rounded text-sm text-foreground">cockpit project create meu-projeto</code>
		</div>
	{:else}
		<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
			{#each projects as project}
				<a href="/p/projects/{project.slug || project.id}" class="block group relative overflow-hidden dark:bg-slate-900 bg-card border border-border rounded-xl p-5 hover:border-primary/50 transition-all duration-300 hover:shadow-[0_0_20px_rgba(var(--primary),0.1)]">
					<div class="absolute inset-0 bg-gradient-to-br from-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity"></div>
					<div class="relative z-10">
						<h3 class="font-semibold text-lg mb-2 group-hover:text-primary transition-colors">{project.title}</h3>
						<p class="text-sm text-muted-foreground mb-4 line-clamp-2 min-h-[40px]">{project.description}</p>
						
						{#if project.tags && project.tags.length > 0}
							<div class="flex flex-wrap gap-2 mb-4">
								{#each project.tags as tag}
									<span class="px-2 py-1 bg-primary/20 text-primary text-xs rounded-full">{tag}</span>
								{/each}
							</div>
						{/if}

						<div class="flex gap-4 text-xs text-muted-foreground">
							{#if project.repositories?.length}
								<div class="flex items-center gap-1.5">
									<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/></svg>
									{project.repositories.length} {project.repositories.length === 1 ? 'Repo' : 'Repos'}
								</div>
							{/if}
							{#if project.workspaces?.length}
								<div class="flex items-center gap-1.5">
									<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"/><line x1="8" y1="21" x2="16" y2="21"/><line x1="12" y1="17" x2="12" y2="21"/></svg>
									{project.workspaces.length} {project.workspaces.length === 1 ? 'Workspace' : 'Workspaces'}
								</div>
							{/if}
						</div>
					</div>
				</a>
			{/each}
		</div>
	{/if}
</div>
