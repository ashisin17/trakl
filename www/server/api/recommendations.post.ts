export default defineEventHandler(async (event) => {
  const { query } = await readBody(event)
  
  if (!query) {
    throw createError({ statusCode: 400, statusMessage: 'Query is required' })
  }

  try {
    // Create a simple user preference for testing
    const testUserId = '550e8400-e29b-41d4-a716-446655440000'
    
    // First, try to create user preferences
    const preferencesResponse = await $fetch('http://localhost:8001/api/preferences', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: {
        user_id: testUserId,
        visual_preference: 0.8,
        video_preference: 0.9,
        preferred_difficulty: 'intermediate',
        preferred_session_length: 30,
        interests: ['programming', 'web development']
      }
    }).catch(() => null) // Ignore if already exists

    // Get recommendations from the recommendation service
    const recommendations = await $fetch('http://localhost:8001/api/recommendations/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: {
        user_id: testUserId,
        query: query,
        max_results: 5
      }
    })

    return {
      success: true,
      query: query,
      recommendations: (recommendations as any)?.recommendations || [],
      total_count: (recommendations as any)?.total_count || 0
    }
  } catch (error) {
    console.error('Recommendation API error:', error)
    
    // Return mock recommendations if service is unavailable
    return {
      success: true,
      query: query,
      recommendations: [
        {
          id: '1',
          content: {
            title: 'React Fundamentals Course',
            description: 'Learn the basics of React development with hands-on examples',
            url: 'https://example.com/react-course',
            content_type: 'course',
            source_platform: 'Example Learning',
            difficulty_level: 'beginner',
            topics: ['react', 'javascript', 'frontend'],
            rating: 4.5
          },
          final_score: 0.95,
          reasoning: 'Matches your learning goals and preferred content type'
        },
        {
          id: '2',
          content: {
            title: 'Building Interactive UIs with React',
            description: 'Advanced React patterns and state management',
            url: 'https://example.com/react-advanced',
            content_type: 'video',
            source_platform: 'Tech Academy',
            difficulty_level: 'intermediate',
            topics: ['react', 'state management', 'hooks'],
            rating: 4.7
          },
          final_score: 0.87,
          reasoning: 'Perfect for your intermediate level and video preference'
        }
      ],
      total_count: 2,
      fallback: true
    }
  }
})
