<template>
  <div class="movie-card-wrapper" :class="{ expanded: isExpanded }">
    <div class="movie-card card">
      <!-- 电影海报 -->
      <div class="poster-wrapper" v-if="record.poster_path">
        <img
          :src="`https://image.tmdb.org/t/p/w500${record.poster_path}`"
          :alt="record.title"
          class="poster"
          @error="handleImageError"
        />
        <!-- 删除按钮 -->
        <button class="delete-btn" @click.stop="handleDelete" title="删除观影记录">
          <el-icon><Delete /></el-icon>
        </button>
      </div>
      <div class="poster-placeholder" v-else>
        <el-icon size="48"><VideoCamera /></el-icon>
        <!-- 删除按钮 -->
        <button class="delete-btn" @click.stop="handleDelete" title="删除观影记录">
          <el-icon><Delete /></el-icon>
        </button>
      </div>

      <!-- 电影信息 -->
      <div class="movie-info">
        <div class="movie-header">
          <h3 class="movie-title">{{ record.title }}</h3>
          <button
            class="toggle-expand-btn"
            v-if="shouldShowExpandBtn"
            @click="toggleExpand"
          >
            {{ isExpanded ? '收起' : '展开' }}
          </button>
        </div>
        <p class="movie-original-title" v-if="record.original_title && record.original_title !== record.title">
          {{ record.original_title }}
        </p>

        <!-- 元信息标签 -->
        <div class="movie-meta">
          <span class="badge badge-primary" v-if="record.release_date">{{ record.release_date.substring(0, 4) }}</span>
          <span class="badge badge-info" v-if="record.genres">{{ record.genres }}</span>
          <span class="badge badge-rating" v-if="record.vote_count > 0">
            <el-icon><Star /></el-icon> {{ record.vote_average.toFixed(1) }} ({{ record.vote_count }})
          </span>
          <span class="badge badge-watch-count" v-if="record.watch_sequence && record.watch_sequence > 1">
            <el-icon><VideoCamera /></el-icon> 第 {{ record.watch_sequence }} 次观看
          </span>
        </div>

        <!-- 简介 -->
        <p class="movie-overview" v-if="record.overview" :class="{ expanded: isExpanded }">
          {{ isExpanded ? record.overview : displayOverview }}
        </p>
        <p class="movie-overview no-overview" v-else>
          暂无简介
        </p>

        <!-- 底部信息 -->
        <div class="movie-footer">
          <div class="watch-info">
            <span class="watch-date clickable" @click="handleEditDate" title="点击修改日期">
              <el-icon><Clock /></el-icon> {{ formatDate(record.watched_date) }}
              <el-icon class="edit-icon"><Edit /></el-icon>
            </span>
            <span class="personal-rating" v-if="record.rating">
              <el-icon><Star /></el-icon> 我的评分: {{ record.rating }}分
            </span>
          </div>
          <div class="action-buttons">
            <el-button type="primary" size="small" @click="openCinemaDialog">影院观看</el-button>
          </div>
        </div>
      </div>
    </div>
  </div>

    <!-- 影院选择对话框 -->
    <el-dialog v-model="showCinemaDialog" title="选择影院" width="40%" @close="closeCinemaDialog">
      <div class="cinema-selector">
        <div class="selector-group">
          <label>城市：</label>
          <el-select v-model="selectedCity" placeholder="选择城市" filterable>
            <el-option
              v-for="city in availableCities"
              :key="city"
              :label="city"
              :value="city"
            />
          </el-select>
        </div>
        <div class="selector-group" v-if="selectedCity">
          <label>影院：</label>
          <el-select v-model="selectedCinema" placeholder="选择影院" filterable>
            <el-option
              v-for="cinema in filteredCinemas"
              :key="cinema.id"
              :label="cinema.name"
              :value="cinema"
            />
          </el-select>
        </div>
      </div>
      <template #footer>
        <el-button @click="closeCinemaDialog">取消</el-button>
        <el-button type="primary" @click="saveCinemaRecord" :disabled="!selectedCinema">保存</el-button>
      </template>
    </el-dialog>
</template>

<script>
import { computed, ref } from 'vue'
import { VideoCamera, Clock, Star, Edit, Delete } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { movieAPI } from '../api.js'

