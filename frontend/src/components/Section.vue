<!-- Section.vue -->
<template>
  <div>
    <div :style="{ fontWeight: 600, marginBottom: '10px', color }">
      {{ title }}
    </div>
    <slot />
  </div>
</template>

<script setup>
defineProps({
  title: String,
  color: String,
})
</script>
