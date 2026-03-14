<template>
  <div class="statistics-page">
    <!-- 顶部导航 -->
    <HeaderCard title="观影统计" subtitle="数据分析与可视化">
    </HeaderCard>

    <!-- 主要内容 -->
    <main class="page-main">
      <div class="container">
        <!-- 历年观影统计 - 独立显示 -->
        <div class="yearly-section">
          <div class="section-title">历年观影统计</div>
          <div id="yearChart" class="chart-wrapper"></div>
        </div>

        <!-- 年份过滤 -->
        <div class="filter-section">
          <el-select v-model="selectedYear" placeholder="按年份筛选" clearable style="width: 200px" @change="onYearChange">
            <el-option label="全部年份" value="" />
            <el-option
              v-for="item in availableYears"
              :key="item"
              :label="item"
              :value="item"
            />
          </el-select>
        </div>

        <!-- Tab标签页 - 出品年代、评分、主题 -->
        <el-tabs v-model="currentTab" class="tabs-container" @tab-change="onTabChange">
          <!-- 按出品年代统计 -->
          <el-tab-pane label="按出品年代统计" name="by-decade">
            <div id="decadeChart" class="chart-wrapper"></div>
          </el-tab-pane>

          <!-- 按评分统计 -->
          <el-tab-pane label="按评分区间统计" name="by-rating">
            <div id="ratingChart" class="chart-wrapper"></div>
          </el-tab-pane>

          <!-- 按主题统计 -->
          <el-tab-pane label="按主题统计" name="by-genre">
            <div id="genreChart" class="chart-wrapper"></div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </main>
  </div>
</template>

<script>
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import HeaderCard from './components/HeaderCard.vue'
import { movieAPI } from './api.js'

