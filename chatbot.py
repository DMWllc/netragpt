from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import os
import random
import re
import time
import hashlib

app = Flask(__name__)
CORS(app)

openai.api_key = os.environ.get("OPENAI_API_KEY")

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
            'conversation_stage': 'greeting'  # greeting -> get_name -> main_conversation
        }
    return conversation_history[user_id]

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
            "Hello! 👋 I'm NetraGPT, your assistant for Aidnest Africa and the Netra platform. It's wonderful to meet you! What's your name?",
            "Hi there! 🌟 Welcome! I'm NetraGPT from Aidnest Africa. I'd love to know your name so we can have a more personal conversation.",
            "Greetings! 🚀 I'm NetraGPT, here to help you discover everything about Aidnest Africa and Netra. May I know your name?",
            "Hey! 💫 Wonderful to connect with you! I'm NetraGPT. What should I call you during our conversation?",
            "Hello! 😊 I'm NetraGPT, your guide to Aidnest Africa's services. To make our chat more personal, could you tell me your name?"
        ]
        return random.choice(greeting_responses)
    
    # If we're in get_name stage and haven't stored name yet
    if user_session['conversation_stage'] == 'get_name' and not user_session['user_name']:
        # Extract name from message (simple approach)
        potential_name = message.strip()
        if len(potential_name) < 30:  # Basic sanity check
            user_session['user_name'] = potential_name
            user_session['conversation_stage'] = 'main_conversation'
            name_responses = [
                f"Nice to meet you, {potential_name}! 🌟 I'm NetraGPT from Aidnest Africa. How can I help you today?",
                f"Hello {potential_name}! 👋 Thanks for introducing yourself. I'm excited to tell you about Aidnest Africa and Netra. What would you like to know?",
                f"Wonderful to meet you, {potential_name}! 🚀 I'm NetraGPT, your assistant for all things Aidnest Africa. What can I help you with?",
                f"Hi {potential_name}! 💫 It's a pleasure to connect. I'm here to guide you through Aidnest Africa's services and Netra platform. What interests you?",
                f"Great to know you, {potential_name}! 😊 I'm NetraGPT, ready to help you explore Aidnest Africa. What would you like to learn about?"
            ]
            return random.choice(name_responses)
    
    # Use user's name in responses if available
    user_name = user_session.get('user_name', '')
    name_prefix = f"{user_name}, " if user_name else ""
    
    # Enhanced greeting detection (for subsequent greetings)
    greeting_patterns = [
        r'hello', r'hi', r'hey', r'greetings', r'good morning', r'good afternoon', 
        r'good evening', r'howdy', r'hi there', r'hello there', r'hey there'
    ]
    
    is_greeting = any(re.search(pattern, message_lower) for pattern in greeting_patterns)
    
    if is_greeting:
        greeting_responses = [
            f"{name_prefix}Hello again! 👋 How can I help you with Aidnest Africa or Netra today?",
            f"{name_prefix}Hi there! 🌟 Good to see you again. What would you like to know about our services?",
            f"{name_prefix}Hey! 🚀 Welcome back. What aspect of Aidnest Africa can I help you explore?",
            f"{name_prefix}Greetings! 💫 How can I assist you with Netra or Aidnest Africa today?",
            f"{name_prefix}Hello! 😊 What would you like to learn about Aidnest Africa's platform?"
        ]
        return random.choice(greeting_responses)
    
    # Handle yes/no responses to suggestions
    yes_patterns = [r'yes', r'yeah', r'yep', r'sure', r'okay', r'ok', r'go ahead', r'please', r'absolutely']
    no_patterns = [r'no', r'nope', r'nah', r'not really', r'maybe later', r'i\'m good', r'no thanks']
    
    if any(re.search(pattern, message_lower) for pattern in yes_patterns) and user_session.get('last_topic'):
        return handle_yes_response(user_session['last_topic'], user_session)
    
    if any(re.search(pattern, message_lower) for pattern in no_patterns) and user_session.get('last_topic'):
        return handle_no_response(user_session)
    
    # MAIN CONTENT RESPONSES - PRACTICAL AND ACTION-ORIENTED
    content_responses = {
        'aidnest_africa': {
            'responses': [
                f"{name_prefix}Aidnest Africa creates practical digital solutions that make life easier across Africa. We focus on real community problems - from access to services to tools that empower local professionals and businesses.",
                f"{name_prefix}Aidnest Africa is an organization building smart digital solutions for African communities. We use technology to solve real challenges and empower local professionals through platforms like Netra.",
                f"{name_prefix}We're Aidnest Africa - focused on creating digital tools that actually work for African users. Our main platform is Netra, which connects service providers with clients across the continent."
            ],
            'suggestions': [
                "Would you like me to tell you about our Netra platform?",
                "Should I explain how to get started with Netra?",
                "Want to know how Netra helps both service providers and clients?"
            ]
        },
        
        'netra_platform': {
            'responses': [
                f"{name_prefix}Netra is our digital platform that connects people with trusted service providers - technicians, creatives, professionals, and more. It's available on the Play Store for easy access.",
                f"{name_prefix}Netra is a bridge between skilled professionals and people who need their services. You can download the Netra app from the Play Store to get started.",
                f"{name_prefix}The Netra platform makes it easy to find and connect with verified service providers. Simply get the app from Play Store to begin using our services."
            ],
            'suggestions': [
                "Would you like to know how to download the Netra app?",
                "Should I explain how service providers can join Netra?",
                "Want to learn how clients use Netra to find services?"
            ]
        },
        
        'download_app': {
            'responses': [
                f"{name_prefix}To get Netra, simply go to the Google Play Store on your Android device and search for 'Netra App'. Download and install it to start connecting with service providers or offering your services.",
                f"{name_prefix}Getting Netra is easy! Visit the Play Store, search for 'Netra App', and download it. The app is free and will guide you through the setup process.",
                f"{name_prefix}You can download Netra from the Play Store. Just search for 'Netra App' and install it. Once installed, you can register as a client or service provider."
            ],
            'suggestions': [
                "Would you like to know how to register as a service provider?",
                "Should I explain how clients use the app?",
                "Want to know what types of services are available on Netra?"
            ]
        },
        
        'join_netra_provider': {
            'responses': [
                f"{name_prefix}To join Netra as a service provider: 1) Download the Netra app from Play Store 2) Register with your email 3) Submit your service profile with details about your skills 4) Verify your email with OTP 5) Start receiving client requests!",
                f"{name_prefix}Service providers can join Netra by: Downloading our app, registering with email, creating a service profile, verifying via OTP, and then they're ready to connect with clients.",
                f"{name_prefix}Becoming a Netra service provider is simple: Get the app, register with email, build your service profile, verify with OTP code, and begin offering your services to clients."
            ],
            'suggestions': [
                "Would you like to know what information you need for your service profile?",
                "Should I explain how the OTP verification works?",
                "Want to know how clients find and book providers?"
            ]
        },
        
        'client_usage': {
            'responses': [
                f"{name_prefix}As a client, just download Netra from Play Store, browse service providers by category, check their ratings and reviews, and book the service you need. It's that simple!",
                f"{name_prefix}Clients use Netra by: Downloading the app, searching for services they need, comparing provider ratings, and booking directly through the app. No complicated registration needed!",
                f"{name_prefix}For clients: Get the Netra app, find service providers in your area, read reviews from other clients, and book appointments directly. You can start using services immediately after downloading."
            ],
            'suggestions': [
                "Would you like to know what service categories are available?",
                "Should I explain how the booking system works?",
                "Want to know about the rating and review system?"
            ]
        },
        
        'service_categories': {
            'responses': [
                f"{name_prefix}Netra has various service categories including: Technicians (plumbers, electricians), Creative Services (designers, photographers), Professional Services (consultants, tutors), Home Services (cleaners, repair), and many more!",
                f"{name_prefix}We offer multiple service categories: Technical services, Creative professionals, Home maintenance, Business consulting, Educational services, and Personal care services. New categories are added regularly.",
                f"{name_prefix}Service categories on Netra include: Technical repairs, Creative work, Professional consulting, Home services, Education, Healthcare services, and more. Providers can register in their area of expertise."
            ],
            'suggestions': [
                "Would you like to know how to find providers in a specific category?",
                "Should I explain how providers set up their service profiles?",
                "Want to know about the verification process for providers?"
            ]
        },
        
        'provider_verification': {
            'responses': [
                f"{name_prefix}All Netra service providers are verified through: 1) Email verification with OTP 2) Service profile review 3) Document verification where applicable 4) Ongoing client rating system to maintain quality standards.",
                f"{name_prefix}We verify providers through multiple steps: Email OTP verification, service profile assessment, and for certain categories, document validation. Client reviews also help maintain service quality.",
                f"{name_prefix}Provider verification includes: Email OTP confirmation, detailed service profile submission, and in some cases document checks. The rating system ensures ongoing quality maintenance."
            ],
            'suggestions': [
                "Would you like to know what documents might be required?",
                "Should I explain how the client rating system works?",
                "Want to know how long verification usually takes?"
            ]
        },
        
        'booking_process': {
            'responses': [
                f"{name_prefix}The booking process is simple: Clients browse providers, select a service, choose appointment time, and book. Providers receive notifications and can confirm or reschedule. All communication happens through the app.",
                f"{name_prefix}Clients book services by: Selecting a provider, choosing service type, picking available time slots, and confirming booking. Providers get instant notifications to manage their schedule.",
                f"{name_prefix}Booking on Netra: Find provider, select service, choose time, confirm booking. Providers manage their availability and clients can reschedule if needed. Everything is handled within the app."
            ],
            'suggestions': [
                "Would you like to know how providers manage their availability?",
                "Should I explain the cancellation policy?",
                "Want to know about in-app communication features?"
            ]
        },
        
        'netra_benefits': {
            'responses': [
                f"{name_prefix}Netra benefits everyone: Providers get more clients and business management tools. Clients find trusted services easily. Communities benefit from reliable local services and economic growth.",
                f"{name_prefix}Benefits include: For providers - more visibility, client management tools, secure payments. For clients - verified providers, easy booking, reliable services. For communities - economic growth and trust.",
                f"{name_prefix}Netra creates value: Providers grow their business, clients save time finding services, communities develop stronger local economies through trusted digital connections."
            ],
            'suggestions': [
                "Would you like to know about the business tools for providers?",
                "Should I explain how clients can rate services?",
                "Want to know about the economic impact in communities?"
            ]
        },
        
        'get_started': {
            'responses': [
                f"{name_prefix}To get started: Download Netra from Play Store. If you're a service provider, register with email and create your profile. If you're a client, just browse and book services immediately!",
                f"{name_prefix}Getting started is easy: Download the app, choose your role (provider or client), and follow the simple setup steps. Providers need email verification, clients can start browsing right away.",
                f"{name_prefix}Start with Netra today: Get the app from Play Store. Service providers register and verify, clients can immediately search for services. The platform guides you through every step."
            ],
            'suggestions': [
                "Would you like the exact steps for service provider registration?",
                "Should I explain what clients see when they first open the app?",
                "Want to know about the support available if you need help?"
            ]
        }
    }
    
    # Enhanced keyword mapping with priority
    keyword_mapping = {
        'aidnest': 'aidnest_africa',
        'organization': 'aidnest_africa',
        'company': 'aidnest_africa',
        'what is aidnest': 'aidnest_africa',
        
        'netra': 'netra_platform',
        'platform': 'netra_platform',
        'what is netra': 'netra_platform',
        
        'download': 'download_app',
        'play store': 'download_app',
        'get app': 'download_app',
        'install': 'download_app',
        'where to get': 'download_app',
        
        'join': 'join_netra_provider',
        'register': 'join_netra_provider',
        'provider': 'join_netra_provider',
        'service provider': 'join_netra_provider',
        'become provider': 'join_netra_provider',
        'offer services': 'join_netra_provider',
        
        'client': 'client_usage',
        'customer': 'client_usage',
        'use netra': 'client_usage',
        'find services': 'client_usage',
        'book services': 'client_usage',
        
        'categories': 'service_categories',
        'types of services': 'service_categories',
        'what services': 'service_categories',
        'available services': 'service_categories',
        
        'verification': 'provider_verification',
        'verify': 'provider_verification',
        'otp': 'provider_verification',
        'email verification': 'provider_verification',
        
        'booking': 'booking_process',
        'how to book': 'booking_process',
        'appointment': 'booking_process',
        'schedule': 'booking_process',
        
        'benefits': 'netra_benefits',
        'advantages': 'netra_benefits',
        'why netra': 'netra_benefits',
        
        'get started': 'get_started',
        'start using': 'get_started',
        'how to start': 'get_started',
        'begin': 'get_started'
    }
    
    # Find the best matching content
    selected_topic = 'get_started'  # Default to getting started
    for keyword, topic in keyword_mapping.items():
        if keyword in message_lower:
            selected_topic = topic
            break
    
    # Check if this is out of scope
    aidnest_netra_keywords = ['aidnest', 'netra', 'provider', 'client', 'service', 'app', 'download', 'register', 'booking', 'verify']
    is_related = any(keyword in message_lower for keyword in aidnest_netra_keywords)
    
    if not is_related:
        out_of_scope_responses = [
            f"{name_prefix}That's an interesting question! Currently, I'm focused on helping with Aidnest Africa and Netra-related topics. For other questions, you'll need to wait for NetraGPT 2.0 coming soon!",
            f"{name_prefix}I'm specialized in Aidnest Africa and Netra topics right now. For broader questions, NetraGPT 2.0 will have expanded capabilities when it launches!",
            f"{name_prefix}That falls outside my current focus on Aidnest Africa and Netra. The upcoming NetraGPT 2.0 will handle more diverse topics!"
        ]
        return random.choice(out_of_scope_responses)
    
    content = content_responses[selected_topic]
    response = random.choice(content['responses'])
    suggestion = random.choice(content['suggestions'])
    
    # Store context for yes/no handling
    user_session['last_topic'] = selected_topic
    user_session['context'] = selected_topic
    
    return f"{response}\n\n{suggestion}"

