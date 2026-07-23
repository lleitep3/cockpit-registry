<script lang="ts">
	import { onMount } from 'svelte';
	import { page } from '$app/stores';
	import { api } from '$lib/api';
	import { marked } from 'marked';
	import DOMPurify from 'dompurify';

	let selectedProject = $state<any>(null);
	let loading = $state(true);

	onMount(async () => {
		const slug = $page.params.slug;
		await loadProject(slug);
	});

	async function loadProject(slug: string) {
		try {
			if (!selectedProject || selectedProject.id !== slug) {
				loading = true;
			}
			selectedProject = await api.get(`/api/v1/projects/${slug}`);
		} catch (err) {
			console.error('Failed to load project details:', err);
		} finally {
			loading = false;
		}
	}

	let newTaskTitle = $state('');
	let viewMode = $state<'list' | 'board'>('list');
	let selectedTask = $state<any>(null);
	let isTaskDrawerOpen = $state(false);
	let isMarkdownPreview = $state(false);
	let syncInProgress = $state(false);

	function openTask(task: any) {
		selectedTask = { ...task };
		selectedTask._labelsStr = selectedTask.labels?.join(', ') || '';
		selectedTask._assigneesStr = selectedTask.assignees?.join(', ') || '';
		if (!selectedTask.state) selectedTask.state = 'open';
		isMarkdownPreview = false;
		isTaskDrawerOpen = true;
	}

	function closeTaskDrawer() {
		isTaskDrawerOpen = false;
		selectedTask = null;
	}

	async function syncGitHubIssue() {
		if (!selectedProject || !selectedTask || !selectedTask.repository) {
			alert('Selecione um repositório antes de sincronizar.');
			return;
		}
		
		syncInProgress = true;
		try {
			const res = await api.post<any>(`/api/v1/projects/${selectedProject.id}/task/${selectedTask.id}/sync`, {});
			if (res.error) {
				alert(res.error);
			} else {
				selectedTask = { ...res.task };
				selectedTask._labelsStr = selectedTask.labels?.join(', ') || '';
				selectedTask._assigneesStr = selectedTask.assignees?.join(', ') || '';
				
				const index = selectedProject.tasks?.findIndex((t: any) => t.id === selectedTask.id);
				if (index !== undefined && index !== -1) {
					selectedProject.tasks[index] = { ...selectedTask };
				}
				alert('Sincronizado com sucesso!');
			}
		} catch (err) {
			console.error(err);
			alert('Erro na sincronização');
		} finally {
			syncInProgress = false;
		}
	}

	async function updateTask() {
		if (!selectedProject || !selectedTask) return;
		try {
			if (typeof selectedTask._labelsStr === 'string') {
				selectedTask.labels = selectedTask._labelsStr.split(',').map((s: string) => s.trim()).filter(Boolean);
			}
			if (typeof selectedTask._assigneesStr === 'string') {
				selectedTask.assignees = selectedTask._assigneesStr.split(',').map((s: string) => s.trim()).filter(Boolean);
			}
			delete selectedTask._labelsStr;
			delete selectedTask._assigneesStr;

			const index = selectedProject.tasks?.findIndex((t: any) => t.id === selectedTask.id);
			if (index !== undefined && index !== -1) {
				selectedProject.tasks[index] = { ...selectedTask };
			}
			await saveProjectMeta();
			closeTaskDrawer();
		} catch (err) {
			console.error('Failed to update task:', err);
		}
	}

	async function saveProjectMeta() {
		if (!selectedProject) return;
		try {
			await api.put(`/api/v1/projects/${selectedProject.id}`, {
				tags: selectedProject.tags,
				repositories: selectedProject.repositories,
				links: selectedProject.links,
				tasks: selectedProject.tasks
			});
			await loadProject(selectedProject.id);
		} catch (err) {
			console.error('Failed to save project:', err);
		}
	}

	let newTag = $state('');
	function addTag() {
		if (!newTag || !selectedProject) return;
		if (!selectedProject.tags) selectedProject.tags = [];
		if (!selectedProject.tags.includes(newTag)) {
			selectedProject.tags = [...selectedProject.tags, newTag];
			saveProjectMeta();
		}
		newTag = '';
	}
	function removeTag(tag: string) {
		if (!selectedProject) return;
		selectedProject.tags = selectedProject.tags.filter((t: string) => t !== tag);
		saveProjectMeta();
	}

	let newRepo = $state('');
	function addRepo() {
		if (!newRepo || !selectedProject) return;
		if (!selectedProject.repositories) selectedProject.repositories = [];
		if (!selectedProject.repositories.includes(newRepo)) {
			selectedProject.repositories = [...selectedProject.repositories, newRepo];
			saveProjectMeta();
		}
		newRepo = '';
	}
	function removeRepo(repo: string) {
		if (!selectedProject) return;
		selectedProject.repositories = selectedProject.repositories.filter((r: string) => r !== repo);
		saveProjectMeta();
	}

	let newRef = $state('');
	function addRef() {
		if (!newRef || !selectedProject) return;
		if (!selectedProject.links) selectedProject.links = [];
		if (!selectedProject.links.some((l: any) => l.url === newRef)) {
			selectedProject.links = [...selectedProject.links, { title: newRef, url: newRef }];
			saveProjectMeta();
		}
		newRef = '';
	}
	function removeRef(url: string) {
		if (!selectedProject) return;
		selectedProject.links = selectedProject.links.filter((r: any) => r.url !== url);
		saveProjectMeta();
	}


	
	async function addTask() {
		if (!newTaskTitle || !selectedProject) return;
		try {
			await api.post(`/api/v1/projects/${selectedProject.id}/task`, { title: newTaskTitle });
			newTaskTitle = '';
			await loadProject(selectedProject.id);
		} catch (err) {
			console.error(err);
		}
	}

	async function moveTask(taskId: string, col: string) {
		if (!selectedProject) return;
		try {
			await api.put(`/api/v1/projects/${selectedProject.id}/task/${taskId}/move`, { column: col });
			await loadProject(selectedProject.id);
		} catch (err) {
			console.error(err);
		}
	}

	let draggedTaskId: string | null = $state(null);

	function handleDragStart(e: DragEvent, taskId: string) {
		draggedTaskId = taskId;
		if (e.dataTransfer) {
			e.dataTransfer.effectAllowed = 'move';
			e.dataTransfer.setData('text/plain', taskId);
		}
	}

	function handleDragOver(e: DragEvent) {
		e.preventDefault();
		if (e.dataTransfer) {
			e.dataTransfer.dropEffect = 'move';
		}
	}

	function handleDrop(e: DragEvent, col: string) {
		e.preventDefault();
		if (draggedTaskId) {
			moveTask(draggedTaskId, col);
			draggedTaskId = null;
		}
	}

	async function handleTaskDrop(e: DragEvent, targetTask: any) {
		e.preventDefault();
		e.stopPropagation();
		if (!draggedTaskId || !selectedProject) return;
		if (draggedTaskId === targetTask.id) return;
		
		const dTaskId = draggedTaskId;
		draggedTaskId = null;

		const draggedTask = selectedProject.tasks.find((t: any) => t.id === dTaskId);
		if (!draggedTask) return;

		// Move first if different column
		if (draggedTask.status !== targetTask.status) {
			await api.put(`/api/v1/projects/${selectedProject.id}/task/${dTaskId}/move`, { column: targetTask.status });
			// Reload to get fresh tasks order after move
			await loadProject(selectedProject.id);
		}

		// Now reorder
		const newIndex = selectedProject.tasks.findIndex((t: any) => t.id === targetTask.id);
		if (newIndex !== -1) {
			await api.put(`/api/v1/projects/${selectedProject.id}/task/${dTaskId}/reorder`, { index: newIndex });
		}
		
		await loadProject(selectedProject.id);
	}
