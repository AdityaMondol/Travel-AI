export interface User {
  id: string;
  name?: string;
  username: string;
  email: string;
  role: string;
  quota_used_usd: number;
  quota_monthly_usd: number;
}

export interface Message {
  id: string;
  text: string;
  sender: 'user' | 'agent' | 'assistant';
  timestamp: string;
  content: string;
  role: 'user' | 'assistant';
}

export interface ChatSession {
  id: string;
  session_id: string;
  title: string;
  created_at: string;
  messages: Message[];
}

export interface SystemStatus {
  agents: {
    active: number;
  };
  system: {
    cpu_percent: number;
    memory_mb: number;
  };
  cpuUsage: number;
  memoryUsage: number;
}

export interface Agent {
  id: string;
  agent_id: string;
  name: string;
  agent_type: string;
  status: 'idle' | 'running';
  state: 'idle' | 'running';
  action_count: number;
  cost_used: number;
  created_at: string;
}
