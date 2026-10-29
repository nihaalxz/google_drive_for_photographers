<script lang="ts">
  import { toast } from '$lib/stores/toast';

  let defaultExpiryDays = $state('30');
  let defaultAllowDownloads = $state(true);
  let defaultAllowFavorites = $state(true);
  let isSaving = $state(false);

  function handleSave(e: Event) {
    e.preventDefault();
    isSaving = true;
    setTimeout(() => {
      isSaving = false;
      toast.success('Sharing defaults saved successfully');
    }, 400);
  }
</script>

<svelte:head>
  <title>Sharing Defaults — LensVault</title>
</svelte:head>

<div class="space-y-6 text-xs text-card-foreground">
  <div class="space-y-1">
    <h2 class="text-base font-semibold text-foreground">Client Sharing Defaults</h2>
    <p class="text-muted-foreground">Configure global defaults applied whenever generating new client proofing galleries or file share links.</p>
  </div>

  <form onsubmit={handleSave} class="p-6 rounded border border-border bg-card space-y-4 shadow-sm">
    <div class="space-y-1.5">
      <label for="def-exp" class="font-medium text-foreground block">Default Link Expiration</label>
      <select
        id="def-exp"
        bind:value={defaultExpiryDays}
        class="w-full h-8 px-2.5 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
      >
        <option value="7">7 Days</option>
        <option value="14">14 Days</option>
        <option value="30">30 Days (Recommended)</option>
        <option value="90">90 Days</option>
        <option value="365">1 Year</option>
        <option value="0">Never Expire (Manual revocation only)</option>
      </select>
    </div>

    <div class="space-y-3 pt-2">
      <span class="font-medium text-foreground block">Default Permissions</span>

      <label class="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          bind:checked={defaultAllowDownloads}
          class="rounded border-border text-primary focus:ring-primary"
        />
        <div>
          <span class="font-medium text-foreground block">Allow High-Resolution Downloads by Default</span>
          <span class="text-muted-foreground text-[11px]">Clients can download uncompressed master photographs.</span>
        </div>
      </label>

      <label class="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          bind:checked={defaultAllowFavorites}
          class="rounded border-border text-primary focus:ring-primary"
        />
        <div>
          <span class="font-medium text-foreground block">Enable Client Proofing & Favorite Selection</span>
          <span class="text-muted-foreground text-[11px]">Clients can star/favorite photographs for album selection.</span>
        </div>
      </label>
    </div>

    <div class="pt-3 border-t border-border flex justify-end">
      <button
        type="submit"
        disabled={isSaving}
        class="px-4 py-1.5 rounded bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
      >
        {isSaving ? 'Saving...' : 'Save Defaults'}
      </button>
    </div>
  </form>
</div>
