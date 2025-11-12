import functools
from typing import Any, Callable

from sqlalchemy.exc import IntegrityError

from app.v1.common.db.models import InBoxEvents
from app.v1.common.db.orm import async_session


def inbox_based_idempotency(queue: str = "", exchange: str = "", on_processed: Any = None):
    def decorator(f: Callable):
        @functools.wraps(f)
        async def check_inbox_events(*args, **kwargs):
            event_id = None
            payload = None

            for arg in list(args) + list(kwargs.values()):
                if hasattr(arg, "event_id"):
                    payload = arg
                    event_id = arg.event_id
                    break

                elif isinstance(arg, dict) and "event_id" in arg:
                    payload = arg
                    event_id = arg["event_id"]
                    break

            if not event_id:
                raise ValueError("missing event_id for the inbox idempotency")

            async with async_session() as session:
                try:
                    inbox_event = await InBoxEvents.register_processed_event(session,
                                                                             event_id,
                                                                             payload,
                                                                             exchange,
                                                                             queue)

                except IntegrityError:
                    return (on_processed
                            if not isinstance(on_processed, Callable)
                            else on_processed())

                try:
                    result = await f(*args, **kwargs)
                    return result

                except Exception as e:
                    await inbox_event.delete(session)
                    raise e

        return check_inbox_events
    return decorator

