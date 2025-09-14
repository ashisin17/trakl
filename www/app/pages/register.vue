<script setup lang="ts">

const answers = reactive<Record<string, string>>({})
const loading = ref(false)
const toast = useToast()

// Add debug logging
console.log('Register component mounted')

async function submit(event?: Event) {
  if (event) {
    event.preventDefault()
  }
  
  console.log('Submit function called')
  console.log('Form answers:', JSON.stringify(answers, null, 2))
  const missing = QUIZ_QUESTIONS.filter(q => !answers[q.id])
  if (missing.length) {
    toast.add({ title: 'Please answer all questions', description: `${missing.length} question(s) left`, color: 'warning' })
    return
  }

  loading.value = true
  
  try {
    // Create a new chat with the user's preferences
    const preferences = Object.entries(answers)
      .map(([questionId, answer]) => {
        const question = QUIZ_QUESTIONS.find(q => q.id === questionId)
        return `${question?.question || questionId}: ${answer}`
      })
      .join('\n')
    
    try {
      console.log('Creating new chat with preferences:', preferences)
      
      // Create a new chat with the preferences as the first message
      const chat = await $fetch('/api/chats', {
        method: 'POST',
        body: {
          message: `Here are my learning preferences:\n\n${preferences}\n\nPlease recommend me a learning plan.`
        },
        onResponse({ response }) {
          console.log('Chat creation response:', response.status, response._data)
        },
        onResponseError({ response }) {
          console.error('Chat creation error:', response.status, response._data)
        }
      })
      
      if (chat?.id) {
        console.log('Navigating to chat:', chat.id)
        // Use hard navigation to ensure full page reload
        window.location.href = `/chat/${chat.id}`
      } else {
        throw new Error('Failed to create chat: No chat ID returned')
      }
    } catch (error) {
      console.error('Error in registration submission:', error)
      throw error // Re-throw to be caught by the outer try-catch
    }
    
  } catch (error) {
    console.error('Error creating chat:', error)
    toast.add({
      title: 'Error',
      description: 'Could not create chat. Please try again.',
      color: 'red'
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="p-4 max-w-3xl mx-auto">
    <h1 class="text-2xl font-bold mb-6">Learning Preferences</h1>
    <p class="text-gray-600 dark:text-gray-400 mb-6">Answer these questions to help us create a personalized learning plan for you.</p>
    <div class="space-y-6">
      <div v-for="q in QUIZ_QUESTIONS" :key="q.id">
        <UCard class="p-4">
          <div class="mb-3">
            <h4 class="text-sm font-semibold">{{ q.question }}</h4>
            <p class="text-xs text-gray-500">(category: {{ q.category || '—' }})</p>
          </div>

          <div class="flex flex-col gap-2">
            <label v-for="opt in q.options" :key="opt.value" class="flex items-center gap-3 cursor-pointer p-2 hover:bg-gray-50 dark:hover:bg-gray-800 rounded-md">
              <input
                type="radio"
                :name="q.id"
                :value="opt.value"
                :checked="answers[q.id] === opt.value"
                @change="answers[q.id] = opt.value"
                class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 dark:border-gray-600 accent-indigo-600"
              />
              <div>
                <div class="text-sm">{{ opt.text }}</div>
                <div v-if="opt.category || opt.weight" class="text-xs text-gray-400">{{ opt.category ? `category: ${opt.category}` : '' }} {{ opt.weight ? ` · weight: ${opt.weight}` : '' }}</div>
              </div>
            </label>
          </div>
        </UCard>
      </div>

      <div @submit="submit" class="mt-8">
        <div class="flex justify-end">
          <UButton 
            type="submit"
            :loading="loading"
            icon="i-heroicons-sparkles"
            size="lg"
          >
            Generate My Learning Plan
          </UButton>
        </div>
      </div>
    </div>
  </div>
</template>