export default defineEventHandler(async (event) => {
  try {
    console.log('Chat GET endpoint called')
    const session = await getUserSession(event)
    const { id } = getRouterParams(event)
    
    console.log('Session:', session)
    console.log('Chat ID:', id)

    // Initialize mock chats if not exists
    global.mockChats = global.mockChats || {}
    console.log('Current mock chats:', Object.keys(global.mockChats))

    // Return mock chat if it exists
    if (global.mockChats[id as string]) {
      console.log('Returning existing chat:', id)
      return global.mockChats[id as string]
    }

    console.log('Creating new mock chat:', id)
    // Create a new mock chat if it doesn't exist
    global.mockChats[id as string] = {
      id: id as string,
      title: 'New Chat',
      userId: session.user?.id || session.id || 'anonymous',
      createdAt: new Date().toISOString(),
      messages: []
    }

    console.log('Created new chat:', global.mockChats[id as string])
    return global.mockChats[id as string]
    
  } catch (error) {
    console.error('Error in chat GET endpoint:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to retrieve chat',
      data: error
    })
  }
})
