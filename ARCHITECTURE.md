# Notification System - Architecture Documentation

## Overview

A production-ready notification system built with clean architecture principles and design patterns. The system dispatches notifications across multiple channels (Email, SMS, iOS, Android) using Apache Kafka for reliable message handling.

## Architecture

### Design Patterns Used

1. **Strategy Pattern** - Notification handlers (email, SMS, iOS, Android) implement a common interface
2. **Factory Pattern** - `NotificationHandlerFactory` creates handlers for different channels
3. **Repository Pattern** - `UserRepository` abstracts user data access
4. **Service Layer Pattern** - `NotificationService` and `ConsumerService` handle business logic
5. **Observer Pattern** - Kafka topics act as event streams for async processing

### Directory Structure

```
notification_system/
├── models.py                    # Domain models and enums
├── handlers.py                  # Notification handler implementations (Strategy)
├── handler_factory.py           # Handler factory (Factory pattern)
├── user_repository.py           # User data access (Repository pattern)
├── notification_service.py      # Core notification dispatch logic
├── consumer_service.py          # Kafka consumer workers
├── notification_system.py       # Main system orchestrator
├── kafka_producer.py            # Kafka producer configuration
├── kafka_consumer.py            # Generic Kafka consumer logic
├── database.py                  # User metadata (legacy)
├── main.py                      # Entry point
└── README.md                    # This file
```

## Core Components

### 1. Models (`models.py`)

**Domain Objects:**
- `NotificationChannel` - Enum for supported channels (EMAIL, SMS, IOS, ANDROID)
- `NotificationStatus` - Enum for delivery status
- `User` - User model with notification preferences
- `NotificationEvent` - Event to be dispatched
- `NotificationMessage` - Message sent to Kafka

**Benefits:**
- Type-safe representation of domain concepts
- Easy validation and transformation
- Clear contracts between layers

### 2. Handlers (`handlers.py`)

**Strategy Pattern Implementation:**
- `NotificationHandler` - Abstract base class defining the interface
- `EmailHandler` - Email notifications
- `SMSHandler` - SMS notifications
- `IOSPushHandler` - iOS push notifications
- `AndroidPushHandler` - Android push notifications

**Benefits:**
- Easy to add new notification channels
- Handlers are interchangeable
- Encapsulates external provider logic
- Simple to test and mock

```python
# Easy to add new handlers
class SlackHandler(NotificationHandler):
    def send(self, recipient: str, message: str) -> None:
        # Implementation
        pass
```

### 3. Handler Factory (`handler_factory.py`)

**Factory Pattern:**
- Centralizes handler creation
- Makes it easy to swap implementations
- Supports registration of custom handlers

```python
# Usage
handler = NotificationHandlerFactory.get_handler(NotificationChannel.EMAIL)

# Register custom handler
class CustomEmailHandler(NotificationHandler):
    pass

NotificationHandlerFactory.register_handler(
    NotificationChannel.EMAIL, 
    CustomEmailHandler
)
```

### 4. User Repository (`user_repository.py`)

**Repository Pattern:**
- Abstracts user data access
- Single source of truth for user information
- Easy to switch data sources (database, API, cache)

```python
# Usage
user_repo = UserRepository(users_data)
user = user_repo.get_user(user_id)
```

### 5. Notification Service (`notification_service.py`)

**Core Business Logic:**
- Validates users and channels
- Resolves recipient identifiers
- Sends messages to appropriate Kafka topics
- Routes failed events to DLQ

```python
service = NotificationService(user_repo)
event = NotificationEvent(user_id=1, channel="email", message="Hello")
service.dispatch(event)
```

### 6. Consumer Service (`consumer_service.py`)

**Kafka Message Processing:**
- `ConsumerWorker` - Abstract consumer base class
- `NotificationConsumerWorker` - Processes notifications with retry logic (3 retries)
- `DLQConsumerWorker` - Processes failed messages
- `ConsumerService` - Manages multiple workers

**Features:**
- Automatic retries for failed messages
- Dead Letter Queue for unprocessable messages
- Pluggable message handlers
- Configurable timeouts

### 7. Notification System (`notification_system.py`)

**Main Orchestrator:**
- Coordinates all components
- Sets up consumers for all channels
- Provides high-level API for event dispatch
- Manages complete flow from dispatch to processing

```python
system = NotificationSystem(USERS_DATA)
system.dispatch_event({"user_id": 1, "topic": "email", "message": "Hi!"})
system.process_messages()
```

