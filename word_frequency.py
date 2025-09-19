#!/usr/bin/env python3
"""
Word Frequency Analysis for Sidechat Posts
Searches for a word in posts and creates a histogram by month/year.
"""

import sys
import re
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from collections import defaultdict, Counter
from pathlib import Path
import argparse

def parse_timestamp(epoch_str):
    """Convert epoch timestamp to datetime object."""
    try:
        epoch = int(epoch_str)
        return datetime.fromtimestamp(epoch)
    except (ValueError, OSError):
        return None

def extract_posts_from_file(filepath):
    """Extract posts from the condensed text file."""
    posts = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                # Parse format: epoch:"text"
                if ':' not in line:
                    continue

                epoch_str, text_part = line.split(':', 1)

                # Remove quotes from text
                if text_part.startswith('"') and text_part.endswith('"'):
                    text = text_part[1:-1]
                else:
                    text = text_part

                # Unescape text
                text = text.replace('\\"', '"').replace('\\n', '\n').replace('\\r', '\r')

                timestamp = parse_timestamp(epoch_str)
                if timestamp:
                    posts.append((timestamp, text))

    except FileNotFoundError:
        print(f"Error: File {filepath} not found")
        return []
    except Exception as e:
        print(f"Error reading file: {e}")
        return []

    return posts

def search_word_in_posts(posts, search_word):
    """Search for word in posts (case-insensitive) and group by month."""
    monthly_counts = defaultdict(int)
    monthly_totals = defaultdict(int)
    matching_posts = []

    search_word_lower = search_word.lower()

    for timestamp, text in posts:
        # Group by year-month
        month_key = timestamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_totals[month_key] += 1

        # Case-insensitive word search
        if search_word_lower in text.lower():
            monthly_counts[month_key] += 1
            matching_posts.append((timestamp, text))

    return monthly_counts, monthly_totals, matching_posts

def create_histogram(monthly_counts, monthly_totals, search_word, output_file, normalize=False):
    """Create and save histogram of word frequency over time."""
    if not monthly_counts:
        print(f"No posts found containing '{search_word}'")
        return

    # Sort by date
    sorted_months = sorted(monthly_counts.keys())

    if normalize:
        # Calculate normalized frequencies (percentage)
        counts = [(monthly_counts[month] / monthly_totals[month]) * 100
                 for month in sorted_months]
        ylabel = 'Percentage of Posts (%)'
        title_suffix = '(Normalized)'
    else:
        counts = [monthly_counts[month] for month in sorted_months]
        ylabel = 'Number of Posts'
        title_suffix = ''

    # Create figure
    plt.figure(figsize=(12, 6))

    # Create bar chart
    bars = plt.bar(sorted_months, counts, width=20, alpha=0.7, color='steelblue', edgecolor='black')

    # Customize the plot
    plt.title(f'Frequency of "{search_word}" in Sidechat Posts Over Time {title_suffix}',
             fontsize=14, fontweight='bold')
    plt.xlabel('Month/Year', fontsize=12)
    plt.ylabel(ylabel, fontsize=12)

    # Format x-axis to show month/year
    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    plt.gca().xaxis.set_major_locator(mdates.MonthLocator(interval=1))

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=45)

    # Add value labels on top of bars
    for bar, count in zip(bars, counts):
        if normalize:
            label = f"{count:.1f}%"
        else:
            label = str(int(count))
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (max(counts) * 0.01),
                label, ha='center', va='bottom', fontsize=10)

    # Add grid for better readability
    plt.grid(axis='y', alpha=0.3)

    # Adjust layout to prevent label cutoff
    plt.tight_layout()

    # Save the plot
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Histogram saved to: {output_file}")

    # Show statistics
    total_posts = sum(counts)
    print(f"Total posts containing '{search_word}': {total_posts}")
    print(f"Date range: {min(sorted_months).strftime('%b %Y')} to {max(sorted_months).strftime('%b %Y')}")

    # Close the plot to free memory
    plt.close()

def main():
    parser = argparse.ArgumentParser(description='Analyze word frequency in Sidechat posts')
    parser.add_argument('word', help='Word to search for (case-insensitive)')
    parser.add_argument('--input', '-i', default='data/sidechat_posts.txt',
                        help='Input file path (default:data/sidechat_posts.txt)')
    parser.add_argument('--output', '-o', help='Output PNG file path (default: word_frequency_WORD.png)')
    parser.add_argument('--show-posts', '-s', action='store_true',
                        help='Show sample posts containing the word')
    parser.add_argument('--normalize', '-n', action='store_true',
                        help='Normalize frequencies by total posts per month (show percentages)')

    args = parser.parse_args()

    # Set default output filename
    if not args.output:
        safe_word = re.sub(r'[^\w\-_]', '_', args.word)
        # Ensure visualizations directory exists
        viz_dir = Path("visualizations")
        viz_dir.mkdir(exist_ok=True)
        args.output = f"visualizations/word_frequency_{safe_word}.png"

    # Check if input file exists
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file '{args.input}' not found")
        return 1

    print(f"Loading posts from: {args.input}")
    posts = extract_posts_from_file(input_path)

    if not posts:
        print("No valid posts found in the file")
        return 1

    print(f"Loaded {len(posts)} posts")
    print(f"Searching for word: '{args.word}' (case-insensitive)")

    # Search for the word
    monthly_counts, monthly_totals, matching_posts = search_word_in_posts(posts, args.word)

    if not monthly_counts:
        print(f"No posts found containing '{args.word}'")
        return 1

    # Create histogram
    create_histogram(monthly_counts, monthly_totals, args.word, args.output, args.normalize)

    # Show sample posts if requested
    if args.show_posts and matching_posts:
        print(f"\nSample posts containing '{args.word}':")
        for i, (timestamp, text) in enumerate(matching_posts[:5], 1):
            print(f"{i}. [{timestamp.strftime('%Y-%m-%d %H:%M')}] {text[:100]}{'...' if len(text) > 100 else ''}")
        if len(matching_posts) > 5:
            print(f"... and {len(matching_posts) - 5} more posts")

    return 0

if __name__ == "__main__":
    exit(main())