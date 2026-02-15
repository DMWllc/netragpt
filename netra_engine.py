"""
Netra Engine - With Memory and Conversation Understanding
"""

import requests
import re
import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from collections import Counter
import hashlib

class ConversationMemory:
    """Stores conversation history and context for each user"""
    
    def __init__(self):
        self.conversations = {}  # user_id -> list of messages
        self.context = {}  # user_id -> current context
        self.max_history = 10  # Remember last 10 messages
    
    def add_message(self, user_id: str, message: str, response: str):
        """Add a message to conversation history"""
        if user_id not in self.conversations:
            self.conversations[user_id] = []
            self.context[user_id] = {}
        
        self.conversations[user_id].append({
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'response': response
        })
        
        # Keep only last max_history messages
        if len(self.conversations[user_id]) > self.max_history:
            self.conversations[user_id] = self.conversations[user_id][-self.max_history:]
    
    def get_last_message(self, user_id: str) -> Optional[Dict]:
        """Get the last message from a user"""
        if user_id in self.conversations and self.conversations[user_id]:
            return self.conversations[user_id][-1]
        return None
    
    def get_conversation_summary(self, user_id: str) -> str:
        """Get a summary of the conversation for context"""
        if user_id not in self.conversations:
            return ""
        
        summary = []
        for msg in self.conversations[user_id][-3:]:  # Last 3 messages
            summary.append(f"User: {msg['message']}")
            summary.append(f"Assistant: {msg['response'][:100]}...")
        
        return "\n".join(summary)
    
    def set_context(self, user_id: str, key: str, value: Any):
        """Set context value for a user"""
        if user_id not in self.context:
            self.context[user_id] = {}
        self.context[user_id][key] = value
    
    def get_context(self, user_id: str, key: str, default=None) -> Any:
        """Get context value for a user"""
        if user_id in self.context:
            return self.context[user_id].get(key, default)
        return default
    
    def detect_intent(self, message: str, user_id: str = None) -> Dict:
        """Detect what the user is asking about, using context"""
        message_lower = message.lower()
        
        # Intent patterns
        intents = {
            'greeting': ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening'],
            'thanks': ['thanks', 'thank you', 'appreciate', 'thx'],
            'what_is': ['what is', 'tell me about', 'about', 'explain'],
            'how_to': ['how to', 'how do i', 'how can i', 'steps to', 'guide'],
            'can_i': ['can i', 'is it possible', 'am i able', 'do you allow'],
            'delete': ['delete', 'remove', 'close account', 'cancel account'],
            'create': ['create', 'sign up', 'register', 'make account', 'new account'],
            'book': ['book', 'booking', 'schedule', 'appointment', 'reserve', 'hire'],
            'rate': ['rate', 'rating', 'review', 'feedback', 'star'],
            'pay': ['pay', 'payment', 'money', 'cost', 'price', 'fee'],
            'support': ['support', 'help', 'contact', 'customer service']
        }
        
        # Check for follow-up patterns
        follow_up_patterns = ['what about', 'how about', 'and', 'also', 'then', 'what regarding']
        is_follow_up = any(pattern in message_lower for pattern in follow_up_patterns)
        
        # Detect primary intent
        detected_intent = 'general'
        confidence = 0
        
        for intent, patterns in intents.items():
            for pattern in patterns:
                if pattern in message_lower:
                    # If it's a follow-up, give higher weight to related intents
                    if is_follow_up and user_id:
                        last_intent = self.get_context(user_id, 'last_intent')
                        if last_intent and intent == last_intent:
                            confidence += 30
                    
                    confidence += 10
                    detected_intent = intent
        
        return {
            'intent': detected_intent,
            'confidence': min(100, confidence),
            'is_follow_up': is_follow_up,
            'keywords': [w for w in message_lower.split() if len(w) > 3]
        }
    
    def extract_topic(self, message: str) -> str:
        """Extract the main topic from a message"""
        message_lower = message.lower()
        
        # Remove common question words
        question_words = ['what', 'how', 'can', 'do', 'is', 'are', 'about', 'tell', 'me']
        for word in question_words:
            message_lower = message_lower.replace(word, '')
        
        # Extract key nouns
        words = message_lower.split()
        key_words = [w for w in words if len(w) > 3]
        
        if key_words:
            return ' '.join(key_words[:2])  # Return first two key words
        return message

