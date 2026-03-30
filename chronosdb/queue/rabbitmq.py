"""
RabbitMQ client - connection mangment
Queue connection pool
"""
import aio_pika
from aio_pika import Connection, Channel, RobustConnection
from chronosdb.config.settings import settings

class RabbitMQClient:
    """
    Handles:
        - connection to RabbitMQ
        - Automatic reconnection if connection drops
        - Channel creation

    """
    def __init__(self, url: str = None):
        self.url = url or settings.rabbitmq_url
        self.connection: RobustConnection = None
        self.channel: Channel = None

    async def connect(self):
        """
        Establish connection to RabbitMQ.

        Uses RobustConnection = auto-reconnect on neetwork function.

        Examples:
            client = RabbitMQClient()
            await client.connect()
        """
        if self.connection and not self.connection.is_closed:
            return #already connected
        
        self.connection = await aio_pika.connect_robust(
            self.url,
            timeout=10,
        )

        print(f"Connected to rabbitMQ at {self.url}")

        self.channel = await self.connection.channel()

        #QoS (Quality of Service) = prefetch count
        #This means "Only send 1 message at time"
        await self.channel.set_qos(prefetch_count=1)

    async def close(self):
        """Close connection to RabbitMQ."""
        if self.channel:
            await self.channel.close()

        if self.connection:
            await self.connection.close()

        print("Disconnected from RabbitMQ")

    async def declare_queue(self, queue_name: str, durable: bool =True):
        """
        Declare a queue (create if doesn't exist).
        
        Args:
            queue_name: Name of the queue
            durable: If True, queue survives RabbitMQ restart
        
        Returns:
            Queue object
        
        Example:
            queue = await client.declare_queue("jobs")
        """
        if not self.channel:
            await self.connect()
        
        # Declare queue
        # durable=True = queue persists even if RabbitMQ restarts
        queue = await self.channel.declare_queue(
            queue_name,
            durable=durable,
            # auto_delete=False means queue stays even if no consumers
        )
        
        return queue
    
    async def get_channel(self) -> Channel:
        """Get or create channel."""
        if not self.channel:
            await self.connect()
        
        return self.channel