def handle_yes_response(topic, user_session):
    """Handle positive responses to suggestions"""
    user_name = user_session.get('user_name', '')
    name_prefix = f"{user_name}, " if user_name else ""
    
    yes_responses = {
        'aidnest_africa': [
            f"{name_prefix}Netra is our platform connecting service providers with clients across Africa. It's available on Play Store and helps skilled professionals grow their business while making services accessible to everyone.",
            f"{name_prefix}Netra is our digital marketplace where providers offer services and clients find trusted professionals. The app is free on Play Store and simplifies the entire process from discovery to booking.",
            f"{name_prefix}Netra creates opportunities by connecting local service providers with people who need their skills. It's designed specifically for African markets and available on the Play Store."
        ],
        'netra_platform': [
            f"{name_prefix}To download Netra: Open Play Store on your Android device, search for 'Netra App', and install it. The download is free and takes just a few minutes.",
            f"{name_prefix}Getting the app: Visit Google Play Store, search 'Netra App', tap install. Once downloaded, you can immediately start browsing services or register as a provider.",
            f"{name_prefix}Download from Play Store: Search for Netra App, click install. The app will guide you through setup whether you're a client or service provider."
        ],
        'download_app': [
            f"{name_prefix}Service providers register by: Downloading the app, signing up with email, creating a detailed service profile, verifying email with OTP, and then they can start receiving client requests.",
            f"{name_prefix}Providers join through: App download, email registration, profile creation with service details, OTP verification, and then they're visible to clients seeking their services.",
            f"{name_prefix}Provider registration: Get app, register with email, build service profile (include skills, experience, portfolio), verify via OTP, and begin offering services."
        ],
        'join_netra_provider': [
            f"{name_prefix}Clients use Netra by: Downloading the app, browsing service categories, checking provider ratings, selecting services, and booking appointments. No lengthy registration required!",
            f"{name_prefix}For clients: Get the app, search for needed services, compare provider reviews and ratings, choose preferred provider, and book directly through the app's scheduling system.",
            f"{name_prefix}Client experience: Download app, immediately browse services, read client reviews, select provider, choose appointment time, and confirm booking - all within minutes."
        ],
        'client_usage': [
            f"{name_prefix}Service categories include: Technical (plumbers, electricians), Creative (designers, photographers), Professional (consultants, tutors), Home services, Personal care, and many specialized fields.",
            f"{name_prefix}We have categories like: Home repair technicians, Creative professionals, Business consultants, Educational services, Healthcare providers, Beauty services, and Technology experts.",
            f"{name_prefix}Categories available: Technical repairs, Creative design, Professional advice, Home maintenance, Education, Healthcare, Beauty, and Automotive services among others."
        ]
    }
    
    if topic in yes_responses:
        response = random.choice(yes_responses[topic])
        # Add new practical suggestion
        new_suggestions = [
            "Would you like to know how to download the Netra app?",
            "Should I explain the registration process in more detail?",
            "Want to know what makes Netra different from other platforms?",
            "Would you like to know about the verification process?",
            "Should I explain how the booking system works?"
        ]
        suggestion = random.choice(new_suggestions)
        return f"{response}\n\n{suggestion}"
    
    return f"{name_prefix}I'd be happy to provide more details! What specific aspect would you like me to explain?"

def handle_no_response(user_session):
    """Handle negative responses to suggestions"""
    user_name = user_session.get('user_name', '')
    name_prefix = f"{user_name}, " if user_name else ""
    
    no_responses = [
        f"{name_prefix}No problem! What else would you like to know about Aidnest Africa or Netra?",
        f"{name_prefix}That's fine! What other aspect of our platform interests you?",
        f"{name_prefix}Understood! What would you prefer to learn about instead?",
        f"{name_prefix}Okay! What other questions do you have about Netra or Aidnest Africa?",
        f"{name_prefix}No worries! What would you like to explore about our services?"
    ]
    return random.choice(no_responses)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").strip()
    user_id = request.remote_addr  # Simple user identification

    if not message:
        return jsonify({"reply": "Please enter a message."}), 400

    try:
        reply = get_fallback_response(message, user_id)

    except Exception as e:
        # If any error occurs, use fallback
        error_responses = [
            "I'm here to help you with Aidnest Africa and Netra! What would you like to know?",
            "Let me assist you with Netra and Aidnest Africa services. What can I help you with?",
            "I'm ready to help you discover Aidnest Africa and Netra. What would you like to explore?"
        ]
        reply = random.choice(error_responses)

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)