"""
Netra Engine - Intelligent Site Analyzer
Understands page sections and extracts specific features
"""

import requests
import re
import time
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import Counter
import json

class HumanizedNetraEngine:
    """
    Netra AI Assistant that analyzes page sections for specific features
    """
    
    def __init__(self):
        self.base_url = "https://netra.strobid.com"
        self.all_pages = {}
        self.crawled_urls: Set[str] = set()
        self.features = {
            'bookings': [],
            'ratings': [],
            'payments': [],
            'accounts': [],
            'services': []
        }
        self.last_crawl = None
        
        # Start crawling
        self._crawl_site()
    
    def _fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch a page and return BeautifulSoup object"""
        try:
            print(f"🌐 Fetching: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"  ❌ Failed: {e}")
            return None
    
    def _extract_sections(self, soup: BeautifulSoup, url: str) -> List[Dict]:
        """Extract meaningful sections from a page"""
        sections = []
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Find main content
        main = soup.find('main') or soup.find('article') or soup.body
        
        if main:
            # Split into sections based on headings
            current_section = {'heading': 'Main', 'content': [], 'type': 'general'}
            for element in main.children:
                if element.name in ['h1', 'h2', 'h3']:
                    # Save previous section
                    if current_section['content']:
                        sections.append(current_section)
                    
                    # Start new section
                    heading = element.get_text().strip()
                    section_type = self._classify_section(heading)
                    current_section = {
                        'heading': heading,
                        'content': [],
                        'type': section_type,
                        'page_url': url
                    }
                elif element.name in ['p', 'ul', 'ol', 'div']:
                    text = element.get_text().strip()
                    if text and len(text) > 30:
                        current_section['content'].append(text)
            
            # Add last section
            if current_section['content']:
                sections.append(current_section)
        
        return sections
    
    def _classify_section(self, heading: str) -> str:
        """Classify what type of section this is"""
        heading_lower = heading.lower()
        
        if any(word in heading_lower for word in ['book', 'booking', 'schedule', 'appointment', 'reserve']):
            return 'bookings'
        elif any(word in heading_lower for word in ['rate', 'rating', 'review', 'feedback', 'testimonial']):
            return 'ratings'
        elif any(word in heading_lower for word in ['pay', 'payment', 'billing', 'subscription', 'invoice']):
            return 'payments'
        elif any(word in heading_lower for word in ['account', 'profile', 'login', 'signup', 'register']):
            return 'accounts'
        elif any(word in heading_lower for word in ['service', 'provider', 'professional', 'category']):
            return 'services'
        else:
            return 'general'
    
    def _extract_features(self, soup: BeautifulSoup, url: str):
        """Extract specific features from the page"""
        page_features = {
            'bookings': [],
            'ratings': [],
            'payments': [],
            'accounts': [],
            'services': []
        }
        
        # Look for booking-related elements
        booking_keywords = ['book', 'booking', 'schedule', 'appointment', 'reserve', 'hire']
        for element in soup.find_all(['button', 'a', 'div'], class_=re.compile('|'.join(booking_keywords), re.I)):
            text = element.get_text().strip()
            if text and len(text) < 100:
                page_features['bookings'].append({
                    'text': text,
                    'type': 'button',
                    'context': self._get_surrounding_text(element)
                })
        
        # Look for rating-related elements
        rating_keywords = ['rate', 'rating', 'review', 'feedback', 'star']
        for element in soup.find_all(['div', 'span', 'form'], class_=re.compile('|'.join(rating_keywords), re.I)):
            text = element.get_text().strip()
            if text and len(text) < 200:
                page_features['ratings'].append({
                    'text': text,
                    'type': 'section',
                    'context': self._get_surrounding_text(element)
                })
        
        # Look for payment-related elements
        payment_keywords = ['pay', 'payment', 'price', 'cost', 'fee', 'checkout']
        for element in soup.find_all(['div', 'form', 'section'], class_=re.compile('|'.join(payment_keywords), re.I)):
            text = element.get_text().strip()
            if text and len(text) < 300:
                page_features['payments'].append({
                    'text': text,
                    'type': 'section',
                    'context': self._get_surrounding_text(element)
                })
        
        return page_features
    
    def _get_surrounding_text(self, element, words: int = 20):
        """Get text surrounding an element for context"""
        parent = element.find_parent(['div', 'section', 'article'])
        if parent:
            text = parent.get_text().strip()
            # Truncate to reasonable length
            words_list = text.split()
            if len(words_list) > words:
                return ' '.join(words_list[:words]) + '...'
            return text
        return ''
    
    def _crawl_site(self, max_pages: int = 30):
        """Crawl the site and analyze all pages"""
        print("\n🔍 ANALYZING NETRA.STROBID.COM")
        print("=" * 60)
        
        to_crawl = [self.base_url]
        crawled = set()
        
        pages_crawled = 0
        
        while to_crawl and pages_crawled < max_pages:
            url = to_crawl.pop(0)
            if url in crawled:
                continue
            
            print(f"\n📄 Analyzing: {url}")
            soup = self._fetch_page(url)
            
            if soup:
                # Extract sections
                sections = self._extract_sections(soup, url)
                
                # Extract features
                features = self._extract_features(soup, url)
                
                # Store page data
                self.all_pages[url] = {
                    'url': url,
                    'title': soup.find('title').get_text() if soup.find('title') else url,
                    'sections': sections,
                    'features': features
                }
                
                # Add features to global feature list
                for feature_type, feature_list in features.items():
                    for feature in feature_list:
                        feature['page_url'] = url
                        self.features[feature_type].append(feature)
                
                # Find new links
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith('/'):
                        full_url = urljoin(self.base_url, href)
                        if full_url not in crawled and full_url not in to_crawl:
                            to_crawl.append(full_url)
                
                pages_crawled += 1
            
            crawled.add(url)
            time.sleep(0.5)
        
        self.crawled_urls = crawled
        self.last_crawl = datetime.now()
        
        self._print_analysis()
    
    def _print_analysis(self):
        """Print analysis of found features"""
        print("\n📊 FEATURES FOUND")
        print("=" * 60)
        for feature_type, features in self.features.items():
            if features:
                print(f"\n{feature_type.upper()}: {len(features)} items")
                for f in features[:3]:
                    print(f"  • {f['text'][:100]}...")
    
    def _find_relevant_content(self, query: str) -> Dict:
        """Find the most relevant content for a query"""
        query_lower = query.lower()
        
        # Determine what the user is asking about
        intent = 'general'
        if any(word in query_lower for word in ['book', 'booking', 'schedule', 'appointment', 'reserve', 'hire']):
            intent = 'bookings'
        elif any(word in query_lower for word in ['rate', 'rating', 'review', 'feedback', 'star']):
            intent = 'ratings'
        elif any(word in query_lower for word in ['pay', 'payment', 'money', 'cost', 'price']):
            intent = 'payments'
        elif any(word in query_lower for word in ['account', 'profile', 'login', 'signup']):
            intent = 'accounts'
        elif any(word in query_lower for word in ['service', 'provider', 'professional']):
            intent = 'services'
        
        # Look for relevant features first
        if intent in self.features and self.features[intent]:
            best_match = self.features[intent][0]
            
            # Try to find the page this feature came from
            page_url = best_match.get('page_url')
            page = self.all_pages.get(page_url, {})
            
            return {
                'type': 'feature',
                'intent': intent,
                'content': best_match['text'],
                'context': best_match.get('context', ''),
                'page': page,
                'confidence': 90
            }
        
        # Look through page sections
        best_section = None
        best_score = 0
        
        for url, page in self.all_pages.items():
            for section in page.get('sections', []):
                if section['type'] == intent or intent == 'general':
                    section_text = ' '.join(section['content']).lower()
                    score = 0
                    
                    for word in query_lower.split():
                        if word in section_text:
                            score += 1
                    
                    if score > best_score:
                        best_score = score
                        best_section = section
                        best_section['page_url'] = url
                        best_section['page_title'] = page['title']
        
        if best_section and best_score > 0:
            return {
                'type': 'section',
                'intent': intent,
                'content': best_section['content'],
                'heading': best_section['heading'],
                'page': best_section,
                'confidence': min(90, 60 + best_score * 5)
            }
        
        return None
    
    def _format_response(self, content: Dict, query: str) -> str:
        """Format the found content into a natural response"""
        response_parts = []
        
        if content['type'] == 'feature':
            # Format feature-based response
            if content['intent'] == 'bookings':
                response_parts.append("**Netra Bookings**")
                response_parts.append("")
                response_parts.append("Here's what I found about bookings on Netra:")
                response_parts.append("")
                response_parts.append(content['content'])
                if content.get('context'):
                    response_parts.append("")
                    response_parts.append(content['context'])
            
            elif content['intent'] == 'ratings':
                response_parts.append("**Netra Ratings & Reviews**")
                response_parts.append("")
                response_parts.append("Information about ratings on Netra:")
                response_parts.append("")
                response_parts.append(content['content'])
            
            else:
                response_parts.append(f"**Netra {content['intent'].title()}**")
                response_parts.append("")
                response_parts.append(content['content'])
        
        elif content['type'] == 'section':
            # Format section-based response
            if content.get('heading'):
                response_parts.append(f"**{content['heading']}**")
                response_parts.append("")
            
            if isinstance(content['content'], list):
                response_parts.extend(content['content'])
            else:
                response_parts.append(content['content'])
        
        return '\n'.join(response_parts)
    
    def process_query(self, message: str, user_id: str = None) -> Dict[str, Any]:
        """Process user query"""
        try:
            print(f"\n🤔 Processing: {message}")
            
            # Handle greetings
            greetings = ['hi', 'hello', 'hey', 'good morning']
            if any(g in message.lower() for g in greetings):
                return {
                    'response': "Hello! I'm your Netra assistant. I can help you with bookings, ratings, payments, accounts, and more. What would you like to know?",
                    'suggestions': [
                        "How do bookings work?",
                        "How do ratings work?",
                        "How do I create an account?",
                        "Tell me about Netra"
                    ],
                    'confidence': 100,
                    'engine_used': 'netra_engine',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Find relevant content
            content = self._find_relevant_content(message)
            
            if content:
                response = self._format_response(content, message)
                
                # Generate suggestions based on intent
                suggestions_map = {
                    'bookings': [
                        "How do I cancel a booking?",
                        "Can I reschedule?",
                        "How do payments work?",
                        "How do I rate a provider?"
                    ],
                    'ratings': [
                        "How do I leave a review?",
                        "Can I edit my rating?",
                        "How are ratings calculated?",
                        "What if I had a bad experience?"
                    ],
                    'payments': [
                        "What payment methods?",
                        "How do refunds work?",
                        "Are there fees?",
                        "How do subscriptions work?"
                    ],
                    'accounts': [
                        "How do I verify my account?",
                        "How do I reset my password?",
                        "How do I delete my account?",
                        "How do I update my profile?"
                    ],
                    'services': [
                        "How do I find a provider?",
                        "What services are available?",
                        "How do I become a provider?",
                        "How do I contact support?"
                    ]
                }
                
                suggestions = suggestions_map.get(content['intent'], [
                    "What is Netra?",
                    "How do I create an account?",
                    "How do bookings work?",
                    "How do I contact support?"
                ])
                
                return {
                    'response': response,
                    'suggestions': suggestions[:4],
                    'confidence': content['confidence'],
                    'engine_used': 'netra_engine',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # No relevant content found
                return {
                    'response': "I couldn't find specific information about that. Here are some topics I can help with:\n\n• How bookings work\n• How ratings work\n• Creating an account\n• Making payments\n• Available services\n• Contacting support",
                    'suggestions': [
                        "How do bookings work?",
                        "How do ratings work?",
                        "How do I create an account?",
                        "How do I contact support?"
                    ],
                    'confidence': 70,
                    'engine_used': 'netra_engine',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return {
                'response': "I'm here to help with Netra! You can ask me about bookings, ratings, payments, accounts, and more. What would you like to know?",
                'suggestions': [
                    "How do bookings work?",
                    "How do ratings work?",
                    "How do I create an account?",
                    "How do I contact support?"
                ],
                'confidence': 60,
                'engine_used': 'netra_engine',
                'timestamp': datetime.now().isoformat()
            }

# Create the instance
netra_engine = HumanizedNetraEngine()