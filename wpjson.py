#!/usr/bin/env python3
"""
Wpjson - WordPress JSON API CLI Tool
Fetch posts, categories, and media from WordPress REST API
"""

import argparse
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from urllib.parse import urlparse, unquote

import requests


class Wpjson:
    def __init__(self, config=None):
        """
        Initialize Wpjson with configuration
        
        Args:
            config (dict): Configuration dictionary with keys:
                - targetUrl (str): WordPress API endpoint URL (required)
                - downloadImage (bool): Download featured media and content images
                - myWebsiteLink (str): Replace links in content with your website
                - dirOutputName (str): Output directory name (default: "output")
                - saveFileJson (bool): Save results to JSON files (default: True)
        """
        if config is None:
            config = {}
        
        self.target_url = ""
        self.download_image = False
        self.my_website_link = ""
        self.save_file_json = True
        self.dir_output_name = "output"
        self.result = []
        
        self._set_config(config)
    
    def _set_config(self, config):
        """Set configuration values"""
        target_url = config.get("targetUrl", "").rstrip("/") + "/" if config.get("targetUrl") else ""
        
        if not target_url:
            print("Error: targetUrl Config is Required!", file=sys.stderr)
            sys.exit(1)
        
        self.target_url = target_url
        self.download_image = config.get("downloadImage", self.download_image)
        self.my_website_link = config.get("myWebsiteLink", self.my_website_link)
        self.dir_output_name = config.get("dirOutputName", self.dir_output_name)
        self.save_file_json = config.get("saveFileJson", self.save_file_json)
        
        self._ensure_dirs()
        return self
    
    def _ensure_dirs(self):
        """Create necessary output directories"""
        base_path = Path.cwd() / self.dir_output_name
        base_path.mkdir(parents=True, exist_ok=True)
        (base_path / "images").mkdir(parents=True, exist_ok=True)
        (base_path / "posts").mkdir(parents=True, exist_ok=True)
    
    def set_save_file_json(self, boolean):
        """Toggle save file JSON option"""
        self.save_file_json = boolean
        return self
    
    def _get_request(self, url):
        """Make HTTP GET request and return JSON response"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=30,
                allow_redirects=True,
                verify=True
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request error: {e}", file=sys.stderr)
            return []
        except json.JSONDecodeError:
            return []
    
    def _to_json(self, data):
        """Output JSON response to stdout"""
        print(json.dumps(data, indent=2, ensure_ascii=False))
    
    def _seofy(self, s_string="", strip=""):
        """Create SEO-friendly slug"""
        if strip == "":
            s_string = re.sub(r'[^\w\s-]+', '-', s_string, flags=re.UNICODE)
            s_string = s_string.strip("-")
        else:
            s_string = re.sub(r'[^\w\s-]+', '_', s_string, flags=re.UNICODE)
            s_string = s_string.strip("_")
        
        # Transliterate unicode to ascii
        s_string = unicodedata.normalize('NFKD', s_string).encode('ascii', 'ignore').decode('ascii')
        s_string = s_string.lower()
        s_string = re.sub(r'[^-a-z0-9_]+', '', s_string)
        return s_string
    
    def _clean_text(self, text="", spc=" "):
        """Clean and sanitize text"""
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'[^\w\s-]+', spc if spc else " ", text, flags=re.UNICODE)
        text = text.strip("-")
        text = text.replace("_", " ")
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('ascii')
        text = text.lower()
        text = re.sub(r'[^-a-z0-9_]+', spc if spc else " ", text)
        return text
    
    def get_all_category(self, page=1, per_page=10):
        """Fetch all categories from WordPress API"""
        url = f"{self.target_url}wp-json/wp/v2/categories?page={page}&per_page={per_page}"
        self.result = self._get_request(url)
        return self
    
    def get_all_post_category(self, ctg_id=1, page=1, per_page=10):
        """Fetch posts by category ID"""
        url = f"{self.target_url}wp-json/wp/v2/posts?categories={ctg_id}&page={page}&per_page={per_page}"
        self.result = self._get_request(url)
        return self
    
    def _download_image(self, content):
        """Download all images from HTML content"""
        save_dir = Path.cwd() / self.dir_output_name / "images"
        pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
        matches = re.findall(pattern, content, re.IGNORECASE)
        
        result = []
        for img_url in matches:
            parsed = urlparse(unquote(img_url))
            file_name = Path(parsed.path).name
            file_name = re.sub(r'[^a-zA-Z0-9._-]', '_', file_name)
            file_path = save_dir / file_name
            
            try:
                img_data = requests.get(img_url, timeout=30).content
                with open(file_path, 'wb') as f:
                    f.write(img_data)
                result.append(img_url)
            except requests.exceptions.RequestException:
                continue
        
        return result
    
    def _get_feature_media(self, media_id):
        """Get featured media URL by ID"""
        url = f"{self.target_url}wp-json/wp/v2/media/{media_id}"
        result = self._get_request(url)
        if result and isinstance(result, dict) and "guid" in result:
            return result["guid"].get("rendered", "")
        return None
    
    def _download_single_image(self, image_url):
        """Download a single image and return filename"""
        save_dir = Path.cwd() / self.dir_output_name / "images"
        
        try:
            parsed = urlparse(unquote(image_url))
            file_name = Path(parsed.path).name
            file_name = re.sub(r'[^a-zA-Z0-9._-]', '_', file_name)
            file_path = save_dir / file_name
            
            img_data = requests.get(image_url, timeout=30).content
            with open(file_path, 'wb') as f:
                f.write(img_data)
            return file_name
        except requests.exceptions.RequestException:
            return None
    
    def build_data_post_category(self, ctg_id, page=1, per_page=10):
        """Build post data for a category with image downloads"""
        datas = self.get_all_post_category(ctg_id, page, per_page).response_object()
        self.result = []
        
        if not datas:
            return self
        
        for r in datas:
            feature_media_filename = "default.png"
            featured_media_id = r.get("featured_media")
            
            if featured_media_id:
                feature_media = self._get_feature_media(featured_media_id)
                if feature_media:
                    downloaded = self._download_single_image(feature_media)
                    if downloaded:
                        feature_media_filename = downloaded
            
            content = r.get("content", {}).get("rendered", "")
            pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
            image_contents = re.findall(pattern, content, re.IGNORECASE)
            
            if self.download_image:
                image_contents = self._download_image(content)
            
            if self.my_website_link:
                content = content.replace(self.target_url, self.my_website_link)
            
            self.result.append({
                "author_id": 1,
                "title": r.get("title", {}).get("rendered", "").strip(),
                "slug": r.get("slug", ""),
                "featured_media": feature_media_filename,
                "summary": r.get("excerpt", {}).get("rendered", ""),
                "content": content,
                "category_id": ctg_id,
                "wp_featured_media_url": feature_media or "",
                "wp_categories": r.get("categories", []),
                "wp_tags": r.get("tags", []),
                "status": "publish",
                "all_image_content": image_contents
            })
        
        if self.result and self.save_file_json:
            output_file = Path.cwd() / self.dir_output_name / "posts" / f"post_ctg_{ctg_id}_page_{page}_limit_{per_page}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.result, f, indent=2, ensure_ascii=False)
        
        return self
    
    def save_post(self, ctg_id, url):
        """Save a single post by URL"""
        data = self._get_request(url)
        
        if not data:
            return self
        
        feature_media_filename = "default.png"
        featured_media_id = data.get("featured_media")
        
        if featured_media_id:
            feature_media = self._get_feature_media(featured_media_id)
            if feature_media:
                downloaded = self._download_single_image(feature_media)
                if downloaded:
                    feature_media_filename = downloaded
        
        content = data.get("content", {}).get("rendered", "")
        pattern = r'<img[^>]+src=["\']([^"\']+)["\']'
        image_contents = re.findall(pattern, content, re.IGNORECASE)
        
        if self.download_image:
            image_contents = self._download_image(content)
        
        if self.my_website_link:
            content = content.replace(self.target_url, self.my_website_link)
        
        self.result = {
            "author_id": 1,
            "title": data.get("title", {}).get("rendered", "").strip(),
            "slug": data.get("slug", ""),
            "featured_media": feature_media_filename,
            "summary": self._clean_text(data.get("excerpt", {}).get("rendered", "")).title(),
            "content": content,
            "category_id": ctg_id,
            "wp_categories": data.get("categories", []),
            "wp_tags": data.get("tags", []),
            "status": "publish",
            "all_image_content": image_contents
        }
        
        if self.result and self.save_file_json:
            slug = data.get("slug", "unknown")
            output_file = Path.cwd() / self.dir_output_name / "posts" / f"{slug}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.result, f, indent=2, ensure_ascii=False)
        
        return self
    
    def response_json(self):
        """Return JSON response to stdout"""
        self._to_json(self.result)
        return self
    
    def response_object(self):
        """Return result as list/dict"""
        return self.result


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(
        description="WordPress JSON API CLI Tool - Fetch posts, categories, and media",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Fetch all categories
  python wpjson.py --target https://example.com --categories

  # Fetch posts from category ID 5
  python wpjson.py --target https://example.com --category-posts 5

  # Fetch a single post by URL
  python wpjson.py --target https://example.com --save-post "https://example.com/wp-json/wp/v2/posts/123" --category-id 5

  # Download images and replace links
  python wpjson.py --target https://example.com --category-posts 5 --download-images --replace-link https://mysite.com
        """
    )
    
    parser.add_argument("--target", "-t", required=True, help="WordPress site URL (e.g., https://example.com)")
    
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument("--categories", "-c", action="store_true", help="Fetch all categories")
    action_group.add_argument("--category-posts", "-p", type=int, metavar="CATEGORY_ID", help="Fetch posts from a specific category ID")
    action_group.add_argument("--save-post", "-s", metavar="POST_URL", help="Save a single post by its WP JSON API URL")
    
    parser.add_argument("--category-id", "-C", type=int, default=1, help="Category ID for --save-post action (default: 1)")
    parser.add_argument("--page", type=int, default=1, help="Page number for pagination (default: 1)")
    parser.add_argument("--per-page", type=int, default=10, help="Items per page (default: 10)")
    parser.add_argument("--download-images", "-d", action="store_true", help="Download featured media and content images")
    parser.add_argument("--replace-link", "-r", metavar="URL", help="Replace target URL links in content with this URL")
    parser.add_argument("--output-dir", "-o", default="output", help="Output directory name (default: output)")
    parser.add_argument("--no-save", action="store_true", help="Don't save results to JSON files (output to stdout only)")
    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress progress output")
    
    args = parser.parse_args()
    
    config = {
        "targetUrl": args.target,
        "downloadImage": args.download_images,
        "myWebsiteLink": args.replace_link or "",
        "dirOutputName": args.output_dir,
        "saveFileJson": not args.no_save
    }
    
    wp = Wpjson(config)
    
    try:
        if args.categories:
            if not args.quiet:
                print(f"Fetching categories (page {args.page}, per_page {args.per_page})...", file=sys.stderr)
            wp.get_all_category(args.page, args.per_page)
        
        elif args.category_posts:
            if not args.quiet:
                print(f"Fetching posts for category {args.category_posts}...", file=sys.stderr)
            wp.build_data_post_category(args.category_posts, args.page, args.per_page)
        
        elif args.save_post:
            if not args.quiet:
                print(f"Saving post from URL: {args.save_post}", file=sys.stderr)
            wp.save_post(args.category_id, args.save_post)
        
        wp.response_json()
        
    except KeyboardInterrupt:
        print("\nOperation cancelled by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
