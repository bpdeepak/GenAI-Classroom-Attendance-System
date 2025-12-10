import os
import json
import time
import numpy as np
from pathlib import Path
from sqlmodel import Session, select
from database import engine, create_db_and_tables
from models import Student
import ai_engine
from typing import List, Dict

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
IMAGES_DIR = BASE_DIR.parent / "images"
LABELS_FILE = BASE_DIR / "test_labels.json"
REPORT_FILE = Path("/home/deepak/.gemini/antigravity/brain/343821c5-1118-42f0-b405-e97ae5d19bed/evaluation_report.md")

def load_ground_truth():
    with open(LABELS_FILE, 'r') as f:
        return json.load(f)

def get_student_map(session: Session) -> Dict[int, str]:
    """Map DB ID (int) to Student ID (str)"""
    students = session.exec(select(Student)).all()
    return {s.id: s.student_id for s in students}

def ensure_artifacts_dir():
    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

def calculate_metrics(tp, fp, fn):
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    accuracy = tp / (tp + fp + fn) # Basic definition for object detection context
    return precision, recall, f1, accuracy

def main():
    print("Starting Evaluation...")
    ensure_artifacts_dir()
    
    # Initialize DB and Models
    create_db_and_tables()
    with Session(engine) as session:
        students = session.exec(select(Student)).all()
        print(f"Loading {len(students)} students from DB...")
        ai_engine.load_roster_embeddings(students)
        student_map = get_student_map(session)

    ground_truth = load_ground_truth()
    
    results = []
    total_latency = 0
    total_images = 0
    
    # Global counts
    total_tp = 0
    total_fp = 0
    total_fn = 0

    report_lines = []
    report_lines.append("# Evaluation Report\n")
    report_lines.append(f"**Date**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    report_lines.append("## Per-Image Analysis\n")
    report_lines.append("| Image | Latency (s) | Wanted IDs | Predicted IDs | TP | FP | FN |")
    report_lines.append("|-------|-------------|------------|---------------|----|----|----|")

    for filename, expected_ids in ground_truth.items():
        image_path = IMAGES_DIR / filename
        if not image_path.exists():
            print(f"Warning: Image {filename} not found in {IMAGES_DIR}. Skipping.")
            continue
            
        print(f"Processing {filename}...")
        
        start_time = time.time()
        # Run Inference
        try:
            recognized_int_ids, unknown_count = ai_engine.recognize_faces(str(image_path))
        except Exception as e:
            print(f"Error processing {filename}: {e}")
            continue
            
        latency = time.time() - start_time
        total_latency += latency
        total_images += 1
        
        # Convert IDs
        predicted_ids = [student_map.get(mid, f"Unknown_DB_ID_{mid}") for mid in recognized_int_ids]
        
        # Calculate Image Metrics
        expected_set = set(expected_ids)
        predicted_set = set(predicted_ids)
        
        tp = len(expected_set.intersection(predicted_set))
        fp = len(predicted_set - expected_set)
        fn = len(expected_set - predicted_set)
        
        total_tp += tp
        total_fp += fp
        total_fn += fn
        
        report_lines.append(f"| {filename} | {latency:.4f} | {', '.join(expected_ids)} | {', '.join(predicted_ids)} | {tp} | {fp} | {fn} |")

    # Aggregate Metrics
    precision, recall, f1, accuracy = calculate_metrics(total_tp, total_fp, total_fn)
    avg_latency = total_latency / total_images if total_images > 0 else 0

    print("\n--- Summary ---")
    print(f"Precision: {precision:.2%}")
    print(f"Recall:    {recall:.2%}")
    print(f"F1 Score:  {f1:.2%}")
    print(f"Avg Latency: {avg_latency:.4f}s")

    report_lines.append("\n## Aggregate Metrics\n")
    report_lines.append("| Metric | Value |")
    report_lines.append("|--------|-------|")
    report_lines.append(f"| **Precision** | {precision:.2%} |")
    report_lines.append(f"| **Recall** | {recall:.2%} |")
    report_lines.append(f"| **F1 Score** | {f1:.2%} |")
    report_lines.append(f"| **Accuracy** (TP / All) | {accuracy:.2%} |")
    report_lines.append(f"| **Average Latency** | {avg_latency:.4f}s |")
    
    # Save Report
    with open(REPORT_FILE, "w") as f:
        f.write("\n".join(report_lines))
        
    print(f"Report saved to {REPORT_FILE}")

if __name__ == "__main__":
    main()
