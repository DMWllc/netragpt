from flask import Flask, request, jsonify, render_template, session # type: ignore
from flask_cors import CORS # type: ignore
from openai import OpenAI # type: ignore
import os
import random
import re
import time
import secrets
from datetime import timedelta
import base64 # type: ignore

# Import from our new modules
from session_manager import (
    initialize_user_session, get_user_session, is_session_expired,
    get_session_time_remaining, get_session_warning, cleanup_expired_sessions,
    update_conversation_memory, enhance_memory_retention, get_memory_context,
    session_conversations
)
from scientific_visualizations import process_scientific_content, format_scientific_response
from mathematical_utils import process_mathematical_content, format_mathematical_response
from web_utils import (
    get_external_knowledge, handle_special_queries, get_dynamic_netra_info,
    analyze_query_domain, build_diverse_context
)
from knowledge_base import KNOWLEDGE_DOMAINS, COMPANY_INFO

# IMPORT THE NEW ENGINES
from physics_engine import physics_engine
from chemistry_engine import chemistry_engine
from biology_engine import biology_engine
from netra_engine import netra_engine

app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", secrets.token_hex(32))
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=20)

CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def route_to_engine(message):
    """Determine which engine to use based on message content"""
    message_lower = message.lower()
    
    # EXPANDED Netra keywords for better detection
    netra_keywords = [
        # App name and company
        'netra', 'strobid', 'jovira',
        
        # Account related
        'account', 'password', 'login', 'signup', 'register', 'sign up', 'log in',
        'create account', 'new account', 'delete account', 'close account',
        'verify', 'verification', 'otp', 'code', 'confirm',
        'forgot password', 'reset password', 'change password',
        
        # Support related
        'support', 'help', 'assist', 'customer service', 'contact',
        'issue', 'problem', 'ticket', 'complaint', 'not working',
        'broken', 'error', 'urgent', 'help desk',
        
        # Payment related
        'payment', 'pay', 'billing', 'invoice', 'subscription',
        'subscribe', 'premium', 'plan', 'upgrade', 'downgrade',
        'refund', 'money', 'transaction', 'charge',
        
        # Features
        'notification', 'alert', 'setting', 'preference',
        'profile', 'photo', 'picture', 'avatar',
        'message', 'chat', 'conversation',
        
        # Service related
        'provider', 'client', 'service', 'book', 'booking',
        'hire', 'review', 'rating', 'feedback',
        
        # How-to questions
        'how to', 'how do i', 'can i', 'where do i',
        'what is netra', 'tell me about netra',
        'netra app', 'about netra'
    ]
    
    # Check for Netra-related queries (HIGHEST PRIORITY)
    if any(keyword in message_lower for keyword in netra_keywords):
        print(f"🔍 Routing to Netra Engine: {message[:50]}...")
        return 'netra'
    
    # Physics queries
    physics_keywords = [
        'physics', 'force', 'velocity', 'acceleration', 'energy',
        'projectile', 'pendulum', 'circular motion', 'inclined plane',
        'newton', 'kinematics', 'mechanics', 'gravity', 'friction',
        'momentum', 'torque', 'electric field', 'magnetic field'
    ]
    
    if any(keyword in message_lower for keyword in physics_keywords):
        return 'physics'
    
    # Chemistry queries
    chemistry_keywords = [
        'chemistry', 'chemical', 'reaction', 'molecule', 'compound',
        'organic', 'inorganic', 'periodic', 'bond', 'reaction',
        'synthesis', 'aromatic', 'benzene', 'friedel', 'crafts',
        'atom', 'element', 'periodic table', 'organic chemistry'
    ]
    
    if any(keyword in message_lower for keyword in chemistry_keywords):
        return 'chemistry'
    
    # Biology queries
    biology_keywords = [
        'biology', 'biological', 'cell', 'dna', 'protein',
        'metabolism', 'krebs', 'glycolysis', 'mitochondria',
        'enzyme', 'respiration', 'photosynthesis', 'krebs cycle',
        'cell structure', 'dna replication', 'protein synthesis'
    ]
    
    if any(keyword in message_lower for keyword in biology_keywords):
        return 'biology'
    
    # Default to general AI
    return 'general'

