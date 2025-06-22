from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, JSON, ForeignKey, Enum, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from passlib.context import CryptContext
import jwt
import stripe
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/usc_trea")
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY")
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.gmail.com")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# Initialize services
app = FastAPI(title="USC TREA API", version="1.0.0")
stripe.api_key = STRIPE_SECRET_KEY
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://usctrea.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database setup
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), unique=True, index=True)
    password_hash = Column(String(255))
    first_name = Column(String(50))
    last_name = Column(String(50))
    phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    status = Column(Enum("active", "inactive", "pending", name="user_status"), default="pending")
    
    # Relationships
    applications = relationship("MemberApplication", back_populates="user")
    collaborations = relationship("AlumniCollaboration", back_populates="user")
    roles = relationship("UserRole", back_populates="user")
    profile = relationship("MemberProfile", back_populates="user", uselist=False)

class MemberApplication(Base):
    __tablename__ = "member_applications"
    
    application_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    graduation_year = Column(Integer)
    major = Column(String(100))
    career_interests = Column(JSON)
    interest_reason = Column(Text)
    experience = Column(Text)
    goals = Column(Text)
    application_status = Column(
        Enum("pending", "approved", "rejected", name="application_status"), 
        default="pending"
    )
    submitted_at = Column(DateTime, default=datetime.utcnow)
    reviewed_at = Column(DateTime)
    reviewed_by = Column(Integer, ForeignKey("users.user_id"))
    
    # Relationships
    user = relationship("User", back_populates="applications", foreign_keys=[user_id])

class AlumniCollaboration(Base):
    __tablename__ = "alumni_collaborations"
    
    collaboration_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    company = Column(String(100))
    position = Column(String(100))
    industry = Column(String(50))
    collaboration_type = Column(
        Enum("mentorship", "speaking", "funding", "consulting", name="collaboration_type")
    )
    collaboration_details = Column(Text)
    linkedin_url = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="collaborations")

class MemberProfile(Base):
    __tablename__ = "member_profiles"
    
    profile_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), unique=True)
    bio = Column(Text)
    linkedin_url = Column(String(255))
    experience_level = Column(
        Enum("student", "alumni", "professional", name="experience_level")
    )
    specializations = Column(JSON)
    profile_image_url = Column(String(500))
    is_public = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="profile")

class Resource(Base):
    __tablename__ = "resources"
    
    resource_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    description = Column(Text)
    file_url = Column(String(500))
    resource_type = Column(String(50))
    access_level = Column(
        Enum("public", "member", "admin", name="access_level"), 
        default="member"
    )
    created_by = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    download_count = Column(Integer, default=0)
    tags = Column(JSON)

