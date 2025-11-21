// Application State
const state = {
    view: 'landing',
    destination: '',
    data: null,
    loading: false,
    theme: localStorage.getItem('theme') || 'dark',
    user: null,
    apiConfig: window.API_CONFIG || {}
};

// DOM Reference
const app = document.getElementById('app');

// API Helper
const API = {
    async request(endpoint, options = {}) {
        const url = `${state.apiConfig.baseURL || ''}${endpoint}`;
        const defaultOptions = {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            },
            timeout: state.apiConfig.timeout || 30000
        };
        
        const config = { ...defaultOptions, ...options };
        
        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), config.timeout);
            
            const response = await fetch(url, {
                ...config,
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (!response.ok) {
                const error = await response.json().catch(() => ({ message: response.statusText }));
                throw new Error(error.message || `HTTP ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error(`API Error [${endpoint}]:`, error);
            throw error;
        }
    },
    
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    },
    
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data)
        });
    },
    
    stream(endpoint, onMessage, onError) {
        const url = `${state.apiConfig.baseURL || ''}${endpoint}`;
        const eventSource = new EventSource(url);
        
        eventSource.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                onMessage(data);
            } catch (e) {
                console.error('Stream parse error:', e);
            }
        };
        
        eventSource.onerror = (error) => {
            console.error('Stream error:', error);
            eventSource.close();
            if (onError) onError(error);
        };
        
        return eventSource;
    }
};

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
    applyTheme(state.theme);
    checkUserAuth();
    renderView();
    lucide.createIcons();
});

// Theme Management
const themes = {
    dark: {
        name: 'Dark',
        icon: 'moon',
        color: '#3b82f6',
        bgPreview: '#09090b'
    },
    light: {
        name: 'Light',
        icon: 'sun',
        color: '#3b82f6',
        bgPreview: '#ffffff'
    },
    ocean: {
        name: 'Ocean',
        icon: 'waves',
        color: '#06b6d4',
        bgPreview: '#0a1628'
    },
    sunset: {
        name: 'Sunset',
        icon: 'sunset',
        color: '#f97316',
        bgPreview: '#1a0b2e'
    },
    forest: {
        name: 'Forest',
        icon: 'trees',
        color: '#10b981',
        bgPreview: '#0f1c14'
    }
};

function applyTheme(themeName) {
    document.documentElement.setAttribute('data-theme', themeName);
    state.theme = themeName;
    localStorage.setItem('theme', themeName);
}

function toggleThemeSwitcher() {
    const switcher = document.getElementById('themeSwitcherPanel');
    if (switcher) {
        switcher.classList.toggle('hidden');
    }
}

function renderThemeSwitcher() {
    return `
        <!-- Theme Switcher Trigger -->
        <div class="theme-switcher">
            <button 
                onclick="toggleThemeSwitcher()"
                class="theme-trigger"
                title="Change Theme"
            >
                <i data-lucide="palette" class="w-5 h-5"></i>
            </button>
            
            <!-- Theme Panel -->
            <div id="themeSwitcherPanel" class="theme-panel hidden">
                <div class="theme-panel-header">
                    <span class="font-semibold">Choose Theme</span>
                    <button onclick="toggleThemeSwitcher()" class="theme-close">
                        <i data-lucide="x" class="w-4 h-4"></i>
                    </button>
                </div>
                <div class="theme-grid">
                    ${Object.keys(themes).map(themeKey => `
                        <button
                            onclick="changeTheme('${themeKey}')"
                            class="theme-option ${state.theme === themeKey ? 'active' : ''}"
                        >
                            <div class="theme-preview" style="background: ${themes[themeKey].bgPreview}">
                                <div class="theme-accent" style="background: ${themes[themeKey].color}"></div>
                            </div>
                            <div class="theme-info">
                                <i data-lucide="${themes[themeKey].icon}" class="w-4 h-4"></i>
                                <span class="text-sm font-medium">${themes[themeKey].name}</span>
                            </div>
                            ${state.theme === themeKey ? `
                                <div class="theme-check">
                                    <i data-lucide="check" class="w-3 h-3"></i>
                                </div>
                            ` : ''}
                        </button>
                    `).join('')}
                </div>
            </div>
        </div>
    `;
}

function changeTheme(themeName) {
    applyTheme(themeName);
    renderView();
    // Re-create icons after theme change
    setTimeout(() => {
        lucide.createIcons();
    }, 100);
}

// Router
function renderView() {
    switch (state.view) {
        case 'landing':
            renderLanding();
            break;
        case 'loading':
            renderLoading();
            break;
        case 'dashboard':
            renderDashboard();
            break;
        default:
            renderLanding();
    }
    lucide.createIcons();
}

// Voice Interaction
const synth = window.speechSynthesis;
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
let recognition;

if (SpeechRecognition) {
    recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        const input = document.getElementById('destinationInput');
        if (input) {
            input.value = transcript;
            handleSearch();
        }
    };

    recognition.onerror = (event) => {
        console.error('Speech recognition error', event.error);
        alert('Voice input failed. Please try again.');
    };
}

function toggleVoiceInput() {
    if (!recognition) {
        alert('Voice input is not supported in this browser.');
        return;
    }

    try {
        recognition.start();
        const btn = document.getElementById('micBtn');
        if (btn) btn.classList.add('text-[var(--accent-primary)]', 'animate-pulse');
    } catch (e) {
        recognition.stop();
    }
}

function speakText(text) {
    if (synth.speaking) {
        synth.cancel();
        return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 1;
    utterance.pitch = 1;
    synth.speak(utterance);
}

// Update renderLanding to include Mic button
function renderLanding() {
    app.innerHTML = `
        <!-- Animated Background -->
        <div class="bg-animated">
            <div class="bg-orb bg-orb-1"></div>
            <div class="bg-orb bg-orb-2"></div>
        </div>

        <div class="min-h-screen flex flex-col">
            <!-- Header -->
            <header class="border-b border-[var(--border-primary)] backdrop-blur fade-in">
                <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div class="flex items-center gap-2">
                        <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--accent-primary)] to-[var(--accent-secondary)] flex items-center justify-center">
                            <i data-lucide="sparkles" class="w-5 h-5 text-white"></i>
                        </div>
                        <span class="font-semibold text-lg">TravelAI</span>
                    </div>
                    <div class="flex items-center gap-2">
                        <button id="userMenuBtn" onclick="toggleUserMenu()" class="btn btn-ghost px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2">
                            <i data-lucide="user" class="w-4 h-4"></i>
                            <span id="userNameDisplay">Account</span>
                        </button>
                        <button class="btn btn-ghost px-4 py-2 rounded-lg text-sm font-medium">
                            About
                        </button>
                    </div>
                </div>
                <!-- User Menu Dropdown -->
                <div id="userMenuDropdown" class="hidden absolute top-16 right-6 bg-[var(--bg-secondary)] border border-[var(--border-primary)] rounded-lg shadow-lg z-50">
                    <button onclick="loginWithGoogle()" class="w-full text-left px-4 py-2 hover:bg-[var(--bg-tertiary)] flex items-center gap-2">
                        <i data-lucide="log-in" class="w-4 h-4"></i>
                        Login with Google
                    </button>
                    <button id="logoutBtn" onclick="logoutUser()" class="w-full text-left px-4 py-2 hover:bg-[var(--bg-tertiary)] flex items-center gap-2 hidden">
                        <i data-lucide="log-out" class="w-4 h-4"></i>
                        Logout
                    </button>
                </div>
            </header>

            <!-- Main Content -->
            <main class="flex-1 flex items-center justify-center px-6 py-12">
                <div class="w-full max-w-2xl space-y-8">
                    <!-- Badge -->
                    <div class="flex justify-center fade-in">
                        <span class="badge inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium">
                            <i data-lucide="sparkles" class="w-4 h-4"></i>
                            AI-Powered Travel Planning
                        </span>
                    </div>

                    <!-- Title -->
                    <div class="text-center space-y-4 fade-in" style="animation-delay: 0.1s">
                        <h1 class="text-5xl md:text-6xl font-bold gradient-text">
                            Plan your next journey
                        </h1>
                        <p class="text-xl text-[var(--text-secondary)] max-w-xl mx-auto">
                            Get personalized travel recommendations powered by advanced AI technology
                        </p>
                    </div>

                    <!-- Search Input -->
                    <div class="space-y-4 fade-in" style="animation-delay: 0.2s">
                        <div class="relative">
                            <div class="absolute left-4 top-1/2 -translate-y-1/2 pointer-events-none">
                                <i data-lucide="search" class="w-5 h-5 text-[var(--text-tertiary)]"></i>
                            </div>
                            <input
                                type="text"
                                id="destinationInput"
                                placeholder="Where do you want to go?"
                                class="input-field w-full pl-12 pr-12 py-4 rounded-xl text-lg font-medium"
                                onkeypress="handleSearchEnter(event)"
                                autofocus
                            />
                            <button 
                                id="micBtn"
                                onclick="toggleVoiceInput()"
                                class="absolute right-4 top-1/2 -translate-y-1/2 text-[var(--text-tertiary)] hover:text-[var(--accent-primary)] transition-colors"
                                title="Voice Search"
                            >
                                <i data-lucide="mic" class="w-5 h-5"></i>
                            </button>
                        </div>
                        
                        <button
                            type="button"
                            onclick="handleSearch(event)"
                            class="btn btn-primary w-full py-4 rounded-xl font-semibold text-lg flex items-center justify-center gap-2 glow"
                        >
                            Generate Itinerary
                            <i data-lucide="sparkles" class="w-5 h-5"></i>
                        </button>
                    </div>

                    <!-- Quick Suggestions -->
                    <div class="flex flex-wrap justify-center gap-2 fade-in" style="animation-delay: 0.3s">
                        <span class="text-sm text-[var(--text-tertiary)] font-medium">Popular destinations:</span>
                        ${['Tokyo', 'Paris', 'New York', 'Dubai', 'Bali', 'London'].map((city, i) => `
                            <button
                                onclick="setDestination('${city}')"
                                class="badge text-sm px-4 py-2 rounded-lg font-medium"
                                style="animation-delay: ${0.3 + (i * 0.05)}s"
                            >
                                ${city}
                            </button>
                        `).join('')}
                    </div>

                    <!-- Features -->
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 pt-8 fade-in" style="animation-delay: 0.4s">
                        ${[
            { icon: 'map-pin', title: 'Top Places', desc: 'Curated attractions' },
            { icon: 'calendar', title: 'Itineraries', desc: 'Day-by-day plans' },
            { icon: 'utensils', title: 'Local Food', desc: 'Must-try dishes' },
            { icon: 'star', title: 'Recommendations', desc: 'Personalized tips' },
            { icon: 'download', title: 'Export', desc: 'Multiple formats' },
            { icon: 'search', title: 'Search', desc: 'Find anything' }
        ].map(feature => `
                            <div class="card p-4 rounded-xl text-center">
                                <div class="inline-flex p-3 rounded-lg bg-[var(--bg-tertiary)] mb-3">
                                    <i data-lucide="${feature.icon}" class="w-5 h-5 text-[var(--accent-primary)]"></i>
                                </div>
                                <h3 class="font-semibold mb-1">${feature.title}</h3>
                                <p class="text-sm text-[var(--text-secondary)]">${feature.desc}</p>
                            </div>
                        `).join('')}
                    </div>
                </div>
            </main>

            <!-- Footer -->
            <footer class="border-t border-[var(--border-primary)] backdrop-blur fade-in">
                <div class="max-w-7xl mx-auto px-6 py-6 text-center text-sm text-[var(--text-secondary)]">
                    © 2025 TravelAI. Powered by AI • Made with ❤️
                </div>
            </footer>
        </div>

        ${renderThemeSwitcher()}
    `;
}

// Update renderDashboard to include Speak buttons
function renderDashboard() {
    const data = state.data || {};
    const destination = data.destination || state.destination;
    const places = data.places?.places || [];
    const itinerary = data.itinerary?.three_days || [];
    const dishes = data.food?.must_try_dishes || [];
    const weather = data.weather || {};
    const budget = data.budget || {};

    app.innerHTML = `
        <!-- Animated Background -->
        <div class="bg-animated">
            <div class="bg-orb bg-orb-1"></div>
            <div class="bg-orb bg-orb-2"></div>
        </div>

        <div class="min-h-screen">
            <!-- Header -->
            <header class="sticky top-0 z-50 border-b border-[var(--border-primary)] backdrop backdrop-blur fade-in">
                <div class="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
                    <div class="flex items-center gap-4">
                        <button onclick="goBack()" class="btn btn-ghost p-2 rounded-lg">
                            <i data-lucide="arrow-left" class="w-5 h-5"></i>
                        </button>
                        <div>
                            <h1 class="font-bold text-lg">${destination}</h1>
                            <p class="text-xs text-[var(--text-tertiary)]">Your Travel Guide</p>
                        </div>
                    </div>
                    <div class="flex gap-2">
                        <button onclick="speakText('Here is your travel guide for ${destination}')" class="btn btn-ghost p-2 rounded-lg" title="Read Aloud">
                            <i data-lucide="volume-2" class="w-5 h-5"></i>
                        </button>
                        <a href="${data.filename || '#'}" download class="btn btn-secondary px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2">
                            <i data-lucide="download" class="w-4 h-4"></i>
                            Export
                        </a>
                    </div>
                </div>
            </header>

            <!-- Main Content -->
            <main class="max-w-7xl mx-auto px-6 py-8 space-y-10">
                
                <!-- Hero Stats -->
                <section class="fade-in">
                    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                        ${[
            { icon: 'thermometer', label: 'Climate', value: weather.current_season || 'Moderate', gradient: true },
            { icon: 'banknote', label: 'Currency', value: budget.local_currency || 'N/A' },
            { icon: 'shield-check', label: 'Safety', value: data.safety_health?.safety_level || 'Good' }
        ].map((stat, i) => `
                            <div class="card ${stat.gradient ? 'card-gradient' : ''} p-6 rounded-xl slide-in" style="animation-delay: ${i * 0.1}s">
                                <div class="flex items-center gap-3 mb-3">
                                    <i data-lucide="${stat.icon}" class="w-6 h-6 ${stat.gradient ? 'text-white' : 'text-[var(--accent-primary)]'}"></i>
                                    <span class="text-sm ${stat.gradient ? 'text-white/80' : 'text-[var(--text-secondary)]'} font-medium">${stat.label}</span>
                                </div>
                                <p class="text-2xl font-bold ${stat.gradient ? 'text-white' : ''}">${stat.value}</p>
                            </div>
                        `).join('')}
                    </div>
                </section>

                <!-- Places Section -->
                ${places.length > 0 ? `
                <section class="fade-in" style="animation-delay: 0.2s">
                    <div class="flex items-end justify-between mb-6">
                        <div>
                            <h2 class="text-3xl font-bold mb-1">Top Places</h2>
                            <p class="text-[var(--text-secondary)]">Must-visit destinations</p>
                        </div>
                        <div class="badge px-4 py-2 rounded-lg">
                            ${places.length} locations
                        </div>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                        ${places.slice(0, 6).map((place, i) => `
                            <div class="card rounded-xl overflow-hidden scale-in" style="animation-delay: ${0.3 + (i * 0.05)}s">
                                <div class="aspect-video overflow-hidden bg-[var(--bg-tertiary)] image-zoom">
                                    <img
                                        src="${place.image_url}"
                                        alt="${place.name}"
                                        class="w-full h-full object-cover"
                                        onerror="this.src='https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=600&h=400&fit=crop'"
                                    />
                                </div>
                                <div class="p-5">
                                    <h3 class="font-semibold text-lg mb-2">${place.name}</h3>
                                    <p class="text-sm text-[var(--text-secondary)] line-clamp-2">${place.description || 'A must-visit destination in ' + destination}</p>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </section>
                ` : ''}

                <!-- Itinerary Section -->
                ${itinerary.length > 0 ? `
                <section class="fade-in" style="animation-delay: 0.4s">
                    <div class="mb-6">
                        <h2 class="text-3xl font-bold mb-1">3-Day Itinerary</h2>
                        <p class="text-[var(--text-secondary)]">Your perfect travel plan</p>
                    </div>
                    <div class="space-y-4">
                        ${itinerary.map((day, index) => `
                            <div class="card p-6 rounded-xl slide-in" style="animation-delay: ${0.5 + (index * 0.1)}s">
                                <div class="flex items-center gap-4 mb-4">
                                    <div class="w-12 h-12 rounded-full bg-gradient-to-br from-[var(--accent-primary)] to-[var(--accent-secondary)] flex items-center justify-center text-lg font-bold text-white">
                                        ${day.day || index + 1}
                                    </div>
                                    <div>
                                        <h3 class="font-bold text-lg">Day ${day.day || index + 1}</h3>
                                        <p class="text-sm text-[var(--text-secondary)]">${(day.activities || []).length} activities planned</p>
                                    </div>
                                </div>
                                <ul class="space-y-3">
                                    ${(day.activities || []).map(activity => `
                                        <li class="flex gap-3 text-[var(--text-secondary)]">
                                            <i data-lucide="check-circle" class="w-5 h-5 text-[var(--success)] flex-shrink-0 mt-0.5"></i>
                                            <span>${activity}</span>
                                        </li>
                                    `).join('')}
                                </ul>
                            </div>
                        `).join('')}
                    </div>
                </section>
                ` : ''}

                <!-- Food Section -->
                ${dishes.length > 0 ? `
                <section class="fade-in" style="animation-delay: 0.6s">
                    <div class="mb-6">
                        <h2 class="text-3xl font-bold mb-1">Must-Try Dishes</h2>
                        <p class="text-[var(--text-secondary)]">Local culinary experiences</p>
                    </div>
                    <div class="flex flex-wrap gap-3">
                        ${dishes.map((dish, i) => `
                            <span class="card px-5 py-3 rounded-lg font-medium scale-in" style="animation-delay: ${0.7 + (i * 0.05)}s">
                                ${dish}
                            </span>
                        `).join('')}
                    </div>
                </section>
                ` : ''}

                <!-- Export Section -->
                <section class="fade-in" style="animation-delay: 0.8s">
                    <div class="mb-6">
                        <h2 class="text-3xl font-bold mb-1">Export Your Guide</h2>
                        <p class="text-[var(--text-secondary)]">Download in your preferred format</p>
                    </div>
                    <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
                        ${[
                            { format: 'json', icon: 'file-json', label: 'JSON' },
                            { format: 'markdown', icon: 'file-text', label: 'Markdown' },
                            { format: 'html', icon: 'file-code', label: 'HTML' },
                            { format: 'pdf', icon: 'file-pdf', label: 'PDF' }
                        ].map((fmt, i) => `
                            <button onclick="exportGuide('${fmt.format}')" class="card p-4 rounded-xl text-center hover:bg-[var(--accent-primary)] hover:text-white transition-all scale-in" style="animation-delay: ${0.9 + (i * 0.05)}s">
                                <i data-lucide="${fmt.icon}" class="w-8 h-8 mx-auto mb-2"></i>
                                <p class="font-semibold">${fmt.label}</p>
                            </button>
                        `).join('')}
                    </div>
                </section>

            </main>
        </div>

        ${renderThemeSwitcher()}
    `;
}

// Event Handlers
function handleSearchEnter(event) {
    if (event.key === 'Enter') {
        handleSearch();
    }
}

// API Call & SSE
function startStream(destination) {
    const eventSource = new EventSource(`/api/stream?destination=${encodeURIComponent(destination)}&mother_tongue=en`);
    const stepsEl = document.getElementById('loadingSteps');
    const statusEl = document.getElementById('loadingStatus');
    const progressBar = document.querySelector('.progress-bar > div');

    // Reset steps
    if (stepsEl) stepsEl.innerHTML = '';
    let completedAgents = 0;
    const totalAgents = 16; // Approx total agents

    eventSource.onmessage = function (event) {
        const data = JSON.parse(event.data);

        if (data.type === 'start') {
            if (statusEl) statusEl.textContent = 'Initializing AI Agent Army...';
        } else if (data.type === 'agent_start') {
            if (statusEl) statusEl.textContent = `Agent ${data.agent} is working...`;
            addAgentStep(data.agent, 'working');
        } else if (data.type === 'agent_complete') {
            updateAgentStep(data.agent, 'completed');
            completedAgents++;
            if (progressBar) {
                progressBar.style.width = `${(completedAgents / totalAgents) * 100}%`;
            }
        } else if (data.type === 'agent_error') {
            updateAgentStep(data.agent, 'error');
        } else if (data.type === 'complete') {
            eventSource.close();

            // Store the context data and transition to dashboard
            if (data.context) {
                state.data = data.context;
                state.view = 'dashboard';
                renderView();
            } else {
                // Fallback: if no context, display error
                alert('Data processing completed but no results received.');
                goBack();
            }
        }
    };

    eventSource.onerror = function (error) {
        console.error('EventSource failed:', error);
        eventSource.close();
        alert('Connection lost. Please try again.');
        goBack();
    };
}

function addAgentStep(agentName, status) {
    const stepsEl = document.getElementById('loadingSteps');
    if (!stepsEl) return;

    const stepDiv = document.createElement('div');
    stepDiv.id = `agent-${agentName}`;
    stepDiv.className = 'flex items-center gap-3 p-4 card rounded-lg slide-in border-l-4 border-[var(--accent-primary)]';
    stepDiv.innerHTML = `
        <i data-lucide="loader-2" class="w-5 h-5 text-[var(--accent-primary)] spinner"></i>
        <div class="flex-1">
            <h4 class="font-semibold text-sm capitalize">${agentName} Agent</h4>
            <p class="text-xs text-[var(--text-secondary)]">Analyzing data...</p>
        </div>
    `;
    stepsEl.prepend(stepDiv); // Add to top
    lucide.createIcons();
}

function updateAgentStep(agentName, status) {
    const stepDiv = document.getElementById(`agent-${agentName}`);
    if (!stepDiv) return;

    if (status === 'completed') {
        stepDiv.className = 'flex items-center gap-3 p-4 card rounded-lg border-l-4 border-[var(--success)]';
        stepDiv.innerHTML = `
            <i data-lucide="check-circle" class="w-5 h-5 text-[var(--success)]"></i>
            <div class="flex-1">
                <h4 class="font-semibold text-sm capitalize">${agentName} Agent</h4>
                <p class="text-xs text-[var(--text-secondary)]">Task completed</p>
            </div>
        `;
    } else if (status === 'error') {
        stepDiv.className = 'flex items-center gap-3 p-4 card rounded-lg border-l-4 border-red-500';
        stepDiv.innerHTML = `
            <i data-lucide="alert-circle" class="w-5 h-5 text-red-500"></i>
            <div class="flex-1">
                <h4 class="font-semibold text-sm capitalize">${agentName} Agent</h4>
                <p class="text-xs text-[var(--text-secondary)]">Task failed</p>
            </div>
        `;
    }
    lucide.createIcons();
}

function handleSearch(event) {
    if (event) event.preventDefault();

    const input = document.getElementById('destinationInput');
    const destination = input?.value.trim();

    if (!destination) {
        input?.focus();
        return;
    }

    state.destination = destination;
    state.view = 'loading';
    renderView();
    startStream(destination);
}

function setDestination(city) {
    const input = document.getElementById('destinationInput');
    if (input) {
        input.value = city;
        handleSearch();
    }
}

function goBack() {
    state.view = 'landing';
    state.data = null;
    renderView();
}

function toggleUserMenu() {
    const dropdown = document.getElementById('userMenuDropdown');
    if (dropdown) {
        dropdown.classList.toggle('hidden');
    }
}

function loginWithGoogle() {
    window.location.href = '/auth/login';
}

function logoutUser() {
    window.location.href = '/auth/logout';
}

async function checkUserAuth() {
    try {
        const response = await fetch('/auth/user');
        const user = await response.json();
        if (user.authenticated && user.name) {
            document.getElementById('userNameDisplay').textContent = user.name;
            document.getElementById('logoutBtn').classList.remove('hidden');
        }
    } catch (e) {
        console.log('User not authenticated');
    }
}

async function exportGuide(format) {
    if (!state.data) {
        alert('No guide data available');
        return;
    }
    
    try {
        const response = await fetch('/api/export', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                destination: state.destination,
                language: 'en'
            })
        });
        
        const result = await response.json();
        if (result.status === 'success') {
            alert(`Guide exported successfully as ${format.toUpperCase()}`);
        } else {
            alert('Export failed: ' + result.message);
        }
    } catch (e) {
        alert('Export error: ' + e.message);
    }
}

