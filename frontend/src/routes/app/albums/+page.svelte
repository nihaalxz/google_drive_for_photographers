<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/services/api';
  import { auth } from '$lib/stores/auth';
  import { toast } from '$lib/stores/toast';
  import TopToolbar from '$lib/components/layout/TopToolbar.svelte';
  import ShareModal from '$lib/components/gallery/ShareModal.svelte';
  import {
    Images,
    Plus,
    Share2,
    Calendar,
    User,
    Camera,
    X,
    ExternalLink
  } from 'lucide-svelte';
  import type { Album } from '$lib/types';

  let albums = $state<Album[]>([]);
  let loading = $state(true);
  let isCreateOpen = $state(false);

  // New Album Form
  let title = $state('');
  let description = $state('');
  let clientName = $state('');
  let clientEmail = $state('');
  let eventDate = $state('');
  let isSubmitting = $state(false);

  // Share Modal
  let shareModalState = $state<{
    isOpen: boolean;
    targetType: 'ALBUM';
    targetId: string;
    targetTitle: string;
  }>({
    isOpen: false,
    targetType: 'ALBUM',
    targetId: '',
    targetTitle: ''
  });

  async function loadAlbums() {
    if (!auth.activeWorkspace) return;
    loading = true;
    try {
      const res = await api.albums.list({ workspace_id: auth.activeWorkspace.id });
      albums = res.results || [];
    } catch (err: unknown) {
      toast.error('Failed to load albums');
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadAlbums();
  });

  async function handleCreateAlbum(e: Event) {
    e.preventDefault();
    if (!auth.activeWorkspace) return;
    isSubmitting = true;
    try {
      const res = await api.albums.create({
        workspace_id: auth.activeWorkspace.id,
        title,
        description,
        client_name: clientName,
        client_email: clientEmail,
        event_date: eventDate || null
      });
      albums = [res, ...albums];
      isCreateOpen = false;
      title = '';
      description = '';
      clientName = '';
      clientEmail = '';
      eventDate = '';
      toast.success(`Album '${res.title}' created`);
    } catch (err: unknown) {
      toast.error('Failed to create album');
    } finally {
      isSubmitting = false;
    }
  }

  function openShare(album: Album) {
    shareModalState = {
      isOpen: true,
      targetType: 'ALBUM',
      targetId: album.id,
      targetTitle: album.title
    };
  }
</script>

<svelte:head>
  <title>Albums & Client Proofing — LensVault</title>
</svelte:head>

<TopToolbar />

<div class="h-10 px-6 border-b border-border bg-card/40 flex items-center justify-between shrink-0">
  <div class="flex items-center gap-2 text-xs font-medium text-foreground">
    <Images size={15} />
    <span>Client Delivery Albums & Proofing Collections</span>
  </div>
  <button
    onclick={() => isCreateOpen = true}
    class="inline-flex items-center gap-1.5 h-7 px-2.5 rounded bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/90 transition-colors shadow-sm"
  >
    <Plus size={13} />
    <span>New Album</span>
  </button>
</div>

