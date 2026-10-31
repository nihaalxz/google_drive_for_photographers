<script lang="ts">
  import { api } from '../../services/api';
  import { toast } from '../../stores/toast';
  import { auth } from '../../stores/auth';
  import {
    Share2,
    X,
    Copy,
    Check,
    Lock,
    Calendar,
    Download,
    Heart,
    ExternalLink,
    QrCode
  } from 'lucide-svelte';
  import type { ShareLink } from '../../types';
  import PrintableQrModal from './PrintableQrModal.svelte';

  interface Props {
    isOpen: boolean;
    targetType: 'ALBUM' | 'FOLDER' | 'FILE';
    targetId: string;
    targetTitle: string;
    onClose: () => void;
  }

  let { isOpen, targetType, targetId, targetTitle, onClose }: Props = $props();

  let title = $state('');
  let password = $state('');
  let expiresAt = $state('');
  let allowDownloads = $state(true);
  let allowFavorites = $state(true);
  let isSubmitting = $state(false);
  let createdLink = $state<ShareLink | null>(null);
  let copied = $state(false);
  let isQrOpen = $state(false);
  let existingLink = $state<ShareLink | null>(null);
  let selectedQrLink = $state<ShareLink | null>(null);
  let checkingExisting = $state(false);

  async function checkExistingLink() {
    if (!auth.activeWorkspace) return;
    checkingExisting = true;
    try {
      const res = await api.sharing.list(auth.activeWorkspace.id);
      const matches = (res.results || []).filter(link => {
        if (targetType === 'ALBUM' && link.album === targetId) return true;
        if (targetType === 'FOLDER' && link.folder === targetId) return true;
        if (targetType === 'FILE' && link.file_asset === targetId) return true;
        return false;
      });
      existingLink = matches.length > 0 ? matches[0] : null;
    } catch {
      existingLink = null;
    } finally {
      checkingExisting = false;
    }
  }

  $effect(() => {
    if (isOpen) {
      title = targetTitle || 'Shared Collection';
      createdLink = null;
      copied = false;
      isQrOpen = false;
      selectedQrLink = null;
      checkExistingLink();
    }
  });

  async function handleCreate(e: Event) {
    e.preventDefault();
    if (!auth.activeWorkspace) return;

    isSubmitting = true;
    try {
      const payload: {
        workspace_id: string;
        title: string;
        target_type: 'ALBUM' | 'FOLDER' | 'FILE';
        album?: string;
        folder?: string;
        file_asset?: string;
        password?: string;
        expires_at?: string;
        allow_downloads: boolean;
        allow_favorites: boolean;
      } = {
        workspace_id: auth.activeWorkspace.id,
        title,
        target_type: targetType,
        allow_downloads: allowDownloads,
        allow_favorites: allowFavorites
      };

      if (targetType === 'ALBUM') payload.album = targetId;
      if (targetType === 'FOLDER') payload.folder = targetId;
      if (targetType === 'FILE') payload.file_asset = targetId;
      if (password) payload.password = password;
      if (expiresAt) payload.expires_at = new Date(expiresAt).toISOString();

      const res = await api.sharing.create(payload);
      createdLink = res;
      toast.success('Share link generated successfully!');
    } catch (err: unknown) {
      toast.error(err instanceof Error ? err.message : 'Failed to generate share link');
    } finally {
      isSubmitting = false;
    }
  }

  function getShareUrl(token: string): string {
    if (typeof window === 'undefined') return `/share/${token}`;
    return `${window.location.origin}/share/${token}`;
  }

  function copyUrl(token: string) {
    const url = getShareUrl(token);
    navigator.clipboard.writeText(url);
    copied = true;
    toast.info('Share URL copied to clipboard');
    setTimeout(() => copied = false, 2500);
  }
</script>

