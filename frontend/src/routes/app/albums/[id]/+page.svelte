<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { api } from '$lib/services/api';
  import { auth } from '$lib/stores/auth';
  import { toast } from '$lib/stores/toast';
  import { uploadManager } from '$lib/services/uploadManager';
  import TopToolbar from '$lib/components/layout/TopToolbar.svelte';
  import ShareModal from '$lib/components/gallery/ShareModal.svelte';
  import AddPhotosToAlbumModal from '$lib/components/gallery/AddPhotosToAlbumModal.svelte';
  import ImageViewerModal from '$lib/components/viewer/ImageViewerModal.svelte';
  import VideoThumbnail from '$lib/components/drive/VideoThumbnail.svelte';
  import {
    ArrowLeft,
    Images,
    Plus,
    UploadCloud,
    Share2,
    Calendar,
    User,
    Camera,
    Trash2,
    Star,
    MoreVertical,
    Download,
    Eye,
    Check,
    Film,
    FileText
  } from 'lucide-svelte';
  import type { Album, AlbumAsset, FileAsset } from '$lib/types';

  let albumId = $derived(page.params.id);
  let album = $state<Album | null>(null);
  let assets = $state<AlbumAsset[]>([]);
  let loading = $state(true);
  let previewFileId = $state<string | null>(null);

  // Modals
  let isAddPhotosOpen = $state(false);
  let isShareOpen = $state(false);
  let fileInputRef = $state<HTMLInputElement>();

  async function loadAlbumData() {
    if (!albumId) return;
    loading = true;
    try {
      const [albumRes, assetsRes] = await Promise.all([
        api.albums.get(albumId),
        api.albums.getAssets(albumId)
      ]);
      album = albumRes;
      assets = assetsRes;
    } catch (err: unknown) {
      toast.error('Failed to load album details');
      goto('/app/albums');
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadAlbumData();

    function handleAutoRefresh() {
      loadAlbumData();
    }

    window.addEventListener('lensvault:file-uploaded', handleAutoRefresh);
    window.addEventListener('lensvault:uploads-completed', handleAutoRefresh);

    return () => {
      window.removeEventListener('lensvault:file-uploaded', handleAutoRefresh);
      window.removeEventListener('lensvault:uploads-completed', handleAutoRefresh);
    };
  });

  async function handleRemoveAsset(asset: AlbumAsset) {
    if (!album) return;
    try {
      await api.albums.removeAsset(album.id, asset.file_asset.id);
      assets = assets.filter(a => a.id !== asset.id);
      if (album.cover_asset?.id === asset.file_asset.id) {
        album.cover_asset = assets.length > 0 ? assets[0].file_asset : null;
      }
      toast.success(`Removed '${asset.file_asset.safe_display_name}' from album`);
    } catch (err: unknown) {
      toast.error('Failed to remove photo from album');
    }
  }

  async function handleSetCover(asset: AlbumAsset) {
    if (!album) return;
    try {
      const updated = await api.albums.setCover(album.id, asset.file_asset.id);
      album = updated;
      toast.success('Album cover updated');
    } catch (err: unknown) {
      toast.error('Failed to set album cover');
    }
  }

  async function handleDeleteAlbum() {
    if (!album) return;
    if (!confirm(`Are you sure you want to delete the album '${album.title}'? (Photos will remain in your drive)`)) return;
    try {
      await api.albums.delete(album.id);
      toast.success(`Album '${album.title}' deleted`);
      goto('/app/albums');
    } catch (err: unknown) {
      toast.error('Failed to delete album');
    }
  }

  function handleDirectUpload(e: Event) {
    const target = e.target as HTMLInputElement;
    if (target.files && target.files.length > 0 && auth.activeWorkspace && album) {
      const count = target.files.length;
      toast.info(`Uploading ${count} files directly to '${album.title}'...`);
      uploadManager.enqueue(
        target.files,
        auth.activeWorkspace.id,
        null,
        async (newAsset) => {
          if (!album) return;
          try {
            await api.albums.addAssets(album.id, [newAsset.id]);
            loadAlbumData();
          } catch {
            // ignore
          }
        }
      );
      target.value = '';
    }
  }
</script>

<svelte:head>
  <title>{album ? `${album.title} — Album` : 'Album'} — LensVault</title>
</svelte:head>

<TopToolbar />

