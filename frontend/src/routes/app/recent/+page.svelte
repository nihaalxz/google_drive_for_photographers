<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/services/api';
  import { auth } from '$lib/stores/auth';
  import { toast } from '$lib/stores/toast';
  import TopToolbar from '$lib/components/layout/TopToolbar.svelte';
  import FileCard from '$lib/components/drive/FileCard.svelte';
  import FileList from '$lib/components/drive/FileList.svelte';
  import ImageViewerModal from '$lib/components/viewer/ImageViewerModal.svelte';
  import { Clock } from 'lucide-svelte';
  import type { FileAsset } from '$lib/types';

  let files = $state<FileAsset[]>([]);
  let loading = $state(true);
  let viewMode = $state<'grid' | 'list'>('grid');
  let selectedFileIds = $state<Set<string>>(new Set());
  let previewFileId = $state<string | null>(null);

  async function loadRecent() {
    if (!auth.initialized) {
      await auth.init();
    }
    if (!auth.activeWorkspace) {
      loading = false;
      return;
    }
    loading = true;
    try {
      const res = await api.files.list({
        workspace_id: auth.activeWorkspace.id,
        sort_by: 'created_at',
        sort_direction: 'desc'
      });
      files = res.results || [];
    } catch (err: unknown) {
      toast.error('Failed to load recent files');
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadRecent();

    function handleAutoRefresh() {
      loadRecent();
      auth.refreshWorkspace();
    }

    window.addEventListener('lensvault:file-uploaded', handleAutoRefresh);
    window.addEventListener('lensvault:uploads-completed', handleAutoRefresh);

    return () => {
      window.removeEventListener('lensvault:file-uploaded', handleAutoRefresh);
      window.removeEventListener('lensvault:uploads-completed', handleAutoRefresh);
    };
  });
</script>

<svelte:head>
  <title>Recent Files — LensVault</title>
</svelte:head>

<TopToolbar bind:viewMode />

<div class="h-10 px-3 sm:px-6 border-b border-border bg-card/40 flex items-center justify-between gap-2 shrink-0">
  <div class="flex items-center gap-2 text-xs font-medium text-foreground truncate min-w-0">
    <Clock size={15} class="shrink-0" />
    <span class="truncate">Recently Uploaded & Modified</span>
  </div>
  <div class="text-[11px] text-muted-foreground font-mono shrink-0">
    {files.length} items
  </div>
</div>

<div class="flex-1 overflow-y-auto p-3 sm:p-6">
  {#if loading}
    <div class="flex flex-col items-center justify-center py-24 text-xs text-muted-foreground gap-3">
      <div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
      <span>Loading recent assets...</span>
    </div>
  {:else if files.length === 0}
    <div class="text-center py-20 border border-dashed border-border rounded text-xs text-muted-foreground">
      No recent files found. Upload media to see it here.
    </div>
  {:else}
    {#if viewMode === 'grid'}
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
              const res = await api.files.toggleStar(f.id);
              f.is_starred = res.is_starred;
            }}
            onTrash={async (f) => {
              await api.files.trash(f.id);
              files = files.filter(item => item.id !== f.id);
              toast.success('Moved to trash');
            }}
            onDownload={(f) => {
              if (f.download_url) window.open(f.download_url, '_blank');
            }}
          />
        {/each}
      </div>
    {:else}
      <FileList
        {files}
        selectedIds={selectedFileIds}
        onSelect={(f) => {
          if (selectedFileIds.has(f.id)) selectedFileIds.delete(f.id);
          else selectedFileIds.add(f.id);
          selectedFileIds = new Set(selectedFileIds);
        }}
        onSelectAll={() => {
          if (files.every(f => selectedFileIds.has(f.id))) selectedFileIds = new Set();
          else selectedFileIds = new Set(files.map(f => f.id));
        }}
        onPreview={(f) => previewFileId = f.id}
        onToggleStar={async (f) => {
          const res = await api.files.toggleStar(f.id);
          f.is_starred = res.is_starred;
        }}
        onTrash={async (f) => {
          await api.files.trash(f.id);
          files = files.filter(item => item.id !== f.id);
          toast.success('Moved to trash');
        }}
        onDownload={(f) => {
          if (f.download_url) window.open(f.download_url, '_blank');
        }}
      />
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
