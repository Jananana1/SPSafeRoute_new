import os
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, status, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
import random
import uuid
from .config import load_project_env
from . import models, schemas, auth, database, email_service
from .routes import incidents, users
from . import admin_routes 
from . import tasks
import logging
logging.basicConfig(level=logging.DEBUG)
# Create tables
models.Base.metadata.create_all(bind=database.engine)

load_project_env()

# ===== Create FastAPI app =====
app = FastAPI(title="SP Core Service")

if os.getenv("ENFORCE_HTTPS", "false").lower() in ("1", "true", "yes"):
    app.add_middleware(HTTPSRedirectMiddleware)

trusted_hosts = os.getenv("TRUSTED_HOSTS")
if trusted_hosts:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=[host.strip() for host in trusted_hosts.split(",") if host.strip()])

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

@app.on_event("startup")
def start_scheduler():
    tasks.scheduler.start()

@app.get("/auth/captcha", response_model=schemas.CaptchaResponse)
def get_captcha(db: Session = Depends(auth.get_db)):
    a = random.randint(1, 10)
    b = random.randint(1, 10)
    answer = str(a + b)
    captcha_id = str(uuid.uuid4())
    challenge = models.CaptchaChallenge(
        id=captcha_id,
        answer=answer,
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )
    db.add(challenge)
    db.commit()
    return {"captcha_id": captcha_id, "question": f"What is {a} + {b}?"}

@app.post("/auth/register", response_model=schemas.Token)
def register(user: schemas.UserCreate, db: Session = Depends(auth.get_db)):
    # Validate Captcha
    challenge = db.query(models.CaptchaChallenge).filter(models.CaptchaChallenge.id == user.captcha_id).first()
    if not challenge or challenge.expires_at < datetime.utcnow() or challenge.answer != user.captcha_answer:
        raise HTTPException(status_code=400, detail="Invalid or expired CAPTCHA")
    
    if user.password != user.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
        
    strength = auth.check_password_strength(user.password)
    if strength in ["Too Short", "Weak"]:
        raise HTTPException(status_code=400, detail="Password is too weak. Must be at least 8 characters and contain uppercase, lowercase, and numbers.")
        
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
    
    # Generate OTP for new user verification
    otp = auth.generate_otp()
    otp_record = models.OTPToken(
        user_id=db_user.id,
        otp_code=otp,
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )
    db.add(otp_record)
    db.commit()
    
    # Send email
    email_service.send_email(db_user.email, "SP SafeRoute – Registration Verification", f"Your OTP is: {otp}", otp_code=otp, email_type="registration")
    
    # Return temp token for MFA
    temp_token = auth.create_access_token(data={"mfa_sub": str(db_user.id)}, expires_delta=timedelta(minutes=5))
    return {"access_token": temp_token, "token_type": "bearer", "mfa_required": True}

