<script lang="ts">
  import {
    Camera,
    Info,
    Calendar,
    HardDrive,
    Maximize2,
    Sliders,
    Download,
    Star
  } from 'lucide-svelte';
  import type { FileAsset } from '../../types';

  interface Props {
    file: FileAsset;
    onDownload: () => void;
    onToggleStar: () => void;
  }

  let { file, onDownload, onToggleStar }: Props = $props();

  function formatBytes(bytes: number): string {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  function formatDate(iso: string | null): string {
    if (!iso) return 'Not recorded';
    const d = new Date(iso);
    return d.toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }

  let megapixels = $derived(
    file.width && file.height ? ((file.width * file.height) / 1000000).toFixed(1) : null
  );
</script>

<div class="w-80 h-full border-l border-border bg-card p-4 overflow-y-auto flex flex-col gap-5 text-xs text-card-foreground select-none">
  <!-- Header Title -->
  <div class="space-y-1">
    <div class="flex items-center justify-between">
      <span class="text-[10px] font-mono font-semibold uppercase tracking-wider text-muted-foreground">
        {file.file_extension} {file.is_raw ? 'RAW Master' : 'Asset'}
      </span>
      <button
        onclick={onToggleStar}
        class={`p-1 rounded transition-colors ${file.is_starred ? 'text-amber-500' : 'text-muted-foreground hover:text-foreground'}`}
        title={file.is_starred ? 'Unstar' : 'Star'}
        aria-label="Star file"
      >
        <Star size={15} class={file.is_starred ? 'fill-amber-500' : ''} />
      </button>
    </div>
    <h3 class="text-sm font-semibold text-foreground break-words leading-snug">
      {file.safe_display_name}
    </h3>
    <p class="text-[11px] font-mono text-muted-foreground truncate">
      {file.original_filename}
    </p>
  </div>

  <!-- Exposure Grid (f-stop, shutter, ISO, focal length) -->
  <div class="rounded border border-border bg-background/50 p-3 space-y-2">
    <div class="flex items-center gap-1.5 text-muted-foreground font-medium mb-1">
      <Sliders size={14} />
      <span>Exposure Parameters</span>
    </div>

    <div class="grid grid-cols-2 gap-2 text-center">
      <div class="p-2 rounded bg-muted/40 border border-border/50">
        <div class="text-[10px] text-muted-foreground uppercase font-mono">Aperture</div>
        <div class="font-mono font-semibold text-foreground text-xs mt-0.5">{file.f_stop || '—'}</div>
      </div>
      <div class="p-2 rounded bg-muted/40 border border-border/50">
        <div class="text-[10px] text-muted-foreground uppercase font-mono">Shutter</div>
        <div class="font-mono font-semibold text-foreground text-xs mt-0.5">{file.shutter_speed || '—'}</div>
      </div>
      <div class="p-2 rounded bg-muted/40 border border-border/50">
        <div class="text-[10px] text-muted-foreground uppercase font-mono">ISO</div>
        <div class="font-mono font-semibold text-foreground text-xs mt-0.5">{file.iso ? `ISO ${file.iso}` : '—'}</div>
      </div>
      <div class="p-2 rounded bg-muted/40 border border-border/50">
        <div class="text-[10px] text-muted-foreground uppercase font-mono">Focal Length</div>
        <div class="font-mono font-semibold text-foreground text-xs mt-0.5">{file.focal_length || '—'}</div>
      </div>
    </div>
  </div>

  <!-- Camera & Optical Hardware -->
  <div class="space-y-2">
    <div class="flex items-center gap-1.5 text-muted-foreground font-medium">
      <Camera size={14} />
      <span>Hardware</span>
    </div>
    <div class="space-y-1.5 text-foreground">
      <div class="flex justify-between py-1 border-b border-border/50">
        <span class="text-muted-foreground">Camera</span>
        <span class="font-medium text-right truncate max-w-[170px]">
          {[file.camera_make, file.camera_model].filter(Boolean).join(' ') || 'Not detected'}
        </span>
      </div>
      <div class="flex justify-between py-1 border-b border-border/50">
        <span class="text-muted-foreground">Lens</span>
        <span class="font-medium text-right truncate max-w-[170px]">
          {file.lens_model || 'Not detected'}
        </span>
      </div>
    </div>
  </div>

  <!-- File Dimensions & Storage Details -->
  <div class="space-y-2">
    <div class="flex items-center gap-1.5 text-muted-foreground font-medium">
      <Maximize2 size={14} />
      <span>Geometry & Storage</span>
    </div>
    <div class="space-y-1.5 text-foreground">
      <div class="flex justify-between py-1 border-b border-border/50">
        <span class="text-muted-foreground">Resolution</span>
        <span class="font-mono font-medium">
          {file.width && file.height ? `${file.width} × ${file.height}` : '—'}
        </span>
      </div>
      {#if megapixels}
        <div class="flex justify-between py-1 border-b border-border/50">
          <span class="text-muted-foreground">Megapixels</span>
          <span class="font-mono font-medium">{megapixels} MP</span>
        </div>
      {/if}
      <div class="flex justify-between py-1 border-b border-border/50">
        <span class="text-muted-foreground">File Size</span>
        <span class="font-mono font-medium">{formatBytes(file.file_size)}</span>
      </div>
      <div class="flex justify-between py-1 border-b border-border/50">
        <span class="text-muted-foreground">Format</span>
        <span class="font-mono uppercase font-medium">{file.file_extension}</span>
      </div>
    </div>
  </div>

  <!-- Dates -->
  <div class="space-y-2">
    <div class="flex items-center gap-1.5 text-muted-foreground font-medium">
      <Calendar size={14} />
      <span>Timestamps</span>
    </div>
    <div class="space-y-1.5 text-foreground">
      <div class="flex justify-between py-1 border-b border-border/50">
        <span class="text-muted-foreground">Captured</span>
        <span class="font-mono text-[11px]">{formatDate(file.date_taken)}</span>
      </div>
      <div class="flex justify-between py-1 border-b border-border/50">
        <span class="text-muted-foreground">Uploaded</span>
        <span class="font-mono text-[11px]">{formatDate(file.created_at)}</span>
      </div>
    </div>
  </div>

  <!-- Download Action Button -->
  <div class="mt-auto pt-4 border-t border-border">
    <button
      onclick={onDownload}
      class="w-full flex items-center justify-center gap-2 h-9 rounded bg-primary text-primary-foreground hover:bg-primary/90 font-medium transition-colors text-xs"
    >
      <Download size={14} />
      <span>Download Original Asset</span>
    </button>
  </div>
</div>
