"""
电影数据构建器
用于从 API 响应构建 Movie 对象
"""
from typing import Dict, Any, Optional
from .model import Movie


class MovieBuilder:
    """电影构建器"""

    @staticmethod
    def from_tmdb_detail(data: Dict[str, Any]) -> Movie:
        """从 TMDB 详情 API 响应构建 Movie"""
        # 处理类型
        genres = ", ".join([g["name"] for g in data.get("genres", [])])

        # 处理发布日期
        release_date = data.get("release_date", "")

        return Movie(
            tmdb_id=data.get("id", 0),
            title=data.get("title", ""),
            original_title=data.get("original_title", ""),
            overview=data.get("overview", ""),
            release_date=release_date,
            poster_path=data.get("poster_path", ""),
            backdrop_path=data.get("backdrop_path", ""),
            runtime=data.get("runtime"),
            genres=genres,
            vote_average=data.get("vote_average", 0.0),
            vote_count=data.get("vote_count", 0),
            popularity=data.get("popularity", 0.0),
            adult=data.get("adult", False),
            watched=False,
            watched_date=None,
            rating=None,
            review=None,
        )

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> Movie:
        """从字典构建 Movie（用于本地数据）"""
        return Movie(
            tmdb_id=data.get("tmdb_id", data.get("id", 0)),
            title=data.get("title", ""),
            original_title=data.get("original_title", ""),
            overview=data.get("overview", ""),
            release_date=data.get("release_date"),
            poster_path=data.get("poster_path"),
            backdrop_path=data.get("backdrop_path"),
            runtime=data.get("runtime"),
            genres=data.get("genres", ""),
            vote_average=data.get("vote_average", 0.0),
            vote_count=data.get("vote_count", 0),
            popularity=data.get("popularity", 0.0),
            adult=data.get("adult", False),
            watched=data.get("watched", False),
            watched_date=data.get("watched_date"),
            rating=data.get("rating"),
            review=data.get("review"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
        )

    @staticmethod
    def update_watched_info(
        movie: Movie,
        watched: bool = True,
        watched_date: Optional[str] = None,
        rating: Optional[int] = None,
        review: Optional[str] = None,
    ) -> Movie:
        """更新观影信息"""
        movie.watched = watched
        movie.watched_date = watched_date
        movie.rating = rating
        movie.review = review
        return movie
