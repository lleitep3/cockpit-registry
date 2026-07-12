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
			.attr('fill', (d: any) => (d.orphan ? '#94a3b8' : '#8b5cf6'));

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
	<div class="fixed inset-y-0 right-0 z-50 w-full max-w-lg bg-slate-900 border-l border-border p-6 overflow-y-auto shadow-2xl">
		<div class="flex items-center justify-between mb-6">
			<h2 class="text-xl font-bold">{selected.name}</h2>
			<button class="text-muted-foreground hover:text-foreground" onclick={() => (selected = null)}>✕</button>
		</div>
		<div class="prose prose-invert prose-sm max-w-none">
			<pre class="whitespace-pre-wrap text-sm text-muted-foreground font-mono">{preview}</pre>
		</div>
	</div>
{/if}
