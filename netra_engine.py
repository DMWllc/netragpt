"""
Netra Engine - Dynamic Web Crawler
Searches netra.strobid.com for relevant pages in real-time
"""

import requests
import re
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import concurrent.futures
from difflib import SequenceMatcher

class HumanizedNetraEngine:
    """
    Netra AI Assistant that dynamically crawls the website for information
    """
    
    def __init__(self):
        self.base_url = "https://netra.strobid.com"
        self.all_pages = {}  # Cache of discovered pages
        self.crawled_urls = set()
        self.last_crawl = None
        
        # Start with known pages
        self._discover_pages()
    
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
        parsed_base = urlparse(self.base_url)
        
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
            
            # Only keep .php and .html pages
            if any(ext in full_url for ext in ['.php', '.html', '/']):
                links.append(full_url)
        
        return list(set(links))  # Remove duplicates
    
    def _discover_pages(self, max_pages: int = 50):
        """Discover all pages on the site by crawling"""
        print("\n🔍 DISCOVERING PAGES ON NETRA.STROBID.COM")
        print("=" * 60)
        
        to_crawl = [self.base_url]
        crawled = set()
        pages = {}
        
        while to_crawl and len(crawled) < max_pages:
            url = to_crawl.pop(0)
            if url in crawled:
                continue
            
            print(f"📄 Crawling: {url}")
            soup = self._fetch_page(url)
            
            if soup:
                # Store page info
                title = soup.find('title')
                title_text = title.get_text() if title else url.split('/')[-1]
                
                # Get main content
                content = self._extract_content(soup)
                
                pages[url] = {
                    'url': url,
                    'title': title_text,
                    'content': content,
                    'keywords': self._extract_keywords(content),
                    'headers': self._extract_headers(soup)
                }
                
                # Find new links
                new_links = self._extract_links(soup, url)
                for link in new_links:
                    if link not in crawled and link not in to_crawl:
                        to_crawl.append(link)
                
                crawled.add(url)
                time.sleep(0.5)  # Be nice to the server
        
        self.all_pages = pages
        self.crawled_urls = crawled
        self.last_crawl = datetime.now()
        
        print(f"\n✅ Discovered {len(pages)} pages")
        for url, page in pages.items():
            print(f"  • {page['title']} - {url}")
        print("=" * 60)
    
    def _extract_content(self, soup: BeautifulSoup) -> str:
        """Extract main content from a page"""
        # Remove unwanted elements
        for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()
        
        # Find main content area
        main = None
        for selector in ['main', 'article', '.content', '#content', 'body']:
            main = soup.select_one(selector)
            if main:
                break
        
        if not main:
            main = soup.body
        
        if main:
            # Get text and clean it
            text = main.get_text(separator='\n', strip=True)
            lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 30]
            return '\n'.join(lines)
        
        return ""
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important keywords from text"""
        # Simple keyword extraction (can be improved)
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        stop_words = {'this', 'that', 'with', 'from', 'have', 'were', 'they', 'will', 'their', 'what', 'about', 'there', 'page', 'would', 'could', 'should'}
        keywords = [w for w in words if w not in stop_words]
        
        # Count frequency
        from collections import Counter
        keyword_counts = Counter(keywords)
        
        # Return top keywords
        return [word for word, count in keyword_counts.most_common(20)]
    
    def _extract_headers(self, soup: BeautifulSoup) -> List[str]:
        """Extract headers from page"""
        headers = []
        for h in soup.find_all(['h1', 'h2', 'h3']):
            text = h.get_text().strip()
            if text:
                headers.append(text)
        return headers
    
    def _calculate_relevance(self, query: str, page: Dict) -> float:
        """Calculate how relevant a page is to the query"""
        query_lower = query.lower()
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        score = 0.0
        
        # Check URL for keywords
        url_lower = page['url'].lower()
        for word in query_words:
            if word in url_lower:
                score += 10.0
        
        # Check title
        title_lower = page['title'].lower()
        for word in query_words:
            if word in title_lower:
                score += 8.0
        
        # Check headers
        for header in page['headers']:
            header_lower = header.lower()
            for word in query_words:
                if word in header_lower:
                    score += 5.0
            
            # Check for exact phrase match
            if query_lower in header_lower:
                score += 15.0
        
        # Check content
        content_lower = page['content'].lower()
        for word in query_words:
            if len(word) > 3:
                count = content_lower.count(word)
                score += count * 0.5
        
        # Check for exact phrase in content
        if query_lower in content_lower:
            score += 20.0
        
        # Check keywords
        for keyword in page['keywords']:
            if keyword in query_lower:
                score += 3.0
        
        return score
    
    def _find_relevant_pages(self, query: str) -> List[Dict]:
        """Find pages relevant to the query"""
        results = []
        
        for url, page in self.all_pages.items():
            score = self._calculate_relevance(query, page)
            if score > 5.0:  # Minimum relevance threshold
                results.append({
                    'url': url,
                    'title': page['title'],
                    'content': page['content'],
                    'score': score,
                    'headers': page['headers']
                })
        
        # Sort by relevance score
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def _extract_answer(self, page: Dict, query: str) -> str:
        """Extract the most relevant answer from a page"""
        content = page['content']
        query_lower = query.lower()
        
        # Split into paragraphs
        paragraphs = content.split('\n')
        
        # Find most relevant paragraph
        best_para = None
        best_score = 0
        
        for para in paragraphs:
            if len(para) < 50:  # Skip very short paragraphs
                continue
            
            para_lower = para.lower()
            score = 0
            
            # Check for query words
            for word in query_lower.split():
                if word in para_lower:
                    score += 1
            
            # Bonus for paragraphs with steps (numbers or bullets)
            if re.search(r'\d+\.|•|\*', para):
                score += 5
            
            if score > best_score:
                best_score = score
                best_para = para
        
        # Format the answer
        answer_parts = []
        
        # Add title
        answer_parts.append(f"**{page['title']}**")
        answer_parts.append('')
        
        # Add best paragraph or first few paragraphs
        if best_para and best_score > 2:
            answer_parts.append(best_para)
        else:
            # Show first few paragraphs
            for para in paragraphs[:3]:
                if len(para) > 50:
                    answer_parts.append(para)
        
        return '\n'.join(answer_parts)
    
    def _is_link_request(self, query: str) -> bool:
        """Check if user is asking for a link"""
        query_lower = query.lower()
        link_keywords = ['link', 'url', 'website', 'page', 'take me to', 'direct me to']
        return any(keyword in query_lower for keyword in link_keywords)
    
    def _get_page_url_for_query(self, query: str) -> Optional[str]:
        """Find the most relevant page URL for a query"""
        results = self._find_relevant_pages(query)
        if results:
            return results[0]['url']
        return None
    
    def process_query(self, message: str, user_id: str = None) -> Dict[str, Any]:
        """Process user query by searching the website"""
        try:
            print(f"\n🤔 Processing: {message}")
            
            # Handle greetings
            greetings = ['hi', 'hello', 'hey', 'good morning']
            if any(g in message.lower() for g in greetings):
                return {
                    'response': "Hello! I'm your Netra assistant. I can search the website for information about accounts, payments, bookings, ratings, and more. What would you like to know?",
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
            
            # Check if this is a link request
            if self._is_link_request(message):
                url = self._get_page_url_for_query(message)
                if url:
                    return {
                        'response': f"Here's the page you're looking for:\n\n🔗 {url}",
                        'suggestions': [
                            "Tell me more about this",
                            "What else can you help with?",
                            "How do I create an account?"
                        ],
                        'confidence': 90,
                        'engine_used': 'netra_engine',
                        'timestamp': datetime.now().isoformat()
                    }
            
            # Find relevant pages
            relevant_pages = self._find_relevant_pages(message)
            
            if relevant_pages:
                best_page = relevant_pages[0]
                print(f"✅ Best match: {best_page['title']} (score: {best_page['score']})")
                
                # Extract answer from the page
                answer = self._extract_answer(best_page, message)
                
                # Get related topics for suggestions
                suggestions = []
                for page in relevant_pages[1:4]:
                    title = page['title']
                    if len(title) > 30:
                        title = title[:30] + "..."
                    suggestions.append(f"Tell me about {title}")
                
                return {
                    'response': answer,
                    'suggestions': suggestions[:4],
                    'confidence': min(95, int(best_page['score'])),
                    'engine_used': 'netra_engine',
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # No relevant pages found
                return {
                    'response': "I couldn't find specific information about that on the website. Here are some topics I can help with:\n\n• What is Netra?\n• Creating an account\n• Making payments\n• Booking services\n• Ratings and reviews\n• Contacting support",
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
            return {
                'response': "I'm here to help with Netra! You can ask me about accounts, payments, bookings, ratings, and more. What would you like to know?",
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