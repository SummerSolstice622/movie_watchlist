<template>
  <div class="movie-manage-page">
    <!-- 顶部导航 -->
    <HeaderCard title="电影数据管理" subtitle="更新电影信息、管理影院数据">
    </HeaderCard>

    <!-- 主要内容 -->
    <main class="page-main">
      <div class="container">
        <el-tabs v-model="activeTab">
          <!-- 标签页1：更新电影信息 -->
          <el-tab-pane label="更新电影信息" name="update-movies">
            <div class="tab-content">
              <div class="section-title">从 TMDB 同步电影数据</div>
              <p class="description">选择要更新的电影，系统将从 TMDB 查询最新数据，对比本地数据后展示变化。</p>

              <div class="action-buttons">
                <el-button type="primary" @click="showSelectMoviesDialog = true">选择电影</el-button>
              </div>

              <!-- 更新预览 -->
              <div v-if="updatePreview.length > 0" class="preview-section">
                <div class="section-title">待更新电影</div>
                <el-table :data="updatePreview" stripe style="width: 100%">
                  <el-table-column prop="title" label="电影标题" min-width="150" />
                  <el-table-column label="变更字段" min-width="200">
                    <template #default="{ row }">
                      <div v-for="(change, field) in row.changes" :key="field" class="change-item">
                        <span class="field-name">{{ field }}:</span>
                        <span class="old-value">{{ change.old }}</span>
                        <span class="arrow"> → </span>
                        <span class="new-value">{{ change.new }}</span>
                      </div>
                    </template>
                  </el-table-column>
                </el-table>
                <div class="action-buttons">
                  <el-button type="success" :loading="isUpdating" @click="confirmUpdate">确认更新</el-button>
                  <el-button @click="cancelUpdate">取消</el-button>
                </div>
              </div>
            </div>
          </el-tab-pane>

          <!-- 标签页2：管理影院 -->
          <el-tab-pane label="影院管理" name="cinema-management">
            <div class="tab-content">
              <div class="section-title">影院信息管理</div>

              <div class="action-buttons">
                <el-button type="primary" @click="addNewCinema">新增影院</el-button>
              </div>

              <!-- 影院列表 -->
              <el-table :data="cinemas" stripe style="width: 100%">
                <el-table-column prop="name" label="影院名称" min-width="150" />
                <el-table-column prop="city" label="城市" min-width="100" />
                <el-table-column label="操作" width="200" fixed="right">
                  <template #default="{ row }">
                    <el-button link type="primary" size="small" @click="editCinema(row)">编辑</el-button>
                    <el-button link type="danger" size="small" @click="deleteCinema(row.id)">删除</el-button>
                  </template>
                </el-table-column>
              </el-table>
            </div>
          </el-tab-pane>
        </el-tabs>
      </div>
    </main>

    <!-- 电影选择对话框 -->
    <el-dialog v-model="showSelectMoviesDialog" title="选择要更新的电影" width="60%">
      <el-tree
        ref="movieTreeRef"
        :data="movieTreeData"
        node-key="tmdb_id"
        show-checkbox
        :props="{ children: 'children', label: 'label' }"
      />
      <template #footer>
        <el-button @click="showSelectMoviesDialog = false">取消</el-button>
        <el-button type="primary" @click="performMovieUpdate">查询并对比</el-button>
      </template>
    </el-dialog>

    <!-- 影院编辑对话框 -->
    <el-dialog v-model="showCinemaDialog" :title="editingCinema ? '编辑影院' : '新增影院'" width="40%">
      <el-form v-model="cinemaForm" label-width="80px">
        <el-form-item label="影院名称">
          <el-input v-model="cinemaForm.name" placeholder="请输入影院名称" />
        </el-form-item>
        <el-form-item label="城市">
          <el-input v-model="cinemaForm.city" placeholder="请输入城市" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCinemaDialog = false">取消</el-button>
        <el-button type="primary" @click="saveCinema">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import HeaderCard from './components/HeaderCard.vue'
import { movieAPI } from './api'

