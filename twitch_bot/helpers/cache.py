from collections import defaultdict
from .clear_strings import parse_string
from datetime import timedelta


def spawn_cache(channels: list, users: str, streamers: str, database):
    cache = defaultdict(list)
    try:
        for channel in channels:
            cache[channel] = set(users)

        cache["streamers"] = set(streamers)

        send_from_redis_to_cache(cache, database)

    except BaseException as e:
        print(f"An exception ocurred while spawning cache: {e}")
    return cache


def add_to_session_cache(data, key, value):
    data[key].add(value)


def send_from_redis_to_cache(cache, conn):
    for key in cache.keys():
        for m in conn.smembers(key):
            parsed_member = m.decode("utf-8")
            cache[key].add(parsed_member)


def send_from_cache_to_redis(cache, conn, time: timedelta):
    with conn.pipeline() as pipe:
        for set_id, set_value in cache.items():
            pipe.sadd(set_id, *set_value)
            pipe.expire(set_id, time)
        pipe.execute()


# @run_once
def add_all_users_in_chat_to_cache(cache, key, chatters):
    print(f"Adicionou chatters ao cache de `{key}`: {chatters.all}")
    return [cache[key].add(c) for c in chatters.all]
