export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  bio: string;
  avatar_url: string;
  timezone: string;
  created_at: string;
}

export interface Workspace {
  id: string;
  name: string;
  slug: string;
  storage_limit_bytes: number;
  storage_used_bytes: number;
  storage_available_bytes: number;
  storage_used_percent: number;
  created_at: string;
  updated_at: string;
}

export interface WorkspaceMembership {
  id: string;
  workspace: string;
  user: User;
  role: 'OWNER' | 'ADMIN' | 'MEMBER' | 'VIEWER';
  joined_at: string;
}

export interface Breadcrumb {
  id: string;
  name: string;
}

export interface Folder {
  id: string;
  workspace: string;
  parent: string | null;
  name: string;
  color: string;
  is_starred: boolean;
  is_deleted: boolean;
  deleted_at: string | null;
  breadcrumbs: Breadcrumb[];
  children_count: number;
  files_count: number;
  created_at: string;
  updated_at: string;
}

export interface FileAsset {
  id: string;
  workspace: string;
  folder: string | null;
  original_filename: string;
  safe_display_name: string;
  mime_type: string;
  file_size: number;
  file_extension: string;
  etag: string;
  upload_status: 'PENDING' | 'PROCESSING' | 'UPLOADED' | 'FAILED';
  width: number | null;
  height: number | null;
  camera_make: string;
  camera_model: string;
  lens_model: string;
  iso: number | null;
  f_stop: string;
  shutter_speed: string;
  focal_length: string;
  date_taken: string | null;
  raw_metadata: Record<string, unknown>;
  is_starred: boolean;
  is_deleted: boolean;
  deleted_at: string | null;
  preview_url: string | null;
  download_url: string | null;
  is_image: boolean;
  is_video: boolean;
  is_raw: boolean;
  created_at: string;
  updated_at: string;
}

export interface Album {
  id: string;
  workspace: string;
  title: string;
  description: string;
  client_name: string;
  client_email: string;
  event_date: string | null;
  cover_asset: FileAsset | null;
  photo_count: number;
  is_starred: boolean;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
}

export interface AlbumAsset {
  id: string;
  album: string;
  file_asset: FileAsset;
  sort_order: number;
  is_favorite: boolean;
  client_selected: boolean;
  added_at: string;
}

export interface ShareLink {
  id: string;
  workspace: string;
  token: string;
  title: string;
  target_type: 'ALBUM' | 'FOLDER' | 'FILE';
  album: string | null;
  folder: string | null;
  file_asset: string | null;
  album_title?: string;
  folder_name?: string;
  file_name?: string;
  is_password_protected: boolean;
  expires_at: string | null;
  is_expired: boolean;
  allow_downloads: boolean;
  allow_favorites: boolean;
  is_active: boolean;
  view_count: number;
  download_count: number;
  created_at: string;
}

export interface ActivityLog {
  id: string;
  workspace: string;
  user: string;
  user_email: string;
  action: string;
  target_type: string;
  target_id: string;
  description: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface UploadQueueItem {
  id: string;
  file: File;
  name: string;
  size: number;
  mimeType: string;
  progress: number;
  status: 'QUEUED' | 'UPLOADING' | 'COMPLETED' | 'ERROR' | 'CANCELLED';
  error?: string;
  folderId?: string | null;
  xhr?: XMLHttpRequest;
}
