from notification_service import NotificationService
from consumer_service import ConsumerService
from user_repository import UserRepository
from handler_factory import NotificationHandlerFactory
from models import NotificationEvent
from kafka_producer import KafkaProducer


class NotificationSystem:
    """Main orchestrator for the notification system."""

    def __init__(self, user_repository):
        self.user_repo = user_repository
        self.notification_service = NotificationService(user_repository)
        self.handler_factory = NotificationHandlerFactory()
        self.consumer_service = ConsumerService()
        self._setup_consumers()

    def _setup_consumers(self):
        """Set up Kafka consumer workers for all topics."""
        from kafka_producer import EMAIL_TOPIC, SMS_TOPIC, IOS_TOPIC, ANDROID_TOPIC, DLQ_TOPIC
        from consumer_service import NotificationConsumerWorker, DLQConsumerWorker
        from handlers import EmailHandler, SMSHandler, IOSPushHandler, AndroidPushHandler

        self.consumer_service.add_worker(NotificationConsumerWorker(EMAIL_TOPIC, EmailHandler(), 'EMAIL'))
        self.consumer_service.add_worker(NotificationConsumerWorker(SMS_TOPIC, SMSHandler(), 'SMS'))
        self.consumer_service.add_worker(NotificationConsumerWorker(IOS_TOPIC, IOSPushHandler(), 'IOS'))
        self.consumer_service.add_worker(NotificationConsumerWorker(ANDROID_TOPIC, AndroidPushHandler(), 'ANDROID'))
        self.consumer_service.add_worker(DLQConsumerWorker(DLQ_TOPIC, None, 'DLQ'))

    def dispatch_event(self, event: NotificationEvent) -> bool:
        """Dispatch a single notification event."""
        return self.notification_service.dispatch(event)

    def dispatch_events(self, events: list):
        """Dispatch multiple notification events."""
        for event in events:
            self.dispatch_event(event)

    def process_messages(self):
        """Process messages from Kafka topics."""
        self.consumer_service.consume_all()

    def run(self, events: list):
        """Run the full notification system with dispatch and processing."""
        try:
            print("\nStarting Notification System...")
            self.dispatch_events(events)
            self.process_messages()
            print("\nNotification System completed.\n")
        finally:
            self.notification_service.close()

    @staticmethod
    def create_with_in_memory(users_data: dict):
        """Factory method to create system with in-memory repository."""
        repo = UserRepository(users_data)
        return NotificationSystem(repo)
