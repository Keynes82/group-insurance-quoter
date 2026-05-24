"""方案模板 API 路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from src.core.database import get_db
from src.models.schemas import InsuranceTemplate
from src.api.models import TemplateCreate, TemplateResponse

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("/", response_model=List[TemplateResponse])
def get_templates(
    industry: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    获取方案模板列表
    """
    query = db.query(InsuranceTemplate)
    if industry:
        query = query.filter(InsuranceTemplate.industry == industry)
    templates = query.offset(skip).limit(limit).all()
    return templates


@router.get("/{template_id}", response_model=TemplateResponse)
def get_template(template_id: int, db: Session = Depends(get_db)):
    """
    获取单个模板详情
    """
    template = db.query(InsuranceTemplate).filter(
        InsuranceTemplate.id == template_id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return template


@router.post("/", response_model=TemplateResponse)
def create_template(template: TemplateCreate, db: Session = Depends(get_db)):
    """
    创建新模板
    """
    db_template = InsuranceTemplate(**template.model_dump())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.delete("/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    """
    删除模板
    """
    template = db.query(InsuranceTemplate).filter(
        InsuranceTemplate.id == template_id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    db.delete(template)
    db.commit()
    return {"message": "模板已删除"}
