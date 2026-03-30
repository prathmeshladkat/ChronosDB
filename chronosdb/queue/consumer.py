"""
Job consumer - receives jobs from RabbitMQ and process them.
"""
import json
import asyncio
from typing import Callable, Awaitable
from aio_pika import IncomingMessage
from chronosdb.queue.rabbitmq import RabbitMQClient

class JobConsumer:
    """
    Consumes jobs from RabbitMQ queue.
    
    Used by Worker process.
    """
    
    JOBS_QUEUE = "chronosdb_jobs"
    
    def __init__(self, client: RabbitMQClient = None):
        """
        Initialize consumer.
        
        Args:
            client: RabbitMQ client
        """
        self.client = client or RabbitMQClient()
        self.is_consuming = False
    
    async def start_consuming(
        self,
        callback: Callable[[dict], Awaitable[None]]
    ):
        """
        Start consuming jobs from queue.
        
        Args:
            callback: Async function to process each job
                     Signature: async def process_job(payload: dict) -> None
        
        Example:
            async def process_job(payload):
                job_id = payload['job_id']
                print(f"Processing job {job_id}")
                # Do work...
            
            consumer = JobConsumer()
            await consumer.start_consuming(process_job)
        """
        # Connect to RabbitMQ
        await self.client.connect()
        
        # Declare queue
        queue = await self.client.declare_queue(self.JOBS_QUEUE)
        
        print(f"👂 Listening for jobs on queue: {self.JOBS_QUEUE}")
        
        # Define message handler
        async def on_message(message: IncomingMessage):
            """
            Called for each message received.
            
            This is like:
            - TypeScript: worker.process((job) => { ... })
            - Python: similar to event handler
            """
            # async with message.process():
            # - If no exception: AUTO-ACK (message removed from queue)
            # - If exception raised: AUTO-NACK + requeue (message re-delivered)
            
            async with message.process():
                # Decode message
                payload = json.loads(message.body.decode('utf-8'))
                
                print(f"📥 Received job: {payload.get('job_id')}")
                
                # Call user-provided callback
                await callback(payload)
                
                print(f"✅ Completed job: {payload.get('job_id')}")
                
                # Message is auto-ACKed here (removed from queue)
        
        # Start consuming
        await queue.consume(on_message)
        
        self.is_consuming = True
        
        # Keep running forever
        try:
            await asyncio.Future()  # Run until interrupted
        except KeyboardInterrupt:
            print("\n⏹️  Consumer stopped")
        finally:
            await self.client.close()
    
    async def stop(self):
        """Stop consuming and close connection."""
        self.is_consuming = False
        await self.client.close()