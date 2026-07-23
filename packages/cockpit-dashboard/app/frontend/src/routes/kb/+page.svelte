<script lang="ts">
	import { onMount } from 'svelte';
	import { api } from '$lib/api';
	import * as d3 from 'd3';
	import { marked } from 'marked';

	type Document = {
		id: string;
		name: string;
		path: string;
		tags?: string[];
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
	let selectedTag = $state<string | null>(null);
	let documents = $state<Document[]>([]);
	let graph = $state<Graph | null>(null);
	let selected = $state<Document | null>(null);
	let preview = $state<string>('');
	let viewMode = $state<'preview' | 'edit'>('preview');
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
		viewMode = 'preview';
		try {
			const res = await api.get<{content: string}>(`/api/v1/kb/document?path=${encodeURIComponent(doc.path)}`);
			preview = res.content;
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

		const container = svg.append('g');

		const zoom = d3.zoom()
			.scaleExtent([0.1, 4])
			.on('zoom', (event: any) => {
				container.attr('transform', event.transform);
			});

		svg.call(zoom as any);

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

		const link = container
			.append('g')
			.selectAll('line')
			.data(edges)
			.enter()
			.append('line')
			.attr('stroke', 'currentColor')
			.attr('stroke-opacity', 0.3)
			.attr('stroke-width', 1);

		const node = container
			.append('g')
			.selectAll('g')
			.data(nodes)
			.enter()
			.append('g')
			.attr('cursor', 'pointer')
			.on('click', (_event, d) => {
				const doc = documents.find((doc) => doc.id === d.id);
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

	let allTags = $derived(Array.from(new Set(documents.flatMap(d => d.tags || []))).sort());

	let filteredDocs = $derived(documents.filter(d => {
		if (selectedTag && (!d.tags || !d.tags.includes(selectedTag))) return false;
		if (query && !d.name.toLowerCase().includes(query.toLowerCase()) && !d.path.toLowerCase().includes(query.toLowerCase())) return false;
		return true;
	}));

	let selectedBacklinks = $derived(() => {
		if (!selected || !graph) return [];
		const id = selected.id;
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
	<div class="flex items-center justify-between">
		<div>
			<h1 class="text-3xl font-bold tracking-tight text-white flex items-center gap-3">
				<svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-amber-400 drop-shadow-[0_0_10px_rgba(245,158,11,0.5)]"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1 0-5H20"></path></svg>
				Knowledge Base
			</h1>
			<p class="text-muted-foreground mt-1">Explore notas, conexões e documentações técnicas do seu workspace.</p>
		</div>
		<div class="flex gap-2 w-[32rem] relative z-10">
			<div class="flex-1 relative">
				<div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
					<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-muted-foreground"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
				</div>
				<input
					type="text"
					placeholder="Buscar notas e documentos..."
					class="w-full rounded-full border border-white/10 bg-black/40 pl-10 pr-4 py-2 text-sm text-white focus:outline-none focus:border-amber-500/50 focus:ring-1 focus:ring-amber-500/50 transition-all backdrop-blur-md placeholder:text-muted-foreground/70"
					bind:value={query}
				/>
			</div>
			
			<select 
				class="rounded-full border border-white/10 bg-black/40 px-4 py-2 text-sm text-white focus:outline-none focus:border-amber-500/50 focus:ring-1 focus:ring-amber-500/50 transition-all backdrop-blur-md appearance-none cursor-pointer hover:bg-black/60"
				bind:value={selectedTag}
			>
				<option value={null}>Todas as tags</option>
				{#each allTags as tag}
					<option value={tag}>{tag}</option>
				{/each}
			</select>
		</div>
	</div>

	<div class="grid gap-6 lg:grid-cols-4 h-[calc(100%-4rem)]">
		<div class="lg:col-span-1 overflow-y-auto space-y-3 pr-2 custom-scrollbar">
			<div class="flex items-center justify-between mb-4">
				<h2 class="text-xs font-bold uppercase tracking-widest text-muted-foreground">Documentos ({filteredDocs.length})</h2>
			</div>
			{#each filteredDocs as doc}
				<button
					class="w-full text-left rounded-xl border border-white/5 bg-black/20 px-4 py-3 text-sm hover:bg-black/60 hover:border-amber-500/30 transition-all duration-300 group relative overflow-hidden"
					onclick={() => showPreview(doc)}
				>
					<div class="absolute inset-0 bg-gradient-to-r from-amber-500/0 via-amber-500/0 to-amber-500/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
					<div class="relative z-10 flex items-center gap-3">
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-muted-foreground group-hover:text-amber-400 transition-colors"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
						<span class="text-gray-300 group-hover:text-white transition-colors truncate font-medium">{doc.name}</span>
					</div>
				</button>
			{/each}
		</div>
		<div class="lg:col-span-3 relative overflow-hidden rounded-2xl border border-white/5 bg-black/40 backdrop-blur-md shadow-[0_0_30px_rgba(0,0,0,0.5)] flex flex-col">
			<div class="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-[1px] bg-gradient-to-r from-transparent via-amber-500/20 to-transparent"></div>
			
			<div class="absolute top-4 right-4 z-10 flex gap-2">
				<button 
					class="bg-black/60 hover:bg-black/80 text-white border border-white/10 p-2 rounded-lg backdrop-blur-md transition-colors"
					onclick={() => d3.select(svgRef).transition().duration(750).call(d3.zoom().transform as any, d3.zoomIdentity)}
					title="Reset Zoom"
				>
					<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path><polyline points="9 22 9 12 15 12 15 22"></polyline></svg>
				</button>
			</div>

			<svg bind:this={svgRef} class="flex-1 w-full min-h-[300px]"></svg>
			{#if graph && graph.nodes.length === 0}
				<div class="absolute inset-0 flex items-center justify-center text-muted-foreground flex-col gap-3">
					<svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="opacity-50"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
					<span>Nenhuma nota encontrada na rede.</span>
				</div>
			{/if}
		</div>
	</div>
</div>

{#if selected}
	<div class="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm" onclick={() => (selected = null)} role="presentation"></div>
	<div class="fixed inset-y-0 right-0 z-50 w-full max-w-4xl bg-black/95 backdrop-blur-2xl border-l border-white/10 flex flex-col shadow-[-20px_0_50px_rgba(0,0,0,0.5)]">
		<!-- Header -->
		<div class="p-5 border-b border-white/10 flex items-center justify-between bg-black/40">
			<h2 class="text-xl font-bold text-white flex items-center gap-3">
				<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="text-amber-500"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
				{selected.name}
			</h2>
			<div class="flex items-center gap-4">
				<div class="flex bg-black/60 rounded-full border border-white/5 p-1 mr-2">
					<button 
						class="px-4 py-1.5 rounded-full text-xs font-bold transition-colors {viewMode === 'preview' ? 'bg-amber-500 text-black' : 'text-gray-400 hover:text-white'}"
						onclick={() => viewMode = 'preview'}
					>Preview</button>
					<button 
						class="px-4 py-1.5 rounded-full text-xs font-bold transition-colors {viewMode === 'edit' ? 'bg-amber-500 text-black' : 'text-gray-400 hover:text-white'}"
						onclick={() => viewMode = 'edit'}
					>Editor</button>
				</div>
				<button 
					class="bg-amber-500/20 hover:bg-amber-500/40 text-amber-400 hover:text-amber-300 border border-amber-500/50 px-5 py-2 rounded-full text-sm font-bold transition-all disabled:opacity-50 hover:shadow-[0_0_15px_rgba(245,158,11,0.2)]" 
					onclick={savePreview}
					disabled={saving}
				>
					{saving ? 'Salvando...' : 'Salvar Arquivo'}
				</button>
				<button class="text-muted-foreground hover:text-white transition-colors bg-white/5 hover:bg-white/10 p-2 rounded-full" onclick={() => (selected = null)}>
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
				</button>
			</div>
		</div>
		
		<!-- Content -->
		<div class="flex-1 flex overflow-hidden">
			<!-- Editor / Preview -->
			<div class="flex-1 p-8 overflow-y-auto custom-scrollbar bg-black/20">
				{#if viewMode === 'edit'}
					<textarea 
						class="w-full h-full min-h-[70vh] bg-transparent border-0 p-0 font-mono text-sm text-gray-300 focus:outline-none focus:ring-0 resize-none transition-colors leading-relaxed"
						bind:value={preview}
						spellcheck="false"
					></textarea>
				{:else}
					<div class="prose prose-invert prose-amber max-w-none">
						{@html marked(preview)}
					</div>
				{/if}
			</div>

			<!-- Sidebar (Backlinks & Meta) -->
			<div class="w-72 border-l border-white/5 bg-black/40 p-6 overflow-y-auto custom-scrollbar flex flex-col gap-8">
				<div>
					<h3 class="font-bold text-xs mb-4 text-muted-foreground uppercase tracking-[0.2em] flex items-center gap-2">
						<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>
						Backlinks
					</h3>
					{#if selectedBacklinks.length > 0}
						<ul class="space-y-3">
							{#each selectedBacklinks as bl}
								<li>
									<button 
										class="text-left w-full text-sm text-blue-400 hover:text-blue-300 hover:underline truncate bg-blue-500/10 hover:bg-blue-500/20 px-3 py-2 rounded-lg border border-blue-500/20 transition-colors"
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
						<div class="text-sm text-muted-foreground/70 italic bg-white/5 p-4 rounded-lg border border-white/5">Nenhum documento aponta para cá.</div>
					{/if}
				</div>
				
				<div>
					<h3 class="font-bold text-xs mb-4 text-muted-foreground uppercase tracking-[0.2em]">Caminho Físico</h3>
					<div class="text-[11px] text-gray-400 font-mono break-all bg-black/60 p-3 rounded-lg border border-white/10 shadow-inner">
						{selected.path}
					</div>
				</div>
			</div>
		</div>
	</div>
{/if}
