# Networker

A GitHub talent scraper that uses LLMs to identify promising candidates based on their profiles.

## Overview
Networker is a CLI tool that:
- Scrapes GitHub profiles
- Analyzes profiles using Claude (LLM)
- Stores candidate data in a SQL database
- Provides summaries of top candidates

## Features
- Automated GitHub profile scraping
- LLM-powered candidate evaluation
- Persistent storage to avoid duplicate processing
- Concise talent reports

## Tech Stack
- Python
- Typer (CLI framework)
- Postgres
- Claude API for LLM analysis
- Selenium for web scraping

## Local Development

### Prerequisites
- Docker
- Make
- Python 3.10+

### Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/networker.git
cd networker

# Install dependencies
pip install -r requirements.txt

# Start PostgreSQL in Docker and create environment file
make start
make setup-env

# Edit .env to add your API keys
nano .env

# Run the CLI tool
python -m src.main scrape --count 10
```

### Database Configuration
The application supports both individual database variables and a DATABASE_URL:

```
# Individual variables (preferred for local development)
DB_NAME=networker
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Or complete URL (used by Heroku)
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/networker
```

### Makefile Commands
- `make start` - Start PostgreSQL Docker container
- `make stop` - Stop the container
- `make restart` - Restart the container
- `make logs` - View container logs
- `make psql` - Connect to the database via psql
- `make status` - Check container status
- `make setup-env` - Create .env file from template with correct DB settings

## Project Structure
```
src/
├── __init__.py
├── main.py          # CLI entry point using Typer
├── scraper/         # GitHub scraping functionality
├── analyzer/        # Claude integration for analysis
└── database/        # Postgres database management
    ├── db.py        # Database connection handling
    └── models/      # Database models
        ├── base.py  # BaseModel definition
        └── candidate.py  # Candidate model
```

## Deployment
Networker can be deployed on Heroku with the following steps:

1. Create a Heroku app with Postgres add-on
2. Set required environment variables
3. Deploy the application
4. Configure the Heroku scheduler for periodic runs

## Roadmap
- Additional CLI commands for report generation
- Profile filtering options
- Advanced candidate matching algorithms
- Web interface 