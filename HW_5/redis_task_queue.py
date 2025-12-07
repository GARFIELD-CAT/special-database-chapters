import time

import redis


class RedisTaskQueue:
    def __init__(
            self,
            host='localhost',
            port=6379,
            password=None,
            queue_name='task_queue'
    ):
        self.redis = redis.Redis(
            host=host,
            port=port,
            decode_responses=True,
            password=password,
        )
        self.queue_name = queue_name

    def add_task(self, task):
        """Добавить задачу в очередь."""
        self.redis.rpush(self.queue_name, task)
        print(f"Задача добавлена: {task}")

    def _get_task(self):
        """Получить задачу из очереди и удалить ее."""
        task = self.redis.lpop(self.queue_name)
        return task

    def process_tasks(self):
        """Обработать задачи из очереди."""
        while True:
            task = None

            try:
                task = self._get_task()
                if task:
                    print(f"Обработка задачи: {task}")
                    time.sleep(2)
                else:
                    print("Очередь пуста, ждем новой задачи...")
                    time.sleep(5)  # Ждать, если нет задач
            except Exception as e:
                print(
                    f"Ошибка при обработке задачи '{task}': {e.__class__.__name__}")


if __name__ == "__main__":
    queue = RedisTaskQueue()

    # Добавить задачи в очередь
    queue.add_task('Задача 1')
    queue.add_task('Задача 2')
    queue.add_task('Задача 3')

    # Обработать задачи
    queue.process_tasks()
