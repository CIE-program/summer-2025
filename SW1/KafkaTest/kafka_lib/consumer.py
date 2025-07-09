#Kafka Library Consumer Client
#Simple function to Retrieve all the Messages based on the Limit
#Does not need asyncio
#This is v0.5 and would need tweaks

from kafka import KafkaConsumer, TopicPartition
from kafka.errors import NoBrokersAvailable
import json
import logging
from typing import Iterator, Dict, Any, AsyncIterator
from tenacity import retry, stop_after_attempt, wait_exponential
import asyncio
from typing import List

logger = logging.getLogger("kafka.consumer")

class KafkaConsumerClient:
    def __init__(
        self,
        topic: str,
        group_id: str,
        bootstrap_servers: str = "kafka:9092",
        auto_offset_reset: str = "earliest"
    ):
        self.topic = topic
        self.group_id = group_id
        self.bootstrap_servers = bootstrap_servers
        self.auto_offset_reset = auto_offset_reset
        self.consumer = None
        self.running = False

    def _create_consumer(self):
        """Create a new consumer instance"""
        return KafkaConsumer(
            self.topic,
            group_id=self.group_id,
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset=self.auto_offset_reset,
            enable_auto_commit=False,
            value_deserializer=lambda x: json.loads(x.decode("utf-8")) if x else None,
            session_timeout_ms=30000,
            heartbeat_interval_ms=10000,
            consumer_timeout_ms=1000  # Add timeout for polling
        )

    @retry(
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def get_all_messages(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Fetch all available messages from the topic (non-blocking)"""
        logging.debug("get_all_messages - Library Call")
        consumer = KafkaConsumer(
            bootstrap_servers=self.bootstrap_servers,
            auto_offset_reset=self.auto_offset_reset,
            enable_auto_commit=False,
            value_deserializer=lambda x: json.loads(x.decode("utf-8")) if x else None,
            consumer_timeout_ms=1000  # Return after 1 second if no messages
        )
        
        try:
            # Get partition info
            partitions = consumer.partitions_for_topic(self.topic)
            if not partitions:
                return []
            logging.debug("Partitions found")
            # Seek to beginning for all partitions
            topic_partitions = [TopicPartition(self.topic, p) for p in partitions]
            consumer.assign(topic_partitions)
            consumer.seek_to_beginning()
            
            logging.debug("Consumer - Looping through the messages and reading")
            # Fetch messages
            messages = []
            for _ in range(limit):  # Safety limit
                batch = consumer.poll(timeout_ms=500)
                if not batch:
                    break
                
                for _, records in batch.items():
                    for msg in records:
                        messages.append({
                            "topic": msg.topic,
                            "partition": msg.partition,
                            "offset": msg.offset,
                            "key": msg.key.decode() if msg.key else None,
                            "value": msg.value,
                            "timestamp": msg.timestamp
                        })
            
            return messages
            
        finally:
            consumer.close()


    def stop(self):
        """Stop the async consumer"""
        self.running = False

    def close(self):
        """Close the consumer"""
        if self.consumer:
            try:
                self.consumer.close()
            except Exception as e:
                logger.error(f"Error closing consumer: {e}")
            finally:
                self.consumer = None


