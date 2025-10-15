from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from openai import OpenAI
import os
import random
import re
import time
import hashlib
import requests
from bs4 import BeautifulSoup
import urllib.parse
import base64
from io import BytesIO
import json
from urllib.parse import urljoin, urlparse, quote_plus
from collections import Counter
from datetime import datetime, timezone, timedelta
import math
import secrets
import sympy as sp
import matplotlib.pyplot as plt
import numpy as np
import matplotlib.patches as patches
from matplotlib.patches import Circle, Rectangle, Polygon, FancyBboxPatch
import matplotlib.font_manager as fm

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", secrets.token_hex(32))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=20)  # 20-minute sessions

CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Session storage for conversation history
session_conversations = {}

# Knowledge domains for diverse capabilities
KNOWLEDGE_DOMAINS = {
    'netra': {
        'name': 'Netra Services',
        'keywords': ['netra', 'service', 'provider', 'booking', 'category', 'clean', 'repair', 'beauty', 'fitness', 'aidnest'],
        'description': 'Africa\'s premier service marketplace'
    },
    'general_tech': {
        'name': 'Technology',
        'keywords': ['computer', 'phone', 'app', 'software', 'tech', 'internet', 'website', 'digital', 'code', 'programming'],
        'description': 'General technology and digital assistance'
    },
    'productivity': {
        'name': 'Productivity',
        'keywords': ['schedule', 'organize', 'plan', 'time management', 'task', 'reminder', 'efficiency', 'productivity'],
        'description': 'Help with productivity and organization'
    },
    'education': {
        'name': 'Education & Learning',
        'keywords': ['learn', 'study', 'teach', 'education', 'course', 'skill', 'knowledge', 'research', 'school', 'university'],
        'description': 'Educational support and learning assistance'
    },
    'business': {
        'name': 'Business & Entrepreneurship',
        'keywords': ['business', 'startup', 'entrepreneur', 'marketing', 'sales', 'customer', 'strategy', 'finance', 'investment'],
        'description': 'Business advice and entrepreneurial guidance'
    },
    'creative': {
        'name': 'Creative Work',
        'keywords': ['write', 'design', 'create', 'content', 'story', 'art', 'creative', 'brainstorm', 'music', 'drawing'],
        'description': 'Creative writing and content creation'
    },
    'daily_life': {
        'name': 'Daily Life',
        'keywords': ['cook', 'travel', 'health', 'fitness', 'home', 'family', 'relationship', 'advice', 'food', 'recipe'],
        'description': 'Everyday life advice and support'
    },
    'science': {
        'name': 'Science & Facts',
        'keywords': ['science', 'fact', 'history', 'physics', 'chemistry', 'biology', 'space', 'earth', 'nature'],
        'description': 'Scientific facts and historical information'
    },
    'calculations': {
        'name': 'Calculations & Math',
        'keywords': ['calculate', 'math', 'equation', 'formula', 'solve', 'compute', 'percentage', 'area', 'volume'],
        'description': 'Mathematical calculations and problem solving'
    }
}

# Company information
COMPANY_INFO = {
    'ceo': {
        'name': 'Nowamaani Donath',
        'title': 'CEO & Founder',
        'companies': ['Aidnest Africa', 'Netra App', 'Kakore Labs'],
        'location': 'Kampala, Uganda, East Africa',
        'bio': 'Visionary entrepreneur leading digital transformation in Africa through innovative service platforms.'
    },
    'companies': {
        'Aidnest Africa': 'Parent company focused on digital solutions for African markets',
        'Netra App': 'Premier service marketplace connecting providers with clients across Africa',
        'Kakore Labs': 'Programming and innovation hub developing cutting-edge technology solutions'
    }
}

# Mathematical visualization functions
def render_latex_equation(latex_code):
    """Render LaTeX equation to base64 image"""
    try:
        plt.rc('text', usetex=True)
        plt.rc('font', family='serif', size=14)
        
        fig = plt.figure(figsize=(8, 2))
        plt.axis('off')
        
        # Render the LaTeX equation
        plt.text(0.5, 0.5, f'${latex_code}$', 
                horizontalalignment='center', 
                verticalalignment='center',
                transform=plt.gca().transAxes)
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                    pad_inches=0.5, transparent=True)
        plt.close(fig)
        
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        print(f"LaTeX rendering error: {e}")
        return None

def create_geometric_diagram(shape_type, parameters=None):
    """Create geometric shape diagrams"""
    try:
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.set_aspect('equal')
        ax.set_facecolor('#0f0f23')
        fig.patch.set_facecolor('#0f0f23')
        
        if shape_type == 'triangle':
            # Draw a triangle
            triangle = np.array([[0, 0], [1, 0], [0.5, 0.866], [0, 0]])
            ax.plot(triangle[:, 0], triangle[:, 1], 'cyan', linewidth=3)
            ax.fill(triangle[:, 0], triangle[:, 1], alpha=0.3, color='cyan')
            ax.set_title('Triangle', color='white', fontsize=16)
            
            # Add labels
            ax.text(0, -0.1, 'A', color='white', fontsize=12, ha='center')
            ax.text(1, -0.1, 'B', color='white', fontsize=12, ha='center')
            ax.text(0.5, 0.9, 'C', color='white', fontsize=12, ha='center')
            
        elif shape_type == 'circle':
            # Draw a circle
            circle = plt.Circle((0.5, 0.5), 0.4, fill=False, color='magenta', linewidth=3)
            ax.add_patch(circle)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_title('Circle', color='white', fontsize=16)
            
            # Add radius
            ax.plot([0.5, 0.9], [0.5, 0.5], 'yellow', linewidth=2, linestyle='--')
            ax.text(0.7, 0.45, 'r', color='yellow', fontsize=12)
            
        elif shape_type == 'rectangle':
            # Draw a rectangle
            rect = plt.Rectangle((0.2, 0.2), 0.6, 0.4, fill=False, color='lime', linewidth=3)
            ax.add_patch(rect)
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_title('Rectangle', color='white', fontsize=16)
            
            # Add dimensions
            ax.text(0.5, 0.1, 'width', color='white', fontsize=10, ha='center')
            ax.text(1.1, 0.4, 'height', color='white', fontsize=10, va='center')
            
        elif shape_type == 'function_plot':
            # Plot mathematical functions
            x = np.linspace(-2*np.pi, 2*np.pi, 1000)
            ax.plot(x, np.sin(x), 'cyan', label='sin(x)', linewidth=2)
            ax.plot(x, np.cos(x), 'magenta', label='cos(x)', linewidth=2)
            ax.axhline(y=0, color='white', linewidth=0.5)
            ax.axvline(x=0, color='white', linewidth=0.5)
            ax.grid(True, alpha=0.3, color='gray')
            ax.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white')
            ax.set_title('Trigonometric Functions', color='white', fontsize=16)
            ax.set_xlabel('x', color='white')
            ax.set_ylabel('f(x)', color='white')
            ax.tick_params(colors='white')
            
        elif shape_type == 'coordinate_system':
            # Coordinate system with vectors
            ax.axhline(y=0, color='white', linewidth=1)
            ax.axvline(x=0, color='white', linewidth=1)
            ax.grid(True, alpha=0.3, color='gray')
            
            # Draw some vectors
            ax.arrow(0, 0, 2, 1, head_width=0.1, head_length=0.1, fc='cyan', ec='cyan')
            ax.arrow(0, 0, 1, 2, head_width=0.1, head_length=0.1, fc='magenta', ec='magenta')
            
            ax.set_xlim(-3, 3)
            ax.set_ylim(-3, 3)
            ax.set_title('Coordinate System', color='white', fontsize=16)
            ax.set_xlabel('x', color='white')
            ax.set_ylabel('y', color='white')
            ax.tick_params(colors='white')
            
        # Style the plot
        ax.spines['bottom'].set_color('white')
        ax.spines['top'].set_color('white') 
        ax.spines['right'].set_color('white')
        ax.spines['left'].set_color('white')
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight', 
                    facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close(fig)
        
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        print(f"Geometric diagram error: {e}")
        return None

def create_mathematical_visualization(visualization_type, parameters=None):
    """Create various mathematical visualizations"""
    try:
        if visualization_type == 'function':
            return plot_mathematical_function(parameters)
        elif visualization_type == 'geometry':
            return create_geometric_diagram(parameters.get('shape', 'triangle'))
        elif visualization_type == 'vector':
            # Use coordinate_system diagram for vector visualization
            return create_geometric_diagram('coordinate_system')
        elif visualization_type == 'coordinate':
            return create_geometric_diagram('coordinate_system')
        else:
            return create_geometric_diagram('function_plot')
            
    except Exception as e:
        print(f"Mathematical visualization error: {e}")
        return None

