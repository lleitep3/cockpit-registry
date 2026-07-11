import { defineConfig } from 'vite';
import { sveltekit } from '@sveltejs/vite-plugin-svelte';

export default defineConfig({
	plugins: [sveltekit()],
	server: {
		host: '0.0.0.0',
		port: 3000,
		watch: {
			usePolling: true, // necessário para hot-reload dentro do container
		},
	},
});
