"""SQLModel database models"""

from typing import Optional, List
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import UniqueConstraint


class Student(SQLModel, table=True):
    """Student model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    enrollments: List["Enrollment"] = Relationship(back_populates="student")


class Activity(SQLModel, table=True):
    """Activity model"""
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    description: str
    schedule: str
    max_participants: int = Field(default=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    enrollments: List["Enrollment"] = Relationship(back_populates="activity")
    
    @property
    def participant_count(self) -> int:
        """Get number of enrolled participants"""
        return len(self.enrollments)


class Enrollment(SQLModel, table=True):
    """Enrollment model - represents a student signed up for an activity"""
    id: Optional[int] = Field(default=None, primary_key=True)
    student_id: int = Field(foreign_key="student.id")
    activity_id: int = Field(foreign_key="activity.id")
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Relationships
    student: Student = Relationship(back_populates="enrollments")
    activity: Activity = Relationship(back_populates="enrollments")
    
    __table_args__ = (
        UniqueConstraint("student_id", "activity_id", name="uq_student_activity"),
    )
