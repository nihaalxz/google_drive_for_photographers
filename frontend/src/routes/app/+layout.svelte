<script lang="ts">
  import { onMount, type Snippet } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { goto } from '$app/navigation';
  import Sidebar from '$lib/components/layout/Sidebar.svelte';
  import TopToolbar from '$lib/components/layout/TopToolbar.svelte';
  import MobileBottomNav from '$lib/components/layout/MobileBottomNav.svelte';

  let { children }: { children: Snippet } = $props();

  let isAuthed = $derived(auth.user !== null);
  let isChecking = $derived(auth.loading || !auth.initialized);

  onMount(async () => {
    if (!auth.initialized) {
      await auth.init();
    }
    if (!auth.user) {
      goto('/login');
    }
  });

  $effect(() => {
    if (auth.initialized && !auth.user) {
      goto('/login');
    }
  });
</script>

{#if isChecking}
  <div class="min-h-screen bg-background flex flex-col items-center justify-center text-xs text-muted-foreground gap-3">
    <div class="w-6 h-6 border-2 border-primary border-t-transparent rounded-full animate-spin"></div>
    <span>Authenticating session...</span>
  </div>
{:else if isAuthed}
  <div class="h-screen w-screen flex overflow-hidden bg-background">
    <!-- Sidebar / Drawer -->
    <Sidebar />

    <!-- Main Content Viewport -->
    <div
      class="flex-1 flex flex-col min-w-0 overflow-hidden relative lg:!pb-0"
      style="padding-bottom: calc(3.5rem + env(safe-area-inset-bottom, 0px));"
    >
      {@render children()}
    </div>

    <!-- Mobile Fixed Bottom Navigation -->
    <MobileBottomNav />
  </div>
{/if}
