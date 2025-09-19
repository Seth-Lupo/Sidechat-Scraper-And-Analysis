#!/usr/bin/env python3
"""
Extract condensed text from Sidechat JSON files.
Format: epoch_timestamp:"text_content"
"""

import json
import glob
import os
from datetime import datetime
from pathlib import Path

def iso_to_epoch(iso_timestamp):
    """Convert ISO timestamp to Unix epoch."""
    dt = datetime.fromisoformat(iso_timestamp.replace('Z', '+00:00'))
    return int(dt.timestamp())

def extract_posts_from_file(filepath):
    """Extract posts from a single JSON file."""
    posts = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle both direct API response and our wrapped format
        if 'data' in data and 'posts' in data['data']:
            posts_data = data['data']['posts']
        elif 'posts' in data:
            posts_data = data['posts']
        else:
            return posts

        for post in posts_data:
            if 'text' in post and 'created_at' in post:
                text = post['text'].strip()
                if text:  # Only include non-empty posts
                    epoch = iso_to_epoch(post['created_at'])
                    # Escape quotes in text and remove newlines
                    escaped_text = text.replace('"', '\\"').replace('\n', '\\n').replace('\r', '\\r')
                    posts.append(f'{epoch}:"{escaped_text}"')

    except Exception as e:
        print(f"Error processing {filepath}: {e}")

    return posts

def main():
    data_dir = Path("data")

    if not data_dir.exists():
        print("Data directory not found")
        return

    # Find all batch JSON files
    batch_files = glob.glob(str(data_dir / "batch_*.json"))

    if not batch_files:
        print("No batch files found")
        return

    print(f"Processing {len(batch_files)} files...")

    all_posts = []

    for filepath in sorted(batch_files):
        print(f"Processing: {filepath}")
        posts = extract_posts_from_file(filepath)
        all_posts.extend(posts)

    # Remove duplicates while preserving order
    seen = set()
    unique_posts = []
    for post in all_posts:
        if post not in seen:
            seen.add(post)
            unique_posts.append(post)

    # Sort by timestamp (first part before colon)
    unique_posts.sort(key=lambda x: int(x.split(':', 1)[0]))

    # Write to output file
    output_file = "sidechat_posts.txt"
    with open(output_file, 'w', encoding='utf-8') as f:
        for post in unique_posts:
            f.write(post + '\n')

    print(f"Extracted {len(unique_posts)} unique posts to {output_file}")

    # Show sample output
    print("\nSample lines:")
    for i, post in enumerate(unique_posts[:5]):
        print(f"{i+1}: {post}")

if __name__ == "__main__":
    main()