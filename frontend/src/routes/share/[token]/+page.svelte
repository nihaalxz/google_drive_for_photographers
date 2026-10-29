<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/state';
  import { api } from '$lib/services/api';
  import { toast } from '$lib/stores/toast';
  import ThemeToggle from '$lib/components/layout/ThemeToggle.svelte';
  import ImageViewerModal from '$lib/components/viewer/ImageViewerModal.svelte';
  import {
    Aperture,
    Lock,
    Heart,
    Download,
    Eye,
    Calendar,
    ArrowRight,
    Camera
  } from 'lucide-svelte';
  import type { FileAsset, AlbumAsset } from '$lib/types';
  import VideoThumbnail from '$lib/components/drive/VideoThumbnail.svelte';

  let token = $derived(page.params.token || '');
  let loading = $state(true);
  let requiresPassword = $state(false);
  let passwordInput = $state('');
  let passwordError = $state('');
  let galleryData = $state<any>(null);
  let activeTab = $state<'all' | 'favorites'>('all');
  let previewFileId = $state<string | null>(null);

  async function loadGallery(password?: string) {
    if (!token) return;
    loading = true;
    passwordError = '';
    try {
      const data = await api.sharing.getPublic(token, password);
      galleryData = data;
      requiresPassword = false;
    } catch (err: any) {
      if (err.status === 401) {
        requiresPassword = true;
        if (password) {
          passwordError = 'Incorrect gallery password.';
        }
      } else if (err.status === 410) {
        toast.error('This client gallery link has expired.');
      } else {
        toast.error(err.message || 'Failed to load gallery.');
      }
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadGallery();
  });

  function handlePasswordSubmit(e: Event) {
    e.preventDefault();
    loadGallery(passwordInput);
  }

  async function toggleFavorite(asset: AlbumAsset) {
    if (!token || !galleryData.allow_favorites) return;

    try {
      const res = await api.sharing.submitPublicAction(token, {
        action: 'favorite',
        file_id: asset.file_asset.id
      });
      asset.is_favorite = res.is_favorite ?? !asset.is_favorite;
      if (asset.is_favorite) {
        toast.success('Added to favorites');
      } else {
        toast.info('Removed from favorites');
      }
    } catch (err: any) {
      toast.error('Could not update favorite');
    }
  }

  let displayedAssets = $derived(
    galleryData?.assets
      ? (activeTab === 'favorites' ? galleryData.assets.filter((a: AlbumAsset) => a.is_favorite) : galleryData.assets)
      : []
  );

  let flatFiles = $derived<FileAsset[]>(
    displayedAssets.map((a: AlbumAsset) => a.file_asset)
  );

  let favoriteCount = $derived(
    galleryData?.assets ? galleryData.assets.filter((a: AlbumAsset) => a.is_favorite).length : 0
  );
</script>

<svelte:head>
  <title>{galleryData?.title || 'Client Gallery'} — LensVault</title>
</svelte:head>

