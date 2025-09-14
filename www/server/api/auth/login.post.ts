export default defineEventHandler(async event => {
  const { name } = await readBody(event);

  console.log('Registering user with name:', name);

  return true;
})