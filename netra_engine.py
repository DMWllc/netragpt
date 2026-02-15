"""
Netra Engine - Complete Web Crawler for Netra Sites
Crawls: netra.strobid.com, netra.strobid.com/help, and follows all article links
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
    AI Engine that crawls all Netra websites to get REAL information.
    It reads pages, follows links, and extracts actual content.
    """
    
    def __init__(self):
        # Base URLs to crawl
        self.help_center_url = "https://netra.strobid.com/help"
        self.base_url = "https://netra.strobid.com"
        self.main_site_url = "https://strobid.com"
        self.netra_site_url = "https://netra.strobid.com"
        
        # Track crawled URLs to avoid duplicates
        self.crawled_urls: Set[str] = set()
        self.url_queue: List[str] = []
        
        # Knowledge base built by crawling
        self.knowledge_base = {
            'articles': {},      # Individual help articles
            'pages': {},          # General pages
            'faqs': [],           # Frequently asked questions
            'topics': {},         # Organized by topic
            'site_structure': {}  # Map of URLs to topics
        }
        
        # Cache settings
        self.cache = {
            'last_crawl': None,
            'pages': {}
        }
        self.cache_duration = timedelta(hours=6)
        
        # Start crawling on initialization
        self._crawl_all_sites()
    
    def _fetch_page(self, url: str) -> Optional[BeautifulSoup]:
        """Fetch a page and return BeautifulSoup object"""
        try:
            print(f"🌐 Crawling: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            # Check if we got meaningful content
            content_length = len(response.text)
            if content_length < 500:
                print(f"  ⚠️ Page seems small ({content_length} bytes)")
            
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"  ❌ Failed to fetch {url}: {e}")
            return None
    
    def _extract_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all internal links from a page"""
        links = []
        parsed_base = urlparse(base_url)
        base_domain = f"{parsed_base.scheme}://{parsed_base.netloc}"
        
        for link in soup.find_all('a', href=True):
            href = link['href'].strip()
            
            # Skip empty, anchors, and external links
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue
            
            # Make absolute URL
            if href.startswith('/'):
                full_url = urljoin(base_domain, href)
            elif href.startswith('http'):
                # Only include netra.strobid.com and strobid.com
                if 'netra.strobid.com' in href or 'strobid.com' in href:
                    full_url = href
                else:
                    continue
            else:
                full_url = urljoin(base_url, href)
            
            # Remove fragments
            full_url = full_url.split('#')[0]
            
            if full_url not in self.crawled_urls and full_url not in links:
                links.append(full_url)
        
        return links
    
    def _extract_page_content(self, soup: BeautifulSoup, url: str) -> Dict:
        """
        Extract all meaningful content from a page
        """
        content = {
            'url': url,
            'title': '',
            'summary': '',
            'headings': [],
            'paragraphs': [],
            'lists': [],
            'steps': [],
            'tips': [],
            'warnings': [],
            'faqs': [],
            'metadata': {}
        }
        
        # Get title
        title_tag = soup.find('title')
        if title_tag:
            content['title'] = title_tag.get_text().strip()
        
        # Get meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            content['metadata']['description'] = meta_desc['content']
        
        # Find main content area
        main_content = None
        for selector in ['main', 'article', '.content', '#content', '.main-content', '.help-content', 'body']:
            main_content = soup.select_one(selector)
            if main_content:
                break
        
        if not main_content:
            main_content = soup.body
        
        if main_content:
            # Remove unwanted elements
            for element in main_content.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Extract headings (for structure)
            for heading in main_content.find_all(['h1', 'h2', 'h3']):
                text = heading.get_text().strip()
                if text:
                    content['headings'].append({
                        'level': heading.name,
                        'text': text
                    })
            
            # Extract paragraphs
            for p in main_content.find_all('p'):
                text = p.get_text().strip()
                if text and len(text) > 20:
                    content['paragraphs'].append(text)
            
            # Set summary from first paragraph
            if content['paragraphs']:
                content['summary'] = content['paragraphs'][0]
            
            # Extract lists (potential steps)
            for list_elem in main_content.find_all(['ol', 'ul']):
                items = []
                for li in list_elem.find_all('li'):
                    item_text = li.get_text().strip()
                    if item_text:
                        items.append(item_text)
                
                if items:
                    # Check if it's a numbered list (steps)
                    if list_elem.name == 'ol' or any(item[0].isdigit() for item in items if item):
                        content['steps'].extend(items)
                    else:
                        content['lists'].extend(items)
            
            # Look for warnings
            for warning in main_content.find_all(['div', 'p'], class_=re.compile(r'warning|alert|caution|important|note', re.I)):
                text = warning.get_text().strip()
                if text:
                    content['warnings'].append(text)
            
            # Look for tips
            for tip in main_content.find_all(['div', 'p'], class_=re.compile(r'tip|hint|pro|best', re.I)):
                text = tip.get_text().strip()
                if text:
                    content['tips'].append(text)
            
            # Look for FAQ sections
            faq_heading = main_content.find(['h2', 'h3', 'h4'], string=re.compile(r'faq|frequently asked|common questions', re.I))
            if faq_heading:
                current = faq_heading.next_sibling
                faq_items = []
                while current and current.name not in ['h2', 'h3', 'h4']:
                    if current.name in ['div', 'p', 'li']:
                        text = current.get_text().strip()
                        if text and len(text) > 20:
                            faq_items.append(text)
                    current = current.next_sibling
                if faq_items:
                    content['faqs'].extend(faq_items)
        
        return content
    
    def _determine_topic(self, url: str, content: Dict) -> str:
        """Determine the topic of a page based on URL and content"""
        url_lower = url.lower()
        text = content['title'].lower() + ' ' + content['summary'].lower()
        
        # Check URL first
        if 'account' in url_lower or any(word in url_lower for word in ['signup', 'register', 'login', 'password']):
            return 'account'
        elif 'payment' in url_lower or any(word in url_lower for word in ['pay', 'subscription', 'billing']):
            return 'payment'
        elif 'setting' in url_lower or 'notification' in url_lower:
            return 'settings'
        elif 'support' in url_lower or 'contact' in url_lower or 'help' in url_lower:
            return 'support'
        elif 'service' in url_lower or 'provider' in url_lower or 'client' in url_lower:
            return 'service'
        
        # Check content
        topics = {
            'account': ['account', 'sign up', 'register', 'login', 'password', 'verify'],
            'payment': ['payment', 'pay', 'subscription', 'billing', 'refund', 'money'],
            'settings': ['setting', 'notification', 'alert', 'preference', 'privacy'],
            'support': ['support', 'help', 'contact', 'assist', 'faq'],
            'service': ['service', 'provider', 'client', 'book', 'hire']
        }
        
        max_score = 0
        best_topic = 'general'
        
        for topic, keywords in topics.items():
            score = 0
            for keyword in keywords:
                if keyword in text:
                    score += 1
            if score > max_score:
                max_score = score
                best_topic = topic
        
        return best_topic
    
    def _crawl_site(self, start_url: str, max_pages: int = 50):
        """Crawl a site starting from a URL"""
        print(f"\n📚 STARTING CRAWL OF: {start_url}")
        print("="*60)
        
        self.url_queue = [start_url]
        
        while self.url_queue and len(self.crawled_urls) < max_pages:
            url = self.url_queue.pop(0)
            
            if url in self.crawled_urls:
                continue
            
            # Fetch page
            soup = self._fetch_page(url)
            if not soup:
                self.crawled_urls.add(url)
                continue
            
            # Extract content
            content = self._extract_page_content(soup, url)
            
            # Store in knowledge base
            page_id = hashlib.md5(url.encode()).hexdigest()[:8]
            
            # Determine if it's an article or general page
            if '/help/' in url or any(keyword in url for keyword in ['account', 'payment', 'subscription']):
                self.knowledge_base['articles'][page_id] = {
                    'url': url,
                    'title': content['title'] or url.split('/')[-1].replace('.html', '').replace('-', ' ').title(),
                    'content': content
                }
                print(f"  ✅ Stored as article: {content['title']}")
            else:
                self.knowledge_base['pages'][page_id] = {
                    'url': url,
                    'title': content['title'] or 'Netra Page',
                    'content': content
                }
                print(f"  ✅ Stored as page: {url}")
            
            # Determine topic
            topic = self._determine_topic(url, content)
            if topic not in self.knowledge_base['topics']:
                self.knowledge_base['topics'][topic] = []
            self.knowledge_base['topics'][topic].append(page_id)
            
            # Store site structure
            self.knowledge_base['site_structure'][url] = {
                'topic': topic,
                'title': content['title'],
                'page_id': page_id
            }
            
            # Extract new links to crawl
            new_links = self._extract_links(soup, url)
            for link in new_links:
                if link not in self.crawled_urls and link not in self.url_queue:
                    self.url_queue.append(link)
            
            self.crawled_urls.add(url)
            
            # Be nice to the server
            time.sleep(0.5)
    
    def _crawl_all_sites(self):
        """Crawl all Netra sites"""
        print("\n" + "🚀"*10)
        print("🚀 STARTING FULL SITE CRAWL")
        print("🚀"*10)
        
        # Clear previous crawl data
        self.crawled_urls = set()
        self.knowledge_base = {
            'articles': {},
            'pages': {},
            'faqs': [],
            'topics': {},
            'site_structure': {}
        }
        
        # Crawl netra.strobid.com
        self._crawl_site(self.netra_site_url, max_pages=30)
        
        # Crawl help center (if different from main site)
        if self.help_center_url != self.netra_site_url:
            self._crawl_site(self.help_center_url, max_pages=30)
        
        # Crawl main strobid.com
        self._crawl_site(self.main_site_url, max_pages=20)
        
        self.cache['last_crawl'] = datetime.now()
        
        # Print summary
        self._print_crawl_summary()
    
    def _print_crawl_summary(self):
        """Print summary of what was crawled"""
        print("\n" + "="*60)
        print("📊 CRAWL SUMMARY")
        print("="*60)
        print(f"📚 Total pages crawled: {len(self.crawled_urls)}")
        print(f"📄 Articles stored: {len(self.knowledge_base['articles'])}")
        print(f"📑 General pages: {len(self.knowledge_base['pages'])}")
        print("\n📋 Topics covered:")
        for topic, pages in self.knowledge_base['topics'].items():
            print(f"   • {topic.capitalize()}: {len(pages)} pages")
        print("="*60)
    
    def _search_knowledge_base(self, query: str) -> List[Dict]:
        """Search the knowledge base for relevant information"""
        query_lower = query.lower()
        query_words = set(query_lower.split())
        results = []
        
        # Search through articles (prioritize these)
        for article_id, article in self.knowledge_base['articles'].items():
            content = article['content']
            
            # Combine all text for searching
            searchable_text = (
                article['title'].lower() + ' ' +
                content['summary'].lower() + ' ' +
                ' '.join(content['paragraphs']).lower() + ' ' +
                ' '.join(content['steps']).lower() + ' ' +
                ' '.join(content['lists']).lower()
            )
            
            # Calculate relevance
            score = 0
            
            # Exact phrase match
            if query_lower in searchable_text:
                score += 20
            
            # Word matches
            for word in query_words:
                if len(word) > 2 and word in searchable_text:
                    score += 3
            
            # Title match bonus
            if any(word in article['title'].lower() for word in query_words):
                score += 5
            
            if score > 0:
                results.append({
                    'type': 'article',
                    'id': article_id,
                    'title': article['title'],
                    'content': content,
                    'score': score,
                    'url': article['url']
                })
        
        # Search through general pages
        for page_id, page in self.knowledge_base['pages'].items():
            content = page['content']
            searchable_text = (
                page['title'].lower() + ' ' +
                content['summary'].lower() + ' ' +
                ' '.join(content['paragraphs']).lower()
            )
            
            score = 0
            if query_lower in searchable_text:
                score += 10
            
            for word in query_words:
                if len(word) > 2 and word in searchable_text:
                    score += 2
            
            if score > 5:  # Only include reasonably relevant pages
                results.append({
                    'type': 'page',
                    'id': page_id,
                    'title': page['title'],
                    'content': content,
                    'score': score,
                    'url': page['url']
                })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def _format_response(self, result: Dict, query: str) -> str:
        """Format search result into a natural response"""
        content = result['content']
        response_parts = []
        
        # Add title
        if result['title']:
            response_parts.append(f"**{result['title']}**")
        
        # Add summary if available
        if content.get('summary'):
            response_parts.append(content['summary'])
        
        # Add steps if available
        if content.get('steps'):
            response_parts.append("\n**Here's how:**")
            for i, step in enumerate(content['steps'][:5], 1):
                response_parts.append(f"{i}. {step}")
        
        # Add key paragraphs if no steps
        elif content.get('paragraphs'):
            # Get paragraphs that contain query words
            relevant_paras = []
            query_words = set(query.lower().split())
            for para in content['paragraphs'][:3]:
                if any(word in para.lower() for word in query_words):
                    relevant_paras.append(para)
            
            if relevant_paras:
                response_parts.append("\n" + '\n\n'.join(relevant_paras))
            else:
                response_parts.append("\n" + '\n\n'.join(content['paragraphs'][:2]))
        
        # Add warnings if relevant
        if content.get('warnings'):
            response_parts.append(f"\n⚠️ **Important:** {content['warnings'][0]}")
        
        # Add tips if available
        if content.get('tips'):
            response_parts.append(f"\n💡 **Tip:** {content['tips'][0]}")
        
        # Add source
        response_parts.append(f"\n📌 *Source: {result['url']}*")
        
        return '\n'.join(response_parts)
    
    def process_query(self, message: str, user_id: str = None) -> Dict[str, Any]:
        """Process user query by searching crawled content"""
        try:
            print(f"\n🤔 Processing query: {message}")
            
            # Check if we need to re-crawl
            if (self.cache['last_crawl'] is None or 
                datetime.now() - self.cache['last_crawl'] > self.cache_duration):
                print("⏰ Cache expired, re-crawling...")
                self._crawl_all_sites()
            
            # Handle greetings
            greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'good evening']
            if any(g in message.lower() for g in greetings):
                return {
                    'response': "Hello! 👋 I'm your Netra assistant. I can help you with accounts, payments, settings, and more. What would you like to know?",
                    'suggestions': [
                        "How do I create an account?",
                        "How do payments work?",
                        "How do I reset my password?",
                        "How do I contact support?"
                    ],
                    'confidence': 100,
                    'engine_used': 'netra_engine',
                    'help_center_url': self.help_center_url,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Search knowledge base
            results = self._search_knowledge_base(message)
            
            if results:
                best = results[0]
                print(f"✅ Found match: {best['title']} (score: {best['score']})")
                
                # Format response
                response = self._format_response(best, message)
                
                # Calculate confidence
                confidence = min(95, 70 + best['score'])
                
                # Generate suggestions based on topic
                topic = self._determine_topic(best.get('url', ''), best['content'])
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
                        "How do I change my profile?",
                        "Privacy settings"
                    ],
                    'support': [
                        "How do I contact support?",
                        "What are your support hours?",
                        "Email support"
                    ],
                    'service': [
                        "How do I become a provider?",
                        "How do I book a service?",
                        "How do reviews work?"
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
                    'confidence': confidence,
                    'engine_used': 'netra_engine',
                    'help_center_url': self.help_center_url,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                print("❌ No relevant content found")
                
                # Show available topics
                topics = list(self.knowledge_base['topics'].keys())
                response = f"I couldn't find specific information about '{message}'. Here are the topics I can help with:\n\n"
                
                for topic in topics[:5]:
                    response += f"• {topic.capitalize()}\n"
                
                response += f"\nYou can also visit {self.help_center_url} for more information."
                
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
            print(f"❌ Error in process_query: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                'response': f"I'm having trouble accessing information right now. Please visit our Help Center at {self.help_center_url} for assistance.",
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