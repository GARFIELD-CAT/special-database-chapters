import time

import redis


# Redis кэш
class RedisCache:
    def __init__(
            self,
            host='localhost',
            port=6379,
            password=None
    ):
        self.redis = redis.Redis(
            host=host,
            port=port,
            decode_responses=True,
            password=password,
        )

    def set_cache(self, key: str, value: str,
                  expire_seconds: int = 3600) -> None:
        """Сохранение в кэш"""
        self.redis.setex(key, value, expire_seconds)

    def get_cache(self, key: str) -> str:
        """Получение из кэша"""
        return self.redis.get(key)

    def delete_cache(self, key: str) -> str:
        """Удаление из кэша"""
        return self.redis.delete(key)


if __name__ == '__main__':
    cache = RedisCache()

    cache.set_cache("user_1", "Denis Yagunov", 5)

    user = cache.get_cache("user_1")
    print(f'user from cache: {user}')

    print(f'wait 10 sec')
    time.sleep(10)

    user = cache.get_cache("user_1")
    print(f'user from cache: {user}')

    print('create cache again')
    cache.set_cache("user_1", "Denis Yagunov", 5)
    user = cache.get_cache("user_1")
    print(f'user from cache: {user}')

    print('delete user cache')
    cache.delete_cache("user_1")
    user = cache.get_cache("user_1")
    print(f'user from cache after delete: {user}')
