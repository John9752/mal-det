from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# ── Auth Schemas ──────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    full_name: str
    email: str
    password: str
    center_name: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class UserSync(BaseModel):
    uid: str
    email: str
    full_name: str
    center_name: Optional[str] = None

class UserResponse(BaseModel):
    id: str
    full_name: str
    email: str
    center_name: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# ── Child Schemas ─────────────────────────────────────────────────────────────

class ChildBase(BaseModel):
    name: str
    gender: str
    age_months: float
    family_income: str
    village: str
    district: str
    state: str

class ChildCreate(ChildBase):
    pass

class ChildResponse(ChildBase):
    id: int
    worker_id: str
    created_at: datetime

    class Config:
        from_attributes = True

# ── Health Record Schemas ─────────────────────────────────────────────────────

class HealthRecordBase(BaseModel):
    weight_kg: float
    height_cm: float
    muac_cm: float
    hemoglobin_gdl: Optional[float] = None
    dietary_habits: str

class HealthRecordCreate(HealthRecordBase):
    pass

class HealthRecordResponse(HealthRecordBase):
    id: int
    child_id: int
    image_path: Optional[str] = None
    wasting_z: Optional[float] = None
    stunting_z: Optional[float] = None
    underweight_z: Optional[float] = None
    status: str
    risk_score: float
    recorded_at: datetime

    class Config:
        from_attributes = True

# ── Follow-Up Schemas ─────────────────────────────────────────────────────────

class FollowUpBase(BaseModel):
    scheduled_date: datetime
    completed: bool = False
    notes: Optional[str] = None

class FollowUpResponse(FollowUpBase):
    id: int
    child_id: int

    class Config:
        from_attributes = True

class ChildDetailResponse(ChildResponse):
    records: List[HealthRecordResponse] = []
    followups: List[FollowUpResponse] = []

    class Config:
        from_attributes = True
