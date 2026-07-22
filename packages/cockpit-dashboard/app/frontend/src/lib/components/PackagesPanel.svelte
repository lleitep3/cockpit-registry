<script lang="ts">
	let { packages }: { packages: { name: string; version?: string; description?: string }[] | null } = $props();
</script>

<div class="rounded-xl border border-border bg-card/50 backdrop-blur p-6">
	<h2 class="text-lg font-semibold mb-4">Pacotes Instalados</h2>
	{#if packages}
		{#if packages.length === 0}
			<p class="text-muted-foreground">Nenhum pacote instalado.</p>
		{:else}
			<ul class="space-y-2">
				{#each packages as pkg}
					<li class="rounded-lg border border-border bg-background/50 px-3 py-2">
						<div class="flex items-center justify-between">
							<span class="font-medium">{pkg.name}</span>
							{#if pkg.version}
								<span class="font-mono text-xs text-muted-foreground">v{pkg.version}</span>
							{/if}
						</div>
						{#if pkg.description}
							<p class="text-xs text-muted-foreground mt-1">{pkg.description}</p>
						{/if}
					</li>
				{/each}
			</ul>
		{/if}
	{:else}
		<p class="text-muted-foreground">Carregando...</p>
	{/if}
</div>
