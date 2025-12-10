export interface Student {
    id: number;
    name: string;
    student_id: string;
    face_encoding_path?: string;
}

export interface AttendanceRecord {
    id: number;
    student_id: number;
    status: "PRESENT" | "ABSENT";
    confidence: number;
    student: Student;
}

export interface AttendanceSession {
    id: number;
    created_at: string;
    classroom_image_path: string;
    ai_analysis_report?: string;
    unknown_faces_count?: number;
    records?: AttendanceRecord[];
}
