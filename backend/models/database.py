from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker

# 默认本地开发 PostgreSQL 数据库连接; 生产环境应通过环境变量注入
SQLALCHEMY_DATABASE_URL = "postgresql://matrixv:password@localhost/matrixv"

# 创建数据库引擎
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# 创建本地 Session 工厂类
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 创建 Declarative Base 基类，所有的模型类都要继承该类
Base = declarative_base()

def get_db():
    """
    依赖注入函数: 获取数据库 Session。
    在 FastAPI 的 endpoint 中通过 Depends(get_db) 注入使用。
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

