from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import os
import random
import re

app = Flask(__name__)
CORS(app)

openai.api_key = os.environ.get("OPENAI_API_KEY")

# Predefined responses for Aidnest Africa and Netra
def get_fallback_response(message):
    message_lower = message.lower().strip()
    
    # Enhanced greeting detection
    greeting_patterns = [
        r'hello', r'hi', r'hey', r'greetings', r'good morning', r'good afternoon', 
        r'good evening', r'howdy', r'yo', r'what\'s up', r'sup', r'hi there',
        r'hello there', r'hey there', r'good day', r'hi bot', r'hello bot'
    ]
    
    # Check if it's a greeting
    is_greeting = any(re.search(pattern, message_lower) for pattern in greeting_patterns)
    
    if is_greeting:
        greeting_responses = [
            "Hello! 👋 I'm NetraGPT, your assistant for Aidnest Africa and the Netra platform. How can I help you today?",
            "Hi there! 🌟 Welcome to NetraGPT. I'm here to tell you all about Aidnest Africa and our Netra platform. What would you like to know?",
            "Greetings! 🚀 I'm NetraGPT, powered by Aidnest Africa. Ready to explore how we're connecting skilled professionals with clients across Africa?",
            "Hey! 💫 I'm your NetraGPT assistant. Here to help you discover everything about Aidnest Africa and our digital solutions!"
        ]
        return random.choice(greeting_responses)
    
    # Main content responses with suggestions
    content_responses = {
        'aidnest_africa': {
            'response': "Aidnest Africa is an organization focused on creating smart, practical digital solutions that make life and work easier for people across Africa. We use technology to solve real community problems — from access to reliable services to tools that empower local professionals and businesses.",
            'suggestions': [
                "Would you like me to tell you about our Netra platform?",
                "Should I explain how we create opportunities through technology?",
                "Want to know more about our vision for digital solutions in Africa?"
            ]
        },
        'netra_platform': {
            'response': "Netra is our flagship digital platform that connects people to trusted service providers — technicians, creatives, professionals, and more. Think of it as a bridge between skilled individuals and clients who need their services. Built in partnership with Kakore Labs.",
            'suggestions': [
                "Would you like to know how Netra helps service providers?",
                "Should I explain how clients find trusted professionals on Netra?",
                "Want to learn about the smart tools Netra offers to professionals?"
            ]
        },
        'netra_features': {
            'response': "Netra makes it easy to find verified providers, view their ratings, and book them directly. Beyond just a marketplace, Netra has smart tools that help professionals manage their work better — handling client requests, secure communication, and job tracking.",
            'suggestions': [
                "Would you like me to explain how the provider verification works?",
                "Should I tell you about the booking system?",
                "Want to know more about the professional tools available?"
            ]
        },
        'netragpt_assistant': {
            'response': "I'm NetraGPT! 🤖 An AI-powered assistant that supports both clients and providers in real time — answering questions, offering guidance, and simplifying the process of connecting people. I'm here to make your experience smoother!",
            'suggestions': [
                "Would you like to know what kind of questions I can help with?",
                "Should I explain how I assist both clients and providers?",
                "Want to learn about my real-time support capabilities?"
            ]
        },
        'vision_mission': {
            'response': "At Aidnest Africa, our vision is to create opportunities through technology — giving visibility to skilled Africans, promoting trust, and helping communities grow in a digital age. We believe in building products in Africa, for Africa, by people who understand its challenges and potential.",
            'suggestions': [
                "Would you like to know more about our community impact?",
                "Should I explain how we promote trust in digital services?",
                "Want to learn about our approach to African-focused solutions?"
            ]
        },
        'services_providers': {
            'response': "Netra connects you with various service providers including technicians, creatives, consultants, and other professionals. All providers are verified to ensure quality and reliability for our clients.",
            'suggestions': [
                "Would you like me to list the types of professionals available?",
                "Should I explain the verification process for providers?",
                "Want to know how providers benefit from using Netra?"
            ]
        },
        'default': {
            'response': "That's an interesting question about Aidnest Africa and Netra!",
            'suggestions': [
                "Would you like to know about our Netra platform?",
                "Should I explain what Aidnest Africa does?",
                "Want to learn how we're connecting professionals with clients?",
                "Would you like to know about our vision for technology in Africa?"
            ]
        }
    }
    
    # Keyword mapping with priority
    keyword_mapping = {
        'aidnest': 'aidnest_africa',
        'organization': 'aidnest_africa',
        'company': 'aidnest_africa',
        'what is aidnest': 'aidnest_africa',
        'netra': 'netra_platform',
        'platform': 'netra_platform',
        'digital platform': 'netra_platform',
        'features': 'netra_features',
        'tools': 'netra_features',
        'verification': 'netra_features',
        'booking': 'netra_features',
        'netragpt': 'netragpt_assistant',
        'ai assistant': 'netragpt_assistant',
        'chatbot': 'netragpt_assistant',
        'vision': 'vision_mission',
        'mission': 'vision_mission',
        'goal': 'vision_mission',
        'purpose': 'vision_mission',
        'services': 'services_providers',
        'providers': 'services_providers',
        'professionals': 'services_providers',
        'technicians': 'services_providers',
        'creatives': 'services_providers'
    }
    
    # Find the best matching content
    selected_topic = 'default'
    for keyword, topic in keyword_mapping.items():
        if keyword in message_lower:
            selected_topic = topic
            break
    
    content = content_responses[selected_topic]
    response = content['response']
    suggestion = random.choice(content['suggestions'])
    
    return f"{response}\n\n{suggestion}"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"reply": "Please enter a message."}), 400

    try:
        # Enhanced greeting detection - handle without API
        greeting_patterns = [
            r'hello', r'hi', r'hey', r'greetings', r'good morning', r'good afternoon', 
            r'good evening', r'howdy', r'yo', r'what\'s up', r'sup', r'hi there',
            r'hello there', r'hey there', r'good day'
        ]
        
        is_greeting = any(re.search(pattern, message.lower()) for pattern in greeting_patterns)
        
        if is_greeting:
            reply = get_fallback_response(message)
        else:
            # For non-greeting content that needs deeper understanding, use fallback
            # but you can modify this to use OpenAI for complex queries
            reply = get_fallback_response(message)
            
            # Uncomment below if you want to use OpenAI for complex queries
            # response = openai.ChatCompletion.create(
            #     model="gpt-3.5-turbo",
            #     messages=[{"role": "user", "content": message}],
            #     max_tokens=200
            # )
            # reply = response.choices[0].message.content.strip()

    except Exception as e:
        # If any error occurs, use our fallback system
        if "quota" in str(e).lower() or "billing" in str(e).lower() or "exceeded" in str(e).lower():
            reply = get_fallback_response(message)
        else:
            reply = f"That's all I have for you for now. Try me again later when I have advanced. 💬"

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)