from sqlmodel import Session, select
from database import engine
from models import Student, AttendanceRecord
from ai_engine import register_face

# Map of student_id -> source image path provided by user
source_map = {
    "1MS22CS039": "/home/deepak/Desktop/Gen-AI-Classroom-Attendance-System/images/Deepak_1MS22CS039.jpg",
    "1MS22EC015": "/home/deepak/Desktop/Gen-AI-Classroom-Attendance-System/images/Puneeth_1MS22EC015.jpeg"
}

def upgrade_roster():
    with Session(engine) as session:
        students = session.exec(select(Student)).all()
        print(f"Checking {len(students)} students...")
        
        for student in students:
            if student.student_id in source_map:
                src_path = source_map[student.student_id]
                print(f"Upgrading {student.name} ({student.student_id})...")
                
                # Try to register REAL face
                # Note: register_face uses the image at src_path to generate encoding
                new_encoding_path = register_face(student.id, src_path)
                
                if new_encoding_path:
                    print(f"  [SUCCESS] New encoding: {new_encoding_path}")
                    student.face_encoding_path = new_encoding_path
                    session.add(student)
                else:
                    print(f"  [FAIL] No face found in {src_path}. Removing student.")
                    # Delete association records first
                    records = session.exec(select(AttendanceRecord).where(AttendanceRecord.student_id == student.id)).all()
                    for r in records:
                        session.delete(r)
                    session.delete(student)
            else:
                print(f"Skipping {student.name} (No source image known)")
        
        session.commit()
        print("Roster upgrade complete.")

if __name__ == "__main__":
    upgrade_roster()
