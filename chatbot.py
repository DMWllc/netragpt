from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
import os
import random
import re
import time

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
            'question_count': 0
        }
    return conversation_history[user_id]

def get_fallback_response(message, user_id="default"):
    user_session = get_user_session(user_id)
    message_lower = message.lower().strip()
    
    # Update session
    user_session['last_interaction'] = time.time()
    user_session['question_count'] += 1
    
    # Enhanced greeting detection with variations
    greeting_patterns = [
        r'hello', r'hi', r'hey', r'greetings', r'good morning', r'good afternoon', 
        r'good evening', r'howdy', r'yo', r'what\'s up', r'sup', r'hi there',
        r'hello there', r'hey there', r'good day', r'hi bot', r'hello bot',
        r'hey bot', r'morning', r'afternoon', r'evening', r'how are you',
        r'how do you do', r'whats good', r'how\'s it going', r'how goes it',
        r'long time', r'nice to see you', r'pleasure to meet you', r'how have you been'
    ]
    
    # Check if it's a greeting
    is_greeting = any(re.search(pattern, message_lower) for pattern in greeting_patterns)
    
    if is_greeting:
        greeting_responses = [
            "Hey there! 👋 It's great to hear from you! I'm NetraGPT, your friendly assistant for everything Aidnest Africa and Netra. What's on your mind today?",
            "Hello! 🌟 Wow, nice to see you! I'm NetraGPT, and I'm super excited to tell you all about Aidnest Africa and our amazing Netra platform. What would you love to know?",
            "Hi! 🚀 Awesome timing! I was just thinking about how to help someone today. I'm NetraGPT, your go-to guide for Aidnest Africa's digital solutions. What can I help you explore?",
            "Hey! 💫 Perfect timing! I'm NetraGPT, and I'm absolutely thrilled to chat with you about Aidnest Africa and Netra. What's got you curious today?",
            "Well hello there! 😊 What a pleasant surprise! I'm NetraGPT, your dedicated assistant for all things Aidnest Africa. How can I make your day better?",
            "Hi there! 🌈 Wonderful to meet you! I'm NetraGPT, and I'm here to walk you through the incredible world of Aidnest Africa and Netra. What would you like to dive into first?",
            "Hey! 🎉 Great to connect with you! I'm NetraGPT, your partner in exploring Aidnest Africa's tech solutions. What's sparked your interest today?",
            "Hello! ✨ So glad you reached out! I'm NetraGPT, and I'm passionate about sharing how Aidnest Africa is transforming digital experiences. What would you like to know?",
            "Hi there! 🌟 What a wonderful time to chat! I'm NetraGPT, excited to help you discover Aidnest Africa and Netra. What's on your mind?",
            "Hey! 🚀 Fantastic! I'm NetraGPT, and I'm here to make your journey with Aidnest Africa amazing. What would you love to explore together?"
        ]
        user_session['context'] = 'greeting'
        return random.choice(greeting_responses)
    
    # Handle yes/no responses to suggestions
    yes_patterns = [r'yes', r'yeah', r'yep', r'sure', r'okay', r'ok', r'go ahead', r'please', r'absolutely', r'definitely', r'of course', r'why not', r'certainly']
    no_patterns = [r'no', r'nope', r'nah', r'not really', r'maybe later', r'i\'m good', r'no thanks', r'not now', r'perhaps later']
    
    if any(re.search(pattern, message_lower) for pattern in yes_patterns) and user_session.get('last_topic'):
        return handle_yes_response(user_session['last_topic'], user_session)
    
    if any(re.search(pattern, message_lower) for pattern in no_patterns) and user_session.get('last_topic'):
        return handle_no_response(user_session['last_topic'], user_session)
    
    # Enhanced content responses with human-like variations
    content_responses = {
        'aidnest_africa': {
            'responses': [
                "You know, Aidnest Africa is really something special! 🌍 We're all about creating smart, practical digital solutions that genuinely make life easier for people across Africa. We use technology to solve real community problems - from giving people access to reliable services to building tools that empower local professionals and businesses to thrive.",
                "I'm so excited to tell you about Aidnest Africa! 💫 We're an organization that's deeply passionate about creating digital solutions that actually matter. Our focus is on making life and work easier for people across Africa by tackling real community challenges with technology that truly works for them.",
                "Let me share what makes Aidnest Africa unique! 🚀 We're not just another tech company - we're deeply committed to building practical digital solutions that address real African challenges. From empowering local professionals to creating accessible services, we're here to make a genuine difference in people's lives.",
                "Aidnest Africa is close to my heart! ❤️ We're focused on crafting digital solutions that are both smart and deeply practical for African communities. Our mission is to use technology in ways that truly solve problems - whether it's helping people find reliable services or giving local businesses the tools they need to succeed.",
                "I love talking about Aidnest Africa! 🌟 We're an organization that believes in the power of technology to transform lives across Africa. We create solutions that are not just innovative, but genuinely useful - helping bridge gaps in services and empowering communities through digital tools that actually work."
            ],
            'suggestions': [
                "Would you like me to tell you about our amazing Netra platform?",
                "Should I explain how we're creating real opportunities through technology?",
                "Want to dive deeper into how we're making a difference in African communities?",
                "Would you be interested in hearing about our partnership approach?",
                "Should I share more about our vision for digital transformation in Africa?"
            ]
        },
        'netra_platform': {
            'responses': [
                "Oh, Netra is absolutely fantastic! 🌐 It's our flagship digital platform that connects people with trusted service providers - think technicians, creatives, professionals, and so many more skilled individuals. Imagine it as a smart bridge between talented people and those who need their services. And the best part? It's built in close partnership with the amazing Kakore Labs!",
                "Let me tell you about Netra - it's really revolutionary! 💼 Our platform is designed to connect people with verified service providers across various fields. Whether you need a technician, a creative professional, or a consultant, Netra makes finding the right person smooth and reliable. We built this in collaboration with Kakore Labs to ensure it's truly effective.",
                "Netra is something I'm particularly proud of! 🎯 It's our digital platform that serves as a meeting point for skilled professionals and people who need their services. From technicians to creatives and consultants, we've created a space where trust and quality come first. Partnering with Kakore Labs has made this platform incredibly robust.",
                "I'm thrilled to explain Netra to you! 🤝 It's our comprehensive platform that brings together service providers and clients in a seamless way. We've focused on building trust and reliability into every interaction. The collaboration with Kakore Labs has been instrumental in making Netra the success it is today.",
                "Netra is where magic happens! ✨ Our platform connects talented service providers with people who appreciate quality work. Whether it's technical services, creative projects, or professional consultations, Netra ensures every connection counts. Working with Kakore Labs has allowed us to create something truly special for our community."
            ],
            'suggestions': [
                "Would you like to know how Netra specifically helps service providers grow?",
                "Should I explain the amazing benefits clients experience when using Netra?",
                "Want to learn about the smart verification system we've implemented?",
                "Would you be curious about how the booking process works?",
                "Should I tell you about the partnership dynamics with Kakore Labs?"
            ]
        },
        'netra_features': {
            'responses': [
                "The features we've built into Netra are really impressive! 🛠️ We make it incredibly easy to find verified providers, check their ratings, and book them directly. But here's what makes Netra special - it's not just a marketplace. We've built smart tools that help professionals manage their entire workflow, from handling client requests to secure communication and comprehensive job tracking. It's like having a professional assistant built right in!",
                "Let me walk you through Netra's amazing features! 📱 Finding verified providers with genuine ratings and direct booking is just the beginning. We've created a whole ecosystem where professionals can manage their business efficiently - think client management, secure messaging, and job organization tools that actually make their work easier and more productive.",
                "Netra's features are designed with real people in mind! 💡 We've made provider discovery and booking super straightforward, but we didn't stop there. Our platform includes powerful tools that help professionals streamline their work - managing client interactions, maintaining secure communications, and keeping track of all their projects in one organized space.",
                "I'm excited to share Netra's feature set with you! 🌟 Beyond the obvious benefits of finding rated providers and easy booking, we've built comprehensive management tools for professionals. They can handle client requests, communicate safely, and monitor all their jobs - everything they need to run their business effectively.",
                "Netra's features are all about empowerment! 🚀 We've created a system where finding and booking trusted providers is simple, but we've also equipped professionals with smart tools to manage their workflow. From client communication to job tracking, every feature is designed to make their professional lives smoother and more successful."
            ],
            'suggestions': [
                "Would you like me to explain how our provider verification process ensures quality?",
                "Should I walk you through the seamless booking experience we've created?",
                "Want to learn about the professional tools that help service providers succeed?",
                "Would you be interested in hearing about our rating and review system?",
                "Should I detail how our communication tools protect both clients and providers?"
            ]
        },
        'netragpt_assistant': {
            'responses': [
                "That's me! 🤖 I'm NetraGPT, your friendly AI assistant who's here to support both clients and providers in real-time. I help answer questions, offer guidance, and make the whole process of connecting people much simpler and more enjoyable. Think of me as your personal guide through the Netra experience - I'm always here to help things go smoothly!",
                "You're talking to me right now! 😊 I'm NetraGPT, the AI assistant designed to make everyone's experience with Netra better. Whether you're a client looking for services or a provider managing your business, I'm here to offer real-time support, answer your questions, and provide guidance whenever you need it.",
                "I'm NetraGPT, and I'm absolutely delighted to assist you! 💫 As your AI assistant, I support both clients and providers with instant help, clear answers, and helpful guidance. My goal is to make every interaction on Netra smooth, efficient, and genuinely helpful for everyone involved.",
                "That would be me - NetraGPT at your service! 🌈 I'm the AI assistant built into Netra to help clients and providers alike. I provide real-time support, answer questions, and offer guidance to make sure everyone has the best possible experience using our platform.",
                "I'm NetraGPT, and I love helping people! ❤️ As your AI assistant, I'm here to support both clients looking for services and providers building their businesses. I offer instant answers, helpful guidance, and make the process of connecting and working together as smooth as possible."
            ],
            'suggestions': [
                "Would you like to know what kinds of questions I can help you with right now?",
                "Should I explain how I assist both clients and providers differently?",
                "Want to learn about my real-time support capabilities?",
                "Would you be interested in hearing how I make the user experience better?",
                "Should I tell you about the types of guidance I can provide?"
            ]
        },
        'vision_mission': {
            'responses': [
                "Our vision at Aidnest Africa is something I'm truly passionate about! 🌍 We're dedicated to creating meaningful opportunities through technology - giving skilled Africans the visibility they deserve, building trust in digital services, and helping communities grow in this digital age. What makes us different? We believe in building products in Africa, for Africa, by people who truly understand both the challenges and the incredible potential here.",
                "Let me share our vision - it's what drives everything we do! 💫 At Aidnest Africa, we're committed to creating opportunities through thoughtful technology. We want to give skilled professionals the platform they need, establish trust in digital interactions, and support community growth. Our approach is unique: we build solutions in Africa, for Africa, with deep understanding of local contexts and opportunities.",
                "Our mission is close to my heart! 🚀 Aidnest Africa exists to create genuine opportunities through appropriate technology. We focus on making skilled Africans more visible, fostering trust in digital platforms, and enabling community development. The key is that we build our solutions right here in Africa, for African users, with people who truly grasp both the challenges and the amazing potential.",
                "I'm so excited to share our vision with you! ❤️ At Aidnest Africa, we're all about creating opportunities through technology that actually makes sense for our context. We work to amplify skilled professionals, build trustworthy digital spaces, and support community advancement. Our philosophy is simple: build in Africa, for Africa, with people who understand what Africa needs.",
                "Our vision drives every decision we make! 🌟 Aidnest Africa is committed to creating meaningful opportunities through well-designed technology. We strive to give talented Africans the recognition they deserve, establish reliable digital trust, and contribute to community growth. What sets us apart? We develop our solutions locally, for local needs, with teams that deeply understand African markets and potential."
            ],
            'suggestions': [
                "Would you like to know more about our specific community impact goals?",
                "Should I explain how we're working to build trust in digital services?",
                "Want to learn about our approach to understanding African markets?",
                "Would you be interested in hearing how we measure our social impact?",
                "Should I share stories about the opportunities we've helped create?"
            ]
        },
        'services_providers': {
            'responses': [
                "The range of professionals on Netra is really impressive! 👥 We connect people with various service providers including skilled technicians, creative professionals, business consultants, and many other experts. What makes Netra special is our commitment to verification - every provider goes through a process to ensure they meet our quality and reliability standards, so clients can feel completely confident in their choices.",
                "Let me tell you about the amazing professionals on Netra! 💼 We've got a diverse range of service providers - from technical experts and creative talents to business consultants and specialized professionals. The best part? Our verification system ensures that every provider meets strict quality standards, giving clients peace of mind and great results.",
                "Netra brings together such talented professionals! 🎨 We connect users with various service providers including technicians, creatives, consultants, and specialized experts. Our focus on verification means we carefully check each provider to maintain high standards of quality and reliability - because we believe everyone deserves access to trustworthy professionals.",
                "I'm proud of the professional community we're building on Netra! 🤝 We offer connections to various service providers - technical experts, creative professionals, business consultants, and more. What sets us apart is our thorough verification process that ensures every provider meets our quality standards, creating a trustworthy environment for everyone.",
                "The professionals on Netra are truly exceptional! 🌟 We connect people with a wide range of service providers including technicians, creative experts, consultants, and specialized professionals. Our verification system is designed to maintain high standards - we check each provider carefully to ensure quality and reliability for our valued clients."
            ],
            'suggestions': [
                "Would you like me to list the specific types of professionals available?",
                "Should I explain our detailed verification process step by step?",
                "Want to learn how providers benefit from being on Netra?",
                "Would you be curious about how we ensure ongoing quality?",
                "Should I tell you about the support we offer to our providers?"
            ]
        },
        'partnership_kakore': {
            'responses': [
                "Our partnership with Kakore Labs is absolutely fantastic! 🤝 They bring incredible technical expertise and deep understanding of African markets to the table. Working together has allowed us to build Netra with robust technology while keeping it perfectly aligned with local needs. It's a collaboration that truly leverages the strengths of both organizations to create something remarkable for our users.",
                "The partnership with Kakore Labs is one of our greatest strengths! 💫 They provide amazing technical capabilities and genuine insight into African market dynamics. This collaboration has been crucial in developing Netra - we combine their technical excellence with our market understanding to create a platform that's both technologically advanced and perfectly suited for our users.",
                "I'm so proud of our partnership with Kakore Labs! 🚀 They offer exceptional technical expertise and valuable perspectives on African markets. This collaboration has been instrumental in building Netra - we merge their technical prowess with our contextual understanding to deliver a platform that's both powerful and perfectly tailored for our community.",
                "Our collaboration with Kakore Labs is truly special! ❤️ They bring outstanding technical skills and deep African market knowledge to our partnership. Working together has enabled us to create Netra with the right blend of technological sophistication and local relevance - it's a perfect combination that serves our users exceptionally well.",
                "The Kakore Labs partnership is a game-changer! 🌟 They contribute incredible technical expertise and authentic understanding of African markets. This collaboration has been key to developing Netra - we combine their technical excellence with our market insights to build a platform that's both advanced and perfectly adapted for our users' needs."
            ],
            'suggestions': [
                "Would you like to know how the partnership benefits Netra users directly?",
                "Should I explain the specific roles each organization plays?",
                "Want to learn about the technical innovations from Kakore Labs?",
                "Would you be interested in hearing how we maintain this partnership?",
                "Should I share how the partnership influences our future plans?"
            ]
        },
        'technology_approach': {
            'responses': [
                "Our approach to technology is really thoughtful and practical! 💻 We believe in using technology as an enabler rather than just adding complexity. Every solution we build at Aidnest Africa is designed with real people in mind - focusing on usability, reliability, and genuine problem-solving. We prioritize creating tools that people can actually use and benefit from in their daily lives and businesses.",
                "Let me share how we think about technology! 🛠️ At Aidnest Africa, we view technology as a means to solve real problems, not just create flashy features. We design our solutions with careful attention to user experience, reliability, and practical benefits. Our goal is always to create tools that make tangible differences in people's lives and work.",
                "Our technology philosophy is centered on real impact! 🌐 We approach technology as a practical tool for solving genuine challenges. Every solution from Aidnest Africa is crafted with user-friendly design, dependable performance, and meaningful functionality. We're committed to building technology that people find genuinely useful and empowering.",
                "I love explaining our technology approach! 💡 We see technology as a powerful enabler for positive change. At Aidnest Africa, we design solutions that prioritize user experience, reliability, and real-world usefulness. We're passionate about creating tools that not only work well but actually improve how people live and work.",
                "Our technology strategy is all about meaningful innovation! 🚀 We believe in using technology to address real needs rather than just following trends. Aidnest Africa focuses on developing solutions that are user-friendly, reliable, and genuinely beneficial. We're dedicated to creating technology that makes a practical difference in our users' lives."
            ],
            'suggestions': [
                "Would you like to know how we ensure our technology remains user-friendly?",
                "Should I explain our approach to testing and quality assurance?",
                "Want to learn about how we incorporate user feedback?",
                "Would you be interested in hearing about our technology stack?",
                "Should I share how we balance innovation with practicality?"
            ]
        },
        'community_impact': {
            'responses': [
                "The community impact we're creating is what motivates us every day! 🌍 Through Netra and our other initiatives, we're helping skilled professionals build sustainable businesses, enabling clients to access reliable services, and contributing to local economic growth. Seeing real people achieve their goals and improve their lives through our platform is the most rewarding part of what we do.",
                "Our community impact stories are truly inspiring! 💫 We're witnessing how Netra helps professionals establish successful businesses, enables clients to find trustworthy services, and supports local economic development. The real-life success stories of people transforming their circumstances through our platform are what drive our passion and commitment.",
                "The impact we're making in communities is incredible! 🚀 Through Netra, we're empowering professionals to build sustainable careers, helping clients access quality services, and contributing to economic growth. Nothing compares to seeing actual people achieve their dreams and improve their lives using the opportunities we've created.",
                "Our community impact is deeply meaningful to us! ❤️ We're proud that Netra enables professionals to create successful businesses, helps clients find reliable services, and supports local economic development. The stories of real people changing their lives through our platform are what make all our efforts worthwhile.",
                "The community impact we're achieving is absolutely wonderful! 🌟 Through Netra, we're supporting professionals in building sustainable livelihoods, assisting clients in accessing quality services, and fostering economic growth. Witnessing real people transform their lives and achieve their goals using our platform is incredibly fulfilling."
            ],
            'suggestions': [
                "Would you like to hear specific success stories from our users?",
                "Should I explain how we measure our community impact?",
                "Want to learn about the economic benefits for local communities?",
                "Would you be interested in hearing how professionals' lives have changed?",
                "Should I share how clients benefit beyond just finding services?"
            ]
        }
    }
    
    # Enhanced keyword mapping with priority
    keyword_mapping = {
        'aidnest': 'aidnest_africa',
        'organization': 'aidnest_africa',
        'company': 'aidnest_africa',
        'what is aidnest': 'aidnest_africa',
        'who are you': 'aidnest_africa',
        
        'netra': 'netra_platform',
        'platform': 'netra_platform',
        'digital platform': 'netra_platform',
        'what is netra': 'netra_platform',
        
        'features': 'netra_features',
        'tools': 'netra_features',
        'verification': 'netra_features',
        'booking': 'netra_features',
        'ratings': 'netra_features',
        'how does it work': 'netra_features',
        
        'netragpt': 'netragpt_assistant',
        'ai assistant': 'netragpt_assistant',
        'chatbot': 'netragpt_assistant',
        'you': 'netragpt_assistant',
        
        'vision': 'vision_mission',
        'mission': 'vision_mission',
        'goal': 'vision_mission',
        'purpose': 'vision_mission',
        'why': 'vision_mission',
        
        'services': 'services_providers',
        'providers': 'services_providers',
        'professionals': 'services_providers',
        'technicians': 'services_providers',
        'creatives': 'services_providers',
        'consultants': 'services_providers',
        'experts': 'services_providers',
        
        'kakore': 'partnership_kakore',
        'partnership': 'partnership_kakore',
        'collaboration': 'partnership_kakore',
        'labs': 'partnership_kakore',
        
        'technology': 'technology_approach',
        'tech': 'technology_approach',
        'digital': 'technology_approach',
        'innovation': 'technology_approach',
        
        'community': 'community_impact',
        'impact': 'community_impact',
        'social': 'community_impact',
        'economic': 'community_impact',
        'success stories': 'community_impact'
    }
    
    # Find the best matching content
    selected_topic = 'default'
    for keyword, topic in keyword_mapping.items():
        if keyword in message_lower:
            selected_topic = topic
            break
    
    # Check if this is out of scope
    if selected_topic == 'default':
        out_of_scope_responses = [
            "That's an interesting question! 🤔 Currently, I'm specifically focused on helping with Aidnest Africa and Netra-related topics. For questions outside this scope, you'll need to wait for NetraGPT 2.0 - it's coming with expanded capabilities that will be able to handle much more diverse topics!",
            "Hmm, that's beyond my current expertise! 📚 Right now, I'm specialized in everything about Aidnest Africa and Netra. But don't worry - NetraGPT 2.0 is in development and will have broader knowledge to answer all sorts of questions!",
            "I'd love to help with that, but I'm currently optimized for Aidnest Africa and Netra topics! 🎯 For questions outside this scope, you'll be excited to know that NetraGPT 2.0 is coming soon with expanded capabilities!",
            "That's a great question, but it falls outside my current focus area! 🌟 I'm specifically designed to assist with Aidnest Africa and Netra. The upcoming NetraGPT 2.0 will have wider knowledge to handle diverse topics like yours!",
            "Interesting question! Currently, I'm specialized in Aidnest Africa and Netra topics. 📖 For broader questions, you'll need to wait for NetraGPT 2.0 - it's being developed with expanded capabilities that will cover much more ground!"
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
    yes_responses = {
        'aidnest_africa': [
            "Absolutely! Let me tell you about Netra - it's our amazing platform that connects people with trusted service providers across Africa. Think of it as a smart bridge between skilled professionals and those who need their services. We built it in partnership with Kakore Labs to ensure it's both powerful and perfectly suited for our markets!",
            "I'd love to! Netra is our flagship platform that brings together service providers and clients in a seamless way. Whether you need a technician, creative professional, or consultant, Netra makes finding the right person reliable and straightforward. The partnership with Kakore Labs has been key to making it so effective!",
            "Sure thing! Netra is where the magic happens - it's our digital platform connecting talented professionals with people who appreciate quality work. From technical services to creative projects, Netra ensures every connection is built on trust and quality. Working with Kakore Labs has made this platform truly special!"
        ],
        'netra_platform': [
            "Great! Let me explain how Netra helps service providers - it gives them tools to manage their business efficiently, connects them with genuine clients, and helps build their reputation through our verification system. Providers can handle bookings, communicate securely, and track their work all in one place!",
            "Awesome! Netra benefits clients by making it easy to find verified professionals, see genuine ratings, and book services with confidence. The platform ensures quality through our verification process and provides secure communication channels for smooth interactions!",
            "Perfect! Our verification system is designed to ensure quality and trust. Every provider goes through a careful screening process where we check their credentials, experience, and customer feedback. This helps maintain high standards and gives clients peace of mind when choosing services!"
        ],
        # ... (similar extensive responses for all topics)
    }
    
    if topic in yes_responses:
        response = random.choice(yes_responses[topic])
        # Add new suggestion
        new_suggestions = [
            "Would you like to explore this further?",
            "Should I provide more details about this aspect?",
            "Want to dive deeper into how this works?",
            "Would you be interested in related information?",
            "Should I explain another related feature?"
        ]
        suggestion = random.choice(new_suggestions)
        return f"{response}\n\n{suggestion}"
    
    return "I'd be happy to tell you more! What specific aspect would you like to explore?"

def handle_no_response(topic, user_session):
    """Handle negative responses to suggestions"""
    no_responses = [
        "No problem at all! 😊 Is there something else about Aidnest Africa or Netra that you'd like to know? I'm here to help with whatever interests you!",
        "That's completely fine! 🌟 What other aspect of Aidnest Africa or Netra would you like to explore? I'm excited to help you discover what matters to you!",
        "No worries! 🚀 What would you prefer to learn about instead? Whether it's our technology, community impact, or specific features - I'm ready to share!",
        "Absolutely fine! 💫 What catches your interest about Aidnest Africa or Netra? I'm here to guide you through whatever topic you choose!",
        "That's okay! ❤️ What would you like to know about instead? I'm passionate about sharing all aspects of Aidnest Africa and Netra with you!"
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
        # Enhanced greeting detection - handle without API
        greeting_patterns = [
            r'hello', r'hi', r'hey', r'greetings', r'good morning', r'good afternoon', 
            r'good evening', r'howdy', r'yo', r'what\'s up', r'sup', r'hi there',
            r'hello there', r'hey there', r'good day', r'how are you', r'how do you do'
        ]
        
        is_greeting = any(re.search(pattern, message.lower()) for pattern in greeting_patterns)
        
        if is_greeting:
            reply = get_fallback_response(message, user_id)
        else:
            # For non-greeting content, use our enhanced fallback system
            reply = get_fallback_response(message, user_id)

    except Exception as e:
        # If any error occurs, use our fallback system
        error_responses = [
            "I'm having a little trouble right now, but I'd love to tell you about Aidnest Africa and Netra! What would you like to know? 🌟",
            "Let me share what I know about Aidnest Africa and Netra instead! What aspect interests you most? 🚀",
            "I'm here to help you discover Aidnest Africa and Netra! What would you love to learn about? 💫"
        ]
        reply = random.choice(error_responses)

    return jsonify({"reply": reply})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)