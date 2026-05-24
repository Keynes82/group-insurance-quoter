"""保费计算引擎 - 使用占位精算公式"""
from typing import Dict, List, Optional

# 行业风险系数
INDUSTRY_RISK_FACTOR = {
    "制造业": 1.2,
    "IT互联网": 0.8,
    "零售贸易": 1.0,
    "建筑工程": 1.5,
    "物流运输": 1.3,
    "金融服务": 0.9,
    "教育培训": 0.7,
    "医疗健康": 1.1,
}

# 险种基础费率（每万元保额的年保费）
BASE_RATE = {
    "团体意外险": 15.0,
    "团体定期寿险": 25.0,
    "团体健康险": 35.0,
    "雇主责任险": 45.0,
    "团体年金险": 20.0,
}

# 年龄调整系数
AGE_ADJUSTMENT = {
    (18, 25): 0.8,
    (26, 35): 1.0,
    (36, 45): 1.2,
    (46, 55): 1.5,
    (56, 65): 2.0,
}


def get_age_factor(average_age: float) -> float:
    """根据平均年龄获取调整系数"""
    for (min_age, max_age), factor in AGE_ADJUSTMENT.items():
        if min_age <= average_age <= max_age:
            return factor
    # 默认最高档
    return 2.5


def calculate_premium(
    industry: str,
    employee_count: int,
    average_age: float,
    insurance_type: str,
    coverage_amount: float,
) -> Dict:
    """
    计算保费
    
    Args:
        industry: 行业类型
        employee_count: 员工人数
        average_age: 平均年龄
        insurance_type: 投保险种
        coverage_amount: 保额（万元）
    
    Returns:
        dict: 包含保费明细和风控信息
    """
    # 获取系数
    industry_factor = INDUSTRY_RISK_FACTOR.get(industry, 1.0)
    base_rate = BASE_RATE.get(insurance_type, 30.0)
    age_factor = get_age_factor(average_age)
    
    # 人数折扣
    count_discount = 1.0
    if employee_count >= 500:
        count_discount = 0.85
    elif employee_count >= 200:
        count_discount = 0.90
    elif employee_count >= 100:
        count_discount = 0.95
    
    # 计算人均保费
    per_capita_premium = coverage_amount * base_rate * industry_factor * age_factor * count_discount
    
    # 总保费
    total_premium = per_capita_premium * employee_count
    
    # 风控评级
    risk_score = (industry_factor - 0.7) / 0.8 * 0.4 + (age_factor - 0.8) / 1.7 * 0.4
    if employee_count < 10:
        risk_score += 0.2
    
    if risk_score < 0.3:
        risk_level = "low"
        risk_notes = "风险可控，标准承保"
    elif risk_score < 0.6:
        risk_level = "medium"
        risk_notes = "中等风险，建议加费或附加条款"
    else:
        risk_level = "high"
        risk_notes = "高风险，建议分保或拒保"
    
    # 额外风控建议
    additional_notes = []
    if industry in ["建筑工程", "物流运输"]:
        additional_notes.append("高风险行业，建议增加职业意外险")
    if average_age > 50:
        additional_notes.append("员工年龄偏大，建议增加健康检查要求")
    if employee_count < 30:
        additional_notes.append("小规模企业，建议提高最低保费门槛")
    
    if additional_notes:
        risk_notes += "；" + "；".join(additional_notes)
    
    return {
        "per_capita_premium": round(per_capita_premium, 2),
        "total_premium": round(total_premium, 2),
        "risk_level": risk_level,
        "risk_notes": risk_notes,
        "breakdown": {
            "base_rate": base_rate,
            "industry_factor": industry_factor,
            "age_factor": age_factor,
            "count_discount": count_discount,
            "coverage_amount": coverage_amount,
            "employee_count": employee_count,
        }
    }


def get_available_industries() -> List[str]:
    """获取支持的行业列表"""
    return list(INDUSTRY_RISK_FACTOR.keys())


def get_available_insurance_types() -> List[str]:
    """获取支持的险种列表"""
    return list(BASE_RATE.keys())
