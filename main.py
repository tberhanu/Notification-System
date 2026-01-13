"""
Notification System - Main Entry Point
Uses in-memory repository for development/testing
"""
from notification_system import NotificationSystem
from models import NotificationChannel, NotificationEvent

# Sample user data
USERS_DATA = {
    1: {
        'email': 'alice@example.com',
        'phone': '+1234567890',
        'ios_token': 'ios_alice_token',
        'android_token': 'android_alice_token',
    },
    2: {
        'email': 'bob@example.com',
        'phone': '+0987654321',
        'ios_token': 'ios_bob_token',
        'android_token': None,
    },
    3: {
        'email': 'charlie@example.com',
        'phone': '+1122334455',
        'ios_token': None,
        'android_token': 'android_charlie_token',
    },
}

# Sample notification events
SAMPLE_EVENTS = [
    NotificationEvent(user_id=1, channel=NotificationChannel.EMAIL, message="Welcome Alice!"),
    NotificationEvent(user_id=2, channel=NotificationChannel.SMS, message="Hello Bob!"),
    NotificationEvent(user_id=3, channel=NotificationChannel.IOS, message="Welcome Charlie!"),
    NotificationEvent(user_id=2, channel=NotificationChannel.ANDROID, message="Android notification for Bob"),
    NotificationEvent(user_id=1, channel=NotificationChannel.ANDROID, message="Android notification for Alice"),
    NotificationEvent(user_id=2, channel=NotificationChannel.EMAIL, message="Email for Bob (disabled)"),
    NotificationEvent(user_id=3, channel=NotificationChannel.SMS, message="SMS for Charlie (disabled)"),
]

if __name__ == "__main__":
    # Create system with in-memory repository
    system = NotificationSystem.create_with_in_memory(USERS_DATA)

    # Configure user preferences
    # Disable email for user 2
    system.user_repo.set_channel_preference(2, NotificationChannel.EMAIL, False)

    # Disable SMS for user 3
    system.user_repo.set_channel_preference(3, NotificationChannel.SMS, False)

    # Set quiet hours for user 1 SMS (22:00 - 08:00)
    system.user_repo.set_quiet_hours(1, NotificationChannel.SMS, "22:00", "08:00")

    # Run the notification system
    system.run(SAMPLE_EVENTS)
