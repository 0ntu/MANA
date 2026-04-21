# MANA Deployment Pipeline

## Prerequisites

1. **GitHub Secrets** — Set these in your repository settings:
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: Your Docker Hub access token
   - `DEPLOY_HOST`: Your production server IP/hostname
   - `DEPLOY_USER`: SSH username for deployment
   - `DEPLOY_KEY`: SSH private key (add as a secret, not in repo)

2. **Production Server Setup**:
   ```bash
   ssh your-server
   cd ~
   git clone <your-repo-url> mana
   cd mana
   ```

## Workflow Overview

The pipeline in `.github/workflows/deploy.yml` executes on every push:

### Build Stage
- Builds backend and frontend Docker images in parallel
- Pushes to Docker Hub only on `main` branch
- Caches layers using GitHub Actions cache for faster rebuilds

### Deploy Stage
- Runs only after successful build on `main` branch
- SSH into production server
- Pulls latest code and images
- Runs `docker compose up -d` to deploy services
- Cleans up dangling images

## Local Testing

Test your build locally before pushing:
```bash
docker compose build
docker compose up
```

Visit:
- Frontend: http://localhost:8501
- Backend API: http://localhost:8000

## Health Checks

- **Backend**: Uvicorn health endpoint (added HEALTHCHECK to Dockerfile)
- **Frontend**: Streamlit built-in health endpoint
- **MongoDB**: Native MongoDB health check

## Rollback

SSH to production and run:
```bash
docker compose down
git checkout <previous-commit>
docker compose up -d
```

## Notes

- Images tagged with commit SHA and `latest`
- Production deploys only from `main` branch
- Pull requests trigger build but not deployment
- MongoDB data persists in `mongodb_data` volume
