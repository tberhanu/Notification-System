# -----------------------------
# Domain Models and Enums
# -----------------------------
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Set


class NotificationChannel(Enum):
    """Enumeration of supported notification channels"""
    EMAIL = "email"
    SMS = "sms"
    IOS = "ios"
    ANDROID = "android"


class NotificationPreference(Enum):
    """Enumeration of notification preferences"""
    ENABLED = "enabled"
    DISABLED = "disabled"
    QUIET_HOURS = "quiet_hours"  # Do not send during quiet hours


class NotificationStatus(Enum):
    """Enumeration of notification delivery status"""
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    DLQ = "dlq"


@dataclass
class User:
    """User model with notification preferences"""
    user_id: int
    email: Optional[str] = None
    phone: Optional[str] = None
    ios_token: Optional[str] = None
    android_token: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Initialize preferences with defaults if not provided"""
        if self.preferences is None:
            self.preferences = self._get_default_preferences()

    @staticmethod
    def _get_default_preferences() -> Dict[str, Any]:
        """Get default notification preferences"""
        return {
            "email": {
                "enabled": True,
                "quiet_hours": {"start": None, "end": None}  # No quiet hours by default
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

    def is_channel_enabled(self, channel: NotificationChannel) -> bool:
        """Check if a channel is enabled for this user"""
        return self.preferences.get(channel.value, {}).get("enabled", True)

    def has_quiet_hours(self, channel: NotificationChannel) -> bool:
        """Check if channel has quiet hours configured"""
        quiet_hours = self.preferences.get(channel.value, {}).get("quiet_hours", {})
        return quiet_hours.get("start") is not None and quiet_hours.get("end") is not None

    def get_quiet_hours(self, channel: NotificationChannel) -> Optional[Dict[str, Optional[str]]]:
        """Get quiet hours for a channel"""
        return self.preferences.get(channel.value, {}).get("quiet_hours")

    def set_channel_preference(self, channel: NotificationChannel, enabled: bool) -> None:
        """Enable or disable a notification channel"""
        if channel.value not in self.preferences:
            self.preferences[channel.value] = {"enabled": enabled, "quiet_hours": {"start": None, "end": None}}
        else:
            self.preferences[channel.value]["enabled"] = enabled

    def set_quiet_hours(self, channel: NotificationChannel, start: Optional[str], end: Optional[str]) -> None:
        """Set quiet hours for a channel (e.g., '22:00' to '08:00')"""
        if channel.value not in self.preferences:
            self.preferences[channel.value] = {"enabled": True, "quiet_hours": {"start": start, "end": end}}
        else:
            self.preferences[channel.value]["quiet_hours"] = {"start": start, "end": end}

    def get_identifier_for_channel(self, channel: NotificationChannel) -> Optional[str]:
        """Get the appropriate identifier for a given channel"""
        if channel == NotificationChannel.EMAIL:
            return self.email
        elif channel == NotificationChannel.SMS:
            return self.phone
        elif channel == NotificationChannel.IOS:
            return self.ios_token
        elif channel == NotificationChannel.ANDROID:
            return self.android_token
        return None


@dataclass
class NotificationEvent:
    """Notification event model"""
    user_id: int
    channel: Any  # Can be NotificationChannel enum or string
    message: str

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        # Convert enum to value if necessary
        channel_value = self.channel.value if hasattr(self.channel, 'value') else self.channel
        return {
            "user_id": self.user_id,
            "topic": channel_value,
            "message": self.message
        }


@dataclass
class NotificationMessage:
    """Message model for Kafka topics"""
    recipient: str
    message: str
    metadata: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "recipient": self.recipient,
            "message": self.message,
            **(self.metadata or {})
        }
