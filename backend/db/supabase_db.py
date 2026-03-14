"""
Supabase数据库实现 (占位，后续实现)
"""

import os
from typing import Any, Dict, List, Optional, Tuple

from .base import BaseMovieDB, MovieInfo

# Supabase 配置
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "")


class SupabaseMovieDB(BaseMovieDB):
    """电影Supabase数据库实现"""

    def __init__(self):
        # TODO: 初始化 Supabase 客户端
        pass

    def get_records(
        self,
        year: str = "",
        month: str = "",
        rating_min: Optional[float] = None,
        rating_max: Optional[float] = None,
        decade: str = "",
        vote_count_min: Optional[int] = None,
        search: str = "",
        sort_by: str = "watched_date",
        sort_order: str = "desc",
        page: int = 1,
        limit: int = 20,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """获取观影记录列表"""
        # TODO: 实现 Supabase 查询
        raise NotImplementedError("Supabase implementation not yet available")

    def get_years(
        self,
        month: str = "",
        decade: str = "",
        rating_min: Optional[float] = None,
        rating_max: Optional[float] = None,
        vote_count_min: Optional[int] = None,
        search: str = "",
    ) -> List[str]:
        """获取观影年份列表"""
        raise NotImplementedError("Supabase implementation not yet available")

    def get_months(
        self,
        year: str = "",
        decade: str = "",
        rating_min: Optional[float] = None,
        rating_max: Optional[float] = None,
        vote_count_min: Optional[int] = None,
        search: str = "",
    ) -> List[str]:
        """获取观影月份列表"""
        raise NotImplementedError("Supabase implementation not yet available")

    def get_decades(
        self,
        year: str = "",
        month: str = "",
        rating_min: Optional[float] = None,
        rating_max: Optional[float] = None,
        vote_count_min: Optional[int] = None,
        search: str = "",
    ) -> List[str]:
        """获取出品年代列表"""
        raise NotImplementedError("Supabase implementation not yet available")

    def get_stats(self) -> Dict[str, Any]:
        """获取观影统计"""
        raise NotImplementedError("Supabase implementation not yet available")

    def get_movie_detail(self, tmdb_id: int) -> Optional[Dict[str, Any]]:
        """获取电影详情"""
        raise NotImplementedError("Supabase implementation not yet available")

    def add_movie_info(self, movie: MovieInfo) -> bool:
        """添加电影信息"""
        raise NotImplementedError("Supabase implementation not yet available")

    def add_record(
        self,
        tmdb_id: int,
        watched_date: str,
        rating: Optional[float] = None,
        review: str = "",
    ) -> bool:
        """添加观影记录"""
        raise NotImplementedError("Supabase implementation not yet available")

    def movie_exists(self, tmdb_id: int) -> bool:
        """检查电影是否存在"""
        raise NotImplementedError("Supabase implementation not yet available")

    def update_watched_date(self, tmdb_id: int, old_date: str, new_date: str) -> bool:
        """更新观影日期"""
        raise NotImplementedError("Supabase implementation not yet available")

    def delete_record(self, tmdb_id: int, watched_date: str) -> bool:
        """删除观影记录"""
        raise NotImplementedError("Supabase implementation not yet available")
