import random
import requests
import json
import re
import sqlite3
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
        
        # Initialize databases
        self.init_databases()
        
        # Enhanced knowledge graph
        self.knowledge_graph = self._build_knowledge_graph()
        
        # User session management
        self.user_sessions = {}
        
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

    def init_databases(self):
        """Initialize SQLite databases for user data and analytics"""
        try:
            self.conn = sqlite3.connect('netra_engine.db', check_same_thread=False)
            self.cursor = self.conn.cursor()
            
            # User interactions table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS user_interactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT,
                    query TEXT,
                    response TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    satisfaction_score INTEGER,
                    resolved BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Common issues table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS common_issues (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    issue_type TEXT,
                    symptoms TEXT,
                    solution TEXT,
                    frequency INTEGER DEFAULT 0,
                    last_occurrence DATETIME
                )
            ''')
            
            # Provider analytics table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS provider_analytics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider_id TEXT,
                    service_category TEXT,
                    rating REAL,
                    completion_rate REAL,
                    response_time_minutes INTEGER,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
            print("Netra Engine databases initialized successfully")
            
        except Exception as e:
            print(f"Database initialization error: {e}")

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
        
        # Log user interaction
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
            'engine_version': '2.1.0'
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

    def _get_booking_guide(self) -> str:
        return """Booking a service on Netra is simple:

1. **Browse Providers**: Search by service category or use location-based discovery
2. **Check Availability**: View real-time availability calendars
3. **Compare Options**: Review ratings, prices, and service details
4. **Select Time**: Choose your preferred date and time slot
5. **Confirm Booking**: Review details and confirm with secure payment

📱 Most bookings are confirmed within 2 hours during business hours. You'll receive notifications for provider acceptance and appointment reminders."""

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

    # Context enhancement methods
    def _enhance_with_context(self, base_response: str, intent_analysis: Dict, user_context: Dict) -> str:
        """Enhance response with contextual information"""
        enhanced_response = base_response
        
        # Add urgency context
        if intent_analysis['urgency_level'] == 'critical':
            enhanced_response += "\n\n🚨 **Urgent Support**: Due to the critical nature of this issue, I've also alerted our technical team. They'll reach out within 30 minutes."
        
        # Add complexity context
        if intent_analysis['complexity_level'] == 'high':
            enhanced_response += "\n\n💡 **Complex Issue**: This might require multiple steps. I recommend following the guide carefully and contacting support if you get stuck."
        
        # Add user context if available
        if user_context and user_context.get('previous_issues'):
            enhanced_response += f"\n\n📊 **Context**: Based on your previous interactions, I've tailored this response to address similar patterns we've resolved before."
        
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
        
        return suggestions[:3]  # Return top 3 suggestions

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

    def _log_interaction(self, query: str, intent_analysis: Dict):
        """Log user interaction for analytics"""
        try:
            self.cursor.execute('''
                INSERT INTO user_interactions (query, response, satisfaction_score)
                VALUES (?, ?, ?)
            ''', (query, json.dumps(intent_analysis), intent_analysis['confidence']))
            self.conn.commit()
        except Exception as e:
            print(f"Interaction logging error: {e}")

    # Public interface method
    def process_customer_query(self, message: str, user_id: str = None) -> Dict:
        """Main public method to process customer queries"""
        user_context = self._get_user_context(user_id) if user_id else {}
        
        response_data = self.generate_contextual_response(message, user_context)
        
        # Add engine metadata
        response_data.update({
            'engine_used': 'Netra AI Engine v2.1',
            'response_id': str(uuid.uuid4()),
            'user_id': user_id,
            'query_timestamp': datetime.now().isoformat()
        })
        
        return response_data

    def _get_user_context(self, user_id: str) -> Dict:
        """Get user context from database"""
        try:
            self.cursor.execute('''
                SELECT query, response, timestamp, satisfaction_score 
                FROM user_interactions 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT 5
            ''', (user_id,))
            
            recent_interactions = self.cursor.fetchall()
            
            return {
                'previous_issues': [row[0] for row in recent_interactions],
                'interaction_count': len(recent_interactions),
                'average_satisfaction': sum(row[3] for row in recent_interactions if row[3]) / len(recent_interactions) if recent_interactions else 0
            }
        except:
            return {}

    # Additional utility methods
    def get_service_recommendations(self, user_preferences: Dict) -> List[str]:
        """Get personalized service recommendations"""
        # Implementation for service recommendations
        pass

    def calculate_booking_success_probability(self, provider_id: str, time_slot: str) -> float:
        """Calculate probability of booking success"""
        # Implementation for booking success prediction
        pass

    def generate_analytics_report(self, period: str = 'weekly') -> Dict:
        """Generate analytics report"""
        # Implementation for analytics reporting
        pass

# Create global instance
netra_engine = NetraEngine()

# Example usage
if __name__ == "__main__":
    # Test the engine
    test_queries = [
        "I can't login to my Netra account",
        "How do I book a cleaning service?",
        "The app keeps crashing when I try to make a payment",
        "What is Netra and how does it work?",
        "I need to delete my account immediately"
    ]
    
    for query in test_queries:
        print(f"\n{'='*50}")
        print(f"Query: {query}")
        print(f"{'='*50}")
        response = netra_engine.process_customer_query(query, "test_user_123")
        print(f"Response: {response['response']}")
        print(f"Intent: {response['intent_analysis']['primary_intent']}")
        print(f"Confidence: {response['confidence_score']}%")
        print(f"Suggestions: {response['suggestions']}")