<script lang="ts">
  import { Folder as FolderIcon, Star, MoreVertical, Trash2, Edit2 } from 'lucide-svelte';
  import type { Folder } from '../../types';

  interface Props {
    folder: Folder;
    onOpen: (folder: Folder) => void;
    onToggleStar: (folder: Folder) => void;
    onTrash: (folder: Folder) => void;
    onRename?: (folder: Folder) => void;
  }

  let { folder, onOpen, onToggleStar, onTrash, onRename }: Props = $props();

  let isMenuOpen = $state(false);
</script>

<div
  role="button"
  tabindex="0"
  onclick={() => onOpen(folder)}
  onkeydown={(e) => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); onOpen(folder); } }}
  class="group relative flex items-center justify-between p-2.5 sm:p-3 rounded border border-border bg-card hover:bg-muted/40 transition-colors cursor-pointer select-none"
>
  <div class="flex items-center gap-2 sm:gap-3 min-w-0">
    <div
      class="w-7 h-7 sm:w-8 sm:h-8 rounded flex items-center justify-center shrink-0 border border-border/80"
      style={`background-color: ${folder.color ? folder.color + '15' : 'hsl(var(--muted))'}; color: ${folder.color || 'hsl(var(--foreground))'}`}
    >
      <FolderIcon size={16} class="fill-current sm:size-[18px]" />
    </div>

    <div class="min-w-0 flex flex-col">
      <span class="text-[11px] sm:text-xs font-medium text-foreground truncate">{folder.name}</span>
      <span class="text-[10px] sm:text-[11px] text-muted-foreground truncate">
        {folder.files_count} {folder.files_count === 1 ? 'file' : 'files'}
        {#if folder.children_count > 0}
          · {folder.children_count} {folder.children_count === 1 ? 'folder' : 'folders'}
        {/if}
      </span>
    </div>
  </div>

  <div class="flex items-center gap-0.5 sm:gap-1 opacity-80 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity shrink-0">
    <button
      type="button"
      onclick={(e) => { e.stopPropagation(); onToggleStar(folder); }}
      class={`p-1 rounded hover:bg-muted text-muted-foreground transition-colors ${folder.is_starred ? 'text-amber-500 opacity-100' : ''}`}
      title={folder.is_starred ? 'Unstar folder' : 'Star folder'}
      aria-label="Star folder"
    >
      <Star size={14} class={folder.is_starred ? 'fill-amber-500' : ''} />
    </button>

    <div class="relative">
      <button
        type="button"
        onclick={(e) => { e.stopPropagation(); isMenuOpen = !isMenuOpen; }}
        class="p-1 rounded hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
        title="More actions"
        aria-label="Folder menu"
      >
        <MoreVertical size={14} />
      </button>

      {#if isMenuOpen}
        <button
          type="button"
          onclick={(e) => { e.stopPropagation(); isMenuOpen = false; }}
          class="fixed inset-0 z-30"
          aria-label="Close menu overlay"
        ></button>
        <div class="absolute right-0 top-full mt-1 w-36 rounded border border-border bg-card p-1 shadow-md z-40 text-xs">
          {#if onRename}
            <button
              type="button"
              onclick={(e) => { e.stopPropagation(); isMenuOpen = false; onRename(folder); }}
              class="w-full flex items-center gap-2 px-2 py-1.5 rounded text-left hover:bg-muted text-foreground transition-colors"
            >
              <Edit2 size={13} />
              <span>Rename</span>
            </button>
          {/if}
          <button
            type="button"
            onclick={(e) => { e.stopPropagation(); isMenuOpen = false; onTrash(folder); }}
            class="w-full flex items-center gap-2 px-2 py-1.5 rounded text-left hover:bg-destructive/10 text-destructive transition-colors"
          >
            <Trash2 size={13} />
            <span>Move to Trash</span>
          </button>
        </div>
      {/if}
    </div>
  </div>
</div>
