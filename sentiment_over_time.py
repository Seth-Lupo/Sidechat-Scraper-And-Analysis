#!/usr/bin/env python3
"""
Analyze and graph sentiment of messages over time per month/year.
Reads from sidechat_posts.txt and creates a sentiment timeline.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from textblob import TextBlob
from datetime import datetime
import re
import argparse
import numpy as np

def load_messages(filepath):
    """Load messages from the text file."""
    messages = []

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Parse format: epoch_timestamp:"text_content"
            match = re.match(r'^(\d+):"(.+)"$', line)
            if match:
                timestamp = int(match.group(1))
                text = match.group(2)
                # Unescape text
                text = text.replace('\\"', '"').replace('\\n', '\n').replace('\\r', '\r')
                messages.append({'timestamp': timestamp, 'text': text})

    return messages

def analyze_sentiment_textblob(text):
    """Analyze sentiment using TextBlob."""
    blob = TextBlob(text)
    return blob.sentiment.polarity

def analyze_sentiment_lexicon(text):
    """Simple lexicon-based sentiment analysis."""
    positive_words = {'good', 'great', 'awesome', 'amazing', 'love', 'wonderful', 'excellent', 'fantastic', 'perfect', 'happy', 'joy', 'beautiful', 'best', 'nice', 'cool', 'fun', 'excited', 'glad', 'pleased', 'satisfied'}
    negative_words = {'bad', 'terrible', 'awful', 'horrible', 'hate', 'worst', 'stupid', 'dumb', 'sucks', 'annoying', 'frustrated', 'angry', 'sad', 'disappointed', 'disgusting', 'boring', 'lame', 'trash', 'garbage', 'crappy'}

    words = text.lower().split()
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)

    total = positive_count + negative_count
    if total == 0:
        return 0
    return (positive_count - negative_count) / total

def analyze_sentiment_simple(text):
    """Very simple sentiment analysis based on punctuation and caps."""
    text = text.strip()
    score = 0

    # Exclamation marks suggest excitement (positive)
    score += text.count('!') * 0.1

    # Question marks are neutral to slightly negative
    score -= text.count('?') * 0.05

    # All caps suggests strong emotion (could be positive or negative)
    if text.isupper() and len(text) > 3:
        score += 0.2 if '!' in text else -0.2

    # Emojis/emoticons (simplified)
    positive_emojis = [':)', '😊', '😄', '😁', '❤️', '💕']
    negative_emojis = [':(', '😢', '😡', '😤', '💔']

    for emoji in positive_emojis:
        score += text.count(emoji) * 0.3
    for emoji in negative_emojis:
        score -= text.count(emoji) * 0.3

    return max(-1, min(1, score))

def analyze_sentiment(text, method='textblob'):
    """Analyze sentiment using specified method."""
    if method == 'textblob':
        return analyze_sentiment_textblob(text)
    elif method == 'lexicon':
        return analyze_sentiment_lexicon(text)
    elif method == 'simple':
        return analyze_sentiment_simple(text)
    else:
        raise ValueError(f"Unknown sentiment analysis method: {method}")

def create_sentiment_timeline(messages, method='textblob', granularity='month'):
    """Create DataFrame with sentiment analysis by month/year."""
    df = pd.DataFrame(messages)

    # Convert timestamp to datetime
    df['datetime'] = pd.to_datetime(df['timestamp'], unit='s')

    # Analyze sentiment
    print(f"Analyzing sentiment using {method} method...")
    df['sentiment'] = df['text'].apply(lambda x: analyze_sentiment(x, method))

    # Create time period column based on granularity
    if granularity == 'month':
        df['time_period'] = df['datetime'].dt.to_period('M')
        period_name = 'month'
    elif granularity == 'week':
        df['time_period'] = df['datetime'].dt.to_period('W')
        period_name = 'week'
    elif granularity == 'day':
        df['time_period'] = df['datetime'].dt.to_period('D')
        period_name = 'day'
    elif granularity == 'year':
        df['time_period'] = df['datetime'].dt.to_period('Y')
        period_name = 'year'
    else:
        raise ValueError(f"Unknown granularity: {granularity}")

    # Group by time period and calculate average sentiment
    period_sentiment = df.groupby('time_period').agg({
        'sentiment': ['mean', 'std', 'count']
    }).round(3)

    period_sentiment.columns = ['avg_sentiment', 'std_sentiment', 'message_count']
    period_sentiment = period_sentiment.reset_index()

    return df, period_sentiment, period_name

def plot_sentiment_timeline(period_sentiment, period_name, method, granularity):
    """Create visualization of sentiment over time."""
    plt.figure(figsize=(15, 8))

    # Convert period to datetime for plotting
    x_data = period_sentiment['time_period'].dt.to_timestamp()

    # Main sentiment line plot
    plt.subplot(2, 1, 1)
    plt.plot(x_data, period_sentiment['avg_sentiment'],
             marker='o', linewidth=2, markersize=4, color='steelblue')
    plt.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
    plt.title(f'Average Sentiment Over Time ({method} method, {granularity}ly)', fontsize=16, fontweight='bold')
    plt.ylabel('Average Sentiment Score', fontsize=12)
    plt.grid(True, alpha=0.3)

    # Add sentiment range
    plt.fill_between(x_data,
                     period_sentiment['avg_sentiment'] - period_sentiment['std_sentiment'],
                     period_sentiment['avg_sentiment'] + period_sentiment['std_sentiment'],
                     alpha=0.2, color='steelblue')

    # Message count subplot
    plt.subplot(2, 1, 2)
    width = 20 if granularity == 'month' else 7 if granularity == 'week' else 1
    plt.bar(x_data, period_sentiment['message_count'],
            alpha=0.7, color='lightcoral', width=width)
    plt.title(f'Message Count Over Time ({granularity}ly)', fontsize=16, fontweight='bold')
    plt.ylabel('Number of Messages', fontsize=12)
    plt.xlabel('Time', fontsize=12)
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.xticks(rotation=45)

    # Save the plot
    filename = f'visualizations/sentiment_over_time_{method}_{granularity}.png'
    plt.savefig(filename, dpi=300, bbox_inches='tight')
    plt.show()
    return filename

def print_summary_stats(df, period_sentiment, period_name, method):
    """Print summary statistics."""
    print(f"\n=== SENTIMENT ANALYSIS SUMMARY ({method} method) ===")
    print(f"Total messages analyzed: {len(df):,}")
    print(f"Time period: {df['datetime'].min().strftime('%Y-%m-%d')} to {df['datetime'].max().strftime('%Y-%m-%d')}")
    print(f"Average sentiment: {df['sentiment'].mean():.3f}")
    print(f"Sentiment std: {df['sentiment'].std():.3f}")

    print(f"\nSentiment distribution:")
    print(f"  Positive (>0.1): {(df['sentiment'] > 0.1).sum():,} ({(df['sentiment'] > 0.1).mean()*100:.1f}%)")
    print(f"  Neutral (-0.1 to 0.1): {((df['sentiment'] >= -0.1) & (df['sentiment'] <= 0.1)).sum():,} ({((df['sentiment'] >= -0.1) & (df['sentiment'] <= 0.1)).mean()*100:.1f}%)")
    print(f"  Negative (<-0.1): {(df['sentiment'] < -0.1).sum():,} ({(df['sentiment'] < -0.1).mean()*100:.1f}%)")

    print(f"\nMost positive {period_name}: {period_sentiment.loc[period_sentiment['avg_sentiment'].idxmax(), 'time_period']} ({period_sentiment['avg_sentiment'].max():.3f})")
    print(f"Most negative {period_name}: {period_sentiment.loc[period_sentiment['avg_sentiment'].idxmin(), 'time_period']} ({period_sentiment['avg_sentiment'].min():.3f})")

def main():
    parser = argparse.ArgumentParser(description='Analyze sentiment of messages over time')
    parser.add_argument('--method', choices=['textblob', 'lexicon', 'simple'],
                       default='textblob', help='Sentiment analysis method (default: textblob)')
    parser.add_argument('--granularity', choices=['day', 'week', 'month', 'year'],
                       default='month', help='Time granularity (default: month)')
    parser.add_argument('--input', default='data/sidechat_posts.txt',
                       help='Input file path (default: data/sidechat_posts.txt)')
    parser.add_argument('--compare', action='store_true',
                       help='Compare all three sentiment analysis methods')

    args = parser.parse_args()

    # Load and process data
    print("Loading messages...")
    messages = load_messages(args.input)

    if not messages:
        print("No messages found!")
        return

    print(f"Loaded {len(messages):,} messages")

    if args.compare:
        # Compare all methods
        methods = ['textblob', 'lexicon', 'simple']
        plt.figure(figsize=(20, 12))

        for i, method in enumerate(methods):
            df, period_sentiment, period_name = create_sentiment_timeline(messages, method, args.granularity)

            plt.subplot(3, 1, i+1)
            x_data = period_sentiment['time_period'].dt.to_timestamp()
            plt.plot(x_data, period_sentiment['avg_sentiment'],
                    marker='o', linewidth=2, markersize=3,
                    label=f'{method} (avg: {df["sentiment"].mean():.3f})')
            plt.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
            plt.title(f'Sentiment Over Time - {method.title()} Method', fontsize=14, fontweight='bold')
            plt.ylabel('Sentiment Score', fontsize=10)
            plt.grid(True, alpha=0.3)
            plt.legend()

        plt.tight_layout()
        plt.xticks(rotation=45)
        filename = f'visualizations/sentiment_comparison_{args.granularity}.png'
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        plt.show()

        print(f"\nComparison complete! Graph saved as '{filename}'")

        # Print comparison stats
        print("\n=== METHOD COMPARISON ===")
        for method in methods:
            df, _, _ = create_sentiment_timeline(messages, method, args.granularity)
            print(f"{method.title():8}: avg={df['sentiment'].mean():.3f}, std={df['sentiment'].std():.3f}")

    else:
        # Single method analysis
        df, period_sentiment, period_name = create_sentiment_timeline(messages, args.method, args.granularity)

        # Print summary
        print_summary_stats(df, period_sentiment, period_name, args.method)

        # Create visualization
        print("\nCreating visualization...")
        filename = plot_sentiment_timeline(period_sentiment, period_name, args.method, args.granularity)

        print(f"\nSentiment analysis complete! Graph saved as '{filename}'")

if __name__ == "__main__":
    main()