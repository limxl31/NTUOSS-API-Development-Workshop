"""
Introduction to API Development (Part 2)
NTUOSS TGIFHacks #132
by Jay Gupta for NTU Open Source Society
"""

# Imports
from fastapi import FastAPI, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import List, Optional
from database import SessionLocal
from schema import DBMember
from sqlalchemy import desc, asc
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "fakehashedsecret",
        "disabled": False,
    },
    "alice": {
        "username": "alice",
        "full_name": "Alice Wonderson",
        "email": "alice@example.com",
        "hashed_password": "fakehashedsecret2",
        "disabled": True,
    },
}

# Create a FastAPI Instance
app = FastAPI()

origins = [
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.get("/items/")
async def read_items(token: str = Depends(oauth2_scheme)):
    return {"token": token}


# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# A Pydantic Member
# Data validation and settings management using python type annotations.
class Member(BaseModel):
    name: str
    school: str
    graduation_year: int
    
    class Config:
        orm_mode = True


class User(BaseModel):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None


def fake_hash_password(password: str):
    return "fakehashed" + password

class UserInDB(User):
    hashed_password: str


def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)


def fake_decode_token(token):
    # This doesn't provide any security at all
    # Check the next version
    user = get_user(fake_users_db, token)
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)):
    user = fake_decode_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user_dict = fake_users_db.get(form_data.username)
    if not user_dict:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    user = UserInDB(**user_dict)
    hashed_password = fake_hash_password(form_data.password)
    if not hashed_password == user.hashed_password:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    return {"access_token": user.username, "token_type": "bearer"}


@app.get("/users/me")
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


# Methods for interacting with the SQLite Database
# ------------------------------------------------
def get_member(db: Session, member_id: int):
    return db.query(DBMember).where(DBMember.id == member_id).first()

def get_members(db: Session, sort_by: str):
    if(sort_by == 'desc'):
        return db.query(DBMember).order_by(desc(DBMember.name)).all()
    elif(sort_by == 'asc'):
        return db.query(DBMember).order_by(asc(DBMember.name)).all()
    else:
        return db.query(DBMember).all()

def create_member(db: Session, member: Member):
    db_member = DBMember(**member.dict())
    db.add(db_member)
    db.commit()
    db.refresh(db_member)

    return db_member
# ------------------------------------------------

# API Routes
# ------------------------------------------------
@app.post('/members/', response_model=Member)
async def create_members_view(member: Member, db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)):
    db_member = create_member(db, member)
    return db_member

@app.get('/members/', response_model=List[Member])
async def get_members_view(db: Session = Depends(get_db), sort_by: Optional[str] = None):
    return get_members(db, sort_by)

@app.get('/member/{member_id}')
async def get_member_view(member_id: int, db: Session = Depends(get_db)):
    return get_member(db, member_id)
# ------------------------------------------------

# Health Check
@app.get('/healthcheck', status_code=status.HTTP_200_OK)
def perform_healthcheck():
    return {'healthcheck': 'Everything OK!'}