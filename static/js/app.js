class LeonoreAI {
    constructor() {
        this.sessionId = this.generateId();
        this.messages = [];
        this.agents = new Map();
        this.isDark = true;
        this.isStreaming = false;
        this.init();
    }

    generateId() {
        return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    }

    init() {
        this.chatContainer = document.getElementById('chatContainer');
        this.messageInput = document.getElementById('messageInput');
        this.sendBtn = document.getElementById('sendBtn');
        this.agentList = document.getElementById('agentList');
        this.thoughtStream = document.getElementById('thoughtStream');
        this.thoughtPanel = document.getElementById('thoughtPanel');
        this.fileInput = document.getElementById('fileInput');

        this.sendBtn.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        document.getElementById('themeToggle').addEventListener('click', () => this.toggleTheme());
        document.getElementById('voiceBtn').addEventListener('click', () => this.startVoiceInput());
        document.getElementById('newChat').addEventListener('click', () => this.newChat());
        document.getElementById('fileBtn').addEventListener('click', () => this.fileInput.click());
        this.fileInput.addEventListener('change', (e) => this.handleFileUpload(e.target.files));

        this.addMessage('system', '🚀 Leonore AI initialized. Multi-agent system ready.');
        this.loadAgentStatus();
        setInterval(() => this.loadAgentStatus(), 10000);
    }

    async sendMessage() {
        const text = this.messageInput.value.trim();
        if (!text || this.isStreaming) return;

        this.addMessage('user', text);
        this.messageInput.value = '';
        this.messageInput.disabled = true;
        this.sendBtn.disabled = true;
        this.isStreaming = true;
        this.thoughtPanel.classList.remove('hidden');

        let assistantDiv = null;
        let fullText = '';

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: this.sessionId,
                    message: text
                })
            });

            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let buffer = '';

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;

                buffer += decoder.decode(value, { stream: true });
                const lines = buffer.split('\n\n');
                buffer = lines.pop();

                for (const line of lines) {
                    if (!line.startsWith('data: ')) continue;
                    
                    try {
                        const data = JSON.parse(line.slice(6));
                        
                        switch (data.type) {
                            case 'start':
                                this.addThought('System', 'Processing request...');
                                break;
                            
                            case 'agent_start':
                                this.updateAgentStatus(data.data.agent, 'active');
                                this.addThought(data.data.agent, 'Started working');
                                break;
                            
                            case 'agent_thought':
                                this.addThought(data.data.agent, data.data.thought);
                                break;
                            
                            case 'agent_complete':
                                this.updateAgentStatus(data.data.agent, 'idle');
                                this.addThought(data.data.agent, '✓ Completed');
                                break;
                            
                            case 'chunk':
                                if (!assistantDiv) {
                                    assistantDiv = this.addMessage('assistant', '', true);
                                }
                                fullText += data.data;
                                this.updateMessage(assistantDiv, fullText);
                                break;
                            
                            case 'complete':
                                if (!assistantDiv) {
                                    const result = data.data.synthesis || data.data.result || 'Task completed';
                                    this.addMessage('assistant', result);
                                } else {
                                    this.finalizeMessage(assistantDiv, fullText);
                                }
                                this.addThought('System', '✓ Response complete');
                                break;
                            
                            case 'error':
                                this.addMessage('error', `Error: ${data.data.error || data.error || 'Unknown error'}`);
                                break;
                        }
                    } catch (e) {
                        console.error('Parse error:', e, line);
                    }
                }
            }
        } catch (error) {
            console.error('Stream error:', error);
            this.addMessage('error', `Connection error: ${error.message}`);
        } finally {
            this.isStreaming = false;
            this.messageInput.disabled = false;
            this.sendBtn.disabled = false;
            this.messageInput.focus();
        }
    }

    addMessage(role, content, isStreaming = false) {
        const div = document.createElement('div');
        div.className = `chat-message p-4 rounded-lg ${
            role === 'user' ? 'bg-blue-600 ml-auto max-w-2xl' :
            role === 'assistant' ? 'bg-gray-800 max-w-4xl' :
            role === 'system' ? 'bg-gray-700 text-center text-sm max-w-xl mx-auto' :
            'bg-red-900 max-w-2xl'
        }`;

        if (role === 'assistant') {
            const contentDiv = document.createElement('div');
            contentDiv.className = 'markdown-body';
            if (isStreaming) {
                contentDiv.dataset.raw = content;
                contentDiv.innerHTML = this.renderMarkdown(content);
            } else {
                contentDiv.innerHTML = this.renderMarkdown(content);
            }
            div.appendChild(contentDiv);
        } else {
            div.textContent = content;
        }

        this.chatContainer.appendChild(div);
        this.scrollToBottom();
        return div;
    }

    updateMessage(div, text) {
        const contentDiv = div.querySelector('.markdown-body');
        if (contentDiv) {
            contentDiv.dataset.raw = text;
            contentDiv.innerHTML = this.renderMarkdown(text);
            this.scrollToBottom();
        }
    }

    finalizeMessage(div, text) {
        const contentDiv = div.querySelector('.markdown-body');
        if (contentDiv) {
            contentDiv.innerHTML = this.renderMarkdown(text);
            delete contentDiv.dataset.raw;
        }
    }

    renderMarkdown(text) {
        try {
            return marked.parse(text || '');
        } catch (e) {
            return text || '';
        }
    }

    addThought(agent, thought) {
        const div = document.createElement('div');
        div.className = 'p-3 bg-gray-700 rounded-lg text-sm border-l-4 border-blue-500';
        
        const agentSpan = document.createElement('div');
        agentSpan.className = 'font-semibold text-blue-400 mb-1';
        agentSpan.textContent = agent;
        
        const thoughtSpan = document.createElement('div');
        thoughtSpan.className = 'text-gray-300';
        thoughtSpan.textContent = thought;
        
        div.appendChild(agentSpan);
        div.appendChild(thoughtSpan);
        
        this.thoughtStream.appendChild(div);
        this.thoughtStream.scrollTop = this.thoughtStream.scrollHeight;

        if (this.thoughtStream.children.length > 50) {
            this.thoughtStream.removeChild(this.thoughtStream.firstChild);
        }
    }

    updateAgentStatus(agentName, status) {
        if (!this.agents.has(agentName)) {
            const agentDiv = document.createElement('div');
            agentDiv.className = 'p-3 bg-gray-700 rounded-lg';
            agentDiv.dataset.agent = agentName;
            
            agentDiv.innerHTML = `
                <div class="flex items-center justify-between">
                    <span class="font-medium">${agentName}</span>
                    <span class="status-indicator w-2 h-2 rounded-full bg-gray-500"></span>
                </div>
                <div class="text-xs text-gray-400 mt-1">Idle</div>
            `;
            
            this.agentList.appendChild(agentDiv);
            this.agents.set(agentName, agentDiv);
        }

        const agentDiv = this.agents.get(agentName);
        const indicator = agentDiv.querySelector('.status-indicator');
        const statusText = agentDiv.querySelector('.text-xs');

        if (status === 'active') {
            indicator.className = 'status-indicator w-2 h-2 rounded-full bg-green-500 agent-pulse';
            statusText.textContent = 'Active';
        } else {
            indicator.className = 'status-indicator w-2 h-2 rounded-full bg-gray-500';
            statusText.textContent = 'Idle';
        }
    }

    async loadAgentStatus() {
        try {
            const response = await fetch('/api/agents');
            const data = await response.json();
            
            if (data.agent_pool) {
                Object.entries(data.agent_pool).forEach(([role, agent]) => {
                    this.updateAgentStatus(agent.name || role, agent.state === 'executing' ? 'active' : 'idle');
                });
            }
        } catch (e) {
            console.error('Failed to load agent status:', e);
        }
    }

    scrollToBottom() {
        this.chatContainer.scrollTop = this.chatContainer.scrollHeight;
    }

    toggleTheme() {
        this.isDark = !this.isDark;
        document.body.classList.toggle('bg-gray-900', this.isDark);
        document.body.classList.toggle('bg-white', !this.isDark);
        document.body.classList.toggle('text-gray-100', this.isDark);
        document.body.classList.toggle('text-gray-900', !this.isDark);
        
        const icon = document.getElementById('themeToggle');
        icon.textContent = this.isDark ? '🌙' : '☀️';
    }

    startVoiceInput() {
        if (!('webkitSpeechRecognition' in window)) {
            this.addMessage('error', 'Voice input not supported in this browser');
            return;
        }

        const recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'en-US';

        recognition.onstart = () => {
            document.getElementById('voiceBtn').textContent = '🔴';
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            this.messageInput.value = transcript;
            document.getElementById('voiceBtn').textContent = '🎤';
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
            document.getElementById('voiceBtn').textContent = '🎤';
        };

        recognition.onend = () => {
            document.getElementById('voiceBtn').textContent = '🎤';
        };

        recognition.start();
    }

    async handleFileUpload(files) {
        for (const file of files) {
            const formData = new FormData();
            formData.append('file', file);
            formData.append('session_id', this.sessionId);

            this.addMessage('system', `📎 Uploading ${file.name}...`);

            try {
                const response = await fetch('/api/upload', {
                    method: 'POST',
                    body: formData
                });

                const data = await response.json();
                
                if (data.status === 'success') {
                    this.addMessage('system', `✓ Uploaded ${file.name} (${this.formatBytes(data.size)})`);
                } else {
                    this.addMessage('error', `Failed to upload ${file.name}`);
                }
            } catch (error) {
                this.addMessage('error', `Upload error: ${error.message}`);
            }
        }
        
        this.fileInput.value = '';
    }

    formatBytes(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    newChat() {
        if (confirm('Start a new chat? Current conversation will be saved.')) {
            this.sessionId = this.generateId();
            this.messages = [];
            this.chatContainer.innerHTML = '';
            this.thoughtStream.innerHTML = '';
            this.thoughtPanel.classList.add('hidden');
            this.addMessage('system', '🚀 New chat started');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.leonoreApp = new LeonoreAI();
});
