# UF MANA

An energy-aware scheduling web application for students prone to burnout.

## Tech Stack

- **Frontend**: Streamlit
- **Backend**: FastAPI
- **Database**: MongoDB

## Quick Start

### Using Docker (recommended)

```bash
docker compose up
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

## Demo Accounts

On first startup the backend seeds dummy data so you can explore the app immediately. All dummy accounts use the password **`password123`**.
In total, these accounts include more than 100 different data points spanning energy logs, tasks, and mana levels.

| Username | Password |
|----------|----------|
| alice | password123 |
| bob | password123 |
| carol | password123 |
| dave | password123 |
| eve | password123 |
| frank | password123 |
| grace | password123 |
| hank | password123 |
| iris | password123 |
| jack | password123 |

### Admin Panel

The admin panel is accessible by logging in with:

- **Username:** `admin`
- **Password:** `admin`

## Features

- Energy-aware scheduling
- Task management
- Dashboard with energy usage insights

## Troubleshooting

- If Docker fails to start, ensure ports 8501 and 8000 are not in use.
- Check MongoDB connection settings in `docker-compose.yml` or `.env` file.
