import tailwindcss from '@tailwindcss/vite';
import adapter from '@sveltejs/adapter-auto';
import { sveltekit } from '@sveltejs/kit/vite';
import { defineConfig } from 'vite';

export default defineConfig({
	plugins: [
		tailwindcss(),
		sveltekit({
			alias: {
				'$lib': 'src/lib',
				'$lib/*': 'src/lib/*'
			},
			compilerOptions: {
				runes: ({ filename }) =>
					filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},
			adapter: adapter()
		})
	],
	server: {
		proxy: {
			'/api': {
				target: 'http://127.0.0.1:8008',
				changeOrigin: true
			},
			'/media': {
				target: 'http://127.0.0.1:8008',
				changeOrigin: true
			}
		}
	}
});