export default {
  name: 'MovieCard',
  components: { VideoCamera, Clock, Star, Edit, Delete },
  props: {
    record: {
      type: Object,
      required: true
    },
    overviewMaxLength: {
      type: Number,
      default: 100
    },
    cinemas: {
      type: Array,
      default: () => []
    }
  },
  emits: ['edit-date', 'delete'],
  setup(props, { emit }) {
    const imageError = ref(false)
    const isExpanded = ref(false)
    const showCinemaDialog = ref(false)
    const selectedCity = ref('')
    const selectedCinema = ref(null)

    // 中文字符按 2 个计算长度
    const getTextLength = (text) => {
      let length = 0
      for (const char of text) {
        if (char.charCodeAt(0) > 127) {
          length += 2
        } else {
          length += 1
        }
      }
      return length
    }

    const displayOverview = computed(() => {
      const overview = props.record.overview || ''
      const maxLength = props.overviewMaxLength

      // 按实际显示长度截取
      let length = 0
      let endIndex = 0
      for (let i = 0; i < overview.length; i++) {
        const charLen = overview.charCodeAt(i) > 127 ? 2 : 1
        if (length + charLen > maxLength) {
          break
        }
        length += charLen
        endIndex = i + 1
      }

      if (endIndex < overview.length) {
        return overview.substring(0, endIndex) + '...'
      }
      return overview
    })

    const shouldShowExpandBtn = computed(() => {
      const overview = props.record.overview || ''
      return getTextLength(overview) > props.overviewMaxLength
    })

    const toggleExpand = () => {
      isExpanded.value = !isExpanded.value
    }

    const formatDate = (dateStr) => {
      if (!dateStr) return ''
      return dateStr.replace(/\//g, '-')
    }

    const handleImageError = (e) => {
      e.target.style.display = 'none'
      imageError.value = true
    }

    const handleEditDate = () => {
      emit('edit-date', props.record)
    }

    const handleDelete = () => {
      emit('delete', props.record)
    }

    const openCinemaDialog = () => {
      selectedCity.value = '上海'  // 默认选择上海
      selectedCinema.value = null   // 清空之前的选择
      showCinemaDialog.value = true
    }

    const closeCinemaDialog = () => {
      showCinemaDialog.value = false
      selectedCity.value = ''
      selectedCinema.value = null
    }

    const availableCities = computed(() => {
      const cities = new Set(props.cinemas.map(c => c.city))
      return Array.from(cities).sort()
    })

    const filteredCinemas = computed(() => {
      return props.cinemas.filter(c => c.city === selectedCity.value)
    })

    const saveCinemaRecord = async () => {
      if (!selectedCinema.value) {
        ElMessage.warning('请选择影院')
        return
      }
      try {
        // 这里应该调用API保存影院观影记录
        // 暂时先关闭对话框，显示成功消息
        ElMessage.success(`已记录在 ${selectedCinema.value.name} 观看`)
        closeCinemaDialog()
      } catch (error) {
        ElMessage.error('保存失败')
      }
    }

    return {
      displayOverview,
      shouldShowExpandBtn,
      isExpanded,
      toggleExpand,
      formatDate,
      handleImageError,
      handleEditDate,
      handleDelete,
      openCinemaDialog,
      closeCinemaDialog,
      showCinemaDialog,
      selectedCity,
      selectedCinema,
      availableCities,
      filteredCinemas,
      saveCinemaRecord
    }
  }
}
</script>

<style scoped>
.movie-card-wrapper {
  display: flex;
  flex-direction: column;
}

.movie-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  box-sizing: border-box;
}

.poster-wrapper {
  width: 100%;
  height: 200px;
  overflow: hidden;
  background: #f0f0f0;
  position: relative;
}

.poster {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.poster-placeholder {
  width: 100%;
  height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f0f0f0;
  color: #a0aec0;
  position: relative;
}

.delete-btn {
  position: absolute;
  top: 8px;
  right: 8px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: rgba(239, 68, 68, 0.9);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s ease, transform 0.2s ease;
  z-index: 10;
}

.poster-wrapper:hover .delete-btn,
.poster-placeholder:hover .delete-btn {
  opacity: 1;
}

.delete-btn:hover {
  background: rgba(220, 38, 38, 1);
  transform: scale(1.1);
}

.movie-info {
  padding: 16px;
  display: flex;
  flex-direction: column;
  flex: 1;
}

.movie-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 6px;
}

.movie-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--dark-text, #1e293b);
  margin: 0;
  line-height: 1.3;
  flex: 1;
}

.toggle-expand-btn {
  padding: 2px 8px;
  font-size: 12px;
  color: var(--primary-color, #6366f1);
  background: transparent;
  border: 1px solid var(--primary-color, #6366f1);
  border-radius: 4px;
  cursor: pointer;
  white-space: nowrap;
  transition: all 0.2s ease;
}

.toggle-expand-btn:hover {
  background: var(--primary-color, #6366f1);
  color: white;
}

.movie-original-title {
  font-size: 13px;
  color: #718096;
  margin: 0 0 12px 0;
  font-style: italic;
}

.movie-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 12px;
}

.badge {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 10px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
}

.badge-primary {
  background: #e0e7ff;
  color: #4338ca;
}

.badge-info {
  background: #dbeafe;
  color: #1d4ed8;
}

.badge-rating {
  background: #fef3c7;
  color: #d97706;
}

.badge-watch-count {
  background: #ddd6fe;
  color: #7c3aed;
}

.movie-overview {
  font-size: 13px;
  color: #4a5568;
  line-height: 1.6;
  margin: 0 0 12px 0;
  flex: 1;
}

.movie-overview.no-overview {
  color: #a0aec0;
  font-style: italic;
}

.movie-footer {
  padding-top: 12px;
  border-top: 1px solid var(--border-color, #e2e8f0);
}

.watch-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  font-size: 12px;
  color: #718096;
}

.watch-date {
  display: flex;
  align-items: center;
  gap: 4px;
  color: var(--success-color, #10b981);
  font-weight: 500;
}

.watch-date.clickable {
  cursor: pointer;
  transition: color 0.2s ease;
}

.watch-date.clickable:hover {
  color: #059669;
}

.watch-date .edit-icon {
  opacity: 0;
  transition: opacity 0.2s ease;
  font-size: 12px;
  margin-left: 2px;
}

.watch-date.clickable:hover .edit-icon {
  opacity: 1;
}

.personal-rating {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #f59e0b;
}

.action-buttons {
  margin-top: 12px;
  display: flex;
  gap: 8px;
}

.cinema-selector {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.selector-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.selector-group label {
  font-weight: 500;
  color: #333;
}

.selector-group .el-select {
  width: 100%;
}

</style>
