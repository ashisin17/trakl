<script setup lang="ts">
const currentQuestion = ref(0)
const answers = ref<Record<string, string>>({})
const loading = ref(false)

const questions = [
  {
    id: 'learning_style_1',
    question: 'When learning something new, I prefer to:',
    options: [
      { value: 'visual', text: 'See diagrams, charts, and visual aids' },
      { value: 'auditory', text: 'Listen to explanations and discussions' },
      { value: 'kinesthetic', text: 'Try it out hands-on immediately' },
      { value: 'reading', text: 'Read detailed written instructions' }
    ]
  },
  {
    id: 'content_type_1',
    question: 'For learning programming, I find most helpful:',
    options: [
      { value: 'video', text: 'Video tutorials with screen recordings' },
      { value: 'article', text: 'Written tutorials and documentation' },
      { value: 'interactive', text: 'Interactive coding exercises' },
      { value: 'course', text: 'Structured online courses' }
    ]
  },
  {
    id: 'difficulty_pref',
    question: 'I prefer learning materials that are:',
    options: [
      { value: 'beginner', text: 'Step-by-step from the basics' },
      { value: 'intermediate', text: 'Moderately challenging with some prior knowledge' },
      { value: 'advanced', text: 'Advanced and assume strong fundamentals' }
    ]
  }
]

function selectAnswer(questionId: string, value: string) {
  answers.value[questionId] = value
}

function nextQuestion() {
  if (currentQuestion.value < questions.length - 1) {
    currentQuestion.value++
  } else {
    submitQuiz()
  }
}

async function submitQuiz() {
  loading.value = true
  try {
    // Submit quiz results to create user preferences
    await $fetch('/api/preferences/quiz/submit', {
      method: 'POST',
      body: {
        responses: Object.entries(answers.value).map(([questionId, answer]) => ({
          question_id: questionId,
          answer: answer,
          weight: 1.0
        }))
      }
    })
    
    // Redirect to main app
    navigateTo('/')
  } catch (error) {
    console.error('Quiz submission error:', error)
  } finally {
    loading.value = false
  }
}

const canProceed = computed(() => {
  return answers.value[questions[currentQuestion.value].id]
})
</script>

<template>
  <UDashboardPanel id="quiz" :ui="{ body: 'p-0 sm:p-0' }">
    <template #body>
      <UContainer class="flex-1 flex flex-col justify-center gap-6 py-8 max-w-2xl">
        <div class="text-center">
          <h1 class="text-3xl font-bold mb-2">Learning Style Quiz</h1>
          <p class="text-gray-600">Help us personalize your learning experience</p>
          <div class="mt-4">
            <div class="text-sm text-gray-500">
              Question {{ currentQuestion + 1 }} of {{ questions.length }}
            </div>
            <UProgress 
              :value="((currentQuestion + 1) / questions.length) * 100" 
              class="mt-2"
            />
          </div>
        </div>

        <div class="bg-white rounded-lg p-6 shadow-sm border">
          <h2 class="text-xl font-semibold mb-6">
            {{ questions[currentQuestion].question }}
          </h2>
          
          <div class="space-y-3">
            <div 
              v-for="option in questions[currentQuestion].options"
              :key="option.value"
              class="cursor-pointer"
              @click="selectAnswer(questions[currentQuestion].id, option.value)"
            >
              <div 
                class="p-4 border rounded-lg transition-all duration-200 hover:bg-gray-50 hover:shadow-sm cursor-pointer"
                :class="{
                  'border-blue-500 bg-blue-50 shadow-sm': answers[questions[currentQuestion].id] === option.value,
                  'border-gray-200 hover:border-gray-300': answers[questions[currentQuestion].id] !== option.value
                }"
              >
                <div class="flex items-center">
                  <div 
                    class="w-5 h-5 rounded-full border-2 mr-3 transition-all duration-200 flex items-center justify-center"
                    :class="{
                      'border-blue-500 bg-blue-500': answers[questions[currentQuestion].id] === option.value,
                      'border-gray-300 hover:border-blue-300': answers[questions[currentQuestion].id] !== option.value
                    }"
                  >
                    <div 
                      v-if="answers[questions[currentQuestion].id] === option.value"
                      class="w-2 h-2 bg-white rounded-full transition-all duration-200"
                    />
                  </div>
                  <span 
                    class="transition-colors duration-200"
                    :class="{
                      'text-blue-700 font-medium': answers[questions[currentQuestion].id] === option.value,
                      'text-gray-700': answers[questions[currentQuestion].id] !== option.value
                    }"
                  >{{ option.text }}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="flex justify-between">
          <UButton 
            v-if="currentQuestion > 0"
            variant="outline"
            @click="currentQuestion--"
          >
            Previous
          </UButton>
          <div v-else></div>
          
          <UButton 
            :disabled="!canProceed || loading"
            :loading="loading"
            @click="nextQuestion"
          >
            {{ currentQuestion === questions.length - 1 ? 'Complete Quiz' : 'Next' }}
          </UButton>
        </div>
      </UContainer>
    </template>
  </UDashboardPanel>
</template>
