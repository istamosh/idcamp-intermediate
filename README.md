# Jenius Sentiment Analysis

This project now uses a CSV-first workflow for review data.

1. Generate the reusable review cache once with `python scripts/scrape_jenius_reviews.py`.
2. Open `jenius_sentiment_analysis.ipynb` and run the notebook.

The scraper creates `data/jenius_reviews.csv` only when the file is missing. The notebook does not call the Google Play API; it stops immediately if the CSV is not present.
