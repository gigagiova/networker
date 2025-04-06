from peewee import *
from datetime import datetime
from .base import BaseModel


class Session(BaseModel):
    """Tracks GitHub scraping sessions"""
    timestamp = DateTimeField(default=datetime.now)
    last_created_at = DateTimeField()  # Creation date of the last GitHub user processed
    profiles_scraped = IntegerField(default=0)

    class Meta:
        table_name = 'sessions'
