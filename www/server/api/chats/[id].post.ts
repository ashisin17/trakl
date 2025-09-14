import { convertToModelMessages, createUIMessageStream, createUIMessageStreamResponse, generateText, streamText } from 'ai'
import { gateway } from '@ai-sdk/gateway'
import type { UIMessage } from 'ai'
import { z } from 'zod'

// Helper functions
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
      }
    ]
  }
  
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

function generateLearningPlan(query: string) {
  let response = `Perfect! I'll create your personalized learning plan now.\n\n`
  response += `# 📋 Personalized Python Programming Journey\n\n`
  response += `A structured 4-week learning path tailored for your goals\n\n`
  
  response += `## Week 1: Python Basics & Syntax\n`
  response += `**Topics to cover:**\n`
  response += `- Understand Python syntax and structure\n`
  response += `- Learn variables, data types, and operators\n`
  response += `- Write your first Python programs\n`
  response += `**Deliverable:** Simple calculator program\n\n`
  
  response += `## Week 2: Control Flow & Functions\n`
  response += `**Topics to cover:**\n`
  response += `- Master if/else statements and loops\n`
  response += `- Create and use functions effectively\n`
  response += `- Handle user input and validation\n`
  response += `**Deliverable:** Interactive quiz game\n\n`
  
  response += `## Week 3: Data Structures & File Handling\n`
  response += `**Topics to cover:**\n`
  response += `- Master lists, dictionaries, and sets\n`
  response += `- Read and write files\n`
  response += `- Process and analyze data\n`
  response += `**Deliverable:** Data analysis script\n\n`
  
  response += `## Week 4: Object-Oriented Programming & Projects\n`
  response += `**Topics to cover:**\n`
  response += `- Understand classes and objects\n`
  response += `- Build a complete application\n`
  response += `- Best practices and code organization\n`
  response += `**Deliverable:** Personal project (task manager, game, or web scraper)\n\n`
  
  response += `---\n\n`
  response += `**📊 Plan Summary:**\n`
  response += `- **Total Duration:** 4 weeks\n`
  response += `- **Weekly Commitment:** 3-4 hours\n`
  response += `- **Learning Style:** Visual + Interactive\n\n`
  response += `🎉 Your personalized learning journey is ready! You can start with Week 1 and progress at your own pace.`
  
  return response
}

// Global type declaration
declare global {
  var mockChats: any
}

defineRouteMeta({
  openAPI: {
    description: 'Chat with AI.',
    tags: ['ai']
  }
})

export default defineEventHandler(async (event) => {
  const session = await getUserSession(event)

  const { id } = getRouterParams(event)

  const body = await readBody(event)
  
  // Handle simple message input - bypass database and use mock system
  if (body.message || body.input) {
    const userMessage = body.message || body.input
    
    // Check if this is a "yes" response for learning plan
    if (userMessage.toLowerCase().includes('yes') || userMessage.toLowerCase().includes('create') || userMessage.toLowerCase().includes('plan')) {
      // Generate learning plan
      const learningPlan = generateLearningPlan(userMessage)
      
      // Add to mock chat
      if (global.mockChats && global.mockChats[id as string]) {
        global.mockChats[id as string].messages.push(
          {
            id: `msg-${Date.now()}-user`,
            chatId: id as string,
            role: 'user',
            parts: [{ type: 'text', text: userMessage }],
            createdAt: new Date().toISOString()
          },
          {
            id: `msg-${Date.now()}-assistant`,
            chatId: id as string,
            role: 'assistant',
            parts: [{ type: 'text', text: learningPlan }],
            createdAt: new Date().toISOString()
          }
        )
      }
      
      return { success: true }
    } else {
      // Generate new recommendations
      const recommendations = generateRecommendations(userMessage)
      const response = formatRecommendationsResponse(userMessage, recommendations)
      
      // Add to mock chat
      if (global.mockChats && global.mockChats[id as string]) {
        global.mockChats[id as string].messages.push(
          {
            id: `msg-${Date.now()}-user`,
            chatId: id as string,
            role: 'user',
            parts: [{ type: 'text', text: userMessage }],
            createdAt: new Date().toISOString()
          },
          {
            id: `msg-${Date.now()}-assistant`,
            chatId: id as string,
            role: 'assistant',
            parts: [{ type: 'text', text: response }],
            createdAt: new Date().toISOString()
          }
        )
      }
      
      return { success: true }
    }
  }

  // Fallback for any other requests - return success to avoid errors
  return { success: true }

})
