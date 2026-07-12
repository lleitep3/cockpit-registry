<script lang="ts">
	import '../app.css';
	import { ModeWatcher } from 'mode-watcher';

	let { children } = $props();
</script>

<ModeWatcher defaultMode="dark" />

<div class="min-h-screen bg-background text-foreground">
	<header class="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
		<div class="container flex h-14 max-w-screen-xl mx-auto items-center px-4">
			<a href="/" class="mr-6 flex items-center space-x-2">
				<span class="font-bold text-lg">Cockpit Dashboard</span>
			</a>
		</div>
	</header>

	<main class="container max-w-screen-xl mx-auto px-4 py-8">
		{@render children()}
	</main>
</div>
