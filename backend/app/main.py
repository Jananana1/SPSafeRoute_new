import os
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, status, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import timedelta
from . import models, schemas, auth, database
from .routes import incidents, users
from . import admin_routes 
from . import tasks
import logging
logging.basicConfig(level=logging.DEBUG)
# Create tables
models.Base.metadata.create_all(bind=database.engine)

# ===== Create FastAPI app =====
app = FastAPI(title="SP Core Service")

# ===== Startup event: seed admin =====
@app.on_event("startup")
def seed_admin_on_startup():
    from .database import SessionLocal
    from .auth import seed_admin
    db = SessionLocal()
    try:
        seed_admin(db)
    finally:
        db.close()

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Include routers =====
app.include_router(incidents.router)
app.include_router(users.router)
app.include_router(admin_routes.router)   # <-- now this works

# ===== Firebase Service Worker =====
@app.get("/firebase-messaging-sw.js")
async def firebase_sw():
    sw_path = Path.cwd() / "firebase-messaging-sw.js"
    if sw_path.exists():
        return FileResponse(sw_path, media_type="application/javascript")
    return Response("Service worker not found", status_code=404)

# ===== Health & Auth endpoints =====
@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/auth/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(auth.get_db)):
    existing = db.query(models.User).filter(models.User.email == user.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = auth.get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        hashed_password=hashed,
        full_name=user.full_name,
        is_admin=False
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    access_token = auth.create_access_token(data={"sub": str(db_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

@app.on_event("startup")
def start_scheduler():
    tasks.scheduler.start()

@app.post("/auth/login", response_model=schemas.Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(auth.get_db)):
    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user or not auth.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}


# ===== FCM Token registration =====
@app.post("/user/fcm-token")
def register_fcm_token(
    data: schemas.FCMTokenCreate,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    db.query(models.FCMToken).filter(
        models.FCMToken.user_id == current_user.id,
        models.FCMToken.token == data.token
    ).delete()
    new_token = models.FCMToken(user_id=current_user.id, token=data.token)
    db.add(new_token)
    db.commit()
    return {"message": "FCM token saved"}

# ===== Static files mount (MUST BE LAST) =====
project_root = Path.cwd()
print(f"Serving static files from: {project_root}")
app.mount("/", StaticFiles(directory=str(project_root), html=True), name="root")