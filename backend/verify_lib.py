import sys
try:
    import face_recognition_models
    print(f"Models found: {face_recognition_models.__file__}")
    import face_recognition
    print("face_recognition imported successfully")
except Exception as e:
    print(f"Error: {e}")
except SystemExit:
    print("SystemExit caught - library tried to quit")
