#!/usr/bin/env python3
"""
Sidechat Posts Scraper
Fetches posts from Sidechat API and saves them as JSON files with rate limiting.
"""

import os
import json
import time
import requests
import urllib3
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

class SidechatScraper:
    def __init__(self):
        self.base_url = "https://api.sidechat.lol/v1/posts"
        self.auth_token = os.getenv("SIDECHAT_AUTH_TOKEN")
        self.group_id = os.getenv("SIDECHAT_GROUP_ID")
        self.output_dir = Path(os.getenv("OUTPUT_DIR", "data"))
        self.post_type = os.getenv("POST_TYPE", "hot")
        self.initial_cursor = os.getenv("INITIAL_CURSOR")
        self.save_json = os.getenv("SAVE_JSON", "true").lower() == "true"
        self.save_cleaned = os.getenv("SAVE_CLEANED", "true").lower() == "true"
        self.request_interval = int(os.getenv("REQUEST_INTERVAL", "1000"))

        if not self.auth_token:
            raise ValueError("SIDECHAT_AUTH_TOKEN environment variable is required")
        if not self.group_id:
            raise ValueError("SIDECHAT_GROUP_ID environment variable is required")

        self.headers = {
            "accept": "*/*",
            "authorization": f"bearer {self.auth_token}",
            "app-version": "5.5.19",
            "user-agent": "sidechat/5.5.19 (com.flowerave.sidechat; build:3; iOS 17.4.0) Alamofire/5.9.1",
            "accept-language": "en-US;q=1.0",
            "accept-encoding": "br;q=1.0, gzip;q=0.9, deflate;q=0.8"
        }

        if self.save_cleaned:
            self.text_file = self.output_dir / "sidechat_posts.txt"
        self.setup_output_directory()

    def setup_output_directory(self):
        """Create output directory structure."""
        self.output_dir.mkdir(exist_ok=True)
        # Initialize empty text file if saving cleaned format
        if self.save_cleaned:
            self.text_file.write_text("", encoding='utf-8')
        print(f"Output directory: {self.output_dir.absolute()}")

    def iso_to_epoch(self, iso_timestamp):
        """Convert ISO timestamp to Unix epoch."""
        dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
        return int(dt.timestamp())

    def make_request(self, cursor: Optional[str] = None) -> Dict[str, Any]:
        """Make a request to the Sidechat API with rate limiting."""
        params = {
            "group_id": self.group_id,
            "type": self.post_type
        }

        if cursor:
            params["cursor"] = cursor


        try:
            response = requests.get(self.base_url, headers=self.headers, params=params, verify=False)
            response.raise_for_status()

            # Rate limiting based on REQUEST_INTERVAL
            if self.request_interval > 0:
                time.sleep(self.request_interval / 1000.0)

            return response.json()

        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response headers: {dict(e.response.headers)}")
                try:
                    print(f"Response body: {e.response.text}")
                except:
                    pass
            return {}

    def save_batch(self, data: Dict[str, Any], batch_number: int, cursor: Optional[str] = None):
        """Save a batch of posts to a JSON file and append condensed text."""
        timestamp = datetime.now().isoformat()

        # Add metadata to the batch
        batch_data = {
            "metadata": {
                "batch_number": batch_number,
                "timestamp": timestamp,
                "group_id": self.group_id,
                "post_type": self.post_type,
                "cursor": cursor,
                "total_posts": len(data.get("posts", []))
            },
            "data": data
        }

        posts = data.get("posts", [])
        saved_files = []

        # Save JSON file if enabled
        if self.save_json:
            filename = f"batch_{batch_number:04d}_{timestamp.replace(':', '-').replace('.', '_')}.json"
            filepath = self.output_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(batch_data, f, indent=2, ensure_ascii=False)
            saved_files.append(f"JSON: {filename}")

        # Extract and append condensed text if enabled
        text_lines = []
        if self.save_cleaned:
            for post in posts:
                if 'text' in post and 'created_at' in post:
                    text = post['text'].strip()
                    if text:  # Only include non-empty posts
                        epoch = self.iso_to_epoch(post['created_at'])
                        # Escape quotes and newlines
                        escaped_text = text.replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
                        text_lines.append(f'{epoch}:"{escaped_text}"')

            # Append to text file
            if text_lines:
                with open(self.text_file, 'a', encoding='utf-8') as f:
                    for line in text_lines:
                        f.write(line + '\n')
                saved_files.append(f"text lines: {len(text_lines)}")

        print(f"Saved {len(posts)} posts - {', '.join(saved_files) if saved_files else 'no output (both formats disabled)'}")

    def scrape_all_posts(self, max_batches: Optional[int] = None):
        """Scrape all posts iteratively using cursor pagination."""
        print("Starting Sidechat scraper...")
        print(f"Group ID: {self.group_id}")
        print(f"Post type: {self.post_type}")
        print(f"Max batches: {max_batches or 'unlimited'}")
        if self.initial_cursor:
            print(f"Starting cursor: {self.initial_cursor}")
        print("-" * 50)

        cursor = self.initial_cursor
        batch_number = 1
        total_posts = 0

        # Save metadata file
        metadata = {
            "scrape_start_time": datetime.now().isoformat(),
            "group_id": self.group_id,
            "post_type": self.post_type,
            "auth_token_length": len(self.auth_token) if self.auth_token else 0
        }

        with open(self.output_dir / "scrape_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)

        while True:
            if max_batches and batch_number > max_batches:
                print(f"Reached maximum batch limit: {max_batches}")
                break

            data = self.make_request(cursor)

            if not data or "posts" not in data:
                print("No data received or invalid response")
                break

            posts = data.get("posts", [])
            if not posts:
                print("No more posts found")
                break

            self.save_batch(data, batch_number, cursor)
            total_posts += len(posts)

            # Get next cursor
            next_cursor = data.get("cursor")
            if not next_cursor or next_cursor == cursor:
                print("No more pages available")
                break

            cursor = next_cursor
            batch_number += 1

        # Update metadata with completion info
        metadata["scrape_end_time"] = datetime.now().isoformat()
        metadata["total_batches"] = batch_number - 1
        metadata["total_posts"] = total_posts

        with open(self.output_dir / "scrape_metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)

        print("-" * 50)
        print(f"Scraping completed!")
        print(f"Total batches: {batch_number - 1}")
        print(f"Total posts: {total_posts}")
        print(f"Data saved to: {self.output_dir.absolute()}")

def main():
    try:
        scraper = SidechatScraper()

        # Get max batches from environment or command line
        max_batches = os.getenv("MAX_BATCHES")
        if max_batches:
            max_batches = int(max_batches)

        scraper.scrape_all_posts(max_batches=max_batches)

    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0

if __name__ == "__main__":
    exit(main())