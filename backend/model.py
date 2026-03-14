"""
电影模型
"""

from typing import Optional

from pydantic import BaseModel, Field


class Movie(BaseModel):
    """电影模型"""

    tmdb_id: int = Field(..., description="TMDB 电影 ID")
    title: str = Field(..., description="电影标题")
    original_title: Optional[str] = Field(None, description="原标题")
    overview: Optional[str] = Field(None, description="简介")
    release_date: Optional[str] = Field(None, description="发布日期")
    poster_path: Optional[str] = Field(None, description="海报路径")
    backdrop_path: Optional[str] = Field(None, description="背景图路径")
    runtime: Optional[int] = Field(None, description="时长(分钟)")
    genres: str = Field("", description="类型，多个用逗号分隔")
    vote_average: float = Field(0.0, description="评分")
    vote_count: int = Field(0, description="评分人数")
    popularity: float = Field(0.0, description="热度")
    adult: bool = Field(False, description="成人内容")

    # 观影记录
    watched: bool = Field(False, description="是否已观看")
    watched_date: Optional[str] = Field(None, description="观看日期")
    rating: Optional[int] = Field(None, description="个人评分(1-5)")
    review: Optional[str] = Field(None, description="个人评论")

    # 元数据
    created_at: Optional[str] = Field(None, description="创建时间")
    updated_at: Optional[str] = Field(None, description="更新时间")

    class Config:
        from_attributes = True
