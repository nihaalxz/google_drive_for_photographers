<script lang="ts">
  import { theme, type Theme } from '$lib/stores/theme';
  import { toast } from '$lib/stores/toast';
  import { Sun, Moon, Laptop, Check } from 'lucide-svelte';

  let currentTheme = $state<Theme>('system');

  theme.subscribe(v => {
    currentTheme = v;
  });

  function selectTheme(t: Theme) {
    theme.set(t);
    toast.info(`Theme set to ${t} mode`);
  }
</script>

<svelte:head>
  <title>Preferences & Theme — LensVault</title>
</svelte:head>

<div class="space-y-6 text-xs text-card-foreground">
  <div class="space-y-1">
    <h2 class="text-base font-semibold text-foreground">Interface Appearance</h2>
    <p class="text-muted-foreground">Select your preferred color theme. Optimized for photographic color grading and studio environments.</p>
  </div>

  <div class="p-6 rounded border border-border bg-card space-y-4 shadow-sm">
    <span class="font-medium text-foreground block">Color Theme</span>

    <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
      <!-- Light Mode Option -->
      <button
        type="button"
        onclick={() => selectTheme('light')}
        class={`p-4 rounded border text-left transition-all flex flex-col justify-between gap-3 ${
          currentTheme === 'light'
            ? 'border-foreground ring-1 ring-foreground bg-muted/30'
            : 'border-border hover:border-foreground/50 bg-background'
        }`}
      >
        <div class="flex items-center justify-between">
          <Sun size={18} class="text-foreground" />
          {#if currentTheme === 'light'}
            <Check size={14} class="text-foreground" />
          {/if}
        </div>
        <div>
          <div class="font-semibold text-foreground">Light Theme</div>
          <div class="text-[11px] text-muted-foreground mt-0.5">High-contrast neutral white</div>
        </div>
      </button>

      <!-- Dark Mode Option -->
      <button
        type="button"
        onclick={() => selectTheme('dark')}
        class={`p-4 rounded border text-left transition-all flex flex-col justify-between gap-3 ${
          currentTheme === 'dark'
            ? 'border-foreground ring-1 ring-foreground bg-muted/30'
            : 'border-border hover:border-foreground/50 bg-background'
        }`}
      >
        <div class="flex items-center justify-between">
          <Moon size={18} class="text-foreground" />
          {#if currentTheme === 'dark'}
            <Check size={14} class="text-foreground" />
          {/if}
        </div>
        <div>
          <div class="font-semibold text-foreground">Dark Theme</div>
          <div class="text-[11px] text-muted-foreground mt-0.5">Deep charcoal studio surface</div>
        </div>
      </button>

      <!-- System Option -->
      <button
        type="button"
        onclick={() => selectTheme('system')}
        class={`p-4 rounded border text-left transition-all flex flex-col justify-between gap-3 ${
          currentTheme === 'system'
            ? 'border-foreground ring-1 ring-foreground bg-muted/30'
            : 'border-border hover:border-foreground/50 bg-background'
        }`}
      >
        <div class="flex items-center justify-between">
          <Laptop size={18} class="text-foreground" />
          {#if currentTheme === 'system'}
            <Check size={14} class="text-foreground" />
          {/if}
        </div>
        <div>
          <div class="font-semibold text-foreground">System Default</div>
          <div class="text-[11px] text-muted-foreground mt-0.5">Sync with operating system</div>
        </div>
      </button>
    </div>
  </div>
</div>