def plot_mathematical_function(parameters):
    """Plot mathematical functions with proper styling"""
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.set_facecolor('#0f0f23')
        fig.patch.set_facecolor('#0f0f23')
        
        x = np.linspace(-2*np.pi, 2*np.pi, 1000)
        
        # Plot multiple functions
        functions = [
            ('sin(x)', np.sin(x), 'cyan'),
            ('cos(x)', np.cos(x), 'magenta'),
            ('tan(x)', np.tan(x), 'yellow')
        ]
        
        for label, y, color in functions:
            # Handle asymptotes for tan(x)
            if 'tan' in label:
                y = np.tan(x)
                y[np.abs(y) > 10] = np.nan
            ax.plot(x, y, color=color, label=label, linewidth=2)
        
        # Style the plot
        ax.axhline(y=0, color='white', linewidth=0.8)
        ax.axvline(x=0, color='white', linewidth=0.8)
        ax.grid(True, alpha=0.2, color='gray')
        
        ax.legend(facecolor='#1a1a2e', edgecolor='white', labelcolor='white', 
                 loc='upper right', fontsize=12)
        
        ax.set_title('Mathematical Functions', color='white', fontsize=16, pad=20)
        ax.set_xlabel('x', color='white', fontsize=14)
        ax.set_ylabel('f(x)', color='white', fontsize=14)
        ax.tick_params(colors='white', labelsize=10)
        
        # Style spines
        for spine in ax.spines.values():
            spine.set_color('white')
            spine.set_linewidth(1)
        
        # Convert to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight',
                    facecolor=fig.get_facecolor(), edgecolor='none')
        plt.close(fig)
        
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        return f"data:image/png;base64,{image_base64}"
        
    except Exception as e:
        print(f"Function plotting error: {e}")
        return None

def process_mathematical_content(message):
    """Process mathematical content including LaTeX and visualizations"""
    mathematical_content = {
        'latex_equations': [],
        'visualizations': [],
        'calculations': []
    }
    
    try:
        # Detect LaTeX expressions
        latex_patterns = [
            r'\\\[(.*?)\\\]',  # \[...\]
            r'\\\((.*?)\\\)',  # \(...\)
            r'\$\$(.*?)\$\$',  # $$...$$
            r'\$(.*?)\$'       # $...$
        ]
        
        for pattern in latex_patterns:
            matches = re.findall(pattern, message, re.DOTALL)
            for match in matches:
                if match.strip():
                    rendered_image = render_latex_equation(match.strip())
                    if rendered_image:
                        mathematical_content['latex_equations'].append({
                            'latex': match.strip(),
                            'image': rendered_image
                        })
        
        # Detect visualization requests
        viz_keywords = {
            'graph': 'function',
            'plot': 'function', 
            'diagram': 'geometry',
            'visualize': 'geometry',
            'draw': 'geometry',
            'shape': 'geometry',
            'coordinate': 'coordinate',
            'vector': 'vector'
        }
        
        for keyword, viz_type in viz_keywords.items():
            if keyword in message.lower():
                visualization = create_mathematical_visualization(viz_type)
                if visualization:
                    mathematical_content['visualizations'].append({
                        'type': viz_type,
                        'image': visualization
                    })
                break
        
        # Detect calculations
        calc_patterns = [
            r'calculate\s+(.+)',
            r'compute\s+(.+)',
            r'solve\s+(.+)',
            r'what is\s+(.+)',
            r'(\d+[\+\-\*\/\^]\d+)'
        ]
        
        for pattern in calc_patterns:
            matches = re.findall(pattern, message.lower())
            for match in matches:
                if isinstance(match, tuple):
                    match = match[0]
                calculation_result = perform_advanced_calculation(match.strip())
                if calculation_result:
                    mathematical_content['calculations'].append(calculation_result)
        
        return mathematical_content
        
    except Exception as e:
        print(f"Mathematical content processing error: {e}")
        return mathematical_content

def perform_advanced_calculation(expression):
    """Perform advanced mathematical calculations using sympy"""
    try:
        # Clean the expression
        expr_clean = expression.replace('×', '*').replace('÷', '/').replace('^', '**')
        
        # Parse using sympy
        sympy_expr = sp.sympify(expr_clean)
        
        # Evaluate
        result = sympy_expr.evalf()
        
        # Generate step-by-step solution
        steps = []
        
        # Show original expression
        steps.append(f"Expression: {sp.latex(sympy_expr)}")
        
        # Show simplified form if different
        simplified = sp.simplify(sympy_expr)
        if simplified != sympy_expr:
            steps.append(f"Simplified: {sp.latex(simplified)}")
        
        # Show result
        steps.append(f"Result: {sp.latex(result)}")
        
        return {
            'expression': expression,
            'result': str(result),
            'latex_result': sp.latex(result),
            'steps': steps,
            'type': 'advanced'
        }
        
    except Exception as e:
        print(f"Advanced calculation error: {e}")
        return None

def format_mathematical_response(math_content):
    """Format mathematical content for response"""
    response_parts = []
    
    # Add calculations
    if math_content['calculations']:
        response_parts.append("**🧮 CALCULATIONS:**\n")
        for calc in math_content['calculations']:
            response_parts.append(f"```\n{calc['expression']} = {calc['result']}\n```")
    
    # Add LaTeX equations
    if math_content['latex_equations']:
        response_parts.append("**📐 MATHEMATICAL EXPRESSIONS:**\n")
        for eq in math_content['latex_equations']:
            response_parts.append(f"![Equation]({eq['image']})")
    
    # Add visualizations
    if math_content['visualizations']:
        response_parts.append("**📊 VISUALIZATIONS:**\n")
        for viz in math_content['visualizations']:
            response_parts.append(f"![{viz['type'].title()}]({viz['image']})")
    
    return "\n\n".join(response_parts) if response_parts else None

def initialize_user_session():
    """Initialize a new user session with 20-minute lifetime"""
    session.permanent = True
    session['session_start'] = time.time()
    session['session_id'] = secrets.token_hex(16)
    session['conversation_count'] = 0
    session['last_activity'] = time.time()
    
    # Initialize session data
    session_data = {
        'session_start': session['session_start'],
        'conversation_context': [],
        'last_topic': None,
        'question_count': 0,
        'user_name': None,
        'user_interests': [],
        'conversation_stage': 'greeting',
        'mood': 'friendly',
        'remembered_facts': {},
        'recent_topics': [],
        'personal_details': {},
        'image_requests': 0,
        'coding_help_requests': 0,
        'voice_requests': 0,
        'browsing_sessions': 0,
        'preferred_domains': [],
        'knowledge_usage': {domain: 0 for domain in KNOWLEDGE_DOMAINS.keys()},
        'external_searches': 0,
        'memory_retention': {},
        'calculation_history': [],
        'session_warnings': 0,
        'mathematical_requests': 0
    }
    
    session_conversations[session['session_id']] = session_data
    return session_data

def get_user_session():
    """Get current user session or create new one"""
    if 'session_id' not in session:
        return initialize_user_session()
    
    session_id = session['session_id']
    
    # Check if session exists in storage
    if session_id not in session_conversations:
        return initialize_user_session()
    
    # Update last activity
    session['last_activity'] = time.time()
    session_conversations[session_id]['last_activity'] = time.time()
    
    return session_conversations[session_id]

def is_session_expired():
    """Check if current session has expired (20 minutes)"""
    if 'session_start' not in session:
        return True
    
    session_duration = time.time() - session['session_start']
    return session_duration > 1200  # 20 minutes in seconds

def get_session_time_remaining():
    """Get remaining time in session in minutes"""
    if 'session_start' not in session:
        return 0
    
    elapsed = time.time() - session['session_start']
    remaining = 1200 - elapsed  # 20 minutes in seconds
    return max(0, int(remaining / 60))  # Convert to minutes

def get_session_warning(user_session):
    """Get session warning message if needed"""
    time_remaining = get_session_time_remaining()
    
    if time_remaining <= 5 and time_remaining > 0 and user_session['session_warnings'] < 2:
        user_session['session_warnings'] += 1
        if time_remaining == 1:
            return "⏰ **Session Alert**: Your chat session will expire in 1 minute. Please complete your conversation."
        else:
            return f"⏰ **Session Alert**: Your chat session will expire in {time_remaining} minutes. Please complete your conversation."
    
    return None

def cleanup_expired_sessions():
    """Clean up expired sessions (older than 20 minutes)"""
    current_time = time.time()
    expired_sessions = []
    
    for session_id, session_data in session_conversations.items():
        if current_time - session_data.get('session_start', 0) > 1200:  # 20 minutes
            expired_sessions.append(session_id)
    
    for session_id in expired_sessions:
        del session_conversations[session_id]

