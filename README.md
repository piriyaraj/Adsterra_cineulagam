# Automated Tamil Cinema News Publisher

An automated system that fetches Tamil cinema news articles from Cineulagam.com, processes them, and publishes them to Blogger and Telegram channels.

## Features

- 🔍 **Sitemap Parsing**: Automatically fetches article URLs from the sitemap
- 📰 **Article Scraping**: Extracts title, content, and images from articles
- ✍️ **Content Processing**: Summarizes and rewrites content to avoid copyright issues
- 📝 **Blogger Publishing**: Publishes articles to Google Blogger
- 📱 **Telegram Integration**: Shares articles to Telegram channels
- 🗄️ **MongoDB Tracking**: Stores posted articles to prevent duplicates
- ⏰ **Scheduled Execution**: Designed for cron job execution every 2-3 hours
- 🚀 **Smart Processing**: Only processes new articles since the last posted article

## Project Structure

```
cineulagam-publisher/
├── main.py              # Main orchestrator
├── scraper.py           # Article scraping and sitemap parsing
├── blogger.py           # Blogger API integration
├── telegram_bot.py      # Telegram Bot API integration
├── db.py               # MongoDB Atlas integration
├── requirements.txt    # Python dependencies
├── env.example         # Environment variables template
└── README.md           # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Copy `env.example` to `.env` and fill in your credentials:

```bash
cp env.example .env
```

Edit `.env` with your actual values:

```env
# MongoDB Atlas Configuration
MONGODB_URI=mongodb+srv://piriyaraj1998_db_user:cT0Qz5R4DoFad1Ef@cineulagam.jcy8gsj.mongodb.net/?retryWrites=true&w=majority&appName=Cineulagam
MONGODB_DATABASE=cineulagam
MONGODB_COLLECTION=posted_articles

# Blogger API Configuration
BLOGGER_BLOG_ID=your_blog_id_here
BLOGGER_CREDENTIALS_FILE=credentials.json
BLOGGER_TOKEN_FILE=token.pickle

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
TELEGRAM_CHANNEL_ID=@your_channel_username_or_channel_id
```

### 3. Google Blogger API Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing one
3. Enable the Blogger API v3
4. Create credentials (OAuth 2.0 Client ID)
5. Download the credentials JSON file and save as `credentials.json`
6. Get your Blog ID from your Blogger dashboard

### 4. Telegram Bot Setup

1. Create a new bot with [@BotFather](https://t.me/botfather)
2. Get the bot token
3. Add the bot to your channel as an administrator
4. Get your channel ID (use @userinfobot or similar)

### 5. MongoDB Atlas Setup

The MongoDB connection string is already provided in the example. The database and collection will be created automatically.

## Usage

### Manual Execution

```bash
python main.py
```

### Management Commands

Use the deploy script for various management tasks:

```bash
# Run the publisher
python deploy.py run

# Test all connections
python deploy.py test

# Check environment configuration
python deploy.py check

# Show database statistics
python deploy.py stats

# List recent posted articles
python deploy.py list --limit 20

# Show last posted article URL
python deploy.py last-posted

# Send test message to Telegram
python deploy.py test-telegram
```

### Scheduled Execution (Cron)

Add to your crontab for every 2 hours:

```bash
0 */2 * * * cd /path/to/project && python cron_job.py
```

### Render.com Deployment

1. Connect your GitHub repository to Render
2. Create a new Web Service
3. Set build command: `pip install -r requirements.txt`
4. Set start command: `python main.py`
5. Add environment variables in Render dashboard
6. For scheduled execution, use Render Cron Jobs

## Configuration Options

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `MONGODB_URI` | MongoDB Atlas connection string | Yes |
| `MONGODB_DATABASE` | Database name | No (default: cineulagam) |
| `MONGODB_COLLECTION` | Collection name | No (default: posted_articles) |
| `BLOGGER_BLOG_ID` | Your Blogger blog ID | Yes |
| `BLOGGER_CREDENTIALS_FILE` | Path to Google credentials JSON | No (default: credentials.json) |
| `BLOGGER_TOKEN_FILE` | Path to store OAuth token | No (default: token.pickle) |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | Yes |
| `TELEGRAM_CHANNEL_ID` | Your Telegram channel ID | Yes |

## Logging

The application logs all activities to both console and `cineulagam_publisher.log` file. Log levels can be configured via environment variables.

## Error Handling

- Network timeouts and retries
- Duplicate article prevention
- Graceful failure handling
- Comprehensive logging

## Security Notes

- Never commit `.env` file to version control
- Keep your API tokens secure
- Use environment variables for all sensitive data
- Regularly rotate your API keys

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Check your connection string
   - Ensure your IP is whitelisted in MongoDB Atlas

2. **Blogger Authentication Failed**
   - Verify your credentials.json file
   - Check if Blogger API is enabled
   - Ensure your blog ID is correct

3. **Telegram Posting Failed**
   - Verify bot token and channel ID
   - Ensure bot is admin in the channel
   - Check message formatting

4. **Scraping Issues**
   - Website structure might have changed
   - Check if the site is accessible
   - Verify sitemap URL

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational and personal use. Please respect the terms of service of the websites you're scraping and the APIs you're using.


dabatabase: Piriyrarj1998
blogger: Techfarm
