<script lang="ts">
  import { onMount } from 'svelte';
  import ExifDetailPanel from './ExifDetailPanel.svelte';
  import {
    X,
    ChevronLeft,
    ChevronRight,
    Download,
    Star,
    Info,
    Camera,
    ZoomIn,
    ZoomOut,
    Maximize2
  } from 'lucide-svelte';
  import type { FileAsset } from '../../types';

  interface Props {
    files: FileAsset[];
    activeFileId: string | null;
    onClose: () => void;
    onToggleStar: (file: FileAsset) => void;
    onDownload: (file: FileAsset) => void;
  }

  let { files, activeFileId = $bindable(null), onClose, onToggleStar, onDownload }: Props = $props();

  let showInfoPanel = $state(true);
  let zoomLevel = $state(1);

  let currentIndex = $derived(
    files.findIndex(f => f.id === activeFileId)
  );

  let activeFile = $derived(
    currentIndex >= 0 ? files[currentIndex] : null
  );

  function prev() {
    if (currentIndex > 0) {
      activeFileId = files[currentIndex - 1].id;
      zoomLevel = 1;
    }
  }

  function next() {
    if (currentIndex < files.length - 1) {
      activeFileId = files[currentIndex + 1].id;
      zoomLevel = 1;
    }
  }

  function handleKeydown(e: KeyboardEvent) {
    if (e.key === 'Escape') {
      onClose();
    } else if (e.key === 'ArrowLeft') {
      prev();
    } else if (e.key === 'ArrowRight') {
      next();
    } else if (e.key === 'i' || e.key === 'I') {
      showInfoPanel = !showInfoPanel;
    }
  }

  function toggleZoom() {
    zoomLevel = zoomLevel === 1 ? 2 : 1;
  }
</script>

<svelte:window onkeydown={handleKeydown} />

