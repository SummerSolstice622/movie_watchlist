"""
电影管理 API - 更新电影信息
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any, Dict, List, Tuple

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/movie", tags=["movie-admin"])


def get_db():
    """获取数据库实例"""
    from .db.sqlite_db import SQLiteMovieDB

    return SQLiteMovieDB()


class MovieUpdateRequest(BaseModel):
    """电影更新请求"""

    tmdb_ids: List[int]


class MovieUpdateResponse(BaseModel):
    """电影更新响应"""

    total: int
    success: int
    failed: int
    changes: List[Dict[str, Any]]


def fetch_movie_info_from_tmdb(tmdb_client, tmdb_id: int) -> Tuple[int, Dict[str, Any]]:
    """从TMDB获取电影信息"""
    try:
        movie_data = tmdb_client.get_movie(tmdb_id)
        return tmdb_id, {
            "title": movie_data.get("title"),
            "original_title": movie_data.get("original_title"),
            "overview": movie_data.get("overview"),
            "release_date": movie_data.get("release_date"),
            "poster_path": movie_data.get("poster_path"),
            "backdrop_path": movie_data.get("backdrop_path"),
            "runtime": movie_data.get("runtime"),
            "genres": ", ".join([g["name"] for g in movie_data.get("genres", [])]),
            "vote_average": movie_data.get("vote_average"),
            "vote_count": movie_data.get("vote_count"),
            "popularity": movie_data.get("popularity"),
            "adult": movie_data.get("adult"),
        }
    except Exception as e:
        return tmdb_id, {"error": str(e)}


@router.post("/refresh-from-tmdb")
def refresh_movies_from_tmdb(request: MovieUpdateRequest):
    """
    从 TMDB 刷新电影信息
    1. 多线程查询 TMDB API
    2. 返回要修改的字段清单
    3. 用户确认后更新数据库
    """
    from .tmdb_client import TMDBClient

    db = get_db()
    if not request.tmdb_ids:
        raise HTTPException(status_code=400, detail="未提供 TMDB IDs")

    tmdb_client = TMDBClient()
    changes = []
    failed_count = 0

    # 使用线程池并行查询 TMDB API
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {
            executor.submit(fetch_movie_info_from_tmdb, tmdb_client, tmdb_id): tmdb_id
            for tmdb_id in request.tmdb_ids
        }

        for future in as_completed(futures):
            tmdb_id, movie_data = future.result()

            if "error" in movie_data:
                failed_count += 1
                continue

            # 获取当前数据库中的电影信息
            current = db.get_movie_info(tmdb_id)
            if not current:
                failed_count += 1
                continue

            # 比较字段，只记录有变化的字段
            changed_fields = {}
            for key, new_value in movie_data.items():
                old_value = current.get(key)
                if old_value != new_value:
                    changed_fields[key] = {"old": old_value, "new": new_value}

            if changed_fields:
                changes.append(
                    {
                        "tmdb_id": tmdb_id,
                        "title": current.get("title"),
                        "changes": changed_fields,
                    }
                )

    return {
        "success": True,
        "data": {
            "total": len(request.tmdb_ids),
            "success": len(request.tmdb_ids) - failed_count,
            "failed": failed_count,
            "changes": changes,
        },
    }


class ConfirmUpdateRequest(BaseModel):
    """确认更新请求"""

    updates: List[Dict[str, Any]]  # [{'tmdb_id': int, 'fields': {...}}]


@router.post("/confirm-tmdb-update")
def confirm_update_from_tmdb(request: ConfirmUpdateRequest):
    """
    确认并执行电影信息更新
    """
    db = get_db()

    if not request.updates:
        raise HTTPException(status_code=400, detail="未提供更新数据")

    success_count = 0
    failed_count = 0

    for update in request.updates:
        tmdb_id = update.get("tmdb_id")
        fields = update.get("fields", {})

        if not tmdb_id or not fields:
            failed_count += 1
            continue

        try:
            success = db.update_movie_info(tmdb_id, fields)
            if success:
                success_count += 1
            else:
                failed_count += 1
        except Exception as e:
            print(f"更新电影 {tmdb_id} 失败: {e}")
            failed_count += 1

    return {
        "success": True,
        "message": f"更新完成：成功 {success_count}，失败 {failed_count}",
        "data": {"success": success_count, "failed": failed_count},
    }
