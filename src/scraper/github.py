from typing import List, Dict
import requests
from datetime import datetime
import os
from time import sleep
from src.database.models.session import Session


class GitHubAPI:
    """GitHub API client for fetching user profiles"""

    base_url = "https://api.github.com"
    
    @staticmethod
    def _format_headers():
        """Headers for the GitHub API"""
        token = os.getenv("GITHUB_API_TOKEN")
        return {
            "Accept": "application/vnd.github.v3+json",
            "Authorization": f"token {token}" if token else None
        }

    @staticmethod
    def get_last_created_at():
        """Get the creation date of the last processed GitHub user"""
        last_session = Session.select().order_by(Session.last_created_at.desc()).first()
        return last_session.last_created_at if last_session else datetime(2018, 1, 1)

    @staticmethod
    def search_users(*, page: int = 1, count: int = 50) -> List[Dict]:
        """
        Search for users matching our criteria
        Returns list of user data dictionaries
        """
        
        # Search for users created before our last scraped date
        query = " ".join([
            "type:user",
            "followers:<50",
            "location:Italy",
            f"created:<{GitHubAPI.get_last_created_at().isoformat()}Z",
            "sort:created-desc"
        ])
        
        url = f"{GitHubAPI.base_url}/search/users"
        params = {"q": query, "page": page, "per_page": count}
        
        response = requests.get(url, headers=GitHubAPI._format_headers(), params=params)
        
        # If we are rate limited, wait and retry
        if response.status_code == 403:
            reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
            sleep_time = max(reset_time - datetime.now().timestamp(), 0)
            sleep(sleep_time + 1)
            return GitHubAPI.search_users(page=page, count=count)
            
        response.raise_for_status()
        items = response.json()["items"]
        
        # If we got results, create a new session
        if items:
            last_user = GitHubAPI.get_user_details(items[-1]["login"])
            Session.create(last_created_at=last_user["created_at"], profiles_scraped=len(items))

        return items


    @staticmethod
    def get_user_details(username: str) -> Dict:
        """Fetch detailed information for a specific user"""
        url = f"{GitHubAPI.base_url}/users/{username}"
        response = requests.get(url, headers=GitHubAPI._format_headers())
        response.raise_for_status()
        return response.json() 
