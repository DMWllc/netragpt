"""
Netra Engine - Humanized AI Assistant for Netra App Support
Knowledge Base: https://netra.strobid.com/help
"""

import random
import re
import time
import json
import hashlib
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import html2text # type: ignore

class HumanizedNetraEngine:
    """
    Humanized AI Engine for Netra customer support
    Uses official help center as knowledge base
    """
    
    def __init__(self):
        # Core Netra information
        self.help_center_url = "https://netra.strobid.com/help"
        self.base_url = "https://netra.strobid.com"
        
        # Company information
        self.netra_info = {
            'name': 'Netra',
            'full_name': 'Netra App',
            'description': 'Professional social app connecting service providers and clients',
            'website': 'https://netra.strobid.com',
            'help_center': 'https://netra.strobid.com/help',
            'play_store': 'https://play.google.com/store/apps/details?id=com.netra.app',
            'app_store': 'https://apps.apple.com/app/netra',
            'emblem': 'butterfly-like emblem without fill',
            'security_features': ['No screenshots', 'No screen recording', 'Encrypted messages'],
            'ceo': 'Nowamaani Donath',
            'company': 'Strobid',
            'location': 'Kampala, Uganda',
            'timezone': 'East Africa Time (EAT, UTC+3)',
            'founded': '2023',
            'email': 'support@strobid.com'
        }
        
        # Help center structure based on actual content from netra.strobid.com/help
        self.help_topics = {
            'account': {
                'id': 'account',
                'title': 'Account Management',
                'icon': '👤',
                'articles': [
                    {
                        'title': 'How to create a Netra account',
                        'slug': 'create-account',
                        'keywords': ['create account', 'sign up', 'register', 'join', 'new account', 'get started'],
                        'summary': 'Step-by-step guide to signing up and starting with Netra.'
                    },
                    {
                        'title': 'How to verify your account',
                        'slug': 'verify-account',
                        'keywords': ['verify', 'verification', 'confirm', 'verify email', 'otp', 'code'],
                        'summary': 'Learn how to complete your account verification quickly.'
                    },
                    {
                        'title': 'How to reset your password',
                        'slug': 'reset-password',
                        'keywords': ['reset password', 'forgot password', 'change password', 'new password', 'password help'],
                        'summary': 'Forgot your password? Here’s how to reset it safely.'
                    },
                    {
                        'title': 'How to delete your Netra account',
                        'slug': 'delete-account',
                        'keywords': ['delete account', 'remove account', 'close account', 'cancel account', 'deactivate'],
                        'summary': 'Step-by-step guide to permanently remove your account.'
                    }
                ]
            },
            'payments': {
                'id': 'payments',
                'title': 'Payments & Subscriptions',
                'icon': '💰',
                'articles': [
                    {
                        'title': 'How payments work on Netra',
                        'slug': 'payments-overview',
                        'keywords': ['payment', 'pay', 'how payments work', 'transaction', 'money', 'pay for service', 'client payment'],
                        'summary': 'Understand how to make, track, and manage payments.'
                    },
                    {
                        'title': 'Manage subscriptions & billing',
                        'slug': 'subscriptions',
                        'keywords': ['subscription', 'billing', 'subscribe', 'cancel subscription', 'premium', 'plan', 'upgrade', 'downgrade'],
                        'summary': 'Learn how to subscribe, cancel, or update your plan.'
                    }
                ]
            },
            'settings': {
                'id': 'settings',
                'title': 'App Settings',
                'icon': '⚙️',
                'articles': [
                    {
                        'title': 'Manage notifications',
                        'slug': 'notifications',
                        'keywords': ['notification', 'alert', 'notifications', 'push notification', 'email alert', 'turn off notifications'],
                        'summary': 'Turn on/off alerts and notifications in Netra.'
                    }
                ]
            },
            'support': {
                'id': 'support',
                'title': 'Contact Support',
                'icon': '📞',
                'articles': [
                    {
                        'title': 'Contact Netra support',
                        'slug': 'contact-support',
                        'keywords': ['contact', 'support', 'help', 'customer service', 'reach', 'email support', 'help desk', 'assistance'],
                        'summary': 'Reach out to our support team for personalized help.'
                    }
                ]
            }
        }
        
        # Expanded article content (in production, this would fetch from actual URLs)
        self.article_content = {
            'create-account': {
                'content': """
                **Creating Your Netra Account**
                
                Getting started with Netra is simple! Follow these steps:
                
                1. **Download the App**
                   - Go to Google Play Store
                   - Search for "Netra" (look for the butterfly emblem)
                   - Tap Install
                
                2. **Open the App**
                   - Launch Netra after installation
                   - Tap "Create Account" or "Sign Up"
                
                3. **Enter Your Details**
                   - Provide your email address
                   - Create a strong password
                   - Enter your phone number (optional but recommended)
                   - Fill in your basic profile information
                
                4. **Verify Your Email**
                   - Check your inbox for a verification code
                   - Enter the 6-digit code in the app
                   - If you don't see it, check spam folder
                
                5. **Complete Your Profile**
                   - Add a profile picture
                   - Tell others about yourself
                   - Set your preferences
                
                6. **Start Exploring!**
                   - Browse services
                   - Connect with providers
                   - Book your first service
                
                **Pro Tips:**
                - Use a professional photo for better engagement
                - Complete your profile fully to build trust
                - Enable notifications to never miss updates
                
                Need help? Visit our Help Center at https://netra.strobid.com/help
                """,
                'faqs': [
                    {
                        'question': 'Is it free to create an account?',
                        'answer': 'Yes! Creating a Netra account is completely free.'
                    },
                    {
                        'question': 'Can I use my Google account to sign up?',
                        'answer': 'Yes, Netra supports Google Sign-In for quick registration.'
                    },
                    {
                        'question': 'What if I don\'t receive the verification email?',
                        'answer': 'Check your spam folder, or request a new code after 2 minutes.'
                    }
                ]
            },
            'verify-account': {
                'content': """
                **Account Verification Guide**
                
                Verifying your account helps build trust in the Netra community. Here's how:
                
                **Email Verification (Required)**
                1. After signing up, check your email
                2. Look for the verification email from Netra
                3. Click the verification link or enter the 6-digit code
                4. Your email is now verified!
                
                **Phone Verification (Recommended)**
                1. Go to Settings > Account > Verify Phone
                2. Enter your phone number
                3. Receive SMS with verification code
                4. Enter the code to complete verification
                
                **Provider Verification (For Service Providers)**
                If you're offering services, you may need:
                - Government-issued ID
                - Professional certifications
                - Business documents (if applicable)
                - Profile photo verification
                
                **Why Verify?**
                ✅ Builds trust with potential clients
                ✅ Unlocks all app features
                ✅ Higher visibility in search results
                ✅ Secure transactions
                
                **Verification Status**
                - Basic Account: Email verified
                - Trusted Account: Phone verified
                - Professional Account: Full verification complete
                
                Need assistance? Contact support at support@strobid.com
                """,
                'faqs': [
                    {
                        'question': 'How long does verification take?',
                        'answer': 'Email verification is instant. Provider verification may take 24-48 hours.'
                    },
                    {
                        'question': 'Is my ID safe?',
                        'answer': 'Yes, all documents are encrypted and securely stored.'
                    }
                ]
            },
            'reset-password': {
                'content': """
                **Password Reset Instructions**
                
                Forgot your password? No worries! Here's how to reset it safely:
                
                **Using the App:**
                1. Open Netra app
                2. On login screen, tap "Forgot Password"
                3. Enter your registered email address
                4. Check your email for reset instructions
                5. Click the reset link (valid for 1 hour)
                6. Create a new strong password
                7. Log in with your new password
                
                **Using the Website:**
                1. Visit netra.strobid.com
                2. Click "Login" then "Forgot Password"
                3. Follow the same email verification steps
                
                **Password Requirements:**
                - At least 8 characters
                - Mix of letters and numbers
                - Include one uppercase letter
                - Optional: special characters for extra security
                
                **Tips for Strong Passwords:**
                🔐 Use a phrase you'll remember
                🔐 Don't use personal information
                🔐 Avoid common words
                🔐 Use a password manager
                
                **Still having trouble?**
                Contact support at support@strobid.com for assistance.
                """,
                'faqs': [
                    {
                        'question': 'I didn\'t receive the reset email',
                        'answer': 'Check spam folder and ensure you entered the correct email. You can request another after 2 minutes.'
                    },
                    {
                        'question': 'Can I change my password without email?',
                        'answer': 'If you\'re logged in, go to Settings > Account > Change Password.'
                    }
                ]
            },
            'delete-account': {
                'content': """
                **Deleting Your Netra Account**
                
                We're sorry to see you go! Here's how to permanently delete your account:
                
                **Before You Delete:**
                ⚠️ This action is PERMANENT and cannot be undone
                ⚠️ All your data will be erased
                ⚠️ Active subscriptions must be cancelled first
                ⚠️ Complete any pending transactions
                
                **Steps to Delete:**
                
                1. **Open Netra App**
                   - Log in to your account
                
                2. **Go to Settings**
                   - Tap your profile icon
                   - Select "Settings" (gear icon)
                
                3. **Navigate to Account**
                   - Scroll to "Account Settings"
                   - Tap "Account Management"
                
                4. **Delete Account Option**
                   - Select "Delete Account"
                   - Read the warning carefully
                
                5. **Confirm Your Identity**
                   - Enter your password
                   - Or use biometric verification
                
                6. **Choose Reason (Optional)**
                   - Help us improve by sharing why
                
                7. **Final Confirmation**
                   - Tap "Permanently Delete"
                   - Wait for confirmation email
                
                **What Gets Deleted:**
                ✓ Profile information
                ✓ Photos and posts
                ✓ Conversation history
                ✓ Payment information
                ✓ Ratings and reviews
                
                **What Remains (for legal purposes):**
                📋 Transaction records (anonymized)
                📋 Support tickets (if any)
                
                **Changed Your Mind?**
                If you haven't completed the process, just close the app. Your account remains active.
                
                Need help? Contact support before deleting!
                """,
                'faqs': [
                    {
                        'question': 'Can I recover my account after deletion?',
                        'answer': 'No, account deletion is permanent. You would need to create a new account.'
                    },
                    {
                        'question': 'What happens to my reviews?',
                        'answer': 'Reviews become anonymous but remain to help the community.'
                    }
                ]
            },
            'payments-overview': {
                'content': """
                **How Payments Work on Netra**
                
                Netra makes payments simple and secure for both clients and providers.
                
                **For Clients (Paying for Services):**
                
                1. **Booking a Service**
                   - Find a provider you like
                   - Select service and date
                   - Review price and details
                
                2. **Payment Methods**
                   - 💳 Credit/Debit Cards
                   - 📱 Mobile Money (MTN, Airtel)
                   - 💵 Cash (with provider approval)
                   - 🏦 Bank Transfer
                
                3. **Payment Process**
                   - Pay a deposit to confirm booking
                   - Balance paid after service completion
                   - Funds held securely until service is done
                
                4. **Payment Protection**
                   - Your money is safe until satisfied
                   - Dispute resolution if issues arise
                   - Refund policy protects clients
                
                **For Providers (Receiving Payments):**
                
                1. **Setting Up Payouts**
                   - Add bank account or mobile money
                   - Verify your payment details
                   - Set preferred payout schedule
                
                2. **Getting Paid**
                   - Receive payment after service completion
                   - Funds released within 24 hours
                   - Track earnings in your dashboard
                
                3. **Fees & Commissions**
                   - Small platform fee on completed bookings
                   - Transparent fee structure
                   - No hidden charges
                
                **Security Features:**
                🔒 End-to-end encryption
                🔒 PCI compliant payment processing
                🔒 Fraud detection systems
                🔒 Secure data storage
                
                **Need Help?**
                Visit our Help Center or contact support@strobid.com
                """,
                'faqs': [
                    {
                        'question': 'Are there any fees for clients?',
                        'answer': 'No fees for clients! You pay only the service price.'
                    },
                    {
                        'question': 'How long until providers receive payment?',
                        'answer': 'Payments are typically processed within 24 hours after service completion.'
                    }
                ]
            },
            'subscriptions': {
                'content': """
                **Managing Subscriptions & Billing**
                
                Netra offers premium features through flexible subscription plans.
                
                **Available Plans:**
                
                **Free Plan** (Always Free)
                ✓ Basic profile
                ✓ Search and browse
                ✓ Message providers
                ✓ Standard support
                
                **Provider Pro** (For Service Providers)
                ✓ Featured listings
                ✓ Advanced analytics
                ✓ Priority support
                ✓ Verified badge
                ✓ More visibility
                
                **Business Plan** (For Companies)
                ✓ Multiple team accounts
                ✓ Custom branding
                ✓ API access
                ✓ Dedicated account manager
                ✓ Bulk booking tools
                
                **How to Subscribe:**
                
                1. **In the App:**
                   - Go to Settings
                   - Tap "Subscription"
                   - Choose your plan
                   - Select payment method
                   - Confirm subscription
                
                2. **On Website:**
                   - Visit netra.strobid.com
                   - Log in to your account
                   - Navigate to Billing
                   - Upgrade your plan
                
                **Managing Your Subscription:**
                
                **View Current Plan**
                - Check your plan details anytime
                - See usage and limits
                - Review billing history
                
                **Upgrade Plan**
                - Get more features anytime
                - Prorated pricing available
                - Instant access to new features
                
                **Downgrade Plan**
                - Switch to lower tier
                - Takes effect next billing cycle
                - Keep premium features until then
                
                **Cancel Subscription**
                - No long-term contracts
                - Cancel anytime
                - Access until billing period ends
                
                **Billing Information:**
                - Monthly or annual billing
                - Automatic renewal
                - Email receipts
                - Download invoices
                
                **Need Billing Help?**
                Contact support@strobid.com for subscription assistance.
                """,
                'faqs': [
                    {
                        'question': 'Can I switch between plans?',
                        'answer': 'Yes! You can upgrade, downgrade, or cancel anytime.'
                    },
                    {
                        'question': 'Do you offer refunds?',
                        'answer': 'We have a 7-day money-back guarantee for annual plans.'
                    }
                ]
            },
            'notifications': {
                'content': """
                **Managing Notifications**
                
                Stay in control of your alerts! Customize what notifications you receive.
                
                **Types of Notifications:**
                
                **Push Notifications** (On Your Phone)
                🔔 New messages
                🔔 Booking confirmations
                🔔 Payment updates
                🔔 New reviews
                🔔 Promotional offers
                
                **Email Notifications**
                📧 Weekly summaries
                📧 Account updates
                📧 Security alerts
                📧 Marketing (optional)
                
                **In-App Notifications**
                📱 Activity feed
                📱 System messages
                📱 Community updates
                
                **How to Manage Notifications:**
                
                **In the App:**
                1. Open Netra
                2. Go to Settings
                3. Tap "Notifications"
                4. Toggle each type on/off
                5. Set quiet hours (optional)
                
                **On Android:**
                1. Phone Settings
                2. Apps & Notifications
                3. Select Netra
                4. Manage notification permissions
                
                **On iOS:**
                1. iPhone Settings
                2. Notifications
                3. Find Netra
                4. Customize alert style
                
                **Recommended Settings:**
                
                **For Clients:**
                ✓ New messages (ON)
                ✓ Booking updates (ON)
                ✓ Payment confirmations (ON)
                ✓ Promotions (optional)
                
                **For Providers:**
                ✓ All client communications (ON)
                ✓ New booking requests (ON)
                ✓ Payment received (ON)
                ✓ Reviews (ON)
                
                **Quiet Hours:**
                - Set do-not-disturb times
                - Only priority alerts come through
                - Perfect for sleeping or focus time
                
                **Troubleshooting:**
                Not getting notifications?
                - Check phone settings
                - Ensure app has permission
                - Verify internet connection
                - Update to latest app version
                
                Need more help? Contact support@strobid.com
                """,
                'faqs': [
                    {
                        'question': 'Why am I not getting notifications?',
                        'answer': 'Check your phone settings, app permissions, and ensure notifications are enabled in the app.'
                    },
                    {
                        'question': 'Can I schedule quiet hours?',
                        'answer': 'Yes! You can set specific times when you don\'t want to be disturbed.'
                    }
                ]
            },
            'contact-support': {
                'content': """
                **Contact Netra Support**
                
                Need personalized help? Our support team is here for you!
                
                **Support Channels:**
                
                **📧 Email Support**
                - General inquiries: support@strobid.com
                - Technical issues: tech@strobid.com
                - Billing questions: billing@strobid.com
                - Response time: Within 24 hours
                
                **💬 In-App Chat**
                1. Open Netra app
                2. Go to Settings
                3. Tap "Help & Support"
                4. Start live chat
                - Available: 24/7 for urgent issues
                
                **🌐 Help Center**
                - Visit: https://netra.strobid.com/help
                - Browse articles
                - Search for solutions
                - Video tutorials
                
                **📱 Social Media**
                - Twitter: @NetraApp
                - Facebook: /NetraOfficial
                - Instagram: @netra_app
                
                **🏢 Office Location**
                Strobid Headquarters
                Kampala, Uganda
                East Africa
                
                **Support Hours:**
                Monday - Friday: 8:00 AM - 8:00 PM (EAT)
                Saturday: 9:00 AM - 5:00 PM (EAT)
                Sunday: Closed
                
                **Before Contacting Support:**
                ✅ Check the Help Center first
                ✅ Have your account info ready
                ✅ Describe your issue clearly
                ✅ Include screenshots if helpful
                
                **Common Support Topics:**
                - Account access issues
                - Payment problems
                - Technical glitches
                - Provider verification
                - Report inappropriate behavior
                - Feature requests
                
                **Emergency Support:**
                For urgent issues like security concerns:
                - Email: security@strobid.com
                - Subject line: "URGENT - [Your Issue]"
                
                **We're Here to Help!**
                Our team responds to all inquiries within 24 hours. For faster service, use the in-app chat feature.
                
                Thank you for being part of the Netra community! 🌟
                """,
                'faqs': [
                    {
                        'question': 'How fast do you respond?',
                        'answer': 'Most emails are answered within 24 hours. Live chat is immediate.'
                    },
                    {
                        'question': 'Do you have phone support?',
                        'answer': 'Currently, we offer email and chat support. Phone support coming soon!'
                    }
                ]
            }
        }
        
        # Cache for dynamic content
        self.cache = {
            'last_update': None,
            'content': {}
        }
        
        # Response variations
        self.conversation_starters = [
            "Hey there! ",
            "Oh, about Netra? ",
            "Sure thing! ",
            "I'd be happy to explain! ",
            "Awesome question! ",
            "Glad you asked! ",
            "Let me break this down: ",
            "Here's the scoop: ",
            "Perfect timing! ",
            "Oh, I love talking about Netra! ",
            "Great question! ",
            "Yeah, let me explain: ",
            "So, Netra is... ",
            "Let me tell you about it: ",
            "Happy to help! "
        ]
        
        self.friendly_closers = [
            " Hope that helps!",
            " Let me know if you have other questions!",
            " Pretty cool, right?",
            " Makes sense?",
            " Easy enough?",
            " Got it?",
            " Clear?",
            " Sound good?",
            " Awesome, right?",
            " Neat, huh?",
            " Pretty straightforward!",
            " Simple as that!",
            " That's the gist of it!",
            " Any other questions?",
            " Happy to explain more if needed!"
        ]
        
        self.positive_reactions = [
            "Nice! ",
            "Awesome! ",
            "Great! ",
            "Perfect! ",
            "Excellent! ",
            "Brilliant! ",
            "Fantastic! ",
            "Sweet! ",
            "Cool! ",
            "Wonderful! ",
            "Love it! ",
            "Amazing! "
        ]
        
        self.understanding_phrases = [
            "I see what you mean! ",
            "Got it! ",
            "Ah, good question! ",
            "I understand! ",
            "Makes sense! ",
            "Right on! ",
            "Totally! ",
            "For sure! "
        ]
        
        # Initialize cache
        self._initialize_cache()
    
    def _initialize_cache(self):
        """Initialize the content cache"""
        self.cache['last_update'] = datetime.now()
        self.cache['content'] = self.article_content.copy()
    
    def _get_random_opener(self) -> str:
        """Get random conversation opener"""
        return random.choice(self.conversation_starters)
    
    def _get_random_closer(self) -> str:
        """Get random friendly closer"""
        return random.choice(self.friendly_closers)
    
    def _get_random_reaction(self) -> str:
        """Get random positive reaction"""
        return random.choice(self.positive_reactions)
    
    def _get_understanding(self) -> str:
        """Get random understanding phrase"""
        return random.choice(self.understanding_phrases)
    
    def _detect_intent(self, message: str) -> Tuple[str, Dict[str, Any]]:
        """
        Detect user intent from message
        Returns: (intent_id, intent_data)
        """
        message_lower = message.lower()
        words = set(message_lower.split())
        
        best_match = None
        best_score = 0
        matched_article = None
        matched_topic = None
        
        # Check each topic and article
        for topic_id, topic in self.help_topics.items():
            for article in topic['articles']:
                score = 0
                
                # Check keywords
                for keyword in article['keywords']:
                    if keyword in message_lower:
                        score += 2
                    elif any(word in keyword.split() for word in words):
                        score += 1
                
                # Check if words appear in title
                title_words = set(article['title'].lower().split())
                common_words = words.intersection(title_words)
                score += len(common_words) * 1.5
                
                if score > best_score:
                    best_score = score
                    best_match = topic_id
                    matched_article = article
                    matched_topic = topic
        
        # If no good match, check for general help
        if best_score < 2:
            # Check for help/support intent
            help_keywords = ['help', 'support', 'assist', 'question', 'problem', 'issue']
            if any(kw in message_lower for kw in help_keywords):
                return 'support', {
                    'topic': self.help_topics['support'],
                    'article': self.help_topics['support']['articles'][0],
                    'confidence': 0.7
                }
            
            # Default to general
            return 'general', {
                'confidence': 0.5,
                'topic': None,
                'article': None
            }
        
        # Calculate confidence (normalize to 0-100)
        confidence = min(95, int((best_score / 10) * 100))
        
        return best_match, {
            'topic': matched_topic,
            'article': matched_article,
            'confidence': confidence,
            'score': best_score
        }
    
    def _get_article_content(self, slug: str) -> Optional[Dict]:
        """Get content for a specific article by slug"""
        return self.article_content.get(slug)
    
    def _format_article_response(self, article: Dict, topic: Dict) -> str:
        """Format article content into a friendly response"""
        slug = article['slug']
        content_data = self._get_article_content(slug)
        
        if not content_data:
            return f"{self._get_random_opener()}I'd love to help with '{article['title']}'. For the most accurate information, please visit our Help Center at {self.help_center_url}"
        
        # Build response
        response_parts = [
            f"{self._get_random_reaction()}**{article['title']}**\n",
            content_data['content'].strip(),
            "\n**Frequently Asked Questions:**"
        ]
        
        # Add FAQs
        for faq in content_data.get('faqs', []):
            response_parts.append(f"\n❓ **{faq['question']}**\n💬 {faq['answer']}")
        
        # Add helpful links
        response_parts.append(f"\n📚 **More Help**: Visit {self.help_center_url}/{slug}")
        response_parts.append(f"📧 **Contact Support**: {self.netra_info['email']}")
        
        return "\n".join(response_parts) + self._get_random_closer()
    
    def _get_help_center_response(self, intent: str, intent_data: Dict) -> Optional[str]:
        """Get response based on help center content"""
        
        # If we have a specific article match
        if intent_data.get('article'):
            article = intent_data['article']
            topic = intent_data['topic']
            return self._format_article_response(article, topic)
        
        # If we have a topic but no specific article
        if intent in self.help_topics:
            topic = self.help_topics[intent]
            
            # Build topic overview
            response_parts = [
                f"{self._get_random_opener()}Here's what I can help you with regarding **{topic['title']}**:\n"
            ]
            
            for article in topic['articles']:
                response_parts.append(f"📌 **{article['title']}**")
                response_parts.append(f"   {article['summary']}\n")
            
            response_parts.append(f"Visit our Help Center for detailed guides: {self.help_center_url}")
            
            return "\n".join(response_parts) + self._get_random_closer()
        
        return None
    
    def _generate_suggestions(self, intent: str) -> List[str]:
        """Generate follow-up suggestions based on intent"""
        
        if intent in self.help_topics:
            # Return article titles from this topic
            return [article['title'] for article in self.help_topics[intent]['articles']]
        
        # Default suggestions
        return [
            "How to create a Netra account",
            "How payments work on Netra",
            "Manage notifications",
            "Contact Netra support",
            "Reset my password"
        ]
    
    def _add_visual_elements(self, response: str, intent: str) -> str:
        """Add emojis and formatting to response"""
        
        # Get icon for intent
        icon = self.help_topics.get(intent, {}).get('icon', '🤖')
        
        # Add icon if not present
        if not response.startswith(('👋', '🤖', '🚀', '💼', '🔍', '✨', '🔐', '📅', '💰', '🛡️', '⭐', '🎵', '📞', '🤔', '👤', '⚙️')):
            response = f"{icon} {response}"
        
        return response
    
    def process_query(self, message: str, user_id: str = None, context: Dict = None) -> Dict[str, Any]:
        """
        Main method to process user queries
        
        Args:
            message: User's message
            user_id: Optional user identifier for personalization
            context: Optional conversation context
        
        Returns:
            Dict containing response and metadata
        """
        try:
            # Detect intent
            intent, intent_data = self._detect_intent(message)
            
            # Try to get help center response
            response = self._get_help_center_response(intent, intent_data)
            
            # Fallback responses
            if not response:
                fallbacks = [
                    f"{self._get_random_opener()}I'd be happy to help you with Netra! What specific aspect are you interested in? You can ask about account setup, payments, notifications, or contact support.",
                    
                    f"{self._get_understanding()}I want to make sure you get the right information. Our Help Center at {self.help_center_url} has detailed guides on all Netra features. What would you like to know?",
                    
                    f"{self._get_random_reaction()}Netra is designed to connect service providers with clients seamlessly. For specific questions, check out {self.help_center_url} or let me know what you need help with!"
                ]
                response = random.choice(fallbacks)
            
            # Add visual elements
            response = self._add_visual_elements(response, intent)
            
            # Generate suggestions
            suggestions = self._generate_suggestions(intent)
            
            # Build response object
            response_data = {
                'response': response,
                'suggestions': suggestions[:4],  # Limit to 4 suggestions
                'confidence': intent_data.get('confidence', 85),
                'intent': intent,
                'engine_used': 'netra_engine',
                'help_center_url': self.help_center_url,
                'timestamp': datetime.now().isoformat(),
                'has_more_info': intent in self.help_topics
            }
            
            # Add article reference if available
            if intent_data.get('article'):
                response_data['article'] = intent_data['article']['slug']
                response_data['article_title'] = intent_data['article']['title']
            
            return response_data
            
        except Exception as e:
            # Fallback error response
            error_response = {
                'response': f"{self._get_random_reaction()}I'm having a small technical issue, but don't worry! You can always visit our Help Center at {self.help_center_url} for accurate information about Netra. What would you like to know?",
                'suggestions': [
                    "How to create a Netra account",
                    "How payments work",
                    "Contact support"
                ],
                'confidence': 80,
                'intent': 'fallback',
                'engine_used': 'netra_engine',
                'help_center_url': self.help_center_url,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            return error_response
    
    def get_help_topics(self) -> List[Dict]:
        """Get all available help topics"""
        return [
            {
                'id': topic_id,
                'title': topic['title'],
                'icon': topic['icon'],
                'articles': [a['title'] for a in topic['articles']]
            }
            for topic_id, topic in self.help_topics.items()
        ]
    
    def search_help(self, query: str) -> List[Dict]:
        """Search help center for a query"""
        results = []
        query_lower = query.lower()
        
        for topic_id, topic in self.help_topics.items():
            for article in topic['articles']:
                # Check title
                if query_lower in article['title'].lower():
                    results.append({
                        'topic': topic['title'],
                        'article': article['title'],
                        'slug': article['slug'],
                        'relevance': 0.9
                    })
                # Check keywords
                elif any(query_lower in kw for kw in article['keywords']):
                    results.append({
                        'topic': topic['title'],
                        'article': article['title'],
                        'slug': article['slug'],
                        'relevance': 0.7
                    })
        
        return sorted(results, key=lambda x: x['relevance'], reverse=True)[:5]

# Create the instance with the name that matches the import
netra_engine = HumanizedNetraEngine()

# For testing
if __name__ == "__main__":
    # Test the engine
    test_queries = [
        "How do I create an account?",
        "I forgot my password",
        "How do payments work?",
        "I need to contact support",
        "Tell me about Netra",
        "How do I delete my account?"
    ]
    
    print("🤖 Testing Netra Engine\n" + "="*50)
    for query in test_queries:
        print(f"\n👤 User: {query}")
        result = netra_engine.process_query(query)
        print(f"🤖 Netra: {result['response'][:200]}...")
        print(f"💡 Suggestions: {result['suggestions']}")
        print(f"📊 Confidence: {result['confidence']}%")
        print("-"*50)