"""
Job publisher - sends jobs to RabbitMQ queue
"""
import json 
from typing import Dict, Any
from aio_pika import Message, DeliveryMode
from chronosdb.queue.rabbitmq import RabbitMQClient

class JobPublisher:
    """
    Publishes jobs to RbbitMQ.

    Used by API when creating jobs
    """
    JOBS_QUEUE = "chronosdb_jobs"

    def __init__(self, client: RabbitMQClient = None):
        self.client = client or RabbitMQClient()

    async def publish_job(self, job_id: int, tenant_id: int, **metadata) -> bool:
        """
        Publish a job to the queue

        Args:
            job_id: Job ID to process
            tenant_id: Tenant ID (for security)
            **metadata: Additional metadata

        Returns" 
            Tre if published successfully
        """
        await self.client.connect()

        channel = await self.client.get_channel()

        await self.client.declare_queue(self.JOBS_QUEUE)

        payload = {
            "job_id": job_id,
            "tenant_id": tenant_id,
            **metadata
        }

        message = Message(
            body=json.dumps(payload).encode('utf-8'),
            delivery_mode=DeliveryMode.PERSISTENT,
            content_type="application/json",
            content_encoding="utf-8",
        )

        await channel.default_exchange.publish(
            message, 
            routing_key=self.JOBS_QUEUE,
        )

        print(f"Published job {job_id} to queue")

        return True
    
    async def close(self):
        await self.client.close()


#notes:-
#Message(): Wraps your data
#DeliveryMode.PERSISTENT: Message survives RabbitMQ restart
#routing_key: Where to send the message (queue name)
#json.dumps().encode(): Convert dict → JSON string → bytes