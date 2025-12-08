# System Architecture

## 3.1 Overview
The system follows a modern Tiered Architecture, decoupling the user interface from the processing logic to ensure scalability and maintainability.

## 3.2 Component Details

### 3.2.1 Frontend (The Presentation Layer)
*   **Technology**: Next.js 14, React, Typescript.
*   **Styling**: TailwindCSS.
*   **Role**:
    *   Serves the Dashboard UI to the user.
    *   Handles Image Uploads via standard HTTP POST requests.
    *   Displays real-time analysis results (JSON) in a human-readable format.
    *   Adheres to a "Classic Professional" design system (White/Blue/Gray).

### 3.2.2 Backend (The Logic Layer)
*   **Technology**: Python 3.12, FastAPI, Uvicorn.
*   **Role**:
    *   **API Gateway**: Exposes endpoints (`/attendance/mark`, `/students/`) for the frontend.
    *   **Logic Unit**: Orchestrates the flow between the Database, Face Recognition Engine, and Gemini AI.
    *   **Data Access Object (DAO)**: Uses SQLModel to interact with the SQLite database.

### 3.2.3 The AI Engine (The Intelligence Layer)
This is the core differentiator of the system.
*   **Module**: `ai_engine.py`.
*   **Workflow**:
    1.  **Face Registration**: Converts an uploaded reference photo into a serialized 128-dimensional NumPy array stored in the file system.
    2.  **Face Recognition**: Detects faces in the target image → Computes encodings → Calculates Euclidean distance to known faces → Returns matches with a tolerance of 0.6.
    3.  **Atmosphere Analysis**: Loads the classroom image → Processes with BLIP processor → Generates caption using locally-hosted Salesforce BLIP model → Returns contextual description of the classroom scene.

### 3.2.4 Database (The Persistence Layer)
*   **Technology**: SQLite (for MVP context).
*   **Schema**:
    *   `Student`: Stores ID, Name, and Reference Path.
    *   `AttendanceSession`: Stores timestamp, image path, and AI report.
    *   `AttendanceRecord`: Links Students to Sessions with a status (Present/Absent).

## 3.3 Data Flow Diagram
[User] -> (Upload Photo) -> [Frontend] -> (API Request) -> [Backend]
                                                            |
                                      +---------------------+---------------------+
                                      |                     |                     |
                                [Face Rec Engine]     [BLIP Model]          [Database]
                                      |                     |                     |
                                (Identify IDs)      (Generate Caption)    (Store Results)
