import requests
from bs4 import BeautifulSoup
import urllib.parse
import re
from urllib.parse import urljoin, urlparse, quote_plus
from collections import Counter
import random
import hashlib
import os
from datetime import datetime, timezone, timedelta
import math

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
        
        # Check if it's Nowamaani Donath (CEO information)
        if 'nowamaani' in person_name.lower() or 'donath' in person_name.lower():
            from knowledge_base import COMPANY_INFO
            ceo_info = COMPANY_INFO['ceo']
            return {
                'source': 'company_database',
                'name': ceo_info['name'],
                'information': f"{ceo_info['title']} of {', '.join(ceo_info['companies'])}. Based in {ceo_info['location']}. {ceo_info['bio']}",
                'url': 'https://myaidnest.com',
                'confidence': 'high'
            }
        
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
    
    return has_external_phrase or has_external_topic or is_complex_factual or has_person_pattern or is_complex_factual

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

def get_current_time(timezone_str=None):
    """Get current time in different timezones - ENHANCED FOR EAST AFRICA"""
    try:
        # Timezone offsets in hours (East Africa focused)
        timezone_offsets = {
            'eat': 3, 'east africa': 3, 'nairobi': 3, 'kampala': 3, 'dar es salaam': 3,
            'kigali': 2, 'addis ababa': 3, 'juba': 2,
            'est': -5, 'edt': -4,  # Eastern
            'pst': -8, 'pdt': -7,  # Pacific
            'cst': -6, 'cdt': -5,  # Central
            'mst': -7, 'mdt': -6,  # Mountain
            'gmt': 0, 'utc': 0, 'zulu': 0,    # GMT/UTC/Zulu
            'ist': 5.5,            # India
            'cet': 1, 'cedt': 2,   # Central European
            'aest': 10,            # Australian Eastern
            'west': 1,             # West Africa
            'cat': 2,              # Central Africa
            'lagos': 1,            # Nigeria
            'accra': 0,            # Ghana
            'johannesburg': 2      # South Africa
        }
        
        if timezone_str:
            tz_lower = timezone_str.lower()
            # Find the best matching timezone
            for tz_name, offset in timezone_offsets.items():
                if tz_name in tz_lower:
                    utc_offset = timedelta(hours=offset)
                    tz_display = tz_name.upper()
                    break
            else:
                # Default to East Africa Time if no match found
                utc_offset = timedelta(hours=3)
                tz_display = "EAT"
        else:
            # Default to East Africa Time
            utc_offset = timedelta(hours=3)
            tz_display = "EAT"
        
        # Calculate time with offset
        current_utc = datetime.now(timezone.utc)
        current_time = current_utc + utc_offset
        
        # Format the time with clear timezone indication
        return current_time.strftime(f"%Y-%m-%d %H:%M:%S {tz_display}")
    
    except Exception as e:
        print(f"Timezone error: {e}")
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S EAT")

def get_currency_rates(base_currency='USD'):
    """Get current currency exchange rates"""
    try:
        # Using a free currency API
        response = requests.get(f'https://api.exchangerate-api.com/v4/latest/{base_currency}', timeout=10)
        if response.status_code == 200:
            data = response.json()
            rates = data.get('rates', {})
            
            # Return major currencies with focus on African currencies
            major_currencies = ['USD', 'EUR', 'GBP', 'KES', 'UGX', 'TZS', 'NGN', 'GHS', 'ZAR', 'CNY']
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

def handle_special_queries(message):
    """Handle special queries like time, weather, calculations, etc."""
    message_lower = message.lower()
    
    # Time queries
    if any(word in message_lower for word in ['time', 'current time', 'what time']):
        time_match = re.search(r'(?:in|at)?\s*([^.?]+)?', message_lower)
        location = time_match.group(1) if time_match and time_match.group(1) else None
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

def analyze_query_domain(query):
    """Analyze which knowledge domains are relevant to the query"""
    from knowledge_base import KNOWLEDGE_DOMAINS
    
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
        domain_scores['netra'] = domain_scores.get('netra', 0) + 3
    
    # Boost science for factual queries
    if any(word in query_lower for word in ['fact', 'science', 'history', 'research', 'study']):
        domain_scores['science'] = domain_scores.get('science', 0) + 2
    
    # Boost calculations for math queries
    if any(word in query_lower for word in ['calculate', 'compute', 'solve', 'math', 'equation']):
        domain_scores['calculations'] = domain_scores.get('calculations', 0) + 3
    
    # Boost physics for physics queries
    if any(word in query_lower for word in ['physics', 'force', 'motion', 'energy', 'electric']):
        domain_scores['physics'] = domain_scores.get('physics', 0) + 3
    
    # Boost biology for biology queries
    if any(word in query_lower for word in ['biology', 'cell', 'dna', 'genetics', 'ecosystem']):
        domain_scores['biology'] = domain_scores.get('biology', 0) + 3
    
    # Boost chemistry for chemistry queries
    if any(word in query_lower for word in ['chemistry', 'reaction', 'molecule', 'atom', 'mechanism']):
        domain_scores['chemistry'] = domain_scores.get('chemistry', 0) + 3
    
    # Sort by relevance
    sorted_domains = sorted(domain_scores.items(), key=lambda x: x[1], reverse=True)
    relevant_domains = [domain for domain, score in sorted_domains if score > 0]
    
    return relevant_domains[:3] if relevant_domains else ['general_tech']

def build_diverse_context(user_session, relevant_domains, query, external_info):
    """Build context for diverse knowledge domains - ENHANCED VERSION"""
    from knowledge_base import KNOWLEDGE_DOMAINS
    
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
    
    # Add memory context
    from session_manager import get_memory_context
    memory_context = get_memory_context(user_session)
    if memory_context != "New conversation":
        context_parts.append(f"CONVERSATION MEMORY:\n{memory_context}")
    
    # Add domain-specific context
    domain_descriptions = []
    for domain in relevant_domains:
        domain_info = KNOWLEDGE_DOMAINS[domain]
        domain_descriptions.append(f"{domain_info['name']}: {domain_info['description']}")
        user_session['knowledge_usage'] = user_session.get('knowledge_usage', {})
        user_session['knowledge_usage'][domain] = user_session['knowledge_usage'].get(domain, 0) + 1
    
    context_parts.append(f"RELEVANT KNOWLEDGE DOMAINS: {', '.join(domain_descriptions)}")
    
    return "\n\n".join(context_parts)

def get_dynamic_netra_info(query):
    """Get real-time information by browsing Netra website with analysis"""
    try:
        return get_static_netra_info(query)  # Simplified version for now
    except Exception as e:
        print(f"Dynamic info error: {e}")
        return get_static_netra_info(query)

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