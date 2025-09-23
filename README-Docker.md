# Docker Hub Deployment Guide

This guide will help you deploy your Cineulagam Publisher application to Docker Hub.

## Prerequisites

1. **Docker installed** on your system
2. **Docker Hub account** (create one at https://hub.docker.com)
3. **Docker Hub repository** created (public or private)

## Setup Steps

### 1. Create Docker Hub Repository

1. Go to [Docker Hub](https://hub.docker.com)
2. Click "Create Repository"
3. Name it `cineulagam-publisher` (or your preferred name)
4. Choose Public or Private
5. Click "Create"

### 2. Login to Docker Hub

```bash
docker login
```

Enter your Docker Hub username and password when prompted.

### 3. Update Configuration

Edit the deployment script and replace `your-dockerhub-username` with your actual Docker Hub username:

**For Linux/Mac:**
```bash
# Edit docker-hub-deploy.sh
nano docker-hub-deploy.sh
```

**For Windows:**
```cmd
REM Edit docker-hub-deploy.bat
notepad docker-hub-deploy.bat
```

Change this line:
```bash
DOCKER_USERNAME="your-dockerhub-username"  # Replace with your Docker Hub username
```

### 4. Deploy to Docker Hub

**For Linux/Mac:**
```bash
chmod +x docker-hub-deploy.sh
./docker-hub-deploy.sh
```

**For Windows:**
```cmd
docker-hub-deploy.bat
```

### 5. Manual Deployment (Alternative)

If you prefer manual steps:

```bash
# 1. Build the image
docker build -t your-username/cineulagam-publisher:latest .

# 2. Push to Docker Hub
docker push your-username/cineulagam-publisher:latest
```

## Using Your Published Image

Once pushed, others can use your image:

```bash
# Pull and run
docker run -p 5000:5000 your-username/cineulagam-publisher:latest

# Or with docker-compose
docker-compose up
```

## Versioning

To push different versions:

```bash
# Build with specific tag
docker build -t your-username/cineulagam-publisher:v1.0.0 .

# Push specific version
docker push your-username/cineulagam-publisher:v1.0.0

# Push latest
docker tag your-username/cineulagam-publisher:v1.0.0 your-username/cineulagam-publisher:latest
docker push your-username/cineulagam-publisher:latest
```

## Docker Hub Repository Settings

In your Docker Hub repository, you can:

1. **Add description** and documentation
2. **Set up automated builds** from GitHub
3. **Configure webhooks** for CI/CD
4. **Manage access** for private repositories

## Troubleshooting

### Login Issues
```bash
# Logout and login again
docker logout
docker login
```

### Permission Denied
- Make sure you're logged in with `docker login`
- Check your Docker Hub username is correct
- Verify the repository exists and you have push access

### Build Issues
- Check Dockerfile syntax
- Ensure all dependencies are in requirements.txt
- Test locally first: `docker build -t test .`

## Security Notes

- Never commit sensitive data (API keys, passwords) to Docker images
- Use environment variables for configuration
- Consider using Docker secrets for production
- Regularly update base images for security patches
