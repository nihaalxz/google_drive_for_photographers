<script lang="ts">
  import { HardDrive, ChevronRight } from 'lucide-svelte';
  import type { Breadcrumb } from '../../types';

  interface Props {
    crumbs: Breadcrumb[];
    onNavigate: (folderId: string | null) => void;
  }

  let { crumbs, onNavigate }: Props = $props();
</script>

<nav class="flex items-center gap-1.5 text-xs text-muted-foreground select-none" aria-label="Breadcrumb navigation">
  <button
    onclick={() => onNavigate(null)}
    class="flex items-center gap-1 hover:text-foreground transition-colors p-1 rounded focus:outline-none focus:ring-1 focus:ring-ring"
  >
    <HardDrive size={14} />
    <span>My Drive</span>
  </button>

  {#each crumbs as crumb, idx}
    <ChevronRight size={13} class="text-muted-foreground/60 shrink-0" />
    {#if idx === crumbs.length - 1}
      <span class="font-medium text-foreground truncate max-w-[200px]" aria-current="page">
        {crumb.name}
      </span>
    {:else}
      <button
        onclick={() => onNavigate(crumb.id)}
        class="hover:text-foreground transition-colors truncate max-w-[150px] p-1 rounded focus:outline-none focus:ring-1 focus:ring-ring"
      >
        {crumb.name}
      </button>
    {/if}
  {/each}
</nav>
