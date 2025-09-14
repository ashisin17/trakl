export default defineEventHandler(async (event) => {
  const session = await getUserSession(event)
  const { message } = await readBody(event)

  // Skip database entirely - create mock chat that works
  const mockChatId = `chat-${Date.now()}`
  const mockChat = {
    id: mockChatId,
    title: 'New Chat',
    userId: session.user?.id || session.id,
    createdAt: new Date().toISOString()
  }

  // Store the conversation in memory for this session
  global.mockChats = global.mockChats || {}
  global.mockChats[mockChatId] = {
    ...mockChat,
    messages: [
      {
        id: `msg-${Date.now()}-1`,
        chatId: mockChatId,
        role: 'user',
        parts: [{ type: 'text', text: message }],
        createdAt: new Date().toISOString()
      },
      {
        id: `msg-${Date.now()}-2`, 
        chatId: mockChatId,
        role: 'assistant',
        parts: [{ type: 'text', text: formatRecommendationsResponse(message, generateRecommendations(message)) }],
        createdAt: new Date().toISOString()
      }
    ]
  }

  return mockChat
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
