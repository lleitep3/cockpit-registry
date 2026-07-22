<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';

	type Secret = {
		key: string;
		created_at: string;
	};

	let status = $state<{ locked: boolean; raw: string } | null>(null);
	let secrets = $state<Secret[]>([]);
	let masterPassword = $state('');
	let showPassword = $state(false);
	let newKey = $state('');
	let newValue = $state('');
	let revealed = $state<Record<string, string>>({});
	let lastActivity = $state(Date.now());
	let autoLockMs = $state(5 * 60 * 1000); // 5 min

	async function load() {
		try {
			const [statusRes, secretsRes] = await Promise.all([
				api.get<{ locked: boolean; raw: string }>('/api/v1/vault/status').catch(() => ({ locked: true, raw: '' })),
				api.get<{ secrets: Secret[] }>('/api/v1/vault/secrets').catch(() => ({ secrets: [] })),
			]);
			status = statusRes;
			secrets = secretsRes.secrets;
		} catch {
			status = { locked: true, raw: '' };
			secrets = [];
		}
	}

	onMount(() => {
		load();
		const interval = setInterval(() => {
			load();
			if (!status?.locked && Date.now() - lastActivity > autoLockMs) {
				lock();
			}
		}, 30000);
		const activity = () => (lastActivity = Date.now());
		window.addEventListener('click', activity);
		window.addEventListener('keydown', activity);
		return () => {
			clearInterval(interval);
			window.removeEventListener('click', activity);
			window.removeEventListener('keydown', activity);
		};
	});

	async function lock() {
		if (!masterPassword) return;
		const res = await api.post<{ success: boolean; error?: string }>('/api/v1/vault/lock', { master_password: masterPassword });
		if (!res.success) {
			alert(res.error || 'Erro ao bloquear');
		} else {
			status = { locked: true, raw: '' };
			revealed = {};
		}
	}

	async function unlock() {
		if (!masterPassword) return;
		const res = await api.post<{ success: boolean; error?: string }>('/api/v1/vault/unlock', { master_password: masterPassword });
		if (!res.success) {
			alert(res.error || 'Erro ao desbloquear');
		} else {
			status = { locked: false, raw: '' };
			load();
		}
	}

	async function addSecret() {
		if (!newKey || !newValue || !masterPassword) return;
		const res = await api.post<{ success: boolean; error?: string }>('/api/v1/vault/secrets', {
			key: newKey,
			value: newValue,
			master_password: masterPassword,
		});
		if (!res.success) {
			alert(res.error || 'Erro ao adicionar');
		} else {
			newKey = '';
			newValue = '';
			load();
		}
	}

	async function reveal(key: string) {
		if (!masterPassword) return;
		const res = await api.post<{ success: boolean; value?: string; error?: string }>('/api/v1/vault/secrets/reveal', {
			key,
			master_password: masterPassword,
		});
		if (res.success && res.value) {
			revealed = { ...revealed, [key]: res.value };
			setTimeout(() => {
				revealed = { ...revealed, [key]: '' };
			}, 30000);
		} else {
			alert(res.error || 'Erro ao revelar');
		}
	}

	function copy(value: string) {
		navigator.clipboard.writeText(value);
	}

	function mask(value: string) {
		return value ? '•'.repeat(Math.min(value.length, 20)) : '••••••';
	}
</script>

<svelte:head>
	<title>Vault | Cockpit Dashboard</title>
	<meta name="description" content="Gerenciador de credenciais do cockpit" />
</svelte:head>

<div class="space-y-6">
	<div>
		<h1 class="text-3xl font-bold tracking-tight">Vault</h1>
		<p class="text-muted-foreground mt-1">Cofre criptografado de credenciais locais.</p>
	</div>

	<!-- Status card -->
	<div class="rounded-xl border border-border bg-card/50 p-6">
		<div class="flex items-center justify-between">
			<div>
				<div class="text-sm text-muted-foreground">Status</div>
				<div class="text-2xl font-bold {status?.locked ? 'text-red-400' : 'text-emerald-400'}">
					{status?.locked ? 'Bloqueado' : 'Desbloqueado'}
				</div>
			</div>
			{#if status?.locked}
				<button class="bg-emerald-500 text-white px-4 py-2 rounded-md" onclick={unlock}>Desbloquear</button>
			{:else}
				<button class="bg-red-500 text-white px-4 py-2 rounded-md" onclick={lock}>Bloquear</button>
			{/if}
		</div>
	</div>

	<!-- Master password input -->
	<div class="rounded-xl border border-border bg-card/50 p-6 space-y-4">
		<h2 class="font-semibold">Senha mestra</h2>
		<div class="flex gap-2">
			<input
				type={showPassword ? 'text' : 'password'}
				placeholder="Senha mestra do vault"
				class="flex-1 rounded-md border border-border bg-background px-3 py-2 text-sm"
				bind:value={masterPassword}
			/>
			<button
				class="text-sm border border-border px-3 py-2 rounded-md"
				onclick={() => (showPassword = !showPassword)}
			>
				{showPassword ? 'Ocultar' : 'Mostrar'}
			</button>
		</div>
		<div class="text-xs text-muted-foreground">
			Auto-lock após inatividade: {autoLockMs / 60000} minutos
		</div>
	</div>

	<!-- Add secret -->
	<div class="rounded-xl border border-border bg-card/50 p-6 space-y-4">
		<h2 class="font-semibold">Nova credencial</h2>
		<div class="grid gap-3 md:grid-cols-2">
			<input
				type="text"
				placeholder="Nome/chave"
				class="rounded-md border border-border bg-background px-3 py-2 text-sm"
				bind:value={newKey}
			/>
			<input
				type="text"
				placeholder="Valor"
				class="rounded-md border border-border bg-background px-3 py-2 text-sm"
				bind:value={newValue}
			/>
		</div>
		<button class="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm" onclick={addSecret}>
			Adicionar ao vault
		</button>
	</div>

	<!-- Secrets list -->
	<div class="rounded-xl border border-border bg-card/50 p-6">
		<h2 class="font-semibold mb-4">Credenciais ({secrets.length})</h2>
		{#if secrets.length === 0}
			<p class="text-sm text-muted-foreground">Nenhuma credencial armazenada.</p>
		{:else}
			<ul class="space-y-2">
				{#each secrets as secret}
					<li class="flex items-center justify-between rounded-lg border border-border bg-background/50 px-3 py-2">
						<div class="font-medium text-sm">{secret.key}</div>
						<div class="flex items-center gap-2">
							{#if revealed[secret.key]}
								<code class="text-xs font-mono text-emerald-400">{mask(revealed[secret.key])}</code>
								<button class="text-xs border border-border px-2 py-1 rounded" onclick={() => copy(revealed[secret.key])}>Copiar</button>
							{:else}
								<code class="text-xs font-mono text-muted-foreground">••••••</code>
								<button class="text-xs border border-border px-2 py-1 rounded" onclick={() => reveal(secret.key)}>Revelar</button>
							{/if}
						</div>
					</li>
				{/each}
			</ul>
		{/if}
	</div>
</div>
