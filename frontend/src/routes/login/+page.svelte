<script lang="ts">
  import { api } from '$lib/services/api';
  import { auth } from '$lib/stores/auth';
  import { toast } from '$lib/stores/toast';
  import { goto } from '$app/navigation';
  import ThemeToggle from '$lib/components/layout/ThemeToggle.svelte';
  import { Aperture, ArrowRight, Lock, Mail, Eye, EyeOff } from 'lucide-svelte';

  let email = $state('');
  let password = $state('');
  let showPassword = $state(false);
  let isSubmitting = $state(false);
  let error = $state('');

  async function handleLogin(e: Event) {
    e.preventDefault();
    error = '';
    isSubmitting = true;
    try {
      const res = await api.auth.login({ email, password });
      auth.setUserAndWorkspace(res.user, res.active_workspace);
      toast.success(`Welcome back, ${res.user.full_name || res.user.username}`);
      goto('/app');
    } catch (err: unknown) {
      error = err instanceof Error ? err.message : 'Invalid email or password.';
    } finally {
      isSubmitting = false;
    }
  }
</script>

<svelte:head>
  <title>Sign In — LensVault</title>
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
      <h1 class="text-xl font-bold tracking-tight text-foreground">Sign In to LensVault</h1>
      <p class="text-xs text-muted-foreground">Access your photography library and client galleries</p>
    </div>

    <form onsubmit={handleLogin} class="p-6 rounded-md border border-border bg-card space-y-4 shadow-sm text-xs">
      {#if error}
        <div class="p-2.5 rounded bg-destructive/10 border border-destructive/20 text-destructive">
          {error}
        </div>
      {/if}

      <div class="space-y-1.5">
        <label for="email" class="font-medium text-foreground block">Email Address</label>
        <div class="relative">
          <Mail size={15} class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
          <input
            id="email"
            type="email"
            bind:value={email}
            required
            placeholder="photographer@example.com"
            class="w-full h-9 pl-9 pr-3 rounded border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          />
        </div>
      </div>

      <div class="space-y-1.5">
        <div class="flex items-center justify-between">
          <label for="password" class="font-medium text-foreground block">Password</label>
          <a href="/forgot-password" class="text-[11px] text-muted-foreground hover:text-foreground">
            Forgot?
          </a>
        </div>
        <div class="relative">
          <Lock size={15} class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
          <input
            id="password"
            type={showPassword ? 'text' : 'password'}
            bind:value={password}
            required
            placeholder="••••••••"
            class="w-full h-9 pl-9 pr-10 rounded border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          />
          <button
            type="button"
            onclick={() => showPassword = !showPassword}
            class="absolute right-2.5 top-1/2 -translate-y-1/2 p-1 rounded text-muted-foreground hover:text-foreground transition-colors"
            title={showPassword ? 'Hide password' : 'Show password'}
            aria-label={showPassword ? 'Hide password' : 'Show password'}
          >
            {#if showPassword}
              <EyeOff size={15} />
            {:else}
              <Eye size={15} />
            {/if}
          </button>
        </div>
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        class="w-full h-9 rounded bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors flex items-center justify-center gap-2 disabled:opacity-50 shadow-sm"
      >
        <span>{isSubmitting ? 'Signing in...' : 'Sign In'}</span>
        <ArrowRight size={14} />
      </button>
    </form>

    <div class="text-center text-xs text-muted-foreground">
      Don't have an account?
      <a href="/register" class="text-foreground font-semibold hover:underline ml-1">
        Create Studio Account
      </a>
    </div>
  </div>
</div>
