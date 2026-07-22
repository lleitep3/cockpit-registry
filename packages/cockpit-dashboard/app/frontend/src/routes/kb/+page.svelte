<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import * as d3 from 'd3';

	type Document = {
		name: string;
		path: string;
	};

	type Node = {
		id: string;
		label: string;
		path: string;
		orphan: boolean;
	};

	type Edge = {
		source: string | Node;
		target: string | Node;
	};

	type Graph = {
		nodes: Node[];
		edges: Edge[];
	};

	let query = $state('');
	let documents = $state<Document[]>([]);
	let graph = $state<Graph | null>(null);
	let selected = $state<Document | null>(null);
	let preview = $state<string>('');
	let svgRef: SVGSVGElement | null = null;
	let width = 0;
	let height = 0;

	async function load() {
		try {
			const [docsRes, graphRes] = await Promise.all([
				api.get<{ documents: Document[] }>('/api/v1/kb'),
				api.get<Graph>('/api/v1/kb/graph'),
			]);
			documents = docsRes.documents;
			graph = graphRes;
		} catch {
			documents = [];
			graph = { nodes: [], edges: [] };
		}
	}

	onMount(() => {
		load();
	});

	async function search() {
		if (!query.trim()) {
			load();
			return;
		}
		try {
			const res = await api.get<{ results: Document[] }>(`/api/v1/kb/search?query=${encodeURIComponent(query)}`);
			// keep graph but highlight search results
		} catch {
			// ignore
		}
	}

	async function showPreview(doc: Document) {
		selected = doc;
		try {
			const res = await fetch(doc.path);
			preview = await res.text();
		} catch {
			preview = 'Não foi possível carregar o preview.';
		}
	}

	function drawGraph() {
		if (!svgRef || !graph) return;
		width = svgRef.clientWidth || 800;
		height = svgRef.clientHeight || 400;
		const svg = d3.select(svgRef);
		svg.selectAll('*').remove();

		const nodes = graph.nodes.map((n) => ({ ...n }));
		const edges = graph.edges.map((e) => ({ source: e.source, target: e.target }));

		const simulation = d3
			.forceSimulation(nodes as any)
			.force(
				'link',
				d3
					.forceLink(edges as any)
					.id((d: any) => d.id)
					.distance(80)
			)
			.force('charge', d3.forceManyBody().strength(-200))
			.force('center', d3.forceCenter(width / 2, height / 2));

		const link = svg
			.append('g')
			.selectAll('line')
			.data(edges)
			.enter()
			.append('line')
			.attr('stroke', 'currentColor')
			.attr('stroke-opacity', 0.3)
			.attr('stroke-width', 1);

		const node = svg
			.append('g')
			.selectAll('g')
			.data(nodes)
			.enter()
			.append('g')
			.attr('cursor', 'pointer')
			.on('click', (_event, d) => {
				const doc = documents.find((doc) => doc.name.toLowerCase().replace(/\s+/g, '-') === d.id);
				if (doc) showPreview(doc);
			})
			.call(d3.drag().on('start', dragstarted).on('drag', dragged).on('end', dragended) as any);

		node
			.append('circle')
			.attr('r', 8)
			.attr('fill', (d: any) => {
				if (d.path.includes('/raw/failures/')) return '#ef4444';
				if (d.path.includes('/raw/')) return '#22c55e';
				if (d.path.includes('/wiki/')) return '#3b82f6';
				return d.orphan ? '#94a3b8' : '#8b5cf6';
			});

		node
			.append('text')
			.text((d: any) => d.label)
			.attr('x', 12)
			.attr('y', 4)
			.attr('font-size', '10px')
			.attr('fill', 'currentColor')
			.attr('class', 'select-none');

		simulation.on('tick', () => {
			link
				.attr('x1', (d: any) => d.source.x)
				.attr('y1', (d: any) => d.source.y)
				.attr('x2', (d: any) => d.target.x)
				.attr('y2', (d: any) => d.target.y);
			node.attr('transform', (d: any) => `translate(${d.x},${d.y})`);
		});

		function dragstarted(event: any, d: any) {
			if (!event.active) simulation.alphaTarget(0.3).restart();
			d.fx = d.x;
			d.fy = d.y;
		}
		function dragged(event: any, d: any) {
			d.fx = event.x;
			d.fy = event.y;
		}
		function dragended(event: any, d: any) {
			if (!event.active) simulation.alphaTarget(0);
			d.fx = null;
			d.fy = null;
		}
	}

	$effect(() => {
		if (graph && svgRef) {
			drawGraph();
		}
	});

	let saving = $state(false);
	
	async function savePreview() {
		if (!selected) return;
		saving = true;
		try {
			await api.put('/api/v1/kb/document', { path: selected.path, content: preview });
		} catch (e) {
			console.error(e);
		} finally {
			saving = false;
		}
	}

	let selectedBacklinks = $derived(() => {
		if (!selected || !graph) return [];
		const id = selected.name.toLowerCase().replace(/\s+/g, '-');
		return graph.edges
			.filter(e => {
				const targetId = typeof e.target === 'object' ? (e.target as any).id : e.target;
				return targetId === id;
			})
			.map(e => {
				const sourceId = typeof e.source === 'object' ? (e.source as any).id : e.source;
				return graph.nodes.find(n => n.id === sourceId);
			})
			.filter(Boolean);
	});
