from arq.connections import RedisSettings
from app.core.config import settings

redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)

class WorkerSettings:
    redis_settings = redis_settings
    functions = [] # To be populated with tasks
    queue_name = 'arq:queue'
