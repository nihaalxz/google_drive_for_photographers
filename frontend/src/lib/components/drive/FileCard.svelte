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
    file: FileAsset;
    isSelected: boolean;
    onSelect: (file: FileAsset, isShift: boolean) => void;
    onPreview: (file: FileAsset) => void;
    onToggleStar: (file: FileAsset) => void;
    onTrash: (file: FileAsset) => void;
    onDownload: (file: FileAsset) => void;
  }

  let {
    file,
    isSelected,
    onSelect,
    onPreview,
    onToggleStar,
    onTrash,
    onDownload
  }: Props = $props();

  let isMenuOpen = $state(false);

  function formatBytes(bytes: number): string {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  function handleClick(e: MouseEvent) {
    if (e.shiftKey) {
      onSelect(file, true);
    } else {
      onPreview(file);
    }
  }
</script>

<div
  role="button"
  tabindex="0"
  onclick={handleClick}
  onkeydown={(e) => { if (e.key === 'Enter') onPreview(file); }}
  class={`group relative flex flex-col rounded border transition-all duration-150 select-none overflow-hidden text-left bg-card cursor-pointer
    ${isSelected
      ? 'border-foreground ring-1 ring-foreground shadow-sm'
      : 'border-border hover:border-border/90 hover:bg-muted/30'
    }
  `}
>
  <!-- Thumbnail Container -->
  <div class="relative aspect-[4/3] w-full bg-muted/60 overflow-hidden flex items-center justify-center">
    {#if file.is_image && (file.thumbnail_url || file.preview_url)}
      <img
        src={file.thumbnail_url || file.preview_url}
        alt={file.safe_display_name}
        loading="lazy"
        decoding="async"
        class="w-full h-full object-cover transition-transform duration-200 group-hover:scale-105"
      />
    {:else if file.is_video && file.thumbnail_url}
      <div class="relative w-full h-full">
        <img
          src={file.thumbnail_url}
          alt={file.safe_display_name}
          loading="lazy"
          decoding="async"
          class="w-full h-full object-cover transition-transform duration-200 group-hover:scale-105"
        />
        <div class="absolute inset-0 flex items-center justify-center bg-black/20">
          <div class="p-1.5 rounded-full bg-black/60 text-white backdrop-blur-sm">
            <Film size={18} />
          </div>
        </div>
      </div>
    {:else if file.is_video && file.preview_url}
      <VideoThumbnail
        src={file.preview_url}
        alt={file.safe_display_name}
        class="w-full h-full object-cover transition-transform duration-200 group-hover:scale-105"
      />
    {:else if file.is_video}
      <div class="flex flex-col items-center justify-center text-muted-foreground gap-1.5">
        <Film size={28} />
        <span class="text-[10px] uppercase font-semibold tracking-wider">Video</span>
      </div>
    {:else if file.is_raw}
      <div class="flex flex-col items-center justify-center text-muted-foreground gap-1.5">
        <Camera size={28} class="text-foreground" />
        <span class="text-[10px] font-mono font-bold tracking-widest text-foreground bg-foreground/10 px-1.5 py-0.5 rounded">
          {file.file_extension.toUpperCase()} RAW
        </span>
      </div>
    {:else}
      <div class="flex flex-col items-center justify-center text-muted-foreground gap-1.5">
        <FileText size={28} />
        <span class="text-[10px] uppercase font-medium">{file.file_extension}</span>
      </div>
    {/if}

    <!-- Selection Checkbox -->
    <button
      type="button"
      onclick={(e) => { e.stopPropagation(); onSelect(file, e.shiftKey); }}
      class={`absolute top-2 left-2 w-5 h-5 rounded border transition-colors flex items-center justify-center
        ${isSelected
          ? 'bg-foreground border-foreground text-background'
          : 'bg-card/90 border-border text-transparent opacity-0 group-hover:opacity-100 hover:border-foreground'
        }
      `}
      aria-label="Select file"
    >
      <Check size={12} class={isSelected ? 'stroke-[2.5]' : ''} />
    </button>

    <!-- Star Button Overlay -->
    <button
      type="button"
      onclick={(e) => { e.stopPropagation(); onToggleStar(file); }}
      class={`absolute top-2 right-2 p-1 rounded bg-card/90 border border-border/80 transition-opacity
        ${file.is_starred ? 'opacity-100 text-amber-500' : 'opacity-0 group-hover:opacity-100 text-muted-foreground hover:text-foreground'}
      `}
      title={file.is_starred ? 'Unstar' : 'Star'}
      aria-label="Star file"
    >
      <Star size={13} class={file.is_starred ? 'fill-amber-500' : ''} />
    </button>

    <!-- Camera EXIF Tag Pill (Photographer Centric) -->
    {#if file.camera_model || file.f_stop || file.focal_length}
      <div class="absolute bottom-2 left-2 right-2 flex items-center gap-1 overflow-hidden pointer-events-none">
        <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-black/75 text-white/90 truncate max-w-full">
          {[file.camera_model, file.f_stop, file.shutter_speed, file.iso ? `ISO ${file.iso}` : ''].filter(Boolean).join(' · ')}
        </span>
      </div>
    {/if}
  </div>

  <!-- File Metadata Footer -->
  <div class="p-2.5 flex items-start justify-between gap-2 border-t border-border/60">
    <div class="min-w-0 flex-1 flex flex-col">
      <span class="text-xs font-medium text-foreground truncate" title={file.safe_display_name}>
        {file.safe_display_name}
      </span>
      <div class="flex items-center gap-1.5 text-[11px] text-muted-foreground mt-0.5">
        <span>{formatBytes(file.file_size)}</span>
        {#if file.width && file.height}
          <span>·</span>
          <span>{file.width}×{file.height}</span>
        {/if}
      </div>
    </div>

    <!-- More Actions Menu -->
    <div class="relative">
      <button
        type="button"
        onclick={(e) => { e.stopPropagation(); isMenuOpen = !isMenuOpen; }}
        class="p-1 rounded hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
        title="More actions"
        aria-label="File actions"
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
        <div class="absolute right-0 bottom-full mb-1 w-40 rounded border border-border bg-card p-1 shadow-md z-40 text-xs">
          <button
            type="button"
            onclick={(e) => { e.stopPropagation(); isMenuOpen = false; onPreview(file); }}
            class="w-full flex items-center gap-2 px-2 py-1.5 rounded text-left hover:bg-muted text-foreground transition-colors"
          >
            <Eye size={13} />
            <span>View Full Details</span>
          </button>
          <button
            type="button"
            onclick={(e) => { e.stopPropagation(); isMenuOpen = false; onDownload(file); }}
            class="w-full flex items-center gap-2 px-2 py-1.5 rounded text-left hover:bg-muted text-foreground transition-colors"
          >
            <Download size={13} />
            <span>Download</span>
          </button>
          <div class="my-1 border-t border-border"></div>
          <button
            type="button"
            onclick={(e) => { e.stopPropagation(); isMenuOpen = false; onTrash(file); }}
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
