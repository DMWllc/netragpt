from flask import Flask, request, jsonify, render_template
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

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Conversation memory
conversation_history = {}

def get_user_session(user_id):
    if user_id not in conversation_history:
        conversation_history[user_id] = {
            'last_interaction': time.time(),
            'context': None,
            'last_topic': None,
            'question_count': 0,
            'user_name': None,
            'has_asked_name': False,
            'conversation_stage': 'greeting',  # greeting -> get_name -> main_conversation
            'use_api': True  # Default to using API for intelligent responses
        }
    return conversation_history[user_id]

def scrape_netra_website(query):
    """Scrape myaidnest.com for relevant information about Netra"""
    try:
        # Search for relevant pages
        search_urls = [
            "https://myaidnest.com",
            "https://myaidnest.com/netra",
            "https://myaidnest.com/services",
            "https://myaidnest.com/about"
        ]
        
        scraped_content = []
        for url in search_urls:
            try:
                response = requests.get(url, timeout=10)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract relevant text
                text_content = soup.get_text()
                # Clean up the text
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                clean_text = ' '.join(lines[:500])  # Limit content length
                
                scraped_content.append(f"From {url}: {clean_text}")
                
            except Exception as e:
                continue
        
        return " ".join(scraped_content) if scraped_content else None
        
    except Exception as e:
        return None

def get_ai_response(message, conversation_context, website_content=None):
    """Get intelligent response from OpenAI API with context"""
    try:
        # Prepare conversation context
        context_messages = []
        
        # Add system message with Netra specialization
        system_message = """You are NetraGPT, an AI assistant for Aidnest Africa and the Netra platform. 
        Netra is a digital platform connecting service providers with clients across Africa.
        Key features:
        - Service providers can register with email and OTP verification
        - Clients can browse and book services directly
        - Available on Google Play Store
        - Categories include technicians, creatives, professionals, home services
        - Focus on African markets and communities
        
        Be helpful, professional, and focus on practical guidance about Netra and Aidnest Africa."""
        
        context_messages.append({"role": "system", "content": system_message})
        
        # Add website content if available
        if website_content:
            context_messages.append({
                "role": "system", 
                "content": f"Additional context from website: {website_content[:2000]}"
            })
        
        # Add conversation context
        if conversation_context:
            for msg in conversation_context[-6:]:  # Last 6 messages for context
                context_messages.append({
                    "role": "user" if msg['sender'] == 'User' else "assistant",
                    "content": msg['text']
                })
        
        # Add current message
        context_messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=context_messages,
            max_tokens=300,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

