# -----------------------------
# Notification Service (Service Layer)
# -----------------------------
from typing import Dict, Optional
from models import NotificationEvent, NotificationChannel, NotificationMessage
from repository import IUserRepository
from kafka_producer import kafka_producer, EMAIL_TOPIC, SMS_TOPIC, IOS_TOPIC, ANDROID_TOPIC, DLQ_TOPIC


class NotificationService:
    """Core service for dispatching notifications"""
    
    def __init__(self, user_repository: IUserRepository):
        """Initialize with user repository"""
        self.user_repo = user_repository

    # Mapping of channels to Kafka topics
    CHANNEL_TOPIC_MAP = {
        NotificationChannel.EMAIL: EMAIL_TOPIC,
        NotificationChannel.SMS: SMS_TOPIC,
        NotificationChannel.IOS: IOS_TOPIC,
        NotificationChannel.ANDROID: ANDROID_TOPIC,
    }

    def dispatch(self, event: NotificationEvent) -> bool:
        """
        Dispatch a notification event
        
        Args:
            event: NotificationEvent to dispatch
            
        Returns:
            True if dispatched successfully, False otherwise
        """
        user = self.user_repo.get_user(event.user_id)
        if not user:
            print(f"User {event.user_id} not found")
            return False

        try:
            channel = NotificationChannel(event.channel)
        except ValueError:
            print(f"Invalid channel: {event.channel}")
            return False

        print(f"Event received → user {event.user_id}, topic {event.channel}")

        # Check if channel is enabled for this user
        if not user.is_channel_enabled(channel):
            print(f"→ {channel.value} is disabled for user {event.user_id} → sending to DLQ")
            kafka_producer.send(DLQ_TOPIC, {
                **event.to_dict(),
                "reason": f"{channel.value}_disabled"
            })
            return False

        recipient = user.get_identifier_for_channel(channel)
        if recipient:
            topic = self.CHANNEL_TOPIC_MAP.get(channel)
            if topic:
                message = NotificationMessage(
                    recipient=recipient,
                    message=event.message,
                    metadata={
                        "user_id": event.user_id,
                        "channel": channel.value
                    }
                )
                kafka_producer.send(topic, message.to_dict())
                print(f"→ sent to {channel.value}-topic")
                return True

        # No valid channel or recipient found, send to DLQ
        print("No valid channel found → sending to DLQ")
        kafka_producer.send(DLQ_TOPIC, event.to_dict())
        return False

    def flush(self, timeout: int = 5) -> None:
        """Flush pending messages with timeout"""
        try:
            kafka_producer.flush(timeout=timeout)
        except Exception as e:
            print(f"Warning: Flush timeout - {e}")
    
    def close(self) -> None:
        """Close the Kafka producer"""
        try:
            self.flush(timeout=10)
            kafka_producer.close(timeout=10)
        except Exception as e:
            print(f"Warning: Error closing producer - {e}")
