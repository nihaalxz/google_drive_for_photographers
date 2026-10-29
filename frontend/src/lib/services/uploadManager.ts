import { writable } from 'svelte/store';
import { api } from './api';
import type { UploadQueueItem, FileAsset } from '../types';

export interface UploadManagerState {
  items: UploadQueueItem[];
  isOpen: boolean;
  activeCount: number;
  totalProgress: number;
}

const initialState: UploadManagerState = {
  items: [],
  isOpen: false,
  activeCount: 0,
  totalProgress: 0
};

function createUploadManager() {
  const { subscribe, update, set } = writable<UploadManagerState>(initialState);

  const MAX_CONCURRENT = 3;

  function calculateProgress(items: UploadQueueItem[]): number {
    if (items.length === 0) return 0;
    const totalSize = items.reduce((acc, i) => acc + i.size, 0);
    if (totalSize === 0) return 0;
    const uploadedSize = items.reduce((acc, i) => acc + (i.size * (i.progress / 100)), 0);
    return Math.round((uploadedSize / totalSize) * 100);
  }

  function recalculate() {
    update(state => ({
      ...state,
      totalProgress: calculateProgress(state.items),
      activeCount: state.items.filter(i => i.status === 'UPLOADING').length
    }));
  }

  async function processQueue(workspaceId: string, onFileUploaded?: (asset: FileAsset) => void) {
    update(state => {
      const active = state.items.filter(i => i.status === 'UPLOADING').length;
      const availableSlots = MAX_CONCURRENT - active;

      if (availableSlots <= 0) return state;

      const pending = state.items.filter(i => i.status === 'QUEUED').slice(0, availableSlots);

      for (const item of pending) {
        item.status = 'UPLOADING';
        startUpload(item, workspaceId, onFileUploaded);
      }

      return {
        ...state,
        activeCount: state.items.filter(i => i.status === 'UPLOADING').length
      };
    });
  }

  async function startUpload(
    item: UploadQueueItem,
    workspaceId: string,
    onFileUploaded?: (asset: FileAsset) => void
  ) {
    try {
      // 1. Request upload session from Django
      const session = await api.storage.createSession({
        workspace_id: workspaceId,
        original_filename: item.file.name,
        file_size: item.file.size,
        mime_type: item.file.type || 'application/octet-stream',
        folder_id: item.folderId
      });

      // 2. Direct browser upload to Backblaze B2 via S3 Presigned URL
      const xhr = new XMLHttpRequest();
      item.xhr = xhr;

      const uploadUrl = session.presigned_data.upload_url || (session.presigned_data.parts && session.presigned_data.parts[0]?.url);

      if (!uploadUrl) {
        throw new Error('No upload URL provided by storage service.');
      }

      await new Promise<string>((resolve, reject) => {
        xhr.upload.onprogress = (evt) => {
          if (evt.lengthComputable) {
            const percent = Math.round((evt.loaded / evt.total) * 100);
            update(state => {
              const current = state.items.find(i => i.id === item.id);
              if (current && current.status === 'UPLOADING') {
                current.progress = percent;
              }
              return { ...state, totalProgress: calculateProgress(state.items) };
            });
          }
        };

        xhr.onload = () => {
          if (xhr.status >= 200 && xhr.status < 300) {
            const etag = (xhr.getResponseHeader('ETag') || '').replace(/"/g, '');
            resolve(etag);
          } else {
            reject(new Error(`Storage rejected upload with status ${xhr.status}`));
          }
        };

        xhr.onerror = () => reject(new Error('Network error during object upload to storage.'));
        xhr.onabort = () => reject(new Error('Upload cancelled.'));

        xhr.open('PUT', uploadUrl, true);
        if (item.file.type) {
          xhr.setRequestHeader('Content-Type', item.file.type);
        }
        xhr.send(item.file);
      }).then(async (etag) => {
        // 3. Complete session with Django & update MySQL ledger
        const asset = await api.storage.completeSession({
          session_id: session.session_id,
          etag,
          metadata: {
            width: null,
            height: null
          }
        });

        update(state => {
          const current = state.items.find(i => i.id === item.id);
          if (current) {
            current.status = 'COMPLETED';
            current.progress = 100;
          }
          return {
            ...state,
            totalProgress: calculateProgress(state.items),
            activeCount: state.items.filter(i => i.status === 'UPLOADING').length
          };
        });

        if (onFileUploaded) {
          onFileUploaded(asset);
        }

        // Trigger next file in queue
        processQueue(workspaceId, onFileUploaded);
      }).catch((err: Error) => {
        if (err.message === 'Upload cancelled.') {
          update(state => {
            const current = state.items.find(i => i.id === item.id);
            if (current) current.status = 'CANCELLED';
            return { ...state };
          });
        } else {
          update(state => {
            const current = state.items.find(i => i.id === item.id);
            if (current) {
              current.status = 'ERROR';
              current.error = err.message;
            }
            return { ...state };
          });
        }
        recalculate();
        processQueue(workspaceId, onFileUploaded);
      });

    } catch (err: unknown) {
      update(state => {
        const current = state.items.find(i => i.id === item.id);
        if (current) {
          current.status = 'ERROR';
          current.error = err instanceof Error ? err.message : 'Upload initialization failed';
        }
        return { ...state };
      });
      recalculate();
      processQueue(workspaceId, onFileUploaded);
    }
  }

  return {
    subscribe,
    enqueue: (files: FileList | File[], workspaceId: string, folderId: string | null = null, onFileUploaded?: (asset: FileAsset) => void) => {
      const newItems: UploadQueueItem[] = Array.from(files).map(file => ({
        id: crypto.randomUUID(),
        file,
        name: file.name,
        size: file.size,
        mimeType: file.type || 'application/octet-stream',
        progress: 0,
        status: 'QUEUED',
        folderId
      }));

      update(state => ({
        ...state,
        items: [...state.items, ...newItems],
        isOpen: true
      }));

      processQueue(workspaceId, onFileUploaded);
    },

    cancel: (id: string) => {
      update(state => {
        const item = state.items.find(i => i.id === id);
        if (item && item.xhr) {
          item.xhr.abort();
          item.status = 'CANCELLED';
        }
        return { ...state };
      });
      recalculate();
    },

    retry: (id: string, workspaceId: string, onFileUploaded?: (asset: FileAsset) => void) => {
      update(state => {
        const item = state.items.find(i => i.id === id);
        if (item) {
          item.status = 'QUEUED';
          item.progress = 0;
          item.error = undefined;
        }
        return { ...state };
      });
      processQueue(workspaceId, onFileUploaded);
    },

    clearCompleted: () => {
      update(state => ({
        ...state,
        items: state.items.filter(i => i.status !== 'COMPLETED')
      }));
      recalculate();
    },

    toggleOpen: () => update(s => ({ ...s, isOpen: !s.isOpen })),
    setOpen: (open: boolean) => update(s => ({ ...s, isOpen: open }))
  };
}

export const uploadManager = createUploadManager();
