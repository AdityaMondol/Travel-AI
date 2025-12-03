import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import axios from 'axios';
import PlanTree from '../components/PlanTree';
import { Terminal, FileText, Activity, Clock, Box } from 'lucide-react';

const JobView = () => {
    const { jobId } = useParams();
    const [job, setJob] = useState(null);
    const [logs, setLogs] = useState([]);
    const [activeTab, setActiveTab] = useState('plan');

    useEffect(() => {
        const interval = setInterval(async () => {
            try {
                const response = await axios.get(`http://localhost:8000/jobs/${jobId}`);
                setJob(response.data);
                if (response.data.logs) setLogs(response.data.logs);
            } catch (error) {
                console.error("Error fetching job:", error);
            }
        }, 2000);
        return () => clearInterval(interval);
    }, [jobId]);

    if (!job) return (
        <div className="h-full flex items-center justify-center">
            <div className="flex flex-col items-center gap-4">
                <div className="w-12 h-12 border-4 border-emerald-500/30 border-t-emerald-500 rounded-full animate-spin"></div>
                <p className="text-neutral-500 font-mono text-sm animate-pulse">Establishing uplink...</p>
            </div>
        </div>
    );

    return (
        <div className="h-full flex flex-col bg-[#fcfcfc]">
            {/* Header */}
            <header className="glass border-b border-black/5 p-6 z-10">
                <div className="flex justify-between items-start">
                    <div>
                        <div className="flex items-center gap-3 mb-1">
                            <h2 className="text-2xl font-bold text-neutral-900 tracking-tight">Mission Control</h2>
                            <span className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider border ${job.status === 'completed' ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20' :
                                job.status === 'failed' ? 'bg-red-500/10 text-red-400 border-red-500/20' :
                                    'bg-blue-500/10 text-blue-400 border-blue-500/20 animate-pulse'
                                }`}>
                                {job.status}
                            </span>
                        </div>
                        <p className="text-neutral-500 text-xs font-mono flex items-center gap-2">
                            <Box size={12} />
                            ID: {jobId}
                        </p>
                    </div>
                    <div className="text-right">
                        <p className="text-xs text-neutral-500 font-mono mb-1">ELAPSED TIME</p>
                        <p className="text-xl font-mono text-neutral-900 tabular-nums">00:02:14</p>
                    </div>
                </div>
            </header>

            {/* Tabs */}
            <div className="flex border-b border-black/5 bg-white/50 px-6 backdrop-blur-sm">
                <TabButton active={activeTab === 'plan'} onClick={() => setActiveTab('plan')} icon={<Activity size={16} />} label="Execution Plan" />
                <TabButton active={activeTab === 'logs'} onClick={() => setActiveTab('logs')} icon={<Terminal size={16} />} label="Live Terminal" />
                <TabButton active={activeTab === 'artifacts'} onClick={() => setActiveTab('artifacts')} icon={<FileText size={16} />} label="Artifacts" />
            </div>

            {/* Content */}
            <div className="flex-1 overflow-hidden relative">
                {activeTab === 'plan' && (
                    <div className="h-full overflow-auto p-8 custom-scrollbar">
                        <div className="max-w-4xl mx-auto animate-fade-in">
                            <div className="mb-10 p-6 glass-panel rounded-xl border-l-4 border-l-emerald-500">
                                <h3 className="text-xs font-bold text-emerald-400 mb-2 uppercase tracking-wider">Primary Objective</h3>
                                <p className="text-neutral-800 text-xl font-light leading-relaxed">{job.objective}</p>
                            </div>
                            <PlanTree plan={job.plan} />
                        </div>
                    </div>
                )}

                {activeTab === 'logs' && (
                    <div className="h-full overflow-auto bg-[#f5f5f5] p-6 font-mono text-xs leading-relaxed custom-scrollbar">
                        {logs.map((log, i) => (
                            <div key={i} className="mb-1.5 flex gap-3 text-neutral-500 hover:bg-black/5 p-1 rounded transition-colors">
                                <span className="text-neutral-600 shrink-0 select-none">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
                                <span className={`font-bold shrink-0 w-24 text-right ${log.agent === 'system' ? 'text-purple-400' :
                                    log.agent === 'error' ? 'text-red-400' :
                                        'text-emerald-400'
                                    }`}>{log.agent}</span>
                                <span className="text-neutral-700 break-all">{log.message}</span>
                            </div>
                        ))}
                        {logs.length === 0 && (
                            <div className="text-neutral-700 italic text-center mt-20">Waiting for agent transmission...</div>
                        )}
                        <div className="h-4"></div> {/* Spacer */}
                    </div>
                )}

                {activeTab === 'artifacts' && (
                    <div className="h-full overflow-auto p-8 custom-scrollbar">
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-fade-in">
                            {job.artifacts && job.artifacts.map((artifact, i) => (
                                <div key={artifact.id} className="glass-panel rounded-xl p-5 hover:border-emerald-500/50 transition-all cursor-pointer group hover:-translate-y-1" style={{ animationDelay: `${i * 0.1}s` }}>
                                    <div className="flex items-center justify-between mb-4">
                                        <div className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400 group-hover:bg-emerald-500 group-hover:text-black transition-colors">
                                            <FileText size={20} />
                                        </div>
                                        <span className="text-[10px] font-bold text-neutral-500 uppercase border border-black/10 px-2 py-1 rounded bg-white/50">
                                            {artifact.type}
                                        </span>
                                    </div>
                                    <h4 className="text-neutral-900 font-medium truncate mb-2 text-lg">{artifact.path.split('/').pop()}</h4>
                                    <div className="flex items-center justify-between text-xs text-neutral-500">
                                        <span>{artifact.agent}</span>
                                        <span className="group-hover:text-emerald-400 transition-colors">Download ➜</span>
                                    </div>
                                </div>
                            ))}
                            {(!job.artifacts || job.artifacts.length === 0) && (
                                <div className="col-span-full flex flex-col items-center justify-center py-32 text-neutral-600">
                                    <Box size={48} className="mb-4 opacity-20" />
                                    <p>No artifacts generated yet.</p>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

const TabButton = ({ active, onClick, icon, label }) => (
    <button
        onClick={onClick}
        className={`flex items-center gap-2 px-6 py-4 text-sm font-medium border-b-2 transition-all duration-200 ${active
            ? 'border-emerald-500 text-emerald-700 bg-emerald-50'
            : 'border-transparent text-neutral-500 hover:text-neutral-700 hover:bg-black/5'
            }`}
    >
        {icon}
        {label}
    </button>
);

export default JobView;