def format_netra_response(engine_response):
    """Format Netra engine response for the chat"""
    if not engine_response:
        return None
    
    # Extract response parts
    response = engine_response.get('response', '')
    suggestions = engine_response.get('suggestions', [])
    confidence = engine_response.get('confidence', 95)
    
    # Add help center reference if available
    help_url = engine_response.get('help_center_url', 'https://netra.strobid.com/help')
    
    # Format the response with proper structure
    formatted_response = response
    
    # Add help center reference if not already included
    if help_url and 'help' not in response.lower():
        formatted_response += f"\n\n📚 For more details, visit our Help Center: {help_url}"
    
    return formatted_response

def format_science_response(engine_response, engine_type):
    """Format science engine responses"""
    if not engine_response:
        return None
    
    response_parts = []
    
    # Add visualizations if available
    if 'visualizations' in engine_response and engine_response['visualizations']:
        for viz in engine_response['visualizations']:
            response_parts.append(f"📊 **{viz.get('type', 'Diagram').replace('_', ' ').title()}**")
    
    # Add calculations if available
    if 'calculations' in engine_response and engine_response['calculations']:
        response_parts.append("🧮 **Calculations:**")
        for calc in engine_response['calculations']:
            if isinstance(calc, dict):
                for key, value in calc.items():
                    response_parts.append(f"• {key.replace('_', ' ').title()}: {value}")
    
    # Add explanations if available
    if 'explanations' in engine_response and engine_response['explanations']:
        response_parts.append("📚 **Explanation:**")
        response_parts.extend(engine_response['explanations'])
    
    # Add predictions if available
    if 'predictions' in engine_response and engine_response['predictions']:
        for pred in engine_response['predictions']:
            response_parts.append(f"🔮 **Prediction**: {pred.get('prediction', '')}")
            if 'explanation' in pred:
                response_parts.append(f"*{pred['explanation']}*")
    
    if response_parts:
        return "\n\n".join(response_parts)
    
    return None

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    # Clean up expired sessions periodically
    if random.random() < 0.1:
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
        
        # ROUTE TO APPROPRIATE ENGINE
        engine_type = route_to_engine(message)
        engine_response = None
        ai_response = None
        
        print(f"🎯 Engine selected: {engine_type}")
        
        if engine_type == 'netra':
            # Use Netra Engine for customer service
            try:
                engine_response = netra_engine.process_query(
                    message=message, 
                    user_id=session.get('user_id', 'anonymous')
                )
                
                if engine_response and engine_response.get('response'):
                    ai_response = format_netra_response(engine_response)
                    
                    # Store suggestions for frontend
                    suggestions = engine_response.get('suggestions', [])
                else:
                    # Fallback if engine returns empty
                    ai_response = "I'd be happy to help you with Netra! What specific information are you looking for? You can ask about creating an account, payments, notifications, or contact support."
                    suggestions = [
                        "How to create a Netra account",
                        "How payments work on Netra",
                        "Contact Netra support",
                        "Reset my password"
                    ]
                    
            except Exception as e:
                print(f"Netra Engine error: {e}")
                ai_response = "I'm here to help with Netra! While I'm having a quick technical moment, you can always visit our Help Center at https://netra.strobid.com/help for immediate assistance. What would you like to know?"
                suggestions = [
                    "How to create a Netra account",
                    "How payments work on Netra",
                    "Contact Netra support"
                ]
            
        elif engine_type == 'physics':
            # Use Physics Engine
            try:
                engine_response = physics_engine.process_physics_query(message)
                ai_response = format_science_response(engine_response, 'physics')
            except Exception as e:
                print(f"Physics Engine error: {e}")
                ai_response = None
            
        elif engine_type == 'chemistry':
            # Use Chemistry Engine
            try:
                engine_response = chemistry_engine.process_chemistry_query(message)
                ai_response = format_science_response(engine_response, 'chemistry')
            except Exception as e:
                print(f"Chemistry Engine error: {e}")
                ai_response = None
            
        elif engine_type == 'biology':
            # Use Biology Engine
            try:
                engine_response = biology_engine.process_biology_query(message)
                ai_response = format_science_response(engine_response, 'biology')
            except Exception as e:
                print(f"Biology Engine error: {e}")
                ai_response = None
            
        else:
            # Use existing OpenAI flow for general queries
            ai_response = get_ai_response(message, user_session['conversation_context'], user_session)
            suggestions = []
        
        # If no response from specialized engines, fallback to general AI
        if not ai_response and engine_type != 'netra':
            ai_response = get_ai_response(message, user_session['conversation_context'], user_session)
            suggestions = []
        
        if ai_response:
            # Update memory with this interaction
            enhance_memory_retention(user_session, message, ai_response)
            update_conversation_memory(user_session, message, ai_response)
            
            # Add to conversation context
            user_session['conversation_context'].append({
                'sender': 'assistant', 
                'text': ai_response, 
                'timestamp': time.time()
            })
            
            response_data = {"reply": ai_response}
            
            # Add engine metadata
            response_data["engine_used"] = engine_type
            
            # Add suggestions for Netra responses
            if engine_type == 'netra' and suggestions:
                response_data["suggestions"] = suggestions
            
            # Add help center link for Netra
            if engine_type == 'netra':
                response_data["help_center"] = "https://netra.strobid.com/help"
            
            # Add session warning if needed
            if session_warning:
                response_data["session_warning"] = session_warning
                response_data["time_remaining"] = get_session_time_remaining()
            
            return jsonify(response_data)
        
        # Ultimate fallback response
        fallback_responses = [
            "I'm here to help! For Netra-specific questions, you can visit https://netra.strobid.com/help or let me know what you'd like to know about Netra.",
            "I'd be happy to assist you with Netra! What would you like to know? You can ask about accounts, payments, features, or how to get started.",
            "I'm your Netra assistant! Feel free to ask me anything about the Netra app - from creating an account to managing payments."
        ]
        
        reply = random.choice(fallback_responses)
        enhance_memory_retention(user_session, message, reply)
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
            "I'm experiencing some technical difficulties right now. For Netra support, please visit https://netra.strobid.com/help directly! 🔄",
            "My services seem to be temporarily unavailable. You can visit https://netra.strobid.com/help for Netra information! 🌐",
        ]
        return jsonify({"reply": random.choice(error_responses)})

