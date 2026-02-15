"""
Netra Engine - Dynamic AI Assistant for Netra App Support
Fetches content from: strobid.com, netra.strobid.com, netra.strobid.com/help
"""

import requests
import random
import re
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import html2text # type: ignore

class HumanizedNetraEngine:
    """
    AI Engine that dynamically fetches content from Netra websites
    """
    
    def __init__(self):
        # Base URLs to fetch from
        self.urls = {
            'main': 'https://strobid.com',
            'netra': 'https://netra.strobid.com',
            'help': 'https://netra.strobid.com/help'
        }
        
        # Cache for fetched content
        self.cache = {
            'content': {},
            'last_fetch': None,
            'fetch_count': 0
        }
        
        # Cache duration (1 hour)
        self.cache_duration = timedelta(hours=1)
        
        # Initialize HTML to text converter with proper settings
        self.converter = html2text.HTML2Text()
        self.converter.ignore_links = True  # Don't show raw links
        self.converter.ignore_images = True  # Don't show image markdown
        self.converter.ignore_tables = False
        self.converter.body_width = 0  # Don't wrap text
        self.converter.protect_links = False
        self.converter.mark_code = False
        
        # Natural language templates
        self.response_templates = {
            'account': "Here's what you need to know about Netra accounts:\n\n{content}",
            'payment': "Let me explain how payments work on Netra:\n\n{content}",
            'subscription': "Here's information about Netra subscriptions:\n\n{content}",
            'general': "Here's what I found about that:\n\n{content}",
            'not_found': "I couldn't find specific information about '{query}' in our help center. Would you like to know about:\n\n• Creating an account\n• Making payments\n• Managing subscriptions\n• Contacting support"
        }
        
        # Fetch content on startup
        self._refresh_cache()
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and format text for natural language response
        """
        # Remove markdown links [text](link) -> just keep the text
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        # Remove image markdown ![alt](src)
        text = re.sub(r'!\[[^\]]*\]\([^\)]+\)', '', text)
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Fix weird characters
        replacements = {
            'âs': "'s",
            'â': "'",
            'â': '"',
            'â': '"',
            'â': '-',
            'â': '-',
            'â¢': '™',
            'Â': '',
            '&nbsp;': ' ',
            '&amp;': '&',
            '&lt;': '<',
            '&gt;': '>',
            '&quot;': '"',
            '&#39;': "'",
            '##': '',  # Remove markdown headers
            '__': '',  # Remove markdown bold
            '*': '',   # Remove markdown bullets (will add our own)
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        # Remove multiple newlines
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # Remove multiple spaces
        text = re.sub(r' {2,}', ' ', text)
        
        return text.strip()
    
    def _format_as_natural_language(self, text: str, topic: str = 'general') -> str:
        """
        Convert raw content into natural language
        """
        # Split into lines and clean
        lines = text.split('\n')
        cleaned_lines = []
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('Skip to content') or line.startswith('Skip to main menu'):
                continue
            
            # Remove navigation elements
            if any(word in line.lower() for word in ['home', 'menu', 'navigation', 'search', 'toggle']):
                continue
            
            # Remove very short lines (likely navigation)
            if len(line) < 3:
                continue
            
            cleaned_lines.append(line)
        
        # Join and clean
        clean_text = ' '.join(cleaned_lines)
        clean_text = self._clean_text(clean_text)
        
        # Break into sentences for better readability
        sentences = re.split(r'(?<=[.!?])\s+', clean_text)
        
        # Format into paragraphs
        paragraphs = []
        current_para = []
        
        for sentence in sentences:
            current_para.append(sentence)
            if len(current_para) >= 3:  # 3 sentences per paragraph
                paragraphs.append(' '.join(current_para))
                current_para = []
        
        if current_para:
            paragraphs.append(' '.join(current_para))
        
        # Join paragraphs
        formatted_text = '\n\n'.join(paragraphs)
        
        return formatted_text
    
    def _fetch_url(self, url: str) -> Optional[str]:
        """
        Fetch content from URL
        """
        try:
            print(f"🌐 Fetching: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; NetraBot/1.0; +https://netra.strobid.com)'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse with BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Find main content
            main_content = None
            for selector in ['main', 'article', '.content', '#content', '.main-content', '.help-content']:
                main_content = soup.select_one(selector)
                if main_content:
                    break
            
            if not main_content:
                main_content = soup.body
            
            if main_content:
                # Convert to text
                text = self.converter.handle(str(main_content))
                return text
            
            return None
            
        except Exception as e:
            print(f"❌ Error fetching {url}: {e}")
            return None
    
    def _refresh_cache(self):
        """
        Fetch fresh content from all URLs
        """
        print("\n🔄 Refreshing cache...")
        
        for name, url in self.urls.items():
            print(f"  Fetching {name}...")
            content = self._fetch_url(url)
            
            if content:
                # Clean and format the content
                clean_content = self._format_as_natural_language(content)
                
                self.cache['content'][name] = {
                    'url': url,
                    'raw': content,
                    'clean': clean_content,
                    'fetched_at': datetime.now().isoformat()
                }
                print(f"  ✅ Cached {len(clean_content)} chars from {name}")
            else:
                print(f"  ❌ Failed to fetch {name}")
        
        self.cache['last_fetch'] = datetime.now()
        print("✅ Cache refresh complete\n")
    
    def _search_content(self, query: str) -> List[Dict]:
        """
        Search for relevant content
        """
        query_lower = query.lower()
        results = []
        
        for source_name, source_data in self.cache['content'].items():
            clean_text = source_data.get('clean', '')
            
            # Split into sections
            sections = re.split(r'\n\s*\n', clean_text)
            
            for section in sections:
                if len(section) < 30:
                    continue
                
                section_lower = section.lower()
                score = 0
                
                # Check for keywords
                keywords = {
                    'account': ['account', 'sign up', 'register', 'create', 'password', 'login', 'verify'],
                    'payment': ['payment', 'pay', 'money', 'transaction', 'fee', 'cost', 'price', 'subscription'],
                    'help': ['help', 'support', 'contact', 'assistance', 'guide', 'tutorial'],
                    'service': ['service', 'provider', 'client', 'book', 'booking', 'hire']
                }
                
                for category, words in keywords.items():
                    for word in words:
                        if word in section_lower and word in query_lower:
                            score += 2
                        elif word in section_lower:
                            score += 1
                
                # Bonus for exact phrase match
                if query_lower in section_lower:
                    score += 5
                
                if score > 0:
                    results.append({
                        'source': source_name,
                        'content': section,
                        'score': score,
                        'url': source_data['url']
                    })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def process_query(self, message: str, user_id: str = None) -> Dict[str, Any]:
        """
        Process user query and return natural language response
        """
        try:
            # Check cache
            if (self.cache['last_fetch'] is None or 
                datetime.now() - self.cache['last_fetch'] > self.cache_duration):
                self._refresh_cache()
            
            # Handle greetings
            greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
            if any(g in message.lower() for g in greetings):
                return {
                    'response': "Hello! 👋 I'm your Netra assistant. I can help you with accounts, payments, subscriptions, and more. What would you like to know?",
                    'suggestions': [
                        "How do I create an account?",
                        "How do payments work?",
                        "How do I contact support?"
                    ],
                    'confidence': 100,
                    'engine_used': 'netra_engine',
                    'help_center_url': self.urls['help'],
                    'timestamp': datetime.now().isoformat()
                }
            
            # Search for relevant content
            results = self._search_content(message)
            
            if results and results[0]['score'] > 2:
                best = results[0]
                
                # Format response naturally
                response = best['content']
                
                # Add source attribution naturally
                source_names = {
                    'main': 'our main website',
                    'netra': 'the Netra website',
                    'help': 'our help center'
                }
                source = source_names.get(best['source'], best['source'])
                
                # Build natural response
                natural_response = f"{response}\n\n(I found this information in {source}. You can visit {self.urls['help']} for more details.)"
                
                return {
                    'response': natural_response,
                    'suggestions': [
                        "How do I reset my password?",
                        "How do payments work?",
                        "How do I contact support?",
                        "How do I delete my account?"
                    ],
                    'confidence': min(95, 70 + best['score']),
                    'engine_used': 'netra_engine',
                    'help_center_url': self.urls['help'],
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # No good match found
                return {
                    'response': f"I couldn't find specific information about '{message}' in our help center. Would you like to know about:\n\n• Creating an account\n• Making payments\n• Managing subscriptions\n• Contacting support\n\nYou can also browse {self.urls['help']} for more information.",
                    'suggestions': [
                        "How do I create an account?",
                        "How do payments work?",
                        "How do I contact support?",
                        "How do I reset my password?"
                    ],
                    'confidence': 60,
                    'engine_used': 'netra_engine',
                    'help_center_url': self.urls['help'],
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"Error in process_query: {e}")
            return {
                'response': f"I'm having trouble accessing information right now. Please visit our Help Center at {self.urls['help']} for assistance, or try asking about:\n\n• Creating an account\n• Making payments\n• Contacting support",
                'suggestions': [
                    "How do I create an account?",
                    "How do payments work?",
                    "How do I contact support?"
                ],
                'confidence': 50,
                'engine_used': 'netra_engine',
                'help_center_url': self.urls['help'],
                'timestamp': datetime.now().isoformat()
            }

# Create the instance
netra_engine = HumanizedNetraEngine()