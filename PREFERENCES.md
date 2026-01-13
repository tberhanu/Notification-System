# User Preferences Feature Documentation

## Overview

The notification system now includes a comprehensive user preferences management system that allows users to:

1. **Enable/Disable Notification Channels** - Control which channels they receive notifications on
2. **Set Quiet Hours** - Specify times when they don't want to receive notifications
3. **Configure General Preferences** - Control marketing, transactional, and general notification settings

## Features

### 1. Channel Control
Users can enable or disable any notification channel:
- Email
- SMS
- iOS Push
- Android Push

### 2. Quiet Hours
Set time ranges when notifications should not be sent (e.g., 22:00 - 08:00)

### 3. General Preferences
- `marketing` - Receive marketing/promotional notifications
- `transactional` - Receive transactional/system notifications
- `notifications` - Receive general notifications

## Default Preferences Structure

```python
{
    "email": {
        "enabled": True,
        "quiet_hours": {"start": None, "end": None}
    },
    "sms": {
        "enabled": True,
        "quiet_hours": {"start": None, "end": None}
    },
    "ios": {
        "enabled": True,
        "quiet_hours": {"start": None, "end": None}
    },
    "android": {
        "enabled": True,
        "quiet_hours": {"start": None, "end": None}
    },
    "general": {
        "marketing": True,
        "transactional": True,
        "notifications": True
    }
}
```

## Usage Examples

### Example 1: Define User with Custom Preferences

```python
USERS_DATA = {
    1: {
        "email": "user@example.com",
        "phone": "+1234567890",
        "ios_token": "ios_token_123",
        "android_token": "android_token_123",
        "preferences": {
            "email": {"enabled": True, "quiet_hours": {"start": None, "end": None}},
            "sms": {"enabled": False, "quiet_hours": {"start": None, "end": None}},  # SMS disabled
            "ios": {"enabled": True, "quiet_hours": {"start": "22:00", "end": "08:00"}},  # iOS with quiet hours
            "android": {"enabled": True, "quiet_hours": {"start": None, "end": None}},
            "general": {"marketing": False, "transactional": True, "notifications": True}  # No marketing
        }
    }
}
```

### Example 2: Modify Preferences Programmatically

```python
from user_repository import UserRepository
from models import NotificationChannel

repo = UserRepository(USERS_DATA)

# Disable email for user 1
repo.set_channel_preference(1, NotificationChannel.EMAIL, False)

# Set quiet hours for SMS (22:00 - 08:00)
repo.set_quiet_hours(1, NotificationChannel.SMS, "22:00", "08:00")

# Check if channel is enabled
is_enabled = repo.is_channel_enabled_for_user(1, NotificationChannel.EMAIL)

# Get all preferences for a user
preferences = repo.get_user_preferences(1)

# Get quiet hours for a specific channel
quiet_hours = repo.get_user_quiet_hours(1, NotificationChannel.SMS)
```

### Example 3: Check Preferences Before Dispatching

```python
from models import NotificationChannel, User

user = repo.get_user(user_id)

# Check if channel is enabled
if user.is_channel_enabled(NotificationChannel.EMAIL):
    # Send email
    pass
else:
    # Channel disabled - send to DLQ
    kafka_producer.send(DLQ_TOPIC, event)

# Check quiet hours
if user.has_quiet_hours(NotificationChannel.SMS):
    quiet_hours = user.get_quiet_hours(NotificationChannel.SMS)
    # Check if current time is within quiet hours
    # If yes, defer or skip the message
```

## Integration with Notification Service

The `NotificationService` automatically respects user preferences:

```python
def dispatch(self, event: NotificationEvent) -> bool:
    user = self.user_repo.get_user(event.user_id)
    
    # Check if channel is enabled for this user
    if not user.is_channel_enabled(channel):
        # Send to DLQ with reason
        kafka_producer.send(DLQ_TOPIC, {
            **event.to_dict(),
            "reason": f"{channel.value}_disabled"
        })
        return False
    
    # Continue with normal dispatch...
```

## API Reference

### User Model Methods

```python
# Check if a channel is enabled
user.is_channel_enabled(channel: NotificationChannel) -> bool

# Check if a channel has quiet hours configured
user.has_quiet_hours(channel: NotificationChannel) -> bool

# Get quiet hours for a channel
user.get_quiet_hours(channel: NotificationChannel) -> Optional[Dict]

# Enable or disable a channel
user.set_channel_preference(channel: NotificationChannel, enabled: bool) -> None

# Set quiet hours for a channel
user.set_quiet_hours(channel: NotificationChannel, start: Optional[str], end: Optional[str]) -> None
```

### UserRepository Methods

```python
# Enable/disable a channel for a user
repo.set_channel_preference(user_id: int, channel: NotificationChannel, enabled: bool) -> bool

# Set quiet hours for a user's channel
repo.set_quiet_hours(user_id: int, channel: NotificationChannel, start: Optional[str], end: Optional[str]) -> bool

# Get all preferences for a user
repo.get_user_preferences(user_id: int) -> Optional[Dict]

# Check if a channel is enabled for a user
repo.is_channel_enabled_for_user(user_id: int, channel: NotificationChannel) -> bool

# Get quiet hours for a user's channel
repo.get_user_quiet_hours(user_id: int, channel: NotificationChannel) -> Optional[Dict]
```

## Running the Preferences Demo

```bash
python preferences_demo.py
```

This will show:
1. Default preferences for a user
2. How to disable a channel
3. How to set quiet hours
4. How to check channel status
5. How to update preferences programmatically
6. Full preferences structure

## Data Flow with Preferences

```
NotificationEvent
    ↓
[User Lookup] → UserRepository
    ↓
[Check Channel Enabled?] → User.is_channel_enabled()
    ├─ YES → [Check Quiet Hours?] → User.has_quiet_hours()
    │   ├─ YES → [Check Current Time] → Defer/Skip (future enhancement)
    │   └─ NO → Send to appropriate Kafka topic
    └─ NO → Send to DLQ with reason="channel_disabled"
```

## Future Enhancements

1. **Quiet Hours Enforcement** - Actually check current time against quiet hours
2. **Do Not Disturb Mode** - Disable all notifications for a time period
3. **Channel-Specific Content** - Different message formats for different channels
4. **Preference Groups** - Save and reuse preference templates
5. **Audit Trail** - Track preference changes
6. **Preference Expiry** - Auto-reset preferences after a certain time
7. **A/B Testing** - Test different preference configurations
8. **User Preference UI** - Web interface for preference management

## Testing

Run the main system with preferences:
```bash
python main.py
```

You should see messages for disabled channels being sent to DLQ with a reason.
