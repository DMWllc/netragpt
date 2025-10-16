import random
import requests
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
        
        # Natural conversation responses
        self.knowledge_base = {
            'delete_account': {
                'response': "To delete your Netra account, go to Settings → Account Management → Delete Account. Just be aware this permanently removes all your data and cannot be undone.",
                'quick_tip': "Make sure to download any important booking history first!"
            },
            
            'edit_profile': {
                'response': "You can update your profile by tapping your picture in the top right and selecting 'Edit Profile'. You can change your name, contact info, and bio there.",
                'quick_tip': "Keeping your profile updated helps service providers serve you better."
            },
            
            'booking_new': {
                'response': "To book a service, browse available providers in your area, check their ratings and availability, then select your preferred time slot. You'll need a verified Autra account for payments.",
                'quick_tip': "Most bookings are confirmed within 2 hours during business hours."
            },
            
            'booking_manage': {
                'response': "You can reschedule or cancel bookings in the 'My Bookings' section. Reschedule up to 2 hours before your appointment, or cancel if needed.",
                'quick_tip': "Late cancellations might have charges depending on the provider's policy."
            },
            
            'autra_integration': {
                'response': "Autra handles payments and provider verification for Netra. You need a verified Autra account to book services - it makes the process secure and seamless.",
                'quick_tip': "Both apps sync in real-time once connected."
            },
            
            'technical_issues': {
                'response': "If the app isn't working, try restarting it, checking your internet connection, or clearing the app cache. Also make sure you're using the latest version.",
                'quick_tip': "If problems continue, our tech team can help at tech@myaidnest.com"
            },
            
            'billing': {
                'response': "For billing questions, you can view your payment history in the app's billing section. For specific invoice issues or refunds, email accounts@myaidnest.com.",
                'quick_tip': "The billing team usually responds within 24 hours on business days."
            },
            
            'general_info': {
                'response': "AidNest Africa connects users with verified service providers through Netra. We offer home services, professional services, technical support, and wellness services across East Africa.",
                'quick_tip': "We're constantly expanding to new cities and service categories."
            },
            
            'what_is_netra': {
                'response': "Netra is our platform that connects you with trusted service providers for everything from home repairs to professional consultations. It's designed to make finding and booking reliable services easy and secure.",
                'quick_tip': "All providers are verified through our Autra system."
            },
            
            'company_info': {
                'response': "AidNest Africa is a technology company based in East Africa, focused on connecting people with reliable service providers through our Netra platform. We're committed to making quality services accessible to everyone.",
                'quick_tip': "Founded to solve the challenge of finding trusted local service providers."
            },
            
            'services_offered': {
                'response': "Through Netra, you can book: home services (cleaning, repairs), professional services (consulting, tutoring), technical services (IT support), and wellness services (fitness, therapy).",
                'quick_tip': "We're always adding new service categories based on user demand."
            },
            
            'how_to_start': {
                'response': "To get started with Netra, download the app, create your account, verify your Autra account for payments, and start browsing available service providers in your area.",
                'quick_tip': "Take a moment to complete your profile - it helps providers understand your needs better."
            },
            
            'provider_verification': {
                'response': "All service providers on Netra go through a thorough verification process including background checks, skill assessments, and customer reviews to ensure quality and reliability.",
                'quick_tip': "You can see provider ratings and reviews before booking."
            },
            
            'payment_methods': {
                'response': "Payments are processed securely through Autra integration. We support mobile money, bank transfers, and card payments depending on your region.",
                'quick_tip': "All payments are held securely until service completion."
            },
            
            'safety_measures': {
                'response': "Your safety is our priority. We verify all providers, offer secure payments, provide service tracking, and have a 24/7 support team for any concerns during bookings.",
                'quick_tip': "Always communicate through the app for your safety and record-keeping."
            },
            
            'contact_support': {
                'response': "You can reach our support team at support@myaidnest.com for general questions, or tech@myaidnest.com for technical issues. We're here to help!",
                'quick_tip': "Include your account email for faster assistance."
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
            
            # Extract key information
            scraped_data = {
                'services': [],
                'contact_info': {},
                'latest_updates': []
            }
            
            # Try to extract services
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

    def get_natural_response(self, message):
        """Get a natural, direct response without robotic formatting"""
        message_lower = message.lower()
        
        # Direct company-related queries
        if any(word in message_lower for word in ['what is netra', 'tell me about netra']):
            return self.knowledge_base['what_is_netra']['response']
        
        elif any(word in message_lower for word in ['what is aidnest africa', 'about aidnest', 'your company']):
            return self.knowledge_base['company_info']['response']
        
        # Service queries
        elif any(word in message_lower for word in ['what services', 'what do you offer', 'what can i book']):
            return self.knowledge_base['services_offered']['response']
        
        elif any(word in message_lower for word in ['how to start', 'get started', 'begin using']):
            return self.knowledge_base['how_to_start']['response']
        
        # Account management
        elif any(word in message_lower for word in ['delete account', 'remove account']):
            return f"{self.knowledge_base['delete_account']['response']} {self.knowledge_base['delete_account']['quick_tip']}"
        
        elif any(word in message_lower for word in ['edit profile', 'update profile', 'change profile']):
            return f"{self.knowledge_base['edit_profile']['response']} {self.knowledge_base['edit_profile']['quick_tip']}"
        
        # Booking queries
        elif any(word in message_lower for word in ['book', 'schedule', 'make appointment', 'how to book']):
            return f"{self.knowledge_base['booking_new']['response']} {self.knowledge_base['booking_new']['quick_tip']}"
        
        elif any(word in message_lower for word in ['reschedule', 'cancel booking', 'change booking']):
            return f"{self.knowledge_base['booking_manage']['response']} {self.knowledge_base['booking_manage']['quick_tip']}"
        
        # Technical queries
        elif any(word in message_lower for word in ['autra', 'integration', 'connect account']):
            return f"{self.knowledge_base['autra_integration']['response']} {self.knowledge_base['autra_integration']['quick_tip']}"
        
        elif any(word in message_lower for word in ['technical', 'not working', 'bug', 'error', 'app crash']):
            return f"{self.knowledge_base['technical_issues']['response']} {self.knowledge_base['technical_issues']['quick_tip']}"
        
        elif any(word in message_lower for word in ['billing', 'payment', 'invoice', 'refund']):
            return f"{self.knowledge_base['billing']['response']} {self.knowledge_base['billing']['quick_tip']}"
        
        # Provider and safety queries
        elif any(word in message_lower for word in ['provider', 'verified', 'background check']):
            return f"{self.knowledge_base['provider_verification']['response']} {self.knowledge_base['provider_verification']['quick_tip']}"
        
        elif any(word in message_lower for word in ['payment method', 'how to pay', 'payment options']):
            return f"{self.knowledge_base['payment_methods']['response']} {self.knowledge_base['payment_methods']['quick_tip']}"
        
        elif any(word in message_lower for word in ['safety', 'secure', 'trust', 'reliable']):
            return f"{self.knowledge_base['safety_measures']['response']} {self.knowledge_base['safety_measures']['quick_tip']}"
        
        # Contact queries
        elif any(word in message_lower for word in ['contact', 'support', 'help', 'email', 'phone']):
            return f"{self.knowledge_base['contact_support']['response']} {self.knowledge_base['contact_support']['quick_tip']}"
        
        # Fallback for general Netra/AidNest questions
        elif any(word in message_lower for word in ['netra', 'aidnest', 'your app', 'your service']):
            website_data = self.scrape_website_data()
            if website_data and website_data['services']:
                services_text = ", ".join(website_data['services'][:3])
                return f"I can help you with Netra! We currently offer services like {services_text}. What specific help do you need - booking, account issues, or something else?"
            else:
                return "I can help you with Netra account questions, booking services, technical issues, or general information about AidNest Africa. What specific help do you need?"
        
        else:
            return "I specialize in helping with Netra and AidNest Africa services. You can ask me about booking services, account management, technical support, payment questions, or general information about our platform."

    def process_customer_query(self, message):
        """Simple, clean response without ticket numbers or robotic structure"""
        natural_response = self.get_natural_response(message)
        
        return {
            'response': natural_response,
            'engine_used': 'Netra Customer Service'
        }

# Create global instance
netra_engine = NetraEngine()