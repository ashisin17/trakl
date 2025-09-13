<script setup lang="ts">
import { ref } from 'vue'

const name = ref('')
const username = useUsername();

function submit() {
  if (!name.value.trim()) return
  username.value = name.value.trim();
}

function cancel() {
}
</script>

<template>
  <div>
    <div class="fixed inset-0 flex items-center justify-center bg-black/50 z-50" @keydown.esc="cancel">
      <UCard class="w-11/12 max-w-md p-6" role="dialog" aria-modal="true" aria-labelledby="register-title">
        <h2 id="register-title" class="text-lg font-semibold mb-1">What's your name?</h2>
        <p class="text-sm text-gray-600 mb-4">Please enter your full name below.</p>

        <UInput
          v-model="name"
          placeholder="Your name"
          class="mb-4"
          @keyup.enter="submit"
          autofocus
        />

        <div class="flex justify-end gap-3">
          <UButton variant="ghost" color="neutral" @click="cancel">Cancel</UButton>
          <UButton color="primary" @click="submit">Submit</UButton>
        </div>
      </UCard>
    </div>
  </div>
</template>