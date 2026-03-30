"""
Test RabbitMQ publisher and consumer.

This will:
1. Publish a test job to queue
2. Consume it and print the payload
"""
import asyncio
from chronosdb.queue.publisher import JobPublisher
from chronosdb.queue.consumer import JobConsumer


async def test_publisher():
    """Test publishing a job."""
    print("=" * 60)
    print("Testing Publisher")
    print("=" * 60)
    
    publisher = JobPublisher()
    
    # Publish test job
    await publisher.publish_job(
        job_id=999,
        tenant_id=1,
        test=True
    )
    
    await publisher.close()
    
    print("✅ Published test job")


async def test_consumer():
    """Test consuming jobs."""
    print("=" * 60)
    print("Testing Consumer")
    print("=" * 60)
    
    async def process_job(payload: dict):
        """Process received job."""
        print(f"📦 Received payload: {payload}")
        
        # Simulate work
        await asyncio.sleep(1)
        
        print(f"✅ Processed job {payload.get('job_id')}")
    
    consumer = JobConsumer()
    
    # This will run forever - press Ctrl+C to stop
    await consumer.start_consuming(process_job)


async def main():
    """Run tests."""
    print("Choose test:")
    print("1. Test Publisher")
    print("2. Test Consumer")
    
    choice = input("Enter choice (1 or 2): ")
    
    if choice == "1":
        await test_publisher()
    elif choice == "2":
        await test_consumer()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())