from typing import Dict
import requests
from datetime import datetime
import os
from time import sleep
from src.database.models.session import Session


class GitHubAPI:
    """GitHub API client for fetching user profiles"""

    base_url = "https://api.github.com"
    graphql_url = "https://api.github.com/graphql"
    
    @staticmethod
    def _format_headers():
        """Format headers for GitHub REST API requests"""
        token = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_API_TOKEN")
        if not token:
            raise ValueError("Either GITHUB_TOKEN or GITHUB_API_TOKEN environment variable is required")
            
        return {
            "Authorization": f"token {token}",  # REST API uses 'token' prefix
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Networker-Scraper"  # GitHub requires a User-Agent
        }

    @staticmethod
    def _format_graphql_headers():
        """Format headers specifically for GitHub GraphQL API"""
        token = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_API_TOKEN")
        if not token:
            raise ValueError("Either GITHUB_TOKEN or GITHUB_API_TOKEN environment variable is required")
            
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": "Networker-Scraper"
        }

    @staticmethod
    def get_last_created_at():
        """Get the creation date of the last processed GitHub user"""
        last_session = Session.select().order_by(Session.last_created_at.desc()).first()
        return last_session.last_created_at if last_session else datetime(2018, 1, 1)

    @staticmethod
    def search_users(*, page: int = 1, count: int = 50):
        """
        Search for users matching our criteria
        Returns list of user data dictionaries
        """
        
        # Search for users created after our last scraped date
        query = " ".join([
            "type:user",
            "followers:<50",
            "location:Italy",
            "repos:>2",
            "created:2020-01-01..2024-12-31",
            "sort:repositories-desc"
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

        for item in items:
            if GitHubAPI.meets_criteria(item["login"]):
                yield item


    @staticmethod
    def get_user_details(username: str) -> Dict:
        """Fetch detailed information for a specific user"""
        url = f"{GitHubAPI.base_url}/users/{username}"
        response = requests.get(url, headers=GitHubAPI._format_headers())
        response.raise_for_status()
        return response.json()

    @staticmethod
    def meets_criteria(username: str) -> bool:
        """
        Check if a user meets our minimum criteria:
        - At least 800 contributions in last 18 months
        - At least 3 public non-forked repos
        """
        
        # Get list of repos to check non-forked count
        repos_url = f"{GitHubAPI.base_url}/users/{username}/repos"
        response = requests.get(repos_url, headers=GitHubAPI._format_headers())
        response.raise_for_status()
        repos = response.json()
        
        # Count non-forked repos
        non_forked_repos = sum(1 for repo in repos if not repo['fork'])
        
        # Get contribution count
        contribution_count = GitHubAPI._get_contribution_count(username)
        
        return contribution_count >= 800 and non_forked_repos >= 3

    @staticmethod
    def _get_contribution_count(username: str) -> int:
        """Get the total number of contributions for a user in the last year using GraphQL"""
        query = """
        query($username: String!) {
          user(login: $username) {
            contributionsCollection {
              totalCommitContributions
              totalIssueContributions
              totalPullRequestContributions
              totalPullRequestReviewContributions
              restrictedContributionsCount
            }
          }
        }
        """
        
        variables = {"username": username}
        response = requests.post(
            GitHubAPI.graphql_url,
            headers=GitHubAPI._format_graphql_headers(),
            json={"query": query, "variables": variables}
        )
        response.raise_for_status()
        
        data = response.json()
        try:
            collection = data["data"]["user"]["contributionsCollection"]
            return (
                collection["totalCommitContributions"] +
                collection["totalIssueContributions"] +
                collection["totalPullRequestContributions"] +
                collection["totalPullRequestReviewContributions"] +
                collection["restrictedContributionsCount"]
            )
        except (KeyError, TypeError):
            return 0 
