import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ArrowRight, Sparkles, Globe, Code, Shield } from 'lucide-react';

const Submission = () => {
    const [objective, setObjective] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!objective.trim()) return;

        setLoading(true);
        try {
            const response = await axios.post('http://localhost:8000/jobs', {
                objective: objective,
                selected_agents: ["planner", "researcher", "coder", "verifier"]
            });

            const jobId = response.data.job_id;
            navigate(`/job/${jobId}`);
        } catch (error) {
            console.error("Failed to submit job:", error);
            alert("Failed to submit job. Ensure backend is running.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="max-w-5xl mx-auto py-24 px-8 h-full flex flex-col justify-center">
            <div className="mb-12 text-center animate-fade-in">
                <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium mb-6">
                    <Sparkles size={12} />
                    <span>Manus Agent System v1.0</span>
                </div>
                <h2 className="text-5xl md:text-6xl font-bold text-neutral-900 mb-6 tracking-tight leading-tight">
                    What shall we <span className="text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-cyan-400">build</span> today?
                </h2>
                <p className="text-neutral-600 text-xl max-w-2xl mx-auto leading-relaxed">
                    Describe your objective. Our autonomous agents will plan, research, code, and verify the results in real-time.
                </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-8 max-w-3xl mx-auto w-full animate-fade-in" style={{ animationDelay: '0.1s' }}>
                <div className="relative group">
                    <div className="absolute -inset-0.5 bg-gradient-to-r from-emerald-500 to-cyan-500 rounded-2xl blur opacity-20 group-hover:opacity-40 transition duration-500"></div>
                    <div className="relative glass-panel rounded-2xl p-2">
                        <textarea
                            value={objective}
                            onChange={(e) => setObjective(e.target.value)}
                            placeholder="e.g., Research the latest advancements in solid-state batteries and create a summary slide deck..."
                            className="w-full bg-transparent text-neutral-900 placeholder-neutral-400 text-lg p-6 focus:outline-none min-h-[220px] resize-none font-light"
                            autoFocus
                        />
                        <div className="flex justify-between items-center px-6 pb-4 pt-2 border-t border-black/5">
                            <div className="text-xs text-neutral-500 font-medium">
                                {objective.length} characters
                            </div>
                            <button
                                type="submit"
                                disabled={loading || !objective.trim()}
                                className="flex items-center gap-2 bg-neutral-900 text-white hover:bg-emerald-600 px-8 py-3 rounded-xl font-bold transition-all transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 shadow-lg shadow-black/10"
                            >
                                {loading ? (
                                    <span className="flex items-center gap-2">
                                        <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
                                        Processing...
                                    </span>
                                ) : (
                                    <>
                                        <span>Start Mission</span>
                                        <ArrowRight size={18} />
                                    </>
                                )}
                            </button>
                        </div>
                    </div>
                </div>
            </form>

            <div className="mt-20 grid grid-cols-1 md:grid-cols-3 gap-6 animate-fade-in" style={{ animationDelay: '0.2s' }}>
                <FeatureCard
                    icon={<Globe className="text-cyan-400" />}
                    title="Deep Research"
                    desc="Autonomous web scraping & RAG with citation tracking."
                />
                <FeatureCard
                    icon={<Code className="text-emerald-400" />}
                    title="Code Synthesis"
                    desc="TDD-based generation with local sandbox execution."
                />
                <FeatureCard
                    icon={<Shield className="text-purple-400" />}
                    title="Verification"
                    desc="Multi-step fact checking and safety policy enforcement."
                />
            </div>
        </div>
    );
};

const FeatureCard = ({ icon, title, desc }) => (
    <div className="glass-panel p-6 rounded-xl hover:bg-black/5 transition-colors group">
        <div className="w-12 h-12 rounded-lg bg-black/5 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
            {icon}
        </div>
        <h3 className="text-lg font-bold text-neutral-900 mb-2">{title}</h3>
        <p className="text-sm text-neutral-600 leading-relaxed">{desc}</p>
    </div>
);

export default Submission;
