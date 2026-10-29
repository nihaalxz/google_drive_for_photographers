<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/services/api';
  import { auth } from '$lib/stores/auth';
  import { toast } from '$lib/stores/toast';
  import TopToolbar from '$lib/components/layout/TopToolbar.svelte';
  import {
    Trash2,
    RotateCcw,
    AlertTriangle,
    Folder as FolderIcon,
    Camera,
    Film,
    FileText
  } from 'lucide-svelte';
  import type { Folder, FileAsset } from '$lib/types';

  let folders = $state<Folder[]>([]);
  let files = $state<FileAsset[]>([]);
  let loading = $state(true);

  async function loadTrash() {
    if (!auth.activeWorkspace) return;
    loading = true;
    try {
      const [foldersRes, filesRes] = await Promise.all([
        api.folders.list({ workspace_id: auth.activeWorkspace.id, deleted: true }),
        api.files.list({ workspace_id: auth.activeWorkspace.id, deleted: true })
      ]);
      folders = foldersRes.results || [];
      files = filesRes.results || [];
    } catch (err: unknown) {
      toast.error('Failed to load trash items');
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadTrash();
  });

  async function restoreFile(file: FileAsset) {
    try {
      await api.files.restore(file.id);
      files = files.filter(f => f.id !== file.id);
      toast.success(`Restored '${file.safe_display_name}'`);
    } catch (err: unknown) {
      toast.error('Failed to restore file');
    }
  }

  async function restoreFolder(folder: Folder) {
    try {
      await api.folders.restore(folder.id);
      folders = folders.filter(f => f.id !== folder.id);
      toast.success(`Restored folder '${folder.name}'`);
    } catch (err: unknown) {
      toast.error('Failed to restore folder');
    }
  }

  async function permanentDeleteFile(file: FileAsset) {
    if (!confirm(`Permanently delete '${file.safe_display_name}'? This will remove the file from Backblaze B2 storage forever.`)) return;

    try {
      await api.files.permanentDelete(file.id);
      files = files.filter(f => f.id !== file.id);
      auth.refreshWorkspace();
      toast.success(`Permanently deleted '${file.safe_display_name}'`);
    } catch (err: unknown) {
      toast.error('Failed to permanently delete');
    }
  }

  function formatBytes(bytes: number): string {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }
</script>

<svelte:head>
  <title>Trash — LensVault</title>
</svelte:head>

<TopToolbar />

<div class="h-10 px-6 border-b border-border bg-card/40 flex items-center justify-between shrink-0">
  <div class="flex items-center gap-2 text-xs font-medium text-foreground">
    <Trash2 size={15} />
    <span>Trash & Deleted Assets</span>
  </div>
  <div class="text-[11px] text-muted-foreground font-mono">
    {folders.length + files.length} deleted items
  </div>
</div>

<div class="flex-1 overflow-y-auto p-6 space-y-6">
  {#if loading}
    <div class="flex flex-col items-center justify-center py-24 text-xs text-muted-foreground gap-3">
      <div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
      <span>Loading trash...</span>
    </div>

  {:else if folders.length === 0 && files.length === 0}
    <div class="text-center py-20 border border-dashed border-border rounded text-xs text-muted-foreground space-y-1">
      <p class="font-medium text-foreground">Trash is empty</p>
      <p>Items deleted from your drive or albums will appear here.</p>
    </div>

  {:else}
    <div class="p-3 rounded border border-amber-500/30 bg-amber-500/10 text-xs text-amber-600 dark:text-amber-400 flex items-center gap-2.5">
      <AlertTriangle size={16} class="shrink-0" />
      <span>Items in the trash still count toward your storage quota until permanently deleted.</span>
    </div>

    <div class="rounded border border-border bg-card overflow-hidden text-xs">
      <table class="w-full text-left border-collapse">
        <thead>
          <tr class="border-b border-border bg-muted/40 text-muted-foreground font-medium select-none">
            <th class="px-4 py-3">Item Name</th>
            <th class="px-4 py-3">Type</th>
            <th class="px-4 py-3">Size</th>
            <th class="px-4 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border/60">
          <!-- Deleted Folders -->
          {#each folders as folder (folder.id)}
            <tr class="hover:bg-muted/30 transition-colors">
              <td class="px-4 py-3 font-medium text-foreground">
                <div class="flex items-center gap-2">
                  <FolderIcon size={16} class="text-muted-foreground" />
                  <span>{folder.name}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-muted-foreground">Folder</td>
              <td class="px-4 py-3 text-muted-foreground font-mono">—</td>
              <td class="px-4 py-3 text-right">
                <button
                  onclick={() => restoreFolder(folder)}
                  class="inline-flex items-center gap-1 px-2.5 py-1 rounded border border-border hover:bg-muted text-foreground transition-colors"
                >
                  <RotateCcw size={12} />
                  <span>Restore</span>
                </button>
              </td>
            </tr>
          {/each}

          <!-- Deleted Files -->
          {#each files as file (file.id)}
            <tr class="hover:bg-muted/30 transition-colors">
              <td class="px-4 py-3 font-medium text-foreground">
                <div class="flex items-center gap-2">
                  {#if file.is_image}
                    <Camera size={15} class="text-muted-foreground" />
                  {:else if file.is_video}
                    <Film size={15} class="text-muted-foreground" />
                  {:else}
                    <FileText size={15} class="text-muted-foreground" />
                  {/if}
                  <span class="truncate max-w-xs">{file.safe_display_name}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-muted-foreground uppercase font-mono text-[11px]">
                {file.file_extension}
              </td>
              <td class="px-4 py-3 text-muted-foreground font-mono">
                {formatBytes(file.file_size)}
              </td>
              <td class="px-4 py-3 text-right">
                <div class="inline-flex items-center gap-1.5">
                  <button
                    onclick={() => restoreFile(file)}
                    class="inline-flex items-center gap-1 px-2.5 py-1 rounded border border-border hover:bg-muted text-foreground transition-colors"
                    title="Restore to Drive"
                  >
                    <RotateCcw size={12} />
                    <span>Restore</span>
                  </button>
                  <button
                    onclick={() => permanentDeleteFile(file)}
                    class="inline-flex items-center gap-1 px-2.5 py-1 rounded hover:bg-destructive/10 text-destructive transition-colors"
                    title="Delete permanently from B2"
                  >
                    <Trash2 size={12} />
                    <span>Delete</span>
                  </button>
                </div>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
    </div>
  {/if}
</div>
