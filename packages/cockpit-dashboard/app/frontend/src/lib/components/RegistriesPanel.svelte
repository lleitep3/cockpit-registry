<script lang="ts">
	let { registries }: { registries: { name: string; url?: string }[] | null } = $props();
</script>

<div class="rounded-xl border border-border bg-card/50 backdrop-blur p-6">
	<h2 class="text-lg font-semibold mb-4">Registries</h2>
	{#if registries}
		{#if registries.length === 0}
			<p class="text-muted-foreground">Nenhum registry registrado.</p>
		{:else}
			<ul class="space-y-2">
				{#each registries as registry}
					<li class="rounded-lg border border-border bg-background/50 px-3 py-2">
						<div class="font-medium">{registry.name}</div>
						{#if registry.url}
							<a href={registry.url} target="_blank" rel="noopener noreferrer" class="text-xs text-primary hover:underline break-all">
								{registry.url}
							</a>
						{/if}
					</li>
				{/each}
			</ul>
		{/if}
	{:else}
		<p class="text-muted-foreground">Carregando...</p>
	{/if}
</div>
