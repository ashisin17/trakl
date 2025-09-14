export default defineNuxtRouteMiddleware((to, _from) => {
  const {username} = useUsername();

  if (to.path !== '/auth' && !username.value) {
    // return navigateTo('/auth');
  }
});