import random
from typing import Dict, List

class HumanizedNetraEngine:
    def __init__(self):
        # Netra core information
        self.netra_info = {
            'name': 'Netra',
            'description': 'Professional social app connecting service providers and clients',
            'website': 'https://netra.strobid.com',
            'play_store': 'Google Play Store',
            'emblem': 'butterfly-like emblem without fill',
            'security': 'No screenshots or screen recording'
        }
        
        # Response variations for human-like conversations
        self.conversation_starters = [
            "Hey there! ",
            "Oh, about Netra? ",
            "Sure thing! ",
            "I'd be happy to explain! ",
            "Awesome question! ",
            "Glad you asked! ",
            "Let me break this down: ",
            "Here's the scoop: ",
            "Perfect timing! ",
            "Oh, I love talking about Netra! ",
            "Great question! ",
            "Yeah, let me explain: ",
            "So, Netra is... ",
            "Let me tell you about it: ",
            "Happy to help! "
        ]
        
        self.friendly_closers = [
            " Hope that helps!",
            " Let me know if you have other questions!",
            " Pretty cool, right?",
            " Makes sense?",
            " Easy enough?",
            " Got it?",
            " Clear?",
            " Sound good?",
            " Awesome, right?",
            " Neat, huh?",
            " Pretty straightforward!",
            " Simple as that!",
            " That's the gist of it!"
        ]
        
        self.positive_reactions = [
            "Nice! ",
            "Awesome! ",
            "Great! ",
            "Perfect! ",
            "Excellent! ",
            "Brilliant! ",
            "Fantastic! ",
            "Sweet! ",
            "Cool! ",
            "Wonderful! "
        ]

    def _get_random_opener(self) -> str:
        return random.choice(self.conversation_starters)

    def _get_random_closer(self) -> str:
        return random.choice(self.friendly_closers)

    def _get_random_reaction(self) -> str:
        return random.choice(self.positive_reactions)

    def _humanize_netra_intro(self) -> str:
        """Multiple ways to introduce Netra"""
        intros = [
            f"{self._get_random_reaction()}Netra's this really cool app that connects skilled professionals with people who need their services right in their community! It's like a social network but for legit service providers.",
            
            f"{self._get_random_opener()}it's a professional social app that builds networks between service providers and potential clients. Think of it as your go-to for finding reliable pros in your area!",
            
            f"You know how hard it can be to find trustworthy service people? {self._get_random_reaction()}Netra solves that! It's basically a digital marketplace where professionals showcase their work and clients can easily find them.",
            
            f"{self._get_random_opener()}it's this awesome platform where service providers and clients connect. From plumbers to musicians, everyone can find what they need or offer what they're good at!",
            
            f"Netra's pretty amazing actually! {self._get_random_reaction()}It creates professional networks within communities - so you can find reliable service providers or get your services discovered by people who need them."
        ]
        return random.choice(intros) + self._get_random_closer()

    def _humanize_getting_started(self) -> str:
        """Different ways to explain getting started"""
        approaches = [
            f"{self._get_random_opener()}getting started is super simple! Just download Netra from Play Store (look for the butterfly logo), tap 'Get Started', and you're in. No complicated sign-up needed if you're just browsing!",
            
            f"Ready to jump in? {self._get_random_reaction()}Download the app → Open it → Hit 'Get Started'. Boom, you're on the 'For You' page seeing recommended providers right away!",
            
            f"{self._get_random_opener()}it's really straightforward: Install from Play Store, open the app, tap that 'Get Started' button, and you'll immediately see services around you. No account needed to start exploring!",
            
            f"Starting with Netra is a breeze! {self._get_random_reaction()}Grab the app, open it up, click 'Get Started', and you'll land on personalized recommendations. The app does all the heavy lifting for you!"
        ]
        return random.choice(approaches) + self._get_random_closer()

    def _humanize_provider_registration(self) -> str:
        """Multiple ways to explain provider registration"""
        variations = [
            {
                'opener': f"{self._get_random_opener()}to join as a provider: ",
                'steps': [
                    "Tap the 'Account' button at the bottom",
                    "Hit 'Create account' since you're new",
                    "Fill in your professional details",
                    "They'll email you a verification code",
                    "Enter the code and you're all set!"
                ],
                'details': "You'll need your service info, location, experience level, and a profile pic ready."
            },
            {
                'opener': f"Becoming a provider? {self._get_random_reaction()}",
                'steps': [
                    "Click 'Account' in the navigation",
                    "Choose 'Create account' to begin",
                    "Share your service details and experience",
                    "Check email for the OTP code",
                    "Verify and start getting clients!"
                ],
                'details': "The form asks about what you do, where you operate, and your background."
            },
            {
                'opener': f"Ready to offer services? {self._get_random_reaction()}Here's how: ",
                'steps': [
                    "Head to the 'Account' section",
                    "Tap 'Create account' to start",
                    "Fill out your professional information",
                    "Watch for the email verification code",
                    "Verify and build your client base!"
                ],
                'details': "You'll share your service category, location, years of experience - all the important stuff."
            }
        ]
        
        variation = random.choice(variations)
        steps_formatted = "\n".join([f"• {step}" for step in variation['steps']])
        
        return f"{variation['opener']}\n\n{steps_formatted}\n\n{variation['details']}{self._get_random_closer()}"

    def _humanize_client_usage(self) -> str:
        """Different ways to explain client usage"""
        approaches = [
            "search three ways: by provider name, by service category, or by location!",
            "there are multiple search options - look for specific people, browse service types, or find what's nearby!",
            "you can search flexibly - by professional names, service categories, or local providers!",
            "the app lets you search by name, category, or what's available in your area!"
        ]
        
        tips = [
            "If 'For You' doesn't show what you need, try the category search from Home page!",
            "Not finding the perfect match? The 'Get Services' button after category search usually works better!",
            "Pro tip: Category search from Home often gives more targeted results than the 'For You' page!",
            "Helpful hint: The category search tends to be more specific than the general recommendations!"
        ]
        
        openers = [
            f"{self._get_random_opener()}the best part is you can start using it immediately - no account needed! ",
            f"{self._get_random_reaction()}You don't even need an account to begin! ",
            f"{self._get_random_opener()}you can dive right in without any sign-up! ",
            f"Here's the cool part: {self._get_random_reaction()}No account required to start browsing! "
        ]
        
        return f"{random.choice(openers)}You can {random.choice(approaches)} {random.choice(tips)}{self._get_random_closer()}"

    def _humanize_netra_features(self) -> str:
        """Different ways to explain Netra features"""
        features_list = [
            "bookings, ratings, music streaming from local artists, mixtapes from DJs, reels for pros... it's like multiple apps in one!",
            "beyond just bookings, there's music streaming through Artist Studio, mixtapes via DJ Studio, and reels for professionals to showcase their work!",
            "service bookings, a solid rating system, music features for artists and DJs, content creation options, and partnership opportunities!",
            "practical service bookings mixed with creative features like music streaming, professional reels, and partnership programs!"
        ]
        
        reactions = [
            f"{self._get_random_opener()}Netra's packed with features - ",
            f"{self._get_random_reaction()}There's so much you can do: ",
            f"{self._get_random_opener()}it's not just a service app - ",
            f"What I love about Netra: {self._get_random_reaction()}"
        ]
        
        return f"{random.choice(reactions)}{random.choice(features_list)}{self._get_random_closer()}"

    def _humanize_account_issues(self) -> str:
        """Help with account problems"""
        solutions = [
            f"{self._get_random_opener()}if you're having account trouble, try these quick fixes:\n\n• Double-check your email and password\n• Use the 'Forgot Password' feature\n• Make sure you have stable internet for OTP verification\n• Try force-closing and reopening the app\n\nSometimes a quick app restart does the trick!",
            
            f"Account issues? {self._get_random_reaction()}Here are some things to try:\n\n• Verify you're using the correct email\n• Request a new password reset if needed\n• Ensure good network connection for email verification\n• Clear the app cache in your phone settings\n\nUsually one of these solves the problem!",
            
            f"{self._get_random_opener()}let's troubleshoot your account:\n\n• Confirm your email is entered correctly\n• Use the password recovery option\n• Check that your internet is stable for OTPs\n• Try logging in from a different device\n\nMost account issues are quick to resolve!"
        ]
        return random.choice(solutions)

    def _humanize_booking_help(self) -> str:
        """Help with booking process"""
        guides = [
            f"{self._get_random_opener()}booking services is pretty straightforward!\n\n1. Find a provider you like\n2. Check their ratings and reviews\n3. Contact them through the app\n4. Arrange the service details\n5. Enjoy great service!\n\nThe rating system helps everyone maintain quality.",
            
            f"Want to book a service? {self._get_random_reaction()}Easy!\n\n1. Browse or search for providers\n2. Look at their experience and ratings\n3. Reach out via the app\n4. Finalize the arrangements\n5. Get your service done!\n\nDon't forget to rate your experience afterward!",
            
            f"{self._get_random_opener()}here's the booking flow:\n\n1. Discover providers that match your needs\n2. Review their background and ratings\n3. Initiate contact through Netra\n4. Coordinate the service details\n5. Receive quality service!\n\nThe community ratings keep everything transparent."
        ]
        return random.choice(guides)

    def _humanize_general_help(self) -> str:
        """General help response"""
        responses = [
            f"{self._get_random_opener()}I'm here to help with anything Netra-related! What would you like to know about - getting started, provider registration, features, or something else?",
            
            f"{self._get_random_reaction()}I can help you with Netra! Are you wondering about how to use the app, become a provider, or maybe explore its features?",
            
            f"{self._get_random_opener()}I'd love to assist you with Netra! What specifically are you curious about - the app itself, creating an account, or finding services?"
        ]
        return random.choice(responses)

    def _generate_suggestions(self, intent: str) -> List[str]:
        """Generate context-aware suggestions"""
        suggestion_pools = {
            'netra_intro': [
                "How to get started with Netra",
                "Netra features explained", 
                "Provider registration process",
                "Client usage guide"
            ],
            'getting_started': [
                "Provider account creation",
                "How clients can search services",
                "Netra features overview",
                "Download and installation help"
            ],
            'provider_registration': [
                "What information providers need",
                "Client usage without account", 
                "Netra's security features",
                "Service categories available"
            ],
            'client_usage': [
                "Provider registration process",
                "Netra's rating system",
                "Search tips and tricks", 
                "Service categories explained"
            ],
            'features': [
                "How to become a provider",
                "Client quick start guide",
                "Music streaming features",
                "Partnership programs"
            ],
            'account_help': [
                "Provider registration",
                "Client quick start",
                "Netra security features", 
                "Contact methods"
            ],
            'booking_help': [
                "Provider registration",
                "Client search methods",
                "Rating system explained",
                "Service categories"
            ],
            'general_help': [
                "What is Netra?",
                "How to get started",
                "Provider vs client features",
                "Netra's main features"
            ]
        }
        
        pool = suggestion_pools.get(intent, suggestion_pools['general_help'])
        return random.sample(pool, min(3, len(pool)))

    def process_query(self, message: str, user_id: str = None) -> Dict:
        """Main method to process queries with human-like responses"""
        message_lower = message.lower()
        
        # Simple intent detection
        if any(word in message_lower for word in ['what is netra', 'tell me about netra', 'netra app', 'what is this app']):
            response = self._humanize_netra_intro()
            intent = 'netra_intro'
            
        elif any(word in message_lower for word in ['how to start', 'get started', 'install', 'download', 'begin']):
            response = self._humanize_getting_started()
            intent = 'getting_started'
            
        elif any(word in message_lower for word in ['provider', 'registration', 'create account', 'sign up', 'become provider']):
            response = self._humanize_provider_registration()
            intent = 'provider_registration'
            
        elif any(word in message_lower for word in ['client', 'search', 'find service', 'browse', 'look for']):
            response = self._humanize_client_usage()
            intent = 'client_usage'
            
        elif any(word in message_lower for word in ['features', 'what can it do', 'capabilities', 'functionality']):
            response = self._humanize_netra_features()
            intent = 'features'
            
        elif any(word in message_lower for word in ['account', 'login', 'password', 'otp', 'verification']):
            response = self._humanize_account_issues()
            intent = 'account_help'
            
        elif any(word in message_lower for word in ['book', 'booking', 'schedule', 'hire']):
            response = self._humanize_booking_help()
            intent = 'booking_help'
            
        else:
            response = self._humanize_general_help()
            intent = 'general_help'
        
        # Generate natural suggestions based on intent
        suggestions = self._generate_suggestions(intent)
        
        return {
            'response': response,
            'suggestions': suggestions,
            'confidence': random.randint(85, 98),  # Vary confidence slightly
            'intent': intent
        }

# Create the instance with the name that matches the import
netra_engine = HumanizedNetraEngine()