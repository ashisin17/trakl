import { useStorage } from '@vueuse/core';

export default function useUsername() {
  const username = useStorage<string | null>('userName', null);

  return username;
}