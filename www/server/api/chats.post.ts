export default defineEventHandler(async (event) => {
  try {
    console.log('Chat creation endpoint called')
    const session = await getUserSession(event)
    const body = await readBody(event)
    const { message } = body
    
    console.log('Received message:', message)
    console.log('Session:', session)
    
    // Initialize mock chats if not exists
    global.mockChats = global.mockChats || {}
    
    // Create a new chat
    const chatId = `chat-${Date.now()}`
    const newChat = {
      id: chatId,
      title: 'New Chat',
      userId: session.user?.id || session.id,
      createdAt: new Date().toISOString(),
      messages: []
    }
    
    console.log('Creating new chat:', chatId)
  
  // Store chat in memory
  global.mockChats[chatId] = newChat
  
  // If there's an initial message, add it to the chat
  if (message) {
    console.log('Adding initial message to chat')
    const now = new Date().toISOString()
    
    try {
      // Add user message
      const userMessage = {
        id: `msg-${Date.now()}-user`,
        chatId,
        role: 'user' as const,
        parts: [{ type: 'text' as const, text: message }],
        content: message,
        createdAt: now
      }
      
      global.mockChats[chatId].messages.push(userMessage)
      
      // Generate recommendations using the recommendation service
      console.log('Fetching recommendations from service...')
      const recommendations = await $fetch('http://localhost:8001/api/recommendations/generate', {
        method: 'POST',
        body: {
          user_id: session.user?.id || 'anonymous',
          query: message,
          max_results: 5
        }
      }).catch(error => {
        console.error('Error fetching recommendations:', error)
        // Fallback to basic response if recommendation service is down
        return {
          recommendations: [{
            content: {
              title: 'Learning Plan',
              description: 'I\'m having trouble connecting to the recommendation service. Here\'s a basic learning plan based on your input.',
              type: 'text',
              content: `Based on your input: ${message}\n\n1. Start with the basics\n2. Practice regularly\n3. Build projects\n4. Join a community\n5. Keep learning!`
            },
            score: 0.9,
            reason: 'Fallback response'
          }]
        }
      })
      
      // Format the response based on the recommendations
      const response = formatRecommendationsResponse(
        message, 
        (recommendations as { recommendations?: RecommendationItem[] }).recommendations || []
      )
      
      const assistantMessage = {
        id: `msg-${Date.now()}-assistant`,
        chatId,
        role: 'assistant' as const,
        parts: [{ type: 'text' as const, text: response }],
        content: response,
        createdAt: now
      }
      
      global.mockChats[chatId].messages.push(assistantMessage)
      console.log('Added initial messages to chat')
      
    } catch (error) {
      console.error('Error processing initial message:', error)
      // Don't fail the entire request if message processing fails
    }
  }
  
    const createdChat = {
      ...newChat,
      // Ensure we're returning the latest state with messages
      ...(global.mockChats[chatId] || {})
    }
    console.log('Chat created successfully:', createdChat)
    return createdChat
  } catch (error) {
    console.error('Error in chat creation:', error)
    throw createError({
      statusCode: 500,
      statusMessage: 'Failed to create chat',
      data: error
    })
  }
})

// Format recommendations from the recommendation service into a user-friendly response
interface RecommendationItem {
  content?: {
    title?: string;
    description?: string;
    type?: string;
    platform?: string;
    duration?: string;
    rating?: number;
  };
  reason?: string;
  score?: number;
}

function formatRecommendationsResponse(query: string, recommendations: RecommendationItem[] = []) {
  if (!recommendations || recommendations.length === 0) {
    return `I couldn't find specific recommendations for "${query}". Here's a general learning plan:\n\n1. Start with the fundamentals\n2. Practice with small exercises\n3. Work on a small project\n4. Get feedback from others\n5. Keep iterating and improving!`
  }

  // Group recommendations by type
  const byType: Record<string, RecommendationItem[]> = {}
  
  recommendations.forEach(rec => {
    const type = rec.content?.type || 'Other'
    if (!byType[type]) {
      byType[type] = []
    }
    byType[type].push(rec)
  })

  // Build the response
  let response = `I found personalized learning recommendations for: "${query}"\n\n`
  
  Object.entries(byType).forEach(([type, items]) => {
    response += `## 📚 ${type.charAt(0).toUpperCase() + type.slice(1)}\n`
    
    items.forEach((item, index) => {
      const content = item.content || {}
      response += `\n**${index + 1}. ${content.title || 'Untitled Resource'}**`
      
      if (content.platform) response += ` (${content.platform})`
      if (content.duration) response += ` - ${content.duration}`
      if (content.rating) response += ` - ${'★'.repeat(Math.round(content.rating))} (${content.rating.toFixed(1)})`
      
      response += `\n${content.description || item.reason || 'No description available.'}\n`
    })
    
    response += '\n---\n\n'
  })

  // Add a call to action
  response += 'Would you like me to create a personalized learning roadmap based on these recommendations?\n\n'
  response += 'Type "yes" to generate your learning path!'

  return response
}

// Add global type declaration
declare global {
  var mockChats: any
}
