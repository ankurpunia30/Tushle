from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "automation_dashboard",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=['app.tasks.ai_tasks', 'app.tasks.email_tasks', 'app.tasks.content_tasks']
)

# Configuration
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    result_expires=3600,
)

# Periodic tasks
celery_app.conf.beat_schedule = {
    'daily-topic-research': {
        'task': 'app.tasks.ai_tasks.daily_topic_research',
        'schedule': 60.0 * 60.0 * 24.0,  # Daily
    },
    'follow-up-leads': {
        'task': 'app.tasks.email_tasks.follow_up_leads',
        'schedule': 60.0 * 60.0 * 2.0,  # Every 2 hours
    },
    'auto-post-content': {
        'task': 'app.tasks.content_tasks.auto_post_scheduled_content',
        'schedule': 60.0 * 15.0,  # Every 15 minutes
    },
}
