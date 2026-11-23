from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class UserRegister(BaseModel):
    email: str = Field(..., pattern=r"^[^@]+@[^@]+\.[^@]+$")
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: str
    role: str = Field("STUDENT", pattern="^(ADMIN|DRIVER|STUDENT)$")
    phone: Optional[str] = None
    roll_number: Optional[str] = None       # For student
    department: Optional[str] = None        # For student
    license_number: Optional[str] = None    # For driver
    overwrite_if_exists: Optional[bool] = False

class PasswordReset(BaseModel):
    username_or_email: str
    new_password: str = Field(..., min_length=6)

class TokenReviewItem(BaseModel):
    role: str
    label: str
    email: str
    username: str
    password: str
    token: str

class UserLogin(BaseModel):
    username_or_email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    username: str
    full_name: str
    role: str
    phone: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None

Token.model_rebuild()
