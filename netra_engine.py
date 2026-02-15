"""
Netra Engine - Dynamic AI Assistant for Netra App Support
Fetches content from: strobid.com, netra.strobid.com, netra.strobid.com/help
"""

import requests
import random
import re
import time
import hashlib
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
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
            'pages': {},  # URL -> {content, timestamp, etag}
            'sitemap': None,
            'last_full_refresh': None
        }
        
        # Cache duration (6 hours)
        self.cache_duration = timedelta(hours=6)
        
        # Initialize HTML to text converter
        self.converter = html2text.HTML2Text()
        self.converter.ignore_links = False
        self.converter.ignore_images = False
        self.converter.ignore_tables = False
        self.converter.body_width = 0
        
        # Conversation starters (keep these for personality)
        self.conversation_starters = [
            "Hey there! ",
            "I just checked our latest info: ",
            "According to our website: ",
            "Let me fetch that for you: ",
            "Great question! Here's what I found: ",
            "Based on our help center: ",
            "I looked that up for you: "
        ]
        
        self.friendly_closers = [
            "\n\nHope that helps! 😊",
            "\n\nLet me know if you need anything else!",
            "\n\nYou can always check our website for more details.",
            "\n\nIs there anything else you'd like to know?",
            "\n\nHappy to help with more questions!"
        ]
    
    def _fetch_url(self, url: str) -> Optional[str]:
        """
        Fetch content from URL with caching
        """
        try:
            # Check cache
            now = datetime.now()
            if url in self.cache['pages']:
                cached = self.cache['pages'][url]
                if now - cached['timestamp'] < self.cache_duration:
                    print(f"✅ Using cached content for {url}")
                    return cached['content']
            
            # Fetch fresh content
            print(f"🌐 Fetching fresh content from {url}")
            headers = {
                'User-Agent': 'NetraBot/1.0 (+https://netra.strobid.com)'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            # Parse and clean content
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.decompose()
            
            # Convert to readable text
            text = self.converter.handle(str(soup))
            
            # Clean up text
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            clean_text = '\n'.join(lines)
            
            # Cache it
            self.cache['pages'][url] = {
                'content': clean_text,
                'timestamp': now,
                'etag': response.headers.get('etag', '')
            }
            
            return clean_text
            
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None
    
    def _extract_sections(self, content: str) -> Dict[str, str]:
        """
        Extract logical sections from content
        """
        sections = {}
        
        # Look for headings and their content
        lines = content.split('\n')
        current_section = 'general'
        section_content = []
        
        for line in lines:
            # Check if line looks like a heading
            if line.strip() and not line[0].isspace() and len(line.strip()) < 100:
                if section_content:
                    sections[current_section] = '\n'.join(section_content)
                current_section = line.strip().lower().replace(' ', '_').replace('#', '')
                section_content = []
            else:
                section_content.append(line)
        
        # Add last section
        if section_content:
            sections[current_section] = '\n'.join(section_content)
        
        return sections
    
    def _search_content(self, query: str, content: str) -> List[Dict]:
        """
        Search for relevant content based on query
        """
        query_words = set(query.lower().split())
        results = []
        
        # Split into paragraphs
        paragraphs = content.split('\n\n')
        
        for para in paragraphs:
            if len(para.strip()) < 20:  # Skip short paragraphs
                continue
            
            para_lower = para.lower()
            
            # Calculate relevance score
            score = 0
            matched_words = []
            
            for word in query_words:
                if len(word) < 3:  # Skip very short words
                    continue
                if word in para_lower:
                    score += 1
                    matched_words.append(word)
            
            # Bonus for exact phrase matches
            if query.lower() in para_lower:
                score += 5
            
            if score > 0:
                results.append({
                    'content': para.strip(),
                    'score': score,
                    'matched': matched_words
                })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results[:3]  # Return top 3
    
    def _get_best_response(self, query: str) -> Optional[str]:
        """
        Get the best response by searching across all sources
        """
        all_results = []
        
        # Fetch from all sources
        for source_name, url in self.urls.items():
            content = self._fetch_url(url)
            if content:
                results = self._search_content(query, content)
                for r in results:
                    r['source'] = source_name
                    r['source_url'] = url
                    all_results.append(r)
        
        if not all_results:
            return None
        
        # Sort by score
        all_results.sort(key=lambda x: x['score'], reverse=True)
        best = all_results[0]
        
        # Format response
        response = best['content']
        
        # Add source attribution
        if best['score'] > 2:  # Only add source if reasonably confident
            source_names = {
                'main': 'strobid.com',
                'netra': 'netra.strobid.com',
                'help': 'help center'
            }
            source = source_names.get(best['source'], best['source'])
            response += f"\n\n📌 *Source: {source}*"
        
        return response
    
    def _generate_suggestions(self, query: str) -> List[str]:
        """
        Generate follow-up suggestions based on common help topics
        """
        # Common help topics from the help center
        suggestions = [
            "How to create a Netra account",
            "How to verify my account",
            "Reset my password",
            "Delete my account",
            "How payments work",
            "Manage subscriptions",
            "Notification settings",
            "Contact support"
        ]
        
        # Randomly select 4 suggestions
        return random.sample(suggestions, 4)
    
    def process_query(self, message: str, user_id: str = None) -> Dict[str, Any]:
        """
        Process user query by fetching and searching website content
        """
        try:
            # First, check if it's a general greeting
            greetings = ['hi', 'hello', 'hey', 'greetings']
            if any(g in message.lower() for g in greetings):
                return {
                    'response': "Hello! 👋 I'm your Netra assistant. I can help you with anything about Netra - accounts, payments, settings, and more. What would you like to know?",
                    'suggestions': self._generate_suggestions(''),
                    'confidence': 95,
                    'engine_used': 'netra_engine_dynamic',
                    'help_center_url': self.urls['help'],
                    'timestamp': datetime.now().isoformat()
                }
            
            # Get best response from website content
            response = self._get_best_response(message)
            
            if response:
                # Add random opener
                opener = random.choice(self.conversation_starters)
                response = opener + response
                
                # Add random closer (30% chance)
                if random.random() > 0.7:
                    response += random.choice(self.friendly_closers)
                
                confidence = 90
                suggestions = self._generate_suggestions(message)
            else:
                # Fallback response
                response = f"I couldn't find specific information about that in our help center. You might want to check {self.urls['help']} directly, or try asking about:\n\n• Creating an account\n• Payments and subscriptions\n• Account settings\n• Contacting support"
                confidence = 60
                suggestions = self._generate_suggestions('general')
            
            return {
                'response': response,
                'suggestions': suggestions,
                'confidence': confidence,
                'engine_used': 'netra_engine_dynamic',
                'help_center_url': self.urls['help'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Netra Engine error: {e}")
            return {
                'response': f"I'm having trouble fetching the latest information right now. Please visit our Help Center at {self.urls['help']} for accurate and up-to-date assistance.",
                'suggestions': [
                    "How to create an account",
                    "Payment methods",
                    "Contact support"
                ],
                'confidence': 70,
                'engine_used': 'netra_engine_dynamic',
                'help_center_url': self.urls['help'],
                'timestamp': datetime.now().isoformat()
            }

# Create the instance
netra_engine = HumanizedNetraEngine()