<script setup lang="ts">
const input = ref('')
const loading = ref(false)

async function createChat(prompt: string) {
  input.value = prompt
  loading.value = true
  
  try {
    // Get AI recommendations for the learning query
    const recommendations = await $fetch('/api/recommendations', {
      method: 'POST',
      body: { query: prompt }
    })
    
    // Generate a learning plan
    const learningPlan = await $fetch('/api/learning-plans', {
      method: 'POST',
      body: { query: prompt }
    })
    
    // Create chat with AI recommendations and plan
    const chat = await $fetch('/api/chats', {
      method: 'POST',
      body: { 
        input: prompt,
        recommendations: recommendations,
        learningPlan: learningPlan
      }
    })

    refreshNuxtData('chats')
    navigateTo(`/chat/${chat?.id}`)
  } catch (error) {
    console.error('Error creating chat:', error)
    // Fallback to regular chat creation
    const chat = await $fetch('/api/chats', {
      method: 'POST',
      body: { input: prompt }
    })
    refreshNuxtData('chats')
    navigateTo(`/chat/${chat?.id}`)
  } finally {
    loading.value = false
  }
}

function onSubmit() {
  createChat(input.value)
}

const quickChats = [
  {
    label: 'I want to learn React development',
  },
  {
    label: 'Help me master Python programming',
  },
  {
    label: 'How to study Machine Learning fundamentals?',
  }
]
</script>

<template>
  <NuxtLayout name="default">
    <UDashboardPanel id="home" :ui="{ body: 'p-0 sm:p-0' }">
      <template #header>
        <DashboardNavbar />
      </template>

      <template #body>
        <UContainer class="flex-1 flex flex-col justify-center gap-4 sm:gap-6 py-8">
          <h1 class="text-3xl sm:text-4xl text-highlighted font-bold">
            How can we help you learn?
          </h1>

          <UChatPrompt
            v-model="input"
            :status="loading ? 'streaming' : 'ready'"
            class="[view-transition-name:chat-prompt]"
            variant="subtle"
            @submit="onSubmit"
          >
            <UChatPromptSubmit color="neutral" />
          </UChatPrompt>

          <div class="flex flex-wrap gap-2">
            <UButton
              v-for="quickChat in quickChats"
              :key="quickChat.label"
              :label="quickChat.label"
              size="sm"
              color="neutral"
              variant="outline"
              class="rounded-full"
              @click="createChat(quickChat.label)"
            />
          </div>
        </UContainer>
      </template>
    </UDashboardPanel>
  </NuxtLayout>
</template>
