from arq.connections import RedisSettings
from app.core.config import settings

redis_settings = RedisSettings.from_dsn(settings.REDIS_URL)

from app.workers.image_tasks import generate_watermark

class WorkerSettings:
    redis_settings = redis_settings
    functions = [generate_watermark] # To be populated with tasks
    queue_name = 'arq:queue'
