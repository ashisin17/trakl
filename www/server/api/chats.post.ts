export default defineEventHandler(async (event) => {
  const session = await getUserSession(event)
  const { message } = await readBody(event)
  
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
  
  // Store chat in memory
  global.mockChats[chatId] = newChat
  
  // If there's an initial message, add it to the chat
  if (message) {
    // Add user message
    global.mockChats[chatId].messages.push({
      id: `msg-${Date.now()}-user`,
      chatId,
      role: 'user',
      parts: [{ type: 'text', text: message }],
      createdAt: new Date().toISOString()
    })
    
    // Generate and add assistant response
    const recommendations = generateRecommendations(message)
    const response = formatRecommendationsResponse(message, recommendations)
    
    global.mockChats[chatId].messages.push({
      id: `msg-${Date.now()}-assistant`,
      chatId,
      role: 'assistant',
      parts: [{ type: 'text', text: response }],
      createdAt: new Date().toISOString()
    })
  }
  
  // Return the new chat
  return newChat
})

function generateRecommendations(query: string) {
  const lowerQuery = query.toLowerCase()
  
  if (lowerQuery.includes('python')) {
    return [
      {
        title: "Python Complete Course - Visual Learning",
        platform: "YouTube",
        type: "Video Tutorial", 
        duration: "45 minutes",
        rating: 4.8,
        reason: "Perfect match for visual learners who prefer video content"
      },
      {
        title: "Interactive Python Coding Bootcamp",
        platform: "Codecademy",
        type: "Interactive Course",
        duration: "30 minutes per session", 
        rating: 4.7,
        reason: "Interactive format matches preference for engaging learning"
      },
      {
        title: "Python Fundamentals with Diagrams",
        platform: "Medium",
        type: "Article Series",
        duration: "25 minutes per article",
        rating: 4.6,
        reason: "Uses visual aids to explain concepts clearly"
      }
    ]
  }
  
  if (lowerQuery.includes('react')) {
    return [
      {
        title: "React Complete Guide - Modern Development", 
        platform: "Udemy",
        type: "Video Course",
        duration: "60 minutes per lesson",
        rating: 4.9,
        reason: "Comprehensive coverage perfect for building real-world applications"
      },
      {
        title: "Interactive React Tutorial",
        platform: "React.dev", 
        type: "Interactive Tutorial",
        duration: "2-3 hours",
        rating: 4.8,
        reason: "Official documentation with practical examples"
      }
    ]
  }
  
  // Default recommendations
  return [
    {
      title: "Complete Learning Guide",
      platform: "Various",
      type: "Mixed Content",
      duration: "Flexible",
      rating: 4.5,
      reason: "Curated resources for your learning goal"
    }
  ]
}

function formatRecommendationsResponse(query: string, recommendations: any[]) {
  let response = `I found personalized learning recommendations for: "${query}"\n\n`
  response += `## 🎯 Recommended Learning Resources\n\n`
  
  recommendations.forEach((rec, index) => {
    response += `**${index + 1}. ${rec.title}**\n`
    response += `Platform: ${rec.platform} | Type: ${rec.type} | Duration: ${rec.duration} | Rating: ${rec.rating}⭐\n`
    response += `💡 Why recommended: ${rec.reason}\n\n`
  })
  
  response += `---\n\n**Would you like me to create a detailed learning plan based on these recommendations?**\n\n`
  response += `Type "yes" to generate your personalized learning roadmap!`
  
  return response
}

// Add global type declaration
declare global {
  var mockChats: any
}
