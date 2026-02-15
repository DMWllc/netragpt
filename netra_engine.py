"""
Netra Engine - Enhanced Dynamic Web Crawler
Searches netra.strobid.com for relevant pages and extracts meaningful content
"""

import requests
import re
import time
from typing import Dict, List, Optional, Any, Set
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from collections import Counter
import heapq

class HumanizedNetraEngine:
    """
    Netra AI Assistant that dynamically crawls the website for information
    """
    
    def __init__(self):
        self.base_url = "https://netra.strobid.com"
        self.all_pages = {}  # Cache of discovered pages
        self.crawled_urls: Set[str] = set()
        self.url_queue: List[str] = []
        self.last_crawl = None
        
        # Page type patterns
        self.page_patterns = {
            'account': ['account', 'profile', 'login', 'signup', 'register', 'create'],
            'payment': ['payment', 'pay', 'billing', 'subscription', 'invoice'],
            'booking': ['book', 'booking', 'schedule', 'appointment', 'reserve', 'hire'],
            'rating': ['rate', 'rating', 'review', 'feedback', 'testimonial'],
            'service': ['service', 'provider', 'professional', 'category'],
            'support': ['support', 'help', 'contact', 'faq', 'assist']
        }
        
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
    
    def _extract_links(self, soup: BeautifulSoup, current_url: str) -> List[str]:
        """Extract all internal links from a page"""
        links = []
        
        for link in soup.find_all('a', href=True):
            href = link['href'].strip()
            
            # Skip empty, anchors, and external links
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue
            
            # Make absolute URL
            if href.startswith('/'):
                full_url = urljoin(self.base_url, href)
            elif href.startswith('http'):
                # Only include netra.strobid.com links
                if 'netra.strobid.com' in href:
                    full_url = href
                else:
                    continue
            else:
                full_url = urljoin(current_url, href)
            
            # Remove fragments
            full_url = full_url.split('#')[0]
            
            # Remove query parameters
            full_url = full_url.split('?')[0]
            
            links.append(full_url)
        
        return list(set(links))  # Remove duplicates
    
    def _crawl_site(self, max_pages: int = 50):
        """Crawl the entire site to discover all pages"""
        print("\n🔍 CRAWLING NETRA.STROBID.COM")
        print("=" * 60)
        
        self.url_queue = [self.base_url]
        self.crawled_urls = set()
        self.all_pages = {}
        
        pages_crawled = 0
        
        while self.url_queue and pages_crawled < max_pages:
            url = self.url_queue.pop(0)
            if url in self.crawled_urls:
                continue
            
            print(f"\n📄 Crawling: {url}")
            soup = self._fetch_page(url)
            
            if soup:
                # Extract page information
                page_info = self._extract_page_info(soup, url)
                self.all_pages[url] = page_info
                
                # Find new links to crawl
                new_links = self._extract_links(soup, url)
                for link in new_links:
                    if link not in self.crawled_urls and link not in self.url_queue:
                        self.url_queue.append(link)
                
                pages_crawled += 1
                print(f"  ✅ Title: {page_info['title']}")
                print(f"  📝 Type: {page_info['page_type']}")
                print(f"  🔑 Keywords: {', '.join(page_info['keywords'][:5])}")
            
            self.crawled_urls.add(url)
            time.sleep(0.5)  # Be nice to the server
        
        self.last_crawl = datetime.now()
        
        print(f"\n✅ Crawled {len(self.all_pages)} pages")
        self._print_crawl_summary()
    
    def _extract_page_info(self, soup: BeautifulSoup, url: str) -> Dict:
        """Extract all relevant information from a page"""
        # Get title
        title_tag = soup.find('title')
        title = title_tag.get_text().strip() if title_tag else url.split('/')[-1]
        
        # Get meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        description = meta_desc.get('content', '') if meta_desc else ''
        
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
            element.decompose()
        
        # Find main content
        main = None
        for selector in ['main', 'article', '.content', '#content', '.main-content', 'body']:
            main = soup.select_one(selector)
            if main:
                break
        
        if not main:
            main = soup.body
        
        # Extract headers
        headers = []
        for h in main.find_all(['h1', 'h2', 'h3']):
            text = h.get_text().strip()
            if text:
                headers.append(text)
        
        # Extract paragraphs
        paragraphs = []
        for p in main.find_all('p'):
            text = p.get_text().strip()
            if text and len(text) > 30:
                paragraphs.append(text)
        
        # Extract lists (often contain steps)
        lists = []
        for ul in main.find_all(['ul', 'ol']):
            items = []
            for li in ul.find_all('li'):
                text = li.get_text().strip()
                if text:
                    items.append(text)
            if items:
                lists.append(items)
        
        # Extract buttons/actions
        buttons = []
        for btn in main.find_all(['button', 'a'], class_=re.compile(r'btn|button|action')):
            text = btn.get_text().strip()
            if text:
                buttons.append(text)
        
        # Combine all text for keyword extraction
        all_text = title + ' ' + description + ' ' + ' '.join(headers) + ' ' + ' '.join(paragraphs)
        
        # Extract keywords
        keywords = self._extract_keywords(all_text)
        
        # Determine page type
        page_type = self._determine_page_type(url, title, headers, keywords)
        
        return {
            'url': url,
            'title': title,
            'description': description,
            'headers': headers,
            'paragraphs': paragraphs,
            'lists': lists,
            'buttons': buttons,
            'keywords': keywords,
            'page_type': page_type,
            'full_text': all_text
        }
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Clean text
        text = text.lower()
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Split into words
        words = text.split()
        
        # Filter out common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'this', 'that', 'these', 'those', 'from', 'have', 'are', 'was', 'were', 'will', 'can', 'could', 'would', 'should', 'their', 'there', 'about', 'page', 'website', 'click', 'here'}
        
        filtered_words = [w for w in words if len(w) > 3 and w not in stop_words]
        
        # Count frequencies
        word_counts = Counter(filtered_words)
        
        # Return top keywords
        return [word for word, count in word_counts.most_common(15)]
    
    def _determine_page_type(self, url: str, title: str, headers: List[str], keywords: List[str]) -> str:
        """Determine the type of page based on its content"""
        text = (url + ' ' + title + ' ' + ' '.join(headers) + ' ' + ' '.join(keywords)).lower()
        
        scores = {}
        for page_type, patterns in self.page_patterns.items():
            score = 0
            for pattern in patterns:
                if pattern in text:
                    score += 1
                # Check URL specifically
                if pattern in url.lower():
                    score += 2
            scores[page_type] = score
        
        # Get the page type with highest score
        if scores:
            best_type = max(scores, key=scores.get)
            if scores[best_type] > 0:
                return best_type
        
        return 'general'
    
    def _calculate_relevance(self, query: str, page: Dict) -> float:
        """Calculate how relevant a page is to the query"""
        query_lower = query.lower()
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        score = 0.0
        
        # Check URL (highest priority)
        url_lower = page['url'].lower()
        for word in query_words:
            if len(word) > 3 and word in url_lower:
                score += 15.0
        
        # Check page type match
        if page['page_type'] in query_lower:
            score += 12.0
        
        # Check title
        title_lower = page['title'].lower()
        for word in query_words:
            if word in title_lower:
                score += 10.0
        
        # Check headers
        for header in page['headers']:
            header_lower = header.lower()
            # Exact phrase match in headers
            if query_lower in header_lower:
                score += 20.0
            for word in query_words:
                if word in header_lower:
                    score += 5.0
        
        # Check description
        if page['description']:
            desc_lower = page['description'].lower()
            if query_lower in desc_lower:
                score += 15.0
        
        # Check keywords
        for keyword in page['keywords']:
            if keyword in query_lower:
                score += 8.0
        
        # Check paragraphs (partial matches)
        for para in page['paragraphs']:
            para_lower = para.lower()
            if query_lower in para_lower:
                score += 25.0
            else:
                for word in query_words:
                    if len(word) > 3 and word in para_lower:
                        score += 2.0
        
        # Check lists (often contain step-by-step instructions)
        for lst in page['lists']:
            for item in lst:
                item_lower = item.lower()
                if query_lower in item_lower:
                    score += 30.0
        
        return score
    
    def _extract_answer(self, page: Dict, query: str) -> str:
        """Extract the most relevant answer from a page"""
        query_lower = query.lower()
        answer_parts = []
        
        # Add title
        answer_parts.append(f"**{page['title']}**")
        answer_parts.append('')
        
        # Look for lists first (often contain steps)
        best_list = None
        best_list_score = 0
        
        for lst in page['lists']:
            list_text = ' '.join(lst).lower()
            score = 0
            for word in query_lower.split():
                if word in list_text:
                    score += 1
            if score > best_list_score:
                best_list_score = score
                best_list = lst
        
        if best_list and best_list_score > 2:
            answer_parts.extend(best_list)
            answer_parts.append('')
        
        # Look for relevant paragraphs
        relevant_paras = []
        for para in page['paragraphs']:
            para_lower = para.lower()
            if query_lower in para_lower or any(word in para_lower for word in query_lower.split()):
                relevant_paras.append(para)
        
        if relevant_paras:
            answer_parts.extend(relevant_paras[:2])
        elif page['description']:
            answer_parts.append(page['description'])
        
        # If still no content, show headers
        if len(answer_parts) < 3 and page['headers']:
            answer_parts.append("Here's what I found:")
            answer_parts.extend(page['headers'][:3])
        
        return '\n'.join(answer_parts)
    
    def _is_link_request(self, query: str) -> bool:
        """Check if user is asking for a link"""
        query_lower = query.lower()
        link_keywords = ['link', 'url', 'website', 'page', 'take me to', 'direct me to', 'go to']
        return any(keyword in query_lower for keyword in link_keywords)
    
    def _get_follow_up_suggestions(self, page: Dict, query: str) -> List[str]:
        """Generate relevant follow-up suggestions"""
        suggestions = []
        
        # Suggestions based on page type
        if page['page_type'] == 'booking':
            suggestions = [
                "How do I cancel a booking?",
                "Can I reschedule a booking?",
                "How do payments work?",
                "How do I rate a provider?"
            ]
        elif page['page_type'] == 'rating':
            suggestions = [
                "How do I leave a review?",
                "Can I edit my review?",
                "How do ratings work?",
                "What if I had a bad experience?"
            ]
        elif page['page_type'] == 'account':
            suggestions = [
                "How do I verify my account?",
                "How do I reset my password?",
                "How do I delete my account?",
                "How do I update my profile?"
            ]
        elif page['page_type'] == 'payment':
            suggestions = [
                "What payment methods are accepted?",
                "How do I get a refund?",
                "Are there any fees?",
                "How do subscriptions work?"
            ]
        else:
            suggestions = [
                "What is Netra?",
                "How do I create an account?",
                "How do bookings work?",
                "How do I contact support?"
            ]
        
        return suggestions[:4]
    
    def _print_crawl_summary(self):
        """Print summary of crawled pages"""
        print("\n📊 PAGE SUMMARY BY TYPE")
        type_counts = {}
        for page in self.all_pages.values():
            page_type = page['page_type']
            type_counts[page_type] = type_counts.get(page_type, 0) + 1
        
        for page_type, count in type_counts.items():
            print(f"  • {page_type.capitalize()}: {count} pages")
    
    def process_query(self, message: str, user_id: str = None) -> Dict[str, Any]:
        """Process user query by searching crawled pages"""
        try:
            print(f"\n🤔 Processing: {message}")
            
            # Handle greetings
            greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon']
            if any(g in message.lower() for g in greetings):
                return {
                    'response': "Hello! I'm your Netra assistant. I can help you with accounts, bookings, payments, ratings, and more. What would you like to know?",
                    'suggestions': [
                        "Tell me about Netra",
                        "How do I create an account?",
                        "How do bookings work?",
                        "How do ratings work?"
                    ],
                    'confidence': 100,
                    'engine_used': 'netra_engine',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Handle thanks
            thanks = ['thanks', 'thank you', 'appreciate it']
            if any(t in message.lower() for t in thanks):
                return {
                    'response': "You're welcome! 😊 Is there anything else you'd like to know about Netra?",
                    'suggestions': [
                        "Tell me about Netra",
                        "How do I create an account?",
                        "How do bookings work?",
                        "How do I contact support?"
                    ],
                    'confidence': 100,
                    'engine_used': 'netra_engine',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Check if this is a link request
            if self._is_link_request(message):
                # Find best matching page
                best_page = None
                best_score = 0
                
                for page in self.all_pages.values():
                    score = self._calculate_relevance(message, page)
                    if score > best_score:
                        best_score = score
                        best_page = page
                
                if best_page and best_score > 10:
                    return {
                        'response': f"Here's the page you're looking for:\n\n🔗 {best_page['url']}",
                        'suggestions': self._get_follow_up_suggestions(best_page, message),
                        'confidence': 90,
                        'engine_used': 'netra_engine',
                        'timestamp': datetime.now().isoformat()
                    }
            
            # Find relevant pages for the query
            relevant_pages = []
            for page in self.all_pages.values():
                score = self._calculate_relevance(message, page)
                if score > 5:
                    relevant_pages.append((score, page))
            
            # Sort by score
            relevant_pages.sort(key=lambda x: x[0], reverse=True)
            
            if relevant_pages:
                best_score, best_page = relevant_pages[0]
                print(f"✅ Best match: {best_page['title']} (score: {best_score:.1f})")
                
                # Extract answer
                answer = self._extract_answer(best_page, message)
                
                # Get suggestions
                suggestions = self._get_follow_up_suggestions(best_page, message)
                
                return {
                    'response': answer,
                    'suggestions': suggestions,
                    'confidence': min(95, int(best_score)),
                    'engine_used': 'netra_engine',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # No relevant pages found
                return {
                    'response': "I couldn't find specific information about that. Here are some topics I can help with:\n\n• What is Netra?\n• Creating an account\n• Making payments\n• Booking services\n• Ratings and reviews\n• Contacting support",
                    'suggestions': [
                        "What is Netra?",
                        "How do I create an account?",
                        "How do bookings work?",
                        "How do I contact support?"
                    ],
                    'confidence': 70,
                    'engine_used': 'netra_engine',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'response': "I'm here to help with Netra! You can ask me about accounts, bookings, payments, ratings, and more. What would you like to know?",
                'suggestions': [
                    "What is Netra?",
                    "How do I create an account?",
                    "How do bookings work?",
                    "How do I contact support?"
                ],
                'confidence': 60,
                'engine_used': 'netra_engine',
                'timestamp': datetime.now().isoformat()
            }

# Create the instance
netra_engine = HumanizedNetraEngine()