</script>

<div class="flex flex-col gap-6 w-full max-w-5xl mx-auto pb-12">
	<div class="flex flex-col gap-2">
		<a href="/p/projects" class="text-muted-foreground hover:text-foreground text-sm flex items-center gap-2 mb-2 w-fit transition-colors">
			&larr; Voltar pra Projetos
		</a>
		
		{#if loading}
			<div class="text-center p-12 text-muted-foreground">Carregando detalhes do projeto...</div>
		{:else if !selectedProject}
			<div class="p-8 border border-dashed border-border rounded-xl text-center">
				<p class="text-muted-foreground mb-4">Projeto não encontrado.</p>
			</div>
		{:else}
			<div class="flex flex-wrap items-center gap-3">
				<h1 class="text-3xl font-bold tracking-tight">{selectedProject.title}</h1>
				<span class="px-2 py-0.5 bg-emerald-500/10 border border-emerald-500/20 text-emerald-500 text-[10px] font-bold uppercase rounded tracking-wider">Active</span>
				<span class="px-2 py-0.5 dark:bg-slate-800 bg-muted text-muted-foreground text-[10px] font-bold uppercase rounded tracking-wider">Sem Prazo</span>
			</div>
			<p class="text-muted-foreground text-sm mt-1">{selectedProject.description}</p>
			
			<div class="mt-8 flex flex-col gap-3">
				<div class="grid grid-cols-12 text-sm items-center gap-4 border-b border-border/50 pb-3">
					<div class="col-span-3 md:col-span-2 text-muted-foreground">Slug</div>
					<div class="col-span-9 md:col-span-10 flex items-center gap-2">
						{selectedProject.slug || $page.params.slug}
						<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="text-muted-foreground hover:text-foreground cursor-pointer transition-colors"><path d="M12 20h9"/><path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z"/></svg>
					</div>
				</div>
				<div class="grid grid-cols-12 text-sm items-center gap-4 border-b border-border/50 pb-3">
					<div class="col-span-3 md:col-span-2 text-muted-foreground">Owner</div>
					<div class="col-span-9 md:col-span-10 text-foreground">{selectedProject.owner || 'Não definido'}</div>
				</div>
				<div class="grid grid-cols-12 text-sm items-center gap-4 border-b border-border/50 pb-3">
					<div class="col-span-3 md:col-span-2 text-muted-foreground">Criado em</div>
					<div class="col-span-9 md:col-span-10 text-foreground">{selectedProject.created_at || 'Desconhecido'}</div>
				</div>
				<div class="grid grid-cols-12 text-sm items-center gap-4 border-b border-border/50 pb-3">
					<div class="col-span-3 md:col-span-2 text-muted-foreground">Workspace</div>
					<div class="col-span-9 md:col-span-10 text-muted-foreground font-mono text-xs">{selectedProject.workspaces?.[0] || 'Nenhum'}</div>
				</div>
			</div>

			<div class="mt-8">
				<h3 class="font-semibold text-base mb-3">Tags</h3>
				{#if selectedProject.tags && selectedProject.tags.length > 0}
					<div class="flex flex-wrap gap-2 mb-3">
						{#each selectedProject.tags as tag}
							<div class="flex items-center gap-1 px-3 py-1 dark:bg-slate-900 bg-card border border-border text-foreground text-sm rounded-full">
								<span>{tag}</span>
								<button class="text-muted-foreground hover:text-destructive transition-colors ml-1" onclick={() => removeTag(tag)}>
									<svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
								</button>
							</div>
						{/each}
					</div>
				{/if}
				<form class="flex max-w-sm" onsubmit={(e) => { e.preventDefault(); addTag(); }}>
					<input type="text" placeholder="Adicionar tag..." class="bg-transparent border-none outline-none text-sm text-muted-foreground placeholder:text-muted-foreground/50 w-full flex-1" bind:value={newTag} />
					<button type="submit" class="text-xs text-primary font-medium hover:underline ml-2" disabled={!newTag}>Adicionar</button>
				</form>
			</div>

			<div class="mt-8 border-t border-border pt-6">
				<h3 class="font-semibold text-base mb-3">Repositórios</h3>
				{#if selectedProject.repositories?.length}
					<div class="flex flex-col gap-2 mb-3">
						{#each selectedProject.repositories as repo}
							<div class="flex items-center gap-2 group">
								<a href={repo} target="_blank" class="text-blue-400 hover:underline text-sm block truncate flex-1">{repo}</a>
								<button class="opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-destructive transition-all" onclick={() => removeRepo(repo)}>
									<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
								</button>
							</div>
						{/each}
					</div>
				{:else}
					<p class="text-sm text-muted-foreground mb-3">Nenhum repositório associado ainda.</p>
				{/if}
				<form class="flex max-w-sm mt-2" onsubmit={(e) => { e.preventDefault(); addRepo(); }}>
					<input type="text" placeholder="URL do repositório..." class="dark:bg-slate-900 bg-card border border-border text-sm rounded px-3 py-1.5 focus:ring-1 focus:ring-primary outline-none flex-1" bind:value={newRepo} />
					<button type="submit" class="bg-primary text-primary-foreground px-3 py-1.5 rounded ml-2 text-sm font-medium hover:opacity-90" disabled={!newRepo}>Adicionar</button>
				</form>
			</div>

			<div class="mt-8 border-t border-border pt-6">
				<h3 class="font-semibold text-base mb-3">Outras referências</h3>
				{#if selectedProject.links?.length}
					<div class="flex flex-col gap-2 mb-3">
						{#each selectedProject.links as link}
							<div class="flex items-center gap-2 group">
								<a href={link.url} target="_blank" class="text-blue-400 hover:underline text-sm block truncate flex-1">{link.title || link.url}</a>
								<button class="opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-destructive transition-all" onclick={() => removeRef(link.url)}>
									<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
								</button>
							</div>
						{/each}
					</div>
				{:else}
					<p class="text-sm text-muted-foreground mb-3">Nenhuma outra referência (Jira, Confluence, docs...).</p>
				{/if}
				<form class="flex max-w-sm mt-2" onsubmit={(e) => { e.preventDefault(); addRef(); }}>
					<input type="text" placeholder="URL da referência..." class="dark:bg-slate-900 bg-card border border-border text-sm rounded px-3 py-1.5 focus:ring-1 focus:ring-primary outline-none flex-1" bind:value={newRef} />
					<button type="submit" class="bg-primary text-primary-foreground px-3 py-1.5 rounded ml-2 text-sm font-medium hover:opacity-90" disabled={!newRef}>Adicionar</button>
				</form>
			</div>

			<div class="mt-10 border-t border-border pt-6">
				<div class="flex items-center justify-between mb-4">
					<h3 class="font-semibold text-base">Tasks ({selectedProject.tasks?.length || 0})</h3>
					<div class="flex items-center gap-4 text-xs">
						<div class="text-muted-foreground">{selectedProject.tasks?.filter((t: any) => t.status?.toLowerCase() === 'done').length || 0}/{selectedProject.tasks?.length || 0} concluidas</div>
						<div class="flex items-center dark:bg-slate-900 bg-card rounded border border-border overflow-hidden">
							<button class="px-3 py-1.5 transition-colors font-medium" class:bg-primary={viewMode === 'list'} class:text-primary-foreground={viewMode === 'list'} class:text-muted-foreground={viewMode !== 'list'} onclick={() => viewMode = 'list'}>Lista</button>
							<button class="px-3 py-1.5 transition-colors font-medium" class:bg-primary={viewMode === 'board'} class:text-primary-foreground={viewMode === 'board'} class:text-muted-foreground={viewMode !== 'board'} onclick={() => viewMode = 'board'}>Board</button>
						</div>
					</div>
				</div>

				<div class="w-full dark:bg-slate-900 bg-card h-1.5 rounded-full overflow-hidden mb-6">
					<div class="bg-primary h-full rounded-full transition-all duration-500" style="width: {selectedProject.tasks?.length ? ((selectedProject.tasks.filter((t: any) => t.status?.toLowerCase() === 'done').length) / selectedProject.tasks.length) * 100 : 0}%"></div>
				</div>

				{#if viewMode === 'list'}
					<div class="flex flex-col border border-border rounded-xl dark:bg-slate-900/30 bg-card/50 overflow-hidden">
						<div class="grid grid-cols-12 gap-4 p-4 border-b border-border dark:bg-slate-900/80 bg-card text-sm font-semibold text-muted-foreground">
							<div class="col-span-2">ID</div>
							<div class="col-span-6">Titulo</div>
							<div class="col-span-2">Estagio</div>
							<div class="col-span-2">Status</div>
						</div>
						<div class="flex flex-col divide-y divide-border/50">
							{#each (selectedProject.tasks || []) as task (task.id)}
								<!-- svelte-ignore a11y_click_events_have_key_events -->
								<!-- svelte-ignore a11y_no_static_element_interactions -->
								<div class="grid grid-cols-12 gap-4 p-4 text-sm hover:dark:bg-slate-900/50 hover:bg-muted/50 transition-colors items-center cursor-pointer" onclick={() => openTask(task)}>
									<div class="col-span-2 text-muted-foreground font-mono text-xs">{task.id.slice(0, 8).toUpperCase()}</div>
									<div class="col-span-6 font-medium text-foreground">{task.title}</div>
									<div class="col-span-2 text-muted-foreground text-xs">{task.status}</div>
									<div class="col-span-2 text-xs flex items-center gap-2">
										<div class="w-1.5 h-1.5 rounded-full {task.status === 'done' ? 'bg-emerald-500' : 'bg-amber-500'}"></div>
										{task.status === 'done' ? 'concluido' : 'ativo'}
									</div>
								</div>
							{/each}
							{#if !selectedProject.tasks?.length}
								<div class="p-8 text-center text-muted-foreground text-sm">Nenhuma task encontrada.</div>
							{/if}
						</div>
					</div>
					<form class="mt-4 flex gap-2 max-w-xl" onsubmit={(e) => { e.preventDefault(); addTask(); }}>
						<input type="text" placeholder="Nova task..." class="flex-1 dark:bg-slate-900 bg-card border border-border text-sm rounded-lg px-3 py-2 focus:ring-1 focus:ring-primary outline-none" bind:value={newTaskTitle} />
						<button type="submit" class="bg-primary text-primary-foreground px-4 py-2 rounded-lg hover:opacity-90 text-sm font-medium transition-opacity">Adicionar</button>
					</form>
				{:else}
					<div class="flex gap-4 overflow-x-auto pb-4 pt-2">
						{#if selectedProject.board_columns}
							{#each selectedProject.board_columns as col}
								<div 
									class="min-w-[280px] w-[280px] dark:bg-slate-900 bg-muted/30 border border-border rounded-xl p-3 flex flex-col h-[500px]"
									role="region"
									aria-label="{col} column"
									ondragover={handleDragOver}
									ondrop={(e) => handleDrop(e, col)}
								>
									<div class="flex items-center justify-between mb-3 px-1">
										<h4 class="font-semibold text-sm uppercase tracking-wide">{col}</h4>
										<span class="dark:bg-slate-800 bg-background text-xs px-2 py-0.5 rounded-full">
											{selectedProject.tasks?.filter((t: any) => t.status?.toLowerCase() === col.toLowerCase()).length || 0}
										</span>
									</div>
									
									<div class="flex-1 overflow-y-auto space-y-2 pr-1">
										{#each (selectedProject.tasks || []).filter((t: any) => t.status?.toLowerCase() === col.toLowerCase()) as task (task.id)}
											<!-- svelte-ignore a11y_click_events_have_key_events -->
											<!-- svelte-ignore a11y_no_static_element_interactions -->
											<div 
												class="dark:bg-slate-800 bg-card p-3 rounded-lg border dark:border-slate-700 border-border shadow-sm text-sm group cursor-pointer hover:border-primary transition-colors {draggedTaskId === task.id ? 'opacity-50' : ''}" 
												onclick={() => openTask(task)}
												role="button"
												tabindex="0"
												draggable="true"
												ondragstart={(e) => handleDragStart(e, task.id)}
												ondragover={handleDragOver}
												ondrop={(e) => handleTaskDrop(e, task)}
											>
												<p class="mb-2 font-medium">{task.title}</p>
												
												<div class="opacity-0 group-hover:opacity-100 transition-opacity flex gap-1 flex-wrap">
													{#each selectedProject.board_columns as moveCol}
														{#if moveCol !== col}
															<button 
																class="text-[10px] dark:bg-slate-700 bg-muted hover:bg-primary hover:text-primary-foreground px-1.5 py-0.5 rounded transition-colors"
																onclick={(e) => { e.stopPropagation(); moveTask(task.id, moveCol); }}
															>
																{moveCol}
															</button>
														{/if}
													{/each}
												</div>
											</div>
										{/each}
									</div>

									{#if col === 'todo'}
										<div class="mt-3 pt-3 border-t dark:border-slate-800 border-border">
											<form 
												class="flex gap-2"
												onsubmit={(e) => { e.preventDefault(); addTask(); }}
											>
												<input 
													type="text" 
													placeholder="Nova task..." 
													class="flex-1 dark:bg-slate-800 bg-background border border-border text-sm rounded px-2 py-1.5 focus:ring-1 focus:ring-primary outline-none"
													bind:value={newTaskTitle}
												/>
												<button type="submit" class="bg-primary text-primary-foreground p-1.5 rounded hover:opacity-90">
													<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
												</button>
											</form>
										</div>
									{/if}
								</div>
							{/each}
						{/if}
					</div>
				{/if}
			</div>
		{/if}
	</div>
</div>

<!-- Task Edit Drawer -->
{#if isTaskDrawerOpen && selectedTask}
	<div class="fixed inset-0 z-50 flex justify-end bg-black/50 backdrop-blur-sm" onclick={closeTaskDrawer} role="presentation">
		<!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
		<!-- svelte-ignore a11y_click_events_have_key_events -->
		<aside 
			class="w-full max-w-md h-full dark:bg-slate-900 bg-card border-l border-border shadow-2xl flex flex-col transform transition-transform animate-in slide-in-from-right"
			onclick={(e) => e.stopPropagation()}
			role="dialog"
		>
			<div class="flex items-center justify-between p-4 border-b border-border">
				<div class="flex items-center gap-2">
					<span class="text-xs text-muted-foreground font-mono bg-muted px-2 py-1 rounded">{selectedTask.id.slice(0, 8).toUpperCase()}</span>
				</div>
				<button class="p-2 hover:bg-muted rounded-full transition-colors" onclick={closeTaskDrawer}>
					<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
				</button>
			</div>

			<div class="flex-1 overflow-y-auto p-6 flex flex-col gap-6">
				<div>
					<label class="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2" for="task-title">Título da Task</label>
					<input id="task-title" type="text" bind:value={selectedTask.title} class="w-full bg-transparent border-b border-border pb-2 outline-none text-xl font-medium focus:border-primary transition-colors" />
				</div>

				<div class="grid grid-cols-2 gap-4">
					<div>
						<label class="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2" for="task-status">Status (Board)</label>
						<select id="task-status" bind:value={selectedTask.status} class="w-full dark:bg-slate-800 bg-muted border border-border text-sm rounded-lg px-3 py-2 outline-none focus:ring-1 focus:ring-primary">
							{#if selectedProject?.board_columns}
								{#each selectedProject.board_columns as col}
									<option value={col}>{col}</option>
								{/each}
							{/if}
						</select>
					</div>
					<div>
						<label class="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2" for="task-state">State (Issue)</label>
						<select id="task-state" bind:value={selectedTask.state} class="w-full dark:bg-slate-800 bg-muted border border-border text-sm rounded-lg px-3 py-2 outline-none focus:ring-1 focus:ring-primary">
							<option value="open">Open</option>
							<option value="closed">Closed</option>
						</select>
					</div>
				</div>

				<div class="grid grid-cols-2 gap-4">
					<div>
						<label class="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2" for="task-assignee">Responsáveis (Vírgula)</label>
						<input id="task-assignee" type="text" bind:value={selectedTask._assigneesStr} placeholder="user1, user2" class="w-full dark:bg-slate-800 bg-muted border border-border text-sm rounded-lg px-3 py-2 outline-none focus:ring-1 focus:ring-primary" />
					</div>
					<div>
						<label class="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2" for="task-labels">Labels (Vírgula)</label>
						<input id="task-labels" type="text" bind:value={selectedTask._labelsStr} placeholder="bug, ui" class="w-full dark:bg-slate-800 bg-muted border border-border text-sm rounded-lg px-3 py-2 outline-none focus:ring-1 focus:ring-primary" />
					</div>
				</div>
				
				<div class="grid grid-cols-2 gap-4">
					<div>
						<label class="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2" for="task-milestone">Milestone</label>
						<input id="task-milestone" type="text" bind:value={selectedTask.milestone} placeholder="v1.0.0" class="w-full dark:bg-slate-800 bg-muted border border-border text-sm rounded-lg px-3 py-2 outline-none focus:ring-1 focus:ring-primary" />
					</div>
					<div>
						<label class="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2" for="task-repo">Repositório</label>
						<select id="task-repo" bind:value={selectedTask.repository} class="w-full dark:bg-slate-800 bg-muted border border-border text-sm rounded-lg px-3 py-2 outline-none focus:ring-1 focus:ring-primary">
							<option value="">Nenhum</option>
							{#if selectedProject?.repositories}
								{#each selectedProject.repositories as repo}
									<option value={repo}>{repo}</option>
								{/each}
							{/if}
						</select>
					</div>
				</div>

				<div>
					<div class="flex items-center justify-between mb-2">
						<label class="block text-xs font-semibold text-muted-foreground uppercase tracking-wider" for="task-desc">Descrição / Body</label>
						<button class="text-xs text-primary hover:underline font-medium" onclick={() => isMarkdownPreview = !isMarkdownPreview}>
							{isMarkdownPreview ? 'Editar' : 'Visualizar Markdown'}
						</button>
					</div>
					{#if isMarkdownPreview}
						<div class="w-full min-h-[140px] dark:bg-slate-900 bg-white border border-border text-sm rounded-lg p-4 prose prose-sm dark:prose-invert max-w-none" style="overflow-y: auto;">
							<!-- svelte-ignore a11y_hidden -->
							<span aria-hidden="true">{@html DOMPurify.sanitize(marked.parse(selectedTask.description || '') as string)}</span>
						</div>
					{:else}
						<textarea id="task-desc" bind:value={selectedTask.description} rows="6" class="w-full dark:bg-slate-800 bg-muted border border-border text-sm rounded-lg p-3 outline-none focus:ring-1 focus:ring-primary resize-y" placeholder="Adicione mais detalhes a esta task..."></textarea>
					{/if}
				</div>
			</div>

			<div class="p-4 border-t border-border flex justify-between gap-3 bg-muted/30">
				<div>
					<button class="px-4 py-2 text-sm font-medium bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors flex items-center gap-2 disabled:opacity-50" onclick={syncGitHubIssue} disabled={syncInProgress}>
						<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class={syncInProgress ? "animate-spin" : ""}><path d="M21.5 2v6h-6M2.5 22v-6h6M2 11.5a10 10 0 0 1 18.8-4.3M22 12.5a10 10 0 0 1-18.8 4.2"/></svg>
						{syncInProgress ? 'Sincronizando...' : 'Sync Issue'}
					</button>
				</div>
				<div class="flex gap-2">
					<button class="px-4 py-2 text-sm font-medium border border-border rounded-lg hover:bg-muted transition-colors" onclick={closeTaskDrawer}>Cancelar</button>
					<button class="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground rounded-lg hover:opacity-90 transition-opacity" onclick={updateTask}>Salvar</button>
				</div>
			</div>
		</aside>
	</div>
{/if}
