<script lang="ts">
  import { uploadManager } from '../../services/uploadManager';
  import { auth } from '../../stores/auth';
  import {
    UploadCloud,
    X,
    ChevronDown,
    ChevronUp,
    RotateCw,
    CheckCircle2,
    AlertCircle,
    XCircle,
    Trash2
  } from 'lucide-svelte';
  import type { UploadQueueItem } from '../../types';

  let uploadState = $state({
    items: [] as UploadQueueItem[],
    isOpen: false,
    activeCount: 0,
    totalProgress: 0
  });

  let isMinimized = $state(false);

  uploadManager.subscribe(s => {
    uploadState = s;
  });

  function formatBytes(bytes: number): string {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }
</script>

{#if uploadState.isOpen && uploadState.items.length > 0}
  <div class="fixed bottom-16 inset-x-3 sm:inset-x-auto sm:right-4 sm:bottom-4 sm:w-96 max-w-md z-50 rounded-md border border-border bg-card text-card-foreground shadow-2xl overflow-hidden text-xs subtle-fade">
    <!-- Header -->
    <div class="p-3 border-b border-border bg-muted/40 flex items-center justify-between">
      <div class="flex items-center gap-2">
        <UploadCloud size={16} class="text-primary" />
        <span class="font-medium text-foreground">
          Upload Manager ({uploadState.items.length} {uploadState.items.length === 1 ? 'file' : 'files'})
        </span>
        {#if uploadState.activeCount > 0}
          <span class="text-[11px] text-muted-foreground font-mono">
            {uploadState.totalProgress}%
          </span>
        {/if}
      </div>

      <div class="flex items-center gap-1">
        <button
          onclick={() => isMinimized = !isMinimized}
          class="p-1 rounded text-muted-foreground hover:text-foreground transition-colors"
          title={isMinimized ? 'Expand' : 'Minimize'}
          aria-label="Toggle minimized"
        >
          {#if isMinimized}
            <ChevronUp size={15} />
          {:else}
            <ChevronDown size={15} />
          {/if}
        </button>

        <button
          onclick={() => uploadManager.setOpen(false)}
          class="p-1 rounded text-muted-foreground hover:text-foreground transition-colors"
          title="Close upload tray"
          aria-label="Close"
        >
          <X size={15} />
        </button>
      </div>
    </div>

    <!-- Overall Progress bar -->
    <div class="h-1 w-full bg-muted overflow-hidden">
      <div
        class="h-full bg-primary transition-all duration-200"
        style={`width: ${uploadState.totalProgress}%`}
      ></div>
    </div>

    <!-- Items List (shown if not minimized) -->
    {#if !isMinimized}
      <div class="max-h-64 overflow-y-auto divide-y divide-border/60">
        {#each uploadState.items as item (item.id)}
          <div class="p-2.5 flex items-center justify-between gap-3 hover:bg-muted/30 transition-colors">
            <!-- Icon by Status -->
            <div class="shrink-0">
              {#if item.status === 'COMPLETED'}
                <CheckCircle2 size={16} class="text-emerald-500" />
              {:else if item.status === 'ERROR'}
                <AlertCircle size={16} class="text-destructive" />
              {:else if item.status === 'CANCELLED'}
                <XCircle size={16} class="text-muted-foreground" />
              {:else}
                <UploadCloud size={16} class="text-primary animate-pulse" />
              {/if}
            </div>

            <!-- Name and progress info -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between gap-2 mb-1">
                <span class="font-medium text-foreground truncate" title={item.name}>
                  {item.name}
                </span>
                <span class="text-[11px] font-mono text-muted-foreground shrink-0">
                  {formatBytes(item.size)}
                </span>
              </div>

              <!-- Item progress bar -->
              <div class="h-1 w-full rounded-full bg-muted overflow-hidden">
                <div
                  class={`h-full transition-all duration-150 ${
                    item.status === 'COMPLETED' ? 'bg-emerald-500' :
                    item.status === 'ERROR' ? 'bg-destructive' : 'bg-primary'
                  }`}
                  style={`width: ${item.progress}%`}
                ></div>
              </div>

              {#if item.error}
                <div class="text-[10px] text-destructive truncate mt-1">
                  {item.error}
                </div>
              {/if}
            </div>

            <!-- Actions (Retry, Cancel) -->
            <div class="shrink-0 flex items-center gap-1">
              {#if item.status === 'ERROR'}
                <button
                  onclick={() => {
                    if (auth.activeWorkspace) {
                      uploadManager.retry(item.id, auth.activeWorkspace.id);
                    }
                  }}
                  class="p-1 rounded text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
                  title="Retry Upload"
                  aria-label="Retry upload"
                >
                  <RotateCw size={13} />
                </button>
              {/if}

              {#if item.status === 'UPLOADING' || item.status === 'QUEUED'}
                <button
                  onclick={() => uploadManager.cancel(item.id)}
                  class="p-1 rounded text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
                  title="Cancel Upload"
                  aria-label="Cancel upload"
                >
                  <X size={13} />
                </button>
              {/if}
            </div>
          </div>
        {/each}
      </div>

      <!-- Footer -->
      <div class="p-2 border-t border-border bg-muted/20 flex items-center justify-between text-[11px] text-muted-foreground">
        <span>Direct S3 upload to Backblaze B2</span>
        <button
          onclick={() => uploadManager.clearCompleted()}
          class="hover:text-foreground transition-colors flex items-center gap-1 font-medium"
        >
          <Trash2 size={12} />
          <span>Clear Completed</span>
        </button>
      </div>
    {/if}
  </div>
{/if}
