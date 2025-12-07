import datetime
import json
import threading
import time

import redis


class RedisPubSub:
    def __init__(
            self,
            host='localhost',
            port=6379,
            password=None
    ):
        self.publisher = redis.Redis(
            host=host,
            port=port,
            decode_responses=True,
            password=password,
        )

        self.subscriber = redis.Redis(
            host=host,
            port=port,
            decode_responses=True,
            password=password,
        )
        self.running = False

    def publish_message(self, channel: str, message: dict):
        """Публикация в канал"""
        try:
            message_json = json.dumps({
                **message,
                'timestamp': datetime.datetime.now().isoformat()
            })

            result = self.publisher.publish(channel, message_json)
            print(
                f'Опубликовано в {channel}: {message_json} (подписчиков: {result})')

            return result
        except Exception as e:
            print(f'Ошибка публикации: {e.__class__.__name__}')
            return None

    def subscribe_to_channel(self, channel: str, callback):
        """Подписка на канал"""
        try:
            pubsub = self.subscriber.pubsub()
            pubsub.subscribe(**{channel: callback})

            return pubsub
        except Exception as e:
            print(f'Ошибка подписки: {e.__class__.__name__}')
            return None

    def start_subscriber_thread(self, channel: str, name: str):
        """Запуск подписчика в потоке"""

        def message_handler(message):
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    print(f'[{name}] Получено из "{channel=}": {data}')
                except json.JSONDecodeError as e:
                    print(
                        f'Ошибка декодирования сообщения: {e.__class__.__name__} {message["data"]}')
                except Exception as e:
                    print(
                        f'Ошибка обработки сообщения: {e.__class__.__name__}')

        def run_subscriber():
            pubsub = self.subscribe_to_channel(channel, message_handler)

            if pubsub:
                print(f'[{name}] Подписан на канал {channel=}')

                while self.running:
                    try:
                        pubsub.get_message(timeout=1.0)
                    except Exception as e:
                        print(
                            f'Ошибка подписчика {name}: {e.__class__.__name__}')
                        break
                    time.sleep(1)

        self.running = True
        thread = threading.Thread(target=run_subscriber, daemon=True)
        thread.start()

        return thread


def demo_pub_sub():
    redis_pubsub = RedisPubSub()
    redis_pubsub.start_subscriber_thread('channel_1', 'Subscriber_1')
    redis_pubsub.start_subscriber_thread('channel_2', 'Subscriber_2')
    redis_pubsub.start_subscriber_thread('channel_1', 'Subscriber_3')

    time.sleep(1)

    redis_pubsub.publish_message(
        'channel_1',
        {
            'title': 'Some title 1',
            'content': 'Some content 1',
            'category': 'Some category 1'
        },
    )
    time.sleep(1)
    redis_pubsub.publish_message(
        'channel_2',
        {
            'title': 'Some title 2',
            'content': 'Some content 2',
            'category': 'Some category 2'
        },
    )
    time.sleep(1)
    redis_pubsub.publish_message(
        'channel_1',
        {
            'title': 'Some title 3',
            'content': 'Some content 3',
            'category': 'Some category 3'
        },
    )


if __name__ == '__main__':
    demo_pub_sub()