def get_ai_response(message, conversation_context, user_session=None):
    """Enhanced AI response with memory, calculations, and proper formatting"""
    try:
        user_name = user_session.get('user_name', 'there')
        
        # Check for special queries first (time, calculations, etc.)
        special_response = handle_special_queries(message)
        if special_response:
            return special_response
        
        # Process scientific content (physics, biology, chemistry)
        scientific_content = process_scientific_content(message)
        if any([scientific_content['physics_visualizations'], 
                scientific_content['biology_visualizations'],
                scientific_content['chemical_mechanisms']]):
            
            scientific_response = format_scientific_response(scientific_content)
            if scientific_response:
                return scientific_response
        
        # Process mathematical content (LaTeX, visualizations, calculations)
        math_content = process_mathematical_content(message)
        if any(math_content.values()):
            user_session['mathematical_requests'] = user_session.get('mathematical_requests', 0) + 1
            math_response = format_mathematical_response(math_content)
            if math_response:
                return math_response
        
        # Analyze which knowledge domains are relevant
        relevant_domains = analyze_query_domain(message)
        
        # Get external knowledge for factual queries
        external_info = get_external_knowledge(message)
        if external_info['sources_used']:
            user_session['external_searches'] = user_session.get('external_searches', 0) + 1
            print(f"External search performed. Sources used: {external_info['sources_used']}")
        
        # Update user preferences based on usage
        if len(user_session.get('preferred_domains', [])) < 5:
            for domain in relevant_domains:
                if domain not in user_session.get('preferred_domains', []):
                    user_session.setdefault('preferred_domains', []).append(domain)
        
        # Get diverse context including memory, Netra information and external research
        diverse_context = build_diverse_context(user_session, relevant_domains, message, external_info)
        
        # Build comprehensive system message with enhanced memory
        system_message = f"""
        You are Jovira, an AI assistant created by Strobid (Strobid's programming hub). 
        You serve as a team member for Netra but have diverse knowledge across multiple domains.

        COMPANY INFORMATION:
        - CEO: Nowamaani Donath
        - Companies: Strobid, Netra App
        - Location: Kampala, Uganda, East Africa
        - Timezone: East Africa Time (EAT, UTC+3)
        - Website: https://strobid.com
        - Netra Help Center: https://netra.strobid.com/help

        YOUR CAPABILITIES:
        - Primary role: Netra customer service and support
        - Secondary: General AI assistant with diverse knowledge
        - Mathematical calculations and problem solving
        - Code generation and explanation
        - External research via Wikipedia and Google
        - Memory retention across conversations
        - LaTeX equation rendering and mathematical visualizations
        - Physics diagrams and calculations
        - Biology illustrations and systems
        - Chemical reaction mechanisms
        - Scientific visualizations across all domains

        CURRENT CONTEXT:
        {diverse_context}

        RESPONSE GUIDELINES:
        - For Netra/service queries: Provide specific, accurate information using the official help center at https://netra.strobid.com/help
        - For calculations: Show step-by-step working and final result in code blocks
        - For code: Format code properly using markdown code blocks with language specification
        - For mathematical expressions: Use LaTeX formatting for complex equations
        - For scientific queries: Create appropriate diagrams and explanations
        - For factual queries: Use external research when available, cite sources when helpful
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
        - Relevant domains: {', '.join([KNOWLEDGE_DOMAINS[d]['name'] for d in relevant_domains]) if relevant_domains else 'General'}
        - External sources used: {', '.join(external_info['sources_used']) if external_info['sources_used'] else 'None'}
        """
        
        context_messages = [{"role": "system", "content": system_message}]
        
        # Add conversation history
        if conversation_context:
            for msg in conversation_context[-10:]:
                role = "user" if msg.get('sender') == 'user' else "assistant"
                context_messages.append({"role": role, "content": msg.get('text', '')})
        
        # Add current message
        context_messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=context_messages,
            max_tokens=800,
            temperature=0.7
        )
        
        ai_response = response.choices[0].message.content.strip()
        
        # Enhance memory with this interaction
        enhance_memory_retention(user_session, message, ai_response)
        
        return ai_response
        
    except Exception as e:
        print(f"AI response error: {e}")
        return "I'm having trouble accessing information right now. For Netra-specific questions, please visit https://netra.strobid.com/help directly."

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
        "🔄 **New Session Started**! Welcome back! You now have 20 minutes to chat with Jovira. How can I help you with Netra today?",
        "🌟 **Fresh Session Activated**! Hello again! Your 20-minute chat timer has started. What would you like to know about Netra?",
        "🆕 **New Chat Session**! Great to see you! You have 20 minutes for this conversation. Ask me anything about Netra!"
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

