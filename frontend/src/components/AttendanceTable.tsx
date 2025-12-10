import React from 'react';
import { AttendanceRecord } from '../types';

interface AttendanceTableProps {
    records: AttendanceRecord[];
}

export default function AttendanceTable({ records }: AttendanceTableProps) {
    if (!records || records.length === 0) {
        return <div className="p-8 text-center text-gray-500">No records found.</div>;
    }

    return (
        <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                    <tr>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Student Name
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            ID
                        </th>
                        <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                            Status
                        </th>
                    </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                    {records.map((record) => (
                        <tr key={record.id} className="hover:bg-gray-50 transition-colors">
                            <td className="px-6 py-4 whitespace-nowrap">
                                <div className="text-sm font-medium text-gray-900">{record.student?.name || `Student #${record.student_id}`}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                                <div className="text-sm text-gray-500">{record.student?.student_id}</div>
                            </td>
                            <td className="px-6 py-4 whitespace-nowrap">
                                <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full 
                                    ${record.status === 'PRESENT' 
                                        ? 'bg-green-100 text-green-800 border border-green-200' 
                                        : 'bg-red-100 text-red-800 border border-red-200'}`}>
                                    {record.status}
                                </span>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
}
