<script lang="ts">
  import { Star, Download, Trash2, X, Images } from 'lucide-svelte';

  interface Props {
    selectedCount: number;
    onClear: () => void;
    onStar: () => void;
    onTrash: () => void;
    onDownload: () => void;
    onAddToAlbum?: () => void;
  }

  let { selectedCount, onClear, onStar, onTrash, onDownload, onAddToAlbum }: Props = $props();
</script>

{#if selectedCount > 0}
  <div class="fixed bottom-16 sm:bottom-6 left-1/2 -translate-x-1/2 z-40 flex items-center gap-1 sm:gap-2 p-1 sm:p-1.5 px-2.5 sm:px-3 rounded-md border border-border bg-card/95 backdrop-blur-md text-card-foreground shadow-xl text-xs max-w-[calc(100vw-24px)] overflow-x-auto subtle-fade">
    <span class="font-medium text-foreground px-1.5 sm:px-2 border-r border-border shrink-0">
      {selectedCount} <span class="hidden xs:inline">selected</span>
    </span>

    {#if onAddToAlbum}
      <button
        onclick={onAddToAlbum}
        class="flex items-center gap-1 sm:gap-1.5 px-2 sm:px-2.5 py-1.5 rounded hover:bg-muted text-foreground transition-colors shrink-0"
        title="Add selected items to an album"
      >
        <Images size={14} />
        <span class="hidden xs:inline">Album</span>
      </button>
    {/if}

    <button
      onclick={onStar}
      class="flex items-center gap-1 sm:gap-1.5 px-2 sm:px-2.5 py-1.5 rounded hover:bg-muted text-foreground transition-colors shrink-0"
      title="Star selected items"
    >
      <Star size={14} />
      <span class="hidden xs:inline">Star</span>
    </button>

    <button
      onclick={onDownload}
      class="flex items-center gap-1 sm:gap-1.5 px-2 sm:px-2.5 py-1.5 rounded hover:bg-muted text-foreground transition-colors shrink-0"
      title="Download selected items"
    >
      <Download size={14} />
      <span class="hidden xs:inline">Download</span>
    </button>

    <button
      onclick={onTrash}
      class="flex items-center gap-1 sm:gap-1.5 px-2 sm:px-2.5 py-1.5 rounded hover:bg-destructive/10 text-destructive transition-colors shrink-0"
      title="Move selected items to trash"
    >
      <Trash2 size={14} />
      <span class="hidden xs:inline">Trash</span>
    </button>

    <div class="w-px h-4 bg-border my-auto shrink-0"></div>

    <button
      onclick={onClear}
      class="p-1 rounded text-muted-foreground hover:text-foreground transition-colors shrink-0"
      title="Clear selection"
      aria-label="Clear selection"
    >
      <X size={15} />
    </button>
  </div>
{/if}
