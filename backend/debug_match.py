import face_recognition
import os

# Paths provided by user
roster_images = [
    "/home/deepak/Desktop/Gen-AI-Classroom-Attendance-System/images/Deepak_1MS22CS039.jpg",
    "/home/deepak/Desktop/Gen-AI-Classroom-Attendance-System/images/Puneeth_1MS22EC015.jpeg"
]
classroom_image = "/home/deepak/Desktop/Gen-AI-Classroom-Attendance-System/images/Classroom_001.jpg"

def run_debug():
    print("--- Debugging Face Recognition ---")
    
    known_encodings = []
    known_names = []

    # 1. Encode Roster
    print("\n1. Encoding Roster Images:")
    for img_path in roster_images:
        name = os.path.basename(img_path)
        if not os.path.exists(img_path):
            print(f"  [MISSING] {img_path}")
            continue
            
        try:
            img = face_recognition.load_image_file(img_path)
            encs = face_recognition.face_encodings(img)
            if len(encs) == 0:
                print(f"  [FAIL] No face found in {name}")
            else:
                print(f"  [OK] Encoded {name} (Faces found: {len(encs)})")
                known_encodings.append(encs[0])
                known_names.append(name)
        except Exception as e:
            print(f"  [ERROR] {name}: {e}")

    if not known_encodings:
        print("Aborting: No known faces to match against.")
        return

    # 2. Analyze Classroom
    print(f"\n2. Analyzing Classroom Image: {os.path.basename(classroom_image)}")
    if not os.path.exists(classroom_image):
        print("  [MISSING] Classroom image not found")
        return

    try:
        unknown_img = face_recognition.load_image_file(classroom_image)
        # Try default HOG first
        locs = face_recognition.face_locations(unknown_img) 
        print(f"  [INFO] Faces detected (HOG): {len(locs)}")
        
        # If 0, try CNN (Upsample)
        if len(locs) == 0:
             print("  [INFO] Retrying with upsampling=2...")
             locs = face_recognition.face_locations(unknown_img, number_of_times_to_upsample=2)
             print(f"  [INFO] Faces detected (Upsampled): {len(locs)}")

        unknown_encs = face_recognition.face_encodings(unknown_img, locs)
        
        print("\n3. Matching Results:")
        for i, unknown_enc in enumerate(unknown_encs):
            print(f"\n  Unknown Face #{i+1}:")
            # Calculate distances to ALL knowns
            distances = face_recognition.face_distance(known_encodings, unknown_enc)
            
            for name, dist in zip(known_names, distances):
                match = dist <= 0.6
                print(f"    vs {name}: Distance={dist:.4f} -> {'MATCH' if match else 'NO MATCH'}")
                
    except Exception as e:
        print(f"  [ERROR] {e}")

if __name__ == "__main__":
    run_debug()
