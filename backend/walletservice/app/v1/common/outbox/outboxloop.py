import asyncio
import json

from pamqp.exceptions import AMQPError

from ..db.models import OutBoxEvent
from ..db.orm import async_session
from ..broker.rabbitmq import rabbitmq


async def outbox_forwarding_loop():
    while True:
        try:
            async with async_session() as session:
                events = await OutBoxEvent.get_pending_events(session)
                if not events:
                    await asyncio.sleep(3)
                    continue

                for event in events:
                    try:
                        payload = json.loads(event.payload) if isinstance(event.payload, str) else event.payload
                        await rabbitmq.publish(message=payload, queue=event.queue or "", exchange=event.exchange or None, persist=True)
                        event.mark_sent()
                    except AMQPError:
                        event.mark_failed()
                    except json.JSONDecodeError:
                        event.mark_failed()

                await session.commit()
        except Exception as e:
            print(f"Outbox loop error: {e}")

        await asyncio.sleep(3)
