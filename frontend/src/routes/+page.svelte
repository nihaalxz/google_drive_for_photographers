<script lang="ts">
  import { onMount } from 'svelte';
  import { goto } from '$app/navigation';
  import { auth } from '$lib/stores/auth';
  import { Aperture, Loader2 } from 'lucide-svelte';

  onMount(async () => {
    let user = auth.user;
    if (!auth.initialized) {
      const res = await auth.init();
      user = res ? res.user : null;
    }

    if (user) {
      goto('/app', { replaceState: true });
    } else {
      goto('/login', { replaceState: true });
    }
  });
</script>

<svelte:head>
  <title>LensVault</title>
</svelte:head>

<div class="min-h-screen flex flex-col items-center justify-center bg-background text-foreground">
  <div class="flex flex-col items-center gap-3">
    <div class="w-10 h-10 rounded bg-foreground text-background flex items-center justify-center shadow-sm">
      <Aperture size={22} class="stroke-[2.2]" />
    </div>
    <div class="flex items-center gap-2 text-xs text-muted-foreground font-mono">
      <Loader2 size={13} class="animate-spin text-foreground" />
      <span>Redirecting to LensVault...</span>
    </div>
  </div>
</div>
