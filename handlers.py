# -----------------------------
# Notification Handlers (Strategy Pattern)
# -----------------------------
from abc import ABC, abstractmethod
from typing import Callable
from random import random


class NotificationHandler(ABC):
    """Abstract base class for notification handlers"""

    @abstractmethod
    def send(self, recipient: str, message: str) -> None:
        """Send notification to recipient"""
        pass

    def __call__(self, recipient: str, message: str) -> None:
        """Allow handler to be called directly"""
        self.send(recipient, message)


class EmailHandler(NotificationHandler):
    """Email notification handler"""

    def send(self, recipient: str, message: str) -> None:
        print(f"[EMAIL] Sending to {recipient}: {message}")
        if random() < 0.7:
            raise Exception("Email provider failed")


class SMSHandler(NotificationHandler):
    """SMS notification handler"""

    def send(self, recipient: str, message: str) -> None:
        print(f"[SMS] Sending to {recipient}: {message}")
        if random() < 0.7:
            raise Exception("SMS provider failed")


class IOSPushHandler(NotificationHandler):
    """iOS Push notification handler"""

    def send(self, recipient: str, message: str) -> None:
        print(f"[iOS PUSH] Sending to token={recipient}: {message}")
        if random() < 0.7:
            raise Exception("iOS push provider failed")


class AndroidPushHandler(NotificationHandler):
    """Android Push notification handler"""

    def send(self, recipient: str, message: str) -> None:
        print(f"[ANDROID PUSH] Sending to token={recipient}: {message}")
        if random() < 0.7:
            raise Exception("Android push provider failed")
