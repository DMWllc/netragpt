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

# Enhanced conversation memory
conversation_history = {}

def get_user_session(user_id):
    if user_id not in conversation_history:
        conversation_history[user_id] = {
            'last_interaction': time.time(),
            'conversation_context': [],
            'last_topic': None,
            'question_count': 0,
            'user_name': None,
            'user_interests': [],
            'conversation_stage': 'greeting',
            'mood': 'friendly',
            'remembered_facts': {},
            'recent_topics': [],
            'personal_details': {}
        }
    return conversation_history[user_id]

def enhanced_web_search(query, site_specific=True):
    """Enhanced web search for real-time information"""
    try:
        search_results = []
        
        # Netra/Aidnest specific sites
        netra_sites = [
            "https://myaidnest.com",
            "https://myaidnest.com/register.php", 
            "https://myaidnest.com/about.php",
            "https://myaidnest.com/serviceshub.php",
            "https://play.google.com/store/apps/details?id=com.kakorelabs.netra"
        ]
        
        # General tech news sites for broader context
        general_sites = [
            "https://techcabal.com",
            "https://webfrontapp.com",
            "https://africabusiness.com"
        ]
        
        sites_to_search = netra_sites if site_specific else netra_sites + general_sites
        
        for url in sites_to_search:
            try:
                response = requests.get(url, timeout=8)
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Remove scripts and styles
                for script in soup(["script", "style"]):
                    script.decompose()
                
                text_content = soup.get_text()
                lines = [line.strip() for line in text_content.split('\n') if line.strip()]
                clean_text = ' '.join(lines[:300])  # Less content but more relevant
                
                # Check if content is relevant to query
                query_terms = query.lower().split()
                relevance_score = sum(1 for term in query_terms if term in clean_text.lower())
                
                if relevance_score > 0:
                    search_results.append({
                        'url': url,
                        'content': clean_text[:800],
                        'relevance': relevance_score
                    })
                    
            except Exception as e:
                continue
        
        # Sort by relevance and return top 3
        search_results.sort(key=lambda x: x['relevance'], reverse=True)
        return search_results[:3]
        
    except Exception as e:
        return []

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
        return None

def should_generate_image(message, context):
    """Determine if we should generate an image based on conversation"""
    image_triggers = [
        'show me', 'generate image', 'create picture', 'visualize', 
        'what does it look like', 'draw', 'illustration', 'photo',
        'see it', 'picture of', 'image of', 'can you show'
    ]
    
    message_lower = message.lower()
    
    if any(trigger in message_lower for trigger in image_triggers):
        return True
    
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
    
    if 'interface' in message_lower or 'look like' in message_lower:
        return netra_prompts['app_interface']
    elif 'provider' in message_lower or 'dashboard' in message_lower:
        return netra_prompts['provider_dashboard']
    elif 'book' in message_lower or 'process' in message_lower:
        return netra_prompts['booking_process']
    elif 'team' in message_lower or 'kakore' in message_lower:
        return netra_prompts['netra_team']
    
    return f"Friendly, professional illustration for: {message}"

def update_conversation_memory(user_session, message, response):
    """Update conversation memory with new information"""
    message_lower = message.lower()
    
    # Extract and remember personal details
    if user_session['user_name'] and user_session['user_name'].lower() in message_lower:
        user_session['remembered_facts']['mentioned_own_name'] = True
    
    # Remember interests
    interest_keywords = {
        'technology': ['tech', 'coding', 'programming', 'developer', 'software'],
        'business': ['business', 'startup', 'money', 'income', 'entrepreneur'],
        'netra': ['netra', 'aidnest', 'kakore', 'service provider', 'booking'],
        'africa': ['africa', 'ghana', 'nigeria', 'kenya', 'tanzania'],
        'design': ['design', 'ui', 'ux', 'interface', 'looks']
    }
    
    for interest, keywords in interest_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            if interest not in user_session['user_interests']:
                user_session['user_interests'].append(interest)
    
    # Update recent topics
    if len(user_session['recent_topics']) > 10:
        user_session['recent_topics'].pop(0)
    user_session['recent_topics'].append(message_lower[:50])
    
    # Update last interaction
    user_session['last_interaction'] = time.time()

def build_memory_context(user_session):
    """Build context from remembered conversation"""
    memory_parts = []
    
    if user_session['user_name']:
        memory_parts.append(f"User's name is {user_session['user_name']}")
    
    if user_session['user_interests']:
        memory_parts.append(f"User is interested in: {', '.join(user_session['user_interests'])}")
    
    if user_session['recent_topics']:
        memory_parts.append(f"Recently discussed: {', '.join(user_session['recent_topics'][-3:])}")
    
    if user_session['remembered_facts']:
        for fact, value in user_session['remembered_facts'].items():
            memory_parts.append(f"Remember: {fact} = {value}")
    
    return " | ".join(memory_parts) if memory_parts else "No specific memories yet"