def get_fallback_response(message, user_id="default"):
    user_session = get_user_session(user_id)
    message_lower = message.lower().strip()
    
    # Update session
    user_session['last_interaction'] = time.time()
    user_session['question_count'] += 1
    
    # Handle name collection logic
    if user_session['conversation_stage'] == 'greeting':
        user_session['conversation_stage'] = 'get_name'
        greeting_responses = [
            "Hello! 👋 I'm NetraGPT, your intelligent assistant for Aidnest Africa and the Netra platform. It's wonderful to meet you! What's your name?",
            "Hi there! 🌟 Welcome! I'm NetraGPT from Aidnest Africa. I'd love to know your name so we can have a more personal conversation.",
            "Greetings! 🚀 I'm NetraGPT, here to help you discover everything about Aidnest Africa and Netra. May I know your name?",
        ]
        return random.choice(greeting_responses)
    
    # If we're in get_name stage and haven't stored name yet
    if user_session['conversation_stage'] == 'get_name' and not user_session['user_name']:
        potential_name = message.strip()
        if len(potential_name) < 30:
            user_session['user_name'] = potential_name
            user_session['conversation_stage'] = 'main_conversation'
            name_responses = [
                f"Nice to meet you, {potential_name}! 🌟 I'm NetraGPT. I can help you with Netra platform info, or answer other questions using AI. What would you like to know?",
                f"Hello {potential_name}! 👋 Thanks for introducing yourself. I'm here to assist with Netra and beyond! What can I help you with today?",
            ]
            return random.choice(name_responses)
    
    # Use user's name in responses if available
    user_name = user_session.get('user_name', '')
    name_prefix = f"{user_name}, " if user_name else ""
    
    # Enhanced greeting detection
    greeting_patterns = [
        r'hello', r'hi', r'hey', r'greetings', r'good morning', r'good afternoon', 
        r'good evening', r'howdy', r'hi there', r'hello there', r'hey there'
    ]
    
    is_greeting = any(re.search(pattern, message_lower) for pattern in greeting_patterns)
    
    if is_greeting:
        greeting_responses = [
            f"{name_prefix}Hello again! 👋 How can I help you with Aidnest Africa, Netra, or anything else today?",
            f"{name_prefix}Hi there! 🌟 Good to see you again. What would you like to explore?",
        ]
        return random.choice(greeting_responses)
    
    # Handle yes/no responses to suggestions
    yes_patterns = [r'yes', r'yeah', r'yep', r'sure', r'okay', r'ok', r'go ahead', r'please', r'absolutely']
    no_patterns = [r'no', r'nope', r'nah', r'not really', r'maybe later', r'i\'m good', r'no thanks']
    
    if any(re.search(pattern, message_lower) for pattern in yes_patterns) and user_session.get('last_topic'):
        return handle_yes_response(user_session['last_topic'], user_session)
    
    if any(re.search(pattern, message_lower) for pattern in no_patterns) and user_session.get('last_topic'):
        return handle_no_response(user_session)
    
    # Check if this is a Netra/Aidnest Africa specific question
    netra_keywords = [
        'netra', 'aidnest', 'service provider', 'client', 'booking', 'download app',
        'play store', 'register', 'verify', 'otp', 'technician', 'creative', 'professional',
        'booking', 'appointment', 'categories', 'verification'
    ]
    
    is_netra_question = any(keyword in message_lower for keyword in netra_keywords)
    
    # For Netra-specific questions, use predefined responses OR AI with web scraping
    if is_netra_question:
        # Try to get real-time info from website first
        website_content = scrape_netra_website(message)
        
        # Get conversation context for AI
        chat_history = get_chat_history(user_id)
        
        # Try AI response with website context
        ai_response = get_ai_response(message, chat_history, website_content)
        
        if ai_response:
            # Add Netra-specific suggestion
            suggestions = [
                "Would you like to know more about specific Netra features?",
                "Should I explain how to get started with Netra?",
                "Want to learn about the benefits for service providers?",
            ]
            suggestion = random.choice(suggestions)
            user_session['last_topic'] = 'netra_ai'
            return f"{ai_response}\n\n{suggestion}"
        
        # Fallback to predefined responses if AI fails
        return get_netra_predefined_response(message, user_session)
    
    else:
        # For non-Netra questions, use AI with general knowledge
        chat_history = get_chat_history(user_id)
        ai_response = get_ai_response(message, chat_history)
        
        if ai_response:
            return f"{ai_response}\n\n💡 *This is an AI-generated response. For official Netra information, visit myaidnest.com*"
        
        # Fallback for AI failure
        return f"{name_prefix}I'd be happy to help with that! For the most accurate information about Netra and Aidnest Africa, please visit our website at myaidnest.com or contact info@myaidnest.com"

def get_chat_history(user_id):
    """Get conversation history for context"""
    user_session = get_user_session(user_id)
    # This would typically come from your database
    # For now, return basic context
    return []

def get_netra_predefined_response(message, user_session):
    """Predefined responses for Netra-specific questions"""
    user_name = user_session.get('user_name', '')
    name_prefix = f"{user_name}, " if user_name else ""
    message_lower = message.lower()
    
    # Enhanced predefined responses with more depth
    predefined_responses = {
        'netra': [
            f"{name_prefix}Netra is Aidnest Africa's flagship platform that connects skilled service providers with clients across Africa. It's designed specifically for African markets, focusing on reliability and trust through verification systems.",
            f"{name_prefix}Netra serves as a digital bridge between talent and opportunity in Africa. We verify providers, facilitate secure bookings, and build communities around quality services.",
        ],
        'download': [
            f"{name_prefix}You can download Netra from the Google Play Store. Search for 'Netra App' - it's free to download and use for both clients and service providers.",
            f"{name_prefix}Get started with Netra by downloading from Play Store. The app guides you through registration whether you're looking for services or offering them.",
        ],
        'provider': [
            f"{name_prefix}Service providers join Netra by: 1) Downloading the app 2) Registering with email 3) Creating a detailed service profile 4) Email verification with OTP 5) Starting to receive client requests.",
            f"{name_prefix}As a Netra service provider, you get: Client management tools, secure messaging, booking system, rating system, and business growth opportunities across Africa.",
        ],
        'client': [
            f"{name_prefix}Clients use Netra to: Browse verified service providers, check ratings and reviews, book appointments directly, and communicate securely through the app.",
            f"{name_prefix}For clients, Netra offers: Trusted service providers, easy booking system, secure payments, and quality assurance through our verification process.",
        ],
        'features': [
            f"{name_prefix}Netra's key features include: Provider verification, secure booking, in-app messaging, rating system, service categories, and business tools for providers.",
            f"{name_prefix}Netra offers: Multiple service categories, provider verification, secure payments, client reviews, appointment scheduling, and community building features.",
        ]
    }
    
    # Find best matching response
    for keyword, responses in predefined_responses.items():
        if keyword in message_lower:
            response = random.choice(responses)
            suggestions = [
                "Would you like more details about this?",
                "Should I explain how this works in practice?",
                "Want to know the benefits of this feature?",
            ]
            suggestion = random.choice(suggestions)
            user_session['last_topic'] = keyword
            return f"{response}\n\n{suggestion}"
    
    # Default Netra response
    default_responses = [
        f"{name_prefix}Netra is designed to make service access reliable across Africa. Could you tell me more about what specific aspect interests you?",
        f"{name_prefix}I'd love to help you with Netra! Are you interested in becoming a service provider, finding services, or learning about our platform features?",
    ]
    return random.choice(default_responses)

