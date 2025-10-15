import random
from datetime import datetime

class NetraEngine:
    def __init__(self):
        self.company_info = {
            'name': 'AidNest Africa',
            'contact': {
                'primary_email': 'support@myaidnest.com',
                'technical_email': 'tech@myaidnest.com',
                'phone': '+254-700-123-456',
                'emergency_phone': '+254-711-987-654'
            }
        }

        self.greetings = [
            "Hello! I’m Jovira, your AidNest Africa assistant. How can I help you today?",
            "Hi there! Jovira at your service. What do you need help with in Netra?"
        ]

        self.farewells = [
            "Thank you for choosing AidNest Africa! Have a great day!",
            "We’re here if you need further assistance!"
        ]

        # Main menu options
        self.main_menu = {
            1: "Delete my account",
            2: "Edit my profile",
            3: "Book a service provider",
            4: "Reschedule or cancel a booking",
            5: "Autra integration help",
            6: "Technical support",
            7: "Billing inquiries",
            8: "Network/Internet issues",
            9: "Software issues",
            10: "Hardware issues"
        }

        # Booking submenu
        self.booking_menu = {
            1: "New booking",
            2: "Reschedule booking",
            3: "Cancel booking",
            4: "Back to main menu"
        }

        # Knowledge base for step guidance
        self.knowledge_base = {
            'delete_account': [
                "Go to Settings in Netra.",
                "Scroll to the bottom.",
                "Tap 'Delete Account' and confirm."
            ],
            'edit_profile': [
                "Go to Settings → Edit Profile.",
                "Update name, email, phone, and bio.",
                "Ensure your details are correct for verification."
            ],
            'booking_new': [
                "Ensure you have a verified Autra account.",
                "Open the service provider's profile in Netra.",
                "Tap 'Bookings'.",
                "Verify your Autra username.",
                "Select time slot and confirm booking."
            ],
            'booking_reschedule': [
                "Go to My Bookings → Upcoming.",
                "Select booking → choose Reschedule.",
                "Confirm new time slot."
            ],
            'booking_cancel': [
                "Go to My Bookings → Upcoming.",
                "Select booking → choose Cancel.",
                "Confirm cancellation."
            ],
            'autra_integration': [
                "Autra app handles provider registration, payments, and booking confirmation.",
                "Users must verify their Autra accounts before booking services."
            ],
            'technical_support': [
                "Describe the technical issue you’re facing.",
                "Provide device model and software version."
            ],
            'billing_inquiries': [
                "Please provide your invoice number or payment details.",
                "Our accounts team will get back to you within 24 hours."
            ]
        }

    def start_conversation(self):
        return random.choice(self.greetings) + "\n" + self.display_main_menu()

    def display_main_menu(self):
        menu_text = "Please select the option that best describes your issue:\n"
        for key, value in self.main_menu.items():
            menu_text += f"{key}. {value}\n"
        return menu_text

    def display_booking_menu(self):
        menu_text = "Booking Options:\n"
        for key, value in self.booking_menu.items():
            menu_text += f"{key}. {value}\n"
        return menu_text

    def handle_main_menu_selection(self, selection):
        if selection == 1:
            return self.knowledge_base['delete_account']
        elif selection == 2:
            return self.knowledge_base['edit_profile']
        elif selection == 3:
            return self.display_booking_menu()
        elif selection == 4:
            return self.knowledge_base['booking_reschedule'] + self.knowledge_base['booking_cancel']
        elif selection == 5:
            return self.knowledge_base['autra_integration']
        elif selection == 6:
            return self.knowledge_base['technical_support']
        elif selection == 7:
            return self.knowledge_base['billing_inquiries']
        else:
            return ["Sorry, I didn’t understand. Please choose a valid option or type 'live' for assistance."]

    def handle_booking_menu_selection(self, selection):
        if selection == 1:
            return self.knowledge_base['booking_new']
        elif selection == 2:
            return self.knowledge_base['booking_reschedule']
        elif selection == 3:
            return self.knowledge_base['booking_cancel']
        elif selection == 4:
            return self.display_main_menu()
        else:
            return ["Invalid selection. Please choose again."]

    def escalate_to_live(self):
        return [
            "You are now connected to Jovira live chat.",
            "If I am unable to assist, I will escalate you to our top technical support team.",
            "Contact: tech@myaidnest.com | Phone: +254-700-123-456"
        ]
