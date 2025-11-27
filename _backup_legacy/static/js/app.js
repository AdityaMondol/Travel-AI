class LeonoreApp {
    constructor() {
        this.sessionId = this.generateSessionId();
        this.apiBase = '/api';
        this.currentUser = null;
        this.init();
    }
    
    generateSessionId() {
        return 'session_' + Math.random().toString(36).substr(2, 9);
    }
    
    async init() {
        this.setupEventListeners();
        await this.checkAuth();
    }
    
    setupEventListeners() {
        document.querySelectorAll('[data-action]').forEach(el => {
            el.addEventListener('click', (e) => {
                const action = el.dataset.action;
                this[action]?.call(this);
            });
        });
    }
    
    async checkAuth() {
        const token = localStorage.getItem('auth_token');
        if (!token) {
            this.showAuthModal();
        }
    }
    
    showAuthModal() {
        const modal = document.getElementById('authModal');
        if (modal) modal.classList.add('active');
    }
    
    async sendMessage(message) {
        try {
            const response = await fetch(`${this.apiBase}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    message: message
                })
            });
            
            if (!response.ok) throw new Error('Request failed');
            
            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            
            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                
                const chunk = decoder.decode(value);
                this.handleStreamChunk(chunk);
            }
        } catch (error) {
            this.showError(error.message);
        }
    }
    
    handleStreamChunk(chunk) {
        const lines = chunk.split('\n');
        lines.forEach(line => {
            if (line.startsWith('data: ')) {
                try {
                    const data = JSON.parse(line.slice(6));
                    this.updateUI(data);
                } catch (e) {
                    // Ignore parse errors
                }
            }
        });
    }
    
    updateUI(data) {
        if (data.type === 'chunk') {
            this.appendMessage(data.content, 'assistant');
        } else if (data.type === 'complete') {
            this.markMessageComplete();
        }
    }
    
    appendMessage(content, role) {
        const container = document.getElementById('chatContainer');
        if (!container) return;
        
        const message = document.createElement('div');
        message.className = `message ${role}`;
        message.textContent = content;
        container.appendChild(message);
        container.scrollTop = container.scrollHeight;
    }
    
    markMessageComplete() {
        // Mark last message as complete
    }
    
    showError(message) {
        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.style.background = '#991b1b';
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => toast.remove(), 3000);
    }
    
    async getAgentStatus() {
        try {
            const response = await fetch(`${this.apiBase}/agents`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                }
            });
            return await response.json();
        } catch (error) {
            console.error('Failed to get agent status:', error);
            return null;
        }
    }
    
    async getSystemStatus() {
        try {
            const response = await fetch(`${this.apiBase}/status`, {
                headers: {
                    'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
                }
            });
            return await response.json();
        } catch (error) {
            console.error('Failed to get system status:', error);
            return null;
        }
    }
}

const app = new LeonoreApp();
