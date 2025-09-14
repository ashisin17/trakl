export default defineEventHandler(async (event) => {
  const session = await getUserSession(event)
  
  try {
    const db = useDrizzle()
    const chats = await db.query.chats.findMany({
      where: (chat, { eq }) => eq(chat.userId, session.user?.id || session.id),
      orderBy: (chat, { desc }) => desc(chat.createdAt)
    })
    return chats
  } catch (error: any) {
    // Return empty array if database fails - allows frontend to work
    console.log('Database error, returning empty chats:', error?.message || error)
    return []
  }
})
