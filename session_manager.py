import time
import secrets
import re
from datetime import datetime, timezone, timedelta
from flask import session

# Session storage for conversation history (shared with app.py)
session_conversations = {}

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
        'knowledge_usage': {},
        'external_searches': 0,
        'memory_retention': {},
        'calculation_history': [],
        'session_warnings': 0,
        'mathematical_requests': 0,
        'last_interaction': time.time()
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
            user_session['calculation_history'] = user_session.get('calculation_history', [])
            user_session['calculation_history'].append({
                'query': message,
                'result': response,
                'timestamp': time.time()
            })
    
    # Keep only recent calculations (last 10)
    if len(user_session.get('calculation_history', [])) > 10:
        user_session['calculation_history'] = user_session['calculation_history'][-10:]

def get_memory_context(user_session):
    """Get comprehensive memory context for AI"""
    memory_parts = []
    
    # Personal information
    if user_session.get('user_name'):
        memory_parts.append(f"User's name: {user_session['user_name']}")
    
    if user_session.get('memory_retention'):
        for fact_type, value in user_session['memory_retention'].items():
            memory_parts.append(f"{fact_type.replace('_', ' ').title()}: {value}")
    
    # Recent topics
    if user_session.get('recent_topics'):
        memory_parts.append(f"Recent topics: {', '.join(user_session['recent_topics'][-3:])}")
    
    # Domain preferences
    if user_session.get('knowledge_usage'):
        top_domains = sorted(user_session['knowledge_usage'].items(), key=lambda x: x[1], reverse=True)[:2]
        if top_domains:
            from knowledge_base import KNOWLEDGE_DOMAINS
            domain_names = [KNOWLEDGE_DOMAINS[domain]['name'] for domain, count in top_domains if count > 0]
            if domain_names:
                memory_parts.append(f"User frequently asks about: {', '.join(domain_names)}")
    
    # Session info
    time_remaining = get_session_time_remaining()
    memory_parts.append(f"Session time remaining: {time_remaining} minutes")
    
    return " | ".join(memory_parts) if memory_parts else "New conversation"

def update_conversation_memory(user_session, message, response):
    """Enhanced conversation memory tracking"""
    message_lower = message.lower()
    
    # Track browsing sessions
    if any(word in message_lower for word in ['browse', 'analyze', 'find', 'search', 'look up']):
        user_session['browsing_sessions'] = user_session.get('browsing_sessions', 0) + 1
    
    # Update recent topics
    user_session['recent_topics'] = user_session.get('recent_topics', [])
    if len(user_session['recent_topics']) >= 5:
        user_session['recent_topics'].pop(0)
    user_session['recent_topics'].append(message_lower[:40])
    
    user_session['last_interaction'] = time.time()
    user_session['last_topic'] = message_lower