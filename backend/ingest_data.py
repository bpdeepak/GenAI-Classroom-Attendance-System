
import os
import sys
# Fix path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, Session, create_db_and_tables
from models import Student
from ai_engine import register_face
from sqlmodel import select

def ingest_roster():
    create_db_and_tables()
    roster_dir = "static/roster"
    
    # Files to ingest
    files = [f for f in os.listdir(roster_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    
    with Session(engine) as session:
        for filename in files:
            # Parse filename format: Name_ID.ext
            try:
                name_part = os.path.splitext(filename)[0]
                if "_" in name_part:
                    parts = name_part.split("_")
                    name = parts[0]
                    student_id = parts[1]
                else:
                    name = name_part
                    student_id = f"UNK-{name_part}"
                
                # Check if exists
                statement = select(Student).where(Student.student_id == student_id)
                existing = session.exec(statement).first()
                
                if existing:
                    print(f"Skipping {name} ({student_id}) - Already exists")
                    continue
                
                print(f"Processing {name} ({student_id})...")
                file_path = os.path.join(roster_dir, filename)
                
                # Register face
                encoding_path = register_face(student_id, file_path)
                
                if encoding_path:
                    student = Student(name=name, student_id=student_id, face_encoding_path=encoding_path)
                    session.add(student)
                    session.commit()
                    print(f"Successfully registered {name}")
                else:
                    print(f"Failed to find face in {filename}")
                    
            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    ingest_roster()
