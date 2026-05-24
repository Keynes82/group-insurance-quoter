from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from src.models.schemas import init_db
from src.api.routes import quotation, templates


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化数据库
    init_db()
    yield
    # 关闭时清理（如需）


app = FastAPI(
    title="团险报价助手 API",
    description="为企业客户提供快速保费计算、方案模板和风控建议",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(quotation.router)
app.include_router(templates.router)


@app.get("/")
def root():
    return {
        "message": "团险报价助手 API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}
