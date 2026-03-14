"""
数据访问层抽象基类
定义统一接口，所有数据库实现类需继承
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class MovieInfo:
    """电影信息"""

    tmdb_id: int
    title: str
    original_title: str = ""
    overview: str = ""
    release_date: str = ""
    poster_path: str = ""
    backdrop_path: str = ""
    genres: str = ""
    vote_average: float = 0.0
    vote_count: int = 0
    runtime: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tmdb_id": self.tmdb_id,
            "title": self.title,
            "original_title": self.original_title,
            "overview": self.overview,
            "release_date": self.release_date,
            "poster_path": self.poster_path,
            "backdrop_path": self.backdrop_path,
            "genres": self.genres,
            "vote_average": self.vote_average,
            "vote_count": self.vote_count,
            "runtime": self.runtime,
        }


@dataclass
class MovieRecord:
    """观影记录"""

    id: int
    tmdb_id: int
    watched_date: str
    rating: Optional[float] = None
    review: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "tmdb_id": self.tmdb_id,
            "watched_date": self.watched_date,
            "rating": self.rating,
            "review": self.review,
        }


class BaseMovieDB(ABC):
    """电影数据库操作基类"""

    @abstractmethod
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
        """
        获取观影记录列表

        Returns:
            (records, total) - 记录列表和总数
        """
        pass

    @abstractmethod
    def get_years(
        self,
        month: str = "",
        decade: str = "",
        rating_min: Optional[float] = None,
        rating_max: Optional[float] = None,
        vote_count_min: Optional[int] = None,
        search: str = "",
    ) -> List[str]:
        """获取观影年份列表（联动筛选）"""
        pass

    @abstractmethod
    def get_months(
        self,
        year: str = "",
        decade: str = "",
        rating_min: Optional[float] = None,
        rating_max: Optional[float] = None,
        vote_count_min: Optional[int] = None,
        search: str = "",
    ) -> List[str]:
        """获取观影月份列表（联动筛选）"""
        pass

    @abstractmethod
    def get_decades(
        self,
        year: str = "",
        month: str = "",
        rating_min: Optional[float] = None,
        rating_max: Optional[float] = None,
        vote_count_min: Optional[int] = None,
        search: str = "",
    ) -> List[str]:
        """获取出品年代列表（联动筛选）"""
        pass

    @abstractmethod
    def get_stats(self) -> Dict[str, Any]:
        """获取观影统计"""
        pass

    @abstractmethod
    def get_movie_detail(self, tmdb_id: int) -> Optional[Dict[str, Any]]:
        """获取电影详情"""
        pass

    @abstractmethod
    def add_movie_info(self, movie: MovieInfo) -> bool:
        """添加电影信息"""
        pass

    @abstractmethod
    def add_record(
        self,
        tmdb_id: int,
        watched_date: str,
        rating: Optional[float] = None,
        review: str = "",
    ) -> bool:
        """添加观影记录"""
        pass

    @abstractmethod
    def movie_exists(self, tmdb_id: int) -> bool:
        """检查电影是否存在"""
        pass

    @abstractmethod
    def update_watched_date(self, tmdb_id: int, old_date: str, new_date: str) -> bool:
        """更新观影日期"""
        pass

    @abstractmethod
    def delete_record(self, tmdb_id: int, watched_date: str) -> bool:
        """删除观影记录（不删除电影信息）"""
        pass
