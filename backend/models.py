from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    student_id: str = Field(unique=True, index=True)
    face_encoding_path: Optional[str] = None
    
    attendance_records: List["AttendanceRecord"] = Relationship(back_populates="student")

class AttendanceSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    classroom_image_path: str
    ai_analysis_report: Optional[str] = Field(default=None, description="Gen-AI analysis of the classroom")
    
    records: List["AttendanceRecord"] = Relationship(back_populates="session")

class AttendanceRecord(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="attendancesession.id")
    student_id: int = Field(foreign_key="student.id")
    status: str = Field(default="PRESENT") # PRESENT, ABSENT
    confidence: float = Field(default=0.0)
    
    session: AttendanceSession = Relationship(back_populates="records")
    student: Student = Relationship(back_populates="attendance_records")
