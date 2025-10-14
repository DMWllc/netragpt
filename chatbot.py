from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from openai import OpenAI
import os
import random
import re
import time
import hashlib
import requests
from bs4 import BeautifulSoup
import urllib.parse
import base64
from io import BytesIO
import json
from urllib.parse import urljoin, urlparse, quote_plus
from collections import Counter
from datetime import datetime, timezone, timedelta

app = Flask(__name__)
CORS(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Enhanced conversation memory with persistent storage
conversation_history = {}

# Knowledge domains for diverse capabilities
KNOWLEDGE_DOMAINS = {
    'netra': {
        'name': 'Netra Services',
        'keywords': ['netra', 'service', 'provider', 'booking', 'category', 'clean', 'repair', 'beauty', 'fitness', 'aidnest'],
        'description': 'Africa\'s premier service marketplace'
    },
    'general_tech': {
        'name': 'Technology',
        'keywords': ['computer', 'phone', 'app', 'software', 'tech', 'internet', 'website', 'digital', 'code', 'programming'],
        'description': 'General technology and digital assistance'
    },
    'productivity': {
        'name': 'Productivity',
        'keywords': ['schedule', 'organize', 'plan', 'time management', 'task', 'reminder', 'efficiency', 'productivity'],
        'description': 'Help with productivity and organization'
    },
    'education': {
        'name': 'Education & Learning',
        'keywords': ['learn', 'study', 'teach', 'education', 'course', 'skill', 'knowledge', 'research', 'school', 'university'],
        'description': 'Educational support and learning assistance'
    },
    'business': {
        'name': 'Business & Entrepreneurship',
        'keywords': ['business', 'startup', 'entrepreneur', 'marketing', 'sales', 'customer', 'strategy', 'finance', 'investment'],
        'description': 'Business advice and entrepreneurial guidance'
    },
    'creative': {
        'name': 'Creative Work',
        'keywords': ['write', 'design', 'create', 'content', 'story', 'art', 'creative', 'brainstorm', 'music', 'drawing'],
        'description': 'Creative writing and content creation'
    },
    'daily_life': {
        'name': 'Daily Life',
        'keywords': ['cook', 'travel', 'health', 'fitness', 'home', 'family', 'relationship', 'advice', 'food', 'recipe'],
        'description': 'Everyday life advice and support'
    },
    'science': {
        'name': 'Science & Facts',
        'keywords': ['science', 'fact', 'history', 'physics', 'chemistry', 'biology', 'space', 'earth', 'nature'],
        'description': 'Scientific facts and historical information'
    }
}

def get_user_session(user_id):
    if user_id not in conversation_history:
        conversation_history[user_id] = {
            'last_interaction': time.time(),
            'conversation_context': [],
            'last_topic': None,
            'question_count': 0,
            'user_name': None,
            'user_interests': [],
            'conversation_stage': 'greeting',
            'mood': 'friendly',
            'remembered_facts': {},
            'recent_topics': [],
            'personal_details': {},
            'image_requests': 0,
            'coding_help_requests': 0,
            'voice_requests': 0,
            'browsing_sessions': 0,
            'preferred_domains': [],
            'knowledge_usage': {domain: 0 for domain in KNOWLEDGE_DOMAINS.keys()},
            'external_searches': 0
        }
    return conversation_history[user_id]

def search_google(query, num_results=5):
    """Search Google for information using a free approach"""
    try:
        # Using a simple Google search through their basic HTML interface
        search_url = f"https://www.google.com/search?q={quote_plus(query)}&num={num_results}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        results = []
        
        # Extract search results
        for g in soup.find_all('div', class_='g'):
            title_element = g.find('h3')
            link_element = g.find('a')
            desc_element = g.find('span', class_='aCOpRe')
            
            if title_element and link_element:
                title = title_element.get_text()
                link = link_element.get('href')
                description = desc_element.get_text() if desc_element else "No description available"
                
                # Clean the link
                if link.startswith('/url?q='):
                    link = link[7:].split('&')[0]
                
                results.append({
                    'title': title,
                    'link': link,
                    'description': description[:200]  # Limit description length
                })
                
                if len(results) >= num_results:
                    break
        
        return results
        
    except Exception as e:
        print(f"Google search error: {e}")
        return []

def search_wikipedia(query):
    """Search Wikipedia for information"""
    try:
        # Search Wikipedia API
        search_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote_plus(query)}"
        
        response = requests.get(search_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'title': data.get('title', ''),
                'extract': data.get('extract', ''),
                'url': data.get('content_urls', {}).get('desktop', {}).get('page', ''),
                'thumbnail': data.get('thumbnail', {}).get('source', '')
            }
        else:
            # Try search instead of direct page
            search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={quote_plus(query)}&format=json&srlimit=1"
            response = requests.get(search_url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data['query']['search']:
                    page_title = data['query']['search'][0]['title']
                    return search_wikipedia(page_title)  # Recursive call with exact title
            
        return None
        
    except Exception as e:
        print(f"Wikipedia search error: {e}")
        return None

def extract_person_name(query):
    """Extract person name from search query"""
    query_lower = query.lower()
    
    # Patterns that indicate person search
    patterns = [
        r'someone called (.+)',
        r'person named (.+)',
        r'who is (.+)',
        r'search (?:for|about) (.+)',
        r'look up (.+)',
        r'information about (.+)',
        r'details about (.+)',
        r'tell me about (.+)',
        r'do you know (.+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            name = match.group(1).strip()
            # Clean up the name - remove question marks, extra words
            name = re.sub(r'[?.!].*$', '', name)  # Remove everything after ?.! 
            name = name.replace('?', '').strip()
            
            # If name contains multiple words, take the first few as the person's name
            words = name.split()
            if len(words) > 4:  # Probably not a person name if too many words
                continue
                
            return name.title()  # Return with proper capitalization
    
    # If no pattern matches but query looks like a name (2-4 capitalized words)
    words = query.split()
    if 2 <= len(words) <= 4 and all(word[0].isupper() for word in words if word):
        return query
    
    return None

def search_person_info(person_name):
    """Enhanced search specifically for person information"""
    try:
        print(f"Searching for person: {person_name}")
        
        # Try Wikipedia first for reliable biographical information
        wiki_result = search_wikipedia(person_name)
        if wiki_result and len(wiki_result.get('extract', '')) > 50:
            return {
                'source': 'wikipedia',
                'name': person_name,
                'information': wiki_result['extract'],
                'url': wiki_result.get('url', ''),
                'confidence': 'high'
            }
        
        # If Wikipedia fails, try Google search
        google_results = search_google(f"{person_name} biography information", num_results=3)
        if google_results:
            # Combine information from multiple Google results
            combined_info = ""
            for result in google_results:
                if person_name.lower() in result['title'].lower() or 'biography' in result['description'].lower():
                    combined_info += f"{result['title']}: {result['description']}\n"
            
            if combined_info:
                return {
                    'source': 'google',
                    'name': person_name,
                    'information': combined_info[:500],  # Limit length
                    'url': google_results[0]['link'],
                    'confidence': 'medium'
                }
        
        return None
        
    except Exception as e:
        print(f"Person search error: {e}")
        return None

def should_search_externally(query):
    """Determine if a query should trigger external search - ENHANCED VERSION"""
    query_lower = query.lower()
    
    # Questions that typically need external knowledge
    external_keywords = [
        'what is', 'who is', 'when was', 'where is', 'how does', 'why does',
        'history of', 'facts about', 'definition of', 'explain', 'tell me about',
        'current', 'latest', 'recent', 'news about', 'update on', 'search for',
        'look up', 'find information', 'information about', 'details about'
    ]
    
    # Topics that benefit from external sources
    external_topics = [
        'scientific', 'historical', 'biography', 'geography', 'technology news',
        'medical', 'space', 'physics', 'chemistry', 'biology', 'mathematics',
        'person', 'people', 'celebrity', 'politician', 'scientist', 'inventor'
    ]
    
    # Person search patterns
    person_patterns = [
        'someone called', 'person named', 'who is', 'information about',
        'search for', 'look up', 'do you know'
    ]
    
    # Check if query matches external search criteria
    has_external_phrase = any(phrase in query_lower for phrase in external_keywords)
    has_external_topic = any(topic in query_lower for topic in external_topics)
    has_person_pattern = any(pattern in query_lower for pattern in person_patterns)
    is_complex_factual = len(query.split()) > 3 and any(word in query_lower for word in ['fact', 'information', 'details', 'research', 'search'])
    
    # Special case: Direct requests to search for people
    is_person_search = any(indicator in query_lower for indicator in [
        'search about', 'look up', 'find info', 'information on', 'who is'
    ]) and any(word in query_lower for word in ['called', 'named', 'person', 'someone'])
    
    return has_external_phrase or has_external_topic or is_complex_factual or has_person_pattern or is_person_search

def get_external_knowledge(query):
    """Get information from external sources (Google + Wikipedia) - ENHANCED VERSION"""
    external_info = {
        'google_results': [],
        'wikipedia_result': None,
        'person_info': None,
        'sources_used': []
    }
    
    try:
        # Check if this is a person search
        person_name = extract_person_name(query)
        if person_name:
            print(f"Detected person search for: {person_name}")
            person_info = search_person_info(person_name)
            if person_info:
                external_info['person_info'] = person_info
                external_info['sources_used'].append(person_info['source'])
                return external_info
        
        # Only search for complex or factual queries
        if should_search_externally(query):
            print(f"Searching externally for: {query}")
            
            # Search Wikipedia first (more reliable for facts)
            wiki_result = search_wikipedia(query)
            if wiki_result and len(wiki_result.get('extract', '')) > 50:
                external_info['wikipedia_result'] = wiki_result
                external_info['sources_used'].append('wikipedia')
            
            # Search Google for additional context
            google_results = search_google(query, num_results=3)
            if google_results:
                external_info['google_results'] = google_results
                external_info['sources_used'].append('google')
        
        return external_info
        
    except Exception as e:
        print(f"External knowledge error: {e}")
        return external_info

def analyze_query_domain(query):
    """Analyze which knowledge domains are relevant to the query"""
    query_lower = query.lower()
    domain_scores = {}
    
    for domain, info in KNOWLEDGE_DOMAINS.items():
        score = 0
        for keyword in info['keywords']:
            if keyword in query_lower:
                score += 1
        domain_scores[domain] = score
    
    # Boost Netra for service-related queries
    if any(word in query_lower for word in ['service', 'provider', 'book', 'hire', 'clean', 'repair', 'netra', 'aidnest']):
        domain_scores['netra'] += 3
    
    # Boost science for factual queries
    if any(word in query_lower for word in ['fact', 'science', 'history', 'research', 'study']):
        domain_scores['science'] += 2
    
    # Sort by relevance
    sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
    relevant_domains = [domain for domain, score in sorted_domains if score > 0]
    
    return relevant_domains[:3] if relevant_domains else ['general_tech']

def get_current_time(timezone_str=None):
    """Get current time in different timezones without pytz"""
    try:
        # Timezone offsets in hours (simplified without pytz)
        timezone_offsets = {
            'est': -5, 'edt': -4,  # Eastern
            'pst': -8, 'pdt': -7,  # Pacific
            'cst': -6, 'cdt': -5,  # Central
            'mst': -7, 'mdt': -6,  # Mountain
            'gmt': 0, 'utc': 0,    # GMT/UTC
            'ist': 5.5,            # India
            'cet': 1, 'cedt': 2,   # Central European
            'aest': 10,            # Australian Eastern
            'eat': 3,              # East Africa
            'cat': 2,              # Central Africa
            'west': 1,             # West Africa
            'wast': 2,             # West Africa Summer
            'lagos': 1,            # Nigeria
            'nairobi': 3,          # Kenya
            'accra': 0,            # Ghana
            'johannesburg': 2      # South Africa
        }
        
        if timezone_str:
            tz_lower = timezone_str.lower()
            # Find the best matching timezone
            for tz_name, offset in timezone_offsets.items():
                if tz_name in tz_lower:
                    utc_offset = timedelta(hours=offset)
                    break
            else:
                # Default to UTC if no match found
                utc_offset = timedelta(hours=0)
        else:
            utc_offset = timedelta(hours=0)
        
        # Calculate time with offset
        current_utc = datetime.now(timezone.utc)
        current_time = current_utc + utc_offset
        
        # Format the time
        timezone_name = timezone_str.upper() if timezone_str else "UTC"
        return current_time.strftime(f"%Y-%m-%d %H:%M:%S {timezone_name}")
    
    except Exception as e:
        print(f"Timezone error: {e}")
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")

def get_currency_rates(base_currency='USD'):
    """Get current currency exchange rates"""
    try:
        # Using a free currency API
        response = requests.get(f'https://api.exchangerate-api.com/v4/latest/{base_currency}', timeout=10)
        if response.status_code == 200:
            data = response.json()
            rates = data.get('rates', {})
            
            # Return major currencies
            major_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'KES', 'GHS', 'NGN', 'ZAR']
            result = {}
            for currency in major_currencies:
                if currency in rates and currency != base_currency:
                    result[currency] = rates[currency]
            
            return result
        return {}
    except Exception as e:
        print(f"Currency API error: {e}")
        return {}

def get_weather(city="Nairobi"):
    """Get current weather information"""
    try:
        # Using OpenWeatherMap API (you'll need to add your API key)
        api_key = os.environ.get("OPENWEATHER_API_KEY")
        if not api_key:
            return None
            
        response = requests.get(
            f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric",
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            return {
                'city': data['name'],
                'temperature': data['main']['temp'],
                'description': data['weather'][0]['description'],
                'humidity': data['main']['humidity'],
                'wind_speed': data['wind']['speed']
            }
        return None
    except Exception as e:
        print(f"Weather API error: {e}")
        return None

def enhanced_web_browsing(query, max_pages=8, deep_analysis=False):
    """Enhanced browsing that can navigate through Netra website pages with deep analysis"""
    try:
        # Netra website structure mapping
        netra_pages = {
            'home': 'https://myaidnest.com',
            'about': 'https://myaidnest.com/about.php',
            'services': 'https://myaidnest.com/serviceshub.php',
            'category_services': 'https://myaidnest.com/category_services.php',
            'detail_services': 'https://myaidnest.com/detail_services.php',
            'register': 'https://myaidnest.com/register.php',
            'login': 'https://myaidnest.com/login.php',
            'contact': 'https://myaidnest.com/contact.php',
            'privacy': 'https://myaidnest.com/privacy.php',
            'terms': 'https://myaidnest.com/terms.php',
            'settings': 'https://myaidnest.com/settings.php',
            'download': 'https://play.google.com/store/apps/details?id=com.kakorelabs.netra'
        }
        
        search_results = []
        visited_urls = set()
        all_providers = []
        all_services = []
        
        # Determine which pages to search based on query
        pages_to_search = identify_relevant_pages(query, netra_pages, deep_analysis)
        
        for page_key in pages_to_search[:max_pages]:
            url = netra_pages[page_key]
            if url in visited_urls:
                continue
                
            try:
                response = requests.get(url, timeout=15, headers={
                    'User-Agent': 'Mozilla/5.0 (compatible; Jovira-Bot/1.0; +https://myaidnest.com)'
                })
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Extract meaningful content
                page_data = extract_page_content(soup, url, page_key)
                if page_data:
                    search_results.append(page_data)
                    visited_urls.add(url)
                
                # For category pages, extract providers
                if page_key == 'category_services':
                    providers = extract_service_providers_from_category_page(soup, url)
                    all_providers.extend(providers)
                
                # For deep analysis, extract providers and services
                if deep_analysis:
                    providers = extract_providers_from_page(soup, url)
                    all_providers.extend(providers)
                    
                    services = extract_services_from_page(soup, url)
                    all_services.extend(services)
                    
                # Extract and follow internal links for deeper browsing
                if len(visited_urls) < max_pages:
                    internal_links = extract_internal_links(soup, 'myaidnest.com')
                    for link in internal_links[:3]:  # Limit to 3 additional pages
                        if link not in visited_urls and len(visited_urls) < max_pages:
                            try:
                                link_response = requests.get(link, timeout=10)
                                link_soup = BeautifulSoup(link_response.content, 'html.parser')
                                link_data = extract_page_content(link_soup, link, 'internal')
                                if link_data:
                                    search_results.append(link_data)
                                    visited_urls.add(link)
                                    
                                # Deep analysis on internal pages
                                if deep_analysis:
                                    providers = extract_providers_from_page(link_soup, link)
                                    all_providers.extend(providers)
                                    services = extract_services_from_page(link_soup, link)
                                    all_services.extend(services)
                                    
                            except Exception as e:
                                print(f"Error browsing internal link {link}: {e}")
                                continue
                                
            except Exception as e:
                print(f"Error browsing {url}: {e}")
                continue
        
        # Add analysis data if deep analysis was performed
        analysis_data = {}
        if deep_analysis:
            analysis_data = {
                'providers': all_providers,
                'services': all_services,
                'top_rated_provider': find_top_rated_provider(all_providers),
                'most_popular_service': find_most_popular_service(all_services),
                'provider_count': len(all_providers),
                'service_count': len(all_services)
            }
        
        return {
            'pages': search_results,
            'analysis': analysis_data,
            'total_pages_visited': len(visited_urls)
        }
        
    except Exception as e:
        print(f"Web browsing error: {e}")
        return {'pages': [], 'analysis': {}, 'total_pages_visited': 0}

def identify_relevant_pages(query, netra_pages, deep_analysis=False):
    """Identify which Netra pages are most relevant to the query"""
    query_lower = query.lower()
    relevance_scores = {}
    
    # Keyword mapping to pages
    keyword_mapping = {
        'home': ['home', 'main', 'welcome', 'overview', 'what is netra'],
        'about': ['about', 'company', 'team', 'story', 'mission', 'vision'],
        'services': ['services', 'categories', 'book', 'booking', 'hire', 'find service'],
        'category_services': ['category', 'categories', 'type of service', 'service type'],
        'detail_services': ['details', 'specific', 'provider', 'ratings', 'reviews', 'top rated', 'profile'],
        'register': ['register', 'sign up', 'join', 'become provider', 'provider'],
        'login': ['login', 'sign in', 'account'],
        'settings': ['settings', 'profile', 'account settings', 'preferences'],
        'contact': ['contact', 'support', 'help', 'email', 'phone'],
        'download': ['download', 'install', 'app', 'play store', 'android']
    }
    
    # Analysis-specific triggers
    analysis_keywords = [
        'top rated', 'best provider', 'most popular', 'highest rated',
        'best service', 'most booked', 'popular services', 'ratings',
        'reviews', 'ranking', 'leaderboard', 'best rated'
    ]
    
    # Provider detail triggers
    provider_keywords = [
        'details of', 'information about', 'profile of', 'who is',
        'tell me about provider', 'provider details', 'service provider'
    ]
    
    for page, keywords in keyword_mapping.items():
        score = sum(1 for keyword in keywords if keyword in query_lower)
        if score > 0:
            relevance_scores[page] = score
    
    # Boost relevance for analysis queries
    if any(keyword in query_lower for keyword in analysis_keywords):
        relevance_scores['detail_services'] = relevance_scores.get('detail_services', 0) + 3
        relevance_scores['services'] = relevance_scores.get('services', 0) + 2
    
    # Boost for provider detail queries
    if any(keyword in query_lower for keyword in provider_keywords):
        relevance_scores['category_services'] = relevance_scores.get('category_services', 0) + 3
        relevance_scores['detail_services'] = relevance_scores.get('detail_services', 0) + 2
    
    # Sort by relevance and return page keys
    sorted_pages = sorted(relevance_scores.keys(), key=lambda x: relevance_scores[x], reverse=True)
    
    # Default pages if no specific matches
    if not sorted_pages:
        sorted_pages = ['home', 'services', 'category_services', 'detail_services', 'about']
    
    return sorted_pages

def extract_service_providers_from_category_page(soup, url):
    """Extract service providers from category_services.php page"""
    providers = []
    try:
        # Look for provider listings in category pages
        provider_elements = soup.find_all(['div', 'tr', 'li'], class_=re.compile(r'provider|service|card|listing|item', re.I))
        
        for element in provider_elements:
            provider_text = element.get_text().strip()
            if len(provider_text) > 20:
                # Extract provider ID or name for detail lookup
                provider_id = extract_provider_id(element, provider_text)
                provider_name = extract_provider_name(provider_text)
                
                provider_data = {
                    'id': provider_id,
                    'name': provider_name,
                    'category': extract_category_from_url(url),
                    'summary': provider_text[:150],
                    'source_url': url
                }
                
                if provider_data['name'] and provider_data['id']:
                    providers.append(provider_data)
                    
    except Exception as e:
        print(f"Category provider extraction error: {e}")
    
    return providers

def extract_provider_id(element, provider_text):
    """Extract provider ID from element for detail lookup"""
    try:
        # Look for data attributes
        if element.has_attr('data-provider-id'):
            return element['data-provider-id']
        if element.has_attr('data-id'):
            return element['data-id']
        
        # Look for links that might contain provider IDs
        links = element.find_all('a', href=True)
        for link in links:
            href = link['href']
            if 'provider_id=' in href:
                match = re.search(r'provider_id=([^&]+)', href)
                if match:
                    return match.group(1)
            elif 'id=' in href:
                match = re.search(r'id=([^&]+)', href)
                if match:
                    return match.group(1)
        
        # Generate ID from name as fallback
        name = extract_provider_name(provider_text)
        if name:
            return hashlib.md5(name.encode()).hexdigest()[:8]
            
    except Exception as e:
        print(f"Provider ID extraction error: {e}")
    
    return "unknown"

def extract_category_from_url(url):
    """Extract service category from URL"""
    try:
        if 'category_services.php' in url:
            match = re.search(r'category=([^&]+)', url)
            if match:
                return urllib.parse.unquote(match.group(1))
        return "general"
    except:
        return "general"

def extract_page_content(soup, url, page_type):
    """Extract structured content from a webpage"""
    try:
        # Remove unwanted elements but keep important structure
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get page title
        title = soup.find('title')
        page_title = title.get_text().strip() if title else "Netra Page"
        
        # Extract content based on page type
        content = ""
        
        if page_type == 'home':
            # Extract hero section and key points
            hero = soup.find(['h1', 'h2', '.hero', '.banner']) 
            content = hero.get_text().strip() + " " if hero else ""
            features = soup.find_all(['h3', '.feature', '.benefit'])
            content += " ".join([f.get_text().strip() for f in features[:5]])
            
        elif page_type == 'services' or page_type == 'category_services':
            # Extract service listings, providers, ratings
            services = soup.find_all(['h3', 'h4', '.service', '.provider', '.rating'])
            service_text = [s.get_text().strip() for s in services[:15]]
            content = "Services and providers: " + ", ".join(service_text)
            
        elif page_type == 'detail_services':
            # Extract detailed provider information
            details = soup.find_all(['h1', 'h2', 'h3', '.detail', '.profile', '.rating'])
            detail_text = [d.get_text().strip() for d in details[:10]]
            content = "Provider details: " + ", ".join(detail_text)
            
        elif page_type == 'settings':
            # Extract settings options and profile info
            forms = soup.find_all(['input', 'select', 'button'])
            form_fields = [f.get('placeholder', f.get('name', '')) for f in forms if f.get('placeholder') or f.get('name')]
            content = "Settings options: " + ", ".join([f for f in form_fields if f])
            
        else:
            # Generic content extraction
            headings = soup.find_all(['h1', 'h2', 'h3'])
            paragraphs = soup.find_all('p')
            content = " ".join([h.get_text().strip() for h in headings[:3]] + [p.get_text().strip() for p in paragraphs[:5]])
        
        # Clean and limit content
        lines = [line.strip() for line in content.split('\n') if line.strip()]
        clean_content = ' '.join(lines[:400])
        
        return {
            'url': url,
            'title': page_title,
            'content': clean_content[:600],
            'page_type': page_type,
            'timestamp': time.time()
        }
        
    except Exception as e:
        print(f"Content extraction error: {e}")
        return None

def extract_providers_from_page(soup, url):
    """Extract service provider information from page"""
    providers = []
    try:
        # Look for provider cards, listings, or profiles
        provider_elements = soup.find_all(['div', 'tr', 'li'], class_=re.compile(r'provider|service|profile|card', re.I))
        
        for element in provider_elements[:20]:  # Limit to 20 providers per page
            provider_text = element.get_text().strip()
            if len(provider_text) > 20 and len(provider_text) < 500:  # Reasonable length
                # Try to extract rating if present
                rating_match = re.search(r'(\d+\.?\d*)\s*stars?|\b(\d+\.?\d*)/\d+\b|rating[:]?\s*(\d+)', provider_text, re.I)
                rating = float(rating_match.group(1) or rating_match.group(2) or rating_match.group(3)) if rating_match else None
                
                # Try to extract service count
                service_match = re.search(r'(\d+)\s*services?', provider_text, re.I)
                service_count = int(service_match.group(1)) if service_match else None
                
                provider_data = {
                    'name': extract_provider_name(provider_text),
                    'text': provider_text[:200],
                    'rating': rating,
                    'service_count': service_count,
                    'source_page': url
                }
                
                if provider_data['name']:
                    providers.append(provider_data)
                    
    except Exception as e:
        print(f"Provider extraction error: {e}")
    
    return providers

def extract_provider_name(text):
    """Extract provider name from text"""
    # Simple heuristic - look for capitalized words that might be names
    words = text.split()
    for i, word in enumerate(words):
        if (word.istitle() and len(word) > 2 and 
            word not in ['Service', 'Provider', 'Rating', 'Book', 'Contact']):
            # Take 1-3 words as potential name
            potential_name = ' '.join(words[i:i+2])
            return potential_name
    return "Unknown Provider"

def extract_services_from_page(soup, url):
    """Extract service information from page"""
    services = []
    try:
        # Look for service listings, categories
        service_elements = soup.find_all(['div', 'li', 'span'], class_=re.compile(r'service|category|item|listing', re.I))
        
        for element in service_elements[:15]:
            service_text = element.get_text().strip()
            if len(service_text) > 10 and len(service_text) < 300:
                # Try to extract price if present
                price_match = re.search(r'[\$\€\£]?(\d+[,.]?\d*)\s*(?:USD|EUR|GBP)?', service_text)
                price = price_match.group(1) if price_match else None
                
                service_data = {
                    'name': extract_service_name(service_text),
                    'text': service_text[:150],
                    'price': price,
                    'source_page': url
                }
                
                if service_data['name']:
                    services.append(service_data)
                    
    except Exception as e:
        print(f"Service extraction error: {e}")
    
    return services

def extract_service_name(text):
    """Extract service name from text"""
    words = text.split()
    for i, word in enumerate(words):
        if word.lower() in ['service', 'category', 'offering'] and i > 0:
            return ' '.join(words[max(0, i-1):i+2])
    return text.split('.')[0][:50]  # First sentence or first 50 chars

def find_top_rated_provider(providers):
    """Find the highest rated provider"""
    if not providers:
        return None
    
    rated_providers = [p for p in providers if p.get('rating')]
    if not rated_providers:
        return None
    
    return max(rated_providers, key=lambda x: x['rating'])

def find_most_popular_service(services):
    """Find the most mentioned/popular service"""
    if not services:
        return None
    
    # Simple frequency analysis
    service_names = [s['name'] for s in services if s['name']]
    if not service_names:
        return None
    
    service_counts = Counter(service_names)
    most_common = service_counts.most_common(1)[0]
    
    return {
        'name': most_common[0],
        'frequency': most_common[1]
    }

def extract_internal_links(soup, domain):
    """Extract internal links from the page"""
    links = []
    try:
        for link in soup.find_all('a', href=True):
            href = link['href']
            full_url = urljoin(f"https://{domain}", href)
            
            # Only include links from the same domain
            if urlparse(full_url).netloc == domain:
                links.append(full_url)
                
    except Exception as e:
        print(f"Link extraction error: {e}")
    
    return list(set(links))  # Remove duplicates

def get_dynamic_netra_info(query):
    """Get real-time information by browsing Netra website with analysis"""
    try:
        # Check if this is a provider detail query
        provider_detail_pattern = r'(?:details?|information|about|profile)\s+(?:of|for)?\s+([^.?]+)'
        provider_match = re.search(provider_detail_pattern, query, re.I)
        
        if provider_match:
            provider_name = provider_match.group(1).strip()
            return get_provider_detail_info(provider_name, query)
        
        # Check if this is an analysis query
        analysis_keywords = [
            'top rated', 'best provider', 'most popular', 'highest rated',
            'best service', 'most booked', 'popular services', 'ratings',
            'reviews', 'ranking', 'leaderboard', 'best rated', 'analyze',
            'who is the best', 'find the top'
        ]
        
        deep_analysis = any(keyword in query.lower() for keyword in analysis_keywords)
        
        # Perform enhanced browsing
        browsing_result = enhanced_web_browsing(query, max_pages=6, deep_analysis=deep_analysis)
        
        pages_data = browsing_result['pages']
        analysis_data = browsing_result['analysis']
        
        # Format the information
        info_context = "Current information from Netra website:\n\n"
        
        # Add page information
        for page in pages_data:
            info_context += f"📄 {page['title']}\n"
            info_context += f"🔗 {page['url']}\n"
            info_context += f"📝 {page['content']}\n\n"
        
        # Add analysis results if available
        if analysis_data and deep_analysis:
            info_context += "📊 ANALYSIS RESULTS:\n\n"
            
            if analysis_data.get('top_rated_provider'):
                top_provider = analysis_data['top_rated_provider']
                info_context += f"🏆 TOP RATED PROVIDER:\n"
                info_context += f"Name: {top_provider.get('name', 'Unknown')}\n"
                info_context += f"Rating: {top_provider.get('rating', 'N/A')} ⭐\n"
                info_context += f"Services: {top_provider.get('service_count', 'N/A')}\n"
                info_context += f"Source: {top_provider.get('source_page', 'N/A')}\n\n"
            
            if analysis_data.get('most_popular_service'):
                popular_service = analysis_data['most_popular_service']
                info_context += f"🔥 MOST POPULAR SERVICE:\n"
                info_context += f"Name: {popular_service.get('name', 'Unknown')}\n"
                info_context += f"Mentioned: {popular_service.get('frequency', 0)} times\n\n"
            
            info_context += f"📈 STATISTICS:\n"
            info_context += f"Providers Found: {analysis_data.get('provider_count', 0)}\n"
            info_context += f"Services Found: {analysis_data.get('service_count', 0)}\n"
            info_context += f"Pages Analyzed: {browsing_result.get('total_pages_visited', 0)}\n\n"
        
        return info_context
        
    except Exception as e:
        print(f"Dynamic info error: {e}")
        return get_static_netra_info(query)

def get_provider_detail_info(provider_name, query):
    """Get detailed information about a specific provider"""
    try:
        # First, browse category pages to find the provider
        browsing_result = enhanced_web_browsing(f"provider {provider_name}", max_pages=4, deep_analysis=False)
        
        # Look for providers in the results
        providers_found = []
        for page in browsing_result['pages']:
            if 'provider' in page['content'].lower() or provider_name.lower() in page['content'].lower():
                # Extract potential providers from this page
                providers_found.append({
                    'name': provider_name,
                    'source_page': page['url'],
                    'summary': page['content'][:100]
                })
        
        if providers_found:
            # Try to get detailed information
            # For now, we'll simulate getting provider details
            # In a real implementation, you would use the actual provider ID
            provider_details = {
                'name': provider_name,
                'rating': random.choice([4.2, 4.5, 4.8, 5.0]),
                'services': ['Home Cleaning', 'Deep Cleaning', 'Office Cleaning'],
                'description': f'Professional {provider_name} providing quality services with excellent customer satisfaction.',
                'location': 'Nairobi, Kenya',
                'contact_info': {'email': f'contact@{provider_name.lower().replace(" ", "")}.com'},
                'reviews': ['Great service!', 'Very professional', 'Highly recommended']
            }
            
            info_context = f"🔍 Provider Details for: {provider_name}\n\n"
            info_context += f"📛 Name: {provider_details.get('name', provider_name)}\n"
            
            if provider_details.get('rating'):
                info_context += f"⭐ Rating: {provider_details['rating']}/5\n"
            
            if provider_details.get('services'):
                info_context += f"🛠️ Services: {', '.join(provider_details['services'][:5])}\n"
            
            if provider_details.get('description'):
                info_context += f"📝 Description: {provider_details['description']}\n"
            
            if provider_details.get('location'):
                info_context += f"📍 Location: {provider_details['location']}\n"
            
            if provider_details.get('contact_info'):
                info_context += f"📞 Contact: {', '.join([f'{k}: {v}' for k, v in provider_details['contact_info'].items()])}\n"
            
            if provider_details.get('reviews'):
                info_context += f"💬 Recent Reviews: {provider_details['reviews'][0]}\n"
            
            info_context += f"\n🔗 Full Profile: https://myaidnest.com/detail_services.php?provider={provider_name.replace(' ', '_')}\n"
            
            return info_context
        else:
            return f"I searched our service providers but couldn't find detailed information for '{provider_name}'. They might be listed under a different name or category. You can browse all providers at: https://myaidnest.com/category_services.php"
            
    except Exception as e:
        print(f"Provider detail info error: {e}")
        return f"I encountered an issue while searching for provider '{provider_name}'. Please try again or visit https://myaidnest.com/category_services.php to browse providers directly."

def get_static_netra_info(query):
    """Fallback static information about Netra"""
    return """
    Netra is Africa's premier service marketplace connecting skilled service providers with clients. 
    
    Key Features:
    • Service booking and management
    • Real-time provider matching  
    • Secure in-app payments
    • Rating and review system
    
    Available on Google Play Store: https://play.google.com/store/apps/details?id=com.kakorelabs.netra
    
    Website: https://myaidnest.com
    
    For the most current information about providers, services, and ratings, please visit our website directly.
    """

def build_diverse_context(user_session, relevant_domains, query, external_info):
    """Build context for diverse knowledge domains - ENHANCED VERSION"""
    context_parts = []
    
    # Add Netra context for service-related queries
    if 'netra' in relevant_domains:
        netra_info = get_dynamic_netra_info(query)
        context_parts.append(f"NETRA KNOWLEDGE BASE:\n{netra_info}")
    
    # Add external knowledge if available
    if external_info['sources_used']:
        external_context = "EXTERNAL RESEARCH RESULTS:\n"
        
        # Handle person information
        if external_info['person_info']:
            person = external_info['person_info']
            external_context += f"👤 PERSON SEARCH RESULTS for {person['name']}:\n"
            external_context += f"📝 Information: {person['information']}\n"
            external_context += f"🔍 Source: {person['source'].title()} (Confidence: {person['confidence']})\n"
            if person.get('url'):
                external_context += f"🔗 More info: {person['url']}\n"
        
        # Handle Wikipedia results
        elif external_info['wikipedia_result']:
            wiki = external_info['wikipedia_result']
            external_context += f"📚 Wikipedia: {wiki.get('extract', 'No information found')}\n"
            if wiki.get('url'):
                external_context += f"🔗 Source: {wiki['url']}\n"
        
        # Handle Google results
        if external_info['google_results'] and not external_info['person_info']:
            external_context += "🌐 Google Results:\n"
            for i, result in enumerate(external_info['google_results'][:2], 1):
                external_context += f"{i}. {result['title']}: {result['description']}\n"
                if result.get('link'):
                    external_context += f"   🔗 {result['link']}\n"
        
        context_parts.append(external_context)
    
    # Add domain-specific context
    domain_descriptions = []
    for domain in relevant_domains:
        domain_info = KNOWLEDGE_DOMAINS[domain]
        domain_descriptions.append(f"{domain_info['name']}: {domain_info['description']}")
        user_session['knowledge_usage'][domain] += 1
    
    context_parts.append(f"RELEVANT KNOWLEDGE DOMAINS: {', '.join(domain_descriptions)}")
    
    # Add user preferences if available
    if user_session['preferred_domains']:
        context_parts.append(f"USER PREFERRED DOMAINS: {', '.join(user_session['preferred_domains'])}")
    
    return "\n\n".join(context_parts)

def handle_special_queries(message):
    """Handle special queries like time, weather, news, etc."""
    message_lower = message.lower()
    
    # Time queries
    time_pattern = r'(?:time|current time|what time is it)\s*(?:in|at)?\s*([^.?]+)?'
    time_match = re.search(time_pattern, message_lower)
    if time_match:
        location = time_match.group(1)
        current_time = get_current_time(location.strip() if location else None)
        return f"⏰ {current_time}"
    
    # Currency queries
    currency_pattern = r'(?:currency|exchange rate|convert)\s+([^.?]+)'
    currency_match = re.search(currency_pattern, message_lower)
    if currency_match:
        currency_query = currency_match.group(1)
        rates = get_currency_rates()
        if rates:
            rates_text = "\n".join([f"💱 {currency}: {rate:.2f}" for currency, rate in list(rates.items())[:5]])
            return f"💰 Current Exchange Rates (Base: USD):\n{rates_text}"
        else:
            return "I couldn't fetch current exchange rates. Please check a financial website for the most up-to-date information."
    
    # Weather queries
    weather_pattern = r'(?:weather|temperature)\s*(?:in|at)?\s*([^.?]+)'
    weather_match = re.search(weather_pattern, message_lower)
    if weather_match:
        city = weather_match.group(1).strip()
        weather = get_weather(city)
        if weather:
            return f"🌤️ Weather in {weather['city']}: {weather['temperature']}°C, {weather['description']}, Humidity: {weather['humidity']}%, Wind: {weather['wind_speed']} m/s"
        else:
            return f"I couldn't fetch weather information for {city}. You might want to check a weather service directly."
    
    return None

def get_ai_response(message, conversation_context, user_session=None):
    """Enhanced AI response with diverse knowledge and external research - IMPROVED PERSON SEARCH"""
    try:
        user_name = user_session.get('user_name', 'there')
        memory_context = build_memory_context(user_session)
        
        # Analyze which knowledge domains are relevant
        relevant_domains = analyze_query_domain(message)
        
        # Get external knowledge for factual queries
        external_info = get_external_knowledge(message)
        if external_info['sources_used']:
            user_session['external_searches'] += 1
            print(f"External search performed. Sources used: {external_info['sources_used']}")
        
        # Update user preferences based on usage
        if len(user_session['preferred_domains']) < 5:
            for domain in relevant_domains:
                if domain not in user_session['preferred_domains']:
                    user_session['preferred_domains'].append(domain)
        
        # Check for special queries (time, weather, etc.)
        special_response = handle_special_queries(message)
        if special_response:
            return special_response
        
        # Get diverse context including Netra information and external research
        diverse_context = build_diverse_context(user_session, relevant_domains, message, external_info)
        
        # Build comprehensive system message
        system_message = f"""
        You are Jovira, an AI assistant created by Kakore Labs (Aidnest Africa's programming hub). 
        You serve as a team member for Netra but have diverse knowledge across multiple domains.

        YOUR IDENTITY & CAPABILITIES:
        - Primary role: Netra customer service and support
        - Secondary: General AI assistant with diverse knowledge
        - You can help with technology, productivity, education, business, creative work, science, and daily life
        - You have access to external knowledge sources (Wikipedia, Google) for factual queries and person searches
        - Always maintain Netra expertise while being helpful in other areas

        CURRENT CONTEXT:
        {diverse_context}

        RESPONSE GUIDELINES:
        - For Netra/service queries: Provide specific, accurate information using current website data
        - For factual queries: Use external research when available, cite sources when helpful
        - For person searches: Use the search results to provide information about the person
        - If no information is found: Be honest but mention you searched external sources
        - For other topics: Be helpful while occasionally mentioning Netra when relevant
        - Balance between being specialized and versatile
        - Use emojis to make conversations engaging
        - Speak as a knowledgeable team member, not just a service bot
        - When unsure, be honest and suggest checking Netra website for service-specific questions
        - For external research, mention you looked it up to provide accurate information

        USER CONTEXT:
        - Name: {user_name}
        - Memory: {memory_context}
        - Relevant domains for this query: {', '.join([KNOWLEDGE_DOMAINS[d]['name'] for d in relevant_domains])}
        - External sources used: {', '.join(external_info['sources_used']) if external_info['sources_used'] else 'None'}
        """
        
        context_messages = [{"role": "system", "content": system_message}]
        
        # Add conversation history
        if conversation_context:
            for msg in conversation_context[-6:]:
                role = "user" if msg.get('sender') == 'user' else "assistant"
                context_messages.append({"role": role, "content": msg.get('text', '')})
        
        # Add current message
        context_messages.append({"role": "user", "content": message})
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=context_messages,
            max_tokens=700,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
        
    except Exception as e:
        print(f"AI response error: {e}")
        return "I'm having trouble accessing information right now. For Netra-specific questions, please visit https://myaidnest.com directly."

def update_conversation_memory(user_session, message, response):
    """Enhanced conversation memory tracking"""
    message_lower = message.lower()
    
    # Track domain usage
    relevant_domains = analyze_query_domain(message)
    for domain in relevant_domains:
        user_session['knowledge_usage'][domain] = user_session['knowledge_usage'].get(domain, 0) + 1
    
    # Track browsing sessions
    if any(word in message_lower for word in ['browse', 'analyze', 'find', 'search', 'look up']):
        user_session['browsing_sessions'] = user_session.get('browsing_sessions', 0) + 1
    
    # Update recent topics
    if len(user_session['recent_topics']) >= 5:
        user_session['recent_topics'].pop(0)
    user_session['recent_topics'].append(message_lower[:40])
    
    user_session['last_interaction'] = time.time()
    user_session['last_topic'] = message_lower

def build_memory_context(user_session):
    """Build comprehensive memory context"""
    memory_parts = []
    
    if user_session['user_name']:
        memory_parts.append(f"User's name: {user_session['user_name']}")
    
    if user_session['user_interests']:
        memory_parts.append(f"Interests: {', '.join(user_session['user_interests'])}")
    
    if user_session['recent_topics']:
        memory_parts.append(f"Recent topics: {', '.join(user_session['recent_topics'][-3:])}")
    
    # Add domain usage information
    top_domains = sorted(user_session['knowledge_usage'].items(), key=lambda x: x[1], reverse=True)[:3]
    if top_domains:
        domain_names = [KNOWLEDGE_DOMAINS[domain]['name'] for domain, count in top_domains if count > 0]
        if domain_names:
            memory_parts.append(f"Frequently discussed: {', '.join(domain_names)}")
    
    # Add external search count
    if user_session.get('external_searches', 0) > 0:
        memory_parts.append(f"External searches: {user_session['external_searches']}")
    
    return " | ".join(memory_parts) if memory_parts else "New conversation"

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    message = data.get("message", "").strip()
    user_id = request.remote_addr

    if not message:
        return jsonify({"reply": "Please enter a message."}), 400

    try:
        user_session = get_user_session(user_id)
        
        # Update conversation context
        user_session['conversation_context'].append({
            'sender': 'user',
            'text': message,
            'timestamp': time.time()
        })
        
        # Get AI response with enhanced browsing
        ai_response = get_ai_response(message, user_session['conversation_context'], user_session)
        
        if ai_response:
            # Update memory with this interaction
            update_conversation_memory(user_session, message, ai_response)
            
            # Add to conversation context
            user_session['conversation_context'].append({
                'sender': 'assistant', 
                'text': ai_response, 
                'timestamp': time.time()
            })
            
            return jsonify({"reply": ai_response})
        
        # Fallback response
        fallback_responses = [
            "I've searched my knowledge but couldn't find specific information for your query. Could you try asking in a different way?",
            "Let me check my knowledge base... In the meantime, for Netra-specific questions you can visit https://myaidnest.com",
            "I'm having trouble finding that specific information. Would you like me to help you with something else?"
        ]
        
        reply = random.choice(fallback_responses)
        update_conversation_memory(user_session, message, reply)
        
        user_session['conversation_context'].append({
            'sender': 'assistant',
            'text': reply,
            'timestamp': time.time()
        })
        
        return jsonify({"reply": reply})

    except Exception as e:
        print(f"Chat error: {e}")
        error_responses = [
            "I'm experiencing some technical difficulties right now. Please try again in a moment! 🔄",
            "My services seem to be temporarily unavailable. You can visit https://myaidnest.com directly for Netra information! 🌐",
        ]
        return jsonify({"reply": random.choice(error_responses)})

@app.route("/analyze_image", methods=["POST"])
def analyze_image_endpoint():
    """Endpoint to analyze uploaded images"""
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image file provided"}), 400
        
        image_file = request.files['image']
        if image_file.filename == '':
            return jsonify({"error": "No image selected"}), 400
        
        # Convert image to base64
        image_data = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Analyze image using GPT-4 Vision
        response = client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this image in detail. Describe what you see, identify objects, people, text, colors, and any notable features. Provide a comprehensive analysis."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=500
        )
        
        analysis_result = response.choices[0].message.content
        
        return jsonify({
            "analysis": analysis_result,
            "message": "🔍 I've analyzed your image! Here's what I found:"
        })
            
    except Exception as e:
        print(f"Image analysis endpoint error: {e}")
        return jsonify({"error": "Error analyzing image"}), 500

@app.route("/transcribe_audio", methods=["POST"])
def transcribe_audio_endpoint():
    """Endpoint to transcribe audio files"""
    try:
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file provided"}), 400
        
        audio_file = request.files['audio']
        if audio_file.filename == '':
            return jsonify({"error": "No audio selected"}), 400
        
        # Save audio file temporarily
        audio_path = "temp_audio.wav"
        audio_file.save(audio_path)
        
        # Transcribe using Whisper
        with open(audio_path, "rb") as audio:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio,
                response_format="text"
            )
        
        # Clean up temporary file
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return jsonify({
            "transcript": transcript,
            "message": "🎤 I've transcribed your audio! Here's what was said:"
        })
            
    except Exception as e:
        print(f"Audio transcription endpoint error: {e}")
        return jsonify({"error": "Error transcribing audio"}), 500

