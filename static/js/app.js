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
    dark: { name: 'Dark', icon: 'moon' },
    light: { name: 'Light', icon: 'sun' },
    ocean: { name: 'Ocean', icon: 'waves' },
    sunset: { name: 'Sunset', icon: 'sunset' },
    forest: { name: 'Forest', icon: 'trees' }
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
        <div class="theme-switcher">
            <button class="theme-trigger" onclick="toggleThemeSwitcher()" title="Change Theme">
                <i data-lucide="palette" style="width: 20px; height: 20px;"></i>
            </button>
            
            <div id="themeSwitcherPanel" class="theme-panel hidden">
                <div class="theme-panel-header">
                    <span>Theme</span>
                    <button class="theme-close" onclick="toggleThemeSwitcher()">
                        <i data-lucide="x" style="width: 16px; height: 16px;"></i>
                    </button>
                </div>
                <div class="theme-grid">
                    ${Object.keys(themes).map(themeKey => `
                        <button class="theme-option ${state.theme === themeKey ? 'active' : ''}" onclick="changeTheme('${themeKey}')">
                            <div class="theme-preview"></div>
                            <div class="theme-info">
                                <i data-lucide="${themes[themeKey].icon}" style="width: 14px; height: 14px;"></i>
                                <span>${themes[themeKey].name}</span>
                            </div>
                            ${state.theme === themeKey ? `<div class="theme-check"><i data-lucide="check" style="width: 12px; height: 12px;"></i></div>` : ''}
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
    setTimeout(() => lucide.createIcons(), 100);
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
        if (btn) btn.style.color = 'var(--accent-primary)';
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

// Landing Page
function renderLanding() {
    app.innerHTML = `
        <div class="bg-animated">
            <div class="bg-orb bg-orb-1"></div>
            <div class="bg-orb bg-orb-2"></div>
        </div>

        <div style="min-height: 100vh; display: flex; flex-direction: column;">
            <!-- Header -->
            <header style="border-bottom: 1px solid var(--border-primary); padding: 16px 0; position: relative; z-index: 10;">
                <div style="max-width: 1280px; margin: 0 auto; padding: 0 24px; display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 12px;">
                        <div style="width: 32px; height: 32px; border-radius: 8px; background: var(--accent-gradient); display: flex; align-items: center; justify-content: center;">
                            <i data-lucide="globe" style="width: 18px; height: 18px; color: white;"></i>
                        </div>
                        <span style="font-size: 18px; font-weight: 600; letter-spacing: -0.5px;">TravelAI</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <button onclick="showAbout()" class="btn btn-ghost" style="font-size: 14px;">
                            <i data-lucide="info" style="width: 16px; height: 16px;"></i>
                            About
                        </button>
                        <button id="userMenuBtn" onclick="toggleUserMenu()" class="btn btn-ghost" style="font-size: 14px;">
                            <i data-lucide="user" style="width: 16px; height: 16px;"></i>
                            <span id="userNameDisplay">Account</span>
                        </button>
                    </div>
                </div>
                <!-- User Menu Dropdown -->
                <div id="userMenuDropdown" class="hidden" style="position: absolute; top: 56px; right: 24px; width: 200px; background: var(--bg-secondary); border: 1px solid var(--border-primary); border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,0.15); z-index: 50; overflow: hidden;">
                    <button onclick="loginWithGoogle()" style="width: 100%; text-align: left; padding: 12px 16px; border: none; background: transparent; color: var(--text-primary); cursor: pointer; display: flex; align-items: center; gap: 8px; font-size: 14px; transition: background 0.2s;">
                        <i data-lucide="log-in" style="width: 16px; height: 16px;"></i>
                        Login with Google
                    </button>
                    <button id="logoutBtn" onclick="logoutUser()" style="width: 100%; text-align: left; padding: 12px 16px; border: none; background: transparent; color: var(--text-primary); cursor: pointer; display: none; align-items: center; gap: 8px; font-size: 14px; transition: background 0.2s;">
                        <i data-lucide="log-out" style="width: 16px; height: 16px;"></i>
                        Logout
                    </button>
                </div>
            </header>

            <!-- Main Content -->
            <main style="flex: 1; display: flex; align-items: center; justify-content: center; padding: 48px 24px;">
                <div style="width: 100%; max-width: 640px; display: flex; flex-direction: column; gap: 48px;">
                    
                    <!-- Hero Section -->
                    <div style="text-align: center; display: flex; flex-direction: column; gap: 24px; animation: fadeIn 0.6s ease-out;">
                        <div style="display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 8px 16px; background: var(--bg-secondary); border: 1px solid var(--border-primary); border-radius: 6px; width: fit-content; margin: 0 auto; font-size: 13px; font-weight: 500; color: var(--text-secondary);">
                            <i data-lucide="cpu" style="width: 14px; height: 14px;"></i>
                            Powered by AI
                        </div>
                        
                        <h1 style="font-size: 56px; font-weight: 700; line-height: 1.2; letter-spacing: -1px; margin: 0;">
                            <span class="gradient-text">Plan your perfect journey</span>
                        </h1>
                        
                        <p style="font-size: 18px; color: var(--text-secondary); margin: 0; max-width: 500px; margin-left: auto; margin-right: auto; line-height: 1.6;">
                            Get AI-powered travel recommendations tailored to your style and budget
                        </p>
                    </div>

                    <!-- Search Section -->
                    <div style="display: flex; flex-direction: column; gap: 16px; animation: fadeIn 0.6s ease-out 0.1s both;">
                        <div style="position: relative;">
                            <div style="position: absolute; left: 16px; top: 50%; transform: translateY(-50%); pointer-events: none;">
                                <i data-lucide="search" style="width: 18px; height: 18px; color: var(--text-tertiary);"></i>
                            </div>
                            <input
                                type="text"
                                id="destinationInput"
                                placeholder="Where do you want to go?"
                                class="input-field"
                                style="width: 100%; padding: 14px 16px 14px 44px; font-size: 16px;"
                                onkeypress="handleSearchEnter(event)"
                                autofocus
                            />
                            <button 
                                id="micBtn"
                                onclick="toggleVoiceInput()"
                                style="position: absolute; right: 16px; top: 50%; transform: translateY(-50%); background: none; border: none; color: var(--text-tertiary); cursor: pointer; padding: 4px; transition: color 0.2s;"
                                title="Voice Search"
                            >
                                <i data-lucide="mic" style="width: 18px; height: 18px;"></i>
                            </button>
                        </div>
                        
                        <button
                            type="button"
                            onclick="handleSearch(event)"
                            class="btn btn-primary"
                            style="width: 100%; padding: 14px 24px; font-size: 16px; font-weight: 600;"
                        >
                            Generate Guide
                            <i data-lucide="arrow-right" style="width: 18px; height: 18px;"></i>
                        </button>
                    </div>

                    <!-- Popular Destinations -->
                    <div style="display: flex; flex-direction: column; gap: 12px; animation: fadeIn 0.6s ease-out 0.2s both;">
                        <p style="font-size: 13px; color: var(--text-tertiary); font-weight: 500; margin: 0;">Popular destinations</p>
                        <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                            ${['Tokyo', 'Paris', 'New York', 'Dubai', 'Bali', 'Barcelona'].map((city, i) => `
                                <button
                                    onclick="setDestination('${city}')"
                                    class="badge"
                                    style="font-size: 13px; animation: fadeIn 0.4s ease-out ${0.3 + (i * 0.05)}s both;"
                                >
                                    ${city}
                                </button>
                            `).join('')}
                        </div>
                    </div>
                </div>
            </main>

            <!-- Footer -->
            <footer style="border-top: 1px solid var(--border-primary); padding: 24px; text-align: center; color: var(--text-tertiary); font-size: 13px;">
                © 2025 TravelAI. Crafted with care.
            </footer>
        </div>

        ${renderThemeSwitcher()}
    `;
}

// Loading Page
function renderLoading() {
    app.innerHTML = `
        <div class="bg-animated">
            <div class="bg-orb bg-orb-1"></div>
            <div class="bg-orb bg-orb-2"></div>
        </div>

        <div style="min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 24px;">
            <div style="width: 100%; max-width: 500px; display: flex; flex-direction: column; gap: 32px;">
                <div style="text-align: center; display: flex; flex-direction: column; gap: 16px;">
                    <h1 style="font-size: 32px; font-weight: 700; margin: 0;">Generating your guide</h1>
                    <p style="color: var(--text-secondary); margin: 0;">Our AI agents are working on your travel plan...</p>
                </div>

                <div style="display: flex; flex-direction: column; gap: 8px;">
                    <div style="display: flex; justify-content: space-between; font-size: 13px; color: var(--text-tertiary);">
                        <span>Progress</span>
                        <span id="progressPercent">0%</span>
                    </div>
                    <div class="progress-bar">
                        <div style="width: 0%; height: 100%;"></div>
                    </div>
                </div>

                <div style="text-align: center;">
                    <p id="loadingStatus" style="color: var(--text-secondary); margin: 0; font-size: 14px;">Initializing...</p>
                </div>

                <div id="loadingSteps" style="display: flex; flex-direction: column; gap: 8px; max-height: 300px; overflow-y: auto;"></div>

                <button onclick="goBack()" class="btn btn-secondary" style="width: 100%; padding: 12px 24px;">
                    Cancel
                </button>
            </div>
        </div>

        ${renderThemeSwitcher()}
    `;
}

// Dashboard Page
function renderDashboard() {
    const data = state.data || {};
    const destination = data.destination || state.destination;
    const places = data.places?.places || [];
    const itinerary = data.itinerary?.three_days || [];
    const dishes = data.food?.must_try_dishes || [];

    app.innerHTML = `
        <div class="bg-animated">
            <div class="bg-orb bg-orb-1"></div>
            <div class="bg-orb bg-orb-2"></div>
        </div>

        <div style="min-height: 100vh;">
            <!-- Header -->
            <header style="border-bottom: 1px solid var(--border-primary); padding: 16px 0; position: sticky; top: 0; z-index: 10; background: var(--bg-primary);">
                <div style="max-width: 1280px; margin: 0 auto; padding: 0 24px; display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center; gap: 16px;">
                        <button onclick="goBack()" class="btn btn-ghost" style="padding: 8px;">
                            <i data-lucide="arrow-left" style="width: 18px; height: 18px;"></i>
                        </button>
                        <div>
                            <h1 style="font-size: 20px; font-weight: 600; margin: 0;">${destination}</h1>
                            <p style="font-size: 13px; color: var(--text-tertiary); margin: 0;">Your travel guide</p>
                        </div>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button onclick="speakText('Here is your travel guide for ${destination}')" class="btn btn-ghost" title="Read Aloud">
                            <i data-lucide="volume-2" style="width: 18px; height: 18px;"></i>
                        </button>
                        <button onclick="exportGuide('html')" class="btn btn-secondary" style="font-size: 14px;">
                            <i data-lucide="download" style="width: 16px; height: 16px;"></i>
                            Export
                        </button>
                    </div>
                </div>
            </header>

            <!-- Main Content -->
            <main style="max-width: 1280px; margin: 0 auto; padding: 48px 24px; display: flex; flex-direction: column; gap: 48px;">
                
                <!-- Places Section -->
                ${places.length > 0 ? `
                <section style="animation: fadeIn 0.6s ease-out;">
                    <div style="margin-bottom: 24px;">
                        <h2 style="font-size: 28px; font-weight: 700; margin: 0 0 8px 0;">Top Places</h2>
                        <p style="color: var(--text-secondary); margin: 0; font-size: 14px;">Must-visit destinations</p>
                    </div>
                    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 16px;">
                        ${places.slice(0, 6).map((place, i) => `
                            <div class="card" style="overflow: hidden; animation: fadeIn 0.6s ease-out ${0.1 + (i * 0.05)}s both;">
                                <div class="image-zoom" style="height: 200px;">
                                    <img src="${place.image_url}" alt="${place.name}" onerror="this.src='https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=600&h=400&fit=crop'" />
                                </div>
                                <div style="padding: 16px;">
                                    <h3 style="font-size: 16px; font-weight: 600; margin: 0 0 8px 0;">${place.name}</h3>
                                    <p style="font-size: 14px; color: var(--text-secondary); margin: 0; line-height: 1.5;">${place.description || 'A must-visit destination'}</p>
                                </div>
                            </div>
                        `).join('')}
                    </div>
                </section>
                ` : ''}

                <!-- Itinerary Section -->
                ${itinerary.length > 0 ? `
                <section style="animation: fadeIn 0.6s ease-out 0.1s both;">
                    <div style="margin-bottom: 24px;">
                        <h2 style="font-size: 28px; font-weight: 700; margin: 0 0 8px 0;">3-Day Itinerary</h2>
                        <p style="color: var(--text-secondary); margin: 0; font-size: 14px;">Your perfect travel plan</p>
                    </div>
                    <div style="display: flex; flex-direction: column; gap: 16px;">
                        ${itinerary.map((day, index) => `
                            <div class="card" style="padding: 24px; animation: fadeIn 0.6s ease-out ${0.2 + (index * 0.1)}s both;">
                                <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
                                    <div style="width: 40px; height: 40px; border-radius: 50%; background: var(--accent-gradient); display: flex; align-items: center; justify-content: center; color: white; font-weight: 600; font-size: 16px;">
                                        ${day.day || index + 1}
                                    </div>
                                    <div>
                                        <h3 style="font-size: 16px; font-weight: 600; margin: 0;">Day ${day.day || index + 1}</h3>
                                        <p style="font-size: 13px; color: var(--text-tertiary); margin: 0;">${(day.activities || []).length} activities</p>
                                    </div>
                                </div>
                                <ul style="list-style: none; padding: 0; margin: 0; display: flex; flex-direction: column; gap: 8px;">
                                    ${(day.activities || []).map(activity => `
                                        <li style="display: flex; gap: 8px; align-items: flex-start; font-size: 14px; color: var(--text-secondary);">
                                            <i data-lucide="check-circle" style="width: 16px; height: 16px; color: var(--accent-primary); flex-shrink: 0; margin-top: 2px;"></i>
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
                <section style="animation: fadeIn 0.6s ease-out 0.2s both;">
                    <div style="margin-bottom: 24px;">
                        <h2 style="font-size: 28px; font-weight: 700; margin: 0 0 8px 0;">Must-Try Dishes</h2>
                        <p style="color: var(--text-secondary); margin: 0; font-size: 14px;">Local culinary experiences</p>
                    </div>
                    <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                        ${dishes.map((dish, i) => `
                            <span class="badge" style="animation: fadeIn 0.4s ease-out ${0.3 + (i * 0.05)}s both;">
                                ${dish}
                            </span>
                        `).join('')}
                    </div>
                </section>
                ` : ''}

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
            document.getElementById('logoutBtn').style.display = 'flex';
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
        const response = await API.post('/api/export', {
            destination: state.destination,
            language: 'en'
        });
        
        if (response.status === 'success') {
            alert(`Guide exported successfully as ${format.toUpperCase()}`);
        } else {
            alert('Export failed: ' + response.message);
        }
    } catch (e) {
        alert('Export error: ' + e.message);
    }
}

function startStream(destination) {
    let completedAgents = 0;
    const totalAgents = 16;
    
    const eventSource = API.stream(
        `/api/stream?destination=${encodeURIComponent(destination)}&mother_tongue=en`,
        (data) => {
            if (data.type === 'agent_start') {
                addAgentStep(data.agent, 'working');
            } else if (data.type === 'agent_complete') {
                completedAgents++;
                updateAgentStep(data.agent, 'completed');
                updateProgress(completedAgents, totalAgents);
            } else if (data.type === 'complete') {
                eventSource.close();
                if (data.context) {
                    state.data = data.context;
                    state.view = 'dashboard';
                    renderView();
                }
            }
        },
        (error) => {
            console.error('Stream error:', error);
            alert('Connection lost. Please try again.');
            goBack();
        }
    );
}

function updateProgress(completed, total) {
    const percentage = Math.round((completed / total) * 100);
    const progressBar = document.querySelector('.progress-bar > div');
    const progressPercent = document.getElementById('progressPercent');
    
    if (progressBar) {
        progressBar.style.width = percentage + '%';
    }
    if (progressPercent) {
        progressPercent.textContent = percentage + '%';
    }
}

function addAgentStep(agentName, status) {
    const stepsEl = document.getElementById('loadingSteps');
    if (!stepsEl) return;

    const stepDiv = document.createElement('div');
    stepDiv.id = `agent-${agentName}`;
    stepDiv.style.cssText = `
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        background: var(--bg-secondary);
        border: 1px solid var(--border-primary);
        border-radius: 8px;
        border-left: 3px solid var(--accent-primary);
        animation: slideIn 0.3s ease-out;
    `;
    stepDiv.innerHTML = `
        <i data-lucide="loader-2" style="width: 16px; height: 16px; color: var(--accent-primary); animation: spin 1s linear infinite;"></i>
        <div style="flex: 1;">
            <p style="font-size: 13px; font-weight: 500; margin: 0; text-transform: capitalize;">${agentName}</p>
            <p style="font-size: 12px; color: var(--text-tertiary); margin: 0;">Processing...</p>
        </div>
    `;
    stepsEl.prepend(stepDiv);
    lucide.createIcons();
}

function updateAgentStep(agentName, status) {
    const stepDiv = document.getElementById(`agent-${agentName}`);
    if (!stepDiv) return;

    if (status === 'completed') {
        stepDiv.style.borderLeftColor = 'var(--success)';
        stepDiv.innerHTML = `
            <i data-lucide="check-circle" style="width: 16px; height: 16px; color: var(--success);"></i>
            <div style="flex: 1;">
                <p style="font-size: 13px; font-weight: 500; margin: 0; text-transform: capitalize;">${agentName}</p>
                <p style="font-size: 12px; color: var(--text-tertiary); margin: 0;">Completed</p>
            </div>
        `;
    }
    lucide.createIcons();
}

function showAbout() {
    const aboutModal = document.createElement('div');
    aboutModal.id = 'aboutModal';
    aboutModal.style.cssText = `
        position: fixed;
        inset: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 1000;
        padding: 24px;
        animation: fadeIn 0.3s ease-out;
    `;
    
    aboutModal.innerHTML = `
        <div class="card" style="max-width: 600px; max-height: 80vh; overflow-y: auto; padding: 32px; animation: scaleIn 0.3s ease-out;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 24px;">
                <h2 style="font-size: 24px; font-weight: 700; margin: 0;">About TravelAI</h2>
                <button onclick="document.getElementById('aboutModal').remove()" class="btn btn-ghost" style="padding: 4px;">
                    <i data-lucide="x" style="width: 20px; height: 20px;"></i>
                </button>
            </div>
            
            <div style="display: flex; flex-direction: column; gap: 16px; font-size: 14px; line-height: 1.6; color: var(--text-secondary);">
                <p style="margin: 0;">
                    <strong>TravelAI</strong> is a production-ready, AI-powered travel planning platform that leverages a sophisticated multi-agent architecture to generate personalized, comprehensive travel guides with real-time streaming updates.
                </p>
                
                <div>
                    <h3 style="font-size: 16px; font-weight: 600; color: var(--text-primary); margin: 0 0 8px 0;">Key Features</h3>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li>16+ specialized AI agents working in parallel</li>
                        <li>Real-time streaming updates via Server-Sent Events</li>
                        <li>Dynamic LLM support (Google Gemini, OpenRouter, NVIDIA NIM)</li>
                        <li>Voice interaction with TTS and STT</li>
                        <li>Premium UI with 5 stunning themes</li>
                        <li>Progressive Web App with offline support</li>
                        <li>Enterprise-grade security</li>
                        <li>WCAG 2.2 AA accessibility</li>
                    </ul>
                </div>
                
                <div>
                    <h3 style="font-size: 16px; font-weight: 600; color: var(--text-primary); margin: 0 0 8px 0;">Tech Stack</h3>
                    <p style="margin: 0;">
                        <strong>Backend:</strong> Python 3.11 + FastAPI + Uvicorn<br>
                        <strong>Frontend:</strong> HTML5 + Vanilla JS + Tailwind CSS<br>
                        <strong>AI/LLM:</strong> Google Gemini, OpenRouter, NVIDIA NIM<br>
                        <strong>DevOps:</strong> Docker + Docker Compose
                    </p>
                </div>
                
                <div>
                    <h3 style="font-size: 16px; font-weight: 600; color: var(--text-primary); margin: 0 0 8px 0;">Capabilities</h3>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li>Generate comprehensive travel guides</li>
                        <li>Personalized recommendations</li>
                        <li>Multi-format export (JSON, Markdown, HTML)</li>
                        <li>Advanced search and filtering</li>
                        <li>Favorites and bookmarks</li>
                        <li>Itinerary customization</li>
                        <li>Real-time analytics</li>
                    </ul>
                </div>
                
                <div style="border-top: 1px solid var(--border-primary); padding-top: 16px; margin-top: 16px;">
                    <p style="margin: 0; font-size: 12px; color: var(--text-tertiary);">
                        © 2025 TravelAI. Made with ❤️ by the TravelAI Team.<br>
                        <a href="https://github.com" style="color: var(--accent-primary); text-decoration: none;">GitHub</a> • 
                        <a href="https://docs.example.com" style="color: var(--accent-primary); text-decoration: none;">Documentation</a>
                    </p>
                </div>
            </div>
        </div>
    `;
    
    document.body.appendChild(aboutModal);
    aboutModal.addEventListener('click', (e) => {
        if (e.target === aboutModal) {
            aboutModal.remove();
        }
    });
    lucide.createIcons();
}
