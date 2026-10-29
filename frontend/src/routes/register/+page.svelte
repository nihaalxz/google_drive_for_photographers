<script lang="ts">
  import { api } from '$lib/services/api';
  import { auth } from '$lib/stores/auth';
  import { toast } from '$lib/stores/toast';
  import { goto } from '$app/navigation';
  import ThemeToggle from '$lib/components/layout/ThemeToggle.svelte';
  import { Aperture, ArrowRight, Lock, Mail, User, Building } from 'lucide-svelte';

  let fullName = $state('');
  let workspaceName = $state('');
  let username = $state('');
  let email = $state('');
  let password = $state('');
  let isSubmitting = $state(false);
  let error = $state('');

  async function handleRegister(e: Event) {
    e.preventDefault();
    error = '';
    if (password.length < 8) {
      error = 'Password must be at least 8 characters long.';
      return;
    }
    isSubmitting = true;
    try {
      const res = await api.auth.register({
        email,
        username: username || email.split('@')[0],
        password,
        full_name: fullName,
        workspace_name: workspaceName || (fullName ? `${fullName}'s Studio` : 'My Vault')
      });
      auth.setUserAndWorkspace(res.user, res.active_workspace);
      toast.success('Studio account created successfully!');
      goto('/app');
    } catch (err: unknown) {
      error = err instanceof Error ? err.message : 'Registration failed. Please check inputs.';
    } finally {
      isSubmitting = false;
    }
  }
</script>

<svelte:head>
  <title>Create Studio Account — LensVault</title>
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
      <h1 class="text-xl font-bold tracking-tight text-foreground">Create Studio Account</h1>
      <p class="text-xs text-muted-foreground">Start storing and delivering uncompressed client media</p>
    </div>

    <form onsubmit={handleRegister} class="p-6 rounded-md border border-border bg-card space-y-3.5 shadow-sm text-xs">
      {#if error}
        <div class="p-2.5 rounded bg-destructive/10 border border-destructive/20 text-destructive">
          {error}
        </div>
      {/if}

      <div class="space-y-1.5">
        <label for="reg-name" class="font-medium text-foreground block">Full Name</label>
        <div class="relative">
          <User size={15} class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            id="reg-name"
            type="text"
            bind:value={fullName}
            required
            placeholder="Elena Rostova"
            class="w-full h-9 pl-9 pr-3 rounded border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          />
        </div>
      </div>

      <div class="space-y-1.5">
        <label for="reg-ws" class="font-medium text-foreground block">Studio / Business Name</label>
        <div class="relative">
          <Building size={15} class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            id="reg-ws"
            type="text"
            bind:value={workspaceName}
            placeholder="Elena Rostova Fine Art & Weddings"
            class="w-full h-9 pl-9 pr-3 rounded border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          />
        </div>
      </div>

      <div class="space-y-1.5">
        <label for="reg-email" class="font-medium text-foreground block">Email Address</label>
        <div class="relative">
          <Mail size={15} class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            id="reg-email"
            type="email"
            bind:value={email}
            required
            placeholder="elena@studio.com"
            class="w-full h-9 pl-9 pr-3 rounded border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
          />
        </div>
      </div>

      <div class="space-y-1.5">
        <label for="reg-pass" class="font-medium text-foreground block">Password (8+ chars)</label>
        <div class="relative">
          <Lock size={15} class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            id="reg-pass"
            type="password"
            bind:value={password}
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
        class="w-full h-9 rounded bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors flex items-center justify-center gap-2 disabled:opacity-50 shadow-sm mt-2"
      >
        <span>{isSubmitting ? 'Creating account...' : 'Start 10 GB Free'}</span>
        <ArrowRight size={14} />
      </button>
    </form>

    <div class="text-center text-xs text-muted-foreground">
      Already have a vault?
      <a href="/login" class="text-foreground font-semibold hover:underline ml-1">
        Sign In
      </a>
    </div>
  </div>
</div>
