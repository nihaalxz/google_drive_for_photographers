<script lang="ts">
  import { page } from '$app/state';
  import { auth } from '../../stores/auth';
  import {
    Aperture,
    HardDrive,
    Clock,
    Star,
    Share2,
    Images,
    Trash2,
    Database,
    Settings,
    LogOut,
    Menu,
    X,
    ChevronRight,
    UserCircle
  } from 'lucide-svelte';

  let isCollapsed = $state(false);
  let isMobileOpen = $state(false);

  let currentPath = $derived(page.url.pathname);
  let activeWs = $derived(auth.activeWorkspace);
  let currentUser = $derived(auth.user);

  function formatBytes(bytes: number): string {
    if (!bytes || bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
  }

  const navItems = [
    { label: 'My Drive', href: '/app', icon: HardDrive },
    { label: 'Recent', href: '/app/recent', icon: Clock },
    { label: 'Starred', href: '/app/starred', icon: Star },
    { label: 'Shared', href: '/app/shared', icon: Share2 },
    { label: 'Albums & Galleries', href: '/app/albums', icon: Images },
    { label: 'Trash', href: '/app/trash', icon: Trash2 },
    { label: 'Storage & Quota', href: '/app/storage', icon: Database },
    { label: 'Settings', href: '/app/settings/profile', icon: Settings },
  ];

  function isActive(href: string): boolean {
    if (href === '/app') {
      return currentPath === '/app';
    }
    return currentPath.startsWith(href);
  }
</script>

<!-- Mobile Menu Trigger -->
<div class="lg:hidden fixed top-3 left-3 z-40">
  <button
    onclick={() => isMobileOpen = !isMobileOpen}
    class="p-2 rounded border border-border bg-card text-foreground shadow-sm"
    aria-label="Toggle navigation menu"
  >
    {#if isMobileOpen}
      <X size={20} />
    {:else}
      <Menu size={20} />
    {/if}
  </button>
</div>

<!-- Mobile Drawer Backdrop -->
{#if isMobileOpen}
  <button
    onclick={() => isMobileOpen = false}
    class="fixed inset-0 bg-black/60 z-30 lg:hidden"
    aria-label="Close navigation overlay"
  ></button>
{/if}

<!-- Sidebar Container -->
<aside
  class={`fixed lg:static top-0 left-0 bottom-0 z-40 h-full flex flex-col border-r border-border bg-card text-card-foreground transition-all duration-200 select-none
    ${isMobileOpen ? 'translate-x-0 w-64 shadow-2xl' : '-translate-x-full lg:translate-x-0'}
    ${isCollapsed ? 'lg:w-16' : 'lg:w-64'}
  `}
>
  <!-- Brand Header -->
  <div class="h-14 border-b border-border flex items-center justify-between px-4">
    <a href="/app" class="flex items-center gap-2.5 overflow-hidden">
      <div class="w-8 h-8 rounded bg-foreground text-background flex items-center justify-center shrink-0">
        <Aperture size={20} class="stroke-[2.2]" />
      </div>
      {#if !isCollapsed}
        <div class="flex flex-col min-w-0">
          <span class="font-semibold text-sm tracking-tight text-foreground leading-none">LensVault</span>
          <span class="text-[11px] text-muted-foreground truncate leading-tight mt-0.5">
            {activeWs?.name || 'Studio Vault'}
          </span>
        </div>
      {/if}
    </a>

    <!-- Desktop Collapse Button -->
    <button
      onclick={() => isCollapsed = !isCollapsed}
      class="hidden lg:flex p-1 rounded text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
      title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
      aria-label="Toggle sidebar expansion"
    >
      <ChevronRight size={16} class={`transition-transform ${isCollapsed ? '' : 'rotate-180'}`} />
    </button>
  </div>

  <!-- Navigation Links -->
  <nav class="flex-1 overflow-y-auto px-2 py-3 space-y-1" aria-label="Main Navigation">
    {#each navItems as item}
      {@const active = isActive(item.href)}
      <a
        href={item.href}
        onclick={() => isMobileOpen = false}
        class={`group flex items-center gap-3 px-3 py-2 rounded text-sm transition-colors relative
          ${active
            ? 'bg-muted text-foreground font-medium'
            : 'text-muted-foreground hover:text-foreground hover:bg-muted/60'
          }
          ${isCollapsed ? 'justify-center px-0' : ''}
        `}
        title={isCollapsed ? item.label : undefined}
      >
        <!-- Active indicator -->
        {#if active}
          <span class="absolute left-0 top-1.5 bottom-1.5 w-1 rounded-r bg-foreground"></span>
        {/if}

        <item.icon size={20} class="shrink-0 stroke-[1.8]" />

        {#if !isCollapsed}
          <span class="truncate">{item.label}</span>
        {/if}
      </a>
    {/each}
  </nav>

  <!-- Storage Meter Section -->
  {#if !isCollapsed && activeWs}
    <div class="p-4 mx-2 mb-2 rounded border border-border bg-background/50 text-xs space-y-2">
      <div class="flex items-center justify-between text-muted-foreground font-medium">
        <span>Storage</span>
        <span>{activeWs.storage_used_percent}%</span>
      </div>
      <div class="w-full h-1.5 rounded-full bg-muted overflow-hidden">
        <div
          class="h-full bg-foreground transition-all duration-300"
          style={`width: ${Math.min(100, activeWs.storage_used_percent)}%`}
        ></div>
      </div>
      <div class="text-[11px] text-muted-foreground truncate">
        {formatBytes(activeWs.storage_used_bytes)} of {formatBytes(activeWs.storage_limit_bytes)}
      </div>
    </div>
  {/if}

  <!-- User Account & Logout Footer -->
  <div class="border-t border-border p-3 flex items-center justify-between">
    <div class="flex items-center gap-2.5 min-w-0">
      <div class="w-8 h-8 rounded-full bg-muted border border-border flex items-center justify-center shrink-0 text-muted-foreground">
        <UserCircle size={20} />
      </div>
      {#if !isCollapsed}
        <div class="min-w-0 flex flex-col">
          <span class="text-xs font-medium text-foreground truncate leading-tight">
            {currentUser?.full_name || currentUser?.username || 'Photographer'}
          </span>
          <span class="text-[11px] text-muted-foreground truncate leading-tight">
            {currentUser?.email || ''}
          </span>
        </div>
      {/if}
    </div>

    <button
      onclick={() => auth.logout().then(() => window.location.href = '/login')}
      class="p-1.5 rounded text-muted-foreground hover:text-destructive hover:bg-muted transition-colors shrink-0"
      title="Sign Out"
      aria-label="Sign out"
    >
      <LogOut size={16} />
    </button>
  </div>
</aside>
