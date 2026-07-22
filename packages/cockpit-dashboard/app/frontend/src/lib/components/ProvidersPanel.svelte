<script lang="ts">
	let { providers }: { providers: { name: string; active?: boolean }[] | null } = $props();
</script>

<div class="rounded-xl border border-border bg-card/50 backdrop-blur p-6">
	<h2 class="text-lg font-semibold mb-4">Providers</h2>
	{#if providers}
		{#if providers.length === 0}
			<p class="text-muted-foreground">Nenhum provider configurado.</p>
		{:else}
			<ul class="space-y-2">
				{#each providers as provider}
					<li class="flex items-center justify-between rounded-lg border border-border bg-background/50 px-3 py-2">
						<span class="font-medium">{provider.name}</span>
						<span class="inline-flex items-center gap-1.5 text-xs">
							<span class="h-2 w-2 rounded-full {provider.active !== false ? 'bg-green-500' : 'bg-yellow-500'}"></span>
							{provider.active !== false ? 'Ativo' : 'Inativo'}
						</span>
					</li>
				{/each}
			</ul>
		{/if}
	{:else}
		<p class="text-muted-foreground">Carregando...</p>
	{/if}
</div>
