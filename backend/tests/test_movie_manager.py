"""
测试电影管理器
"""

import asyncio
import os
import sys

sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)  # noqa: E402

from movie.manager import get_movie_manager  # noqa: E402


async def test_search_movies():
    """测试搜索电影"""
    manager = get_movie_manager()
    print("=" * 50)
    print("测试搜索电影: 肖申克的救赎")
    print("=" * 50)

    movies = await manager.search_movies("肖申克的救赎")
    print(movies)
    for i, movie in enumerate(movies[:5], 1):
        print(f"{i}. {movie.title} ({movie.release_date}) - 评分: {movie.vote_average}")

    return movies


async def test_get_detail():
    """测试获取电影详情"""
    manager = get_movie_manager()
    print("\n" + "=" * 50)
    print("测试获取电影详情: TMDB ID 278 (肖申克的救赎)")
    print("=" * 50)

    movie = await manager.get_movie_detail(278)
    print(f"标题: {movie.title}")
    print(f"原标题: {movie.original_title}")
    print(f"简介: {movie.overview[:100]}..." if movie.overview else "简介: 无")
    print(f"类型: {movie.genres}")
    print(f"时长: {movie.runtime} 分钟" if movie.runtime else "时长: 未知")
    print(f"评分: {movie.vote_average}")

    return movie


async def test_get_popular():
    """测试获取热门电影"""
    manager = get_movie_manager()
    print("\n" + "=" * 50)
    print("测试获取热门电影")
    print("=" * 50)

    movies = await manager.get_popular_movies(page=1)
    for i, movie in enumerate(movies[:5], 1):
        print(f"{i}. {movie.title} ({movie.release_date}) - 评分: {movie.vote_average}")

    return movies


async def test_bawangbieji():
    """测试搜索霸王别姬"""
    manager = get_movie_manager()
    print("\n" + "=" * 50)
    print("测试搜索电影: 霸王别姬")
    print("=" * 50)

    movies = await manager.search_movies("霸王别姬")
    for movie in movies:
        print(f"标题: {movie.title}")
        print(f"原标题: {movie.original_title}")
        print(f"TMDB ID: {movie.tmdb_id}")
        print(f"简介: {movie.overview}")
        print(f"发布日期: {movie.release_date}")
        print(f"评分: {movie.vote_average}")
        print(f"评分人数: {movie.vote_count}")
        print(f"热度: {movie.popularity}")
        print(f"成人: {movie.adult}")
        print(f"类型: {movie.genres}")
        print(f"海报: {movie.poster_path}")
        print(f"背景: {movie.backdrop_path}")
        break  # 只打印第一个

    return movies


async def test_get_recommendations():
    """测试获取电影推荐"""
    manager = get_movie_manager()
    print("\n" + "=" * 50)
    print("测试获取电影推荐: 肖申克的救赎 (ID: 278)")
    print("=" * 50)

    movies = await manager.get_recommendations(278)
    for i, movie in enumerate(movies[:5], 1):
        print(f"{i}. {movie.title} ({movie.release_date}) - 评分: {movie.vote_average}")

    return movies


async def main():
    """主测试函数"""
    manager = get_movie_manager()

    try:
        # 测试搜索
        await test_search_movies()

        # 测试详情
        await test_get_detail()

        # 测试热门
        await test_get_popular()

        # 测试霸王别姬
        await test_bawangbieji()

        # 测试推荐
        await test_get_recommendations()

        print("\n" + "=" * 50)
        print("所有测试完成!")
        print("=" * 50)

    finally:
        await manager.close()


if __name__ == "__main__":
    asyncio.run(test_search_movies())