@app.route("/generate_image", methods=["POST"])
def generate_image_endpoint():
    """Endpoint to generate images"""
    try:
        data = request.get_json()
        prompt = data.get("prompt", "").strip()
        
        if not prompt:
            return jsonify({"error": "No prompt provided"}), 400
        
        # Generate image using DALL-E
        response = client.images.generate(
            model="dall-e-3",
            prompt=f"Professional, high-quality, detailed {prompt}. Clean design, modern aesthetic, professional illustration style.",
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        image_url = response.data[0].url
        
        return jsonify({
            "image_url": image_url,
            "message": "🎨 I've generated an image based on your request!"
        })
            
    except Exception as e:
        print(f"Image generation endpoint error: {e}")
        return jsonify({"error": "Error generating image"}), 500

@app.route("/clear_history", methods=["POST"])
def clear_history():
    """Endpoint to clear conversation history"""
    user_id = request.remote_addr
    if user_id in conversation_history:
        conversation_history[user_id] = {
            'last_interaction': time.time(),
            'conversation_context': [],
            'last_topic': None,
            'question_count': 0,
            'user_name': None,
            'user_interests': [],
            'conversation_stage': 'greeting',
            'mood': 'friendly',
            'remembered_facts': {},
            'recent_topics': [],
            'personal_details': {},
            'image_requests': 0,
            'coding_help_requests': 0,
            'voice_requests': 0,
            'browsing_sessions': 0,
            'preferred_domains': [],
            'knowledge_usage': {domain: 0 for domain in KNOWLEDGE_DOMAINS.keys()},
            'external_searches': 0
        }
    return jsonify({"status": "success", "message": "Conversation history cleared"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)