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
        
        # User session management (in-memory only)
        self.user_sessions = {}
        self.interaction_history = []

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

    def _handle_account_queries(self, message: str) -> str:
        """Handle account-related queries"""
        if any(word in message for word in ['delete', 'remove', 'close account']):
            return """To delete your Netra account:

1. Open Netra app → Settings → Account Management
2. Scroll to "Danger Zone" → "Delete Account"
3. Read important information about data loss
4. Enter password to confirm
5. Check email for deletion confirmation

⚠️ This action is permanent and cannot be undone."""
        
        elif any(word in message for word in ['create', 'sign up', 'register']):
            return """Creating a Netra account:

1. Download Netra from App Store or Google Play
2. Tap "Sign Up" and enter your email
3. Verify email through the link sent
4. Complete profile with personal details
5. Connect payment method

✅ Ready in 5 minutes!"""
        
        elif any(word in message for word in ['login', 'sign in', 'password']):
            return """Login troubleshooting:

🔧 Quick Fixes:
- Check internet connection
- Use correct email/password
- Try "Forgot Password"
- Restart the app

🔄 If issues persist:
1. Clear app cache
2. Update Netra app
3. Try different device
4. Contact support@myaidnest.com"""
        
        else:
            return "I can help with account issues: login, profile updates, or account security. What specific problem are you having?"

    def _handle_booking_queries(self, message: str) -> str:
        """Handle booking-related queries"""
        if any(word in message for word in ['book', 'schedule', 'new appointment']):
            return """Booking a service:

1. Browse providers by category/location
2. Check ratings, reviews, availability
3. Select preferred date and time
4. Review service details & pricing
5. Confirm with secure payment

📱 Most bookings confirmed within 2 hours"""
        
        elif any(word in message for word in ['reschedule', 'change booking']):
            return """Rescheduling:

1. Go to "My Bookings" in app
2. Select booking → "Reschedule"
3. Choose new date/time from available slots
4. Confirm changes

🔄 Free rescheduling up to 2 hours before"""
        
        elif any(word in message for word in ['cancel', 'cancel booking']):
            return """Cancellation:

1. Open "My Bookings"
2. Select booking → "Cancel"
3. Select reason → Confirm

🚫 Policy:
- Free: 24+ hours before
- 50% charge: within 24 hours
- Full charge: no-shows"""
        
        else:
            return "I can assist with booking services, managing appointments, or understanding booking policies."

    def _handle_technical_queries(self, message: str) -> str:
        """Handle technical support queries"""
        return """Technical support:

🔧 Quick Troubleshooting:
- Force close and restart Netra app
- Check internet connection
- Clear app cache
- Update to latest version

📋 If issues continue:
1. Note error messages
2. Test on WiFi and mobile data
3. Try different device
4. Contact tech@myaidnest.com with details"""

    def _handle_billing_queries(self, message: str) -> str:
        """Handle billing and payment queries"""
        if any(word in message for word in ['refund', 'money back']):
            return """Refund Policy:

🔄 Eligible:
- Services not as described
- Provider no-show
- Technical issues
- Double charges

❌ Not Eligible:
- Change of mind after service
- Issues not reported within 24h
- Partial service completion

📞 Request: accounts@myaidnest.com"""
        
        elif any(word in message for word in ['payment failed', 'declined']):
            return """Payment Issues:

💳 Check:
- Sufficient funds
- Correct card details
- Active mobile money
- Try different payment method

🔒 Security:
- Payment may be held for verification
- Contact bank if declined
- Check payment limits"""
        
        else:
            return """Billing Information:

💰 Payment Methods:
- M-Pesa, Airtel Money
- Visa/Mastercard
- Bank Transfer
- PayPal

🌍 Currencies: KES, UGX, TZS, USD

🔐 All payments encrypted and secure"""

    def _handle_provider_queries(self, message: str) -> str:
        """Handle provider-related queries"""
        return """Our Providers:

✅ Verification Levels:
- Basic: ID + Phone verification
- ⭐ Premium: Background check + Skills assessment  
- 🏆 Elite: Full background + Insurance + 5+ reviews

All providers undergo rigorous verification for your safety and quality assurance."""

    def _handle_safety_queries(self, message: str) -> str:
        """Handle safety and security queries"""
        return """Your Safety First:

🔒 Security Features:
- Provider background verification
- Real-time booking tracking
- Emergency contact integration
- Encrypted communications
- Secure payment processing
- Anonymous rating system

24/7 support available for any concerns."""

    def _handle_general_queries(self, message: str) -> str:
        """Handle general information queries"""
        if any(word in message for word in ['what is netra', 'tell me about netra']):
            return """Netra by AidNest Africa:

A trusted service marketplace connecting African communities with verified service providers.

🏠 Home Services | 💼 Professional Services
🔧 Technical Services | 💪 Wellness Services

Mission: Empowering African communities through accessible technology
Founded: 2023 | HQ: Kampala, Uganda"""
        
        elif any(word in message for word in ['services', 'what do you offer']):
            service_list = []
            for category in self.service_categories.values():
                service_list.append(f"**{category['name']}**")
                service_list.extend([f"  • {sub}" for sub in category['subcategories'][:3]])
                service_list.append(f"  💰 {category['average_pricing']}")
                service_list.append("")
            
            return "\n".join(service_list)
        
        elif any(word in message for word in ['how it works', 'how does it work']):
            return """How Netra Works:

1. **Browse** - Search services by category/location
2. **Compare** - Check ratings, reviews, prices
3. **Book** - Select provider, time, confirm
4. **Pay** - Secure payment processing
5. **Enjoy** - Quality service delivery
6. **Review** - Share your experience

⭐ All providers verified with background checks"""
        
        else:
            return """Hello! I'm Netra AI Assistant. I can help with:

🔹 Account Management
🔹 Booking Services  
🔹 Technical Support
🔹 Billing & Payments
🔹 Provider Information
🔹 Safety & Security

What do you need help with today?"""

    def process_netra_query(self, message: str, user_id: str = None) -> Dict:
        """Main method to process Netra-related queries - follows same pattern as chemistry_engine"""
        netra_content = {
            'response': '',
            'suggestions': [],
            'confidence': 0,
            'intent': 'unknown',
            'resources': []
        }
        
        try:
            # Analyze the query intent
            intent_analysis = self.analyze_query_intent(message)
            
            # Generate response based on intent
            response_templates = {
                'account_issue': self._handle_account_queries,
                'booking_help': self._handle_booking_queries,
                'technical_support': self._handle_technical_queries,
                'billing_query': self._handle_billing_queries,
                'provider_info': self._handle_provider_queries,
                'safety_concern': self._handle_safety_queries,
                'general_info': self._handle_general_queries
            }
            
            handler = response_templates.get(intent_analysis['primary_intent'], self._handle_general_queries)
            response_text = handler(message.lower())
            
            # Log interaction
            self._log_interaction(message, intent_analysis, user_id)
            
            # Build response
            netra_content.update({
                'response': response_text,
                'confidence': intent_analysis['confidence'],
                'intent': intent_analysis['primary_intent'],
                'suggestions': self._generate_suggestions(intent_analysis),
                'resources': self._get_resources(intent_analysis)
            })
            
        except Exception as e:
            netra_content['response'] = f"I apologize, but I encountered an error: {str(e)}. Please contact support@myaidnest.com for assistance."
            netra_content['suggestions'] = ['Try rephrasing your question', 'Contact our support team directly']
        
        return netra_content

    def _generate_suggestions(self, intent_analysis: Dict) -> List[str]:
        """Generate proactive suggestions"""
        suggestions_map = {
            'account_issue': [
                "Enable two-factor authentication",
                "Review your privacy settings",
                "Keep your profile updated"
            ],
            'booking_help': [
                "Save favorite providers",
                "Set booking reminders",
                "Review cancellation policies"
            ],
            'technical_support': [
                "Keep app updated",
                "Clear cache regularly",
                "Save support contacts"
            ],
            'billing_query': [
                "Check transaction history",
                "Verify payment methods",
                "Review billing FAQs"
            ]
        }
        
        return suggestions_map.get(intent_analysis['primary_intent'], [
            "Explore our service categories",
            "Check provider ratings and reviews",
            "Contact support for specific questions"
        ])

    def _get_resources(self, intent_analysis: Dict) -> List[str]:
        """Get relevant resources"""
        resources_map = {
            'account_issue': ['support@myaidnest.com', 'Account Settings Guide'],
            'booking_help': ['Booking Tutorial', 'Provider Directory'],
            'technical_support': ['tech@myaidnest.com', 'Troubleshooting Guide'],
            'billing_query': ['accounts@myaidnest.com', 'Billing Policy']
        }
        
        return resources_map.get(intent_analysis['primary_intent'], ['support@myaidnest.com', 'Help Center'])

    def _log_interaction(self, query: str, intent_analysis: Dict, user_id: str = None):
        """Log interaction to in-memory storage"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'intent': intent_analysis['primary_intent'],
            'confidence': intent_analysis['confidence'],
            'user_id': user_id
        }
        
        self.interaction_history.append(log_entry)
        
        # Keep only last 100 interactions
        if len(self.interaction_history) > 100:
            self.interaction_history.pop(0)

    def get_service_recommendations(self, user_preferences: Dict) -> List[str]:
        """Get personalized service recommendations"""
        recommendations = []
        for category, prefs in user_preferences.items():
            if category in self.service_categories:
                recommendations.extend(self.service_categories[category]['subcategories'][:2])
        return recommendations[:5]

# Create global instance - FOLLOWS SAME PATTERN AS CHEMISTRY_ENGINE
netra_engine = NetraEngine()