"""
Netra Engine - With natural conversational responses
"""

import random
import re
from typing import Dict, List, Optional, Any
from datetime import datetime

class HumanizedNetraEngine:
    """
    Netra AI Assistant with natural conversational responses
    """
    
    def __init__(self):
        self.help_center_url = "https://netra.strobid.com/help"  # FOR INTERNAL USE ONLY
        self.base_url = "https://netra.strobid.com"
        
        # Complete knowledge base
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
                'keywords': ['what is netra', 'about netra', 'netra app', 'netra do', 'what does netra do', 'netra explained', 'tell me about netra', 'netra'],
                'topic': 'general',
                'url': 'https://netra.strobid.com/about',
                'question_patterns': [
                    r'what.*netra',
                    r'tell.*about.*netra',
                    r'explain.*netra'
                ]
            },
            'what_is_strobid': {
                'title': 'What is Strobid?',
                'content': [
                    'Strobid is the parent company behind Netra, founded by Nowamaani Donath.',
                    'Strobid is a programming hub and technology company based in Kampala, Uganda.',
                    'The company focuses on building innovative digital solutions for the East African market.',
                    'Netra is Strobid\'s flagship product - a professional service marketplace app.'
                ],
                'keywords': ['what is strobid', 'strobid', 'strobid ltd', 'strobid company', 'about strobid', 'who made netra', 'who created netra'],
                'topic': 'company',
                'url': 'https://strobid.com/about',
                'question_patterns': [
                    r'what.*strobid',
                    r'who.*(made|created|built).*netra',
                    r'about.*strobid'
                ]
            },
            'create_account': {
                'title': 'How to create a Netra account',
                'question_response': 'Yes, absolutely! Anyone can create a Netra account. It\'s free and takes just a few minutes. Here\'s how:',
                'steps': [
                    'Download the Netra app from the Google Play Store',
                    'Open the app and tap "Create Account"',
                    'Enter your email address and create a secure password',
                    'Fill in your profile information (name, phone number)',
                    'Check your email for a verification code',
                    'Enter the code to verify your account'
                ],
                'keywords': ['create account', 'sign up', 'register', 'new account', 'join netra', 'how to create', 'make account', 'create netra account', 'can i create', 'can I create'],
                'topic': 'account',
                'url': 'https://netra.strobid.com/help/create-account.html',
                'question_patterns': [
                    r'can (i|one) create (an|a) account',
                    r'how (do|can) (i|one) (create|make|sign up)',
                    r'is it possible to create',
                    r'create (a|an) netra account'
                ]
            },
            'verify_account': {
                'title': 'How to verify your account',
                'question_response': 'Yes, account verification is required to access all features. Here\'s how to get verified:',
                'steps': [
                    'Log in to your Netra account',
                    'Go to Settings > Account > Verification',
                    'Choose email or phone verification',
                    'Check your inbox for a verification link',
                    'Enter the code sent to your phone',
                    'Your account is now verified!'
                ],
                'keywords': ['verify account', 'verification', 'confirm account', 'verify email', 'verify phone', 'get verified', 'do i need to verify'],
                'topic': 'account',
                'url': 'https://netra.strobid.com/help/verify-account.html',
                'question_patterns': [
                    r'(do|must) (i|one) verify',
                    r'how to verify',
                    r'verification (process|steps)',
                    r'is verification required'
                ]
            },
            'reset_password': {
                'title': 'How to reset your password',
                'question_response': 'Yes, you can reset your password if you\'ve forgotten it. Here\'s how:',
                'steps': [
                    'Open the Netra app',
                    'Tap "Forgot Password" on the login screen',
                    'Enter your registered email address',
                    'Check your email for a reset link',
                    'Click the link (valid for 1 hour)',
                    'Create a new strong password'
                ],
                'keywords': ['reset password', 'forgot password', 'change password', 'new password', 'password reset', 'can i reset', 'lost password'],
                'topic': 'account',
                'url': 'https://netra.strobid.com/help/reset-password.html',
                'question_patterns': [
                    r'(can|could) (i|one) reset',
                    r'(forgot|lost) (my|the) password',
                    r'how (to|do) (reset|change) password',
                    r'password (reset|recovery)'
                ]
            },
            'delete_account': {
                'title': 'How to delete your Netra account',
                'question_response': 'Yes, you can delete your account, but please note that this action is permanent and cannot be undone. Here\'s how:',
                'steps': [
                    'Open the Netra app and log in',
                    'Go to Settings > Account > Delete Account',
                    'Read the warning carefully',
                    'Enter your password to confirm',
                    'Select a reason for leaving (optional)',
                    'Tap "Permanently Delete"'
                ],
                'warnings': ['⚠️ This action is PERMANENT and cannot be undone'],
                'keywords': ['delete account', 'remove account', 'close account', 'cancel account', 'deactivate', 'delete netra account', 'can i delete'],
                'topic': 'account',
                'url': 'https://netra.strobid.com/help/delete-account.html',
                'question_patterns': [
                    r'(can|could) (i|one) delete',
                    r'how (to|do) (delete|remove|close)',
                    r'is it possible to (delete|remove)',
                    r'(delete|remove|close) (my|the) account'
                ]
            },
            'payments': {
                'title': 'How payments work on Netra',
                'question_response': 'Great question! Netra has a secure and simple payment system. Here\'s how it works:',
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
                'keywords': ['payment', 'pay', 'how payments work', 'payment methods', 'mobile money', 'credit card', 'debit card', 'can i pay'],
                'topic': 'payment',
                'url': 'https://netra.strobid.com/help/payments.html',
                'question_patterns': [
                    r'how (do|does) payments? work',
                    r'what payment methods',
                    r'can (i|one) pay (with|using)',
                    r'payment (process|system)'
                ]
            },
            'subscriptions': {
                'title': 'Manage subscriptions & billing',
                'question_response': 'Yes, Netra offers subscription plans with additional features. Here\'s what you need to know:',
                'steps': [
                    'Go to Settings > Subscription',
                    'Browse available plans (Free, Pro, Business)',
                    'Select your preferred plan',
                    'Choose monthly or annual billing',
                    'Enter payment details',
                    'Confirm subscription'
                ],
                'keywords': ['subscription', 'premium', 'plan', 'upgrade', 'downgrade', 'billing', 'subscribe', 'is there a premium'],
                'topic': 'payment',
                'url': 'https://netra.strobid.com/help/subscriptions.html',
                'question_patterns': [
                    r'(is there|do you have) (a|any) subscription',
                    r'how (do|can) (i|one) subscribe',
                    r'premium (plan|features)',
                    r'what (are the|is the) (plans|pricing)'
                ]
            },
            'notifications': {
                'title': 'Manage notifications',
                'question_response': 'Yes, you can control what notifications you receive. Here\'s how to manage them:',
                'steps': [
                    'Open Netra app',
                    'Go to Settings > Notifications',
                    'Toggle each notification type on/off:',
                    '• Message notifications',
                    '• Booking updates',
                    '• Payment notifications',
                    '• Promotional offers'
                ],
                'keywords': ['notification', 'alert', 'notifications', 'turn off notifications', 'manage alerts', 'push notification', 'can i turn off'],
                'topic': 'settings',
                'url': 'https://netra.strobid.com/help/notifications.html',
                'question_patterns': [
                    r'(can|how to) (turn (off|on)|manage) notifications',
                    r'notification (settings|preferences)',
                    r'stop (getting|receiving) alerts',
                    r'control notifications'
                ]
            },
            'contact_support': {
                'title': 'Contact Netra support',
                'question_response': 'Of course! Our support team is here to help. Here\'s how you can reach us:',
                'details': [
                    'Email: support@strobid.com',
                    'In-app chat: Settings > Help & Support',
                    'Response time: Within 24 hours',
                    'Support hours: Monday-Friday 8AM-8PM (EAT)'
                ],
                'keywords': ['contact support', 'customer service', 'help desk', 'get help', 'support team', 'reach netra', 'how to contact', 'talk to someone'],
                'topic': 'support',
                'url': 'https://netra.strobid.com/help/contact-support.html',
                'question_patterns': [
                    r'how (do|can) (i|one) (contact|reach)',
                    r'(is there|do you have) (a|any) (support|customer service)',
                    r'need (help|assistance)',
                    r'talk to (a|someone|human)'
                ]
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
        """Find the best matching article based on keywords and question patterns"""
        query_lower = query.lower()
        
        best_match = None
        best_score = 0
        
        for article_id, article in self.articles.items():
            score = 0
            
            # Check question patterns first (highest priority)
            for pattern in article.get('question_patterns', []):
                if re.search(pattern, query_lower):
                    score += 30
            
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
            if 'pay' in query_lower and 'payment' in article['title'].lower():
                score += 20
            if 'contact' in query_lower and 'support' in article['title'].lower():
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
    
    def _format_article_response(self, article: Dict, query: str) -> str:
        """Format article into natural response - answers the question first, then gives steps"""
        response_parts = []
        
        # Check if this is a yes/no question that needs acknowledgment
        is_yes_no_question = any(word in query.lower() for word in ['can i', 'do i', 'is it', 'are there', 'will i', 'should i'])
        
        # For yes/no questions, start with acknowledgment
        if is_yes_no_question and article.get('question_response'):
            response_parts.append(article['question_response'])
            response_parts.append('')  # Empty line for spacing
        else:
            # For other questions, just show the title
            response_parts.append(f"**{article['title']}**")
            response_parts.append('')
        
        # Add content
        if 'content' in article:
            # For 'what is' type articles
            response_parts.extend(article['content'])
        else:
            # For 'how to' type articles with steps
            if article.get('steps'):
                response_parts.extend(article['steps'])
            
            # Add any additional details
            if article.get('details'):
                if response_parts:
                    response_parts.append('')
                response_parts.extend(article['details'])
            
            # Add warnings at the end
            if article.get('warnings'):
                response_parts.append('')
                response_parts.extend(article['warnings'])
        
        return '\n'.join(response_parts)
    
    def _format_link_response(self, article: Dict) -> str:
        """Format a response that ONLY gives the link"""
        return f"Here's the direct link you requested:\n\n🔗 {article['url']}\n\nThis page contains detailed information about {article['title'].lower()}."
    
    def _get_suggestions(self, topic: str, current_article: Dict = None) -> List[str]:
        """Get relevant follow-up suggestions"""
        suggestion_map = {
            'general': [
                "What is Netra?",
                "Can I create an account?",
                "How do payments work?"
            ],
            'account': [
                "How do I verify my account?",
                "Can I reset my password?",
                "How do I delete my account?"
            ],
            'payment': [
                "How do payments work?",
                "What payment methods are accepted?",
                "Are there subscription plans?"
            ],
            'settings': [
                "How do I manage notifications?",
                "Can I change my profile?",
                "Privacy settings"
            ],
            'support': [
                "How do I contact support?",
                "What are your support hours?",
                "Can I talk to someone?"
            ]
        }
        
        # Get base suggestions for the topic
        suggestions = suggestion_map.get(topic, suggestion_map['general'])[:3]
        
        # Add link suggestion if we have a current article
        if current_article:
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
        """Process user query with natural conversational responses"""
        try:
            print(f"\n🤔 Processing: {message}")
            
            # Handle greetings
            greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
            if any(g in message.lower() for g in greetings):
                if user_id and user_id in self.context and self.context[user_id].get('last_greeting'):
                    greeting_response = "Hello again! How can I assist you today?"
                else:
                    greeting_response = "Hello! How can I assist you today?"
                
                if user_id:
                    if user_id not in self.context:
                        self.context[user_id] = {}
                    self.context[user_id]['last_greeting'] = True
                
                return {
                    'response': greeting_response,
                    'suggestions': [
                        "What is Netra?",
                        "Can I create an account?",
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
                    'response': "You're welcome! 😊 If you have any more questions, feel free to ask.",
                    'suggestions': [
                        "What is Netra?",
                        "Can I create an account?",
                        "How do payments work?"
                    ],
                    'confidence': 100,
                    'engine_used': 'netra_engine',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Check if this is a link request
            is_link_request = self._is_link_request(message)
            
            if is_link_request:
                topic_id = self._extract_requested_topic(message)
                
                if topic_id and topic_id in self.articles:
                    article = self.articles[topic_id]
                    response = self._format_link_response(article)
                    
                    suggestions = [
                        f"Tell me about {article['title']}",
                        "What is Netra?",
                        "How do payments work?"
                    ]
                    
                    return {
                        'response': response,
                        'suggestions': suggestions[:4],
                        'confidence': 98,
                        'engine_used': 'netra_engine',
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    return {
                        'response': "I'd be happy to provide a link! Which topic are you interested in? You can ask for links about:\n\n• Creating an account\n• Making payments\n• Contacting support\n• Deleting your account",
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
                
                # Format response with natural language
                response = self._format_article_response(article, message)
                
                # Get suggestions
                suggestions = self._get_suggestions(article.get('topic', 'general'), article)
                
                # Store context
                if user_id:
                    if user_id not in self.context:
                        self.context[user_id] = {}
                    self.context[user_id]['last_topic'] = article.get('topic', 'general')
                    self.context[user_id]['last_article'] = article['title']
                
                return {
                    'response': response,
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
                response += "\nWhat would you like to know about Netra?"
                
                return {
                    'response': response,
                    'suggestions': [
                        "What is Netra?",
                        "Can I create an account?",
                        "How do payments work?"
                    ],
                    'confidence': 80,
                    'engine_used': 'netra_engine',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return {
                'response': "I'm here to help with Netra! You can ask me about:\n\n• What Netra is\n• Creating an account\n• Making payments\n• Contacting support",
                'suggestions': [
                    "What is Netra?",
                    "Can I create an account?",
                    "How do payments work?"
                ],
                'confidence': 70,
                'engine_used': 'netra_engine',
                'timestamp': datetime.now().isoformat()
            }

# Create the instance
netra_engine = HumanizedNetraEngine()