<script lang="ts">
  import { onMount } from 'svelte';
  import { api, getAssetThumbnailUrl, getAssetPreviewUrl } from '../../services/api';
  import { auth } from '../../stores/auth';
  import { toast } from '../../stores/toast';
  import { uploadManager } from '../../services/uploadManager';
  import VideoThumbnail from '../drive/VideoThumbnail.svelte';
  import {
    X,
    Plus,
    Check,
    Search,
    UploadCloud,
    Camera,
    Film,
    FileText,
    Images
  } from 'lucide-svelte';
  import type { Album, FileAsset, AlbumAsset } from '../../types';

  interface Props {
    isOpen: boolean;
    album: Album;
    onClose: () => void;
    onSuccess: () => void;
  }

  let { isOpen, album, onClose, onSuccess }: Props = $props();

  let files = $state<FileAsset[]>([]);
  let existingAssetIds = $state<Set<string>>(new Set());
  let selectedIds = $state<Set<string>>(new Set());
  let loading = $state(true);
  let isSubmitting = $state(false);
  let searchQuery = $state('');
  let activeTab = $state<'library' | 'upload'>('library');
  let fileInputRef = $state<HTMLInputElement>();

  async function loadData() {
    if (!auth.activeWorkspace) return;
    loading = true;
    try {
      const [filesRes, albumAssetsRes] = await Promise.all([
        api.files.list({ workspace_id: auth.activeWorkspace.id }),
        api.albums.getAssets(album.id)
      ]);

      files = filesRes.results || [];
      existingAssetIds = new Set(albumAssetsRes.map(a => a.file_asset.id));
      selectedIds = new Set();
    } catch (err: unknown) {
      toast.error('Failed to load library photos');
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    if (isOpen) {
      loadData();
    }
  });

  $effect(() => {
    if (isOpen) {
      loadData();
    }
  });

  let filteredFiles = $derived.by(() => {
    let list = files.filter(f => !f.is_deleted);
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      list = list.filter(f => f.safe_display_name.toLowerCase().includes(q) || f.original_filename.toLowerCase().includes(q));
    }
    return list;
  });

  function toggleSelect(id: string) {
    if (existingAssetIds.has(id)) return;
    const next = new Set(selectedIds);
    if (next.has(id)) {
      next.delete(id);
    } else {
      next.add(id);
    }
    selectedIds = next;
  }

  function selectAllAvailable() {
    const available = filteredFiles.filter(f => !existingAssetIds.has(f.id));
    if (selectedIds.size === available.length) {
      selectedIds = new Set();
    } else {
      selectedIds = new Set(available.map(f => f.id));
    }
  }

  async function handleAddSelected() {
    if (selectedIds.size === 0) return;
    isSubmitting = true;
    try {
      const res = await api.albums.addAssets(album.id, Array.from(selectedIds));
      toast.success(`Added ${res.added} items to '${album.title}'`);
      onSuccess();
      onClose();
    } catch (err: unknown) {
      toast.error('Failed to add photos to album');
    } finally {
      isSubmitting = false;
    }
  }

  function handleUploadChange(e: Event) {
    const target = e.target as HTMLInputElement;
    if (target.files && target.files.length > 0 && auth.activeWorkspace) {
      const count = target.files.length;
      toast.info(`Uploading ${count} files directly to '${album.title}'...`);
      uploadManager.enqueue(
        target.files,
        auth.activeWorkspace.id,
        null,
        async (asset) => {
          try {
            await api.albums.addAssets(album.id, [asset.id]);
            onSuccess();
          } catch {
            // ignore
          }
        }
      );
      target.value = '';
      onClose();
    }
  }
</script>