export default {
  name: 'Statistics',
  components: { HeaderCard },
  setup() {
    const currentTab = ref('by-decade')
    const selectedYear = ref('') // 默认为全部年份
    const yearlyStats = ref([])
    const filteredStats = ref({ by_decade: [], by_rating: [], by_genre: [] })

    let yearChartInstance = null
    let decadeChartInstance = null
    let ratingChartInstance = null
    let genreChartInstance = null

    const availableYears = computed(() => {
      return yearlyStats.value
        .map(item => item.year)
        .filter(year => year !== null && year !== undefined)
        .sort((a, b) => b - a)
    })

    const initCharts = async () => {
      try {
        const [resYearly, res] = await Promise.all([
          movieAPI.getStatisticsYearly(),
          movieAPI.getStatistics({ year: selectedYear.value })
        ])
        if (resYearly.data.success) {
          yearlyStats.value = resYearly.data.data
        }
        if (res.data.success) {
          filteredStats.value = res.data.data
        }
        await nextTick()
        renderYearChart()
        renderCharts()
      } catch (error) {
        console.error('获取统计数据失败:', error)
      }
    }

    const renderCharts = () => {
      if (currentTab.value === 'by-decade') {
        renderDecadeChart()
      } else if (currentTab.value === 'by-rating') {
        renderRatingChart()
      } else if (currentTab.value === 'by-genre') {
        renderGenreChart()
      }
    }

    const renderYearChart = () => {
      const chartDom = document.getElementById('yearChart')
      if (!chartDom) return

      const data = yearlyStats.value || []
      const sortedData = [...data].sort((a, b) => parseInt(a.year) - parseInt(b.year))
      const years = sortedData.map(item => String(item.year))
      const counts = sortedData.map(item => item.count)

      // 设置尺寸必须在 echarts.init() 之前
      const containerWidth = Math.max(600, years.length * 40)
      chartDom.style.width = containerWidth + 'px'
      chartDom.style.height = '400px'

      if (yearChartInstance) yearChartInstance.dispose()
      yearChartInstance = echarts.init(chartDom)

      const option = {
        title: { show: false },
        tooltip: { trigger: 'axis' },
        grid: { left: 50, right: 50, top: 20, bottom: 60, containLabel: false },
        xAxis: {
          type: 'category',
          data: years,
          axisLabel: {
            interval: 0,
            rotate: 45,
            fontSize: 11,
            margin: 8
          }
        },
        yAxis: { type: 'value', name: '电影数', axisLabel: { margin: 8 } },
        series: [{
          data: counts,
          type: 'bar',
          itemStyle: {
            color: '#6366f1',
            borderRadius: [4, 4, 0, 0]
          },
          label: {
            show: counts.length <= 20,
            position: 'top',
            fontSize: 11
          }
        }]
      }

      yearChartInstance.setOption(option)
      yearChartInstance.resize()
    }

    const renderDecadeChart = () => {
      const chartDom = document.getElementById('decadeChart')
      if (!chartDom) return

      chartDom.style.width = '100%'
      chartDom.style.height = '400px'

      if (decadeChartInstance) decadeChartInstance.dispose()
      decadeChartInstance = echarts.init(chartDom)

      const data = filteredStats.value.by_decade || []
      const decadeOrder = ['1940s及更早', '1950s', '1960s', '1970s', '1980s', '1990s', '2000s', '2010s', '2020s']
      const sortedData = [...data].sort((a, b) => decadeOrder.indexOf(a.decade) - decadeOrder.indexOf(b.decade))
      const decades = sortedData.map(item => item.decade)
      const counts = sortedData.map(item => item.count)

      const option = {
        title: { show: false },
        tooltip: { trigger: 'axis' },
        grid: { left: 80, right: 50, top: 20, bottom: 40, containLabel: true },
        xAxis: {
          type: 'category',
          data: decades,
          axisLabel: { rotate: 45, fontSize: 11 }
        },
        yAxis: { type: 'value', name: '电影数' },
        series: [{
          data: counts,
          type: 'bar',
          itemStyle: {
            color: '#ec4899',
            borderRadius: [4, 4, 0, 0]
          }
        }]
      }

      decadeChartInstance.setOption(option)
      decadeChartInstance.resize()
    }

    const renderRatingChart = () => {
      const chartDom = document.getElementById('ratingChart')
      if (!chartDom) return

      chartDom.style.width = '100%'
      chartDom.style.height = '400px'

      if (ratingChartInstance) ratingChartInstance.dispose()
      ratingChartInstance = echarts.init(chartDom)

      const data = filteredStats.value.by_rating || []
      const ratingOrder = ['9-10分', '8-9分', '7-8分', '6-7分', '低于6分']
      const sortedData = [...data].sort((a, b) => ratingOrder.indexOf(a.range) - ratingOrder.indexOf(b.range))
      const ranges = sortedData.map(item => item.range)
      const counts = sortedData.map(item => item.count)

      const option = {
        title: { show: false },
        tooltip: { trigger: 'axis' },
        grid: { left: 60, right: 50, top: 20, bottom: 40, containLabel: true },
        xAxis: {
          type: 'category',
          data: ranges,
          axisLabel: { fontSize: 11 }
        },
        yAxis: { type: 'value', name: '电影数' },
        series: [{
          data: counts,
          type: 'bar',
          itemStyle: {
            color: '#f59e0b',
            borderRadius: [4, 4, 0, 0]
          }
        }]
      }

      ratingChartInstance.setOption(option)
      ratingChartInstance.resize()
    }

    const renderGenreChart = () => {
      const chartDom = document.getElementById('genreChart')
      if (!chartDom) return

      const data = filteredStats.value.by_genre || []
      const genres = data.map(item => item.genre)
      const counts = data.map(item => item.count)

      const containerWidth = Math.max(800, genres.length * 60)
      chartDom.style.width = containerWidth + 'px'
      chartDom.style.height = '400px'

      if (genreChartInstance) genreChartInstance.dispose()
      genreChartInstance = echarts.init(chartDom)

      const option = {
        title: { show: false },
        tooltip: { trigger: 'axis' },
        grid: { left: 60, right: 50, top: 20, bottom: 80, containLabel: true },
        xAxis: {
          type: 'category',
          data: genres,
          axisLabel: {
            rotate: 45,
            fontSize: 11,
            interval: 0
          }
        },
        yAxis: { type: 'value', name: '出现次数' },
        series: [{
          data: counts,
          type: 'bar',
          itemStyle: {
            color: '#10b981',
            borderRadius: [4, 4, 0, 0]
          }
        }]
      }

      genreChartInstance.setOption(option)
      genreChartInstance.resize()
    }

    const onYearChange = () => {}
    // 年份变化由 watch 处理

    const onTabChange = () => {}
    // Tab 变化由 watch 处理

    onMounted(async () => {
      await initCharts()
    })

    // 监听年份变化
    watch(selectedYear, async () => {
      try {
        const res = await movieAPI.getStatistics({ year: selectedYear.value })
        if (res.data.success) {
          filteredStats.value = res.data.data
          await nextTick()
          renderCharts()
        }
      } catch (error) {
        console.error('获取统计数据失败:', error)
      }
    }, { immediate: false })

    // 监听tab切换，重新渲染图表
    watch(currentTab, async () => {
      await nextTick()
      renderCharts()
    })

    return {
      currentTab,
      selectedYear,
      availableYears,
      onYearChange,
      onTabChange,
      yearlyStats,
      filteredStats
    }
  }
}
</script>

<style scoped>
.statistics-page {
  padding: 24px;
  background: #f8fafc;
  min-height: calc(100vh - 60px);
}

.page-main {
  padding-bottom: 40px;
}

.container {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  max-width: 100%;
}

.yearly-section {
  margin-bottom: 40px;
  padding-bottom: 30px;
  border-bottom: 2px solid #f0f0f0;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 16px;
  color: #333;
}

.filter-section {
  margin-bottom: 24px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.tabs-container {
  margin-top: 20px;
}

.chart-wrapper {
  padding: 20px 0;
  overflow-x: auto;
  min-height: 400px;
}

:deep(.el-tabs__content) {
  padding: 0;
}

:deep(.el-tab-pane) {
  padding: 20px 0;
}
</style>