<div class="flex-1 overflow-y-auto p-6">
  {#if loading}
    <div class="flex flex-col items-center justify-center py-24 text-xs text-muted-foreground gap-3">
      <div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
      <span>Loading collections...</span>
    </div>

  {:else if albums.length === 0}
    <div class="text-center py-20 border border-dashed border-border rounded text-xs text-muted-foreground space-y-3 max-w-sm mx-auto">
      <p class="font-medium text-foreground">No albums created yet</p>
      <p>Curate client collections, assign cover photographs, and generate proofing links.</p>
      <button
        onclick={() => isCreateOpen = true}
        class="inline-flex items-center gap-1.5 h-8 px-3 rounded bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
      >
        <Plus size={14} />
        <span>Create First Album</span>
      </button>
    </div>

  {:else}
    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-5">
      {#each albums as album (album.id)}
        <div class="rounded border border-border bg-card overflow-hidden text-xs flex flex-col group hover:border-border/90 transition-all">
          <!-- Cover Image -->
          <div class="aspect-[16/10] bg-muted/60 relative overflow-hidden flex items-center justify-center">
            {#if album.cover_asset && album.cover_asset.preview_url}
              <img
                src={album.cover_asset.preview_url}
                alt={album.title}
                class="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
              />
            {:else}
              <div class="flex flex-col items-center justify-center text-muted-foreground gap-1.5">
                <Camera size={28} />
                <span class="text-[10px] uppercase font-mono">No Cover Photo</span>
              </div>
            {/if}

            <span class="absolute top-2 right-2 px-2 py-0.5 rounded bg-black/75 text-white font-mono text-[10px]">
              {album.photo_count} photos
            </span>
          </div>

          <!-- Album Info -->
          <div class="p-3.5 flex-1 flex flex-col justify-between gap-3">
            <div>
              <h3 class="font-semibold text-foreground text-sm truncate" title={album.title}>
                {album.title}
              </h3>
              {#if album.client_name}
                <div class="flex items-center gap-1.5 text-muted-foreground mt-1">
                  <User size={12} />
                  <span class="truncate">{album.client_name}</span>
                </div>
              {/if}
              {#if album.event_date}
                <div class="flex items-center gap-1.5 text-muted-foreground text-[11px] mt-0.5">
                  <Calendar size={12} />
                  <span>{album.event_date}</span>
                </div>
              {/if}
            </div>

            <!-- Actions Footer -->
            <div class="pt-2 border-t border-border flex items-center justify-between">
              <button
                onclick={() => openShare(album)}
                class="inline-flex items-center gap-1 text-primary hover:underline font-medium"
              >
                <Share2 size={13} />
                <span>Share Gallery</span>
              </button>
            </div>
          </div>
        </div>
      {/each}
    </div>
  {/if}
</div>

<!-- Create Album Modal -->
{#if isCreateOpen}
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <button
      onclick={() => isCreateOpen = false}
      class="fixed inset-0 bg-black/60"
      aria-label="Close modal overlay"
    ></button>

    <div
      role="dialog"
      aria-modal="true"
      class="relative w-full max-w-md rounded border border-border bg-card p-5 shadow-lg text-xs space-y-4 z-10 text-card-foreground subtle-fade"
    >
      <div class="flex items-center justify-between border-b border-border pb-3">
        <h2 class="font-semibold text-sm text-foreground">Create Client Album</h2>
        <button
          onclick={() => isCreateOpen = false}
          class="p-1 rounded text-muted-foreground hover:text-foreground transition-colors"
          aria-label="Close"
        >
          <X size={15} />
        </button>
      </div>

      <form onsubmit={handleCreateAlbum} class="space-y-3">
        <div class="space-y-1">
          <label for="alb-title" class="font-medium text-foreground block">Album Title</label>
          <input
            id="alb-title"
            type="text"
            bind:value={title}
            required
            placeholder="Sarah & James — Lake Como Wedding"
            class="w-full h-8 px-2.5 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          />
        </div>

        <div class="space-y-1">
          <label for="alb-desc" class="font-medium text-foreground block">Description (Optional)</label>
          <textarea
            id="alb-desc"
            bind:value={description}
            rows="2"
            placeholder="Official wedding collection and client delivery proofing."
            class="w-full p-2.5 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          ></textarea>
        </div>

        <div class="grid grid-cols-2 gap-3">
          <div class="space-y-1">
            <label for="alb-cname" class="font-medium text-foreground block">Client Name</label>
            <input
              id="alb-cname"
              type="text"
              bind:value={clientName}
              placeholder="Sarah & James"
              class="w-full h-8 px-2.5 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            />
          </div>
          <div class="space-y-1">
            <label for="alb-edate" class="font-medium text-foreground block">Event Date</label>
            <input
              id="alb-edate"
              type="date"
              bind:value={eventDate}
              class="w-full h-8 px-2.5 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            />
          </div>
        </div>

        <div class="pt-3 border-t border-border flex justify-end gap-2">
          <button
            type="button"
            onclick={() => isCreateOpen = false}
            class="px-3 py-1.5 rounded border border-border bg-background hover:bg-muted text-foreground transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            class="px-4 py-1.5 rounded bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
          >
            {isSubmitting ? 'Creating...' : 'Create Album'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}

{#if shareModalState.isOpen}
  <ShareModal
    isOpen={shareModalState.isOpen}
    targetType="ALBUM"
    targetId={shareModalState.targetId}
    targetTitle={shareModalState.targetTitle}
    onClose={() => shareModalState = { ...shareModalState, isOpen: false }}
  />
{/if}
