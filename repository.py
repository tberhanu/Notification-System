from abc import ABC, abstractmethod
from models import User, NotificationChannel


class IUserRepository(ABC):
    """Abstract interface for user repository implementations."""

    @abstractmethod
    def get_user(self, user_id: int) -> User:
        """Retrieve a user by ID."""
        pass

    @abstractmethod
    def add_user(self, user: User) -> None:
        """Add or update a user."""
        pass

    @abstractmethod
    def user_exists(self, user_id: int) -> bool:
        """Check if a user exists."""
        pass

    @abstractmethod
    def set_channel_preference(self, user_id: int, channel: NotificationChannel, enabled: bool) -> None:
        """Enable or disable a notification channel for a user."""
        pass

    @abstractmethod
    def set_quiet_hours(self, user_id: int, channel: NotificationChannel, start: str, end: str) -> None:
        """Set quiet hours for a notification channel (format: HH:MM)."""
        pass

    @abstractmethod
    def get_user_preferences(self, user_id: int) -> dict:
        """Get all preferences for a user."""
        pass

    @abstractmethod
    def is_channel_enabled_for_user(self, user_id: int, channel: NotificationChannel) -> bool:
        """Check if a channel is enabled for a user."""
        pass
