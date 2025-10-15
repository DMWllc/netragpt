import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import random

class NetraEngine:
    def __init__(self):
        # --- Company Info ---
        self.company_info = {
            'name': 'AidNest Africa',
            'tagline': 'Empowering Africa through Technology',
            'mission': 'Providing innovative technology solutions and digital transformation services across Africa',
            'services': [
                'IT Support & Technical Consulting',
                'Custom Software Development',
                'Network Infrastructure Setup',
                'Cloud Services & Migration',
                'Digital Transformation Strategy',
                'Technical Training & Workshops',
                'Hardware Maintenance & Repair',
                'Cybersecurity Solutions',
                'Data Analytics & Business Intelligence',
                'Mobile App Development'
            ],
            'contact': {
                'primary_email': 'support@aidnestafrica.com',
                'technical_email': 'tech@aidnestafrica.com',
                'billing_email': 'accounts@aidnestafrica.com',
                'phone': '+254-700-123-456',
                'emergency_phone': '+254-711-987-654',
                'website': 'www.aidnestafrica.com',
                'address': 'Technology Plaza, Westlands, Nairobi, Kenya'
            },
            'operating_hours': {
                'weekdays': '8:00 AM - 6:00 PM EAT',
                'saturdays': '9:00 AM - 2:00 PM EAT',
                'sundays': 'Emergency Support Only',
                'emergency': '24/7 for Critical Issues'
            },
            'service_areas': [
                'Kenya', 'Uganda', 'Tanzania', 'Rwanda', 'Ethiopia',
                'Ghana', 'Nigeria', 'South Africa', 'Zambia', 'Zimbabwe'
            ]
        }

        # --- Issue Categories ---
        self.issue_categories = {
            'technical_support': {
                'keywords': ['not working', 'broken', 'error', 'crash', 'slow', 'install', 'update', 'virus', 'wifi', 'internet'],
                'response_time': '2-4 hours',
                'priority': 'High'
            },
            'billing_inquiries': {
                'keywords': ['invoice', 'payment', 'bill', 'charge', 'refund', 'price', 'cost', 'subscription'],
                'response_time': '24 hours',
                'priority': 'Medium'
            },
            'service_requests': {
                'keywords': ['new service', 'upgrade', 'install', 'setup', 'configure', 'train', 'consult'],
                'response_time': '1-2 business days',
                'priority': 'Medium'
            },
            'emergency_issues': {
                'keywords': ['emergency', 'urgent', 'critical', 'down', 'outage', 'security breach', 'hack'],
                'response_time': '30 minutes',
                'priority': 'Critical'
            },
            'general_inquiries': {
                'keywords': ['what is', 'how to', 'can you', 'do you', 'information', 'about'],
                'response_time': '4-8 hours',
                'priority': 'Low'
            }
        }

        # --- Solutions Library ---
        self.solutions_library = {
            'internet_issues': {
                'symptoms': ['slow internet', 'no connection', 'wifi not working', 'network down'],
                'troubleshooting': [
                    '🔧 Restart your router and modem (wait 30 seconds)',
                    '📶 Check if other devices can connect',
                    '🔍 Test internet speed at speedtest.net',
                    '🔄 Update network drivers',
                    '⚙️ Reset network settings (ipconfig /release then ipconfig /renew)'
                ],
                'escalation': 'network_team'
            },
            'software_problems': {
                'symptoms': ['software not opening', 'program crash', 'installation failed', 'update error'],
                'troubleshooting': [
                    '🔄 Restart the application',
                    '💻 Restart your computer',
                    '👨‍💼 Run as administrator',
                    '🛡️ Temporarily disable antivirus',
                    '📥 Reinstall the software'
                ],
                'escalation': 'software_team'
            },
            'email_issues': {
                'symptoms': ['cannot send email', 'cannot receive', 'password reset', 'account locked'],
                'troubleshooting': [
                    '🔐 Verify password is correct',
                    '🌐 Check internet connection',
                    '🧹 Clear browser cache and cookies',
                    '📱 Try different email client',
                    '⚙️ Check email server settings'
                ],
                'escalation': 'email_team'
            },
            'hardware_problems': {
                'symptoms': ['computer not starting', 'blue screen', 'hardware failure', 'printer issues'],
                'troubleshooting': [
                    '🔌 Check all power connections',
                    '🔊 Listen for beep codes during startup',
                    '💾 Try booting in safe mode (F8)',
                    '🖥️ Check cable connections',
                    '🔧 Update device drivers'
                ],
                'escalation': 'hardware_team'
            }
        }

        # --- Escalation Teams ---
        self.escalation_teams = {
            'network_team': {
                'contact': 'network@aidnestafrica.com',
                'phone': 'Ext. 201',
                'lead': 'Sarah K., Network Specialist'
            },
            'software_team': {
                'contact': 'software@aidnestafrica.com',
                'phone': 'Ext. 202',
                'lead': 'David M., Senior Developer'
            },
            'hardware_team': {
                'contact': 'hardware@aidnestafrica.com',
                'phone': 'Ext. 203',
                'lead': 'James O., Hardware Engineer'
            },
            'email_team': {
                'contact': 'email@aidnestafrica.com',
                'phone': 'Ext. 204',
                'lead': 'Grace W., Systems Administrator'
            },
            'billing_team': {
                'contact': 'accounts@aidnestafrica.com',
                'phone': 'Ext. 205',
                'lead': 'Michael T., Accounts Manager'
            }
        }

        # --- Greetings & Farewells ---
        self.greetings = [
            "Hello! Welcome to AidNest Africa support. How can I assist you today?",
            "Good day! Thank you for contacting AidNest Africa. What can I help you with?",
            "Welcome to AidNest Africa customer service. How may I be of service?",
            "Hello! I'm Jovira, your AidNest Africa assistant. How can I help you?"
        ]

        self.farewells = [
            "Thank you for choosing AidNest Africa! Have a great day!",
            "We appreciate your business. Don't hesitate to reach out if you need further assistance!",
            "Thank you for contacting AidNest Africa. We're here to help!",
            "Have a wonderful day! Remember, we're just a message away if you need us."
        ]

        # --- Netra App Knowledge (Jovira Knowledge Base) ---
        self.netra_app_knowledge = {
            'account_management': {
                'delete_account': [
                    "Go to Settings in Netra.",
                    "Scroll to the bottom.",
                    "Tap 'Delete Account' and confirm."
                ],
                'edit_profile': [
                    "Go to Settings → Edit Profile.",
                    "Update name, email, phone, and bio.",
                    "Ensure your details are correct for verification."
                ]
            },
            'booking_services': {
                'requirements': [
                    "You must have a verified Autra account.",
                    "Bookings are processed through Netra but synced with Autra."
                ],
                'steps': [
                    "Open the service provider's detailed profile in Netra.",
                    "Tap 'Bookings'.",
                    "Verify your Autra username.",
                    "Select time slot and confirm booking."
                ],
                'reschedule_cancel': [
                    "Go to My Bookings → Upcoming.",
                    "Select booking → choose Reschedule or Cancel.",
                    "Notifications are sent to both client and provider."
                ]
            },
            'support': {
                'general_support': [
                    "Jovira can answer questions about using Netra features.",
                    "For advanced support, users can visit Netra Help Center."
                ],
                'emergency': [
                    "Emergency issues are handled 24/7.",
                    "Call emergency line: +254-711-987-654."
                ]
            },
            'autra_integration': [
                "Autra app handles provider registration, payments, and booking confirmation.",
                "Users must verify their Autra accounts before booking services."
            ]
        }

    # -------------------- Issue Classification --------------------
    def classify_issue(self, message: str) -> Dict:
        message_lower = message.lower()
        for category, info in self.issue_categories.items():
            for keyword in info['keywords']:
                if keyword in message_lower:
                    return {
                        'category': category,
                        'response_time': info['response_time'],
                        'priority': info['priority'],
                        'matched_keyword': keyword
                    }
        return {
            'category': 'general_inquiries',
            'response_time': '4-8 hours',
            'priority': 'Low',
            'matched_keyword': None
        }

    # -------------------- Ticket Number --------------------
    def generate_ticket_number(self) -> str:
        timestamp = datetime.now().strftime("%Y%m%d%H%M")
        random_num = random.randint(100, 999)
        return f"ANA-{timestamp}-{random_num}"

    # -------------------- Troubleshooting --------------------
    def get_troubleshooting_steps(self, issue_description: str) -> List[str]:
        issue_lower = issue_description.lower()
        for issue_type, details in self.solutions_library.items():
            for symptom in details['symptoms']:
                if symptom in issue_lower:
                    return details['troubleshooting']
        return [
            "🔧 Restart your device",
            "🔄 Check for software updates",
            "📞 Ensure you have stable internet connection",
            "💾 Clear cache and temporary files",
            "🛠️ Contact our technical team for specialized assistance"
        ]

    # -------------------- Netra App Guidance --------------------
    def get_netra_app_guidance(self, topic: str) -> List[str]:
        for category, info in self.netra_app_knowledge.items():
            if topic in info:
                return info[topic]
        # fallback for general guidance
        return ["Jovira can help you navigate Netra. Please provide more details."]

    # -------------------- Create Response --------------------
    def create_service_response(self, user_message: str, user_context: Dict = None) -> Dict:
        response = {
            'ticket_number': self.generate_ticket_number(),
            'timestamp': datetime.now().isoformat(),
            'greeting': random.choice(self.greetings),
            'issue_analysis': {},
            'immediate_assistance': [],
            'next_steps': [],
            'escalation_info': {},
            'farewell': random.choice(self.farewells)
        }

        # --- Classify Issue ---
        issue_classification = self.classify_issue(user_message)
        response['issue_analysis'] = issue_classification

        # --- Netra App Guidance Overrides ---
        if 'delete account' in user_message.lower():
            response['immediate_assistance'] = self.get_netra_app_guidance('delete_account')
        elif 'book service' in user_message.lower() or 'booking' in user_message.lower():
            response['immediate_assistance'] = self.get_netra_app_guidance('booking_services')['steps']
        elif 'autra' in user_message.lower():
            response['immediate_assistance'] = self.get_netra_app_guidance('autra_integration')
        else:
            # --- Standard Issue Handling ---
            category = issue_classification['category']
            if category == 'emergency_issues':
                response['immediate_assistance'] = [
                    "🚨 EMERGENCY SUPPORT ACTIVATED",
                    f"Ticket Priority: {issue_classification['priority']}",
                    "Our emergency response team has been notified",
                    "Please call our emergency line: +254-711-987-654"
                ]
                response['next_steps'] = [
                    "Emergency technician will contact you within 30 minutes",
                    "Please ensure you're available at your contact number",
                    "Have your device and error details ready"
                ]
            elif category == 'technical_support':
                troubleshooting_steps = self.get_troubleshooting_steps(user_message)
                response['immediate_assistance'] = [
                    "🔧 Technical Support Assistance",
                    f"Expected Resolution Time: {issue_classification['response_time']}",
                    "Here are immediate troubleshooting steps:"
                ] + troubleshooting_steps
                response['next_steps'] = [
                    "If issues persist, our technical team will contact you",
                    "Please have your device model and software version ready",
                    "Keep this ticket number for reference: " + response['ticket_number']
                ]
            elif category == 'billing_inquiries':
                response['immediate_assistance'] = [
                    "💰 Billing Department Assistance",
                    "Our accounts team will review your inquiry",
                    f"Response Time: {issue_classification['response_time']}",
                    "For immediate billing questions, email: accounts@aidnestafrica.com"
                ]
                response['next_steps'] = [
                    "Billing specialist will contact you within 24 hours",
                    "Please have your invoice number ready",
                    "Check your email for updates on this ticket"
                ]
            elif category == 'service_requests':
                response['immediate_assistance'] = [
                    "🛠️ New Service Request Received",
                    "Our sales team will contact you to discuss requirements",
                    f"Response Time: {issue_classification['response_time']}",
                    "We'll schedule a consultation at your convenience"
                ]
                response['next_steps'] = [
                    "Service consultant will contact you within 1-2 business days",
                    "Please think about your specific requirements",
                    "We'll provide a customized solution and quote"
                ]
            else:
                response['immediate_assistance'] = [
                    "ℹ️ General Information Request",
                    "Here's information about AidNest Africa:",
                    f"Services: {', '.join(self.company_info['services'][:3])}...",
                    f"Contact: {self.company_info['contact']['primary_email']}",
                    f"Hours: {self.company_info['operating_hours']['weekdays']}"
                ]
                response['next_steps'] = [
                    "For specific technical questions, please provide more details",
                    "Visit our website: " + self.company_info['contact']['website'],
                    "We're here to help with any technology needs!"
                ]

        return response

    # -------------------- Sentiment Analysis --------------------
    def _analyze_sentiment(self, text: str) -> str:
        text_lower = text.lower()
        positive_words = ['thanks', 'thank you', 'great', 'good', 'excellent', 'appreciate']
        negative_words = ['angry', 'frustrated', 'terrible', 'awful', 'horrible', 'disappointed']
        urgent_words = ['urgent', 'emergency', 'critical', 'asap', 'immediately']

        if any(word in text_lower for word in urgent_words):
            return 'URGENT'
        elif any(word in text_lower for word in negative_words):
            return 'NEGATIVE'
        elif any(word in text_lower for word in positive_words):
            return 'POSITIVE'
        else:
            return 'NEUTRAL'

    # -------------------- Company Info & Service Status --------------------
    def get_company_info(self) -> Dict:
        return self.company_info

    def get_service_status(self) -> Dict:
        current_time = datetime.now()
        is_business_hours = self._is_business_hours()
        return {
            'current_time': current_time.strftime("%Y-%m-%d %H:%M:%S EAT"),
            'business_hours_status': 'OPEN' if is_business_hours else 'CLOSED',
            'emergency_support': 'AVAILABLE 24/7',
            'recent_updates': [
                "✅ Cloud services operating normally",
                "✅ Network infrastructure stable",
                "🔄 Scheduled maintenance: Sunday 2AM-4AM",
                "📢 New: Cybersecurity awareness training available"
            ],
            'contact_instructions': self._get_contact_instructions(is_business_hours)
        }

    def _is_business_hours(self) -> bool:
        now = datetime.now()
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        hour = now.hour
        if weekday < 5:
            return 8 <= hour < 18
        elif weekday == 5:
            return 9 <= hour < 14
        else:
            return False

    def _get_contact_instructions(self, is_business_hours: bool) -> List[str]:
        if is_business_hours:
            return [
                "📞 Call our main line: " + self.company_info['contact']['phone'],
                "📧 Email: " + self.company_info['contact']['primary_email'],
                "🆘 Emergency: " + self.company_info['contact']['emergency_phone']
            ]
        else:
            return [
                "🌙 After Hours Support",
                "📧 Email will be responded to next business day",
                "🆘 Emergency issues: " + self.company_info['contact']['emergency_phone'],
                "📞 Regular support resumes at 8:00 AM EAT"
            ]

    # -------------------- Customer Query Processor --------------------
    def process_customer_query(self, message: str) -> Dict:
        try:
            sentiment = self._analyze_sentiment(message)
            service_response = self.create_service_response(message)
            service_response['sentiment'] = sentiment
            service_response['urgency'] = 'HIGH' if 'urgent' in message.lower() else 'NORMAL'
            return service_response
        except Exception as e:
            return {
                'error': 'Sorry, I encountered an issue processing your request.',
                'alternative_assistance': [
                    "Please call us directly: " + self.company_info['contact']['phone'],
                    "Or email: " + self.company_info['contact']['primary_email'],
                    "We'll help you resolve this immediately!"
                ]
            }

# -------------------- Global Instance --------------------
netra_engine = NetraEngine()
