"use client";
import React, { useState, useEffect } from 'react';
import { Student } from '../../types';

export default function RosterPage() {
    const [name, setName] = useState("");
    const [studentId, setStudentId] = useState("");
    const [file, setFile] = useState<File | null>(null);
    const [message, setMessage] = useState("");
    const [status, setStatus] = useState<"idle" | "success" | "error">("idle");
    const [students, setStudents] = useState<Student[]>([]);

    useEffect(() => {
        fetchStudents();
    }, []);

    const fetchStudents = async () => {
        try {
            const res = await fetch("http://localhost:8000/students/");
            if (res.ok) {
                const data = await res.json();
                setStudents(data);
            }
        } catch (err) {
            console.error("Failed to fetch students");
        }
    };

    const handleDelete = async (id: number) => {
        // Simple direct delete for now to avoid browser blocking 'confirm'
        console.log("Deleting student:", id);
        try {
            const res = await fetch(`http://localhost:8000/students/${id}`, {
                method: "DELETE"
            });
            if (res.ok) {
                fetchStudents();
            } else {
                alert("Failed to delete");
            }
        } catch (err) {
            console.error(err);
            alert("Error deleting student");
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setMessage("");
        
        if (!file || !name || !studentId) return;

        const formData = new FormData();
        formData.append("name", name);
        formData.append("student_id", studentId);
        formData.append("file", file);

        try {
            const res = await fetch("http://localhost:8000/students/", {
                method: "POST",
                body: formData
            });
            
            if (res.ok) {
                setMessage("Student added successfully to the secure roster.");
                setStatus("success");
                setName("");
                setStudentId("");
                setFile(null);
                fetchStudents();
            } else {
                const data = await res.json();
                setMessage(data.detail || "Failed to add student. Please try again.");
                setStatus("error");
            }
        } catch (err) {
            console.error(err);
            setMessage("Server connection failed. Please check if Backend is running.");
            setStatus("error");
        }
    };

    return (
        <main className="min-h-screen bg-gray-50 font-sans">
             <nav className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                     <span className="text-xl font-bold text-blue-600">CLASSROOM AI</span>
                     <a href="/" className="text-sm font-medium text-gray-500 hover:text-blue-600 transition-colors">← Back to Dashboard</a>
                </div>
            </nav>

            <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8 grid grid-cols-1 lg:grid-cols-2 gap-10">
                
                {/* Add Student Form */}
                <div className="bg-white py-8 px-10 shadow rounded-lg border border-gray-100 h-fit">
                    <div className="mb-6">
                        <h2 className="text-xl font-bold text-gray-900">Add New Student</h2>
                        <p className="text-sm text-gray-500">Register a student for automated facial recognition.</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Student Name</label>
                            <div className="mt-1">
                                <input 
                                    type="text" 
                                    value={name}
                                    onChange={e => setName(e.target.value)}
                                    className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                    required
                                />
                            </div>
                        </div>
                        
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Student ID</label>
                            <div className="mt-1">
                                <input 
                                    type="text" 
                                    value={studentId}
                                    onChange={e => setStudentId(e.target.value)}
                                    className="appearance-none block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm placeholder-gray-400 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
                                    required
                                />
                            </div>
                        </div>
                        
                        <div>
                            <label className="block text-sm font-medium text-gray-700">Reference Photo</label>
                            <div className="mt-1">
                                <input 
                                    type="file" 
                                    accept="image/*"
                                    onChange={e => e.target.files && setFile(e.target.files[0])}
                                    className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                                    required
                                />
                            </div>
                        </div>
                        
                        <div>
                            <button 
                                type="submit"
                                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                            >
                                Add to Roster
                            </button>
                        </div>
                    </form>

                    {message && (
                        <div className={`mt-4 p-3 rounded text-sm text-center ${status === 'success' ? 'bg-green-50 text-green-700' : 'bg-red-50 text-red-700'}`}>
                            {message}
                        </div>
                    )}
                </div>

                {/* Current Roster List */}
                <div className="bg-white py-8 px-6 shadow rounded-lg border border-gray-100 h-fit">
                     <div className="mb-6 flex justify-between items-center">
                        <h2 className="text-xl font-bold text-gray-900">Current Roster</h2>
                        <span className="text-sm bg-blue-100 text-blue-800 py-1 px-3 rounded-full font-medium">{students.length} Students</span>
                    </div>
                    
                    {students.length === 0 ? (
                        <p className="text-gray-500 text-center py-10">No students registered yet.</p>
                    ) : (
                        <div className="flow-root">
                            <ul role="list" className="-my-5 divide-y divide-gray-200">
                                {students.map((student) => (
                                    <li key={student.id} className="py-4">
                                        <div className="flex items-center space-x-4">
                                            <div className="flex-1 min-w-0">
                                                <p className="text-sm font-medium text-gray-900 truncate">
                                                    {student.name}
                                                </p>
                                                <p className="text-sm text-gray-500 truncate">
                                                    ID: {student.student_id}
                                                </p>
                                            </div>
                                            <div>
                                                <button
                                                    onClick={() => handleDelete(student.id)}
                                                    className="inline-flex items-center shadow-sm px-2.5 py-0.5 border border-gray-300 text-sm leading-5 font-medium rounded-full text-red-700 bg-white hover:bg-gray-50"
                                                >
                                                    Delete
                                                </button>
                                            </div>
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    )}
                </div>

            </div>
        </main>
    );
}