class Event(Base):
    __tablename__ = "events"
    
    event_id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    description = Column(Text)
    event_date = Column(DateTime)
    event_type = Column(String(50))
    location = Column(String(200))
    virtual_link = Column(String(500))
    registration_required = Column(Boolean, default=True)
    max_attendees = Column(Integer)
    created_by = Column(Integer, ForeignKey("users.user_id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    registrations = relationship("EventRegistration", back_populates="event")

class EventRegistration(Base):
    __tablename__ = "event_registrations"
    
    registration_id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("events.event_id"))
    user_id = Column(Integer, ForeignKey("users.user_id"))
    registered_at = Column(DateTime, default=datetime.utcnow)
    attended = Column(Boolean, default=False)
    
    # Relationships
    event = relationship("Event", back_populates="registrations")

class UserRole(Base):
    __tablename__ = "user_roles"
    
    role_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    role_name = Column(
        Enum("admin", "member", "alumni", name="role_name")
    )
    permissions = Column(JSON)
    assigned_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="roles")

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class UserBase(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    user_id: int
    created_at: datetime
    status: str
    
    class Config:
        from_attributes = True

class MemberApplicationCreate(BaseModel):
    graduation_year: int
    major: str
    career_interests: List[str]
    interest_reason: str
    experience: Optional[str] = None
    goals: str

class AlumniCollaborationCreate(BaseModel):
    company: str
    position: str
    industry: str
    collaboration_type: str
    collaboration_details: str
    linkedin_url: Optional[str] = None
    specializations: List[str]

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Utility Functions
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    return user

def send_email(to_email: str, subject: str, body: str):
    """Send email notifications"""
    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = to_email
    msg['Subject'] = subject
    
    msg.attach(MIMEText(body, 'html'))
    
    try:
        server = smtplib.SMTP(EMAIL_HOST, EMAIL_PORT)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False

def match_alumni_to_members(db: Session, collaboration_type: str) -> List[Dict]:
    """Intelligent matching algorithm"""
    alumni = db.query(AlumniCollaboration).filter(
        AlumniCollaboration.collaboration_type == collaboration_type,
        AlumniCollaboration.is_active == True
    ).all()
    
    members = db.query(MemberApplication).filter(
        MemberApplication.application_status == "approved"
    ).all()
    
    matches = []
    for alum in alumni:
        alum_profile = db.query(MemberProfile).filter(
            MemberProfile.user_id == alum.user_id
        ).first()
        
        if alum_profile and alum_profile.specializations:
            for member in members:
                # Calculate match score based on interests
                common_interests = set(member.career_interests) & set(alum_profile.specializations)
                if common_interests:
                    matches.append({
                        "alumni_id": alum.user_id,
                        "member_id": member.user_id,
                        "match_score": len(common_interests),
                        "common_interests": list(common_interests)
                    })
    
    return sorted(matches, key=lambda x: x['match_score'], reverse=True)

# API Endpoints
@app.post("/api/auth/register", response_model=UserResponse)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    # Check if user exists
    db_user = db.query(User).filter(User.email == user.email).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        email=user.email,
        password_hash=hashed_password,
        first_name=user.first_name,
        last_name=user.last_name,
        phone=user.phone
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    # Send welcome email
    send_email(
        user.email,
        "Welcome to USC TREA",
        f"<h2>Welcome {user.first_name}!</h2><p>Your account has been created. Please complete your member application.</p>"
    )
    
    return db_user

@app.post("/api/auth/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login endpoint"""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/api/applications/submit")
async def submit_application(
    application: MemberApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit member application"""
    # Check if application already exists
    existing = db.query(MemberApplication).filter(
        MemberApplication.user_id == current_user.user_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Application already submitted")
    
    # Create application
    db_application = MemberApplication(
        user_id=current_user.user_id,
        graduation_year=application.graduation_year,
        major=application.major,
        career_interests=application.career_interests,
        interest_reason=application.interest_reason,
        experience=application.experience,
        goals=application.goals
    )
    db.add(db_application)
    db.commit()
    
    # Notify admins
    admins = db.query(User).join(UserRole).filter(
        UserRole.role_name == "admin"
    ).all()
    
    for admin in admins:
        send_email(
            admin.email,
            "New Member Application",
            f"<p>New application from {current_user.first_name} {current_user.last_name}</p>"
        )
    
    return {"message": "Application submitted successfully"}

@app.post("/api/alumni/collaborate")
async def submit_collaboration(
    collaboration: AlumniCollaborationCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Submit alumni collaboration offer"""
    db_collaboration = AlumniCollaboration(
        user_id=current_user.user_id,
        company=collaboration.company,
        position=collaboration.position,
        industry=collaboration.industry,
        collaboration_type=collaboration.collaboration_type,
        collaboration_details=collaboration.collaboration_details,
        linkedin_url=collaboration.linkedin_url
    )
    db.add(db_collaboration)
    
    # Update/create profile
    profile = db.query(MemberProfile).filter(
        MemberProfile.user_id == current_user.user_id
    ).first()
    
    if profile:
        profile.specializations = collaboration.specializations
        profile.linkedin_url = collaboration.linkedin_url
    else:
        profile = MemberProfile(
            user_id=current_user.user_id,
            linkedin_url=collaboration.linkedin_url,
            experience_level="professional",
            specializations=collaboration.specializations
        )
        db.add(profile)
    
    db.commit()
    
    # Find matching members
    matches = match_alumni_to_members(db, collaboration.collaboration_type)
    
    return {
        "message": "Collaboration offer submitted",
        "potential_matches": len(matches)
    }

@app.get("/api/resources")
async def get_resources(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available resources based on user access level"""
    # Determine user's access level
    user_role = db.query(UserRole).filter(
        UserRole.user_id == current_user.user_id
    ).first()
    
    access_level = "member"  # Default
    if user_role:
        if user_role.role_name == "admin":
            access_level = "admin"
    
    # Get resources
    resources = db.query(Resource).filter(
        Resource.access_level.in_(["public", access_level])
    ).all()
    
    return resources

@app.post("/api/events/{event_id}/register")
async def register_for_event(
    event_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register for an event"""
    # Check if event exists
    event = db.query(Event).filter(Event.event_id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if already registered
    existing = db.query(EventRegistration).filter(
        EventRegistration.event_id == event_id,
        EventRegistration.user_id == current_user.user_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already registered")
    
    # Check capacity
    current_registrations = db.query(EventRegistration).filter(
        EventRegistration.event_id == event_id
    ).count()
    
    if event.max_attendees and current_registrations >= event.max_attendees:
        raise HTTPException(status_code=400, detail="Event is full")
    
    # Register
    registration = EventRegistration(
        event_id=event_id,
        user_id=current_user.user_id
    )
    db.add(registration)
    db.commit()
    
    # Send confirmation email
    send_email(
        current_user.email,
        f"Registration Confirmed: {event.title}",
        f"<p>You're registered for {event.title} on {event.event_date}</p>"
    )
    
    return {"message": "Successfully registered"}

@app.post("/api/payments/create-checkout-session")
async def create_checkout_session(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create Stripe checkout session for premium membership"""
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'USC TREA Premium Membership',
                        'description': 'Annual membership with full access to resources and events',
                    },
                    'unit_amount': 9900,  # $99.00
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://usctrea.com/success?session_id={CHECKOUT_SESSION_ID}',
            cancel_url='https://usctrea.com/cancel',
            customer_email=current_user.email,
            metadata={
                'user_id': current_user.user_id
            }
        )
        
        return {"checkout_url": checkout_session.url}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/analytics/dashboard")
async def get_analytics(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get analytics data for admin dashboard"""
    # Check admin permission
    user_role = db.query(UserRole).filter(
        UserRole.user_id == current_user.user_id,
        UserRole.role_name == "admin"
    ).first()
    
    if not user_role:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Gather analytics
    total_members = db.query(MemberApplication).filter(
        MemberApplication.application_status == "approved"
    ).count()
    
    pending_applications = db.query(MemberApplication).filter(
        MemberApplication.application_status == "pending"
    ).count()
    
    total_alumni = db.query(AlumniCollaboration).filter(
        AlumniCollaboration.is_active == True
    ).count()
    
    upcoming_events = db.query(Event).filter(
        Event.event_date > datetime.utcnow()
    ).count()
    
    # Member growth (last 30 days)
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    new_members = db.query(MemberApplication).filter(
        MemberApplication.submitted_at > thirty_days_ago,
        MemberApplication.application_status == "approved"
    ).count()
    
    return {
        "total_members": total_members,
        "pending_applications": pending_applications,
        "total_alumni": total_alumni,
        "upcoming_events": upcoming_events,
        "new_members_30d": new_members,
        "member_growth_percentage": round((new_members / max(total_members, 1)) * 100, 1)
    }

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)