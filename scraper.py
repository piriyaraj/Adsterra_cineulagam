#!/usr/bin/env python3
"""
Article scraper for Tamil Cinema News
Handles sitemap parsing and article content extraction
"""

import logging
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional
import time
import random

logger = logging.getLogger(__name__)


class ArticleScraper:
    """Scraper class for fetching and processing articles"""
    
    def __init__(self):
        """Initialize the scraper with headers and session"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
        })
        
    def fetch_articles_from_sitemap(self) -> List[Dict[str, str]]:
        """
        Fetch article URLs from the sitemap
        Returns list of article dictionaries with url and title
        """
        sitemap_url = "https://sitemap.cineulagam.com/articles-0.xml"
        
        try:
            logger.info(f"Fetching sitemap from: {sitemap_url}")
            response = self.session.get(sitemap_url, timeout=30)
            response.raise_for_status()
            
            # Parse XML sitemap
            soup = BeautifulSoup(response.content, 'xml')
            articles = []
            
            # Extract URLs and titles from sitemap
            for url_tag in soup.find_all('url'):
                loc = url_tag.find('loc')
                lastmod = url_tag.find('lastmod')
                
                if loc:
                    article_url = loc.text.strip()
                    # Extract title from URL or use a placeholder
                    title = self._extract_title_from_url(article_url)
                    
                    articles.append({
                        'url': article_url,
                        'title': title,
                        'lastmod': lastmod.text.strip() if lastmod else None
                    })
            
            logger.info(f"Found {len(articles)} articles in sitemap")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching sitemap: {str(e)}")
            return []
    
    def fetch_new_articles_since_last_post(self, last_posted_url: str) -> List[Dict[str, str]]:
        """
        Fetch only new articles since the last posted article
        Returns list of new article dictionaries with url and title
        """
        try:
            # Get all articles from sitemap
            all_articles = self.fetch_articles_from_sitemap()
            
            if not all_articles:
                logger.warning("No articles found in sitemap")
                return []
            
            # Find the index of the last posted article
            last_posted_index = -1
            for i, article in enumerate(all_articles):
                if article['url'] == last_posted_url:
                    last_posted_index = i
                    break
            
            if last_posted_index == -1:
                # Last posted article not found in sitemap, return all articles
                logger.warning(f"Last posted article not found in sitemap: {last_posted_url}")
                logger.info("Processing all articles from sitemap")
                return all_articles
            
            # Return only articles after the last posted one
            new_articles = all_articles[:last_posted_index]  # Articles before the last posted one
            logger.info(f"Found {len(new_articles)} new articles since last post")
            return new_articles
            
        except Exception as e:
            logger.error(f"Error fetching new articles: {str(e)}")
            return []
    
    def scrape_article(self, url: str) -> Optional[Dict[str, str]]:
        """
        Scrape individual article content
        Returns article details including title, content, and image
        """
        try:
            logger.info(f"Scraping article: {url}")
            
            # Add random delay to avoid being blocked
            time.sleep(random.uniform(1, 3))
            
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = self._extract_title(soup)
            if not title:
                logger.warning(f"Could not extract title from: {url}")
                return None

            # Extract content
            content = self._extract_content(soup)
            if not content:
                logger.warning(f"Could not extract content from: {url}")
                return None
            
            # Extract images
            image_urls = self._extract_images(soup, url)
            
            # Extract tags
            tags = self._extract_tags(soup)
            
            # Extract slug from URL
            slug = self._extract_slug_from_url(url)
            
            # Summarize/rewrite content to avoid copyright issues
            summarized_content = self._summarize_content(content)
            
            html_content = self.make_html_content(title, content, image_urls, url, tags)
            return {
                'url': url,
                'title': title,
                'content': summarized_content,
                'original_content': content,
                'image_urls': image_urls,
                'image_url': image_urls[0] if image_urls else None,  # Keep backward compatibility
                'tags': tags,
                'slug': slug,
                'html_content': html_content
            }
            
        except Exception as e:
            logger.error(f"Error scraping article {url}: {str(e)}")
            return None
    
    def _extract_title_from_url(self, url: str) -> str:
        """Extract a basic title from URL"""
        # Remove domain and clean up URL to create a basic title
        parsed = urlparse(url)
        path = parsed.path.strip('/')
        title = path.replace('-', ' ').replace('/', ' ').title()
        return title[:100]  # Limit length
    
    def _extract_slug_from_url(self, url: str) -> str:
        """Extract slug from Cineulagam URL"""
        try:
            parsed = urlparse(url)
            path = parsed.path.strip('/')
            
            # Remove 'article/' prefix if present
            if path.startswith('article/'):
                path = path[8:]  # Remove 'article/'
            
            # Remove the numeric ID at the end (last part after last dash)
            parts = path.split('-')
            if parts and parts[-1].isdigit():
                # Remove the last part if it's numeric
                parts = parts[:-1]
            
            # Join back with dashes to create slug
            slug = '-'.join(parts)
            return slug
        except Exception as e:
            logger.warning(f"Could not extract slug from URL {url}: {str(e)}")
            return ""
    
    def _extract_title(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article title from HTML"""
        # Try multiple selectors for title
        title_selectors = [
            'h1.entry-title',
            'h1.post-title',
            'h1.article-title',
            'h1',
            '.entry-title',
            '.post-title',
            '.article-title',
            'title'
        ]
        
        for selector in title_selectors:
            title_elem = soup.select_one(selector)
            if title_elem and title_elem.get_text().strip():
                return title_elem.get_text().strip()
        
        return None
    
    def _extract_content(self, soup: BeautifulSoup) -> Optional[str]:
        """Extract article content from HTML"""
        # Try multiple selectors for content
        content_selectors = [
            '.ds-content',
            '.entry-content',
            '.post-content',
            '.article-content',
            '.content',
            'article',
            '.post-body',
            '.entry-body'
        ]
        
        for selector in content_selectors:
            content_elem = soup.select_one(selector)
            if content_elem:
                # Remove script and style elements
                for script in content_elem(["script", "style"]):
                    script.decompose()
                
                # Remove promotional content with class "article-promo"
                for promo in content_elem.find_all(class_="article-promo"):
                    promo.decompose()
                
                # Extract content while preserving iframe elements as HTML
                content = self._extract_content_with_iframes(content_elem)
                if content and len(content) > 100:  # Ensure substantial content
                    return content
        
        return None
    
    def _extract_content_with_iframes(self, content_elem) -> str:
        """
        Extract content while preserving iframe elements as HTML
        and converting other elements to text
        """
        content_parts = []
        
        for element in content_elem.find_all():
            print(element.name)
            if element.name == 'blockquote':
                print("iframe found................")
                # Preserve iframe as HTML
                iframe_html = str(element)
                content_parts.append(iframe_html)
            elif element.name in ['p', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                # For text elements, get the text content
                text_content = element.get_text(strip=True)
                if text_content:
                    content_parts.append(text_content)
            elif element.name == 'br':
                # Preserve line breaks
                content_parts.append('\n')
        
        # Join all parts with newlines
        return '\n'.join(content_parts)
    
    def _extract_images(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract all images from article, prioritizing .img-fluid in .ds-content"""
        images = []
        
        def normalize_url(img_src: str) -> str:
            """Convert relative URLs to absolute"""
            if img_src.startswith('//'):
                return 'https:' + img_src
            elif img_src.startswith('/'):
                return urljoin(base_url, img_src)
            elif not img_src.startswith('http'):
                return urljoin(base_url, img_src)
            return img_src
        
        # 1. Try to find all images with class "img-fluid" within ".ds-content"
        ds_content = soup.select_one('.ds-content')
        if ds_content:
            # Find all img-fluid images in ds-content
            img_elems = ds_content.find_all('img', class_='img-fluid')
            for img_elem in img_elems:
                if img_elem.get('src'):
                    img_src = normalize_url(img_elem.get('src'))
                    if img_src not in images:  # Avoid duplicates
                        images.append(img_src)
            
            # If no img-fluid found, try any <img> in ds-content
            if not images:
                img_elems = ds_content.find_all('img')
                for img_elem in img_elems:
                    if img_elem.get('src'):
                        img_src = normalize_url(img_elem.get('src'))
                        if img_src not in images:  # Avoid duplicates
                            images.append(img_src)

        # 2. If no images found in ds-content, try to find any image with class "img-fluid" in the whole document
        if not images:
            img_elems = soup.find_all('img', class_='img-fluid')
            for img_elem in img_elems:
                if img_elem.get('src'):
                    img_src = normalize_url(img_elem.get('src'))
                    if img_src not in images:  # Avoid duplicates
                        images.append(img_src)
    
        return images
    
    def _extract_tags(self, soup: BeautifulSoup) -> List[str]:
        """Extract tags from article HTML"""
        tags = []
        
        # First, try the specific ds-topics structure for this website
        ds_topics = soup.select_one('.ds-topics')
        if ds_topics:
            tag_links = ds_topics.find_all('a')
            for link in tag_links:
                tag_text = link.get_text().strip()
                if tag_text and len(tag_text) > 1:
                    # Clean up the tag text
                    tag_text = re.sub(r'[^\w\s\-]', '', tag_text).strip()
                    if tag_text and tag_text not in tags:
                        tags.append(tag_text)
            
            if tags:
                logger.info(f"Found {len(tags)} tags from .ds-topics: {tags}")
                return tags[:10]  # Return early if we found tags from ds-topics
        
        # Common tag selectors for different website structures
        tag_selectors = [
            '.tags a',           # Common pattern: <div class="tags"><a>tag1</a><a>tag2</a></div>
            '.tag a',            # Alternative: <div class="tag"><a>tag1</a><a>tag2</a></div>
            '.post-tags a',      # WordPress style: <div class="post-tags"><a>tag1</a></div>
            '.entry-tags a',     # Another common pattern
            '.article-tags a',   # Article-specific tags
            '.meta-tags a',      # Meta tags section
            '.tag-list a',       # Tag list pattern
            'a[rel="tag"]',      # WordPress rel="tag" pattern
            '.keywords a',       # Keywords section
            '.categories a',     # Categories that might be used as tags
            '.post-categories a', # Post categories
            '.entry-categories a', # Entry categories
            'meta[name="keywords"]', # Meta keywords tag
            'meta[property="article:tag"]', # Open Graph article tags
            'meta[name="news_keywords"]', # News keywords
        ]
        
        # Try each selector
        for selector in tag_selectors:
            if selector.startswith('meta'):
                # Handle meta tags differently
                meta_elem = soup.select_one(selector)
                if meta_elem and meta_elem.get('content'):
                    content = meta_elem.get('content')
                    # Split by common separators
                    meta_tags = re.split(r'[,;|]', content)
                    for tag in meta_tags:
                        tag = tag.strip()
                        if tag and len(tag) > 1 and tag not in tags:
                            tags.append(tag)
            else:
                # Handle regular tag elements
                tag_elements = soup.select(selector)
                for elem in tag_elements:
                    tag_text = elem.get_text().strip()
                    if tag_text and len(tag_text) > 1 and tag_text not in tags:
                        # Clean up tag text
                        tag_text = re.sub(r'[^\w\s\-]', '', tag_text)  # Remove special chars except word chars, spaces, hyphens
                        tag_text = tag_text.strip()
                        if tag_text:
                            tags.append(tag_text)
        
        # Additional fallback: look for any element with "tag" in class name
        if not tags:
            tag_elements = soup.find_all(['a', 'span', 'div'], class_=re.compile(r'tag', re.I))
            for elem in tag_elements:
                tag_text = elem.get_text().strip()
                if tag_text and len(tag_text) > 1 and tag_text not in tags:
                    tag_text = re.sub(r'[^\w\s\-]', '', tag_text)
                    tag_text = tag_text.strip()
                    if tag_text:
                        tags.append(tag_text)
        
        # Limit number of tags and clean them up
        tags = tags[:10]  # Limit to 10 tags max
        
        # Clean up tags - remove very short ones and duplicates
        cleaned_tags = []
        for tag in tags:
            if len(tag) >= 2 and tag.lower() not in [t.lower() for t in cleaned_tags]:
                cleaned_tags.append(tag)
        
        logger.info(f"Extracted {len(cleaned_tags)} tags: {cleaned_tags}")
        return cleaned_tags
    
    def _generate_tags_html(self, tags: list) -> str:
        """Generate HTML for tags display"""
        if not tags:
            return ''
        
        tag_spans = []
        for tag in tags:
            tag_spans.append(f'<span class="tag">{tag}</span>')
        
        return f'''<div class="article-tags">
            <h3>Tags:</h3>
            <div class="tag-list">{" ".join(tag_spans)}</div>
        </div>'''
    
    def make_html_content(self, title: str, content: str, image_urls: list, url: str = "", tags: list = None) -> str:
        """Make attractive, SEO-optimized HTML content for the article"""
        
        # Extract meta description from content (first 160 characters)
        meta_description = content[:160].replace('\n', ' ').strip()
        if len(content) > 160:
            meta_description += "..."
        
        # Prepare tags for meta keywords
        if tags is None:
            tags = []
        tags_str = ', '.join(tags) if tags else 'Tamil cinema, movie news, entertainment'
        
        # Create unique article ID from URL
        article_id = url.split('/')[-1] if url else "article"
        
        # Process content into paragraphs
        paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
        
        # Create image gallery HTML
        image_gallery = ""
        if image_urls:
            image_gallery = '<div class="image-gallery">'
            for i, img_url in enumerate(image_urls):
                image_gallery += f'''
                <div class="gallery-item">
                    <img src="{img_url}" alt="{title} - Image {i+1}" loading="lazy" class="gallery-image">
                </div>'''
            image_gallery += '</div>'
        
        # Create structured content with images interspersed
        structured_content = ""
        for i, paragraph in enumerate(paragraphs):
            structured_content += f'<p class="content-paragraph">{paragraph}</p>'
            
            # Insert images between paragraphs for better visual flow
            if image_urls and i < len(image_urls) and i % 2 == 1:  # Insert every other paragraph
                img_index = min(i // 2, len(image_urls) - 1)
                structured_content += f'''
                <div class="inline-image-container">
                    <img src="{image_urls[img_index]}" alt="{title} - Related Image" loading="lazy" class="inline-image">
                </div>'''
        
        html_content = f'''<style>
                    * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }}
                    
                    body {{
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                    }}
                    
                    .article-container {{
                        max-width: 1200px;
                        margin: 0 auto;
                        background: white;
                        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                        border-radius: 15px;
                        overflow: hidden;
                        margin-top: 20px;
                        margin-bottom: 20px;
                    }}
                    
                    .article-header {{
                        background: linear-gradient(135deg, #ff6b6b, #ee5a24);
                        color: white;
                        padding: 40px 30px;
                        text-align: center;
                        position: relative;
                        overflow: hidden;
                    }}
                    
                    .article-header::before {{
                        content: '';
                        position: absolute;
                        top: -50%;
                        left: -50%;
                        width: 200%;
                        height: 200%;
                        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
                        animation: float 6s ease-in-out infinite;
                    }}
                    
                    @keyframes float {{
                        0%, 100% {{ transform: translateY(0px) rotate(0deg); }}
                        50% {{ transform: translateY(-20px) rotate(180deg); }}
                    }}
                    
                    .article-title {{
                        font-size: 2.5rem;
                        font-weight: 700;
                        margin-bottom: 15px;
                        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                        position: relative;
                        z-index: 1;
                    }}
                    
                    .article-meta {{
                        font-size: 1rem;
                        opacity: 0.9;
                        position: relative;
                        z-index: 1;
                    }}
                    
                    .article-content {{
                        padding: 40px 30px;
                    }}
                    
                    .image-gallery {{
                        display: grid;
                        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                        gap: 20px;
                        margin: 30px 0;
                        padding: 20px;
                        background: #f8f9fa;
                        border-radius: 10px;
                    }}
                    
                    .gallery-item {{
                        position: relative;
                        overflow: hidden;
                        border-radius: 10px;
                        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                        transition: transform 0.3s ease;
                    }}
                    
                    .gallery-item:hover {{
                        transform: translateY(-5px);
                    }}
                    
                    .gallery-image {{
                        width: 100%;
                        height: 250px;
                        object-fit: cover;
                        transition: transform 0.3s ease;
                    }}
                    
                    .gallery-item:hover .gallery-image {{
                        transform: scale(1.05);
                    }}
                    
                    .inline-image-container {{
                        text-align: center;
                        margin: 30px 0;
                        padding: 20px;
                        background: #f8f9fa;
                        border-radius: 10px;
                    }}
                    
                    .inline-image {{
                        max-width: 100%;
                        height: auto;
                        border-radius: 10px;
                        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                    }}
                    
                    .content-paragraph {{
                        font-size: 1.1rem;
                        margin-bottom: 20px;
                        text-align: justify;
                        color: #444;
                    }}
                    
                    .content-paragraph:first-of-type {{
                        font-size: 1.2rem;
                        font-weight: 500;
                        color: #2c3e50;
                    }}
                    
                    .article-tags {{
                        margin-top: 30px;
                        padding: 20px;
                        background: #f8f9fa;
                        border-radius: 10px;
                        border-left: 4px solid #3498db;
                    }}
                    
                    .article-tags h3 {{
                        margin-bottom: 15px;
                        color: #2c3e50;
                        font-size: 1.1rem;
                    }}
                    
                    .tag-list {{
                        display: flex;
                        flex-wrap: wrap;
                        gap: 8px;
                    }}
                    
                    .tag {{
                        display: inline-block;
                        padding: 6px 12px;
                        background: #3498db;
                        color: white;
                        border-radius: 20px;
                        font-size: 0.9rem;
                        font-weight: 500;
                        text-decoration: none;
                        transition: background 0.3s ease;
                    }}
                    
                    .tag:hover {{
                        background: #2980b9;
                    }}
                    
                    .article-footer {{
                        background: #2c3e50;
                        color: white;
                        padding: 30px;
                        text-align: center;
                    }}
                    
                    .source-link {{
                        color: #3498db;
                        text-decoration: none;
                        font-weight: 500;
                        transition: color 0.3s ease;
                    }}
                    
                    .source-link:hover {{
                        color: #2980b9;
                    }}
                    
                    .social-share {{
                        margin-top: 20px;
                    }}
                    
                    .share-button {{
                        display: inline-block;
                        padding: 10px 20px;
                        margin: 5px;
                        background: #3498db;
                        color: white;
                        text-decoration: none;
                        border-radius: 25px;
                        transition: background 0.3s ease;
                    }}
                    
                    .share-button:hover {{
                        background: #2980b9;
                    }}
                    
                    @media (max-width: 768px) {{
                        .article-title {{
                            font-size: 2rem;
                        }}
                        
                        .article-content {{
                            padding: 20px 15px;
                        }}
                        
                        .image-gallery {{
                            grid-template-columns: 1fr;
                            padding: 15px;
                        }}
                    }}
                </style>
                <body>
                    <div class="article-container">
                        <main class="article-content">
                            {image_gallery}
                            
                            <div class="article-text">
                                {structured_content}
                            </div>
                            
                            {self._generate_tags_html(tags)}
                        </main>
                    </div>
                </body>'''
        
        return html_content
            
    def _summarize_content(self, content: str) -> str:
        """
        Summarize and rewrite content to avoid copyright issues
        This is a basic implementation - you might want to use AI services for better summarization
        """
        # Basic summarization - take first few sentences and clean up
        sentences = content.split('.')
        
        # Take first 3-5 sentences that are substantial
        summary_sentences = []
        for sentence in sentences[:10]:  # Check first 10 sentences
            sentence = sentence.strip()
            if len(sentence) > 20:  # Only substantial sentences
                summary_sentences.append(sentence)
                if len(summary_sentences) >= 3:
                    break
        
        if summary_sentences:
            summary = '. '.join(summary_sentences) + '.'
            
            # Add a disclaimer
            summary += "\n\n[This is a summarized version of the original article. Read the full article for complete details.]"
            
            return summary
        
        # Fallback: return truncated content
        return content[:500] + "..." if len(content) > 500 else content

if __name__ == "__main__":
    scraper = ArticleScraper()
    articles = scraper.fetch_articles_from_sitemap()
    if articles:
        url = articles[0]['url']
        url = "https://cineulagam.com/article/pradeep-gift-to-his-helper-video-goes-viral-1760618319"
        article = scraper.scrape_article(url)
        html_content = scraper.make_html_content(
            article['title'], 
            article['original_content'], 
            article['image_urls'], 
            article['url'],
            article.get('tags', [])
        )
        # print(html_content)
        with open('article.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Article saved with {len(article.get('image_urls', []))} images")
