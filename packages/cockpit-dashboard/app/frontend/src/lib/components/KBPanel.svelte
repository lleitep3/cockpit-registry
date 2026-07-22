<script lang="ts">
	let { documents }: { documents: { name: string; category: string; path: string }[] | null } = $props();
</script>

<div class="rounded-xl border border-border bg-card/50 backdrop-blur p-6">
	<h2 class="text-lg font-semibold mb-4">Knowledge Base</h2>
	{#if documents}
		{#if documents.length === 0}
			<p class="text-muted-foreground">Nenhum documento na KB.</p>
		{:else}
			<ul class="space-y-2">
				{#each documents as doc}
					<li class="rounded-lg border border-border bg-background/50 px-3 py-2">
						<div class="font-medium">{doc.name}</div>
						<div class="text-xs text-muted-foreground">{doc.category}</div>
					</li>
				{/each}
			</ul>
		{/if}
	{:else}
		<p class="text-muted-foreground">Carregando...</p>
	{/if}
</div>
