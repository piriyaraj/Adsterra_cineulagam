#!/usr/bin/env python3
"""
MongoDB Atlas integration for storing posted articles
Handles database operations and article tracking
"""

import logging
import os
from datetime import datetime
from typing import Optional, Dict, Any
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, DuplicateKeyError
import urllib.parse

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Handles MongoDB operations for article tracking"""
    
    def __init__(self):
        """Initialize MongoDB connection"""
        self.client = None
        self.db = None
        self.collection = None
        
        # MongoDB connection details
        self.mongo_uri = os.getenv('MONGODB_URI',"mongodb+srv://piriyaraj1998_db_user:cT0Qz5R4DoFad1Ef@cineulagam.jcy8gsj.mongodb.net/?retryWrites=true&w=majority&appName=Cineulagam")
        self.database_name = os.getenv('MONGODB_DATABASE', 'cineulagam')
        self.collection_name = os.getenv('MONGODB_COLLECTION', 'posted_articles')
        
        if not self.mongo_uri:
            logger.error("MONGODB_URI not found in environment variables")
            return
        
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB Atlas"""
        try:
            # Parse the URI to ensure proper encoding
            parsed_uri = urllib.parse.urlparse(self.mongo_uri)
            
            # Create MongoDB client
            self.client = MongoClient(
                self.mongo_uri,
                serverSelectionTimeoutMS=5000,  # 5 second timeout
                connectTimeoutMS=10000,  # 10 second timeout
                socketTimeoutMS=20000,  # 20 second timeout
                retryWrites=True
            )
            
            # Test the connection
            self.client.admin.command('ping')
            
            # Get database and collection
            self.db = self.client[self.database_name]
            self.collection = self.db[self.collection_name]
            
            # Create indexes for better performance
            self._create_indexes()
            
            logger.info(f"Successfully connected to MongoDB Atlas: {self.database_name}.{self.collection_name}")
            
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB Atlas: {str(e)}")
            self.client = None
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {str(e)}")
            self.client = None
    
    def _create_indexes(self):
        """Create necessary indexes for better performance"""
        try:
            # Create unique index on URL to prevent duplicates
            self.collection.create_index("url", unique=True)
            
            # Create index on posted_at for time-based queries
            self.collection.create_index("posted_at")
            
            # Create index on blogger_id for cross-referencing
            self.collection.create_index("blogger_id")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.warning(f"Failed to create indexes: {str(e)}")
    
    def is_article_posted(self, url: str) -> bool:
        """
        Check if an article has already been posted
        Returns True if article exists, False otherwise
        """
        if self.collection is None:
            logger.error("Database not connected")
            return False
        
        try:
            result = self.collection.find_one({"url": url})
            return result is not None
            
        except Exception as e:
            logger.error(f"Error checking if article is posted: {str(e)}")
            return False
    
    def store_posted_article(self, url: str, title: str, blogger_id: str, posted_at: datetime) -> bool:
        """
        Store information about a posted article
        Returns True if successful, False otherwise
        """
        if self.collection is None:
            logger.error("Database not connected")
            return False
        
        try:
            article_doc = {
                "url": url,
                "title": title,
                "blogger_id": blogger_id,
                "posted_at": posted_at,
                "created_at": datetime.now()
            }
            
            result = self.collection.insert_one(article_doc)
            
            if result.inserted_id:
                logger.info(f"Successfully stored article: {title}")
                return True
            else:
                logger.error("Failed to store article - no inserted ID")
                return False
                
        except DuplicateKeyError:
            logger.warning(f"Article already exists in database: {url}")
            return True
        except Exception as e:
            logger.error(f"Error storing article: {str(e)}")
            return False
    
    def get_posted_articles(self, limit: int = 100) -> list:
        """
        Get list of posted articles
        Returns list of article documents
        """
        if self.collection is None:
            logger.error("Database not connected")
            return []
        
        try:
            cursor = self.collection.find().sort("posted_at", -1).limit(limit)
            articles = list(cursor)
            
            # Convert ObjectId to string for JSON serialization
            for article in articles:
                article['_id'] = str(article['_id'])
            
            return articles
            
        except Exception as e:
            logger.error(f"Error getting posted articles: {str(e)}")
            return []
    
    def get_article_by_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get article details by URL
        Returns article document or None
        """
        if self.collection is None:
            logger.error("Database not connected")
            return None
        
        try:
            article = self.collection.find_one({"url": url})
            if article:
                article['_id'] = str(article['_id'])
            return article
            
        except Exception as e:
            logger.error(f"Error getting article by URL: {str(e)}")
            return None
    
    def get_last_posted_article_url(self) -> Optional[str]:
        """
        Get the URL of the most recently posted article
        Returns URL string or None if no articles found
        """
        if self.collection is None:
            logger.error("Database not connected")
            return None
        
        try:
            # Get the most recent article by posted_at date
            last_article = self.collection.find_one(
                sort=[("posted_at", -1)]
            )
            
            if last_article:
                logger.info(f"Last posted article: {last_article.get('title', 'Unknown')}")
                return last_article.get('url')
            else:
                logger.info("No articles found in database")
                return None
                
        except Exception as e:
            logger.error(f"Error getting last posted article: {str(e)}")
            return None
    
    def delete_article(self, url: str) -> bool:
        """
        Delete an article from the database
        Returns True if successful, False otherwise
        """
        if self.collection is None:
            logger.error("Database not connected")
            return False
        
        try:
            result = self.collection.delete_one({"url": url})
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error deleting article: {str(e)}")
            return False
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get database statistics
        Returns dictionary with various stats
        """
        if self.collection is None:
            return {"error": "Database not connected"}
        
        try:
            total_articles = self.collection.count_documents({})
            
            # Get articles posted today
            today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            today_articles = self.collection.count_documents({"posted_at": {"$gte": today}})
            
            # Get most recent article
            recent_article = self.collection.find_one(sort=[("posted_at", -1)])
            
            stats = {
                "total_articles": total_articles,
                "today_articles": today_articles,
                "most_recent": recent_article.get("title") if recent_article else None,
                "most_recent_date": recent_article.get("posted_at") if recent_article else None
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting stats: {str(e)}")
            return {"error": str(e)}
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
    
    def __del__(self):
        """Destructor to ensure connection is closed"""
        self.close_connection()
