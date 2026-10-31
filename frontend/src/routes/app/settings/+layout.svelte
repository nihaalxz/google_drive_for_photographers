<script lang="ts">
  import type { Snippet } from 'svelte';
  import { page } from '$app/state';
  import TopToolbar from '$lib/components/layout/TopToolbar.svelte';
  import { User, Lock, Sliders, Share2 } from 'lucide-svelte';

  let { children }: { children: Snippet } = $props();

  let currentPath = $derived(page.url.pathname);

  const tabs = [
    { label: 'Profile & Studio', href: '/app/settings/profile', icon: User },
    { label: 'Security & Auth', href: '/app/settings/security', icon: Lock },
    { label: 'Preferences & Theme', href: '/app/settings/preferences', icon: Sliders },
    { label: 'Sharing Defaults', href: '/app/settings/sharing', icon: Share2 },
  ];
</script>

<TopToolbar />

<div class="h-10 px-3 sm:px-6 border-b border-border bg-card/40 flex items-center gap-3 sm:gap-6 shrink-0 overflow-x-auto text-xs no-scrollbar">
  {#each tabs as tab}
    {@const active = currentPath === tab.href}
    <a
      href={tab.href}
      class={`flex items-center gap-1.5 h-full border-b-2 px-1 transition-colors font-medium whitespace-nowrap ${
        active
          ? 'border-foreground text-foreground'
          : 'border-transparent text-muted-foreground hover:text-foreground'
      }`}
    >
      <tab.icon size={13} />
      <span>{tab.label}</span>
    </a>
  {/each}
</div>

<div class="flex-1 overflow-y-auto p-3 sm:p-6 max-w-3xl">
  {@render children()}
</div>