{#if isOpen}
  <div class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4">
    <!-- Backdrop -->
    <button
      onclick={onClose}
      class="fixed inset-0 bg-black/60 transition-opacity"
      aria-label="Close dialog"
    ></button>

    <!-- Dialog Body -->
    <div
      role="dialog"
      aria-modal="true"
      class="relative w-full max-w-3xl rounded-lg border border-border bg-card shadow-2xl z-10 flex flex-col max-h-[90vh] text-card-foreground text-xs subtle-fade overflow-hidden"
    >
      <!-- Hidden File Input for Direct Upload -->
      <input
        type="file"
        multiple
        bind:this={fileInputRef}
        onchange={handleUploadChange}
        class="hidden"
        aria-hidden="true"
      />

      <!-- Header -->
      <div class="p-3.5 sm:p-4 border-b border-border flex items-center justify-between shrink-0 bg-muted/20">
        <div class="flex items-center gap-2.5 min-w-0">
          <div class="w-8 h-8 rounded bg-primary/10 text-primary flex items-center justify-center shrink-0">
            <Images size={16} />
          </div>
          <div class="min-w-0">
            <h2 class="font-semibold text-sm text-foreground truncate">
              Add Media to '{album.title}'
            </h2>
            <p class="text-[11px] text-muted-foreground truncate">
              Select existing photos and videos from your drive, or upload new files
            </p>
          </div>
        </div>

        <button
          onclick={onClose}
          class="p-1.5 rounded text-muted-foreground hover:text-foreground hover:bg-muted transition-colors shrink-0"
          aria-label="Close"
        >
          <X size={16} />
        </button>
      </div>

      <!-- Tab Switcher & Search Bar -->
      <div class="p-3 border-b border-border bg-card flex flex-wrap items-center justify-between gap-2.5 shrink-0">
        <div class="flex items-center gap-1 p-0.5 rounded border border-border bg-muted/30">
          <button
            type="button"
            onclick={() => activeTab = 'library'}
            class={`px-3 py-1 rounded text-xs font-medium transition-colors ${
              activeTab === 'library'
                ? 'bg-foreground text-background shadow-xs'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            Drive Library ({files.length})
          </button>
          <button
            type="button"
            onclick={() => fileInputRef?.click()}
            class="px-3 py-1 rounded text-xs font-medium transition-colors text-muted-foreground hover:text-foreground flex items-center gap-1.5"
          >
            <UploadCloud size={13} />
            <span>Upload New Files</span>
          </button>
        </div>

        {#if activeTab === 'library'}
          <div class="flex items-center gap-2 flex-1 max-w-xs min-w-[160px]">
            <div class="relative w-full">
              <Search size={13} class="absolute left-2.5 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
              <input
                type="search"
                bind:value={searchQuery}
                placeholder="Search photos..."
                class="w-full h-7 pl-7 pr-2.5 rounded border border-border bg-background text-foreground text-xs placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
              />
            </div>
          </div>
        {/if}
      </div>

      <!-- Main Library Grid Content -->
      <div class="flex-1 overflow-y-auto p-3 sm:p-4">
        {#if loading}
          <div class="flex flex-col items-center justify-center py-20 text-xs text-muted-foreground gap-3">
            <div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
            <span>Loading workspace files...</span>
          </div>

        {:else if filteredFiles.length === 0}
          <div class="text-center py-16 border border-dashed border-border rounded text-xs text-muted-foreground space-y-3 p-4">
            <Camera size={32} class="mx-auto text-muted-foreground/60" />
            <p class="font-medium text-foreground">No photos or videos found in Drive</p>
            <p>Upload files to your vault first, or upload them directly to this album.</p>
            <button
              type="button"
              onclick={() => fileInputRef?.click()}
              class="inline-flex items-center gap-1.5 h-8 px-3 rounded bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
            >
              <UploadCloud size={14} />
              <span>Upload Directly to Album</span>
            </button>
          </div>

        {:else}
          <div class="flex items-center justify-between pb-2 text-[11px] text-muted-foreground">
            <button
              type="button"
              onclick={selectAllAvailable}
              class="text-primary hover:underline font-medium"
            >
              {selectedIds.size === filteredFiles.filter(f => !existingAssetIds.has(f.id)).length && selectedIds.size > 0
                ? 'Deselect All'
                : 'Select All Available'}
            </button>
            <span>{selectedIds.size} selected for import</span>
          </div>

          <div class="grid grid-cols-2 xs:grid-cols-3 sm:grid-cols-4 md:grid-cols-5 gap-2.5">
            {#each filteredFiles as file (file.id)}
              {@const isExisting = existingAssetIds.has(file.id)}
              {@const isSelected = selectedIds.has(file.id)}
              <div
                role="button"
                tabindex="0"
                onclick={() => toggleSelect(file.id)}
                onkeydown={(e) => { if (e.key === 'Enter') toggleSelect(file.id); }}
                class={`group relative rounded border overflow-hidden aspect-square flex flex-col bg-muted/30 transition-all select-none ${
                  isExisting
                    ? 'opacity-50 cursor-not-allowed border-border/40'
                    : isSelected
                      ? 'border-primary ring-2 ring-primary ring-offset-1 ring-offset-background cursor-pointer'
                      : 'border-border hover:border-foreground/40 cursor-pointer'
                }`}
              >
                <!-- Thumbnail -->
                {#if file.is_image}
                  {@const thumb = getAssetThumbnailUrl(file)}
                  {@const prev = getAssetPreviewUrl(file)}
                  {#if thumb}
                    <img
                      src={thumb}
                      alt={file.safe_display_name}
                      class="w-full h-full object-cover"
                      loading="lazy"
                      onerror={(e) => {
                        const target = e.currentTarget;
                        if (prev && target.src !== prev) {
                          target.src = prev;
                        }
                      }}
                    />
                  {:else}
                    <div class="w-full h-full flex items-center justify-center text-muted-foreground">
                      <Camera size={24} />
                    </div>
                  {/if}
                {:else if file.is_video}
                  {@const vThumb = getAssetThumbnailUrl(file)}
                  {@const vPrev = getAssetPreviewUrl(file)}
                  {#if vThumb}
                    <img
                      src={vThumb}
                      alt={file.safe_display_name}
                      class="w-full h-full object-cover"
                      loading="lazy"
                      onerror={(e) => {
                        const target = e.currentTarget;
                        if (vPrev && target.src !== vPrev) {
                          target.src = vPrev;
                        }
                      }}
                    />
                  {:else if vPrev}
                    <VideoThumbnail src={vPrev} showBadge={false} showPlayOverlay={false} class="w-full h-full object-cover" />
                  {:else}
                    <div class="w-full h-full flex items-center justify-center text-muted-foreground">
                      <Film size={24} />
                    </div>
                  {/if}
                {:else}
                  <div class="w-full h-full flex items-center justify-center text-muted-foreground">
                    <FileText size={24} />
                  </div>
                {/if}

                <!-- Status Overlay Checkbox -->
                {#if isExisting}
                  <div class="absolute inset-0 bg-black/40 flex items-center justify-center text-white text-[10px] font-medium text-center p-1">
                    Already in Album
                  </div>
                {:else}
                  <div
                    class={`absolute top-1.5 left-1.5 w-5 h-5 rounded border transition-colors flex items-center justify-center ${
                      isSelected
                        ? 'bg-primary border-primary text-primary-foreground'
                        : 'bg-black/40 border-white/80 text-transparent group-hover:border-white'
                    }`}
                  >
                    {#if isSelected}
                      <Check size={12} class="stroke-[2.5]" />
                    {/if}
                  </div>
                {/if}

                <!-- Title Tooltip footer -->
                <div class="absolute bottom-0 inset-x-0 bg-black/70 text-white text-[9px] px-1.5 py-0.5 truncate pointer-events-none">
                  {file.safe_display_name}
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </div>

      <!-- Footer Actions -->
      <div class="p-3 sm:p-4 border-t border-border bg-card flex items-center justify-between shrink-0">
        <span class="text-xs text-muted-foreground">
          {selectedIds.size} {selectedIds.size === 1 ? 'item' : 'items'} selected
        </span>

        <div class="flex items-center gap-2">
          <button
            type="button"
            onclick={onClose}
            class="px-3 py-1.5 rounded border border-border bg-background hover:bg-muted text-xs text-foreground transition-colors"
          >
            Cancel
          </button>
          <button
            type="button"
            onclick={handleAddSelected}
            disabled={selectedIds.size === 0 || isSubmitting}
            class="px-4 py-1.5 rounded bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 flex items-center gap-1.5 shadow-sm"
          >
            <Plus size={13} />
            <span>{isSubmitting ? 'Adding...' : `Add to Album (${selectedIds.size})`}</span>
          </button>
        </div>
      </div>
    </div>
  </div>
{/if}
