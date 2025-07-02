import { ref } from 'vue';

export const useApi = () => {
  const loading = ref(false);
  const error = ref<null | string>(null);

  const get = async <T>(url: string, params?: Record<string, any>): Promise<T | null> => {
    loading.value = true;
    error.value = null;
    try {
      const query = params ? '?' + new URLSearchParams(params).toString() : '';
      const res = await fetch(url + query);
      if (!res.ok) throw new Error(await res.text());
      return await res.json();
    } catch (e: any) {
      error.value = e.message;
      return null;
    } finally {
      loading.value = false;
    }
  };

  const post = async <T>(url: string, body: any): Promise<T | null> => {
    loading.value = true;
    error.value = null;
    try {
      const res = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      if (!res.ok) throw new Error(await res.text());
      return await res.json();
    } catch (e: any) {
      error.value = e.message;
      return null;
    } finally {
      loading.value = false;
    }
  };

  const del = async <T>(url: string): Promise<T | null> => {
    loading.value = true;
    error.value = null;
    try {
      const res = await fetch(url, { method: 'DELETE' });
      if (!res.ok) throw new Error(await res.text());
      return await res.json();
    } catch (e: any) {
      error.value = e.message;
      return null;
    } finally {
      loading.value = false;
    }
  };

  return { get, post, del, loading, error };
}; 