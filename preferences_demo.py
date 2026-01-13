# -----------------------------
# Demo: User Preferences
# This script demonstrates how to manage user notification preferences
# -----------------------------
from user_repository import UserRepository
from models import NotificationChannel


# Sample user data
USERS_DATA = {
    1: {
        "email": "alice@example.com",
        "phone": "+15550001",
        "ios_token": "ios_tok_1",
        "android_token": None,
    },
    2: {
        "email": "bob@example.com",
        "phone": "+15550002",
        "ios_token": None,
        "android_token": "and_tok_2",
    },
}


if __name__ == "__main__":
    print("=" * 60)
    print("User Preferences Demo")
    print("=" * 60)

    # Initialize repository
    repo = UserRepository(USERS_DATA)

    # --- Demo 1: View default preferences
    print("\n[1] Default Preferences for User 1:")
    print("-" * 60)
    prefs = repo.get_user_preferences(1)
    for channel, settings in prefs.items():
        print(f"  {channel}: {settings}")

    # --- Demo 2: Disable a channel
    print("\n[2] Disable Email for User 2:")
    print("-" * 60)
    repo.set_channel_preference(2, NotificationChannel.EMAIL, False)
    user2 = repo.get_user(2)
    print(f"  Email enabled: {user2.is_channel_enabled(NotificationChannel.EMAIL)}")
    print(f"  SMS enabled: {user2.is_channel_enabled(NotificationChannel.SMS)}")

    # --- Demo 3: Set quiet hours
    print("\n[3] Set Quiet Hours for User 1 SMS (22:00 - 08:00):")
    print("-" * 60)
    repo.set_quiet_hours(1, NotificationChannel.SMS, "22:00", "08:00")
    quiet_hours = repo.get_user_quiet_hours(1, NotificationChannel.SMS)
    print(f"  SMS Quiet Hours: {quiet_hours}")

    # --- Demo 4: Check multiple channels
    print("\n[4] User 2 Channel Status:")
    print("-" * 60)
    for channel in NotificationChannel:
        enabled = repo.is_channel_enabled_for_user(2, channel)
        print(f"  {channel.value.upper():10} - {'✓ Enabled' if enabled else '✗ Disabled'}")

    # --- Demo 5: Update preferences programmatically
    print("\n[5] Update User 1 Preferences (disable iOS):")
    print("-" * 60)
    repo.set_channel_preference(1, NotificationChannel.IOS, False)
    user1 = repo.get_user(1)
    print(f"  Email: {user1.is_channel_enabled(NotificationChannel.EMAIL)}")
    print(f"  SMS: {user1.is_channel_enabled(NotificationChannel.SMS)}")
    print(f"  iOS: {user1.is_channel_enabled(NotificationChannel.IOS)}")
    print(f"  Android: {user1.is_channel_enabled(NotificationChannel.ANDROID)}")

    # --- Demo 6: Full user preferences
    print("\n[6] Full User 2 Preferences:")
    print("-" * 60)
    user2_prefs = repo.get_user_preferences(2)
    import json
    print(json.dumps(user2_prefs, indent=2))

    print("\n" + "=" * 60)
    print("Demo completed!")
    print("=" * 60)
