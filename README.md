# Movie Tracker

电影观看记录追踪。

## 目录结构

```
movie/
├── backend/           # FastAPI 后端
│   ├── main.py        # 应用入口
│   ├── movie/         # 电影核心模块（DB、Manager、TMDB客户端）
│   ├── router/        # API 路由
│   │   ├── movie_router.py       # 观影记录 API
│   │   ├── cinema_router.py      # 影院管理 API
│   │   └── movie_admin_router.py # 电影数据管理 API
│   ├── llm/           # LLM 集成（可选）
│   ├── tests/         # 测试
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── movie/     # Vue 组件
│       └── api.js     # Movie API 客户端
└── docs/              # 相关文档
```

## 快速启动

### 后端

```bash
cd movie
pip install -r backend/requirements.txt
uvicorn backend.main:app --reload --port 5002
```

### 环境变量

| 变量 | 说明 |
|------|------|
| `TMDB_API_KEY` | TMDB API 密钥 |
| `DB_TYPE` | 数据库类型（`sqlite` 或 `supabase`） |
| `SUPABASE_URL` | Supabase URL（DB_TYPE=supabase 时） |
| `SUPABASE_KEY` | Supabase Key（DB_TYPE=supabase 时） |

## API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/movie/records` | GET | 获取观影记录列表 |
| `/movie/records` | POST | 添加观影记录 |
| `/movie/statistics` | GET | 获取观影统计 |
| `/movie/cinemas` | GET/POST | 影院管理 |
| `/api/movie/refresh-from-tmdb` | POST | 从TMDB刷新电影信息 |
