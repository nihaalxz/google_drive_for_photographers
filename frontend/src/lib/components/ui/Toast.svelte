<script lang="ts">
  import { toast, type ToastMessage } from '../../stores/toast';
  import { CheckCircle2, AlertCircle, Info, X } from 'lucide-svelte';

  let toasts: ToastMessage[] = $state([]);

  toast.subscribe(value => {
    toasts = value;
  });
</script>

<div class="fixed bottom-4 right-4 z-50 flex flex-col gap-2 max-w-sm w-full pointer-events-none" aria-live="polite">
  {#each toasts as t (t.id)}
    <div
      class="pointer-events-auto flex items-start gap-3 p-3.5 rounded-md border shadow-sm text-sm bg-card text-card-foreground border-border subtle-fade"
      role="status"
    >
      <div class="shrink-0 mt-0.5">
        {#if t.type === 'success'}
          <CheckCircle2 size={18} class="text-emerald-500" />
        {:else if t.type === 'error'}
          <AlertCircle size={18} class="text-destructive" />
        {:else if t.type === 'warning'}
          <AlertCircle size={18} class="text-amber-500" />
        {:else}
          <Info size={18} class="text-primary" />
        {/if}
      </div>

      <div class="flex-1 min-w-0">
        {#if t.title}
          <div class="font-medium text-xs tracking-wide uppercase text-muted-foreground mb-0.5">{t.title}</div>
        {/if}
        <div class="text-foreground leading-snug">{t.message}</div>
      </div>

      <button
        onclick={() => toast.dismiss(t.id)}
        class="shrink-0 text-muted-foreground hover:text-foreground transition-colors p-0.5 rounded"
        aria-label="Dismiss notification"
      >
        <X size={14} />
      </button>
    </div>
  {/each}
</div>
