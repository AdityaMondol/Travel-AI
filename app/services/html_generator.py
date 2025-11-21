from typing import Dict, Any, List
from app.core.logger import setup_logger

logger = setup_logger(__name__)

class PremiumHTMLGenerator:
    @staticmethod
    def generate(travel_data: Dict[str, Any]) -> str:
        destination = travel_data.get("destination", "Unknown")
        mother_tongue = travel_data.get("mother_tongue", "en")
        agents_active = travel_data.get("agents_active", [])
        
        places = travel_data.get("places", {}).get("places", [])
        weather = travel_data.get("weather", {})
        budget = travel_data.get("budget", {})
        safety = travel_data.get("safety_health", {})
        food = travel_data.get("food", {})
        transport = travel_data.get("transport", {})
        learning_phrases = travel_data.get("learning_phrases", [])
        
        places_html = PremiumHTMLGenerator._generate_places(places)
        phrases_html = PremiumHTMLGenerator._generate_phrases(learning_phrases)
        agent_badges = PremiumHTMLGenerator._generate_badges(agents_active)
        
        return f"""<!DOCTYPE html>
<html lang="{mother_tongue}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{destination} - Premium Travel Guide</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://unpkg.com/lucide@latest"></script>
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700;800;900&display=swap" rel="stylesheet">
    <style>
        * {{ font-family: 'Poppins', sans-serif; }}
        
        @keyframes fadeInUp {{ from {{ opacity: 0; transform: translateY(40px); }} to {{ opacity: 1; transform: translateY(0); }} }}
        @keyframes slideInLeft {{ from {{ opacity: 0; transform: translateX(-40px); }} to {{ opacity: 1; transform: translateX(0); }} }}
        @keyframes float {{ 0%, 100% {{ transform: translateY(0px); }} 50% {{ transform: translateY(-20px); }} }}
        @keyframes glow {{ 0%, 100% {{ box-shadow: 0 0 30px rgba(139, 92, 246, 0.3); }} 50% {{ box-shadow: 0 0 60px rgba(139, 92, 246, 0.6); }} }}
        @keyframes shimmer {{ 0% {{ background-position: -1000px 0; }} 100% {{ background-position: 1000px 0; }} }}
        
        body {{ background: linear-gradient(135deg, #ffffff 0%, #f8fafc 50%, #ffffff 100%); color: #1e293b; min-height: 100vh; }}
        
        .hero {{ background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 50%, #0ea5e9 100%); position: relative; overflow: hidden; }}
        .hero::before {{ content: ''; position: absolute; inset: 0; background: radial-gradient(circle at 20% 50%, rgba(255,255,255,0.2) 0%, transparent 50%); }}
        .hero::after {{ content: ''; position: absolute; inset: 0; background: radial-gradient(circle at 80% 80%, rgba(255,255,255,0.15) 0%, transparent 50%); }}
        
        .glass {{ background: rgba(255, 255, 255, 0.8); backdrop-filter: blur(10px); border: 1px solid rgba(59, 130, 246, 0.2); box-shadow: 0 8px 32px rgba(59, 130, 246, 0.1); }}
        
        .section-title {{ font-size: 3.5rem; font-weight: 900; background: linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
        
        .card-hover {{ transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); }}
        .card-hover:hover {{ transform: translateY(-12px) scale(1.02); }}
        
        .icon-glow {{ animation: glow 3s ease-in-out infinite; }}
        
        .smooth-scroll {{ scroll-behavior: smooth; }}
    </style>
</head>
<body class="smooth-scroll">
    <nav class="sticky top-0 z-50 glass border-b border-purple-500/20">
        <div class="max-w-7xl mx-auto px-6 py-5 flex justify-between items-center">
            <div class="flex items-center gap-3">
                <div class="w-12 h-12 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center">
                    <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                    </svg>
                </div>
                <div>
                    <h1 class="text-3xl font-black bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">{destination}</h1>
                    <p class="text-xs text-purple-300">AI Travel Guide</p>
                </div>
            </div>
            <div class="flex items-center gap-2 text-purple-300 text-sm">
                <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path d="M10.5 1.5H5.75A2.25 2.25 0 003.5 3.75v12.5A2.25 2.25 0 005.75 18.5h8.5a2.25 2.25 0 002.25-2.25V9.5m-11-4h6m-6 3h6m-6 3h3"></path></svg>
                <span>Live Preview</span>
            </div>
        </div>
    </nav>
    
    <div class="hero text-white py-48 relative z-10">
        <div class="max-w-7xl mx-auto px-6 text-center relative z-20">
            <div class="inline-block mb-6 px-4 py-2 glass rounded-full">
                <span class="text-sm font-semibold text-purple-200">✨ Powered by AI Agents</span>
            </div>
            <h2 class="text-7xl md:text-8xl font-black mb-6 animate-fadeInUp">Welcome to {destination}</h2>
            <p class="text-2xl md:text-3xl opacity-95 mb-12 font-light">Discover extraordinary experiences with AI-powered insights</p>
            <div class="flex flex-wrap justify-center gap-3 mb-8">
                {agent_badges}
            </div>
        </div>
    </div>
    
    <div class="max-w-7xl mx-auto px-6 py-24">
        <div class="mb-32">
            <h2 class="section-title mb-16 text-center">Quick Overview</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div class="glass p-8 rounded-2xl card-hover group">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-purple-300 font-bold text-lg">Safety</h3>
                        <svg class="w-6 h-6 text-purple-400 group-hover:scale-125 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m7 0a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    </div>
                    <p class="text-3xl font-bold text-white">{safety.get('safety_level', 'Safe')}</p>
                </div>
                <div class="glass p-8 rounded-2xl card-hover group">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-pink-300 font-bold text-lg">Budget</h3>
                        <svg class="w-6 h-6 text-pink-400 group-hover:scale-125 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    </div>
                    <p class="text-3xl font-bold text-white">{budget.get('daily_costs', {}).get('mid_range', '$50-150')}</p>
                </div>
                <div class="glass p-8 rounded-2xl card-hover group">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-blue-300 font-bold text-lg">Weather</h3>
                        <svg class="w-6 h-6 text-blue-400 group-hover:scale-125 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.051A4.002 4.002 0 003 15z"></path></svg>
                    </div>
                    <p class="text-3xl font-bold text-white">{weather.get('temperature_range', '15-25°C')}</p>
                </div>
                <div class="glass p-8 rounded-2xl card-hover group">
                    <div class="flex items-center justify-between mb-4">
                        <h3 class="text-green-300 font-bold text-lg">Best Time</h3>
                        <svg class="w-6 h-6 text-green-400 group-hover:scale-125 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                    </div>
                    <p class="text-3xl font-bold text-white">{weather.get('best_time', 'Spring')}</p>
                </div>
            </div>
        </div>
        
        <div class="mb-32">
            <h2 class="section-title mb-16 text-center">Top Attractions</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                {places_html}
            </div>
        </div>
        
        <div class="mb-32">
            <h2 class="section-title mb-16 text-center">Essential Phrases</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {phrases_html}
            </div>
        </div>
        
        <div class="mb-32">
            <h2 class="section-title mb-16 text-center">Travel Information</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
                <div class="glass p-8 rounded-2xl">
                    <div class="flex items-center gap-3 mb-6">
                        <svg class="w-8 h-8 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4"></path></svg>
                        <h3 class="text-2xl font-bold text-purple-300">Food & Dining</h3>
                    </div>
                    <ul class="space-y-3">
                        {f''.join([f'<li class="text-gray-300 flex items-center gap-2"><svg class="w-4 h-4 text-purple-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>{dish}</li>' for dish in food.get('must_try_dishes', ['Local specialties'])[:5]])}
                    </ul>
                </div>
                <div class="glass p-8 rounded-2xl">
                    <div class="flex items-center gap-3 mb-6">
                        <svg class="w-8 h-8 text-pink-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                        <h3 class="text-2xl font-bold text-pink-300">Transportation</h3>
                    </div>
                    <ul class="space-y-3">
                        {f''.join([f'<li class="text-gray-300 flex items-center gap-2"><svg class="w-4 h-4 text-pink-400" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>{option}</li>' for option in transport.get('getting_there', ['Flight', 'Train', 'Bus'])[:5]])}
                    </ul>
                </div>
            </div>
        </div>
    </div>
    
    <footer class="glass border-t border-purple-500/20 py-12 mt-20">
        <div class="max-w-7xl mx-auto px-6 text-center">
            <p class="text-lg font-semibold text-purple-300 mb-2">Powered by {len(agents_active)} AI Agents</p>
            <p class="text-gray-400">Premium Travel Guide for {destination}</p>
        </div>
    </footer>
    
    <script>
        lucide.createIcons();
    </script>
</body>
</html>"""
    
    @staticmethod
    def _generate_places(places: List[Dict[str, Any]]) -> str:
        html = ""
        for place in places[:6]:
            rating = int(place.get('rating', 0))
            stars = "*" * min(rating, 5)
            html += f"""
            <div class="glass rounded-2xl overflow-hidden card-hover group">
                <div class="relative overflow-hidden h-64">
                    <img src="{place.get('image_url', 'https://via.placeholder.com/400x300')}" alt="{place.get('name', '')}" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500">
                    <div class="absolute inset-0 bg-gradient-to-t from-black via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                </div>
                <div class="p-6">
                    <div class="flex justify-between items-start mb-3">
                        <h3 class="text-xl font-bold text-white">{place.get('name', 'N/A')}</h3>
                        <span class="bg-purple-500/30 text-purple-200 px-3 py-1 rounded-full text-sm font-semibold">{stars}</span>
                    </div>
                    <p class="text-gray-300 text-sm mb-4">{place.get('description', 'N/A')[:100]}...</p>
                    <div class="flex justify-between text-xs text-gray-400">
                        <span> {place.get('duration', 'N/A')}</span>
                        <span> {place.get('entry_fee', 'N/A')}</span>
                    </div>
                </div>
            </div>"""
        return html
    
    @staticmethod
    def _generate_phrases(phrases: List[Dict[str, Any]]) -> str:
        html = ""
        for phrase in phrases[:6]:
            html += f"""
            <div class="glass p-6 rounded-xl border border-purple-500/30 card-hover">
                <p class="text-2xl font-bold text-purple-300 mb-3">{phrase.get('phrase', 'N/A')}</p>
                <p class="text-gray-300 mb-2"><span class="font-semibold text-purple-200">Translation:</span> {phrase.get('translation', 'N/A')}</p>
                <p class="text-sm text-gray-400"><span class="font-semibold text-purple-200">Context:</span> {phrase.get('context', 'N/A')}</p>
            </div>"""
        return html
    
    @staticmethod
    def _generate_badges(agents: List[str]) -> str:
        html = ""
        colors = ["from-purple-600 to-pink-600", "from-blue-600 to-cyan-600", "from-green-600 to-emerald-600", "from-orange-600 to-red-600"]
        for idx, agent in enumerate(agents):
            color = colors[idx % len(colors)]
            html += f'<span class="inline-flex items-center gap-2 bg-gradient-to-r {color} text-white px-4 py-2 rounded-full text-sm font-semibold shadow-lg hover:shadow-xl transition-shadow">{agent}</span>'
        return html
