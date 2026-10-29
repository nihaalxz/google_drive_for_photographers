<script lang="ts">
  import ThemeToggle from '$lib/components/layout/ThemeToggle.svelte';
  import { toast } from '$lib/stores/toast';
  import { goto } from '$app/navigation';
  import { Aperture, ArrowLeft, Lock, Key } from 'lucide-svelte';

  let resetToken = $state('');
  let newPassword = $state('');
  let confirmPassword = $state('');
  let isSubmitting = $state(false);
  let error = $state('');

  function handleReset(e: Event) {
    e.preventDefault();
    if (newPassword.length < 8) {
      error = 'Password must be at least 8 characters long.';
      return;
    }
    if (newPassword !== confirmPassword) {
      error = 'Passwords do not match.';
      return;
    }
    error = '';
    isSubmitting = true;

    setTimeout(() => {
      isSubmitting = false;
      toast.success('Your password has been successfully reset.');
      goto('/login');
    }, 600);
  }
</script>

<svelte:head>
  <title>Set New Password — LensVault</title>
</svelte:head>

<div class="min-h-screen flex flex-col justify-center items-center p-4 bg-background">
  <div class="absolute top-4 right-4">
    <ThemeToggle />
  </div>

  <div class="w-full max-w-sm space-y-6">
    <div class="text-center space-y-2">
      <div class="w-10 h-10 rounded bg-foreground text-background flex items-center justify-center mx-auto mb-3">
        <Aperture size={24} class="stroke-[2.2]" />
      </div>
      <h1 class="text-xl font-bold tracking-tight text-foreground">Set New Password</h1>
      <p class="text-xs text-muted-foreground">Enter the recovery token and choose a new password</p>
    </div>

    <form onsubmit={handleReset} class="p-6 rounded-md border border-border bg-card space-y-3.5 shadow-sm text-xs">
      {#if error}
        <div class="p-2.5 rounded bg-destructive/10 border border-destructive/20 text-destructive">
          {error}
        </div>
      {/if}

      <div class="space-y-1.5">
        <label for="rp-token" class="font-medium text-foreground block">Recovery Token</label>
        <div class="relative">
          <Key size={15} class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            id="rp-token"
            type="text"
            bind:value={resetToken}
            required
            placeholder="Paste reset token from email"
            class="w-full h-9 pl-9 pr-3 rounded border border-border bg-background text-foreground font-mono placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          />
        </div>
      </div>

      <div class="space-y-1.5">
        <label for="rp-pass" class="font-medium text-foreground block">New Password (8+ chars)</label>
        <div class="relative">
          <Lock size={15} class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            id="rp-pass"
            type="password"
            bind:value={newPassword}
            required
            minlength="8"
            placeholder="••••••••"
            class="w-full h-9 pl-9 pr-3 rounded border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          />
        </div>
      </div>

      <div class="space-y-1.5">
        <label for="rp-confirm" class="font-medium text-foreground block">Confirm Password</label>
        <div class="relative">
          <Lock size={15} class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            id="rp-confirm"
            type="password"
            bind:value={confirmPassword}
            required
            minlength="8"
            placeholder="••••••••"
            class="w-full h-9 pl-9 pr-3 rounded border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          />
        </div>
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        class="w-full h-9 rounded bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors shadow-sm disabled:opacity-50 mt-2"
      >
        {isSubmitting ? 'Resetting password...' : 'Update Password & Sign In'}
      </button>
    </form>

    <div class="text-center text-xs">
      <a href="/login" class="inline-flex items-center gap-1.5 text-muted-foreground hover:text-foreground font-medium">
        <ArrowLeft size={13} />
        <span>Back to Sign In</span>
      </a>
    </div>
  </div>
</div>
