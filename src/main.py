import typer
import os
from typing import Optional
from src.database import init_db, Candidate
from src.scraper import GitHubAPI
from src.database.models.base import db
from src.scraper.github import GitHubAPI


# Initialize Typer app, calling init_db on startup
app = typer.Typer(help="Talent scraper", callback=init_db)

@app.command()
def scrape(
    count: int = typer.Option(50, "--count", "-c", help="Number of profiles to scrape"),
):
    """
    Scrape GitHub profiles and analyze them with Claude
    """
    typer.echo(f"Scraping {count} GitHub profiles")
    
    # Get users from GitHub API search
    users = GitHubAPI.search_users(count=count)
    
    # Save matching users to a text file, appending each URL
    with open("profiles.txt", "a") as f:
        for user in users:
            f.write(f"{user['html_url']} MATCHES\n")
            print(f"{user['html_url']} MATCHES")


if __name__ == "__main__":
    app() 