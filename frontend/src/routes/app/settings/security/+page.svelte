<script lang="ts">
  import { api } from '$lib/services/api';
  import { toast } from '$lib/stores/toast';

  let oldPassword = $state('');
  let newPassword = $state('');
  let confirmPassword = $state('');
  let isSaving = $state(false);
  let error = $state('');

  async function handlePasswordChange(e: Event) {
    e.preventDefault();
    error = '';
    if (newPassword.length < 8) {
      error = 'New password must be at least 8 characters long.';
      return;
    }
    if (newPassword !== confirmPassword) {
      error = 'New passwords do not match.';
      return;
    }

    isSaving = true;
    try {
      await api.auth.changePassword({
        old_password: oldPassword,
        new_password: newPassword
      });
      oldPassword = '';
      newPassword = '';
      confirmPassword = '';
      toast.success('Password changed successfully');
    } catch (err: unknown) {
      error = err instanceof Error ? err.message : 'Failed to change password. Check current password.';
    } finally {
      isSaving = false;
    }
  }
</script>

<svelte:head>
  <title>Security Settings — LensVault</title>
</svelte:head>

<div class="space-y-6 text-xs text-card-foreground">
  <div class="space-y-1">
    <h2 class="text-base font-semibold text-foreground">Authentication & Security</h2>
    <p class="text-muted-foreground">Update your password and view account protection standards.</p>
  </div>

  <form onsubmit={handlePasswordChange} class="p-6 rounded border border-border bg-card space-y-4 shadow-sm">
    {#if error}
      <div class="p-2.5 rounded bg-destructive/10 border border-destructive/20 text-destructive">
        {error}
      </div>
    {/if}

    <div class="space-y-1.5">
      <label for="old-pass" class="font-medium text-foreground block">Current Password</label>
      <input
        id="old-pass"
        type="password"
        bind:value={oldPassword}
        required
        placeholder="••••••••"
        class="w-full h-8 px-2.5 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
      />
    </div>

    <div class="space-y-1.5">
      <label for="new-pass" class="font-medium text-foreground block">New Password (8+ characters)</label>
      <input
        id="new-pass"
        type="password"
        bind:value={newPassword}
        required
        minlength="8"
        placeholder="••••••••"
        class="w-full h-8 px-2.5 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
      />
    </div>

    <div class="space-y-1.5">
      <label for="confirm-pass" class="font-medium text-foreground block">Confirm New Password</label>
      <input
        id="confirm-pass"
        type="password"
        bind:value={confirmPassword}
        required
        minlength="8"
        placeholder="••••••••"
        class="w-full h-8 px-2.5 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
      />
    </div>

    <div class="pt-3 border-t border-border flex justify-end">
      <button
        type="submit"
        disabled={isSaving}
        class="px-4 py-1.5 rounded bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
      >
        {isSaving ? 'Updating...' : 'Update Password'}
      </button>
    </div>
  </form>
</div>
