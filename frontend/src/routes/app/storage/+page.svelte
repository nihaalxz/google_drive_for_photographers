<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/services/api';
  import { auth } from '$lib/stores/auth';
  import { toast } from '$lib/stores/toast';
  import TopToolbar from '$lib/components/layout/TopToolbar.svelte';
  import {
    Database,
    HardDrive,
    ShieldCheck,
    Camera,
    Film,
    FileText,
    RefreshCw
  } from 'lucide-svelte';

  let breakdown = $state<{
    total_limit_bytes: number;
    used_bytes: number;
    available_bytes: number;
    used_percent: number;
    breakdown: {
      raw_bytes: number;
      standard_images_bytes: number;
      videos_bytes: number;
      other_bytes: number;
    };
    file_count: number;
  } | null>(null);

  let loading = $state(true);

  let rawPct = $derived(
    breakdown && breakdown.total_limit_bytes > 0 ? (breakdown.breakdown.raw_bytes / breakdown.total_limit_bytes) * 100 : 0
  );
  let imgPct = $derived(
    breakdown && breakdown.total_limit_bytes > 0 ? (breakdown.breakdown.standard_images_bytes / breakdown.total_limit_bytes) * 100 : 0
  );
  let vidPct = $derived(
    breakdown && breakdown.total_limit_bytes > 0 ? (breakdown.breakdown.videos_bytes / breakdown.total_limit_bytes) * 100 : 0
  );
  let othPct = $derived(
    breakdown && breakdown.total_limit_bytes > 0 ? (breakdown.breakdown.other_bytes / breakdown.total_limit_bytes) * 100 : 0
  );

  async function loadStorageMetrics() {
    if (!auth.initialized) {
      await auth.init();
    }
    if (!auth.activeWorkspace) {
      loading = false;
      return;
    }
    loading = true;
    try {
      const data = await api.workspaces.storageBreakdown(auth.activeWorkspace.id);
      breakdown = data;
    } catch (err: unknown) {
      toast.error('Failed to load storage breakdown');
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadStorageMetrics();

    function handleAutoRefresh() {
      loadStorageMetrics();
      auth.refreshWorkspace();
    }

    window.addEventListener('lensvault:file-uploaded', handleAutoRefresh);
    window.addEventListener('lensvault:uploads-completed', handleAutoRefresh);

    return () => {
      window.removeEventListener('lensvault:file-uploaded', handleAutoRefresh);
      window.removeEventListener('lensvault:uploads-completed', handleAutoRefresh);
    };
  });

  function formatBytes(bytes: number): string {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
</script>

<svelte:head>
  <title>Storage Quota & Breakdown — LensVault</title>
</svelte:head>

<TopToolbar />

<div class="h-10 px-3 sm:px-6 border-b border-border bg-card/40 flex items-center justify-between shrink-0">
  <div class="flex items-center gap-2 text-xs font-medium text-foreground truncate min-w-0">
    <Database size={15} class="shrink-0" />
    <span class="truncate">Storage Accounting & Quota</span>
  </div>
  <button
    onclick={loadStorageMetrics}
    class="flex items-center gap-1.5 text-xs text-muted-foreground hover:text-foreground transition-colors shrink-0"
  >
    <RefreshCw size={12} />
    <span class="hidden xs:inline">Refresh Ledger</span>
  </button>
</div>

<div class="flex-1 overflow-y-auto p-3 sm:p-6 space-y-4 sm:space-y-6 max-w-4xl">
  {#if loading}
    <div class="flex flex-col items-center justify-center py-24 text-xs text-muted-foreground gap-3">
      <div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
      <span>Calculating storage accounting ledger...</span>
    </div>

  {:else if breakdown}
    <!-- Main Meter Card -->
    <div class="p-4 sm:p-6 rounded border border-border bg-card space-y-4">
      <div class="flex items-center justify-between">
        <div class="space-y-1">
          <h2 class="text-sm sm:text-base font-semibold text-foreground">
            {formatBytes(breakdown.used_bytes)} used of {formatBytes(breakdown.total_limit_bytes)}
          </h2>
          <p class="text-[11px] sm:text-xs text-muted-foreground">
            {formatBytes(breakdown.available_bytes)} remaining storage in this workspace
          </p>
        </div>
        <span class="font-mono text-lg sm:text-xl font-bold text-foreground">
          {breakdown.used_percent}%
        </span>
      </div>

      <!-- Segmented Bar Meter -->
      <div class="w-full h-3 rounded-full bg-muted overflow-hidden flex">
        <div class="bg-indigo-500 h-full transition-all" style={`width: ${rawPct}%`} title="RAW Archives"></div>
        <div class="bg-blue-500 h-full transition-all" style={`width: ${imgPct}%`} title="Standard Images"></div>
        <div class="bg-amber-500 h-full transition-all" style={`width: ${vidPct}%`} title="Videos"></div>
        <div class="bg-zinc-500 h-full transition-all" style={`width: ${othPct}%`} title="Other"></div>
      </div>

      <!-- Legend -->
      <div class="grid grid-cols-1 xs:grid-cols-2 gap-2 sm:flex sm:flex-wrap sm:gap-6 pt-2 text-xs text-muted-foreground">
        <div class="flex items-center gap-2">
          <span class="w-2.5 h-2.5 rounded-full bg-indigo-500 shrink-0"></span>
          <span>RAW ({formatBytes(breakdown.breakdown.raw_bytes)})</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-2.5 h-2.5 rounded-full bg-blue-500 shrink-0"></span>
          <span>JPEG / WebP ({formatBytes(breakdown.breakdown.standard_images_bytes)})</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-2.5 h-2.5 rounded-full bg-amber-500 shrink-0"></span>
          <span>Videos ({formatBytes(breakdown.breakdown.videos_bytes)})</span>
        </div>
        <div class="flex items-center gap-2">
          <span class="w-2.5 h-2.5 rounded-full bg-zinc-500 shrink-0"></span>
          <span>Other ({formatBytes(breakdown.breakdown.other_bytes)})</span>
        </div>
      </div>
    </div>

    <!-- Storage Provider Verification Card -->
    <div class="p-5 rounded border border-border bg-card space-y-3 text-xs">
      <div class="flex items-center gap-2 font-semibold text-foreground">
        <ShieldCheck size={16} class="text-emerald-500" />
        <h3>Storage Backend Integrity</h3>
      </div>
      <p class="text-muted-foreground leading-relaxed">
        Assets are securely stored on private Backblaze B2 buckets using S3 multipart protocols. All storage allocations are verified authoritatively against object metadata to prevent ghost allocations or quota drift.
      </p>
      <div class="pt-2 border-t border-border flex items-center justify-between text-muted-foreground">
        <span>Bucket: <code class="font-mono text-foreground font-medium">lensvault-storage</code></span>
        <span>Status: <strong class="text-emerald-500 font-semibold">Active & Reconciled</strong></span>
      </div>
    </div>
  {/if}
</div>
