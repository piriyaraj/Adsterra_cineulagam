#!/usr/bin/env python3
"""
Telegram Bot integration for posting articles
Handles posting to Telegram channel with proper formatting
"""

import logging
import os
import requests
from typing import Optional
from urllib.parse import quote

logger = logging.getLogger(__name__)


class TelegramBot:
    """Handles Telegram Bot API operations for posting articles"""
    
    def __init__(self):
        """Initialize Telegram Bot with token and channel ID"""
        self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN','8204617778:AAE3oY_BvngFe2Ywfa-qz6f78_JPW6HrrM4')
        self.channel_id = os.getenv('TELEGRAM_CHANNEL_ID','@kollywoodmirrors')
        
        if not self.bot_token or self.bot_token.strip() == "":
            logger.warning("TELEGRAM_BOT_TOKEN not configured - Telegram posting will be disabled")
            self.bot_token = None
            return
        
        if not self.channel_id or self.channel_id.strip() == "":
            logger.warning("TELEGRAM_CHANNEL_ID not configured - Telegram posting will be disabled")
            self.channel_id = None
            return
        
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        # Test bot connection
        self._test_connection()
    
    def _test_connection(self):
        """Test bot connection and get bot info"""
        try:
            response = requests.get(f"{self.base_url}/getMe", timeout=10)
            response.raise_for_status()
            
            bot_info = response.json()
            if bot_info.get('ok'):
                logger.info(f"Telegram bot connected: @{bot_info['result']['username']}")
            else:
                logger.error("Failed to connect to Telegram bot")
                
        except Exception as e:
            logger.error(f"Telegram bot connection test failed: {str(e)}")
    
    def post_article(self, title: str, content: str, blogger_url: str, image_url: Optional[str] = None) -> bool:
        """
        Post an article to Telegram channel
        Returns True if successful, False otherwise
        """
        if not self.bot_token or not self.channel_id:
            logger.info("Telegram not configured - skipping Telegram posting")
            return True  # Return True so the pipeline continues
        
        try:
            # Format the message
            message = self._format_message(title, "", blogger_url)
            
            # If image is available, send photo with caption
            if image_url:
                return self._send_photo_with_caption(image_url, message, blogger_url)
            else:
                return self._send_text_message(message, blogger_url)
                
        except Exception as e:
            logger.error(f"Failed to post to Telegram: {str(e)}")
            return False
    
    def _format_message(self, title: str, content: str, blogger_url: str) -> str:
        """Format the message for Telegram posting"""
        # Create a short snippet from content (first 200 characters)
        snippet = content[:200].strip()
        if len(content) > 200:
            snippet += "..."
        
        # Clean up snippet - remove HTML tags and extra whitespace
        import re
        snippet = re.sub(r'<[^>]+>', '', snippet)  # Remove HTML tags
        snippet = re.sub(r'\s+', ' ', snippet)  # Normalize whitespace
        snippet = snippet.strip()
        
        # Format message
        message = f"📰 *{title}*\n\n"
        message += f"{snippet}"
        
        return message
    
    def _send_photo_with_caption(self, image_url: str, caption: str, blogger_url: str = None) -> bool:
        """Send photo with caption to Telegram channel"""
        try:
            url = f"{self.base_url}/sendPhoto"
            
            data = {
                'chat_id': self.channel_id,
                'photo': image_url,
                'caption': caption,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': False
            }
            
            # Add inline keyboard with "Read more" button if URL is provided
            if blogger_url:
                reply_markup = {
                    'inline_keyboard': [[
                        {
                            'text': '📖 Read More',
                            'url': blogger_url
                        }
                    ]]
                }
                data['reply_markup'] = str(reply_markup).replace("'", '"')
            
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                logger.info("Successfully posted photo with caption to Telegram")
                return True
            else:
                logger.error(f"Telegram API error: {result.get('description', 'Unknown error')}")
                return False
                
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error sending photo to Telegram: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    logger.error(f"Telegram API error details: {error_data}")
                except:
                    logger.error(f"Response content: {e.response.text}")
            # Fallback to text message
            return self._send_text_message(caption, blogger_url)
        except Exception as e:
            logger.error(f"Failed to send photo to Telegram: {str(e)}")
            # Fallback to text message
            return self._send_text_message(caption, blogger_url)
    
    def _send_text_message(self, message: str, blogger_url: str = None) -> bool:
        """Send text message to Telegram channel"""
        try:
            url = f"{self.base_url}/sendMessage"
            
            data = {
                'chat_id': self.channel_id,
                'text': message,
                'parse_mode': 'Markdown',
                'disable_web_page_preview': False
            }
            
            # Add inline keyboard with "Read more" button if URL is provided
            if blogger_url:
                reply_markup = {
                    'inline_keyboard': [[
                        {
                            'text': '📖 Read More',
                            'url': blogger_url
                        }
                    ]]
                }
                data['reply_markup'] = str(reply_markup).replace("'", '"')
            
            response = requests.post(url, data=data, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                logger.info("Successfully posted text message to Telegram")
                return True
            else:
                logger.error(f"Telegram API error: {result.get('description', 'Unknown error')}")
                return False
                
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error sending message to Telegram: {e}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    logger.error(f"Telegram API error details: {error_data}")
                except:
                    logger.error(f"Response content: {e.response.text}")
            return False
        except Exception as e:
            logger.error(f"Failed to send message to Telegram: {str(e)}")
            return False
    
    def send_test_message(self) -> bool:
        """Send a test message to verify bot setup"""
        test_message = "🤖 *Test Message*\n\nThis is a test message from the Tamil Cinema News Publisher bot."
        
        try:
            return self._send_text_message(test_message)
        except Exception as e:
            logger.error(f"Failed to send test message: {str(e)}")
            return False
    
    def get_channel_info(self) -> Optional[dict]:
        """Get information about the channel"""
        try:
            url = f"{self.base_url}/getChat"
            data = {'chat_id': self.channel_id}
            
            response = requests.post(url, data=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            if result.get('ok'):
                return result.get('result')
            else:
                logger.error(f"Failed to get channel info: {result.get('description', 'Unknown error')}")
                return None
                
        except Exception as e:
            logger.error(f"Failed to get channel info: {str(e)}")
            return None


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    print("Starting Telegram bot test...")
    bot = TelegramBot()
    
    if bot.bot_token and bot.channel_id:
        print(f"Bot token: {bot.bot_token[:10]}...")
        print(f"Channel ID: {bot.channel_id}")
        print("Sending test message...")
        result = bot.send_test_message()
        if result:
            print("✅ Test message sent successfully!")
        else:
            print("❌ Failed to send test message")
    else:
        print("❌ Bot not properly configured")