# Research & Datasets

## 1. AI Model Research
To build a robust "Gen-AI" system, we researched two distinct categories of AI models:

### 1.1 Face Recognition (The "Who")
For the core attendance tracking, we required a model capable of One-Shot Learning (identifying a person from a single reference photo).
*   **Selected Model**: `dlib` (via `face_recognition` library).
*   **Reasoning**: It uses a HOG (Histogram of Oriented Gradients) feature extractor combined with a deep ResNet to generate 128-dimensional face embeddings. It is known for high accuracy (99.38% on LFW benchmark) and low computational overhead compared to massive deep learning models.

### 1.2 Generative Analysis (The "Atmosphere")
To add the "Gen-AI" uniqueness, we researched Vision-Language Models (VLMs) for classroom scene understanding.
*   **Candidates Evaluated**: CLIP, BLIP, LLaVA, and cloud-based models (GPT-4o, Gemini 1.5).
*   **Selected Model**: **Salesforce BLIP (Bootstrapping Language-Image Pre-training)**.
*   **Reasoning**: BLIP provides an optimal balance between performance and deployment simplicity. Unlike cloud-based solutions requiring API keys and internet connectivity, BLIP runs entirely locally using the Transformers library. The base model generates contextually relevant image captions that capture classroom setting and student positioning. This approach prioritizes privacy, eliminates API costs, and removes latency concerns inherent to external service dependencies.

## 2. Dataset Exploration
Extensive training and validation require diverse datasets. We investigated several publicly available datasets to benchmark our system:

### 2.1 Face-Based Attendance Dataset (Kaggle)
*   **Description**: specifically designed for classroom surveillance. Contains labeled face images in classroom settings with varying lighting and angles.
*   **Relevance**: High. This dataset most closely mimics our deployment environment.

### 2.2 Labeled Faces in the Wild (LFW)
*   **Description**: 13,000+ images of faces collected from the web.
*   **Relevance**: Used as a benchmark for face verification accuracy. If our system can perform well on LFW-style variations, it will be robust in classrooms.

### 2.3 Tufts Face Database
*   **Description**: Images across multiple modalities (thermal, 3D).
*   **Relevance**: Useful for future work involving low-light attendance tracking.

### 2.4 Custom "Micro-Dataset" (Project Specific)
For this implementation, we utilized a custom micro-dataset provided by the user:
*   **Reference Images**: High-quality portraits of students (e.g., `Deepak_1MS22CS039.jpg`).
*   **Test Images**: Real-world classroom photos (e.g., `Classroom_001.jpg`).
This allows us to validate the "One-Shot" capabilities of our system in a specific context.
