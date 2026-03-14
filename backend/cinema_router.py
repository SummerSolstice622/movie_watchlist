"""
影院管理 API
"""

from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter(prefix="/movie", tags=["movie-cinema"])


def get_db():
    """获取数据库实例"""
    from .db.sqlite_db import SQLiteMovieDB

    return SQLiteMovieDB()


class CinemaCreate(BaseModel):
    """影院创建"""

    name: str
    city: str


class CinemaUpdate(BaseModel):
    """影院更新"""

    name: Optional[str] = None
    city: Optional[str] = None


class Cinema(BaseModel):
    """影院信息"""

    id: int
    name: str
    city: str


@router.get("/cinemas")
def list_cinemas(
    city: str = Query("", description="按城市筛选"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=10000),
):
    """获取影院列表"""
    db = get_db()

    try:
        cinemas = db.get_cinemas(city=city, page=page, limit=limit)
        return {
            "success": True,
            "data": cinemas,
            "pagination": {"page": page, "limit": limit},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cinemas")
def create_cinema(request: CinemaCreate):
    """创建影院"""
    db = get_db()

    if not request.name or not request.city:
        raise HTTPException(status_code=400, detail="影院名称和城市不能为空")

    try:
        cinema_id = db.create_cinema(request.name, request.city)
        return {
            "success": True,
            "message": "影院创建成功",
            "data": {"id": cinema_id, "name": request.name, "city": request.city},
        }
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=409, detail="该影院在该城市已存在")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cinemas/{cinema_id}")
def get_cinema(cinema_id: int):
    """获取影院详情"""
    db = get_db()

    try:
        cinema = db.get_cinema(cinema_id)
        if not cinema:
            raise HTTPException(status_code=404, detail="影院不存在")
        return {"success": True, "data": cinema}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/cinemas/{cinema_id}")
def update_cinema(cinema_id: int, request: CinemaUpdate):
    """更新影院信息"""
    db = get_db()

    try:
        success = db.update_cinema(cinema_id, request.dict(exclude_unset=True))
        if not success:
            raise HTTPException(status_code=404, detail="影院不存在")
        return {"success": True, "message": "影院更新成功"}
    except Exception as e:
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=409, detail="该影院在该城市已存在")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cinemas/{cinema_id}")
def delete_cinema(cinema_id: int):
    """删除影院"""
    db = get_db()

    try:
        success = db.delete_cinema(cinema_id)
        if not success:
            raise HTTPException(status_code=404, detail="影院不存在")
        return {"success": True, "message": "影院删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 影院观影记录 API
class CinemaRecordCreate(BaseModel):
    """影院观影记录创建"""

    record_id: int
    cinema_id: int
    ticket_price: Optional[float] = None


@router.post("/cinema-records")
def create_cinema_record(request: CinemaRecordCreate):
    """创建影院观影记录"""
    db = get_db()

    try:
        record_id = db.create_cinema_record(
            request.record_id, request.cinema_id, request.ticket_price
        )
        return {"success": True, "message": "记录创建成功", "data": {"id": record_id}}
    except Exception as e:
        if "FOREIGN KEY constraint failed" in str(e):
            raise HTTPException(status_code=400, detail="观影记录或影院ID无效")
        if "UNIQUE constraint failed" in str(e):
            raise HTTPException(status_code=409, detail="该观影记录已关联该影院")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/cinema-records")
def list_cinema_records(
    record_id: Optional[int] = Query(None),
    cinema_id: Optional[int] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    """获取影院观影记录列表"""
    db = get_db()

    try:
        records = db.get_cinema_records(
            record_id=record_id, cinema_id=cinema_id, page=page, limit=limit
        )
        return {
            "success": True,
            "data": records,
            "pagination": {"page": page, "limit": limit},
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/cinema-records/{record_id}")
def update_cinema_record(record_id: int, request: CinemaRecordCreate):
    """更新影院观影记录"""
    db = get_db()

    try:
        success = db.update_cinema_record(
            record_id, request.cinema_id, request.ticket_price
        )
        if not success:
            raise HTTPException(status_code=404, detail="记录不存在")
        return {"success": True, "message": "记录更新成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/cinema-records/{record_id}")
def delete_cinema_record(record_id: int):
    """删除影院观影记录"""
    db = get_db()

    try:
        success = db.delete_cinema_record(record_id)
        if not success:
            raise HTTPException(status_code=404, detail="记录不存在")
        return {"success": True, "message": "记录删除成功"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
