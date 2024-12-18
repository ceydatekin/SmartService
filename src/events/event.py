import json
from datetime import datetime
from kafka import KafkaProducer, KafkaConsumer
from abc import ABC, abstractmethod

class EventPublisher:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )

    def publish(self, event_type: str, event_data: dict):
        self.producer.send(
            'smart_service_events',
            {
                'type': event_type,
                'data': event_data,
                'timestamp': datetime.utcnow().isoformat()
            }
        )

class EventHandler(ABC):
    @abstractmethod
    def handle(self, event: dict):
        pass

class ModelCreatedHandler(EventHandler):
    def handle(self, event: dict):
        # Notify monitoring systems
        # Update analytics
        # Trigger integrations
        pass

class EventListener:
    def __init__(self, handlers: Dict[str, EventHandler]):
        self.consumer = KafkaConsumer(
            'smart_service_events',
            bootstrap_servers=['localhost:9092'],
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        self.handlers = handlers

    def start_listening(self):
        for message in self.consumer:
            event = message.value
            if event['type'] in self.handlers:
                self.handlers[event['type']].handle(event['data'])