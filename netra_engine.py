"""
Netra Engine - Fixed version with proper query matching
"""

import requests
import random
import re
import time
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from urllib.parse import urljoin
import hashlib
from bs4 import BeautifulSoup

class HumanizedNetraEngine:
    """
    AI Engine with proper query matching
    """
    
    def __init__(self):
        self.help_center_url = "https://netra.strobid.com/help"
        self.base_url = "https://netra.strobid.com"
        
        # Comprehensive knowledge base with proper articles
        self.articles = {
            'what_is_netra': {
                'title': 'What is Netra?',
                'summary': 'Netra is Africa\'s trusted service marketplace connecting skilled professionals with clients.',
                'details': [
                    'Netra is a professional social app that connects service providers with clients in their community.',
                    'Service providers can showcase their work and clients can find reliable services - from plumbing to music lessons.',
                    'The app features service bookings, ratings, music streaming, and professional reels.',
                    'Built by Strobid and based in Kampala, Uganda, serving East Africa.'
                ],
                'keywords': ['what is netra', 'about netra', 'netra app', 'netra do', 'what does netra do', 'netra explained'],
                'topic': 'general'
            },
            'create_account': {
                'title': 'How to create a Netra account',
                'summary': 'Creating a Netra account is quick and easy. Follow these steps to get started.',
                'steps': [
                    'Download the Netra app from the Google Play Store',
                    'Open the app and tap "Create Account"',
                    'Enter your email address and create a secure password',
                    'Fill in your profile information (name, phone number)',
                    'Check your email for a verification code',
                    'Enter the code to verify your account'
                ],
                'keywords': ['create account', 'sign up', 'register', 'new account', 'join netra', 'how to create', 'make account'],
                'topic': 'account'
            },
            'verify_account': {
                'title': 'How to verify your account',
                'summary': 'Account verification helps build trust in the Netra community.',
                'steps': [
                    'Log in to your Netra account',
                    'Go to Settings > Account > Verification',
                    'Choose email or phone verification',
                    'Check your inbox for a verification link',
                    'Enter the code sent to your phone',
                    'Your account is now verified!'
                ],
                'keywords': ['verify account', 'verification', 'confirm account', 'verify email', 'verify phone', 'get verified'],
                'topic': 'account'
            },
            'reset_password': {
                'title': 'How to reset your password',
                'summary': "Forgot your password? Here's how to reset it safely.",
                'steps': [
                    'Open the Netra app',
                    'Tap "Forgot Password" on the login screen',
                    'Enter your registered email address',
                    'Check your email for a reset link',
                    'Click the link (valid for 1 hour)',
                    'Create a new strong password'
                ],
                'keywords': ['reset password', 'forgot password', 'change password', 'new password', 'password reset'],
                'topic': 'account'
            },
            'delete_account': {
                'title': 'How to delete your Netra account',
                'summary': 'Step-by-step guide to permanently remove your account.',
                'steps': [
                    'Open the Netra app and log in',
                    'Go to Settings > Account > Delete Account',
                    'Read the warning carefully',
                    'Enter your password to confirm',
                    'Select a reason for leaving (optional)',
                    'Tap "Permanently Delete"'
                ],
                'warnings': ['This action is PERMANENT and cannot be undone'],
                'keywords': ['delete account', 'remove account', 'close account', 'cancel account', 'deactivate'],
                'topic': 'account'
            },
            'payments': {
                'title': 'How payments work on Netra',
                'summary': 'Understand how to make, track, and manage payments.',
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
                'topic': 'payment'
            },
            'subscriptions': {
                'title': 'Manage subscriptions & billing',
                'summary': 'Learn how to subscribe, cancel, or update your plan.',
                'steps': [
                    'Go to Settings > Subscription',
                    'Browse available plans (Free, Pro, Business)',
                    'Select your preferred plan',
                    'Choose monthly or annual billing',
                    'Enter payment details',
                    'Confirm subscription'
                ],
                'keywords': ['subscription', 'premium', 'plan', 'upgrade', 'downgrade', 'billing', 'subscribe'],
                'topic': 'payment'
            },
            'notifications': {
                'title': 'Manage notifications',
                'summary': 'Turn on/off alerts and notifications in Netra.',
                'steps': [
                    'Open Netra app',
                    'Go to Settings > Notifications',
                    'Toggle each notification type on/off',
                    '• Message notifications',
                    '• Booking updates',
                    '• Payment notifications',
                    '• Promotional offers'
                ],
                'keywords': ['notification', 'alert', 'notifications', 'turn off notifications', 'manage alerts', 'push notification'],
                'topic': 'settings'
            },
            'contact_support': {
                'title': 'Contact Netra support',
                'summary': 'Reach out to our support team for personalized help.',
                'details': [
                    'Email: support@strobid.com',
                    'In-app chat: Settings > Help & Support',
                    'Help Center: https://netra.strobid.com/help',
                    'Response time: Within 24 hours',
                    'Support hours: Monday-Friday 8AM-8PM (EAT)'
                ],
                'keywords': ['contact support', 'customer service', 'help desk', 'get help', 'support team', 'reach netra'],
                'topic': 'support'
            }
        }
        
        # Group by topic for suggestions
        self.topics = {}
        for article_id, article in self.articles.items():
            topic = article['topic']
            if topic not in self.topics:
                self.topics[topic] = []
            self.topics[topic].append(article_id)
    
    def _find_best_article(self, query: str) -> Optional[Dict]:
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
            
            # Check title words
            title_words = article['title'].lower().split()
            for word in query_lower.split():
                if word in title_words:
                    score += 5
            
            # Special handling for "what does netra do"
            if 'what' in query_lower and 'do' in query_lower and article_id == 'what_is_netra':
                score += 15
            
            # Special handling for delete vs create
            if 'delete' in query_lower and article_id == 'delete_account':
                score += 20
            if 'create' in query_lower and article_id == 'create_account':
                score += 20
            
            if score > best_score:
                best_score = score
                best_match = article
        
        return best_match
    
    def _format_article_response(self, article: Dict) -> str:
        """Format article into natural response"""
        response_parts = []
        
        # Title
        response_parts.append(f"**{article['title']}**")
        
        # Summary
        if article.get('summary'):
            response_parts.append(article['summary'])
        
        # Steps
        if article.get('steps'):
            response_parts.append("\n**Here's how:**")
            for i, step in enumerate(article['steps'], 1):
                response_parts.append(f"{i}. {step}")
        
        # Details
        if article.get('details') and not article.get('steps'):
            response_parts.append("\n" + '\n'.join(article['details']))
        
        # Warnings
        if article.get('warnings'):
            response_parts.append(f"\n⚠️ **Important:** {article['warnings'][0]}")
        
        return '\n'.join(response_parts)
    
    def _get_topic_suggestions(self, topic: str) -> List[str]:
        """Get suggestions based on topic"""
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
                "How do I get a refund?"
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
        return suggestion_map.get(topic, suggestion_map['general'])
    
    def process_query(self, message: str, user_id: str = None) -> Dict[str, Any]:
        """Process user query with proper matching"""
        try:
            print(f"\n🤔 Processing: {message}")
            
            # Handle greetings
            greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon']
            if any(g in message.lower() for g in greetings):
                return {
                    'response': "Hello! 👋 I'm your Netra assistant. I can help you with accounts, payments, settings, and more. What would you like to know?",
                    'suggestions': [
                        "What is Netra?",
                        "How do I create an account?",
                        "How do payments work?",
                        "How do I contact support?"
                    ],
                    'confidence': 100,
                    'engine_used': 'netra_engine',
                    'help_center_url': self.help_center_url,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Find best matching article
            article = self._find_best_article(message)
            
            if article:
                print(f"✅ Found: {article['title']}")
                response = self._format_article_response(article)
                suggestions = self._get_topic_suggestions(article.get('topic', 'general'))
                
                return {
                    'response': response,
                    'suggestions': suggestions[:4],
                    'confidence': 95,
                    'engine_used': 'netra_engine',
                    'help_center_url': self.help_center_url,
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
                        "How do I create an account?",
                        "How do payments work?",
                        "How do I contact support?"
                    ],
                    'confidence': 80,
                    'engine_used': 'netra_engine',
                    'help_center_url': self.help_center_url,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return {
                'response': "I'm here to help with Netra! You can ask me about:\n\n• What Netra is\n• Creating an account\n• Making payments\n• Contacting support",
                'suggestions': [
                    "What is Netra?",
                    "How do I create an account?",
                    "How do payments work?",
                    "How do I contact support?"
                ],
                'confidence': 70,
                'engine_used': 'netra_engine',
                'help_center_url': self.help_center_url,
                'timestamp': datetime.now().isoformat()
            }

# Create the instance
netra_engine = HumanizedNetraEngine()