@app.route("/generate_scientific_diagram", methods=["POST"])
def generate_scientific_diagram():
    """Endpoint to generate scientific diagrams"""
    try:
        data = request.get_json()
        diagram_type = data.get("type", "")
        parameters = data.get("parameters", {})
        
        if not diagram_type:
            return jsonify({"error": "No diagram type provided"}), 400
        
        from scientific_visualizations import (
            create_physics_visualization, 
            create_biology_visualization, 
            create_chemical_mechanism_visualization
        )
        
        if diagram_type.startswith('physics_'):
            physics_type = diagram_type.replace('physics_', '')
            image_data = create_physics_visualization(physics_type, parameters)
        elif diagram_type.startswith('biology_'):
            biology_type = diagram_type.replace('biology_', '')
            image_data = create_biology_visualization(biology_type, parameters)
        elif diagram_type.startswith('chemistry_'):
            chemistry_type = diagram_type.replace('chemistry_', '')
            image_data = create_chemical_mechanism_visualization(chemistry_type, parameters)
        else:
            return jsonify({"error": "Invalid diagram type"}), 400
        
        if image_data:
            return jsonify({
                "image_data": image_data,
                "message": f"🔬 Generated {diagram_type.replace('_', ' ').title()} diagram!"
            })
        else:
            return jsonify({"error": "Failed to generate diagram"}), 500
            
    except Exception as e:
        print(f"Scientific diagram generation error: {e}")
        return jsonify({"error": "Error generating scientific diagram"}), 500

if __name__ == "__main__":
    # Get port from environment variable or default to 8080 for Railway
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)