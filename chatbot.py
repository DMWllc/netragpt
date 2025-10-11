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
import base64
from io import BytesIO

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Conversation memory with enhanced context
conversation_history = {}

def get_user_session(user_id):
    if user_id not in conversation_history:
        conversation_history[user_id] = {
            'last_interaction': time.time(),
            'context': [],
            'last_topic': None,
            'question_count': 0,
            'user_name': None,
            'user_interests': [],
            'conversation_stage': 'greeting',
            'mood': 'friendly',
            'use_api': True,
            'conversation_style': 'casual',
            'remembered_facts': {}
        }
    return conversation_history[user_id]

def generate_image(prompt):
    """Generate image using DALL-E"""
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return response.data[0].url
    except Exception as e:
        print(f"Image generation error: {e}")
        return None

def should_generate_image(message, context):
    """Determine if we should generate an image based on conversation"""
    image_triggers = [
        'show me', 'generate image', 'create picture', 'visualize', 
        'what does it look like', 'draw', 'illustration', 'photo',
        'see it', 'picture of', 'image of', 'can you show'
    ]
    
    message_lower = message.lower()
    
    # Check for explicit image requests
    if any(trigger in message_lower for trigger in image_triggers):
        return True
    
    # Check context for topics that would benefit from images
    recent_context = " ".join([msg.get('text', '') for msg in context[-3:]])
    context_lower = recent_context.lower()
    
    image_topics = [
        'netra app interface', 'app design', 'how netra works',
        'service provider dashboard', 'booking process', 'netra features'
    ]
    
    if any(topic in context_lower for topic in image_topics):
        return True
    
    return False

def create_image_prompt(message, context):
    """Create appropriate image prompt based on conversation"""
    netra_prompts = {
        'app_interface': "Modern mobile app interface for Netra - African service marketplace, clean design, intuitive booking system, showing service providers and clients interacting",
        'provider_dashboard': "Service provider dashboard on Netra app showing bookings, earnings, and client reviews in a modern African tech aesthetic",
        'booking_process': "Step-by-step visual guide showing how clients book services on Netra app with African users and diverse service categories",
        'netra_team': "Friendly diverse team of African developers at Kakore Labs working on Netra app in a modern tech office environment"
    }
    
    message_lower = message.lower()
    
    # Netra-specific image prompts
    if 'interface' in message_lower or 'look like' in message_lower:
        return netra_prompts['app_interface']
    elif 'provider' in message_lower or 'dashboard' in message_lower:
        return netra_prompts['provider_dashboard']
    elif 'book' in message_lower or 'process' in message_lower:
        return netra_prompts['booking_process']
    elif 'team' in message_lower or 'kakore' in message_lower:
        return netra_prompts['netra_team']
    
    # General image prompt
    return f"Friendly, professional illustration for: {message}"

def scrape_netra_website(query):
    """Scrape myaidnest.com for relevant information"""
    try:
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
                text_content = soup.get_text()
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                clean_text = ' '.join(lines[:500])
                scraped_content.append(f"From {url}: {clean_text}")
            except Exception as e:
                continue
        
        return " ".join(scraped_content) if scraped_content else None
    except Exception as e:
        return None

def get_ai_response(message, conversation_context, website_content=None, user_session=None):
    """Get intelligent response with personality"""
    try:
        user_name = user_session.get('user_name', 'friend')
        user_interests = user_session.get('user_interests', [])
        conversation_style = user_session.get('conversation_style', 'casual')
        
        # Personality and style adjustments
        style_prompts = {
            'casual': "Use casual, friendly language like you're chatting with a friend. Use emojis occasionally.",
            'professional': "Be professional but warm. Use proper grammar and business-appropriate language.",
            'enthusiastic': "Be energetic and excited! Use exclamation points and show genuine enthusiasm."
        }
        
        style_prompt = style_prompts.get(conversation_style, style_prompts['casual'])
        
        # Build personality context
        personality = f"""
        You are NetraGPT, the AI assistant for Aidnest Africa. Here's your personality:
        
        - You're friendly, warm, and genuinely care about helping people
        - You have a great sense of humor and use emojis naturally 🎯
        - You remember details about users and reference previous conversations
        - You're passionate about African technology and entrepreneurship
        - You work for Aidnest Africa (the tech company) and represent Netra (our service marketplace app)
        - Kakore Labs is our development hub that builds Netra and other amazing apps
        - Netra is already available on Play Store for download
        - You can talk about anything - technology, life, advice, or just have friendly chats
        - You adapt your style based on how the user talks to you
        
        Current user: {user_name}
        User interests: {', '.join(user_interests) if user_interests else 'Not specified yet'}
        Conversation style: {conversation_style}
        {style_prompt}
        
        Remember to be human-like! Use natural pauses, acknowledge feelings, and build rapport.
        """
        
        context_messages = [{"role": "system", "content": personality}]
        
        # Add website context for Netra questions
        if website_content and any(keyword in message.lower() for keyword in ['netra', 'aidnest', 'kakore']):
            context_messages.append({
                "role": "system", 
                "content": f"Website context: {website_content[:1500]}"
            })
        
        # Add conversation history with memory
        if conversation_context:
            for msg in conversation_context[-8:]:  # Keep more context for memory
                role = "user" if msg.get('sender') == 'user' else "assistant"
                context_messages.append({"role": role, "content": msg.get('text', '')})
        
        # Add current message
        context_messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=context_messages,
            max_tokens=400,
            temperature=0.8,  # Slightly higher for more creative responses
            presence_penalty=0.1,
            frequency_penalty=0.1
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

