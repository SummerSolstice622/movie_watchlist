<template>
  <div class="movie-page">
    <!-- 顶部导航 -->
    <HeaderCard title="观影列表" subtitle="记录我看过的电影">
      <template #stats v-if="stats">
        <div class="stat-item">
          <span class="stat-value">{{ stats.total || 0 }}</span>
          <span class="stat-label">部</span>
        </div>
      </template>
    </HeaderCard>

    <!-- 主要内容 -->
    <main class="page-main">
      <div class="container">
        <!-- 过滤控件 -->
        <div class="filter-bar">
          <div class="filter-row">
            <!-- 时间过滤：粒度选择和级联选择器 -->
            <div class="filter-group">
              <span class="filter-label">观影时间</span>
              <!-- 粒度切换选项 -->
              <el-radio-group
                v-model="dateGranularity"
                @change="onDateGranularityChange"
                size="small"
                style="margin-right: 12px"
              >
                <el-radio value="year">按年</el-radio>
                <el-radio value="month">按月</el-radio>
              </el-radio-group>
              <!-- 级联选择器 -->
              <el-cascader
                v-model="dateFilterValue"
                :options="dateFilterOptions"
                :props="cascaderProps"
                clearable
                :placeholder="dateGranularity === 'year' ? '选择年份' : '选择年/月'"
                @change="onDateFilterChange"
                :max-collapse-tags="1"
                style="width: 180px"
              />
              <!-- 快速过滤标签 -->
              <div class="quick-date-filters">
                <el-button
                  v-for="tag in quickDateTags"
                  :key="tag.value"
                  :type="isDateTagActive(tag) ? 'primary' : 'info'"
                  link
                  size="small"
                  @click="setQuickDateFilter(tag)"
                >
                  {{ tag.label }}
                </el-button>
              </div>
            </div>

            <!-- 出品年代 -->
            <el-select v-model="filters.decade" @change="onDecadeChange" placeholder="出品年代" clearable style="width: 130px">
              <el-option v-for="d in decades" :key="d" :label="d" :value="d" />
            </el-select>

            <!-- 评分人数 -->
            <el-select v-model="filters.vote_count_min" @change="onVoteCountChange" placeholder="评分人数" clearable style="width: 130px">
              <el-option v-for="v in voteCountOptions" :key="v.value" :label="v.label" :value="v.value" />
            </el-select>

            <!-- 电影主题/类型 -->
            <el-select v-model="filters.genres" @change="onGenresChange" placeholder="电影主题" clearable style="width: 150px">
              <el-option v-for="g in genresList" :key="g" :label="g" :value="g" />
            </el-select>

            <!-- 搜索 -->
            <el-input v-model="filters.search" @input="onSearch" placeholder="搜索电影名" clearable style="width: 160px">
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>

            <!-- 排序 -->
            <el-select v-model="filters.sort_by" @change="onSortChange" placeholder="排序" style="width: 150px">
              <el-option v-for="s in sortOptions" :key="s.value" :label="s.label" :value="s.value" />
            </el-select>

            <!-- 评分范围 -->
            <div class="rating-filter">
              <span class="rating-label">评分</span>
              <el-slider
                v-model="ratingRange"
                range
                :min="0"
                :max="10"
                :step="0.5"
                :marks="ratingMarks"
                :format-tooltip="(val) => val + '分'"
                @change="onRatingChange"
                style="width: 200px"
              />
              <el-button
                v-if="ratingRange[0] !== 0 || ratingRange[1] !== 10"
                type="info"
                link
                size="small"
                @click="clearRatingFilter"
              >
                重置
              </el-button>
            </div>

            <!-- 多次观看 -->
            <el-checkbox v-model="filters.multipleWatch" @change="onMultipleWatchChange">
              只看多次观看
            </el-checkbox>

            <!-- 重置按钮 -->
            <el-button type="primary" plain @click="resetFilters" size="default">
              <el-icon><Refresh /></el-icon>
            </el-button>
          </div>
        </div>

        <!-- 结果统计和操作按钮 -->
        <div class="result-bar">
          <span class="result-count">共 {{ pagination.total }} 部</span>
          <div class="action-buttons">
            <el-button type="success" @click="showAddMovieDialog" size="default">
              <el-icon><Plus /></el-icon> 新增观影
            </el-button>
            <el-button type="primary" plain @click="handleExport" size="default" :loading="exporting">
              <el-icon><Download /></el-icon> 导出Excel
            </el-button>
          </div>
        </div>

        <!-- 电影列表 -->
        <div v-if="loading" class="loading">
          <div class="spinner"></div>
          <p>加载中...</p>
        </div>

        <div v-else-if="records.length === 0" class="empty-state">
          <h3>暂无观影记录</h3>
          <p>请尝试调整过滤条件</p>
        </div>

        <div v-else class="grid grid-3">
          <MovieCard
            v-for="record in records"
            :key="`${record.tmdb_id}-${record.watched_date}`"
            :record="record"
            :cinemas="cinemas"
            @edit-date="handleEditDate"
            @delete="handleDeleteRecord"
          />
        </div>

        <!-- 分页 -->
        <div class="pagination-bar" v-if="pagination.pages > 1">
          <el-pagination
            v-model:current-page="currentPage"
            :page-size="pagination.limit"
            :total="pagination.total"
            layout="prev, pager, next"
            @current-change="fetchRecords"
          />
        </div>
      </div>
    </main>

    <!-- 编辑日期对话框 -->
    <el-dialog v-model="editDateDialogVisible" title="修改观影日期" width="400px">
      <div class="edit-date-form">
        <p class="movie-name">{{ editingRecord?.title }}</p>
        <el-date-picker
          v-model="newWatchedDate"
          type="date"
          placeholder="选择观影日期"
          format="YYYY-MM-DD"
          value-format="YYYY-MM-DD"
          style="width: 100%"
        />
      </div>
      <template #footer>
        <el-button @click="editDateDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmEditDate" :loading="saving">确定</el-button>
      </template>
    </el-dialog>

    <!-- 新增观影对话框 -->
    <el-dialog v-model="addMovieDialogVisible" title="新增观影记录" width="600px">
      <div class="add-movie-form">
        <!-- 搜索模式选择 -->
        <div class="search-mode-section">
          <el-radio-group v-model="searchMode" size="small">
            <el-radio value="name">按名称搜索</el-radio>
            <el-radio value="id">按ID搜索</el-radio>
          </el-radio-group>
        </div>

        <!-- 搜索电影 -->
        <div class="search-section">
          <el-input
            v-model="searchQuery"
            :placeholder="searchMode === 'id' ? '输入电影ID (如: 407545)' : '搜索电影名称'"
            @keyup.enter="searchMovies(1)"
            clearable
          >
            <template #append>
              <el-button @click="searchMovies(1)" :loading="searching">
                <el-icon><Search /></el-icon>
              </el-button>
            </template>
          </el-input>
        </div>

        <!-- 搜索结果 -->
        <div v-if="searchResults.length > 0" ref="searchResultsContainer" class="search-results">
          <div
            v-for="movie in searchResults"
            :key="movie.id"
            class="search-result-item"
            :class="{ selected: selectedMovie?.id === movie.id }"
            @click="selectMovie(movie)"
          >
            <img
              v-if="movie.poster_path"
              :src="`https://image.tmdb.org/t/p/w92${movie.poster_path}`"
              class="result-poster"
            />
            <div v-else class="result-poster-placeholder">
              <el-icon><VideoCamera /></el-icon>
            </div>
            <div class="result-info">
              <div class="result-title">{{ movie.title }}</div>
              <div class="result-original" v-if="movie.original_title !== movie.title">{{ movie.original_title }}</div>
              <div class="result-meta">{{ movie.release_date?.substring(0, 4) || '未知年份' }}</div>
            </div>
          </div>

          <!-- 搜索结果分页（仅名称搜索模式显示） -->
          <div class="search-pagination" v-if="searchResults.length > 0 && searchMode === 'name'">
            <el-button
              @click="searchPrevPage"
              :disabled="searchPagination.page <= 1"
              size="small"
            >
              上一页
            </el-button>
            <span class="pagination-info">第 {{ searchPagination.page }} 页</span>
            <el-button
              @click="searchNextPage"
              :disabled="searchResults.length < 20"
              size="small"
            >
              下一页
            </el-button>
          </div>
        </div>

        <!-- 选中的电影 -->
        <div v-if="selectedMovie" class="selected-movie-section">
          <h4>已选择: {{ selectedMovie.title }}</h4>
          <el-date-picker
            v-model="addWatchedDate"
            type="date"
            placeholder="选择观影日期"
            format="YYYY-MM-DD"
            value-format="YYYY-MM-DD"
            style="width: 100%"
          />
        </div>
      </div>
      <template #footer>
        <el-button @click="addMovieDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmAddMovie" :loading="adding" :disabled="!selectedMovie || !addWatchedDate">
          添加
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch, nextTick } from 'vue'
import { Search, Refresh, Plus, Download, VideoCamera } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import MovieCard from './components/MovieCard.vue'
import HeaderCard from './components/HeaderCard.vue'
import { movieAPI } from './api.js'

