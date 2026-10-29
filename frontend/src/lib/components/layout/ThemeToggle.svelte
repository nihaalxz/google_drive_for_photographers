<script lang="ts">
  import { onMount } from 'svelte';
  import { theme } from '../../stores/theme';
  import { Sun, Moon } from 'lucide-svelte';

  let isDark = $state(false);

  function syncThemeState() {
    if (typeof document !== 'undefined') {
      isDark = document.documentElement.classList.contains('dark');
    }
  }

  onMount(() => {
    syncThemeState();
    const unsubscribe = theme.subscribe(() => {
      syncThemeState();
    });
    return unsubscribe;
  });

  function handleToggle() {
    theme.toggle();
    syncThemeState();
  }
</script>

<button
  onclick={handleToggle}
  class="relative inline-flex items-center justify-center w-8 h-8 rounded border border-border bg-card text-foreground hover:bg-muted transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring shrink-0"
  title={isDark ? "Switch to Light Theme" : "Switch to Dark Theme"}
  aria-label="Toggle between dark and light theme"
>
  {#if isDark}
    <Sun size={15} class="text-amber-400 stroke-[2.2]" />
  {:else}
    <Moon size={15} class="text-foreground stroke-[2.2]" />
  {/if}
</button>
