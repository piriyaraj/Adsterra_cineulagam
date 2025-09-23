
#!/usr/bin/env python3
"""
Blogger API integration for publishing articles
Handles authentication and post publishing to Google Blogger
"""

import logging
import os
from typing import Optional, Dict
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle
import base64
from datetime import datetime

logger = logging.getLogger(__name__)

# Blogger API scopes
SCOPES = ['https://www.googleapis.com/auth/blogger']


class BloggerPublisher:
    """Handles Blogger API operations for publishing articles"""
    
    def __init__(self):
        """Initialize Blogger API client"""
        self.service = None
        self.blog_id = os.getenv('BLOGGER_BLOG_ID',"6380171182056049355")
        self.credentials_file = os.getenv('BLOGGER_CREDENTIALS_FILE', 'credentials.json')
        self.token_file = os.getenv('BLOGGER_TOKEN_FILE', 'token.pickle')
        
        if not self.blog_id:
            logger.error("BLOGGER_BLOG_ID not found in environment variables")
            return
            
        self._authenticate()
    
    def _authenticate(self):
        """Authenticate with Google Blogger API"""
        try:
            creds = None
            
            # Load existing token
            if os.path.exists(self.token_file):
                with open(self.token_file, 'rb') as token:
                    creds = pickle.load(token)
            
            # If no valid credentials, get new ones
            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(Request())
                else:
                    if not os.path.exists(self.credentials_file):
                        logger.error(f"Credentials file not found: {self.credentials_file}")
                        logger.error("Please follow these steps to set up Blogger API credentials:")
                        logger.error("1. Go to Google Cloud Console (https://console.cloud.google.com/)")
                        logger.error("2. Create a new project or select existing one")
                        logger.error("3. Enable Blogger API v3")
                        logger.error("4. Go to Credentials > Create Credentials > OAuth 2.0 Client IDs")
                        logger.error("5. Choose 'Desktop application' as application type")
                        logger.error("6. Download the JSON file and save as 'credentials.json'")
                        return
                    
                    try:
                        flow = InstalledAppFlow.from_client_secrets_file(
                            self.credentials_file, SCOPES)
                        creds = flow.run_local_server(port=0)
                    except Exception as flow_error:
                        logger.error(f"OAuth flow failed: {str(flow_error)}")
                        logger.error("Make sure your credentials.json is for a 'Desktop application' type")
                        logger.error("Check that the file contains 'installed' in the JSON structure")
                        return
                
                # Save credentials for next run
                with open(self.token_file, 'wb') as token:
                    pickle.dump(creds, token)
            
            # Build the service
            self.service = build('blogger', 'v3', credentials=creds)
            logger.info("Successfully authenticated with Blogger API")
            
        except Exception as e:
            logger.error(f"Authentication failed: {str(e)}")
            logger.error("Please check your credentials.json file format")
            self.service = None
    
    def publish_post(self, article: Dict[str, str]) -> Optional[Dict[str, str]]:
        """
        Publish an article to Blogger
        Returns post details including URL and ID
        """
        if not self.service:
            logger.error("Blogger service not initialized")
            return None
        
        try:
            # Prepare post content
            title = article['title']
            content = article['html_content']
            image_url = article.get('image_url')
            tags = article.get('tags', [])
            slug = article.get('slug', '')
            
            # Create HTML content
            html_content = self._create_html_content(content, image_url)
            
            # Prepare labels (tags) for Blogger
            labels = []
            
            # Add fetched tags to labels
            if tags:
                # Clean and add fetched tags
                for tag in tags:
                    if tag and len(tag.strip()) > 0:
                        clean_tag = tag.strip()
                        if clean_tag not in labels:  # Avoid duplicates
                            labels.append(clean_tag)
            
            # Limit to 20 labels max (Blogger limit)
            labels = labels[:20]
            
            # Prepare post body
            post_body = {
                'title': title,
                'content': html_content,
                'labels': labels,
                'status': 'LIVE'  # Publish immediately
            }
            
            # Add custom URL slug if available
            if slug:
                post_body['url'] = slug
                logger.info(f"Using custom slug for Blogger post: {slug}")
            
            # Publish the post
            logger.info(f"Publishing post: {title}")
            logger.info(f"Using labels: {labels}")
            request = self.service.posts().insert(
                blogId=self.blog_id,
                body=post_body
            )
            
            post = request.execute()
            
            # Extract post details
            post_url = post.get('url')
            post_id = post.get('id')
            
            logger.info(f"Successfully published post: {post_url}")
            
            return {
                'id': post_id,
                'url': post_url,
                'title': title,
                'published': post.get('published')
            }
            
        except Exception as e:
            logger.error(f"Failed to publish post: {str(e)}")
            return None
    
    def _create_html_content(self, content: str, image_url: Optional[str] = None) -> str:
        """Create HTML content for the blog post"""
        html_parts = []
        
        # Add image if available
        if image_url:
            html_parts.append(f'<img src="{image_url}" alt="Featured Image" style="max-width: 100%; height: auto; margin-bottom: 20px;">')
        
        # Add content
        # Convert line breaks to HTML paragraphs
        paragraphs = content.split('\n\n')
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph:
                # Convert single line breaks to <br>
                paragraph = paragraph.replace('\n', '<br>')
                html_parts.append(f'<p>{paragraph}</p>')
        
        # Add source attribution
        html_parts.append('<hr>')
        html_parts.append('<p><em>Source: Entertainment News</em></p>')
        
        return '\n'.join(html_parts)
    
    def get_blog_info(self) -> Optional[Dict]:
        """Get blog information"""
        if not self.service:
            return None
        
        try:
            blog = self.service.blogs().get(blogId=self.blog_id).execute()
            return {
                'name': blog.get('name'),
                'url': blog.get('url'),
                'description': blog.get('description')
            }
        except Exception as e:
            logger.error(f"Failed to get blog info: {str(e)}")
            return None
    
    def list_posts(self, max_results: int = 10) -> list:
        """List recent posts from the blog"""
        if not self.service:
            return []
        
        try:
            request = self.service.posts().list(
                blogId=self.blog_id,
                maxResults=max_results,
                status='LIVE'
            )
            posts = request.execute()
            return posts.get('items', [])
        except Exception as e:
            logger.error(f"Failed to list posts: {str(e)}")
            return []
