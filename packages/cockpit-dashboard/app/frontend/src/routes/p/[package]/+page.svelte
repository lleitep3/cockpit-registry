<script lang="ts">
	import { page } from '$app/state';
</script>

<div class="flex flex-col gap-6">
	<div>
		<h1 class="text-3xl font-bold tracking-tight capitalize">{page.params.package}</h1>
		<p class="text-muted-foreground mt-2">
			Este pacote não possui uma interface customizada registrada no Dashboard.
		</p>
	</div>

	<div class="p-8 border border-dashed border-border rounded-xl flex flex-col items-center justify-center text-center">
		<svg class="w-16 h-16 text-muted-foreground mb-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1" stroke-linecap="round" stroke-linejoin="round">
			<rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
			<line x1="3" y1="9" x2="21" y2="9"/>
			<line x1="9" y1="21" x2="9" y2="9"/>
		</svg>
		<h2 class="text-xl font-semibold mb-2">Interface não disponível</h2>
		<p class="text-muted-foreground max-w-md">
			O pacote <strong>{page.params.package}</strong> está instalado no seu CLI, mas não expõe componentes visuais para o Dashboard.
		</p>
	</div>
</div>
