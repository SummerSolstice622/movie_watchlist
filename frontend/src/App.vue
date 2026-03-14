<template>
  <div class="app-container">
    <header class="app-header">
      <h1>🎬 电影观看记录</h1>
      <nav class="nav-menu">
        <button 
          @click="currentTab = 'list'"
          :class="{ active: currentTab === 'list' }"
        >
          观影记录
        </button>
        <button 
          @click="currentTab = 'manage'"
          :class="{ active: currentTab === 'manage' }"
        >
          管理数据
        </button>
        <button 
          @click="currentTab = 'stats'"
          :class="{ active: currentTab === 'stats' }"
        >
          统计信息
        </button>
      </nav>
    </header>

    <main class="app-main">
      <MovieList v-if="currentTab === 'list'" />
      <MovieManage v-else-if="currentTab === 'manage'" />
      <Statistics v-else-if="currentTab === 'stats'" />
    </main>
  </div>
</template>

<script>
import MovieList from './MovieList.vue'
import MovieManage from './MovieManage.vue'
import Statistics from './Statistics.vue'

export default {
  name: 'App',
  components: {
    MovieList,
    MovieManage,
    Statistics
  },
  data() {
    return {
      currentTab: 'list'
    }
  }
}
</script>

<style scoped>
.app-container {
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
}

.app-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 30px 20px;
  text-align: center;
}

.app-header h1 {
  font-size: 2.5em;
  margin-bottom: 20px;
  font-weight: 700;
}

.nav-menu {
  display: flex;
  justify-content: center;
  gap: 10px;
  flex-wrap: wrap;
}

.nav-menu button {
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 1em;
  font-weight: 500;
  transition: all 0.3s ease;
}

.nav-menu button:hover {
  background: rgba(255, 255, 255, 0.3);
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-2px);
}

.nav-menu button.active {
  background: white;
  color: #667eea;
  border-color: white;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.app-main {
  padding: 30px;
  min-height: 500px;
}

@media (max-width: 768px) {
  .app-header h1 {
    font-size: 1.8em;
  }

  .app-main {
    padding: 20px;
  }

  .nav-menu {
    gap: 5px;
  }

  .nav-menu button {
    padding: 8px 15px;
    font-size: 0.9em;
  }
}
</style>
