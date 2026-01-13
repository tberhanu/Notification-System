# -----------------------------
# User Repository
# -----------------------------
from typing import Optional, Dict, Any
from models import User, NotificationChannel
from repository import IUserRepository


class UserRepository(IUserRepository):
    """Repository for user data access and preference management"""

    def __init__(self, users_data: dict):
        """Initialize with user data"""
        self._users = {
            user_id: User(
                user_id=user_id,
                email=data.get("email"),
                phone=data.get("phone"),
                ios_token=data.get("ios_token"),
                android_token=data.get("android_token"),
                preferences=data.get("preferences")  # Load preferences if provided
            )
            for user_id, data in users_data.items()
        }

    def get_user(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self._users.get(user_id)

    def add_user(self, user: User) -> None:
        """Add or update a user"""
        self._users[user.user_id] = user

    def get_all_users(self) -> dict:
        """Get all users"""
        return self._users.copy()

    def user_exists(self, user_id: int) -> bool:
        """Check if a user exists"""
        return user_id in self._users

    def set_channel_preference(self, user_id: int, channel: NotificationChannel, enabled: bool) -> bool:
        """Enable or disable a notification channel for a user"""
        user = self.get_user(user_id)
        if not user:
            return False
        user.set_channel_preference(channel, enabled)
        return True

    def set_quiet_hours(self, user_id: int, channel: NotificationChannel, start: Optional[str], end: Optional[str]) -> bool:
        """Set quiet hours for a user's channel"""
        user = self.get_user(user_id)
        if not user:
            return False
        user.set_quiet_hours(channel, start, end)
        return True

    def get_user_preferences(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get all preferences for a user"""
        user = self.get_user(user_id)
        if not user:
            return None
        return user.preferences.copy()

    def is_channel_enabled_for_user(self, user_id: int, channel: NotificationChannel) -> bool:
        """Check if a channel is enabled for a specific user"""
        user = self.get_user(user_id)
        if not user:
            return False
        return user.is_channel_enabled(channel)

    def get_user_quiet_hours(self, user_id: int, channel: NotificationChannel) -> Optional[Dict[str, Optional[str]]]:
        """Get quiet hours for a user's channel"""
        user = self.get_user(user_id)
        if not user:
            return None
        return user.get_quiet_hours(channel)
