from sqlmodel import Session, select
from database import engine
from models import Student
import os

with Session(engine) as session:
    students = session.exec(select(Student)).all()
    print(f"Found {len(students)} students in DB:")
    for s in students:
        print(f"ID: {s.id}, Name: {s.name}, Path: {s.face_encoding_path}")
        if s.face_encoding_path:
            exists = os.path.exists(s.face_encoding_path)
            print(f"  -> File Exists: {exists}")
