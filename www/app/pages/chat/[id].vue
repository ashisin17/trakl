<script setup lang="ts">
import type { DefineComponent } from 'vue'
import type { UIMessage } from 'ai'
import { useClipboard } from '@vueuse/core'
import { getTextFromMessage } from '@nuxt/ui/utils/ai'
import ProseStreamPre from '../../components/prose/PreStream.vue'
import { marked } from 'marked'
import { markedHighlight } from 'marked-highlight'
import hljs from 'highlight.js'

// Configure marked with syntax highlighting
marked.use({
  mangle: false,
  headerIds: false,
  gfm: true,
  breaks: true,
  smartLists: true,
  smartypants: true,
  xhtml: true
})

marked.use(markedHighlight({
  highlight: (code, lang) => {
    const language = hljs.getLanguage(lang) ? lang : 'plaintext'
    return hljs.highlight(code, { language }).value
  }
}))

interface ChatMessage {
  id: string
  role: 'user' | 'assistant'
  content: string
  parts?: Array<{ type: string; text: string }>
  createdAt: string
}

interface ChatState {
  id: string
  messages: ChatMessage[]
  status: 'idle' | 'sending' | 'streaming' | 'error'
  error: string | null
}

const components = {
  pre: ProseStreamPre as unknown as DefineComponent
}

const route = useRoute()
const toast = useToast()
const clipboard = useClipboard()

const chatId = computed(() => route.params.id as string)
const input = ref('')
const loading = ref(false)

// Initialize chat state
const chat = ref<ChatState>({
  id: chatId.value,
  messages: [],
  status: 'idle',
  error: null
})

// Fetch chat data
const { data, refresh, error } = await useFetch(`/api/chats/${chatId.value}`, {
  cache: 'force-cache',
  onResponse({ response }) {
    console.log('Chat fetch response:', response.status, response._data)
    if (response._data) {
      chat.value = {
        ...chat.value,
        ...response._data,
        status: 'idle'
      }
      
      // Auto-scroll to bottom when new messages arrive
      nextTick(() => {
        const container = document.querySelector('.chat-messages')
        if (container) {
          container.scrollTop = container.scrollHeight
        }
      })
    }
  },
  onResponseError({ response }) {
    console.error('Chat fetch error:', response.status, response._data)
    chat.value.error = response._data?.message || 'Failed to load chat'
    toast.add({
      title: 'Error',
      description: chat.value.error,
      color: 'red'
    })
  }
})

if (error.value) {
  console.error('Error loading chat:', error.value)
  chat.value.error = 'Failed to load chat. Please try again.'
}

// Watch for route changes to handle navigation between chats
watch(() => route.params.id, async (newId) => {
  if (newId) {
    await refresh()
  }
})

async function handleSubmit(e: Event) {
  e.preventDefault()
  const message = input.value.trim()
  if (!message || loading.value) return
  
  input.value = ''
  loading.value = true
  chat.value.status = 'sending'
  
  try {
    // Add user message immediately for better UX
    const userMessage: ChatMessage = {
      id: `msg-${Date.now()}`,
      role: 'user',
      content: message,
      createdAt: new Date().toISOString()
    }
    
    // Update local state
    chat.value.messages = [...(chat.value.messages || []), userMessage]
    
    // Add a temporary assistant message for better UX
    const tempAssistantMessage: ChatMessage = {
      id: `temp-${Date.now()}`,
      role: 'assistant',
      content: '',
      parts: [{ type: 'text', text: 'Thinking...' }],
      createdAt: new Date().toISOString()
    }
    
    chat.value.messages = [...chat.value.messages, tempAssistantMessage]
    
    // Send to server
    const response = await $fetch(`/api/chats/${chatId.value}`, {
      method: 'POST',
      body: { message },
      onResponse({ response }) {
        console.log('Message sent successfully:', response.status)
      },
      onResponseError({ response }) {
        console.error('Error sending message:', response.status, response._data)
        throw new Error(response._data?.message || 'Failed to send message')
      }
    })
    
    // Refresh chat data from server to get the complete response
    await refresh()
    
  } catch (error: any) {
    console.error('Error in handleSubmit:', error)
    
    // Remove the temporary message if it exists
    chat.value.messages = chat.value.messages.filter((msg: ChatMessage) => !msg.id.startsWith('temp-'))
    
    chat.value.error = error.message || 'Failed to send message. Please try again.'
    toast.add({
      title: 'Error',
      description: chat.value.error,
      color: 'red'
    })
  } finally {
    loading.value = false
    chat.value.status = 'idle'
  }
}

const copied = ref(false)

function copy(e: MouseEvent, message: UIMessage) {
  clipboard.copy(getTextFromMessage(message))

  copied.value = true

  setTimeout(() => {
    copied.value = false
  }, 2000)
}

onMounted(() => {
  if (data.value?.messages.length === 1) {
    // ask anshita for regeneration
  }
})
</script>

