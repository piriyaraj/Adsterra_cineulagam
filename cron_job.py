#!/usr/bin/env python3
"""
Cron job wrapper for the Tamil Cinema News Publisher
This script is designed to be run by cron every 2-3 hours
"""

import logging
import sys
import os
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging for cron
log_file = os.getenv('LOG_FILE', 'cineulagam_publisher.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main cron job function"""
    try:
        logger.info("="*60)
        logger.info(f"Starting scheduled run at {datetime.now()}")
        logger.info("="*60)
        
        # Import and run the main publisher
        from main import NewsPublisher
        
        publisher = NewsPublisher()
        publisher.run_pipeline()
        
        logger.info("="*60)
        logger.info(f"Scheduled run completed at {datetime.now()}")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"Cron job failed: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
