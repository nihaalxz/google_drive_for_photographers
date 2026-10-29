<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/services/api';
  import { auth } from '$lib/stores/auth';
  import { toast } from '$lib/stores/toast';
  import { uploadManager } from '$lib/services/uploadManager';
  import TopToolbar from '$lib/components/layout/TopToolbar.svelte';
  import Breadcrumbs from '$lib/components/drive/Breadcrumbs.svelte';
  import FolderCard from '$lib/components/drive/FolderCard.svelte';
  import FileCard from '$lib/components/drive/FileCard.svelte';
  import FileList from '$lib/components/drive/FileList.svelte';
  import BulkActionToolbar from '$lib/components/drive/BulkActionToolbar.svelte';
  import CreateFolderDialog from '$lib/components/drive/CreateFolderDialog.svelte';
  import ImageViewerModal from '$lib/components/viewer/ImageViewerModal.svelte';
  import ShareModal from '$lib/components/gallery/ShareModal.svelte';
  import {
    Folder as FolderIcon,
    HardDrive,
    UploadCloud,
    FolderPlus,
    SearchX,
    Star,
    Trash2
  } from 'lucide-svelte';
  import type { Folder, FileAsset, Breadcrumb } from '$lib/types';

  let currentFolderId = $state<string | null>(null);
  let breadcrumbs = $state<Breadcrumb[]>([]);
  let folders = $state<Folder[]>([]);
  let files = $state<FileAsset[]>([]);
  let loading = $state(true);

  // View & Filter states
  let searchQuery = $state('');
  let viewMode = $state<'grid' | 'list'>('grid');
  let sortBy = $state('created_at');
  let sortDirection = $state<'asc' | 'desc'>('desc');

  let sortedFolders = $derived.by(() => {
    return [...folders].sort((a, b) => {
      if (sortBy === 'name') {
        const cmp = a.name.localeCompare(b.name);
        return sortDirection === 'asc' ? cmp : -cmp;
      }
      const dateA = new Date(a.updated_at || a.created_at).getTime();
      const dateB = new Date(b.updated_at || b.created_at).getTime();
      return sortDirection === 'asc' ? dateA - dateB : dateB - dateA;
    });
  });

  // Selection states
  let selectedFileIds = $state<Set<string>>(new Set());

  // Modals
  let isCreateFolderOpen = $state(false);
  let previewFileId = $state<string | null>(null);
  let shareModalState = $state<{
    isOpen: boolean;
    targetType: 'ALBUM' | 'FOLDER' | 'FILE';
    targetId: string;
    targetTitle: string;
  }>({
    isOpen: false,
    targetType: 'FOLDER',
    targetId: '',
    targetTitle: ''
  });

  let fileInputRef = $state<HTMLInputElement>();

  async function loadData() {
    if (!auth.initialized) {
      await auth.init();
    }
    if (!auth.activeWorkspace) {
      loading = false;
      return;
    }
    loading = true;
    try {
      const [foldersRes, filesRes] = await Promise.all([
        api.folders.list({
          workspace_id: auth.activeWorkspace.id,
          parent_id: currentFolderId,
          q: searchQuery
        }),
        api.files.list({
          workspace_id: auth.activeWorkspace.id,
          folder_id: currentFolderId,
          q: searchQuery,
          sort_by: sortBy,
          sort_direction: sortDirection
        })
      ]);

      folders = foldersRes.results || [];
      files = filesRes.results || [];

      if (currentFolderId) {
        const cur = await api.folders.get(currentFolderId);
        breadcrumbs = cur.breadcrumbs || [];
      } else {
        breadcrumbs = [];
      }
    } catch (err: unknown) {
      toast.error('Failed to load drive items');
    } finally {
      loading = false;
    }
  }

  onMount(async () => {
    await loadData();
  });

  $effect(() => {
    const wsId = auth.activeWorkspace?.id;
    const folderId = currentFolderId;
    const q = searchQuery;
    const sort = sortBy;
    const dir = sortDirection;
    if (wsId) {
      loadData();
    }
  });

  function handleFolderNavigate(folderId: string | null) {
    currentFolderId = folderId;
    selectedFileIds = new Set();
    loadData();
  }

  function handleFileSelect(file: FileAsset, isShift: boolean) {
    const next = new Set(selectedFileIds);
    if (next.has(file.id)) {
      next.delete(file.id);
    } else {
      next.add(file.id);
    }
    selectedFileIds = next;
  }

  function handleSelectAll() {
    if (files.length > 0 && files.every(f => selectedFileIds.has(f.id))) {
      selectedFileIds = new Set();
    } else {
      selectedFileIds = new Set(files.map(f => f.id));
    }
  }

  async function handleToggleFileStar(file: FileAsset) {
    try {
      const res = await api.files.toggleStar(file.id);
      file.is_starred = res.is_starred;
      toast.info(file.is_starred ? 'Starred file' : 'Unstarred file');
    } catch (err: unknown) {
      toast.error('Failed to update star status');
    }
  }

  async function handleToggleFolderStar(folder: Folder) {
    try {
      const res = await api.folders.toggleStar(folder.id);
      folder.is_starred = res.is_starred;
      toast.info(folder.is_starred ? 'Starred folder' : 'Unstarred folder');
    } catch (err: unknown) {
      toast.error('Failed to update star status');
    }
  }

  async function handleTrashFile(file: FileAsset) {
    try {
      await api.files.trash(file.id);
      files = files.filter(f => f.id !== file.id);
      selectedFileIds.delete(file.id);
      selectedFileIds = new Set(selectedFileIds);
      toast.success(`Moved '${file.safe_display_name}' to trash`);
    } catch (err: unknown) {
      toast.error('Failed to move to trash');
    }
  }

  async function handleTrashFolder(folder: Folder) {
    try {
      await api.folders.trash(folder.id);
      folders = folders.filter(f => f.id !== folder.id);
      toast.success(`Moved folder '${folder.name}' to trash`);
    } catch (err: unknown) {
      toast.error('Failed to move folder to trash');
    }
  }

  function handleDownloadFile(file: FileAsset) {
    if (file.download_url) {
      window.open(file.download_url, '_blank');
    } else {
      toast.error('Download URL not ready.');
    }
  }

  async function handleCreateFolder(name: string, color: string) {
    if (!auth.activeWorkspace) return;
    const res = await api.folders.create({
      workspace_id: auth.activeWorkspace.id,
      name,
      parent: currentFolderId,
      color
    });
    folders = [res, ...folders];
    toast.success(`Folder '${name}' created`);
  }

  function handleFileInputChange(e: Event) {
    const target = e.target as HTMLInputElement;
    if (target.files && target.files.length > 0 && auth.activeWorkspace) {
      uploadManager.enqueue(target.files, auth.activeWorkspace.id, currentFolderId, (newAsset) => {
        files = [newAsset, ...files];
        auth.refreshWorkspace();
      });
      target.value = '';
    }
  }

  // Bulk operations
  async function handleBulkTrash() {
    const ids = Array.from(selectedFileIds);
    try {
      await api.files.bulkAction({ action: 'trash', file_ids: ids });
      files = files.filter(f => !selectedFileIds.has(f.id));
      selectedFileIds = new Set();
      toast.success(`Moved ${ids.length} items to trash`);
    } catch (err: unknown) {
      toast.error('Failed bulk trash operation');
    }
  }

  async function handleBulkStar() {
    const ids = Array.from(selectedFileIds);
    try {
      await api.files.bulkAction({ action: 'star', file_ids: ids });
      for (const f of files) {
        if (selectedFileIds.has(f.id)) f.is_starred = true;
      }
      selectedFileIds = new Set();
      toast.success(`Starred ${ids.length} items`);
    } catch (err: unknown) {
      toast.error('Failed bulk star operation');
    }
  }

  function handleBulkDownload() {
    const ids = Array.from(selectedFileIds);
    toast.info(`Preparing download bundle for ${ids.length} files...`);
    for (const id of ids) {
      const f = files.find(item => item.id === id);
      if (f && f.download_url) {
        window.open(f.download_url, '_blank');
      }
    }
  }
