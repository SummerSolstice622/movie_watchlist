<template>
  <header class="header-card">
    <div class="header-content">
      <h1 class="header-title">{{ title }}</h1>
      <p v-if="subtitle" class="header-subtitle">{{ subtitle }}</p>
    </div>
    <slot />
  </header>
</template>

<script>
export default {
  name: 'HeaderCard',
  props: {
    title: {
      type: String,
      required: true
    },
    subtitle: {
      type: String,
      default: ''
    }
  }
}
</script>

<style scoped>
.header-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  padding: 24px 32px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 12px;
}
.header-title {
  margin: 0;
  font-size: 1.6rem;
  font-weight: 700;
}
.header-subtitle {
  margin: 4px 0 0;
  font-size: 0.95rem;
  opacity: 0.85;
}
</style>
