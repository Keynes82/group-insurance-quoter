"""测试保费计算引擎"""
import pytest
from src.core.calculator import calculate_premium, get_age_factor


class TestAgeFactor:
    """测试年龄系数计算"""
    
    def test_young_age(self):
        assert get_age_factor(22) == 0.8
    
    def test_middle_age(self):
        assert get_age_factor(35) == 1.0
    
    def test_old_age(self):
        assert get_age_factor(60) == 2.0
    
    def test_boundary_age(self):
        assert get_age_factor(18) == 0.8
        assert get_age_factor(25) == 0.8
        assert get_age_factor(26) == 1.0


class TestPremiumCalculation:
    """测试保费计算"""
    
    def test_basic_calculation(self):
        result = calculate_premium(
            industry="IT互联网",
            employee_count=100,
            average_age=30,
            insurance_type="团体意外险",
            coverage_amount=50,
        )
        
        assert "per_capita_premium" in result
        assert "total_premium" in result
        assert "risk_level" in result
        assert result["total_premium"] == result["per_capita_premium"] * 100
    
    def test_industry_risk_factor(self):
        """测试行业风险系数影响"""
        it_result = calculate_premium(
            industry="IT互联网", employee_count=50, average_age=30,
            insurance_type="团体意外险", coverage_amount=50,
        )
        
        construction_result = calculate_premium(
            industry="建筑工程", employee_count=50, average_age=30,
            insurance_type="团体意外险", coverage_amount=50,
        )
        
        # 建筑工程风险系数更高，保费应该更高
        assert construction_result["total_premium"] > it_result["total_premium"]
    
    def test_count_discount(self):
        """测试人数折扣"""
        small = calculate_premium(
            industry="IT互联网", employee_count=50, average_age=30,
            insurance_type="团体意外险", coverage_amount=50,
        )
        
        large = calculate_premium(
            industry="IT互联网", employee_count=500, average_age=30,
            insurance_type="团体意外险", coverage_amount=50,
        )
        
        # 大企业的折扣后人均保费应该更低
        assert large["per_capita_premium"] < small["per_capita_premium"]
    
    def test_risk_levels(self):
        """测试不同风险等级"""
        low_risk = calculate_premium(
            industry="教育培训", employee_count=100, average_age=25,
            insurance_type="团体意外险", coverage_amount=30,
        )
        
        high_risk = calculate_premium(
            industry="建筑工程", employee_count=5, average_age=60,
            insurance_type="雇主责任险", coverage_amount=100,
        )
        
        assert low_risk["risk_level"] == "low"
        assert high_risk["risk_level"] == "high"