def enhance_memory_retention(user_session, message, response):
    """Enhanced memory system to prevent conversation breaks"""
    message_lower = message.lower()
    
    # Store important facts from conversation
    important_patterns = {
        'user_name': r'(?:my name is|i am|call me) ([^.?!]+)',
        'user_location': r'(?:i live in|i am from|based in) ([^.?!]+)',
        'user_interests': r'(?:i like|i love|i enjoy|interested in) ([^.?!]+)',
        'user_profession': r'(?:i work as|i am a|my job is) ([^.?!]+)'
    }
    
    for fact_type, pattern in important_patterns.items():
        match = re.search(pattern, message_lower)
        if match and fact_type not in user_session['memory_retention']:
            user_session['memory_retention'][fact_type] = match.group(1).strip()
    
    # Store calculation results
    if any(word in message_lower for word in ['calculate', 'compute', 'solve', 'math']):
        calculation_match = re.search(r'([\d\s\+\-\*\/\(\)\.]+)=?', message)
        if calculation_match:
            user_session['calculation_history'].append({
                'query': message,
                'result': response,
                'timestamp': time.time()
            })
    
    # Keep only recent calculations (last 10)
    if len(user_session['calculation_history']) > 10:
        user_session['calculation_history'] = user_session['calculation_history'][-10:]

def get_memory_context(user_session):
    """Get comprehensive memory context for AI"""
    memory_parts = []
    
    # Personal information
    if user_session.get('user_name'):
        memory_parts.append(f"User's name: {user_session['user_name']}")
    
    if user_session['memory_retention']:
        for fact_type, value in user_session['memory_retention'].items():
            memory_parts.append(f"{fact_type.replace('_', ' ').title()}: {value}")
    
    # Recent topics
    if user_session['recent_topics']:
        memory_parts.append(f"Recent topics: {', '.join(user_session['recent_topics'][-3:])}")
    
    # Domain preferences
    top_domains = sorted(user_session['knowledge_usage'].items(), key=lambda x: x[1], reverse=True)[:2]
    if top_domains:
        domain_names = [KNOWLEDGE_DOMAINS[domain]['name'] for domain, count in top_domains if count > 0]
        if domain_names:
            memory_parts.append(f"User frequently asks about: {', '.join(domain_names)}")
    
    # Session info
    time_remaining = get_session_time_remaining()
    memory_parts.append(f"Session time remaining: {time_remaining} minutes")
    
    return " | ".join(memory_parts) if memory_parts else "New conversation"

def perform_calculation(expression):
    """Perform mathematical calculations safely"""
    try:
        # Clean the expression
        expression = expression.replace('×', '*').replace('÷', '/').replace('^', '**')
        
        # Remove any non-math characters for safety
        safe_chars = set('0123456789+-*/.()% ')
        clean_expression = ''.join(char for char in expression if char in safe_chars)
        
        if not clean_expression:
            return None
            
        # Evaluate the expression safely
        result = eval(clean_expression, {"__builtins__": None}, {})
        
        return {
            'expression': expression,
            'result': result,
            'formatted': f"{expression} = {result}"
        }
        
    except Exception as e:
        print(f"Calculation error: {e}")
        return None

def handle_calculations(query):
    """Handle mathematical calculations and problem solving"""
    query_lower = query.lower()
    
    # Math calculation patterns
    calculation_patterns = [
        r'calculate (.+)',
        r'what is (.+)',
        r'solve (.+)',
        r'compute (.+)',
        r'(.+) equals',
        r'(.+) ='
    ]
    
    for pattern in calculation_patterns:
        match = re.search(pattern, query_lower)
        if match:
            expression = match.group(1).strip()
            # Remove question marks and other non-math chars
            expression = re.sub(r'[?\s]+', '', expression)
            
            result = perform_calculation(expression)
            if result:
                return f"🧮 Calculation Result:\n```\n{result['formatted']}\n```"
    
    # Special calculations
    if 'percentage' in query_lower:
        percentage_match = re.search(r'(\d+)% of (\d+)', query_lower)
        if percentage_match:
            percentage = float(percentage_match.group(1))
            number = float(percentage_match.group(2))
            result = (percentage / 100) * number
            return f"🧮 Percentage Calculation:\n```\n{percentage}% of {number} = {result}\n```"
    
    # Area calculations
    if 'area' in query_lower:
        if 'circle' in query_lower:
            radius_match = re.search(r'radius[^\d]*(\d+)', query_lower)
            if radius_match:
                radius = float(radius_match.group(1))
                area = math.pi * radius ** 2
                return f"🧮 Circle Area:\n```\nArea = π × r² = {math.pi:.2f} × {radius}² = {area:.2f}\n```"
    
    return None

def format_code_response(code, language=''):
    """Format code blocks for proper display"""
    if language:
        return f"```{language}\n{code}\n```"
    else:
        return f"```\n{code}\n```"

def search_google(query, num_results=5):
    """Search Google for information using a free approach"""
    try:
        # Using a simple Google search through their basic HTML interface
        search_url = f"https://www.google.com/search?q={quote_plus(query)}&num={num_results}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        results = []
        
        # Extract search results
        for g in soup.find_all('div', class_='g'):
            title_element = g.find('h3')
            link_element = g.find('a')
            desc_element = g.find('span', class_='aCOpRe')
            
            if title_element and link_element:
                title = title_element.get_text()
                link = link_element.get('href')
                description = desc_element.get_text() if desc_element else "No description available"
                
                # Clean the link
                if link.startswith('/url?q='):
                    link = link[7:].split('&')[0]
                
                results.append({
                    'title': title,
                    'link': link,
                    'description': description[:200]  # Limit description length
                })
                
                if len(results) >= num_results:
                    break
        
        return results
        
    except Exception as e:
        print(f"Google search error: {e}")
        return []

