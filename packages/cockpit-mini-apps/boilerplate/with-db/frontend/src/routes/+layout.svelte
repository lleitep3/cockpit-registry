<script lang="ts">
	import '../app.css';
	import { ModeWatcher, toggleMode, mode } from 'mode-watcher';
	import { Moon, Sun } from 'lucide-svelte';

	let { children } = $props();
</script>

<ModeWatcher defaultMode="dark" />

<div class="min-h-screen bg-background text-foreground">
	<!-- Navbar -->
	<header class="sticky top-0 z-50 w-full border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
		<div class="container flex h-14 max-w-screen-xl mx-auto items-center px-4">
			<a href="/" class="mr-6 flex items-center space-x-2">
				<span class="font-bold text-lg">{{PROJECT_NAME_TITLE}}</span>
			</a>

			<nav class="flex flex-1 items-center space-x-4 text-sm font-medium">
				<a href="/" class="text-foreground/60 hover:text-foreground transition-colors">Home</a>
				<a href="/items" class="text-foreground/60 hover:text-foreground transition-colors">Items</a>
			</nav>

			<!-- Toggle dark/light -->
			<button
				onclick={toggleMode}
				class="rounded-md p-2 hover:bg-accent hover:text-accent-foreground transition-colors"
				aria-label="Alternar tema"
			>
				{#if $mode === 'dark'}
					<Sun class="h-4 w-4" />
				{:else}
					<Moon class="h-4 w-4" />
				{/if}
			</button>
		</div>
	</header>

	<!-- Conteúdo principal -->
	<main class="container max-w-screen-xl mx-auto px-4 py-8">
		{@render children()}
	</main>
</div>
