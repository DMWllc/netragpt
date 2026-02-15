"""
Netra Engine - Production version with JavaScript rendering support
Fetches content from netra.strobid.com/help and follows all article links
"""

import requests
import random
import re
import time
import asyncio
from typing import Dict, List, Optional, Any, Set
from datetime import datetime, timedelta
from urllib.parse import urljoin, urlparse
import hashlib
from bs4 import BeautifulSoup

# For JavaScript rendering
try:
    from requests_html import HTMLSession
    HAS_HTML = True
except ImportError:
    HAS_HTML = False
    print("⚠️ requests-html not installed. Run: pip install requests-html")

class HumanizedNetraEngine:
    """
    AI Engine that fetches content with JavaScript support
    """
    
    def __init__(self):
        self.help_center_url = "https://netra.strobid.com/help"
        self.base_url = "https://netra.strobid.com"
        self.netra_site_url = "https://netra.strobid.com"
        self.main_site_url = "https://strobid.com"
        
        # Initialize HTML session for JavaScript rendering
        self.session = None
        if HAS_HTML:
            self.session = HTMLSession()
        
        # Knowledge base
        self.knowledge_base = {
            'help_articles': {},
            'site_pages': {},
            'topics': {}
        }
        
        # Cache settings
        self.last_crawl = None
        self.cache_duration = timedelta(hours=6)
        
        # Fallback knowledge in case fetch fails
        self.fallback_articles = {
            'create_account': {
                'title': 'How to create a Netra account',
                'url': 'https://netra.strobid.com/help/create-account.html',
                'summary': 'Creating a Netra account is quick and easy. Follow these steps to get started.',
                'steps': [
                    'Download the Netra app from the Google Play Store',
                    'Open the app and tap "Create Account"',
                    'Enter your email address and create a secure password',
                    'Fill in your profile information (name, phone number)',
                    'Check your email for a verification code',
                    'Enter the code to verify your account'
                ],
                'topic': 'account'
            },
            'verify_account': {
                'title': 'How to verify your account',
                'url': 'https://netra.strobid.com/help/verify-account.html',
                'summary': 'Account verification helps build trust in the Netra community.',
                'steps': [
                    'Log in to your Netra account',
                    'Go to Settings > Account > Verification',
                    'Choose email or phone verification',
                    'Check your inbox for a verification link',
                    'Enter the code sent to your phone',
                    'Your account is now verified!'
                ],
                'topic': 'account'
            },
            'reset_password': {
                'title': 'How to reset your password',
                'url': 'https://netra.strobid.com/help/reset-password.html',
                'summary': "Forgot your password? Here's how to reset it safely.",
                'steps': [
                    'Open the Netra app',
                    'Tap "Forgot Password" on the login screen',
                    'Enter your registered email address',
                    'Check your email for a reset link',
                    'Click the link (valid for 1 hour)',
                    'Create a new strong password'
                ],
                'topic': 'account'
            },
            'delete_account': {
                'title': 'How to delete your Netra account',
                'url': 'https://netra.strobid.com/help/delete-account.html',
                'summary': 'Step-by-step guide to permanently remove your account.',
                'steps': [
                    'Open the Netra app and log in',
                    'Go to Settings > Account > Delete Account',
                    'Read the warning carefully',
                    'Enter your password to confirm',
                    'Select a reason for leaving (optional)',
                    'Tap "Permanently Delete"'
                ],
                'warnings': ['This action is PERMANENT and cannot be undone'],
                'topic': 'account'
            },
            'payments': {
                'title': 'How payments work on Netra',
                'url': 'https://netra.strobid.com/help/payments.html',
                'summary': 'Understand how to make, track, and manage payments.',
                'steps': [
                    'See the total price when booking',
                    'Choose payment method (card, mobile money, cash)',
                    'Pay deposit to confirm booking',
                    'Pay balance after service completion',
                    'Funds held securely until satisfied',
                    'Providers paid within 24 hours'
                ],
                'details': [
                    'Accepted: Visa, Mastercard, MTN Mobile Money, Airtel Money',
                    'No fees for clients',
                    'Providers pay small commission on completed bookings'
                ],
                'topic': 'payment'
            },
            'subscriptions': {
                'title': 'Manage subscriptions & billing',
                'url': 'https://netra.strobid.com/help/subscriptions.html',
                'summary': 'Learn how to subscribe, cancel, or update your plan.',
                'steps': [
                    'Go to Settings > Subscription',
                    'Browse available plans (Free, Pro, Business)',
                    'Select your preferred plan',
                    'Choose monthly or annual billing',
                    'Enter payment details',
                    'Confirm subscription'
                ],
                'topic': 'payment'
            },
            'notifications': {
                'title': 'Manage notifications',
                'url': 'https://netra.strobid.com/help/notifications.html',
                'summary': 'Turn on/off alerts and notifications in Netra.',
                'steps': [
                    'Open Netra app',
                    'Go to Settings > Notifications',
                    'Toggle each notification type',
                    'Message notifications',
                    'Booking updates',
                    'Payment notifications'
                ],
                'topic': 'settings'
            },
            'contact_support': {
                'title': 'Contact Netra support',
                'url': 'https://netra.strobid.com/help/contact-support.html',
                'summary': 'Reach out to our support team for personalized help.',
                'details': [
                    'Email: support@strobid.com',
                    'In-app chat: Settings > Help & Support',
                    'Help Center: https://netra.strobid.com/help',
                    'Response time: Within 24 hours'
                ],
                'topic': 'support'
            }
        }
        
        # Initialize with fallback
        self._init_fallback()
        
        # Start crawling
        self._crawl_all_sites()
    
    def _init_fallback(self):
        """Initialize knowledge base with fallback articles"""
        for article_id, article in self.fallback_articles.items():
            self.knowledge_base['help_articles'][article_id] = article
            topic = article.get('topic', 'general')
            if topic not in self.knowledge_base['topics']:
                self.knowledge_base['topics'][topic] = []
            self.knowledge_base['topics'][topic].append(article_id)
    
    def _fetch_with_js(self, url: str) -> Optional[str]:
        """Fetch page with JavaScript rendering"""
        if not self.session:
            return None
        
        try:
            print(f"🌐 JS Fetch: {url}")
            response = self.session.get(url, timeout=15)
            
            # Try to render JavaScript
            try:
                response.html.render(timeout=20, sleep=2, keep_page=False)
                print(f"  ✅ JS rendered successfully")
                return response.html.html
            except Exception as e:
                print(f"  ⚠️ JS render failed: {e}")
                return response.text  # Return raw HTML if render fails
                
        except Exception as e:
            print(f"  ❌ JS fetch failed: {e}")
            return None
    
    def _fetch_simple(self, url: str) -> Optional[str]:
        """Simple fetch without JS"""
        try:
            print(f"🌐 Simple fetch: {url}")
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"  ❌ Simple fetch failed: {e}")
            return None
    
    def _extract_article_links(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract article links from help center page"""
        articles = []
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            text = link.get_text().strip()
            
            if not text or len(text) < 5:
                continue
            
            # Make full URL
            if href.startswith('/'):
                full_url = urljoin(self.base_url, href)
            elif href.startswith('http'):
                if 'netra.strobid.com' not in href:
                    continue
                full_url = href
            else:
                full_url = urljoin(self.help_center_url, href)
            
            # Skip non-help pages
            skip_patterns = ['privacy', 'terms', 'cookie', 'login', 'signup']
            if any(p in full_url.lower() for p in skip_patterns):
                continue
            
            # Check if it's a help article
            help_keywords = ['account', 'payment', 'subscription', 'notification', 'support', 
                           'create', 'verify', 'reset', 'delete', 'manage']
            
            if any(k in text.lower() for k in help_keywords) or any(k in href.lower() for k in help_keywords):
                articles.append({
                    'title': text,
                    'url': full_url,
                    'text': text
                })
        
        # Remove duplicates
        unique = {}
        for a in articles:
            if a['url'] not in unique:
                unique[a['url']] = a
        
        return list(unique.values())
    
    def _extract_article_content(self, html: str, url: str, title: str) -> Dict:
        """Extract content from article page"""
        soup = BeautifulSoup(html, 'html.parser')
        
        content = {
            'title': title,
            'url': url,
            'summary': '',
            'steps': [],
            'details': [],
            'warnings': []
        }
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Find main content
        main = None
        for selector in ['main', 'article', '.content', '#content', '.help-content', 'body']:
            main = soup.select_one(selector)
            if main:
                break
        
        if not main:
            main = soup.body
        
        if main:
            # Get title from page if available
            h1 = main.find('h1')
            if h1:
                content['title'] = h1.get_text().strip()
            
            # Get summary (first paragraph)
            first_p = main.find('p')
            if first_p:
                content['summary'] = first_p.get_text().strip()
            
            # Extract steps
            for ol in main.find_all('ol'):
                steps = []
                for li in ol.find_all('li'):
                    step = li.get_text().strip()
                    if step:
                        steps.append(step)
                if steps:
                    content['steps'].extend(steps)
            
            # If no ordered lists, try unordered
            if not content['steps']:
                for ul in main.find_all('ul'):
                    items = []
                    for li in ul.find_all('li'):
                        item = li.get_text().strip()
                        if item:
                            items.append(item)
                    if items and len(items) >= 2:
                        content['steps'].extend(items)
            
            # Get other paragraphs
            for p in main.find_all('p')[1:3]:
                text = p.get_text().strip()
                if text and len(text) > 30:
                    content['details'].append(text)
            
            # Look for warnings
            for warning in main.find_all(['div', 'p'], class_=re.compile(r'warning|alert|important', re.I)):
                text = warning.get_text().strip()
                if text:
                    content['warnings'].append(text)
        
        return content
    
    def _crawl_help_center(self):
        """Crawl help center and read all articles"""
        print("\n" + "="*60)
        print("📚 CRAWLING HELP CENTER")
        print("="*60)
        
        # Try JS fetch first
        html = self._fetch_with_js(self.help_center_url)
        if not html:
            html = self._fetch_simple(self.help_center_url)
        
        if not html:
            print("❌ Could not fetch help center, using fallback")
            return
        
        soup = BeautifulSoup(html, 'html.parser')
        articles = self._extract_article_links(soup)
        
        print(f"📋 Found {len(articles)} articles")
        
        # Clear existing and add fetched articles
        self.knowledge_base['help_articles'] = {}
        self.knowledge_base['topics'] = {}
        
        for i, article in enumerate(articles, 1):
            print(f"\n📄 Reading: {article['title']}")
            
            # Try JS fetch for article
            article_html = self._fetch_with_js(article['url'])
            if not article_html:
                article_html = self._fetch_simple(article['url'])
            
            if article_html:
                content = self._extract_article_content(article_html, article['url'], article['title'])
                
                # Determine topic
                topic = 'general'
                if any(w in content['title'].lower() for w in ['account', 'create', 'verify', 'reset', 'delete']):
                    topic = 'account'
                elif any(w in content['title'].lower() for w in ['payment', 'subscription', 'billing']):
                    topic = 'payment'
                elif 'notification' in content['title'].lower():
                    topic = 'settings'
                elif 'support' in content['title'].lower() or 'contact' in content['title'].lower():
                    topic = 'support'
                
                content['topic'] = topic
                
                # Store
                article_id = hashlib.md5(article['url'].encode()).hexdigest()[:8]
                self.knowledge_base['help_articles'][article_id] = content
                
                if topic not in self.knowledge_base['topics']:
                    self.knowledge_base['topics'][topic] = []
                self.knowledge_base['topics'][topic].append(article_id)
                
                print(f"  ✅ Loaded - Topic: {topic}")
                if content.get('steps'):
                    print(f"  📋 Steps: {len(content['steps'])}")
            
            time.sleep(0.5)
        
        # If no articles found, use fallback
        if not self.knowledge_base['help_articles']:
            print("\n⚠️ No articles fetched, using fallback")
            self._init_fallback()
    
    def _crawl_all_sites(self):
        """Crawl all sites"""
        print("\n" + "🚀"*10)
        print("🚀 STARTING CRAWL")
        print("🚀"*10)
        
        self._crawl_help_center()
        
        self.last_crawl = datetime.now()
        
        # Summary
        print("\n" + "="*60)
        print("📊 CRAWL SUMMARY")
        print("="*60)
        print(f"📚 Articles: {len(self.knowledge_base['help_articles'])}")
        for topic, articles in self.knowledge_base['topics'].items():
            print(f"   • {topic.capitalize()}: {len(articles)} articles")
        print("="*60)
    
    def _search_articles(self, query: str) -> List[Dict]:
        """Search for relevant articles"""
        query_lower = query.lower()
        results = []
        
        for article_id, article in self.knowledge_base['help_articles'].items():
            score = 0
            title_lower = article['title'].lower()
            
            # Title match
            if any(word in title_lower for word in query_lower.split()):
                score += 10
            
            # Summary match
            if article.get('summary'):
                if any(word in article['summary'].lower() for word in query_lower.split()):
                    score += 5
            
            # Steps match
            if article.get('steps'):
                steps_text = ' '.join(article['steps']).lower()
                if any(word in steps_text for word in query_lower.split()):
                    score += 8
            
            if score > 0:
                results.append({
                    'id': article_id,
                    'article': article,
                    'score': score,
                    'title': article['title']
                })
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def _format_response(self, article: Dict) -> str:
        """Format article into natural response"""
        response_parts = []
        
        # Title
        response_parts.append(f"**{article['title']}**")
        
        # Summary
        if article.get('summary'):
            response_parts.append(article['summary'])
        
        # Steps
        if article.get('steps'):
            response_parts.append("\n**Here's how:**")
            for i, step in enumerate(article['steps'][:6], 1):
                response_parts.append(f"{i}. {step}")
        
        # Details
        if article.get('details') and not article.get('steps'):
            response_parts.append("\n" + '\n'.join(article['details']))
        
        # Warnings
        if article.get('warnings'):
            response_parts.append(f"\n⚠️ **Important:** {article['warnings'][0]}")
        
        return '\n'.join(response_parts)
    
    def process_query(self, message: str, user_id: str = None) -> Dict[str, Any]:
        """Process user query"""
        try:
            print(f"\n🤔 Processing: {message}")
            
            # Check cache
            if self.last_crawl and datetime.now() - self.last_crawl > self.cache_duration:
                print("⏰ Cache expired, re-crawling...")
                self._crawl_all_sites()
            
            # Handle greetings
            greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon']
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
            
            # Search articles
            results = self._search_articles(message)
            
            if results:
                best = results[0]
                print(f"✅ Found: {best['title']} (score: {best['score']})")
                
                response = self._format_response(best['article'])
                
                # Get topic suggestions
                topic = best['article'].get('topic', 'general')
                suggestions_map = {
                    'account': [
                        "How do I verify my account?",
                        "How do I reset my password?",
                        "How do I delete my account?"
                    ],
                    'payment': [
                        "How do payments work?",
                        "What payment methods are accepted?",
                        "How do I get a refund?"
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
                # Show available topics
                topics = list(self.knowledge_base['topics'].keys())
                response = f"I can help you with these topics:\n\n"
                for topic in topics:
                    response += f"• {topic.capitalize()}\n"
                response += f"\nWhat would you like to know about Netra?"
                
                return {
                    'response': response,
                    'suggestions': [
                        "How do I create an account?",
                        "How do payments work?",
                        "How do I contact support?"
                    ],
                    'confidence': 80,
                    'engine_used': 'netra_engine',
                    'help_center_url': self.help_center_url,
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"❌ Error: {e}")
            return {
                'response': "I'm here to help with Netra! You can ask me about:\n\n• Creating an account\n• Making payments\n• Managing settings\n• Contacting support",
                'suggestions': [
                    "How do I create an account?",
                    "How do payments work?",
                    "How do I contact support?"
                ],
                'confidence': 70,
                'engine_used': 'netra_engine',
                'help_center_url': self.help_center_url,
                'timestamp': datetime.now().isoformat()
            }

# Create the instance
netra_engine = HumanizedNetraEngine()