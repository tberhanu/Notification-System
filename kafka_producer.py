# -----------------------------
# Kafka Producer and Topics
# -----------------------------
from kafka import KafkaProducer
import json

# Initialize Kafka Producer
kafka_producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    request_timeout_ms=5000,
    retries=1,
    acks='all'
)

# Kafka Topics for Team A
EMAIL_TOPIC = 'teamA-notification-email'
SMS_TOPIC = 'teamA-notification-sms'
ANDROID_TOPIC = 'teamA-notification-android'
IOS_TOPIC = 'teamA-notification-ios'
DLQ_TOPIC = 'teamA-notification-dlq'