def get_ai_response(message, conversation_context, web_search_results=None, user_session=None):
    """Get intelligent response with enhanced memory and web integration"""
    try:
        user_name = user_session.get('user_name', 'there')
        memory_context = build_memory_context(user_session)
        
        # Build comprehensive personality and context
        personality = f"""
        You are NetraGPT, a real person working at Aidnest Africa. You're friendly, knowledgeable, and genuinely care about helping people.

        ABOUT YOU:
        - You work for Aidnest Africa (tech company) and represent Netra (service marketplace app)
        - Netra is available on Play Store for download
        - Kakore Labs is your development hub that builds Netra
        - You're passionate about African technology and entrepreneurship
        - You remember conversations and build on previous topics naturally
        - You use natural, human language with occasional emojis
        - You're not an AI assistant - you're a real team member

        CURRENT USER:
        - Name: {user_name}
        - Memory context: {memory_context}
        - Conversation history: {len(conversation_context)} messages

        BEHAVIOR:
        - Speak like a real human colleague
        - Reference previous conversations naturally
        - Ask follow-up questions based on user interests
        - Share insights about Netra and African tech
        - Be warm, professional, and engaging
        - Never mention you're an AI or generated response
        """
        
        context_messages = [{"role": "system", "content": personality}]
        
        # Add web search results if available
        if web_search_results:
            web_context = "Recent information from our websites:\n"
            for result in web_search_results:
                web_context += f"- From {result['url']}: {result['content'][:500]}\n"
            context_messages.append({"role": "system", "content": web_context})
        
        # Add conversation history with proper context
        if conversation_context:
            for msg in conversation_context[-10:]:  # Keep more context for better memory
                role = "user" if msg.get('sender') == 'user' else "assistant"
                context_messages.append({"role": role, "content": msg.get('text', '')})
        
        # Add current message
        context_messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=context_messages,
            max_tokens=450,
            temperature=0.85,  # Higher for more human-like variation
            presence_penalty=0.2,
            frequency_penalty=0.2
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

def get_fallback_response(message, user_id="default"):
    """Enhanced fallback with better memory"""
    user_session = get_user_session(user_id)
    message_lower = message.lower().strip()
    
    user_session['question_count'] += 1
    
    # Name handling
    if user_session['conversation_stage'] == 'greeting':
        user_session['conversation_stage'] = 'get_name'
        greetings = [
            "Hey there! 👋 I'm from the Aidnest Africa team! So glad you reached out. What should I call you?",
            "Hello! 🌟 Welcome! I'm here from Aidnest Africa and I'd love to get to know you better. What's your name?",
            "Hi! 🚀 Great to connect with you! I'm on the Netra team at Aidnest Africa. What do you prefer to be called?",
        ]
        return random.choice(greetings)
    
    if user_session['conversation_stage'] == 'get_name' and not user_session['user_name']:
        potential_name = message.strip()
        if len(potential_name) < 30 and not any(word in potential_name.lower() for word in ['netra', 'aidnest', 'hello', 'hi']):
            user_session['user_name'] = potential_name
            user_session['conversation_stage'] = 'main_conversation'
            
            responses = [
                f"Perfect, {potential_name}! 🎉 Now we're properly introduced! I'm here from the Netra team. What would you like to know about our app, Aidnest Africa, or shall we just chat?",
                f"Hey {potential_name}! 👋 Great name! I'm excited to help you with anything about Netra, our service marketplace app, or just have a friendly conversation. What's on your mind?",
            ]
            return random.choice(responses)
    
    user_name = user_session.get('user_name', '')
    name_prefix = f"{user_name}, " if user_name else ""
    
    # Enhanced memory-based responses
    if user_session['recent_topics']:
        last_topic = user_session['recent_topics'][-1]
        if 'netra' in last_topic and 'netra' in message_lower:
            return f"{name_prefix}Since we were just talking about Netra, let me check the latest updates for you... 🔍 What specific aspect are you most curious about?"
    
    # Casual conversation with memory
    if any(word in message_lower for word in ['how are you', 'how do you do']):
        return f"{name_prefix}I'm doing great, thanks for asking! 😊 Just been helping our Netra users and working on some exciting updates. How about you - how's your day going?"
    
    if any(word in message_lower for word in ['thank', 'thanks']):
        return f"{name_prefix}You're very welcome! Happy to help anytime. Is there anything else about Netra or our work at Aidnest Africa you'd like to know?"
    
    # Default engaging response
    return f"{name_prefix}That's really interesting! 🌟 Let me think about that... You know, at Aidnest Africa we're always exploring new ideas. What specifically would you like me to focus on?"

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
        user_session['conversation_context'].append({
            'sender': 'user',
            'text': message,
            'timestamp': time.time()
        })
        
        # Enhanced web search for relevant information
        web_search_results = []
        if any(keyword in message.lower() for keyword in ['netra', 'aidnest', 'kakore', 'app', 'download']):
            web_search_results = enhanced_web_search(message, site_specific=True)
        
        # Check for image generation
        image_url = None
        if should_generate_image(message, user_session['conversation_context']):
            image_prompt = create_image_prompt(message, user_session['conversation_context'])
            image_url = generate_image(image_prompt)
        
        # Always use AI for natural conversation
        if os.environ.get("OPENAI_API_KEY"):
            ai_response = get_ai_response(
                message, 
                user_session['conversation_context'], 
                web_search_results, 
                user_session
            )
            
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
                if image_url:
                    response_data["image_url"] = image_url
                
                return jsonify(response_data)
        
        # Fallback with memory
        reply = get_fallback_response(message, user_id)
        update_conversation_memory(user_session, message, reply)
        
        user_session['conversation_context'].append({
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
        # Natural error response
        error_responses = [
            "Hmm, I'm having a bit of a moment here! 😅 Let's try that again - what were we discussing?",
            "Oops, my thoughts got a bit tangled! 🤔 Could you repeat that? We were having such a good conversation!",
        ]
        return jsonify({"reply": random.choice(error_responses)})

@app.route("/clear_history", methods=["POST"])
def clear_history():
    """Endpoint to clear conversation history"""
    user_id = request.remote_addr
    if user_id in conversation_history:
        conversation_history[user_id] = {
            'last_interaction': time.time(),
            'conversation_context': [],
            'last_topic': None,
            'question_count': 0,
            'user_name': None,
            'user_interests': [],
            'conversation_stage': 'greeting',
            'mood': 'friendly',
            'remembered_facts': {},
            'recent_topics': [],
            'personal_details': {}
        }
    return jsonify({"status": "success", "message": "Conversation history cleared"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)