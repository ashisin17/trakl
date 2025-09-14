<script setup lang="ts">
const answers = reactive<Record<string, string>>({})

const toast = useToast()

async function submit() {
  const missing = QUIZ_QUESTIONS.filter(q => !answers[q.id])
  if (missing.length) {
    toast.add({ title: 'Please answer all questions', description: `${missing.length} question(s) left`, color: 'warning' })
    return
  }

  toast.add({ title: 'Preferences saved', description: 'Thanks — your preferences were recorded', color: 'success' })
  // navigate back or forward as needed
  navigateTo('/')
}
</script>

<template>
  <div class="p-4">
    <div class="space-y-4">
      <div v-for="q in QUIZ_QUESTIONS" :key="q.id">
        <UCard class="p-4">
          <div class="mb-3">
            <h4 class="text-sm font-semibold">{{ q.question }}</h4>
            <p class="text-xs text-gray-500">(category: {{ q.category || '—' }})</p>
          </div>

          <div class="flex flex-col gap-2">
            <label v-for="opt in q.options" :key="opt.value" class="flex items-center gap-3 cursor-pointer">
              <input
                type="radio"
                :name="q.id"
                :value="opt.value"
                v-model="answers[q.id]"
                class="accent-indigo-600"
              />
              <div>
                <div class="text-sm">{{ opt.text }}</div>
                <div v-if="opt.category || opt.weight" class="text-xs text-gray-400">{{ opt.category ? `category: ${opt.category}` : '' }} {{ opt.weight ? ` · weight: ${opt.weight}` : '' }}</div>
              </div>
            </label>
          </div>
        </UCard>
      </div>

      <div class="flex justify-end">
        <UButton color="primary" @click="submit">Save preferences</UButton>
      </div>
    </div>
  </div>
</template>