export default {
  name: 'MovieManage',
  components: {
    HeaderCard
  },
  setup() {
    const activeTab = ref('update-movies')

    // 电影更新相关
    const showSelectMoviesDialog = ref(false)
    const showConfirmDialog = ref(false)
    const movieTreeRef = ref(null)
    const movieTreeData = ref([])
    const updatePreview = ref([])
    const isUpdating = ref(false)

    // 影院管理相关
    const showAddCinemaDialog = ref(false)
    const showCinemaDialog = ref(false)
    const cinemas = ref([])
    const cinemaForm = ref({ name: '', city: '' })
    const editingCinema = ref(null)

    // 加载电影列表用于选择
    const loadMovieList = async () => {
      try {
        let allMovies = []
        let page = 1
        const pageSize = 100

        // 分页循环加载所有电影
        while (true) {
          const res = await movieAPI.getRecords({ page, limit: pageSize })
          if (res.data.success && res.data.data.length > 0) {
            allMovies = allMovies.concat(res.data.data)
            // 如果返回条数小于分页大小，说明已经到最后
            if (res.data.data.length < pageSize) {
              break
            }
            page++
          } else {
            break
          }
        }

        // 转换为树形数据格式
        movieTreeData.value = allMovies.map(record => ({
          tmdb_id: record.tmdb_id,
          label: `${record.title}`,
        }))
      } catch (error) {
        console.error('加载电影列表失败:', error)
        ElMessage.error('加载电影列表失败')
      }
    }

    // 查询并对比电影信息 - 更新所有电影
    const performMovieUpdate = async () => {
      try {
        isUpdating.value = true
        ElMessage.loading('正在多线程查询所有电影数据，请稍候...')

        // 不需要选择，直接查询所有电影
        const res = await movieAPI.refreshMoviesFromTMDB({ tmdb_ids: 'all' })
        if (res.data.success) {
          updatePreview.value = res.data.data.changes
          showSelectMoviesDialog.value = false
          if (updatePreview.value.length === 0) {
            ElMessage.info('所有电影信息都是最新的，无需更新')
          } else {
            ElMessage.success(`发现 ${updatePreview.value.length} 部电影需要更新`)
            // 显示确认对话框
            showConfirmDialog.value = true
          }
        }
      } catch (error) {
        console.error('查询电影信息失败:', error)
        ElMessage.error(error.response?.data?.detail || '查询失败')
      } finally {
        isUpdating.value = false
      }
    }

    // 确认更新
    const confirmUpdate = async () => {
      try {
        isUpdating.value = true
        const updates = updatePreview.value.map(item => ({
          tmdb_id: item.tmdb_id,
          fields: Object.fromEntries(
            Object.entries(item.changes).map(([key, change]) => [key, change.new])
          )
        }))

        const res = await movieAPI.confirmTMDBUpdate({ updates })
        if (res.data.success) {
          ElMessage.success(res.data.message)
          updatePreview.value = []
        }
      } catch (error) {
        console.error('确认更新失败:', error)
        ElMessage.error('更新失败')
      } finally {
        isUpdating.value = false
      }
    }

    const cancelUpdate = () => {
      updatePreview.value = []
    }

    // 影院管理
    const loadCinemas = async () => {
      try {
        const res = await movieAPI.getCinemas({ limit: 1000 })
        if (res.data.success) {
          cinemas.value = res.data.data
        }
      } catch (error) {
        console.error('加载影院列表失败:', error)
      }
    }

    const editCinema = (cinema) => {
      editingCinema.value = cinema
      cinemaForm.value = { ...cinema }
      showCinemaDialog.value = true
    }

    const addNewCinema = () => {
      editingCinema.value = null
      cinemaForm.value = { name: '', city: '' }
      showCinemaDialog.value = true
    }

    const saveCinema = async () => {
      if (!cinemaForm.value.name || !cinemaForm.value.city) {
        ElMessage.warning('请填写影院名称和城市')
        return
      }

      try {
        if (editingCinema.value) {
          await movieAPI.updateCinema(editingCinema.value.id, cinemaForm.value)
          ElMessage.success('影院更新成功')
        } else {
          await movieAPI.createCinema(cinemaForm.value)
          ElMessage.success('影院创建成功')
        }
        showCinemaDialog.value = false
        loadCinemas()
      } catch (error) {
        console.error('保存影院失败:', error)
        ElMessage.error(error.response?.data?.detail || '保存失败')
      }
    }

    const deleteCinema = async (cinemaId) => {
      try {
        await ElMessageBox.confirm('确认删除该影院吗？', '提示', {
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'warning',
        })

        await movieAPI.deleteCinema(cinemaId)
        ElMessage.success('影院删除成功')
        loadCinemas()
      } catch (error) {
        console.error('删除影院失败:', error)
      }
    }

    onMounted(() => {
      loadMovieList()
      loadCinemas()
    })

    return {
      activeTab,
      showSelectMoviesDialog,
      movieTreeRef,
      movieTreeData,
      updatePreview,
      isUpdating,
      showSelectMoviesDialog,
      showConfirmDialog,
      performMovieUpdate,
      confirmUpdate,
      cancelUpdate,
      showAddCinemaDialog,
      showCinemaDialog,
      cinemas,
      cinemaForm,
      editingCinema,
      editCinema,
      addNewCinema,
      saveCinema,
      deleteCinema,
    }
  }
}
</script>

<style scoped>
.movie-manage-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.page-main {
  padding: 40px 20px;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  background: white;
  border-radius: 8px;
  padding: 30px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.tab-content {
  padding: 20px 0;
}

.section-title {
  font-size: 16px;
  font-weight: bold;
  margin-bottom: 12px;
  color: #333;
}

.description {
  color: #666;
  font-size: 14px;
  margin-bottom: 20px;
}

.action-buttons {
  margin-bottom: 30px;
  display: flex;
  gap: 10px;
}

.preview-section {
  margin-top: 30px;
}

.change-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 0;
  font-size: 12px;
}

.field-name {
  font-weight: bold;
  color: #333;
  min-width: 80px;
}

.old-value {
  color: #f56c6c;
}

.arrow {
  color: #999;
}

.new-value {
  color: #67c23a;
}

:deep(.el-table) {
  margin: 20px 0;
}
</style>