<template>
  <UDashboardPanel id="chat" class="relative" :ui="{ body: 'p-0 sm:p-0' }">
    <template #header>
      <DashboardNavbar />
    </template>

    <template #body>
      <UDashboardPanelContent class="flex flex-col h-full">
        <div class="flex-1 overflow-y-auto p-4 space-y-6 chat-messages">
          <template v-if="chat.messages?.length">
            <div v-for="message in chat.messages" :key="message.id" class="message">
              <div class="flex items-start gap-3 mb-6">
                <UAvatar
                  :src="message.role === 'assistant' ? '/logo.png' : undefined"
                  :alt="message.role === 'assistant' ? 'AI' : 'You'"
                  :text="message.role === 'assistant' ? 'AI' : 'You'"
                  size="sm"
                  class="flex-shrink-0 mt-1"
                />
                
                <div class="flex-1 min-w-0">
                  <div class="font-medium text-sm mb-1">
                    {{ message.role === 'assistant' ? 'AI Assistant' : 'You' }}
                  </div>
                  <div class="prose prose-sm dark:prose-invert max-w-none">
                    <template v-if="message.parts?.length">
                      <div v-for="(part, i) in message.parts" :key="i">
                        <div v-if="part.type === 'text'" class="whitespace-pre-wrap">
                          {{ part.text }}
                        </div>
                      </div>
                    </template>
                    <template v-else>
                      <div 
                        class="prose prose-sm dark:prose-invert max-w-none"
                        v-html="marked.parse(message.content || message.text || '')"
                      ></div>
                    </template>
                    
                    <!-- Add copy button for code blocks -->
                    <div v-if="message.role === 'assistant'" class="mt-2 flex justify-end">
                      <UButton
                        size="2xs"
                        color="gray"
                        variant="ghost"
                        icon="i-heroicons-clipboard-document"
                        :padded="false"
                        @click="copy($event, message)"
                        :title="copied ? 'Copied!' : 'Copy to clipboard'"
                        :class="{ 'text-green-500': copied }"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
          
          <div v-else class="flex items-center justify-center h-64 text-gray-500">
            <div class="text-center space-y-2">
              <UIcon name="i-heroicons-chat-bubble-oval-left-ellipsis" class="w-8 h-8 mx-auto text-gray-400" />
              <p>Start a new conversation</p>
            </div>
          </div>
          
          <div v-if="loading" class="flex items-center justify-center p-4">
            <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" />
          </div>
        </div>
        
        <div class="sticky bottom-0 bg-background/80 backdrop-blur-sm border-t border-gray-200 dark:border-gray-800 p-4">
          <form @submit.prevent="handleSubmit" class="max-w-3xl mx-auto w-full">
            <div class="relative">
              <UInput
                v-model="input"
                placeholder="Type your message..."
                :ui="{ size: 'lg', icon: { trailing: { pointer: 'cursor-pointer' } } }"
                :loading="loading"
                autocomplete="off"
                class="w-full"
              >
                <template #trailing>
                  <UButton
                    type="submit"
                    color="primary"
                    :disabled="!input.trim() || loading"
                    :loading="loading"
                    icon="i-heroicons-paper-airplane"
                    size="xs"
                    class="ml-2"
                  />
                </template>
              </UInput>
            </div>
          </form>
        </div>
      </UDashboardPanelContent>
    </template>
  </UDashboardPanel>
</template>

<style scoped>
.chat-messages {
  scroll-behavior: smooth;
}

.message {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.prose {
  --tw-prose-body: var(--color-gray-700);
  --tw-prose-headings: var(--color-gray-900);
  --tw-prose-links: var(--color-primary-600);
  --tw-prose-bold: var(--color-gray-900);
  --tw-prose-code: var(--color-gray-900);
  --tw-prose-pre-bg: var(--color-gray-50);
  --tw-prose-quote-borders: var(--color-gray-200);
  --tw-prose-quotes: var(--color-gray-600);
  --tw-prose-captions: var(--color-gray-500);
  --tw-prose-hr: var(--color-gray-200);
  --tw-prose-th-borders: var(--color-gray-300);
  --tw-prose-td-borders: var(--color-gray-200);
}

.dark .prose {
  --tw-prose-body: var(--color-gray-300);
  --tw-prose-headings: var(--color-white);
  --tw-prose-links: var(--color-primary-400);
  --tw-prose-bold: var(--color-white);
  --tw-prose-code: var(--color-white);
  --tw-prose-pre-bg: var(--color-gray-800);
  --tw-prose-quote-borders: var(--color-gray-700);
  --tw-prose-quotes: var(--color-gray-400);
  --tw-prose-captions: var(--color-gray-500);
  --tw-prose-hr: var(--color-gray-800);
  --tw-prose-th-borders: var(--color-gray-700);
  --tw-prose-td-borders: var(--color-gray-800);
}

.prose pre {
  @apply rounded-lg p-4 my-2 overflow-x-auto;
  background-color: var(--tw-prose-pre-bg);
}

.prose code {
  @apply px-1 py-0.5 rounded text-sm;
  background-color: var(--tw-prose-pre-bg);
}

.prose pre code {
  @apply p-0 bg-transparent;
}

.prose a {
  @apply underline-offset-4 hover:underline;
}

.prose ul {
  @apply list-disc pl-5 space-y-1;
}

.prose ol {
  @apply list-decimal pl-5 space-y-1;
}

.prose blockquote {
  @apply border-l-4 border-gray-200 dark:border-gray-700 pl-4 italic;
}

.prose table {
  @apply w-full border-collapse;
}

.prose th {
  @apply border-b-2 border-gray-200 dark:border-gray-700 p-2 text-left;
}

.prose td {
  @apply border-b border-gray-100 dark:border-gray-800 p-2;
}
</style>
