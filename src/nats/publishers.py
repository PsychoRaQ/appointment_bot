# системное
from datetime import datetime
# натс
from nats.js.client import JetStreamContext

'''
Паблишеры для натса
'''


# паблишер для отложенных уведомлений о записи
async def send_delay_message_publisher(
        js: JetStreamContext,
        subject: str,
        delay: int,
        date: str,
        time: str,
        message_id: str,
) -> None:
    headers = {
        'Tg-Delayed-Msg-Timestamp': str(datetime.now().timestamp()),
        'Tg-Delayed-Msg-Delay': str(delay),
        'date': date,
        'time': time,
        'message_id': message_id,

    }
    await js.publish(subject=subject, headers=headers)


# паблишер для рассылки
async def send_dispatch(
        js: JetStreamContext,
        subject: str,
        delay: int,
        user_id: int,
        payload: bytes,
) -> None:
    headers = {
        'Tg-Delayed-Msg-Timestamp': str(datetime.now().timestamp()),
        'Tg-Delayed-Msg-Delay': str(delay),
        'user_id': str(user_id),

    }
    await js.publish(subject=subject, payload=payload, headers=headers)
