<script lang="ts">
  import { onMount } from 'svelte';
  import QRCode from 'qrcode';
  import {
    X,
    Printer,
    Download,
    QrCode,
    Sparkles,
    Copy,
    Check,
    Sliders,
    Type,
    FileText
  } from 'lucide-svelte';
  import { toast } from '../../stores/toast';

  interface Props {
    isOpen: boolean;
    url: string;
    initialTitle?: string;
    initialSubtitle?: string;
    studioName?: string;
    hasPassword?: boolean;
    onClose: () => void;
  }

  let {
    isOpen,
    url,
    initialTitle = 'Photo Gallery',
    initialSubtitle = 'Scan with your phone camera to view and download full-resolution photographs.',
    studioName = 'LensVault Studio',
    hasPassword = false,
    onClose
  }: Props = $props();

  // Customization Form State
  let headerTitle = $state('');
  let customTextUnderneath = $state('');
  let footerStudioText = $state('');
  let accessNote = $state('');
  let cardStyle = $state<'modern' | 'luxury' | 'table_tent'>('luxury');

  // QR output state
  let qrDataUrl = $state<string>('');
  let isGenerating = $state(true);
  let isCopied = $state(false);

  // Initialize form defaults when opened or url changes
  let prevOpen = false;
  let prevUrl = '';

  $effect(() => {
    if (isOpen && (!prevOpen || url !== prevUrl)) {
      prevOpen = true;
      prevUrl = url;
      headerTitle = initialTitle || 'Client Photo Gallery';
      customTextUnderneath = initialSubtitle || 'Scan with your camera to view & download our gallery.';
      footerStudioText = studioName || 'LensVault Photography';
      accessNote = hasPassword ? 'Access Passcode Required' : '';
      generateQr(url);
    } else if (!isOpen) {
      prevOpen = false;
    }
  });

  async function generateQr(targetUrl: string) {
    if (!targetUrl) return;
    isGenerating = true;
    try {
      const dataUrl = await QRCode.toDataURL(targetUrl, {
        width: 800,
        margin: 1,
        errorCorrectionLevel: 'H',
        color: {
          dark: '#000000',
          light: '#ffffff'
        }
      });
      qrDataUrl = dataUrl;
    } catch (err: unknown) {
      toast.error('Failed to generate QR code');
    } finally {
      isGenerating = false;
    }
  }

  function handlePrint() {
    window.print();
  }

  async function handleDownloadCard() {
    if (!qrDataUrl) return;

    try {
      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      // Card dimensions: 1200 x 1600 (High Resolution 3:4 ratio for crisp printing)
      const w = 1200;
      const h = 1600;
      canvas.width = w;
      canvas.height = h;

      // Background
      ctx.fillStyle = '#ffffff';
      ctx.fillRect(0, 0, w, h);

      // Decorative Frame for Luxury style
      if (cardStyle === 'luxury') {
        ctx.strokeStyle = '#27272a';
        ctx.lineWidth = 4;
        ctx.strokeRect(60, 60, w - 120, h - 120);

        ctx.strokeStyle = '#d4d4d8';
        ctx.lineWidth = 1.5;
        ctx.strokeRect(74, 74, w - 148, h - 148);
      } else if (cardStyle === 'modern') {
        ctx.strokeStyle = '#e4e4e7';
        ctx.lineWidth = 2;
        ctx.strokeRect(40, 40, w - 80, h - 80);
      }

      // Title
      ctx.fillStyle = '#09090b';
      ctx.textAlign = 'center';
      ctx.font = cardStyle === 'luxury' ? 'italic bold 52px Georgia, serif' : 'bold 48px -apple-system, BlinkMacSystemFont, sans-serif';
      
      const titleLines = wrapText(ctx, headerTitle, w - 240);
      let textY = 220;
      for (const line of titleLines.slice(0, 2)) {
        ctx.fillText(line, w / 2, textY);
        textY += 65;
      }

      // Draw QR Code in Center
      const qrImg = new Image();
      await new Promise<void>((resolve, reject) => {
        qrImg.onload = () => resolve();
        qrImg.onerror = () => reject(new Error('QR image load error'));
        qrImg.src = qrDataUrl;
      });

      const qrSize = 580;
      const qrX = (w - qrSize) / 2;
      const qrY = textY + 40;
      ctx.drawImage(qrImg, qrX, qrY, qrSize, qrSize);

      // Text Underneath
      ctx.fillStyle = '#27272a';
      ctx.font = cardStyle === 'luxury' ? '500 32px Georgia, serif' : '500 30px -apple-system, BlinkMacSystemFont, sans-serif';

      const underLines = wrapText(ctx, customTextUnderneath, w - 260);
      let underY = qrY + qrSize + 70;
      for (const line of underLines.slice(0, 4)) {
        ctx.fillText(line, w / 2, underY);
        underY += 46;
      }

      // Access Note (if provided)
      if (accessNote.trim()) {
        ctx.fillStyle = '#71717a';
        ctx.font = '600 24px monospace';
        ctx.fillText(accessNote.trim(), w / 2, underY + 25);
        underY += 50;
      }

      // Footer Studio Name
      if (footerStudioText.trim()) {
        ctx.fillStyle = '#71717a';
        ctx.font = '600 22px -apple-system, BlinkMacSystemFont, sans-serif';
        ctx.letterSpacing = '2px';
        ctx.fillText(footerStudioText.trim().toUpperCase(), w / 2, h - 110);
      }

      // Download Trigger
      const downloadLink = document.createElement('a');
      const safeFilename = (headerTitle || 'gallery').replace(/[^a-z0-9_-]/gi, '_').toLowerCase();
      downloadLink.download = `${safeFilename}_qr_code.png`;
      downloadLink.href = canvas.toDataURL('image/png');
      downloadLink.click();

      toast.success('Printable QR Card image downloaded');
    } catch (err: unknown) {
      toast.error('Failed to generate high-res image download');
    }
  }

  function wrapText(ctx: CanvasRenderingContext2D, text: string, maxWidth: number): string[] {
    if (!text) return [];
    const paragraphs = text.split('\n');
    const allLines: string[] = [];

    for (const paragraph of paragraphs) {
      const trimmed = paragraph.trim();
      if (!trimmed) {
        allLines.push('');
        continue;
      }
      const words = trimmed.split(/\s+/);
      let currentLine = words[0] || '';

      for (let i = 1; i < words.length; i++) {
        const word = words[i];
        const width = ctx.measureText(currentLine + ' ' + word).width;
        if (width < maxWidth) {
          currentLine += ' ' + word;
        } else {
          allLines.push(currentLine);
          currentLine = word;
        }
      }
      if (currentLine) allLines.push(currentLine);
    }
    return allLines;
  }

  function copyShareUrl() {
    navigator.clipboard.writeText(url);
    isCopied = true;
    toast.info('Link copied to clipboard');
    setTimeout(() => isCopied = false, 2500);
  }
