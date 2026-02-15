"""
Netra Engine - Final Version with ABSOLUTELY NO LINKS unless explicitly requested
"""

import random
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

class HumanizedNetraEngine:
    """
    Netra AI Assistant - ZERO links in responses unless user asks for them
    """
    
    def __init__(self):
        self.help_center_url = "https://netra.strobid.com/help"  # Store but NEVER use
        self.base_url = "https://netra.strobid.com"
        
        # Complete knowledge base with URLs for each article
        self.articles = {
            'what_is_netra': {
                'title': 'What is Netra?',
                'content': [
                    'Netra is Africa\'s trusted service marketplace connecting skilled professionals with clients.',
                    'Netra is a professional social app that connects service providers with clients in their community.',
                    'Service providers can showcase their work and clients can find reliable services - from plumbing to music lessons.',
                    'The app features service bookings, ratings, music streaming, and professional reels.',
                    'Built by Strobid and based in Kampala, Uganda, serving East Africa.'
                ],
                'keywords': ['what is netra', 'about netra', 'netra app', 'netra do', 'what does netra do', 'netra explained', 'tell me about netra'],
                'topic': 'general',
                'url': 'https://netra.strobid.com/about'
            },
            'create_account': {
                'title': 'How to create a Netra account',
                'steps': [
                    'Download the Netra app from the Google Play Store',
                    'Open the app and tap "Create Account"',
                    'Enter your email address and create a secure password',
                    'Fill in your profile information (name, phone number)',
                    'Check your email for a verification code',
                    'Enter the code to verify your account'
                ],
                'keywords': ['create account', 'sign up', 'register', 'new account', 'join netra', 'how to create', 'make account', 'create netra account'],
                'topic': 'account',
                'url': 'https://netra.strobid.com/help/create-account.html'
            },
            'verify_account': {
                'title': 'How to verify your account',
                'steps': [
                    'Log in to your Netra account',
                    'Go to Settings > Account > Verification',
                    'Choose email or phone verification',
                    'Check your inbox for a verification link',
                    'Enter the code sent to your phone',
                    'Your account is now verified!'
                ],
                'keywords': ['verify account', 'verification', 'confirm account', 'verify email', 'verify phone', 'get verified'],
                'topic': 'account',
                'url': 'https://netra.strobid.com/help/verify-account.html'
            },
            'reset_password': {
                'title': 'How to reset your password',
                'steps': [
                    'Open the Netra app',
                    'Tap "Forgot Password" on the login screen',
                    'Enter your registered email address',
                    'Check your email for a reset link',
                    'Click the link (valid for 1 hour)',
                    'Create a new strong password'
                ],
                'keywords': ['reset password', 'forgot password', 'change password', 'new password', 'password reset'],
                'topic': 'account',
                'url': 'https://netra.strobid.com/help/reset-password.html'
            },
            'delete_account': {
                'title': 'How to delete your Netra account',
                'steps': [
                    'Open the Netra app and log in',
                    'Go to Settings > Account > Delete Account',
                    'Read the warning carefully',
                    'Enter your password to confirm',
                    'Select a reason for leaving (optional)',
                    'Tap "Permanently Delete"'
                ],
                'warnings': ['⚠️ This action is PERMANENT and cannot be undone'],
                'keywords': ['delete account', 'remove account', 'close account', 'cancel account', 'deactivate', 'delete netra account'],
                'topic': 'account',
                'url': 'https://netra.strobid.com/help/delete-account.html'
            },
            'payments': {
                'title': 'How payments work on Netra',
                'steps': [
                    'See the total price when booking a service',
                    'Choose your payment method (card, mobile money, cash)',
                    'Pay a deposit to confirm your booking',
                    'Pay the balance after service completion',
                    'Funds are held securely until you\'re satisfied',
                    'Providers receive payment within 24 hours'
                ],
                'details': [
                    'Accepted payments: Visa, Mastercard, MTN Mobile Money, Airtel Money',
                    'No fees for clients - you pay only the service price',
                    'Providers pay a small commission on completed bookings'
                ],
                'keywords': ['payment', 'pay', 'how payments work', 'payment methods', 'mobile money', 'credit card', 'debit card'],
                'topic': 'payment',
                'url': 'https://netra.strobid.com/help/payments.html'
            },
            'subscriptions': {
                'title': 'Manage subscriptions & billing',
                'steps': [
                    'Go to Settings > Subscription',
                    'Browse available plans (Free, Pro, Business)',
                    'Select your preferred plan',
                    'Choose monthly or annual billing',
                    'Enter payment details',
                    'Confirm subscription'
                ],
                'keywords': ['subscription', 'premium', 'plan', 'upgrade', 'downgrade', 'billing', 'subscribe'],
                'topic': 'payment',
                'url': 'https://netra.strobid.com/help/subscriptions.html'
            },
            'notifications': {
                'title': 'Manage notifications',
                'steps': [
                    'Open Netra app',
                    'Go to Settings > Notifications',
                    'Toggle each notification type on/off:',
                    '• Message notifications',
                    '• Booking updates',
                    '• Payment notifications',
                    '• Promotional offers'
                ],
                'keywords': ['notification', 'alert', 'notifications', 'turn off notifications', 'manage alerts', 'push notification'],
                'topic': 'settings',
                'url': 'https://netra.strobid.com/help/notifications.html'
            },
            'contact_support': {
                'title': 'Contact Netra support',
                'details': [
                    'Email: support@strobid.com',
                    'In-app chat: Settings > Help & Support',
                    'Response time: Within 24 hours',
                    'Support hours: Monday-Friday 8AM-8PM (EAT)'
                ],
                'keywords': ['contact support', 'customer service', 'help desk', 'get help', 'support team', 'reach netra'],
                'topic': 'support',
                'url': 'https://netra.strobid.com/help/contact-support.html'
            }
        }
        
        # Group by topic for suggestions
        self.topics = {}
        for article_id, article in self.articles.items():
            topic = article['topic']
            if topic not in self.topics:
                self.topics[topic] = []
            self.topics[topic].append(article_id)
        
        # Conversation context
        self.context = {}
    
    def _is_link_request(self, query: str) -> bool:
        """Check if user is asking for a link"""
        query_lower = query.lower()
        link_keywords = [
            'link', 'url', 'website', 'page', 'webpage', 'site',
            'where can i find', 'where do i go', 'take me to',
            'link to', 'url for', 'website for', 'page for',
            'online', 'on the web', 'internet page',
            'send me the link', 'give me the link', 'provide link'
        ]
        return any(keyword in query_lower for keyword in link_keywords)
    
    def _extract_requested_topic(self, query: str) -> Optional[str]:
        """Extract what topic the user wants a link for"""
        query_lower = query.lower()
        
        # Remove link-related words
        link_words = ['link', 'url', 'website', 'page', 'to', 'for', 'the', 'give', 'send', 'provide', 'need', 'me', 'get', 'find', 'where', 'can', 'i']
        for word in link_words:
            query_lower = query_lower.replace(word, '')
        
        query_lower = query_lower.strip()
        
        # If query is too short after cleaning, return None
        if len(query_lower) < 3:
            return None
        
        # Match against article keywords
        best_match = None
        best_score = 0
        
        for article_id, article in self.articles.items():
            for keyword in article.get('keywords', []):
                if keyword in query_lower:
                    score = len(keyword)
                    if score > best_score:
                        best_score = score
                        best_match = article_id
        
        return best_match
    
    def _find_best_article(self, query: str, user_id: str = None) -> Optional[Dict]:
        """Find the best matching article based on keywords"""
        query_lower = query.lower()
        
        best_match = None
        best_score = 0
        
        for article_id, article in self.articles.items():
            score = 0
            
            # Check keywords
            for keyword in article.get('keywords', []):
                if keyword in query_lower:
                    score += 10
            
            # Check for exact matches in title
            if query_lower in article['title'].lower():
                score += 15
            
            # Boost score for very specific queries
            if 'delete' in query_lower and 'delete' in article['title'].lower():
                score += 20
            if 'create' in query_lower and 'create' in article['title'].lower():
                score += 20
            if 'verify' in query_lower and 'verify' in article['title'].lower():
                score += 20
            if 'reset' in query_lower and 'reset' in article['title'].lower():
                score += 20
            
            # Use context from previous conversation
            if user_id and user_id in self.context:
                prev_topic = self.context[user_id].get('last_topic')
                if prev_topic and prev_topic == article['topic']:
                    score += 5
            
            if score > best_score:
                best_score = score
                best_match = article
        
        # If no good match, check for general help
        if best_score < 5 and any(word in query_lower for word in ['help', 'support', 'question', 'assist']):
            return self.articles.get('contact_support')
        
        return best_match
    
    def _format_article_response(self, article: Dict) -> str:
        """Format article into natural response - ABSOLUTELY NO LINKS"""
        response_parts = []
        
        # Title
        response_parts.append(f"**{article['title']}**")
        response_parts.append('')  # Empty line for spacing
        
        # Content (either from 'content' field or build from steps/details)
        if 'content' in article:
            # For 'what is' type articles
            response_parts.extend(article['content'])
        else:
            # For 'how to' type articles with steps
            if article.get('steps'):
                response_parts.extend(article['steps'])
            
            # Add any additional details
            if article.get('details'):
                if response_parts:  # Add spacing if we already have content
                    response_parts.append('')
                response_parts.extend(article['details'])
            
            # Add warnings at the end
            if article.get('warnings'):
                response_parts.append('')
                response_parts.extend(article['warnings'])
        
        # Join with newlines - ABSOLUTELY NO LINK ADDED
        return '\n'.join(response_parts)
    
    def _format_link_response(self, article: Dict) -> str:
        """Format a response that ONLY gives the link"""
        return f"Here's the direct link you requested:\n\n🔗 {article['url']}\n\nThis page contains detailed information about {article['title'].lower()}."
    
    def _get_suggestions(self, topic: str, current_article: Dict = None) -> List[str]:
        """Get relevant follow-up suggestions"""
        suggestion_map = {
            'general': [
                "What is Netra?",
                "How do I create an account?",
                "How do payments work?"
            ],
            'account': [
                "How do I verify my account?",
                "How do I reset my password?",
                "How do I delete my account?"
            ],
            'payment': [
                "How do payments work?",
                "What payment methods are accepted?",
                "How do subscriptions work?"
            ],
            'settings': [
                "How do I manage notifications?",
                "How do I change my profile?",
                "Privacy settings"
            ],
            'support': [
                "How do I contact support?",
                "What are your support hours?",
                "Email support"
            ]
        }
        
        # Get base suggestions for the topic
        suggestions = suggestion_map.get(topic, suggestion_map['general'])[:3]
        
        # Add link suggestion if we have a current article
        if current_article:
            # Extract the main action word from the article title
            title = current_article['title'].lower()
            if 'create' in title:
                suggestions.append("Link for creating account")
            elif 'delete' in title:
                suggestions.append("Link for deleting account")
            elif 'verify' in title:
                suggestions.append("Link for account verification")
            elif 'reset' in title:
                suggestions.append("Link for password reset")
            elif 'payment' in title:
                suggestions.append("Link for payments")
            elif 'notification' in title:
                suggestions.append("Link for notifications")
            elif 'support' in title:
                suggestions.append("Link for support")
            elif 'what is' in title or 'about' in title:
                suggestions.append("Link for Netra info")
            else:
                suggestions.append(f"Link for {current_article['title']}")
        
        return suggestions
    
    def process_query(self, message: str, user_id: str = None) -> Dict[str, Any]:
        """Process user query - NO LINKS unless requested"""
        try:
            print(f"\n🤔 Processing: {message}")
            
            # Handle greetings
            greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
            if any(g in message.lower() for g in greetings):
                # Check if it's a repeat greeting
                if user_id and user_id in self.context and self.context[user_id].get('last_greeting'):
                    greeting_response = "Hello again! How can I assist you today?"
                else:
                    greeting_response = "Hello! How can I assist you today?"
                
                # Store greeting context
                if user_id:
                    if user_id not in self.context:
                        self.context[user_id] = {}
                    self.context[user_id]['last_greeting'] = True
                
                return {
                    'response': greeting_response,  # NO LINK HERE
                    'suggestions': [
                        "What is Netra?",
                        "How do I create an account?",
                        "How do payments work?"
                    ],
                    'confidence': 100,
                    'engine_used': 'netra_engine',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Handle thanks
            thanks = ['thanks', 'thank you', 'appreciate it', 'thx']
            if any(t in message.lower() for t in thanks):
                return {
                    'response': "You're welcome! 😊 If you have any more questions, feel free to ask.",  # NO LINK HERE
                    'suggestions': [
                        "What is Netra?",
                        "How do I create an account?",
                        "How do payments work?"
                    ],
                    'confidence': 100,
                    'engine_used': 'netra_engine',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Check if this is a link request
            is_link_request = self._is_link_request(message)
            
            if is_link_request:
                # Extract what they want a link for
                topic_id = self._extract_requested_topic(message)
                
                if topic_id and topic_id in self.articles:
                    article = self.articles[topic_id]
                    response = self._format_link_response(article)
                    
                    # Suggestions after giving a link
                    suggestions = [
                        f"Tell me about {article['title']}",
                        "What is Netra?",
                        "How do payments work?"
                    ]
                    
                    return {
                        'response': response,  # ONLY HERE DO LINKS APPEAR
                        'suggestions': suggestions[:4],
                        'confidence': 98,
                        'engine_used': 'netra_engine',
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    # If we can't figure out what link they want
                    return {
                        'response': "I'd be happy to provide a link! Which topic are you interested in? You can ask for links about:\n\n• Creating an account\n• Making payments\n• Contacting support\n• Deleting your account",  # NO LINK HERE
                        'suggestions': [
                            "Link for creating account",
                            "Link for payments",
                            "Link for support",
                            "What is Netra?"
                        ],
                        'confidence': 85,
                        'engine_used': 'netra_engine',
                        'timestamp': datetime.now().isoformat()
                    }
            
            # Not a link request - find best article
            article = self._find_best_article(message, user_id)
            
            if article:
                print(f"✅ Found: {article['title']}")
                
                # Format response WITHOUT any link
                response = self._format_article_response(article)
                
                # Get suggestions including link option
                suggestions = self._get_suggestions(article.get('topic', 'general'), article)
                
                # Store context
                if user_id:
                    if user_id not in self.context:
                        self.context[user_id] = {}
                    self.context[user_id]['last_topic'] = article.get('topic', 'general')
                    self.context[user_id]['last_article'] = article['title']
                
                return {
                    'response': response,  # NO LINK HERE
                    'suggestions': suggestions[:4],
                    'confidence': 95,
                    'engine_used': 'netra_engine',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Show available topics
                response = "I can help you with these topics:\n\n"
                for topic in self.topics.keys():
                    response += f"• {topic.capitalize()}\n"
                response += "\nWhat would you like to know about Netra?"  # NO LINK HERE
                
                return {
                    'response': response,
                    'suggestions': [
                        "What is Netra?",
                        "How do I create an account?",
                        "How do payments work?"
                    ],
                    'confidence': 80,
                    'engine_used': 'netra_engine',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return {
                'response': "I'm here to help with Netra! You can ask me about:\n\n• What Netra is\n• Creating an account\n• Making payments\n• Contacting support",  # NO LINK HERE
                'suggestions': [
                    "What is Netra?",
                    "How do I create an account?",
                    "How do payments work?"
                ],
                'confidence': 70,
                'engine_used': 'netra_engine',
                'timestamp': datetime.now().isoformat()
            }

# Create the instance
netra_engine = HumanizedNetraEngine()