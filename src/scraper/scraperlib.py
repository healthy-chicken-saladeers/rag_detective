import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from datetime import datetime
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import ChromiumOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}


def set_chrome_options() -> ChromiumOptions:
    """Sets chrome options for Selenium.Chrome options for headless browser is enabled.
    Args: None

    returns:
        Chrome options that can work headless i.e. without actually launching the browser.
    """
    chrome_options = ChromiumOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_prefs = {}
    chrome_options.experimental_options["prefs"] = chrome_prefs
    chrome_prefs["profile.default_content_settings"] = {"images": 2}
    return chrome_options


def scrape_sitemap(url):
    """
    Extracts all the links from a company's sitemap.xml.

    Args:
    url (str): The URL for a company sitemap.xml.

    Returns:
    pd.Series: A pandas Series with all the links, or None if no links found.
    """
    try:
        with requests.get(url, headers=headers) as response:
            response.raise_for_status()  # Check if the request was successful
            soup = BeautifulSoup(response.text, 'lxml-xml')
            urls = [link.text.strip() for link in soup.find_all('loc') if link]

            if not urls:
                return None  # Return None if no URLs found

            extended_urls = []
            for link in urls:
                if link.endswith('xml'):
                    try:
                        with requests.get(link, headers=headers) as response:
                            response.raise_for_status()  # Check if the request was successful
                            nested_soup = BeautifulSoup(response.text, 'lxml')
                            nested_urls = [url.text.strip() for url in nested_soup.find_all \
                                ('loc') if url]
                            extended_urls.extend(nested_urls)
                    except requests.RequestException as e:
                        print(f"Error occurred while processing {link}: {e}")
                else:
                    extended_urls.append(link)

            if not extended_urls:
                return None  # Return None if no extended URLs found

            return pd.Series(extended_urls).drop_duplicates().str.strip()

    except requests.RequestException as e:
        print(f"Error occurred: {e}")
        return None  # Return None if the initial request fails


def scrape_website(all_links, options):
    """
    Extracts all the text data from the webpages of a company.

    Args:
    all_links (pd.Series): A pandas Series with all the links in the company's website.
    options: Chrome options to apply to the browser

    Returns:
    pd.DataFrame: A pandas DataFrame with the columns 'key' (webpage link), 'text' (includes
                  the text of the webpage), and 'timestamp' (when the data was scraped).

    pd.DataFrame : A pandas dataframe with columns 'key' (webpage link), 'error with timestamp' .
    """
    log_dict = {}
    text_dict = {}
    wait_condition = (By.TAG_NAME, ['html', 'div', 'body'])

    for link in all_links.to_list():
        try:
            # First, scrape the page using requests
            with requests.get(link, headers=headers) as response:
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'lxml')

                    [tag.decompose() for tag in soup.find_all(['header', 'nav', 'footer'])]
                    text_only_requests = soup.get_text(separator=' ', strip=True)
                    print(link)

                # If content seems too short or response code is not 200, use Selenium
                if response.status_code != 200 or len(text_only_requests.split()) < 50:
                    try:
                        browser = webdriver.Chrome(options)
                        browser.get(link)
                        wait = WebDriverWait(browser, timeout=30)

                        wait.until(lambda d: browser.find_element \
                            (By.TAG_NAME, 'html').is_displayed() \
                            if browser.find_element(By.TAG_NAME, 'html') else True & \
                                  np.all(np.array([i.is_displayed() \
                                                   for i in \
                                                   browser.find_elements( \
                                                       By.TAG_NAME, \
                                                       'div')])) \
                            if browser.find_elements(By.TAG_NAME, 'div') else True)

                        soup_selenium = BeautifulSoup(browser.page_source, 'lxml')

                        [tag.decompose() for tag in soup_selenium.find_all \
                            (['header', 'nav', 'footer'])]
                        text_only_selenium = soup_selenium.get_text(separator=' ', strip=True).lower()

                        text_dict[link] = text_only_selenium

                        if len(text_only_selenium.lower().split()) < 20:
                            log_dict[link] = str(pd.to_datetime(datetime.today().date())) + \
                                             " " + text_only_selenium

                    except Exception as e:
                        print(f"Error occurred while processing {link} in selenium: \
                        {e.with_traceback}")
                        log_dict[link] = f'{pd.to_datetime(datetime.today().date())}\
                          {e.with_traceback}'

                    finally:
                        browser.close()

                else:
                    text_dict[link] = text_only_requests.lower()

        except requests.RequestException as e:
            print(f"Error occurred while processing {link}: {e}")
            log_dict[link] = f'pd.to_datetime(datetime.today().date())  {e.with_traceback}'
    if not log_dict:
        df_log = pd.DataFrame()
    else:

        df_log = pd.DataFrame(list(log_dict.items()), columns=['key', 'error'])

    if not text_dict:
        return pd.DataFrame(), df_log  # return empty DataFrame if no text is extracted

    df = pd.DataFrame(list(text_dict.items()), columns=['key', 'text'])
    df['timestamp'] = pd.to_datetime(datetime.today().date())

    return df, df_log
