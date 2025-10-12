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
import json

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Enhanced conversation memory with persistent storage
conversation_history = {}

# Company and Team Information
COMPANY_INFO = {
    "kakore_labs": {
        "name": "Kakore Labs",
        "description": "Kakore Labs is the innovative development hub and technical arm of Aidnest Africa, specializing in creating cutting-edge digital solutions for African markets.",
        "focus_areas": [
            "Mobile App Development",
            "Web Platforms", 
            "AI and Machine Learning",
            "Cloud Infrastructure",
            "UI/UX Design",
            "Digital Transformation"
        ],
        "key_projects": [
            "Netra - Service Marketplace App",
            "Autra - Automotive Services Platform",
            "Aidnest Africa Main Website",
            "Various Enterprise Solutions"
        ],
        "expertise": [
            "Flutter & Dart for cross-platform mobile apps",
            "Python Django & Flask for backend services",
            "React.js & Vue.js for modern web interfaces",
            "PostgreSQL & MongoDB for database solutions",
            "AWS & Google Cloud for scalable infrastructure",
            "AI/ML integration for smart features"
        ],
        "mission": "To build transformative digital solutions that empower African businesses and communities through innovative technology.",
        "team_culture": "Agile, collaborative, and user-focused development approach with emphasis on clean code and scalable architecture."
    },
    "nowamaani_donath": {
        "name": "Nowamaani Donath",
        "role": "Lead Developer & Technical Director at Kakore Labs",
        "background": "Seasoned software engineer and technology leader with extensive experience in full-stack development and digital solution architecture.",
        "expertise": [
            "Full-Stack Web Development",
            "Mobile App Development (Flutter, React Native)",
            "Cloud Architecture & DevOps",
            "Database Design & Optimization",
            "API Development & Integration",
            "Technical Team Leadership"
        ],
        "education": [
            "Advanced degrees in Computer Science and Software Engineering",
            "Multiple certifications in cloud technologies and agile methodologies"
        ],
        "achievements": [
            "Led development of Netra app from concept to Play Store launch",
            "Architected scalable backend systems for multiple enterprise clients",
            "Mentored and built high-performing development teams",
            "Pioneered AI integration in service marketplace platforms"
        ],
        "philosophy": "Believes in building technology that solves real-world problems while maintaining elegance in code and user experience.",
        "contact": "Available for technical consultations and complex project discussions"
    },
    "aidnest_africa": {
        "name": "Aidnest Africa",
        "description": "A innovative technology company focused on creating digital solutions that bridge service gaps across African markets.",
        "core_products": [
            "Netra - Service Marketplace connecting providers with clients",
            "Autra - Automotive services and maintenance platform",
            "Various custom enterprise solutions"
        ],
        "vision": "To become Africa's leading technology enabler for service-based businesses and digital transformation.",
        "values": [
            "Innovation and Excellence",
            "User-Centric Design",
            "African Market Focus",
            "Sustainable Technology",
            "Community Impact"
        ]
    }
}

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
            'personal_details': {},
            'image_requests': 0,
            'coding_help_requests': 0,
            'voice_requests': 0
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
                clean_text = ' '.join(lines[:300])
                
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
    """Generate image using DALL-E with enhanced prompts"""
    try:
        # Enhance prompt for better results
        enhanced_prompt = f"Professional, high-quality, detailed {prompt}. Clean design, modern aesthetic, professional illustration style."
        
        response = client.images.generate(
            model="dall-e-3",
            prompt=enhanced_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        return response.data[0].url
    except Exception as e:
        print(f"Image generation error: {e}")
        return None

def analyze_image(image_data):
    """Analyze image using GPT-4 Vision"""
    try:
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
        return response.choices[0].message.content
    except Exception as e:
        print(f"Image analysis error: {e}")
        return None

def transcribe_audio(audio_file):
    """Transcribe audio using Whisper"""
    try:
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
            
        return transcript
    except Exception as e:
        print(f"Audio transcription error: {e}")
        return None

def should_generate_image(message, context, user_session):
    """Enhanced image generation detection"""
    message_lower = message.lower()
    
    # Direct image requests
    image_triggers = [
        'generate image', 'create picture', 'visualize', 'draw', 'illustration',
        'show me a picture', 'make an image', 'create visual', 'generate visual'
    ]
    
    if any(trigger in message_lower for trigger in image_triggers):
        return True
    
    # Context-based image generation
    recent_context = " ".join([msg.get('text', '') for msg in context[-3:]])
    context_lower = recent_context.lower()
    
    image_topics = [
        'netra app interface', 'app design', 'how netra looks',
        'service provider dashboard', 'booking process', 'netra features',
        'kakore labs office', 'team photo', 'app screenshot',
        'website design', 'mobile app design', 'user interface'
    ]
    
    if any(topic in context_lower for topic in image_topics):
        return True
    
    # User interest-based generation
    if user_session.get('image_requests', 0) < 5:  # Limit to prevent abuse
        visual_keywords = ['look like', 'appearance', 'design', 'interface', 'screenshot', 'visual']
        if any(keyword in message_lower for keyword in visual_keywords):
            return True
    
    return False

def should_analyze_image(message):
    """Check if user wants image analysis"""
    message_lower = message.lower()
    
    analysis_triggers = [
        'analyze this image', 'what is in this image', 'describe this picture',
        'what do you see', 'analyze the image', 'tell me about this image',
        'what does this show', 'explain this picture'
    ]
    
    return any(trigger in message_lower for trigger in analysis_triggers)

def should_transcribe_audio(message):
    """Check if user wants audio transcription"""
    message_lower = message.lower()
    
    transcription_triggers = [
        'transcribe this', 'what is being said', 'convert speech to text',
        'transcribe audio', 'speech to text', 'what did they say'
    ]
    
    return any(trigger in message_lower for trigger in transcription_triggers)

def create_image_prompt(message, context, user_session):
    """Create appropriate image prompt based on conversation"""
    # Company-specific prompts
    company_prompts = {
        'netra_interface': "Modern mobile app interface for Netra African service marketplace, clean design, intuitive booking system, African aesthetic, professional UI/UX design",
        'kakore_labs_team': "Friendly diverse team of African developers at Kakore Labs working in modern tech office environment, collaborative atmosphere, computers and code visible",
        'aidnest_office': "Modern African tech company office space with creative workspace, technology equipment, team collaboration, professional environment",
        'netra_booking': "Step-by-step visual guide showing African users booking services on Netra app, mobile interface, diverse users, seamless experience",
        'service_provider': "African service provider using Netra app on smartphone, showing booking notifications, earning dashboard, professional setting"
    }
    
    message_lower = message.lower()
    
    # Determine the best prompt based on conversation
    if any(word in message_lower for word in ['interface', 'look like', 'design', 'ui', 'ux']):
        return company_prompts['netra_interface']
    elif any(word in message_lower for word in ['team', 'kakore', 'developers', 'office']):
        return company_prompts['kakore_labs_team']
    elif any(word in message_lower for word in ['booking', 'process', 'how to book']):
        return company_prompts['netra_booking']
    elif any(word in message_lower for word in ['provider', 'service provider', 'earn']):
        return company_prompts['service_provider']
    else:
        # Generic prompt based on current topic
        return f"Professional illustration of: {message}"

def update_conversation_memory(user_session, message, response):
    """Enhanced conversation memory tracking"""
    message_lower = message.lower()
    
    # Track user interests with more categories
    interest_keywords = {
        'technology': ['tech', 'coding', 'programming', 'developer', 'software', 'code', 'algorithm'],
        'business': ['business', 'startup', 'money', 'income', 'entrepreneur', 'revenue', 'profit'],
        'netra': ['netra', 'aidnest', 'service provider', 'booking', 'appointment', 'client'],
        'kakore_labs': ['kakore', 'labs', 'development', 'technical', 'programmer', 'coder'],
        'design': ['design', 'ui', 'ux', 'interface', 'looks', 'appearance', 'visual'],
        'career': ['job', 'career', 'work', 'employment', 'hire', 'recruitment']
    }
    
    for interest, keywords in interest_keywords.items():
        if any(keyword in message_lower for keyword in keywords):
            if interest not in user_session['user_interests']:
                user_session['user_interests'].append(interest)
    
    # Track specific facts about the user
    if 'name' in message_lower and user_session['user_name']:
        user_session['remembered_facts']['knows_name'] = True
    
    # Track image requests
    if any(word in message_lower for word in ['image', 'picture', 'visual', 'generate']):
        user_session['image_requests'] = user_session.get('image_requests', 0) + 1
    
    # Track coding help requests
    if any(word in message_lower for word in ['code', 'programming', 'developer', 'script']):
        user_session['coding_help_requests'] = user_session.get('coding_help_requests', 0) + 1
    
    # Track voice requests
    if any(word in message_lower for word in ['voice', 'audio', 'speech', 'transcribe']):
        user_session['voice_requests'] = user_session.get('voice_requests', 0) + 1
    
    # Update recent topics (keep last 5)
    if len(user_session['recent_topics']) >= 5:
        user_session['recent_topics'].pop(0)
    user_session['recent_topics'].append(message_lower[:40])
    
    user_session['last_interaction'] = time.time()
    user_session['last_topic'] = message_lower

def build_memory_context(user_session):
    """Build comprehensive memory context"""
    memory_parts = []
    
    if user_session['user_name']:
        memory_parts.append(f"User's name: {user_session['user_name']}")
    
    if user_session['user_interests']:
        memory_parts.append(f"Interests: {', '.join(user_session['user_interests'])}")
    
    if user_session['recent_topics']:
        memory_parts.append(f"Recent topics: {', '.join(user_session['recent_topics'][-3:])}")
    
    if user_session.get('image_requests', 0) > 0:
        memory_parts.append(f"Image requests: {user_session['image_requests']}")
    
    if user_session.get('coding_help_requests', 0) > 0:
        memory_parts.append(f"Coding help requests: {user_session['coding_help_requests']}")
    
    if user_session.get('voice_requests', 0) > 0:
        memory_parts.append(f"Voice requests: {user_session['voice_requests']}")
    
    return " | ".join(memory_parts) if memory_parts else "New conversation"

def get_company_context(query):
    """Provide specific company and team information"""
    query_lower = query.lower()
    
    if any(word in query_lower for word in ['kakore', 'labs', 'development', 'technical']):
        return COMPANY_INFO['kakore_labs']
    elif any(word in query_lower for word in ['nowamaani', 'donath', 'lead developer', 'technical director']):
        return COMPANY_INFO['nowamaani_donath']
    elif any(word in query_lower for word in ['aidnest', 'company', 'about us']):
        return COMPANY_INFO['aidnest_africa']
    
    return None

def get_ai_response(message, conversation_context, web_search_results=None, user_session=None):
    """Enhanced AI response with better memory and company knowledge"""
    try:
        user_name = user_session.get('user_name', 'there')
        memory_context = build_memory_context(user_session)
        
        # Get company-specific context if relevant
        company_context = get_company_context(message)
        
        # Build comprehensive system message
        system_message = f"""
        You are Jovira, a real team member at Aidnest Africa. You're friendly, knowledgeable, and provide helpful information.

        ABOUT YOUR COMPANY:
        - Aidnest Africa: Technology company creating digital solutions for African markets
        - Netra: Service marketplace app connecting providers with clients (available on Play Store)
        - Kakore Labs: Development hub building Netra and other innovative apps
        - Nowamaani Donath: Lead Developer & Technical Director at Kakore Labs

        YOUR PERSONALITY:
        - Speak like a real human colleague, not an AI
        - Remember previous conversations and build on them naturally
        - Use emojis occasionally to express warmth
        - Be professional but friendly and approachable
        - If you don't know something, be honest but helpful
        - You can analyze images, generate images, and transcribe voice messages

        CURRENT CONVERSATION:
        - User: {user_name}
        - Memory Context: {memory_context}
        - Previous Messages: {len(conversation_context)}

        RESPONSE GUIDELINES:
        - Reference previous topics when relevant
        - Ask follow-up questions based on user interests
        - Provide specific information about Netra, Kakore Labs, and Aidnest Africa
        - Offer coding help and technical guidance when requested
        - Suggest image generation when visual explanations would help
        - Offer to analyze images or transcribe audio when relevant
        - Never say you're an AI or mention being generated
        """
        
        context_messages = [{"role": "system", "content": system_message}]
        
        # Add company-specific information
        if company_context:
            company_info = f"Specific information about {company_context['name']}:\n{json.dumps(company_context, indent=2)}"
            context_messages.append({"role": "system", "content": company_info})
        
        # Add web search results
        if web_search_results:
            web_context = "Latest information from our websites:\n"
            for result in web_search_results:
                web_context += f"- {result['url']}: {result['content'][:400]}\n"
            context_messages.append({"role": "system", "content": web_context})
        
        # Add conversation history (last 12 messages for better context)
        if conversation_context:
            for msg in conversation_context[-12:]:
                role = "user" if msg.get('sender') == 'user' else "assistant"
                context_messages.append({"role": role, "content": msg.get('text', '')})
        
        # Add current message
        context_messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=context_messages,
            max_tokens=500,
            temperature=0.8,
            presence_penalty=0.1,
            frequency_penalty=0.1
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None

def get_fallback_response(message, user_id="default"):
    """Enhanced fallback with company knowledge"""
    user_session = get_user_session(user_id)
    message_lower = message.lower().strip()
    
    user_session['question_count'] += 1
    
    # Name handling
    if user_session['conversation_stage'] == 'greeting':
        user_session['conversation_stage'] = 'get_name'
        greetings = [
            "Hey there! 👋 I'm Jovira from the Aidnest Africa team! I help with Netra, Kakore Labs, and tech questions. What should I call you?",
            "Hello! 🌟 Welcome! I'm Jovira from Aidnest Africa and I'd love to get to know you better. What's your name?",
            "Hi! 🚀 Great to connect! I'm Jovira on the Netra team at Aidnest Africa, working with Kakore Labs. What do you prefer to be called?",
        ]
        return random.choice(greetings)
    
    if user_session['conversation_stage'] == 'get_name' and not user_session['user_name']:
        potential_name = message.strip()
        if len(potential_name) < 30 and not any(word in potential_name.lower() for word in ['netra', 'aidnest', 'hello', 'hi']):
            user_session['user_name'] = potential_name
            user_session['conversation_stage'] = 'main_conversation'
            
            responses = [
                f"Perfect, {potential_name}! 🎉 Now we're properly introduced! I can help you with Netra, Kakore Labs development, or any tech questions. What's on your mind?",
                f"Hey {potential_name}! 👋 Great name! I'm excited to help with Netra app, Kakore Labs projects, or anything tech-related. What would you like to explore?",
            ]
            return random.choice(responses)
    
    user_name = user_session.get('user_name', '')
    name_prefix = f"{user_name}, " if user_name else ""
    
    # Company-specific responses
    if any(word in message_lower for word in ['kakore', 'labs']):
        kakore_info = COMPANY_INFO['kakore_labs']
        return f"{name_prefix}Kakore Labs is our amazing development hub! 🏢 They specialize in {', '.join(kakore_info['focus_areas'][:3])}. Want me to tell you more about their projects or technical expertise?"
    
    if any(word in message_lower for word in ['nowamaani', 'donath']):
        donath_info = COMPANY_INFO['nowamaani_donath']
        return f"{name_prefix}Nowamaani Donath is our Lead Developer! 👨‍💻 He's an expert in {', '.join(donath_info['expertise'][:3])}. He led the Netra app development from concept to launch!"
    
    # Memory-based responses
    if user_session['recent_topics']:
        last_topic = user_session['recent_topics'][-1]
        if any(topic in last_topic for topic in ['netra', 'app', 'booking']):
            return f"{name_prefix}Since we were discussing Netra features, would you like me to generate a visual of the app interface to better explain? 🎨"
    
    # Feature suggestions
    if any(word in message_lower for word in ['what can you do', 'help', 'features']):
        return f"{name_prefix}I can help you with: 📱 Netra app info, 💻 Kakore Labs projects, 🎨 image generation, 🔍 image analysis, 🎤 voice transcription, and 💡 coding help! What interests you most?"
    
    # Casual conversation
    if any(word in message_lower for word in ['how are you', 'how do you do']):
        return f"{name_prefix}I'm doing great! 😊 Just been helping users with Netra and working with the Kakore Labs team on some exciting updates. How about you?"
    
    if any(word in message_lower for word in ['thank', 'thanks']):
        return f"{name_prefix}You're very welcome! Happy to help. The Kakore Labs team puts a lot of care into building great solutions. Anything else you're curious about?"
    
    # Default engaging response
    engaging_responses = [
        f"{name_prefix}That's interesting! 🤔 At Aidnest Africa, we're always exploring how technology can solve real problems. What specific aspect would you like me to focus on?",
        f"{name_prefix}Fascinating topic! 💡 Our Kakore Labs team would love this kind of discussion. Should I provide more technical details or keep it general?",
        f"{name_prefix}Great question! 🌟 Let me think about the best way to explain this... Would a code example or visual illustration help clarify things?"
    ]
    return random.choice(engaging_responses)

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
        if any(keyword in message.lower() for keyword in ['netra', 'aidnest', 'kakore', 'app', 'download', 'nowamaani']):
            web_search_results = enhanced_web_search(message, site_specific=True)
        
        # Check for image generation (with limits)
        image_url = None
        if should_generate_image(message, user_session['conversation_context'], user_session):
            image_prompt = create_image_prompt(message, user_session['conversation_context'], user_session)
            image_url = generate_image(image_prompt)
            if image_url:
                user_session['image_requests'] = user_session.get('image_requests', 0) + 1
        
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
                    ai_response += f"\n\n🎨 *I've generated a visual to help explain this better!*"
                
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
        error_responses = [
            "Hmm, I'm having a bit of a moment here! 😅 Let's try that again - what were we discussing?",
            "Oops, my thoughts got a bit tangled! 🤔 Could you repeat that? We were having such a good conversation about technology!",
        ]
        return jsonify({"reply": random.choice(error_responses)})

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
        
        # Analyze image
        analysis_result = analyze_image(image_data)
        
        if analysis_result:
            return jsonify({
                "analysis": analysis_result,
                "message": "🔍 I've analyzed your image! Here's what I found:"
            })
        else:
            return jsonify({"error": "Failed to analyze image"}), 500
            
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
        
        # Transcribe audio
        transcript = transcribe_audio(audio_file)
        
        if transcript:
            return jsonify({
                "transcript": transcript,
                "message": "🎤 I've transcribed your audio! Here's what was said:"
            })
        else:
            return jsonify({"error": "Failed to transcribe audio"}), 500
            
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
        
        # Generate image
        image_url = generate_image(prompt)
        
        if image_url:
            return jsonify({
                "image_url": image_url,
                "message": "🎨 I've generated an image based on your request!"
            })
        else:
            return jsonify({"error": "Failed to generate image"}), 500
            
    except Exception as e:
        print(f"Image generation endpoint error: {e}")
        return jsonify({"error": "Error generating image"}), 500

@app.route("/company_info")
def company_info():
    """Endpoint to get company information"""
    return jsonify(COMPANY_INFO)

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
            'personal_details': {},
            'image_requests': 0,
            'coding_help_requests': 0,
            'voice_requests': 0
        }
    return jsonify({"status": "success", "message": "Conversation history cleared"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)