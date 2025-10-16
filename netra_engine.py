import random
import requests # type: ignore
from datetime import datetime
from bs4 import BeautifulSoup
import re

class NetraEngine:
    def __init__(self):
        self.company_info = {
            'name': 'AidNest Africa',
            'website': 'https://myaidnest.com',
            'contact': {
                'primary_email': 'support@myaidnest.com',
                'technical_email': 'tech@myaidnest.com', 
                'phone': '+254-700-123-456',
                'emergency_phone': '+254-711-987-654'
            }
        }
        
        # Enhanced knowledge base with conversational responses
        self.knowledge_base = {
            'delete_account': {
                'response': "I can help you delete your Netra account. This is a straightforward process but please note it's permanent. Would you like me to walk you through the steps?",
                'steps': [
                    "Open the Netra app and go to Settings",
                    "Scroll down to 'Account Management'", 
                    "Tap 'Delete Account' and follow the prompts",
                    "You'll need to confirm your password for security"
                ],
                'notes': "⚠️ Account deletion is permanent and cannot be undone. All your data, bookings, and history will be lost."
            },
            
            'edit_profile': {
                'response': "Updating your profile is easy! Let me guide you through the process to ensure all your information is current.",
                'steps': [
                    "Tap your profile picture in the top right",
                    "Select 'Edit Profile' from the menu",
                    "Update your name, email, phone, or bio",
                    "Don't forget to save your changes!"
                ],
                'notes': "📱 Keeping your profile updated helps service providers serve you better."
            },
            
            'booking_new': {
                'response': "I'd be happy to help you book a service! The booking process is designed to be smooth and efficient.",
                'steps': [
                    "Make sure your Autra account is verified first",
                    "Browse available service providers in your area", 
                    "Check their ratings and availability",
                    "Select your preferred time slot and confirm"
                ],
                'notes': "⏰ Most bookings are confirmed within 2 hours during business hours."
            },
            
            'booking_manage': {
                'response': "Managing your bookings is simple. Are you looking to reschedule or cancel an existing booking?",
                'reschedule_steps': [
                    "Go to 'My Bookings' in the app",
                    "Find the booking you want to change",
                    "Tap 'Reschedule' and pick a new time",
                    "Confirm the new appointment slot"
                ],
                'cancel_steps': [
                    "Navigate to 'My Bookings' → 'Upcoming'",
                    "Select the booking to cancel", 
                    "Choose 'Cancel Booking' and provide reason",
                    "Confirm the cancellation"
                ],
                'notes': "🔄 You can reschedule up to 2 hours before the appointment."
            },
            
            'autra_integration': {
                'response': "The Autra integration makes payments and verifications seamless. Let me explain how it works!",
                'steps': [
                    "Autra handles all payment processing securely",
                    "Provider verification happens through Autra",
                    "Booking confirmations are automated",
                    "Both apps sync in real-time"
                ],
                'notes': "🔗 You need a verified Autra account to book services on Netra."
            },
            
            'technical_issues': {
                'response': "Technical issues can be frustrating! Let's troubleshoot this step by step.",
                'common_solutions': [
                    "Restart the Netra app completely",
                    "Check your internet connection", 
                    "Clear the app cache in settings",
                    "Update to the latest app version"
                ],
                'escalation': "If these don't work, our technical team can investigate further."
            },
            
            'billing': {
                'response': "I can help with billing questions. For detailed invoice issues, our accounts team provides the best support.",
                'self_help': [
                    "View billing history in 'Payments' section",
                    "Download invoices from transaction history", 
                    "Check payment status in real-time"
                ],
                'contact': "For payment disputes or refunds, email accounts@myaidnest.com"
            },
            
            'general_info': {
                'response': "AidNest Africa connects users with verified service providers across multiple categories through our Netra platform.",
                'services': [
                    "Home services (cleaning, repairs)",
                    "Professional services (consulting, tutoring)", 
                    "Technical services (IT support, installations)",
                    "Wellness services (fitness, therapy)"
                ],
                'coverage': "Currently serving major cities in East Africa with plans to expand."
            }
        }
        
        # Web scraping cache
        self.website_data = None
        self.last_scrape_time = None

    def scrape_website_data(self):
        """Scrape current information from myaidnest.com"""
        try:
            # Cache scraping to avoid too frequent requests
            if self.website_data and self.last_scrape_time:
                time_diff = (datetime.now() - self.last_scrape_time).total_seconds()
                if time_diff < 3600:  # 1 hour cache
                    return self.website_data
            
            response = requests.get(self.company_info['website'], timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract key information (adjust selectors based on actual website structure)
            scraped_data = {
                'services': [],
                'contact_info': {},
                'latest_updates': []
            }
            
            # Try to extract services (example selectors - adjust as needed)
            service_elements = soup.find_all(['h2', 'h3'], string=re.compile(r'service|feature|offer', re.I))
            for element in service_elements[:5]:
                scraped_data['services'].append(element.get_text().strip())
            
            # Try to extract contact info
            contact_elements = soup.find_all(text=re.compile(r'@|phone|contact', re.I))
            for element in contact_elements[:3]:
                scraped_data['contact_info'][element.parent.name if element.parent else 'text'] = element.strip()
            
            self.website_data = scraped_data
            self.last_scrape_time = datetime.now()
            
            return scraped_data
            
        except Exception as e:
            print(f"Web scraping error: {e}")
            return None

    def generate_conversational_response(self, query):
        """Generate OpenAI-style conversational responses using our knowledge base"""
        query_lower = query.lower()
        
        # Determine query type and select appropriate response strategy
        if any(word in query_lower for word in ['delete', 'remove', 'close account']):
            return self._handle_account_deletion(query)
        elif any(word in query_lower for word in ['edit', 'update', 'change profile']):
            return self._handle_profile_edits(query)
        elif any(word in query_lower for word in ['book', 'schedule', 'appointment']):
            return self._handle_booking_queries(query)
        elif any(word in query_lower for word in ['reschedule', 'cancel', 'change booking']):
            return self._handle_booking_management(query)
        elif any(word in query_lower for word in ['autra', 'integration', 'connect']):
            return self._handle_autra_integration(query)
        elif any(word in query_lower for word in ['technical', 'not working', 'bug', 'error']):
            return self._handle_technical_issues(query)
        elif any(word in query_lower for word in ['billing', 'payment', 'invoice', 'refund']):
            return self._handle_billing_queries(query)
        elif any(word in query_lower for word in ['what is', 'how does', 'tell me about']):
            return self._handle_general_info(query)
        else:
            return self._handle_unknown_query(query)

    def _handle_account_deletion(self, query):
        """Handle account deletion queries conversationally"""
        kb = self.knowledge_base['delete_account']
        response = f"{kb['response']}\n\n"
        
        if 'step' in query.lower() or 'how' in query.lower():
            response += "Here are the detailed steps:\n"
            for i, step in enumerate(kb['steps'], 1):
                response += f"{i}. {step}\n"
            response += f"\n{kb['notes']}"
        else:
            response += kb['notes']
            
        return response

    def _handle_profile_edits(self, query):
        """Handle profile editing queries"""
        kb = self.knowledge_base['edit_profile']
        response = f"{kb['response']}\n\n"
        
        response += "The main steps are:\n"
        for i, step in enumerate(kb['steps'], 1):
            response += f"{i}. {step}\n"
        response += f"\n{kb['notes']}"
        
        return response

    def _handle_booking_queries(self, query):
        """Handle new booking queries"""
        kb = self.knowledge_base['booking_new']
        response = f"{kb['response']}\n\n"
        
        # Add scraped website info if available
        website_data = self.scrape_website_data()
        if website_data and website_data['services']:
            response += "Based on our current offerings, we provide:\n"
            for service in website_data['services'][:3]:
                response += f"• {service}\n"
            response += "\n"
        
        response += "To book a service:\n"
        for i, step in enumerate(kb['steps'], 1):
            response += f"{i}. {step}\n"
        response += f"\n{kb['notes']}"
        
        return response

    def _handle_booking_management(self, query):
        """Handle booking modifications"""
        kb = self.knowledge_base['booking_manage']
        response = f"{kb['response']}\n\n"
        
        if 'reschedule' in query.lower():
            response += "To reschedule:\n"
            for i, step in enumerate(kb['reschedule_steps'], 1):
                response += f"{i}. {step}\n"
        else:
            response += "To cancel:\n"
            for i, step in enumerate(kb['cancel_steps'], 1):
                response += f"{i}. {step}\n"
                
        response += f"\n{kb['notes']}"
        return response

    def _handle_autra_integration(self, query):
        """Handle Autra integration questions"""
        kb = self.knowledge_base['autra_integration']
        response = f"{kb['response']}\n\n"
        
        response += "Key integration points:\n"
        for i, step in enumerate(kb['steps'], 1):
            response += f"{i}. {step}\n"
        response += f"\n{kb['notes']}"
        
        return response

    def _handle_technical_issues(self, query):
        """Handle technical support queries"""
        kb = self.knowledge_base['technical_issues']
        response = f"{kb['response']}\n\n"
        
        response += "Let's try these solutions first:\n"
        for i, solution in enumerate(kb['common_solutions'], 1):
            response += f"{i}. {solution}\n"
            
        response += f"\n{kb['escalation']}"
        
        # Add technical contact for complex issues
        if any(word in query.lower() for word in ['urgent', 'critical', 'not working at all']):
            response += f"\n\nFor immediate assistance, contact: {self.company_info['contact']['technical_email']}"
            
        return response

    def _handle_billing_queries(self, query):
        """Handle billing and payment questions"""
        kb = self.knowledge_base['billing']
        response = f"{kb['response']}\n\n"
        
        response += "You can:\n"
        for i, option in enumerate(kb['self_help'], 1):
            response += f"{i}. {option}\n"
            
        response += f"\n{kb['contact']}"
        return response

    def _handle_general_info(self, query):
        """Handle general information queries"""
        kb = self.knowledge_base['general_info']
        response = f"{kb['response']}\n\n"
        
        # Add scraped website info
        website_data = self.scrape_website_data()
        if website_data:
            response += "Our current services include:\n"
            for service in website_data['services'][:4] if website_data['services'] else kb['services'][:4]:
                response += f"• {service}\n"
        else:
            response += "Our services include:\n"
            for service in kb['services'][:4]:
                response += f"• {service}\n"
                
        response += f"\n{kb['coverage']}"
        return response

    def _handle_unknown_query(self, query):
        """Handle queries not in our knowledge base"""
        response = "I understand you're looking for information about Netra or AidNest Africa. "
        response += "While I specialize in account management, bookings, and technical support, "
        response += "I might need more context to provide the best assistance.\n\n"
        
        response += "Could you tell me more specifically about:\n"
        response += "• Account or profile issues\n"
        response += "• Booking services or managing appointments\n" 
        response += "• Technical problems with the app\n"
        response += "• Billing or payment questions\n"
        response += "• General information about our services"
        
        return response

    def process_customer_query(self, message):
        """Main method to process customer queries - behaves like OpenAI but uses our data"""
        # Generate conversational response
        conversational_response = self.generate_conversational_response(message)
        
        # Add professional formatting and metadata
        ticket_number = f"ANA-{datetime.now().strftime('%Y%m%d%H%M')}-{random.randint(100, 999)}"
        
        response_data = {
            'ticket_number': ticket_number,
            'timestamp': datetime.now().isoformat(),
            'response': conversational_response,
            'sources_used': ['knowledge_base', 'website_scraping'],
            'suggested_next': self._get_suggested_next_steps(message)
        }
        
        return response_data

    def _get_suggested_next_steps(self, query):
        """Provide intelligent next step suggestions"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['technical', 'not working', 'error']):
            return [
                "Try the troubleshooting steps above",
                "Contact technical support if issues persist",
                "Provide your device model for better assistance"
            ]
        elif any(word in query_lower for word in ['billing', 'payment']):
            return [
                "Check your payment history in the app",
                "Email accounts team with invoice numbers",
                "Allow 24 hours for billing responses"
            ]
        else:
            return [
                "Let me know if you need more detailed steps",
                "Contact support for immediate assistance",
                "Check our website for latest updates"
            ]

# Create global instance
netra_engine = NetraEngine()