# Agentic AI Healthcare Claims Processing System

An intelligent healthcare claims processing system that automatically reads emails, extracts claim information, and performs clinical adjudication using AI agents.

## Overview

This system automates the healthcare claims processing workflow by:
- Reading unread emails from Gmail with specific labels
- Extracting claim data using OpenAI's GPT models
- Validating member information and policy balances
- Performing clinical adjudication with policy context
- Automatically approving or denying claims based on medical necessity and coverage

## Key Features

- **Email Integration**: Connects to Gmail API to fetch unread emails from designated labels
- **AI-Powered Data Extraction**: Uses OpenAI GPT-4 to extract structured claim data from email content
- **Member Validation**: Checks member existence and policy balance before processing
- **Clinical Adjudication**: AI-driven medical necessity evaluation with policy context
- **Database Management**: Stores emails, claims, members, and policies in structured databases
- **Automated Workflow**: End-to-end processing from email receipt to claim decision

## System Architecture

```
Gmail → Email Reader → AI Agent → Database → Clinical Adjudication → Final Decision
```

## Core Components

- `main.py` - Main orchestration script
- `gmail_reader.py` - Gmail API integration
- `openai_agent.py` - AI agent for data extraction and clinical decisions
- `claims_db.py` - Claims database management
- `members_db.py` - Member information database
- `policies_db.py` - Policy database with coverage details
- `db_manager.py` - General database utilities

## Prerequisites

- Python 3.8+
- Gmail API credentials
- OpenAI API key
- PostgreSQL database

## Installation

1. Clone the repository
2. Create virtual environment:
   ```bash
   python -m venv myenv
   myenv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables in `.env`:
   ```
   OPENAI_API_KEY=your_openai_api_key
   DATABASE_URL=your_postgresql_connection_string
   ```

5. Configure Gmail API:
   - Place `credentials.json` in the project directory
   - Run the application to complete OAuth flow

6. Initialize database:
   ```sql
   CREATE DATABASE EmailStore;
   ```

## Usage

Run the main processing script:
```bash
python main.py
```

The system will:
1. Fetch unread emails from the 'Agentic_AI' Gmail label
2. Extract claim information using AI
3. Validate member and policy data
4. Perform clinical adjudication
5. Update claim status and member balances
6. Mark processed emails as read

## Workflow Process

1. **Email Retrieval**: Fetches unread emails with specific labels
2. **Data Extraction**: AI extracts member ID, diagnosis, service, and amount
3. **Member Validation**: Checks if member exists and has sufficient balance
4. **Policy Retrieval**: Gets relevant policy context for adjudication
5. **Clinical Review**: AI evaluates medical necessity against policy terms
6. **Decision Making**: Combines financial and clinical factors for final decision
7. **Balance Update**: Deducts approved amounts from member balances
8. **Email Management**: Marks processed emails as read

## Database Schema

- **emails**: Stores processed email metadata
- **claims**: Tracks all claim submissions and statuses
- **members**: Member information and policy balances
- **policies**: Policy terms and coverage details

## Configuration

- Modify Gmail label names in `main.py`
- Adjust AI model parameters in `openai_agent.py`
- Configure database connections in respective DB modules

## Security Notes

- Keep `credentials.json` and `.env` files secure
- Use environment variables for sensitive data
- Implement proper access controls for production use

## Contributing

1. Follow existing code structure
2. Add appropriate error handling
3. Update documentation for new features
4. Test with sample data before production use