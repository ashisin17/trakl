export default defineEventHandler(async (event) => {
  const { query } = await readBody(event)
  
  if (!query) {
    throw createError({ statusCode: 400, statusMessage: 'Query is required' })
  }

  console.log('🎯 Frontend input received:', query)

  try {
    // Test recommendation service connection
    console.log('📡 Calling recommendation service...')
    const recommendations = await $fetch('http://localhost:8001/api/recommendations/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: {
        user_id: '550e8400-e29b-41d4-a716-446655440000',
        query: query,
        max_results: 3
      }
    }).catch((error) => {
      console.log('❌ Recommendation service error:', error.message)
      return null
    })

    // Test agent service connection  
    console.log('🤖 Calling agent service...')
    const learningPlan = await $fetch('http://localhost:8002/api/plans/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: {
        user_id: '550e8400-e29b-41d4-a716-446655440000',
        learning_goal: query,
        preferences: {
          experience_level: 'intermediate',
          time_commitment: '2 hours per day'
        }
      }
    }).catch((error) => {
      console.log('❌ Agent service error:', error.message)
      return null
    })

    console.log('✅ Flow test completed successfully')

    return {
      success: true,
      input_received: query,
      recommendation_service_connected: !!recommendations,
      agent_service_connected: !!learningPlan,
      recommendations: recommendations || 'Service unavailable - using fallback',
      learning_plan: learningPlan || 'Service unavailable - using fallback',
      timestamp: new Date().toISOString()
    }
  } catch (error) {
    console.error('🚨 Test flow error:', error)
    return {
      success: false,
      error: error.message,
      input_received: query,
      timestamp: new Date().toISOString()
    }
  }
})
