"""
TMDB API 客户端
"""

import os
import sys
from typing import Any, Dict, List, Optional

import httpx

# 添加 backend 路径
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

load_dotenv()

# 全局 TMDB 客户端实例（单例模式）
_tmdb_client: Optional[httpx.AsyncClient] = None


class TMDBClient:
    """TMDB API 客户端（单例模式）"""

    BASE_URL = "https://api.tmdb.org/3"

    def __init__(self):
        global _tmdb_client
        self.api_key = os.getenv("TMDB_KEY", "")
        self.read_token = os.getenv("TMDB_READ_TOKEN", "")

        # 使用全局单例客户端，避免频繁创建销毁导致连接泄漏
        if _tmdb_client is None:
            _tmdb_client = httpx.AsyncClient(
                timeout=30.0,
                limits=httpx.Limits(max_connections=5, max_keepalive_connections=5),
            )
        self.client = _tmdb_client

    async def close(self):
        """不关闭全局客户端（由应用程序关闭时统一处理）"""
        pass

    @staticmethod
    async def close_global():
        """关闭全局客户端（应在应用关闭时调用）"""
        global _tmdb_client
        if _tmdb_client is not None:
            await _tmdb_client.aclose()
            _tmdb_client = None

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.read_token}",
            "Content-Type": "application/json",
        }

    async def _get(self, url: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """GET 请求"""
        try:
            response = await self.client.get(
                url, headers=self._get_headers(), params=params, timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            # 添加更详细的错误信息，帮助调试
            error_msg = f"Failed to request {url}: {str(e)}"
            if "nodename nor servname provided" in str(e) or "ConnectError" in str(
                type(e)
            ):
                error_msg += "\n[Network Error] Cannot connect to TMDB API. Please check your internet connection."
            raise Exception(error_msg) from e

    async def get_movie_detail(
        self, movie_id: int, language: str = "zh-CN"
    ) -> Dict[str, Any]:
        """获取电影详情"""
        url = f"{self.BASE_URL}/movie/{movie_id}"
        params = {"language": language}
        return await self._get(url, params)

    async def search_movies(
        self,
        query: str,
        language: str = "zh-CN",
        page: int = 1,
        include_adult: bool = False,
    ) -> List[Dict[str, Any]]:
        """搜索电影"""
        url = f"{self.BASE_URL}/search/movie"
        params = {
            "query": query,
            "language": language,
            "page": page,
            "include_adult": include_adult,
        }
        data = await self._get(url, params)
        return data.get("results", [])

    async def get_popular_movies(
        self, language: str = "zh-CN", page: int = 1, region: str = "US"
    ) -> List[Dict[str, Any]]:
        """获取热门电影"""
        url = f"{self.BASE_URL}/movie/popular"
        params = {"language": language, "page": page, "region": region}
        data = await self._get(url, params)
        return data.get("results", [])

    async def get_top_rated_movies(
        self, language: str = "zh-CN", page: int = 1, region: str = "US"
    ) -> List[Dict[str, Any]]:
        """获取高分电影"""
        url = f"{self.BASE_URL}/movie/top_rated"
        params = {"language": language, "page": page, "region": region}
        data = await self._get(url, params)
        return data.get("results", [])

    async def get_now_playing_movies(
        self, language: str = "zh-CN", page: int = 1, region: str = "US"
    ) -> List[Dict[str, Any]]:
        """获取正在上映的电影"""
        url = f"{self.BASE_URL}/movie/now_playing"
        params = {"language": language, "page": page, "region": region}
        data = await self._get(url, params)
        return data.get("results", [])

    async def get_upcoming_movies(
        self, language: str = "zh-CN", page: int = 1, region: str = "US"
    ) -> List[Dict[str, Any]]:
        """获取即将上映的电影"""
        url = f"{self.BASE_URL}/movie/upcoming"
        params = {"language": language, "page": page, "region": region}
        data = await self._get(url, params)
        return data.get("results", [])

    async def get_movie_credits(
        self, movie_id: int, language: str = "zh-CN"
    ) -> Dict[str, Any]:
        """
        获取电影演职人员信息（导演、主演等）

        Returns:
            {
                "cast": [{"name": "演员名", "character": "角色名", ...}],
                "crew": [{"name": "导演名", "job": "Director", ...}]
            }
        """
        url = f"{self.BASE_URL}/movie/{movie_id}/credits"
        params = {"language": language}
        return await self._get(url, params)

    async def get_movie_directors(
        self, movie_id: int, language: str = "zh-CN"
    ) -> List[Dict[str, Any]]:
        """
        获取电影导演列表

        Returns:
            [{"name": "导演名", "id": xxx, ...}]
        """
        credits = await self.get_movie_credits(movie_id, language)
        directors = [
            person
            for person in credits.get("crew", [])
            if person.get("job") == "Director"
        ]
        return directors

    async def get_movie_cast(
        self, movie_id: int, language: str = "zh-CN", limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        获取电影主演列表

        Args:
            limit: 返回的演员数量，默认前 10 位

        Returns:
            [{"name": "演员名", "character": "角色名", "profile_path": "xxx", ...}]
        """
        credits = await self.get_movie_credits(movie_id, language)
        cast = credits.get("cast", [])[:limit]
        return cast

    async def get_movie_awards(self, movie_id: int) -> Dict[str, Any]:
        """
        获取电影奖项信息

        注意: TMDB 没有直接的奖项 API，但可以通过 external_ids 获取 IMDB ID，
        然后使用第三方服务查询奖项。这里返回基本信息。

        Returns:
            {"imdb_id": "ttxxxxxxx", "note": "TMDB 不直接提供奖项信息"}
        """
        url = f"{self.BASE_URL}/movie/{movie_id}/external_ids"
        data = await self._get(url)
        return {
            "imdb_id": data.get("imdb_id"),
            "note": "TMDB 不直接提供奖项信息，可通过 IMDB ID 在其他服务查询",
        }

    async def get_movie_keywords(self, movie_id: int) -> List[Dict[str, Any]]:
        """
        获取电影关键词标签

        Returns:
            [{"id": xxx, "name": "关键词"}, ...]
        """
        url = f"{self.BASE_URL}/movie/{movie_id}/keywords"
        data = await self._get(url)
        return data.get("keywords", [])

    async def get_movie_videos(
        self, movie_id: int, language: str = "zh-CN"
    ) -> List[Dict[str, Any]]:
        """
        获取电影视频（预告片等）

        Returns:
            [{"key": "youtube_id", "name": "预告片", "type": "Trailer", ...}]
        """
        url = f"{self.BASE_URL}/movie/{movie_id}/videos"
        params = {"language": language}
        data = await self._get(url, params)
        return data.get("results", [])

    async def get_movie_images(self, movie_id: int) -> Dict[str, List]:
        """
        获取电影图片（海报、剧照等）

        Returns:
            {"backdrops": [...], "posters": [...], "logos": [...]}
        """
        url = f"{self.BASE_URL}/movie/{movie_id}/images"
        return await self._get(url)

    async def get_movie_full_info(
        self, movie_id: int, language: str = "zh-CN"
    ) -> Dict[str, Any]:
        """
        获取电影完整信息（包含基本信息、演职人员、关键词等）
        使用 append_to_response 一次请求获取多个信息

        Returns:
            完整的电影信息，包含 credits, keywords, videos 等
        """
        url = f"{self.BASE_URL}/movie/{movie_id}"
        params = {
            "language": language,
            "append_to_response": "credits,keywords,videos,external_ids",
        }
        return await self._get(url, params)

    async def get_movie_recommendations(
        self, movie_id: int, language: str = "zh-CN"
    ) -> List[Dict[str, Any]]:
        """获取电影推荐"""
        url = f"{self.BASE_URL}/movie/{movie_id}/recommendations"
        params = {"language": language}
        data = await self._get(url, params)
        return data.get("results", [])

    async def get_similar_movies(
        self, movie_id: int, language: str = "zh-CN"
    ) -> List[Dict[str, Any]]:
        """获取相似电影"""
        url = f"{self.BASE_URL}/movie/{movie_id}/similar"
        params = {"language": language}
        data = await self._get(url, params)
        return data.get("results", [])

    async def discover_movies(
        self,
        language: str = "zh-CN",
        page: int = 1,
        sort_by: str = "popularity.desc",
        with_genres: str = None,
        primary_release_year: int = None,
        vote_average_gte: float = None,
        vote_count_gte: int = None,
    ) -> List[Dict[str, Any]]:
        """发现电影（高级搜索）"""
        url = f"{self.BASE_URL}/discover/movie"
        params = {
            "language": language,
            "page": page,
            "sort_by": sort_by,
        }
        if with_genres:
            params["with_genres"] = with_genres
        if primary_release_year:
            params["primary_release_year"] = primary_release_year
        if vote_average_gte:
            params["vote_average.gte"] = vote_average_gte
        if vote_count_gte:
            params["vote_count.gte"] = vote_count_gte

        data = await self._get(url, params)
        return data.get("results", [])

    def get_image_url(self, path: str, size: str = "w500") -> str:
        """获取图片 URL"""
        if not path:
            return ""
        return f"https://image.tmdb.org/t/p/{size}{path}"


# 单例实例
_tmdb_client: Optional[TMDBClient] = None


def get_tmdb_client() -> TMDBClient:
    """获取 TMDB 客户端单例"""
    global _tmdb_client
    if _tmdb_client is None:
        _tmdb_client = TMDBClient()
    return _tmdb_client
