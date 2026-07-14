from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    """
    User 表：存储系统用户的基本信息。
    """
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, comment="用户自增ID")
    username = Column(String(50), unique=True, index=True, comment="用户名，系统内唯一")
    role = Column(String(50), default="user", comment="角色权限 (如: admin, user)")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="账户创建时间")
    
    # 关系映射：一个用户可以有多个项目
    projects = relationship("Project", back_populates="user")

class Project(Base):
    """
    Project 表：存储用户的视频创作项目。
    每个项目可以包含多个视频生成任务 (VideoTask)。
    """
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True, comment="项目自增ID")
    user_id = Column(Integer, ForeignKey("users.id"), comment="所属用户ID")
    name = Column(String(100), comment="项目名称")
    mode = Column(String(20), default="auto", comment="运行模式 (auto/manual)")
    platform_target = Column(String(50), comment="目标分发平台 (如: douyin, xiaohongshu)")
    
    # 关系映射
    user = relationship("User", back_populates="projects")
    tasks = relationship("VideoTask", back_populates="project")

class VideoTask(Base):
    """
    VideoTask 表：核心任务表，记录单条视频从选题到发布的整个生命周期。
    内部维护一个状态机：pending → scraping → writing → rendering → publishing → done/failed。
    """
    __tablename__ = "video_tasks"
    id = Column(Integer, primary_key=True, index=True, comment="任务自增ID")
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, comment="所属项目ID(可空，支持独立任务)")
    title = Column(String(200), nullable=True, comment="任务标题/视频标题")
    status = Column(String(20), default="pending", comment="当前所处状态机节点")
    source_topic_id = Column(Integer, nullable=True, comment="关联的热点选题ID")
    script_text = Column(Text, nullable=True, comment="Agent 2 生成的最终视频文案")
    video_url = Column(String(255), nullable=True, comment="最终生成的成品视频URL")
    anti_detect_config = Column(JSON, nullable=True, comment="当前任务采用的去重策略参数(JSON)")
    publish_status = Column(String(50), nullable=True, comment="分发状态")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="任务创建时间")
    
    # 关系映射
    project = relationship("Project", back_populates="tasks")
    assets = relationship("Asset", back_populates="task")  # 该任务产生的所有中间素材
    logs = relationship("AgentLog", back_populates="task") # 各个Agent执行的日志轨迹

class Asset(Base):
    """
    Asset 表：存储任务执行过程中产生的各类中间资产 (空镜、配音、字幕等)。
    """
    __tablename__ = "assets"
    id = Column(Integer, primary_key=True, index=True, comment="资产自增ID")
    task_id = Column(Integer, ForeignKey("video_tasks.id"), comment="归属任务ID")
    type = Column(String(20), comment="资产类型 (video/audio/image/subtitle)")
    storage_url = Column(String(255), comment="对象存储(如MinIO)的访问URL")
    duration = Column(Integer, nullable=True, comment="若是音视频，记录其时长(秒/毫秒)")
    metadata_json = Column(JSON, nullable=True, comment="额外元数据(如: 关键帧, BGM情感标签等)")
    
    # 关系映射
    task = relationship("VideoTask", back_populates="assets")

class AgentLog(Base):
    """
    AgentLog 表：记录所有 Agent 的每一次执行动作、LLM调用耗时及消耗，以便于后续审计及重试。
    """
    __tablename__ = "agent_logs"
    id = Column(Integer, primary_key=True, index=True, comment="日志自增ID")
    task_id = Column(Integer, ForeignKey("video_tasks.id"), comment="归属任务ID")
    agent_name = Column(String(50), comment="执行的Agent名称 (如: trend_catcher)")
    input_data = Column(JSON, nullable=True, comment="Agent接收到的输入参数契约(JSON)")
    output_data = Column(JSON, nullable=True, comment="Agent输出的结果契约(JSON)")
    llm_tokens = Column(Integer, nullable=True, comment="本次调用消耗的LLM Token数")
    duration_ms = Column(Integer, nullable=True, comment="Agent执行总耗时(毫秒)")
    error_message = Column(Text, nullable=True, comment="若失败，记录异常详情")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="日志记录时间")
    
    # 关系映射
    task = relationship("VideoTask", back_populates="logs")
