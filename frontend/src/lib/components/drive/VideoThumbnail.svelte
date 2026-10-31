<script lang="ts">
  import { Film, Play } from 'lucide-svelte';

  interface Props {
    src: string;
    alt?: string;
    class?: string;
    showBadge?: boolean;
    showPlayOverlay?: boolean;
  }

  let {
    src,
    alt = '',
    class: className = 'w-full h-full object-cover',
    showBadge = true,
    showPlayOverlay = true
  }: Props = $props();

  // In-memory cache for extracted video frame data URLs
  const getCache = () => {
    const g = globalThis as unknown as { __lensvault_thumb_cache?: Map<string, string> };
    if (!g.__lensvault_thumb_cache) {
      g.__lensvault_thumb_cache = new Map<string, string>();
    }
    return g.__lensvault_thumb_cache;
  };

  const cache = getCache();

  let videoEl = $state<HTMLVideoElement | null>(null);
  let thumbnailDataUrl = $state<string | null>(null);
  let durationFormatted = $state<string | null>(null);
  let hasError = $state(false);
  let isLoaded = $state(false);

  $effect(() => {
    if (src && cache.has(src)) {
      thumbnailDataUrl = cache.get(src) || null;
    }
  });

  function formatDuration(sec: number): string {
    if (!sec || isNaN(sec) || !isFinite(sec)) return '';
    const m = Math.floor(sec / 60);
    const s = Math.floor(sec % 60);
    return `${m}:${s.toString().padStart(2, '0')}`;
  }

  function handleLoadedMetadata() {
    if (videoEl) {
      isLoaded = true;
      if (videoEl.duration) {
        durationFormatted = formatDuration(videoEl.duration);
        const seekTime = Math.min(1.0, videoEl.duration > 0.5 ? videoEl.duration / 4 : 0.1);
        try {
          videoEl.currentTime = seekTime;
        } catch {
          // ignore
        }
      }
    }
  }

  function handleSeeked() {
    if (!videoEl || thumbnailDataUrl) return;
    try {
      const canvas = document.createElement('canvas');
      const w = Math.min(videoEl.videoWidth || 640, 640);
      const h = Math.round((w / (videoEl.videoWidth || 16)) * (videoEl.videoHeight || 9));
      if (w > 0 && h > 0) {
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.drawImage(videoEl, 0, 0, w, h);
          const dataUrl = canvas.toDataURL('image/jpeg', 0.82);
          thumbnailDataUrl = dataUrl;
          if (src) cache.set(src, dataUrl);
        }
      }
    } catch {
      // Cross-origin canvas restriction: <video> element remains visible and directly displays frame
    }
  }

  function handleError() {
    hasError = true;
  }
</script>

<div class="relative w-full h-full bg-zinc-950 overflow-hidden flex items-center justify-center select-none">
  {#if hasError}
    <!-- Fallback if video cannot be loaded -->
    <div class="flex flex-col items-center justify-center text-muted-foreground gap-1.5 p-4 text-center">
      <Film size={28} />
      <span class="text-[10px] uppercase font-semibold tracking-wider">Video</span>
    </div>
  {:else if thumbnailDataUrl}
    <!-- Cached High-Efficiency Image Snapshot -->
    <img
      src={thumbnailDataUrl}
      {alt}
      loading="lazy"
      class={className}
    />
  {:else}
    <!-- Native HTML5 Video Frame Render -->
    <video
      bind:this={videoEl}
      src={`${src}#t=0.5`}
      preload="metadata"
      muted
      playsinline
      class={`${className} pointer-events-none`}
      onloadedmetadata={handleLoadedMetadata}
      onseeked={handleSeeked}
      onerror={handleError}
    >
      <track kind="captions" />
    </video>
  {/if}

  <!-- Play Badge in Corner (with duration if available) -->
  {#if showBadge && !hasError}
    <div class="absolute bottom-2 right-2 px-1.5 py-0.5 rounded bg-black/80 backdrop-blur-xs text-[10px] font-mono font-medium text-white flex items-center gap-1 shadow-sm pointer-events-none z-10 border border-white/10">
      <Play size={9} class="fill-current text-white shrink-0" />
      <span>{durationFormatted || 'VIDEO'}</span>
    </div>
  {/if}

  <!-- Center Hover Play Overlay Button -->
  {#if showPlayOverlay && !hasError}
    <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity duration-200 bg-black/30 pointer-events-none z-10">
      <div class="w-10 h-10 rounded-full bg-black/75 backdrop-blur-sm border border-white/20 flex items-center justify-center text-white shadow-lg transition-transform duration-200 group-hover:scale-110">
        <Play size={15} class="fill-current ml-0.5" />
      </div>
    </div>
  {/if}
</div>
