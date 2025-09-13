export default defineNuxtRouteMiddleware((to, _from) => {
  const {username} = useUsername();

  if (to.path !== '/register' && !username.value) {
    return navigateTo('/register');
  }
});