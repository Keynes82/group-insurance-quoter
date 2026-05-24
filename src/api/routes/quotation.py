"""报价相关 API 路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.core.database import get_db
from src.core.calculator import calculate_premium
from src.models.schemas import Quotation
from src.api.models import (
    QuotationRequest,
    QuotationResponse,
    QuotationDetail,
)

router = APIRouter(prefix="/quotations", tags=["quotations"])


@router.post("/calculate", response_model=QuotationDetail)
def calculate_quotation(request: QuotationRequest, db: Session = Depends(get_db)):
    """
    计算保费（不保存）
    """
    result = calculate_premium(
        industry=request.client.industry,
        employee_count=request.client.employee_count,
        average_age=request.client.average_age,
        insurance_type=request.insurance_type,
        coverage_amount=request.coverage_amount,
    )
    return result


@router.post("/save", response_model=QuotationResponse)
def save_quotation(request: QuotationRequest, db: Session = Depends(get_db)):
    """
    计算并保存报价
    """
    result = calculate_premium(
        industry=request.client.industry,
        employee_count=request.client.employee_count,
        average_age=request.client.average_age,
        insurance_type=request.insurance_type,
        coverage_amount=request.coverage_amount,
    )
    
    quotation = Quotation(
        company_name=request.client.company_name,
        industry=request.client.industry,
        employee_count=request.client.employee_count,
        average_age=request.client.average_age,
        insurance_type=request.insurance_type,
        coverage_amount=request.coverage_amount,
        premium=result["total_premium"],
        risk_level=result["risk_level"],
        risk_notes=result["risk_notes"],
        template_name=request.template_name,
    )
    
    db.add(quotation)
    db.commit()
    db.refresh(quotation)
    
    return quotation


@router.get("/history", response_model=List[QuotationResponse])
def get_quotation_history(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取报价历史
    """
    quotations = db.query(Quotation).order_by(
        Quotation.created_at.desc()
    ).offset(skip).limit(limit).all()
    return quotations


@router.get("/{quotation_id}", response_model=QuotationResponse)
def get_quotation(quotation_id: int, db: Session = Depends(get_db)):
    """
    获取单个报价详情
    """
    quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not quotation:
        raise HTTPException(status_code=404, detail="报价记录不存在")
    return quotation


@router.delete("/{quotation_id}")
def delete_quotation(quotation_id: int, db: Session = Depends(get_db)):
    """
    删除报价记录
    """
    quotation = db.query(Quotation).filter(Quotation.id == quotation_id).first()
    if not quotation:
        raise HTTPException(status_code=404, detail="报价记录不存在")
    
    db.delete(quotation)
    db.commit()
    return {"message": "报价记录已删除"}
