export default defineEventHandler(async (event) => {
  const session = await getUserSession(event)
  const { id } = getRouterParams(event)

  // Initialize mock chats if not exists
  global.mockChats = global.mockChats || {}

  // Return mock chat if it exists
  if (global.mockChats[id as string]) {
    return global.mockChats[id as string]
  }

  // Create a new mock chat if it doesn't exist
  global.mockChats[id as string] = {
    id: id as string,
    title: 'New Chat',
    userId: session.user?.id || session.id,
    createdAt: new Date().toISOString(),
    messages: []
  }

  return global.mockChats[id as string]
})
