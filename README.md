# UF MANA

An energy-aware scheduling web application for students prone to burnout.

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Database**: MongoDB

## Quick Start

### Using Docker (recommended)

```bash
docker-compose up --build
```

Then open http://localhost:8501 in your browser.

## Project Structure

```
MANA/
├── backend/                # Backend FastAPI application
│   ├── app/               # Application logic
│   ├── tests/             # Unit tests
│   └── requirements.txt   # Backend dependencies
├── frontend/               # Frontend Streamlit application
│   ├── pages/             # Streamlit pages
│   ├── services/          # API service calls
│   └── requirements.txt   # Frontend dependencies
└── docker-compose.yml      # Docker configuration
```

## Setup Instructions

### Prerequisites

- Docker and Docker Compose installed
- MongoDB instance (local or cloud)

### Running Locally Without Docker

1. Install dependencies for the backend:

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Install dependencies for the frontend:

   ```bash
   cd frontend
   pip install -r requirements.txt
   ```

3. Start the backend server:

   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

4. Start the frontend application:

   ```bash
   cd frontend
   streamlit run app.py
   ```

5. Open http://localhost:8501 in your browser.
