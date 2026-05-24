from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class Quotation(Base):
    """报价记录"""
    __tablename__ = "quotations"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 企业客户信息
    company_name = Column(String(200), nullable=False)
    industry = Column(String(50), nullable=False)
    employee_count = Column(Integer, nullable=False)
    average_age = Column(Float, nullable=False)
    
    # 投保信息
    insurance_type = Column(String(50), nullable=False)
    coverage_amount = Column(Float, nullable=False)  # 保额（万元）
    premium = Column(Float, nullable=False)  # 应交保费（元）
    
    # 风控信息
    risk_level = Column(String(20), nullable=False)  # low/medium/high
    risk_notes = Column(Text, nullable=True)
    
    # 方案模板
    template_name = Column(String(100), nullable=True)

class InsuranceTemplate(Base):
    """保险方案模板"""
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    industry = Column(String(50), nullable=False)
    description = Column(Text, nullable=True)
    
    # 默认配置
    default_coverage = Column(Float, nullable=False)  # 默认保额（万元）
    default_insurance_type = Column(String(50), nullable=False)
    base_rate = Column(Float, nullable=False)  # 基础费率
    
    created_at = Column(DateTime, default=datetime.utcnow)

# 数据库连接
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/quotations.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """初始化数据库"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()