<script lang="ts">
  import ThemeToggle from '$lib/components/layout/ThemeToggle.svelte';
  import { Aperture, ArrowLeft, Mail, CheckCircle2 } from 'lucide-svelte';

  let email = $state('');
  let isSent = $state(false);

  function handleSubmit(e: Event) {
    e.preventDefault();
    isSent = true;
  }
</script>

<svelte:head>
  <title>Reset Password — LensVault</title>
</svelte:head>

<div class="min-h-screen flex flex-col justify-center items-center p-4 bg-background">
  <div class="absolute top-4 right-4">
    <ThemeToggle />
  </div>

  <div class="w-full max-w-sm space-y-6">
    <div class="text-center space-y-2">
      <div class="w-10 h-10 rounded bg-foreground text-background flex items-center justify-center mx-auto mb-3">
        <Aperture size={24} class="stroke-[2.2]" />
      </div>
      <h1 class="text-xl font-bold tracking-tight text-foreground">Forgot Password</h1>
      <p class="text-xs text-muted-foreground">We'll send password recovery instructions to your email</p>
    </div>

    <div class="p-6 rounded-md border border-border bg-card space-y-4 shadow-sm text-xs">
      {#if isSent}
        <div class="space-y-3 text-center py-2">
          <CheckCircle2 size={32} class="text-emerald-500 mx-auto" />
          <h2 class="font-semibold text-foreground text-sm">Recovery Link Sent</h2>
          <p class="text-muted-foreground leading-relaxed">
            If an account exists for <strong class="text-foreground">{email}</strong>, you will receive password reset instructions shortly.
          </p>
          <a
            href="/reset-password"
            class="inline-block mt-2 text-primary font-medium hover:underline text-xs"
          >
            Enter reset code or token →
          </a>
        </div>
      {:else}
        <form onsubmit={handleSubmit} class="space-y-4">
          <div class="space-y-1.5">
            <label for="fp-email" class="font-medium text-foreground block">Registered Email Address</label>
            <div class="relative">
              <Mail size={15} class="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
              <input
                id="fp-email"
                type="email"
                bind:value={email}
                required
                placeholder="photographer@example.com"
                class="w-full h-9 pl-9 pr-3 rounded border border-border bg-background text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-ring"
              />
            </div>
          </div>

          <button
            type="submit"
            class="w-full h-9 rounded bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors shadow-sm"
          >
            Send Recovery Email
          </button>
        </form>
      {/if}
    </div>

    <div class="text-center text-xs">
      <a href="/login" class="inline-flex items-center gap-1.5 text-muted-foreground hover:text-foreground font-medium">
        <ArrowLeft size={13} />
        <span>Back to Sign In</span>
      </a>
    </div>
  </div>
</div>
