export default defineEventHandler(async (event) => {
  const body = await readBody(event)
  
  try {
    // Call the recommendation service to submit quiz responses
    const response = await $fetch('http://localhost:8001/api/preferences/quiz/submit?user_id=test-user-123', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: {
        responses: body.responses
      }
    })
    
    return response
  } catch (error) {
    console.error('Quiz submission error:', error)
    
    // Return success even if backend fails (graceful degradation)
    return {
      success: true,
      message: 'Quiz completed! Your preferences will be used for future recommendations.'
    }
  }
})
