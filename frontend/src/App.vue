<template>
  <AppLayout>
    <router-view></router-view>
  </AppLayout>
  <ToastContainer />
</template>

<script setup>
import AppLayout from '@/components/common/AppLayout.vue'
import ToastContainer from '@/components/common/ToastContainer.vue'
</script>

<style>
/* 全局样式由 variables.css 提供 */
</style>
