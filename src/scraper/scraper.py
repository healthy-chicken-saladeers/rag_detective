import pandas as pd
from datetime import datetime
from scraperlib import *
from pathlib import Path

def main():
    """
    Runs the scraping engine, extracts data from the specified sitemaps, and saves
    the extracted data to a CSV file.

    The CSV file contains the scraped data from the first 10 webpages of each sitemap.
    """
    options = set_chrome_options()
    try:
        sitemap_df = pd.read_csv("sitemap.csv")
    except FileNotFoundError:
        print("Error: The file 'sitemap.csv' was not found.")
        return
    except pd.errors.EmptyDataError:
        print("Error: The file 'sitemap.csv' is empty.")
        return

    if 'sitemap' not in sitemap_df.columns:
        print("Error: The expected 'sitemap' column is missing in 'sitemap.csv'.")
        return

    print("Starting scraping:\n")
    for index, item in enumerate(sitemap_df['sitemap'], start=1):
        print(f"Working on {item} ...")
        links = scrape_sitemap(item)
        if links is None or links.empty:
            print(f"No links were found in {item}.\n")
            continue

        link_split = item.split('/')
        if link_split:
            website_name = link_split[2]
        print(f"{links.shape[0]} webpages found for scraping. Scraping all pages.\n")

        scraped_df, log_df = scrape_website(links, options)
        if scraped_df.empty:
            print(f"No data was scraped for {item}.\n")
            continue

        timestamp = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')

        output_file =   f"{website_name}_{timestamp}.csv"

        flag, stored_message =save_file(scraped_df, output_file)
        if not log_df.empty:
            log_file = f'log/{website_name}_{timestamp}.csv'
            log_df.to_csv(log_file, index=False)

        if flag:
            print(f"Finished scraping.{stored_message}")


if __name__ == "__main__":
    main()
