from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, index=True) # Firebase uid string
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    center_name = Column(String, nullable=True)  # Anganwadi center name
    created_at = Column(DateTime, default=datetime.utcnow)

    children = relationship("Child", back_populates="worker", cascade="all, delete-orphan")

class Child(Base):
    __tablename__ = "children"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    gender = Column(String, nullable=False) # "Male", "Female"
    age_months = Column(Float, nullable=False)
    family_income = Column(String, nullable=False) # "Low", "Medium", "High"
    village = Column(String, nullable=False)
    district = Column(String, nullable=False)
    state = Column(String, nullable=False)
    worker_id = Column(String, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    worker = relationship("User", back_populates="children")
    records = relationship("HealthRecord", back_populates="child", cascade="all, delete-orphan")
    followups = relationship("FollowUp", back_populates="child", cascade="all, delete-orphan")

class HealthRecord(Base):
    __tablename__ = "health_records"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    weight_kg = Column(Float, nullable=False)
    height_cm = Column(Float, nullable=False)
    muac_cm = Column(Float, nullable=False)
    hemoglobin_gdl = Column(Float, nullable=True)
    dietary_habits = Column(String, nullable=False) # "Poor", "Adequate", "Good"
    image_path = Column(String, nullable=True)
    wasting_z = Column(Float, nullable=True)
    stunting_z = Column(Float, nullable=True)
    underweight_z = Column(Float, nullable=True)
    status = Column(String, nullable=False) # "Normal", "Mild Malnutrition", "Moderate Malnutrition", "Severe Malnutrition"
    risk_score = Column(Float, nullable=False) # 0-100
    recorded_at = Column(DateTime, default=datetime.utcnow)

    child = relationship("Child", back_populates="records")

class FollowUp(Base):
    __tablename__ = "follow_ups"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    scheduled_date = Column(Date, nullable=False)
    completed = Column(Boolean, default=False)
    notes = Column(String, nullable=True)

    child = relationship("Child", back_populates="followups")
