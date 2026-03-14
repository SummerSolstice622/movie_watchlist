"""
电影模块 API 路由测试
"""

import os
import sys

import pytest

# 添加 backend 路径
sys.path.insert(
    0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from fastapi.testclient import TestClient

from backend.main import app


@pytest.fixture
def client():
    """创建测试客户端"""
    return TestClient(app)


class TestMovieRoutes:
    """电影路由测试"""

    def test_get_records(self, client):
        """测试获取观影记录"""
        response = client.get("/movie/records")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert data["success"] is True
        assert "data" in data

    def test_get_records_with_year_filter(self, client):
        """测试按年份筛选观影记录"""
        response = client.get("/movie/records?year=2024")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_records_with_sort(self, client):
        """测试排序观影记录"""
        response = client.get("/movie/records?sort_by=vote_average&sort_order=desc")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_get_statistics(self, client):
        """测试获取统计信息"""
        response = client.get("/movie/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        # 检查统计数据结构
        stats = data["data"]
        assert "total" in stats
        assert "by_year" in stats

    def test_get_years(self, client):
        """测试获取年份列表"""
        response = client.get("/movie/years")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)


class TestMovieSearch:
    """电影搜索测试"""

    def test_search_movies(self, client):
        """测试搜索电影"""
        response = client.get("/movie/search?query=肖申克")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert isinstance(data["data"], list)

    def test_search_movies_english(self, client):
        """测试搜索英文电影"""
        response = client.get("/movie/search?query=Inception")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True

    def test_search_movies_empty_query(self, client):
        """测试空查询"""
        response = client.get("/movie/search?query=")
        # 空查询应该返回422验证错误
        assert response.status_code == 422


class TestMovieRecordOperations:
    """观影记录操作测试"""

    def test_update_watched_date(self, client):
        """测试更新观影日期"""
        # 先获取一条记录
        records_response = client.get("/movie/records?limit=1")
        if records_response.status_code == 200:
            data = records_response.json()
            if data["data"]:
                tmdb_id = data["data"][0]["tmdb_id"]
                old_date = data["data"][0]["watched_date"]

                # 更新日期（使用查询参数传递old_date）
                update_response = client.put(
                    f"/movie/records/{tmdb_id}/date?old_date={old_date}",
                    json={"watched_date": "2024-01-15"},
                )
                assert update_response.status_code == 200

                # 恢复原日期
                client.put(
                    f"/movie/records/{tmdb_id}/date?old_date=2024-01-15",
                    json={"watched_date": old_date},
                )

    def test_update_watched_date_invalid_format(self, client):
        """测试无效日期格式"""
        response = client.put(
            "/movie/records/999999/date?old_date=2024-01-01",
            json={"watched_date": "invalid-date"},
        )
        # 应该返回错误（404表示记录不存在也是合理的）
        assert response.status_code in [400, 404, 422, 500]


class TestMovieExport:
    """导出测试"""

    def test_export_records(self, client):
        """测试导出观影记录"""
        response = client.get("/movie/export")
        assert response.status_code == 200
        assert (
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            in response.headers["content-type"]
        )

    def test_export_records_with_year(self, client):
        """测试按年份导出"""
        response = client.get("/movie/export?year=2024")
        assert response.status_code == 200

    def test_export_records_with_month(self, client):
        """测试按月份导出"""
        response = client.get("/movie/export?year=2024&month=1")
        assert response.status_code == 200


class TestMovieAddFromTMDB:
    """从TMDB添加电影测试"""

    def test_add_movie_from_tmdb(self, client):
        """测试从TMDB添加电影"""
        # 使用一个不太常见的电影ID，避免已存在
        # 怪兽屋 Monster House (2006) - TMDB ID 9297
        response = client.post("/movie/movies/9297/add")
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # 可能是新添加或已存在
        assert "message" in data

    def test_add_movie_invalid_id(self, client):
        """测试添加无效电影ID"""
        response = client.post("/movie/movies/999999999/add")
        # TMDB会返回404或服务器会返回500
        assert response.status_code in [404, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
