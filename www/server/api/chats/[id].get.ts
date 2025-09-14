export default defineEventHandler(async (event) => {
  const session = await getUserSession(event)
  const { id } = getRouterParams(event)

  // Check mock chats first
  if (global.mockChats && global.mockChats[id as string]) {
    return global.mockChats[id as string]
  }

  try {
    const db = useDrizzle()

    const chat = await db.query.chats.findFirst({
      where: (chat, { eq }) => and(eq(chat.id, id as string), eq(chat.userId, session.user?.id || session.id)),
      with: {
        messages: true
      }
    })

    if (!chat) {
      throw createError({ statusCode: 404, statusMessage: 'Chat not found' })
    }

    return chat
  } catch (error: any) {
    console.log('Database error, chat not found:', error?.message || error)
    throw createError({ statusCode: 404, statusMessage: 'Chat not found' })
  }
})
