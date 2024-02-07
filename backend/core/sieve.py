#
# An implementation of the SIEVE cache eviction algorithm. SIEVE has two
# desirable properties:
#
# - Lazy promotion
# - Quick demotion
#
# One of the really nice attributes of SIEVE is that it doesn't require
# any locking for cache hits because, unlike LRU, objects do not change
# position. This alone contributes to a 2x increase in throughput
# compared with Python's lru_cache().

from functools import _make_key
from _thread import RLock
import functools


class sieve_cache:
    def __init__(self, maxsize=128):
        self.maxsize = maxsize

    PREV, NEXT, KEY, RESULT, VISITED = 0, 1, 2, 3, 4

    def __call__(self, user_func):
        self.cache = {}
        self.tail = []
        self.full = None
        self.tail[:] = [
            self.tail,  # PREV
            self.tail,  # NEXT
            None,  # KEY
            None,  # RESULT
            None,  # VISITED
        ]

        self.make_key = _make_key
        self.cache_get = self.cache.get
        self.cache_len = self.cache.__len__
        self.lock = RLock()

        self.hand = self.tail

        @functools.wraps(user_func)
        async def wrapper(*args, **kwargs):
            return await self.decorator(user_func, *args, **kwargs)

        return wrapper

    async def decorator(self, user_func, *args, **kwargs):
        key = self.make_key(args, kwargs, typed=False)
        link = self.cache_get(key)
        if link is not None:
            link[sieve_cache.VISITED] = True
            return link[sieve_cache.RESULT]

        result = await user_func(*args, **kwargs)

        # Short-circuit and exit if user_func failed. Most caches don't work
        # this way but it's a good idea for caching HTTP requests which can
        # fail.
        if not result:
            return None

        with self.lock:
            # Cache miss
            if key in self.cache:
                # another thread might have already computed the value
                pass
            elif self.full:
                o = self.hand
                if o[sieve_cache.KEY] is None:
                    o = self.tail[sieve_cache.PREV]

                while o[sieve_cache.VISITED]:
                    o[sieve_cache.VISITED] = False
                    o = o[sieve_cache.PREV]
                    if o[sieve_cache.KEY] is None:
                        o = self.tail[sieve_cache.PREV]

                # Evict o
                hand = o[sieve_cache.PREV]
                oldkey = o[sieve_cache.KEY]
                hand[sieve_cache.NEXT] = o[sieve_cache.NEXT]
                o[sieve_cache.NEXT][sieve_cache.PREV] = hand
                del self.cache[oldkey]

                # Insert at head of linked list
                head = self.tail[sieve_cache.NEXT]
                new_head = [self.tail, head, key, result, True]
                head[sieve_cache.PREV] = self.tail[sieve_cache.NEXT] = self.cache[
                    key
                ] = new_head
            else:
                # Insert at head of linked list
                head = self.tail[sieve_cache.NEXT]
                new_head = [self.tail, head, key, result, True]
                head[sieve_cache.PREV] = self.tail[sieve_cache.NEXT] = self.cache[
                    key
                ] = new_head
                self.full = self.cache_len() >= self.maxsize

        return result
