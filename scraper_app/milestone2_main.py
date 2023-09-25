#import libray
import pandas as pd
from bs4 import BeautifulSoup
import requests
import datetime


def scrape_sitemap(url):
    """
        This method extracts all the links from a companys sitemap.xml
        input: url for a company sitemap.xml
        output : pandas Series with all the links or None if no links found

        """
    r = requests.get(url)
    bs = BeautifulSoup(r.text, 'lxml-xml')
    urlset = bs.find_all('loc')
    urls = []
    if len(urlset) > 0:
        for link in urlset:
            urls.append(link.text.strip())

    urls2 = []
    for link in urls:
        if link.endswith('xml'):
            r = requests.get(link)
            if r.ok:
                bs2 = BeautifulSoup(r.text, 'lxml')
                urlset = bs2.find_all('loc')
                if len(urlset) > 0:
                    for url in urlset:
                        urls2.append(url.text.strip())
        else:
            urls2.append(link)

    if len(urls2) > 0:
        return pd.Series(urls2).drop_duplicates().str.strip()

    return None


def scrape_website(alllinks):
    """
        This method extracts all the the text data from webpages of a company
        input: pandas series with all the links in the company's website
        output : pandas dataframe with the columns , key (webpage link), text
                 that includes the text of the webpage, and the timestamp when the data
                 was scraped.

        """
    text_dict = {}

    for link in alllinks.to_list():
        r = requests.get(link)
        if r.ok:
            print(link)
            bs = BeautifulSoup(r.text, 'lxml')
            for tag in bs.find_all(['header', 'nav', 'footer']):
                tag.decompose()

            text_only = bs.get_text(separator=' ', strip=True)
            text_dict[link] = text_only

    df = pd.DataFrame()
    df['key'] = text_dict.keys()
    df['text'] = text_dict.values()
    df['timestamp'] = pd.to_datetime(datetime.date.today())
    return df

# run the scraping engine, and save the extracted data to csv
def main():
    print("Starting scraping :\n")
    sitemap = pd.read_csv("sitemap.csv")
    for item in sitemap['sitemap']:
        print(f"working on {item}")
        links = scrape_sitemap(item)
        if links is not None:
            print(f"{links.shape[0]} webpages found for scraping. For demo scraping only the first 10 webpage \n")

            df = scrape_website(links[:10])
            df.to_csv('apple.csv', index=False)
            print("\nFinished scraping. Data stored in apple.csv")
        else:
            print(f"No links were found in {item}")



if __name__ == "__main__":
    main()
