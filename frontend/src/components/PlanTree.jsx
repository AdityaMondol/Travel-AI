import React from 'react';
import { CheckCircle2, Circle, Clock, AlertCircle, PlayCircle } from 'lucide-react';

const PlanTree = ({ plan }) => {
    if (!plan || !plan.steps) return (
        <div className="flex flex-col items-center justify-center py-20 text-neutral-500 animate-pulse">
            <div className="w-16 h-16 rounded-full bg-white/5 flex items-center justify-center mb-4">
                <PlayCircle size={32} className="text-neutral-600" />
            </div>
            <p>Waiting for mission plan...</p>
        </div>
    );

    return (
        <div className="space-y-6 relative">
            {/* Vertical Guide Line */}
            <div className="absolute left-[19px] top-4 bottom-4 w-0.5 bg-gradient-to-b from-emerald-500/50 via-neutral-200 to-transparent"></div>

            {plan.steps.map((step, index) => (
                <div key={step.id} className="relative pl-12 group animate-fade-in" style={{ animationDelay: `${index * 0.1}s` }}>

                    {/* Status Icon */}
                    <div className="absolute left-0 top-0 bg-white p-1 rounded-full border border-neutral-200 group-hover:border-emerald-500/50 transition-colors z-10">
                        <StatusIcon status={step.status} />
                    </div>

                    {/* Card */}
                    <div className={`glass-panel rounded-xl p-5 border transition-all duration-300 ${step.status === 'in_progress'
                        ? 'border-emerald-500/30 bg-emerald-50 shadow-[0_0_20px_rgba(16,185,129,0.1)]'
                        : 'border-black/5 hover:border-black/10 hover:bg-black/5'
                        }`}>
                        <div className="flex justify-between items-start mb-3">
                            <h4 className="font-semibold text-neutral-900 capitalize text-lg tracking-tight">
                                {step.id.replace(/_/g, ' ')}
                            </h4>
                            <span className={`text-[10px] font-bold uppercase tracking-wider px-2 py-1 rounded-md border ${step.status === 'in_progress' ? 'bg-emerald-500/20 text-emerald-700 border-emerald-500/20' :
                                step.status === 'completed' ? 'bg-neutral-100 text-neutral-500 border-neutral-200' :
                                    'bg-neutral-50 text-neutral-400 border-neutral-200'
                                }`}>
                                {step.agent}
                            </span>
                        </div>

                        <p className="text-neutral-600 text-sm leading-relaxed font-light">
                            {step.instruction}
                        </p>

                        {step.result && (
                            <div className="mt-4 pt-4 border-t border-black/5">
                                <div className="flex items-start gap-2 text-sm text-emerald-700 font-mono bg-emerald-50/50 p-3 rounded-lg">
                                    <span className="mt-0.5">➜</span>
                                    <span className="break-all">{step.result.summary || "Action completed successfully."}</span>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            ))}
        </div>
    );
};

const StatusIcon = ({ status }) => {
    switch (status) {
        case 'completed':
            return <CheckCircle2 size={28} className="text-emerald-500" />;
        case 'in_progress':
            return <Clock size={28} className="text-cyan-400 animate-spin-slow" />;
        case 'failed':
            return <AlertCircle size={28} className="text-red-500" />;
        default:
            return <Circle size={28} className="text-neutral-300" />;
    }
};

export default PlanTree;
