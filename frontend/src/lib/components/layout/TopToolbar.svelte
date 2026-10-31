<script lang="ts">
  import { auth } from '../../stores/auth';
  import { uploadManager, type UploadManagerState } from '../../services/uploadManager';
  import { toggleMobileNav } from '../../stores/ui';
  import ThemeToggle from './ThemeToggle.svelte';
  import {
    Search,
    UploadCloud,
    FolderPlus,
    LayoutGrid,
    List,
    ArrowUpDown,
    Check,
    Menu
  } from 'lucide-svelte';

  interface Props {
    searchQuery?: string;
    viewMode?: 'grid' | 'list';
    sortBy?: string;
    sortDirection?: 'asc' | 'desc';
    onSearchChange?: (q: string) => void;
    onViewModeChange?: (mode: 'grid' | 'list') => void;
    onSortChange?: (by: string, dir: 'asc' | 'desc') => void;
    onNewFolderClick?: () => void;
    onUploadClick?: () => void;
  }

  let {
    searchQuery = $bindable(''),
    viewMode = $bindable('grid'),
    sortBy = $bindable('created_at'),
    sortDirection = $bindable('desc'),
    onSearchChange,
    onViewModeChange,
    onSortChange,
    onNewFolderClick,
    onUploadClick
  }: Props = $props();

  let isSortOpen = $state(false);
  let internalFileInput = $state<HTMLInputElement>();

  let uploadState = $state<UploadManagerState>({ items: [], isOpen: false, activeCount: 0, totalProgress: 0 });
  uploadManager.subscribe(s => {
    uploadState = s;
  });

  const sortOptions = [
    { label: 'Date Modified (Newest)', by: 'updated_at', dir: 'desc' as const },
    { label: 'Date Modified (Oldest)', by: 'updated_at', dir: 'asc' as const },
    { label: 'Date Uploaded (Newest)', by: 'created_at', dir: 'desc' as const },
    { label: 'Name (A to Z)', by: 'name', dir: 'asc' as const },
    { label: 'Name (Z to A)', by: 'name', dir: 'desc' as const },
    { label: 'File Size (Largest)', by: 'size', dir: 'desc' as const },
    { label: 'File Size (Smallest)', by: 'size', dir: 'asc' as const },
  ];

  function handleSortSelect(by: string, dir: 'asc' | 'desc') {
    sortBy = by;
    sortDirection = dir;
    isSortOpen = false;
    if (onSortChange) onSortChange(by, dir);
  }

  function handleSearchInput(e: Event) {
    const val = (e.target as HTMLInputElement).value;
    searchQuery = val;
    if (onSearchChange) onSearchChange(val);
  }

  function triggerUpload() {
    if (onUploadClick) {
      onUploadClick();
    } else {
      internalFileInput?.click();
    }
  }

  function handleInternalFiles(e: Event) {
    const target = e.target as HTMLInputElement;
    if (target.files && target.files.length > 0 && auth.activeWorkspace) {
      uploadManager.enqueue(target.files, auth.activeWorkspace.id);
      target.value = '';
    }
  }
</script>

<!-- Hidden fallback file input -->
<input
  type="file"
  multiple
  bind:this={internalFileInput}
  onchange={handleInternalFiles}
  class="hidden"
  aria-hidden="true"
/>

<!-- SVG Gooey Filter definition for restrained status indicators -->
<svg class="sr-only" aria-hidden="true">
  <defs>
    <filter id="gooey-filter">
      <feGaussianBlur in="SourceGraphic" stdDeviation="2.5" result="blur" />
      <feColorMatrix in="blur" mode="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 18 -7" result="goo" />
      <feBlend in="SourceGraphic" in2="goo" />
    </filter>
  </defs>
</svg>