{#if isOpen}
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <!-- Backdrop -->
    <button
      onclick={onClose}
      class="fixed inset-0 bg-black/60 transition-opacity"
      aria-label="Close modal overlay"
    ></button>

    <!-- Modal Dialog -->
    <div
      role="dialog"
      aria-modal="true"
      class="relative w-full max-w-lg rounded-md border border-border bg-card p-4 sm:p-5 shadow-xl text-card-foreground text-xs z-10 space-y-4 subtle-fade max-h-[90vh] overflow-y-auto"
    >
      <div class="flex items-center justify-between border-b border-border pb-3">
        <div class="flex items-center gap-2 font-semibold text-sm text-foreground">
          <Share2 size={16} />
          <h2>Share & Client Gallery Link</h2>
        </div>
        <button
          onclick={onClose}
          class="p-1 rounded text-muted-foreground hover:text-foreground transition-colors"
          aria-label="Close"
        >
          <X size={16} />
        </button>
      </div>

      {#if createdLink}
        <!-- Success State: Display Link, 1-Click Copy, and Printable QR Card -->
        <div class="space-y-3.5 py-1">
          <div class="p-3 rounded bg-muted/40 border border-border space-y-2">
            <span class="text-muted-foreground font-medium block">Public Shareable URL:</span>
            <div class="flex items-center gap-2">
              <input
                type="text"
                readonly
                value={getShareUrl(createdLink.token)}
                class="flex-1 h-8 px-2.5 rounded border border-border bg-background text-foreground font-mono text-[11px] select-all"
              />
              <button
                onclick={() => copyUrl(createdLink!.token)}
                class="flex items-center gap-1.5 h-8 px-3 rounded bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors"
              >
                {#if copied}
                  <Check size={14} />
                  <span>Copied</span>
                {:else}
                  <Copy size={14} />
                  <span>Copy</span>
                {/if}
              </button>
            </div>
          </div>

          <!-- Printable QR Code Action Card -->
          <div class="p-3.5 rounded-lg border border-primary/30 bg-primary/5 flex items-center justify-between gap-3">
            <div class="space-y-0.5 min-w-0">
              <div class="flex items-center gap-1.5 font-semibold text-foreground text-xs">
                <QrCode size={15} class="text-primary shrink-0" />
                <span>Printable QR Code Card</span>
              </div>
              <p class="text-[11px] text-muted-foreground leading-normal">
                Print or download high-res QR card with customizable instructions underneath for event tables & photo frames.
              </p>
            </div>
            <button
              type="button"
              onclick={() => { selectedQrLink = createdLink; isQrOpen = true; }}
              class="shrink-0 flex items-center gap-1.5 h-8 px-3 rounded bg-primary text-primary-foreground hover:bg-primary/90 font-medium transition-colors shadow-xs text-xs"
            >
              <QrCode size={13} />
              <span>Customize & Print</span>
            </button>
          </div>

          <div class="flex items-center justify-between text-muted-foreground text-[11px] pt-1">
            <span>Access: {createdLink.is_password_protected ? 'Password Protected' : 'Public Token'}</span>
            <a
              href={`/share/${createdLink.token}`}
              target="_blank"
              class="flex items-center gap-1 text-primary hover:underline font-medium"
            >
              <span>Preview Gallery</span>
              <ExternalLink size={12} />
            </a>
          </div>

          <div class="pt-2 border-t border-border flex justify-end">
            <button
              onclick={onClose}
              class="px-4 py-1.5 rounded bg-muted hover:bg-muted/80 text-foreground font-medium transition-colors"
            >
              Done
            </button>
          </div>
        </div>
      {:else}
        <!-- Notice if an existing link was found for this target -->
        {#if existingLink}
          <div class="p-3 rounded border border-border bg-muted/40 flex items-center justify-between gap-2.5">
            <div class="space-y-0.5 min-w-0">
              <span class="font-medium text-foreground text-xs block truncate">
                Active link exists: {existingLink.title}
              </span>
              <span class="text-[10px] text-muted-foreground font-mono truncate block">
                {getShareUrl(existingLink.token)}
              </span>
            </div>
            <div class="flex items-center gap-1.5 shrink-0">
              <button
                type="button"
                onclick={() => { selectedQrLink = existingLink; isQrOpen = true; }}
                class="flex items-center gap-1 h-7 px-2.5 rounded border border-border bg-background hover:bg-muted text-foreground transition-colors text-[11px] font-medium"
                title="Create printable QR code"
              >
                <QrCode size={12} class="text-primary" />
                <span>Print QR</span>
              </button>
              <button
                type="button"
                onclick={() => copyUrl(existingLink!.token)}
                class="flex items-center gap-1 h-7 px-2.5 rounded bg-primary text-primary-foreground hover:bg-primary/90 transition-colors text-[11px] font-medium"
              >
                <Copy size={12} />
                <span>Copy</span>
              </button>
            </div>
          </div>
        {/if}

        <!-- Form to Configure Link -->
        <form onsubmit={handleCreate} class="space-y-3.5">
          <div class="space-y-1">
            <label for="share-title" class="font-medium text-foreground block">Gallery Title</label>
            <input
              id="share-title"
              type="text"
              bind:value={title}
              required
              class="w-full h-8 px-2.5 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            />
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <div class="space-y-1">
              <label for="share-pass" class="font-medium text-foreground flex items-center gap-1">
                <Lock size={12} />
                <span>Password (Optional)</span>
              </label>
              <input
                id="share-pass"
                type="password"
                bind:value={password}
                placeholder="Leave blank for open access"
                class="w-full h-8 px-2.5 rounded border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
              />
            </div>

            <div class="space-y-1">
              <label for="share-exp" class="font-medium text-foreground flex items-center gap-1">
                <Calendar size={12} />
                <span>Expiration Date</span>
              </label>
              <input
                id="share-exp"
                type="date"
                bind:value={expiresAt}
                class="w-full h-8 px-2.5 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
              />
            </div>
          </div>

          <div class="p-3 rounded border border-border bg-muted/20 space-y-2">
            <span class="font-medium text-foreground block">Client Permissions</span>
            <div class="flex items-center gap-4">
              <label class="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  bind:checked={allowDownloads}
                  class="rounded border-border text-primary focus:ring-primary"
                />
                <span class="flex items-center gap-1 text-muted-foreground hover:text-foreground">
                  <Download size={13} />
                  <span>Allow High-Res Downloads</span>
                </span>
              </label>

              <label class="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  bind:checked={allowFavorites}
                  class="rounded border-border text-primary focus:ring-primary"
                />
                <span class="flex items-center gap-1 text-muted-foreground hover:text-foreground">
                  <Heart size={13} />
                  <span>Allow Client Favorites</span>
                </span>
              </label>
            </div>
          </div>

          <div class="pt-3 border-t border-border flex items-center justify-end gap-2">
            <button
              type="button"
              onclick={onClose}
              class="px-3 py-1.5 rounded border border-border bg-background hover:bg-muted text-foreground transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              class="px-4 py-1.5 rounded bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
            >
              {isSubmitting ? 'Creating...' : 'Create Share Link'}
            </button>
          </div>
        </form>
      {/if}
    </div>
  </div>
{/if}

{#if isQrOpen && (createdLink || selectedQrLink)}
  {@const activeLink = createdLink || selectedQrLink}
  <PrintableQrModal
    isOpen={isQrOpen}
    url={getShareUrl(activeLink!.token)}
    initialTitle={activeLink!.title || title || 'Photo Gallery'}
    initialSubtitle="Scan with your phone to view and download full-resolution photographs."
    studioName={auth.activeWorkspace?.name || 'LensVault Photography'}
    hasPassword={activeLink!.is_password_protected}
    onClose={() => isQrOpen = false}
  />
{/if}
