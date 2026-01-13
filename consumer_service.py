# -----------------------------
# Worker/Consumer Service (Consumer Layer)
# -----------------------------
import time
import json
from abc import ABC, abstractmethod
from typing import Callable
from kafka import KafkaConsumer
from kafka_producer import DLQ_TOPIC, kafka_producer
from handlers import NotificationHandler


class ConsumerWorker(ABC):
    """Abstract base class for Kafka consumers"""

    def __init__(self, topic: str, handler: NotificationHandler, topic_name: str, timeout: int = 5000):
        """Initialize consumer"""
        self.topic = topic
        self.handler = handler
        self.topic_name = topic_name
        self.timeout = timeout
        self.dlq_producer = kafka_producer

    @abstractmethod
    def process_message(self, data: dict) -> None:
        """Process a single message"""
        pass

    def consume(self) -> None:
        """Start consuming messages"""
        consumer = KafkaConsumer(
            self.topic,
            bootstrap_servers=['localhost:9092'],
            auto_offset_reset='earliest',
            consumer_timeout_ms=self.timeout,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

        for message in consumer:
            self.process_message(message.value)

        consumer.close()


class NotificationConsumerWorker(ConsumerWorker):
    """Consumer for notification messages with retry logic"""

    MAX_RETRIES = 3
    RETRY_DELAY = 0.5

    def process_message(self, data: dict) -> None:
        """Process notification message with retries"""
        recipient = data.get("recipient")
        msg_content = data.get("message")
        retries = self.MAX_RETRIES

        while retries > 0:
            try:
                self.handler(recipient, msg_content)
                print(f"{self.topic_name} → delivered successfully")
                return
            except Exception as e:
                retries -= 1
                print(f"{self.topic_name} → failed ({e}), retries left: {retries}")
                time.sleep(self.RETRY_DELAY)

        # All retries exhausted, send to DLQ
        print(f"{self.topic_name} → moved to DLQ")
        self.dlq_producer.send(DLQ_TOPIC, {
            "recipient": recipient,
            "message": msg_content,
            "topic": self.topic_name
        })


class DLQConsumerWorker(ConsumerWorker):
    """Consumer for Dead Letter Queue messages"""

    def process_message(self, data: dict) -> None:
        """Process DLQ message - logs failed messages, no handler"""
        recipient = data.get("recipient", "unknown")
        message = data.get("message", "unknown")
        topic = data.get("topic", "unknown")
        print(f"{self.topic_name} → DLQ Message: recipient={recipient}, topic={topic}, message={message}")


class ConsumerService:
    """Service for managing multiple consumers"""

    def __init__(self):
        """Initialize consumer service"""
        self.workers = []

    def add_worker(self, worker: ConsumerWorker) -> None:
        """Add a consumer worker"""
        self.workers.append(worker)

    def consume_all(self) -> None:
        """Consume from all registered workers"""
        for worker in self.workers:
            worker.consume()
