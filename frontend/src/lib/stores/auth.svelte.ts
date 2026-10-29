import { api } from '../services/api';
import type { User, Workspace } from '../types';

export interface AuthState {
  user: User | null;
  activeWorkspace: Workspace | null;
  workspaces: Workspace[];
  loading: boolean;
  initialized: boolean;
}

class AuthStore {
  user = $state<User | null>(null);
  activeWorkspace = $state<Workspace | null>(null);
  workspaces = $state<Workspace[]>([]);
  loading = $state<boolean>(false);
  initialized = $state<boolean>(false);

  private initPromise: Promise<{ user: User; workspaces: Workspace[]; active_workspace: Workspace | null } | null> | null = null;

  async init() {
    if (this.initialized) {
      return this.user ? { user: this.user, workspaces: this.workspaces, active_workspace: this.activeWorkspace } : null;
    }
    if (this.initPromise) {
      return this.initPromise;
    }

    this.loading = true;
    this.initPromise = (async () => {
      try {
        const res = await api.auth.me();
        this.user = res.user;
        this.workspaces = res.workspaces;
        this.activeWorkspace = res.active_workspace || (res.workspaces.length > 0 ? res.workspaces[0] : null);
        this.loading = false;
        this.initialized = true;
        return res;
      } catch {
        this.user = null;
        this.workspaces = [];
        this.activeWorkspace = null;
        this.loading = false;
        this.initialized = true;
        return null;
      } finally {
        this.initPromise = null;
      }
    })();

    return this.initPromise;
  }

  setUserAndWorkspace(user: User, activeWorkspace: Workspace | null, workspaces: Workspace[] = []) {
    this.user = user;
    this.activeWorkspace = activeWorkspace;
    this.workspaces = workspaces.length > 0 ? workspaces : (activeWorkspace ? [activeWorkspace] : []);
    this.loading = false;
    this.initialized = true;
  }

  setActiveWorkspace(workspace: Workspace) {
    this.activeWorkspace = workspace;
  }

  async refreshWorkspace() {
    if (!this.activeWorkspace) return;
    try {
      const ws = await api.workspaces.get(this.activeWorkspace.id);
      this.activeWorkspace = ws;
    } catch {
      // Ignore
    }
  }

  async logout() {
    try {
      await api.auth.logout();
    } catch {
      // Ignore
    }
    this.user = null;
    this.activeWorkspace = null;
    this.workspaces = [];
    this.loading = false;
    this.initialized = true;
  }
}

export const auth = new AuthStore();
