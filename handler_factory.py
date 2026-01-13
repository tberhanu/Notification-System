# -----------------------------
# Handler Factory (Factory Pattern)
# -----------------------------
from models import NotificationChannel
from handlers import (
    NotificationHandler,
    EmailHandler,
    SMSHandler,
    IOSPushHandler,
    AndroidPushHandler
)


class NotificationHandlerFactory:
    """Factory for creating notification handlers"""

    _handlers = {
        NotificationChannel.EMAIL: EmailHandler,
        NotificationChannel.SMS: SMSHandler,
        NotificationChannel.IOS: IOSPushHandler,
        NotificationChannel.ANDROID: AndroidPushHandler,
    }

    @classmethod
    def get_handler(cls, channel: NotificationChannel) -> NotificationHandler:
        """Get handler for a given channel"""
        handler_class = cls._handlers.get(channel)
        if not handler_class:
            raise ValueError(f"No handler found for channel: {channel}")
        return handler_class()

    @classmethod
    def register_handler(cls, channel: NotificationChannel, handler_class: type) -> None:
        """Register a custom handler for a channel"""
        cls._handlers[channel] = handler_class