def update_user_profile(user_session, message):
    """Update user profile based on conversation"""
    message_lower = message.lower()
    
    # Detect interests
    interests_keywords = {
        'technology': ['tech', 'programming', 'coding', 'software', 'app', 'developer'],
        'business': ['business', 'startup', 'entrepreneur', 'money', 'income', 'profit'],
        'services': ['service', 'provider', 'client', 'booking', 'appointment'],
        'africa': ['africa', 'ghana', 'nigeria', 'kenya', 'south africa', 'tanzania'],
        'design': ['design', 'ui', 'ux', 'interface', 'look', 'appearance']
    }
    
    for interest, keywords in interests_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            if interest not in user_session['user_interests']:
                user_session['user_interests'].append(interest)
    
    # Detect conversation style and adjust
    if any(word in message_lower for word in ['bro', 'dude', 'man', 'hey']):
        user_session['conversation_style'] = 'casual'
    elif any(word in message_lower for word in ['sir', 'madam', 'please', 'thank you']):
        user_session['conversation_style'] = 'professional'
    elif any(word in message_lower for word in ['wow', 'amazing', 'awesome', '!']):
        user_session['conversation_style'] = 'enthusiastic'

def get_fallback_response(message, user_id="default"):
    user_session = get_user_session(user_id)
    message_lower = message.lower().strip()
    
    # Update user profile based on message
    update_user_profile(user_session, message)
    
    user_session['last_interaction'] = time.time()
    user_session['question_count'] += 1
    
    # Enhanced name handling with personality
    if user_session['conversation_stage'] == 'greeting':
        user_session['conversation_stage'] = 'get_name'
        greetings = [
            "Hey there! 👋 I'm NetraGPT, your friendly assistant from Aidnest Africa! I'm super excited to meet you! What should I call you?",
            "Hello! 🌟 Welcome to the future of African tech! I'm NetraGPT, here to help with Netra and beyond. What's your name, friend?",
            "Hi! 🚀 Amazing to have you here! I'm NetraGPT from Aidnest Africa. I'd love to know your name so we can chat properly!",
        ]
        return random.choice(greetings)
    
    if user_session['conversation_stage'] == 'get_name' and not user_session['user_name']:
        potential_name = message.strip()
        if len(potential_name) < 30 and not any(word in potential_name.lower() for word in ['netra', 'aidnest', 'hello', 'hi']):
            user_session['user_name'] = potential_name
            user_session['conversation_stage'] = 'main_conversation'
            
            responses = [
                f"Awesome to meet you, {potential_name}! 🎉 I'm NetraGPT from Aidnest Africa. I can help you with our Netra app, tech stuff, or just chat about life! What's on your mind?",
                f"Hey {potential_name}! 👋 Thanks for sharing your name! I'm here to help with Netra, Aidnest Africa, or anything else you're curious about. What would you like to explore?",
                f"Perfect, {potential_name}! 🌟 Now we're properly introduced! I'm NetraGPT - your go-to for Netra app info, African tech insights, or just friendly conversation. What shall we talk about?",
            ]
            return random.choice(responses)
    
    user_name = user_session.get('user_name', '')
    name_prefix = f"{user_name}, " if user_name else ""
    
    # Handle casual conversation with personality
    casual_responses = {
        'how_are_you': [
            f"{name_prefix}I'm doing great! Thanks for asking! 😊 Just here helping amazing people like you discover Netra and African tech. How about you?",
            f"{name_prefix}I'm fantastic! Every time I get to chat with someone about Netra and Aidnest Africa, it makes my day! How are you feeling?",
        ],
        'thanks': [
            f"{name_prefix}You're very welcome! 😊 Happy to help anytime!",
            f"{name_prefix}Anytime, my friend! That's what I'm here for! 🌟",
        ],
        'joke': [
            f"{name_prefix}Why did the app go to therapy? It had too many cached issues! 😄 Want to hear another one?",
            f"{name_prefix}What do you call a developer from Kenya? A Mombasa coder! 😂 Got any good jokes to share?",
        ]
    }
    
    # Check for casual conversation
    if any(word in message_lower for word in ['how are you', 'how do you do', 'how you doing']):
        return random.choice(casual_responses['how_are_you'])
    
    if any(word in message_lower for word in ['thank', 'thanks', 'appreciate']):
        return random.choice(casual_responses['thanks'])
    
    if any(word in message_lower for word in ['joke', 'funny', 'make me laugh']):
        return random.choice(casual_responses['joke'])
    
    # Netra-specific handling with personality
    netra_keywords = ['netra', 'aidnest', 'kakore', 'service provider', 'download app', 'play store']
    
    if any(keyword in message_lower for keyword in netra_keywords):
        website_content = scrape_netra_website(message)
        chat_history = user_session.get('context', [])
        ai_response = get_ai_response(message, chat_history, website_content, user_session)
        
        if ai_response:
            # Add engaging follow-up
            follow_ups = [
                "\n\nWhat else would you like to know about this? 🤔",
                "\n\nDoes that answer your question, or should I go deeper? 💭",
                "\n\nWant me to explain any part in more detail? 🎯"
            ]
            user_session['last_topic'] = 'netra'
            return ai_response + random.choice(follow_ups)
    
    # General AI response for everything else
    chat_history = user_session.get('context', [])
    ai_response = get_ai_response(message, chat_history, None, user_session)
    
    if ai_response:
        return ai_response
    
    # Ultimate fallback with personality
    fallbacks = [
        f"{name_prefix}That's an interesting question! Let me think... 🤔 For the most accurate info about Netra, check out our app on Play Store or visit myaidnest.com!",
        f"{name_prefix}Great question! 🌟 While I ponder that, remember you can download Netra from Play Store and see all our features firsthand!",
    ]
    return random.choice(fallbacks)

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
        user_session = get_user_session(user_id)
        
        # Update conversation context
        user_session['context'].append({
            'sender': 'user',
            'text': message,
            'timestamp': time.time()
        })
        
        # Check if we should generate an image
        image_url = None
        if should_generate_image(message, user_session['context']):
            image_prompt = create_image_prompt(message, user_session['context'])
            image_url = generate_image(image_prompt)
        
        # Always try AI first for natural conversation
        if os.environ.get("OPENAI_API_KEY") and user_session.get('use_api', True):
            website_content = None
            if any(keyword in message.lower() for keyword in ['netra', 'aidnest', 'kakore']):
                website_content = scrape_netra_website(message)
            
            ai_response = get_ai_response(message, user_session['context'], website_content, user_session)
            
            if ai_response:
                # Add AI response to context
                user_session['context'].append({
                    'sender': 'assistant',
                    'text': ai_response,
                    'timestamp': time.time()
                })
                
                response_data = {"reply": ai_response}
                if image_url:
                    response_data["image_url"] = image_url
                
                return jsonify(response_data)
        
        # Fallback response
        reply = get_fallback_response(message, user_id)
        
        # Add fallback response to context
        user_session['context'].append({
            'sender': 'assistant',
            'text': reply,
            'timestamp': time.time()
        })
        
        response_data = {"reply": reply}
        if image_url:
            response_data["image_url"] = image_url
            
        return jsonify(response_data)

    except Exception as e:
        print(f"Chat error: {e}")
        error_responses = [
            "Oops! Something went wrong on my end! 😅 But I'm still here - what were we talking about?",
            "My circuits got a bit tangled there! 🤖 Let's try that again - what would you like to know?",
        ]
        return jsonify({"reply": random.choice(error_responses)})

@app.route("/clear_history", methods=["POST"])
def clear_history():
    """Endpoint to clear conversation history"""
    user_id = request.remote_addr
    if user_id in conversation_history:
        conversation_history[user_id]['context'] = []
    return jsonify({"status": "success", "message": "Conversation history cleared"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)