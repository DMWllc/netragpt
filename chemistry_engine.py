import random
import requests
import json
import re
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Tuple
import hashlib
import uuid

class NetraEngine:
    def __init__(self):
        self.company_info = {
            'name': 'AidNest Africa',
            'website': 'https://myaidnest.com',
            'foundation_year': '2023',
            'headquarters': 'Kampala, Uganda',
            'mission': 'Empowering African communities through accessible technology services',
            'vision': 'To be Africa\'s leading platform for trusted service connections',
            'contact': {
                'primary_email': 'support@myaidnest.com',
                'technical_email': 'tech@myaidnest.com',
                'billing_email': 'accounts@myaidnest.com',
                'careers_email': 'careers@myaidnest.com',
                'phone': '+254-700-123-456',
                'emergency_phone': '+254-711-987-654',
                'whatsapp': '+254-722-555-777'
            }
        }
        
        # No database initialization
        print("Netra Engine initialized (database-free mode)")
        
        # Enhanced knowledge graph
        self.knowledge_graph = self._build_knowledge_graph()
        
        # User session management (in-memory only)
        self.user_sessions = {}
        self.interaction_history = []  # Simple in-memory storage
        
        # Service categories and details
        self.service_categories = {
            'home_services': {
                'name': 'Home Services',
                'subcategories': [
                    'Cleaning & Sanitation',
                    'Plumbing Repairs',
                    'Electrical Works',
                    'Painting & Decorating',
                    'Furniture Assembly',
                    'Pest Control',
                    'Gardening & Landscaping'
                ],
                'average_pricing': 'KES 1,500 - 15,000',
                'booking_lead_time': '24-48 hours'
            },
            'professional_services': {
                'name': 'Professional Services',
                'subcategories': [
                    'Legal Consultation',
                    'Accounting & Tax',
                    'Business Consulting',
                    'IT Support & Training',
                    'Marketing Services',
                    'Tutoring & Education',
                    'Career Coaching'
                ],
                'average_pricing': 'KES 2,000 - 25,000',
                'booking_lead_time': '1-5 business days'
            },
            'technical_services': {
                'name': 'Technical Services',
                'subcategories': [
                    'Computer Repair',
                    'Phone & Tablet Repair',
                    'Network Setup',
                    'Software Installation',
                    'Data Recovery',
                    'Smart Home Setup',
                    'Electronics Repair'
                ],
                'average_pricing': 'KES 1,000 - 20,000',
                'booking_lead_time': '24-72 hours'
            },
            'wellness_services': {
                'name': 'Wellness Services',
                'subcategories': [
                    'Massage Therapy',
                    'Fitness Training',
                    'Nutrition Counseling',
                    'Mental Health Support',
                    'Yoga Instruction',
                    'Beauty Services',
                    'Wellness Coaching'
                ],
                'average_pricing': 'KES 1,200 - 8,000',
                'booking_lead_time': '24-48 hours'
            }
        }
        
        # Provider verification levels
        self.provider_verification = {
            'basic': {
                'name': 'Basic Verification',
                'requirements': ['ID Verification', 'Phone Verification'],
                'badge': '✅ Verified'
            },
            'premium': {
                'name': 'Premium Verification',
                'requirements': ['ID Verification', 'Background Check', 'Skill Assessment', 'Customer Reviews'],
                'badge': '⭐ Premium Verified'
            },
            'elite': {
                'name': 'Elite Verification',
                'requirements': ['Full Background Check', 'Advanced Skill Testing', 'Insurance Coverage', '5+ Customer Reviews'],
                'badge': '🏆 Elite Verified'
            }
        }
        
        # Payment and billing system
        self.payment_system = {
            'supported_methods': [
                'M-Pesa Mobile Money',
                'Airtel Money',
                'Visa/Mastercard',
                'Bank Transfer',
                'PayPal (International)'
            ],
            'currency_support': ['KES', 'UGX', 'TZS', 'USD'],
            'security_features': [
                'End-to-end encryption',
                'PCI DSS compliant',
                'Two-factor authentication',
                'Fraud detection system'
            ]
        }
        
        # Customer support tiers
        self.support_tiers = {
            'basic': {
                'response_time': '24 hours',
                'channels': ['Email', 'In-app Chat'],
                'availability': 'Business Hours'
            },
            'priority': {
                'response_time': '4 hours',
                'channels': ['Email', 'In-app Chat', 'Phone'],
                'availability': 'Extended Hours'
            },
            'premium': {
                'response_time': '1 hour',
                'channels': ['Email', 'In-app Chat', 'Phone', 'WhatsApp'],
                'availability': '24/7'
            }
        }

    def _build_knowledge_graph(self):
        """Build a comprehensive knowledge graph for intelligent responses"""
        return {
            'account_management': {
                'create_account': {
                    'steps': [
                        "Download Netra app from App Store or Google Play",
                        "Tap 'Sign Up' and enter your email address",
                        "Verify your email through the link sent",
                        "Complete your profile with personal details",
                        "Connect your Autra account for payments"
                    ],
                    'prerequisites': ['Smartphone', 'Email address', 'Internet connection'],
                    'completion_time': '5-10 minutes'
                },
                'delete_account': {
                    'steps': [
                        "Go to Settings → Account Settings",
                        "Scroll to 'Danger Zone' section",
                        "Tap 'Delete Account' and confirm",
                        "Enter your password for security verification",
                        "Check email for deletion confirmation"
                    ],
                    'warnings': ['Permanent action', 'Data cannot be recovered', 'Active bookings will be cancelled'],
                    'completion_time': '24 hours for full processing'
                },
                'profile_optimization': {
                    'tips': [
                        "Add a clear profile picture",
                        "Write a detailed bio about your service needs",
                        "Verify your phone number for security",
                        "Set your service preferences",
                        "Enable notifications for booking alerts"
                    ],
                    'benefits': ['Better provider matches', 'Faster bookings', 'Personalized recommendations']
                }
            },
            
            'booking_system': {
                'new_booking': {
                    'workflow': [
                        "Browse providers by category or search",
                        "Check ratings, reviews, and availability",
                        "Select preferred date and time slot",
                        "Review service details and pricing",
                        "Confirm booking with Autra payment"
                    ],
                    'confirmation_process': [
                        "Instant booking confirmation",
                        "Provider acceptance within 2 hours",
                        "Reminder notifications 24h before",
                        "Service completion confirmation",
                        "Payment release after satisfaction"
                    ]
                },
                'booking_modification': {
                    'reschedule_rules': [
                        "Free rescheduling up to 2 hours before",
                        "Provider availability determines new slots",
                        "No penalty for first reschedule",
                        "Multiple reschedules may affect rating"
                    ],
                    'cancellation_policy': [
                        "Free cancellation up to 24 hours before",
                        "50% charge for cancellations within 24 hours",
                        "Full charge for no-shows",
                        "Emergency cancellations reviewed case-by-case"
                    ]
                }
            },
            
            'technical_support': {
                'troubleshooting_hierarchy': {
                    'level_1': ['App restart', 'Cache clear', 'Update check'],
                    'level_2': ['Reinstall app', 'Device compatibility check', 'Network testing'],
                    'level_3': ['Account verification', 'Server status check', 'Log analysis']
                },
                'common_errors': {
                    'login_issues': ['Wrong password', 'Account locked', 'Server timeout'],
                    'payment_errors': ['Insufficient funds', 'Payment gateway down', 'Card declined'],
                    'booking_errors': ['Slot unavailable', 'Provider busy', 'System conflict']
                }
            },
            
            'security_protocols': {
                'data_protection': [
                    "End-to-end encryption for all communications",
                    "Regular security audits and penetration testing",
                    "GDPR and local data protection compliance",
                    "Secure payment processing with PCI DSS"
                ],
                'user_safety': [
                    "Provider background verification",
                    "Real-time booking tracking",
                    "Emergency contact integration",
                    "Anonymous rating system"
                ]
            }
        }

    def analyze_query_intent(self, message: str) -> Dict:
        """Advanced intent analysis for user queries"""
        message_lower = message.lower()
        
        intent_indicators = {
            'account_issue': ['account', 'login', 'password', 'profile', 'sign in', 'register'],
            'booking_help': ['book', 'schedule', 'appointment', 'reserve', 'availability'],
            'technical_support': ['error', 'bug', 'crash', 'not working', 'technical', 'glitch'],
            'billing_query': ['payment', 'billing', 'invoice', 'refund', 'charge', 'price'],
            'provider_info': ['provider', 'service', 'quality', 'rating', 'review', 'verified'],
            'safety_concern': ['safe', 'security', 'trust', 'reliable', 'background check'],
            'general_info': ['what is', 'how does', 'tell me about', 'explain']
        }
        
        detected_intents = []
        confidence_scores = {}
        
        for intent, indicators in intent_indicators.items():
            matches = sum(1 for indicator in indicators if indicator in message_lower)
            if matches > 0:
                detected_intents.append(intent)
                confidence_scores[intent] = min(100, (matches / len(indicators)) * 100)
        
        # Determine primary intent
        primary_intent = max(confidence_scores.items(), key=lambda x: x[1]) if confidence_scores else ('general_info', 0)
        
        return {
            'detected_intents': detected_intents,
            'primary_intent': primary_intent[0],
            'confidence': primary_intent[1],
            'urgency_level': self._assess_urgency(message_lower),
            'complexity_level': self._assess_complexity(message_lower)
        }

    def _assess_urgency(self, message: str) -> str:
        """Assess urgency level of query"""
        urgent_indicators = ['emergency', 'urgent', 'immediately', 'asap', 'critical', 'not working', 'broken']
        high_indicators = ['problem', 'issue', 'trouble', 'help needed', 'stuck']
        
        if any(indicator in message for indicator in urgent_indicators):
            return 'critical'
        elif any(indicator in message for indicator in high_indicators):
            return 'high'
        else:
            return 'normal'

    def _assess_complexity(self, message: str) -> str:
        """Assess complexity level of query"""
        complex_indicators = ['multiple', 'several', 'complex', 'advanced', 'configuration', 'integration']
        medium_indicators = ['how to', 'step by step', 'guide', 'tutorial']
        
        if any(indicator in message for indicator in complex_indicators):
            return 'high'
        elif any(indicator in message for indicator in medium_indicators):
            return 'medium'
        else:
            return 'low'

    def generate_contextual_response(self, message: str, user_context: Dict = None) -> Dict:
        """Generate intelligent, contextual responses based on comprehensive analysis"""
        # Analyze query intent
        intent_analysis = self.analyze_query_intent(message)
        
        # Log user interaction (in-memory only)
        self._log_interaction(message, intent_analysis)
        
        # Generate base response
        base_response = self._generate_base_response(message, intent_analysis)
        
        # Enhance with contextual information
        enhanced_response = self._enhance_with_context(base_response, intent_analysis, user_context)
        
        # Add proactive suggestions
        proactive_suggestions = self._generate_proactive_suggestions(intent_analysis, user_context)
        
        # Compile comprehensive response
        comprehensive_response = {
            'response': enhanced_response,
            'intent_analysis': intent_analysis,
            'suggestions': proactive_suggestions,
            'next_steps': self._suggest_next_steps(intent_analysis),
            'escalation_path': self._determine_escalation_path(intent_analysis),
            'confidence_score': intent_analysis['confidence'],
            'response_timestamp': datetime.now().isoformat(),
            'engine_version': '2.1.0-database-free'
        }
        
        return comprehensive_response

    def _generate_base_response(self, message: str, intent_analysis: Dict) -> str:
        """Generate base response based on intent analysis"""
        primary_intent = intent_analysis['primary_intent']
        message_lower = message.lower()
        
        response_templates = {
            'account_issue': self._handle_account_queries(message_lower),
            'booking_help': self._handle_booking_queries(message_lower),
            'technical_support': self._handle_technical_queries(message_lower),
            'billing_query': self._handle_billing_queries(message_lower),
            'provider_info': self._handle_provider_queries(message_lower),
            'safety_concern': self._handle_safety_queries(message_lower),
            'general_info': self._handle_general_queries(message_lower)
        }
        
        return response_templates.get(primary_intent, self._handle_unknown_query(message_lower))

    def _handle_account_queries(self, message: str) -> str:
        """Handle account-related queries"""
        if any(word in message for word in ['delete', 'remove', 'close account']):
            return self._get_account_deletion_guide()
        elif any(word in message for word in ['create', 'sign up', 'register']):
            return self._get_account_creation_guide()
        elif any(word in message for word in ['login', 'sign in', 'password']):
            return self._get_login_troubleshooting()
        elif any(word in message for word in ['profile', 'update', 'edit']):
            return self._get_profile_management_guide()
        else:
            return "I can help with various account issues. Are you having trouble with login, profile updates, or account security?"

    def _handle_booking_queries(self, message: str) -> str:
        """Handle booking-related queries"""
        if any(word in message for word in ['book', 'schedule', 'new appointment']):
            return self._get_booking_guide()
        elif any(word in message for word in ['reschedule', 'change booking']):
            return self._get_rescheduling_guide()
        elif any(word in message for word in ['cancel', 'cancel booking']):
            return self._get_cancellation_guide()
        else:
            return "I can assist with booking services, managing existing appointments, or understanding our booking policies."

    def _handle_technical_queries(self, message: str) -> str:
        """Handle technical support queries"""
        urgency = self._assess_urgency(message)
        
        if urgency == 'critical':
            return "This appears to be a critical issue. Let me provide immediate troubleshooting steps while also connecting you with our technical team."
        else:
            return self._get_technical_troubleshooting_guide(message)

    def _handle_billing_queries(self, message: str) -> str:
        """Handle billing and payment queries"""
        if any(word in message for word in ['refund', 'money back']):
            return self._get_refund_policy()
        elif any(word in message for word in ['invoice', 'receipt']):
            return self._get_invoice_help()
        elif any(word in message for word in ['payment failed', 'declined']):
            return self._get_payment_troubleshooting()
        else:
            return self._get_general_billing_info()

    def _handle_provider_queries(self, message: str) -> str:
        """Handle provider-related queries"""
        return "Our providers go through rigorous verification including background checks, skill assessments, and customer reviews. Would you like to know about specific provider categories or verification levels?"

    def _handle_safety_queries(self, message: str) -> str:
        """Handle safety and security queries"""
        return "Your safety is our top priority. We implement multiple security layers including provider verification, real-time tracking, secure payments, and 24/7 support. All communications are encrypted and we never share your personal data."

    def _handle_general_queries(self, message: str) -> str:
        """Handle general information queries"""
        if any(word in message for word in ['what is netra', 'tell me about netra']):
            return self._get_netra_overview()
        elif any(word in message for word in ['services', 'what do you offer']):
            return self._get_services_overview()
        elif any(word in message for word in ['how it works', 'how does it work']):
            return self._get_how_it_works()
        else:
            return self._get_general_introduction()

    def _handle_unknown_query(self, message: str) -> str:
        """Handle unrecognized queries"""
        return "I specialize in Netra platform assistance. I can help with account management, booking services, technical support, billing questions, or general information about our platform. What specific area do you need help with?"

    # Detailed response generators
    def _get_account_deletion_guide(self) -> str:
        return """To delete your Netra account:

1. Open Netra app and go to Settings → Account Management
2. Scroll to "Danger Zone" and tap "Delete Account"
3. Read the important information about data loss
4. Enter your password to confirm
5. Check your email for deletion confirmation

⚠️ Important: This action is permanent and cannot be undone. All your data, booking history, and preferences will be permanently deleted. Active bookings will be automatically cancelled."""

    def _get_account_creation_guide(self) -> str:
        return """Creating a Netra account is easy:

1. **Download the App**: Get Netra from App Store (iOS) or Google Play (Android)
2. **Sign Up**: Tap "Create Account" and enter your email
3. **Verify Email**: Check your inbox for verification link
4. **Complete Profile**: Add your name, phone number, and preferences
5. **Set Location**: Enable location services for better provider matches

✅ Your account will be ready in under 5 minutes!"""

    def _get_login_troubleshooting(self) -> str:
        return """Having trouble logging in? Try these steps:

🔧 **Quick Fixes:**
- Check your internet connection
- Ensure you're using the correct email/password
- Try "Forgot Password" to reset your credentials
- Restart the Netra app

🔄 **If still not working:**
1. Clear app cache in device settings
2. Update Netra app to latest version
3. Try logging in on a different device
4. Contact support@myaidnest.com for assistance

We'll help you regain access quickly!"""

    def _get_profile_management_guide(self) -> str:
        return """To update your Netra profile:

1. Go to Profile tab in the app
2. Tap "Edit Profile" 
3. Update your information:
   - Personal details
   - Service preferences
   - Notification settings
   - Payment methods
4. Save changes

💡 **Pro Tip**: Complete profiles get better provider matches and personalized recommendations!"""

    def _get_booking_guide(self) -> str:
        return """Booking a service on Netra is simple:

1. **Browse Providers**: Search by service category or use location-based discovery
2. **Check Availability**: View real-time availability calendars
3. **Compare Options**: Review ratings, prices, and service details
4. **Select Time**: Choose your preferred date and time slot
5. **Confirm Booking**: Review details and confirm with secure payment

📱 Most bookings are confirmed within 2 hours during business hours. You'll receive notifications for provider acceptance and appointment reminders."""

    def _get_rescheduling_guide(self) -> str:
        return """To reschedule a booking:

1. Go to "My Bookings" in the app
2. Select the booking you want to change
3. Tap "Reschedule" 
4. Choose new date and time from available slots
5. Confirm changes

🔄 **Rescheduling Policy:**
- Free rescheduling up to 2 hours before appointment
- Subject to provider availability
- No penalty for first reschedule per month"""

    def _get_cancellation_guide(self) -> str:
        return """Cancellation process:

1. Open "My Bookings" in Netra app
2. Select the booking to cancel
3. Tap "Cancel Booking"
4. Select cancellation reason
5. Confirm cancellation

🚫 **Cancellation Policy:**
- Free cancellation up to 24 hours before
- 50% charge for cancellations within 24 hours
- Full charge for no-shows
- Emergency cancellations reviewed case-by-case"""

    def _get_technical_troubleshooting_guide(self, message: str) -> str:
        return """Let's troubleshoot this step by step:

🔧 **Quick Fixes to Try First:**
- Force close and restart the Netra app
- Check your internet connection stability
- Clear app cache in your device settings
- Ensure you're using the latest app version

📋 **If issues persist:**
1. Note any specific error messages
2. Check if the issue occurs on WiFi and mobile data
3. Try on a different device if possible
4. Contact tech@myaidnest.com with details

We're here to help resolve any technical issues quickly!"""

    def _get_refund_policy(self) -> str:
        return """Netra Refund Policy:

🔄 **Eligible for Refund:**
- Services not provided as described
- Provider no-show without notice
- Technical issues preventing service delivery
- Double charges or billing errors

❌ **Not Eligible:**
- Change of mind after service completion
- Issues not reported within 24 hours
- Services partially completed as agreed

📞 To request a refund: Contact accounts@myaidnest.com with booking details and reason for refund request."""

    def _get_invoice_help(self) -> str:
        return """Accessing your invoices:

1. Go to "Billing & Payments" in app
2. Select "Transaction History"
3. Tap any completed booking to view invoice
4. Download or email invoice as PDF

📧 **Need duplicate invoices?** Email accounts@myaidnest.com with your account email and booking dates."""

    def _get_payment_troubleshooting(self) -> str:
        return """Payment issue solutions:

💳 **Common Fixes:**
- Check payment method has sufficient funds
- Verify card details are correct
- Ensure your mobile money account is active
- Try a different payment method

🔒 **Security Checks:**
- Payment might be held for security verification
- Contact your bank if card is declined
- Check for payment limits on your account

🆘 Still having issues? Contact accounts@myaidnest.com with error message details."""

    def _get_general_billing_info(self) -> str:
        return """Netra Billing Information:

💰 **Payment Methods:**
- M-Pesa Mobile Money
- Airtel Money  
- Visa/Mastercard
- Bank Transfer
- PayPal (International)

🌍 **Supported Currencies:** KES, UGX, TZS, USD

🔐 **Security:** All payments are encrypted and PCI DSS compliant. We never store your full payment details."""

    def _get_netra_overview(self) -> str:
        return """Welcome to Netra by AidNest Africa! 

**What is Netra?**
Netra is a trusted service marketplace connecting African communities with verified service providers. We make it easy to find, book, and manage home services, professional services, technical support, and wellness services.

**Our Mission:** Empowering African communities through accessible technology services

**Founded:** 2023 | **Headquarters:** Kampala, Uganda

We're committed to quality, safety, and convenience for all our users!"""

    def _get_services_overview(self) -> str:
        return """Netra Service Categories:

🏠 **Home Services**
- Cleaning, plumbing, electrical, painting, pest control, gardening

💼 **Professional Services** 
- Legal, accounting, business consulting, IT support, marketing

🔧 **Technical Services**
- Computer/phone repair, network setup, data recovery, electronics

💪 **Wellness Services**
- Massage, fitness training, nutrition, mental health, beauty

All providers are verified and rated by our community. Book with confidence!"""

    def _get_how_it_works(self) -> str:
        return """How Netra Works:

1. **Browse & Compare** - Search services by category or location
2. **Book Instantly** - Select provider, time, and confirm booking
3. **Secure Payment** - Pay safely through integrated payment system
4. **Service Delivery** - Provider arrives and completes service
5. **Rate & Review** - Share your experience to help others

⭐ All providers are verified with background checks and customer reviews!"""

    def _get_general_introduction(self) -> str:
        return """Hello! I'm Netra AI Assistant, here to help you with:

🔹 **Account Management** - Login, profile, security
🔹 **Booking Services** - Finding, booking, managing appointments  
🔹 **Technical Support** - App issues, errors, troubleshooting
🔹 **Billing & Payments** - Invoices, refunds, payment issues
🔹 **Provider Information** - Verification, ratings, services
🔹 **Safety & Security** - Trust, data protection, emergency

How can I assist you today?"""

    def _log_interaction(self, query: str, intent_analysis: Dict):
        """Log user interaction to in-memory storage"""
        self.interaction_history.append({
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'intent': intent_analysis['primary_intent'],
            'confidence': intent_analysis['confidence'],
            'response_preview': str(intent_analysis)[:100] + '...'  # Truncate for memory
        })
        
        # Keep only last 100 interactions to prevent memory bloat
        if len(self.interaction_history) > 100:
            self.interaction_history.pop(0)

    def _enhance_with_context(self, base_response: str, intent_analysis: Dict, user_context: Dict) -> str:
        """Enhance response with contextual information"""
        enhanced_response = base_response
        
        if intent_analysis['urgency_level'] == 'critical':
            enhanced_response += "\n\n🚨 **Urgent Support**: Due to the critical nature of this issue, I've also alerted our technical team. They'll reach out within 30 minutes."
        
        if intent_analysis['complexity_level'] == 'high':
            enhanced_response += "\n\n💡 **Complex Issue**: This might require multiple steps. I recommend following the guide carefully and contacting support if you get stuck."
        
        return enhanced_response

    def _generate_proactive_suggestions(self, intent_analysis: Dict, user_context: Dict) -> List[str]:
        """Generate proactive suggestions based on intent and context"""
        suggestions = []
        
        if intent_analysis['primary_intent'] == 'account_issue':
            suggestions.extend([
                "Enable two-factor authentication for better security",
                "Review your privacy settings in account preferences",
                "Download your data history before making major changes"
            ])
        
        elif intent_analysis['primary_intent'] == 'booking_help':
            suggestions.extend([
                "Set up favorite providers for quicker bookings",
                "Enable booking reminders in notification settings",
                "Review provider cancellation policies before booking"
            ])
        
        elif intent_analysis['primary_intent'] == 'technical_support':
            suggestions.extend([
                "Keep the app updated to latest version",
                "Clear cache regularly for optimal performance",
                "Save our support email for quick access"
            ])
        
        return suggestions[:3]

    def _suggest_next_steps(self, intent_analysis: Dict) -> List[str]:
        """Suggest logical next steps"""
        next_steps = []
        
        if intent_analysis['confidence'] < 70:
            next_steps.append("Provide more specific details for better assistance")
        
        if intent_analysis['urgency_level'] in ['high', 'critical']:
            next_steps.append("Have your account email ready for support team contact")
        
        next_steps.extend([
            "Keep this conversation for reference",
            "Check your email for any automated follow-ups"
        ])
        
        return next_steps

    def _determine_escalation_path(self, intent_analysis: Dict) -> Dict:
        """Determine if and how to escalate the issue"""
        if intent_analysis['urgency_level'] == 'critical':
            return {
                'needed': True,
                'team': 'technical_support',
                'eta': '30 minutes',
                'contact': 'tech@myaidnest.com'
            }
        elif intent_analysis['confidence'] < 50:
            return {
                'needed': True,
                'team': 'customer_success',
                'eta': '2 hours',
                'contact': 'support@myaidnest.com'
            }
        else:
            return {'needed': False}

    # Public interface method
    def process_customer_query(self, message: str, user_id: str = None) -> Dict:
        """Main public method to process customer queries"""
        user_context = self._get_user_context(user_id) if user_id else {}
        
        response_data = self.generate_contextual_response(message, user_context)
        
        # Add engine metadata
        response_data.update({
            'engine_used': 'Netra AI Engine v2.1 (Database-Free)',
            'response_id': str(uuid.uuid4()),
            'user_id': user_id,
            'query_timestamp': datetime.now().isoformat()
        })
        
        return response_data

    def _get_user_context(self, user_id: str) -> Dict:
        """Get user context from in-memory storage"""
        user_interactions = [i for i in self.interaction_history if i.get('user_id') == user_id]
        
        return {
            'previous_issues': [i['query'] for i in user_interactions[-5:]],  # Last 5
            'interaction_count': len(user_interactions),
            'recent_confidence': sum(i['confidence'] for i in user_interactions[-3:]) / 3 if user_interactions else 0
        }

    def get_recent_interactions(self, limit: int = 10) -> List[Dict]:
        """Get recent interactions for debugging"""
        return self.interaction_history[-limit:]

# Create global instance
netra_engine = NetraEngine()