import { convertToModelMessages, createUIMessageStream, createUIMessageStreamResponse, generateText, streamText } from 'ai'
import { gateway } from '@ai-sdk/gateway'
import type { UIMessage } from 'ai'
import { z } from 'zod'

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
  
  // Handle new message with recommendations
  if (body.input && body.recommendations) {
    const db = useDrizzle()
    
    // Add user message
    await db.insert(tables.messages).values({
      chatId: id as string,
      role: 'user',
      parts: [{ type: 'text', text: body.input }]
    })

    // Create AI response with recommendations only
    let aiResponse = `I found these personalized learning recommendations for: "${body.input}"\n\n`
    
    if (body.recommendations?.recommendations?.length > 0) {
      aiResponse += `## 🎯 Recommended Learning Resources\n\n`
      body.recommendations.recommendations.forEach((rec: any, index: number) => {
        aiResponse += `**${index + 1}. ${rec.content.title}**\n`
        aiResponse += `${rec.content.description}\n`
        aiResponse += `📚 Type: ${rec.content.content_type} | 🎯 Level: ${rec.content.difficulty_level} | ⭐ Rating: ${rec.content.rating}/5\n`
        aiResponse += `💡 Why recommended: ${rec.reasoning}\n\n`
      })
      
      aiResponse += `---\n\n**Would you like me to create a detailed learning plan based on these recommendations?**\n\n`
      aiResponse += `Type "yes" to generate your personalized learning roadmap, or ask me to find different resources.`
    }

    await db.insert(tables.messages).values({
      chatId: id as string,
      role: 'assistant',
      parts: [{ type: 'text', text: aiResponse }]
    })

    return { success: true }
  }

  // Handle user confirmation for learning plan
  if (body.input && (body.input.toLowerCase().includes('yes') || body.input.toLowerCase().includes('create') || body.input.toLowerCase().includes('plan'))) {
    const db = useDrizzle()
    
    // Get the last user message to understand what they wanted to learn
    const lastMessages = await db.query.messages.findMany({
      where: (message, { eq }) => eq(message.chatId, id as string),
      orderBy: (message, { desc }) => desc(message.createdAt),
      limit: 5
    })
    
    const originalQuery = lastMessages.find(msg => msg.role === 'user' && Array.isArray(msg.parts) && msg.parts[0] && !(msg.parts[0] as any).text.toLowerCase().includes('yes'))?.parts?.[0]?.text || 'learning goals'
    
    // Add user confirmation message
    await db.insert(tables.messages).values({
      chatId: id as string,
      role: 'user',
      parts: [{ type: 'text', text: body.input }]
    })

    // Generate learning plan
    const learningPlan = await $fetch('/api/learning-plans', {
      method: 'POST',
      body: { query: originalQuery }
    }).catch(() => null)

    let planResponse = `Perfect! I'll create your personalized learning plan now.\n\n`
    
    if (learningPlan?.plan) {
      planResponse += `# 📋 ${learningPlan.plan.title}\n\n`
      planResponse += `${learningPlan.plan.description}\n\n`
      
      if (learningPlan.plan.weeks) {
        learningPlan.plan.weeks.forEach((week: any) => {
          planResponse += `## Week ${week.week}: ${week.title}\n`
          planResponse += `**Topics to cover:**\n`
          week.topics.forEach((topic: string) => {
            planResponse += `- ${topic}\n`
          })
          planResponse += `**Estimated time:** ${week.estimated_hours} hours\n\n`
        })
        
        planResponse += `---\n\n`
        planResponse += `**📊 Plan Summary:**\n`
        planResponse += `- **Total Duration:** ${learningPlan.plan.total_duration_weeks} weeks\n`
        planResponse += `- **Total Time Investment:** ${learningPlan.plan.estimated_total_hours} hours\n\n`
        planResponse += `Ready to start your learning journey? I can help you with specific questions about any week or topic!`
      }
    } else {
      planResponse += `I'll create a structured learning plan for you:\n\n`
      planResponse += `**Week 1-2: Foundations**\n- Core concepts and setup\n- Basic exercises\n\n`
      planResponse += `**Week 3-4: Practical Application**\n- Hands-on projects\n- Real-world examples\n\n`
      planResponse += `**Week 5-6: Advanced Topics**\n- Complex scenarios\n- Best practices\n\n`
      planResponse += `This plan adapts to your pace. Let me know if you'd like me to adjust anything!`
    }

    await db.insert(tables.messages).values({
      chatId: id as string,
      role: 'assistant',
      parts: [{ type: 'text', text: planResponse }]
    })

    return { success: true }
  }

  // Handle existing chat functionality
  const { model, messages } = await readValidatedBody(event, z.object({
    model: z.string(),
    messages: z.array(z.custom<UIMessage>())
  }).parse)

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

  if (!chat.title) {
    const { text: title } = await generateText({
      model: gateway('openai/gpt-5-nano'),
      system: `You are a title generator for a chat:
          - Generate a short title based on the first user's message
          - The title should be less than 30 characters long
          - The title should be a summary of the user's message
          - Do not use quotes (' or ") or colons (:) or any other punctuation
          - Do not use markdown, just plain text`,
      prompt: JSON.stringify(messages[0])
    })

    setHeader(event, 'X-Chat-Title', title.replace(/:/g, '').split('\n')[0])
    await db.update(tables.chats).set({ title }).where(eq(tables.chats.id, id as string))
  }

  const lastMessage = messages[messages.length - 1]
  if (lastMessage?.role === 'user' && messages.length > 1) {
    await db.insert(tables.messages).values({
      chatId: id as string,
      role: 'user',
      parts: lastMessage.parts
    })
  }

  const stream = createUIMessageStream({
    execute: ({ writer }) => {
      const result = streamText({
        model: gateway(model),
        system: 'You are a helpful assistant that can answer questions and help.',
        messages: convertToModelMessages(messages)
      })

      writer.merge(result.toUIMessageStream())
    },
    onFinish: async ({ messages }) => {
      await db.insert(tables.messages).values(messages.map(message => ({
        chatId: chat.id,
        role: message.role as 'user' | 'assistant',
        parts: message.parts
      })))
    }
  })

  return createUIMessageStreamResponse({
    stream
  })
})
