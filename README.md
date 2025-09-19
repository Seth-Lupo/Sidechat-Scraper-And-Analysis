# QTA Scripts

## Setup

1. **Clone and install:**
   ```bash
   git clone <repo-url>
   cd qta
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Sidechat auth token and group ID
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