# Docker Hub Deployment Guide for Cineulagam Publisher

## Quick Start

### 1. Build and Push to Docker Hub

You've already updated the username in `docker-hub-deploy.bat`. Now run:

```cmd
docker-hub-deploy.bat
```

### 2. Run the Container

After pushing to Docker Hub, you can run your container with:

```bash
# Basic run
docker run -p 5000:5000 piriyaraj1998/cineulagam-publisher:latest

# With environment variables
docker run -p 5000:5000 \
  -e MONGODB_URI="mongodb+srv://piriyaraj1998_db_user:cT0Qz5R4DoFad1Ef@cineulagam.jcy8gsj.mongodb.net/?retryWrites=true&w=majority&appName=Cineulagam" \
  -e MONGODB_DATABASE="cineulagam" \
  -e MONGODB_COLLECTION="posted_articles" \
  -e BLOGGER_BLOG_ID="6380171182056049355" \
  -e TELEGRAM_BOT_TOKEN="your_telegram_bot_token" \
  -e TELEGRAM_CHANNEL_ID="@your_channel" \
  piriyaraj1998/cineulagam-publisher:latest
```

## Environment Variables

The application requires these environment variables:

### Required:
- `MONGODB_URI` - Your MongoDB Atlas connection string
- `BLOGGER_BLOG_ID` - Your Blogger blog ID
- `TELEGRAM_BOT_TOKEN` - Your Telegram bot token
- `TELEGRAM_CHANNEL_ID` - Your Telegram channel ID

### Optional:
- `MONGODB_DATABASE` - Database name (default: cineulagam)
- `MONGODB_COLLECTION` - Collection name (default: posted_articles)
- `BLOGGER_CREDENTIALS_FILE` - Credentials file (default: credentials.json)
- `BLOGGER_TOKEN_FILE` - Token file (default: token.pickle)
- `LOG_LEVEL` - Log level (default: INFO)
- `LOG_FILE` - Log file name (default: cineulagam_publisher.log)

## Docker Compose (Recommended)

Use the updated `docker-compose.yml` for easier deployment:

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

## Production Deployment

### 1. Update Environment Variables

Edit `docker-compose.yml` and replace the placeholder values:

```yaml
environment:
  - TELEGRAM_BOT_TOKEN=your_actual_telegram_bot_token
  - TELEGRAM_CHANNEL_ID=@your_actual_channel
```

### 2. Deploy to Production Server

```bash
# Copy files to server
scp -r . user@your-server:/path/to/app/

# On the server
cd /path/to/app/
docker-compose up -d
```

## Security Notes

⚠️ **Important Security Considerations:**

1. **Never commit sensitive data** to Git
2. **Use Docker secrets** for production
3. **Rotate API keys** regularly
4. **Use environment files** for sensitive data

### Using Docker Secrets (Production)

```bash
# Create secrets
echo "your_mongodb_uri" | docker secret create mongodb_uri -
echo "your_telegram_token" | docker secret create telegram_token -

# Update docker-compose.yml to use secrets
```

## Troubleshooting

### MongoDB Connection Issues

1. **Check MongoDB URI format:**
   ```
   mongodb+srv://username:password@cluster.mongodb.net/database?retryWrites=true&w=majority
   ```

2. **Verify network access:**
   - Ensure your IP is whitelisted in MongoDB Atlas
   - Check firewall settings

3. **Test connection:**
   ```bash
   docker run --rm -e MONGODB_URI="your_uri" piriyaraj1998/cineulagam-publisher:latest python -c "from db import DatabaseManager; db = DatabaseManager(); print('Connected!' if db.client else 'Failed!')"
   ```

### Application Not Starting

1. **Check logs:**
   ```bash
   docker logs cineulagam-publisher
   ```

2. **Verify environment variables:**
   ```bash
   docker exec cineulagam-publisher env | grep -E "(MONGODB|BLOGGER|TELEGRAM)"
   ```

### Build Issues

1. **Clear Docker cache:**
   ```bash
   docker system prune -a
   ```

2. **Rebuild without cache:**
   ```bash
   docker build --no-cache -t piriyaraj1998/cineulagam-publisher:latest .
   ```

## Monitoring

### Health Checks

The container includes health checks. Monitor with:

```bash
docker ps
# Check STATUS column for "healthy" or "unhealthy"
```

### Logs

```bash
# View real-time logs
docker logs -f cineulagam-publisher

# View last 100 lines
docker logs --tail 100 cineulagam-publisher
```

## Scaling

### Multiple Instances

```yaml
# docker-compose.yml
services:
  cineulagam-app:
    # ... existing config
    deploy:
      replicas: 3
```

### Load Balancing

Use nginx or traefik for load balancing multiple instances.

## Updates

### Updating the Application

1. **Build new image:**
   ```bash
   docker build -t piriyaraj1998/cineulagam-publisher:v1.1.0 .
   ```

2. **Push to Docker Hub:**
   ```bash
   docker push piriyaraj1998/cineulagam-publisher:v1.1.0
   ```

3. **Update production:**
   ```bash
   docker-compose pull
   docker-compose up -d
   ```

## Support

If you encounter issues:

1. Check the logs first
2. Verify environment variables
3. Test MongoDB connection
4. Check Docker Hub image status

Your Docker Hub repository: https://hub.docker.com/r/piriyaraj1998/cineulagam-publisher
