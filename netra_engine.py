"""
Netra Engine - Fixed version that correctly identifies help articles
"""

import requests
import random
import re
import time
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import hashlib

class HumanizedNetraEngine:
    """
    AI Engine that correctly identifies and reads help articles
    """
    
    def __init__(self):
        self.help_center_url = "https://netra.strobid.com/help"
        self.base_url = "https://netra.strobid.com"
        self.main_site_url = "https://strobid.com"
        self.netra_site_url = "https://netra.strobid.com"
        
        # Knowledge base
        self.knowledge_base = {
            'help_articles': {},  # Only actual help articles
            'other_pages': {},    # Other pages (privacy, terms, etc.)
            'topics': {}
        }
        
        self.cache = {
            'last_crawl': None,
            'pages': {}
        }
        self.cache_duration = timedelta(hours=6)
        
        # Start crawling
        self._crawl_all_sites()
    
    def _fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch a page and return BeautifulSoup object"""
        try:
            print(f"🌐 Crawling: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Failed: {e}")
            return None
    
    def _is_help_article(self, url: str, link_text: str, soup: BeautifulSoup) -> bool:
        """
        Determine if a page is actually a help article
        """
        url_lower = url.lower()
        text_lower = link_text.lower()
        
        # Check URL patterns - help articles should be in /help/ directory
        if '/help/' not in url_lower and not url_lower.endswith('.html'):
            return False
        
        # Skip obvious non-help pages
        skip_patterns = ['privacy', 'terms', 'cookie', 'legal', 'contact', 'about']
        if any(pattern in url_lower for pattern in skip_patterns):
            return False
        
        # Check link text - help articles have descriptive titles
        help_keywords = ['how to', 'create', 'verify', 'reset', 'delete', 'manage', 
                        'account', 'payment', 'subscription', 'notification']
        
        if not any(keyword in text_lower for keyword in help_keywords):
            return False
        
        # Check page content - help articles typically have step-by-step instructions
        if soup:
            # Look for numbered lists (steps)
            lists = soup.find_all(['ol', 'ul'])
            if lists:
                for lst in lists:
                    items = lst.find_all('li')
                    if len(items) >= 2:  # Has multiple steps
                        return True
            
            # Look for instructional language
            text = soup.get_text().lower()
            instruction_words = ['step', 'first', 'then', 'next', 'finally', 'follow']
            if any(word in text for word in instruction_words):
                return True
        
        return False
    
    def _extract_help_articles(self, soup: BeautifulSoup, base_url: str) -> List[Dict]:
        """
        Extract only actual help articles from the help center
        """
        articles = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().strip()
            
            # Skip empty links
            if not text or len(text) < 5:
                continue
            
            # Make full URL
            if href.startswith('/'):
                full_url = urljoin(base_url, href)
            elif href.startswith('http'):
                if 'netra.strobid.com' not in href:
                    continue
                full_url = href
            else:
                full_url = urljoin(base_url, href)
            
            # Skip non-help URLs
            if any(skip in full_url.lower() for skip in ['privacy', 'terms', 'contact', 'about']):
                continue
            
            # Only include if it looks like a help article
            if any(keyword in text.lower() for keyword in ['how to', 'create', 'verify', 'reset', 'delete', 'manage']):
                articles.append({
                    'title': text,
                    'url': full_url,
                    'link_text': text
                })
        
        # Remove duplicates
        unique = {}
        for article in articles:
            if article['url'] not in unique:
                unique[article['url']] = article
        
        return list(unique.values())
    
    def _extract_article_content(self, soup: BeautifulSoup, url: str, title: str) -> Dict:
        """
        Extract the actual step-by-step content from a help article
        """
        content = {
            'title': title,
            'url': url,
            'summary': '',
            'steps': [],
            'details': [],
            'notes': []
        }
        
        # Find main content
        main_content = None
        for selector in ['main', 'article', '.content', '#content', '.help-content', 'body']:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            main_content = soup.body
        
        if main_content:
            # Remove unwanted elements
            for element in main_content.find_all(['script', 'style', 'nav', 'footer', 'header']):
                element.decompose()
            
            # Get title
            h1 = main_content.find('h1')
            if h1:
                content['title'] = h1.get_text().strip()
            
            # Get summary (first paragraph)
            first_p = main_content.find('p')
            if first_p:
                content['summary'] = first_p.get_text().strip()
            
            # Extract steps from ordered lists
            for ol in main_content.find_all('ol'):
                steps = []
                for li in ol.find_all('li'):
                    step_text = li.get_text().strip()
                    if step_text:
                        steps.append(step_text)
                if steps:
                    content['steps'].extend(steps)
            
            # If no ordered lists, look for bullet points that might be steps
            if not content['steps']:
                for ul in main_content.find_all('ul'):
                    items = []
                    for li in ul.find_all('li'):
                        item_text = li.get_text().strip()
                        if item_text:
                            items.append(item_text)
                    if items and len(items) >= 2:
                        content['steps'].extend(items)
            
            # Get other paragraphs as details
            for p in main_content.find_all('p')[1:3]:  # Next few paragraphs
                text = p.get_text().strip()
                if text and len(text) > 30:
                    content['details'].append(text)
            
            # Look for notes/warnings
            for note in main_content.find_all(['div', 'p'], class_=re.compile(r'note|warning|important', re.I)):
                text = note.get_text().strip()
                if text:
                    content['notes'].append(text)
        
        return content
    
    def _crawl_help_center(self):
        """Crawl help center and read all actual help articles"""
        print("\n" + "="*60)
        print("📚 CRAWLING HELP CENTER")
        print("="*60)
        
        # Fetch main help page
        soup = self._fetch_page(self.help_center_url)
        if not soup:
            print("❌ Could not fetch help center")
            return
        
        # Extract article links
        articles = self._extract_help_articles(soup, self.help_center_url)
        print(f"📋 Found {len(articles)} help articles")
        
        # Read each article
        for i, article in enumerate(articles, 1):
            print(f"\n📄 Reading: {article['title']}")
            
            article_soup = self._fetch_page(article['url'])
            if not article_soup:
                continue
            
            # Extract content
            content = self._extract_article_content(article_soup, article['url'], article['title'])
            
            # Store in knowledge base
            article_id = hashlib.md5(article['url'].encode()).hexdigest()[:8]
            
            self.knowledge_base['help_articles'][article_id] = {
                'title': article['title'],
                'url': article['url'],
                'content': content
            }
            
            # Determine topic
            topic = self._determine_topic(article['title'])
            if topic not in self.knowledge_base['topics']:
                self.knowledge_base['topics'][topic] = []
            self.knowledge_base['topics'][topic].append(article_id)
            
            # Show what we found
            print(f"  ✅ Loaded")
            if content['steps']:
                print(f"  📋 Found {len(content['steps'])} steps")
            if content['summary']:
                print(f"  📝 Summary: {content['summary'][:100]}...")
            
            time.sleep(0.5)
    
    def _crawl_other_pages(self):
        """Crawl other pages (privacy, terms, etc.) but don't confuse them with help"""
        print("\n" + "="*60)
        print("📑 CRAWLING OTHER PAGES")
        print("="*60)
        
        other_urls = [
            "https://netra.strobid.com/privacy.php",
            "https://netra.strobid.com/terms.php",
            "https://netra.strobid.com/about.php",
            "https://strobid.com"
        ]
        
        for url in other_urls:
            print(f"\n📄 Reading: {url}")
            soup = self._fetch_page(url)
            if not soup:
                continue
            
            # Store but mark as non-help
            page_id = hashlib.md5(url.encode()).hexdigest()[:8]
            title = soup.find('title')
            title_text = title.get_text().strip() if title else url.split('/')[-1]
            
            self.knowledge_base['other_pages'][page_id] = {
                'title': title_text,
                'url': url,
                'type': 'other',
                'content': soup.get_text()[:500]  # Store preview
            }
            print(f"  ✅ Stored as reference")
    
    def _determine_topic(self, text: str) -> str:
        """Determine topic from title"""
        text_lower = text.lower()
        
        if 'account' in text_lower or any(word in text_lower for word in ['create', 'verify', 'reset', 'delete']):
            return 'account'
        elif 'payment' in text_lower or 'subscription' in text_lower or 'billing' in text_lower:
            return 'payment'
        elif 'notification' in text_lower or 'setting' in text_lower:
            return 'settings'
        elif 'support' in text_lower or 'contact' in text_lower:
            return 'support'
        elif 'service' in text_lower or 'provider' in text_lower:
            return 'service'
        else:
            return 'general'
    
    def _crawl_all_sites(self):
        """Crawl everything, keeping help articles separate"""
        print("\n" + "🚀"*10)
        print("🚀 STARTING CRAWL")
        print("🚀"*10)
        
        # Clear previous data
        self.knowledge_base = {
            'help_articles': {},
            'other_pages': {},
            'topics': {}
        }
        
        # Crawl help center first (most important)
        self._crawl_help_center()
        
        # Crawl other pages for reference
        self._crawl_other_pages()
        
        self.cache['last_crawl'] = datetime.now()
        
        # Summary
        print("\n" + "="*60)
        print("📊 CRAWL SUMMARY")
        print("="*60)
        print(f"📚 Help articles: {len(self.knowledge_base['help_articles'])}")
        print(f"📑 Reference pages: {len(self.knowledge_base['other_pages'])}")
        for topic, articles in self.knowledge_base['topics'].items():
            print(f"   • {topic.capitalize()}: {len(articles)} articles")
        print("="*60)
    
    def _search_help_articles(self, query: str) -> List[Dict]:
        """Search only help articles (not other pages)"""
        query_lower = query.lower()
        results = []
        
        for article_id, article in self.knowledge_base['help_articles'].items():
            content = article['content']
            
            # Calculate score
            score = 0
            title_lower = article['title'].lower()
            
            # Title match (highest priority)
            if any(word in title_lower for word in query_lower.split()):
                score += 10
            
            # Summary match
            if any(word in content.get('summary', '').lower() for word in query_lower.split()):
                score += 5
            
            # Steps match
            steps_text = ' '.join(content.get('steps', [])).lower()
            if any(word in steps_text for word in query_lower.split()):
                score += 8
            
            if score > 0:
                results.append({
                    'article': article,
                    'content': content,
                    'score': score,
                    'title': article['title']
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def _format_article_response(self, article: Dict, query: str) -> str:
        """Format help article into natural response"""
        content = article['content']
        response_parts = []
        
        # Add title
        response_parts.append(f"**{content['title']}**")
        
        # Add summary if available
        if content.get('summary'):
            response_parts.append(content['summary'])
        
        # Add steps (most important)
        if content.get('steps'):
            response_parts.append("\n**Here's how:**")
            for i, step in enumerate(content['steps'], 1):
                response_parts.append(f"{i}. {step}")
        
        # Add any notes/warnings
        if content.get('notes'):
            response_parts.append(f"\n💡 **Note:** {content['notes'][0]}")
        
        # Add source
        response_parts.append(f"\n📌 *Source: Netra Help Center*")
        
        return '\n'.join(response_parts)
    
    def process_query(self, message: str, user_id: str = None) -> Dict[str, Any]:
        """Process user query"""
        try:
            print(f"\n🤔 Processing: {message}")
            
            # Check cache
            if (self.cache['last_crawl'] is None or 
                datetime.now() - self.cache['last_crawl'] > self.cache_duration):
                print("⏰ Cache expired, re-crawling...")
                self._crawl_all_sites()
            
            # Handle greetings
            greetings = ['hi', 'hello', 'hey', 'good morning']
            if any(g in message.lower() for g in greetings):
                return {
                    'response': "Hello! 👋 I'm your Netra assistant. I can help you with accounts, payments, settings, and more. What would you like to know?",
                    'suggestions': [
                        "How do I create an account?",
                        "How do payments work?",
                        "How do I reset my password?"
                    ],
                    'confidence': 100,
                    'engine_used': 'netra_engine',
                    'help_center_url': self.help_center_url,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Search ONLY help articles
            results = self._search_help_articles(message)
            
            if results:
                best = results[0]
                print(f"✅ Found: {best['title']} (score: {best['score']})")
                
                response = self._format_article_response(best, message)
                
                # Get topic-based suggestions
                topic = self._determine_topic(best['title'])
                suggestions_map = {
                    'account': [
                        "How do I verify my account?",
                        "How do I reset my password?",
                        "How do I delete my account?"
                    ],
                    'payment': [
                        "How do payments work?",
                        "How do I get a refund?",
                        "What payment methods are accepted?"
                    ],
                    'settings': [
                        "How do I manage notifications?",
                        "How do I change my profile?"
                    ],
                    'support': [
                        "How do I contact support?",
                        "What are your support hours?"
                    ]
                }
                
                suggestions = suggestions_map.get(topic, [
                    "How do I create an account?",
                    "How do payments work?",
                    "How do I contact support?"
                ])
                
                return {
                    'response': response,
                    'suggestions': suggestions[:4],
                    'confidence': min(95, 70 + best['score']),
                    'engine_used': 'netra_engine',
                    'help_center_url': self.help_center_url,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Show available help topics
                topics = list(self.knowledge_base['topics'].keys())
                response = f"I couldn't find specific information about '{message}'. Here are the help topics available:\n\n"
                
                for topic in topics[:5]:
                    response += f"• {topic.capitalize()}\n"
                
                response += f"\nYou can visit {self.help_center_url} for more information."
                
                return {
                    'response': response,
                    'suggestions': [
                        "How do I create an account?",
                        "How do payments work?",
                        "How do I contact support?"
                    ],
                    'confidence': 60,
                    'engine_used': 'netra_engine',
                    'help_center_url': self.help_center_url,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return {
                'response': f"I'm having trouble accessing information. Please visit our Help Center at {self.help_center_url} for assistance.",
                'suggestions': [
                    "How do I create an account?",
                    "How do payments work?",
                    "How do I contact support?"
                ],
                'confidence': 50,
                'engine_used': 'netra_engine',
                'help_center_url': self.help_center_url,
                'timestamp': datetime.now().isoformat()
            }

# Create the instance
netra_engine = HumanizedNetraEngine()