import random
from datetime import datetime

class NetraEngine:
    def __init__(self):
        self.company_info = {
            'name': 'AidNest Africa',
            'contact': {
                'primary_email': 'support@myaidnest.com',
                'technical_email': 'tech@myaidnest.com',
                'phone': '+254-700-123-456',
                'emergency_phone': '+254-711-987-654'
            }
        }

        self.greetings = [
            "Hello! I'm Jovira, your AidNest Africa assistant. How can I help you today?",
            "Hi there! Jovira at your service. What do you need help with in Netra?"
        ]

        self.farewells = [
            "Thank you for choosing AidNest Africa! Have a great day!",
            "We're here if you need further assistance!"
        ]

        # Static responses database
        self.static_responses = {
            'delete_account': {
                'steps': [
                    "1. Go to Settings in Netra app",
                    "2. Scroll to the bottom and tap 'Account Settings'",
                    "3. Select 'Delete Account' and confirm your choice",
                    "4. You'll receive a confirmation email within 24 hours"
                ],
                'notes': "⚠️ This action is irreversible. All your data will be permanently deleted."
            },
            'edit_profile': {
                'steps': [
                    "1. Open Netra app and go to your Profile",
                    "2. Tap the 'Edit' button (pencil icon)",
                    "3. Update your name, email, phone, or profile picture",
                    "4. Tap 'Save Changes' to update your profile"
                ],
                'notes': "📱 Profile changes are reflected immediately across the platform."
            },
            'booking_new': {
                'steps': [
                    "1. Ensure you have a verified Autra account linked",
                    "2. Browse service providers in your area",
                    "3. Select a provider and view their availability",
                    "4. Choose your preferred time slot",
                    "5. Confirm booking and await provider confirmation"
                ],
                'notes': "⏰ Bookings are confirmed within 2 hours during business hours."
            },
            'booking_reschedule': {
                'steps': [
                    "1. Go to 'My Bookings' in the Netra app",
                    "2. Select the booking you want to reschedule",
                    "3. Tap 'Reschedule' and choose a new time slot",
                    "4. Confirm the new booking time"
                ],
                'notes': "🔄 You can reschedule up to 2 hours before the appointment time."
            },
            'booking_cancel': {
                'steps': [
                    "1. Navigate to 'My Bookings' section",
                    "2. Find the booking you wish to cancel",
                    "3. Tap 'Cancel Booking' and provide a reason",
                    "4. Confirm cancellation"
                ],
                'notes': "❌ Cancellations within 24 hours may incur charges depending on provider policy."
            },
            'autra_integration': {
                'steps': [
                    "1. Download Autra app from your app store",
                    "2. Create an account and complete verification",
                    "3. Link your Autra account in Netra settings",
                    "4. Your accounts are now integrated for seamless bookings"
                ],
                'notes': "🔗 Autra handles provider verification, payments, and booking confirmations."
            },
            'technical_support': {
                'steps': [
                    "1. Restart the Netra app completely",
                    "2. Check your internet connection",
                    "3. Clear app cache in settings",
                    "4. Update to the latest version of Netra"
                ],
                'notes': "🛠️ If issues persist, our technical team will assist you further."
            },
            'billing_inquiries': {
                'steps': [
                    "1. Go to 'Billing & Payments' in settings",
                    "2. View your transaction history",
                    "3. Select the specific invoice for details",
                    "4. Contact accounts@myaidnest.com for disputes"
                ],
                'notes': "💰 Billing team responds within 24 hours on business days."
            },
            'network_issues': {
                'steps': [
                    "1. Check your WiFi or mobile data connection",
                    "2. Restart your router/modem if using WiFi",
                    "3. Try switching between WiFi and mobile data",
                    "4. Check if other apps have internet access"
                ],
                'notes': "📶 Network issues are usually resolved by reconnecting or restarting devices."
            },
            'software_issues': {
                'steps': [
                    "1. Force close and restart the Netra app",
                    "2. Check for app updates in your app store",
                    "3. Clear app cache and data",
                    "4. Reinstall the Netra app if problems continue"
                ],
                'notes': "📱 Always ensure you're using the latest version of Netra."
            },
            'hardware_issues': {
                'steps': [
                    "1. Check if the issue occurs on other devices",
                    "2. Restart your device completely",
                    "3. Update your device's operating system",
                    "4. Test with a different device if available"
                ],
                'notes': "💻 Hardware compatibility issues are rare but can be device-specific."
            }
        }

        # OpenAI knowledge context for complex queries
        self.openai_context = {
            'complex_queries': [
                "multi-step troubleshooting",
                "integration problems between systems",
                "advanced technical configurations",
                "custom workflow requirements",
                "API integration questions",
                "data migration assistance",
                "security and privacy concerns",
                "performance optimization"
            ],
            'response_guidance': "For complex queries, provide detailed step-by-step guidance while maintaining technical accuracy and user-friendliness."
        }

        # Technical team escalation criteria
        self.escalation_criteria = {
            'urgent_issues': [
                "account security breach",
                "payment processing failure",
                "service outage affecting multiple users",
                "data loss or corruption",
                "legal or compliance concerns"
            ],
            'technical_escalation': [
                "bug that prevents core functionality",
                "integration failure with critical systems",
                "security vulnerability discovery",
                "performance degradation affecting many users",
                "recurring issue after basic troubleshooting"
            ]
        }

    def generate_ticket_number(self):
        """Generate a unique support ticket number"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        random_num = random.randint(100, 999)
        return f"ANA-{timestamp}-{random_num}"

    def process_customer_query(self, message):
        """Main method to process customer queries with 3-sided approach"""
        message_lower = message.lower()
        
        # Generate response structure
        response = {
            'ticket_number': self.generate_ticket_number(),
            'timestamp': datetime.now().isoformat(),
            'greeting': random.choice(self.greetings),
            'static_response': None,
            'openai_knowledge': None,
            'escalation_recommendation': None,
            'farewell': random.choice(self.farewells)
        }

        # 1. STATIC RESPONSES - Direct matches
        static_match = self._get_static_response(message_lower)
        if static_match:
            response['static_response'] = static_match

        # 2. OPENAI KNOWLEDGE - Complex queries
        if self._requires_openai_knowledge(message_lower):
            response['openai_knowledge'] = self._get_openai_guidance(message_lower)

        # 3. TECHNICAL TEAM REFERENCE - Escalation needed
        if self._requires_escalation(message_lower):
            response['escalation_recommendation'] = self._get_escalation_info()

        return response

    def _get_static_response(self, message):
        """Get pre-defined static responses for common queries"""
        keyword_mapping = {
            'delete account': 'delete_account',
            'remove account': 'delete_account',
            'close account': 'delete_account',
            'edit profile': 'edit_profile',
            'update profile': 'edit_profile',
            'change profile': 'edit_profile',
            'book service': 'booking_new',
            'make booking': 'booking_new',
            'schedule appointment': 'booking_new',
            'reschedule': 'booking_reschedule',
            'change booking': 'booking_reschedule',
            'cancel booking': 'booking_cancel',
            'autra': 'autra_integration',
            'integration': 'autra_integration',
            'technical': 'technical_support',
            'app not working': 'technical_support',
            'billing': 'billing_inquiries',
            'payment': 'billing_inquiries',
            'invoice': 'billing_inquiries',
            'network': 'network_issues',
            'internet': 'network_issues',
            'connection': 'network_issues',
            'software': 'software_issues',
            'app crash': 'software_issues',
            'hardware': 'hardware_issues',
            'device': 'hardware_issues'
        }

        for keyword, response_key in keyword_mapping.items():
            if keyword in message:
                data = self.static_responses[response_key]
                return {
                    'type': 'static_guide',
                    'title': f"Guide for: {keyword.title()}",
                    'steps': data['steps'],
                    'notes': data['notes']
                }

        return None

    def _requires_openai_knowledge(self, message):
        """Determine if query requires OpenAI's advanced knowledge"""
        complex_indicators = [
            'how to', 'why does', 'what if', 'can i', 'is it possible',
            'troubleshoot', 'configure', 'set up', 'integrate', 'connect',
            'multiple', 'advanced', 'complex', 'custom', 'workflow'
        ]
        
        return any(indicator in message for indicator in complex_indicators)

    def _get_openai_guidance(self, message):
        """Provide context for OpenAI to generate knowledgeable responses"""
        return {
            'type': 'openai_context',
            'guidance': "This query requires detailed technical knowledge. Please provide comprehensive, step-by-step assistance.",
            'context_hints': [
                "Consider the user's technical level",
                "Provide specific, actionable steps",
                "Include troubleshooting tips",
                "Mention common pitfalls to avoid",
                "Suggest best practices"
            ]
        }

    def _requires_escalation(self, message):
        """Determine if query should be escalated to technical team"""
        escalation_indicators = [
            'urgent', 'emergency', 'critical', 'not working at all',
            'broken', 'failed', 'error', 'bug', 'security', 'hack',
            'lost data', 'corrupted', 'outage', 'down', 'crash'
        ]
        
        return any(indicator in message for indicator in escalation_indicators)

    def _get_escalation_info(self):
        """Get technical team contact information"""
        return {
            'type': 'escalation',
            'priority': 'High',
            'contact': {
                'email': self.company_info['contact']['technical_email'],
                'phone': self.company_info['contact']['emergency_phone'],
                'response_time': 'Within 2 hours for urgent issues'
            },
            'instructions': [
                "Our technical team has been notified",
                "Please have your device details ready",
                "Keep this ticket number for reference"
            ]
        }

    def format_response_for_chat(self, engine_response):
        """Format the engine response for chat display"""
        if not engine_response:
            return "I'm here to help! Please describe your issue with Netra or AidNest Africa services."

        response_parts = []

        # Add greeting
        response_parts.append(f"👋 {engine_response['greeting']}")

        # Add static response if available
        if engine_response['static_response']:
            static = engine_response['static_response']
            response_parts.append(f"**{static['title']}**")
            for step in static['steps']:
                response_parts.append(step)
            response_parts.append(f"💡 *Note: {static['notes']}*")

        # Add OpenAI knowledge context
        if engine_response['openai_knowledge']:
            response_parts.append("\n🔍 **Detailed Assistance:**")
            response_parts.append("I'll provide comprehensive guidance for your complex query.")

        # Add escalation info if needed
        if engine_response['escalation_recommendation']:
            escalation = engine_response['escalation_recommendation']
            response_parts.append("\n🚨 **Technical Support Escalation**")
            response_parts.append(f"Priority: {escalation['priority']}")
            response_parts.append(f"Email: {escalation['contact']['email']}")
            response_parts.append(f"Phone: {escalation['contact']['phone']}")
            response_parts.append(f"Response: {escalation['contact']['response_time']}")
            for instruction in escalation['instructions']:
                response_parts.append(f"• {instruction}")

        # Add ticket number and farewell
        response_parts.append(f"\n🎫 **Ticket Number**: {engine_response['ticket_number']}")
        response_parts.append(f"{engine_response['farewell']}")

        return "\n\n".join(response_parts)

# Create global instance
netra_engine = NetraEngine()