</script>

{#if isOpen}
  <div class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 printable-modal-root">
    <!-- Backdrop (hidden on print) -->
    <button
      onclick={onClose}
      class="fixed inset-0 bg-black/75 transition-opacity print:hidden"
      aria-label="Close modal overlay"
    ></button>

    <!-- Modal Dialog (on screen) -->
    <div
      role="dialog"
      aria-modal="true"
      class="relative w-full max-w-4xl rounded-xl border border-border bg-card shadow-2xl z-10 flex flex-col md:flex-row max-h-[92vh] text-card-foreground text-xs subtle-fade overflow-hidden print:m-0 print:p-0 print:border-none print:shadow-none print:max-h-none print:w-full print:bg-white"
    >
      <!-- LEFT / TOP: Customization Controls (Hidden during print) -->
      <div class="w-full md:w-96 p-4 sm:p-5 border-b md:border-b-0 md:border-r border-border overflow-y-auto space-y-4 print:hidden shrink-0 bg-muted/10">
        <div class="flex items-center justify-between border-b border-border pb-3">
          <div class="flex items-center gap-2 font-semibold text-sm text-foreground">
            <QrCode size={18} class="text-primary" />
            <h2>Printable QR Code Card</h2>
          </div>
          <button
            onclick={onClose}
            class="p-1.5 rounded text-muted-foreground hover:text-foreground hover:bg-muted transition-colors md:hidden"
            aria-label="Close"
          >
            <X size={16} />
          </button>
        </div>

        <!-- Customization Fields -->
        <div class="space-y-3">
          <div class="space-y-1">
            <label for="qr-title" class="font-medium text-foreground block">
              Card Headline / Event Name
            </label>
            <input
              id="qr-title"
              type="text"
              bind:value={headerTitle}
              placeholder="e.g. Sarah & James — Lake Como"
              class="w-full h-8 px-2.5 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            />
          </div>

          <div class="space-y-1">
            <label for="qr-text" class="font-medium text-foreground block">
              Text Underneath QR Code (Customizable)
            </label>
            <textarea
              id="qr-text"
              rows="3"
              bind:value={customTextUnderneath}
              placeholder="e.g. Scan with your phone to view and download full-resolution client photos."
              class="w-full p-2 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring resize-none leading-relaxed"
            ></textarea>
            <span class="text-[10px] text-muted-foreground block">
              Displays directly below the QR code for guest instructions.
            </span>
          </div>

          <div class="space-y-1">
            <label for="qr-note" class="font-medium text-foreground block">
              Access Note / Passcode Notice (Optional)
            </label>
            <input
              id="qr-note"
              type="text"
              bind:value={accessNote}
              placeholder="e.g. Passcode: 2026 or Open Access"
              class="w-full h-8 px-2.5 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring font-mono text-[11px]"
            />
          </div>

          <div class="space-y-1">
            <label for="qr-studio" class="font-medium text-foreground block">
              Studio / Footer Branding
            </label>
            <input
              id="qr-studio"
              type="text"
              bind:value={footerStudioText}
              placeholder="e.g. Elena Rostova Photography"
              class="w-full h-8 px-2.5 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
            />
          </div>

          <!-- Card Style Selector -->
          <div class="space-y-1.5 pt-1">
            <span class="font-medium text-foreground block">Print Design Template</span>
            <div class="grid grid-cols-3 gap-1.5">
              <button
                type="button"
                onclick={() => cardStyle = 'luxury'}
                class={`p-2 rounded border text-center transition-colors ${
                  cardStyle === 'luxury'
                    ? 'border-foreground font-semibold bg-foreground/10 text-foreground ring-1 ring-foreground'
                    : 'border-border text-muted-foreground hover:text-foreground'
                }`}
              >
                Luxury Serif
              </button>
              <button
                type="button"
                onclick={() => cardStyle = 'modern'}
                class={`p-2 rounded border text-center transition-colors ${
                  cardStyle === 'modern'
                    ? 'border-foreground font-semibold bg-foreground/10 text-foreground ring-1 ring-foreground'
                    : 'border-border text-muted-foreground hover:text-foreground'
                }`}
              >
                Clean Modern
              </button>
              <button
                type="button"
                onclick={() => cardStyle = 'table_tent'}
                class={`p-2 rounded border text-center transition-colors ${
                  cardStyle === 'table_tent'
                    ? 'border-foreground font-semibold bg-foreground/10 text-foreground ring-1 ring-foreground'
                    : 'border-border text-muted-foreground hover:text-foreground'
                }`}
              >
                Table Tent
              </button>
            </div>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="pt-3 border-t border-border space-y-2">
          <button
            type="button"
            onclick={handlePrint}
            class="w-full h-9 rounded bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors flex items-center justify-center gap-2 shadow-sm text-xs"
          >
            <Printer size={15} />
            <span>Print QR Card (Letter / A4 / 4x6)</span>
          </button>

          <button
            type="button"
            onclick={handleDownloadCard}
            class="w-full h-8 rounded border border-border bg-background hover:bg-muted text-foreground transition-colors flex items-center justify-center gap-1.5 text-xs font-medium"
          >
            <Download size={14} />
            <span>Download High-Res PNG</span>
          </button>

          <button
            type="button"
            onclick={copyShareUrl}
            class="w-full h-8 rounded border border-border bg-background hover:bg-muted text-muted-foreground hover:text-foreground transition-colors flex items-center justify-center gap-1.5 text-xs"
          >
            {#if isCopied}
              <Check size={13} class="text-emerald-500" />
              <span class="text-emerald-500">Copied Link</span>
            {:else}
              <Copy size={13} />
              <span>Copy Link Only</span>
            {/if}
          </button>
        </div>
      </div>

      <!-- RIGHT: Interactive Live Printable Preview -->
      <div class="flex-1 flex flex-col bg-muted/30 p-4 sm:p-6 overflow-y-auto items-center justify-center print:p-0 print:bg-white print:m-0 print:w-full">
        <div class="w-full flex items-center justify-between pb-3 print:hidden">
          <span class="text-xs font-medium text-muted-foreground flex items-center gap-1.5">
            <Sparkles size={13} class="text-primary" />
            <span>Live Print Preview</span>
          </span>
          <button
            onclick={onClose}
            class="hidden md:flex p-1.5 rounded text-muted-foreground hover:text-foreground hover:bg-muted transition-colors"
            aria-label="Close dialog"
          >
            <X size={18} />
          </button>
        </div>

        <!-- Physical Card Container to Print -->
        <div
          id="printable-qr-card"
          class={`w-full max-w-sm sm:max-w-md bg-white text-zinc-900 rounded-lg p-6 sm:p-8 flex flex-col items-center text-center space-y-4 shadow-xl transition-all print:shadow-none print:border-none print:m-auto print:max-w-none print:w-[85mm] print:p-6 ${
            cardStyle === 'luxury'
              ? 'border-2 border-zinc-800 ring-1 ring-zinc-300 ring-offset-4 ring-offset-white font-serif'
              : cardStyle === 'table_tent'
                ? 'border-2 border-dashed border-zinc-400 font-sans'
                : 'border border-zinc-300 font-sans shadow-md'
          }`}
        >
          <!-- Table tent indicator -->
          {#if cardStyle === 'table_tent'}
            <div class="text-[9px] uppercase tracking-widest text-zinc-400 font-mono border-b border-dashed border-zinc-300 pb-1 w-full print:block">
              Fold Here for Table Tent Stand
            </div>
          {/if}

          <!-- Header Title -->
          <div class="space-y-1 w-full">
            <h3 class={`text-lg sm:text-xl font-bold tracking-tight text-zinc-900 leading-snug px-2 ${
              cardStyle === 'luxury' ? 'italic font-serif' : 'font-sans'
            }`}>
              {headerTitle || 'Photo Gallery'}
            </h3>
          </div>

          <!-- Sharp QR Code -->
          <div class="p-3 bg-white border border-zinc-200 rounded-md shadow-xs flex items-center justify-center">
            {#if qrDataUrl}
              <img
                src={qrDataUrl}
                alt="Gallery Access QR Code"
                class="w-48 h-48 sm:w-56 sm:h-56 object-contain"
              />
            {:else}
              <div class="w-48 h-48 flex items-center justify-center text-zinc-400">
                <QrCode size={40} />
              </div>
            {/if}
          </div>

          <!-- Text Underneath (Customizable) -->
          <div class="space-y-2 max-w-xs px-2">
            <p class="text-xs sm:text-sm text-zinc-700 leading-relaxed font-medium">
              {customTextUnderneath}
            </p>

            {#if accessNote.trim()}
              <div class="inline-block px-2.5 py-1 rounded bg-zinc-100 border border-zinc-200 text-zinc-800 text-[11px] font-mono font-semibold">
                {accessNote}
              </div>
            {/if}
          </div>

          <!-- Studio Footer Branding -->
          {#if footerStudioText.trim()}
            <div class="pt-3 border-t border-zinc-200 w-full text-[10px] sm:text-[11px] uppercase tracking-widest text-zinc-500 font-mono">
              {footerStudioText}
            </div>
          {/if}
        </div>
      </div>
    </div>
  </div>
{/if}

<style>
  @media print {
    :global(body) {
      background: #ffffff !important;
      color: #000000 !important;
    }

    /* Hide everything on screen except the printable QR card container */
    :global(body *) {
      visibility: hidden !important;
    }

    :global(.printable-modal-root),
    :global(.printable-modal-root *) {
      overflow: visible !important;
    }

    :global(#printable-qr-card),
    :global(#printable-qr-card *) {
      visibility: visible !important;
    }

    :global(#printable-qr-card) {
      position: fixed !important;
      left: 50% !important;
      top: 50% !important;
      transform: translate(-50%, -50%) !important;
      margin: 0 !important;
      background: #ffffff !important;
      color: #000000 !important;
      box-shadow: none !important;
      border: 1.5px solid #18181b !important;
      padding: 32px !important;
      width: 100% !important;
      max-width: 440px !important;
      -webkit-print-color-adjust: exact !important;
      print-color-adjust: exact !important;
    }

    @page {
      margin: 1cm;
      size: auto;
    }
  }
</style>
