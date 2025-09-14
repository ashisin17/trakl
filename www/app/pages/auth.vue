<script setup lang="ts">
const loginName = ref('')
const registerName = ref('')
const toast = useToast();

async function login() {
  if (!loginName.value.trim()) return
  try {
    const result = await $fetch('/api/auth/login', {
      method: 'POST',
      body: { name: loginName.value }
    })

    if (result) {
      navigateTo('/')
    }
  } catch (error) {
    toast.add({
      title: 'Login failed',
      description: 'We couldn\'t find your name.',
      icon: 'i-lucide-trash'
    })
  }
}

function register() {
  if (!registerName.value.trim()) return
  // TODO register
  navigateTo('/')
}

definePageMeta({
  middleware: function redirectIfProfileExists(_to, _from) {
    const {username} = useUsername();
    if (username.value) {
      return navigateTo('/');
    }
  },
  layout: 'auth'
})
</script>

<template>
  <div>
    <div class="fixed inset-0 flex items-center justify-center bg-black/50 z-50">
      <UContainer class="rounded-lg w-11/12 max-w-4xl shadow-lg p-6 flex items-stretch">
        <!-- Left: Login -->
        <UCard class="flex-1 p-6">
          <h3 class="text-lg font-semibold mb-2">Login</h3>
          <p class="text-sm text-gray-600 mb-4">Enter your name to sign in.</p>

          <UInput v-model="loginName" placeholder="Your name" class="mb-4" @keyup.enter="login" autofocus />

          <div class="flex justify-end">
            <UButton color="primary" @click="login">Login</UButton>
          </div>
        </UCard>

        <!-- Divider -->
        <div class="w-px bg-gray-800 mx-4 my-2" aria-hidden="true" />

        <!-- Right: Register -->
        <UCard class="flex-1 p-6">
          <h3 class="text-lg font-semibold mb-2">Register</h3>
          <p class="text-sm text-gray-600 mb-4">Create a new profile by entering your full name.</p>

          <UInput v-model="registerName" placeholder="Full name" class="mb-4" @keyup.enter="register" />

          <div class="flex justify-end">
            <UButton color="primary" @click="register">Register</UButton>
          </div>
        </UCard>
      </UContainer>
    </div>
  </div>
</template>