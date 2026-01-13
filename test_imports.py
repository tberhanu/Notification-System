#!/usr/bin/env python3
"""Test that all modules can be imported successfully"""

print("Testing imports...")
print("-" * 60)

try:
    print("✓ Importing models...", end=" ")
    from models import User, NotificationChannel, NotificationEvent
    print("OK")
    
    print("✓ Importing repository interface...", end=" ")
    from repository import IUserRepository
    print("OK")
    
    print("✓ Importing in-memory repository...", end=" ")
    from user_repository import InMemoryUserRepository
    print("OK")
    
    print("✓ Importing handlers...", end=" ")
    from handlers import EmailHandler, SMSHandler, IOSPushHandler, AndroidPushHandler
    print("OK")
    
    print("✓ Importing handler factory...", end=" ")
    from handler_factory import NotificationHandlerFactory
    print("OK")
    
    print("✓ Importing notification service...", end=" ")
    from notification_service import NotificationService
    print("OK")
    
    print("✓ Importing Kafka consumer...", end=" ")
    from kafka_consumer import ConsumerService, NotificationConsumerWorker
    print("OK")
    
    print("✓ Importing notification system...", end=" ")
    from notification_system import NotificationSystem
    print("OK")
    
    print("✓ Importing kafka producer...", end=" ")
    from kafka_producer import kafka_producer, EMAIL_TOPIC
    print("OK")
    
    print("-" * 60)
    print("✓ All imports successful!")
    
    # Test in-memory repository
    print("\nTesting in-memory repository...")
    print("-" * 60)
    
    test_data = {
        1: {"email": "test@example.com", "phone": "+1234567890", "ios_token": "ios_1", "android_token": None}
    }
    
    repo = InMemoryUserRepository(test_data)
    user = repo.get_user(1)
    
    print(f"✓ User retrieved: {user.email}")
    print(f"✓ Email enabled: {user.is_channel_enabled(NotificationChannel.EMAIL)}")
    print(f"✓ Preferences set: {bool(user.preferences)}")
    
    print("-" * 60)
    print("✓ All tests passed!")
    
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
