"use client";
import React, { useState } from 'react';
import AttendanceTable from '../components/AttendanceTable';
import { AttendanceSession } from '../types';

export default function Home() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [currentSession, setCurrentSession] = useState<AttendanceSession | null>(null);
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState<string>("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setSelectedFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) return;
    setLoading(true);
    setAnalysis("");
    
    // Create optimistic session for immediate feedback
    // In a real app, we'd wait, but let's just show loading state cleanly
    const formData = new FormData();
    formData.append("file", selectedFile);

    try {
      const response = await fetch("http://localhost:8000/attendance/mark", {
        method: "POST",
        body: formData,
      });
      
      const data = await response.json();
      
      if (!response.ok) {
          throw new Error(data.detail || "Upload failed");
      }
      
      const sessionData: AttendanceSession = {
          id: data.session_id,
          created_at: new Date().toISOString(),
          classroom_image_path: "", 
          ai_analysis_report: data.analysis,
          // Backend now returns full structure matching AttendanceRecord interface
          records: data.records
      };
      
      setCurrentSession(sessionData);
      setAnalysis(data.analysis);

    } catch (error) {
      console.error(error);
      alert("Error: " + error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 text-gray-800 font-sans">
      {/* Navbar */}
      <nav className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center">
               <span className="text-xl font-bold text-blue-600 tracking-tight">CLASSROOM AI</span>
            </div>
            <div className="flex space-x-4">
                <a href="/" className="text-gray-900 border-b-2 border-blue-500 px-3 py-2 text-sm font-medium">Dashboard</a>
                <a href="/roster" className="text-gray-500 hover:text-gray-900 px-3 py-2 text-sm font-medium transition-colors">Roster</a>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="text-center mb-12">
            <h1 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
              Automated Attendance
            </h1>
            <p className="mt-3 max-w-2xl mx-auto text-xl text-gray-500 sm:mt-4">
              Upload a classroom photo to instantly identify students and analyze engagement.
            </p>
        </div>

        {/* Upload Card */}
        <div className="max-w-3xl mx-auto bg-white rounded-lg shadow-md p-6 mb-8 border border-gray-100">
            <div className="flex flex-col sm:flex-row items-center gap-4 justify-center">
                <label className="block w-full sm:w-auto">
                    <span className="sr-only">Choose profile photo</span>
                    <input 
                        type="file" 
                        accept="image/*"
                        onChange={handleFileChange}
                        className="block w-full text-sm text-slate-500
                        file:mr-4 file:py-2.5 file:px-6
                        file:rounded-full file:border-0
                        file:text-sm file:font-semibold
                        file:bg-blue-50 file:text-blue-700
                        hover:file:bg-blue-100
                        transition-colors cursor-pointer"
                    />
                </label>
                <button 
                    onClick={handleUpload}
                    disabled={!selectedFile || loading}
                    className="w-full sm:w-auto bg-blue-600 hover:bg-blue-700 text-white font-semibold py-2.5 px-8 rounded-full disabled:opacity-50 disabled:cursor-not-allowed shadow transition-all duration-200"
                >
                    {loading ? (
                        <span className="flex items-center justify-center">
                            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                            Processing...
                        </span>
                    ) : (
                        "Mark Attendance"
                    )}
                </button>
            </div>
        </div>

        {/* Results Section */}
        {analysis && (
            <div className="max-w-4xl mx-auto mb-10 animate-fade-in-up">
                <div className="bg-indigo-50 border-l-4 border-indigo-500 italic text-indigo-700 p-6 rounded-r shadow-sm">
                    <h3 className="text-lg font-bold mb-2 not-italic text-indigo-900">✨ Classroom Vibe Analysis</h3>
                    <p className="leading-relaxed">"{analysis}"</p>
                </div>
            </div>
        )}

        {currentSession && (
             <div className="max-w-5xl mx-auto bg-white shadow-lg rounded-xl overflow-hidden border border-gray-200">
                 <div className="bg-gray-50 px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                    <h2 className="text-lg font-bold text-gray-800">Session Results</h2>
                    <div className="flex gap-2">
                        {currentSession.unknown_faces_count !== undefined && currentSession.unknown_faces_count > 0 && (
                            <span className="bg-yellow-100 text-yellow-800 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wide">
                                {currentSession.unknown_faces_count} Unknown Detected
                            </span>
                        )}
                        <span className="bg-green-100 text-green-800 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wide">
                            {currentSession.records?.filter(r => r.status === 'PRESENT').length} / {currentSession.records?.length} Present
                        </span>
                    </div>
                 </div>
                 <div className="p-0">
                     <AttendanceTable records={currentSession.records || []} />
                 </div>
             </div>
        )}
      </div>
    </main>
  );
}
