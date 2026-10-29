<script lang="ts">
  import { Star, Download, Trash2, X } from 'lucide-svelte';

  interface Props {
    selectedCount: number;
    onClear: () => void;
    onStar: () => void;
    onTrash: () => void;
    onDownload: () => void;
  }

  let { selectedCount, onClear, onStar, onTrash, onDownload }: Props = $props();
</script>

{#if selectedCount > 0}
  <div class="fixed bottom-6 left-1/2 -translate-x-1/2 z-40 flex items-center gap-2 p-1.5 px-3 rounded-md border border-border bg-card text-card-foreground shadow-lg text-xs subtle-fade">
    <span class="font-medium text-foreground px-2 border-r border-border">
      {selectedCount} selected
    </span>

    <button
      onclick={onStar}
      class="flex items-center gap-1.5 px-2.5 py-1.5 rounded hover:bg-muted text-foreground transition-colors"
      title="Star selected items"
    >
      <Star size={14} />
      <span>Star</span>
    </button>

    <button
      onclick={onDownload}
      class="flex items-center gap-1.5 px-2.5 py-1.5 rounded hover:bg-muted text-foreground transition-colors"
      title="Download selected items"
    >
      <Download size={14} />
      <span>Download</span>
    </button>

    <button
      onclick={onTrash}
      class="flex items-center gap-1.5 px-2.5 py-1.5 rounded hover:bg-destructive/10 text-destructive transition-colors"
      title="Move selected items to trash"
    >
      <Trash2 size={14} />
      <span>Trash</span>
    </button>

    <div class="w-px h-4 bg-border my-auto"></div>

    <button
      onclick={onClear}
      class="p-1 rounded text-muted-foreground hover:text-foreground transition-colors"
      title="Clear selection"
      aria-label="Clear selection"
    >
      <X size={15} />
    </button>
  </div>
{/if}
