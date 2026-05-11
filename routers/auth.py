# Handles user authentication, registration, JWT token creation, and login pages.
import os

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel
from passlib.context import CryptContext
from ..database import SessionLocal
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from ..models import User
from jose import jwt, JWTError
from datetime import timedelta, datetime, timezone
from fastapi.templating import Jinja2Templates

router = APIRouter(
    prefix = "/auth",
    tags = ["Authentication"]
)
# Connects FastAPI with HTML templates.
templates = Jinja2Templates(directory="templates")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"

# Creates a database session for each request and closes it afterwards.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency for database access.
db_dependency = Annotated[Session, Depends(get_db)]
# Password hashing configuration using bcrypt.
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
# Defines the token endpoint used by OAuth2.
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")

# Request model for creating a new user.
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str

# Response model for access tokens.
class Token(BaseModel):
    access_token: str
    token_type: str

# Creates a JWT access token for the authenticated user.
def create_access_token(username: str, user_id:int, role:str,expires_delta:timedelta):
    encode = {'sub':username, 'id':user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode. update({'exp':expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

# Checks whether the username and password are valid.
def authenticate_user(username: str, password: str, db):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password,user.hashed_password): #match ediyor mu etmiyor mu diye bakarız
        return False
    return user

# Decodes the JWT token and returns the current user's information.
async def get_current_user(token:Annotated[str,Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")
        user_role = payload.get("role")
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Username or ID is invalid")
        return {"username": username, "id":user_id, "role":user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Token is invalid")

# Renders the login page.
@router.get("/login-page")
def render_login_page(request:Request):
    return templates.TemplateResponse("login.html",{"request":request})

# Renders the registration page.
@router.get("/register-page")
def render_register_page(request:Request):
    return templates.TemplateResponse("register.html",{"request":request})

# Creates a new user and stores the hashed password in the database.
@router.post("/",status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user_request: CreateUserRequest):
    user = User(
        username = create_user_request.username,
        email = create_user_request.email,
        first_name = create_user_request.first_name,
        last_name = create_user_request.last_name,
        role = create_user_request.role,
        is_active = True,
        hashed_password = bcrypt_context.hash(create_user_request.password),
        phone_number = create_user_request.phone_number
    )
    db.add(user)
    db.commit()

# Authenticates the user and returns a JWT access token.
@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db:db_dependency):

    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail = "Incorrect username or password")
    token = create_access_token(user.username, user.id, user.role,timedelta(minutes=60))
    return {"access_token":token, "token_type":"bearer"}
