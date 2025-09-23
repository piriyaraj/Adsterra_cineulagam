#!/usr/bin/env python3
"""
Test script to verify all connections and configurations
Run this before deploying to ensure everything is set up correctly
"""

import logging
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def test_mongodb():
    """Test MongoDB connection"""
    try:
        from db import DatabaseManager
        
        logger.info("Testing MongoDB connection...")
        db = DatabaseManager()
        
        if db.client:
            # Test basic operations
            stats = db.get_stats()
            logger.info(f"MongoDB connection successful. Stats: {stats}")
            return True
        else:
            logger.error("MongoDB connection failed")
            return False
            
    except Exception as e:
        logger.error(f"MongoDB test failed: {str(e)}")
        return False


def test_blogger():
    """Test Blogger API connection"""
    try:
        from blogger import BloggerPublisher
        
        logger.info("Testing Blogger API connection...")
        blogger = BloggerPublisher()
        
        if blogger.service:
            # Test getting blog info
            blog_info = blogger.get_blog_info()
            if blog_info:
                logger.info(f"Blogger connection successful. Blog: {blog_info.get('name')}")
                return True
            else:
                logger.error("Failed to get blog info")
                return False
        else:
            logger.error("Blogger service not initialized")
            return False
            
    except Exception as e:
        logger.error(f"Blogger test failed: {str(e)}")
        return False


def test_telegram():
    """Test Telegram Bot connection"""
    try:
        from telegram_bot import TelegramBot
        
        logger.info("Testing Telegram Bot connection...")
        bot = TelegramBot()
        
        if bot.bot_token and bot.channel_id:
            # Test getting channel info
            channel_info = bot.get_channel_info()
            if channel_info:
                logger.info(f"Telegram connection successful. Channel: {channel_info.get('title')}")
                return True
            else:
                logger.error("Failed to get channel info")
                return False
        else:
            logger.error("Telegram bot not properly configured")
            return False
            
    except Exception as e:
        logger.error(f"Telegram test failed: {str(e)}")
        return False


def test_scraper():
    """Test article scraper"""
    try:
        from scraper import ArticleScraper
        
        logger.info("Testing article scraper...")
        scraper = ArticleScraper()
        
        # Test fetching sitemap
        articles = scraper.fetch_articles_from_sitemap()
        if articles:
            logger.info(f"Scraper test successful. Found {len(articles)} articles")
            return True
        else:
            logger.warning("No articles found in sitemap")
            return True  # This might be normal
            
    except Exception as e:
        logger.error(f"Scraper test failed: {str(e)}")
        return False


def check_environment():
    """Check if all required environment variables are set"""
    required_vars = [
        'MONGODB_URI',
        'BLOGGER_BLOG_ID',
        'TELEGRAM_BOT_TOKEN',
        'TELEGRAM_CHANNEL_ID'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        logger.error(f"Missing required environment variables: {', '.join(missing_vars)}")
        return False
    else:
        logger.info("All required environment variables are set")
        return True


def main():
    """Run all tests"""
    logger.info("Starting connection tests...")
    
    tests = [
        ("Environment Variables", check_environment),
        ("MongoDB", test_mongodb),
        ("Blogger API", test_blogger),
        ("Telegram Bot", test_telegram),
        ("Article Scraper", test_scraper)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running {test_name} test...")
        result = test_func()
        results.append((test_name, result))
        
        if result:
            logger.info(f"✅ {test_name} test PASSED")
        else:
            logger.error(f"❌ {test_name} test FAILED")
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "PASSED" if result else "FAILED"
        logger.info(f"{test_name}: {status}")
    
    logger.info(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! Your setup is ready.")
        return 0
    else:
        logger.error("❌ Some tests failed. Please check the configuration.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
