<template>
  <div class="flex min-h-screen bg-dark-950">
    <AppSidebar />
    <main class="flex-1 ml-64 p-8">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import AppSidebar from '@/components/AppSidebar.vue'
</script>
