from flask_caching import Cache

cache = Cache(config={
    "DEBUG": False,
    "CACHE_TYPE": "redis",
    "CACHE_REDIS_HOST": '101.227.48.127',
    "CACHE_REDIS_PORT": 6379,
    "CACHE_REDIS_PASSWORD": 'Lin927919732',
    "CACHE_REDIS_DB": 0,
    "CACHE_DEFAULT_TIMEOUT": 0,
})