async function getRecommendations() {
    if (!state.destination) return;
    
    try {
        const response = await fetch(`/api/recommendations?destination=${encodeURIComponent(state.destination)}`);
        const result = await response.json();
        if (result.status === 'success') {
            console.log('Recommendations:', result.recommendations);
            alert('Recommendations loaded! Check console for details.');
        }
    } catch (e) {
        console.error('Recommendations error:', e);
    }
}

async function searchPlaces(query) {
    if (!state.destination) return;
    
    try {
        const response = await fetch(`/api/search?destination=${encodeURIComponent(state.destination)}&query=${encodeURIComponent(query)}`);
        const result = await response.json();
        if (result.status === 'success') {
            console.log('Search results:', result.results);
            return result.results;
        }
    } catch (e) {
        console.error('Search error:', e);
    }
}

function renderLoading() {
    app.innerHTML = `
        <div class="min-h-screen flex flex-col items-center justify-center px-6">
            <div class="max-w-2xl w-full space-y-8">
                <!-- Loading Header -->
                <div class="text-center space-y-4">
                    <h1 class="text-4xl font-bold gradient-text">Generating Your Guide</h1>
                    <p class="text-[var(--text-secondary)]">Our AI Agent Army is working on your travel plan...</p>
                </div>

                <!-- Progress Bar -->
                <div class="space-y-2">
                    <div class="flex justify-between text-sm">
                        <span class="text-[var(--text-secondary)]">Progress</span>
                        <span id="progressPercent" class="text-[var(--accent-primary)]">0%</span>
                    </div>
                    <div class="progress-bar h-2 rounded-full bg-[var(--bg-tertiary)] overflow-hidden">
                        <div class="h-full bg-gradient-to-r from-[var(--accent-primary)] to-[var(--accent-secondary)] w-0 transition-all duration-300"></div>
                    </div>
                </div>

                <!-- Status -->
                <div class="text-center">
                    <p id="loadingStatus" class="text-[var(--text-secondary)] font-medium">Initializing...</p>
                </div>

                <!-- Agent Steps -->
                <div id="loadingSteps" class="space-y-3 max-h-96 overflow-y-auto">
                    <!-- Agents will be added here -->
                </div>

                <!-- Cancel Button -->
                <div class="flex justify-center">
                    <button onclick="goBack()" class="btn btn-secondary px-6 py-2 rounded-lg font-medium">
                        Cancel
                    </button>
                </div>
            </div>
        </div>
    `;
}
