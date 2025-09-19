# Sidechat Post Scraper

A tool to scrape your university's Sidechat and build neat visualizations from the data.

## Overview

This project allows you to collect posts from your university's Sidechat platform and create insightful visualizations to analyze trends, popular topics, and community engagement patterns.

## Getting Started

### Prerequisites

- Python 3.8+
- macOS (for token extraction instructions)
- Sidechat app installed on Mac

### Token Extraction

To use this scraper, you'll need to extract authentication tokens from the Sidechat app using mitmproxy.

#### Step 1: Install mitmproxy

```bash
brew install mitmproxy
```

#### Step 2: Configure mitmproxy

1. Start mitmproxy:
   ```bash
   mitmproxy
   ```

2. Configure your Mac's proxy settings:
   - Go to System Preferences → Network
   - Select your active network connection
   - Click "Advanced" → "Proxies"
   - Check "Web Proxy (HTTP)" and "Secure Web Proxy (HTTPS)"
   - Set both to `127.0.0.1` port `8080`
   - Click "OK" and "Apply"

#### Step 3: Install mitmproxy certificate

1. With mitmproxy running, visit `mitm.it` in your browser
2. Download and install the certificate for macOS
3. In Keychain Access, find the mitmproxy certificate and set it to "Always Trust"

#### Step 4: Extract tokens

1. Open the Sidechat app on your Mac
2. Navigate through the app (view posts, refresh feed, etc.)
3. In mitmproxy, look for requests to Sidechat's API endpoints
4. Extract the following tokens from the request headers:
   - `Authorization` token
   - `X-API-Key` (if present)
   - Session cookies

### Setup

1. **Clone and install:**
   ```bash
   git clone <repo-url>
   cd qta
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your extracted Sidechat auth token and group ID
   ```

3. **Create directories:**
   ```bash
   mkdir -p data visualizations
   ```

## Scripts

### sidechat_scraper.py

Scrapes posts from Sidechat API and saves them as JSON batches and/or condensed text format.

**Usage:**
```bash
python sidechat_scraper.py
```

**Configuration:**
Edit `.env` file with required tokens. See `.env.example` for all available options.

### extract_texts.py

Extracts condensed text from existing Sidechat JSON files.

**Usage:**
```bash
python extract_texts.py
```

Processes all `batch_*.json` files in `data/` directory and outputs to `sidechat_posts.txt` with format: `epoch_timestamp:"text_content"`

### word_frequency.py

Analyzes word frequency in posts and generates histograms.

**Usage:**
```bash
python word_frequency.py <word> [options]
```

**Options:**
- `-i, --input` - Input file path (default: data/sidechat_posts.txt)
- `-o, --output` - Output PNG file path (default: visualizations/word_frequency_WORD.png)
- `-s, --show-posts` - Show sample posts containing the word
- `-n, --normalize` - Show percentages instead of raw counts

**Examples:**
```bash
python word_frequency.py covid
python word_frequency.py "party" --normalize --show-posts
python word_frequency.py test -i custom_posts.txt -o test_analysis.png
```

### sentiment_over_time.py

Analyzes sentiment of messages over time using multiple techniques and creates timeline visualizations.

**Usage:**
```bash
python sentiment_over_time.py [options]
```

**Options:**
- `--method` - Sentiment analysis method: `textblob`, `lexicon`, `simple` (default: textblob)
- `--granularity` - Time granularity: `day`, `week`, `month`, `year` (default: month)
- `--input` - Input file path (default: data/sidechat_posts.txt)
- `--compare` - Compare all three sentiment analysis methods

**Sentiment Analysis Methods:**
- `textblob` - Machine learning-based sentiment analysis using TextBlob
- `lexicon` - Simple word-based sentiment using positive/negative word lists
- `simple` - Basic analysis using punctuation, capitalization, and emoji cues

**Examples:**
```bash
# Default analysis (TextBlob, monthly)
python sentiment_over_time.py

# Weekly sentiment using lexicon method
python sentiment_over_time.py --method lexicon --granularity week

# Daily sentiment using simple method
python sentiment_over_time.py --method simple --granularity day

# Compare all methods side-by-side
python sentiment_over_time.py --compare --granularity month

# Custom input file
python sentiment_over_time.py --input my_data.txt --method textblob
```

**Output:**
- Saves graphs to `visualizations/sentiment_over_time_METHOD_GRANULARITY.png`
- Comparison mode saves to `visualizations/sentiment_comparison_GRANULARITY.png`
- Displays summary statistics including sentiment distribution and extreme periods

## Features

- Extract posts from your university's Sidechat
- Generate visualizations for:
  - Post frequency over time
  - Popular topics and keywords
  - User engagement metrics
  - Word frequency analysis
  - Sentiment analysis over time with multiple methods

## Troubleshooting

- If token extraction fails, ensure mitmproxy certificate is properly installed
- Check that proxy settings are correctly configured
- Verify the Sidechat app is making network requests while mitmproxy is running
- Some corporate networks may block proxy connections

## Important Notes

- This tool is for educational and research purposes only
- **Only use this on university Sidechats you are authorized to access**
- Respect Sidechat's terms of service and rate limits
- Only scrape data from your own university's community
- **Do not share organization-specific data or personal information from posts**
- Be mindful of privacy and ensure compliance with your university's data policies

## Disclaimer

This project is not affiliated with Sidechat. Use responsibly and in accordance with your university's policies and Sidechat's terms of service.