<div class="min-h-screen bg-background text-foreground flex flex-col">
  <!-- Top Navigation Header -->
  <header class="h-16 border-b border-border bg-card/80 sticky top-0 z-30 px-6 flex items-center justify-between">
    <div class="flex items-center gap-3">
      <div class="w-8 h-8 rounded bg-foreground text-background flex items-center justify-center">
        <Aperture size={20} class="stroke-[2.2]" />
      </div>
      <div>
        <span class="font-semibold text-sm tracking-tight text-foreground block leading-none">
          {galleryData?.workspace_name || 'LensVault'}
        </span>
        <span class="text-[11px] text-muted-foreground mt-0.5 block leading-none">
          Client Proofing Collection
        </span>
      </div>
    </div>

    <div class="flex items-center gap-3">
      <ThemeToggle />
      {#if galleryData?.allow_downloads}
        <button
          onclick={() => toast.info('Starting batch download for high-resolution images...')}
          class="inline-flex items-center gap-1.5 h-8 px-3 rounded bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/90 transition-colors shadow-sm"
        >
          <Download size={14} />
          <span>Download All</span>
        </button>
      {/if}
    </div>
  </header>

  <!-- Main Content -->
  <main class="flex-1">
    {#if loading}
      <div class="flex flex-col items-center justify-center py-32 text-muted-foreground text-xs gap-3">
        <div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
        <span>Opening secure gallery...</span>
      </div>

    {:else if requiresPassword}
      <!-- Password Protection Screen -->
      <div class="max-w-md mx-auto px-6 py-24 text-center space-y-6">
        <div class="w-12 h-12 rounded-full border border-border bg-card flex items-center justify-center mx-auto text-primary">
          <Lock size={20} />
        </div>
        <div class="space-y-1">
          <h1 class="text-xl font-bold text-foreground">Protected Client Gallery</h1>
          <p class="text-xs text-muted-foreground">
            Please enter the client access password provided by your photographer.
          </p>
        </div>

        <form onsubmit={handlePasswordSubmit} class="p-6 rounded border border-border bg-card space-y-4 text-xs shadow-sm">
          {#if passwordError}
            <div class="p-2.5 rounded bg-destructive/10 border border-destructive/20 text-destructive text-left">
              {passwordError}
            </div>
          {/if}
          <div class="space-y-1.5 text-left">
            <label for="gal-pass" class="font-medium text-foreground block">Password</label>
            <input
              id="gal-pass"
              type="password"
              bind:value={passwordInput}
              required
              autofocus
              placeholder="••••••••"
              class="w-full h-9 px-3 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            />
          </div>
          <button
            type="submit"
            class="w-full h-9 rounded bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
          >
            Unlock Gallery
          </button>
        </form>
      </div>

    {:else if galleryData}
      <!-- Gallery Header -->
      <section class="max-w-6xl mx-auto px-6 pt-12 pb-8">
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-6 border-b border-border pb-6">
          <div class="space-y-2 max-w-2xl">
            <h1 class="text-3xl sm:text-4xl font-bold tracking-tight text-foreground">
              {galleryData.title}
            </h1>
            {#if galleryData.album?.description}
              <p class="text-xs text-muted-foreground leading-relaxed">
                {galleryData.album.description}
              </p>
            {/if}
            <div class="flex items-center gap-3 text-xs text-muted-foreground pt-1">
              {#if galleryData.album?.client_name}
                <span>Prepared for <strong>{galleryData.album.client_name}</strong></span>
                <span>·</span>
              {/if}
              <span>{galleryData.assets?.length || 0} Photographs</span>
            </div>
          </div>

          <!-- Filter Tabs -->
          <div class="flex items-center gap-1 rounded border border-border p-1 bg-card text-xs self-start md:self-auto">
            <button
              onclick={() => activeTab = 'all'}
              class={`px-3 py-1.5 rounded transition-colors font-medium ${
                activeTab === 'all' ? 'bg-foreground text-background' : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              All Photos ({galleryData.assets?.length || 0})
            </button>
            {#if galleryData.allow_favorites}
              <button
                onclick={() => activeTab = 'favorites'}
                class={`flex items-center gap-1.5 px-3 py-1.5 rounded transition-colors font-medium ${
                  activeTab === 'favorites' ? 'bg-foreground text-background' : 'text-muted-foreground hover:text-foreground'
                }`}
              >
                <Heart size={13} class={favoriteCount > 0 ? 'fill-current text-rose-500' : ''} />
                <span>Favorites ({favoriteCount})</span>
              </button>
            {/if}
          </div>
        </div>
      </section>

      <!-- Photos Grid -->
      <section class="max-w-6xl mx-auto px-6 pb-24">
        {#if displayedAssets.length === 0}
          <div class="text-center py-20 border border-dashed border-border rounded text-xs text-muted-foreground space-y-2">
            <p>No photographs found in this view.</p>
            {#if activeTab === 'favorites'}
              <p>Click the heart icon on any photo to add it to your client selection.</p>
            {/if}
          </div>
        {:else}
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {#each displayedAssets as asset (asset.id)}
              {@const file = asset.file_asset}
              <div
                role="button"
                tabindex="0"
                onclick={() => previewFileId = file.id}
                onkeydown={(e) => { if (e.key === 'Enter') previewFileId = file.id; }}
                class="group relative rounded border border-border bg-card overflow-hidden cursor-pointer select-none aspect-[4/3]"
              >
                {#if file.is_image && (file.thumbnail_url || file.preview_url)}
                  <img
                    src={file.thumbnail_url || file.preview_url}
                    alt={file.safe_display_name}
                    loading="lazy"
                    decoding="async"
                    class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                  />
                {:else if file.is_video && file.thumbnail_url}
                  <img
                    src={file.thumbnail_url}
                    alt={file.safe_display_name}
                    loading="lazy"
                    decoding="async"
                    class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                  />
                {:else if file.is_video && file.preview_url}
                  <VideoThumbnail
                    src={file.preview_url}
                    alt={file.safe_display_name}
                    class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                  />
                {:else}
                  <div class="w-full h-full flex flex-col items-center justify-center bg-muted text-muted-foreground">
                    <Camera size={24} />
                    <span class="text-[10px] uppercase font-mono mt-1">{file.file_extension}</span>
                  </div>
                {/if}

                <!-- Hover Overlay with Heart and Download -->
                <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-end justify-between p-3 text-white">
                  <span class="text-xs font-medium truncate max-w-[150px]">
                    {file.safe_display_name}
                  </span>

                  <div class="flex items-center gap-1.5" onclick={(e) => e.stopPropagation()}>
                    {#if galleryData.allow_favorites}
                      <button
                        type="button"
                        onclick={() => toggleFavorite(asset)}
                        class={`p-1.5 rounded-full bg-black/60 hover:bg-black/90 transition-transform hover:scale-110 ${
                          asset.is_favorite ? 'text-rose-500' : 'text-white/80'
                        }`}
                        title={asset.is_favorite ? 'Remove from favorites' : 'Mark as favorite'}
                        aria-label="Toggle favorite"
                      >
                        <Heart size={15} class={asset.is_favorite ? 'fill-rose-500' : ''} />
                      </button>
                    {/if}

                    {#if galleryData.allow_downloads}
                      <a
                        href={file.download_url || '#'}
                        download={file.safe_display_name}
                        class="p-1.5 rounded-full bg-black/60 hover:bg-black/90 text-white/80 transition-transform hover:scale-110"
                        title="Download high-resolution master"
                        aria-label="Download image"
                      >
                        <Download size={15} />
                      </a>
                    {/if}
                  </div>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </section>
    {/if}
  </main>
</div>

<!-- Lightbox Modal -->
{#if previewFileId}
  <ImageViewerModal
    files={flatFiles}
    bind:activeFileId={previewFileId}
    onClose={() => previewFileId = null}
    onToggleStar={() => {}}
    onDownload={(file: FileAsset) => {
      if (file.download_url) {
        window.open(file.download_url, '_blank');
      }
    }}
  />
{/if}
