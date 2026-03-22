from __future__ import annotations

from pathlib import Path
import time

import pandas as pd
from google_play_scraper import Sort, reviews


APP_ARGS = {
    "app_id": "com.btpn.dc",
    "lang": "en",
    "country": "id",
}

CACHE_PATH = Path("data/jenius_reviews.csv")
TARGET_COUNT = 10000
BATCH_SIZE = 200
MAX_BATCHES_PER_SORT = (TARGET_COUNT // BATCH_SIZE) * 3
MAX_RUNTIME_SECONDS = 20 * 60
WINDOW_SIZE = 10
MIN_NEW_PER_WINDOW = 20
SLEEP_SECONDS = 1.2


def scrape_reviews() -> pd.DataFrame:
    all_reviews: list[dict] = []
    review_ids: set[str] = set()
    start_time = time.time()

    for sort_type in [Sort.NEWEST, Sort.MOST_RELEVANT]:
        continuation_token = None
        seen_tokens: set[str] = set()
        new_in_window = 0
        consecutive_errors = 0

        for batch_idx in range(1, MAX_BATCHES_PER_SORT + 1):
            if len(all_reviews) >= TARGET_COUNT:
                break

            if time.time() - start_time > MAX_RUNTIME_SECONDS:
                print("Runtime limit reached. Stopping scrape early.")
                break

            try:
                result, next_token = reviews(
                    **APP_ARGS,
                    sort=sort_type,
                    count=BATCH_SIZE,
                    continuation_token=continuation_token,
                )
                consecutive_errors = 0
            except Exception as err:
                consecutive_errors += 1
                print(f"{sort_type.name} batch {batch_idx} failed: {err}")
                if consecutive_errors >= 3:
                    print(f"{sort_type.name}: too many consecutive errors, stopping.")
                    break
                time.sleep(2)
                continue

            if not result:
                print(f"{sort_type.name}: no results returned, stopping.")
                break

            prev_count = len(all_reviews)

            for review in result:
                if len(all_reviews) >= TARGET_COUNT:
                    break

                review_id = review.get("reviewId")
                if review_id and review_id not in review_ids:
                    review_ids.add(review_id)
                    all_reviews.append(review)

            added = len(all_reviews) - prev_count
            new_in_window += added
            print(f"{sort_type.name} batch {batch_idx}: +{added} new, total={len(all_reviews)}")

            if len(all_reviews) >= TARGET_COUNT:
                break

            if next_token is None:
                print(f"{sort_type.name}: no continuation token, source exhausted.")
                break

            token_key = repr(next_token)
            if token_key in seen_tokens:
                print(f"{sort_type.name}: repeated continuation token detected, stopping to avoid loop.")
                break

            seen_tokens.add(token_key)
            continuation_token = next_token

            if batch_idx % WINDOW_SIZE == 0:
                if new_in_window < MIN_NEW_PER_WINDOW:
                    print(
                        f"{sort_type.name}: only {new_in_window} new reviews in last {WINDOW_SIZE} batches, stopping."
                    )
                    break
                new_in_window = 0

            time.sleep(SLEEP_SECONDS)

        if len(all_reviews) >= TARGET_COUNT:
            break

        if time.time() - start_time > MAX_RUNTIME_SECONDS:
            break

    df = pd.DataFrame(all_reviews[:TARGET_COUNT])
    if df.empty:
        raise RuntimeError("No reviews were collected. Cache file was not created.")

    return df


def main() -> None:
    if CACHE_PATH.exists():
        existing_df = pd.read_csv(CACHE_PATH)
        print(f"Cache already exists at {CACHE_PATH} with {len(existing_df)} rows. No API call made.")
        return

    CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
    df = scrape_reviews()
    df.to_csv(CACHE_PATH, index=False)

    print(f"Saved {len(df)} reviews to {CACHE_PATH}.")
    if len(df) < TARGET_COUNT:
        print("Target not fully reached. Keep this cache or delete it and run the script again later.")


if __name__ == "__main__":
    main()