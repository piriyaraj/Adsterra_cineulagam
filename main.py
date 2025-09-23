#!/usr/bin/env python3
"""
Automated Tamil Cinema News Publisher
Main orchestrator for the news publishing pipeline
"""

import logging
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows console
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

from scraper import ArticleScraper
from blogger import BloggerPublisher
from telegram_bot import TelegramBot
from db import DatabaseManager

# Load environment variables
load_dotenv('env.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('cineulagam_publisher.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class NewsPublisher:
    """Main orchestrator class for the news publishing pipeline"""
    
    def __init__(self):
        """Initialize all components"""
        self.scraper = ArticleScraper()
        self.blogger = BloggerPublisher()
        self.telegram_bot = TelegramBot()
        self.db = DatabaseManager()
        
    def run_pipeline(self):
        """Execute the complete news publishing pipeline"""
        try:
            logger.info("Starting Tamil Cinema News Publisher Pipeline")
            
            # Step 1: Get last posted article URL from database
            last_posted_url = self.db.get_last_posted_article_url()
            
            # Step 2: Fetch only new articles since last post
            if last_posted_url:
                logger.info(f"Last posted article URL: {last_posted_url}")
                logger.info("Fetching new articles since last post...")
                articles = self.scraper.fetch_new_articles_since_last_post(last_posted_url)
            else:
                logger.info("No previous posts found. Fetching all articles from sitemap...")
                articles = self.scraper.fetch_articles_from_sitemap()
            
            if not articles:
                logger.warning("No new articles found to publish")
                return
            
            logger.info(f"Found {len(articles)} new articles to process")
            
            # Step 3: Process each article
            published_count = 0
            for i,article in enumerate(articles):
                # if i == 1:
                #     break
                try:
                    # Check if article already posted
                    if self.db.is_article_posted(article['url']):
                        try:
                            logger.info(f"Article already posted: {article['title']}")
                        except UnicodeEncodeError:
                            safe_title = article['title'].encode('ascii', 'replace').decode('ascii')
                            logger.info(f"Article already posted: {safe_title}")
                        continue
                    
                    # Scrape article details
                    try:
                        logger.info(f"Scraping article: {article['title']}")
                    except UnicodeEncodeError:
                        safe_title = article['title'].encode('ascii', 'replace').decode('ascii')
                        logger.info(f"Scraping article: {safe_title}")
                    article_details = self.scraper.scrape_article(article['url'])
                    
                    if not article_details:
                        logger.warning(f"Failed to scrape article: {article['url']}")
                        continue
                    
                    # Publish to Blogger
                    try:
                        logger.info(f"Publishing to Blogger: {article_details['title']}")
                    except UnicodeEncodeError:
                        safe_title = article_details['title'].encode('ascii', 'replace').decode('ascii')
                        logger.info(f"Publishing to Blogger: {safe_title}")
                    blogger_post = self.blogger.publish_post(article_details)
                    
                    if not blogger_post:
                        try:
                            logger.error(f"Failed to publish to Blogger: {article_details['title']}")
                        except UnicodeEncodeError:
                            safe_title = article_details['title'].encode('ascii', 'replace').decode('ascii')
                            logger.error(f"Failed to publish to Blogger: {safe_title}")
                        continue
                    
                    # Post to Telegram
                    try:
                        logger.info(f"Posting to Telegram: {article_details['title']}")
                    except UnicodeEncodeError:
                        safe_title = article_details['title'].encode('ascii', 'replace').decode('ascii')
                        logger.info(f"Posting to Telegram: {safe_title}")
                    telegram_success = self.telegram_bot.post_article(
                        title=article_details['title'],
                        content=article_details['content'],
                        blogger_url=blogger_post['url'],
                        image_url=article_details.get('image_url')
                    )
                    
                    if telegram_success:
                        # Store in database
                        self.db.store_posted_article(
                            url=article['url'],
                            title=article_details['title'],
                            blogger_id=blogger_post['id'],
                            posted_at=datetime.now()
                        )
                        published_count += 1
                        # Safe logging with Unicode handling
                        try:
                            logger.info(f"Successfully published: {article_details['title']}")
                        except UnicodeEncodeError:
                            # Fallback for console that doesn't support Unicode
                            safe_title = article_details['title'].encode('ascii', 'replace').decode('ascii')
                            logger.info(f"Successfully published: {safe_title}")
                    else:
                        try:
                            logger.error(f"Failed to post to Telegram: {article_details['title']}")
                        except UnicodeEncodeError:
                            safe_title = article_details['title'].encode('ascii', 'replace').decode('ascii')
                            logger.error(f"Failed to post to Telegram: {safe_title}")
                        
                except Exception as e:
                    logger.error(f"Error processing article {article.get('url', 'unknown')}: {str(e)}")
                    continue
            
            logger.info(f"Pipeline completed. Published {published_count} articles")
            
        except Exception as e:
            logger.error(f"Pipeline failed: {str(e)}")
            raise


def main():
    """Main entry point"""
    try:
        publisher = NewsPublisher()
        publisher.run_pipeline()
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
