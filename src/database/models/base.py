import datetime
from peewee import Model, DateTimeField
from src.database.db import db

class BaseModel(Model):
    """Base model class that should be inherited by all models"""
    
    # Timestamps for record creation and updates
    created_at = DateTimeField(default=datetime.datetime.now)
    updated_at = DateTimeField(default=datetime.datetime.now)
    
    def save(self, *args, **kwargs):
        """Update the updated_at field on save"""
        self.updated_at = datetime.datetime.now()
        return super(BaseModel, self).save(*args, **kwargs)
        
    class Meta:
        database = db 