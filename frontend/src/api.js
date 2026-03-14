import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  timeout: 60000
})

export const movieAPI = {
  // 获取观影记录列表
  getRecords(params = {}) {
    return api.get('/movie/records', { params })
  },

  // 获取所有观影年份（支持联动筛选）
  getYears(params = {}) {
    return api.get('/movie/years', { params })
  },

  // 获取所有观影月份（支持联动筛选）
  getMonths(params = {}) {
    return api.get('/movie/months', { params })
  },

  // 获取所有出品年代（支持联动筛选）
  getDecades(params = {}) {
    return api.get('/movie/decades', { params })
  },

  // 获取所有电影主题/类型（支持联动筛选）
  getGenres(params = {}) {
    return api.get('/movie/genres', { params })
  },

  // 获取观影统计
  getStats() {
    return api.get('/movie/stats')
  },

  // 获取电影详情
  getMovieDetail(tmdbId) {
    return api.get(`/movie/records/${tmdbId}`)
  },

  // 更新观影日期
  updateWatchedDate(tmdbId, oldDate, newDate) {
    return api.put(`/movie/records/${tmdbId}/date`, { watched_date: newDate }, {
      params: { old_date: oldDate }
    })
  },

  // 删除观影记录
  deleteRecord(tmdbId, watchedDate) {
    return api.delete(`/movie/records/${tmdbId}`, {
      params: { watched_date: watchedDate }
    })
  },

  // 添加观影记录
  addRecord(tmdbId, watchedDate, rating = null, review = '') {
    return api.post('/movie/records', {
      tmdb_id: tmdbId,
      watched_date: watchedDate,
      rating,
      review
    })
  },

  // 搜索TMDB电影
  searchMovies(query, page = 1) {
    return api.get('/movie/search', { params: { query, page } })
  },

  // 按ID获取电影详情
  getMovieById(tmdbId) {
    return api.get('/movie/movie-detail', { params: { id: tmdbId } })
  },

  // 从TMDB添加电影
  addMovieFromTmdb(tmdbId) {
    return api.post(`/movie/movies/${tmdbId}/add`)
  },

  // 导出观影记录
  exportRecords(params = {}) {
    return api.get('/movie/export', {
      params,
      responseType: 'blob'
    })
  },

  // 获取观影统计数据
  getStatistics(params = {}) {
    return api.get('/movie/statistics', { params })
  },

  // 获取历年观影统计（单独接口）
  getStatisticsYearly() {
    return api.get('/movie/statistics-yearly')
  },

  // 获取那些 watched_date 为 null 的观影记录
  getRecordsWithNullDates() {
    return api.get('/movie/records-with-null-dates')
  },

  // ======== 电影管理 API ========
  // 从TMDB刷新电影信息
  refreshMoviesFromTMDB(data) {
    return api.post('/movie/refresh-from-tmdb', data)
  },

  // 确认并执行电影数据更新
  confirmTMDBUpdate(data) {
    return api.post('/movie/confirm-tmdb-update', data)
  },

  // ======== 影院管理 API ========
  // 获取影院列表
  getCinemas(params = {}) {
    const finalParams = { limit: 10000, ...params }
    return api.get('/movie/cinemas', { params: finalParams })
  },

  // 创建影院
  createCinema(data) {
    return api.post('/movie/cinemas', data)
  },

  // 获取影院详情
  getCinema(cinemaId) {
    return api.get(`/movie/cinemas/${cinemaId}`)
  },

  // 更新影院信息
  updateCinema(cinemaId, data) {
    return api.put(`/movie/cinemas/${cinemaId}`, data)
  },

  // 删除影院
  deleteCinema(cinemaId) {
    return api.delete(`/movie/cinemas/${cinemaId}`)
  },

  // ======== 影院观影记录 API ========
  // 创建影院观影记录
  createCinemaRecord(data) {
    return api.post('/movie/cinema-records', data)
  },

  // 获取影院观影记录
  getCinemaRecords(params = {}) {
    return api.get('/movie/cinema-records', { params })
  },

  // 更新影院观影记录
  updateCinemaRecord(recordId, data) {
    return api.put(`/movie/cinema-records/${recordId}`, data)
  },

  // 删除影院观影记录
  deleteCinemaRecord(recordId) {
    return api.delete(`/movie/cinema-records/${recordId}`)
  }
}

export default api
