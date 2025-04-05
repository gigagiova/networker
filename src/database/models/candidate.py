import datetime
from peewee import CharField, TextField, IntegerField, FloatField, DateTimeField
from src.database.models.base import BaseModel


class Candidate(BaseModel):
    """Model for storing candidate information"""
    
    # Basic profile information
    name = CharField(null=True)
    github_url = CharField(unique=True)
    linkedin_url = CharField(null=True)
    
    # GitHub profile data
    contributions = IntegerField(null=True)
    
    # Analysis data
    last_scraped = DateTimeField(default=datetime.datetime.now)
    analysis = TextField(null=True)
    score = FloatField(null=True)
    
    class Meta:
        table_name = 'candidates'
        
    def __str__(self):
        """String representation of the candidate"""
        return f"{self.name or 'Unknown'} ({self.github_username or self.github_url})" 
