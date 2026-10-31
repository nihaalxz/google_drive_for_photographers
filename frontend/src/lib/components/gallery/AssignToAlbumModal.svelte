<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '../../services/api';
  import { auth } from '../../stores/auth';
  import { toast } from '../../stores/toast';
  import {
    X,
    Plus,
    Images,
    Check,
    Calendar,
    User,
    Camera,
    PlusCircle
  } from 'lucide-svelte';
  import type { Album } from '../../types';

  interface Props {
    isOpen: boolean;
    fileIds: string[];
    onClose: () => void;
    onSuccess: () => void;
  }

  let { isOpen, fileIds, onClose, onSuccess }: Props = $props();

  let albums = $state<Album[]>([]);
  let loading = $state(true);
  let isSubmitting = $state(false);
  let selectedAlbumId = $state<string | null>(null);

  // Quick create new album
  let isCreatingNew = $state(false);
  let newTitle = $state('');
  let newClientName = $state('');

  async function loadAlbums() {
    if (!auth.activeWorkspace) return;
    loading = true;
    try {
      const res = await api.albums.list({ workspace_id: auth.activeWorkspace.id });
      albums = res.results || [];
      if (albums.length > 0 && !selectedAlbumId) {
        selectedAlbumId = albums[0].id;
      }
    } catch (err: unknown) {
      toast.error('Failed to load albums');
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    if (isOpen) {
      loadAlbums();
    }
  });

  $effect(() => {
    if (isOpen) {
      loadAlbums();
    }
  });

  async function handleAssign() {
    if (!selectedAlbumId || fileIds.length === 0) return;
    isSubmitting = true;
    try {
      const targetAlbum = albums.find(a => a.id === selectedAlbumId);
      const res = await api.albums.addAssets(selectedAlbumId, fileIds);
      toast.success(`Added ${res.added} items to '${targetAlbum?.title || 'album'}'`);
      onSuccess();
      onClose();
    } catch (err: unknown) {
      toast.error('Failed to add items to album');
    } finally {
      isSubmitting = false;
    }
  }

  async function handleCreateAndAssign(e: Event) {
    e.preventDefault();
    if (!auth.activeWorkspace || !newTitle.trim()) return;
    isSubmitting = true;
    try {
      const newAlbum = await api.albums.create({
        workspace_id: auth.activeWorkspace.id,
        title: newTitle.trim(),
        client_name: newClientName.trim()
      });
      const res = await api.albums.addAssets(newAlbum.id, fileIds);
      toast.success(`Created '${newAlbum.title}' with ${res.added} items`);
      newTitle = '';
      newClientName = '';
      isCreatingNew = false;
      onSuccess();
      onClose();
    } catch (err: unknown) {
      toast.error('Failed to create album and add items');
    } finally {
      isSubmitting = false;
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

    <!-- Dialog -->
    <div
      role="dialog"
      aria-modal="true"
      class="relative w-full max-w-md rounded-lg border border-border bg-card shadow-2xl z-10 flex flex-col max-h-[90vh] text-card-foreground text-xs subtle-fade overflow-hidden"
    >
      <!-- Header -->
      <div class="p-3.5 sm:p-4 border-b border-border flex items-center justify-between shrink-0 bg-muted/20">
        <div class="flex items-center gap-2 font-semibold text-sm text-foreground">
          <Images size={16} />
          <h2>Add {fileIds.length} {fileIds.length === 1 ? 'Item' : 'Items'} to Album</h2>
        </div>
        <button
          onclick={onClose}
          class="p-1.5 rounded text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
          aria-label="Close"
        >
          <X size={16} />
        </button>
      </div>

      {#if isCreatingNew}
        <!-- Create New Album Form -->
        <form onsubmit={handleCreateAndAssign} class="p-4 space-y-3.5 overflow-y-auto">
          <div class="space-y-1">
            <label for="new-alb-title" class="font-medium text-foreground block">New Album Title</label>
            <input
              id="new-alb-title"
              type="text"
              bind:value={newTitle}
              required
              placeholder="e.g. Sarah & James — Lake Como"
              class="w-full h-8 px-2.5 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
              autofocus
            />
          </div>

          <div class="space-y-1">
            <label for="new-alb-cname" class="font-medium text-foreground block">Client Name (Optional)</label>
            <input
              id="new-alb-cname"
              type="text"
              bind:value={newClientName}
              placeholder="Sarah & James"
              class="w-full h-8 px-2.5 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            />
          </div>

          <div class="pt-2 border-t border-border flex items-center justify-between">
            <button
              type="button"
              onclick={() => isCreatingNew = false}
              class="text-xs text-muted-foreground hover:underline"
            >
              ← Back to existing albums
            </button>
            <button
              type="submit"
              disabled={isSubmitting || !newTitle.trim()}
              class="px-4 py-1.5 rounded bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
            >
              {isSubmitting ? 'Creating...' : 'Create & Add Photos'}
            </button>
          </div>
        </form>

      {:else}
        <!-- Select Existing Album List -->
        <div class="flex-1 overflow-y-auto p-4 space-y-3">
          <div class="flex items-center justify-between">
            <span class="font-medium text-foreground">Select Destination Album:</span>
            <button
              type="button"
              onclick={() => isCreatingNew = true}
              class="inline-flex items-center gap-1 text-primary hover:underline font-medium text-[11px]"
            >
              <Plus size={12} />
              <span>Create New Album</span>
            </button>
          </div>

          {#if loading}
            <div class="flex flex-col items-center justify-center py-12 text-xs text-muted-foreground gap-2">
              <div class="w-5 h-5 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
              <span>Loading collections...</span>
            </div>

          {:else if albums.length === 0}
            <div class="text-center py-10 border border-dashed border-border rounded text-xs text-muted-foreground space-y-3 p-3">
              <p>No albums created yet in this workspace.</p>
              <button
                type="button"
                onclick={() => isCreatingNew = true}
                class="inline-flex items-center gap-1.5 h-8 px-3 rounded bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
              >
                <Plus size={13} />
                <span>Create First Album</span>
              </button>
            </div>

          {:else}
            <div class="space-y-1.5">
              {#each albums as album (album.id)}
                {@const isSelected = selectedAlbumId === album.id}
                <button
                  type="button"
                  onclick={() => selectedAlbumId = album.id}
                  class={`w-full flex items-center justify-between p-2.5 rounded border text-left transition-all ${
                    isSelected
                      ? 'border-primary ring-1 ring-primary bg-primary/5'
                      : 'border-border hover:border-foreground/40 bg-background'
                  }`}
                >
                  <div class="flex items-center gap-2.5 min-w-0">
                    <div class="w-9 h-9 rounded bg-muted/60 overflow-hidden flex items-center justify-center shrink-0 border border-border/80">
                      {#if album.cover_asset && (album.cover_asset.thumbnail_url || album.cover_asset.preview_url)}
                        <img
                          src={album.cover_asset.thumbnail_url || album.cover_asset.preview_url}
                          alt=""
                          class="w-full h-full object-cover"
                        />
                      {:else}
                        <Camera size={16} class="text-muted-foreground" />
                      {/if}
                    </div>

                    <div class="min-w-0">
                      <span class="font-medium text-foreground block truncate">
                        {album.title}
                      </span>
                      <span class="text-[11px] text-muted-foreground truncate block">
                        {album.photo_count} photos {#if album.client_name}· {album.client_name}{/if}
                      </span>
                    </div>
                  </div>

                  {#if isSelected}
                    <div class="w-5 h-5 rounded-full bg-primary text-primary-foreground flex items-center justify-center shrink-0">
                      <Check size={12} class="stroke-[3]" />
                    </div>
                  {/if}
                </button>
              {/each}
            </div>
          {/if}
        </div>

        <!-- Footer -->
        <div class="p-3.5 sm:p-4 border-t border-border bg-card flex items-center justify-end gap-2 shrink-0">
          <button
            type="button"
            onclick={onClose}
            class="px-3 py-1.5 rounded border border-border bg-background hover:bg-muted text-xs text-foreground transition-colors"
          >
            Cancel
          </button>
          <button
            type="button"
            onclick={handleAssign}
            disabled={!selectedAlbumId || isSubmitting}
            class="px-4 py-1.5 rounded bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/90 transition-colors disabled:opacity-50 flex items-center gap-1.5 shadow-sm"
          >
            <Plus size={13} />
            <span>{isSubmitting ? 'Adding...' : 'Add to Album'}</span>
          </button>
        </div>
      {/if}
    </div>
  </div>
{/if}