## Data Flow

```
NotificationEvent
    ↓
[User Validation] → UserRepository
    ↓
[Channel Resolution] → Get recipient identifier
    ↓
[Message Formatting] → NotificationMessage
    ↓
Kafka Topics (email, sms, ios, android)
    ↓
[Consumer Workers] (with retry logic)
    ↓
[Notification Handlers] (execute actual send)
    ↓
Success or DLQ
    ↓
DLQ Topic (for failed messages)
    ↓
[DLQ Consumer] (processes failures)
```

## Adding New Features

### 1. Add a New Notification Channel

```python
# 1. Update models.py
class NotificationChannel(Enum):
    SLACK = "slack"  # New channel

# 2. Create handler in handlers.py
class SlackHandler(NotificationHandler):
    def send(self, recipient: str, message: str) -> None:
        print(f"[SLACK] Sending to {recipient}: {message}")
        # Implementation

# 3. Register in handler_factory.py
NotificationHandlerFactory.register_handler(
    NotificationChannel.SLACK, 
    SlackHandler
)

# 4. Update kafka_producer.py
SLACK_TOPIC = 'notification-slack'

# 5. Add to notification_system.py
slack_handler = NotificationHandlerFactory.get_handler(NotificationChannel.SLACK)
slack_worker = NotificationConsumerWorker(
    topic=SLACK_TOPIC,
    handler=slack_handler,
    topic_name="SLACK_TOPIC"
)
self.consumer_service.add_worker(slack_worker)
```

### 2. Add Retry Logic Customization

```python
class CustomNotificationConsumerWorker(NotificationConsumerWorker):
    MAX_RETRIES = 5  # Override
    RETRY_DELAY = 1.0  # Override
    
    def process_message(self, data: dict) -> None:
        # Custom retry logic
        pass
```

### 3. Switch Data Source

```python
# Replace UserRepository with database
class DatabaseUserRepository(UserRepository):
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_user(self, user_id: int) -> Optional[User]:
        # Query database
        pass

# Use in notification system
system = NotificationSystem.from_database(db_connection)
```

## Testing

Due to the clean architecture:

1. **Unit Test Handlers** - Mock the handler interface
2. **Test NotificationService** - Mock repositories and Kafka
3. **Test Consumers** - Use test Kafka messages
4. **Integration Tests** - Test full flow with real Kafka

```python
# Example: Test email handler
def test_email_handler():
    handler = EmailHandler()
    handler.send("test@example.com", "Hello")  # Will randomly fail
    
# Example: Test notification service
def test_dispatch():
    mock_repo = MagicMock()
    mock_repo.get_user.return_value = User(user_id=1, email="test@example.com")
    
    service = NotificationService(mock_repo)
    event = NotificationEvent(user_id=1, channel="email", message="Test")
    assert service.dispatch(event) == True
```

## Configuration

Edit `main.py` to configure:

```python
# User data
USERS_DATA = {
    1: {"email": "user@example.com", "phone": "+1234567890", ...},
}

# Sample events
SAMPLE_EVENTS = [
    {"user_id": 1, "topic": "email", "message": "Welcome!"},
]
```

Edit handlers to adjust failure rates:

```python
# In handlers.py - adjust random threshold
if random() < 0.7:  # 70% failure rate
    raise Exception("Provider failed")
```

## Running the System

```bash
# Run the main system
python main.py

# Run individual components (if needed)
python -c "from models import User; print(User(1, email='test@example.com'))"
```

## Future Enhancements

1. **Persistent Storage** - Use real database instead of in-memory
2. **Authentication** - Add auth headers for external providers
3. **Rate Limiting** - Limit messages per user/channel
4. **Metrics** - Add Prometheus metrics for monitoring
5. **Async Processing** - Use asyncio for parallel processing
6. **Scheduled Messages** - Support delayed delivery
7. **Templates** - Support message templates with variables
8. **Preferences** - Allow users to opt-in/out of channels
9. **Webhooks** - Support custom delivery endpoints
10. **Analytics** - Track delivery metrics and user engagement

## Dependencies

- `kafka-python` - Apache Kafka client
- Python 3.7+

## Summary

This architecture provides:
- ✅ Clean separation of concerns
- ✅ Easy to extend with new channels
- ✅ Testable components (dependency injection ready)
- ✅ Type-safe domain models
- ✅ Production-ready error handling
- ✅ Scalable message processing with Kafka
- ✅ Dead Letter Queue for reliability
- ✅ Flexible configuration
