from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
from core.config import settings
from core.database import get_engine
from core.models import User as DBUser

router = APIRouter()

# Security configuration
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Models for Auth
class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class UserOut(UserBase):
    id: str
    is_active: bool = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# Helper functions
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
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

@router.post("/register", response_model=UserOut)
async def register(user: UserCreate):
    print(f"DEBUG: Registering user: {user.email}")
    engine = get_engine()
    existing_user = await engine.find_one(DBUser, DBUser.email == user.email)
    if existing_user:
        print(f"DEBUG: Registration failed: {user.email} already exists")
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = DBUser(
        email=user.email,
        hashed_password=hashed_password,
        is_active=True
    )
    await engine.save(db_user)
    print(f"DEBUG: User {user.email} saved successfully with ID: {db_user.id}")
    return UserOut(id=str(db_user.id), email=db_user.email, is_active=db_user.is_active)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    print(f"DEBUG: Login attempt for: {form_data.username}")
    engine = get_engine()
    user = await engine.find_one(DBUser, DBUser.email == form_data.username)
    
    if not user:
        print(f"DEBUG: Login failed: User {form_data.username} not found in DB")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    is_valid = verify_password(form_data.password, user.hashed_password)
    print(f"DEBUG: Password verification for {user.email}: {is_valid}")
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

class GoogleAuthRequest(BaseModel):
    id_token: str

@router.post("/google", response_model=Token)
async def google_auth(request: GoogleAuthRequest):
    """
    Verify Google ID token and return a Profolio JWT.
    Creates a new user if one doesn't exist.
    """
    from google.oauth2 import id_token
    from google.auth.transport import requests
    
    import time
    start_time = time.time()
    try:
        # 1. Verify the ID token (Potential bottleneck)
        print(f"DEBUG: {datetime.utcnow()} Starting Google token verification...")
        id_info = id_token.verify_oauth2_token(
            request.id_token, 
            requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )
        print(f"DEBUG: {datetime.utcnow()} Google token verified in {time.time() - start_time:.4f}s")
        
        email = id_info.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Email not provided by Google")
        
        full_name = id_info.get("name")
        
        db_start = time.time()
        engine = get_engine()
        user = await engine.find_one(DBUser, DBUser.email == email)
        print(f"DEBUG: {datetime.utcnow()} DB User lookup in {time.time() - db_start:.4f}s")
        
        if not user:
            # Create user if doesn't exist
            print(f"DEBUG: Creating new OAuth user for {email}")
            hashed_password = get_password_hash(f"oauth-user-{email}")
            user = DBUser(
                email=email,
                full_name=full_name,
                hashed_password=hashed_password,
                is_active=True
            )
            await engine.save(user)
            print(f"DEBUG: Created new OAuth user: {email}")
        
        # Issue internal token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email}, expires_delta=access_token_expires
        )
        
        print(f"DEBUG: {datetime.utcnow()} Total backend google_auth time: {time.time() - start_time:.4f}s")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except ValueError as e:
        # Invalid token
        print(f"DEBUG: Google token verification failed: {str(e)}")
        raise HTTPException(status_code=401, detail=f"Invalid Google token: {str(e)}")
    except Exception as e:
        print(f"DEBUG: Error in google_auth: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during Google auth")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    engine = get_engine()
    user = await engine.find_one(DBUser, DBUser.email == token_data.email)
    
    if user is None:
        raise credentials_exception
    return UserOut(id=str(user.id), email=user.email, is_active=user.is_active)
