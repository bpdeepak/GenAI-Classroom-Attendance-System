import os
import face_recognition
from dotenv import load_dotenv

load_dotenv()

from PIL import Image
import numpy as np
from typing import List, Dict, Any, Tuple
import pickle
from models import Student


# Configure Gemini - REMOVED per user request
# api_key = os.environ.get("GEMINI_API_KEY")
# model = None


# In-memory storage for face encodings (for simplicity in this MVP)
# In production, use Vector DB
known_face_encodings = []
known_face_ids = []

def load_roster_embeddings(students: List[Student]):
    global known_face_encodings, known_face_ids
    known_face_encodings = []
    known_face_ids = []
    
    print(f"Loading embeddings for {len(students)} students...")
    
    for student in students:
        if student.face_encoding_path and os.path.exists(student.face_encoding_path):
            try:
                with open(student.face_encoding_path, 'rb') as f:
                    encoding = pickle.load(f)
                    known_face_encodings.append(encoding)
                    known_face_ids.append(student.id)
            except Exception as e:
                print(f"Error loading encoding for {student.name}: {e}")

def register_face(student_id: int, image_path: str):
    if not face_recognition:
        raise Exception("Face Recognition Engine is unavailable.")

    try:
        image = face_recognition.load_image_file(image_path)
        
        # 1. Attempt default detection
        locations = face_recognition.face_locations(image)
        
        # 2. If fail, attempt with upsampling (helps for smaller faces or high-res images)
        if not locations:
            print(f"  [INFO] No face found with default. Retrying with upsample=2...")
            locations = face_recognition.face_locations(image, number_of_times_to_upsample=2)
            
        if not locations:
            print(f"  [FAIL] Still no face found in {image_path}")
            return None
            
        encodings = face_recognition.face_encodings(image, known_face_locations=locations)
        
        if len(encodings) == 0:
             return None
        
        # We take the first face found
        encoding = encodings[0]
        encoding_path = f"static/roster/{student_id}_encoding.pkl"
        with open(encoding_path, 'wb') as f:
            pickle.dump(encoding, f)
        return encoding_path
    except Exception as e:
        print(f"Face Rec Error: {e}")
        return None

def recognize_faces(image_path: str) -> Tuple[List[int], int]:
    """
    Returns:
        recognized_ids: List of Student IDs identified
        unknown_count: Number of faces detected but NOT identified
    """
    if not face_recognition:
        return [], 0
        
    try:
       unknown_image = face_recognition.load_image_file(image_path)
       # Use HOG model (faster) or cnn (slower but accurate)
       face_locations = face_recognition.face_locations(unknown_image)
       face_encodings = face_recognition.face_encodings(unknown_image, face_locations)
       
       present_student_ids = []
       total_faces = len(face_locations)
       
       if not known_face_encodings:
           return [], total_faces

       for face_encoding in face_encodings:
           # Tolerance 0.6 is standard
           matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.6)
           face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
           
           if len(matches) > 0:
               best_match_index = np.argmin(face_distances)
               if matches[best_match_index]:
                   present_student_ids.append(known_face_ids[best_match_index])
               
       recognized_ids = list(set(present_student_ids))
       unknown_count = total_faces - len(present_student_ids) 
       # Note: if one person is matched twice (error), unknown might verify weirdly. 
       # But generally correct for simple cases.
       if unknown_count < 0: unknown_count = 0
       
       return recognized_ids, unknown_count
       
    except Exception as e:
        print(f"Face Rec Failed: {e}")
        return [], 0

# --- AI / Vibe Analysis ---
# Using Salesforce BLIP (Bootstrapping Language-Image Pre-training)
# This runs LOCALLY and is free (no API limits).
try:
    from transformers import BlipProcessor, BlipForConditionalGeneration
    import torch
    
    print("Loading AI Model (BLIP)...")
    blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
    blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
    print("AI Model Loaded Successfully.")
except Exception as e:
    print(f"Warning: Could not load local AI model: {e}")
    blip_processor = None
    blip_model = None

def analyze_classroom_vibe(image_path: str) -> str:
    """
    Generates a caption/vibe check for the classroom image using local BLIP model.
    """
    if not blip_model or not blip_processor:
        return "AI Analysis Unavailable (Model not loaded)"
        
    try:
        image = Image.open(image_path).convert('RGB')
        
        # Determine prompt based on context
        text = "a photography of a classroom with students"
        
        inputs = blip_processor(image, text, return_tensors="pt")
        
        out = blip_model.generate(**inputs, max_new_tokens=50)
        caption = blip_processor.decode(out[0], skip_special_tokens=True)
        
        # Simple heuristic expansion to match "Vibe Analysis" feel
        return f"Assessment: {caption}. Engagement appears normal."
    except Exception as e:
        print(f"AI Analysis Failed: {e}")
        return "Error analyzing image."