</script>

<svelte:head>
	<title>Knowledge Base | Cockpit Dashboard</title>
	<meta name="description" content="Base de conhecimento do cockpit" />
</svelte:head>

<div class="space-y-6 h-[calc(100vh-8rem)]">
	<div>
		<h1 class="text-3xl font-bold tracking-tight">Knowledge Base</h1>
		<p class="text-muted-foreground mt-1">Explore notas, conexões e documentações.</p>
	</div>

	<div class="flex gap-2">
		<input
			type="text"
			placeholder="Buscar notas..."
			class="flex-1 rounded-md border border-border bg-background px-3 py-2 text-sm"
			bind:value={query}
			onkeydown={(e) => e.key === 'Enter' && search()}
		/>
		<button class="bg-primary text-primary-foreground px-4 py-2 rounded-md text-sm" onclick={search}>Buscar</button>
	</div>

	<div class="grid gap-4 lg:grid-cols-4 h-full">
		<div class="lg:col-span-1 overflow-y-auto space-y-2 pr-2">
			<h2 class="font-semibold mb-2">Documentos ({documents.length})</h2>
			{#each documents as doc}
				<button
					class="w-full text-left rounded-lg border border-border bg-card/50 px-3 py-2 text-sm hover:bg-card/80 transition-colors"
					onclick={() => showPreview(doc)}
				>
					{doc.name}
				</button>
			{/each}
		</div>
		<div class="lg:col-span-3 rounded-xl border border-border bg-card/50 p-4 relative">
			<svg bind:this={svgRef} class="w-full h-full min-h-[300px]"></svg>
			{#if graph && graph.nodes.length === 0}
				<div class="absolute inset-0 flex items-center justify-center text-muted-foreground">
					Nenhuma nota encontrada.
				</div>
			{/if}
		</div>
	</div>
</div>

{#if selected}
	<div class="fixed inset-0 z-50 bg-black/50" onclick={() => (selected = null)} role="presentation"></div>
	<div class="fixed inset-y-0 right-0 z-50 w-full max-w-4xl bg-slate-900 border-l border-border flex flex-col shadow-2xl">
		<!-- Header -->
		<div class="p-4 border-b border-border flex items-center justify-between bg-slate-950">
			<h2 class="text-lg font-bold">{selected.name}</h2>
			<div class="flex items-center gap-3">
				<button 
					class="bg-primary hover:bg-primary/90 text-primary-foreground px-4 py-1.5 rounded-md text-sm font-semibold transition-colors disabled:opacity-50" 
					onclick={savePreview}
					disabled={saving}
				>
					{saving ? 'Salvando...' : 'Salvar'}
				</button>
				<button class="text-muted-foreground hover:text-foreground" onclick={() => (selected = null)}>✕</button>
			</div>
		</div>
		
		<!-- Content -->
		<div class="flex-1 flex overflow-hidden">
			<!-- Editor -->
			<div class="flex-1 p-4 overflow-y-auto">
				<textarea 
					class="w-full h-full min-h-[70vh] bg-slate-950/50 border border-border rounded-lg p-4 font-mono text-sm text-slate-300 focus:outline-none focus:border-primary resize-none transition-colors leading-relaxed"
					bind:value={preview}
				></textarea>
			</div>

			<!-- Sidebar (Backlinks & Meta) -->
			<div class="w-64 border-l border-border bg-slate-950/30 p-4 overflow-y-auto">
				<h3 class="font-semibold text-sm mb-3 text-slate-300 uppercase tracking-wider">Backlinks</h3>
				{#if selectedBacklinks.length > 0}
					<ul class="space-y-2">
						{#each selectedBacklinks as bl}
							<li>
								<button 
									class="text-left w-full text-xs text-blue-400 hover:text-blue-300 hover:underline truncate"
									onclick={() => {
										const doc = documents.find(d => d.path === bl?.path);
										if (doc) showPreview(doc);
									}}
								>
									{bl?.label}
								</button>
							</li>
						{/each}
					</ul>
				{:else}
					<div class="text-xs text-muted-foreground">Nenhum documento aponta para cá.</div>
				{/if}
				
				<div class="mt-6">
					<h3 class="font-semibold text-sm mb-3 text-slate-300 uppercase tracking-wider">File Path</h3>
					<div class="text-[10px] text-muted-foreground font-mono break-all bg-black/40 p-2 rounded border border-border/50">
						{selected.path}
					</div>
				</div>
			</div>
		</div>
	</div>
{/if}
