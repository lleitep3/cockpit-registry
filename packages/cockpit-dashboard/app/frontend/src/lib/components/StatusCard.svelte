<script lang="ts">
	let { status }: { status: { version: string; environment: string; active: boolean } | null } = $props();
</script>

<div class="rounded-xl border border-border bg-card/50 backdrop-blur p-6">
	<h2 class="text-lg font-semibold mb-4">Status Geral</h2>
	{#if status}
		<div class="grid gap-3">
			<div class="flex items-center justify-between">
				<span class="text-muted-foreground">Versão</span>
				<span class="font-mono font-medium">{status.version}</span>
			</div>
			<div class="flex items-center justify-between">
				<span class="text-muted-foreground">Ambiente</span>
				<span class="capitalize">{status.environment}</span>
			</div>
			<div class="flex items-center justify-between">
				<span class="text-muted-foreground">Status</span>
				<span class="inline-flex items-center gap-1.5">
					<span class="h-2 w-2 rounded-full {status.active ? 'bg-green-500' : 'bg-red-500'}"></span>
					{status.active ? 'Ativo' : 'Inativo'}
				</span>
			</div>
		</div>
	{:else}
		<p class="text-muted-foreground">Carregando...</p>
	{/if}
</div>