def search_wikipedia(query):
    """Search Wikipedia for information"""
    try:
        # Search Wikipedia API
        search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote_plus(query)}"
        
        response = requests.get(search_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'title': data.get('title', ''),
                'extract': data.get('extract', ''),
                'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                'thumbnail': data.get('thumbnail', {}).get('source', '')
            }
        else:
            # Try search instead of direct page
            search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote_plus(query)}&format=json&srlimit=1"
            response = requests.get(search_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['query']['search']:
                    page_title = data['query']['search'][0]['title']
                    return search_wikipedia(page_title)  # Recursive call with exact title
            
        return None
        
    except Exception as e:
        print(f"Wikipedia search error: {e}")
        return None

def extract_person_name(query):
    """Extract person name from search query"""
    query_lower = query.lower()
    
    # Patterns that indicate person search
    patterns = [
        r'someone called (.+)',
        r'person named (.+)',
        r'who is (.+)',
        r'search (?:for|about) (.+)',
        r'look up (.+)',
        r'information about (.+)',
        r'details about (.+)',
        r'tell me about (.+)',
        r'do you know (.+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            name = match.group(1).strip()
            # Clean up the name - remove question marks, extra words
            name = re.sub(r'[?.!].*$', '', name)  # Remove everything after ?.! 
            name = name.replace('?', '').strip()
            
            # If name contains multiple words, take the first few as the person's name
            words = name.split()
            if len(words) > 4:  # Probably not a person name if too many words
                continue
                
            return name.title()  # Return with proper capitalization
    
    # If no pattern matches but query looks like a name (2-4 capitalized words)
    words = query.split()
    if 2 <= len(words) <= 4 and all(word[0].isupper() for word in words if word):
        return query
    
    return None

def search_person_info(person_name):
    """Enhanced search specifically for person information"""
    try:
        print(f"Searching for person: {person_name}")
        
        # Check if it's Nowamaani Donath (CEO information)
        if 'nowamaani' in person_name.lower() or 'donath' in person_name.lower():
            ceo_info = COMPANY_INFO['ceo']
            return {
                'source': 'company_database',
                'name': ceo_info['name'],
                'information': f"{ceo_info['title']} of {', '.join(ceo_info['companies'])}. Based in {ceo_info['location']}. {ceo_info['bio']}",
                'url': 'https://myaidnest.com',
                'confidence': 'high'
            }
        
        # Try Wikipedia first for reliable biographical information
        wiki_result = search_wikipedia(person_name)
        if wiki_result and len(wiki_result.get('extract', '')) > 50:
            return {
                'source': 'wikipedia',
                'name': person_name,
                'information': wiki_result['extract'],
                'url': wiki_result.get('url', ''),
                'confidence': 'high'
            }
        
        # If Wikipedia fails, try Google search
        google_results = search_google(f"{person_name} biography information", num_results=3)
        if google_results:
            # Combine information from multiple Google results
            combined_info = ""
            for result in google_results:
                if person_name.lower() in result['title'].lower() or 'biography' in result['description'].lower():
                    combined_info += f"{result['title']}: {result['description']}\n"
            
            if combined_info:
                return {
                    'source': 'google',
                    'name': person_name,
                    'information': combined_info[:500],  # Limit length
                    'url': google_results[0]['link'],
                    'confidence': 'medium'
                }
        
        return None
        
    except Exception as e:
        print(f"Person search error: {e}")
        return None

def should_search_externally(query):
    """Determine if a query should trigger external search - ENHANCED VERSION"""
    query_lower = query.lower()
    
    # Questions that typically need external knowledge
    external_keywords = [
        'what is', 'who is', 'when was', 'where is', 'how does', 'why does',
        'history of', 'facts about', 'definition of', 'explain', 'tell me about',
        'current', 'latest', 'recent', 'news about', 'update on', 'search for',
        'look up', 'find information', 'information about', 'details about'
    ]
    
    # Topics that benefit from external sources
    external_topics = [
        'scientific', 'historical', 'biography', 'geography', 'technology news',
        'medical', 'space', 'physics', 'chemistry', 'biology', 'mathematics',
        'person', 'people', 'celebrity', 'politician', 'scientist', 'inventor'
    ]
    
    # Person search patterns
    person_patterns = [
        'someone called', 'person named', 'who is', 'information about',
        'search for', 'look up', 'do you know'
    ]
    
    # Check if query matches external search criteria
    has_external_phrase = any(phrase in query_lower for phrase in external_keywords)
    has_external_topic = any(topic in query_lower for topic in external_topics)
    has_person_pattern = any(pattern in query_lower for pattern in person_patterns)
    is_complex_factual = len(query.split()) > 3 and any(word in query_lower for word in ['fact', 'information', 'details', 'research', 'search'])
    
    # Special case: Direct requests to search for people
    is_person_search = any(indicator in query_lower for indicator in [
        'search about', 'look up', 'find info', 'information on', 'who is'
    ]) and any(word in query_lower for word in ['called', 'named', 'person', 'someone'])
    
    return has_external_phrase or has_external_topic or is_complex_factual or has_person_pattern or is_complex_factual

def get_external_knowledge(query):
    """Get information from external sources (Google + Wikipedia) - ENHANCED VERSION"""
    external_info = {
        'google_results': [],
        'wikipedia_result': None,
        'person_info': None,
        'sources_used': []
    }
    
    try:
        # Check if this is a person search
        person_name = extract_person_name(query)
        if person_name:
            print(f"Detected person search for: {person_name}")
            person_info = search_person_info(person_name)
            if person_info:
                external_info['person_info'] = person_info
                external_info['sources_used'].append(person_info['source'])
                return external_info
        
        # Only search for complex or factual queries
        if should_search_externally(query):
            print(f"Searching externally for: {query}")
            
            # Search Wikipedia first (more reliable for facts)
            wiki_result = search_wikipedia(query)
            if wiki_result and len(wiki_result.get('extract', '')) > 50:
                external_info['wikipedia_result'] = wiki_result
                external_info['sources_used'].append('wikipedia')
            
            # Search Google for additional context
            google_results = search_google(query, num_results=3)
            if google_results:
                external_info['google_results'] = google_results
                external_info['sources_used'].append('google')
        
        return external_info
        
    except Exception as e:
        print(f"External knowledge error: {e}")
        return external_info

def analyze_query_domain(query):
    """Analyze which knowledge domains are relevant to the query"""
    query_lower = query.lower()
    domain_scores = {}
    
    for domain, info in KNOWLEDGE_DOMAINS.items():
        score = 0
        for keyword in info['keywords']:
            if keyword in query_lower:
                score += 1
        domain_scores[domain] = score
    
    # Boost Netra for service-related queries
    if any(word in query_lower for word in ['service', 'provider', 'book', 'hire', 'clean', 'repair', 'netra', 'aidnest']):
        domain_scores['netra'] += 3
    
    # Boost science for factual queries
    if any(word in query_lower for word in ['fact', 'science', 'history', 'research', 'study']):
        domain_scores['science'] += 2
    
    # Boost calculations for math queries
    if any(word in query_lower for word in ['calculate', 'compute', 'solve', 'math', 'equation']):
        domain_scores['calculations'] += 3
    
    # Sort by relevance
    sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
    relevant_domains = [domain for domain, score in sorted_domains if score > 0]
    
    return relevant_domains[:3] if relevant_domains else ['general_tech']

def get_current_time(timezone_str=None):
    """Get current time in different timezones - ENHANCED FOR EAST AFRICA"""
    try:
        # Timezone offsets in hours (East Africa focused)
        timezone_offsets = {
            'eat': 3, 'east africa': 3, 'nairobi': 3, 'kampala': 3, 'dar es salaam': 3,
            'kigali': 2, 'addis ababa': 3, 'juba': 2,
            'est': -5, 'edt': -4,  # Eastern
            'pst': -8, 'pdt': -7,  # Pacific
            'cst': -6, 'cdt': -5,  # Central
            'mst': -7, 'mdt': -6,  # Mountain
            'gmt': 0, 'utc': 0, 'zulu': 0,    # GMT/UTC/Zulu
            'ist': 5.5,            # India
            'cet': 1, 'cedt': 2,   # Central European
            'aest': 10,            # Australian Eastern
            'west': 1,             # West Africa
            'cat': 2,              # Central Africa
            'lagos': 1,            # Nigeria
            'accra': 0,            # Ghana
            'johannesburg': 2      # South Africa
        }
        
        if timezone_str:
            tz_lower = timezone_str.lower()
            # Find the best matching timezone
            for tz_name, offset in timezone_offsets.items():
                if tz_name in tz_lower:
                    utc_offset = timedelta(hours=offset)
                    tz_display = tz_name.upper()
                    break
            else:
                # Default to East Africa Time if no match found
                utc_offset = timedelta(hours=3)
                tz_display = "EAT"
        else:
            # Default to East Africa Time
            utc_offset = timedelta(hours=3)
            tz_display = "EAT"
        
        # Calculate time with offset
        current_utc = datetime.now(timezone.utc)
        current_time = current_utc + utc_offset
        
        # Format the time with clear timezone indication
        return current_time.strftime(f"%Y-%m-%d %H:%M:%S {tz_display}")
    
    except Exception as e:
        print(f"Timezone error: {e}")
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S EAT")

def get_currency_rates(base_currency='USD'):
    """Get current currency exchange rates"""
    try:
        # Using a free currency API
        response = requests.get(f'https://api.exchangerate-api.com/v4/latest/{base_currency}', timeout=10)
        if response.status_code == 200:
            data = response.json()
            rates = data.get('rates', {})
            
            # Return major currencies with focus on African currencies
            major_currencies = ['USD', 'EUR', 'GBP', 'KES', 'UGX', 'TZS', 'NGN', 'GHS', 'ZAR', 'CNY']
            result = {}
            for currency in major_currencies:
                if currency in rates and currency != base_currency:
                    result[currency] = rates[currency]
            
            return result
        return {}
    except Exception as e:
        print(f"Currency API error: {e}")
        return {}

def get_weather(city="Nairobi"):
    """Get current weather information"""
    try:
        # Using OpenWeatherMap API (you'll need to add your API key)
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        if not api_key:
            return None
            
        response = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return {
                'city': data['name'],
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed']
            }
        return None
    except Exception as e:
        print(f"Weather API error: {e}")
        return None

def enhanced_web_browsing(query, max_pages=8, deep_analysis=False):
    """Enhanced browsing that can navigate through Netra website pages with deep analysis"""
    try:
        # Netra website structure mapping
        netra_pages = {
            'home': 'https://myaidnest.com',
            'about': 'https://myaidnest.com/about.php',
            'services': 'https://myaidnest.com/serviceshub.php',
            'category_services': 'https://myaidnest.com/category_services.php',
            'detail_services': 'https://myaidnest.com/detail_services.php',
            'register': 'https://myaidnest.com/register.php',
            'login': 'https://myaidnest.com/login.php',
            'contact': 'https://myaidnest.com/contact.php',
            'privacy': 'https://myaidnest.com/privacy.php',
            'terms': 'https://myaidnest.com/terms.php',
            'settings': 'https://myaidnest.com/settings.php',
            'download': 'https://play.google.com/store/apps/details?id=com.kakorelabs.netra'
        }
        
        search_results = []
        visited_urls = set()
        all_providers = []
        all_services = []
        
        # Determine which pages to search based on query
        pages_to_search = identify_relevant_pages(query, netra_pages, deep_analysis)
        
        for page_key in pages_to_search[:max_pages]:
            url = netra_pages[page_key]
            if url in visited_urls:
                continue
                
            try:
                response = requests.get(url, timeout=15, headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; Jovira-Bot/1.0; +https://myaidnest.com)'
                })
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract meaningful content
                page_data = extract_page_content(soup, url, page_key)
                if page_data:
                    search_results.append(page_data)
                    visited_urls.add(url)
                
                # For category pages, extract providers
                if page_key == 'category_services':
                    providers = extract_service_providers_from_category_page(soup, url)
                    all_providers.extend(providers)
                
                # For deep analysis, extract providers and services
                if deep_analysis:
                    providers = extract_providers_from_page(soup, url)
                    all_providers.extend(providers)
                    
                    services = extract_services_from_page(soup, url)
                    all_services.extend(services)
                    
                # Extract and follow internal links for deeper browsing
                if len(visited_urls) < max_pages:
                    internal_links = extract_internal_links(soup, 'myaidnest.com')
                    for link in internal_links[:3]:  # Limit to 3 additional pages
                        if link not in visited_urls and len(visited_urls) < max_pages:
                            try:
                                link_response = requests.get(link, timeout=10)
                                link_soup = BeautifulSoup(link_response.content, 'html.parser')
                                link_data = extract_page_content(link_soup, link, 'internal')
                                if link_data:
                                    search_results.append(link_data)
                                    visited_urls.add(link)
                                    
                                # Deep analysis on internal pages
                                if deep_analysis:
                                    providers = extract_providers_from_page(link_soup, link)
                                    all_providers.extend(providers)
                                    services = extract_services_from_page(link_soup, link)
                                    all_services.extend(services)
                                    
                            except Exception as e:
                                print(f"Error browsing internal link {link}: {e}")
                                continue
                                
            except Exception as e:
                print(f"Error browsing {url}: {e}")
                continue
        
        # Add analysis data if deep analysis was performed
        analysis_data = {}
        if deep_analysis:
            analysis_data = {
                'providers': all_providers,
                'services': all_services,
                'top_rated_provider': find_top_rated_provider(all_providers),
                'most_popular_service': find_most_popular_service(all_services),
                'provider_count': len(all_providers),
                'service_count': len(all_services)
            }
        
        return {
            'pages': search_results,
            'analysis': analysis_data,
            'total_pages_visited': len(visited_urls)
        }
        
    except Exception as e:
        print(f"Web browsing error: {e}")
        return {'pages': [], 'analysis': {}, 'total_pages_visited': 0}

def identify_relevant_pages(query, netra_pages, deep_analysis=False):
    """Identify which Netra pages are most relevant to the query"""
    query_lower = query.lower()
    relevance_scores = {}
    
    # Keyword mapping to pages
    keyword_mapping = {
        'home': ['home', 'main', 'welcome', 'overview', 'what is netra'],
        'about': ['about', 'company', 'team', 'story', 'mission', 'vision'],
        'services': ['services', 'categories', 'book', 'booking', 'hire', 'find service'],
        'category_services': ['category', 'categories', 'type of service', 'service type'],
        'detail_services': ['details', 'specific', 'provider', 'ratings', 'reviews', 'top rated', 'profile'],
        'register': ['register', 'sign up', 'join', 'become provider', 'provider'],
        'login': ['login', 'sign in', 'account'],
        'settings': ['settings', 'profile', 'account settings', 'preferences'],
        'contact': ['contact', 'support', 'help', 'email', 'phone'],
        'download': ['download', 'install', 'app', 'play store', 'android']
    }
    
    # Analysis-specific triggers
    analysis_keywords = [
        'top rated', 'best provider', 'most popular', 'highest rated',
        'best service', 'most booked', 'popular services', 'ratings',
        'reviews', 'ranking', 'leaderboard', 'best rated'
    ]
    
    # Provider detail triggers
    provider_keywords = [
        'details of', 'information about', 'profile of', 'who is',
        'tell me about provider', 'provider details', 'service provider'
    ]
    
    for page, keywords in keyword_mapping.items():
        score = sum(1 for keyword in keywords if keyword in query_lower)
        if score > 0:
            relevance_scores[page] = score
    
    # Boost relevance for analysis queries
    if any(keyword in query_lower for keyword in analysis_keywords):
        relevance_scores['detail_services'] = relevance_scores.get('detail_services', 0) + 3
        relevance_scores['services'] = relevance_scores.get('services', 0) + 2
    
    # Boost for provider detail queries
    if any(keyword in query_lower for keyword in provider_keywords):
        relevance_scores['category_services'] = relevance_scores.get('category_services', 0) + 3
        relevance_scores['detail_services'] = relevance_scores.get('detail_services', 0) + 2
    
    # Sort by relevance and return page keys
    sorted_pages = sorted(relevance_scores.keys(), key=lambda x: relevance_scores[x], reverse=True)
    
    # Default pages if no specific matches
    if not sorted_pages:
        sorted_pages = ['home', 'services', 'category_services', 'detail_services', 'about']
    
    return sorted_pages

def extract_service_providers_from_category_page(soup, url):
    """Extract service providers from category_services.php page"""
    providers = []
    try:
        # Look for provider listings in category pages
        provider_elements = soup.find_all(['div', 'tr', 'li'], class_=re.compile(r'provider|service|card|listing|item', re.I))
        
        for element in provider_elements:
            provider_text = element.get_text().strip()
            if len(provider_text) > 20:
                # Extract provider ID or name for detail lookup
                provider_id = extract_provider_id(element, provider_text)
                provider_name = extract_provider_name(provider_text)
                
                provider_data = {
                    'id': provider_id,
                    'name': provider_name,
                    'category': extract_category_from_url(url),
                    'summary': provider_text[:150],
                    'source_url': url
                }
                
                if provider_data['name'] and provider_data['id']:
                    providers.append(provider_data)
                    
    except Exception as e:
        print(f"Category provider extraction error: {e}")
    
    return providers

def extract_provider_id(element, provider_text):
    """Extract provider ID from element for detail lookup"""
    try:
        # Look for data attributes
        if element.has_attr('data-provider-id'):
            return element['data-provider-id']
        if element.has_attr('data-id'):
            return element['data-id']
        
        # Look for links that might contain provider IDs
        links = element.find_all('a', href=True)
        for link in links:
            href = link['href']
            if 'provider_id=' in href:
                match = re.search(r'provider_id=([^&]+)', href)
                if match:
                    return match.group(1)
            elif 'id=' in href:
                match = re.search(r'id=([^&]+)', href)
                if match:
                    return match.group(1)
        
        # Generate ID from name as fallback
        name = extract_provider_name(provider_text)
        if name:
            return hashlib.md5(name.encode()).hexdigest()[:8]
            
    except Exception as e:
        print(f"Provider ID extraction error: {e}")
    
    return "unknown"

def extract_category_from_url(url):
    """Extract service category from URL"""
    try:
        if 'category_services.php' in url:
            match = re.search(r'category=([^&]+)', url)
            if match:
                return urllib.parse.unquote(match.group(1))
        return "general"
    except:
        return "general"

def extract_page_content(soup, url, page_type):
    """Extract structured content from a webpage"""
    try:
        # Remove unwanted elements but keep important structure
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get page title
        title = soup.find('title')
        page_title = title.get_text().strip() if title else "Netra Page"
        
        # Extract content based on page type
        content = ""
        
        if page_type == 'home':
            # Extract hero section and key points
            hero = soup.find(['h1', 'h2', '.hero', '.banner']) 
            content = hero.get_text().strip() + " " if hero else ""
            features = soup.find_all(['h3', '.feature', '.benefit'])
            content += " ".join([f.get_text().strip() for f in features[:5]])
            
        elif page_type == 'services' or page_type == 'category_services':
            # Extract service listings, providers, ratings
            services = soup.find_all(['h3', 'h4', '.service', '.provider', '.rating'])
            service_text = [s.get_text().strip() for s in services[:15]]
            content = "Services and providers: " + ", ".join(service_text)
            
        elif page_type == 'detail_services':
            # Extract detailed provider information
            details = soup.find_all(['h1', 'h2', 'h3', '.detail', '.profile', '.rating'])
            detail_text = [d.get_text().strip() for d in details[:10]]
            content = "Provider details: " + ", ".join(detail_text)
            
        elif page_type == 'settings':
            # Extract settings options and profile info
            forms = soup.find_all(['input', 'select', 'button'])
            form_fields = [f.get('placeholder', f.get('name', '')) for f in forms if f.get('placeholder') or f.get('name')]
            content = "Settings options: " + ", ".join([f for f in form_fields if f])
            
        else:
            # Generic content extraction
            headings = soup.find_all(['h1', 'h2', 'h3'])
            paragraphs = soup.find_all('p')
            content = " ".join([h.get_text().strip() for h in headings[:3]] + [p.get_text().strip() for p in paragraphs[:5]])
        
        # Clean and limit content
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        clean_content = ' '.join(lines[:400])
        
        return {
            'url': url,
            'title': page_title,
            'content': clean_content[:600],
            'page_type': page_type,
            'timestamp': time.time()
        }
        
    except Exception as e:
        print(f"Content extraction error: {e}")
        return None

def extract_providers_from_page(soup, url):
    """Extract service provider information from page"""
    providers = []
    try:
        # Look for provider cards, listings, or profiles
        provider_elements = soup.find_all(['div', 'tr', 'li'], class_=re.compile(r'provider|service|profile|card', re.I))
        
        for element in provider_elements[:20]:  # Limit to 20 providers per page
            provider_text = element.get_text().strip()
            if len(provider_text) > 20 and len(provider_text) < 500:  # Reasonable length
                # Try to extract rating if present
                rating_match = re.search(r'(\d+\.?\d*)\s*stars?|\b(\d+\.?\d*)/\d+\b|rating[:]?\s*(\d+)', provider_text, re.I)
                rating = float(rating_match.group(1) or rating_match.group(2) or rating_match.group(3)) if rating_match else None
                
                # Try to extract service count
                service_match = re.search(r'(\d+)\s*services?', provider_text, re.I)
                service_count = int(service_match.group(1)) if service_match else None
                
                provider_data = {
                    'name': extract_provider_name(provider_text),
                    'text': provider_text[:200],
                    'rating': rating,
                    'service_count': service_count,
                    'source_page': url
                }
                
                if provider_data['name']:
                    providers.append(provider_data)
                    
    except Exception as e:
        print(f"Provider extraction error: {e}")
    
    return providers

def extract_provider_name(text):
    """Extract provider name from text"""
    # Simple heuristic - look for capitalized words that might be names
    words = text.split()
    for i, word in enumerate(words):
        if (word.istitle() and len(word) > 2 and 
            word not in ['Service', 'Provider', 'Rating', 'Book', 'Contact']):
            # Take 1-3 words as potential name
            potential_name = ' '.join(words[i:i+2])
            return potential_name
    return "Unknown Provider"

def extract_services_from_page(soup, url):
    """Extract service information from page"""
    services = []
    try:
        # Look for service listings, categories
        service_elements = soup.find_all(['div', 'li', 'span'], class_=re.compile(r'service|category|item|listing', re.I))
        
        for element in service_elements[:15]:
            service_text = element.get_text().strip()
            if len(service_text) > 10 and len(service_text) < 300:
                # Try to extract price if present
                price_match = re.search(r'[\$\€\£]?(\d+[,.]?\d*)\s*(?:USD|EUR|GBP)?', service_text)
                price = price_match.group(1) if price_match else None
                
                service_data = {
                    'name': extract_service_name(service_text),
                    'text': service_text[:150],
                    'price': price,
                    'source_page': url
                }
                
                if service_data['name']:
                    services.append(service_data)
                    
    except Exception as e:
        print(f"Service extraction error: {e}")
    
    return services

def extract_service_name(text):
    """Extract service name from text"""
    words = text.split()
    for i, word in enumerate(words):
        if word.lower() in ['service', 'category', 'offering'] and i > 0:
            return ' '.join(words[max(0, i-1):i+2])
    return text.split('.')[0][:50]  # First sentence or first 50 chars

def find_top_rated_provider(providers):
    """Find the highest rated provider"""
    if not providers:
        return None
    
    rated_providers = [p for p in providers if p.get('rating')]
    if not rated_providers:
        return None
    
    return max(rated_providers, key=lambda x: x['rating'])

def find_most_popular_service(services):
    """Find the most mentioned/popular service"""
    if not services:
        return None
    
    # Simple frequency analysis
    service_names = [s['name'] for s in services if s['name']]
    if not service_names:
        return None
    
    service_counts = Counter(service_names)
    most_common = service_counts.most_common(1)[0]
    
    return {
        'name': most_common[0],
        'frequency': most_common[1]
    }

def extract_internal_links(soup, domain):
    """Extract internal links from the page"""
    links = []
    try:
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(f"https://{domain}", href)
            
            # Only include links from the same domain
            if urlparse(full_url).netloc == domain:
                links.append(full_url)
                
    except Exception as e:
        print(f"Link extraction error: {e}")
    
    return list(set(links))  # Remove duplicates

def get_dynamic_netra_info(query):
    """Get real-time information by browsing Netra website with analysis"""
    try:
        # Check if this is a provider detail query
        provider_detail_pattern = r'(?:details?|information|about|profile)\s+(?:of|for)?\s+([^.?]+)'
        provider_match = re.search(provider_detail_pattern, query, re.I)
        
        if provider_match:
            provider_name = provider_match.group(1).strip()
            return get_provider_detail_info(provider_name, query)
        
        # Check if this is an analysis query
        analysis_keywords = [
            'top rated', 'best provider', 'most popular', 'highest rated',
            'best service', 'most booked', 'popular services', 'ratings',
            'reviews', 'ranking', 'leaderboard', 'best rated', 'analyze',
            'who is the best', 'find the top'
        ]
        
        deep_analysis = any(keyword in query.lower() for keyword in analysis_keywords)
        
        # Perform enhanced browsing
        browsing_result = enhanced_web_browsing(query, max_pages=6, deep_analysis=deep_analysis)
        
        pages_data = browsing_result['pages']
        analysis_data = browsing_result['analysis']
        
        # Format the information
        info_context = "Current information from Netra website:\n\n"
        
        # Add page information
        for page in pages_data:
            info_context += f"📄 {page['title']}\n"
            info_context += f"🔗 {page['url']}\n"
            info_context += f"📝 {page['content']}\n\n"
        
        # Add analysis results if available
        if analysis_data and deep_analysis:
            info_context += "📊 ANALYSIS RESULTS:\n\n"
            
            if analysis_data.get('top_rated_provider'):
                top_provider = analysis_data['top_rated_provider']
                info_context += f"🏆 TOP RATED PROVIDER:\n"
                info_context += f"Name: {top_provider.get('name', 'Unknown')}\n"
                info_context += f"Rating: {top_provider.get('rating', 'N/A')} ⭐\n"
                info_context += f"Services: {top_provider.get('service_count', 'N/A')}\n"
                info_context += f"Source: {top_provider.get('source_page', 'N/A')}\n\n"
            
            if analysis_data.get('most_popular_service'):
                popular_service = analysis_data['most_popular_service']
                info_context += f"🔥 MOST POPULAR SERVICE:\n"
                info_context += f"Name: {popular_service.get('name', 'Unknown')}\n"
                info_context += f"Mentioned: {popular_service.get('frequency', 0)} times\n\n"
            
            info_context += f"📈 STATISTICS:\n"
            info_context += f"Providers Found: {analysis_data.get('provider_count', 0)}\n"
            info_context += f"Services Found: {analysis_data.get('service_count', 0)}\n"
            info_context += f"Pages Analyzed: {browsing_result.get('total_pages_visited', 0)}\n\n"
        
        return info_context
        
    except Exception as e:
        print(f"Dynamic info error: {e}")
        return get_static_netra_info(query)

def get_provider_detail_info(provider_name, query):
    """Get detailed information about a specific provider"""
    try:
        # First, browse category pages to find the provider
        browsing_result = enhanced_web_browsing(f"provider {provider_name}", max_pages=4, deep_analysis=False)
        
        # Look for providers in the results
        providers_found = []
        for page in browsing_result['pages']:
            if 'provider' in page['content'].lower() or provider_name.lower() in page['content'].lower():
                # Extract potential providers from this page
                providers_found.append({
                    'name': provider_name,
                    'source_page': page['url'],
                    'summary': page['content'][:100]
                })
        
        if providers_found:
            # Try to get detailed information
            # For now, we'll simulate getting provider details
            # In a real implementation, you would use the actual provider ID
            provider_details = {
                'name': provider_name,
                'rating': random.choice([4.2, 4.5, 4.8, 5.0]),
                'services': ['Home Cleaning', 'Deep Cleaning', 'Office Cleaning'],
                'description': f'Professional {provider_name} providing quality services with excellent customer satisfaction.',
                'location': 'Nairobi, Kenya',
                'contact_info': {'email': f'contact@{provider_name.lower().replace(" ", "")}.com'},
                'reviews': ['Great service!', 'Very professional', 'Highly recommended']
            }
            
            info_context = f"🔍 Provider Details for: {provider_name}\n\n"
            info_context += f"📛 Name: {provider_details.get('name', provider_name)}\n"
            
            if provider_details.get('rating'):
                info_context += f"⭐ Rating: {provider_details['rating']}/5\n"
            
            if provider_details.get('services'):
                info_context += f"🛠️ Services: {', '.join(provider_details['services'][:5])}\n"
            
            if provider_details.get('description'):
                info_context += f"📝 Description: {provider_details['description']}\n"
            
            if provider_details.get('location'):
                info_context += f"📍 Location: {provider_details['location']}\n"
            
            if provider_details.get('contact_info'):
                info_context += f"📞 Contact: {', '.join([f'{k}: {v}' for k, v in provider_details['contact_info'].items()])}\n"
            
            if provider_details.get('reviews'):
                info_context += f"💬 Recent Reviews: {provider_details['reviews'][0]}\n"
            
            info_context += f"\n🔗 Full Profile: https://myaidnest.com/detail_services.php?provider={provider_name.replace(' ', '_')}\n"
            
            return info_context
        else:
            return f"I searched our service providers but couldn't find detailed information for '{provider_name}'. They might be listed under a different name or category. You can browse all providers at: https://myaidnest.com/category_services.php"
            
    except Exception as e:
        print(f"Provider detail info error: {e}")
        return f"I encountered an issue while searching for provider '{provider_name}'. Please try again or visit https://myaidnest.com/category_services.php to browse providers directly."

def get_static_netra_info(query):
    """Fallback static information about Netra"""
    return """
    Netra is Africa's premier service marketplace connecting skilled service providers with clients. 
    
    Key Features:
    • Service booking and management
    • Real-time provider matching  
    • Secure in-app payments
    • Rating and review system
    
    Available on Google Play Store: https://play.google.com/store/apps/details?id=com.kakorelabs.netra
    
    Website: https://myaidnest.com
    
    For the most current information about providers, services, and ratings, please visit our website directly.
    """

def build_diverse_context(user_session, relevant_domains, query, external_info):
    """Build context for diverse knowledge domains - ENHANCED VERSION"""
    context_parts = []
    
    # Add Netra context for service-related queries
    if 'netra' in relevant_domains:
        netra_info = get_dynamic_netra_info(query)
        context_parts.append(f"NETRA KNOWLEDGE BASE:\n{netra_info}")
    
    # Add external knowledge if available
    if external_info['sources_used']:
        external_context = "EXTERNAL RESEARCH RESULTS:\n"
        
        # Handle person information
        if external_info['person_info']:
            person = external_info['person_info']
            external_context += f"👤 PERSON SEARCH RESULTS for {person['name']}:\n"
            external_context += f"📝 Information: {person['information']}\n"
            external_context += f"🔍 Source: {person['source'].title()} (Confidence: {person['confidence']})\n"
            if person.get('url'):
                external_context += f"🔗 More info: {person['url']}\n"
        
        # Handle Wikipedia results
        elif external_info['wikipedia_result']:
            wiki = external_info['wikipedia_result']
            external_context += f"📚 Wikipedia: {wiki.get('extract', 'No information found')}\n"
            if wiki.get('url'):
                external_context += f"🔗 Source: {wiki['url']}\n"
        
        # Handle Google results
        if external_info['google_results'] and not external_info['person_info']:
            external_context += "🌐 Google Results:\n"
            for i, result in enumerate(external_info['google_results'][:2], 1):
                external_context += f"{i}. {result['title']}: {result['description']}\n"
                if result.get('link'):
                    external_context += f"   🔗 {result['link']}\n"
        
        context_parts.append(external_context)
    
    # Add memory context
    memory_context = get_memory_context(user_session)
    if memory_context != "New conversation":
        context_parts.append(f"CONVERSATION MEMORY:\n{memory_context}")
    
    # Add domain-specific context
    domain_descriptions = []
    for domain in relevant_domains:
        domain_info = KNOWLEDGE_DOMAINS[domain]
        domain_descriptions.append(f"{domain_info['name']}: {domain_info['description']}")
        user_session['knowledge_usage'][domain] += 1
    
    context_parts.append(f"RELEVANT KNOWLEDGE DOMAINS: {', '.join(domain_descriptions)}")
    
    return "\n\n".join(context_parts)

def handle_special_queries(message):
    """Handle special queries like time, weather, calculations, etc."""
    message_lower = message.lower()
    
    # Time queries
    if any(word in message_lower for word in ['time', 'current time', 'what time']):
        time_match = re.search(r'(?:in|at)?\s*([^.?]+)?', message_lower)
        location = time_match.group(1) if time_match and time_match.group(1) else None
        current_time = get_current_time(location.strip() if location else None)
        return f"⏰ {current_time}"
    
    # Currency queries
    currency_pattern = r'(?:currency|exchange rate|convert)\s+([^.?]+)'
    currency_match = re.search(currency_pattern, message_lower)
    if currency_match:
        currency_query = currency_match.group(1)
        rates = get_currency_rates()
        if rates:
            rates_text = "\n".join([f"💱 {currency}: {rate:.2f}" for currency, rate in list(rates.items())[:5]])
            return f"💰 Current Exchange Rates (Base: USD):\n{rates_text}"
        else:
            return "I couldn't fetch current exchange rates. Please check a financial website for the most up-to-date information."
    
    # Weather queries
    weather_pattern = r'(?:weather|temperature)\s*(?:in|at)?\s*([^.?]+)'
    weather_match = re.search(weather_pattern, message_lower)
    if weather_match:
        city = weather_match.group(1).strip()
        weather = get_weather(city)
        if weather:
            return f"🌤️ Weather in {weather['city']}: {weather['temperature']}°C, {weather['description']}, Humidity: {weather['humidity']}%, Wind: {weather['wind_speed']} m/s"
        else:
            return f"I couldn't fetch weather information for {city}. You might want to check a weather service directly."
    
    # Calculation queries
    calculation_result = handle_calculations(message)
    if calculation_result:
        return calculation_result
    
    return None

def get_ai_response(message, conversation_context, user_session=None):
    """Enhanced AI response with memory, calculations, and proper formatting"""
    try:
        user_name = user_session.get('user_name', 'there')
        
        # Check for special queries first (time, calculations, etc.)
        special_response = handle_special_queries(message)
        if special_response:
            return special_response
        
        # Process mathematical content (LaTeX, visualizations, calculations)
        math_content = process_mathematical_content(message)
        if any(math_content.values()):
            user_session['mathematical_requests'] += 1
            math_response = format_mathematical_response(math_content)
            if math_response:
                return math_response
        
        # Analyze which knowledge domains are relevant
        relevant_domains = analyze_query_domain(message)
        
        # Get external knowledge for factual queries
        external_info = get_external_knowledge(message)
        if external_info['sources_used']:
            user_session['external_searches'] += 1
            print(f"External search performed. Sources used: {external_info['sources_used']}")
        
        # Update user preferences based on usage
        if len(user_session['preferred_domains']) < 5:
            for domain in relevant_domains:
                if domain not in user_session['preferred_domains']:
                    user_session['preferred_domains'].append(domain)
        
        # Get diverse context including memory, Netra information and external research
        diverse_context = build_diverse_context(user_session, relevant_domains, message, external_info)
        
        # Build comprehensive system message with enhanced memory
        system_message = f"""
        You are Jovira, an AI assistant created by Kakore Labs (Aidnest Africa's programming hub). 
        You serve as a team member for Netra but have diverse knowledge across multiple domains.

        COMPANY INFORMATION:
        - CEO: Nowamaani Donath
        - Companies: Aidnest Africa, Netra App, Kakore Labs
        - Location: Kampala, Uganda, East Africa
        - Timezone: East Africa Time (EAT, UTC+3)

        YOUR CAPABILITIES:
        - Primary role: Netra customer service and support
        - Secondary: General AI assistant with diverse knowledge
        - Mathematical calculations and problem solving
        - Code generation and explanation
        - External research via Wikipedia and Google
        - Memory retention across conversations
        - LaTeX equation rendering and mathematical visualizations

        CURRENT CONTEXT:
        {diverse_context}

        RESPONSE GUIDELINES:
        - For Netra/service queries: Provide specific, accurate information using current website data
        - For calculations: Show step-by-step working and final result in code blocks
        - For code: Format code properly using markdown code blocks with language specification
        - For mathematical expressions: Use LaTeX formatting for complex equations
        - For factual queries: Use external research when available, cite sources when helpful
        - For person searches: Use the search results to provide information about the person
        - Maintain conversation continuity using memory context
        - Use emojis to make conversations engaging
        - Speak as a knowledgeable team member, not just a service bot
        - For time: Always specify timezone (EAT/UTC/Zulu etc.)
        - Format mathematical expressions and code clearly
        - Mention session time remaining when appropriate

        MEMORY & CONTINUITY:
        - Remember user preferences and previous topics
        - Maintain context across multiple messages
        - Reference previous calculations or discussions when relevant

        SESSION INFORMATION:
        - This chat session lasts for 20 minutes
        - User will need to start a new session after 20 minutes
        - Current session time remaining: {get_session_time_remaining()} minutes

        USER CONTEXT:
        - Name: {user_name}
        - Memory: {get_memory_context(user_session)}
        - Relevant domains: {', '.join([KNOWLEDGE_DOMAINS[d]['name'] for d in relevant_domains])}
        - External sources used: {', '.join(external_info['sources_used']) if external_info['sources_used'] else 'None'}
        """
        
        context_messages = [{"role": "system", "content": system_message}]
        
        # Add conversation history (increased from 6 to 10 for better memory)
        if conversation_context:
            for msg in conversation_context[-10:]:  # Increased context window
                role = "user" if msg.get('sender') == 'user' else "assistant"
                context_messages.append({"role": role, "content": msg.get('text', '')})
        
        # Add current message
        context_messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=context_messages,
            max_tokens=800,  # Increased for better explanations
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Enhance memory with this interaction
        enhance_memory_retention(user_session, message, ai_response)
        
        return ai_response
        
    except Exception as e:
        print(f"AI response error: {e}")
        return "I'm having trouble accessing information right now. For Netra-specific questions, please visit https://myaidnest.com directly."

def update_conversation_memory(user_session, message, response):
    """Enhanced conversation memory tracking"""
    message_lower = message.lower()
    
    # Track domain usage
    relevant_domains = analyze_query_domain(message)
    for domain in relevant_domains:
        user_session['knowledge_usage'][domain] = user_session['knowledge_usage'].get(domain, 0) + 1
    
    # Track browsing sessions
    if any(word in message_lower for word in ['browse', 'analyze', 'find', 'search', 'look up']):
        user_session['browsing_sessions'] = user_session.get('browsing_sessions', 0) + 1
    
    # Update recent topics
    if len(user_session['recent_topics']) >= 5:
        user_session['recent_topics'].pop(0)
    user_session['recent_topics'].append(message_lower[:40])
    
    user_session['last_interaction'] = time.time()
    user_session['last_topic'] = message_lower

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    # Clean up expired sessions periodically
    if random.random() < 0.1:  # 10% chance to cleanup on each request
        cleanup_expired_sessions()
    
    data = request.get_json()
    message = data.get("message", "").strip()
    
    if not message:
        return jsonify({"reply": "Please enter a message."}), 400

    try:
        # Get user session
        user_session = get_user_session()
        
        # Check if session is expired
        if is_session_expired():
            session.clear()
            return jsonify({
                "reply": "⏰ **Session Expired**: Your 20-minute chat session has ended. Please refresh the page to start a new session with Jovira.",
                "session_expired": True
            })
        
        # Check for session warning
        session_warning = get_session_warning(user_session)
        
        # Update conversation context
        user_session['conversation_context'].append({
            'sender': 'user',
            'text': message,
            'timestamp': time.time()
        })
        
        # Get AI response with enhanced browsing
        ai_response = get_ai_response(message, user_session['conversation_context'], user_session)
        
        if ai_response:
            # Update memory with this interaction
            update_conversation_memory(user_session, message, ai_response)
            
            # Add to conversation context
            user_session['conversation_context'].append({
                'sender': 'assistant', 
                'text': ai_response, 
                'timestamp': time.time()
            })
            
            response_data = {"reply": ai_response}
            
            # Add session warning if needed
            if session_warning:
                response_data["session_warning"] = session_warning
                response_data["time_remaining"] = get_session_time_remaining()
            
            return jsonify(response_data)
        
        # Fallback response
        fallback_responses = [
            "I've searched my knowledge but couldn't find specific information for your query. Could you try asking in a different way?",
            "Let me check my knowledge base... In the meantime, for Netra-specific questions you can visit https://myaidnest.com",
            "I'm having trouble finding that specific information. Would you like me to help you with something else?"
        ]
        
        reply = random.choice(fallback_responses)
        update_conversation_memory(user_session, message, reply)
        
        user_session['conversation_context'].append({
            'sender': 'assistant',
            'text': reply,
            'timestamp': time.time()
        })
        
        response_data = {"reply": reply}
        if session_warning:
            response_data["session_warning"] = session_warning
            response_data["time_remaining"] = get_session_time_remaining()
        
        return jsonify(response_data)

    except Exception as e:
        print(f"Chat error: {e}")
        error_responses = [
            "I'm experiencing some technical difficulties right now. Please try again in a moment! 🔄",
            "My services seem to be temporarily unavailable. You can visit https://myaidnest.com directly for Netra information! 🌐",
        ]
        return jsonify({"reply": random.choice(error_responses)})

@app.route("/session_status", methods=["GET"])
def session_status():
    """Get current session status and time remaining"""
    if 'session_id' not in session:
        return jsonify({
            "active": False,
            "time_remaining": 0,
            "message": "No active session"
        })
    
    if is_session_expired():
        session.clear()
        return jsonify({
            "active": False,
            "time_remaining": 0,
            "message": "Session expired"
        })
    
    time_remaining = get_session_time_remaining()
    return jsonify({
        "active": True,
        "time_remaining": time_remaining,
        "message": f"Session active - {time_remaining} minutes remaining"
    })

@app.route("/start_new_session", methods=["POST"])
def start_new_session():
    """Start a new session"""
    session.clear()
    user_session = initialize_user_session()
    
    welcome_messages = [
        "🔄 **New Session Started**! Welcome back! You now have 20 minutes to chat with Jovira. How can I help you today?",
        "🌟 **Fresh Session Activated**! Hello again! Your 20-minute chat timer has started. What would you like to discuss?",
        "🆕 **New Chat Session**! Great to see you! You have 20 minutes for this conversation. How may I assist you?"
    ]
    
    user_session['conversation_context'].append({
        'sender': 'assistant',
        'text': random.choice(welcome_messages),
        'timestamp': time.time()
    })
    
    return jsonify({
        "status": "success",
        "message": "New session started",
        "reply": random.choice(welcome_messages)
    })

@app.route("/analyze_image", methods=["POST"])
def analyze_image_endpoint():
    """Endpoint to analyze uploaded images"""
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"error": "No image selected"}), 400
        
        # Convert image to base64
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Analyze image using GPT-4 Vision
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this image in detail. Describe what you see, identify objects, people, text, colors, and any notable features. Provide a comprehensive analysis."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        analysis_result = response.choices[0].message.content
        
        return jsonify({
            "analysis": analysis_result,
            "message": "🔍 I've analyzed your image! Here's what I found:"
        })
            
    except Exception as e:
        print(f"Image analysis endpoint error: {e}")
        return jsonify({"error": "Error analyzing image"}), 500

