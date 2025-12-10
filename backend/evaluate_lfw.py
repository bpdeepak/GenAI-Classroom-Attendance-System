
import time
import numpy as np
import pandas as pd
from sklearn.datasets import fetch_lfw_people
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
import face_recognition
import cv2
import os

def evaluate_lfw():
    print("Fetching LFW dataset (this may take a while)...")
    # Load LFW dataset: only people with at least 20 images to ensure enough data
    lfw_people = fetch_lfw_people(min_faces_per_person=20, resize=None) # resize=None for full quality
    
    n_samples, h, w, c = lfw_people.images.shape if len(lfw_people.images.shape) == 4 else (*lfw_people.images.shape, 1)
    
    # If images are grayscale (h,w), convert to RGB for face_recognition
    images = lfw_people.images
    if len(images.shape) == 3:
        # (N, H, W) -> (N, H, W, 3)
        images_rgb = []
        for img in images:
             # Scikit-learn LFW images are float32 in [0, 1] usually, but face_rec needs uint8
             # Actually fetch_lfw_people returns float [0, 255] or [0,1] depending.
             # Let's inspect ONE image
             pass 
        # Easier: Just handle inside the loop
        
    target_names = lfw_people.target_names
    n_classes = target_names.shape[0]

    print(f"Dataset Size: {n_samples} images")
    print(f"Classes: {n_classes}")

    # Strategy:
    # For each person, take the 1st image as "Roster" (Known).
    # Take the rest as "Test" (Unknown).
    
    known_encodings = []
    known_names = []
    
    test_images = []
    test_labels = [] # True Name
    
    print("Building Roster and Test Set...")
    
    # Group indices by target ID
    from collections import defaultdict
    class_indices = defaultdict(list)
    for idx, target in enumerate(lfw_people.target):
        class_indices[target].append(idx)
        
    # Process
    roster_count = 0
    test_count = 0
    
    for target_id, indices in class_indices.items():
        name = target_names[target_id]
        
        # 1. Register first image
        roster_idx = indices[0]
        roster_img = lfw_people.images[roster_idx]
        
        # Convert to uint8 (0-255)
        if roster_img.max() <= 1.0:
            roster_img = (roster_img * 255).astype(np.uint8)
        else:
            roster_img = roster_img.astype(np.uint8)
            
        if len(roster_img.shape) == 2:
            roster_img = cv2.cvtColor(roster_img, cv2.COLOR_GRAY2RGB)
            
        encodings = face_recognition.face_encodings(roster_img)
        if len(encodings) > 0:
            known_encodings.append(encodings[0])
            known_names.append(name)
            roster_count += 1
            
            # 2. Add rest to test
            for test_idx in indices[1:]:
                test_img = lfw_people.images[test_idx]
                if test_img.max() <= 1.0:
                    test_img = (test_img * 255).astype(np.uint8)
                else:
                    test_img = test_img.astype(np.uint8)
                    
                if len(test_img.shape) == 2:
                    test_img = cv2.cvtColor(test_img, cv2.COLOR_GRAY2RGB)
                
                test_images.append(test_img)
                test_labels.append(name)
                test_count += 1
        else:
            print(f"Skipping {name} - No face found in roster image")

    print(f"Roster Size: {roster_count} people")
    print(f"Test Set Size: {test_count} images")
    
    # Run Evaluation
    print("Running Inference...")
    y_true = []
    y_pred = []
    latencies = []
    
    for i, unknown_image in enumerate(test_images):
        start_time = time.time()
        
        # Detect Face
        # We can pass locations if we assume 1 face (LFW usually is centered), 
        # but let's test the full pipeline detection
        encodings = face_recognition.face_encodings(unknown_image)
        
        predicted_name = "Unknown"
        
        if len(encodings) > 0:
            # Match
            face_encoding = encodings[0]
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.6)
            face_distances = face_recognition.face_distance(known_encodings, face_encoding)
            
            if len(matches) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    predicted_name = known_names[best_match_index]
        
        latency = time.time() - start_time
        latencies.append(latency)
        
        y_true.append(test_labels[i])
        y_pred.append(predicted_name)
        
        if i % 20 == 0:
            print(f"Processed {i}/{len(test_images)}...")
            
    # Metrics
    accuracy = accuracy_score(y_true, y_pred)
    # We use weighted average to account for class imbalance
    precision, recall, f1, _ = precision_recall_fscore_support(y_true, y_pred, average='weighted', zero_division=0)
    avg_latency = np.mean(latencies)
    
    print("\n--- LFW Evaluation Results ---")
    print(f"Accuracy:  {accuracy:.2%}")
    print(f"Precision: {precision:.2%}")
    print(f"Recall:    {recall:.2%}")
    print(f"F1 Score:  {f1:.2%}")
    print(f"Avg Latency: {avg_latency:.4f}s")
    
    # Save detailed report
    report_file = "/home/deepak/Desktop/Gen-AI-Classroom-Attendance-System/docs/lfw_evaluation_report.md"
    
    with open(report_file, "w") as f:
        f.write("# LFW Evaluation Report\n\n")
        f.write(f"**Dataset**: LFW (min_faces_per_person=20)\n")
        f.write(f"**Roster Size**: {roster_count}\n")
        f.write(f"**Test Images**: {test_count}\n\n")
        
        f.write("| Metric | Value |\n")
        f.write("|--------|-------|\n")
        f.write(f"| Accuracy | {accuracy:.2%} |\n")
        f.write(f"| Precision (Weighted) | {precision:.2%} |\n")
        f.write(f"| Recall (Weighted) | {recall:.2%} |\n")
        f.write(f"| F1 Score (Weighted) | {f1:.2%} |\n")
        f.write(f"| Avg Latency | {avg_latency:.4f}s |\n\n")
        
        f.write("## Detailed Classification Report\n")
        f.write("```\n")
        f.write(classification_report(y_true, y_pred, zero_division=0))
        f.write("\n```\n")

    print(f"Report saved to {report_file}")

if __name__ == "__main__":
    evaluate_lfw()
