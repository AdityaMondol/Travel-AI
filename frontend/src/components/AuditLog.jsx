import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { Shield, Lock } from 'lucide-react';

const AuditLog = () => {
    const [logs, setLogs] = useState([]);

    useEffect(() => {
        // Mock data for now as backend endpoint might not be fully populated
        setLogs([
            { id: 1, timestamp: new Date().toISOString(), action: "SYSTEM_INIT", details: "System started", hash: "sha256:..." },
            { id: 2, timestamp: new Date().toISOString(), action: "POLICY_LOAD", details: "Safety policies loaded", hash: "sha256:..." },
        ]);
    }, []);

    return (
        <div className="p-10 max-w-6xl mx-auto">
            <div className="flex items-center gap-3 mb-8">
                <Shield size={32} className="text-emerald-500" />
                <div>
                    <h2 className="text-2xl font-bold text-white">Security Audit Log</h2>
                    <p className="text-neutral-400">Immutable chain-of-custody for all system actions.</p>
                </div>
            </div>

            <div className="bg-neutral-950 border border-neutral-800 rounded-xl overflow-hidden">
                <table className="w-full text-left text-sm">
                    <thead className="bg-neutral-900 text-neutral-400 font-medium">
                        <tr>
                            <th className="p-4 border-b border-neutral-800">Timestamp</th>
                            <th className="p-4 border-b border-neutral-800">Action</th>
                            <th className="p-4 border-b border-neutral-800">Details</th>
                            <th className="p-4 border-b border-neutral-800">Hash</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-neutral-800">
                        {logs.map((log) => (
                            <tr key={log.id} className="hover:bg-neutral-900/50 transition-colors">
                                <td className="p-4 text-neutral-500 font-mono">{new Date(log.timestamp).toLocaleString()}</td>
                                <td className="p-4 text-white font-medium">{log.action}</td>
                                <td className="p-4 text-neutral-400">{log.details}</td>
                                <td className="p-4 text-neutral-600 font-mono text-xs flex items-center gap-2">
                                    <Lock size={12} />
                                    {log.hash}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default AuditLog;
