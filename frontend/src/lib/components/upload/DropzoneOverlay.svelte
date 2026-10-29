<script lang="ts">
  import { UploadCloud } from 'lucide-svelte';

  interface Props {
    isDragging: boolean;
  }

  let { isDragging }: Props = $props();
</script>

{#if isDragging}
  <div class="fixed inset-0 z-50 bg-background/90 backdrop-blur-none border-2 border-dashed border-primary flex flex-col items-center justify-center p-6 text-center select-none pointer-events-none subtle-fade">
    <div class="w-16 h-16 rounded-full bg-muted border border-border flex items-center justify-center mb-4 text-primary animate-bounce">
      <UploadCloud size={32} />
    </div>
    <h2 class="text-base font-semibold text-foreground">
      Drop Photographs & Media to Upload
    </h2>
    <p class="text-xs text-muted-foreground mt-1 max-w-sm">
      Files will be streamed directly to your private Backblaze B2 storage with metadata preservation.
    </p>
  </div>
{/if}