export default {
  name: 'MovieList',
  components: { MovieCard, HeaderCard, Search, Refresh, Plus, Download, VideoCamera },
  setup() {
    const loading = ref(false)
    const records = ref([])
    const years = ref([])
    const cinemas = ref([])
    const months = ref([])
    const monthsByYear = ref({}) // 按年份存储的月份映射
    const decades = ref([])
    const stats = ref({ total: 0 })
    const currentPage = ref(1)
    const pagination = reactive({
      page: 1,
      limit: 20,
      total: 0,
      pages: 0
    })

    const filters = reactive({
      year: '',
      month: '',
      day: '',
      decade: '',
      rating_min: null,
      rating_max: null,
      vote_count_min: null,
      genres: '',
      search: '',
      sort_by: 'watched_date_desc',
      sort_order: 'desc',
      multipleWatch: false
    })

    // 新增：时间过滤相关
    const dateFilterValue = ref([]) // 级联选择器的值，例如 [2015, 6, 22]
    const dateFilterOptions = ref([]) // 级联选择器的选项
    const dateGranularity = ref('month') // 时间粒度：'year' 或 'month'
    const cascaderProps = {
      value: 'value',
      label: 'label',
      children: 'children',
      expandTrigger: 'hover'
    }

    // 快速过滤标签
    const quickDateTags = [
      { value: 'this_month', label: '本月' },
      { value: 'this_year', label: '今年' },
      { value: 'last_month', label: '上月' },
      { value: 'last_year', label: '去年' }
    ]

    const ratingRange = ref([0, 10])

    const ratingMarks = {
      0: '0',
      5: '5',
      10: '10'
    }

    const voteCountOptions = [
      { value: 100, label: '100+人' },
      { value: 500, label: '500+人' },
      { value: 1000, label: '1000+人' },
      { value: 5000, label: '5000+人' },
      { value: 10000, label: '1万+人' }
    ]

    const sortOptions = [
      { value: 'watched_date_desc', label: '观看日期 ↓' },
      { value: 'watched_date_asc', label: '观看日期 ↑' },
      { value: 'release_date_desc', label: '出品年份 ↓' },
      { value: 'release_date_asc', label: '出品年份 ↑' },
      { value: 'vote_average_desc', label: '评分 ↓' },
      { value: 'vote_average_asc', label: '评分 ↑' },
      { value: 'vote_count_desc', label: '评分人数 ↓' },
      { value: 'vote_count_asc', label: '评分人数 ↑' }
    ]

    // 电影主题/类型列表
    const genresList = ref([])

    // 编辑日期相关
    const editDateDialogVisible = ref(false)
    const editingRecord = ref(null)
    const newWatchedDate = ref('')
    const saving = ref(false)

    // 新增电影相关
    const addMovieDialogVisible = ref(false)
    const searchQuery = ref('')
    const searchMode = ref('name') // 'name' 或 'id'
    const searchResults = ref([])
    const searchResultsContainer = ref(null)
    const searchPagination = reactive({
      page: 1,
      total: 20, // TMDB默认每页20条
      pages: 1
    })
    const selectedMovie = ref(null)
    const addWatchedDate = ref('')
    const searching = ref(false)
    const adding = ref(false)

    // 导出相关
    const exporting = ref(false)

    // 构建联动参数
    const buildFilterParams = () => {
      const params = {}
      if (filters.year) params.year = filters.year
      if (filters.month) params.month = filters.month
      if (filters.day) params.day = filters.day
      if (filters.decade) params.decade = filters.decade
      if (filters.rating_min !== null) params.rating_min = filters.rating_min
      if (filters.rating_max !== null) params.rating_max = filters.rating_max
      if (filters.vote_count_min !== null) params.vote_count_min = filters.vote_count_min
      if (filters.genres) params.genres = filters.genres
      if (filters.search) params.search = filters.search
      if (filters.multipleWatch) params.multiple_watch = true
      return params
    }

    // 获取联动筛选项
    const fetchFilterOptions = async (trigger = '') => {
      const params = buildFilterParams()

      // 根据触发源，排除自身参数
      const yearsParams = { ...params }
      const monthsParams = { ...params }
      const decadesParams = { ...params }

      delete yearsParams.year
      delete monthsParams.month
      delete decadesParams.decade

      try {
        const [yearsRes, monthsRes, decadesRes] = await Promise.all([
          movieAPI.getYears(yearsParams),
          movieAPI.getMonths(monthsParams),
          movieAPI.getDecades(decadesParams)
        ])

        if (yearsRes.data.success) {
          years.value = yearsRes.data.data.filter(y => y)
        }
        if (monthsRes.data.success) {
          months.value = monthsRes.data.data.filter(m => m)
        }
        if (decadesRes.data.success) {
          decades.value = decadesRes.data.data.filter(d => d)
        }

        // 为每个年份获取该年份的月份（实现联动）
        await fetchMonthsForEachYear()

        // 构建级联选择器的选项
        buildDateFilterOptions()
      } catch (error) {
        console.error('获取筛选选项失败:', error)
      }
    }

    // 为每个年份获取该年份的月份
    const fetchMonthsForEachYear = async () => {
      const monthsMap = {}

      // 并行获取每个年份的月份
      const promises = years.value.map(year =>
        (async () => {
          const params = buildFilterParams()
          params.year = year
          delete params.month

          try {
            const res = await movieAPI.getMonths(params)
            if (res.data.success) {
              monthsMap[year] = res.data.data.filter(m => m)
            } else {
              monthsMap[year] = []
            }
          } catch (error) {
            console.warn(`获取年份 ${year} 的月份失败:`, error)
            monthsMap[year] = []
          }
        })()
      )

      await Promise.all(promises)
      monthsByYear.value = monthsMap
    }

    // 获取电影主题/类型列表
    const fetchGenres = async () => {
      const params = buildFilterParams()
      // 排除genres参数，因为我们要获取所有可用的genres
      delete params.genres

      try {
        const res = await movieAPI.getGenres(params)
        if (res.data.success) {
          genresList.value = res.data.data || []
        }
      } catch (error) {
        console.error('获取主题列表失败:', error)
      }
    }

    // 构建时间过滤下拉框的级联选项
    const buildDateFilterOptions = () => {
      const options = []
      for (const year of years.value) {
        const yearOption = {
          value: year,
          label: String(year),
          children: []
        }

        // 如果粒度是"月"，则添加月份子选项
        if (dateGranularity.value === 'month') {
          // 对于每个年份，只添加该年份实际存在的月份
          // 这里需要通过API获取该年份的月份，但为了简化，
          // 我们使用一个变量来存储年份对应的月份映射
          const monthsForThisYear = monthsByYear.value[year] || months.value

          for (const month of monthsForThisYear) {
            const monthOption = {
              value: parseInt(month),
              label: `${month}月`
            }

            yearOption.children.push(monthOption)
          }
        }

        options.push(yearOption)
      }
      dateFilterOptions.value = options
    }

    // 下拉框改变事件
    const onYearChange = () => {
      currentPage.value = 1
      fetchFilterOptions('year')
      fetchRecords()
    }

    const onMonthChange = () => {
      currentPage.value = 1
      fetchFilterOptions('month')
      fetchRecords()
    }

    const onDecadeChange = () => {
      currentPage.value = 1
      fetchFilterOptions('decade')
      fetchGenres()
      fetchRecords()
    }

    const onVoteCountChange = () => {
      currentPage.value = 1
      fetchFilterOptions('vote_count')
      fetchGenres()
      fetchRecords()
    }

    const onGenresChange = () => {
      currentPage.value = 1
      fetchRecords()
    }

    let searchTimer = null
    const onSearch = () => {
      if (searchTimer) clearTimeout(searchTimer)
      searchTimer = setTimeout(() => {
        currentPage.value = 1
        fetchFilterOptions('search')
        fetchGenres()
        fetchRecords()
      }, 300)
    }

    const onRatingChange = () => {
      filters.rating_min = ratingRange.value[0]
      filters.rating_max = ratingRange.value[1]
      currentPage.value = 1
      fetchFilterOptions('rating')
      fetchGenres()
      fetchRecords()
    }

    const clearRatingFilter = () => {
      ratingRange.value = [0, 10]
      filters.rating_min = null
      filters.rating_max = null
      currentPage.value = 1
      fetchFilterOptions('rating')
      fetchRecords()
    }

    const resetFilters = () => {
      // 重置所有筛选条件
      dateFilterValue.value = []
      dateGranularity.value = 'month'
      filters.year = ''
      filters.month = ''
      filters.day = ''
      filters.decade = ''
      filters.rating_min = null
      filters.rating_max = null
      filters.vote_count_min = null
      filters.genres = ''
      filters.search = ''
      filters.sort_by = 'watched_date_desc'
      filters.sort_order = 'desc'
      filters.multipleWatch = false
      ratingRange.value = [0, 10]
      currentPage.value = 1
      fetchFilterOptions()
      fetchGenres()
      fetchRecords()
    }

    const onSortChange = () => {
      currentPage.value = 1
      fetchRecords()
    }

    const onMultipleWatchChange = () => {
      currentPage.value = 1
      fetchFilterOptions('multipleWatch')
      fetchRecords()
    }

    // 新增：处理时间粒度变化
    const onDateGranularityChange = () => {
      dateFilterValue.value = []
      filters.year = ''
      filters.month = ''
      filters.day = ''
      currentPage.value = 1
      fetchFilterOptions('date')
      fetchRecords()
    }

    // 新增：处理级联选择器变化
    const onDateFilterChange = (value) => {
      if (!value || value.length === 0) {
        // 清空日期过滤
        filters.year = ''
        filters.month = ''
        filters.day = ''
      } else if (dateGranularity.value === 'year') {
        // 按年粒度：只接受年份
        filters.year = String(value[0])
        filters.month = ''
        filters.day = ''
      } else if (dateGranularity.value === 'month') {
        // 按月粒度：接受年份和月份
        if (value.length === 1) {
          // 只选择年份
          filters.year = String(value[0])
          filters.month = ''
          filters.day = ''
        } else if (value.length >= 2) {
          // 选择年份和月份（精确到月）
          filters.year = String(value[0])
          filters.month = String(value[1]).padStart(2, '0')
          filters.day = ''
        }
      }
      currentPage.value = 1
      fetchFilterOptions('date')
      fetchRecords()
    }

    // 新增：一个辅助函数来支持不指定年份但指定月日的过滤
    const setDateWithoutYear = (month, day) => {
      filters.year = ''
      filters.month = String(month).padStart(2, '0')
      filters.day = String(day).padStart(2, '0')
      dateFilterValue.value = []
      currentPage.value = 1
      fetchFilterOptions('date')
      fetchRecords()
    }

    // 快速过滤：检查标签是否激活
    const isDateTagActive = (tag) => {
      const today = new Date()
      const currentYear = today.getFullYear()
      const currentMonth = String(today.getMonth() + 1).padStart(2, '0')

      switch (tag.value) {
        case 'this_month':
          return filters.year === String(currentYear) && filters.month === currentMonth
        case 'this_year':
          return filters.year === String(currentYear) && filters.month === ''
        case 'last_month':
          const lastMonth = currentMonth === '01' ? '12' : String(parseInt(currentMonth) - 1).padStart(2, '0')
          const lastMonthYear = currentMonth === '01' ? currentYear - 1 : currentYear
          return filters.year === String(lastMonthYear) && filters.month === lastMonth
        case 'last_year':
          return filters.year === String(currentYear - 1) && filters.month === ''
        default:
          return false
      }
    }

    // 快速过滤：设置日期过滤
    const setQuickDateFilter = (tag) => {
      const today = new Date()
      const currentYear = today.getFullYear()
      const currentMonth = String(today.getMonth() + 1).padStart(2, '0')

      dateFilterValue.value = []

      switch (tag.value) {
        case 'this_month':
          filters.year = String(currentYear)
          filters.month = currentMonth
          dateFilterValue.value = [currentYear, parseInt(currentMonth)]
          break
        case 'this_year':
          filters.year = String(currentYear)
          filters.month = ''
          dateFilterValue.value = [currentYear]
          break
        case 'last_month':
          const lastMonth = currentMonth === '01' ? '12' : String(parseInt(currentMonth) - 1).padStart(2, '0')
          const lastMonthYear = currentMonth === '01' ? currentYear - 1 : currentYear
          filters.year = String(lastMonthYear)
          filters.month = lastMonth
          dateFilterValue.value = [lastMonthYear, parseInt(lastMonth)]
          break
        case 'last_year':
          filters.year = String(currentYear - 1)
          filters.month = ''
          dateFilterValue.value = [currentYear - 1]
          break
      }

      currentPage.value = 1
      fetchFilterOptions('date')
      fetchRecords()
    }

    const monthOptions = [
      { value: '01', label: '1月' },
      { value: '02', label: '2月' },
      { value: '03', label: '3月' },
      { value: '04', label: '4月' },
      { value: '05', label: '5月' },
      { value: '06', label: '6月' },
      { value: '07', label: '7月' },
      { value: '08', label: '8月' },
      { value: '09', label: '9月' },
      { value: '10', label: '10月' },
      { value: '11', label: '11月' },
      { value: '12', label: '12月' }
    ]

    const fetchStats = async () => {
      try {
        const res = await movieAPI.getStats()
        if (res.data.success) {
          stats.value = res.data.data
        }
      } catch (error) {
        console.error('获取统计失败:', error)
      }
    }

    const fetchRecords = async () => {
      loading.value = true
      try {
        // 解析排序选项，格式为 sort_by_order
        let sortBy = filters.sort_by
        let sortOrder = filters.sort_order
        if (filters.sort_by.includes('_asc')) {
          sortBy = filters.sort_by.replace('_asc', '')
          sortOrder = 'asc'
        } else if (filters.sort_by.includes('_desc')) {
          sortBy = filters.sort_by.replace('_desc', '')
          sortOrder = 'desc'
        }

        const params = {
          page: currentPage.value,
          limit: pagination.limit,
          year: filters.year || undefined,
          month: filters.month || undefined,
          day: filters.day || undefined,
          decade: filters.decade || undefined,
          rating_min: filters.rating_min || undefined,
          rating_max: filters.rating_max || undefined,
          vote_count_min: filters.vote_count_min || undefined,
          genres: filters.genres || undefined,
          search: filters.search || undefined,
          sort_by: sortBy,
          sort_order: sortOrder,
          multiple_watch: filters.multipleWatch || undefined
        }
        const res = await movieAPI.getRecords(params)
        if (res.data.success) {
          records.value = res.data.data
          Object.assign(pagination, res.data.pagination)
        }
      } catch (error) {
        console.error('获取观影记录失败:', error)
      } finally {
        loading.value = false
      }
    }

    // 加载影院列表
    const fetchCinemas = async () => {
      try {
        const res = await movieAPI.getCinemas({ limit: 1000 })
        if (res.data.success) {
          cinemas.value = res.data.data
        }
      } catch (error) {
        console.error('加载影院列表失败:', error)
      }
    }

    onMounted(() => {
      fetchFilterOptions()
      fetchGenres()
      fetchStats()
      fetchCinemas()
      fetchRecords()
    })

    // 编辑日期处理
    const handleEditDate = (record) => {
      editingRecord.value = record
      newWatchedDate.value = record.watched_date.replace(/\//g, '-')
      editDateDialogVisible.value = true
    }

    const confirmEditDate = async () => {
      if (!newWatchedDate.value) {
        ElMessage.warning('请选择日期')
        return
      }
      saving.value = true
      try {
        const res = await movieAPI.updateWatchedDate(
          editingRecord.value.tmdb_id,
          editingRecord.value.watched_date,
          newWatchedDate.value
        )
        if (res.data.success) {
          ElMessage.success('更新成功')
          editDateDialogVisible.value = false
          fetchRecords()
        }
      } catch (error) {
        console.error('更新日期失败:', error)
        // 显示错误信息
        const errorMsg = error.response?.data?.detail || '更新失败'
        ElMessage.error(errorMsg)
      } finally {
        saving.value = false
      }
    }

    // 删除记录处理
    const handleDeleteRecord = async (record) => {
      try {
        await ElMessageBox.confirm(
          `确定删除「${record.title}」的观影记录吗？`,
          '确认删除',
          { type: 'warning' }
        )
        const res = await movieAPI.deleteRecord(record.tmdb_id, record.watched_date)
        if (res.data.success) {
          ElMessage.success('删除成功')
          fetchRecords()
          fetchStats()
        }
      } catch (error) {
        if (error !== 'cancel') {
          console.error('删除失败:', error)
          ElMessage.error('删除失败')
        }
      }
    }

    // 新增电影处理
    const showAddMovieDialog = () => {
      searchQuery.value = ''
      searchResults.value = []
      searchPagination.page = 1
      selectedMovie.value = null
      addWatchedDate.value = ''
      addMovieDialogVisible.value = true
    }

    const searchMovies = async (page = 1) => {
      if (!searchQuery.value.trim()) return
      searching.value = true
      try {
        let res
        if (searchMode.value === 'id') {
          // 按ID搜索
          res = await movieAPI.getMovieById(searchQuery.value)
          if (res.data.success) {
            searchResults.value = res.data.data ? [res.data.data] : []
            searchPagination.page = 1
            searchPagination.total = 1
          }
        } else {
          // 按名称搜索
          res = await movieAPI.searchMovies(searchQuery.value, page)
          if (res.data.success) {
            searchResults.value = res.data.data
            searchPagination.page = res.data.page || page
            searchPagination.total = res.data.data.length
          }
        }
      } catch (error) {
        console.error('搜索失败:', error)
        ElMessage.error('搜索失败')
      } finally {
        searching.value = false
      }
    }

    const searchNextPage = () => {
      if (searchMode.value === 'id') {
        ElMessage.warning('按ID搜索不支持分页')
        return
      }
      searchMovies(searchPagination.page + 1)
      scrollSearchResultsToTop()
    }

    const searchPrevPage = () => {
      if (searchMode.value === 'id') {
        ElMessage.warning('按ID搜索不支持分页')
        return
      }
      if (searchPagination.page > 1) {
        searchMovies(searchPagination.page - 1)
        scrollSearchResultsToTop()
      }
    }

    const scrollSearchResultsToTop = () => {
      // 使用 nextTick 确保 DOM 更新后再滚动
      nextTick(() => {
        if (searchResultsContainer.value) {
          searchResultsContainer.value.scrollTop = 0
        }
      })
    }

    const selectMovie = (movie) => {
      selectedMovie.value = movie
    }

    const confirmAddMovie = async () => {
      if (!selectedMovie.value || !addWatchedDate.value) return
      adding.value = true
      try {
        // 先添加电影信息
        await movieAPI.addMovieFromTmdb(selectedMovie.value.id)
        // 再添加观影记录
        const res = await movieAPI.addRecord(selectedMovie.value.id, addWatchedDate.value)
        if (res.data.success) {
          ElMessage.success('添加成功')
          addMovieDialogVisible.value = false
          fetchRecords()
          fetchStats()
        }
      } catch (error) {
        console.error('添加失败:', error)
        ElMessage.error(error.response?.data?.detail || '添加失败')
      } finally {
        adding.value = false
      }
    }

    // 导出处理
    const handleExport = async () => {
      exporting.value = true
      try {
        let sortBy = filters.sort_by
        let sortOrder = filters.sort_order
        if (filters.sort_by.includes('_asc')) {
          sortBy = filters.sort_by.replace('_asc', '')
          sortOrder = 'asc'
        } else if (filters.sort_by.includes('_desc')) {
          sortBy = filters.sort_by.replace('_desc', '')
          sortOrder = 'desc'
        }

        const params = {
          year: filters.year || undefined,
          month: filters.month || undefined,
          decade: filters.decade || undefined,
          rating_min: filters.rating_min || undefined,
          rating_max: filters.rating_max || undefined,
          vote_count_min: filters.vote_count_min || undefined,
          search: filters.search || undefined,
          sort_by: sortBy,
          sort_order: sortOrder
        }
        const res = await movieAPI.exportRecords(params)

        // 创建下载链接
        const blob = new Blob([res.data], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' })
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url
        let filename = '观影记录'
        if (filters.year) filename += `_${filters.year}年`
        if (filters.month) filename += `_${filters.month}月`
        a.download = `${filename}.xlsx`
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)

        ElMessage.success('导出成功')
      } catch (error) {
        console.error('导出失败:', error)
        ElMessage.error('导出失败')
      } finally {
        exporting.value = false
      }
    }

    return {
      loading,
      records,
      cinemas,
      years,
      months,
      monthsByYear,
      decades,
      stats,
      currentPage,
      pagination,
      filters,
      monthOptions,
      voteCountOptions,
      sortOptions,
      ratingRange,
      ratingMarks,
      // 新增：时间过滤
      dateFilterValue,
      dateFilterOptions,
      dateGranularity,
      cascaderProps,
      quickDateTags,
      onDateGranularityChange,
      onDateFilterChange,
      setDateWithoutYear,
      isDateTagActive,
      setQuickDateFilter,
      onYearChange,
      onMonthChange,
      onDecadeChange,
      onVoteCountChange,
      onGenresChange,
      onSortChange,
      onMultipleWatchChange,
      onSearch,
      onRatingChange,
      clearRatingFilter,
      resetFilters,
      fetchRecords,
      fetchGenres,
      genresList,
      // 编辑日期
      editDateDialogVisible,
      editingRecord,
      newWatchedDate,
      saving,
      handleEditDate,
      confirmEditDate,
      // 删除记录
      handleDeleteRecord,
      // 新增电影
      addMovieDialogVisible,
      searchQuery,
      searchMode,
      searchResults,
      searchResultsContainer,
      searchPagination,
      selectedMovie,
      addWatchedDate,
      searching,
      adding,
      showAddMovieDialog,
      searchMovies,
      searchNextPage,
      searchPrevPage,
      selectMovie,
      confirmAddMovie,
      // 导出
      exporting,
      handleExport
    }
  }
}
</script>

<style scoped>
.movie-page {
  padding: 24px;
  background: #f8fafc;
  min-height: calc(100vh - 60px);
}

.page-main {
  padding-bottom: 40px;
}

.container {
  background: transparent;
  padding: 0;
  max-width: 100%;
}

.filter-bar {
  margin-bottom: 16px;
}

.filter-row {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
}

/* 时间过滤组 */
.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.filter-label {
  font-size: 13px;
  color: #64748b;
  font-weight: 500;
  white-space: nowrap;
}

/* 快速过滤标签 */
.quick-date-filters {
  display: flex;
  gap: 4px;
  flex-wrap: wrap;
}

.quick-date-filters :deep(.el-button--link) {
  padding: 0 6px;
  font-size: 12px;
}

.quick-date-filters :deep(.el-button--link.is-text) {
  color: #94a3b8;
}

.quick-date-filters :deep(.el-button--link.is-text:hover) {
  color: #6366f1;
}

.quick-date-filters :deep(.el-button--primary) {
  color: #6366f1;
  font-weight: 500;
}

.rating-filter {
  display: flex;
  align-items: center;
  gap: 8px;
}

.rating-label {
  font-size: 14px;
  color: var(--light-text, #64748b);
  white-space: nowrap;
}

.result-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.result-count {
  font-size: 14px;
  color: var(--light-text, #64748b);
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.loading,
.empty-state {
  padding: 60px 20px;
  text-align: center;
  color: var(--light-text, #64748b);
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color, #e2e8f0);
  border-top-color: var(--primary-color, #6366f1);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.pagination-bar {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

/* 网格布局 - 固定 3 列 */
.grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
}

/* 响应式适配 */
@media (max-width: 1200px) {
  .grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .grid {
    grid-template-columns: 1fr;
  }
}

/* 电影卡片统一高度 */
.grid > :deep(.movie-card-wrapper) {
  display: flex;
}

.grid > :deep(.movie-card-wrapper .movie-card) {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* 编辑日期对话框 */
.edit-date-form {
  text-align: center;
}

.edit-date-form .movie-name {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 16px;
  color: var(--dark-text, #1e293b);
}

/* 新增电影对话框 */
.add-movie-form {
  min-height: 300px;
}

.search-section {
  margin-bottom: 16px;
}

.search-results {
  max-height: 250px;
  overflow-y: auto;
  border: 1px solid var(--border-color, #e2e8f0);
  border-radius: 8px;
  margin-bottom: 16px;
}

.search-result-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px;
  cursor: pointer;
  transition: background-color 0.2s ease;
  border-bottom: 1px solid var(--border-color, #e2e8f0);
}

.search-result-item:last-child {
  border-bottom: none;
}

.search-result-item:hover {
  background-color: #f1f5f9;
}

.search-result-item.selected {
  background-color: #e0e7ff;
  border-color: #6366f1;
}

.search-pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-top: 1px solid var(--border-color, #e2e8f0);
  background-color: #f8fafc;
}

.pagination-info {
  font-size: 14px;
  color: #64748b;
}

.result-poster {
  width: 46px;
  height: 69px;
  object-fit: cover;
  border-radius: 4px;
}

.result-poster-placeholder {
  width: 46px;
  height: 69px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  border-radius: 4px;
  color: #a0aec0;
}

.result-info {
  flex: 1;
}

.result-title {
  font-weight: 600;
  color: var(--dark-text, #1e293b);
  margin-bottom: 2px;
}

.result-original {
  font-size: 12px;
  color: #718096;
  margin-bottom: 2px;
}

.result-meta {
  font-size: 12px;
  color: #a0aec0;
}

.selected-movie-section {
  padding: 16px;
  background: #f8fafc;
  border-radius: 8px;
  margin-top: 16px;
}

.selected-movie-section h4 {
  margin: 0 0 12px 0;
  color: var(--dark-text, #1e293b);
}
</style>
