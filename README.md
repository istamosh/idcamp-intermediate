# Jenius Sentiment Analysis

Sentiment classifier (positive / neutral / negative) trained on Google Play reviews for the Jenius banking app. Uses classic ML (Logistic Regression, Naive Bayes, SVM, Random Forest) with TF-IDF / BoW features.

## How to run

Scrape reviews first (only needed once, skips if CSV already exists):

```bash
python scripts/scrape_jenius_reviews.py
```

Then open and run `jenius_sentiment_analysis.ipynb` top to bottom.

## Structure

```
data/
  jenius_reviews.csv        # scraped reviews cache
  experiments/              # train/test/prediction CSVs per experiment
scripts/
  scrape_jenius_reviews.py  # scraper
jenius_sentiment_analysis.ipynb
```
