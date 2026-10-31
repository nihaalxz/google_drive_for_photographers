<script lang="ts">
  import { onMount } from 'svelte';
  import { api } from '$lib/services/api';
  import { auth } from '$lib/stores/auth';
  import { toast } from '$lib/stores/toast';
  import TopToolbar from '$lib/components/layout/TopToolbar.svelte';
  import {
    Share2,
    Copy,
    Check,
    ExternalLink,
    Lock,
    Trash2,
    Eye,
    Download,
    QrCode
  } from 'lucide-svelte';
  import type { ShareLink } from '$lib/types';
  import PrintableQrModal from '$lib/components/gallery/PrintableQrModal.svelte';

  let links = $state<ShareLink[]>([]);
  let loading = $state(true);
  let copiedId = $state<string | null>(null);
  let selectedLinkForQr = $state<ShareLink | null>(null);

  async function loadLinks() {
    if (!auth.activeWorkspace) return;
    loading = true;
    try {
      const res = await api.sharing.list(auth.activeWorkspace.id);
      links = res.results || [];
    } catch (err: unknown) {
      toast.error('Failed to load shared links');
    } finally {
      loading = false;
    }
  }

  onMount(() => {
    loadLinks();
  });

  function getShareUrl(token: string): string {
    if (typeof window === 'undefined') return `/share/${token}`;
    return `${window.location.origin}/share/${token}`;
  }

  function handleCopy(link: ShareLink) {
    const url = getShareUrl(link.token);
    navigator.clipboard.writeText(url);
    copiedId = link.id;
    toast.success('Gallery URL copied to clipboard');
    setTimeout(() => copiedId = null, 2500);
  }

  async function handleDelete(link: ShareLink) {
    try {
      await api.sharing.delete(link.id);
      links = links.filter(l => l.id !== link.id);
      toast.success('Share link revoked');
    } catch (err: unknown) {
      toast.error('Failed to delete share link');
    }
  }
</script>

<svelte:head>
  <title>Shared Galleries — LensVault</title>
</svelte:head>

<TopToolbar />

<div class="h-10 px-3 sm:px-6 border-b border-border bg-card/40 flex items-center justify-between shrink-0">
  <div class="flex items-center gap-2 text-xs font-medium text-foreground truncate min-w-0">
    <Share2 size={15} class="shrink-0" />
    <span class="truncate">Active Galleries & Shared Links</span>
  </div>
  <div class="text-[11px] text-muted-foreground font-mono shrink-0">
    {links.length} active links
  </div>
</div>

<div class="flex-1 overflow-y-auto p-3 sm:p-6">
  {#if loading}
    <div class="flex flex-col items-center justify-center py-24 text-xs text-muted-foreground gap-3">
      <div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
      <span>Loading shared links...</span>
    </div>

  {:else if links.length === 0}
    <div class="text-center py-20 border border-dashed border-border rounded text-xs text-muted-foreground space-y-1 p-4">
      <p class="font-medium text-foreground">No active share links</p>
      <p>Create client proofing galleries or share links from the Albums or Drive page.</p>
    </div>

  {:else}
    <div class="rounded border border-border bg-card overflow-hidden text-xs">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse min-w-[550px]">
        <thead>
          <tr class="border-b border-border bg-muted/40 text-muted-foreground font-medium select-none">
            <th class="px-4 py-3">Gallery / Target Title</th>
            <th class="px-4 py-3">Type</th>
            <th class="px-4 py-3">Security</th>
            <th class="px-4 py-3">Views</th>
            <th class="px-4 py-3">Downloads</th>
            <th class="px-4 py-3 text-right">Actions</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-border/60">
          {#each links as link (link.id)}
            <tr class="hover:bg-muted/30 transition-colors">
              <td class="px-4 py-3 font-medium text-foreground">
                <div class="flex items-center gap-2">
                  <span>{link.title || link.token}</span>
                  <a
                    href={`/share/${link.token}`}
                    target="_blank"
                    class="text-muted-foreground hover:text-foreground"
                    title="Open public gallery"
                  >
                    <ExternalLink size={13} />
                  </a>
                </div>
              </td>
              <td class="px-4 py-3 text-muted-foreground uppercase font-mono text-[11px]">
                {link.target_type}
              </td>
              <td class="px-4 py-3 text-muted-foreground">
                {#if link.is_password_protected}
                  <span class="inline-flex items-center gap-1 text-amber-500 font-medium">
                    <Lock size={12} />
                    <span>Protected</span>
                  </span>
                {:else}
                  <span>Open Token</span>
                {/if}
              </td>
              <td class="px-4 py-3 text-muted-foreground font-mono">
                {link.view_count}
              </td>
              <td class="px-4 py-3 text-muted-foreground font-mono">
                {link.download_count}
              </td>
              <td class="px-4 py-3 text-right">
                <div class="inline-flex items-center gap-1">
                  <button
                    onclick={() => selectedLinkForQr = link}
                    class="p-1 rounded text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
                    title="Generate Printable QR Code Card"
                    aria-label="Generate Printable QR Code Card"
                  >
                    <QrCode size={14} />
                  </button>
                  <button
                    onclick={() => handleCopy(link)}
                    class="p-1 rounded text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
                    title="Copy Share URL"
                    aria-label="Copy URL"
                  >
                    {#if copiedId === link.id}
                      <Check size={14} class="text-emerald-500" />
                    {:else}
                      <Copy size={14} />
                    {/if}
                  </button>
                  <button
                    onclick={() => handleDelete(link)}
                    class="p-1 rounded text-muted-foreground hover:text-destructive hover:bg-destructive/10 transition-colors"
                    title="Revoke Share Link"
                    aria-label="Revoke link"
                  >
                    <Trash2 size={14} />
                  </button>
                </div>
              </td>
            </tr>
          {/each}
        </tbody>
      </table>
      </div>
    </div>
  {/if}
</div>

{#if selectedLinkForQr}
  <PrintableQrModal
    isOpen={!!selectedLinkForQr}
    url={getShareUrl(selectedLinkForQr.token)}
    initialTitle={selectedLinkForQr.title || 'Client Gallery'}
    initialSubtitle="Scan with your phone to view and download full-resolution photographs."
    studioName={auth.activeWorkspace?.name || 'LensVault Photography'}
    hasPassword={selectedLinkForQr.is_password_protected}
    onClose={() => selectedLinkForQr = null}
  />
{/if}
