<script lang="ts">
  import { X, FolderPlus } from 'lucide-svelte';

  interface Props {
    isOpen: boolean;
    onClose: () => void;
    onSubmit: (name: string, color: string) => Promise<void>;
  }

  let { isOpen, onClose, onSubmit }: Props = $props();

  let folderName = $state('');
  let selectedColor = $state('#3b82f6');
  let isSubmitting = $state(false);
  let error = $state('');

  const colors = [
    { label: 'Slate', value: '#64748b' },
    { label: 'Blue', value: '#3b82f6' },
    { label: 'Emerald', value: '#10b981' },
    { label: 'Amber', value: '#f59e0b' },
    { label: 'Rose', value: '#f43f5e' },
    { label: 'Indigo', value: '#6366f1' },
  ];

  async function handleSubmit(e: Event) {
    e.preventDefault();
    const trimmed = folderName.trim();
    if (!trimmed) {
      error = 'Please enter a folder name.';
      return;
    }
    error = '';
    isSubmitting = true;
    try {
      await onSubmit(trimmed, selectedColor);
      folderName = '';
      onClose();
    } catch (err: unknown) {
      error = err instanceof Error ? err.message : 'Failed to create folder.';
    } finally {
      isSubmitting = false;
    }
  }
</script>

{#if isOpen}
  <div class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <!-- Backdrop -->
    <button
      onclick={onClose}
      class="fixed inset-0 bg-black/60 transition-opacity"
      aria-label="Close dialog overlay"
    ></button>

    <!-- Dialog Body -->
    <div
      role="dialog"
      aria-modal="true"
      aria-labelledby="new-folder-title"
      class="relative w-full max-w-md rounded-md border border-border bg-card p-4 sm:p-5 shadow-lg text-card-foreground text-sm z-10 space-y-4 subtle-fade max-h-[90vh] overflow-y-auto"
    >
      <div class="flex items-center justify-between border-b border-border pb-3">
        <div class="flex items-center gap-2 font-semibold text-foreground">
          <FolderPlus size={18} />
          <h2 id="new-folder-title">Create New Folder</h2>
        </div>
        <button
          onclick={onClose}
          class="p-1 rounded text-muted-foreground hover:text-foreground transition-colors"
          aria-label="Close dialog"
        >
          <X size={16} />
        </button>
      </div>

      <form onsubmit={handleSubmit} class="space-y-4">
        {#if error}
          <div class="p-2.5 rounded bg-destructive/10 border border-destructive/20 text-destructive text-xs">
            {error}
          </div>
        {/if}

        <div class="space-y-1.5">
          <label for="folder-name-input" class="text-xs font-medium text-foreground">
            Folder Name
          </label>
          <input
            id="folder-name-input"
            type="text"
            bind:value={folderName}
            placeholder="e.g. Sarah & James - Reception"
            class="w-full h-9 px-3 rounded border border-border bg-background text-foreground text-xs placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            autofocus
            required
          />
        </div>

        <div class="space-y-1.5">
          <label class="text-xs font-medium text-foreground block">
            Folder Accent Tag
          </label>
          <div class="flex items-center gap-2">
            {#each colors as c}
              <button
                type="button"
                onclick={() => selectedColor = c.value}
                class={`w-6 h-6 rounded-full border transition-all ${
                  selectedColor === c.value ? 'ring-2 ring-foreground ring-offset-2 scale-110' : 'border-border'
                }`}
                style={`background-color: ${c.value}`}
                title={c.label}
                aria-label={`Select ${c.label} color`}
              ></button>
            {/each}
          </div>
        </div>

        <div class="flex items-center justify-end gap-2 pt-2 border-t border-border">
          <button
            type="button"
            onclick={onClose}
            class="px-3 py-1.5 rounded border border-border bg-background hover:bg-muted text-xs text-foreground transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            disabled={isSubmitting}
            class="px-4 py-1.5 rounded bg-primary text-primary-foreground hover:bg-primary/90 text-xs font-medium transition-colors disabled:opacity-50"
          >
            {isSubmitting ? 'Creating...' : 'Create Folder'}
          </button>
        </div>
      </form>
    </div>
  </div>
{/if}
