"""
Netra Engine - Intelligent Web Crawler for Netra Help Center
Fetches and understands content from the actual help articles.
"""

import requests
import random
import re
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import hashlib

class HumanizedNetraEngine:
    """
    AI Engine that crawls the Netra Help Center to get REAL information.
    It reads the main page, follows all links, and extracts actual content.
    """
    
    def __init__(self):
        self.help_center_url = "https://netra.strobid.com/help"
        self.base_url = "https://netra.strobid.com"
        self.main_site_url = "https://strobid.com"
        self.netra_site_url = "https://netra.strobid.com"
        
        # Knowledge base built by crawling
        self.knowledge_base = {
            'articles': {},      # Individual help articles
            'pages': {},          # Other pages
            'faqs': [],           # Frequently asked questions
            'topics': {}          # Organized by topic
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
                'Connection': 'keep-alive',
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except requests.exceptions.RequestException as e:
            print(f"❌ Failed to fetch {url}: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error fetching {url}: {e}")
            return None
    
    def _extract_article_content(self, soup: BeautifulSoup, url: str, title: str) -> Dict:
        """
        Extract the actual content from a help article page.
        This gets the REAL information that users need.
        """
        content = {
            'title': title,
            'url': url,
            'summary': '',
            'steps': [],
            'details': [],
            'tips': [],
            'warnings': [],
            'faqs': [],
            'related_topics': []
        }
        
        # Find the main content area
        main_content = None
        
        # Try common content containers
        for selector in ['main', 'article', '.content', '#content', '.help-content', '.documentation', '.post-content', '.entry-content']:
            main_content = soup.select_one(selector)
            if main_content:
                print(f"  📍 Found content with selector: {selector}")
                break
        
        if not main_content:
            # Fallback to body
            main_content = soup.body
            print("  📍 Using body as content")
        
        if main_content:
            # Remove unwanted elements
            for element in main_content.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside', '.sidebar', '#sidebar', '.comments']):
                element.decompose()
            
            # Get all text content
            all_text = main_content.get_text(separator='\n', strip=True)
            
            # Extract summary (first paragraph)
            first_paragraph = main_content.find('p')
            if first_paragraph:
                content['summary'] = first_paragraph.get_text().strip()
            
            # Extract steps (numbered or bulleted lists)
            for list_elem in main_content.find_all(['ol', 'ul']):
                list_items = list_elem.find_all('li')
                if list_items:
                    steps = []
                    for li in list_items:
                        step_text = li.get_text().strip()
                        if step_text:
                            steps.append(step_text)
                    
                    # Check if it looks like steps
                    if len(steps) > 1 and (list_elem.name == 'ol' or any(step[0].isdigit() for step in steps if step)):
                        content['steps'].extend(steps)
                    else:
                        content['details'].extend(steps)
            
            # Look for warning/admonition boxes
            for warning in main_content.find_all(['div', 'p'], class_=re.compile(r'warning|alert|caution|important|note', re.I)):
                content['warnings'].append(warning.get_text().strip())
            
            # Look for tip boxes
            for tip in main_content.find_all(['div', 'p'], class_=re.compile(r'tip|hint|pro|best', re.I)):
                content['tips'].append(tip.get_text().strip())
            
            # Look for FAQ section
            faq_section = main_content.find(['h2', 'h3', 'h4'], string=re.compile(r'faq|frequently asked|common questions', re.I))
            if faq_section:
                # Get next elements until next heading
                current = faq_section.next_sibling
                while current and current.name not in ['h2', 'h3', 'h4']:
                    if current.name in ['div', 'p', 'li']:
                        text = current.get_text().strip()
                        if text and len(text) > 20:
                            content['faqs'].append(text)
                    current = current.next_sibling
            
            # If we couldn't find structured content, use paragraphs
            if not content['steps'] and not content['details']:
                paragraphs = []
                for p in main_content.find_all('p'):
                    text = p.get_text().strip()
                    if text and len(text) > 30:
                        paragraphs.append(text)
                
                if paragraphs:
                    content['summary'] = paragraphs[0]
                    content['details'] = paragraphs[1:5]  # First few paragraphs as details
        
        return content
    
    def _extract_help_center_links(self, soup: BeautifulSoup) -> List[Dict]:
        """
        Extract all article links from the help center main page
        """
        articles = []
        
        # Find all links
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().strip()
            
            # Skip empty links and navigation
            if not text or len(text) < 3:
                continue
            
            # Skip external links
            if href.startswith('http') and self.base_url not in href:
                continue
            
            # Skip anchors and non-article links
            if href.startswith('#') or 'javascript:' in href:
                continue
            
            # Check if it looks like a help article
            full_url = urljoin(self.base_url, href)
            
            # Keywords that indicate it's a help article
            article_keywords = ['account', 'payment', 'subscription', 'notification', 'support', 'contact', 
                              'create', 'verify', 'reset', 'delete', 'manage', 'how', 'guide', 'help', 'faq']
            
            text_lower = text.lower()
            url_lower = href.lower()
            
            is_article = False
            
            # Check by text
            if any(keyword in text_lower for keyword in article_keywords):
                is_article = True
            
            # Check by URL
            if any(keyword in url_lower for keyword in article_keywords):
                is_article = True
            
            # Check if it's from the help center
            if '/help/' in href or '/help' in href:
                is_article = True
            
            if is_article:
                articles.append({
                    'title': text,
                    'url': full_url,
                    'type': 'article'
                })
        
        # Remove duplicates (by URL)
        unique_articles = []
        seen_urls = set()
        
        for article in articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)
        
        return unique_articles
    
    def _crawl_help_center(self):
        """
        Crawl the help center: read main page, then read all articles
        """
        print("\n" + "="*60)
        print("📚 CRAWLING HELP CENTER")
        print("="*60)
        
        # Step 1: Fetch main help page
        main_soup = self._fetch_page(self.help_center_url)
        if not main_soup:
            print("❌ Could not fetch help center main page")
            return
        
        # Step 2: Extract all article links
        articles = self._extract_help_center_links(main_soup)
        print(f"📋 Found {len(articles)} articles in help center")
        
        # Step 3: Read each article
        for i, article in enumerate(articles, 1):
            print(f"\n📄 Article {i}/{len(articles)}: {article['title']}")
            
            # Fetch the article page
            article_soup = self._fetch_page(article['url'])
            if not article_soup:
                continue
            
            # Extract the content
            content = self._extract_article_content(article_soup, article['url'], article['title'])
            
            # Store in knowledge base
            article_id = hashlib.md5(article['url'].encode()).hexdigest()[:8]
            
            self.knowledge_base['articles'][article_id] = {
                'title': article['title'],
                'url': article['url'],
                'content': content
            }
            
            # Determine topic based on content
            topic = self._determine_topic(article['title'] + ' ' + content['summary'])
            if topic not in self.knowledge_base['topics']:
                self.knowledge_base['topics'][topic] = []
            self.knowledge_base['topics'][topic].append(article_id)
            
            # Show what we found
            print(f"  ✅ Loaded: {content['title']}")
            if content['summary']:
                print(f"  📝 Summary: {content['summary'][:100]}...")
            if content['steps']:
                print(f"  📋 Steps: {len(content['steps'])} steps found")
            if content['faqs']:
                print(f"  ❓ FAQs: {len(content['faqs'])} found")
            
            # Be nice to the server
            time.sleep(0.5)
    
    def _crawl_main_site(self):
        """
        Crawl the main strobid.com site for general information
        """
        print("\n" + "="*60)
        print("🌐 CRAWLING MAIN SITE: strobid.com")
        print("="*60)
        
        # Fetch main page
        soup = self._fetch_page(self.main_site_url)
        if not soup:
            print("❌ Could not fetch main site")
            return
        
        # Extract about/company information
        about_section = soup.find(text=re.compile(r'about|company|who we are', re.I))
        if about_section:
            parent = about_section.find_parent(['div', 'section'])
            if parent:
                text = parent.get_text(strip=True)
                self.knowledge_base['pages']['about'] = {
                    'url': self.main_site_url,
                    'content': text
                }
                print(f"✅ Loaded about section")
        
        # Look for contact information
        contact_section = soup.find(text=re.compile(r'contact|reach|email', re.I))
        if contact_section:
            parent = contact_section.find_parent(['div', 'section'])
            if parent:
                text = parent.get_text(strip=True)
                self.knowledge_base['pages']['contact'] = {
                    'url': self.main_site_url,
                    'content': text
                }
                print(f"✅ Loaded contact information")
    
    def _determine_topic(self, text: str) -> str:
        """Determine the topic of an article based on its content"""
        text_lower = text.lower()
        
        topics = {
            'account': ['account', 'sign up', 'register', 'login', 'password', 'verify', 'profile'],
            'payment': ['payment', 'pay', 'subscription', 'billing', 'invoice', 'refund', 'money'],
            'settings': ['setting', 'notification', 'alert', 'preference', 'privacy'],
            'support': ['support', 'help', 'contact', 'assist', 'faq', 'question'],
            'service': ['service', 'provider', 'client', 'book', 'booking', 'hire']
        }
        
        max_score = 0
        best_topic = 'general'
        
        for topic, keywords in topics.items():
            score = 0
            for keyword in keywords:
                if keyword in text_lower:
                    score += 1
            if score > max_score:
                max_score = score
                best_topic = topic
        
        return best_topic
    
    def _crawl_all_sites(self):
        """Crawl all sites to build knowledge base"""
        print("\n" + "🚀"*10)
        print("🚀 STARTING FULL SITE CRAWL")
        print("🚀"*10)
        
        # Crawl help center first (most important)
        self._crawl_help_center()
        
        # Crawl main site for company info
        self._crawl_main_site()
        
        # Crawl netra site for app info
        netra_soup = self._fetch_page(self.netra_site_url)
        if netra_soup:
            print(f"\n📱 Crawling netra.strobid.com")
            # Extract app description
            description = netra_soup.find('meta', {'name': 'description'})
            if description:
                self.knowledge_base['pages']['netra_description'] = {
                    'url': self.netra_site_url,
                    'content': description.get('content', '')
                }
                print(f"✅ Loaded Netra app description")
        
        self.cache['last_crawl'] = datetime.now()
        
        # Summary
        print("\n" + "="*60)
        print("📊 CRAWL SUMMARY")
        print("="*60)
        print(f"📚 Articles loaded: {len(self.knowledge_base['articles'])}")
        for topic, articles in self.knowledge_base['topics'].items():
            print(f"   • {topic.capitalize()}: {len(articles)} articles")
        print("="*60)
    
    def _search_knowledge_base(self, query: str) -> List[Dict]:
        """
        Search the knowledge base for relevant information
        """
        query_lower = query.lower()
        results = []
        
        # Search through articles
        for article_id, article in self.knowledge_base['articles'].items():
            content = article['content']
            
            # Combine all text for searching
            searchable_text = (
                content['title'] + ' ' +
                content['summary'] + ' ' +
                ' '.join(content['steps']) + ' ' +
                ' '.join(content['details']) + ' ' +
                ' '.join(content['faqs'])
            ).lower()
            
            # Calculate relevance score
            score = 0
            
            # Check for exact phrase match
            if query_lower in searchable_text:
                score += 10
            
            # Check for keyword matches
            words = query_lower.split()
            for word in words:
                if len(word) > 3 and word in searchable_text:
                    score += 2
            
            if score > 0:
                results.append({
                    'article': article,
                    'content': content,
                    'score': score,
                    'title': article['title']
                })
        
        # Sort by score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def _format_article_response(self, article: Dict, query: str) -> str:
        """
        Format an article's content into a natural, helpful response
        """
        content = article['content']
        response_parts = []
        
        # Add title as context
        response_parts.append(f"**{content['title']}**")
        
        # Add summary if available
        if content['summary']:
            response_parts.append(content['summary'])
        
        # Add steps if available
        if content['steps']:
            response_parts.append("\n**Here's how:**")
            for i, step in enumerate(content['steps'], 1):
                response_parts.append(f"{i}. {step}")
        
        # Add details if available and no steps
        elif content['details']:
            response_parts.append("\n" + '\n\n'.join(content['details'][:3]))
        
        # Add warnings if relevant
        if content['warnings']:
            response_parts.append(f"\n⚠️ **Important:** {content['warnings'][0]}")
        
        # Add tips if available
        if content['tips']:
            response_parts.append(f"\n💡 **Tip:** {content['tips'][0]}")
        
        # Add FAQ if relevant
        if content['faqs'] and any(word in query.lower() for word in ['faq', 'question', 'common']):
            response_parts.append("\n**Frequently Asked Questions:**")
            for faq in content['faqs'][:2]:
                response_parts.append(f"• {faq}")
        
        # Add source
        response_parts.append(f"\n📌 *Source: Netra Help Center*")
        
        return '\n'.join(response_parts)
    
    def process_query(self, message: str, user_id: str = None) -> Dict[str, Any]:
        """
        Process user query by searching the crawled knowledge base
        """
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
                
                # Format the response
                response = self._format_article_response(best, message)
                
                # Calculate confidence based on score
                confidence = min(95, 70 + best['score'])
                
                # Generate suggestions based on topic
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
                        "How do I change my profile picture?",
                        "Privacy settings"
                    ],
                    'support': [
                        "How do I contact support?",
                        "What are your support hours?",
                        "Email support"
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
                
                # Try to get general help center info
                help_content = []
                for article in list(self.knowledge_base['articles'].values())[:5]:
                    help_content.append(f"• {article['title']}")
                
                if help_content:
                    response = f"I couldn't find specific information about '{message}' in our help center. Here are the main topics we cover:\n\n"
                    response += '\n'.join(help_content[:5])
                    response += f"\n\nYou can browse {self.help_center_url} for more information."
                else:
                    response = f"I couldn't find information about that. Please visit our Help Center at {self.help_center_url} or try asking about accounts, payments, or support."
                
                return {
                    'response': response,
                    'suggestions': [
                        "How do I create an account?",
                        "How do payments work?",
                        "How do I contact support?",
                        "How do I reset my password?"
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