@app.post("/auth/login")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(auth.get_db)):
    ip = request.client.host
    
    # Rate limit check (5 failed attempts / min)
    recent_attempts = db.query(models.LoginHistory).filter(
        models.LoginHistory.ip_address == ip,
        models.LoginHistory.status == "failed",
        models.LoginHistory.created_at >= datetime.utcnow() - timedelta(minutes=1)
    ).count()
    if recent_attempts >= 5:
        raise HTTPException(status_code=429, detail="Too many login attempts. Please try again later.")

    user = db.query(models.User).filter(models.User.email == form_data.username).first()
    if not user:
        # Still log attempt with created_at
        hist = models.LoginHistory(ip_address=ip, status="failed", created_at=datetime.utcnow())
        db.add(hist)
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.locked_until and user.locked_until > datetime.utcnow():
        raise HTTPException(status_code=403, detail="Account locked. Please verify your identity.")

    if not auth.verify_password(form_data.password, user.hashed_password):
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.locked_until = datetime.utcnow() + timedelta(minutes=30)
            db.commit()
            raise HTTPException(status_code=403, detail="Account locked. Please verify your identity.")
        
        hist = models.LoginHistory(user_id=user.id, ip_address=ip, status="failed", created_at=datetime.utcnow())
        db.add(hist)
        db.commit()
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Success
    user.failed_login_attempts = 0
    user.locked_until = None
    hist = models.LoginHistory(user_id=user.id, ip_address=ip, status="success", created_at=datetime.utcnow())
    db.add(hist)
    db.commit()
    
    # Bypass MFA for admin
    if user.is_admin or user.email == "admin@saferoute.sp":
        access_token = auth.create_access_token(data={"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer", "mfa_required": False}
        
    # Generate OTP for regular users
    otp = auth.generate_otp()
    otp_record = models.OTPToken(
        user_id=user.id,
        otp_code=otp,
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )
    db.add(otp_record)
    db.commit()
    
    # Send email
    email_service.send_email(user.email, "SP SafeRoute – Login Verification", f"Your OTP is: {otp}", otp_code=otp, email_type="login")
    
    # Return temp token for MFA
    temp_token = auth.create_access_token(data={"mfa_sub": str(user.id)}, expires_delta=timedelta(minutes=5))
    return {"access_token": temp_token, "token_type": "bearer", "mfa_required": True}

@app.post("/auth/verify-mfa", response_model=schemas.Token)
def verify_mfa(data: schemas.MFAVerify, db: Session = Depends(auth.get_db)):
    try:
        payload = auth.jwt.decode(data.token, auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
        user_id_str = payload.get("mfa_sub")
        if not user_id_str:
            raise HTTPException(status_code=401, detail="Invalid MFA token")
        user_id = int(user_id_str)
    except auth.JWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired MFA token")
        
    otp_record = db.query(models.OTPToken).filter(
        models.OTPToken.user_id == user_id,
        models.OTPToken.otp_code == data.otp,
        models.OTPToken.expires_at > datetime.utcnow()
    ).first()
    
    if not otp_record:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        
    db.delete(otp_record)
    db.commit()
    
    access_token = auth.create_access_token(data={"sub": str(user_id)})
    return {"access_token": access_token, "token_type": "bearer", "mfa_required": False}

@app.post("/auth/forgot-password")
def forgot_password(req: schemas.ForgotPasswordRequest, db: Session = Depends(auth.get_db)):
    user = db.query(models.User).filter(models.User.email == req.email).first()
    if user:
        otp = auth.generate_otp()
        otp_record = models.OTPToken(
            user_id=user.id,
            otp_code=otp,
            expires_at=datetime.utcnow() + timedelta(minutes=15)
        )
        db.add(otp_record)
        db.commit()
        email_service.send_email(user.email, "SP SafeRoute – Password Reset", f"Your OTP for password reset is: {otp}", otp_code=otp, email_type="reset")
    return {"message": "If an account exists, an OTP was sent."}

@app.post("/auth/reset-password")
def reset_password(req: schemas.PasswordResetConfirm, db: Session = Depends(auth.get_db)):
    user = db.query(models.User).filter(models.User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid request")
        
    record = db.query(models.OTPToken).filter(
        models.OTPToken.user_id == user.id,
        models.OTPToken.otp_code == req.otp,
        models.OTPToken.expires_at > datetime.utcnow()
    ).first()
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        
    if req.new_password != req.confirm_password:
        raise HTTPException(status_code=400, detail="Passwords do not match")
        
    if auth.check_password_strength(req.new_password) in ["Too Short", "Weak"]:
        raise HTTPException(status_code=400, detail="Password is too weak. Must be at least 8 characters and contain uppercase, lowercase, and numbers.")
        
    user.hashed_password = auth.get_password_hash(req.new_password)
    user.locked_until = None
    user.failed_login_attempts = 0
    
    # Invalidate token
    db.delete(record)
    db.commit()
    return {"message": "Password successfully reset."}

@app.post("/auth/send-unlock-code")
def send_unlock_code(req: schemas.ForgotPasswordRequest, db: Session = Depends(auth.get_db)):
    user = db.query(models.User).filter(models.User.email == req.email).first()
    if user:
        otp = auth.generate_otp()
        otp_record = models.OTPToken(
            user_id=user.id,
            otp_code=otp,
            expires_at=datetime.utcnow() + timedelta(minutes=15)
        )
        db.add(otp_record)
        db.commit()
        email_service.send_email(user.email, "SP SafeRoute – Account Unlock Verification", f"Your 4-digit OTP to unlock your account is: {otp}", otp_code=otp, email_type="reset")
    return {"message": "If an account exists, an OTP was sent."}

@app.post("/auth/unlock-account")
def unlock_account(req: schemas.UnlockAccountRequest, db: Session = Depends(auth.get_db)):
    user = db.query(models.User).filter(models.User.email == req.email).first()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid request")
        
    record = db.query(models.OTPToken).filter(
        models.OTPToken.user_id == user.id,
        models.OTPToken.otp_code == req.otp,
        models.OTPToken.expires_at > datetime.utcnow()
    ).first()
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        
    user.locked_until = None
    user.failed_login_attempts = 0
    db.delete(record)
    db.commit()
    
    # Automatically log the user in
    access_token = auth.create_access_token(data={"sub": str(user.id)})
    return {
        "message": "Account unlocked successfully.",
        "access_token": access_token,
        "token_type": "bearer",
        "mfa_required": False
    }


# ===== FCM Token registration =====
@app.post("/user/fcm-token")
def register_fcm_token(
    data: schemas.FCMTokenCreate,
    db: Session = Depends(auth.get_db),
    current_user: models.User = Depends(auth.get_current_user)
):
    # Keep exactly one active token per user, and remove any stale duplicate token rows.
    db.query(models.FCMToken).filter(
        (models.FCMToken.user_id == current_user.id) |
        (models.FCMToken.token == data.token)
    ).delete(synchronize_session=False)
    new_token = models.FCMToken(user_id=current_user.id, token=data.token)
    db.add(new_token)
    db.commit()
    import logging
    logging.getLogger(__name__).info(f"FCM token registered for user {current_user.id}")
    return {"message": "FCM token saved"}

# ===== Static files mount (MUST BE LAST) =====
project_root = Path.cwd()
print(f"Serving static files from: {project_root}")
app.mount("/", StaticFiles(directory=str(project_root), html=True), name="root")