<script lang="ts">
  import { auth } from '$lib/stores/auth';
  import { api } from '$lib/services/api';
  import { toast } from '$lib/stores/toast';

  let fullName = $state(auth.user?.full_name || '');
  let bio = $state(auth.user?.bio || '');
  let timezone = $state(auth.user?.timezone || 'UTC');
  let isSaving = $state(false);

  $effect(() => {
    if (auth.user) {
      fullName = auth.user.full_name || '';
      bio = auth.user.bio || '';
      timezone = auth.user.timezone || 'UTC';
    }
  });

  async function handleSave(e: Event) {
    e.preventDefault();
    isSaving = true;
    try {
      const updated = await api.auth.updateProfile({
        full_name: fullName,
        bio,
        timezone
      });
      if (auth.user) {
        auth.user.full_name = updated.full_name;
        auth.user.bio = updated.bio;
        auth.user.timezone = updated.timezone;
      }
      toast.success('Profile details saved successfully');
    } catch (err: unknown) {
      toast.error('Failed to update profile');
    } finally {
      isSaving = false;
    }
  }
</script>

<svelte:head>
  <title>Profile Settings — LensVault</title>
</svelte:head>

<div class="space-y-6 text-xs text-card-foreground">
  <div class="space-y-1">
    <h2 class="text-base font-semibold text-foreground">Photographer Profile</h2>
    <p class="text-muted-foreground">Manage your public studio identification and metadata defaults.</p>
  </div>

  <form onsubmit={handleSave} class="p-6 rounded border border-border bg-card space-y-4 shadow-sm">
    <div class="space-y-1.5">
      <label for="prof-email" class="font-medium text-foreground block">Email Address (Account Owner)</label>
      <input
        id="prof-email"
        type="email"
        disabled
        value={auth.user?.email || ''}
        class="w-full h-8 px-2.5 rounded border border-border bg-muted text-muted-foreground cursor-not-allowed"
      />
    </div>

    <div class="space-y-1.5">
      <label for="prof-name" class="font-medium text-foreground block">Full Display Name</label>
      <input
        id="prof-name"
        type="text"
        bind:value={fullName}
        required
        class="w-full h-8 px-2.5 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
      />
    </div>

    <div class="space-y-1.5">
      <label for="prof-bio" class="font-medium text-foreground block">Studio Bio & Artist Statement</label>
      <textarea
        id="prof-bio"
        bind:value={bio}
        rows="3"
        placeholder="Fine art portrait, commercial editorial, and destination wedding photography."
        class="w-full p-2.5 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
      ></textarea>
    </div>

    <div class="space-y-1.5">
      <label for="prof-tz" class="font-medium text-foreground block">Timezone</label>
      <select
        id="prof-tz"
        bind:value={timezone}
        class="w-full h-8 px-2.5 rounded border border-border bg-background text-foreground focus:outline-none focus:ring-1 focus:ring-ring"
      >
        <option value="UTC">UTC (Coordinated Universal Time)</option>
        <option value="America/New_York">America/New_York (Eastern Time)</option>
        <option value="America/Los_Angeles">America/Los_Angeles (Pacific Time)</option>
        <option value="Europe/London">Europe/London (GMT/BST)</option>
        <option value="Europe/Paris">Europe/Paris (CET)</option>
        <option value="Asia/Tokyo">Asia/Tokyo (JST)</option>
      </select>
    </div>

    <div class="pt-3 border-t border-border flex justify-end">
      <button
        type="submit"
        disabled={isSaving}
        class="px-4 py-1.5 rounded bg-primary text-primary-foreground font-medium hover:bg-primary/90 transition-colors disabled:opacity-50"
      >
        {isSaving ? 'Saving...' : 'Save Profile'}
      </button>
    </div>
  </form>
</div>
