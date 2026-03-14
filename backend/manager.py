"""
电影管理器
封装电影相关的业务逻辑
"""

import os
import sys
from typing import List, Optional

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # noqa: E402

from .builder import MovieBuilder  # noqa: E402
from .model import Movie  # noqa: E402
from .tmdb_client import TMDBClient, get_tmdb_client  # noqa: E402


class MovieManager:
    """电影管理器"""

    def __init__(self):
        self.client: TMDBClient = get_tmdb_client()

    async def search_movies(
        self, query: str, language: str = "zh-CN", page: int = 1
    ) -> List[Movie]:
        """搜索电影"""
        results = await self.client.search_movies(
            query=query, language=language, page=page
        )
        movies = []
        for item in results:
            movie = MovieBuilder.from_dict(item)
            movies.append(movie)
        return movies

    async def get_movie_detail(self, movie_id: int, language: str = "zh-CN") -> Movie:
        """获取电影详情"""
        data = await self.client.get_movie_detail(movie_id, language)
        return MovieBuilder.from_tmdb_detail(data)

    async def get_popular_movies(
        self, language: str = "zh-CN", page: int = 1
    ) -> List[Movie]:
        """获取热门电影"""
        results = await self.client.get_popular_movies(language=language, page=page)
        movies = [MovieBuilder.from_dict(item) for item in results]
        return movies

    async def get_top_rated_movies(
        self, language: str = "zh-CN", page: int = 1
    ) -> List[Movie]:
        """获取高分电影"""
        results = await self.client.get_top_rated_movies(language=language, page=page)
        movies = [MovieBuilder.from_dict(item) for item in results]
        return movies

    async def get_now_playing_movies(
        self, language: str = "zh-CN", page: int = 1
    ) -> List[Movie]:
        """获取正在上映的电影"""
        results = await self.client.get_now_playing_movies(language=language, page=page)
        movies = [MovieBuilder.from_dict(item) for item in results]
        return movies

    async def get_upcoming_movies(
        self, language: str = "zh-CN", page: int = 1
    ) -> List[Movie]:
        """获取即将上映的电影"""
        results = await self.client.get_upcoming_movies(language=language, page=page)
        movies = [MovieBuilder.from_dict(item) for item in results]
        return movies

    async def get_recommendations(
        self, movie_id: int, language: str = "zh-CN"
    ) -> List[Movie]:
        """获取电影推荐"""
        results = await self.client.get_movie_recommendations(movie_id, language)
        movies = [MovieBuilder.from_dict(item) for item in results]
        return movies

    async def get_similar_movies(
        self, movie_id: int, language: str = "zh-CN"
    ) -> List[Movie]:
        """获取相似电影"""
        results = await self.client.get_similar_movies(movie_id, language)
        movies = [MovieBuilder.from_dict(item) for item in results]
        return movies

    async def discover_movies(
        self,
        language: str = "zh-CN",
        page: int = 1,
        sort_by: str = "popularity.desc",
        with_genres: str = None,
        primary_release_year: int = None,
        vote_average_gte: float = None,
        vote_count_gte: int = None,
    ) -> List[Movie]:
        """发现电影"""
        results = await self.client.discover_movies(
            language=language,
            page=page,
            sort_by=sort_by,
            with_genres=with_genres,
            primary_release_year=primary_release_year,
            vote_average_gte=vote_average_gte,
            vote_count_gte=vote_count_gte,
        )
        movies = [MovieBuilder.from_dict(item) for item in results]
        return movies

    async def close(self):
        """关闭管理器"""
        await self.client.close()


# 单例实例
_movie_manager: Optional[MovieManager] = None


def get_movie_manager() -> MovieManager:
    """获取电影管理器单例"""
    global _movie_manager
    if _movie_manager is None:
        _movie_manager = MovieManager()
    return _movie_manager