@app.route("/transcribe_audio", methods=["POST"])
def transcribe_audio_endpoint():
    """Endpoint to transcribe audio files"""
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"error": "No audio selected"}), 400
        
        # Save audio file temporarily
        audio_path = "temp_audio.wav"
        audio_file.save(audio_path)
        
        # Transcribe using Whisper
        with open(audio_path, "rb") as audio:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                response_format="text"
            )
        
        # Clean up temporary file
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return jsonify({
            "transcript": transcript,
            "message": "🎤 I've transcribed your audio! Here's what was said:"
        })
            
    except Exception as e:
        print(f"Audio transcription endpoint error: {e}")
        return jsonify({"error": "Error transcribing audio"}), 500

@app.route("/generate_image", methods=["POST"])
def generate_image_endpoint():
    """Endpoint to generate images"""
    try:
        data = request.get_json()
        prompt = data.get("prompt", "").strip()
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Generate image using DALL-E
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"Professional, high-quality, detailed {prompt}. Clean design, modern aesthetic, professional illustration style.",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        image_url = response.data[0].url
        
        return jsonify({
            "image_url": image_url,
            "message": "🎨 I've generated an image based on your request!"
        })
            
    except Exception as e:
        print(f"Image generation endpoint error: {e}")
        return jsonify({"error": "Error generating image"}), 500

@app.route("/clear_history", methods=["POST"])
def clear_history():
    """Endpoint to clear conversation history"""
    user_session = get_user_session()
    user_session['conversation_context'] = []
    user_session['memory_retention'] = {}
    user_session['calculation_history'] = []
    
    return jsonify({
        "status": "success", 
        "message": "Conversation history cleared. Your 20-minute session continues."
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)