"""Pydantic 数据模型"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ClientInfo(BaseModel):
    """企业客户信息"""
    company_name: str = Field(..., min_length=1, max_length=200, description="企业名称")
    industry: str = Field(..., description="所属行业")
    employee_count: int = Field(..., ge=1, le=10000, description="员工人数")
    average_age: float = Field(..., ge=18, le=65, description="平均年龄")


class QuotationRequest(BaseModel):
    """报价请求"""
    client: ClientInfo
    insurance_type: str = Field(..., description="投保险种")
    coverage_amount: float = Field(..., ge=1, le=1000, description="保额（万元）")
    template_name: Optional[str] = Field(None, description="使用的方案模板名称")


class QuotationResponse(BaseModel):
    """报价响应"""
    id: int
    created_at: datetime
    company_name: str
    industry: str
    employee_count: int
    average_age: float
    insurance_type: str
    coverage_amount: float
    premium: float
    risk_level: str
    risk_notes: Optional[str]
    template_name: Optional[str]


class PremiumBreakdown(BaseModel):
    """保费明细"""
    base_rate: float
    industry_factor: float
    age_factor: float
    count_discount: float
    coverage_amount: float
    employee_count: int


class QuotationDetail(BaseModel):
    """报价详情（含明细）"""
    per_capita_premium: float
    total_premium: float
    risk_level: str
    risk_notes: str
    breakdown: PremiumBreakdown


class TemplateBase(BaseModel):
    """方案模板基础"""
    name: str
    industry: str
    description: Optional[str]
    default_coverage: float
    default_insurance_type: str
    base_rate: float


class TemplateCreate(TemplateBase):
    pass


class TemplateResponse(TemplateBase):
    """模板响应"""
    id: int
    created_at: datetime


class QuotationHistoryItem(BaseModel):
    """报价历史记录"""
    id: int
    created_at: datetime
    company_name: str
    industry: str
    insurance_type: str
    coverage_amount: float
    premium: float
    risk_level: str