{#if activeFile}
  <div
    role="dialog"
    aria-modal="true"
    aria-label="Image previewer"
    class="fixed inset-0 z-50 bg-black/95 flex flex-col select-none overflow-hidden text-white"
  >
    <!-- Top Bar -->
    <header class="h-14 px-4 border-b border-white/10 flex items-center justify-between z-10 shrink-0 bg-black/50">
      <div class="flex items-center gap-3 min-w-0">
        <span class="text-xs font-medium text-white truncate max-w-sm">
          {activeFile.safe_display_name}
        </span>
        <span class="text-[11px] text-white/50 font-mono">
          ({currentIndex + 1} of {files.length})
        </span>
      </div>

      <div class="flex items-center gap-2">
        <button
          onclick={toggleZoom}
          class="p-2 rounded hover:bg-white/10 text-white/80 hover:text-white transition-colors"
          title={zoomLevel === 1 ? 'Zoom in (200%)' : 'Zoom out (100%)'}
          aria-label="Toggle zoom"
        >
          {#if zoomLevel === 1}
            <ZoomIn size={18} />
          {:else}
            <ZoomOut size={18} />
          {/if}
        </button>

        <button
          onclick={() => onToggleStar(activeFile)}
          class={`p-2 rounded hover:bg-white/10 transition-colors ${activeFile.is_starred ? 'text-amber-400' : 'text-white/80 hover:text-white'}`}
          title={activeFile.is_starred ? 'Unstar' : 'Star'}
          aria-label="Star photo"
        >
          <Star size={18} class={activeFile.is_starred ? 'fill-amber-400' : ''} />
        </button>

        <button
          onclick={() => onDownload(activeFile)}
          class="p-2 rounded hover:bg-white/10 text-white/80 hover:text-white transition-colors"
          title="Download original"
          aria-label="Download photo"
        >
          <Download size={18} />
        </button>

        <button
          onclick={() => showInfoPanel = !showInfoPanel}
          class={`p-2 rounded hover:bg-white/10 transition-colors ${showInfoPanel ? 'bg-white/15 text-white' : 'text-white/80 hover:text-white'}`}
          title="Toggle EXIF Metadata Panel (I)"
          aria-label="Toggle info panel"
        >
          <Info size={18} />
        </button>

        <div class="h-4 w-px bg-white/20 mx-1"></div>

        <button
          onclick={onClose}
          class="p-2 rounded hover:bg-white/10 text-white/80 hover:text-white transition-colors"
          title="Close (Esc)"
          aria-label="Close viewer"
        >
          <X size={20} />
        </button>
      </div>
    </header>

    <!-- Main Viewport Area -->
    <div class="flex-1 flex overflow-hidden relative">
      <!-- Media Canvas -->
      <div class="flex-1 flex items-center justify-center p-4 relative overflow-auto">
        <!-- Previous Button -->
        {#if currentIndex > 0}
          <button
            onclick={prev}
            class="absolute left-4 top-1/2 -translate-y-1/2 p-3 rounded-full bg-black/60 hover:bg-black/90 text-white border border-white/20 shadow-lg transition-transform hover:scale-105 z-20"
            title="Previous photograph (Left Arrow)"
            aria-label="Previous photo"
          >
            <ChevronLeft size={24} />
          </button>
        {/if}

        <!-- Next Button -->
        {#if currentIndex < files.length - 1}
          <button
            onclick={next}
            class="absolute right-4 top-1/2 -translate-y-1/2 p-3 rounded-full bg-black/60 hover:bg-black/90 text-white border border-white/20 shadow-lg transition-transform hover:scale-105 z-20"
            title="Next photograph (Right Arrow)"
            aria-label="Next photo"
          >
            <ChevronRight size={24} />
          </button>
        {/if}

        <!-- Content Display -->
        <div class="max-w-full max-h-full flex items-center justify-center">
          {#if activeFile.is_image && activeFile.preview_url}
            <img
              src={activeFile.preview_url}
              alt={activeFile.safe_display_name}
              class="max-w-full max-h-[calc(100vh-80px)] object-contain transition-transform duration-200 select-none"
              style={`transform: scale(${zoomLevel});`}
            />
          {:else if activeFile.is_video && activeFile.preview_url}
            <video
              src={activeFile.preview_url}
              controls
              autoplay
              class="max-w-full max-h-[calc(100vh-80px)] rounded"
            >
              <track kind="captions" />
            </video>
          {:else if activeFile.is_raw}
            <!-- RAW Master Preview Card -->
            <div class="p-8 rounded border border-white/20 bg-zinc-900 text-center max-w-md space-y-4 shadow-2xl">
              <div class="w-16 h-16 rounded-full bg-zinc-800 border border-white/15 flex items-center justify-center mx-auto text-white">
                <Camera size={32} />
              </div>
              <div>
                <h4 class="text-base font-semibold text-white">{activeFile.safe_display_name}</h4>
                <p class="text-xs text-zinc-400 mt-1">
                  Camera RAW File ({activeFile.file_extension.toUpperCase()})
                </p>
              </div>
              <p class="text-xs text-zinc-300 leading-relaxed">
                RAW formats retain uncompressed sensor data for Lightroom and Capture One. Full-resolution raw bytes are safely stored in your Backblaze B2 bucket.
              </p>
              <button
                onclick={() => onDownload(activeFile)}
                class="inline-flex items-center gap-2 px-4 py-2 rounded bg-white text-zinc-900 font-medium text-xs hover:bg-zinc-200 transition-colors shadow-sm"
              >
                <Download size={14} />
                <span>Download RAW File</span>
              </button>
            </div>
          {:else}
            <div class="p-8 rounded border border-white/20 bg-zinc-900 text-center max-w-sm">
              <p class="text-sm font-medium text-white">{activeFile.safe_display_name}</p>
              <p class="text-xs text-zinc-400 mt-1">Preview not available for this format</p>
            </div>
          {/if}
        </div>
      </div>

      <!-- Collapsible EXIF Inspector Side Panel -->
      {#if showInfoPanel}
        <ExifDetailPanel
          file={activeFile}
          onDownload={() => onDownload(activeFile)}
          onToggleStar={() => onToggleStar(activeFile)}
        />
      {/if}
    </div>
  </div>
{/if}
