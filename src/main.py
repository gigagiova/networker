import typer
import os
from typing import Optional
from src.database import init_db, Candidate
from src.scraper import GitHubAPI


# Initialize Typer app, calling init_db on startup
app = typer.Typer(help="Talent scraper", callback=init_db)


@app.command()
def scrape(
    count: int = typer.Option(10, "--count", "-c", help="Number of profiles to scrape"),
    
):
    """
    Scrape GitHub profiles and analyze them with Claude
    """
    typer.echo(f"Scraping {count} GitHub profiles")
    
    users = GitHubAPI.search_users(count=count)
    for user in users:
        print(user)
        github_url = user["html_url"]


if __name__ == "__main__":
    app() 