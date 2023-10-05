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
    p = Path('../../data')
    path = str(p)
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
        print(f"{links.shape[0]} webpages found for scraping. For demo, scraping only the first 10 webpages.\n")

        scraped_df, log_df = scrape_website(links[:3], options)
        if scraped_df.empty:
            print(f"No data was scraped from the first 10 links of {item}.\n")
            continue

        split = str(datetime.now()).split()
        date = str(split[0])
        ms = str(split[1].split('.')[1])
        timestamp = date + "-" + ms

        output_file = path + '/' + website_name + '_' + timestamp + '.csv'
        print(output_file)
        scraped_df.to_csv(output_file, index=False)
        if not log_df.empty:
            log_file = f'log/{website_name}_{timestamp}.csv'
            log_df.to_csv(log_file, index=False)

        print(f"Finished scraping. Data stored in {output_file}\n")


if __name__ == "__main__":
    main()
