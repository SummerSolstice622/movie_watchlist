"""
SQLite数据库实现
"""

import os
import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .base import BaseMovieDB, MovieInfo

# 获取项目根目录（backend的父目录）
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent

# 从环境变量获取数据库路径
# 优先级：环境变量 > 绝对路径 > 相对于项目根目录
db_path_env = os.getenv("DB_PATH")
if db_path_env:
    DB_PATH = db_path_env
else:
    # 使用绝对路径以确保无论从何处运行都能找到数据库
    default_db = PROJECT_ROOT / "life_track.db"
    DB_PATH = str(default_db.resolve())  # resolve() 确保是绝对路径


class _ConnectionWrapper:
    """数据库连接包装类，确保连接被正确关闭"""

    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = None

    def __enter__(self):
        try:
            self.conn = sqlite3.connect(
                self.db_path, timeout=30.0, check_same_thread=False
            )
            self.conn.row_factory = sqlite3.Row
            return self.conn
        except sqlite3.OperationalError as e:
            raise sqlite3.OperationalError(
                f"Failed to open database at {self.db_path}: {e}"
            ) from e

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.conn:
            try:
                if exc_type is None:
                    self.conn.commit()
                else:
                    self.conn.rollback()
            finally:
                self.conn.close()
        return False


class SQLiteMovieDB(BaseMovieDB):
    """电影SQLite数据库实现"""

    def __init__(self, db_path: str = ""):
        self.db_path = db_path or DB_PATH
        # 确保使用绝对路径
        if not os.path.isabs(self.db_path):
            self.db_path = str(PROJECT_ROOT / self.db_path)

    def _get_connection(self):
        """获取数据库连接（返回上下文管理器）"""
        # 确保使用绝对路径
        db_path_to_use = self.db_path
        if not os.path.isabs(db_path_to_use):
            db_path_to_use = str(Path(PROJECT_ROOT) / self.db_path)

        # 确保目录存在
        db_dir = os.path.dirname(db_path_to_use)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)

        # 检查数据库文件是否存在和可访问
        if not os.path.exists(db_path_to_use):
            raise FileNotFoundError(
                f"Database file not found: {db_path_to_use}\n"
                f"Please ensure life_track.db exists in the project root directory."
            )

        if not os.access(db_path_to_use, os.R_OK):
            raise PermissionError(
                f"No read permission for database file: {db_path_to_use}"
            )

        return _ConnectionWrapper(db_path_to_use)

    def _dict_from_row(self, row: sqlite3.Row) -> Dict[str, Any]:
        """将 sqlite Row 转换为字典"""
        return dict(row) if row else None

    def _build_filter_conditions(
        self,
        year: str = "",
        month: str = "",
        rating_min: Optional[float] = None,
        rating_max: Optional[float] = None,
        decade: str = "",
        vote_count_min: Optional[int] = None,
        search: str = "",
        genres: str = "",
    ) -> Tuple[List[str], List[Any], bool]:
        """构建过滤条件"""
        where_clauses = []
        params = []
        need_join = False

        if search:
            where_clauses.append("(m.title LIKE ? OR m.original_title LIKE ?)")
            params.extend([f"%{search}%", f"%{search}%"])
            need_join = True

        if year:
            where_clauses.append(
                "strftime('%Y', replace(r.watched_date, '/', '-')) = ?"
            )
            params.append(year)

        if month:
            where_clauses.append(
                "strftime('%m', replace(r.watched_date, '/', '-')) = ?"
            )
            params.append(month)

        if rating_min is not None:
            where_clauses.append("(m.vote_average IS NULL OR m.vote_average >= ?)")
            params.append(rating_min)
            need_join = True

        if rating_max is not None:
            where_clauses.append("(m.vote_average IS NULL OR m.vote_average <= ?)")
            params.append(rating_max)
            need_join = True

        if decade:
            decade_start = decade.replace("s", "")
            if decade_start.isdigit():
                year_start = int(decade_start)
                year_end = year_start + 9
                where_clauses.append(
                    "CAST(strftime('%Y', m.release_date) AS INTEGER) BETWEEN ? AND ?"
                )
                params.extend([year_start, year_end])
                need_join = True

        if vote_count_min is not None:
            where_clauses.append("(m.vote_count IS NULL OR m.vote_count >= ?)")
            params.append(vote_count_min)
            need_join = True

        if genres:
            # 按逗号分隔的genres过滤（genres字段存储为"类型1, 类型2"的格式）
            where_clauses.append("m.genres LIKE ?")
            params.append(f"%{genres}%")
            need_join = True

        return where_clauses, params, need_join

    def get_records(
        self,
        year: str = "",
        month: str = "",
        rating_min: Optional[float] = None,
        rating_max: Optional[float] = None,
        decade: str = "",
        vote_count_min: Optional[int] = None,
        search: str = "",
        genres: str = "",
        sort_by: str = "watched_date",
        sort_order: str = "desc",
        page: int = 1,
        limit: int = 20,
        multiple_watch: bool = False,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """获取观影记录列表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            where_clauses, params, need_join = self._build_filter_conditions(
                year,
                month,
                rating_min,
                rating_max,
                decade,
                vote_count_min,
                search,
                genres,
            )

            # 添加多次观看过滤
            if multiple_watch:
                where_clauses.append(
                    "(SELECT COUNT(*) FROM movie_records WHERE tmdb_id = m.tmdb_id) > 1"
                )

            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

            # 计数查询
            count_sql = f"""
                SELECT COUNT(*) as total
                FROM movie_records r
                {"INNER JOIN movie_info m ON m.tmdb_id = r.tmdb_id" if need_join or decade or search or multiple_watch else ""}
                WHERE {where_sql}
            """
            cursor.execute(count_sql, params)
            total = cursor.fetchone()["total"]

            # 数据查询
            offset = (page - 1) * limit
            order_dir = "DESC" if sort_order == "desc" else "ASC"

            sql = f"""
                SELECT
                    m.tmdb_id,
                    m.title,
                    m.original_title,
                    m.overview,
                    m.release_date,
                    m.poster_path,
                    m.backdrop_path,
                    m.genres,
                    m.vote_average,
                    m.vote_count,
                    r.watched_date,
                    r.rating,
                    (SELECT COUNT(*) FROM movie_records WHERE tmdb_id = m.tmdb_id AND watched_date <= r.watched_date) as watch_sequence,
                    (SELECT COUNT(*) FROM movie_records WHERE tmdb_id = m.tmdb_id) as watch_count
                FROM movie_info m
                INNER JOIN movie_records r ON m.tmdb_id = r.tmdb_id
                WHERE {where_sql}
                ORDER BY
                    CASE WHEN ? = 'watched_date' THEN 0 ELSE 1 END,
                    CASE WHEN ? = 'release_date' THEN 0 ELSE 1 END,
                    CASE WHEN ? = 'vote_average' THEN 0 ELSE 1 END,
                    CASE WHEN ? = 'vote_count' THEN 0 ELSE 1 END,
                    CASE
                        WHEN ? = 'watched_date' THEN r.watched_date
                        WHEN ? = 'release_date' THEN m.release_date
                        WHEN ? = 'vote_average' THEN m.vote_average
                        WHEN ? = 'vote_count' THEN m.vote_count
                        ELSE NULL
                    END {order_dir} NULLS LAST,
                    r.watched_date DESC
                LIMIT ? OFFSET ?
            """
            cursor.execute(sql, params + [sort_by] * 8 + [limit, offset])
            records = [self._dict_from_row(row) for row in cursor.fetchall()]

            return records, total

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
        with self._get_connection() as conn:
            cursor = conn.cursor()

            where_clauses, params, need_join = self._build_filter_conditions(
                "", month, rating_min, rating_max, decade, vote_count_min, search
            )
            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

            if need_join:
                sql = f"""
                    SELECT DISTINCT strftime('%Y', r.watched_date) as year
                    FROM movie_records r
                    INNER JOIN movie_info m ON m.tmdb_id = r.tmdb_id
                    WHERE {where_sql}
                    ORDER BY year DESC
                """
            else:
                sql = f"""
                    SELECT DISTINCT strftime('%Y', r.watched_date) as year
                    FROM movie_records r
                    WHERE {where_sql}
                    ORDER BY year DESC
                """

            cursor.execute(sql, params)
            return [row["year"] for row in cursor.fetchall() if row["year"]]

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
        with self._get_connection() as conn:
            cursor = conn.cursor()

            where_clauses, params, need_join = self._build_filter_conditions(
                year, "", rating_min, rating_max, decade, vote_count_min, search
            )
            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

            if need_join:
                sql = f"""
                    SELECT DISTINCT strftime('%m', r.watched_date) as month
                    FROM movie_records r
                    INNER JOIN movie_info m ON m.tmdb_id = r.tmdb_id
                    WHERE {where_sql}
                    ORDER BY month ASC
                """
            else:
                sql = f"""
                    SELECT DISTINCT strftime('%m', r.watched_date) as month
                    FROM movie_records r
                    WHERE {where_sql}
                    ORDER BY month ASC
                """

            cursor.execute(sql, params)
            return [row["month"] for row in cursor.fetchall() if row["month"]]

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
        with self._get_connection() as conn:
            cursor = conn.cursor()

            where_clauses, params, _ = self._build_filter_conditions(
                year, month, rating_min, rating_max, "", vote_count_min, search
            )
            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

            sql = f"""
                SELECT DISTINCT (CAST(strftime('%Y', m.release_date) AS INTEGER) / 10 * 10) as decade
                FROM movie_records r
                INNER JOIN movie_info m ON m.tmdb_id = r.tmdb_id
                WHERE {where_sql} AND m.release_date IS NOT NULL
                ORDER BY decade ASC
            """

            cursor.execute(sql, params)
            return [f"{row['decade']}s" for row in cursor.fetchall() if row["decade"]]

    def get_stats(self) -> Dict[str, Any]:
        """获取观影统计"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 总数
            cursor.execute("SELECT COUNT(*) as total FROM movie_records")
            total = cursor.fetchone()["total"]

            # 按年统计
            cursor.execute(
                """
                SELECT strftime('%Y', watched_date) as year, COUNT(*) as count
                FROM movie_records
                GROUP BY year
                ORDER BY year DESC
            """
            )
            by_year = [
                {"year": row["year"], "count": row["count"]}
                for row in cursor.fetchall()
            ]

            return {
                "total": total,
                "by_year": by_year,
            }

    def get_movie_detail(self, tmdb_id: int) -> Optional[Dict[str, Any]]:
        """获取电影详情"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            # 查询电影信息
            cursor.execute("SELECT * FROM movie_info WHERE tmdb_id = ?", (tmdb_id,))
            movie_row = cursor.fetchone()
            if not movie_row:
                return None

            movie = self._dict_from_row(movie_row)

            # 查询观影记录
            cursor.execute(
                """
                SELECT watched_date, rating, review
                FROM movie_records
                WHERE tmdb_id = ?
                ORDER BY watched_date DESC
            """,
                (tmdb_id,),
            )
            records = [self._dict_from_row(row) for row in cursor.fetchall()]

            return {
                "movie": movie,
                "records": records,
            }

    def add_movie_info(self, movie: MovieInfo) -> bool:
        """添加电影信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT OR REPLACE INTO movie_info (
                    tmdb_id, title, original_title, overview, release_date,
                    poster_path, backdrop_path, genres, vote_average, vote_count,
                    runtime
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    movie.tmdb_id,
                    movie.title,
                    movie.original_title,
                    movie.overview,
                    movie.release_date,
                    movie.poster_path,
                    movie.backdrop_path,
                    movie.genres,
                    movie.vote_average,
                    movie.vote_count,
                    movie.runtime,
                ),
            )
            conn.commit()
            return True

    def add_record(
        self,
        tmdb_id: int,
        watched_date: str,
        rating: Optional[float] = None,
        review: str = "",
    ) -> bool:
        """添加观影记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO movie_records (tmdb_id, watched_date, rating, review)
                VALUES (?, ?, ?, ?)
            """,
                (tmdb_id, watched_date, rating, review),
            )
            conn.commit()
            return True

    def movie_exists(self, tmdb_id: int) -> bool:
        """检查电影是否存在"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM movie_info WHERE tmdb_id = ?", (tmdb_id,))
            return cursor.fetchone() is not None

    def update_watched_date(
        self, tmdb_id: int, old_date: str, new_date: str
    ) -> Tuple[bool, Optional[str]]:
        """更新观影日期，如果日期重复则返回错误信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 标准化日期格式（支持 / 和 - 分隔）
            old_date_normalized = old_date.replace("/", "-")
            new_date_normalized = new_date.replace("/", "-")

            # 检查新日期是否已存在（排除当前记录）
            cursor.execute(
                """
                SELECT COUNT(*) as count
                FROM movie_records
                WHERE tmdb_id = ? AND replace(watched_date, '/', '-') = ?
                AND replace(watched_date, '/', '-') != ?
            """,
                (tmdb_id, new_date_normalized, old_date_normalized),
            )
            result = cursor.fetchone()
            if result["count"] > 0:
                return False, "该日期已存在观影记录，请选择其他日期"

            try:
                cursor.execute(
                    """
                    UPDATE movie_records
                    SET watched_date = ?
                    WHERE tmdb_id = ? AND replace(watched_date, '/', '-') = ?
                """,
                    (new_date, tmdb_id, old_date_normalized),
                )
                conn.commit()
                return cursor.rowcount > 0, None
            except Exception as e:
                return False, f"更新失败: {str(e)}"

    def delete_record(self, tmdb_id: int, watched_date: str) -> bool:
        """删除观影记录（不删除电影信息）"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # 标准化日期格式
            watched_date_normalized = watched_date.replace("/", "-")
            cursor.execute(
                """
                DELETE FROM movie_records
                WHERE tmdb_id = ? AND replace(watched_date, '/', '-') = ?
            """,
                (tmdb_id, watched_date_normalized),
            )
            conn.commit()
            return cursor.rowcount > 0

    def get_genres(
        self,
        year: str = "",
        month: str = "",
        decade: str = "",
        rating_min: Optional[float] = None,
        rating_max: Optional[float] = None,
        vote_count_min: Optional[int] = None,
        search: str = "",
    ) -> List[str]:
        """获取所有电影主题/类型列表（根据当前过滤条件）"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            where_clauses, params, need_join = self._build_filter_conditions(
                year, month, rating_min, rating_max, decade, vote_count_min, search, ""
            )

            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

            # 获取所有genres字符串，然后解析
            # 始终需要JOIN到movie_info表以获取genres字段
            sql = f"""
                SELECT DISTINCT m.genres
                FROM movie_records r
                INNER JOIN movie_info m ON m.tmdb_id = r.tmdb_id
                WHERE {where_sql}
                AND m.genres IS NOT NULL AND m.genres != ''
            """

            try:
                cursor.execute(sql, params)
                rows = cursor.fetchall()

                # 解析genres字符串，提取所有唯一的genres
                genres_set = set()
                for row in rows:
                    genres_str = row[0]
                    if genres_str:
                        # genres存储为"类型1, 类型2"的格式，用逗号分隔
                        genres_list = [g.strip() for g in genres_str.split(",")]
                        genres_set.update(genres_list)

                # 返回排序后的genres列表
                return sorted(list(genres_set))
            except Exception as e:
                import logging

                logging.error(f"获取genres失败: {str(e)}, SQL: {sql}, params: {params}")
                return []

    # ==================== 电影管理 ====================

    def get_movie_info(self, tmdb_id: int) -> Optional[Dict[str, Any]]:
        """获取电影完整信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM movie_info WHERE tmdb_id = ?", (tmdb_id,))
            row = cursor.fetchone()
            return self._dict_from_row(row) if row else None

    def update_movie_info(self, tmdb_id: int, fields: Dict[str, Any]) -> bool:
        """更新电影信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if not fields:
                return False

            # 构建 UPDATE 语句
            set_clause = ", ".join([f"{k} = ?" for k in fields.keys()])
            values = list(fields.values()) + [tmdb_id]

            cursor.execute(
                f"UPDATE movie_info SET {set_clause} WHERE tmdb_id = ?", values
            )
            conn.commit()
            return cursor.rowcount > 0

    # ==================== 影院管理 ====================

    def get_cinemas(
        self, city: str = "", page: int = 1, limit: int = 20
    ) -> List[Dict[str, Any]]:
        """获取影院列表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            if city:
                cursor.execute(
                    "SELECT * FROM movie_cinemas WHERE city = ? ORDER BY name LIMIT ? OFFSET ?",
                    (city, limit, (page - 1) * limit),
                )
            else:
                cursor.execute(
                    "SELECT * FROM movie_cinemas ORDER BY name LIMIT ? OFFSET ?",
                    (limit, (page - 1) * limit),
                )

            return [self._dict_from_row(row) for row in cursor.fetchall()]

    def create_cinema(self, name: str, city: str) -> int:
        """创建影院"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO movie_cinemas (name, city) VALUES (?, ?)", (name, city)
            )
            conn.commit()
            return cursor.lastrowid

    def get_cinema(self, cinema_id: int) -> Optional[Dict[str, Any]]:
        """获取影院详情"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM movie_cinemas WHERE id = ?", (cinema_id,))
            row = cursor.fetchone()
            return self._dict_from_row(row) if row else None

    def update_cinema(self, cinema_id: int, fields: Dict[str, Any]) -> bool:
        """更新影院信息"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            if not fields:
                return False

            set_clause = ", ".join([f"{k} = ?" for k in fields.keys()])
            values = list(fields.values()) + [cinema_id]

            cursor.execute(
                f"UPDATE movie_cinemas SET {set_clause} WHERE id = ?", values
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_cinema(self, cinema_id: int) -> bool:
        """删除影院"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM movie_cinemas WHERE id = ?", (cinema_id,))
            conn.commit()
            return cursor.rowcount > 0

    # ==================== 影院观影记录 ====================

    def create_cinema_record(
        self, record_id: int, cinema_id: int, ticket_price: Optional[float] = None
    ) -> int:
        """创建影院观影记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO movie_cinema_records (record_id, cinema_id, ticket_price) VALUES (?, ?, ?)",
                (record_id, cinema_id, ticket_price),
            )
            conn.commit()
            return cursor.lastrowid

    def get_cinema_records(
        self,
        record_id: Optional[int] = None,
        cinema_id: Optional[int] = None,
        page: int = 1,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """获取影院观影记录列表"""
        with self._get_connection() as conn:
            cursor = conn.cursor()

            where_clauses = []
            params = []

            if record_id is not None:
                where_clauses.append("record_id = ?")
                params.append(record_id)

            if cinema_id is not None:
                where_clauses.append("cinema_id = ?")
                params.append(cinema_id)

            where_sql = " AND ".join(where_clauses) if where_clauses else "1=1"

            cursor.execute(
                f"SELECT * FROM movie_cinema_records WHERE {where_sql} ORDER BY id DESC LIMIT ? OFFSET ?",
                params + [limit, (page - 1) * limit],
            )

            return [self._dict_from_row(row) for row in cursor.fetchall()]

    def update_cinema_record(
        self, record_id: int, cinema_id: int, ticket_price: Optional[float] = None
    ) -> bool:
        """更新影院观影记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE movie_cinema_records SET cinema_id = ?, ticket_price = ? WHERE id = ?",
                (cinema_id, ticket_price, record_id),
            )
            conn.commit()
            return cursor.rowcount > 0

    def delete_cinema_record(self, record_id: int) -> bool:
        """删除影院观影记录"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM movie_cinema_records WHERE id = ?", (record_id,)
            )
            conn.commit()
            return cursor.rowcount > 0
