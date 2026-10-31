<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/services/api';
  import { auth } from '$lib/stores/auth';
  import { toast } from '$lib/stores/toast';
  import TopToolbar from '$lib/components/layout/TopToolbar.svelte';
  import FolderCard from '$lib/components/drive/FolderCard.svelte';
  import FileCard from '$lib/components/drive/FileCard.svelte';
  import ImageViewerModal from '$lib/components/viewer/ImageViewerModal.svelte';
  import { Star } from 'lucide-svelte';
  import type { Folder, FileAsset } from '$lib/types';

  let folders = $state<Folder[]>([]);
  let files = $state<FileAsset[]>([]);
  let loading = $state(true);
  let selectedFileIds = $state<Set<string>>(new Set());
  let previewFileId = $state<string | null>(null);

  async function loadStarred() {
    if (!auth.activeWorkspace) return;
    loading = true;
    try {
      const [foldersRes, filesRes] = await Promise.all([
        api.folders.list({ workspace_id: auth.activeWorkspace.id, starred: true }),
        api.files.list({ workspace_id: auth.activeWorkspace.id, starred: true })
      ]);
      folders = foldersRes.results || [];
      files = filesRes.results || [];
    } catch (err: unknown) {
      toast.error('Failed to load starred items');
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadStarred();
  });
</script>

<svelte:head>
  <title>Starred Items — LensVault</title>
</svelte:head>

<TopToolbar />

<div class="h-10 px-3 sm:px-6 border-b border-border bg-card/40 flex items-center justify-between gap-2 shrink-0">
  <div class="flex items-center gap-2 text-xs font-medium text-foreground truncate min-w-0">
    <Star size={15} class="text-amber-500 fill-amber-500 shrink-0" />
    <span class="truncate">Starred Items</span>
  </div>
  <div class="text-[11px] text-muted-foreground font-mono shrink-0">
    {folders.length + files.length} starred
  </div>
</div>

<div class="flex-1 overflow-y-auto p-3 sm:p-6 space-y-4 sm:space-y-6">
  {#if loading}
    <div class="flex flex-col items-center justify-center py-24 text-xs text-muted-foreground gap-3">
      <div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
      <span>Loading starred items...</span>
    </div>

  {:else if folders.length === 0 && files.length === 0}
    <div class="text-center py-20 border border-dashed border-border rounded text-xs text-muted-foreground space-y-1">
      <p class="font-medium text-foreground">No starred items</p>
      <p>Star important photographs or folders to access them quickly here.</p>
    </div>

  {:else}
    {#if folders.length > 0}
      <section class="space-y-2.5">
        <h2 class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Starred Folders
        </h2>
        <div class="grid grid-cols-2 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-2.5 sm:gap-3">
          {#each folders as folder (folder.id)}
            <FolderCard
              {folder}
              onOpen={() => window.location.href = `/app`}
              onToggleStar={async (f) => {
                await api.folders.toggleStar(f.id);
                folders = folders.filter(item => item.id !== f.id);
                toast.info('Removed from starred');
              }}
              onTrash={async (f) => {
                await api.folders.trash(f.id);
                folders = folders.filter(item => item.id !== f.id);
              }}
            />
          {/each}
        </div>
      </section>
    {/if}

    {#if files.length > 0}
      <section class="space-y-2.5">
        <h2 class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Starred Photographs
        </h2>
        <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-2.5 sm:gap-4">
          {#each files as file (file.id)}
            <FileCard
              {file}
              isSelected={selectedFileIds.has(file.id)}
              onSelect={(f) => {
                if (selectedFileIds.has(f.id)) selectedFileIds.delete(f.id);
                else selectedFileIds.add(f.id);
                selectedFileIds = new Set(selectedFileIds);
              }}
              onPreview={(f) => previewFileId = f.id}
              onToggleStar={async (f) => {
                await api.files.toggleStar(f.id);
                files = files.filter(item => item.id !== f.id);
                toast.info('Removed from starred');
              }}
              onTrash={async (f) => {
                await api.files.trash(f.id);
                files = files.filter(item => item.id !== f.id);
              }}
              onDownload={(f) => {
                if (f.download_url) window.open(f.download_url, '_blank');
              }}
            />
          {/each}
        </div>
      </section>
    {/if}
  {/if}
</div>

{#if previewFileId}
  <ImageViewerModal
    {files}
    bind:activeFileId={previewFileId}
    onClose={() => previewFileId = null}
    onToggleStar={() => {}}
    onDownload={(f) => { if (f.download_url) window.open(f.download_url, '_blank'); }}
  />
{/if}
