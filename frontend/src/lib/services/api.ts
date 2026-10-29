import type {
  User,
  Workspace,
  Folder,
  FileAsset,
  Album,
  AlbumAsset,
  ShareLink,
  ActivityLog
} from '../types';

function getCookie(name: string): string | null {
  if (typeof document === 'undefined') return null;
  const match = document.cookie.match(new RegExp('(^|;\\s*)(' + name + ')=([^;]*)'));
  return match ? decodeURIComponent(match[3]) : null;
}

export class ApiError extends Error {
  status: number;
  data: unknown;
  constructor(message: string, status: number, data?: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.data = data;
  }
}

const API_BASE_URL = (import.meta.env.VITE_API_BASE_URL !== undefined)
  ? import.meta.env.VITE_API_BASE_URL
  : (typeof window !== 'undefined' && window.location.hostname.includes('texasholidayssa.com')
    ? 'https://lensvaultapi.texasholidayssa.com'
    : '');

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const url = endpoint.startsWith('http') ? endpoint : `${API_BASE_URL}${endpoint}`;
  const headers = new Headers(options.headers || {});

  if (!headers.has('Content-Type') && !(options.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json');
  }

  const method = (options.method || 'GET').toUpperCase();
  if (['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
    const csrfToken = getCookie('csrftoken');
    if (csrfToken) {
      headers.set('X-CSRFToken', csrfToken);
    }
  }

  const response = await fetch(url, {
    ...options,
    headers,
    credentials: 'include'
  });

  if (response.status === 204) {
    return {} as T;
  }

  let data: unknown;
  const contentType = response.headers.get('content-type');
  if (contentType && contentType.includes('application/json')) {
    data = await response.json();
  } else {
    data = await response.text();
  }

  if (!response.ok) {
    const errMessage = (data && typeof data === 'object' && 'detail' in data)
      ? String((data as { detail: unknown }).detail)
      : `Request failed with status ${response.status}`;
    throw new ApiError(errMessage, response.status, data);
  }

  return data as T;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export const api = {
  auth: {
    csrf: () => request<{ detail: string }>('/api/v1/auth/csrf/'),

    login: (credentials: { email: string; password: string }) =>
      request<{ user: User; active_workspace: Workspace }>('/api/v1/auth/login/', {
        method: 'POST',
        body: JSON.stringify(credentials)
      }),

    register: (data: { email: string; username: string; password: string; full_name?: string; workspace_name?: string }) =>
      request<{ user: User; active_workspace: Workspace }>('/api/v1/auth/register/', {
        method: 'POST',
        body: JSON.stringify(data)
      }),

    logout: () =>
      request<{ detail: string }>('/api/v1/auth/logout/', {
        method: 'POST'
      }),

    me: () =>
      request<{ user: User; workspaces: Workspace[]; active_workspace: Workspace | null }>('/api/v1/auth/me/'),

    updateProfile: (data: Partial<User>) =>
      request<User>('/api/v1/auth/me/', {
        method: 'PATCH',
        body: JSON.stringify(data)
      }),

    changePassword: (data: { old_password: string; new_password: string }) =>
      request<{ detail: string }>('/api/v1/auth/change-password/', {
        method: 'POST',
        body: JSON.stringify(data)
      })
  },

  workspaces: {
    list: () => request<PaginatedResponse<Workspace>>('/api/v1/workspaces/'),
    get: (id: string) => request<Workspace>(`/api/v1/workspaces/${id}/`),
    storageBreakdown: (id: string) =>
      request<{
        total_limit_bytes: number;
        used_bytes: number;
        available_bytes: number;
        used_percent: number;
        breakdown: {
          raw_bytes: number;
          standard_images_bytes: number;
          videos_bytes: number;
          other_bytes: number;
        };
        file_count: number;
      }>(`/api/v1/workspaces/${id}/storage_breakdown/`),
    members: (id: string) => request<unknown[]>(`/api/v1/workspaces/${id}/members/`)
  },

  folders: {
    list: (params: { workspace_id: string; parent_id?: string | null; starred?: boolean; deleted?: boolean; q?: string }) => {
      const q = new URLSearchParams({ workspace_id: params.workspace_id });
      if (params.parent_id !== undefined) q.set('parent_id', params.parent_id === null ? 'root' : params.parent_id);
      if (params.starred !== undefined) q.set('starred', String(params.starred));
      if (params.deleted !== undefined) q.set('deleted', String(params.deleted));
      if (params.q) q.set('q', params.q);
      return request<PaginatedResponse<Folder>>(`/api/v1/folders/?${q.toString()}`);
    },
    create: (data: { workspace_id: string; name: string; parent?: string | null; color?: string }) =>
      request<Folder>('/api/v1/folders/', {
        method: 'POST',
        body: JSON.stringify(data)
      }),
    get: (id: string) => request<Folder>(`/api/v1/folders/${id}/`),
    update: (id: string, data: Partial<Folder>) =>
      request<Folder>(`/api/v1/folders/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(data)
      }),
    trash: (id: string) =>
      request<void>(`/api/v1/folders/${id}/`, {
        method: 'DELETE'
      }),
    restore: (id: string) =>
      request<Folder>(`/api/v1/folders/${id}/restore/`, {
        method: 'POST'
      }),
    toggleStar: (id: string) =>
      request<{ is_starred: boolean }>(`/api/v1/folders/${id}/toggle_star/`, {
        method: 'POST'
      }),
    move: (id: string, parent_id: string | null) =>
      request<Folder>(`/api/v1/folders/${id}/move/`, {
        method: 'POST',
        body: JSON.stringify({ parent_id })
      })
  },

  files: {
    list: (params: {
      workspace_id: string;
      folder_id?: string | null;
      starred?: boolean;
      deleted?: boolean;
      type?: 'image' | 'video' | 'raw';
      q?: string;
      sort_by?: string;
      sort_direction?: 'asc' | 'desc';
      page?: number;
    }) => {
      const q = new URLSearchParams({ workspace_id: params.workspace_id });
      if (params.folder_id !== undefined) q.set('folder_id', params.folder_id === null ? 'root' : params.folder_id);
      if (params.starred !== undefined) q.set('starred', String(params.starred));
      if (params.deleted !== undefined) q.set('deleted', String(params.deleted));
      if (params.type) q.set('type', params.type);
      if (params.q) q.set('q', params.q);
      if (params.sort_by) q.set('sort_by', params.sort_by);
      if (params.sort_direction) q.set('sort_direction', params.sort_direction);
      if (params.page) q.set('page', String(params.page));
      return request<PaginatedResponse<FileAsset>>(`/api/v1/files/?${q.toString()}`);
    },
    get: (id: string) => request<FileAsset>(`/api/v1/files/${id}/`),
    update: (id: string, data: Partial<FileAsset>) =>
      request<FileAsset>(`/api/v1/files/${id}/`, {
        method: 'PATCH',
        body: JSON.stringify(data)
      }),
    trash: (id: string) =>
      request<void>(`/api/v1/files/${id}/`, {
        method: 'DELETE'
      }),
    restore: (id: string) =>
      request<FileAsset>(`/api/v1/files/${id}/restore/`, {
        method: 'POST'
      }),
    permanentDelete: (id: string) =>
      request<void>(`/api/v1/files/${id}/permanent_delete/`, {
        method: 'DELETE'
      }),
    toggleStar: (id: string) =>
      request<{ is_starred: boolean }>(`/api/v1/files/${id}/toggle_star/`, {
        method: 'POST'
      }),
    move: (id: string, folder_id: string | null) =>
      request<FileAsset>(`/api/v1/files/${id}/move/`, {
        method: 'POST',
        body: JSON.stringify({ folder_id })
      }),
    bulkAction: (data: { action: 'trash' | 'restore' | 'delete_permanent' | 'star' | 'unstar' | 'move'; file_ids: string[]; folder_id?: string | null }) =>
      request<{ success: boolean; count: number }>('/api/v1/files/bulk_action/', {
        method: 'POST',
        body: JSON.stringify(data)
      })
  },

  storage: {
    createSession: (data: {
      workspace_id: string;
      original_filename: string;
      file_size: number;
      mime_type: string;
      folder_id?: string | null;
    }) =>
      request<{
        session_id: string;
        object_key: string;
        is_multipart: boolean;
        presigned_data: {
          upload_url?: string;
          part_size?: number;
          part_count?: number;
          parts?: Array<{ part_number: number; url: string }>;
        };
        expires_at: string;
      }>('/api/v1/storage/upload-session/', {
        method: 'POST',
        body: JSON.stringify(data)
      }),

    completeSession: (data: {
      session_id: string;
      etag?: string;
      parts?: Array<{ PartNumber: number; ETag: string }>;
      metadata?: Record<string, unknown>;
    }) =>
      request<FileAsset>('/api/v1/storage/upload-complete/', {
        method: 'POST',
        body: JSON.stringify(data)
      }),

    abortSession: (session_id: string) =>
      request<{ success: boolean }>('/api/v1/storage/upload-abort/', {
        method: 'POST',
        body: JSON.stringify({ session_id })
      })
  },

  albums: {
    list: (params: { workspace_id: string; starred?: boolean; q?: string }) => {
      const q = new URLSearchParams({ workspace_id: params.workspace_id });
      if (params.starred !== undefined) q.set('starred', String(params.starred));
      if (params.q) q.set('q', params.q);
      return request<PaginatedResponse<Album>>(`/api/v1/albums/?${q.toString()}`);
    },
    create: (data: {
      workspace_id: string;
      title: string;
      description?: string;
      client_name?: string;
      client_email?: string;
      event_date?: string | null;
      cover_asset_id?: string | null;
    }) =>
      request<Album>('/api/v1/albums/', {
        method: 'POST',
        body: JSON.stringify(data)
      }),
    get: (id: string) => request<Album>(`/api/v1/albums/${id}/`),
    getAssets: (id: string) => request<AlbumAsset[]>(`/api/v1/albums/${id}/assets/`),
    addAssets: (id: string, file_ids: string[]) =>
      request<{ success: boolean; added: number; photo_count: number }>(`/api/v1/albums/${id}/add_assets/`, {
        method: 'POST',
        body: JSON.stringify({ file_ids })
      }),
    removeAsset: (id: string, file_id: string) =>
      request<{ success: boolean; photo_count: number }>(`/api/v1/albums/${id}/remove_asset/`, {
        method: 'POST',
        body: JSON.stringify({ file_id })
      }),
    setCover: (id: string, file_id: string) =>
      request<Album>(`/api/v1/albums/${id}/set_cover/`, {
        method: 'POST',
        body: JSON.stringify({ file_id })
      }),
    toggleStar: (id: string) =>
      request<{ is_starred: boolean }>(`/api/v1/albums/${id}/toggle_star/`, {
        method: 'POST'
      }),
    delete: (id: string) =>
      request<void>(`/api/v1/albums/${id}/`, {
        method: 'DELETE'
      })
  },

  sharing: {
    list: (workspace_id: string) =>
      request<PaginatedResponse<ShareLink>>(`/api/v1/sharing/links/?workspace_id=${workspace_id}`),
    create: (data: {
      workspace_id: string;
      title: string;
      target_type: 'ALBUM' | 'FOLDER' | 'FILE';
      album?: string | null;
      folder?: string | null;
      file_asset?: string | null;
      password?: string;
      expires_at?: string | null;
      allow_downloads?: boolean;
      allow_favorites?: boolean;
    }) =>
      request<ShareLink>('/api/v1/sharing/links/', {
        method: 'POST',
        body: JSON.stringify(data)
      }),
    delete: (id: string) =>
      request<void>(`/api/v1/sharing/links/${id}/`, {
        method: 'DELETE'
      }),
    getPublic: (token: string, password?: string) => {
      const headers: Record<string, string> = {};
      if (password) {
        headers['X-Share-Password'] = password;
      }
      return request<{
        token: string;
        title: string;
        target_type: 'ALBUM' | 'FOLDER' | 'FILE';
        allow_downloads: boolean;
        allow_favorites: boolean;
        created_at: string;
        workspace_name: string;
        is_password_protected?: boolean;
        album?: Album;
        assets?: AlbumAsset[];
        folder?: Folder;
        files?: FileAsset[];
        file?: FileAsset;
      }>(`/api/v1/sharing/public/${token}/`, { headers });
    },
    submitPublicAction: (token: string, data: { action: 'favorite' | 'download'; file_id?: string }) =>
      request<{ success: boolean; is_favorite?: boolean }>(`/api/v1/sharing/public/${token}/`, {
        method: 'POST',
        body: JSON.stringify(data)
      })
  },

  activity: {
    list: (workspace_id: string) =>
      request<PaginatedResponse<ActivityLog>>(`/api/v1/activity/?workspace_id=${workspace_id}`)
  }
};
