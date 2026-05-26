import redis

redis_client = redis.Redis(
    host="localhost",
    port=6379,
    socket_keepalive=True,
    retry_on_timeout=True,
    decode_responses=True
)