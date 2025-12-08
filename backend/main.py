from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select
from typing import List
import shutil
import os
from contextlib import asynccontextmanager
from database import create_db_and_tables, get_session
from models import Student, AttendanceSession, AttendanceRecord
from ai_engine import register_face, recognize_faces, analyze_classroom_vibe, load_roster_embeddings

# Lifespan header removed as on_startup is used below


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # In production, set to specific domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files to serve images clearly
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    # Initial load
    from database import engine
    with Session(engine) as session:
        students = session.exec(select(Student)).all()
        load_roster_embeddings(students)

@app.get("/")
def read_root():
    return {"message": "Gen-AI Classroom Attendance System API"}

@app.post("/students/")
async def create_student(
    name: str = Form(...),
    student_id: str = Form(...),
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    # Check if exists
    existing_student = session.exec(select(Student).where(Student.student_id == student_id)).first()
    if existing_student:
        raise HTTPException(status_code=400, detail="Student ID already exists")

    # Save Image
    file_path = f"static/roster/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Process Face Encoding
    try:
        encoding_path = register_face(student_id, file_path)
    except Exception as e:
         raise HTTPException(status_code=400, detail=f"Error processing face: {str(e)}")

    if not encoding_path:
        raise HTTPException(status_code=400, detail="No face found in image")

    student = Student(name=name, student_id=student_id, face_encoding_path=encoding_path)
    session.add(student)
    session.commit()
    session.refresh(student)
    
    # Reload embeddings
    students = session.exec(select(Student)).all()
    load_roster_embeddings(students)
    
    return student

@app.post("/attendance/mark")
async def mark_attendance(
    file: UploadFile = File(...),
    session: Session = Depends(get_session)
):
    # Save Classroom Image
    file_path = f"static/uploads/{file.filename}"
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
        
    # 1. Recognize Faces
    present_student_ids, unknown_count = recognize_faces(file_path)
    
    # 2. Analyze Vibe
    analysis = analyze_classroom_vibe(file_path)
    
    # 3. Save Session
    att_session = AttendanceSession(classroom_image_path=file_path, ai_analysis_report=analysis)
    session.add(att_session)
    session.commit()
    session.refresh(att_session)
    
    # 4. Create Records
    all_students = session.exec(select(Student)).all()
    records = []
    
    records_to_return = []
    
    for student in all_students:
        status = "PRESENT" if student.id in present_student_ids else "ABSENT"
        record = AttendanceRecord(
            session_id=att_session.id,
            student_id=student.id,
            status=status
        )
        session.add(record)
        # We delay appending to header response list until we have IDs
        
    session.commit() 
    
    # Re-fetch or iterate to get IDs. 
    # Since we need to return the specific list we just made, let's query them by session_id
    saved_records = session.exec(select(AttendanceRecord).where(AttendanceRecord.session_id == att_session.id)).all()
    
    # Map back to shape
    for record in saved_records:
        # We need the student name, so we can access record.student (lazy load) or map manually
        records_to_return.append({
            "id": record.id,
            "student_id": record.student_id,
            "status": record.status,
            "confidence": 1.0,
            "student": {
                "id": record.student.id,
                "name": record.student.name,
                "student_id": record.student.student_id
            }
        })
    
    return {
        "session_id": att_session.id,
        "present_count": len(present_student_ids),
        "total_students": len(all_students),
        "unknown_faces_count": unknown_count,
        "analysis": analysis,
        "records": records_to_return
    }

@app.get("/sessions/")
def get_sessions(session: Session = Depends(get_session)):
    sessions = session.exec(select(AttendanceSession)).all()
    return sessions

@app.get("/sessions/{session_id}")
def get_session_details(session_id: int, session: Session = Depends(get_session)):
    att_session = session.get(AttendanceSession, session_id)
    if not att_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return att_session

@app.get("/students/")
def get_students(session: Session = Depends(get_session)):
    return session.exec(select(Student)).all()

@app.delete("/students/{student_id}")
def delete_student(student_id: int, session: Session = Depends(get_session)):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Remove files if they exist
    if student.face_encoding_path and os.path.exists(student.face_encoding_path):
        os.remove(student.face_encoding_path)
    
    # Delete associated attendance records first (Manual Cascade)
    # This prevents IntegrityError because student_id is NOT NULL
    records = session.exec(select(AttendanceRecord).where(AttendanceRecord.student_id == student_id)).all()
    for record in records:
        session.delete(record)
        
    session.delete(student)
    session.commit()
    
    # Reload embeddings
    students = session.exec(select(Student)).all()
    load_roster_embeddings(students)
    
    return {"ok": True}
