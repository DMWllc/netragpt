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
                'phone': '+256-700-123-456',
                'emergency_phone': '+256-711-987-654',
                'whatsapp': '+256-722-555-777'
            }
        }
        
        # Pages to crawl for updated information
        self.crawl_pages = {
            'for_you': 'https://myaidnest.com/for_you.php',
            'category_services': 'https://myaidnest.com/category_services.php',
            'serviceshub': 'https://myaidnest.com/serviceshub.php',
            'home': 'https://myaidnest.com'
        }
        
        # Cache for crawled data (to avoid repeated requests)
        self.crawled_data = {}
        self.last_crawl_time = {}
        
        # Service categories - will be updated from crawled data
        self.service_categories = self._initialize_service_categories()
        
        # User session management
        self.user_sessions = {}
        self.interaction_history = []

    def _initialize_service_categories(self) -> Dict:
        """Initialize service categories with basic structure"""
        return {
            'home_services': {
                'name': 'Home Services',
                'subcategories': [],
                'average_pricing': 'KES 1,500 - 15,000',
                'booking_lead_time': '24-48 hours'
            },
            'professional_services': {
                'name': 'Professional Services',
                'subcategories': [],
                'average_pricing': 'KES 2,000 - 25,000',
                'booking_lead_time': '1-5 business days'
            },
            'technical_services': {
                'name': 'Technical Services',
                'subcategories': [],
                'average_pricing': 'KES 1,000 - 20,000',
                'booking_lead_time': '24-72 hours'
            },
            'wellness_services': {
                'name': 'Wellness Services',
                'subcategories': [],
                'average_pricing': 'KES 1,200 - 8,000',
                'booking_lead_time': '24-48 hours'
            }
        }

    def _crawl_website_data(self) -> Dict:
        """Crawl the website for updated service information"""
        crawled_data = {
            'services': [],
            'categories': [],
            'pricing': {},
            'features': []
        }
        
        try:
            # Crawl each important page
            for page_name, page_url in self.crawl_pages.items():
                if self._should_crawl_page(page_name):
                    response = requests.get(page_url, timeout=10)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')
                        
                        if page_name == 'for_you':
                            crawled_data.update(self._parse_for_you_page(soup))
                        elif page_name == 'category_services':
                            crawled_data.update(self._parse_category_services_page(soup))
                        elif page_name == 'serviceshub':
                            crawled_data.update(self._parse_serviceshub_page(soup))
                        elif page_name == 'home':
                            crawled_data.update(self._parse_home_page(soup))
                        
                        self.last_crawl_time[page_name] = datetime.now()
            
            # Update service categories with crawled data
            self._update_service_categories(crawled_data)
            self.crawled_data = crawled_data
            
        except Exception as e:
            print(f"Warning: Could not crawl website: {e}")
            # Use default data if crawling fails
        
        return crawled_data

    def _should_crawl_page(self, page_name: str) -> bool:
        """Check if we should crawl a page (avoid too frequent requests)"""
        if page_name not in self.last_crawl_time:
            return True
        
        time_since_last_crawl = datetime.now() - self.last_crawl_time[page_name]
        return time_since_last_crawl > timedelta(hours=1)  # Crawl every hour

    def _parse_for_you_page(self, soup: BeautifulSoup) -> Dict:
        """Parse the for_you.php page for personalized service recommendations"""
        data = {
            'personalized_services': [],
            'trending_services': [],
            'recommended_providers': []
        }
        
        try:
            # Look for service cards, recommendations, etc.
            service_cards = soup.find_all('div', class_=re.compile(r'service|card|item'))
            for card in service_cards[:10]:  # Limit to first 10
                service_name = self._extract_text(card, ['h3', 'h4', '.title', '.name'])
                service_price = self._extract_text(card, ['.price', '.cost', '.amount'])
                service_category = self._extract_text(card, ['.category', '.type', '.tag'])
                
                if service_name:
                    data['personalized_services'].append({
                        'name': service_name,
                        'price': service_price,
                        'category': service_category
                    })
        
        except Exception as e:
            print(f"Error parsing for_you page: {e}")
        
        return data

    def _parse_category_services_page(self, soup: BeautifulSoup) -> Dict:
        """Parse the category_services.php page for service categories"""
        data = {
            'categories': [],
            'services_by_category': {}
        }
        
        try:
            # Look for category sections
            category_sections = soup.find_all('div', class_=re.compile(r'category|section|group'))
            
            for section in category_sections:
                category_name = self._extract_text(section, ['h2', 'h3', '.category-title'])
                if category_name:
                    services = []
                    service_items = section.find_all('li') or section.find_all('div', class_=re.compile(r'service|item'))
                    
                    for item in service_items[:8]:  # Limit services per category
                        service_name = self._extract_text(item, ['.service-name', '.title', 'strong'])
                        if service_name:
                            services.append(service_name)
                    
                    data['categories'].append(category_name)
                    data['services_by_category'][category_name] = services
        
        except Exception as e:
            print(f"Error parsing category_services page: {e}")
        
        return data

    def _parse_serviceshub_page(self, soup: BeautifulSoup) -> Dict:
        """Parse the serviceshub.php page for comprehensive service listings"""
        data = {
            'all_services': [],
            'service_details': {},
            'pricing_info': {}
        }
        
        try:
            # Look for service listings
            service_listings = soup.find_all('div', class_=re.compile(r'service|listing|offer'))
            
            for listing in service_listings[:20]:  # Limit to 20 services
                service_name = self._extract_text(listing, ['h3', 'h4', '.service-title', '.name'])
                service_desc = self._extract_text(listing, ['.description', '.desc', 'p'])
                service_price = self._extract_text(listing, ['.price', '.cost', '.amount'])
                
                if service_name:
                    data['all_services'].append(service_name)
                    data['service_details'][service_name] = {
                        'description': service_desc,
                        'price': service_price
                    }
        
        except Exception as e:
            print(f"Error parsing serviceshub page: {e}")
        
        return data

    def _parse_home_page(self, soup: BeautifulSoup) -> Dict:
        """Parse the home page for general information and features"""
        data = {
            'features': [],
            'testimonials': [],
            'stats': {}
        }
        
        try:
            # Extract features
            features = soup.find_all('div', class_=re.compile(r'feature|benefit|advantage'))
            for feature in features[:6]:
                feature_text = self._extract_text(feature, ['h3', 'h4', 'p', '.feature-text'])
                if feature_text:
                    data['features'].append(feature_text)
            
            # Extract testimonials
            testimonials = soup.find_all('div', class_=re.compile(r'testimonial|review|feedback'))
            for testimonial in testimonials[:4]:
                testimonial_text = self._extract_text(testimonial, ['.text', 'p', 'blockquote'])
                if testimonial_text:
                    data['testimonials'].append(testimonial_text)
        
        except Exception as e:
            print(f"Error parsing home page: {e}")
        
        return data

    def _extract_text(self, element, selectors: List[str]) -> str:
        """Extract text from an element using multiple selector strategies"""
        for selector in selectors:
            try:
                if selector.startswith('.'):
                    found = element.find(class_=selector[1:])
                else:
                    found = element.find(selector)
                
                if found and found.get_text(strip=True):
                    return found.get_text(strip=True)
            except:
                continue
        
        # Fallback to element's own text
        return element.get_text(strip=True)

    def _update_service_categories(self, crawled_data: Dict):
        """Update service categories with information from crawled data"""
        # Update from category_services page
        if 'services_by_category' in crawled_data:
            for category_name, services in crawled_data['services_by_category'].items():
                # Map crawled categories to our category structure
                if any(keyword in category_name.lower() for keyword in ['home', 'cleaning', 'repair', 'maintenance']):
                    self.service_categories['home_services']['subcategories'] = services[:7]
                elif any(keyword in category_name.lower() for keyword in ['professional', 'business', 'consulting', 'legal']):
                    self.service_categories['professional_services']['subcategories'] = services[:7]
                elif any(keyword in category_name.lower() for keyword in ['technical', 'tech', 'computer', 'phone']):
                    self.service_categories['technical_services']['subcategories'] = services[:7]
                elif any(keyword in category_name.lower() for keyword in ['wellness', 'health', 'fitness', 'beauty']):
                    self.service_categories['wellness_services']['subcategories'] = services[:7]
        
        # Update from serviceshub page
        if 'all_services' in crawled_data:
            # Use crawled services to enrich our categories
            all_services = crawled_data['all_services']
            # You can implement logic to categorize these services
            pass

    def analyze_query_intent(self, message: str) -> Dict:
        """Enhanced intent analysis with website data integration"""
        # Ensure we have fresh data
        if not self.crawled_data or not any(self.last_crawl_time.values()):
            self._crawl_website_data()
        
        message_lower = message.lower()
        
        intent_indicators = {
            'account_issue': ['account', 'login', 'password', 'profile', 'sign in', 'register', 'verify'],
            'booking_help': ['book', 'schedule', 'appointment', 'reserve', 'availability', 'how to book'],
            'technical_support': ['error', 'bug', 'crash', 'not working', 'technical', 'glitch', 'problem'],
            'billing_query': ['payment', 'billing', 'invoice', 'refund', 'charge', 'price', 'money'],
            'provider_info': ['provider', 'service', 'quality', 'rating', 'review', 'verified', 'background'],
            'safety_concern': ['safe', 'security', 'trust', 'reliable', 'background check', 'emergency'],
            'service_info': ['what services', 'offer', 'available', 'categories', 'types of services'],
            'general_info': ['what is', 'how does', 'tell me about', 'explain', 'information about']
        }
        
        detected_intents = []
        confidence_scores = {}
        
        for intent, indicators in intent_indicators.items():
            matches = sum(1 for indicator in indicators if indicator in message_lower)
            if matches > 0:
                detected_intents.append(intent)
                confidence_scores[intent] = min(100, (matches / len(indicators)) * 100)
        
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
        """Handle account-related queries with accurate information"""
        # Use crawled data if available, otherwise use defaults
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['delete', 'remove', 'close account']):
            return """To delete your Netra account:

1. Open Netra app → Settings → Account Management
2. Scroll to "Account Options" → "Delete Account"
3. Read important information about data deletion
4. Enter your password to confirm
5. You'll receive email confirmation

⚠️ Account deletion is permanent and cannot be undone. All your data, bookings, and history will be permanently removed."""

        elif any(word in message_lower for word in ['create', 'sign up', 'register']):
            return """Creating a Netra account is quick and easy:

1. Download Netra from Google Play Store or Apple App Store
2. Tap "Sign Up" and enter your email address
3. Verify your email through the confirmation link sent to you
4. Complete your profile with personal details
5. Set up your preferred payment method
6. Start browsing and booking services immediately

✅ Your account will be ready in under 3 minutes!"""

        elif any(word in message_lower for word in ['login', 'sign in', 'password']):
            return """Having trouble logging in? Here are solutions:

🔧 Quick Troubleshooting:
- Ensure stable internet connection (WiFi or mobile data)
- Double-check your email and password combination
- Use the "Forgot Password" feature to reset your password
- Force close and restart the Netra app
- Clear the app cache (Settings → Apps → Netra → Clear Cache)

🔄 If problems continue:
1. Update to the latest Netra app version
2. Try logging in from a different device
3. Contact our support team at support@myaidnest.com

We'll help you get back into your account quickly!"""

        else:
            return "I can help you with various account-related matters including login issues, profile management, security settings, and account preferences. What specific account issue are you experiencing?"

    def _handle_service_queries(self, message: str) -> str:
        """Handle service-related queries using crawled data"""
        # Ensure we have fresh data
        self._crawl_website_data()
        
        message_lower = message.lower()
        
        # Check if user is asking about specific services
        if any(word in message_lower for word in ['services', 'what do you offer', 'available services']):
            return self._generate_services_overview()
        
        # Check for specific service categories
        for category_id, category in self.service_categories.items():
            if any(keyword in message_lower for keyword in [category['name'].lower(), category_id]):
                return self._generate_category_details(category_id)
        
        return self._generate_services_overview()

    def _generate_services_overview(self) -> str:
        """Generate comprehensive services overview using crawled data"""
        response = "**Netra Service Categories** 🌟\n\n"
        
        for category_id, category in self.service_categories.items():
            if category['subcategories']:  # Only show categories with actual services
                response += f"**{category['name']}**\n"
                for subcat in category['subcategories'][:4]:  # Show top 4 services
                    response += f"  • {subcat}\n"
                response += f"  💰 {category['average_pricing']}\n"
                response += f"  📅 {category['booking_lead_time']}\n\n"
        
        if not any(category['subcategories'] for category in self.service_categories.values()):
            response += """We offer a wide range of services across four main categories:

🏠 **Home Services** - Cleaning, plumbing, electrical works, painting, and home maintenance
💼 **Professional Services** - Legal, accounting, business consulting, and career services  
🔧 **Technical Services** - Computer repair, phone repair, network setup, and IT support
💪 **Wellness Services** - Fitness training, massage therapy, nutrition, and mental health support

Browse our app to see all available services in your area!"""
        
        response += "\n💡 **Tip**: You can ask me about specific services like 'plumbing services' or 'IT support' for more detailed information!"
        return response

    def _generate_category_details(self, category_id: str) -> str:
        """Generate detailed information for a specific service category"""
        category = self.service_categories.get(category_id, {})
        if not category:
            return "I don't have detailed information about that service category at the moment."
        
        response = f"**{category['name']}**\n\n"
        
        if category['subcategories']:
            response += "**Available Services:**\n"
            for subcat in category['subcategories']:
                response += f"  • {subcat}\n"
            response += f"\n**Average Pricing:** {category['average_pricing']}\n"
            response += f"**Booking Time:** {category['booking_lead_time']}\n"
        else:
            response += f"We offer various {category['name'].lower()} but I don't have the specific list right now. "
            response += "Please check the Netra app for the most up-to-date service listings in your area.\n\n"
        
        response += f"\n**How to Book:**\n1. Open Netra app\n2. Select '{category['name']}' category\n3. Choose your preferred service\n4. Pick a provider with good ratings\n5. Book and pay securely\n\nAll our providers are verified for your safety and satisfaction! ✅"
        
        return response

    def process_netra_query(self, message: str, user_id: str = None) -> Dict:
        """Main method to process Netra-related queries with accurate, crawled data"""
        netra_content = {
            'response': '',
            'suggestions': [],
            'confidence': 0,
            'intent': 'unknown',
            'resources': []
        }
        
        try:
            # Crawl for fresh data if needed
            self._crawl_website_data()
            
            # Analyze the query intent
            intent_analysis = self.analyze_query_intent(message)
            
            # Enhanced response handlers with crawled data integration
            response_templates = {
                'account_issue': self._handle_account_queries,
                'booking_help': self._handle_booking_queries,
                'technical_support': self._handle_technical_queries,
                'billing_query': self._handle_billing_queries,
                'provider_info': self._handle_provider_queries,
                'safety_concern': self._handle_safety_queries,
                'service_info': self._handle_service_queries,
                'general_info': self._handle_general_queries
            }
            
            handler = response_templates.get(intent_analysis['primary_intent'], self._handle_general_queries)
            response_text = handler(message)
            
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
            netra_content['response'] = f"I apologize, but I encountered an error while processing your request. Please contact support@myaidnest.com for assistance."
            netra_content['suggestions'] = ['Try rephrasing your question', 'Contact our support team directly', 'Check the Netra app for the most current information']
        
        return netra_content

    # Keep other methods (_handle_booking_queries, _handle_technical_queries, etc.) similar but enhanced
    # with the ability to use crawled data when appropriate

# Create global instance
netra_engine = NetraEngine()