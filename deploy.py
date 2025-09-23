#!/usr/bin/env python3
"""
Deployment and management script for the Tamil Cinema News Publisher
Provides utilities for testing, monitoring, and managing the application
"""

import argparse
import logging
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def run_tests():
    """Run connection tests"""
    logger.info("Running connection tests...")
    os.system("python test_connection.py")


def run_publisher():
    """Run the main publisher"""
    logger.info("Starting Tamil Cinema News Publisher...")
    os.system("python main.py")


def check_environment():
    """Check environment configuration"""
    required_vars = [
        'MONGODB_URI',
        'BLOGGER_BLOG_ID', 
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHANNEL_ID'
    ]
    
    missing = []
    for var in required_vars:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        logger.error(f"Missing environment variables: {', '.join(missing)}")
        logger.error("Please check your .env file")
        return False
    else:
        logger.info("Environment configuration looks good")
        return True


def show_stats():
    """Show database statistics"""
    try:
        from db import DatabaseManager
        
        db = DatabaseManager()
        if db.client:
            stats = db.get_stats()
            logger.info("Database Statistics:")
            for key, value in stats.items():
                logger.info(f"  {key}: {value}")
        else:
            logger.error("Database not connected")
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")


def list_recent_articles(limit=10):
    """List recent posted articles"""
    try:
        from db import DatabaseManager
        
        db = DatabaseManager()
        if db.client:
            articles = db.get_posted_articles(limit)
            logger.info(f"Recent {len(articles)} articles:")
            for i, article in enumerate(articles, 1):
                logger.info(f"  {i}. {article['title']} ({article['posted_at']})")
        else:
            logger.error("Database not connected")
    except Exception as e:
        logger.error(f"Error listing articles: {str(e)}")


def show_last_posted():
    """Show the last posted article URL"""
    try:
        from db import DatabaseManager
        
        db = DatabaseManager()
        if db.client:
            last_url = db.get_last_posted_article_url()
            if last_url:
                logger.info(f"Last posted article URL: {last_url}")
            else:
                logger.info("No articles have been posted yet")
        else:
            logger.error("Database not connected")
    except Exception as e:
        logger.error(f"Error getting last posted article: {str(e)}")


def send_test_telegram():
    """Send test message to Telegram"""
    try:
        from telegram_bot import TelegramBot
        
        bot = TelegramBot()
        if bot.send_test_message():
            logger.info("Test message sent successfully")
        else:
            logger.error("Failed to send test message")
    except Exception as e:
        logger.error(f"Error sending test message: {str(e)}")


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(description='Tamil Cinema News Publisher Management')
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Test command
    subparsers.add_parser('test', help='Run connection tests')
    
    # Run command
    subparsers.add_parser('run', help='Run the publisher')
    
    # Check command
    subparsers.add_parser('check', help='Check environment configuration')
    
    # Stats command
    subparsers.add_parser('stats', help='Show database statistics')
    
    # List command
    list_parser = subparsers.add_parser('list', help='List recent articles')
    list_parser.add_argument('--limit', type=int, default=10, help='Number of articles to show')
    
    # Test telegram command
    subparsers.add_parser('test-telegram', help='Send test message to Telegram')
    
    # Last posted command
    subparsers.add_parser('last-posted', help='Show last posted article URL')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'test':
        run_tests()
    elif args.command == 'run':
        if check_environment():
            run_publisher()
        else:
            sys.exit(1)
    elif args.command == 'check':
        check_environment()
    elif args.command == 'stats':
        show_stats()
    elif args.command == 'list':
        list_recent_articles(args.limit)
    elif args.command == 'test-telegram':
        send_test_telegram()
    elif args.command == 'last-posted':
        show_last_posted()


if __name__ == "__main__":
    main()
