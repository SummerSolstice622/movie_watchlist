"""数据库包"""

import os

from .base import BaseMovieDB, MovieInfo, MovieRecord
from .sqlite_db import SQLiteMovieDB
from .supabase_db import SupabaseMovieDB


def get_movie_db() -> BaseMovieDB:
    """
    获取电影数据库实例
    根据环境变量选择使用 SQLite 或 Supabase
    """
    db_type = os.getenv("DB_TYPE", "sqlite").lower()

    if db_type == "supabase":
        return SupabaseMovieDB()
    else:
        return SQLiteMovieDB()


__all__ = [
    "BaseMovieDB",
    "MovieInfo",
    "MovieRecord",
    "SQLiteMovieDB",
    "SupabaseMovieDB",
    "get_movie_db",
]