<header class="h-14 border-b border-border bg-card px-2.5 sm:px-4 flex items-center justify-between gap-1.5 sm:gap-3 sticky top-0 z-20 select-none">
  <!-- Left: Hamburger Menu + Search Box -->
  <div class="flex items-center gap-1.5 sm:gap-2.5 flex-1 min-w-0">
    <button
      type="button"
      onclick={toggleMobileNav}
      class="lg:hidden p-1.5 rounded border border-border bg-background hover:bg-muted text-foreground transition-colors shrink-0"
      title="Open navigation menu"
      aria-label="Open navigation menu"
    >
      <Menu size={18} />
    </button>

    <!-- Search Box -->
    <div class="flex-1 max-w-[170px] xs:max-w-[220px] sm:max-w-xs md:max-w-md relative min-w-0">
      <Search size={14} class="absolute left-2.5 sm:left-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
      <input
        type="search"
        value={searchQuery}
        oninput={handleSearchInput}
        placeholder="Search photos, folders..."
        class="w-full h-8 pl-7 sm:pl-9 pr-2.5 sm:pr-3 text-xs rounded border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring transition-colors truncate"
        aria-label="Search files and folders"
      />
    </div>
  </div>

  <!-- Right: Actions & Tools -->
  <div class="flex items-center gap-1 sm:gap-2 shrink-0">
    <!-- Upload Status Pill (if uploads active or in progress) -->
    {#if uploadState.items.length > 0}
      <button
        onclick={() => uploadManager.toggleOpen()}
        class="flex items-center gap-1.5 h-8 px-1.5 sm:px-2 rounded border border-border bg-background hover:bg-muted text-xs text-foreground transition-colors shrink-0"
        title="View Upload Manager"
        aria-label="View upload progress"
      >
        <div class="relative flex items-center justify-center">
          <UploadCloud size={14} class="text-primary" />
          {#if uploadState.activeCount > 0}
            <span class="absolute -top-1 -right-1 w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
          {/if}
        </div>
        <span class="font-medium text-[11px]">{uploadState.totalProgress}%</span>
      </button>
    {/if}

    <!-- New Folder Action -->
    <button
      onclick={() => onNewFolderClick && onNewFolderClick()}
      class="inline-flex items-center justify-center h-8 w-8 sm:w-auto sm:px-2.5 rounded border border-border bg-background hover:bg-muted text-xs text-foreground transition-colors font-medium shrink-0"
      title="Create New Folder"
      aria-label="Create New Folder"
    >
      <FolderPlus size={15} />
      <span class="hidden md:inline">New Folder</span>
    </button>

    <!-- Upload Files Action -->
    <button
      onclick={triggerUpload}
      class="inline-flex items-center justify-center gap-1.5 h-8 w-8 sm:w-auto sm:px-3 rounded bg-primary text-primary-foreground hover:bg-primary/90 text-xs font-medium transition-colors shadow-xs shrink-0"
      title="Upload Photos & Media"
      aria-label="Upload Photos & Media"
    >
      <UploadCloud size={15} />
      <span class="hidden sm:inline font-medium">Upload</span>
    </button>

    <!-- View Mode Switcher -->
    <div class="hidden xs:inline-flex rounded border border-border p-0.5 bg-background shrink-0">
      <button
        onclick={() => { viewMode = 'grid'; if (onViewModeChange) onViewModeChange('grid'); }}
        class={`p-1.5 rounded text-xs transition-colors ${viewMode === 'grid' ? 'bg-foreground text-background font-semibold shadow-xs' : 'text-muted-foreground hover:text-foreground hover:bg-muted'}`}
        title="Grid View"
        aria-label="Switch to grid view"
      >
        <LayoutGrid size={14} />
      </button>
      <button
        onclick={() => { viewMode = 'list'; if (onViewModeChange) onViewModeChange('list'); }}
        class={`p-1.5 rounded text-xs transition-colors ${viewMode === 'list' ? 'bg-foreground text-background font-semibold shadow-xs' : 'text-muted-foreground hover:text-foreground hover:bg-muted'}`}
        title="List View"
        aria-label="Switch to list view"
      >
        <List size={14} />
      </button>
    </div>

    <!-- Sorting Dropdown -->
    <div class="relative shrink-0">
      <button
        onclick={() => isSortOpen = !isSortOpen}
        class="inline-flex items-center justify-center w-8 h-8 rounded border border-border bg-background hover:bg-muted text-xs text-muted-foreground hover:text-foreground transition-colors"
        title="Sort Options"
        aria-label="Open sorting options"
      >
        <ArrowUpDown size={15} />
      </button>

      {#if isSortOpen}
        <button
          onclick={() => isSortOpen = false}
          class="fixed inset-0 z-40 bg-transparent"
          aria-label="Close sort menu overlay"
        ></button>
        <div class="absolute right-0 top-full mt-1.5 w-56 rounded border border-border bg-card p-1 shadow-xl z-50 text-xs">
          <div class="px-2 py-1 text-[11px] font-semibold text-muted-foreground uppercase tracking-wider border-b border-border mb-1">
            Sort Items By
          </div>
          {#each sortOptions as opt}
            {@const isSelected = sortBy === opt.by && sortDirection === opt.dir}
            <button
              onclick={() => handleSortSelect(opt.by, opt.dir)}
              class={`w-full flex items-center justify-between px-2.5 py-1.5 rounded text-left transition-colors ${
                isSelected ? 'bg-muted text-foreground font-medium' : 'text-muted-foreground hover:bg-muted/50 hover:text-foreground'
              }`}
            >
              <span>{opt.label}</span>
              {#if isSelected}
                <Check size={14} class="text-foreground shrink-0" />
              {/if}
            </button>
          {/each}
        </div>
      {/if}
    </div>

    <div class="h-4 w-px bg-border mx-0.5"></div>

    <!-- Theme Toggle -->
    <ThemeToggle />
  </div>
</header>