<!-- Breadcrumb Sub-Header -->
<div class="h-10 px-3 sm:px-6 border-b border-border bg-card/40 flex items-center justify-between shrink-0 text-xs">
  <div class="flex items-center gap-2 min-w-0">
    <a
      href="/app/albums"
      class="inline-flex items-center gap-1 text-muted-foreground hover:text-foreground font-medium transition-colors shrink-0"
    >
      <ArrowLeft size={14} />
      <span>Albums</span>
    </a>
    <span class="text-muted-foreground/60">/</span>
    <span class="font-semibold text-foreground truncate">{album?.title || 'Loading...'}</span>
  </div>

  {#if album}
    <div class="flex items-center gap-2 shrink-0">
      <button
        type="button"
        onclick={() => isShareOpen = true}
        class="inline-flex items-center gap-1.5 h-7 px-2.5 rounded border border-border bg-background hover:bg-muted text-xs font-medium text-foreground transition-colors"
      >
        <Share2 size={13} />
        <span class="hidden xs:inline">Share Gallery</span>
      </button>

      <button
        type="button"
        onclick={() => isAddPhotosOpen = true}
        class="inline-flex items-center gap-1.5 h-7 px-2.5 rounded bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/90 transition-colors shadow-sm"
      >
        <Plus size={13} />
        <span>Add Media</span>
      </button>
    </div>
  {/if}
</div>

<!-- Main Canvas -->
<div class="flex-1 overflow-y-auto p-3 sm:p-6 space-y-4 sm:space-y-6">
  <!-- Hidden File Input for Direct Upload -->
  <input
    type="file"
    multiple
    bind:this={fileInputRef}
    onchange={handleDirectUpload}
    class="hidden"
    aria-hidden="true"
  />

  {#if loading}
    <div class="flex flex-col items-center justify-center py-24 text-xs text-muted-foreground gap-3">
      <div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
      <span>Loading collection assets...</span>
    </div>

  {:else if album}
    <!-- Album Meta Banner Card -->
    <div class="rounded-lg border border-border bg-card p-4 sm:p-5 flex flex-col md:flex-row md:items-center justify-between gap-4 shadow-xs">
      <div class="flex items-start sm:items-center gap-3.5 min-w-0">
        <!-- Cover Thumbnail -->
        <div class="w-14 h-14 sm:w-16 sm:h-16 rounded-md bg-muted/60 overflow-hidden flex items-center justify-center shrink-0 border border-border">
          {#if album.cover_asset && (album.cover_asset.thumbnail_url || album.cover_asset.preview_url)}
            <img
              src={album.cover_asset.thumbnail_url || album.cover_asset.preview_url}
              alt=""
              class="w-full h-full object-cover"
            />
          {:else}
            <Camera size={24} class="text-muted-foreground" />
          {/if}
        </div>

        <div class="min-w-0 space-y-1">
          <div class="flex items-center gap-2 flex-wrap">
            <h1 class="text-base sm:text-lg font-bold text-foreground tracking-tight truncate">
              {album.title}
            </h1>
            <span class="px-2 py-0.5 rounded bg-muted text-[10px] font-mono text-muted-foreground">
              {assets.length} {assets.length === 1 ? 'item' : 'items'}
            </span>
          </div>

          <div class="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-muted-foreground">
            {#if album.client_name}
              <div class="flex items-center gap-1.5">
                <User size={12} />
                <span>Client: <strong class="text-foreground font-medium">{album.client_name}</strong></span>
              </div>
            {/if}
            {#if album.event_date}
              <div class="flex items-center gap-1.5">
                <Calendar size={12} />
                <span>Date: <span class="text-foreground">{album.event_date}</span></span>
              </div>
            {/if}
          </div>

          {#if album.description}
            <p class="text-xs text-muted-foreground pt-0.5 max-w-xl line-clamp-2">
              {album.description}
            </p>
          {/if}
        </div>
      </div>

      <!-- Action Buttons -->
      <div class="flex items-center gap-2 pt-2 md:pt-0 border-t md:border-t-0 border-border shrink-0">
        <button
          type="button"
          onclick={() => fileInputRef?.click()}
          class="inline-flex items-center gap-1.5 h-8 px-3 rounded border border-border bg-background hover:bg-muted text-xs font-medium text-foreground transition-colors"
          title="Upload new photos directly into this album"
        >
          <UploadCloud size={14} />
          <span>Upload Media</span>
        </button>

        <button
          type="button"
          onclick={() => isAddPhotosOpen = true}
          class="inline-flex items-center gap-1.5 h-8 px-3 rounded bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/90 transition-colors shadow-sm"
        >
          <Plus size={14} />
          <span>Select from Drive</span>
        </button>

        <button
          type="button"
          onclick={handleDeleteAlbum}
          class="p-2 rounded border border-border text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
          title="Delete Album"
          aria-label="Delete Album"
        >
          <Trash2 size={14} />
        </button>
      </div>
    </div>

    <!-- Media Grid -->
    {#if assets.length === 0}
      <!-- Empty State -->
      <div class="text-center py-20 border border-dashed border-border rounded-lg text-xs text-muted-foreground space-y-3.5 max-w-md mx-auto p-6">
        <div class="w-12 h-12 rounded-full bg-primary/10 text-primary flex items-center justify-center mx-auto">
          <Images size={24} />
        </div>
        <div class="space-y-1">
          <h2 class="text-sm font-semibold text-foreground">This album has no photos yet</h2>
          <p>Curate photos and videos from your Drive library, or upload master RAW and JPEG files directly to this collection.</p>
        </div>
        <div class="pt-2 flex flex-wrap items-center justify-center gap-2.5">
          <button
            type="button"
            onclick={() => isAddPhotosOpen = true}
            class="inline-flex items-center gap-1.5 h-8 px-3 rounded bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
          >
            <Plus size={14} />
            <span>Select Photos from Drive</span>
          </button>
          <button
            type="button"
            onclick={() => fileInputRef?.click()}
            class="inline-flex items-center gap-1.5 h-8 px-3 rounded border border-border bg-background hover:bg-muted text-foreground font-medium transition-colors"
          >
            <UploadCloud size={14} />
            <span>Upload New Files</span>
          </button>
        </div>
      </div>

    {:else}
      <!-- Photo / Video Grid -->
      <div class="grid grid-cols-2 xs:grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2.5 sm:gap-4">
        {#each assets as asset (asset.id)}
          {@const f = asset.file_asset}
          {@const isCover = album.cover_asset?.id === f.id}
          <div
            role="button"
            tabindex="0"
            onclick={() => previewFileId = f.id}
            onkeydown={(e) => { if (e.key === 'Enter') previewFileId = f.id; }}
            class="group relative rounded border border-border bg-card overflow-hidden text-xs flex flex-col hover:border-foreground/40 transition-all cursor-pointer shadow-xs"
          >
            <!-- Media Preview -->
            <div class="aspect-square bg-muted/60 relative overflow-hidden flex items-center justify-center">
              {#if f.is_image && (f.thumbnail_url || f.preview_url)}
                <img
                  src={f.thumbnail_url || f.preview_url}
                  alt={f.safe_display_name}
                  loading="lazy"
                  decoding="async"
                  class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                />
              {:else if f.is_video && f.thumbnail_url}
                <img
                  src={f.thumbnail_url}
                  alt={f.safe_display_name}
                  loading="lazy"
                  decoding="async"
                  class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                />
              {:else if f.is_video && f.preview_url}
                <VideoThumbnail src={f.preview_url} showBadge={false} showPlayOverlay={false} class="w-full h-full object-cover" />
              {:else if f.is_image}
                <Camera size={28} class="text-muted-foreground" />
              {:else if f.is_video}
                <Film size={28} class="text-muted-foreground" />
              {:else}
                <FileText size={28} class="text-muted-foreground" />
              {/if}

              <!-- Cover Badge -->
              {#if isCover}
                <div class="absolute top-2 left-2 px-1.5 py-0.5 rounded bg-amber-500 text-black font-semibold text-[9px] uppercase tracking-wider shadow-sm flex items-center gap-1">
                  <Star size={10} class="fill-current" />
                  <span>Cover</span>
                </div>
              {/if}

              <!-- Top Right Actions Overlay -->
              <div
                class="absolute top-2 right-2 flex items-center gap-1 opacity-70 sm:opacity-0 sm:group-hover:opacity-100 transition-opacity"
                onclick={(e) => e.stopPropagation()}
              >
                {#if !isCover}
                  <button
                    type="button"
                    onclick={() => handleSetCover(asset)}
                    class="p-1 rounded bg-black/70 hover:bg-black text-white transition-colors"
                    title="Set as Album Cover"
                    aria-label="Set as Album Cover"
                  >
                    <Camera size={13} />
                  </button>
                {/if}
                <button
                  type="button"
                  onclick={() => handleRemoveAsset(asset)}
                  class="p-1 rounded bg-black/70 hover:bg-destructive text-white transition-colors"
                  title="Remove from Album"
                  aria-label="Remove from Album"
                >
                  <Trash2 size={13} />
                </button>
              </div>

              <!-- Camera EXIF Tag Pill -->
              {#if f.camera_model || f.f_stop || f.focal_length}
                <div class="absolute bottom-1.5 left-1.5 right-1.5 flex items-center gap-1 overflow-hidden pointer-events-none">
                  <span class="text-[9px] font-mono px-1.5 py-0.5 rounded bg-black/75 text-white/90 truncate max-w-full">
                    {[f.camera_model, f.f_stop, f.shutter_speed, f.iso ? `ISO ${f.iso}` : ''].filter(Boolean).join(' · ')}
                  </span>
                </div>
              {/if}
            </div>

            <!-- Footer Meta -->
            <div class="p-2 sm:p-2.5 flex items-center justify-between gap-1 border-t border-border/60">
              <span class="font-medium text-foreground text-[11px] truncate" title={f.safe_display_name}>
                {f.safe_display_name}
              </span>
            </div>
          </div>
        {/each}
      </div>
    {/if}
  {/if}
</div>

<!-- Add Photos Modal -->
{#if isAddPhotosOpen && album}
  <AddPhotosToAlbumModal
    isOpen={isAddPhotosOpen}
    album={album}
    onClose={() => isAddPhotosOpen = false}
    onSuccess={() => loadAlbumData()}
  />
{/if}

<!-- Share Modal -->
{#if isShareOpen && album}
  <ShareModal
    isOpen={isShareOpen}
    targetType="ALBUM"
    targetId={album.id}
    targetTitle={album.title}
    onClose={() => isShareOpen = false}
  />
{/if}

<!-- Fullscreen Viewer Modal -->
{#if previewFileId && assets.some(a => a.file_asset.id === previewFileId)}
  <ImageViewerModal
    files={assets.map(a => a.file_asset)}
    activeFileId={previewFileId}
    onClose={() => previewFileId = null}
    onToggleStar={() => {}}
    onTrash={() => {}}
  />
{/if}
