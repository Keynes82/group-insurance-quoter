"""测试 API 路由"""
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.models.schemas import init_db

# 初始化数据库
init_db()

client = TestClient(app)


class TestHealth:
    """测试健康检查"""
    
    def test_health_check(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}
    
    def test_root(self):
        response = client.get("/")
        assert response.status_code == 200
        assert "团险报价助手" in response.json()["message"]


class TestQuotation:
    """测试报价接口"""
    
    def test_calculate_quotation(self):
        payload = {
            "client": {
                "company_name": "测试公司",
                "industry": "IT互联网",
                "employee_count": 50,
                "average_age": 30,
            },
            "insurance_type": "团体意外险",
            "coverage_amount": 50,
        }
        
        response = client.post("/quotations/calculate", json=payload)
        assert response.status_code == 200
        
        result = response.json()
        assert "per_capita_premium" in result
        assert "total_premium" in result
        assert "risk_level" in result
        assert "breakdown" in result
    
    def test_calculate_invalid_data(self):
        """测试无效数据"""
        payload = {
            "client": {
                "company_name": "",
                "industry": "IT互联网",
                "employee_count": 0,  # 无效
                "average_age": 30,
            },
            "insurance_type": "团体意外险",
            "coverage_amount": 50,
        }
        
        response = client.post("/quotations/calculate", json=payload)
        assert response.status_code == 422  # Validation error
    
    def test_save_quotation(self):
        payload = {
            "client": {
                "company_name": "保存测试公司",
                "industry": "制造业",
                "employee_count": 100,
                "average_age": 35,
            },
            "insurance_type": "团体定期寿险",
            "coverage_amount": 80,
        }
        
        response = client.post("/quotations/save", json=payload)
        assert response.status_code == 200
        
        result = response.json()
        assert "id" in result
        assert result["company_name"] == "保存测试公司"
    
    def test_get_history(self):
        response = client.get("/quotations/history")
        assert response.status_code == 200
        assert isinstance(response.json(), list)


class TestTemplates:
    """测试模板接口"""
    
    def test_get_templates(self):
        response = client.get("/templates/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_get_templates_by_industry(self):
        response = client.get("/templates/?industry=制造业")
        assert response.status_code == 200
        templates = response.json()
        for t in templates:
            assert t["industry"] == "制造业"
    
    def test_create_and_delete_template(self):
        payload = {
            "name": "测试模板",
            "industry": "IT互联网",
            "description": "测试用模板",
            "default_coverage": 50,
            "default_insurance_type": "团体意外险",
            "base_rate": 15.0,
        }
        
        # 创建
        create_response = client.post("/templates/", json=payload)
        assert create_response.status_code == 200
        template_id = create_response.json()["id"]
        
        # 删除
        delete_response = client.delete(f"/templates/{template_id}")
        assert delete_response.status_code == 200