</script>

<svelte:head>
  <title>My Drive — LensVault</title>
</svelte:head>

<!-- Hidden File Input for Toolbar Upload Button -->
<input
  type="file"
  multiple
  bind:this={fileInputRef}
  onchange={handleFileInputChange}
  class="hidden"
  aria-hidden="true"
/>

<!-- Top Toolbar -->
<TopToolbar
  bind:searchQuery
  bind:viewMode
  bind:sortBy
  bind:sortDirection
  onSearchChange={() => loadData()}
  onSortChange={() => loadData()}
  onNewFolderClick={() => isCreateFolderOpen = true}
  onUploadClick={() => fileInputRef?.click()}
/>

<!-- Sub-header Breadcrumb Bar -->
<div class="h-10 px-6 border-b border-border bg-card/40 flex items-center justify-between shrink-0">
  <Breadcrumbs crumbs={breadcrumbs} onNavigate={handleFolderNavigate} />
  <div class="text-[11px] text-muted-foreground font-mono">
    {folders.length} {folders.length === 1 ? 'folder' : 'folders'} · {files.length} {files.length === 1 ? 'file' : 'files'}
  </div>
</div>

<!-- Main Drive Canvas -->
<div class="flex-1 overflow-y-auto p-6 space-y-6">
  {#if loading}
    <div class="flex flex-col items-center justify-center py-24 text-xs text-muted-foreground gap-3">
      <div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
      <span>Loading library assets...</span>
    </div>

  {:else if folders.length === 0 && files.length === 0}
    <!-- Empty Drive State -->
    <div class="flex flex-col items-center justify-center py-20 border border-dashed border-border rounded-md p-8 text-center max-w-lg mx-auto space-y-4">
      <div class="w-12 h-12 rounded-full bg-muted border border-border flex items-center justify-center text-muted-foreground">
        <HardDrive size={24} />
      </div>
      <div>
        <h3 class="text-sm font-semibold text-foreground">This Folder is Empty</h3>
        <p class="text-xs text-muted-foreground mt-1 max-w-sm">
          Drag and drop photographs here, or use the actions below to create folders and upload raw assets directly to Backblaze B2.
        </p>
      </div>
      <div class="flex items-center gap-2 pt-2">
        <button
          onclick={() => isCreateFolderOpen = true}
          class="inline-flex items-center gap-1.5 h-8 px-3 rounded border border-border bg-card hover:bg-muted text-xs text-foreground font-medium transition-colors"
        >
          <FolderPlus size={14} />
          <span>New Folder</span>
        </button>
        <button
          onclick={() => fileInputRef?.click()}
          class="inline-flex items-center gap-1.5 h-8 px-3 rounded bg-primary text-primary-foreground text-xs font-medium hover:bg-primary/90 transition-colors shadow-sm"
        >
          <UploadCloud size={14} />
          <span>Upload Files</span>
        </button>
      </div>
    </div>

  {:else}
    <!-- Folders Section -->
    {#if sortedFolders.length > 0}
      <section class="space-y-2.5">
        <h2 class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
          Folders
        </h2>
        {#if viewMode === 'grid'}
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
            {#each sortedFolders as folder (folder.id)}
              <FolderCard
                {folder}
                onOpen={(f) => handleFolderNavigate(f.id)}
                onToggleStar={handleToggleFolderStar}
                onTrash={handleTrashFolder}
              />
            {/each}
          </div>
        {:else}
          <div class="rounded border border-border bg-card overflow-hidden divide-y divide-border text-xs">
            {#each sortedFolders as folder (folder.id)}
              <div
                class="flex items-center justify-between px-3.5 py-2.5 hover:bg-muted/50 transition-colors cursor-pointer group"
                onclick={() => handleFolderNavigate(folder.id)}
                onkeydown={(e) => e.key === 'Enter' && handleFolderNavigate(folder.id)}
                role="button"
                tabindex="0"
              >
                <div class="flex items-center gap-3 min-w-0">
                  <div
                    class="w-7 h-7 rounded flex items-center justify-center shrink-0"
                    style={`background-color: ${folder.color ? folder.color + '20' : '#3b82f620'}; color: ${folder.color || '#3b82f6'};`}
                  >
                    <FolderIcon size={16} />
                  </div>
                  <span class="font-medium text-foreground truncate">{folder.name}</span>
                </div>

                <div class="flex items-center gap-4 text-muted-foreground shrink-0">
                  <span class="text-[11px] font-mono">
                    {folder.files_count} {folder.files_count === 1 ? 'file' : 'files'}{folder.children_count > 0 ? ` · ${folder.children_count} ${folder.children_count === 1 ? 'folder' : 'folders'}` : ''}
                  </span>
                  <div class="flex items-center gap-1" onclick={(e) => e.stopPropagation()} role="toolbar" tabindex="0" onkeydown={(e) => e.stopPropagation()}>
                    <button
                      onclick={() => handleToggleFolderStar(folder)}
                      class="p-1.5 rounded hover:bg-muted text-muted-foreground hover:text-foreground transition-colors"
                      title={folder.is_starred ? 'Starred' : 'Star folder'}
                      aria-label="Toggle folder star"
                    >
                      <Star size={14} class={folder.is_starred ? 'fill-amber-400 text-amber-400' : ''} />
                    </button>
                    <button
                      onclick={() => handleTrashFolder(folder)}
                      class="p-1.5 rounded hover:bg-muted text-muted-foreground hover:text-destructive transition-colors"
                      title="Move to trash"
                      aria-label="Move folder to trash"
                    >
                      <Trash2 size={14} />
                    </button>
                  </div>
                </div>
              </div>
            {/each}
          </div>
        {/if}
      </section>
    {/if}

    <!-- Files Section -->
    {#if files.length > 0}
      <section class="space-y-2.5 pt-2">
        <div class="flex items-center justify-between">
          <h2 class="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
            Photographs & Media
          </h2>
          <button
            onclick={handleSelectAll}
            class="text-[11px] text-muted-foreground hover:text-foreground font-medium"
          >
            {files.every(f => selectedFileIds.has(f.id)) ? 'Deselect All' : 'Select All'}
          </button>
        </div>

        {#if viewMode === 'grid'}
          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
            {#each files as file (file.id)}
              <FileCard
                {file}
                isSelected={selectedFileIds.has(file.id)}
                onSelect={handleFileSelect}
                onPreview={(f) => previewFileId = f.id}
                onToggleStar={handleToggleFileStar}
                onTrash={handleTrashFile}
                onDownload={handleDownloadFile}
              />
            {/each}
          </div>
        {:else}
          <FileList
            {files}
            selectedIds={selectedFileIds}
            onSelect={handleFileSelect}
            onSelectAll={handleSelectAll}
            onPreview={(f) => previewFileId = f.id}
            onToggleStar={handleToggleFileStar}
            onTrash={handleTrashFile}
            onDownload={handleDownloadFile}
          />
        {/if}
      </section>
    {/if}
  {/if}
</div>

<!-- Bulk Action Toolbar -->
<BulkActionToolbar
  selectedCount={selectedFileIds.size}
  onClear={() => selectedFileIds = new Set()}
  onStar={handleBulkStar}
  onTrash={handleBulkTrash}
  onDownload={handleBulkDownload}
/>

<!-- Dialogs & Lightbox Modals -->
<CreateFolderDialog
  isOpen={isCreateFolderOpen}
  onClose={() => isCreateFolderOpen = false}
  onSubmit={handleCreateFolder}
/>

{#if previewFileId}
  <ImageViewerModal
    {files}
    bind:activeFileId={previewFileId}
    onClose={() => previewFileId = null}
    onToggleStar={handleToggleFileStar}
    onDownload={handleDownloadFile}
  />
{/if}

{#if shareModalState.isOpen}
  <ShareModal
    isOpen={shareModalState.isOpen}
    targetType={shareModalState.targetType}
    targetId={shareModalState.targetId}
    targetTitle={shareModalState.targetTitle}
    onClose={() => shareModalState = { ...shareModalState, isOpen: false }}
  />
{/if}
