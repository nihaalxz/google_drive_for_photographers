<script lang="ts">
  import './layout.css';
  import { onMount, type Snippet } from 'svelte';
  import { auth } from '$lib/stores/auth';
  import { uploadManager } from '$lib/services/uploadManager';
  import Toast from '$lib/components/ui/Toast.svelte';
  import DropzoneOverlay from '$lib/components/upload/DropzoneOverlay.svelte';
  import UploadManagerModal from '$lib/components/upload/UploadManagerModal.svelte';

  let { children }: { children: Snippet } = $props();

  let isDragging = $state(false);
  let dragCounter = 0;

  onMount(() => {
    auth.init();

    function handleDragEnter(e: DragEvent) {
      if (e.dataTransfer && e.dataTransfer.types.includes('Files')) {
        dragCounter++;
        isDragging = true;
      }
    }

    function handleDragLeave() {
      dragCounter--;
      if (dragCounter <= 0) {
        isDragging = false;
        dragCounter = 0;
      }
    }

    function handleDragOver(e: DragEvent) {
      e.preventDefault();
    }

    function handleDrop(e: DragEvent) {
      e.preventDefault();
      isDragging = false;
      dragCounter = 0;

      if (e.dataTransfer && e.dataTransfer.files.length > 0 && auth.activeWorkspace) {
        uploadManager.enqueue(e.dataTransfer.files, auth.activeWorkspace.id);
      }
    }

    window.addEventListener('dragenter', handleDragEnter);
    window.addEventListener('dragleave', handleDragLeave);
    window.addEventListener('dragover', handleDragOver);
    window.addEventListener('drop', handleDrop);

    return () => {
      window.removeEventListener('dragenter', handleDragEnter);
      window.removeEventListener('dragleave', handleDragLeave);
      window.removeEventListener('dragover', handleDragOver);
      window.removeEventListener('drop', handleDrop);
    };
  });
</script>

<svelte:head>
  <title>LensVault — Cloud Storage for Photographers</title>
  <meta name="description" content="Professional cloud storage, direct-to-B2 S3 uploads, RAW preservation, and client delivery galleries for photographers." />
</svelte:head>

<div class="min-h-screen bg-background text-foreground flex flex-col">
  {@render children()}
</div>

<Toast />
<DropzoneOverlay {isDragging} />
<UploadManagerModal />
