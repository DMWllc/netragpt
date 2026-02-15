"""
Netra Engine - Humanized AI Assistant for Netra App Support
Knowledge Base: https://netra.strobid.com/help
"""

import random
import re
import time
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime

class HumanizedNetraEngine:
    """
    Humanized AI Engine for Netra customer support
    Uses official help center as knowledge base
    """
    
    def __init__(self):
        # Core Netra information
        self.help_center_url = "https://netra.strobid.com/help"
        self.base_url = "https://netra.strobid.com"
        
        # Company information
        self.netra_info = {
            'name': 'Netra',
            'full_name': 'Netra App',
            'description': 'Professional social app connecting service providers and clients',
            'website': 'https://netra.strobid.com',
            'help_center': 'https://netra.strobid.com/help',
            'play_store': 'Google Play Store',
            'app_store': 'Apple App Store',
            'emblem': 'butterfly-like emblem without fill',
            'security_features': ['No screenshots allowed', 'No screen recording', 'Encrypted messages'],
            'ceo': 'Nowamaani Donath',
            'company': 'Strobid',
            'location': 'Kampala, Uganda',
            'timezone': 'East Africa Time (EAT, UTC+3)',
            'founded': '2023',
            'email': 'support@strobid.com'
        }
        
        # Comprehensive knowledge base
        self.knowledge_base = {
            'general': {
                'what_is_netra': {
                    'patterns': ['what is netra', 'tell me about netra', 'about netra', 'netra app', 'what is this app', 'explain netra', 'netra meaning', 'define netra'],
                    'response': "Netra is a professional social app that connects skilled service providers with clients in their community. Think of it as a digital marketplace where professionals can showcase their work and clients can easily find reliable services - from plumbing and electrical work to music lessons and photography! It's built by Strobid and based in Kampala, Uganda, serving the East African community and beyond."
                },
                'how_it_works': {
                    'patterns': ['how does netra work', 'how it works', 'how to use netra', 'how do i use netra', 'netra working', 'platform overview'],
                    'response': "Netra works by creating a platform where service providers can create profiles showcasing their skills, and clients can browse or search for services they need. You can find providers by name, service category, or location. Once you find someone, you can message them directly through the app, check their ratings and reviews, and book their services - all in one place! The app also features music streaming for artists, mixtapes for DJs, and reels for professionals to showcase their work."
                },
                'who_can_use': {
                    'patterns': ['who can use netra', 'netra users', 'target audience', 'who is netra for'],
                    'response': "Netra is for everyone! Whether you're a professional looking to offer your services, a client needing reliable help, an artist wanting to share your music, or a DJ building your brand - Netra has something for you. Service providers, clients, musicians, DJs, and even businesses can all benefit from being part of the Netra community."
                }
            },
            'account': {
                'create': {
                    'patterns': ['create account', 'sign up', 'register', 'join netra', 'new account', 'how to create', 'make account', 'open account'],
                    'response': "Creating a Netra account is super simple! Just download the app from Google Play Store, open it, tap 'Create Account', and follow these steps:\n\n1. Enter your email address\n2. Create a strong password\n3. Add your phone number (optional but recommended)\n4. Fill in your basic profile info\n5. Check your email for a verification code\n6. Enter the code to verify your account\n\nThat's it! You're now part of the Netra community! 🎉\n\n**Pro Tip:** You can also sign up using your Google account for even faster registration!"
                },
                'verify': {
                    'patterns': ['verify account', 'verification', 'verify email', 'confirm account', 'otp', 'code', 'email verification', 'phone verification'],
                    'response': "Account verification helps build trust in the Netra community! Here's how:\n\n**Email Verification:**\n• After signing up, check your email inbox\n• Look for the verification email from Netra (check spam if you don't see it)\n• Click the verification link or enter the 6-digit code\n• Your email is now verified!\n\n**Phone Verification (Recommended):**\n• Go to Settings > Account > Verify Phone\n• Enter your phone number\n• Receive SMS with verification code\n• Enter the code to complete verification\n\n**Provider Verification (For Service Providers):**\nIf you're offering services, you may need:\n• Government-issued ID\n• Professional certifications\n• Business documents (if applicable)\n• Profile photo verification\n\n**Why Verify?**\n✅ Builds trust with potential clients\n✅ Unlocks all app features\n✅ Higher visibility in search results\n✅ Secure transactions"
                },
                'reset_password': {
                    'patterns': ['reset password', 'forgot password', 'change password', 'new password', 'password help', 'can\'t login', 'lost password'],
                    'response': "No worries! Here's how to reset your Netra password:\n\n**In the App:**\n1. On the login screen, tap 'Forgot Password'\n2. Enter your registered email address\n3. Check your email for reset instructions\n4. Click the reset link (valid for 1 hour)\n5. Create a new strong password\n6. Log in with your new password\n\n**On the Website:**\n1. Visit netra.strobid.com\n2. Click 'Login' then 'Forgot Password'\n3. Follow the same email verification steps\n\n**Password Tips:**\n• Use at least 8 characters\n• Mix letters and numbers\n• Include one uppercase letter\n• Add special characters for extra security (!@#$%)\n• Don't use personal info like your name or birthday\n• Consider using a password manager\n\n**Still having trouble?**\nIf you're not receiving the reset email, check your spam folder or contact support at support@strobid.com"
                },
                'delete': {
                    'patterns': ['delete account', 'remove account', 'close account', 'cancel account', 'deactivate', 'delete profile'],
                    'response': "We're sorry to see you go! Here's how to delete your Netra account:\n\n**IMPORTANT WARNING:** This action is PERMANENT and cannot be undone!\n\n**Before You Delete:**\n⚠️ Cancel any active subscriptions first\n⚠️ Complete any pending transactions\n⚠️ Download any important data you want to keep\n\n**Steps to Delete:**\n1. Open Netra app and log in\n2. Go to Settings > Account Settings\n3. Tap 'Account Management'\n4. Select 'Delete Account'\n5. Read the warning carefully\n6. Enter your password to confirm\n7. Choose a reason (optional but helps us improve)\n8. Tap 'Permanently Delete'\n9. Wait for confirmation email\n\n**What gets deleted:**\n• Profile information and photos\n• Conversation history\n• Payment information\n• Ratings and reviews\n• Service listings (for providers)\n\n**What remains (anonymized for legal purposes):**\n• Transaction records\n• Support ticket history\n\n**Changed your mind?**\nIf you haven't completed the final step, just close the app. Your account remains active!\n\nNeed help? Contact support before deleting - we might be able to help!"
                },
                'login_issues': {
                    'patterns': ['can\'t login', 'login problem', 'sign in issue', 'not logging in', 'login failed'],
                    'response': "Having trouble logging in? Let's troubleshoot:\n\n**Common Solutions:**\n1. Check your internet connection\n2. Verify you're using the correct email\n3. Make sure caps lock isn't on\n4. Try resetting your password if you've forgotten it\n5. Clear the app cache (Settings > Apps > Netra > Clear Cache)\n6. Update to the latest app version\n\n**Still can't login?**\n• Wait a few minutes and try again\n• Try logging in on a different device\n• Contact support at support@strobid.com with your account email"
                }
            },
            'payments': {
                'how_payments_work': {
                    'patterns': ['how payments work', 'payment process', 'pay for service', 'make payment', 'how to pay', 'payment methods', 'payments explained'],
                    'response': "Netra makes payments simple and secure! Here's how it works:\n\n**For Clients (Paying for Services):**\n1. When you book a service, you'll see the total price\n2. Choose your payment method:\n   • 💳 Credit/Debit Cards (Visa, Mastercard)\n   • 📱 Mobile Money (MTN, Airtel)\n   • 💵 Cash (with provider approval)\n   • 🏦 Bank Transfer\n3. A deposit may be required to confirm your booking\n4. The balance is paid after service completion\n5. Your money is held securely until you're satisfied\n\n**For Providers (Receiving Payments):**\n1. Set up your payout method in Settings\n2. Add bank account or mobile money details\n3. Get paid within 24 hours after service completion\n4. Track all earnings in your dashboard\n5. Withdraw funds whenever you want\n\n**Fees:**\n• Clients: No fees! You pay only the service price\n• Providers: Small platform fee (5-10%) on completed bookings\n• Completely transparent - no hidden charges\n• You see the exact fee before confirming\n\n**Security:**\n🔒 End-to-end encryption\n🔒 PCI compliant payment processing\n🔒 Fraud detection systems\n🔒 Secure data storage"
                },
                'subscriptions': {
                    'patterns': ['subscription', 'premium', 'plan', 'upgrade', 'downgrade', 'billing', 'subscribe', 'membership', 'netra pro'],
                    'response': "Netra offers flexible plans for different needs:\n\n**Free Plan** (Always Free)\n✓ Basic profile\n✓ Search and browse services\n✓ Message providers\n✓ Standard support\n✓ Leave reviews\n\n**Provider Pro** (For Service Providers)\n✓ Featured listings in search results\n✓ Advanced analytics dashboard\n✓ Priority customer support\n✓ Verified badge on profile\n✓ More visibility (appear higher in searches)\n✓ Access to premium categories\n\n**Business Plan** (For Companies & Agencies)\n✓ Multiple team accounts\n✓ Custom branding options\n✓ API access for integrations\n✓ Dedicated account manager\n✓ Bulk booking tools\n✓ Advanced reporting\n\n**How to Subscribe:**\n1. Open Netra app\n2. Go to Settings > Subscription\n3. Browse available plans\n4. Choose your plan\n5. Select payment method (monthly or annual)\n6. Confirm subscription\n\n**Managing Your Plan:**\n• Upgrade anytime - get new features immediately\n• Downgrade takes effect next billing cycle\n• Cancel anytime - no long-term contracts\n• View billing history in Settings\n\n**Billing:**\n• Monthly or annual billing options\n• Automatic renewal (can be turned off)\n• Email receipts for all transactions\n• Download invoices from your account\n\n**Annual Plans:** Save up to 20% compared to monthly!"
                },
                'refunds': {
                    'patterns': ['refund', 'money back', 'get refund', 'cancel payment', 'dispute', 'return money', 'refund policy'],
                    'response': "Netra has a fair refund policy to protect both clients and providers:\n\n**When You Can Get a Refund:**\n• Provider cancels on short notice (less than 24 hours)\n• Service not delivered as agreed upon\n• Quality issues with the completed service\n• Provider doesn't show up\n• Technical problems with payment (double charges)\n• Service is significantly different from description\n\n**How to Request a Refund:**\n1. First, contact the provider directly to resolve the issue\n2. If no resolution within 48 hours, go to the booking in the app\n3. Tap 'Report an Issue' or 'Request Refund'\n4. Select the reason for your request\n5. Provide details and any evidence (photos, messages)\n6. Submit the request\n7. Our support team will review within 24-48 hours\n8. You'll get email updates on the status\n\n**Refund Timeline:**\n• Approved refunds process in 3-5 business days\n• Mobile Money refunds are usually instant\n• Card refunds depend on your bank (5-10 days)\n• Bank transfers take 2-3 business days\n\n**Dispute Resolution:**\nIf you disagree with a decision, you can:\n• Appeal by emailing disputes@strobid.com\n• Provide additional evidence\n• Request a support supervisor review\n\nFor urgent disputes, contact disputes@strobid.com with your booking details."
                },
                'payment_methods': {
                    'patterns': ['payment methods', 'accepted payments', 'how to pay', 'mobile money', 'credit card', 'debit card', 'mtn', 'airtel'],
                    'response': "Netra accepts multiple payment methods to make it convenient for everyone:\n\n**Accepted Payment Methods:**\n\n💳 **Cards**\n• Visa\n• Mastercard\n• American Express\n• Verve\n\n📱 **Mobile Money**\n• MTN Mobile Money (MoMo)\n• Airtel Money\n• M-PESA\n\n🏦 **Bank Transfers**\n• Direct bank transfers\n• Instant EFT\n\n💵 **Cash**\n• Cash payments (with provider approval)\n• Only for in-person services\n\n**How to Add a Payment Method:**\n1. Go to Settings > Payments\n2. Tap 'Add Payment Method'\n3. Choose your preferred method\n4. Enter the required details\n5. Save for future use\n\n**Default Payment Method:**\nYou can set a default payment method for faster checkout\n\n**Security:**\nAll payment methods are encrypted and securely stored. We never share your full payment details with providers."
                }
            },
            'settings': {
                'notifications': {
                    'patterns': ['notification', 'alert', 'notifications', 'push notification', 'turn off notifications', 'manage alerts', 'notification settings', 'stop notifications'],
                    'response': "Stay in control of your notifications! Here's how to manage them:\n\n**In the App:**\n1. Open Netra\n2. Go to Settings\n3. Tap 'Notifications'\n4. Toggle each type on/off:\n\n**Notification Types:**\n🔔 **New Messages** - When someone messages you\n🔔 **Booking Updates** - Confirmations, reminders, changes\n🔔 **Payment Notifications** - Payments, refunds, receipts\n🔔 **New Reviews** - When someone reviews your service\n🔔 **Promotional Offers** - Special deals and updates\n🔔 **System Alerts** - App updates, security notices\n\n**On Your Phone (System Settings):**\n• **Android:** Settings > Apps > Netra > Notifications\n• **iPhone:** Settings > Notifications > Netra\n\n**Recommended Settings:**\n✅ Keep message notifications ON so you don't miss conversations\n✅ Set quiet hours (e.g., 10 PM - 7 AM) for undisturbed sleep\n✅ Turn off promotional notifications if you prefer fewer alerts\n✅ Keep booking updates ON to never miss a client\n\n**Not Getting Notifications?**\n• Check if notifications are enabled in both app and phone settings\n• Ensure your phone isn't in Do Not Disturb mode\n• Check your internet connection\n• Update to the latest app version\n• Restart your phone\n\n**Email Notifications:**\nYou can also manage email notifications in Settings > Email Preferences"
                },
                'privacy': {
                    'patterns': ['privacy', 'private', 'data', 'security', 'secure', 'safe', 'personal information', 'data protection'],
                    'response': "Netra takes your privacy seriously! Here are our key security features:\n\n**Security Features:**\n🔒 **Screenshot Protection** - No one can screenshot your conversations or profile\n🔒 **Screen Recording Blocked** - Screen recording is automatically blocked in the app\n🔒 **End-to-End Encryption** - Your messages are private and can't be read by others\n🔒 **Secure Payment Processing** - All payments are PCI compliant\n🔒 **Data Encryption** - Your data is encrypted both in transit and at rest\n🔒 **Two-Factor Authentication** - Extra security for your account (optional)\n\n**Privacy Protections:**\n• Your personal info is never shared without consent\n• You control what appears on your profile\n• Conversation history is private to you and the provider\n• Payment details are securely stored\n• You can request your data anytime\n\n**Data We Collect:**\n• Account information (name, email, phone)\n• Profile details and photos\n• Service history and bookings\n• Payment information (securely stored)\n• App usage data (to improve the app)\n\n**How We Use Your Data:**\n• To provide and improve services\n• To process payments\n• To communicate with you\n• To prevent fraud\n• To comply with legal requirements\n\n**Tips to Stay Safe:**\n✓ Never share your password with anyone\n✓ Verify providers through the app before meeting\n✓ Report suspicious behavior immediately\n✓ Keep your app updated for latest security patches\n✓ Use a strong, unique password\n✓ Enable two-factor authentication\n\n**Your Rights:**\n• Request a copy of your data\n• Delete your account anytime\n• Opt out of marketing emails\n• Update your privacy settings\n\nFor privacy concerns, email privacy@strobid.com"
                },
                'profile': {
                    'patterns': ['edit profile', 'change photo', 'update profile', 'profile picture', 'bio', 'about me', 'profile settings'],
                    'response': "Want to update your profile? Here's how:\n\n**Edit Profile Info:**\n1. Open Netra app\n2. Go to your Profile (tap your avatar)\n3. Tap 'Edit Profile'\n4. Update your information:\n   • Profile photo\n   • Display name\n   • Bio/About me\n   • Contact info\n   • Location\n   • Services offered (for providers)\n5. Tap 'Save Changes'\n\n**Profile Photo Tips:**\n📸 Use a clear, professional photo\n📸 Face should be clearly visible\n📸 Good lighting helps\n📸 Avoid group photos\n📸 Keep it appropriate\n\n**For Providers:**\nAdd photos of your work to attract more clients!\n\n**Privacy:**\nYou control what information is public. Some info (like your name and photo) is always visible to help build trust."
                }
            },
            'services': {
                'provider_info': {
                    'patterns': ['become provider', 'offer services', 'list my service', 'service provider', 'professional', 'join as provider', 'sell services', 'offer my skills'],
                    'response': "Want to offer your services on Netra? Great choice! Here's everything you need to know:\n\n**Provider Registration Steps:**\n1. Create a regular Netra account first (if you haven't already)\n2. Go to Settings > 'Become a Provider'\n3. Choose your service category\n4. Fill out your professional details:\n   • Service description (be detailed!)\n   • Years of experience\n   • Service area/location (where you operate)\n   • Pricing (hourly rates or fixed prices)\n   • Availability (days and hours)\n   • Portfolio photos of your work (highly recommended)\n5. Complete identity verification (may need ID)\n6. Submit for review\n7. Wait for approval (usually 24-48 hours)\n\n**What You'll Need Ready:**\n✓ Professional photos of your work\n✓ Clear description of your services\n✓ Your pricing structure\n✓ Service area/locations\n✓ Valid ID for verification\n✓ Any professional certifications\n\n**Service Categories:**\nYou can offer services in many categories:\n• Home Services (plumbing, electrical, cleaning)\n• Professional Services (tutoring, consulting)\n• Creative Services (photography, design)\n• Beauty & Wellness (hair, makeup, fitness)\n• Music & Entertainment (DJ, musician)\n• And many more!\n\n**Tips for Success:**\n📸 **Photos Matter** - Add high-quality photos of your work\n⭐ **Get Reviews** - Encourage happy clients to leave reviews\n💬 **Respond Quickly** - Fast responses lead to more bookings\n📅 **Stay Updated** - Keep your availability current\n💰 **Price Fairly** - Competitive pricing attracts clients\n👍 **Be Professional** - Good communication builds trust\n\n**Provider Benefits:**\n✓ Reach more clients in your area\n✓ Build your professional reputation\n✓ Get verified badge\n✓ Appear in search results\n✓ Access provider analytics\n✓ Priority support\n\nOnce approved, you'll get a verified badge and start appearing in search results!"
                },
                'booking': {
                    'patterns': ['book service', 'how to book', 'hire provider', 'schedule service', 'make booking', 'book appointment', 'reserve service'],
                    'response': "Booking a service on Netra is easy! Here's a complete guide:\n\n**Step-by-Step Booking Process:**\n\n1. **Find a Provider**\n   • Browse the 'For You' page\n   • Search by service category\n   • Search by location\n   • Search by provider name\n\n2. **Check Provider Details**\n   • View their profile\n   • Read reviews and ratings\n   • Check their portfolio photos\n   • Verify their experience\n   • See their pricing\n\n3. **Start the Booking**\n   • Tap 'Book Now' or 'Contact'\n   • Select the specific service you need\n   • Choose date and time\n   • Add any special instructions\n   • Review the total price\n\n4. **Confirm Booking**\n   • Some providers may require a deposit\n   • Confirm the booking\n   • You'll get a confirmation notification\n   • Provider will confirm or may suggest alternative times\n\n5. **Communicate**\n   • Message the provider through the app\n   • Discuss any details\n   • Confirm meeting location/virtual call details\n   • Ask any questions\n\n6. **After Service**\n   • Rate your experience\n   • Leave a review\n   • Tip if you want (optional)\n   • Book again!\n\n**Booking Tips:**\n• Read reviews carefully before booking\n• Be clear about what you need\n• Confirm pricing upfront (including any extra fees)\n• Keep all communication in the app (for your protection)\n• Arrive on time or join virtual calls promptly\n• Communicate any changes immediately\n\n**Need to Change a Booking?**\n• You can reschedule through the app (check provider's policy)\n• Cancel if needed (cancellation fees may apply)\n• Contact provider directly for urgent changes\n\n**Cancellation Policy:**\n• Free cancellation up to 24 hours before\n• Late cancellation may incur a fee\n• Providers can also cancel (rare)\n• Refunds processed according to policy"
                },
                'ratings': {
                    'patterns': ['rating', 'review', 'rate provider', 'leave review', 'feedback', 'star rating', 'write review', 'rate service'],
                    'response': "Ratings and reviews help everyone in the Netra community! Here's how they work:\n\n**Leaving a Review (for Clients):**\n1. After service completion, you'll get a notification\n2. Go to the booking in your history\n3. Tap 'Rate Your Experience'\n4. Give a star rating (1-5 stars):\n   ⭐ - Poor\n   ⭐⭐ - Fair\n   ⭐⭐⭐ - Good\n   ⭐⭐⭐⭐ - Very Good\n   ⭐⭐⭐⭐⭐ - Excellent\n5. Write a brief review (optional but very helpful)\n6. Add photos of the completed work (optional)\n7. Submit - your review will appear on their profile\n\n**What to Include in Your Review:**\n✓ Quality of work/service\n✓ Punctuality and professionalism\n✓ Communication\n✓ Value for money\n✓ Would you recommend them?\n✓ Any specific highlights\n\n**For Providers (Managing Reviews):**\n• Good ratings help you get more clients\n• Respond professionally to any feedback\n• Thank clients for positive reviews\n• Address concerns in negative reviews professionally\n• High-rated providers appear first in searches\n• You can report fake or inappropriate reviews\n\n**Rating System Benefits:**\n✅ Helps clients find quality providers\n✅ Encourages providers to deliver excellent service\n✅ Builds trust in the community\n✅ Provides honest feedback\n✅ Rewards quality work\n\n**Review Guidelines:**\n• Be honest and fair\n• Focus on the service, not personal attacks\n• Don't include personal contact info\n• Reviews are anonymous but helpful\n• Fake reviews are removed\n\n**Disputing a Review:**\nIf you believe a review is fake or violates guidelines:\n1. Go to the review\n2. Tap 'Report'\n3. Select reason\n4. Provide explanation\n5. Our team will review within 48 hours\n\nRemember: Your feedback helps others make informed decisions!"
                },
                'search': {
                    'patterns': ['search', 'find provider', 'find service', 'search by category', 'search by location', 'find near me', 'services near me'],
                    'response': "Finding the right service provider on Netra is easy! Here are all the ways to search:\n\n**Search Methods:**\n\n🔍 **By Provider Name**\n• Type their name in the search bar\n• Great if you already know who you want\n\n📋 **By Service Category**\n• Browse categories like:\n  - Plumbing & Electrical\n  - Cleaning Services\n  - Tutoring & Lessons\n  - Photography & Videography\n  - Beauty & Wellness\n  - Music & Entertainment\n  - And many more!\n\n📍 **By Location**\n• Search for providers in your area\n• Find services near you\n• Specify distance (1km, 5km, 10km, etc.)\n\n⭐ **By Rating**\n• Filter by minimum rating (4+ stars)\n• See top-rated providers first\n\n💰 **By Price**\n• Filter by price range\n• Find services in your budget\n\n**Search Tips:**\n• Use specific keywords (e.g., 'plumber' not just 'services')\n• Try different categories\n• Expand your search radius if needed\n• Check provider profiles before booking\n• Read reviews to verify quality\n\n**'For You' Page:**\nThe homepage shows personalized recommendations based on:\n• Your search history\n• Your location\n• Popular providers in your area\n• Services you've viewed\n\n**Filters Available:**\n✓ Category\n✓ Location/Distance\n✓ Rating (minimum stars)\n✓ Price range\n✓ Availability\n✓ Verified providers only\n✓ New providers\n\n**Can't Find What You Need?**\n• Try broader search terms\n• Increase your search radius\n• Check back later - new providers join daily\n• Contact support for recommendations\n\nPro tip: Save your favorite providers for quick access next time!"
                }
            },
            'features': {
                'music': {
                    'patterns': ['music', 'streaming', 'artist', 'dj', 'mixtape', 'song', 'audio', 'playlist', 'music feature'],
                    'response': "Netra's music features are awesome for artists and music lovers! Here's what you can do:\n\n**For Artists:**\n🎵 **Artist Studio**\n• Upload your original music\n• Create your artist profile\n• Share your songs with the community\n• Get discovered by new fans\n• Connect with event organizers\n\n**For DJs:**\n🎧 **DJ Studio**\n• Upload your mixtapes and mixes\n• Showcase your mixing skills\n• Build a following\n• Get booked for events\n• Share your DJ sets\n\n**For Music Lovers:**\n🎶 **Listen & Discover**\n• Stream music from local artists\n• Discover new talent in your area\n• Create playlists\n• Follow your favorite artists\n• Share music with friends\n• Attend local music events\n\n**Features:**\n• High-quality audio streaming\n• Create and share playlists\n• Like and comment on tracks\n• Follow artists\n• Get notifications when new music drops\n• Share tracks on social media\n\n**For Event Organizers:**\n• Find local talent for events\n• Contact artists directly\n• Check their popularity and following\n• Book through the app\n\n**Getting Started:**\n1. Go to the Music section in the app\n2. Browse featured artists\n3. Search for specific genres\n4. Start listening!\n\nWhether you're an artist, DJ, or just love music, Netra's music features connect you with amazing local talent!"
                },
                'reels': {
                    'patterns': ['reels', 'short videos', 'video showcase', 'pro reels', 'video portfolio', 'showcase work'],
                    'response': "Netra Reels let professionals showcase their work through short videos! Here's how they work:\n\n**What are Reels?**\nShort, engaging videos (15-60 seconds) where professionals can:\n• Showcase their work in action\n• Demonstrate their skills\n• Share before/after transformations\n• Introduce themselves\n• Share tips and tutorials\n\n**For Providers:**\n📹 **Create Reels**\n• Show your work in progress\n• Share completed projects\n• Demonstrate your expertise\n• Add music and effects\n• Reach more potential clients\n\n**Benefits of Reels:**\n✓ More engaging than photos\n✓ Show your personality\n✓ Demonstrate your skills\n✓ Stand out from competitors\n✓ Appear in the Reels feed\n✓ Get more views and bookings\n\n**How to Create a Reel:**\n1. Go to your profile\n2. Tap '+' or 'Create Reel'\n3. Record or upload video\n4. Add music (from Netra's library)\n5. Add text and effects\n6. Publish to your profile\n\n**For Clients:**\n👀 **Watch Reels**\n• See providers in action\n• Get a feel for their work quality\n• Watch before/after results\n• Discover new providers\n• Save reels to watch later\n\n**Reels Tips:**\n🎥 Good lighting matters\n🎥 Keep it focused on your work\n🎥 Add captions for clarity\n🎥 Show your best work\n🎥 Be authentic\n🎥 Post regularly\n\nThe Reels feed appears on the home page, giving your work more visibility!"
                }
            },
            'technical': {
                'app_issues': {
                    'patterns': ['app not working', 'app crashing', 'technical issue', 'bug', 'glitch', 'not loading', 'error message', 'app freezes'],
                    'response': "Having technical issues with the app? Let's troubleshoot:\n\n**Common Solutions:**\n\n1. **Restart the App**\n   • Close it completely\n   • Reopen after a few seconds\n\n2. **Restart Your Phone**\n   • Sometimes a simple restart fixes everything\n\n3. **Check Internet Connection**\n   • Switch between WiFi and mobile data\n   • Test if other apps work\n\n4. **Clear App Cache**\n   • Android: Settings > Apps > Netra > Clear Cache\n   • iPhone: Offload app and reinstall\n\n5. **Update the App**\n   • Check Play Store/App Store for updates\n   • Install latest version\n\n6. **Reinstall the App**\n   • Uninstall, then reinstall from store\n   • Don't worry - your data is safe online\n\n**Specific Issues:**\n\n📱 **App Crashes on Open**\n• Clear cache\n• Update app\n• Reinstall if needed\n\n🔐 **Login Problems**\n• Check internet\n• Reset password\n• Clear app data\n\n💬 **Messages Not Sending**\n• Check internet\n• Restart app\n• Update app\n\n💰 **Payment Issues**\n• Check payment method\n• Contact support with transaction ID\n\n**Still Having Issues?**\nContact technical support:\n📧 Email: tech@strobid.com\n💬 In-app chat: Settings > Help & Support\n\nPlease include:\n• What happened\n• When it happened\n• Your phone model\n• App version (from Settings)\n• Screenshots if possible"
                },
                'update': {
                    'patterns': ['update app', 'new version', 'latest version', 'app update', 'how to update'],
                    'response': "Keeping Netra updated ensures you have the latest features and security fixes!\n\n**How to Update:**\n\n📱 **On Android:**\n1. Open Google Play Store\n2. Tap menu (three lines)\n3. Tap 'My apps & games'\n4. Find Netra in the list\n5. Tap 'Update' if available\n\n📱 **On iPhone:**\n1. Open App Store\n2. Tap your profile icon\n3. Scroll to pending updates\n4. Find Netra\n5. Tap 'Update'\n\n**Enable Auto-Update:**\n\n**Android:**\n• Play Store > Profile > Settings > Auto-update apps\n• Choose 'Over any network' or 'Over Wi-Fi only'\n\n**iPhone:**\n• Settings > App Store > App Updates (toggle on)\n\n**Why Update Regularly:**\n✅ New features and improvements\n✅ Security patches\n✅ Bug fixes\n✅ Better performance\n✅ Compatibility with new phones\n\n**Check Current Version:**\n• Go to Settings > About > App Version\n• Compare with latest version in store\n\n**Update Notes:**\nEach update includes release notes showing:\n• New features added\n• Improvements made\n• Bugs fixed\n• Known issues\n\n**Can't Update?**\n• Check internet connection\n• Ensure enough storage space\n• Restart your phone\n• Contact support if issues persist"
                }
            },
            'support': {
                'contact': {
                    'patterns': ['contact support', 'customer service', 'help desk', 'get help', 'support team', 'reach netra', 'talk to someone', 'live chat'],
                    'response': "Need personalized help? Our support team is here for you!\n\n**Contact Methods:**\n\n📧 **Email Support**\n• General inquiries: support@strobid.com\n• Technical issues: tech@strobid.com\n• Billing questions: billing@strobid.com\n• Privacy concerns: privacy@strobid.com\n• Disputes: disputes@strobid.com\n• Response time: Within 24 hours\n\n💬 **In-App Live Chat**\n1. Open Netra app\n2. Go to Settings\n3. Tap 'Help & Support'\n4. Tap 'Start Live Chat'\n5. Available 24/7 for urgent issues\n6. Get instant responses during business hours\n\n🌐 **Help Center**\n• Visit: https://netra.strobid.com/help\n• Browse hundreds of articles\n• Search for solutions\n• Video tutorials\n• Step-by-step guides\n• FAQ section\n\n📱 **Social Media**\n• Twitter: @NetraApp\n• Facebook: /NetraOfficial\n• Instagram: @netra_app\n• DM for quick questions\n\n🏢 **Office Location**\nStrobid Headquarters\nKampala, Uganda\nEast Africa\n\n**Support Hours:**\nMonday - Friday: 8:00 AM - 8:00 PM (EAT)\nSaturday: 9:00 AM - 5:00 PM (EAT)\nSunday: Closed\nHolidays: Limited support\n\n**Before Contacting Support:**\n✅ Check the Help Center first - your answer might be there!\n✅ Have your account info ready (email, username)\n✅ Know your app version (Settings > About)\n✅ Take screenshots if it's a technical issue\n✅ Describe your issue clearly and step-by-step\n✅ Include relevant booking/transaction IDs\n\n**Common Support Topics:**\n• Account access issues\n• Payment problems\n• Technical glitches\n• Provider verification\n• Report inappropriate behavior\n• Feature requests\n• Feedback and suggestions\n\n**Emergency Support:**\nFor urgent issues like:\n• Security concerns\n• Account hacked\n• Fraudulent activity\n• Payment disputes\n\nEmail: security@strobid.com\nSubject line: \"URGENT - [Brief Description]\"\n\n**Response Times:**\n• Live Chat: Immediate during hours\n• Email: 24 hours\n• Social Media: 24-48 hours\n• Urgent issues: 4-6 hours\n\n**We're Here to Help!**\nOur team responds to all inquiries within 24 hours. For faster service, use the in-app chat feature.\n\nThank you for being part of the Netra community! 🌟"
                },
                'faq': {
                    'patterns': ['faq', 'frequently asked', 'common questions', 'quick help'],
                    'response': "Here are answers to frequently asked questions about Netra:\n\n**General Questions:**\n\n❓ **Is Netra free?**\nYes! Netra is free to download and use. Providers pay a small commission only when they successfully complete a booking.\n\n❓ **Where is Netra available?**\nCurrently available in Uganda, with plans to expand across East Africa soon!\n\n❓ **Do I need an account to browse?**\nNo, you can browse services without an account! You only need an account to book or message providers.\n\n**Account Questions:**\n\n❓ **How do I reset my password?**\nTap 'Forgot Password' on login screen and follow the email instructions.\n\n❓ **Can I have multiple accounts?**\nNo, please maintain one account per person. Multiple accounts may be suspended.\n\n❓ **How do I delete my account?**\nGo to Settings > Account > Delete Account. This is permanent!\n\n**Payment Questions:**\n\n❓ **What payment methods are accepted?**\nCards (Visa, Mastercard), Mobile Money (MTN, Airtel), and bank transfers.\n\n❓ **How do I get a refund?**\nGo to the booking, tap 'Report an Issue', and follow the refund request process.\n\n❓ **When do providers get paid?**\nWithin 24 hours after service completion.\n\n**Service Questions:**\n\n❓ **How do I become a provider?**\nGo to Settings > Become a Provider and complete the registration process.\n\n❓ **How do I leave a review?**\nAfter service completion, you'll get a notification to rate your experience.\n\n❓ **Can I change a booking?**\nYes! You can reschedule or cancel through the app (check provider's policy).\n\n**Technical Questions:**\n\n❓ **Why is the app crashing?**\nTry clearing cache, updating the app, or reinstalling. Contact support if issues persist.\n\n❓ **How do I update the app?**\nCheck your device's app store for the latest version.\n\n❓ **Is my data safe?**\nYes! We use encryption and have strict privacy policies. No screenshots allowed in the app.\n\n**Need more help?**\nVisit our Help Center at https://netra.strobid.com/help or contact support@strobid.com"
                }
            }
        }
        
        # Conversation starters for natural responses
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
            "Happy to help! ",
            "I can definitely help with that! ",
            "Great question! Here's what you need to know: "
        ]
        
        self.friendly_closers = [
            "\n\nHope that helps! 😊",
            "\n\nLet me know if you have other questions!",
            "\n\nPretty cool, right?",
            "\n\nMakes sense?",
            "\n\nEasy enough?",
            "\n\nGot it?",
            "\n\nClear?",
            "\n\nSound good?",
            "\n\nAwesome, right?",
            "\n\nNeat, huh?",
            "\n\nPretty straightforward!",
            "\n\nSimple as that!",
            "\n\nThat's the gist of it!",
            "\n\nAny other questions?",
            "\n\nHappy to explain more if needed!",
            "\n\nWas that helpful?",
            "\n\nGlad I could help!",
            "\n\nLet me know if you need anything else!"
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
            "Wonderful! ",
            "Love it! ",
            "Amazing! ",
            "Excellent question! ",
            "Great question! "
        ]
        
        self.understanding_phrases = [
            "I see what you mean! ",
            "Got it! ",
            "Ah, good question! ",
            "I understand! ",
            "Makes sense! ",
            "Right on! ",
            "Totally! ",
            "For sure! ",
            "Absolutely! ",
            "You got it! "
        ]

    def _get_random_opener(self) -> str:
        """Get random conversation opener"""
        return random.choice(self.conversation_starters)

    def _get_random_closer(self) -> str:
        """Get random friendly closer"""
        return random.choice(self.friendly_closers)

    def _get_random_reaction(self) -> str:
        """Get random positive reaction"""
        return random.choice(self.positive_reactions)
    
    def _get_understanding(self) -> str:
        """Get random understanding phrase"""
        return random.choice(self.understanding_phrases)

    def _find_knowledge(self, message: str) -> Optional[Dict]:
        """Find relevant knowledge based on message patterns"""
        message_lower = message.lower()
        
        best_match = None
        best_score = 0
        matched_category = None
        matched_key = None
        matched_response = None
        
        # Search through knowledge base
        for category, topics in self.knowledge_base.items():
            for key, knowledge in topics.items():
                for pattern in knowledge['patterns']:
                    # Check if pattern matches
                    if pattern in message_lower:
                        # Calculate match score based on pattern length and message length
                        score = len(pattern) / max(len(message_lower), 1)
                        # Bonus for exact matches
                        if message_lower == pattern:
                            score = 1.0
                        if score > best_score:
                            best_score = score
                            matched_response = knowledge['response']
                            matched_category = category
                            matched_key = key
        
        if matched_response:
            return {
                'response': matched_response,
                'category': matched_category,
                'key': matched_key,
                'confidence': int(best_score * 100)
            }
        
        return None

    def _get_follow_up_suggestions(self, category: str, key: str) -> List[str]:
        """Generate relevant follow-up suggestions based on context"""
        suggestion_map = {
            'general': [
                "What is Netra?",
                "How does Netra work?",
                "Who can use Netra?",
                "Is Netra free?"
            ],
            'account': [
                "How do I create an account?",
                "How to verify my account",
                "I forgot my password",
                "How to delete my account",
                "Login issues"
            ],
            'payments': [
                "How do payments work?",
                "What payment methods are accepted?",
                "Subscription plans",
                "How to request a refund",
                "When do providers get paid?"
            ],
            'settings': [
                "How to manage notifications",
                "Privacy and security",
                "How to edit my profile",
                "Change profile photo"
            ],
            'services': [
                "How to become a provider",
                "How to book a service",
                "How to leave a review",
                "How to search for services",
                "Service categories"
            ],
            'features': [
                "Music streaming features",
                "How to create reels",
                "Artist Studio",
                "DJ Studio"
            ],
            'technical': [
                "App not working",
                "How to update the app",
                "Clear app cache",
                "Technical support"
            ],
            'support': [
                "How to contact support",
                "Live chat",
                "Email support",
                "Help Center",
                "FAQ"
            ]
        }
        
        # Get suggestions for the category
        suggestions = suggestion_map.get(category, suggestion_map['general'])
        
        # Return random selection of suggestions (up to 4)
        num_suggestions = min(4, len(suggestions))
        return random.sample(suggestions, num_suggestions)

    def process_query(self, message: str, user_id: str = None) -> Dict[str, Any]:
        """
        Main method to process user queries using knowledge base
        
        Args:
            message: User's message
            user_id: Optional user identifier
        
        Returns:
            Dict containing response and metadata
        """
        try:
            # Find relevant knowledge
            knowledge = self._find_knowledge(message)
            
            if knowledge:
                # Get response from knowledge base
                response = knowledge['response']
                category = knowledge['category']
                key = knowledge['key']
                confidence = knowledge['confidence']
                
                # Add opener for natural feel (70% chance)
                if random.random() > 0.3:
                    response = self._get_random_opener() + response
                
                # Add closer for natural feel (60% chance)
                if random.random() > 0.4:
                    response += self._get_random_closer()
                
                # Get relevant suggestions
                suggestions = self._get_follow_up_suggestions(category, key)
                
                # Add help center reference occasionally (30% chance)
                if random.random() > 0.7:
                    response += f"\n\n📚 For more details, visit our Help Center: {self.help_center_url}"
                
            else:
                # No specific knowledge found - use general response
                general_responses = [
                    f"{self._get_random_opener()}I'd be happy to help you with Netra! What specific aspect are you interested in? You can ask about accounts, payments, services, settings, or features.",
                    
                    f"{self._get_understanding()}I want to make sure you get the right information. Our Help Center at {self.help_center_url} has detailed guides on everything Netra. What would you like to know?",
                    
                    f"{self._get_random_reaction()}Netra is designed to connect service providers with clients seamlessly. To give you the best answer, could you tell me more about what you need help with? For example:\n\n• Creating an account\n• Making payments\n• Booking services\n• Becoming a provider\n• Music features\n• Technical issues\n• Contacting support",
                    
                    f"I'm here to help with anything about Netra! Whether you're a client looking for services, a provider wanting to grow your business, or just curious about the app - just ask! Try asking about:\n\n📱 Account setup\n💰 Payments & subscriptions\n🔍 Finding services\n⭐ Reviews & ratings\n🎵 Music features\n🆘 Technical support"
                ]
                response = random.choice(general_responses)
                confidence = 70
                suggestions = [
                    "What is Netra?",
                    "How to create an account",
                    "How payments work",
                    "Become a provider",
                    "Contact support"
                ]
            
            # Return formatted response
            return {
                'response': response,
                'suggestions': suggestions[:4],  # Limit to 4 suggestions
                'confidence': confidence,
                'engine_used': 'netra_engine',
                'help_center_url': self.help_center_url,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Netra Engine error: {e}")
            # Fallback error response
            return {
                'response': f"{self._get_random_reaction()}I'm here to help with Netra! While I'm having a quick technical moment, you can always visit our Help Center at {self.help_center_url} for accurate information. What would you like to know about Netra?",
                'suggestions': [
                    "What is Netra?",
                    "How to create an account",
                    "How payments work",
                    "Contact support"
                ],
                'confidence': 80,
                'engine_used': 'netra_engine',
                'help_center_url': self.help_center_url,
                'timestamp': datetime.now().isoformat()
            }

# Create the instance
netra_engine = HumanizedNetraEngine()