class HumanizedNetraEngine:
    """
    Netra AI Assistant with memory and conversation understanding
    """
    
    def __init__(self):
        self.base_url = "https://netra.strobid.com"
        self.help_url = "https://netra.strobid.com/help"
        self.memory = ConversationMemory()
        self.knowledge_base = self._initialize_knowledge()
        
        # Cache for fetched pages
        self.page_cache = {}
        self.last_fetch = None
    
    def _initialize_knowledge(self) -> Dict:
        """Initialize base knowledge about Netra"""
        return {
            'what_is_netra': {
                'title': 'What is Netra?',
                'content': [
                    'Netra is Africa\'s trusted service marketplace connecting skilled professionals with clients.',
                    'Netra is a professional social app that connects service providers with clients in their community.',
                    'Service providers can showcase their work and clients can find reliable services - from plumbing to music lessons.',
                    'The app features service bookings, ratings, music streaming, and professional reels.',
                    'Built by Strobid and based in Kampala, Uganda, serving East Africa.'
                ],
                'keywords': ['netra', 'app', 'platform', 'marketplace', 'service']
            },
            'strobid': {
                'title': 'What is Strobid?',
                'content': [
                    'Strobid is the parent company behind Netra, founded by Nowamaani Donath.',
                    'Strobid is a programming hub and technology company based in Kampala, Uganda.',
                    'The company focuses on building innovative digital solutions for the East African market.',
                    'Netra is Strobid\'s flagship product - a professional service marketplace app.'
                ],
                'keywords': ['strobid', 'company', 'parent', 'founder', 'creator']
            }
        }
    
    def _fetch_page_content(self, url: str) -> Optional[str]:
        """Fetch and cache page content"""
        # Check cache first
        if url in self.page_cache:
            cache_time, content = self.page_cache[url]
            if datetime.now() - cache_time < timedelta(hours=1):
                return content
        
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'footer']):
                element.decompose()
            
            # Get main content
            main = soup.find('main') or soup.find('article') or soup.body
            text = main.get_text(separator='\n', strip=True) if main else ''
            
            # Cache it
            self.page_cache[url] = (datetime.now(), text)
            return text
            
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def _search_help_center(self, query: str) -> Optional[Dict]:
        """Search the help center for relevant information"""
        content = self._fetch_page_content(self.help_url)
        if not content:
            return None
        
        # Simple relevance scoring
        query_lower = query.lower()
        lines = content.split('\n')
        
        relevant_lines = []
        score = 0
        
        for line in lines:
            line_lower = line.lower()
            if len(line) > 30:  # Only meaningful lines
                if any(word in line_lower for word in query_lower.split()):
                    relevant_lines.append(line)
                    score += 1
        
        if relevant_lines:
            return {
                'content': '\n'.join(relevant_lines[:3]),
                'source': 'help center',
                'score': score
            }
        
        return None
    
    def _generate_response(self, message: str, user_id: str) -> str:
        """Generate a response based on message and conversation history"""
        
        # Get intent
        intent_info = self.memory.detect_intent(message, user_id)
        intent = intent_info['intent']
        is_follow_up = intent_info['is_follow_up']
        
        # Get last message for context
        last_msg = self.memory.get_last_message(user_id)
        
        # Store current intent for future context
        self.memory.set_context(user_id, 'last_intent', intent)
        
        # Handle based on intent
        if intent == 'greeting':
            if last_msg:
                return "Hello again! How can I help you with Netra today?"
            return "Hello! I'm your Netra assistant. I can help you with accounts, bookings, payments, ratings, and more. What would you like to know?"
        
        elif intent == 'thanks':
            return "You're welcome! 😊 Is there anything else you'd like to know about Netra?"
        
        elif intent == 'what_is':
            # Check knowledge base first
            for key, info in self.knowledge_base.items():
                if any(kw in message.lower() for kw in info['keywords']):
                    response = f"**{info['title']}**\n\n"
                    response += '\n'.join(info['content'])
                    return response
            
            # Search help center
            result = self._search_help_center(message)
            if result:
                return f"Here's what I found:\n\n{result['content']}"
            
            return "Netra is a professional service marketplace connecting skilled providers with clients in their community."
        
        elif intent == 'how_to' or intent == 'can_i':
            # Handle specific topics
            topic = self.memory.extract_topic(message)
            
            # Use context if this is a follow-up
            if is_follow_up and last_msg:
                last_topic = self.memory.get_context(user_id, 'last_topic')
                if last_topic:
                    topic = last_topic + ' ' + topic
            
            # Store topic for follow-ups
            self.memory.set_context(user_id, 'last_topic', topic)
            
            # Handle different topics
            if any(word in topic for word in ['create', 'sign', 'register', 'account']):
                return (
                    "**Creating a Netra Account**\n\n"
                    "Yes, you can create a Netra account! Here's how:\n\n"
                    "1. Download the Netra app from Google Play Store\n"
                    "2. Open the app and tap 'Create Account'\n"
                    "3. Enter your email and create a password\n"
                    "4. Fill in your profile information\n"
                    "5. Check your email for verification\n"
                    "6. Enter the code to verify your account"
                )
            
            elif any(word in topic for word in ['delete', 'remove', 'close']):
                return (
                    "**Deleting Your Netra Account**\n\n"
                    "Yes, you can delete your account. Here's how:\n\n"
                    "1. Open the Netra app and log in\n"
                    "2. Go to Settings > Account > Delete Account\n"
                    "3. Read the warning carefully\n"
                    "4. Enter your password to confirm\n"
                    "5. Tap 'Permanently Delete'\n\n"
                    "⚠️ This action is PERMANENT and cannot be undone!"
                )
            
            elif any(word in topic for word in ['book', 'booking', 'hire']):
                return (
                    "**Booking Services on Netra**\n\n"
                    "Here's how bookings work:\n\n"
                    "1. Find a provider you like (browse or search)\n"
                    "2. Check their profile and reviews\n"
                    "3. Tap 'Book Now' or 'Contact'\n"
                    "4. Select the service and date/time\n"
                    "5. Review the price and confirm\n"
                    "6. Communicate with the provider through the app\n\n"
                    "You can manage all your bookings in the app!"
                )
            
            elif any(word in topic for word in ['rate', 'rating', 'review']):
                return (
                    "**Ratings & Reviews on Netra**\n\n"
                    "Here's how ratings work:\n\n"
                    "1. After a service is completed, you'll get a notification\n"
                    "2. Go to the booking in your history\n"
                    "3. Tap 'Rate Your Experience'\n"
                    "4. Give a star rating (1-5 stars)\n"
                    "5. Write a brief review (optional)\n"
                    "6. Submit your rating\n\n"
                    "Ratings help other clients find quality providers!"
                )
            
            elif any(word in topic for word in ['pay', 'payment', 'money']):
                return (
                    "**Payments on Netra**\n\n"
                    "Here's how payments work:\n\n"
                    "• See the total price when booking\n"
                    "• Choose payment method (card, mobile money, cash)\n"
                    "• Pay a deposit to confirm booking\n"
                    "• Pay balance after service completion\n"
                    "• Funds are held securely until you're satisfied\n"
                    "• Providers get paid within 24 hours\n\n"
                    "Accepted payments: Visa, Mastercard, MTN Mobile Money, Airtel Money"
                )
            
            elif any(word in topic for word in ['support', 'help', 'contact']):
                return (
                    "**Contact Netra Support**\n\n"
                    "You can reach our support team:\n\n"
                    "📧 Email: support@strobid.com\n"
                    "💬 In-app chat: Settings > Help & Support\n"
                    "📱 Help Center: https://netra.strobid.com/help\n\n"
                    "Response time: Within 24 hours"
                )
            
            # If no specific match, search help center
            result = self._search_help_center(message)
            if result:
                return f"Here's what I found about that:\n\n{result['content']}"
            
            return f"I can help you with that! Could you be more specific about what you'd like to know about {topic}?"
        
        # Default response
        return "I'm here to help with Netra! You can ask me about creating accounts, making bookings, ratings and reviews, payments, or contacting support. What would you like to know?"
    
    def process_query(self, message: str, user_id: str = None) -> Dict[str, Any]:
        """Process user query with memory and context"""
        try:
            # Use a default user_id if none provided
            if not user_id:
                user_id = hashlib.md5(message.encode()).hexdigest()
            
            print(f"\n👤 User {user_id[:8]}: {message}")
            
            # Generate response
            response = self._generate_response(message, user_id)
            
            # Store in memory
            self.memory.add_message(user_id, message, response)
            
            # Generate suggestions based on context
            last_intent = self.memory.get_context(user_id, 'last_intent', 'general')
            
            suggestions_map = {
                'greeting': [
                    "What is Netra?",
                    "How do I create an account?",
                    "How do bookings work?"
                ],
                'what_is': [
                    "Tell me about Strobid",
                    "What services are available?",
                    "How do I get started?"
                ],
                'how_to': [
                    "How do I delete my account?",
                    "How do ratings work?",
                    "How do I contact support?"
                ],
                'can_i': [
                    "Can I book a service?",
                    "Can I rate providers?",
                    "Can I get a refund?"
                ],
                'delete': [
                    "What happens after deletion?",
                    "Can I recover my account?",
                    "How to create new account?"
                ],
                'create': [
                    "How to verify account?",
                    "How to reset password?",
                    "How to update profile?"
                ],
                'book': [
                    "How to cancel booking?",
                    "How to reschedule?",
                    "How payments work?"
                ],
                'rate': [
                    "Can I edit my review?",
                    "How are ratings calculated?",
                    "What if bad service?"
                ],
                'pay': [
                    "What payment methods?",
                    "Are there fees?",
                    "How do refunds work?"
                ],
                'support': [
                    "Email support",
                    "Live chat hours",
                    "Help Center"
                ]
            }
            
            suggestions = suggestions_map.get(last_intent, [
                "What is Netra?",
                "How do I create an account?",
                "How do bookings work?",
                "How do I contact support?"
            ])
            
            return {
                'response': response,
                'suggestions': suggestions[:4],
                'confidence': 90,
                'engine_used': 'netra_engine_with_memory',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"❌ Error: {e}")
            return {
                'response': "I'm here to help with Netra! You can ask me about accounts, bookings, payments, ratings, and more. What would you like to know?",
                'suggestions': [
                    "What is Netra?",
                    "How do I create an account?",
                    "How do bookings work?",
                    "How do I contact support?"
                ],
                'confidence': 70,
                'engine_used': 'netra_engine_with_memory',
                'timestamp': datetime.now().isoformat()
            }

# Create the instance
netra_engine = HumanizedNetraEngine()