def handle_yes_response(topic, user_session):
    """Handle positive responses to suggestions"""
    user_name = user_session.get('user_name', '')
    name_prefix = f"{user_name}, " if user_name else ""
    
    deeper_responses = {
        'netra': [
            f"{name_prefix}Netra's impact goes beyond just connections - we're building trusted digital communities where quality service providers can thrive and clients can find reliable help with confidence.",
            f"{name_prefix}What makes Netra special is our focus on African market needs: we understand local challenges and have built solutions that actually work for our communities.",
        ],
        'provider': [
            f"{name_prefix}Providers on Netra benefit from our growing user base, marketing support, and tools that help manage their business efficiently. Many providers see significant growth within their first few months.",
            f"{name_prefix}Beyond basic registration, Netra offers providers analytics, customer management, and promotional opportunities to help grow their client base sustainably.",
        ],
        'client': [
            f"{name_prefix}Clients enjoy peace of mind knowing all providers are verified. Our rating system and secure payment options make the entire experience safe and reliable.",
            f"{name_prefix}Netra clients can save time and reduce stress by finding trusted professionals quickly. The platform handles scheduling, communication, and quality assurance.",
        ]
    }
    
    if topic in deeper_responses:
        response = random.choice(deeper_responses[topic])
    else:
        response = f"{name_prefix}I'm glad you're interested in learning more! What specific aspect would you like me to elaborate on?"
    
    return f"{response}\n\nIs there anything else you'd like to explore about Netra?"

def handle_no_response(user_session):
    """Handle negative responses to suggestions"""
    user_name = user_session.get('user_name', '')
    name_prefix = f"{user_name}, " if user_name else ""
    
    responses = [
        f"{name_prefix}No problem! What else would you like to know about Netra or Aidnest Africa?",
        f"{name_prefix}That's fine! What other aspect interests you?",
        f"{name_prefix}Understood! What would you prefer to discuss instead?",
    ]
    return random.choice(responses)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").strip()
    user_id = request.remote_addr

    if not message:
        return jsonify({"reply": "Please enter a message."}), 400

    try:
        # Always try to use AI first if API key is available and user wants it
        user_session = get_user_session(user_id)
        
        if os.environ.get("OPENAI_API_KEY") and user_session.get('use_api', True):
            # Get AI response for all questions
            chat_history = get_chat_history(user_id)
            website_content = scrape_netra_website(message) if any(keyword in message.lower() for keyword in ['netra', 'aidnest']) else None
            ai_response = get_ai_response(message, chat_history, website_content)
            
            if ai_response:
                # Add appropriate footer based on content
                if any(keyword in message.lower() for keyword in ['netra', 'aidnest', 'provider', 'client']):
                    footer = "\n\n💡 *For the most current information, visit myaidnest.com*"
                else:
                    footer = "\n\n💡 *This is an AI-generated response. For official Netra information, visit myaidnest.com*"
                
                return jsonify({"reply": ai_response + footer})
        
        # Fallback to predefined responses
        reply = get_fallback_response(message, user_id)
        return jsonify({"reply": reply})

    except Exception as e:
        # Final fallback
        error_responses = [
            "I'm here to help you with Aidnest Africa and Netra! What would you like to know?",
            "Let me assist you with Netra platform information. What can I help you with?",
        ]
        reply = random.choice(error_responses)
        return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)