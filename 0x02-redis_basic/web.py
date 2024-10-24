#!/usr/bin/env python3
'''A module with tools for request caching and tracking.
'''
import requests
import redis
import uuid
from typing import Callable

class Cache:
    def __init__(self):
        self._redis = redis.Redis()
        self._redis.flushdb()

    def store(self, key: str, data: str, ex: int = 10) -> None:
        self._redis.setex(key, ex, data)

    def get(self, key: str) -> str:
        data = self._redis.get(key)
        return data.decode('utf-8') if data else None

    def increment_count(self, url: str) -> None:
        self._redis.incr(f"count:{url}")

    def get_count(self, url: str) -> int:
        count = self._redis.get(f"count:{url}")
        return int(count) if count else 0

cache = Cache()

def data_cacher(func: Callable[[str], str]) -> Callable[[str], str]:
    def wrapper(url: str) -> str:
        # Check if the URL is already cached
        cached_data = cache.get(url)
        if cached_data:
            return cached_data

        # If not cached, fetch the data and store it
        response = func(url)
        cache.store(url, response)
        cache.increment_count(url)
        return response
    return wrapper

@data_cacher
def get_page(url: str) -> str:
    '''Returns the content of a URL after caching the request's response,
    and tracking the request.
    '''
    return requests.get(url).text

if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk/delay/5000/url/http://www.google.com"
    print(get_page(url))
    print(f"URL accessed {cache.get_count(url)} times")

