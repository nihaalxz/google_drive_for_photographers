<script lang="ts">
  import { page } from '$app/state';
  import { isMobileNavOpen, toggleMobileNav, closeMobileNav } from '../../stores/ui';
  import {
    HardDrive,
    Clock,
    Star,
    Images,
    Menu
  } from 'lucide-svelte';

  let currentPath = $derived(page.url.pathname);
  let mobileOpen = $state(false);

  isMobileNavOpen.subscribe(v => {
    mobileOpen = v;
  });

  function isActive(href: string): boolean {
    if (href === '/app') {
      return currentPath === '/app';
    }
    return currentPath.startsWith(href);
  }

  const navItems = [
    { label: 'Drive', href: '/app', icon: HardDrive },
    { label: 'Recent', href: '/app/recent', icon: Clock },
    { label: 'Starred', href: '/app/starred', icon: Star },
    { label: 'Albums', href: '/app/albums', icon: Images },
  ];
</script>

<!-- Mobile Fixed Bottom Navigation Bar -->
<nav
  class="lg:hidden fixed bottom-0 left-0 right-0 z-30 bg-card/95 backdrop-blur-md border-t border-border flex items-center justify-around px-1 select-none shadow-[0_-2px_10px_rgba(0,0,0,0.06)]"
  style="padding-bottom: env(safe-area-inset-bottom, 0px); height: calc(3.5rem + env(safe-area-inset-bottom, 0px));"
  aria-label="Mobile Navigation"
>
  {#each navItems as item}
    {@const active = isActive(item.href) && !mobileOpen}
    <a
      href={item.href}
      onclick={() => closeMobileNav()}
      class={`flex flex-col items-center justify-center flex-1 h-full py-1 text-[10px] transition-colors gap-0.5 ${
        active
          ? 'text-primary font-semibold'
          : 'text-muted-foreground hover:text-foreground'
      }`}
    >
      <div class={`p-1 rounded-full transition-transform ${active ? 'bg-primary/10 scale-105' : ''}`}>
        <item.icon size={18} class={`stroke-[1.8] ${active ? 'text-primary stroke-[2.2]' : ''}`} />
      </div>
      <span class="leading-none">{item.label}</span>
    </a>
  {/each}

  <!-- Menu Button for full drawer (Storage, Settings, Trash, Profile) -->
  <button
    type="button"
    onclick={() => toggleMobileNav()}
    class={`flex flex-col items-center justify-center flex-1 h-full py-1 text-[10px] transition-colors gap-0.5 ${
      mobileOpen
        ? 'text-primary font-semibold'
        : 'text-muted-foreground hover:text-foreground'
    }`}
    aria-label="Open full menu"
  >
    <div class={`p-1 rounded-full transition-transform ${mobileOpen ? 'bg-primary/10 scale-105' : ''}`}>
      <Menu size={18} class={`stroke-[1.8] ${mobileOpen ? 'text-primary stroke-[2.2]' : ''}`} />
    </div>
    <span class="leading-none">Menu</span>
  </button>
</nav>
