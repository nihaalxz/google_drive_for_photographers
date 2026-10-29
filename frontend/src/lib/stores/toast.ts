import { writable } from 'svelte/store';

export interface ToastMessage {
  id: string;
  type: 'info' | 'success' | 'warning' | 'error';
  title?: string;
  message: string;
  duration?: number;
}

function createToastStore() {
  const { subscribe, update } = writable<ToastMessage[]>([]);

  function show(type: ToastMessage['type'], message: string, title?: string, duration: number = 4000) {
    const id = crypto.randomUUID();
    const toast: ToastMessage = { id, type, message, title, duration };

    update(toasts => [...toasts, toast]);

    if (duration > 0) {
      setTimeout(() => {
        dismiss(id);
      }, duration);
    }
    return id;
  }

  function dismiss(id: string) {
    update(toasts => toasts.filter(t => t.id !== id));
  }

  return {
    subscribe,
    info: (message: string, title?: string, duration?: number) => show('info', message, title, duration),
    success: (message: string, title?: string, duration?: number) => show('success', message, title, duration),
    warning: (message: string, title?: string, duration?: number) => show('warning', message, title, duration),
    error: (message: string, title?: string, duration?: number) => show('error', message, title, duration),
    dismiss
  };
}

export const toast = createToastStore();
