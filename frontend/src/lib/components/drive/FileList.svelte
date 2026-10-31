<script lang="ts">
  import {
    Star,
    MoreVertical,
    Download,
    Trash2,
    Eye,
    Camera,
    Film,
    FileText,
    Check
  } from 'lucide-svelte';
  import type { FileAsset } from '../../types';
  import VideoThumbnail from './VideoThumbnail.svelte';

  interface Props {
    files: FileAsset[];
    selectedIds: Set<string>;
    onSelect: (file: FileAsset, isShift: boolean) => void;
    onSelectAll: () => void;
    onPreview: (file: FileAsset) => void;
    onToggleStar: (file: FileAsset) => void;
    onTrash: (file: FileAsset) => void;
    onDownload: (file: FileAsset) => void;
  }

  let {
    files,
    selectedIds,
    onSelect,
    onSelectAll,
    onPreview,
    onToggleStar,
    onTrash,
    onDownload
  }: Props = $props();

  function formatBytes(bytes: number): string {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  function formatDate(iso: string): string {
    if (!iso) return '';
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
  }

  let allSelected = $derived(files.length > 0 && files.every(f => selectedIds.has(f.id)));
</script>

<div class="w-full border border-border rounded overflow-hidden bg-card text-xs">
  <div class="overflow-x-auto">
    <table class="w-full text-left border-collapse min-w-[360px]">
    <thead>
      <tr class="border-b border-border bg-muted/40 text-muted-foreground font-medium select-none">
        <th class="w-9 px-3 py-2.5">
          <button
            type="button"
            onclick={onSelectAll}
            class={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${
              allSelected
                ? 'bg-foreground border-foreground text-background'
                : 'border-border bg-background'
            }`}
            aria-label="Select all files"
          >
            {#if allSelected}
              <Check size={11} class="stroke-[2.5]" />
            {/if}
          </button>
        </th>
        <th class="w-6 px-1 py-2.5"></th>
        <th class="px-3 py-2.5">File Name</th>
        <th class="px-3 py-2.5 hidden md:table-cell">Camera & Exposure</th>
        <th class="px-3 py-2.5 hidden sm:table-cell">Dimensions</th>
        <th class="px-3 py-2.5">Size</th>
        <th class="px-3 py-2.5 hidden lg:table-cell">Uploaded</th>
        <th class="w-16 px-3 py-2.5 text-right">Actions</th>
      </tr>
    </thead>
    <tbody class="divide-y divide-border/60">
      {#each files as file (file.id)}
        {@const isSelected = selectedIds.has(file.id)}
        <tr
          role="row"
          tabindex="0"
          onclick={() => onPreview(file)}
          onkeydown={(e) => { if (e.key === 'Enter') onPreview(file); }}
          class={`hover:bg-muted/40 transition-colors cursor-pointer select-none ${
            isSelected ? 'bg-muted/60' : ''
          }`}
        >
          <!-- Selection Checkbox -->
          <td class="px-3 py-2.5" onclick={(e) => e.stopPropagation()}>
            <button
              type="button"
              onclick={(e) => onSelect(file, e.shiftKey)}
              class={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${
                isSelected
                  ? 'bg-foreground border-foreground text-background'
                  : 'border-border bg-background hover:border-foreground'
              }`}
              aria-label="Select row"
            >
              {#if isSelected}
                <Check size={11} class="stroke-[2.5]" />
              {/if}
            </button>
          </td>

          <!-- Star Icon -->
          <td class="px-1 py-2.5" onclick={(e) => e.stopPropagation()}>
            <button
              type="button"
              onclick={() => onToggleStar(file)}
              class={`p-0.5 rounded transition-colors ${file.is_starred ? 'text-amber-500' : 'text-muted-foreground/40 hover:text-muted-foreground'}`}
              title={file.is_starred ? 'Unstar' : 'Star'}
            >
              <Star size={13} class={file.is_starred ? 'fill-amber-500' : ''} />
            </button>
          </td>

          <!-- Name & Icon / Mini Thumbnail -->
          <td class="px-3 py-2.5">
            <div class="flex items-center gap-2.5 min-w-0">
              {#if file.is_image && (file.thumbnail_url || file.preview_url)}
                <div class="w-7 h-7 rounded border border-border/80 bg-muted/40 overflow-hidden shrink-0">
                  <img src={file.thumbnail_url || file.preview_url} alt="" class="w-full h-full object-cover" loading="lazy" decoding="async" />
                </div>
              {:else if file.is_video && file.thumbnail_url}
                <div class="w-7 h-7 rounded border border-border/80 bg-muted/40 overflow-hidden shrink-0">
                  <img src={file.thumbnail_url} alt="" class="w-full h-full object-cover" loading="lazy" decoding="async" />
                </div>
              {:else if file.is_video && file.preview_url}
                <div class="w-7 h-7 rounded border border-border/80 bg-muted/40 overflow-hidden shrink-0">
                  <VideoThumbnail src={file.preview_url} showBadge={false} showPlayOverlay={false} class="w-full h-full object-cover" />
                </div>
              {:else if file.is_image}
                <Camera size={15} class="text-muted-foreground shrink-0" />
              {:else if file.is_video}
                <Film size={15} class="text-muted-foreground shrink-0" />
              {:else}
                <FileText size={15} class="text-muted-foreground shrink-0" />
              {/if}
              <span class="font-medium text-foreground truncate max-w-[120px] sm:max-w-xs">{file.safe_display_name}</span>
            </div>
          </td>

          <!-- Camera & Exposure Details -->
          <td class="px-3 py-2.5 text-muted-foreground font-mono text-[11px] hidden md:table-cell truncate max-w-xs">
            {[file.camera_model, file.f_stop, file.shutter_speed, file.iso ? `ISO ${file.iso}` : ''].filter(Boolean).join(' · ') || '—'}
          </td>

          <!-- Dimensions -->
          <td class="px-3 py-2.5 text-muted-foreground hidden sm:table-cell">
            {file.width && file.height ? `${file.width} × ${file.height}` : '—'}
          </td>

          <!-- Size -->
          <td class="px-3 py-2.5 text-muted-foreground font-mono">
            {formatBytes(file.file_size)}
          </td>

          <!-- Date -->
          <td class="px-3 py-2.5 text-muted-foreground hidden lg:table-cell">
            {formatDate(file.created_at)}
          </td>

          <!-- Action Buttons -->
          <td class="px-3 py-2.5 text-right" onclick={(e) => e.stopPropagation()}>
            <div class="inline-flex items-center gap-1">
              <button
                type="button"
                onclick={() => onDownload(file)}
                class="p-1 rounded text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
                title="Download"
              >
                <Download size={14} />
              </button>
              <button
                type="button"
                onclick={() => onTrash(file)}
                class="p-1 rounded text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
                title="Move to Trash"
              >
                <Trash2 size={14} />
              </button>
            </div>
          </td>
        </tr>
      {/each}
    </tbody>
  </table>
  </div>
</div>
