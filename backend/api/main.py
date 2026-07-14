from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from backend.models.database import SessionLocal
from backend.models.schema import VideoTask
from backend.tasks.video_pipeline import run_video_pipeline

app = FastAPI(title="MatrixV API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/tasks/start")
def start_video_task(db: Session = Depends(get_db)):
    """
    创建一个新任务并触发流水线。
    """
    new_task = VideoTask(
        title="Auto Generated Task",
        status="pending",
        user_id=1 
    )
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    
    # 触发 Celery 任务
    run_video_pipeline.delay(new_task.id)
    
    return {"message": "Task started", "task_id": new_task.id}

@app.get("/api/tasks")
def get_tasks(db: Session = Depends(get_db)):
    tasks = db.query(VideoTask).order_by(VideoTask.created_at.desc()).all()
    return [{"id": t.id, "title": t.title, "status": t.status, "output_url": t.output_url} for t in tasks]

@app.get("/")
def read_root():
    return {"status": "MatrixV Backend API is running"}
