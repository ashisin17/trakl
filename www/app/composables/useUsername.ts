import { useStorage } from '@vueuse/core';

export default function useUsername() {
  const username = useStorage<string | null>('userName', null);
  const loggedIn = computed(() => !!username.value);

  return { username, loggedIn };
}