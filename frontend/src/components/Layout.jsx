import React from 'react';
import { LayoutDashboard, PlusCircle, Activity, ShieldCheck, FileText, Menu } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';

const Layout = ({ children }) => {
    const location = useLocation();

    return (
        <div className="flex h-screen text-neutral-900 font-sans selection:bg-emerald-500/30">
            {/* Sidebar */}
            <aside className="w-72 glass border-r-0 flex flex-col z-20 relative">
                <div className="p-8">
                    <div className="flex items-center gap-3 mb-1">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
                            <span className="font-bold text-black text-lg">M</span>
                        </div>
                        <h1 className="text-2xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-neutral-900 to-neutral-500">
                            Manus
                        </h1>
                    </div>
                    <p className="text-xs text-neutral-500 font-medium tracking-wider pl-11 uppercase">Autonomous Agent</p>
                </div>

                <nav className="flex-1 px-4 space-y-1">
                    <NavItem to="/" icon={<PlusCircle size={20} />} label="New Mission" active={location.pathname === '/'} />
                    <NavItem to="/jobs" icon={<LayoutDashboard size={20} />} label="Active Missions" active={location.pathname.startsWith('/job')} />
                    <NavItem to="/artifacts" icon={<FileText size={20} />} label="Artifact Library" />
                    <NavItem to="/audit" icon={<ShieldCheck size={20} />} label="Security Audit" />
                    <NavItem to="/system" icon={<Activity size={20} />} label="System Health" />
                </nav>

                <div className="p-6">
                    <div className="glass-panel rounded-xl p-4 flex items-center gap-3 transition-transform hover:scale-[1.02] cursor-default">
                        <div className="w-10 h-10 rounded-full bg-gradient-to-tr from-neutral-200 to-neutral-100 flex items-center justify-center border border-black/5">
                            <span className="text-xs font-bold text-neutral-700">US</span>
                        </div>
                        <div>
                            <p className="text-sm font-semibold text-neutral-900">Local User</p>
                            <div className="flex items-center gap-1.5">
                                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                                <p className="text-xs text-neutral-500">System Online</p>
                            </div>
                        </div>
                    </div>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-auto relative">
                {/* Background Ambient Glow */}
                <div className="absolute top-0 left-0 w-full h-96 bg-emerald-500/5 blur-[120px] pointer-events-none"></div>

                <div className="relative z-10 h-full">
                    {children}
                </div>
            </main>
        </div>
    );
};

const NavItem = ({ to, icon, label, active }) => (
    <Link
        to={to}
        className={`flex items-center gap-3 px-4 py-3 rounded-xl transition-all duration-200 group ${active
                ? 'bg-black/5 text-neutral-900 shadow-sm border border-black/5'
                : 'text-neutral-500 hover:text-neutral-900 hover:bg-black/5'
            }`}
    >
        <span className={`transition-colors ${active ? 'text-emerald-400' : 'text-neutral-500 group-hover:text-emerald-400'}`}>
            {icon}
        </span>
        <span className="text-sm font-medium tracking-wide">{label}</span>
        {active && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]"></div>}
    </Link>
);

export default Layout;
