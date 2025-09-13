import { useStorage } from '@vueuse/core';

export default defineNuxtRouteMiddleware((to, from) => {
  const username = useStorage<string | null>('userName', null);

  if (to.path !== '/register' && !username.value) {
    return navigateTo('/register');
  }
});